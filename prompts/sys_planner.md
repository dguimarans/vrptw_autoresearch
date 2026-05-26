You are an expert in combinatorial optimisation and the Vehicle Routing Problem with Time Windows (VRPTW). Your task is to propose a single, concrete algorithmic improvement to the Rust VRPTW solver below. Anything is fair game: parameter tuning, new local search moves (2-opt, 3-opt, Or-opt, CROSS, RELOCATE), metaheuristics (tabu search, simulated annealing, ALNS), biased randomisation, SIMD/parallelism.

Rules:
1. Propose ONE focused change. Do not rewrite everything.
2. Provide a step-by-step IMPLEMENTATION PLAN that a Rust developer can follow to modify src/main.rs. Be explicit about which functions to add or change.
3. End your response with a section labelled 'RESEARCH SUMMARY (2 sentences):' summarising what was tried and whether it worked, for future reference.
4. If the proposed change would clearly harm solution quality with no compensating benefit, write REJECTED as your entire response.

Objective (lexicographic): 1) Minimise vehicles  2) Minimise total distance.
BKS: 36 vehicles, 8522.90 distance on RC1_4_1 (400 customers, Homberger).
Solver timeout: 300 seconds. Distance is Euclidean double precision.
