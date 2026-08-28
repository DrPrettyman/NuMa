# Kids' Maths App — Research Notes

Notes from an exploratory conversation on building a personalised maths-learning app for children, structured around a typed concept/skill/strategy prerequisite graph.

---

## Literature Review

### Foundational theory

- **Doignon, J.-P. & Falmagne, J.-C. (1985).** *Spaces for the assessment of knowledge.* Formalised **Knowledge Space Theory** — the mathematical model underlying ALEKS. Represents a learner's plausible knowledge as a partial order over sets of masterable items, not a simple prerequisite list.
- **Gagné, R. (1968).** Learning hierarchies — the older educational-psychology precursor to prerequisite graphs.
- **Anderson, J.R.** — **ACT-R** cognitive architecture (production-rule model of skill acquisition). This is the cognitive architecture underlying Carnegie Learning's Cognitive Tutor / MATHia lineage.

### Cognitively Guided Instruction (CGI) — the source for strategy/problem-type granularity

- **Carpenter, T., Fennema, E., Franke, M., Levi, L. & Empson, S. — *Children's Mathematics: Cognitively Guided Instruction*** (Heinemann, 2nd ed. 2014). The core text: full problem-type taxonomy (**Join / Separate / Part-Part-Whole / Compare**, each split by which quantity is unknown) plus the strategy-development progression (counting-all → counting-on → derived facts → retrieval) for single-digit addition/subtraction.
- **Empson, S. & Levi, L. (2011). *Extending Children's Mathematics.*** Same CGI framework applied to fractions and decimals.
- **Carpenter, T., Franke, M. & Levi, L. (2003). *Thinking Mathematically.*** CGI applied to early algebraic reasoning (relational thinking, equality).
- **Carpenter, T., Fennema, E., Franke, M. et al. (1988). "A Study of Cognitively Guided Instruction," *Journal for Research in Mathematics Education*.** Primary-source paper with the original strategy classification table.
- Tom Carpenter died in 2018; Fennema, Franke, Levi and Empson continue the line of research. No single machine-readable CGI ontology exists — it has to be extracted from the texts by hand.

### Knowledge tracing / mastery modelling

- **Corbett, A. & Anderson, J. (1995).** Bayesian Knowledge Tracing (BKT) — the classic HMM formulation: four parameters per skill (P(known), P(learn), P(guess), P(slip)), updated after each attempt.
- **pyBKT** — standalone Python BKT implementation from Zachary Pardos's lab (CAHLR, UC Berkeley): [github.com/CAHLR/pyBKT](https://github.com/CAHLR/pyBKT)
- **Nakagawa, H., Iwasawa, Y. & Matsuo, Y. (2019). "Graph-based Knowledge Tracing: Modeling Student Proficiency Using Graph Neural Network."** *IEEE/WIC/ACM Int'l Conf. on Web Intelligence*, pp. 156–163. Models the KC graph explicitly and propagates proficiency estimates via GCN message-passing — directly relevant prior art for a graph-structured mastery model.
- Survey note (from *A Survey of Knowledge Tracing: Models, Variants, and Applications*, [arxiv.org/pdf/2105.15106](https://arxiv.org/pdf/2105.15106)): many deep knowledge-tracing (DLKT) approaches optimise next-answer prediction accuracy at the expense of interpretable tracing — mastery represented only as opaque network weights, hard for educators to act on. Relevant caution against jumping straight to a GNN/deep model before there's enough data and before interpretability is designed in.

### Bayesian-network student models (historical ITS)

- **Conati, C., Gertner, A., VanLehn, K. & Druzdzel, M. (1997). "On-line Student Modeling for Coached Problem Solving Using Bayesian Networks."** *UM97*. [Paper (academia.edu)](https://www.academia.edu/12404465/On_Line_Student_Modeling_for_Coached_Problem_Solving_Using_Bayesian_Networks) — the ANDES physics tutor's student model. Each problem's steps form a Bayes net; strategy recognition, action prediction, and long-term mastery assessment all come out of the same network.
- **VanLehn, K., Van De Sande, B., Shelby, R. & Gershman, S. (2010). "The Andes Physics Tutoring System: An Experiment in Freedom."**
- Review context: [arxiv.org/pdf/1302.7081](https://arxiv.org/pdf/1302.7081) and [arxiv.org/pdf/1812.09628](https://arxiv.org/pdf/1812.09628) — summarise ANDES's Bayes net as doing (1) strategy selection, (2) action prediction, (3) long-term knowledge assessment, and note that the network adapts its probabilities as different students take different problem-solving approaches, then uses this to predict the best strategy for new problems for that student.

### Open-source adaptive tutoring system

- **Pardos, Z., Tang, M., Anastasopoulos, I., Sheel, S. & Zhang, E. (2023). "OATutor: An Open-source Adaptive Tutoring System and Curated Content Library for Learning Sciences Research."** *CHI '23*. DOI: [10.1145/3544548.3581574](https://doi.org/10.1145/3544548.3581574)
- Follow-on: **OATutor-GenAI** — active extension toward Pre-K–8 content using LLMs to speed up authoring, explicitly framed as an access/equity alternative to ALEKS (ALEKS works but is costly, limiting equitable access for under-resourced districts/families).

### CMU DataShop / Knowledge Component research

- **PSLC DataShop** — [pslcdatashop.web.cmu.edu](https://pslcdatashop.web.cmu.edu) — Carnegie Mellon's open repository of tutoring-system interaction data, tagged with "KC models." Origin: PSLC founded 2004 (CMU + Pitt, NSF-funded); DataShop released 2005; became the world's largest open repository of tutoring interaction data.
- **Koedinger, K. et al.** — origin of the term **Knowledge Component**: "an acquired unit of cognitive function or structure that can be inferred from performance on a set of related tasks" — deliberately theory-neutral (could be a fact, concept, procedure, or strategy).
- KC-model validation is treated as an empirical question — DataShop tooling lets researchers compare competing decompositions of the same content against real learning-curve data (does a finer split actually predict performance better, or is it noise).

---

## Theory

### The three-layer structure we converged on

| Layer | Nature | Example |
|---|---|---|
| **Concept** | Declarative knowledge (a fact/relationship exists) | "10-bond: 6+4=10"; place value (a 2-digit number = tens×10 + ones) |
| **Skill** | Procedural, single-step, directly assessable | `split_10(7)→3`; `add_to(N)`; `subtract_from(N)` |
| **Strategy** | A named procedure composing several skills/concepts to solve a problem outside their own range | "bridge through ten" for 8+5; "split ones and tens, add separately" for 46+17 |

### Graph semantics: an AND-OR graph

- **Skill nodes are OR-nodes** — satisfied by *any one* of several possible strategies.
- **Strategy nodes are AND-nodes** — require *all* of their constituent concepts and sub-skills.
- This is the same structural pattern as HTN planning and ACT-R production rules; ANDES's Bayes net (above) is the closest working prior art — its CPTs can be built to encode exactly this AND/OR logic (noisy-AND for strategies, noisy-OR for skills).
- The graph must be **acyclic** (well-founded) — enforce with a topological sort at content-ingestion time, reject on cycle, since diagnosis logic will infinite-loop otherwise.

### Key distinctions identified during design

1. **Split vs. subtract are not the same node**, even where numerically identical (`split_10(7)→3` vs `10-3=7`). They correspond to different CGI problem schemas:
   - **Part-Part-Whole** (split) — a quantity conceived as two parts co-existing; feeds forward into compositional strategies (bridging-through-ten, regrouping, later fraction partitioning).
   - **Separate** (subtract) — an active removal event; feeds forward into take-away and comparison word problems, the standard subtraction algorithm.
   - **Join** (add) — a third distinct schema, a quantity growing by addition of a new amount.
   - No mastery edge should be assumed between them — transfer must be tested, not assumed.
2. **Commutativity is its own conceptual milestone**, not automatic. A child fluent in `1+2` may not yet have generalised to `2+1`; if this matters for your mastery model, it needs its own node rather than being assumed.
3. **Mastery has (at least) two states**: solved-via-strategy (slow, effortful) vs. automatised/fact-retrieval (fast, direct). Response time is the signal that distinguishes them — correctness alone conflates a child still running "make ten" every time with one who just knows the fact.
4. **Strategy nodes need concept edges, not just skill edges.** E.g. "split ones and tens, add separately" for 46+17 needs the **concept** of place-value decomposition as a prerequisite, in addition to the two sub-skills — otherwise a child could pass both sub-skills in isolation and still not see why the decomposition is valid for this problem.
5. **Templating over hand-duplication**: skills should be defined as templates parametrised over N (`split(N)`, `add_to(N)`, `subtract_from(N)`) rather than one hand-authored node per N — keeps the schema small as it scales to bonds-to-20, times tables, etc.

### Granularity: how fine is "fine enough"?

Public/open taxonomies are much coarser than what's needed for this project:

| Source | Approx. granularity |
|---|---|
| Common Core (CCSS) | ~385 KCs, whole K–12 |
| ASSISTments dataset tags | ~100–265 skills, whole K–12 (e.g. "Solve Unit Rate Problems" = one skill) |
| MATHia / Cognitive Tutor (Carnegie Learning) | 2,000+ KCs — finest published, but proprietary and weighted toward algebra/geometry, not early number sense |

None of these reach strategy-level granularity ("making ten from 7 needs 3 more"). That level of resolution is a different axis (**strategy**, not **skill/standard**) and its natural source is the CGI literature above, not an importable dataset.

### Next-item selection: the "moving with the child" part

- Framed as picking from the **frontier**: nodes whose AND-prerequisites are all mastered but the node itself isn't yet — a computable version of Vygotsky's Zone of Proximal Development.
- This is exactly what ALEKS's Knowledge Space Theory engine does: picks the next question to maximise information about the outer fringe of the learner's knowledge state, not randomly or by fixed sequence.
- v1 approach: rank eligible frontier nodes by mastery-probability closest to 0.5 (most uncertain → most informative), sample among the top few (e.g. Thompson sampling) to avoid over-drilling one node. Full RL/bandit optimisation over long-term retention is a viable later upgrade, but needs student volume not available at launch.

---

## Software on the Market

| Product | Mechanism | Strengths | Weaknesses / notes |
|---|---|---|---|
| **[ALEKS](https://www.aleks.com)** | Knowledge Space Theory — rigorous diagnostic placement via partial-order knowledge states | Most theoretically rigorous adaptive placement/diagnostic engine on the market | Dry UI, not built for younger kids |
| **[DreamBox](https://www.dreambox.com)** | Real-time adaptive lesson sequencing driven by mastery signals | Actually *teaches* concepts, not just drills; strong gap-filling | Subscription; K–8 only |
| **[IXL](https://www.ixl.com)** | Skill-level adaptation from accuracy/mastery signal, granular standards-mapped analytics | Best-in-class diagnostics/reporting | Leans practice-drill more than instruction |
| **[Zearn](https://www.zearn.org)** | Standards-aligned video instruction, free | Free, full K–8 curriculum | Less adaptive — closer to linear sequencing |
| **[Khan Academy](https://www.khanacademy.org)** (+ Khanmigo) | Mastery-based practice + LLM conversational tutor layer | Free, huge content library, natural-language tutoring | Adaptivity shallower than ALEKS/DreamBox |
| **[Prodigy](https://www.prodigygame.com)** | Gamified RPG wrapper over practice questions | Strong engagement/motivation | Assumes prior mastery — practice, not instruction |
| **[ST Math](https://www.stmath.com)** | Visual, non-verbal problem-solving with per-strand mastery indicators | Strong conceptual/visual grounding | Supplement, not a full course |
| **Carnegie Learning [MATHia](https://www.carnegielearning.com)** / Cognitive Tutor | ACT-R production-rule model; step-level hinting tied to ~2,000+ knowledge components | Finest-grained published KC taxonomy; step-level intervention | Closed/commercial; school-market focused; weighted toward algebra/geometry |
| **Squirrel AI** (China) | Large-scale AI-adaptive tutoring | Biggest AI-adaptive deployment at scale | Limited English-language documentation of internals |
| **[OATutor](https://github.com/CAHLR/OATutor)** (open source) | ReactJS frontend, BKT mastery model, deployable serverless on GitHub Pages | Fully open source, real working reference implementation of the KT/ITS loop | Content ([OATutor-Content](https://github.com/CAHLR/OATutor-Content)) is OpenStax-derived (stats/algebra, CC BY 4.0), not K–2 arithmetic; simpler than a full prerequisite graph (see below) |

### OATutor — architecture detail (from direct inspection of the repo)

- **`skillModel.json`** ([raw file](https://raw.githubusercontent.com/CAHLR/OATutor-Content/main/skillModel.json)) is a **flat Q-matrix**: a dict mapping problem-step ID → list of skill tags. No prerequisite edges, no hierarchy, no typed relations — e.g.:
  ```json
  "ada72c8boot2f": ["the_bootstrap"],
  "a1f1064rev1a": ["review"]
  ```
- **`coursePlans.json`** encodes ordering as a **hand-sequenced lesson list**, each gated by a target BKT mastery probability per skill (e.g. `"learningObjectives": {"table_methods_and_conditionals_with_iteration": 0.85}`). Prerequisite logic lives in the human-authored lesson order, not in any encoded graph.
- BKT models each skill's mastery **independently** — no cross-skill transfer, no shared parameters by default.
- **Conclusion: OATutor's own data model is simpler than the typed concept/skill/strategy digraph designed in this conversation.** It's a good reference for the mastery-tracking plumbing (BKT update math) and for its spreadsheet-based, non-engineer-friendly content-authoring pipeline — not a template for graph representation.
- Content-authoring pattern worth reusing: problems are templated (placeholders generate many instances from one authored problem) and authored via linked Google Spreadsheets rather than a bespoke CMS — cheap to replicate and lets non-engineers (e.g. a tutor) contribute content directly.

### Misconception / diagnostic-question datasets

- **Eedi** — distractor-level misconception annotations (which wrong answer implies which specific flawed reasoning). Closer in *kind* to strategy-level granularity than skill taxonomies, but labels are still described in the literature as fairly general, not deeply fine-grained.
- **ASSISTments** — public KT research dataset, ~100–265 skill tags total across K–12. [sites.google.com/view/assistmentsdatamining](https://sites.google.com/view/assistmentsdatamining)

---

## Plan (Our Own Plan)

### Content graph

1. **Three typed node kinds**: Concept (declarative), Skill (procedural, directly assessable, OR-node over strategies), Strategy (composite procedure, AND-node over concepts + sub-skills).
2. **Bootstrap the backbone from an existing standards taxonomy** (Common Core or equivalent national curriculum) rather than authoring a full K-12 graph from scratch — a few hundred nodes for sequencing/placement.
3. **Author a fine-grained strategy layer only where it changes the intervention** — early number sense (counting strategies, making ten, place value), fraction operations, multi-digit arithmetic — using the CGI problem-type taxonomy as the source, not uniformly across the whole curriculum.
4. **Template skills over a parameter N** rather than hand-duplicating per instance.
5. **Enforce acyclicity** at ingestion (topological sort; reject cycles).
6. **Model representation-dependent duplicates explicitly** (split vs. subtract vs. add as distinct Join/Separate/Part-Part-Whole schema nodes even when arithmetically identical) rather than collapsing them.
7. Track **commutativity** and **automaticity/fluency** as first-class, separately-assessed nodes/states rather than assuming they follow automatically from single-instance mastery.

### ML — split into three separate subproblems

1. **Mastery estimation**: interpretable Bayesian network over the typed graph, CPTs encoding AND/OR semantics directly (ANDES-style) — v1, not a GNN. Defer graph-neural approaches (e.g. GKT) until there's enough logged usage data to justify them, and be wary of the interpretability trade-off deep KT models carry.
2. **Strategy attribution**: separate classification problem — infer which strategy a child used from behavioural signal (response time, intermediate working, error type). v1: rule-based; upgrade to a learned classifier once traces are logged.
3. **Next-item selection**: frontier-based (ZPD-style) selection — rank eligible nodes (prerequisites met, node not yet mastered) by uncertainty, sample rather than always picking the top result.

### Data/logging

- Log every interaction with enough granularity to revisit modelling decisions later: which strategy was used, response time, correctness, hints used, per-attempt mastery-probability estimate.
- Treat the KC/graph decomposition as a hypothesis to validate against data over time (DataShop's approach to comparing competing KC models), not a fixed ontology authored once and left alone.

### Differentiation vs. the market

- Most competitors are strong on adaptivity (ALEKS, DreamBox, IXL) *or* strong on natural-language tutoring (Khan/Khanmigo) — not both, and none feel personalised in tone/pacing to an individual young child the way a parent/tutor would.
- Domain-expert-authored strategy layer (grounded in CGI, informed by direct tutoring experience) is the plausible edge over systems built primarily by curriculum/psychometrics teams without that granularity.