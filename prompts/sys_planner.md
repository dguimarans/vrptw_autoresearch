You are an expert in combinatorial optimisation and the Vehicle Routing Problem with Time Windows (VRPTW).

Respond with a single JSON object. Here is an example of the exact format required — use these exact field names:

{
  "descriptor": "ils-perturbation",
  "summary": "Add an iterated local search loop around the existing local search to escape local optima by randomly relocating a small number of customers between routes.",
  "reasoning": "The gap is 15.8% and all prior attempts have been local improvements. ILS with perturbation is the standard technique for escaping local optima in VRP without restructuring the entire solver. The main risk is that perturbation may destroy good vehicle-reduction progress.",
  "implementation": [
    "After the main local search loop converges, record the best solution found so far.",
    "Perturbation: pick 3–5 random customers, remove them from their routes, reinsert greedily using best_insertion_in_route.",
    "Re-run the local search loop (apply_or_opt, try_reduce_vehicles, apply_inter_route_2opt) on the perturbed solution.",
    "If the result is better than the recorded best, update the best solution.",
    "Repeat perturbation + local search for up to 30 seconds (use time.time() to enforce the budget).",
    "Return the best solution found across all iterations."
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
- Solver hard timeout: 600 seconds. Any O(n²) or larger loop MUST include a time.time() budget check.
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
