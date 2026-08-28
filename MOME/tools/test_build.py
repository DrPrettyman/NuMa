"""Tests for build.py's two failure modes: dangling references and cycles.

Uses small synthetic in-memory nodes, not the real content data, so these
stay fast and don't need to change whenever content is authored/edited.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import networkx as nx

from build import build_graph, check_references
from schema import ConceptNode


def _concept(id_: str, requires: list[str] | None = None) -> ConceptNode:
    return ConceptNode(
        id=id_, type="concept", label=id_, description="", requires=requires or []
    )


def test_dangling_reference_is_caught():
    nodes = {"concept.a": _concept("concept.a", requires=["concept.missing"])}
    errors = check_references(nodes)
    assert any("concept.missing" in e for e in errors)


def test_valid_references_pass():
    nodes = {
        "concept.a": _concept("concept.a"),
        "concept.b": _concept("concept.b", requires=["concept.a"]),
    }
    assert check_references(nodes) == []


def test_cycle_is_caught():
    nodes = {
        "concept.a": _concept("concept.a", requires=["concept.b"]),
        "concept.b": _concept("concept.b", requires=["concept.a"]),
    }
    assert check_references(nodes) == []
    graph = build_graph(nodes)
    assert not nx.is_directed_acyclic_graph(graph)
    cycle = nx.find_cycle(graph)
    assert len(cycle) == 2


def test_acyclic_graph_passes():
    nodes = {
        "concept.a": _concept("concept.a"),
        "concept.b": _concept("concept.b", requires=["concept.a"]),
    }
    graph = build_graph(nodes)
    assert nx.is_directed_acyclic_graph(graph)


def test_id_must_match_type_prefix():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ConceptNode(id="skill.wrong_prefix", type="concept", label="x", description="")
