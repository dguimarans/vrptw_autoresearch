## Iteration 0 (Baseline) — 2026-05-31T22:04:56
Branch: `main`
Result: 40v / 10016.21 / 2090ms / gap 17.52%
Construction: Regret-2 + vehicle reduction + 2-opt + Or-opt(1/2/3)

---

## Iteration 1 — 2026-05-31T22:04:59
Branch: `experiment/1_inter-2-opt-move`
Proposal: Add a new `apply_2opt_inter` function to perform 2-opt moves between routes, improving distance.
Result: FAILED COMPILE — exhausted 10 repair attempts
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

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

## Iteration 4 — 2026-05-31T23:17:11
Branch: `experiment/4_route-first-cluster-second`
Proposal: Add a new route-first-cluster-second heuristic to merge nearby clusters, improving vehicle reductions.
Result: FAILED COMPILE — exhausted 10 repair attempts
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 5 — 2026-05-31T23:54:55
Branch: `experiment/5_route-first-cluster-second`
Proposal: Implement a route-first cluster-second heuristic to improve vehicle reductions.
Result: FAILED COMPILE — exhausted 10 repair attempts
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 6 — 2026-06-01T00:33:11
Branch: `experiment/6_inter-route-2opt-move`
Proposal: Add a new `apply_inter_route_2opt()` function to perform 2-opt moves between routes, enabling better route merging and vehicle reduction.
Result: FAILED COMPILE — exhausted 10 repair attempts
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 7 — 2026-06-01T00:51:29
Branch: `experiment/7_iter-1780268414`
Proposal: (no summary provided)
Result: FAILED COMPILE — exhausted 10 repair attempts
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 8 — 2026-06-01T01:13:17
Branch: `experiment/8_iter-1780269617`
Proposal: (no summary provided)
Result: FAILED COMPILE — exhausted 10 repair attempts
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 9 — 2026-06-01T01:32:14
Branch: `experiment/9_iter-1780270776`
Proposal: (no summary provided)
Result: FAILED COMPILE — exhausted 10 repair attempts
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 10 — 2026-06-01T01:51:28
Branch: `experiment/10_iter-1780271831`
Proposal: (no summary provided)
Result: FAILED COMPILE — exhausted 10 repair attempts
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---

## Iteration 11 — 2026-06-01T02:36:53
Branch: `experiment/11_iter-1780275354`
Proposal: (no summary provided)
Result: FAILED COMPILE — exhausted 10 repair attempts
Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf
Decision: DISCARDED

---
