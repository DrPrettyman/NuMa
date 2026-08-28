"""Pydantic models for MOME node files.

See ../SCHEMA.md for the full field reference and design rationale.
"""
from __future__ import annotations

from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

CgiSchema = Literal["join", "separate", "part_part_whole", "compare"]
MasterySignal = Literal["correctness", "response_time"]
Status = Literal["draft", "reviewed", "final"]


class Template(BaseModel):
    """Marks a node as a parametrised family, e.g. add_to(N) for N in 1..9.

    v1 scope: the graph treats a templated node as one node representing the
    whole family — no per-value instance expansion or cross-template
    parameter binding. See SCHEMA.md.
    """

    param: str
    domain: list[int]


class NodeBase(BaseModel):
    id: str
    type: str
    label: str
    description: str
    template: Optional[Template] = None
    cgi_schema: Optional[CgiSchema] = None
    mastery_signal: MasterySignal = "correctness"
    tags: list[str] = Field(default_factory=list)
    source: Optional[str] = None
    status: Status = "draft"

    @model_validator(mode="after")
    def _id_matches_type(self) -> "NodeBase":
        prefix = f"{self.type}."
        if not self.id.startswith(prefix):
            raise ValueError(
                f"id {self.id!r} must start with {prefix!r} for type {self.type!r}"
            )
        return self

    def prerequisite_ids(self) -> list[str]:
        """Ids of every node this one directly points at (prerequisite, or —
        for Exercise — tested/hinted-at). Overridden per type."""
        raise NotImplementedError


class ConceptNode(NodeBase):
    """Declarative knowledge. Plain AND over other concepts."""

    type: Literal["concept"]
    requires: list[str] = Field(default_factory=list)

    def prerequisite_ids(self) -> list[str]:
        return list(self.requires)


class SkillNode(NodeBase):
    """Procedural, directly assessable. OR-node: any one strategy suffices.

    Empty satisfied_by = a leaf/base skill with no decomposition.
    """

    type: Literal["skill"]
    satisfied_by: list[str] = Field(default_factory=list)

    def prerequisite_ids(self) -> list[str]:
        return list(self.satisfied_by)


class StrategyRequires(BaseModel):
    concepts: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


class StrategyNode(NodeBase):
    """Composite procedure. AND-node: all listed concepts and skills required."""

    type: Literal["strategy"]
    requires: StrategyRequires = Field(default_factory=StrategyRequires)

    def prerequisite_ids(self) -> list[str]:
        return [*self.requires.concepts, *self.requires.skills]


class ExerciseNode(NodeBase):
    """A concrete, presentable test item. Assesses one or more skills.

    Correctness on an exercise is fairly direct evidence for the skill(s) it
    tests, but only a weak, inferred hint at which strategy was used —
    favors_strategies records that hint (wording/format), it doesn't require
    it. See SCHEMA.md, "Structural edges vs. diagnostic direction".
    """

    type: Literal["exercise"]
    tests: list[str] = Field(default_factory=list)
    favors_strategies: list[str] = Field(default_factory=list)
    prompt: Optional[str] = None
    response_format: Optional[str] = None

    def prerequisite_ids(self) -> list[str]:
        return [*self.tests, *self.favors_strategies]


Node = Annotated[
    Union[ConceptNode, SkillNode, StrategyNode, ExerciseNode],
    Field(discriminator="type"),
]
