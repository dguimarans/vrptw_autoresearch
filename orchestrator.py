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

# --- CONFIGURATION ---
PLANNER         = "deepseek-headless"
CODER           = "qwen2.5-coder-headless"
OLLAMA_URL      = "http://localhost:11434/v1/chat/completions"
OLLAMA_HEALTH_URL = "http://localhost:11434/api/tags"
UNLOAD_URL      = "http://localhost:11434/api/generate"
MAX_REPAIR_ATTEMPTS  = 3
LLM_RETRY_ATTEMPTS   = 3
MAX_ITERATIONS       = 63
MAX_HISTORY_FAILURES = 3
SOLVER_TIMEOUT_S     = 4800
LLM_TIMEOUT_S        = 7200
COOLDOWN_S           = 10
SOLVER_LANGUAGE      = "python"
SOLVER_SCRIPT        = "vrptw.py"    # entry point (read-only infrastructure)
SOLVER_FILE          = "solver.py"   # AI-managed heuristics
VENV_DIR             = "venv"
PYTHON               = None   # resolved by ensure_venv() at startup; do not set manually
INSTANCE_PATH   = "instances/homberger_400_customer_instances/RC1_4_1.TXT"
BKS_DISTANCE    = 8522.90
BKS_VEHICLES    = 36
RESEARCH_LOG_CSV    = "research_log.csv"
BEST_RESULT_JSON    = "best_result.json"
RESEARCH_HISTORY_MD = "research_history.md"
EXPERIMENT_PLAN_JSON = "experiment_plan.json"
SOLUTION_FILE       = "solution.txt"
GRAPHS_DIR          = "graphs"
PROMPTS_DIR         = "prompts"


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


def check_ollama_health() -> bool:
    """Return True if Ollama API is reachable and responding."""
    try:
        r = requests.get(OLLAMA_HEALTH_URL, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def ensure_ollama_or_exit():
    """Check Ollama health; attempt one restart if down; exit if unrecoverable."""
    if check_ollama_health():
        return
    print("\n!!! Ollama is not responding. Attempting restart via systemctl...")
    run_bash("sudo systemctl restart ollama")
    print("    Waiting 30s for Ollama to come back up...")
    time.sleep(30)
    if check_ollama_health():
        print("    Ollama recovered. Continuing.")
        return
    print("!!! Ollama did not recover. Exiting loop — restart Ollama manually and re-run.")
    run_bash("git checkout main")
    sys.exit(1)


# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

def call_local_llm(model, system_prompt, user_content, nudge=None, temperature=0.2,
                   json_mode=False):
    last_exc = None
    for attempt in range(1, LLM_RETRY_ATTEMPTS + 1):
        try:
            content = (f"{nudge}\n\n{user_content}" if nudge and attempt > 1 else user_content)
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": content},
                ],
                "temperature": temperature,
            }
            if json_mode:
                payload["response_format"] = {"type": "json_object"}  # hint only — not reliable on 7B
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
# Python code extraction
# ---------------------------------------------------------------------------

def extract_python_code(raw_text: str) -> str:
    if "```python" in raw_text:
        return raw_text.split("```python")[1].split("```")[0].strip()
    if "```" in raw_text:
        parts = raw_text.split("```")
        if len(parts) >= 3:
            return parts[1].strip()
    return raw_text.strip()


# ---------------------------------------------------------------------------
# Python dependency management
# ---------------------------------------------------------------------------

def ensure_venv():
    """Resolve the Python interpreter to use. Prefers a venv; falls back to system python3."""
    global PYTHON
    if PYTHON is not None:
        return
    venv_python = os.path.join(VENV_DIR, "bin", "python")
    if os.path.exists(venv_python):
        PYTHON = venv_python
        return
    # Try to create the venv
    print(f"    [venv] Creating virtual environment at {VENV_DIR}...")
    out, rc = run_bash(f"python3 -m venv {VENV_DIR} 2>&1")
    if rc == 0:
        PYTHON = venv_python
    else:
        print(f"    [venv] WARNING: venv creation failed ({out.strip()[:120]})")
        print(f"    [venv] Falling back to system python3. Run: sudo apt install python3-venv")
        PYTHON = "python3"


def apply_python_dependencies(code: str):
    """Parse '# DEPENDENCY: package_name' comments and pip-install."""
    ensure_venv()
    pip_cmd = (
        os.path.join(VENV_DIR, "bin", "pip")
        if os.path.exists(os.path.join(VENV_DIR, "bin", "pip"))
        else "pip3 --user"
    )
    installed_out, _ = run_bash(f"{pip_cmd} list --format=columns 2>/dev/null")
    installed_lower = installed_out.lower()
    for line in code.splitlines():
        m = re.match(r"#\s*DEPENDENCY:\s*(\S+)", line)
        if not m:
            continue
        pkg = m.group(1)
        if pkg.lower().replace("-", "_") in installed_lower or pkg.lower() in installed_lower:
            continue
        print(f"    [deps] Installing {pkg}...")
        out, rc = run_bash(f"{pip_cmd} install {pkg} 2>&1")
        if rc != 0:
            print(f"    [deps] WARNING: pip install {pkg} failed: {out[:200]}")


# ---------------------------------------------------------------------------
# Planner JSON parsing
# ---------------------------------------------------------------------------

def parse_plan_json(raw: str) -> dict:
    """Extract and parse the JSON plan from planner output.
    Strips DeepSeek-R1 <think>...</think> blocks, locates the JSON object,
    and applies two repair passes before giving up:
      1. Close any unclosed braces/brackets (truncated response).
      2. Strip trailing commas (most common small-model mistake).
    Raises ValueError if parsing still fails or required fields are absent."""
    text = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        candidate = m.group(0)
    else:
        # No closing brace — response was truncated. Find the opening brace
        # and close any unclosed structure.
        start = text.find("{")
        if start == -1:
            raise ValueError(f"No JSON object found in planner output:\n{raw[:400]}")
        candidate = text[start:].rstrip()
        open_braces   = candidate.count("{") - candidate.count("}")
        open_brackets = candidate.count("[") - candidate.count("]")
        candidate += "]" * max(0, open_brackets) + "}" * max(0, open_braces)

    for attempt in (candidate, re.sub(r",\s*([}\]])", r"\1", candidate)):
        try:
            plan = json.loads(attempt)
            break
        except json.JSONDecodeError:
            pass
    else:
        raise ValueError(f"JSON repair failed. Candidate:\n{candidate[:400]}")

    required = {"descriptor", "summary", "implementation"}
    missing = required - set(plan.keys())
    if missing:
        raise ValueError(
            f"Plan JSON missing required fields: {missing}. Got keys: {list(plan.keys())}"
        )
    return plan


def sanitise_descriptor(descriptor: str) -> str:
    descriptor = re.sub(r"[^a-zA-Z0-9_\-]", "-", descriptor).strip("-").lower()
    descriptor = re.sub(r"-{2,}", "-", descriptor)
    return descriptor or f"iter-{int(time.time())}"


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
        "vehicles":  vehicles,
        "distance":  distance,
        "time_ms":   time_ms,
        "iteration": iteration,
        "branch":    branch,
        "language":  SOLVER_LANGUAGE,
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


LOG_FIELDNAMES = [
    "iteration", "timestamp", "branch",
    "vehicles", "distance", "time_ms",
    "gap_pct", "improves_quality", "improves_time", "kept",
    "language", "summary",
]


def migrate_research_log():
    """Add 'language' column to existing research_log.csv if missing."""
    if not os.path.exists(RESEARCH_LOG_CSV):
        return
    with open(RESEARCH_LOG_CSV, "r") as f:
        reader = csv.DictReader(f)
        if "language" in (reader.fieldnames or []):
            return
        rows = list(reader)
    with open(RESEARCH_LOG_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            row.setdefault("language", "rust")
            writer.writerow(row)
    print("[Migration] Added 'language' column to research_log.csv")


def append_research_log(row: dict):
    file_exists = os.path.exists(RESEARCH_LOG_CSV)
    with open(RESEARCH_LOG_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDNAMES, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def append_history(text: str):
    with open(RESEARCH_HISTORY_MD, "a") as f:
        f.write(text)


def trim_history_for_planner(history_text: str) -> str:
    blocks = [b.strip() for b in history_text.split("\n---\n") if b.strip()]
    signal   = [b for b in blocks if "Vehicles: Inf" not in b and "Distance: Inf" not in b]
    failures = [b for b in blocks if "Vehicles: Inf" in b or "Distance: Inf" in b]
    kept = signal + failures[-MAX_HISTORY_FAILURES:]

    def iter_num(block):
        m = re.search(r"## Iteration (\d+)", block)
        return int(m.group(1)) if m else 0

    kept.sort(key=iter_num)
    return ("\n\n---\n\n".join(kept) + "\n\n---\n") if kept else ""


def commit_log_to_main(iteration, branch_name, timestamp):
    run_bash(f"git add {RESEARCH_LOG_CSV} {RESEARCH_HISTORY_MD} graphs/ README.md")
    run_bash(f'git commit -m "LOG [{iteration}]: update research log ({branch_name})"')
    run_bash("git push origin main")


# ---------------------------------------------------------------------------
# Graphs
# ---------------------------------------------------------------------------

LANG_MARKER     = {"rust": "o", "python": "s"}
LANG_LINE_COLOR = {"rust": "#d35400", "python": "#1a5276"}
LANG_DOT_KEPT   = {"rust": "#e67e22", "python": "#2980b9"}


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

    def safe_float(val):
        try:
            return float(val) if val not in (None, "", "None", "inf", "Inf") else None
        except (TypeError, ValueError):
            return None

    iterations = [int(r["iteration"]) for r in rows]
    distances  = [safe_float(r.get("distance")) for r in rows]
    times_ms   = [safe_float(r.get("time_ms"))  for r in rows]
    languages  = [r.get("language", "rust") for r in rows]
    iq         = [r.get("improves_quality", "False") == "True" for r in rows]
    kept       = [r.get("kept", str(iq[i])) == "True" for i, r in enumerate(rows)]

    def dot_label(row):
        branch = row.get("branch", "")
        return branch.split("/")[-1] if "/" in branch else str(row.get("iteration", ""))

    # --- Distance vs Iteration ---
    fig, ax = plt.subplots(figsize=(12, 5))
    for lang in ["rust", "python"]:
        xi = [iterations[i] for i in range(len(rows)) if languages[i] == lang and distances[i] is not None]
        yi = [distances[i]  for i in range(len(rows)) if languages[i] == lang and distances[i] is not None]
        ci = ["#2ecc71" if kept[i] else "#cccccc"
              for i in range(len(rows)) if languages[i] == lang and distances[i] is not None]
        if xi:
            ax.scatter(xi, yi, c=ci, s=40, marker=LANG_MARKER[lang], label=f"{lang}", zorder=3)
        kx = [iterations[i] for i in range(len(rows)) if languages[i] == lang and kept[i] and distances[i] is not None]
        ky = [distances[i]  for i in range(len(rows)) if languages[i] == lang and kept[i] and distances[i] is not None]
        if kx:
            ax.plot(kx, ky, color=LANG_LINE_COLOR[lang], linewidth=2,
                    label=f"{lang} frontier", zorder=4)
    for i in range(len(rows)):
        if kept[i] and distances[i] is not None:
            ax.annotate(dot_label(rows[i]), (iterations[i], distances[i]),
                        textcoords="offset points", xytext=(5, 4),
                        fontsize=7, color="#1a7a40", zorder=5)
    ax.axhline(BKS_DISTANCE, color="#e74c3c", linestyle="--", linewidth=1.2,
               label=f"BKS {BKS_DISTANCE}")
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Total Distance")
    ax.set_title("Solution Quality vs Iteration")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, "distance_vs_iteration.png"), dpi=120)
    plt.close()

    # --- Runtime vs Iteration (compare within language only) ---
    fig, ax = plt.subplots(figsize=(12, 5))
    for lang in ["rust", "python"]:
        xi = [iterations[i] for i in range(len(rows)) if languages[i] == lang and times_ms[i] is not None]
        yi = [times_ms[i]   for i in range(len(rows)) if languages[i] == lang and times_ms[i] is not None]
        ci = ["#2ecc71" if kept[i] else "#cccccc"
              for i in range(len(rows)) if languages[i] == lang and times_ms[i] is not None]
        if xi:
            ax.scatter(xi, yi, c=ci, s=40, marker=LANG_MARKER[lang], label=f"{lang}", zorder=3)
        kx = [iterations[i] for i in range(len(rows)) if languages[i] == lang and kept[i] and times_ms[i] is not None]
        ky = [times_ms[i]   for i in range(len(rows)) if languages[i] == lang and kept[i] and times_ms[i] is not None]
        if kx:
            ax.plot(kx, ky, color=LANG_LINE_COLOR[lang], linewidth=2,
                    label=f"{lang} frontier", zorder=4)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Runtime (ms)")
    ax.set_title("Solver Runtime vs Iteration  [compare within language only]")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, "runtime_vs_iteration.png"), dpi=120)
    plt.close()

    # --- Quality vs Runtime (Pareto scatter) ---
    fig, ax = plt.subplots(figsize=(8, 6))
    for lang in ["rust", "python"]:
        valid = [(times_ms[i], distances[i], kept[i], rows[i])
                 for i in range(len(rows))
                 if languages[i] == lang and times_ms[i] is not None and distances[i] is not None]
        if valid:
            xt, yd, kp, rs = zip(*valid)
            cp = ["#2ecc71" if k else "#cccccc" for k in kp]
            ax.scatter(xt, yd, c=cp, s=60, marker=LANG_MARKER[lang], label=lang, zorder=3)
            for t, d, _, row in valid:
                ax.annotate(dot_label(row), (t, d),
                            textcoords="offset points", xytext=(5, 4),
                            fontsize=7, color="#555555", zorder=5)
    ax.axhline(BKS_DISTANCE, color="#e74c3c", linestyle="--", linewidth=1.2,
               label=f"BKS {BKS_DISTANCE}")
    ax.set_xlabel("Runtime (ms)")
    ax.set_ylabel("Total Distance")
    ax.set_title("Solution Quality vs Runtime")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, "quality_vs_runtime.png"), dpi=120)
    plt.close()


# ---------------------------------------------------------------------------
# README updates
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


def update_readme_best_result(vehicles, distance, time_ms):
    if not os.path.exists("README.md"):
        return
    gap_pct = round((distance - BKS_DISTANCE) / BKS_DISTANCE * 100, 1)
    with open("README.md", "r") as f:
        content = f.read()
    marker_start = "<!-- BEST_RESULT_START -->"
    marker_end   = "<!-- BEST_RESULT_END -->"
    block = (
        f"{marker_start}\n"
        f"### Current best result on RC1_4\\_1\n\n"
        f"| Metric | Value |\n"
        f"|---|---|\n"
        f"| Vehicles | {vehicles} |\n"
        f"| Total distance | {distance:.2f} |\n"
        f"| Gap to BKS | ~{gap_pct:.1f} % |\n"
        f"| Runtime | ~{time_ms / 1000:.1f} s ({SOLVER_LANGUAGE}) |\n"
        f"{marker_end}"
    )
    if marker_start in content and marker_end in content:
        before = content.split(marker_start)[0]
        after  = content.split(marker_end)[1]
        new_content = before + block + after
    else:
        new_content = content + "\n\n" + block + "\n"
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
ensure_venv()
migrate_research_log()

print("=== VRPTW Auto-Research Loop ===")
print(f"Planner: {PLANNER} | Coder: {CODER} | Language: {SOLVER_LANGUAGE}")
print(f"Max iterations: {MAX_ITERATIONS if MAX_ITERATIONS > 0 else 'unlimited'} | Solver cap: {SOLVER_TIMEOUT_S}s")

# ---------------------------------------------------------------------------
# Bootstrap: run the solver once to seed files (or re-seed on language switch)
# ---------------------------------------------------------------------------

needs_bootstrap = not os.path.exists(BEST_RESULT_JSON)
if not needs_bootstrap:
    _best = load_best_result()
    if _best and _best.get("language", "rust") != SOLVER_LANGUAGE:
        print(f"\n[Bootstrap] Language switched from '{_best.get('language', 'rust')}' "
              f"to '{SOLVER_LANGUAGE}'. Re-running bootstrap to establish new baseline.")
        needs_bootstrap = True

if needs_bootstrap:
    print("\n[Bootstrap] Running solver to establish baseline...")
    apply_python_dependencies(open(SOLVER_FILE).read())
    try:
        solver_out, rc = run_bash(
            f"{PYTHON} {SOLVER_SCRIPT} {INSTANCE_PATH}",
            timeout=SOLVER_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        print("!!! Bootstrap solver timed out. Cannot establish baseline. Exiting.")
        sys.exit(1)

    if rc != 0:
        print(f"!!! Bootstrap solver failed (exit {rc}):")
        print(solver_out[:800])
        sys.exit(1)

    bv, bd, bt = parse_solver_output(solver_out)
    if bv is None or bd is None or bt is None:
        print("!!! Bootstrap solver produced no parseable output. Exiting.")
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
        "language":         SOLVER_LANGUAGE,
        "summary":          "Baseline: Regret-2 + vehicle reduction + 2-opt + Or-opt(1/2/3) + inter-route-2opt",
    })
    append_history(
        f"## Iteration 0 (Baseline — {SOLVER_LANGUAGE}) — {time.strftime('%Y-%m-%dT%H:%M:%S')}\n"
        f"Branch: `main`\n"
        f"Result: {bv}v / {bd:.2f} / {bt:.0f}ms / gap {gap_pct:.2f}%\n"
        f"Construction: Regret-2 + vehicle reduction + 2-opt + Or-opt(1/2/3) + inter-route-2opt\n\n---\n"
    )
    generate_graphs()
    update_readme_graphs()
    update_readme_best_result(bv, bd, bt)
    run_bash(f"git add {RESEARCH_LOG_CSV} {RESEARCH_HISTORY_MD} {BEST_RESULT_JSON} graphs/ README.md {SOLVER_FILE} {SOLVER_SCRIPT}")
    run_bash('git commit -m "LOG [0]: python baseline seeded"')
    run_bash("git push origin main")
    print("[Bootstrap] Baseline seeded and committed to main.\n")

loop_iteration = get_iteration_count()
iterations_done = 0

SYS_PLANNER = load_prompt("sys_planner")
SYS_CODER   = load_prompt("sys_coder")
SYS_REPAIR  = load_prompt("sys_repair")

while True:
    if MAX_ITERATIONS > 0 and iterations_done >= MAX_ITERATIONS:
        print(f">>> Reached {MAX_ITERATIONS} iterations. Stopping.")
        break

    loop_iteration  += 1
    iterations_done += 1
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S")

    # -----------------------------------------------------------------------
    # Health check — exit immediately if Ollama is down
    # -----------------------------------------------------------------------
    ensure_ollama_or_exit()

    # -----------------------------------------------------------------------
    # Start on main; read state
    # -----------------------------------------------------------------------
    run_bash("git checkout main")

    best = load_best_result()
    base_vehicles = best["vehicles"] if best else 9999
    base_distance = best["distance"] if best else float("inf")
    base_time_ms  = best["time_ms"]  if best else float("inf")

    with open(SOLVER_FILE, "r") as f:
        current_solver_code = f.read()

    prior_history = ""
    if os.path.exists(RESEARCH_HISTORY_MD):
        with open(RESEARCH_HISTORY_MD, "r") as f:
            prior_history = trim_history_for_planner(f.read())

    # -----------------------------------------------------------------------
    # PHASE 1: PLANNING
    # -----------------------------------------------------------------------
    print(f"\n>>> Iteration {loop_iteration}")
    print(f"    Baseline: {base_vehicles}v / {base_distance:.2f} / {base_time_ms:.0f}ms")
    print(f"[{PLANNER}] Devising strategy...")

    current_gap_pct = (
        round((base_distance - BKS_DISTANCE) / BKS_DISTANCE * 100, 2)
        if base_distance < float("inf") else float("inf")
    )
    user_planner = (
        f"PRIOR RESEARCH HISTORY:\n{prior_history or '(none yet — this is the first iteration)'}\n\n"
        f"CURRENT {SOLVER_FILE} (the ONLY file you should propose changes to):\n{current_solver_code}\n\n"
        f"CURRENT BEST PERFORMANCE:\n"
        f"  Vehicles : {base_vehicles}\n"
        f"  Distance : {base_distance:.2f}\n"
        f"  Gap to BKS : {current_gap_pct:.2f}% (BKS: {BKS_VEHICLES}v / {BKS_DISTANCE})\n"
        f"  Runtime  : {base_time_ms:.0f} ms"
    )

    try:
        plan_raw = call_local_llm(
            PLANNER, SYS_PLANNER, user_planner,
            nudge="Your previous attempt failed or was interrupted. Be concise — "
                  "return a single valid JSON object only.",
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

    try:
        plan = parse_plan_json(plan_raw)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"!!! Planner produced unparseable JSON: {e}")
        print(f"    Raw output (first 400 chars): {plan_raw[:400]}")
        append_history(
            f"\n## Iteration {loop_iteration} — {timestamp}\n"
            f"Branch: (none — planner JSON parse failed)\n"
            f"Proposal: (none)\n"
            f"Result: PLANNER JSON PARSE FAILURE\n"
            f"Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf\n"
            f"Decision: DISCARDED\n\n---\n"
        )
        run_bash(f"git add {RESEARCH_HISTORY_MD}")
        run_bash(f'git commit -m "LOG [{loop_iteration}]: planner-json-fail"')
        run_bash("git push origin main")
        time.sleep(COOLDOWN_S)
        continue

    descriptor  = sanitise_descriptor(plan.get("descriptor", ""))
    summary     = plan.get("summary", "(no summary provided)")
    reasoning   = plan.get("reasoning", "")
    branch_name = f"experiment/{loop_iteration}_{descriptor}"
    print(f"    Branch: {branch_name}")
    print(f"    Proposal: {summary}")
    if reasoning:
        print(f"    Reasoning: {reasoning[:200]}")

    # Human-readable plan string passed to the coder as context
    impl_steps = plan.get("implementation", [])
    impl_text  = "\n".join(f"{i+1}. {s}" for i, s in enumerate(impl_steps))
    plan_text = (
        f"DESCRIPTOR: {descriptor}\n"
        f"SUMMARY: {summary}\n\n"
        f"REASONING: {reasoning}\n\n"
        f"IMPLEMENTATION:\n{impl_text}"
    )

    # -----------------------------------------------------------------------
    # Create experiment branch; write the plan JSON into it
    # -----------------------------------------------------------------------
    run_bash(f"git checkout -b {branch_name}")

    with open(EXPERIMENT_PLAN_JSON, "w") as f:
        json.dump(plan, f, indent=2)

    # -----------------------------------------------------------------------
    # PHASE 2: CODING
    # -----------------------------------------------------------------------
    print(f"[{CODER}] Implementing...")

    try:
        new_code_raw = call_local_llm(
            CODER, SYS_CODER,
            f"IMPLEMENTATION PLAN:\n{plan_text}\n\nCURRENT {SOLVER_FILE}:\n{current_solver_code}",
            nudge="Your previous attempt failed. Return ONLY a single ```python``` code block "
                  "containing the complete solver.py — no explanations, no stubs.",
            temperature=0.0,
        )
    except Exception as e:
        print(f"!!! Coder failed after {LLM_RETRY_ATTEMPTS} attempts: {e}")
        force_unload(CODER)
        run_bash(f"git add {EXPERIMENT_PLAN_JSON}")
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

    new_code = extract_python_code(new_code_raw)
    apply_python_dependencies(new_code)
    with open(SOLVER_FILE, "w") as f:
        f.write(new_code)

    # -----------------------------------------------------------------------
    # PHASE 3: RUN (with repair loop on failure)
    # -----------------------------------------------------------------------
    ran_successfully = False
    last_error       = ""
    new_vehicles = new_distance = new_time_ms = None

    for attempt in range(1, MAX_REPAIR_ATTEMPTS + 1):
        print(f"[Runner] Attempt {attempt}/{MAX_REPAIR_ATTEMPTS}...")
        try:
            solver_out, rc = run_bash(
                f"{PYTHON} {SOLVER_SCRIPT} {INSTANCE_PATH}",
                timeout=SOLVER_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            last_error = f"Solver timed out after {SOLVER_TIMEOUT_S}s"
            print(f"    {last_error}")
            break  # timeout — don't repair, archive directly

        if rc == 0:
            v, d, t = parse_solver_output(solver_out)
            if v is not None and d is not None and t is not None:
                ran_successfully = True
                new_vehicles, new_distance, new_time_ms = v, d, t
                print(">>> Ran successfully.")
                break
            last_error = f"Solver ran but produced no parseable output:\n{solver_out[:500]}"
        else:
            last_error = solver_out[-3000:]  # traceback is in stderr, merged by run_bash

        print(f"    Run failed (attempt {attempt}). " +
              ("Sending error to repair model..." if attempt < MAX_REPAIR_ATTEMPTS else "Exhausted repair attempts."))

        if attempt >= MAX_REPAIR_ATTEMPTS:
            break

        with open(SOLVER_FILE, "r") as f:
            broken_code = f.read()
        try:
            repair_raw = call_local_llm(
                CODER, SYS_REPAIR,
                f"ERROR OUTPUT:\n{last_error}\n\nBROKEN {SOLVER_FILE}:\n{broken_code}",
                nudge="Your previous attempt failed. Fix ALL errors and return ONLY a single ```python``` block.",
                temperature=0.0,
            )
        except Exception as e:
            print(f"    [LLM] Repair call failed: {type(e).__name__}: {e}. Continuing.")
            continue
        new_code = extract_python_code(repair_raw)
        apply_python_dependencies(new_code)
        with open(SOLVER_FILE, "w") as f:
            f.write(new_code)

    force_unload(CODER)

    if not ran_successfully:
        error_lines = last_error.strip().splitlines()
        error_snippet = "\n".join(error_lines[:30])
        if len(error_lines) > 30:
            error_snippet += f"\n... ({len(error_lines) - 30} more lines)"

        print(">>> Failed to run. Archiving branch.")
        run_bash(f"git add {SOLVER_FILE} {EXPERIMENT_PLAN_JSON}")
        run_bash(f'git commit -m "FAILED RUN [{loop_iteration}]: {descriptor}"')
        run_bash(f"git push origin {branch_name}")
        run_bash("git checkout main")
        append_history(
            f"\n## Iteration {loop_iteration} — {timestamp}\n"
            f"Branch: `{branch_name}`\n"
            f"Proposal: {summary}\n"
            f"Result: FAILED RUN — exhausted {MAX_REPAIR_ATTEMPTS} repair attempts\n"
            f"Error (last attempt):\n```\n{error_snippet}\n```\n"
            f"Vehicles: Inf  Distance: Inf  Time: Inf  Gap: Inf\n"
            f"Decision: DISCARDED\n\n---\n"
        )
        run_bash(f"git add {RESEARCH_HISTORY_MD}")
        run_bash(f'git commit -m "LOG [{loop_iteration}]: run-fail ({branch_name})"')
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
        run_bash(f"git add {EXPERIMENT_PLAN_JSON} {SOLVER_FILE} {SOLUTION_FILE}")
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
    quality_improved = is_better_solution(new_vehicles, new_distance, base_vehicles, base_distance)
    quality_worsened = solution_worsened(new_vehicles, new_distance, base_vehicles, base_distance)
    time_improved    = new_time_ms < base_time_ms
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
        "language":         SOLVER_LANGUAGE,
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
        update_readme_best_result(new_vehicles, new_distance, new_time_ms)
        run_bash("git add .")
        run_bash(
            f'git commit -m "IMPROVEMENT [{loop_iteration}]: '
            f'{new_vehicles}v {new_distance:.2f}dist {new_time_ms:.0f}ms ({descriptor})"'
        )
        run_bash(f"git push origin {branch_name}")
        run_bash("git checkout main")
        run_bash(f"git checkout {branch_name} -- {SOLVER_FILE}")
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
        print("--- Not dominant. Archiving branch.")
        append_research_log(log_row)
        append_history(history_entry)
        generate_graphs()
        run_bash("git add .")
        run_bash(
            f'git commit -m "ARCHIVE [{loop_iteration}]: '
            f'{new_vehicles}v {new_distance:.2f}dist {new_time_ms:.0f}ms ({descriptor})"'
        )
        run_bash(f"git push origin {branch_name}")
        run_bash("git checkout main")
        append_research_log(log_row)
        append_history(history_entry)
        generate_graphs()
        update_readme_graphs()
        commit_log_to_main(loop_iteration, branch_name, timestamp)

    print(f"[Loop] Cooling down {COOLDOWN_S}s...")
    time.sleep(COOLDOWN_S)

print("=== Auto-research loop complete ===")
