# Backward-chaining "46 + 38 = ?" to counting to ten

**Status: planning exercise only. No MOME schema or content files were
created or changed. This maps what *would* need to exist.**

## The target

`46 + 38 = ?` — a two-digit + two-digit sum under 100, where the ones
digits (6 + 8 = 14) sum to ≥10, forcing a carry/regroup. Framed as: what's
the complete node set, back to rote counting to ten, needed to diagnose and
teach this?

## Two constraints from prior decisions, worth stating up front

- **Concepts have no outgoing edges** (`ConceptNode.requires` was removed
  and is now schema-forbidden — see `planning/mome_relations_and_granularity.md`).
  So concepts never chain to other concepts; they only get pointed *at* by
  a Strategy's `requires`. The backward chain below runs entirely through
  Strategy → Skill → (Strategy/Concept) edges, with Concepts as endpoints.
- **`template` is single-parameter, flat-domain only** (`{"param": "N",
  "domain": [1..9]}`). The target exercise class needs a *constrained,
  two-parameter* domain (`a, b < 100` AND `a%10 + b%10 ≥ 10`) — the current
  schema can't express that. Flagged below as a concrete, no-longer-hypothetical
  case for the parameter-binding extension both this doc and the earlier
  granularity notes deferred as "premature."

## Layer map

Existing MOME nodes (18, all already built) are marked **existing**;
everything else is new, proposed here for the first time.

### Layer 0 — rote counting (the literal floor)

| id | type | notes |
|---|---|---|
| `skill.rote_count_to_10` | skill (leaf) | Recite 1..10 in fixed order. No decomposition — literally what you asked to bottom out at. |
| `skill.rote_count_to_20` | skill (leaf) | Recite 1..20. Needed once teen numbers enter the picture. |
| `skill.count_by_tens_to_100` | skill (leaf) | Recite "ten, twenty, thirty, ... one hundred" — the decade-word sequence. |
| `skill.rote_count_to_100` | skill (leaf) | Recite 1..100 (composes decade words + ones words). |

`concept.counting_sequence_to_10` **(existing)** stays as-is; the
declarative counterpart to the extended range is `concept.extended_counting_sequence`
below rather than editing the existing node, since "the sequence to 10 has
a fixed order" and "the sequence keeps going past 10 in a predictable
base-ten pattern" are different-enough claims to keep separate, per this
project's usual caution against assuming one milestone generalises to another.

### Layer 1 — counting objects (0–10) — **already fully built**

`concept.cardinality`, `skill.count_all`, `skill.count_on`,
`strategy.counting_all`, `strategy.counting_on` — all existing. One real
edit these need: both strategies' `requires.skills` should add
`skill.rote_count_to_10` alongside `skill.count_all`/`skill.count_on` —
counting objects presupposes reciting the sequence, and that edge is
currently implicit/unstated. (Not made here — planning only.)

### Layer 2 — single-digit addition fluency (sums to ~18) — **already fully built**

`concept.bond_to_10`, `concept.commutativity_of_addition`, `skill.split_10`,
`skill.add_to`, `skill.add_to_10`, `skill.add_to_fluent`,
`strategy.make_ten`, `strategy.derived_fact`, `strategy.retrieval`, and the
three existing exercises. Nothing new needed here — this layer already
covers ones-column addition up to 9+9=18, which is exactly what the
carrying step needs.

### Layer 3 — teen numbers as "ten and some more"

| id | type | notes |
|---|---|---|
| `concept.extended_counting_sequence` | concept | The count sequence continues past 10 in a predictable base-ten pattern (decade word + ones word). |
| `concept.teen_numbers_as_ten_plus_ones` | concept | 11–19 are "ten and N more" — notoriously the trickiest bit of English number-naming (irregular word order, unlike e.g. Chinese "ten-four"), so worth its own milestone rather than assumed. |
| `skill.decompose_teen_number` | skill (leaf, templated 11–19) | Given a number 11–19, state it as 10 + the remainder, e.g. `decompose_teen_number(14) → 10 + 4`. This is exactly the skill needed to interpret a ones-column carry result. |

### Layer 4 — reading/writing two-digit numbers & place value

| id | type | notes |
|---|---|---|
| `concept.place_value_tens_ones` | concept | A two-digit number = (tens digit)×10 + (ones digit) — this is literally the worked example already sitting in `planning/initial_research.md`'s theory table. |
| `skill.decompose_two_digit_number` | skill (leaf, templated 10–99) | 46 → 4 tens + 6 ones. |
| `skill.compose_two_digit_number` | skill (leaf, templated) | Inverse: 4 tens + 6 ones → 46. |

### Layer 5 — adding tens (the "unitizing" move)

| id | type | notes |
|---|---|---|
| `concept.unitizing_tens` | concept | A group of ten objects can be treated and counted as **one** unit ("1 ten"), the same way single objects are counted as ones. Arguably the deep cognitive move; `place_value_tens_ones` above is closer to its *notational* consequence — kept separate rather than assumed equivalent. |
| `skill.add_tens` | skill (OR-node, templated over tens-digit pairs) | Compute (a tens)+(b tens), e.g. 40+30=70. Deliberately its own skill, not assumed identical to `skill.add_to` — same "different representation, don't assume transfer" reasoning already used for split-vs-subtract. |
| `strategy.add_tens_via_unitizing` | strategy | `requires`: `concept.unitizing_tens` (gate). `uses`: `skill.add_to` — the actual mechanism is *reusing* the known single-digit fact once unitizing licenses treating "tens" as the same kind of countable thing "ones" are. Skill-level separateness and strategy-level reuse aren't in tension: the skill node tracks mastery separately (no assumed transfer), while this particular strategy's mechanism happens to lean on the ones-level fact. |

### Layer 6 & 7 — two-digit addition, without and with regrouping (the target)

| id | type | notes |
|---|---|---|
| `concept.regrouping_ten_ones_equivalence` | concept | Ten ones can be exchanged for one ten (and vice versa) — the specific insight that licenses "carrying." Kept distinct from `place_value_tens_ones`/`unitizing_tens`: a child can know what tens and ones *mean*, and even unitize tens, without yet grasping that a ten's-worth of ones can be *traded in*. |
| `skill.add_two_digit_numbers` | skill (OR-node) | Compute a+b for two-digit a,b, sum<100. One skill regardless of whether carrying is needed — same pattern as `skill.add_to` being satisfied by strategies of varying sophistication. |
| `strategy.column_addition_no_regroup` | strategy | `requires`: `concept.place_value_tens_ones`. `uses`: `decompose_two_digit_number`, `add_to` (ones), `add_tens` (tens), `compose_two_digit_number`. |
| `strategy.column_addition_with_regrouping` | strategy | `requires`: `place_value_tens_ones` + `regrouping_ten_ones_equivalence`. `uses`: `decompose_two_digit_number`, `add_to` (ones — may exceed 10), `decompose_teen_number` (interpret the ones-sum as 1 ten + remainder), `add_tens` (tens column, now including the carried ten), `compose_two_digit_number`. |

Both strategies satisfy `skill.add_two_digit_numbers`. A natural third
alternative, **not** built out here to avoid dragging subtraction into
scope unasked: `strategy.compensation` (46+38 = 46+40−2 = 84 — round up,
add, adjust back). Mechanically needs a subtraction-family skill this
project hasn't built yet; worth a future pass.

### Exercises

| id | tests | favors_strategies | notes |
|---|---|---|---|
| `exercise.two_digit_addition_with_carrying` | `skill.add_two_digit_numbers` | `strategy.column_addition_with_regrouping` | The target class. Needs the 2-parameter constrained template flagged above. |
| `exercise.two_digit_addition_no_carrying` | `skill.add_two_digit_numbers` | `strategy.column_addition_no_regroup` | Deliberately paired with the above as a **contrast exercise**: a learner who fails the carrying version but passes this one has the gap isolated to regrouping specifically, not general two-digit addition or place value. |
| `exercise.decompose_teen_number_drill` | `skill.decompose_teen_number` | — | e.g. "14 = 1 ten and __ ones" |
| `exercise.add_tens_bare_fact` | `skill.add_tens` | — | e.g. "40 + 30 = ?" |
| `exercise.decompose_two_digit_number_drill` | `skill.decompose_two_digit_number` | — | e.g. "46 = __ tens and __ ones" |

## Worked trace: what fires for "46 + 38 = ?"

```
exercise.two_digit_addition_with_carrying
  --tests--> skill.add_two_digit_numbers
    --satisfied_by--> strategy.column_addition_with_regrouping
      --requires (gate)--> concept.place_value_tens_ones
      --requires (gate)--> concept.regrouping_ten_ones_equivalence
      --uses--> skill.decompose_two_digit_number   (46→4t+6o, 38→3t+8o)
      --uses--> skill.add_to                        (ones: 6+8=14)
        --satisfied_by--> strategy.make_ten (or counting_on / derived_fact / retrieval)
          --requires--> concept.bond_to_10
          --uses--> skill.split_10, skill.add_to_10
      --uses--> skill.decompose_teen_number         (14 → 1 ten + 4 ones)
      --uses--> skill.add_tens                       (tens: 4+3+1carried=8)
        --satisfied_by--> strategy.add_tens_via_unitizing
          --requires--> concept.unitizing_tens
          --uses--> skill.add_to                     (reapplies 4+3+1, unitized)
      --uses--> skill.compose_two_digit_number       (8 tens + 4 ones → 84)
```

And every `skill.add_to` / `skill.count_all` / `skill.count_on` in that
tree ultimately bottoms out at `skill.rote_count_to_10` — literally
knowing the order of 1, 2, 3, ... 10, exactly where you asked the chain to
end.

(Note: this trace uses `requires`/`uses` as if the split proposed earlier
this session — `Strategy.requires` gated/concepts-only,
`Strategy.uses` for composed skill-steps — were already implemented. It
isn't yet; today's schema still has one `requires: {concepts, skills}`
bucket per strategy. Worth doing that split before actually authoring this
layer, since this map has *far* more skill-composition going on than the
single-digit layer did, and would hit the same cycle-risk pattern
repeatedly without it.)

## Open questions / gaps this mapping exercise surfaces

1. **The 2-parameter constrained template gap is now concrete, not
   hypothetical.** `exercise.two_digit_addition_with_carrying` genuinely
   needs `{a, b < 100, a%10 + b%10 ≥ 10}`, which is a different shape from
   every template used so far (`{"param": "N", "domain": [1..9]}`). Worth
   weighing whether to extend `template` to support a constraint
   expression, or something narrower/simpler purpose-built for this case.
2. **"Requires carrying" is a stronger relationship than
   `favors_strategies` currently models.** For single-digit facts,
   `favors_strategies` is genuinely a soft hint — any strategy *could* in
   principle be used for any instance. For two-digit addition,
   `strategy.column_addition_no_regroup` literally *cannot* produce a
   correct answer on a carrying instance (it has no step that handles a
   ones-sum ≥10) — so for this pair, the exercise-to-strategy relationship
   is closer to deterministic than probabilistic. Current schema doesn't
   distinguish "soft hint" from "hard constraint" on that field; may not
   need to yet, but it's a real gap, not just a modelling nicety.
3. **Five new place-value-adjacent concepts** (`extended_counting_sequence`,
   `teen_numbers_as_ten_plus_ones`, `unitizing_tens`, `place_value_tens_ones`,
   `regrouping_ten_ones_equivalence`) is a judgment call, not a settled
   count — each is doing distinct work in the trace above, and the
   distinctions are standard ones in base-ten/place-value education
   research (Fuson's line of work on children's multiunit-number concepts
   and multidigit addition/subtraction with regrouping is the natural
   citation here, in the same vein as the Carpenter/CGI citations already
   used elsewhere — flagging that I'm recalling the general line of
   research with reasonable confidence but haven't verified an exact
   citation, so check before using it as a `source` field on real content).
   Could be compressed if it turns out to be more granularity than useful.
4. **`skill.add_tens` reusing `skill.add_to` inside `strategy.add_tens_via_unitizing`**
   is deliberate, not an inconsistency: the *skill* nodes stay separately
   tracked (no assumed transfer from ones-facts to tens-facts), but this
   particular *strategy*'s mechanism is exactly "reuse the ones-fact once
   unitizing licenses it" — skill-level separateness and strategy-level
   reuse are different claims and don't conflict.

## Scale

18 existing nodes + roughly 23 new ones (5 concepts, 9 skills, 4
strategies, 5 exercises) ≈ 41 nodes to cover this one arc from rote
counting to two-digit addition with regrouping. Useful as a rough sense of
how fast the graph grows per "hardest exercise type" — this was one
addition arc; subtraction, multiplication, and fractions each carry a
comparable structure of their own.
