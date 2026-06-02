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

## Iteration 6 — 2026-06-02T22:39:49
Branch: `experiment/6_iter-1780432971`
Proposal: (no summary provided)
Result: INFEASIBLE — solver ran but solution violates constraints
Vehicles: 0  Distance: -0.00  Time: 0ms  Gap: -100.00%
Violations:
INFEASIBLE
  Customer 1 never visited
  Customer 2 never visited
  Customer 3 never visited
  Customer 4 never visited
  Customer 5 never visited
  Customer 6 never visited
  Customer 7 never visited
  Customer 8 never visited
  Customer 9 never visited
  Customer 10 never visited
  Customer 11 never visited
  Customer 12 never visited
  Customer 13 never visited
  Customer 14 never visited
  Customer 15 never visited
  Customer 16 never visited
  Customer 17 never visited
  Customer 18 never visited
  Customer 19 never visited
  Customer 20 never visited
  Customer 21 never visited
  Customer 22 never visited
  Customer 23 never visited
  Customer 24 never visited
  Customer 25 never visited
  Customer 26 never visited
  Customer 27 never visited
  Customer 28 never visited
  Customer 29 never visited
  Customer 30 never visited
  Customer 31 never visited
  Customer 32 never visited
  Customer 33 never visited
  Customer 34 never visited
  Customer 35 never visited
  Customer 36 never visited
  Customer 37 never visited
  Customer 38 never visited
  Customer 39 never visited
  Customer 40 never visited
  Customer 41 never visited
  Customer 42 never visited
  Customer 43 never visited
  Customer 44 never visited
  Customer 45 never visited
  Customer 46 never visited
  Customer 47 never visited
  Customer 48 never visited
  Customer 49 never visited
  Customer 50 never visited
  Customer 51 never visited
  Customer 52 never visited
  Customer 53 never visited
  Customer 54 never visited
  Customer 55 never visited
  Customer 56 never visited
  Customer 57 never visited
  Customer 58 never visited
  Customer 59 never visited
  Customer 60 never visited
  Customer 61 never visited
  Customer 62 never visited
  Customer 63 never visited
  Customer 64 never visited
  Customer 65 never visited
  Customer 66 never visited
  Customer 67 never visited
  Customer 68 never visited
  Customer 69 never visited
  Customer 70 never visited
  Customer 71 never visited
  Customer 72 never visited
  Customer 73 never visited
  Customer 74 never visited
  Customer 75 never visited
  Customer 76 never visited
  Customer 77 never visited
  Customer 78 never visited
  Customer 79 never visited
  Customer 80 never visited
  Customer 81 never visited
  Customer 82 never visited
  Customer 83 never visited
  Customer 84 never visited
  Customer 85 never visited
  Customer 86 never visited
  Customer 87 never visited
  Customer 88 never visited
  Customer 89 never visited
  Customer 90 never visited
  Customer 91 never visited
  Customer 92 never visited
  Customer 93 never visited
  Customer 94 never visited
  Customer 95 never visited
  Customer 96 never visited
  Customer 97 never visited
  Customer 98 never visited
  Customer 99 never visited
  Customer 100 never visited
  Customer 101 never visited
  Customer 102 never visited
  Customer 103 never visited
  Customer 104 never visited
  Customer 105 never visited
  Customer 106 never visited
  Customer 107 never visited
  Customer 108 never visited
  Customer 109 never visited
  Customer 110 never visited
  Customer 111 never visited
  Customer 112 never visited
  Customer 113 never visited
  Customer 114 never visited
  Customer 115 never visited
  Customer 116 never visited
  Customer 117 never visited
  Customer 118 never visited
  Customer 119 never visited
  Customer 120 never visited
  Customer 121 never visited
  Customer 122 never visited
  Customer 123 never visited
  Customer 124 never visited
  Customer 125 never visited
  Customer 126 never visited
  Customer 127 never visited
  Customer 128 never visited
  Customer 129 never visited
  Customer 130 never visited
  Customer 131 never visited
  Customer 132 never visited
  Customer 133 never visited
  Customer 134 never visited
  Customer 135 never visited
  Customer 136 never visited
  Customer 137 never visited
  Customer 138 never visited
  Customer 139 never visited
  Customer 140 never visited
  Customer 141 never visited
  Customer 142 never visited
  Customer 143 never visited
  Customer 144 never visited
  Customer 145 never visited
  Customer 146 never visited
  Customer 147 never visited
  Customer 148 never visited
  Customer 149 never visited
  Customer 150 never visited
  Customer 151 never visited
  Customer 152 never visited
  Customer 153 never visited
  Customer 154 never visited
  Customer 155 never visited
  Customer 156 never visited
  Customer 157 never visited
  Customer 158 never visited
  Customer 159 never visited
  Customer 160 never visited
  Customer 161 never visited
  Customer 162 never visited
  Customer 163 never visited
  Customer 164 never visited
  Customer 165 never visited
  Customer 166 never visited
  Customer 167 never visited
  Customer 168 never visited
  Customer 169 never visited
  Customer 170 never visited
  Customer 171 never visited
  Customer 172 never visited
  Customer 173 never visited
  Customer 174 never visited
  Customer 175 never visited
  Customer 176 never visited
  Customer 177 never visited
  Customer 178 never visited
  Customer 179 never visited
  Customer 180 never visited
  Customer 181 never visited
  Customer 182 never visited
  Customer 183 never visited
  Customer 184 never visited
  Customer 185 never visited
  Customer 186 never visited
  Customer 187 never visited
  Customer 188 never visited
  Customer 189 never visited
  Customer 190 never visited
  Customer 191 never visited
  Customer 192 never visited
  Customer 193 never visited
  Customer 194 never visited
  Customer 195 never visited
  Customer 196 never visited
  Customer 197 never visited
  Customer 198 never visited
  Customer 199 never visited
  Customer 200 never visited
  Customer 201 never visited
  Customer 202 never visited
  Customer 203 never visited
  Customer 204 never visited
  Customer 205 never visited
  Customer 206 never visited
  Customer 207 never visited
  Customer 208 never visited
  Customer 209 never visited
  Customer 210 never visited
  Customer 211 never visited
  Customer 212 never visited
  Customer 213 never visited
  Customer 214 never visited
  Customer 215 never visited
  Customer 216 never visited
  Customer 217 never visited
  Customer 218 never visited
  Customer 219 never visited
  Customer 220 never visited
  Customer 221 never visited
  Customer 222 never visited
  Customer 223 never visited
  Customer 224 never visited
  Customer 225 never visited
  Customer 226 never visited
  Customer 227 never visited
  Customer 228 never visited
  Customer 229 never visited
  Customer 230 never visited
  Customer 231 never visited
  Customer 232 never visited
  Customer 233 never visited
  Customer 234 never visited
  Customer 235 never visited
  Customer 236 never visited
  Customer 237 never visited
  Customer 238 never visited
  Customer 239 never visited
  Customer 240 never visited
  Customer 241 never visited
  Customer 242 never visited
  Customer 243 never visited
  Customer 244 never visited
  Customer 245 never visited
  Customer 246 never visited
  Customer 247 never visited
  Customer 248 never visited
  Customer 249 never visited
  Customer 250 never visited
  Customer 251 never visited
  Customer 252 never visited
  Customer 253 never visited
  Customer 254 never visited
  Customer 255 never visited
  Customer 256 never visited
  Customer 257 never visited
  Customer 258 never visited
  Customer 259 never visited
  Customer 260 never visited
  Customer 261 never visited
  Customer 262 never visited
  Customer 263 never visited
  Customer 264 never visited
  Customer 265 never visited
  Customer 266 never visited
  Customer 267 never visited
  Customer 268 never visited
  Customer 269 never visited
  Customer 270 never visited
  Customer 271 never visited
  Customer 272 never visited
  Customer 273 never visited
  Customer 274 never visited
  Customer 275 never visited
  Customer 276 never visited
  Customer 277 never visited
  Customer 278 never visited
  Customer 279 never visited
  Customer 280 never visited
  Customer 281 never visited
  Customer 282 never visited
  Customer 283 never visited
  Customer 284 never visited
  Customer 285 never visited
  Customer 286 never visited
  Customer 287 never visited
  Customer 288 never visited
  Customer 289 never visited
  Customer 290 never visited
  Customer 291 never visited
  Customer 292 never visited
  Customer 293 never visited
  Customer 294 never visited
  Customer 295 never visited
  Customer 296 never visited
  Customer 297 never visited
  Customer 298 never visited
  Customer 299 never visited
  Customer 300 never visited
  Customer 301 never visited
  Customer 302 never visited
  Customer 303 never visited
  Customer 304 never visited
  Customer 305 never visited
  Customer 306 never visited
  Customer 307 never visited
  Customer 308 never visited
  Customer 309 never visited
  Customer 310 never visited
  Customer 311 never visited
  Customer 312 never visited
  Customer 313 never visited
  Customer 314 never visited
  Customer 315 never visited
  Customer 316 never visited
  Customer 317 never visited
  Customer 318 never visited
  Customer 319 never visited
  Customer 320 never visited
  Customer 321 never visited
  Customer 322 never visited
  Customer 323 never visited
  Customer 324 never visited
  Customer 325 never visited
  Customer 326 never visited
  Customer 327 never visited
  Customer 328 never visited
  Customer 329 never visited
  Customer 330 never visited
  Customer 331 never visited
  Customer 332 never visited
  Customer 333 never visited
  Customer 334 never visited
  Customer 335 never visited
  Customer 336 never visited
  Customer 337 never visited
  Customer 338 never visited
  Customer 339 never visited
  Customer 340 never visited
  Customer 341 never visited
  Customer 342 never visited
  Customer 343 never visited
  Customer 344 never visited
  Customer 345 never visited
  Customer 346 never visited
  Customer 347 never visited
  Customer 348 never visited
  Customer 349 never visited
  Customer 350 never visited
  Customer 351 never visited
  Customer 352 never visited
  Customer 353 never visited
  Customer 354 never visited
  Customer 355 never visited
  Customer 356 never visited
  Customer 357 never visited
  Customer 358 never visited
  Customer 359 never visited
  Customer 360 never visited
  Customer 361 never visited
  Customer 362 never visited
  Customer 363 never visited
  Customer 364 never visited
  Customer 365 never visited
  Customer 366 never visited
  Customer 367 never visited
  Customer 368 never visited
  Customer 369 never visited
  Customer 370 never visited
  Customer 371 never visited
  Customer 372 never visited
  Customer 373 never visited
  Customer 374 never visited
  Customer 375 never visited
  Customer 376 never visited
  Customer 377 never visited
  Customer 378 never visited
  Customer 379 never visited
  Customer 380 never visited
  Customer 381 never visited
  Customer 382 never visited
  Customer 383 never visited
  Customer 384 never visited
  Customer 385 never visited
  Customer 386 never visited
  Customer 387 never visited
  Customer 388 never visited
  Customer 389 never visited
  Customer 390 never visited
  Customer 391 never visited
  Customer 392 never visited
  Customer 393 never visited
  Customer 394 never visited
  Customer 395 never visited
  Customer 396 never visited
  Customer 397 never visited
  Customer 398 never visited
  Customer 399 never visited
  Customer 400 never visited
Decision: DISCARDED

---
