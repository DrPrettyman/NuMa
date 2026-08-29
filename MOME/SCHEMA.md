# MOME node schema (v1)

MOME is a typed graph over four node kinds: **Exercise**, **Skill**,
**Strategy**, **Concept**. Each node is one JSON file under
`data/{exercises,skills,strategies,concepts}/<slug>.json`. The filename is
just the node's local slug for browsability — the file's `id` field is the
canonical, dotted identifier used everywhere a node is referenced.

This is the authoring reference. See `planning/initial_research.md` for the
design rationale behind these choices.

## Common fields

Every node file has:

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | `"<type>.<snake_case_name>"`, e.g. `"skill.add_to"`. The type prefix keeps ids unambiguous wherever they're referenced from another node. |
| `type` | `concept \| skill \| strategy` | yes | |
| `label` | string | yes | Short human-readable name. |
| `description` | string | yes | May be `""` while drafting. |
| `template` | object | no | `{"param": "N", "domain": [1, 9]}`. Marks a parametrised family (e.g. `add_to(N)` for N 1..9) authored as **one** node rather than nine near-duplicate files. See "Templating" below. |
| `cgi_schema` | `join \| separate \| part_part_whole \| compare` | no | The CGI problem-type this node belongs to. Exists so that arithmetically-identical operations (e.g. "split 10 into 6+4" vs. "10-4=6") stay **distinct nodes** — they're different schemas and transfer between them isn't assumed. |
| `mastery_signal` | `correctness \| response_time` | no, default `correctness` | `response_time` marks an automaticity/fluency node — the fast, automatised version of a skill, tracked separately from "solved it via strategy." |
| `tags` | list of strings | no | Free-form + standards refs, e.g. `"ccss:K.OA.A.3"`. |
| `source` | string | no | Citation/provenance, e.g. a CGI chapter reference. |
| `status` | `draft \| reviewed \| final` | no, default `draft` | Lets partially-authored content live in the repo without failing validation. `build.py` warns (doesn't fail) on `draft` nodes. |

## Type-specific edges — this is where AND/OR semantics live

- **Exercise**: `tests: [id, ...]` — skill ids this exercise assesses
  (usually one, can be more than one). `favors_strategies: [id, ...]` —
  strategy ids this exercise's wording/format tends to reveal use of; a
  hint, not a requirement (see "Structural edges vs. diagnostic direction"
  below). `prompt` (optional string) — short free-text description/example
  of the exercise, e.g. the word-problem text. Not a templated
  problem-generation system — MOME maps the graph, it doesn't author full
  problem content (that's future, separate work, the way OATutor keeps its
  problem bank separate from its skill model). `response_format` (optional
  string) — free-text tag for how the answer is captured, e.g.
  `"numeric_answer"`, `"show_working"`, `"numeric_answer_timed"`; the other
  signal (besides wording) that hints at strategy. A timed-drill exercise
  should set `mastery_signal: "response_time"` (reusing the common field
  below, not a new one).
- **Skill** (**OR-node**): `satisfied_by: [id, ...]` — strategy ids; *any
  one* of them being mastered satisfies the skill. Empty = a leaf/base skill
  with no decomposition (directly assessable, e.g. rote perceptual
  counting) — the base case, so diagnosis doesn't need to recurse forever.
- **Strategy** (**AND-node**): `requires: {"concepts": [id, ...], "skills":
  [id, ...]}` — *all* listed concepts and skills are required. Strategies
  need concept edges, not just skill edges: e.g. "bridge through ten" needs
  the *concept* of a 10-bond, not just the *skill* of splitting a number.
- **Concept**: no edges of its own. Concept-to-concept sequencing is
  deliberately out of scope for now — deciding which concepts prerequisite
  which others needs pedagogical/developmental justification this project
  doesn't have yet, not just an intuitive-seeming edge. The schema enforces
  this (`extra="forbid"` on `ConceptNode`): a `requires` field on a concept
  file fails validation rather than silently doing nothing. See
  `planning/mome_relations_and_granularity.md` for the reasoning. A concept
  can still be *required by* a Strategy (see below) — that's a different,
  more directly justifiable claim (the strategy's own procedure invokes the
  concept), and stays in scope.

Edge direction in the compiled graph is **node → what it points at** (a
node points at the things it depends on, or — for Exercise — the things it
tests/hints at).

## Structural edges vs. diagnostic direction

Two different things share this one graph, and they run in opposite
directions:

- **Structural/compositional edges** (`requires`, `satisfied_by`) say what's
  *needed* to perform something: a Strategy requires Concepts and Skills; a
  Skill is satisfied by any one Strategy.
- **Diagnostic direction** is how evidence actually flows at runtime, and
  it's the reverse: observing correctness on an **Exercise** gives fairly
  direct evidence for the **Skill(s)** it tests; the exercise's design
  (`favors_strategies`) gives a weaker, probabilistic hint about *which*
  **Strategy** was used — this is deliberately uncertain (see the research
  doc's "strategy attribution" subproblem) rather than assumed from
  `satisfied_by`; concept-evidence continues to flow **only** through the
  inferred Strategy, never directly from a Skill or Exercise — a learner can
  pass a skill's exercises without the system having good evidence they
  grasp the concept behind whichever strategy they actually used.

## Templating

A `template` block marks a node as a parametrised family instead of
requiring one hand-authored file per value — e.g. `skill.add_to` with
`{"param": "N", "domain": [1,9]}` represents `add_to(1)` through
`add_to(9)` in a single file.

**v1 scope note:** the validator and visualiser treat a templated node as
**one node** representing the whole family — they do not expand it into
per-value instances or bind parameters across edges (e.g. binding a specific
`strategy.make_ten` invocation to the exact `skill.split_10` instance for
that addend pair). That's a known future extension needed once a runtime
mastery-tracking engine exists to track per-instance mastery; it isn't
needed yet to validate the graph's structure or author content against it.

## Automaticity and commutativity

Per the design doc, these are never assumed automatically from a single
mastered node — they're modelled as their own nodes:

- **Automaticity**: a separate skill node with `mastery_signal:
  response_time` (e.g. `skill.add_to_fluent`), distinct from the
  strategy-mediated version of the same skill.
- **Commutativity**: its own concept node (e.g.
  `concept.commutativity_of_addition`) that strategies can require — not
  inferred from mastering `a+b` alone.

## Validating

From `MOME/`:

```
pip install -r tools/requirements.txt
python tools/build.py
```

Checks run: schema conformance (via pydantic), `id` uniqueness, referential
integrity (every `requires`/`satisfied_by` id resolves to a real node), and
acyclicity (topological sort — a cycle is reported with the actual cycle
path). On success it writes `build/graph.json` (compiled node+edge list) and
`visualisation/graph.dot` (Graphviz DOT, colour-coded by node type).
