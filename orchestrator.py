import os
import re
import subprocess
import json
import time
import csv
import signal
import sys
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# --- CONFIGURATION ---
PLANNER = "deepseek-headless"
CODER = "qwen2.5-coder:7b"
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
UNLOAD_URL = "http://localhost:11434/api/generate"
MAX_REPAIR_ATTEMPTS = 3
LLM_RETRY_ATTEMPTS = 3        # retries on LLM network/server error (not on bad output)
MAX_ITERATIONS = 10           # set to 0 for unlimited (Ctrl-C to stop)
MAX_HISTORY_FAILURES = 3      # max recent failure entries shown to planner (signal entries always kept)
SOLVER_TIMEOUT_S = 300        # hard cap on Rust binary execution
LLM_TIMEOUT_S = 7200          # 2h hard cap — covers DeepSeek-R1 worst-case CoT (~15k tokens at 5 tok/s) with 4x margin
COOLDOWN_S = 10               # sleep between iterations
INSTANCE_PATH = "instances/homberger_400_customer_instances/RC1_4_1.TXT"
BKS_DISTANCE = 8522.90        # best known solution distance (CVRPLib)
BKS_VEHICLES = 36             # SINTEF reference vehicle count (8571.32 solution)
RESEARCH_LOG_CSV = "research_log.csv"
BEST_RESULT_JSON = "best_result.json"
RESEARCH_HISTORY_MD = "research_history.md"
EXPERIMENT_PLAN_MD = "experiment_plan.md"
SOLUTION_FILE = "solution.txt"
GRAPHS_DIR = "graphs"
PROMPTS_DIR = "prompts"


# ---------------------------------------------------------------------------
# Shell helpers
# ---------------------------------------------------------------------------

def load_prompt(name: str) -> str:
    path = os.path.join(PROMPTS_DIR, f"{name}.md")
    with open(path, "r") as f:
        return f.read().strip()


def run_bash(cmd, timeout=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return result.stdout.strip() + "\n" + result.stderr.strip(), result.returncode


def force_unload(model_name):
    try:
        requests.post(UNLOAD_URL, json={"model": model_name, "keep_alive": 0}, timeout=10)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

def call_local_llm(model, system_prompt, user_content, nudge=None):
    """Call model with automatic retry on network/server errors.
    On retries, `nudge` is prepended to user_content to discourage repeating the same failure."""
    last_exc = None
    for attempt in range(1, LLM_RETRY_ATTEMPTS + 1):
        try:
            content = (f"{nudge}\n\n{user_content}" if nudge and attempt > 1 else user_content)
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": content},
                ],
                "temperature": 0.2,
            }
            response = requests.post(OLLAMA_URL, json=payload, timeout=LLM_TIMEOUT_S)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            last_exc = e
            print(f"    [LLM] Attempt {attempt}/{LLM_RETRY_ATTEMPTS} failed: {type(e).__name__}: {e}")
            if attempt < LLM_RETRY_ATTEMPTS:
                time.sleep(COOLDOWN_S)
    raise last_exc


# ---------------------------------------------------------------------------
# Code extraction
# ---------------------------------------------------------------------------

def extract_rust_code(raw_text):
    if "```rust" in raw_text:
        return raw_text.split("```rust")[1].split("```")[0].strip()
    return raw_text.strip()


# ---------------------------------------------------------------------------
# Planner output parsing
# ---------------------------------------------------------------------------

def parse_plan_header(plan: str) -> tuple[str, str]:
    """Extract DESCRIPTOR and SUMMARY from the first two lines of the plan.
    Returns (descriptor, summary) with safe fallbacks."""
    descriptor = ""
    summary = ""
    for line in plan.splitlines():
        line = line.strip()
        if line.startswith("DESCRIPTOR:"):
            descriptor = line.split(":", 1)[1].strip()
        elif line.startswith("SUMMARY:"):
            summary = line.split(":", 1)[1].strip()
        if descriptor and summary:
            break

    # Sanitise descriptor for use in a branch name
    descriptor = re.sub(r"[^a-zA-Z0-9_\-]", "-", descriptor).strip("-").lower()
    descriptor = re.sub(r"-{2,}", "-", descriptor)  # collapse consecutive hyphens
    if not descriptor:
        descriptor = f"iter-{int(time.time())}"

    if not summary:
        summary = "(no summary provided)"

    return descriptor, summary


# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------

def load_best_result():
    if not os.path.exists(BEST_RESULT_JSON):
        return None
    with open(BEST_RESULT_JSON, "r") as f:
        return json.load(f)


def save_best_result(vehicles, distance, time_ms, iteration, branch):
    data = {
        "vehicles": vehicles,
        "distance": distance,
        "time_ms": time_ms,
        "iteration": iteration,
        "branch": branch,
    }
    with open(BEST_RESULT_JSON, "w") as f:
        json.dump(data, f, indent=2)


def parse_solver_output(raw_output):
    vehicles, distance, time_ms = None, None, None
    for line in raw_output.splitlines():
        if line.startswith("RESULT_VEHICLES:"):
            vehicles = int(line.split()[-1])
        elif line.startswith("RESULT_DISTANCE:"):
            distance = float(line.split()[-1])
        elif line.startswith("RESULT_TIME_MS:"):
            time_ms = float(line.split()[-1])
    return vehicles, distance, time_ms


def is_better_solution(new_v, new_d, best_v, best_d):
    """Lexicographic: fewer vehicles first, then shorter distance."""
    if new_v < best_v:
        return True
    if new_v == best_v and new_d < best_d:
        return True
    return False


def solution_worsened(new_v, new_d, best_v, best_d):
    if new_v > best_v:
        return True
    if new_v == best_v and new_d > best_d:
        return True
    return False


def get_iteration_count():
    """Return the highest iteration number seen across the log CSV and history file.
    Using max-value (not row-count) ensures a correct resume point even when
    compile-fail / timeout iterations are recorded in history but not in the CSV."""
    max_iter = 0
    if os.path.exists(RESEARCH_LOG_CSV):
        with open(RESEARCH_LOG_CSV, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    max_iter = max(max_iter, int(row["iteration"]))
                except (ValueError, KeyError):
                    pass
    if os.path.exists(RESEARCH_HISTORY_MD):
        with open(RESEARCH_HISTORY_MD, "r") as f:
            for line in f:
                m = re.match(r"^## Iteration (\d+)", line)
                if m:
                    max_iter = max(max_iter, int(m.group(1)))
    return max_iter


def append_research_log(row: dict):
    file_exists = os.path.exists(RESEARCH_LOG_CSV)
    fieldnames = [
        "iteration", "timestamp", "branch",
        "vehicles", "distance", "time_ms",
        "gap_pct", "improves_quality", "improves_time", "kept",
        "summary",
    ]
    with open(RESEARCH_LOG_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def append_history(text: str):
    with open(RESEARCH_HISTORY_MD, "a") as f:
        f.write(text)


def trim_history_for_planner(history_text: str) -> str:
    """Keep all signal entries (finite results) + last MAX_HISTORY_FAILURES failure entries.

    Signal entries contain real data (finite vehicles/distance) and are always kept regardless
    of age — they prevent the planner cycling back to known-bad or known-good territory.
    Failure entries (Inf quality values) carry little signal beyond "this recently failed";
    we cap them so a long compile-fail chain doesn't drown the planner's context.
    """
    blocks = [b.strip() for b in history_text.split("\n---\n") if b.strip()]
    signal  = [b for b in blocks if "Vehicles: Inf" not in b and "Distance: Inf" not in b]
    failures = [b for b in blocks if "Vehicles: Inf" in b or "Distance: Inf" in b]
    kept = signal + failures[-MAX_HISTORY_FAILURES:]

    def iter_num(block):
        m = re.search(r"## Iteration (\d+)", block)
        return int(m.group(1)) if m else 0

    kept.sort(key=iter_num)
    return ("\n\n---\n\n".join(kept) + "\n\n---\n") if kept else ""


def commit_log_to_main(iteration, branch_name, timestamp):
    """Commit research_log.csv and research_history.md updates to main."""
    run_bash(f"git add {RESEARCH_LOG_CSV} {RESEARCH_HISTORY_MD}")
    run_bash(f'git commit -m "LOG [{iteration}]: update research log ({branch_name})"')
    run_bash("git push origin main")


# ---------------------------------------------------------------------------
# Graphs
# ---------------------------------------------------------------------------

def generate_graphs():
    if not os.path.exists(RESEARCH_LOG_CSV):
        return
    os.makedirs(GRAPHS_DIR, exist_ok=True)

    rows = []
    with open(RESEARCH_LOG_CSV, "r") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    if not rows:
        return

    iterations = [int(r["iteration"]) for r in rows]
    distances  = [float(r["distance"]) if r.get("distance") else None for r in rows]
    times_ms   = [float(r["time_ms"]) if r.get("time_ms") else None for r in rows]
    iq = [r["improves_quality"] == "True" for r in rows]
    # kept: True if solution was accepted (quality improved OR faster without quality regression).
    # Falls back to iq for CSVs written before the kept column was added.
    kept = [r.get("kept", str(iq[i])) == "True" for i, r in enumerate(rows)]

    def colour(i):
        return "#2ecc71" if kept[i] else "#cccccc"

    colours = [colour(i) for i in range(len(rows))]

    kept_iters = [iterations[i] for i in range(len(rows)) if kept[i] and distances[i] is not None]
    kept_dists  = [distances[i]  for i in range(len(rows)) if kept[i] and distances[i] is not None]
    kept_times  = [times_ms[i]   for i in range(len(rows)) if kept[i] and times_ms[i] is not None]

    green_patch = mpatches.Patch(color="#2ecc71", label="Kept (quality or runtime improvement)")
    grey_patch  = mpatches.Patch(color="#cccccc", label="Discarded")

    def dot_label(row):
        """Return N_descriptor from branch name, e.g. experiment/3_tabu-search -> 3_tabu-search."""
        branch = row.get("branch", "")
        return branch.split("/")[-1] if "/" in branch else str(row.get("iteration", ""))

    # --- Distance vs Iteration ---
    fig, ax = plt.subplots(figsize=(12, 5))
    valid = [(iterations[i], distances[i], colours[i]) for i in range(len(rows)) if distances[i] is not None]
    if valid:
        xi, yi, ci = zip(*valid)
        ax.scatter(xi, yi, c=ci, s=40, zorder=3)
    for i in range(len(rows)):
        if kept[i] and distances[i] is not None:
            ax.annotate(dot_label(rows[i]), (iterations[i], distances[i]),
                        textcoords="offset points", xytext=(5, 4),
                        fontsize=7, color="#1a7a40", zorder=5)
    if kept_iters:
        ax.plot(kept_iters, kept_dists, color="#27ae60", linewidth=2, zorder=4)
    ax.axhline(BKS_DISTANCE, color="#e74c3c", linestyle="--", linewidth=1.2)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Total Distance")
    ax.set_title("Solution Quality vs Iteration")
    ax.legend(handles=[
        green_patch, grey_patch,
        plt.Line2D([0], [0], color="#27ae60", linewidth=2, label="Kept frontier"),
        plt.Line2D([0], [0], color="#e74c3c", linestyle="--", label=f"BKS {BKS_DISTANCE}"),
    ])
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, "distance_vs_iteration.png"), dpi=120)
    plt.close()

    # --- Runtime vs Iteration ---
    fig, ax = plt.subplots(figsize=(12, 5))
    valid_t = [(iterations[i], times_ms[i], colours[i]) for i in range(len(rows)) if times_ms[i] is not None]
    if valid_t:
        xi, yi, ci = zip(*valid_t)
        ax.scatter(xi, yi, c=ci, s=40, zorder=3)
    for i in range(len(rows)):
        if kept[i] and times_ms[i] is not None:
            ax.annotate(dot_label(rows[i]), (iterations[i], times_ms[i]),
                        textcoords="offset points", xytext=(5, 4),
                        fontsize=7, color="#1a5276", zorder=5)
    if kept_iters:
        ax.plot(kept_iters, kept_times, color="#2980b9", linewidth=2, zorder=4)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Runtime (ms)")
    ax.set_title("Solver Runtime vs Iteration")
    ax.legend(handles=[
        green_patch, grey_patch,
        plt.Line2D([0], [0], color="#2980b9", linewidth=2, label="Runtime of kept solutions"),
    ])
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, "runtime_vs_iteration.png"), dpi=120)
    plt.close()

    # --- Quality vs Runtime (Pareto scatter) ---
    fig, ax = plt.subplots(figsize=(8, 6))
    valid_p = [
        (times_ms[i], distances[i], colours[i], rows[i])
        for i in range(len(rows))
        if times_ms[i] is not None and distances[i] is not None
    ]
    if valid_p:
        xt, yd, cp, _ = zip(*valid_p)
        ax.scatter(xt, yd, c=cp, s=60, zorder=3)
        for t, d, _, row in valid_p:
            ax.annotate(dot_label(row), (t, d),
                        textcoords="offset points", xytext=(5, 4),
                        fontsize=7, color="#555555", zorder=5)
    ax.axhline(BKS_DISTANCE, color="#e74c3c", linestyle="--", linewidth=1.2,
               label=f"BKS {BKS_DISTANCE}")
    ax.set_xlabel("Runtime (ms)")
    ax.set_ylabel("Total Distance")
    ax.set_title("Solution Quality vs Runtime")
    ax.legend(handles=[
        green_patch, grey_patch,
        plt.Line2D([0], [0], color="#e74c3c", linestyle="--", label=f"BKS {BKS_DISTANCE}"),
    ])
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, "quality_vs_runtime.png"), dpi=120)
    plt.close()


# ---------------------------------------------------------------------------
# README graph block update
# ---------------------------------------------------------------------------

def update_readme_graphs():
    if not os.path.exists("README.md"):
        return
    with open("README.md", "r") as f:
        content = f.read()
    marker_start = "<!-- GRAPHS_START -->"
    marker_end   = "<!-- GRAPHS_END -->"
    graph_block = (
        f"{marker_start}\n"
        "## Progress Graphs\n\n"
        "![Distance vs Iteration](graphs/distance_vs_iteration.png)\n\n"
        "![Runtime vs Iteration](graphs/runtime_vs_iteration.png)\n\n"
        "![Quality vs Runtime](graphs/quality_vs_runtime.png)\n"
        f"{marker_end}"
    )
    if marker_start in content and marker_end in content:
        before = content.split(marker_start)[0]
        after  = content.split(marker_end)[1]
        new_content = before + graph_block + after
    else:
        new_content = content + "\n\n" + graph_block + "\n"
    with open("README.md", "w") as f:
        f.write(new_content)


# ---------------------------------------------------------------------------
# Graceful exit
# ---------------------------------------------------------------------------

def graceful_exit(sig, frame):
    print("\n>>> Interrupted. Checking out main and exiting.")
    run_bash("git checkout main")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_exit)


# ---------------------------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------------------------

os.makedirs(GRAPHS_DIR, exist_ok=True)

print("=== VRPTW Auto-Research Loop ===")
print(f"Planner: {PLANNER} | Coder: {CODER}")
print(f"Max iterations: {MAX_ITERATIONS if MAX_ITERATIONS > 0 else 'unlimited'} | Solver cap: {SOLVER_TIMEOUT_S}s")

# ---------------------------------------------------------------------------
# Bootstrap: if no baseline exists, run the current solver once to seed files
# ---------------------------------------------------------------------------
if not os.path.exists(BEST_RESULT_JSON):
    print("\n[Bootstrap] No baseline found. Running current solver to establish baseline...")
    run_bash("cargo build --release 2>&1")
    try:
        solver_out, _ = run_bash(
            f"./target/release/vrptw_autoresearch {INSTANCE_PATH}",
            timeout=SOLVER_TIMEOUT_S
        )
    except subprocess.TimeoutExpired:
        print("!!! Bootstrap solver timed out. Cannot establish baseline. Exiting.")
        sys.exit(1)

    bv, bd, bt = parse_solver_output(solver_out)
    if bv is None or bd is None or bt is None:
        print("!!! Bootstrap solver produced no output. Exiting.")
        print(solver_out[:800])
        sys.exit(1)

    gap_pct = round((bd - BKS_DISTANCE) / BKS_DISTANCE * 100, 4)
    print(f"[Bootstrap] Baseline: {bv}v / {bd:.2f} / {bt:.0f}ms / gap {gap_pct:.2f}%")

    save_best_result(bv, bd, bt, 0, "main")
    append_research_log({
        "iteration":        0,
        "timestamp":        time.strftime("%Y-%m-%dT%H:%M:%S"),
        "branch":           "main",
        "vehicles":         bv,
        "distance":         bd,
        "time_ms":          bt,
        "gap_pct":          gap_pct,
        "improves_quality": True,
        "improves_time":    True,
        "kept":             True,
        "summary":          "Baseline: Regret-2 + vehicle reduction + 2-opt + Or-opt(1/2/3)",
    })
    append_history(
        f"## Iteration 0 (Baseline) — {time.strftime('%Y-%m-%dT%H:%M:%S')}\n"
        f"Branch: `main`\n"
        f"Result: {bv}v / {bd:.2f} / {bt:.0f}ms / gap {gap_pct:.2f}%\n"
        f"Construction: Regret-2 + vehicle reduction + 2-opt + Or-opt(1/2/3)\n\n---\n"
    )
    generate_graphs()
    update_readme_graphs()
    run_bash(f"git add {RESEARCH_LOG_CSV} {RESEARCH_HISTORY_MD} {BEST_RESULT_JSON} graphs/ README.md")
    run_bash('git commit -m "LOG [0]: baseline seeded"')
    run_bash("git push origin main")
    print("[Bootstrap] Baseline seeded and committed to main.\n")

loop_iteration = get_iteration_count()
iterations_done = 0

# Load static system prompts once
SYS_PLANNER = load_prompt("sys_planner")
SYS_CODER   = load_prompt("sys_coder")
SYS_REPAIR  = load_prompt("sys_repair")

while True:
    if MAX_ITERATIONS > 0 and iterations_done >= MAX_ITERATIONS:
        print(f">>> Reached {MAX_ITERATIONS} iterations. Stopping.")
        break

    loop_iteration += 1
    iterations_done += 1
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

    # -----------------------------------------------------------------------
    # Start on main; read state
    # -----------------------------------------------------------------------
    run_bash("git checkout main")

    best = load_best_result()
    base_vehicles = best["vehicles"] if best else 9999
    base_distance = best["distance"] if best else float("inf")
    base_time_ms  = best["time_ms"]  if best else float("inf")

    with open("src/solver.rs", "r") as f:
        current_solver_code = f.read()

    prior_history = ""
    if os.path.exists(RESEARCH_HISTORY_MD):
        with open(RESEARCH_HISTORY_MD, "r") as f:
            prior_history = trim_history_for_planner(f.read())

    # -----------------------------------------------------------------------
    # PHASE 1: PLANNING (Qwen) — runs on main before branch is created
    # -----------------------------------------------------------------------
    print(f"\n>>> Iteration {loop_iteration}")
    print(f"    Baseline: {base_vehicles}v / {base_distance:.2f} / {base_time_ms:.0f}ms")
    print(f"[{PLANNER}] Devising strategy...")

    user_planner = (
        f"PRIOR RESEARCH HISTORY:\n{prior_history or '(none yet — this is the first iteration)'}\n\n"
        f"CURRENT src/solver.rs (the ONLY file you should propose changes to):\n{current_solver_code}\n\n"
        f"CURRENT BEST PERFORMANCE:\n"
        f"  Vehicles : {base_vehicles}\n"
        f"  Distance : {base_distance:.2f}\n"
        f"  Runtime  : {base_time_ms:.0f} ms"
    )

    try:
        plan = call_local_llm(
            PLANNER, SYS_PLANNER, user_planner,
            nudge="Your previous attempt failed or was interrupted. Please be more concise — "
                  "keep reasoning brief and focus on a single, clearly scoped implementation plan.",
        )
    except Exception as e:
        print(f"!!! Planner failed after {LLM_RETRY_ATTEMPTS} attempts: {e}")
        force_unload(PLANNER)
        append_history(
            f"\n## Iteration {loop_iteration} — {timestamp}\n"
            f"Branch: (none — planner failed before branch creation)\n"
            f"Proposal: (none)\n"
            f"Result: PLANNER LLM FAILURE — {type(e).__name__}\n"
            f"Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf\n"
            f"Decision: DISCARDED\n\n---\n"
        )
        run_bash(f"git add {RESEARCH_HISTORY_MD}")
        run_bash(f'git commit -m "LOG [{loop_iteration}]: planner-failed"')
        run_bash("git push origin main")
        time.sleep(COOLDOWN_S)
        continue
    force_unload(PLANNER)

    descriptor, summary = parse_plan_header(plan)
    branch_name = f"experiment/{loop_iteration}_{descriptor}"
    print(f"    Branch: {branch_name}")
    print(f"    Proposal: {summary}")

    # -----------------------------------------------------------------------
    # Create experiment branch; write the plan into it (not into main)
    # -----------------------------------------------------------------------
    run_bash(f"git checkout -b {branch_name}")

    with open(EXPERIMENT_PLAN_MD, "w") as f:
        f.write(plan)

    # -----------------------------------------------------------------------
    # PHASE 2: CODING (Qwen)
    # -----------------------------------------------------------------------
    print(f"[{CODER}] Implementing...")

    try:
        new_code_raw = call_local_llm(
            CODER, SYS_CODER,
            f"IMPLEMENTATION PLAN:\n{plan}\n\nCURRENT src/solver.rs:\n{current_solver_code}",
            nudge="Your previous attempt failed. Return ONLY a single ```rust``` code block "
                  "containing the complete src/solver.rs — no explanations, no stubs.",
        )
    except Exception as e:
        print(f"!!! Coder failed after {LLM_RETRY_ATTEMPTS} attempts: {e}")
        force_unload(CODER)
        run_bash("git add experiment_plan.md")
        run_bash(f'git commit -m "CODER-FAILED [{loop_iteration}]: {descriptor}"')
        run_bash(f"git push origin {branch_name}")
        run_bash("git checkout main")
        append_history(
            f"\n## Iteration {loop_iteration} — {timestamp}\n"
            f"Branch: `{branch_name}`\n"
            f"Proposal: {summary}\n"
            f"Result: CODER LLM FAILURE — {type(e).__name__}\n"
            f"Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf\n"
            f"Decision: DISCARDED\n\n---\n"
        )
        run_bash(f"git add {RESEARCH_HISTORY_MD}")
        run_bash(f'git commit -m "LOG [{loop_iteration}]: coder-failed ({branch_name})"')
        run_bash("git push origin main")
        time.sleep(COOLDOWN_S)
        continue

    clean_code = extract_rust_code(new_code_raw)
    with open("src/solver.rs", "w") as f:
        f.write(clean_code)

    compiled_successfully = False
    last_compile_errors = ""
    for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
        print(f"[Compiler] Attempt {attempt}/{MAX_REPAIR_ATTEMPTS}...")
        output, rc = run_bash("cargo check 2>&1")
        if rc == 0:
            print(">>> Compiled successfully.")
            compiled_successfully = True
            break

        last_compile_errors = output
        print(f"    Compile failed. Sending errors to {CODER}...")
        with open("src/solver.rs", "r") as f:
            broken_code = f.read()

        try:
            repair_raw = call_local_llm(
                CODER, SYS_REPAIR,
                f"COMPILER ERRORS:\n{output}\n\nBROKEN src/solver.rs:\n{broken_code}",
                nudge="Your previous attempt failed. Fix ALL errors and return ONLY a single ```rust``` block.",
            )
        except Exception as e:
            print(f"    [LLM] Repair call failed: {type(e).__name__}: {e}. Counting as failed attempt.")
            continue
        clean_code = extract_rust_code(repair_raw)
        with open("src/solver.rs", "w") as f:
            f.write(clean_code)

    force_unload(CODER)

    if not compiled_successfully:
        # Truncate errors to first 25 lines so the planner can read the root cause
        # without the history entry becoming too large.
        error_lines = last_compile_errors.strip().splitlines()
        error_snippet = "\n".join(error_lines[:25])
        if len(error_lines) > 25:
            error_snippet += f"\n... ({len(error_lines) - 25} more lines)"

        print(">>> Max repair attempts reached. Archiving branch for manual review.")
        run_bash("git add src/solver.rs experiment_plan.md")
        run_bash(f'git commit -m "FAILED COMPILE [{loop_iteration}]: {descriptor}"')
        run_bash(f"git push origin {branch_name}")
        run_bash("git checkout main")
        append_history(
            f"\n## Iteration {loop_iteration} — {timestamp}\n"
            f"Branch: `{branch_name}`\n"
            f"Proposal: {summary}\n"
            f"Result: FAILED COMPILE — exhausted {MAX_REPAIR_ATTEMPTS} repair attempts\n"
            f"Compile errors (last attempt):\n```\n{error_snippet}\n```\n"
            f"Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf\n"
            f"Decision: DISCARDED\n\n---\n"
        )
        run_bash(f"git add {RESEARCH_HISTORY_MD}")
        run_bash(f'git commit -m "LOG [{loop_iteration}]: compile-fail ({branch_name})"')
        run_bash("git push origin main")
        time.sleep(COOLDOWN_S)
        continue

    # -----------------------------------------------------------------------
    # PHASE 3: BUILD & RUN
    # -----------------------------------------------------------------------
    print("[Solver] Building release binary...")
    build_out, build_rc = run_bash("cargo build --release 2>&1")
    if build_rc != 0:
        print("!!! Release build failed after cargo check passed. Archiving.")
        run_bash("git add src/solver.rs experiment_plan.md")
        run_bash(f'git commit -m "FAILED BUILD [{loop_iteration}]: {descriptor}"')
        run_bash(f"git push origin {branch_name}")
        run_bash("git checkout main")
        append_history(
            f"\n## Iteration {loop_iteration} — {timestamp}\n"
            f"Branch: `{branch_name}`\n"
            f"Proposal: {summary}\n"
            f"Result: FAILED RELEASE BUILD — cargo check passed but cargo build --release failed\n"
            f"Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf\n"
            f"Decision: DISCARDED\n\n---\n"
        )
        run_bash(f"git add {RESEARCH_HISTORY_MD}")
        run_bash(f'git commit -m "LOG [{loop_iteration}]: build-fail ({branch_name})"')
        run_bash("git push origin main")
        time.sleep(COOLDOWN_S)
        continue

    print(f"[Solver] Running on RC1_4_1 (timeout {SOLVER_TIMEOUT_S}s)...")
    try:
        solver_out, _ = run_bash(
            f"./target/release/vrptw_autoresearch {INSTANCE_PATH}",
            timeout=SOLVER_TIMEOUT_S
        )
    except subprocess.TimeoutExpired:
        print("!!! Solver timed out. Archiving branch.")
        run_bash("git add experiment_plan.md src/solver.rs")
        run_bash(f'git commit -m "TIMEOUT [{loop_iteration}]: {descriptor}"')
        run_bash(f"git push origin {branch_name}")
        run_bash("git checkout main")
        append_history(
            f"\n## Iteration {loop_iteration} — {timestamp}\n"
            f"Branch: `{branch_name}`\n"
            f"Proposal: {summary}\n"
            f"Result: TIMEOUT — solver exceeded {SOLVER_TIMEOUT_S}s\n"
            f"Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf\n"
            f"Decision: DISCARDED\n\n---\n"
        )
        run_bash(f"git add {RESEARCH_HISTORY_MD}")
        run_bash(f'git commit -m "LOG [{loop_iteration}]: timeout ({branch_name})"')
        run_bash("git push origin main")
        time.sleep(COOLDOWN_S)
        continue

    new_vehicles, new_distance, new_time_ms = parse_solver_output(solver_out)

    if new_vehicles is None or new_distance is None or new_time_ms is None:
        print("!!! Solver produced no parseable output. Archiving branch.")
        print(solver_out[:800])
        run_bash("git add experiment_plan.md src/solver.rs")
        run_bash(f'git commit -m "NO-OUTPUT [{loop_iteration}]: {descriptor}"')
        run_bash(f"git push origin {branch_name}")
        run_bash("git checkout main")
        append_history(
            f"\n## Iteration {loop_iteration} — {timestamp}\n"
            f"Branch: `{branch_name}`\n"
            f"Proposal: {summary}\n"
            f"Result: NO PARSEABLE OUTPUT\n"
            f"Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf\n"
            f"Decision: DISCARDED\n\n---\n"
        )
        run_bash(f"git add {RESEARCH_HISTORY_MD}")
        run_bash(f'git commit -m "LOG [{loop_iteration}]: no-output ({branch_name})"')
        run_bash("git push origin main")
        time.sleep(COOLDOWN_S)
        continue

    gap_pct = round((new_distance - BKS_DISTANCE) / BKS_DISTANCE * 100, 4)
    print(f"    Result: {new_vehicles}v / {new_distance:.2f} / {new_time_ms:.0f}ms / gap {gap_pct:.2f}%")

    # -----------------------------------------------------------------------
    # PHASE 3b: FEASIBILITY VALIDATION
    # -----------------------------------------------------------------------
    print("[Validator] Checking feasibility...")
    validator_out, validator_rc = run_bash(
        f"python3 validate.py {INSTANCE_PATH} {SOLUTION_FILE}"
    )
    first_line = validator_out.strip().splitlines()[0] if validator_out.strip() else "(no output)"
    print(f"    {first_line}")

    if validator_rc != 0:
        print("!!! Solution infeasible. Archiving branch.")
        run_bash(f"git add experiment_plan.md src/solver.rs {SOLUTION_FILE}")
        run_bash(f'git commit -m "INFEASIBLE [{loop_iteration}]: {descriptor}"')
        run_bash(f"git push origin {branch_name}")
        run_bash("git checkout main")
        append_history(
            f"\n## Iteration {loop_iteration} — {timestamp}\n"
            f"Branch: `{branch_name}`\n"
            f"Proposal: {summary}\n"
            f"Result: INFEASIBLE — solver ran but solution violates constraints\n"
            f"Vehicles: {new_vehicles}  Distance: {new_distance:.2f}  "
            f"Time: {new_time_ms:.0f}ms  Gap: {gap_pct:.2f}%\n"
            f"Violations:\n{validator_out.strip()}\n"
            f"Decision: DISCARDED\n\n---\n"
        )
        run_bash(f"git add {RESEARCH_HISTORY_MD}")
        run_bash(f'git commit -m "LOG [{loop_iteration}]: infeasible ({branch_name})"')
        run_bash("git push origin main")
        time.sleep(COOLDOWN_S)
        continue

    # -----------------------------------------------------------------------
    # PHASE 4: ACCEPT / REJECT
    # -----------------------------------------------------------------------
    quality_improved  = is_better_solution(new_vehicles, new_distance, base_vehicles, base_distance)
    quality_worsened  = solution_worsened(new_vehicles, new_distance, base_vehicles, base_distance)
    time_improved     = new_time_ms < base_time_ms
    keep = quality_improved or (time_improved and not quality_worsened)

    log_row = {
        "iteration":        loop_iteration,
        "timestamp":        timestamp,
        "branch":           branch_name,
        "vehicles":         new_vehicles,
        "distance":         new_distance,
        "time_ms":          new_time_ms,
        "gap_pct":          gap_pct,
        "improves_quality": quality_improved,
        "improves_time":    time_improved,
        "kept":             keep,
        "summary":          summary,
    }
    history_entry = (
        f"\n## Iteration {loop_iteration} — {timestamp}\n"
        f"Branch: `{branch_name}`\n"
        f"Proposal: {summary}\n"
        f"Result: {new_vehicles}v / {new_distance:.2f} / {new_time_ms:.0f}ms / gap {gap_pct:.2f}%\n"
        f"Decision: {'KEPT' if keep else 'DISCARDED'} "
        f"(quality_improved={quality_improved}, time_improved={time_improved})\n\n---\n"
    )

    if keep:
        reason = "quality improved" if quality_improved else "runtime improved (no quality regression)"
        print(f"*** KEEPING ({reason}). Applying to main.")
        save_best_result(new_vehicles, new_distance, new_time_ms, loop_iteration, branch_name)
        append_research_log(log_row)
        append_history(history_entry)
        generate_graphs()
        update_readme_graphs()
        # Commit everything (including experiment_plan.md) to the experiment branch for reference
        run_bash("git add .")
        run_bash(
            f'git commit -m "IMPROVEMENT [{loop_iteration}]: '
            f'{new_vehicles}v {new_distance:.2f}dist {new_time_ms:.0f}ms ({descriptor})"'
        )
        # Push the experiment branch so experiment_plan.md is preserved on origin
        run_bash(f"git push origin {branch_name}")
        # Apply only the files we want to main — experiment_plan.md stays on the branch
        run_bash("git checkout main")
        run_bash(f"git checkout {branch_name} -- src/solver.rs")
        run_bash(f"git checkout {branch_name} -- {SOLUTION_FILE}")
        run_bash(f"git checkout {branch_name} -- {BEST_RESULT_JSON}")
        run_bash(f"git checkout {branch_name} -- {RESEARCH_LOG_CSV}")
        run_bash(f"git checkout {branch_name} -- {RESEARCH_HISTORY_MD}")
        run_bash(f"git checkout {branch_name} -- graphs/")
        run_bash(f"git checkout {branch_name} -- README.md")
        run_bash(
            f'git commit -m "IMPROVEMENT [{loop_iteration}]: '
            f'{new_vehicles}v {new_distance:.2f}dist {new_time_ms:.0f}ms ({descriptor})"'
        )
        run_bash("git push origin main")
    else:
        print(f"--- Not dominant. Archiving branch.")
        # Commit experiment results to the experiment branch
        append_research_log(log_row)
        append_history(history_entry)
        generate_graphs()
        run_bash("git add .")
        run_bash(
            f'git commit -m "ARCHIVE [{loop_iteration}]: '
            f'{new_vehicles}v {new_distance:.2f}dist {new_time_ms:.0f}ms ({descriptor})"'
        )
        run_bash(f"git push origin {branch_name}")
        # Switch to main and re-apply the log entries so main is always complete
        run_bash("git checkout main")
        append_research_log(log_row)
        append_history(history_entry)
        generate_graphs()
        commit_log_to_main(loop_iteration, branch_name, timestamp)

    print(f"[Loop] Cooling down {COOLDOWN_S}s...")
    time.sleep(COOLDOWN_S)

print("=== Auto-research loop complete ===")
