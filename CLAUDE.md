# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

NuMa is a (not-yet-started) personalised numeracy-learning app for children. The only thing built so far is **MOME** (`MOME/`) — "Map Of Mathematical Epistemology" — the typed prerequisite content graph the future app will run diagnosis and next-item selection on. `planning/initial_research.md` is the design rationale (literature review, competitive analysis, the theory) behind MOME's schema; when a schema choice looks arbitrary, that doc explains why.

There is no app code yet. All code in this repo is MOME's authoring/validation tooling (`MOME/tools/`), pure Python, operating on hand-authored JSON content (`MOME/data/`).

## Commands

All commands run from `MOME/`, using the venv there:

```bash
cd MOME
python3 -m venv .venv && source .venv/bin/activate   # first time only
pip install -r tools/requirements.txt

python tools/build.py          # validate all content + compile the graph
python -m pytest tools/test_build.py   # run the tooling's own tests
```

`tools/build.py` is the thing to run after any change under `MOME/data/`. It validates every node file against the schema, checks referential integrity (every id another node references must resolve) and acyclicity, and — only on success — writes `MOME/build/graph.json` (compiled node+edge list) and `MOME/visualisation/graph.dot` (Graphviz DOT). It exits non-zero on any failure and prints every error found (not just the first), including the actual cycle path when acyclicity fails. There is no lint/format tooling configured.

To run a single test: `python -m pytest tools/test_build.py::test_cycle_is_caught`.

## Architecture: MOME's content graph

Full field-by-field reference lives in `MOME/SCHEMA.md` — read it before adding fields or a new node type. The essentials:

**Four node types**, each one JSON file under `MOME/data/{exercises,skills,strategies,concepts}/<slug>.json`, modelled in `MOME/tools/schema.py` as a pydantic discriminated union (`ConceptNode` / `SkillNode` / `StrategyNode` / `ExerciseNode`, all subclassing `NodeBase`). A node's `id` field (not the filename) is its canonical identifier, namespaced `"<type>.<snake_case_name>"` and validated to match `type`.

The graph encodes two different relationships that run in **opposite directions**, layered on the same node set — this is the one thing that requires reading `SCHEMA.md` + `schema.py` together to get right, not obvious from any single file:

- **Structural/compositional edges** (what's *needed* to perform something): `Strategy.requires = {concepts: [...], skills: [...]}` is an AND-node; `Skill.satisfied_by = [strategy ids]` is an OR-node (any one strategy suffices — empty means a leaf skill with no decomposition); `Concept.requires = [concept ids]` is plain AND.
- **Diagnostic edges** (what's *observed*, going the other way): `Exercise.tests = [skill ids]` is fairly direct evidence for a skill; `Exercise.favors_strategies = [strategy ids]` is a weak, non-binding *hint* (from wording/response-format) about which strategy was likely used, not a requirement. Concept-mastery evidence deliberately flows only through the (uncertain) strategy layer, never directly from a skill or exercise — a learner can pass a skill's exercises without that being evidence they grasp the concept behind whichever strategy they happened to use.

Every node type implements `prerequisite_ids()` (used uniformly by `build.py` for both referential-integrity checking and edge construction) — add a new node type by subclassing `NodeBase` and implementing that method, following the existing four as the pattern. Compiled-graph edge direction is always **node → what it points at**.

**Templating**: a `template` field (`{"param": "N", "domain": [1,9]}`) marks a node as a parametrised family authored once instead of one file per value (e.g. `skill.add_to` stands for `add_to(1)..add_to(9)`). Current scope: the validator/visualiser treat a templated node as **one node** — no per-instance expansion or cross-template parameter binding. Don't try to encode instance-level dependencies (e.g. "this strategy instance needs that exact skill instance") at the template level; it's a known future extension gated on a runtime mastery-tracking engine that doesn't exist yet. Watch for accidental cycles this causes at the template level: e.g. a strategy that both satisfies a skill and also (at the template level) requires that same general skill as a sub-step is a self-loop `build.py` will correctly reject — the fix used elsewhere in this content (`skill.add_to` vs. the more primitive `skill.add_to_10`) is to introduce a more primitive node for the sub-step rather than reference the same family recursively.

**Other fields worth knowing**: `cgi_schema` (join/separate/part_part_whole/compare) keeps arithmetically-identical operations as distinct nodes when they're different Cognitively-Guided-Instruction problem schemas (e.g. splitting 10 vs. the equivalent subtraction fact) — transfer between them is never assumed. `mastery_signal: response_time` marks a node as an automaticity/fluency variant, assessed by speed rather than correctness alone, and is reused as-is on a timed `Exercise` rather than adding a separate field. `status: draft|reviewed|final` lets in-progress content pass validation; `build.py` only warns on `draft`, never fails on it.

**Explicitly out of scope for MOME** (lives elsewhere, later): the runtime mastery-tracking/Bayesian-network engine, strategy-attribution classifier, and next-item selection are separate ML subproblems described in `planning/initial_research.md` that *consume* MOME's compiled graph — they don't belong inside MOME itself. Likewise a real problem-authoring/templating pipeline for exercise content (MOME's `Exercise.prompt` is just a short descriptive string, not a rendering system).
