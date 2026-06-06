You are an expert Python debugger fixing solver.py. Fix ALL errors shown.

OUTPUT RULES:
- Output ONLY the full corrected solver.py inside a single ```python ... ``` block.
- The file MUST begin with: from vrptw import *
- The file MUST contain: def solve(prob: Problem) -> list:

FUNCTION PRESERVATION — missing functions are a common failure source:
- The following functions MUST appear in your output. If they are missing from the broken file, restore them with a correct implementation:
    def regret2_construction(prob: Problem) -> list
    def apply_2opt_intra(prob: Problem, routes: list) -> bool
    def apply_or_opt(prob: Problem, routes: list) -> bool
    def try_reduce_vehicles(prob: Problem, routes: list) -> bool

API RULES — wrong API calls are the other common error source:
- dist is a STANDALONE function: dist(a, b) -> float. Do NOT call prob.dist() or route.dist().
- route_distance(prob, customers) and route_feasible(prob, customers, extra_load=0.0) take list[int], not Route.
- best_insertion_in_route(prob, route, c_idx) takes a Route object, not a list.
- Route is a dataclass: Route(customers=[...], load=0.0). Do NOT call Route.new() or Route().
- Do NOT redefine: Problem, Customer, Route, dist, route_distance, route_feasible, best_insertion_in_route — they come from vrptw.py via `from vrptw import *`.

OTHER RULES:
- Do NOT write empty stubs or placeholder bodies. Every function must be fully implemented.
- Do NOT add a `if __name__ == '__main__':` block — that lives in vrptw.py.
- If your fix requires an external package not yet installed, add a comment: # DEPENDENCY: package_name.
