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
