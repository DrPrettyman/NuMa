#!/usr/bin/env python3
"""Validate and compile the MOME content graph.

Usage (from MOME/):
    python tools/build.py

Loads every data/**/*.json node file, validates it against the schema
(schema.py / SCHEMA.md), checks referential integrity and acyclicity, then
writes a compiled build/graph.json and a visualisation/graph.dot.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import networkx as nx
from pydantic import TypeAdapter, ValidationError

from schema import Node

MOME_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = MOME_ROOT / "data"
BUILD_DIR = MOME_ROOT / "build"
VIS_DIR = MOME_ROOT / "visualisation"

NODE_ADAPTER = TypeAdapter(Node)

TYPE_COLORS = {
    "concept": "#8ecae6",
    "skill": "#ffb703",
    "strategy": "#fb8500",
    "exercise": "#219ebc",
}


def load_nodes() -> tuple[dict[str, Node], list[str]]:
    """Parse every data/**/*.json file. Returns (id -> node, error messages)."""
    nodes: dict[str, Node] = {}
    errors: list[str] = []
    for path in sorted(DATA_DIR.glob("**/*.json")):
        rel = path.relative_to(MOME_ROOT)
        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: invalid JSON ({exc})")
            continue
        try:
            node = NODE_ADAPTER.validate_python(raw)
        except ValidationError as exc:
            errors.append(f"{rel}: {exc}")
            continue
        if node.id in nodes:
            errors.append(f"{rel}: duplicate id {node.id!r} (already defined elsewhere)")
            continue
        nodes[node.id] = node
    return nodes, errors


def check_references(nodes: dict[str, Node]) -> list[str]:
    errors: list[str] = []
    for node in nodes.values():
        for prereq_id in node.prerequisite_ids():
            if prereq_id not in nodes:
                errors.append(f"{node.id}: references unknown id {prereq_id!r}")
    return errors


def build_graph(nodes: dict[str, Node]) -> nx.DiGraph:
    """Edge direction: node -> its prerequisite."""
    graph = nx.DiGraph()
    for node in nodes.values():
        graph.add_node(node.id, type=node.type, label=node.label, status=node.status)
    for node in nodes.values():
        for prereq_id in node.prerequisite_ids():
            graph.add_edge(node.id, prereq_id)
    return graph


def write_compiled_graph(nodes: dict[str, Node], graph: nx.DiGraph) -> None:
    BUILD_DIR.mkdir(exist_ok=True)
    payload = {
        "nodes": [
            {"id": node.id, "type": node.type, "label": node.label, "status": node.status}
            for node in nodes.values()
        ],
        "edges": [{"from": u, "to": v} for u, v in graph.edges()],
    }
    (BUILD_DIR / "graph.json").write_text(json.dumps(payload, indent=2) + "\n")


def write_dot(graph: nx.DiGraph) -> None:
    VIS_DIR.mkdir(exist_ok=True)
    lines = ["digraph MOME {", '  rankdir="LR";']
    for node_id, data in graph.nodes(data=True):
        color = TYPE_COLORS.get(data.get("type"), "#cccccc")
        style = "dashed" if data.get("status") == "draft" else "solid"
        label = f"{data.get('label', node_id)}\\n({data.get('type')})".replace('"', '\\"')
        lines.append(
            f'  "{node_id}" [label="{label}", style="filled,{style}", fillcolor="{color}"];'
        )
    for u, v in graph.edges():
        lines.append(f'  "{u}" -> "{v}";')
    lines.append("}")
    (VIS_DIR / "graph.dot").write_text("\n".join(lines) + "\n")


def main() -> int:
    nodes, errors = load_nodes()
    errors += check_references(nodes)
    if errors:
        print(f"FAILED — {len(errors)} error(s):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    graph = build_graph(nodes)
    if not nx.is_directed_acyclic_graph(graph):
        cycle = nx.find_cycle(graph)
        path = " -> ".join(u for u, _ in cycle) + f" -> {cycle[0][0]}"
        print(f"FAILED — cycle detected: {path}", file=sys.stderr)
        return 1

    write_compiled_graph(nodes, graph)
    write_dot(graph)

    by_type = {"concept": 0, "skill": 0, "strategy": 0, "exercise": 0}
    draft_count = 0
    for node in nodes.values():
        by_type[node.type] += 1
        if node.status == "draft":
            draft_count += 1

    print(
        f"OK — {len(nodes)} nodes "
        f"({by_type['concept']} concepts, {by_type['skill']} skills, "
        f"{by_type['strategy']} strategies, {by_type['exercise']} exercises), "
        f"{graph.number_of_edges()} edges."
    )
    if draft_count:
        print(f"  note: {draft_count} node(s) still marked status=draft.")
    print(f"  wrote {BUILD_DIR / 'graph.json'}")
    print(f"  wrote {VIS_DIR / 'graph.dot'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
