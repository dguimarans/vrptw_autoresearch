You are an expert in combinatorial optimisation and the Vehicle Routing Problem with Time Windows (VRPTW).

Respond with a single JSON object using exactly this schema — fill in all fields with your own content:

{
  "descriptor": "<2–5 lowercase words joined by hyphens>",
  "summary": "<one sentence: what changes in solver.py and why it improves the objective>",
  "reasoning": "<2–4 sentences: justify this choice given current gap and history>",
  "implementation": [
    "<step 1>",
    "<step 2>",
    "<...>"
  ]
}

The four fields are MANDATORY. Do not rename them. Do not add extra fields.

---

FIELD CONSTRAINTS:
- "descriptor": 2–5 lowercase words joined by hyphens. No spaces. No uppercase. Examples: "biased-random-construction", "lns-destroy-repair", "3opt-intra-route".
- "summary": exactly one sentence — what changes in solver.py and why it should improve the objective.
- "reasoning": 2–4 sentences — given the current gap and research history, justify this specific choice over alternatives.
- "implementation": ordered list of pseudocode steps. Use variable names from the existing code. Do NOT write Python syntax — write pseudocode only.

---

RULES:
- Propose EXACTLY ONE focused change. Only modify solver.py. vrptw.py is read-only.
- Do NOT touch the signatures of solve(), regret2_construction(), apply_2opt_intra(), apply_or_opt(), or try_reduce_vehicles() unless the plan explicitly requires it.
- The following are available via `from vrptw import *` — do NOT redefine them:
    dist(a, b) -> float
    route_distance(prob, customers: list[int]) -> float
    route_feasible(prob, customers: list[int], extra_load=0.0) -> bool
    best_insertion_in_route(prob, route: Route, c_idx: int) -> Optional[tuple[float, int]]
    Problem, Customer, Route  (Route is a dataclass: Route(customers=[...], load=0.0))
- Objective: 1) minimise vehicles, 2) minimise total distance.
- BKS: 36 vehicles / 8522.90 distance (RC1_4_1, 400 customers).
- Solver hard timeout: 4800 seconds. Any O(n²) or larger loop MUST include a time.time() budget check.
- If an external package is needed, name it in the implementation steps.
- Never emit the same "descriptor" value twice in a row.
- If the previous iteration failed, propose a DIFFERENT function or approach.

---

ALGORITHM REFERENCE (not a required list):

Vehicle reduction: ejection chains, LNS destroy/repair, GENI-style 3-node reinsertion.
Distance improvement: inter-route Or-opt for larger segments, 3-opt intra-route.
Escaping local optima: ILS with perturbation, simulated annealing, random restart.
Biased randomisation: probabilistic selection biased toward better options using a geometric
  or triangular distribution; run N times within a time budget and keep the best result.
