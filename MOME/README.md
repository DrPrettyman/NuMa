MOME: Map Of Mathematical Epistemology

The MOME project contains a complete map of mathematical concepts, skills and strategies with the connections between them. 

STATUS: v1 schema and validation tooling in place (see SCHEMA.md and tools/), covering four node kinds -- Exercise, Skill, Strategy, Concept -- with Exercise as the diagnostic layer (what's actually tested) and Skill/Strategy/Concept as the compositional/prerequisite layer beneath it. A first content slice covering early number sense (counting through single-digit addition strategies, plus three example exercises) is authored under data/ as a proof of concept, all marked status: draft pending review. Broader curriculum coverage is not yet started.

Run `python tools/build.py` from this directory to validate the graph and regenerate `build/graph.json` / `visualisation/graph.dot`. See SCHEMA.md for the node schema and the structural-vs-diagnostic distinction.