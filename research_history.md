## Iteration 0 (Baseline) — 2026-05-31T22:04:56
Branch: `main`
Result: 40v / 10016.21 / 2090ms / gap 17.52%
Construction: Regret-2 + vehicle reduction + 2-opt + Or-opt(1/2/3)

---

## Iteration 2 — 2026-05-31T22:50:02
Branch: `experiment/2_inter-route-2-opt`
Proposal: Modify apply_or_opt() to perform 2-opt moves across routes, enabling better vehicle reductions.
Result: 45v / 10761.00 / 1068ms / gap 26.26%
Decision: DISCARDED (quality_improved=False, time_improved=True)

---

## Iteration 3 — 2026-05-31T23:05:37
Branch: `experiment/3_inter-route-2opt-move`
Proposal: Add a new `apply_inter_2opt()` function to perform 2-opt moves between routes, enabling better route merging and vehicle reduction.
Result: 40v / 9870.11 / 2204ms / gap 15.81%
Decision: KEPT (quality_improved=True, time_improved=False)

---

## Iteration 4 — 2026-06-02T22:11:07
Branch: `experiment/4_inter-route-2opt-improvement`
Proposal: Improve the efficiency of `apply_inter_route_2opt()` by reducing redundant checks and optimizing loop structures.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error[E0425]: cannot find function `apply_or_opt` in this scope
   --> src/solver.rs:223:19
    |
223 |         let imp = apply_or_opt(prob, &mut routes);
    |                   ^^^^^^^^^^^^ not found in this scope

For more information about this error, try `rustc --explain E0425`.
error: could not compile `vrptw_autoresearch` (bin "vrptw_autoresearch") due to 1 previous error
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 5 — 2026-06-02T22:24:59
Branch: `experiment/5_inter-route-2opt-improvement-v2`
Proposal: Refine the `apply_inter_route_2opt()` function to improve efficiency and effectiveness, focusing on reducing redundant checks and optimizing loop structures.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error[E0609]: no field `k` on type `&Problem`
   --> src/solver.rs:219:78
    |
219 |             if routes[i].customers.len() + routes[j].customers.len() <= prob.k {
    |                                                                              ^ unknown field
    |
help: a field with a similar name exists
    |
219 -             if routes[i].customers.len() + routes[j].customers.len() <= prob.k {
219 +             if routes[i].customers.len() + routes[j].customers.len() <= prob.n {
    |

error[E0599]: the method `concat` exists for array `[&Vec<usize>; 2]`, but its trait bounds were not satisfied
   --> src/solver.rs:223:19
    |
220 |                   let new_route_customers: Vec<usize> = [
    |  _______________________________________________________-
221 | |                     &routes[i].customers,
222 | |                     &routes[j].customers
223 | |                 ].concat();
    | |                  -^^^^^^ method cannot be called on `[&Vec<usize>; 2]` due to unsatisfied trait bounds
    | |__________________|
    |
    |
... (6 more lines)
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---
