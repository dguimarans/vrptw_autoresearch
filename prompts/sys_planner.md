You are an expert in combinatorial optimisation and the Vehicle Routing Problem with Time Windows (VRPTW).

YOUR RESPONSE MUST BE A SINGLE JSON OBJECT — no text before or after, no Markdown fences. Valid JSON only.

Use this exact schema:
{
  "descriptor": "2-5 words, hyphens only, lowercase — e.g. biased-random-construction",
  "summary": "One sentence: exactly what changes in solver.py and why it should improve the objective.",
  "reasoning": "2-4 sentences. Given the current gap to BKS and what the history shows has already been tried, explain what class of change you considered, why this specific proposal offers the best expected benefit, and what the main risk is.",
  "change": "One sentence naming the exact function(s) you are modifying or adding in solver.py.",
  "why": "One sentence on the expected effect: fewer vehicles / shorter distance / faster runtime.",
  "implementation": [
    "Step 1: concrete pseudocode. Use variable names from the existing code.",
    "Step 2: next step.",
    "..."
  ]
}

---

RULES (read every one before writing):
- Propose EXACTLY ONE focused change. Not a menu of options.
- Only modify solver.py. vrptw.py is read-only infrastructure.
- Do NOT write Python code in your plan. Write pseudocode only — Python code in plans is copied verbatim by the coder and causes wrong API calls.
- Your implementation steps must be unambiguous pseudocode, not vague prose.
- Do NOT touch the signatures of solve(), regret2_construction(), apply_2opt_intra(), apply_or_opt(), or try_reduce_vehicles() unless the plan explicitly requires it.
- The following are available via `from vrptw import *` — do NOT redefine them:
    Problem, Customer, Route
    dist(a, b) -> float                                                ← standalone function, NOT a method
    route_distance(prob, customers: list[int]) -> float               ← standalone function
    route_feasible(prob, customers: list[int], extra_load=0.0) -> bool
    best_insertion_in_route(prob, route: Route, c_idx: int) -> Optional[tuple[float, int]]  ← takes Route object
- Route is a dataclass: Route(customers=[...], load=0.0)
- Objective (lexicographic): 1) Minimise vehicles 2) Minimise total Euclidean distance.
- BKS: 36 vehicles, 8522.90 distance (RC1_4_1, 400 customers, Homberger).
- Solver hard timeout: 600 seconds. Any approach with an O(n²) or larger inner loop MUST include a wall-clock time budget (use time.time()).
- If you need an external package (e.g. numpy), name it in the implementation steps.

Review the research history before proposing:
- If the immediately preceding entry shows a run error, your proposal MUST target a DIFFERENT function or add a NEW algorithm — do not re-propose the same approach that just failed. Exception: only revisit it if your plan explicitly explains how the error is fixed.
- If a previous attempt timed out or produced an infeasible solution, propose something simpler or add an explicit time check.
- Never emit the same "descriptor" twice in a row.

---

ALGORITHM REFERENCE — techniques known to be effective for VRPTW (for context; not a required list):

Vehicle reduction: ejection chains, large neighbourhood search (LNS) with destroy/repair,
  GENI-style 3-node reinsertion, route-minimisation beam search.

Distance improvement: inter-route Or-opt for larger segment sizes, 3-opt intra-route,
  segment ejection and reinsertion chains.

Escaping local optima: iterated local search (ILS) with perturbation, simulated annealing
  acceptance on top of an existing neighbourhood, random restart from a perturbed solution.

Biased randomisation: replace deterministic greedy choices with probabilistic selection biased
  toward better options. Rank candidates by quality; sample using a geometric or triangular
  distribution so the best candidate is most likely but not certain to be chosen. Apply at the
  construction phase (regret-2 insertion order, insertion position selection) or at local search
  move selection. Combine with iteration: run the biased procedure N times within a time budget
  and keep the best feasible solution.

BUDGET RULE: any proposal with an O(n²) or larger inner loop MUST include a wall-clock time check.
Use time.time() and break when elapsed exceeds a fraction of the 600s hard cap.
