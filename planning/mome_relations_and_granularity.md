# MOME relations & granularity — design notes

**Status: brainstorm only. Nothing in this note has been implemented — no
schema or content changes were made. Captures an in-progress design
discussion for when we're ready to act on it.**

## How this started

Looking again at `concept.bond_to_10` (a templated concept, `requires:
["concept.cardinality"]`) alongside the cycles we hit twice while authoring
strategies (`make_ten` and `derived_fact` both tried to reference
`skill.add_to` — the general family they were partly helping to satisfy —
and one of those edges had to be deleted outright to pass validation). That
prompted two questions: is `Concept.requires` even the right relation
between concepts, and more importantly, what is the *real* relationship
between a general node (`skill.add_to`) and a fully concrete instance of it
("1+2=3")?

## Three separable relations, not one `requires`

The discussion converged on there being (at least) three genuinely
different relations that the current schema's single `requires` field
conflates:

1. **Prerequisite / gate** — X must be independently understood before Y is
   even attempted. This is what `Strategy.requires.concepts` models (e.g.
   `make_ten` needs the *concept* of `bond_to_10` before the decomposition
   makes sense). `Concept.requires` used to model the concept-to-concept
   case too, until the discussion below concluded that call isn't ours to
   make yet — see "Does concept→concept requires make sense?". This is the
   relation the acyclicity check exists for — diagnosis walks gate edges to
   find the frontier, and that walk must terminate.

2. **Composition / uses** — Y is literally executed as a step inside X,
   not gated beforehand. `derived_fact` "using an already-known fact" is
   this, not a gate. This relation doesn't need to be acyclic, because
   diagnosis never needs to walk it to find the frontier — it only matters
   for explaining *how* a strategy works, not *whether* a learner is ready
   for it. (This was proposed earlier this session as a `requires`/`uses`
   split on `Strategy` — still on the table, not decided, see below.)

3. **Generalization / instance-of** (the new idea this note is mainly
   about) — X is one concrete instantiation of general family Y. This is
   what `template` already gestures at (`skill.add_to` standing in for
   `add_to(1)..add_to(9)`), but v1 deliberately treats the whole family as
   one flat node. The discussion below is about why that's not just an
   authoring convenience we can defer indefinitely — it's load-bearing for
   how mastery actually should work.

## Does concept→concept `requires` make sense?

First pass at this conflated two different senses of "requires" and needs
correcting:

1. **Definitional/formal necessity** — you can't even *state* "a+b=b+a"
   until addition already exists as a defined operation. True, but this is
   a claim about the formal structure of mathematics as a discipline,
   independent of any learner's mind.
2. **Psychological/readiness necessity** — a learner can't grasp or use
   concept X without already possessing concept Y in their own
   understanding. This is what a `Concept.requires` edge in MOME actually
   needs to mean, since the entire point of the edge is gating what a
   *learner* is ready for.

These don't obviously coincide, and the original examples ("commutativity
requires addition," "prime number requires factor") were both purely
formal/definitional — legitimate claims about mathematical language that
don't automatically transfer to claims about cognitive development. CGI
research (already this project's grounding literature) documents children
noticing and using commutativity through concrete strategy experience as
*part of* how a general concept of addition gets built up, not strictly
after it's already formed — so the developmental order plausibly doesn't
match the formal/definitional order at all here.

**Revised answer:** concept→concept `requires` is legitimate in principle
and still distinct from strategy→concept `requires`, but each edge needs a
*pedagogical* justification — ideally evidence from developmental/CGI
literature about what typically needs to be in place before something
becomes graspable — not a formal/definitional one. "You can't define X
without Y" is not, by itself, evidence for a MOME requires edge. Worth
re-checking the existing requires edges in the actual data
(`concept.bond_to_10 requires concept.cardinality`,
`concept.cardinality requires concept.counting_sequence_to_10`) against
this stricter standard rather than assuming they're fine because they
seemed intuitive at authoring time — they may well hold up, but "seemed
intuitive" isn't the same evidence as "developmental literature backs this
ordering."

**Decided:** concept-to-concept sequencing is out of scope for this project
right now — we don't have the developmental/CGI evidence in hand to make
these calls responsibly, so we're not making them. Implemented, not just
noted: `ConceptNode` no longer has a `requires` field at all (removed from
`MOME/tools/schema.py`, not merely left empty), with
`model_config = ConfigDict(extra="forbid")` so the field can't quietly
reappear in a data file without deliberately revisiting this decision in
code first. The two edges that existed
(`concept.bond_to_10 → concept.cardinality`,
`concept.cardinality → concept.counting_sequence_to_10`) have been removed
from the data. A concept can still be *required by* a Strategy — that's the
separate, more directly justifiable claim (the strategy's own procedure
invokes the concept) — and that edge is unaffected.

The instance/generalization idea below adds a *third* thing that
`bond_to_10 requires cardinality` is definitely **not** an instance of —
`cardinality` isn't a more-general version of `bond_to_10`, they're
unrelated ideas. So this stays a clean, separate case; the new granularity
axis doesn't reopen it.

## The core idea: evidence lands on the most specific node; general nodes' mastery is an aggregate

Worked example, exactly as raised: a learner answers the exercise
**"1 + 2 = ?"** correctly.

- If they used **counting-on**: the direct evidence is for the very
  specific instance *"counts on 2 from 1"* — not the general
  `strategy.counting_on` node. Being able to count on 1→2→3 says nothing
  about counting on from 47 by 8; counting-on has its own difficulty curve
  by magnitude, so it's *itself* a family with instances, and each
  instance is its own evidence point.
- If they used **retrieval**: the direct evidence is for the very specific
  fact *"knows 1+2=3"* — not the general `skill.add_to` family, and
  certainly not some larger aggregate like "addition summing to under 10."
  Knowing one fact by heart doesn't imply the others are memorised too.

Generalizing: **evidence from an exercise always lands on the most
specific node it corresponds to. A general/aggregate node's mastery is
never observed directly — it's computed as some aggregation over the
mastery of its more specific sub-instances.**

I think this is a reasonable and actually important idea, not just a nice
refinement — it's consistent with how Knowledge Space Theory (the
ALEKS-underlying theory the research doc already cites) treats a knowledge
state as defined over the *finest*-grained items, with anything coarser
being a derived summary. It also slots directly into the "mastery
estimation" subproblem the research doc already scoped as a separate piece
of future ML work — the aggregation function *is* that model, or at least
the interpretable-Bayesian-network version of it the doc already leans
towards (ANDES-style CPTs, not a GNN).

## Open questions this raises (not resolved here)

- **Aggregation function.** Plain average? Weakest-link (unmastered until
  *all* instances are)? Weighted by recency/frequency? A proper
  Beta-Binomial/Bayesian pooling model? These have real pedagogical
  differences — weakest-link would keep "bonds to 10" unmastered from one
  never-attempted bond even with 8/9 solid, which is probably too harsh;
  a flat average might be too forgiving. Worth treating as part of the
  mastery-estimation ML subproblem rather than deciding arbitrarily now.
- **Is generalization flat or a real hierarchy?** The example already
  implies more than two levels: *"1+2=3 via retrieval"* (fully concrete) →
  *"add_to(2)"* (all N+2 facts) → *"add_to"* in general (aggregate of
  aggregates) → arguably a broader strand above that. Probably a tree/DAG
  of granularity, not a flat instance/family split.
- **This is the same gap as the deferred "per-instance parameter binding"
  feature** already flagged in `MOME/SCHEMA.md`'s v1 scope note (originally
  motivated just by wanting to fix template-level cycles cleanly). This
  discussion reframes that feature as core infrastructure the whole
  diagnostic purpose of MOME depends on, not a nice-to-have edge case for
  later. Worth weighing that when we next reconsider deferring it.
- **How do templated Exercises interact with this?** An exercise can
  itself be templated (e.g. "N + 5 = ?" for N 1..9). Does a specific
  exercise instance's evidence bind to the matching specific instance of
  the skill/strategy it tests automatically, or does that need its own
  explicit binding syntax? Unresolved.
- **Does this replace the earlier `requires`/`uses` split idea, or is it
  orthogonal?** Orthogonal, as far as this discussion got — gate-vs-composed
  (axis 1 vs 2 above) is about *readiness*, generalization (axis 3) is
  about *specificity*. A strategy instance could plausibly need both: a
  gated concept prerequisite, non-gated composed skill steps, and itself be
  one instance of a more general strategy family. Not fully worked through.

## Where this leaves the earlier `requires`/`uses`/`realizes` ideas

Still on the table from earlier in this session, still not decided:

- Split `Strategy.requires` (concepts, gated) from a new `Strategy.uses`
  (skills, composed-not-gated) — would have properly fixed both cycles we
  hit, instead of one being fixed by inventing `skill.add_to_10` and the
  other by deleting the edge.
- Single-source the Skill↔Strategy link via `Strategy.realizes` instead of
  hand-maintaining `Skill.satisfied_by` on both sides — catches orphaned
  strategies for free.
- Full instance-level parameter binding — now looking less like a
  deferred nicety and more like the actual foundation the granularity idea
  above needs to work at all.

## Not decided — next steps when we're ready

1. Settle whether granularity is a first-class axis in the schema (i.e.
   real instance nodes/edges) or something computed at build/runtime from
   a template + binding syntax.
2. Pick an aggregation function (or explicitly punt it to the future
   Bayesian mastery model, treating MOME itself as only defining *which*
   nodes aggregate into which, not *how*).
3. Decide whether to revisit the `requires`/`uses`/`realizes` split at the
   same time, since a schema change touches the same files either way.
