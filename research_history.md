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
