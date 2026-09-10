"""Phase A #4 — two-axis re-score (general quality vs fit-to-target).

For each Gate-3 C4-vs-C4_WRONG pair, given the scenario + the TRUE target P's
brief, a judge rates each output on general_quality (1-7) and fit_to_person (1-7),
separately. Tests the v0.3 prediction that the two axes DIVERGE: target-
conditioning should move fit (C4 fits P better than C4_WRONG) more than it moves
general quality; and quality vs fit should be weakly correlated (distinct axes).
Distinguishes "judge biased" from "quality and fit genuinely trade off".

Judges: gpt-5.5 (codex, cap-free) on all 64; opus-4.7 on the 10 gpt-authored
decisive cells (cross-provider). Blind to condition (bundle X/Y order). Resumable.

Usage:  python3 drivers/analysis/phaseA4_two_axis.py <gpt-5.5|opus> <all|decisive_gpt>
"""
import json, os, re, subprocess, sys, time, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JUDGE = sys.argv[1] if len(sys.argv) > 1 else "gpt-5.5"
FILTER = sys.argv[2] if len(sys.argv) > 2 else "all"
WORKERS = 6 if JUDGE.startswith("gpt") else 2
TAG = f"{JUDGE}_{FILTER}".replace(".", "p")
CKPT = f"{REPO}/reports/analysis/phaseA4_two_axis_{TAG}.checkpoint.jsonl"
OUT = f"{REPO}/reports/analysis/phaseA4_two_axis_{TAG}.json"

def fam(m): return "openai" if str(m).startswith("gpt") else ("anthropic" if "opus" in str(m) else "other")
tasks = json.load(open("/tmp/gate3_tasks_full.json"))
keys = json.load(open("/tmp/gate3_keys.json"))
scen = {}
for l in open(f"{REPO}/data/v03_full_pilot/scenarios.jsonl"):
    l = l.strip()
    if l: r = json.loads(l); scen[r["scenario_id"]] = r
TMPL = open(f"{REPO}/prompts/07d_two_axis_scalar.md").read().split("---", 1)[1]

def select():
    if FILTER == "all": return tasks
    if FILTER == "decisive_gpt":
        return [t for t in tasks if fam(t["author"]) == "openai" and t["judge_winner_condition"] == "C4_WRONG_PROFILE"]
    raise SystemExit("filter?")
subset = sorted(select(), key=lambda x: x["task_id"])

def render(t):
    k = t["_key"]; p1, p2 = t["persona_1_brief"], t["persona_2_brief"]
    P_brief = p1 if k["P1_persona"] == "P" else p2
    up = scen.get(t["scenario_id"], {}).get("user_prompt", "(situation unavailable)")
    return (TMPL.replace("`{{persona_brief}}`", P_brief).replace("`{{user_prompt}}`", up)
            .replace("`{{response_x}}`", t["output_X"]).replace("`{{response_y}}`", t["output_Y"]))

_CAP = ("usage limit", "hit your limit", "limit · resets", "rate limit", "too many requests", "quota", "5-hour", "429")
def call(prompt, timeout=360):
    if JUDGE.startswith("gpt"):
        cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "--color", "never",
               "-m", "gpt-5.5", "-c", 'model_reasoning_effort="xhigh"']
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0: raise RuntimeError(f"codex rc={r.returncode}: {r.stderr[-200:]}")
        return r.stdout.strip()
    env = os.environ.copy(); env.pop("CLAUDECODE", None)
    r = subprocess.run(["claude", "-p", "--safe-mode", "--model", "claude-opus-4-7"], input=prompt,
                       capture_output=True, text=True, env=env, timeout=timeout, cwd=tempfile.gettempdir())
    if r.returncode != 0:
        so, se = (r.stdout or "").lower(), (r.stderr or "").lower()
        capped = any(m in so or m in se for m in _CAP) or (not so.strip() and not se.strip())
        raise RuntimeError(("CAP:" if capped else "ERR:") + f"claude rc={r.returncode}")
    return r.stdout.strip()

def parse(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m: return None
    try:
        o = json.loads(m.group(0))
        for s in ("X", "Y"):
            for a in ("general_quality", "fit_to_person"):
                float(o[s][a])
        return o
    except Exception: return None

done = {}
if os.path.exists(CKPT):
    for l in open(CKPT):
        l = l.strip()
        if l: r = json.loads(l); done[r["task_id"]] = r
todo = [t for t in subset if t["task_id"] not in done]
print(f"[{JUDGE}/{FILTER}] {len(subset)} tasks, {len(todo)} to run, {WORKERS} workers")

def one(t):
    for attempt in range(4):
        try:
            o = parse(call(render(t)))
            if o is None: raise RuntimeError("parse")
            return {"task_id": t["task_id"], "scores": o, "author_fam": fam(t["author"])}
        except Exception as e:
            if str(e).startswith("CAP:") and attempt < 3:
                time.sleep([60, 300, 900][attempt]); continue
            return {"task_id": t["task_id"], "scores": None, "err": str(e)[:120], "author_fam": fam(t["author"])}

if todo:
    fh = open(CKPT, "a"); t0 = time.time(); n = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(one, t) for t in todo]
        for f in as_completed(futs):
            r = f.result(); done[r["task_id"]] = r; n += 1
            fh.write(json.dumps(r) + "\n"); fh.flush()
            print(f"  [{n}/{len(todo)}] {r['task_id']} {'OK' if r['scores'] else 'FAIL '+r.get('err','')} ({time.time()-t0:.0f}s)")
    fh.close()

# ---- analyze ----
import statistics as st
fit_gaps, qual_gaps, all_q, all_f = [], [], [], []
c4_fit, cw_fit, c4_q, cw_q = [], [], [], []
for t in subset:
    r = done.get(t["task_id"])
    if not r or not r["scores"]: continue
    k = t["_key"]; s = r["scores"]
    c4_slot = "X" if k["X_cond"] == "C4" else "Y"; cw_slot = "Y" if c4_slot == "X" else "X"
    q4, f4 = float(s[c4_slot]["general_quality"]), float(s[c4_slot]["fit_to_person"])
    qw, fw = float(s[cw_slot]["general_quality"]), float(s[cw_slot]["fit_to_person"])
    fit_gaps.append(f4 - fw); qual_gaps.append(q4 - qw)
    all_q += [q4, qw]; all_f += [f4, fw]
    c4_fit.append(f4); cw_fit.append(fw); c4_q.append(q4); cw_q.append(qw)
def corr(a, b):
    if len(a) < 3: return None
    return round(st.correlation(a, b), 3) if len(set(a)) > 1 and len(set(b)) > 1 else None
res = {
    "judge": JUDGE, "filter": FILTER, "n_tasks_scored": len(fit_gaps),
    "mean_fit_gap_C4_minus_CWRONG": round(st.mean(fit_gaps), 3) if fit_gaps else None,
    "mean_quality_gap_C4_minus_CWRONG": round(st.mean(qual_gaps), 3) if qual_gaps else None,
    "mean_fit_C4": round(st.mean(c4_fit), 2) if c4_fit else None,
    "mean_fit_CWRONG": round(st.mean(cw_fit), 2) if cw_fit else None,
    "mean_quality_C4": round(st.mean(c4_q), 2) if c4_q else None,
    "mean_quality_CWRONG": round(st.mean(cw_q), 2) if cw_q else None,
    "corr_quality_fit_across_outputs": corr(all_q, all_f),
    "fit_gap_gt_quality_gap": (st.mean(fit_gaps) > st.mean(qual_gaps)) if fit_gaps else None,
}
json.dump({"summary": res, "results": list(done.values())}, open(OUT, "w"), indent=2)
print("\n=== #4 TWO-AXIS SUMMARY ===")
print(json.dumps(res, indent=1))
print(f"saved -> {OUT}")
