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

## Iteration 28 — 2026-06-06T17:03:54
Branch: (none — planner JSON parse failed)
Proposal: (none)
Result: PLANNER JSON PARSE FAILURE
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 29 — 2026-06-06T17:48:07
Branch: (none — planner JSON parse failed)
Proposal: (none)
Result: PLANNER JSON PARSE FAILURE
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 30 — 2026-06-06T18:04:37
Branch: `experiment/30_iterated-local-search-with-perturbation`
Proposal: Add an iterated local search loop around the existing local search to periodically perturb the solution and escape local optima.
Result: FAILED RUN — exhausted 3 repair attempts
Error (last attempt):
```
Traceback (most recent call last):
  File "/home/dguimarans/workspace/vrptw_autoresearch/vrptw.py", line 192, in <module>
    routes = solve(prob)
             ^^^^^^^^^^^
  File "/home/dguimarans/workspace/vrptw_autoresearch/solver.py", line 280, in solve
    best_cost = route_distance(prob, sum(routes, key=lambda r: r.customers))
                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'key' is an invalid keyword argument for sum()
```
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 31 — 2026-06-06T18:20:39
Branch: (none — planner JSON parse failed)
Proposal: (none)
Result: PLANNER JSON PARSE FAILURE
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 32 — 2026-06-06T18:22:58
Branch: (none — planner JSON parse failed)
Proposal: (none)
Result: PLANNER JSON PARSE FAILURE
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 33 — 2026-06-06T18:25:20
Branch: `experiment/33_iterated-local-search-with-perturbation`
Proposal: Add an iterated local search loop around the existing local search to escape local optima by randomly relocating a small number of customers between routes.
Result: INFEASIBLE — solver ran but solution violates constraints
Vehicles: 40  Distance: 11033.71  Time: 44509ms  Gap: 29.46%
Violations:
INFEASIBLE
  Route 8: TW violated at customer 68 (service starts 326.28, due 218.00)
  Route 9: capacity exceeded (202.0 > 200.0)
  Route 9: TW violated at customer 279 (service starts 539.51, due 196.00)
  Route 9: TW violated at customer 113 (service starts 733.37, due 137.00)
  Route 9: TW violated at customer 343 (service starts 785.89, due 451.00)
  Route 9: TW violated at customer 12 (service starts 807.30, due 595.00)
  Route 9: depot return at 852.64 exceeds depot due 765.00
  Route 20: TW violated at customer 318 (service starts 288.13, due 104.00)
  Route 20: TW violated at customer 237 (service starts 386.05, due 220.00)
  Route 26: TW violated at customer 313 (service starts 153.95, due 65.00)
  Route 26: TW violated at customer 165 (service starts 191.61, due 99.00)
  Route 26: TW violated at customer 90 (service starts 205.85, due 113.00)
  Route 26: TW violated at customer 360 (service starts 217.27, due 124.00)
  Route 26: TW violated at customer 108 (service starts 228.27, due 135.00)
  Route 26: TW violated at customer 314 (service starts 281.28, due 195.00)
  Route 26: TW violated at customer 166 (service starts 300.50, due 252.00)
  Route 26: TW violated at customer 154 (service starts 331.11, due 282.00)
  Route 30: TW violated at customer 366 (service starts 212.68, due 197.00)
  Route 30: TW violated at customer 169 (service starts 320.09, due 141.00)
  Route 30: TW violated at customer 361 (service starts 332.09, due 153.00)
  Route 30: TW violated at customer 393 (service starts 349.37, due 171.00)
  Route 30: TW violated at customer 85 (service starts 369.66, due 206.00)
  Route 32: capacity exceeded (206.0 > 200.0)
  Route 32: TW violated at customer 96 (service starts 292.71, due 126.00)
  Route 32: TW violated at customer 239 (service starts 484.03, due 149.00)
  Route 32: TW violated at customer 110 (service starts 496.03, due 161.00)
  Route 32: TW violated at customer 345 (service starts 507.03, due 172.00)
  Route 32: TW violated at customer 195 (service starts 518.45, due 184.00)
  Route 32: TW violated at customer 111 (service starts 532.92, due 211.00)
  Route 32: TW violated at customer 109 (service starts 549.00, due 227.00)
  Route 32: TW violated at customer 271 (service starts 561.24, due 239.00)
  Route 32: TW violated at customer 1 (service starts 577.32, due 267.00)
  Route 32: TW violated at customer 364 (service starts 590.92, due 254.00)
  Route 32: TW violated at customer 291 (service starts 609.98, due 462.00)
Decision: DISCARDED

---

## Iteration 34 — 2026-06-06T18:32:11
Branch: `experiment/34_ils-with-perturbation`
Proposal: Add an iterated local search loop around the existing local search to escape local optima by randomly relocating small parts of customers between routes.
Result: 40v / 9870.11 / 43566ms / gap 15.81%
Decision: DISCARDED (quality_improved=False, time_improved=False)

---

## Iteration 35 — 2026-06-06T18:39:08
Branch: `experiment/35_ils-with-perturbation`
Proposal: Add iterated local search (ILS) with vehicle count reduction perturbation to escape local optima by randomly relocating customers between routes.
Result: INFEASIBLE — solver ran but solution violates constraints
Vehicles: 28  Distance: 6625.43  Time: 165156ms  Gap: -22.26%
Violations:
INFEASIBLE
  Customer 2 never visited
  Customer 4 never visited
  Customer 6 never visited
  Customer 7 never visited
  Customer 8 never visited
  Customer 10 never visited
  Customer 11 never visited
  Customer 12 never visited
  Customer 18 never visited
  Customer 19 never visited
  Customer 23 never visited
  Customer 24 never visited
  Customer 25 never visited
  Customer 26 never visited
  Customer 31 never visited
  Customer 32 never visited
  Customer 37 never visited
  Customer 38 never visited
  Customer 40 never visited
  Customer 42 never visited
  Customer 44 never visited
  Customer 47 never visited
  Customer 49 never visited
  Customer 51 never visited
  Customer 52 never visited
  Customer 55 never visited
  Customer 66 never visited
  Customer 68 never visited
  Customer 72 never visited
  Customer 73 never visited
  Customer 75 never visited
  Customer 78 never visited
  Customer 79 never visited
  Customer 81 never visited
  Customer 82 never visited
  Customer 84 never visited
  Customer 87 never visited
  Customer 90 never visited
  Customer 91 never visited
  Customer 96 never visited
  Customer 98 never visited
  Customer 102 never visited
  Customer 103 never visited
  Customer 107 never visited
  Customer 113 never visited
  Customer 116 never visited
  Customer 118 never visited
  Customer 120 never visited
  Customer 122 never visited
  Customer 123 never visited
  Customer 124 never visited
  Customer 125 never visited
  Customer 126 never visited
  Customer 128 never visited
  Customer 130 never visited
  Customer 134 never visited
  Customer 135 never visited
  Customer 136 never visited
  Customer 137 never visited
  Customer 140 never visited
  Customer 144 never visited
  Customer 148 never visited
  Customer 151 never visited
  Customer 154 never visited
  Customer 159 never visited
  Customer 161 never visited
  Customer 162 never visited
  Customer 163 never visited
  Customer 166 never visited
  Customer 167 never visited
  Customer 168 never visited
  Customer 170 never visited
  Customer 172 never visited
  Customer 175 never visited
  Customer 176 never visited
  Customer 180 never visited
  Customer 181 never visited
  Customer 182 never visited
  Customer 186 never visited
  Customer 188 never visited
  Customer 191 never visited
  Customer 194 never visited
  Customer 197 never visited
  Customer 200 never visited
  Customer 204 never visited
  Customer 207 never visited
  Customer 208 never visited
  Customer 209 never visited
  Customer 210 never visited
  Customer 211 never visited
  Customer 214 never visited
  Customer 224 never visited
  Customer 226 never visited
  Customer 229 never visited
  Customer 230 never visited
  Customer 231 never visited
  Customer 233 never visited
  Customer 239 never visited
  Customer 244 never visited
  Customer 246 never visited
  Customer 248 never visited
  Customer 250 never visited
  Customer 251 never visited
  Customer 252 never visited
  Customer 255 never visited
  Customer 258 never visited
  Customer 259 never visited
  Customer 261 never visited
  Customer 265 never visited
  Customer 267 never visited
  Customer 269 never visited
  Customer 270 never visited
  Customer 273 never visited
  Customer 276 never visited
  Customer 282 never visited
  Customer 283 never visited
  Customer 285 never visited
  Customer 287 never visited
  Customer 288 never visited
  Customer 293 never visited
  Customer 294 never visited
  Customer 295 never visited
  Customer 297 never visited
  Customer 298 never visited
  Customer 301 never visited
  Customer 306 never visited
  Customer 307 never visited
  Customer 309 never visited
  Customer 311 never visited
  Customer 313 never visited
  Customer 315 never visited
  Customer 319 never visited
  Customer 320 never visited
  Customer 321 never visited
  Customer 323 never visited
  Customer 324 never visited
  Customer 325 never visited
  Customer 328 never visited
  Customer 329 never visited
  Customer 330 never visited
  Customer 332 never visited
  Customer 335 never visited
  Customer 337 never visited
  Customer 338 never visited
  Customer 339 never visited
  Customer 343 never visited
  Customer 349 never visited
  Customer 350 never visited
  Customer 351 never visited
  Customer 352 never visited
  Customer 354 never visited
  Customer 358 never visited
  Customer 363 never visited
  Customer 367 never visited
  Customer 369 never visited
  Customer 373 never visited
  Customer 375 never visited
  Customer 381 never visited
  Customer 383 never visited
  Customer 389 never visited
  Customer 394 never visited
  Customer 395 never visited
  Customer 396 never visited
  Customer 397 never visited
  Customer 398 never visited
Decision: DISCARDED

---
