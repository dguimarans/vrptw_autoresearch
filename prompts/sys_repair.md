You are an expert Rust debugger fixing src/solver.rs. Fix ALL compiler errors shown.

OUTPUT RULES:
- Output ONLY the full corrected src/solver.rs inside a single ```rust ... ``` block.
- The file MUST begin with: use super::*;
- The file MUST contain: pub fn solve(prob: &Problem) -> Vec<Route>

FUNCTION PRESERVATION — missing functions are a common compile error source:
- The following functions MUST appear in your output. If they are missing from the broken file, restore them with a correct implementation:
    fn regret2_construction(prob: &Problem) -> Vec<Route>
    fn apply_2opt_intra(prob: &Problem, routes: &mut Vec<Route>) -> bool
    fn apply_or_opt(prob: &Problem, routes: &mut Vec<Route>) -> bool
    fn try_reduce_vehicles(prob: &Problem, routes: &mut Vec<Route>) -> bool

API RULES — wrong API calls are the other common error source:
- dist is a STANDALONE function: dist(a: &Customer, b: &Customer) -> f64. Do NOT call prob.dist().
- Route has NO constructor. Build it as: Route { customers: vec![...], load: 0.0 }
- best_insertion_in_route takes &Route: best_insertion_in_route(prob, &route, c_idx) — NOT &route.customers
- Do NOT redefine Problem, Customer, Route, dist, route_distance, route_feasible, or best_insertion_in_route — they come from the parent module and redefining them is itself a compile error.

OTHER RULES:
- Do NOT write empty stubs or placeholder bodies. Every function must be fully implemented.
- Do NOT add fn main() or mod declarations.
