"""Phase A #2 — target-conditioned re-judging, full runner (both judges).

Generalizes the pilot to a resumable, cross-provider-aware run. Re-judges the
Gate-3 decisive C4-vs-C4_WRONG pairs with the target-conditioned fit prompt
(07c), target-swap (ask for persona P, then Q). Per-call checkpoint (JSONL) so
a cap-interrupted Opus run resumes. Cross-provider primary: gpt judge on
opus-authored tasks, opus judge on gpt-authored tasks (same-provider kept as a
halo-audit secondary, reported separately).

Usage (from repo root):
  python3 drivers/analysis/phaseA2_target_judge_run.py <judge_key> <filter>
    judge_key: gpt-5.5 | opus
    filter:    all | opus_authored | gpt_authored | decisive_gpt | decisive_opus
Examples:
  python3 ... gpt-5.5 all            # full GPT-5.5 run (cap-free); cross-prov = opus-authored
  python3 ... opus decisive_gpt      # Opus on the gpt-authored decisive slice (cross-provider)
"""
import json, os, re, subprocess, sys, time, tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JUDGE = sys.argv[1] if len(sys.argv) > 1 else "gpt-5.5"
FILTER = sys.argv[2] if len(sys.argv) > 2 else "all"
WORKERS = 6 if JUDGE.startswith("gpt") else 2   # gentle parallelism on the Opus cap
TAG = f"{JUDGE}_{FILTER}".replace(".", "p")
CKPT = f"{REPO}/reports/analysis/gate2c_target_judge_{TAG}.checkpoint.jsonl"
OUT = f"{REPO}/reports/analysis/gate2c_target_judge_{TAG}.json"

MAP = {"slalom_altar": "emily_blender", "emily_blender": "slalom_altar",
       "dario_armadillo": "pawl_gram", "pawl_gram": "dario_armadillo",
       "calibration_goblin": "high_agency_spiraler", "high_agency_spiraler": "calibration_goblin",
       "conflict_allergic_moralist": "patient_craftsperson", "patient_craftsperson": "conflict_allergic_moralist"}
def fam(m): return "openai" if str(m).startswith("gpt") else ("anthropic" if "opus" in str(m) else "other")
JUDGE_FAM = "openai" if JUDGE.startswith("gpt") else "anthropic"

tasks = json.load(open("/tmp/gate3_tasks_full.json"))
scen = {}
for l in open(f"{REPO}/data/v03_full_pilot/scenarios.jsonl"):
    l = l.strip()
    if l:
        r = json.loads(l); scen[r["scenario_id"]] = r
TMPL = open(f"{REPO}/prompts/07c_pairwise_judge_target_conditioned.md").read().split("---", 1)[1]

def select(tasks):
    dec = lambda x: x["judge_winner_condition"] == "C4_WRONG_PROFILE"
    if FILTER == "all": return tasks
    if FILTER == "opus_authored": return [x for x in tasks if fam(x["author"]) == "anthropic"]
    if FILTER == "gpt_authored": return [x for x in tasks if fam(x["author"]) == "openai"]
    if FILTER == "decisive_gpt": return [x for x in tasks if fam(x["author"]) == "openai" and dec(x)]
    if FILTER == "decisive_opus": return [x for x in tasks if fam(x["author"]) == "anthropic" and dec(x)]
    raise SystemExit(f"unknown filter {FILTER}")
subset = sorted(select(tasks), key=lambda x: x["task_id"])

def render(task, which):
    k = task["_key"]
    p1, p2 = task["persona_1_brief"], task["persona_2_brief"]
    P_brief = p1 if k["P1_persona"] == "P" else p2
    Q_brief = p2 if k["P1_persona"] == "P" else p1
    brief = P_brief if which == "P" else Q_brief
    up = scen.get(task["scenario_id"], {}).get("user_prompt", "(situation unavailable)")
    return (TMPL.replace("`{{persona_brief}}`", brief).replace("`{{user_prompt}}`", up)
            .replace("`{{response_a}}`", task["output_X"]).replace("`{{response_b}}`", task["output_Y"]))

_CAP = ("usage limit", "hit your limit", "limit · resets", "rate limit", "too many requests",
        "quota", "5-hour", "429")
def call_judge(prompt, timeout=420):
    if JUDGE.startswith("gpt"):
        cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "--color", "never",
               "-m", "gpt-5.5", "-c", 'model_reasoning_effort="xhigh"']
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            raise RuntimeError(f"codex rc={r.returncode}: {r.stderr[-200:]}")
        return r.stdout.strip()
    # opus via claude CLI, context-isolated + pinned to 4.7 (matches llm.py)
    env = os.environ.copy(); env.pop("CLAUDECODE", None)
    r = subprocess.run(["claude", "-p", "--safe-mode", "--model", "claude-opus-4-7"],
                       input=prompt, capture_output=True, text=True, env=env, timeout=timeout,
                       cwd=tempfile.gettempdir())
    if r.returncode != 0:
        so, se = (r.stdout or "").lower(), (r.stderr or "").lower()
        capped = any(m in so or m in se for m in _CAP) or (not so.strip() and not se.strip())
        raise RuntimeError(("CAP:" if capped else "ERR:") + f"claude rc={r.returncode}: {se[-200:] or so[-200:]}")
    return r.stdout.strip()

def parse_winner(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m: return None, None
    try:
        o = json.loads(m.group(0)); w = str(o.get("winner", "")).strip().upper()
        return (w if w in ("A", "B") else None), o.get("why", "")
    except Exception:
        return None, None

# resume from checkpoint
done = {}
if os.path.exists(CKPT):
    for l in open(CKPT):
        l = l.strip()
        if l:
            r = json.loads(l); done[(r["task_id"], r["which"])] = r
jobs = [(t, w) for t in subset for w in ("P", "Q") if (t["task_id"], w) not in done]
print(f"[{JUDGE} / {FILTER}] {len(subset)} tasks, {len(jobs)} calls to run ({len(done)} resumed), {WORKERS} workers")

def one(task, which):
    for attempt in range(4):
        try:
            out = call_judge(render(task, which))
            w, why = parse_winner(out)
            return {"task_id": task["task_id"], "which": which, "winner": w, "why": why,
                    "author_fam": fam(task["author"]), "target": task["target_persona"]}
        except Exception as e:
            msg = str(e)
            if msg.startswith("CAP:") and attempt < 3:
                back = [60, 300, 900][attempt]
                print(f"    CAP on {task['task_id']}/{which}; backoff {back}s (attempt {attempt+1})")
                time.sleep(back); continue
            return {"task_id": task["task_id"], "which": which, "winner": None,
                    "why": msg[:160], "author_fam": fam(task["author"]), "target": task["target_persona"]}

t0 = time.time(); ckpt = open(CKPT, "a")
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(one, t, w): (t["task_id"], w) for t, w in jobs}
    n = 0
    for f in as_completed(futs):
        r = f.result(); done[(r["task_id"], r["which"])] = r
        ckpt.write(json.dumps(r) + "\n"); ckpt.flush(); n += 1
        print(f"  [{n}/{len(jobs)}] {r['task_id']} for-{r['which']} -> {r['winner']} ({time.time()-t0:.0f}s)")
ckpt.close()

# ---- aggregate ----
TASK = {t["task_id"]: t for t in subset}
def metrics(rows_tasks):
    out = {"p_picks_target": [], "q_picks_opposite": [], "reversed": [], "flip": []}
    rec = []
    for tid in rows_tasks:
        t = TASK[tid]; k = t["_key"]
        c4 = "A" if k["X_cond"] == "C4" else "B"; cw = "B" if c4 == "A" else "A"
        wp = done.get((tid, "P"), {}).get("winner"); wq = done.get((tid, "Q"), {}).get("winner")
        if not wp or not wq: continue
        out["p_picks_target"].append(wp == c4); out["q_picks_opposite"].append(wq == cw)
        out["reversed"].append(wp == c4 and wq == cw); out["flip"].append(wp != wq)
        rec.append({"tid": tid, "wp_target": wp == c4, "wq_opp": wq == cw,
                    "uncond_opp": t["judge_winner_condition"] == "C4_WRONG_PROFILE"})
    def m(a): return [round(sum(a)/len(a), 3), len(a)] if a else [None, 0]
    res = {k: m(v) for k, v in out.items()}
    dec = [r for r in rec if r["uncond_opp"]]
    if dec:
        res["decisive_recover_target_for_P"] = [round(sum(r["wp_target"] for r in dec)/len(dec), 3), len(dec)]
    return res

all_ids = [t["task_id"] for t in subset]
cross_ids = [t["task_id"] for t in subset if fam(t["author"]) != JUDGE_FAM]
same_ids = [t["task_id"] for t in subset if fam(t["author"]) == JUDGE_FAM]
summary = {"judge": JUDGE, "filter": FILTER, "n_tasks": len(subset),
           "overall": metrics(all_ids),
           "cross_provider": {"n": len(cross_ids), **{"metrics": metrics(cross_ids)}} if cross_ids else None,
           "same_provider_halo": {"n": len(same_ids), **{"metrics": metrics(same_ids)}} if same_ids else None}
json.dump({"summary": summary, "results": list(done.values())}, open(OUT, "w"), indent=2)
print("\n=== SUMMARY ===")
print(json.dumps(summary, indent=1))
print(f"saved -> {OUT}")
