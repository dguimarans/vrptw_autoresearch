# VRPTW Auto-Research Loop

An autonomous optimisation research loop for the **Vehicle Routing Problem with Time Windows (VRPTW)**.
A DeepSeek-R1 planning agent proposes algorithmic improvements; a Qwen2.5-Coder agent implements them in Rust; the orchestrator benchmarks, evaluates, and merges improvements automatically.

## Problem

**Instance:** RC1_4\_1 (Homberger 400-customer benchmark)

| Property | Value |
|---|---|
| Customers | 400 |
| Vehicle capacity | 200 |
| Fleet limit | 100 vehicles |
| Best Known Solution (BKS) distance | **8522.90** |
| BKS reference | CVRPLib / SINTEF (8571.32 with 36 vehicles) |
| Objective | Lexicographic: 1) minimise vehicles, 2) minimise total distance |
| Distance metric | Euclidean, double precision |

RC1 instances combine random customer locations with clustered time windows,
testing both feasibility handling (tight TW constraints) and geometric route quality simultaneously.
This makes them a robust all-around benchmark compared to purely random (R) or clustered (C) instances.

## Architecture

```
orchestrator.py
  ├── DeepSeek-R1:14b  (planner)   — reads research history, proposes one improvement
  ├── Qwen2.5-Coder:7b (implementer) — writes Rust code, self-repairs up to 10 times
  └── Rust solver      (evaluator)  — cargo build --release, 300s timeout
```

Both models run locally via **Ollama** and are evicted from VRAM/RAM between phases to conserve memory.

### Loop logic

```
for each iteration (max 100, configurable):
  1. Checkout main; read best_result.json as baseline
  2. Create experiment/opt-<timestamp> branch
  3. DeepSeek reads research_history.md + src/main.rs → writes experiment_plan.md
  4. Qwen reads experiment_plan.md → rewrites src/main.rs
     └── repair loop: cargo check → fix → repeat (max 10 attempts)
  5. cargo build --release
  6. Run solver on RC1_4_1 (hard timeout 300s)
  7. Accept / reject:
     ├── Quality improved (lex.)  → keep (runtime allowed to worsen)
     ├── Runtime improved AND quality not worsened → keep
     └── Neither improved → archive branch, do not merge
  8. If kept: update best_result.json, regenerate graphs, merge to main, delete branch
  9. Sleep 10s (cooling)
```

### Accept / reject rule

Accepting a solution that is faster but equally good in quality allows the loop to trade
computation time for future deeper searches. A quality regression is never accepted for
pure runtime gains.

## Baseline solver (`src/main.rs`)

The initial implementation uses:

1. **Regret-2 construction** — for each unrouted customer, compute the cost difference
   between its best and second-best feasible insertion. Insert the customer with the
   highest regret (most urgent to place now). Creates an initial feasible solution.

2. **Vehicle reduction** — attempt to relocate all customers from the smallest route
   into other routes. Repeat until no further reduction is possible.

3. **Intra-route 2-opt** — standard segment reversal with TW feasibility check.

4. **Or-opt (1/2/3 segments)** — intra- and inter-route segment relocation.
   Interleaved with vehicle reduction until no improvement.

### Baseline result on RC1_4\_1

| Metric | Value |
|---|---|
| Vehicles | 39 |
| Total distance | 11095.09 |
| Gap to BKS | ~30.2 % |
| Runtime | ~8 s |

## Running manually

```bash
# Build
cargo build --release

# Solve RC1_4_1
./target/release/vrptw_autoresearch instances/homberger_400_customer_instances/RC1_4_1.TXT

# The binary prints three machine-parseable lines to stdout:
# RESULT_VEHICLES: <n>
# RESULT_DISTANCE: <d>
# RESULT_TIME_MS: <t>
# Full route detail goes to stderr.
```

## Running the research loop

```bash
# Install Python dependencies (once)
pip install requests matplotlib

# Configure in orchestrator.py:
#   MAX_ITERATIONS = 100   (0 = unlimited, Ctrl-C to stop)
#   SOLVER_TIMEOUT_S = 300

python orchestrator.py
```

## Output files

| File | Description |
|---|---|
| `best_result.json` | Current best solution metadata (vehicles, distance, time, iteration) |
| `research_log.csv` | All iterations: vehicles, distance, runtime, gap%, improvement flags |
| `research_history.md` | Append-only log of all plans and outcomes (read by DeepSeek each iteration) |
| `experiment_plan.md` | Per-iteration plan written by DeepSeek, read by Qwen (overwritten each iteration) |
| `graphs/distance_vs_iteration.png` | Solution quality evolution |
| `graphs/runtime_vs_iteration.png` | Solver runtime evolution |

<!-- GRAPHS_START -->
## Progress Graphs

![Distance vs Iteration](graphs/distance_vs_iteration.png)

![Runtime vs Iteration](graphs/runtime_vs_iteration.png)
<!-- GRAPHS_END -->

## Instance data

Homberger 400-customer instances are stored in `instances/homberger_400_customer_instances/`.
Format follows the Solomon convention: depot at index 0, columns are
`CUST_NO X Y DEMAND READY_TIME DUE_DATE SERVICE_TIME`.
Travel time equals Euclidean distance (no separate speed parameter).

## Repository structure

```
.
├── src/main.rs                          # Rust VRPTW solver (single file, AI-managed)
├── orchestrator.py                      # Python automation loop
├── instances/
│   └── homberger_400_customer_instances/
│       └── RC1_4_1.TXT                  # Benchmark instance
├── graphs/                              # Auto-generated PNG graphs
├── best_result.json                     # Current best solution (auto-updated)
├── research_log.csv                     # Iteration log (auto-updated)
├── research_history.md                  # Research notes (append-only)
└── experiment_plan.md                   # Current iteration plan
```
