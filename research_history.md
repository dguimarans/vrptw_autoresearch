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

## Iteration 4 — 2026-06-03T10:35:48
Branch: `experiment/4_delay-vehicle-reduction`
Proposal: Delay vehicle reduction attempts until after initial route optimization to allow better packing.
Result: 41v / 10040.14 / 3102ms / gap 17.80%
Decision: DISCARDED (quality_improved=False, time_improved=False)

---

## Iteration 5 — 2026-06-03T10:45:03
Branch: `experiment/5_inter-route-2opt-move`
Proposal: Add a new `apply_inter_route_2opt()` function to perform 2-opt moves between routes, enabling better route merging and vehicle reduction.
Result: 40v / 9870.11 / 2202ms / gap 15.81%
Decision: KEPT (quality_improved=False, time_improved=True)

---

## Iteration 6 — 2026-06-03T10:56:34
Branch: `experiment/6_incremental-distance-calculation`
Proposal: Modify apply_or_opt() to compute only incremental distance changes when moving segments between routes, improving runtime without affecting solution quality.
Result: 40v / 9870.11 / 2188ms / gap 15.81%
Decision: KEPT (quality_improved=False, time_improved=True)

---

## Iteration 7 — 2026-06-03T13:11:15
Branch: `experiment/7_incremental-distance-calculation`
Proposal: Modify apply_or_opt() to compute only incremental distance changes when moving segments between routes, improving runtime without affecting solution quality.
Result: 40v / 9870.11 / 2194ms / gap 15.81%
Decision: DISCARDED (quality_improved=False, time_improved=False)

---

## Iteration 8 — 2026-06-03T13:24:33
Branch: `experiment/8_multi-move-loop`
Proposal: Add a loop that alternates between 2-opt and Or-opt moves to explore more route improvements.
Result: 42v / 10052.10 / 1837ms / gap 17.94%
Decision: DISCARDED (quality_improved=False, time_improved=True)

---

## Iteration 9 — 2026-06-03T13:34:11
Branch: `experiment/9_inter-route-2opt-move`
Proposal: Modify apply_or_opt() to compute only incremental distance changes when moving segments between routes, improving runtime without affecting solution quality.
Result: NO PARSEABLE OUTPUT
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 10 — 2026-06-03T13:56:03
Branch: `experiment/10_incremental-vehicle-reduction`
Proposal: Modify vehicle reduction attempts to run multiple passes after inter-route moves, improving opportunities for elimination.
Result: 40v / 9870.11 / 2269ms / gap 15.81%
Decision: DISCARDED (quality_improved=False, time_improved=False)

---

## Iteration 11 — 2026-06-03T14:05:31
Branch: `experiment/11_lin-kernighan-route-construction`
Proposal: Replace regret2_construction() with Lin-Kernighan-based route construction for better initial routes.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error[E0277]: the type `[Customer]` cannot be indexed by `&usize`
  --> src/solver.rs:14:86
   |
14 |         let start_idx = *unrouted.iter().max_by_key(|&c| dist(depot, &prob.customers[c])).unwrap();
   |                                                                                      ^ slice indices are of type `usize` or ranges of `usize`
   |
   = help: the trait `SliceIndex<[Customer]>` is not implemented for `&usize`
help: the following other types implement trait `SliceIndex<T>`
  --> /rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/core/src/bstr/traits.rs:197:0
   |
   = note: `usize` implements `SliceIndex<ByteStr>`
  --> /rustc/59807616e1fa2540724bfbac14d7976d7e4a3860/library/core/src/slice/index.rs:214:0
   |
   = note: `usize` implements `SliceIndex<[T]>`
   = note: required for `Vec<Customer>` to implement `Index<&usize>`
help: dereference this index
   |
14 |         let start_idx = *unrouted.iter().max_by_key(|&c| dist(depot, &prob.customers[*c])).unwrap();
   |                                                                                      +

error[E0277]: the trait bound `f64: Ord` is not satisfied
  --> src/solver.rs:14:42
   |
14 |         let start_idx = *unrouted.iter().max_by_key(|&c| dist(depot, &prob.customers[c])).unwrap();
... (17 more lines)
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 12 — 2026-06-03T14:27:59
Branch: `experiment/12_inter-route-2-opt-integration`
Proposal: Integrate apply_inter_route_2opt() into the main optimization loop for continuous inter-route improvements.
Result: 40v / 9870.11 / 2195ms / gap 15.81%
Decision: DISCARDED (quality_improved=False, time_improved=False)

---

## Iteration 13 — 2026-06-03T14:38:08
Branch: `experiment/13_inter-route-2opt-loop`
Proposal: Add a loop applying inter-route 2-opt followed by other improvements to fully leverage route merging opportunities.
Result: 40v / 9870.11 / 2305ms / gap 15.81%
Decision: DISCARDED (quality_improved=False, time_improved=False)

---

## Iteration 14 — 2026-06-03T19:16:32
Branch: (none — planner failed before branch creation)
Proposal: (none)
Result: PLANNER LLM FAILURE — HTTPError
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 15 — 2026-06-03T19:20:47
Branch: `experiment/15_biased-random-construction`
Proposal: Introduce probabilistic selection in regret-2 construction for diverse route building.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error[E0433]: cannot find module or crate `rand` in this scope
  --> src/solver.rs:35:27
   |
35 |             let mut rng = rand::thread_rng();
   |                           ^^^^ use of unresolved module or unlinked crate `rand`
   |
   = help: if you wanted to use a crate named `rand`, use `cargo add rand` to add it to your `Cargo.toml`

error[E0599]: no method named `shuffle` found for struct `Vec<(f64, usize, usize)>` in the current scope
  --> src/solver.rs:46:21
   |
46 |             options.shuffle(&mut rng);
   |                     ^^^^^^^ method not found in `Vec<(f64, usize, usize)>`

Some errors have detailed explanations: E0433, E0599.
For more information about an error, try `rustc --explain E0433`.
error: could not compile `vrptw_autoresearch` (bin "vrptw_autoresearch") due to 2 previous errors
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 16 — 2026-06-03T20:17:03
Branch: `experiment/16_biased-random-construction`
Proposal: Replace deterministic regret-2 construction with a probabilistic approach to encourage diverse route building.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error: expected identifier, found reserved keyword `gen`
  --> src/solver.rs:38:20
   |
38 |             if rng.gen::<f64>() < prob {
   |                    ^^^ expected identifier, found reserved keyword
   |
help: escape `gen` to use it as an identifier
   |
38 |             if rng.r#gen::<f64>() < prob {
   |                    ++

error[E0433]: cannot find module or crate `rand` in this scope
  --> src/solver.rs:23:23
   |
23 |         let mut rng = rand::thread_rng();
   |                       ^^^^ use of unresolved module or unlinked crate `rand`
   |
   = help: if you wanted to use a crate named `rand`, use `cargo add rand` to add it to your `Cargo.toml`

For more information about this error, try `rustc --explain E0433`.
error: could not compile `vrptw_autoresearch` (bin "vrptw_autoresearch") due to 2 previous errors
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 17 — 2026-06-03T21:12:02
Branch: `experiment/17_biased-random-construction`
Proposal: Replace deterministic regret-2 construction with a probabilistic approach to encourage diverse route building.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error[E0433]: cannot find module or crate `rand` in this scope
  --> src/solver.rs:48:23
   |
48 |         let mut rng = rand::thread_rng();
   |                       ^^^^ use of unresolved module or unlinked crate `rand`
   |
   = help: if you wanted to use a crate named `rand`, use `cargo add rand` to add it to your `Cargo.toml`

For more information about this error, try `rustc --explain E0433`.
error: could not compile `vrptw_autoresearch` (bin "vrptw_autoresearch") due to 1 previous error
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 18 — 2026-06-03T22:08:29
Branch: `experiment/18_inter-route-2opt-loop`
Proposal: [Add a loop applying inter-route 2-opt followed by other improvements.]
Result: 43v / 10085.02 / 2956ms / gap 18.33%
Decision: DISCARDED (quality_improved=False, time_improved=False)

---

## Iteration 19 — 2026-06-03T22:29:00
Branch: `experiment/19_biased-random-construction`
Proposal: Replace deterministic regret-2 route selection with probabilistic choice based on regrets.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error: expected identifier, found reserved keyword `gen`
  --> src/solver.rs:56:24
   |
56 |                 if rng.gen::<f64>() < (remaining * p / total_prob) {
   |                        ^^^ expected identifier, found reserved keyword
   |
help: escape `gen` to use it as an identifier
   |
56 |                 if rng.r#gen::<f64>() < (remaining * p / total_prob) {
   |                        ++

error[E0571]: `break` with value from a `for` loop
  --> src/solver.rs:57:21
   |
55 |             for (i, (_, _, p)) in probs.iter().enumerate() {
   |             ---------------------------------------------- you can't `break` with a value in a `for` loop
56 |                 if rng.gen::<f64>() < (remaining * p / total_prob) {
57 |                     break i;
   |                     ^^^^^^^ can only break with a value inside `loop` or breakable block
   |
help: use `break` on its own without a value inside this `for` loop
   |
57 -                     break i;
57 +                     break;
... (13 more lines)
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 20 — 2026-06-03T23:27:18
Branch: `experiment/20_iterated-local-search`
Proposal: Introduce an iterated local search with perturbation to escape local optima and improve solution quality.
Result: 42v / 10052.10 / 3140ms / gap 17.94%
Decision: DISCARDED (quality_improved=False, time_improved=False)

---

## Iteration 21 — 2026-06-04T00:19:04
Branch: `experiment/21_biased-random-construction`
Proposal: Replace deterministic regret-2 with a probabilistic approach for diverse route building.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error: expected identifier, found reserved keyword `gen`
  --> src/solver.rs:44:41
   |
44 |             .find(|&(_, (_, _, p))| rng.gen::<f64>() < (remaining * p / total_prob))
   |                                         ^^^ expected identifier, found reserved keyword
   |
help: escape `gen` to use it as an identifier
   |
44 |             .find(|&(_, (_, _, p))| rng.r#gen::<f64>() < (remaining * p / total_prob))
   |                                         ++

error[E0433]: cannot find module or crate `rand` in this scope
  --> src/solver.rs:39:23
   |
39 |         let mut rng = rand::thread_rng();
   |                       ^^^^ use of unresolved module or unlinked crate `rand`
   |
   = help: if you wanted to use a crate named `rand`, use `cargo add rand` to add it to your `Cargo.toml`

warning: unused variable: `prob`
  --> src/solver.rs:69:28
   |
69 | fn incremental_feasibility(prob: &Problem, route: &[usize], start: usize, end: usize) -> bool {
   |                            ^^^^ help: if this is intentional, prefix it with an underscore: `_prob`
... (36 more lines)
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 22 — 2026-06-04T01:21:10
Branch: `experiment/22_biased-random-construction`
Proposal: Replace deterministic regret-2 route selection with probabilistic choice based on regrets.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error: expected identifier, found reserved keyword `gen`
  --> src/solver.rs:42:20
   |
42 |             if rng.gen::<f64>() < (remaining * regret / total_prob) {
   |                    ^^^ expected identifier, found reserved keyword
   |
help: escape `gen` to use it as an identifier
   |
42 |             if rng.r#gen::<f64>() < (remaining * regret / total_prob) {
   |                    ++

error[E0433]: cannot find module or crate `rand` in this scope
  --> src/solver.rs:37:23
   |
37 |         let mut rng = rand::thread_rng();
   |                       ^^^^ use of unresolved module or unlinked crate `rand`
   |
   = help: if you wanted to use a crate named `rand`, use `cargo add rand` to add it to your `Cargo.toml`

For more information about this error, try `rustc --explain E0433`.
error: could not compile `vrptw_autoresearch` (bin "vrptw_autoresearch") due to 2 previous errors
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 23 — 2026-06-04T02:15:17
Branch: `experiment/23_biased-random-construction`
Proposal: Replace deterministic regret-2 route selection with probabilistic choice based on regrets to improve solution diversity.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error: expected identifier, found reserved keyword `gen`
  --> src/solver.rs:56:20
   |
56 |             if rng.gen::<f64>() < remaining * p {
   |                    ^^^ expected identifier, found reserved keyword
   |
help: escape `gen` to use it as an identifier
   |
56 |             if rng.r#gen::<f64>() < remaining * p {
   |                    ++

error[E0432]: unresolved import `rand`
  --> src/solver.rs:10:9
   |
10 |     use rand::Rng;
   |         ^^^^ use of unresolved module or unlinked crate `rand`
   |
   = help: if you wanted to use a crate named `rand`, use `cargo add rand` to add it to your `Cargo.toml`

error[E0433]: cannot find module or crate `rand` in this scope
  --> src/solver.rs:11:19
   |
11 |     let mut rng = rand::thread_rng();
   |                   ^^^^ use of unresolved module or unlinked crate `rand`
... (6 more lines)
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 24 — 2026-06-04T03:12:58
Branch: `experiment/24_biased-random-construction`
Proposal: Replace deterministic regret-2 route selection with probabilistic choice based on regrets to improve solution diversity.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error: expected identifier, found reserved keyword `gen`
  --> src/solver.rs:45:17
   |
45 |             rng.gen::<f64>() < cumulative_prob
   |                 ^^^ expected identifier, found reserved keyword
   |
help: escape `gen` to use it as an identifier
   |
45 |             rng.r#gen::<f64>() < cumulative_prob
   |                 ++

error[E0433]: cannot find module or crate `rand` in this scope
  --> src/solver.rs:41:23
   |
41 |         let mut rng = rand::thread_rng();
   |                       ^^^^ use of unresolved module or unlinked crate `rand`
   |
   = help: if you wanted to use a crate named `rand`, use `cargo add rand` to add it to your `Cargo.toml`

For more information about this error, try `rustc --explain E0433`.
error: could not compile `vrptw_autoresearch` (bin "vrptw_autoresearch") due to 2 previous errors
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 25 — 2026-06-04T15:57:04
Branch: `experiment/25_regret-construction-random`
Proposal: Modify regret-2 construction to use probabilistic selection of customers based on their regrets, allowing for more diverse exploration.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error: expected identifier, found reserved keyword `gen`
  --> src/solver.rs:47:20
   |
47 |             if rng.gen::<f64>() < remaining * regrets[ui] / total_prob {
   |                    ^^^ expected identifier, found reserved keyword
   |
help: escape `gen` to use it as an identifier
   |
47 |             if rng.r#gen::<f64>() < remaining * regrets[ui] / total_prob {
   |                    ++

warning: use of deprecated function `rand::thread_rng`: Renamed to `rng`
 --> src/solver.rs:9:25
  |
9 |     let mut rng = rand::thread_rng();
  |                         ^^^^^^^^^^
  |
  = note: `#[warn(deprecated)]` on by default

warning: use of deprecated method `rand::Rng::r#gen`: Renamed to `random` to avoid conflict with the new `gen` keyword in Rust 2024.
  --> src/solver.rs:47:20
   |
47 |             if rng.gen::<f64>() < remaining * regrets[ui] / total_prob {
   |                    ^^^
... (23 more lines)
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 26 — 2026-06-04T18:27:31
Branch: `experiment/26_biased-random-construction`
Proposal: Replace deterministic regret-2 customer selection with probabilistic choice based on regrets to improve solution diversity.
Result: FAILED COMPILE — exhausted 3 repair attempts
Compile errors (last attempt):
```
Checking vrptw_autoresearch v0.1.0 (/home/dguimarans/workspace/vrptw_autoresearch)
error: expected identifier, found reserved keyword `gen`
  --> src/solver.rs:47:20
   |
47 |             if rng.gen::<f64>() < cumulative_prob {
   |                    ^^^ expected identifier, found reserved keyword
   |
help: escape `gen` to use it as an identifier
   |
47 |             if rng.r#gen::<f64>() < cumulative_prob {
   |                    ++

warning: use of deprecated function `rand::thread_rng`: Renamed to `rng`
  --> src/solver.rs:12:25
   |
12 |     let mut rng = rand::thread_rng();
   |                         ^^^^^^^^^^
   |
   = note: `#[warn(deprecated)]` on by default

warning: use of deprecated method `rand::Rng::r#gen`: Renamed to `random` to avoid conflict with the new `gen` keyword in Rust 2024.
  --> src/solver.rs:47:20
   |
47 |             if rng.gen::<f64>() < cumulative_prob {
   |                    ^^^
... (3 more lines)
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 27 (Python baseline) — 2026-06-06T00:00:00
Branch: `main`
Proposal: Direct port of Rust solver to Python (same algorithms, same results).
Result: 40v / 9870.11 / 31836ms / gap 15.81%
Note: Python runtime is ~16x Rust. This establishes the Python-language baseline for future comparisons.
Decision: KEPT (python baseline)

---

## Iteration 28 — 2026-06-07T21:35:07
Branch: `experiment/28_biased-random-construction`
Proposal: Replace deterministic regret-2 route selection with probabilistic choice based on regrets to improve solution diversity.
Result: 42v / 10218.27 / 41274ms / gap 19.89%
Decision: DISCARDED (quality_improved=False, time_improved=False)

---

## Iteration 29 — 2026-06-07T21:54:00
Branch: `experiment/29_iterated-local-search`
Proposal: Modify solve() to implement an iterated local search with perturbation and multiple restarts within time budget.
Result: FAILED RUN — exhausted 3 repair attempts
Error (last attempt):
```
Traceback (most recent call last):
  File "/home/dguimarans/workspace/vrptw_autoresearch/vrptw.py", line 192, in <module>
    routes = solve(prob)
             ^^^^^^^^^^^
  File "/home/dguimarans/workspace/vrptw_autoresearch/solver.py", line 292, in solve
    best_routes[ri].customers.insert(pos, removed_customers.pop(0))
                                          ^^^^^^^^^^^^^^^^^^^^^^^^
IndexError: pop from empty list
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 30 — 2026-06-07T22:43:23
Branch: `experiment/30_inter-route-3-opt`
Proposal: Modify apply_inter_route_2opt() to perform 3-opt swaps between routes, enabling larger route merges and better vehicle reduction.
Result: 40v / 9869.40 / 44930ms / gap 15.80%
Decision: KEPT (quality_improved=True, time_improved=False)

---

## Iteration 31 — 2026-06-07T23:00:56
Branch: `experiment/31_aggressive-vehicle-reduction-loop`
Proposal: Modify solve() to repeatedly attempt vehicle reduction after each improvement, maximizing elimination opportunities.
Result: 40v / 9884.66 / 42096ms / gap 15.98%
Decision: DISCARDED (quality_improved=False, time_improved=True)

---

## Iteration 32 — 2026-06-07T23:17:58
Branch: (none — planner JSON parse failed)
Proposal: (none)
Result: PLANNER JSON PARSE FAILURE
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 33 — 2026-06-07T23:23:37
Branch: `experiment/33_ejection-chain-integration`
Proposal: Integrate ejection chains to systematically remove and reinsert customers, enabling escape from local optima and improving vehicle reduction.
Result: 40v / 10120.96 / 81700ms / gap 18.75%
Decision: DISCARDED (quality_improved=False, time_improved=False)

---

## Iteration 34 — 2026-06-07T23:43:54
Branch: `experiment/34_ejection-chain-integration`
Proposal: Modify solve() to include ejection chains after initial optimizations, enabling escape from local optima and further reducing vehicles.
Result: FAILED RUN — exhausted 3 repair attempts
Error (last attempt):
```
Solver timed out after 600s
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 35 — 2026-06-08T00:26:36
Branch: `experiment/35_ejection-chain-integration`
Proposal: Modify solve() to include ejection chains after initial optimizations, enabling escape from local optima and further reducing vehicles.
Result: FAILED RUN — exhausted 3 repair attempts
Error (last attempt):
```
Solver timed out after 600s
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 36 — 2026-06-08T00:56:15
Branch: `experiment/36_simulated-annealing-integration`
Proposal: Modify solve() to include simulated annealing with perturbation and acceptance of non-improving moves, enabling escape from local optima.
Result: FAILED RUN — exhausted 3 repair attempts
Error (last attempt):
```
Traceback (most recent call last):
  File "/home/dguimarans/workspace/vrptw_autoresearch/vrptw.py", line 192, in <module>
    routes = solve(prob)
             ^^^^^^^^^^^
  File "/home/dguimarans/workspace/vrptw_autoresearch/solver.py", line 304, in solve
    routes = simulated_annealing(prob, routes)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/dguimarans/workspace/vrptw_autoresearch/solver.py", line 266, in simulated_annealing
    old_cost = route_distance(prob, routes[ri]) + route_distance(prob, routes[rj])
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/dguimarans/workspace/vrptw_autoresearch/vrptw.py", line 115, in route_distance
    d = dist(depot, prob.customers[customers[0]])
                                   ~~~~~~~~~^^^
TypeError: 'Route' object is not subscriptable
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---
