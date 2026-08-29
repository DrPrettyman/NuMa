"""Tests for build.py's two failure modes: dangling references and cycles.

Uses small synthetic in-memory nodes, not the real content data, so these
stay fast and don't need to change whenever content is authored/edited.
Built from Skill/Strategy, not Concept: Concept has no edges of its own
(concept-to-concept sequencing is out of scope for now, enforced by
extra="forbid" on ConceptNode — see schema.py and
planning/mome_relations_and_granularity.md), so it can't participate in a
referential-integrity or cycle scenario.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import networkx as nx

from build import build_graph, check_references
from schema import ConceptNode, SkillNode, StrategyNode, StrategyRequires


def _skill(id_: str, satisfied_by: list[str] | None = None) -> SkillNode:
    return SkillNode(
        id=id_, type="skill", label=id_, description="", satisfied_by=satisfied_by or []
    )


def _strategy(id_: str, skills: list[str] | None = None) -> StrategyNode:
    return StrategyNode(
        id=id_,
        type="strategy",
        label=id_,
        description="",
        requires=StrategyRequires(skills=skills or []),
    )


def test_dangling_reference_is_caught():
    nodes = {"skill.a": _skill("skill.a", satisfied_by=["strategy.missing"])}
    errors = check_references(nodes)
    assert any("strategy.missing" in e for e in errors)


def test_valid_references_pass():
    nodes = {
        "skill.a": _skill("skill.a"),
        "strategy.a": _strategy("strategy.a", skills=["skill.a"]),
        "skill.b": _skill("skill.b", satisfied_by=["strategy.a"]),
    }
    assert check_references(nodes) == []


def test_cycle_is_caught():
    nodes = {
        "skill.a": _skill("skill.a", satisfied_by=["strategy.a"]),
        "strategy.a": _strategy("strategy.a", skills=["skill.a"]),
    }
    assert check_references(nodes) == []
    graph = build_graph(nodes)
    assert not nx.is_directed_acyclic_graph(graph)
    cycle = nx.find_cycle(graph)
    assert len(cycle) == 2


def test_acyclic_graph_passes():
    nodes = {
        "skill.a": _skill("skill.a"),
        "strategy.a": _strategy("strategy.a", skills=["skill.a"]),
        "skill.b": _skill("skill.b", satisfied_by=["strategy.a"]),
    }
    graph = build_graph(nodes)
    assert nx.is_directed_acyclic_graph(graph)


def test_id_must_match_type_prefix():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ConceptNode(id="skill.wrong_prefix", type="concept", label="x", description="")


def test_concept_requires_field_is_rejected():
    """Guardrail check: a `requires` field on a concept must fail validation,
    not be silently ignored — this is what makes the "concept-to-concept
    sequencing is out of scope for now" decision structurally real."""
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ConceptNode(
            id="concept.a", type="concept", label="a", description="", requires=[]
        )
