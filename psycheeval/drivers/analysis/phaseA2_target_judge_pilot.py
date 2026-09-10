"""Phase A #2 — target-conditioned re-judging: GPT-5.5 target-swap PILOT.

The v0.3 unconditional-quality pairwise judge rewarded a global trait-pole, not
fit-to-target (gate battery). This re-judges the SAME decisive C4-vs-C4_WRONG
pairs (Gate-3 bundle) with a TARGET-CONDITIONED fit prompt
(prompts/07c_pairwise_judge_target_conditioned.md), asking twice per pair:
"which better serves persona P?" then "...persona Q?" (target swap).

Fit-sensitive judge => picks the P-conditioned output for the P-question and the
Q-conditioned output for the Q-question (its preference REVERSES with the named
target). Global-pole judge => picks the same (dominant-pole) output both times
(no reversal). High reversal here = target-conditioning fixes the eval bottleneck
=> worth spending Opus on. Low reversal = even target-conditioned judging sticks
to the pole.

PILOT scope: GPT-5.5-xhigh via codex CLI only (NO Opus cap). Pre-registered
subset = the 2 lowest-task_id tasks per persona across the 3 GLOBAL-POLE pairs
(dario/pawl, slalom/emily, goblin/spiraler) = 12 tasks x 2 questions = 24 calls.
Blind to condition; A/B order = bundle's pre-randomized output_X/output_Y, held
constant across the P and Q questions so reversal isolates the target effect.

Run from repo root:  python3 drivers/analysis/phaseA2_target_judge_pilot.py
(needs /tmp/gate3_tasks_full.json — regenerate via gate3_prepare.py if absent.)
"""
import json, os, re, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GLOBAL_POLE_PERSONAS = ["dario_armadillo", "pawl_gram", "slalom_altar", "emily_blender",
                        "calibration_goblin", "high_agency_spiraler"]
N_PER_PERSONA = 2
MODEL = "gpt-5.5"
EFFORT = "xhigh"
WORKERS = 4
OUT = f"{REPO}/reports/analysis/gate2b_target_conditioned_pilot.json"

tasks = json.load(open("/tmp/gate3_tasks_full.json"))
scen = {}
for l in open(f"{REPO}/data/v03_full_pilot/scenarios.jsonl"):
    l = l.strip()
    if l:
        r = json.loads(l); scen[r["scenario_id"]] = r
TMPL = open(f"{REPO}/prompts/07c_pairwise_judge_target_conditioned.md").read().split("---", 1)[1]

# ---- pre-registered subset: 2 lowest task_ids per global-pole persona ----------
by_p = {}
for t in sorted(tasks, key=lambda x: x["task_id"]):
    if t["target_persona"] in GLOBAL_POLE_PERSONAS:
        by_p.setdefault(t["target_persona"], []).append(t)
subset = []
for p in GLOBAL_POLE_PERSONAS:
    subset.extend(by_p.get(p, [])[:N_PER_PERSONA])

def render(task, which):
    """which = 'P' (target) or 'Q' (opposite). A=output_X, B=output_Y (bundle order)."""
    k = task["_key"]
    p1, p2 = task["persona_1_brief"], task["persona_2_brief"]
    P_brief = p1 if k["P1_persona"] == "P" else p2
    Q_brief = p2 if k["P1_persona"] == "P" else p1
    brief = P_brief if which == "P" else Q_brief
    up = scen.get(task["scenario_id"], {}).get("user_prompt", "(situation unavailable)")
    body = (TMPL
            .replace("`{{persona_brief}}`", brief)
            .replace("`{{user_prompt}}`", up)
            .replace("`{{response_a}}`", task["output_X"])
            .replace("`{{response_b}}`", task["output_Y"]))
    return body

def call_codex(prompt, timeout=360):
    cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "--color", "never",
           "-m", MODEL, "-c", f'model_reasoning_effort="{EFFORT}"']
    r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"codex rc={r.returncode}: {r.stderr[-300:]}")
    return r.stdout.strip()

def parse_winner(text):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m: return None, None
    try:
        o = json.loads(m.group(0))
        w = str(o.get("winner", "")).strip().upper()
        return (w if w in ("A", "B") else None), o.get("why", "")
    except Exception:
        return None, None

def one(task, which):
    try:
        out = call_codex(render(task, which))
        w, why = parse_winner(out)
        return {"task_id": task["task_id"], "which": which, "winner": w, "why": why}
    except Exception as e:
        return {"task_id": task["task_id"], "which": which, "winner": None, "why": f"ERR:{e}"}

jobs = [(t, w) for t in subset for w in ("P", "Q")]
print(f"PILOT: {len(subset)} tasks x 2 = {len(jobs)} GPT-5.5 calls (model={MODEL} effort={EFFORT}, {WORKERS} workers)")
print("subset task_ids:", [t["task_id"] for t in subset])
print("targets:", [t["target_persona"] for t in subset])
t0 = time.time()
results = {}
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(one, t, w): (t["task_id"], w) for t, w in jobs}
    done = 0
    for f in as_completed(futs):
        r = f.result(); results[(r["task_id"], r["which"])] = r
        done += 1
        print(f"  [{done}/{len(jobs)}] {r['task_id']} for-{r['which']} -> {r['winner']}  ({time.time()-t0:.0f}s)")

# ---- score: reversal / fit-correctness --------------------------------------
rows = []
for t in subset:
    k = t["_key"]
    c4_letter = "A" if k["X_cond"] == "C4" else "B"      # A=output_X
    cw_letter = "B" if c4_letter == "A" else "A"
    wp = results.get((t["task_id"], "P"), {}).get("winner")
    wq = results.get((t["task_id"], "Q"), {}).get("winner")
    rows.append({
        "task_id": t["task_id"], "target": t["target_persona"], "opposite": t["opposite_persona"],
        "c4_letter": c4_letter, "winner_for_P": wp, "winner_for_Q": wq,
        "p_picks_target": (wp == c4_letter) if wp else None,
        "q_picks_opposite": (wq == cw_letter) if wq else None,
        "reversed_correctly": (wp == c4_letter and wq == cw_letter) if (wp and wq) else None,
        "any_flip": (wp != wq) if (wp and wq) else None,
        "uncond_winner": "C4" if t["judge_winner_condition"] == "C4" else "C4_WRONG",
        "why_P": results.get((t["task_id"], "P"), {}).get("why", ""),
        "why_Q": results.get((t["task_id"], "Q"), {}).get("why", ""),
    })

def frac(key):
    vals = [r[key] for r in rows if r[key] is not None]
    return (round(sum(vals)/len(vals), 3), len(vals)) if vals else (None, 0)

complete_rows = [r for r in rows if r["winner_for_P"] and r["winner_for_Q"]]
summary = {
    "model": MODEL, "effort": EFFORT, "n_tasks": len(subset),
    "n_complete": len(complete_rows),
    "p_picks_target": frac("p_picks_target"),
    "q_picks_opposite": frac("q_picks_opposite"),
    "reversed_correctly": frac("reversed_correctly"),
    "any_flip": frac("any_flip"),
    "subset_task_ids": [t["task_id"] for t in subset],
}
# decisive cells: tasks where the UNCONDITIONAL judge preferred the OPPOSITE (global-pole bias)
gp_bias = [r for r in rows if r["uncond_winner"] == "C4_WRONG" and r["winner_for_P"]]
if gp_bias:
    flipped = sum(1 for r in gp_bias if r["p_picks_target"])
    summary["uncond_preferred_opposite_n"] = len(gp_bias)
    summary["of_those_target_judge_now_picks_target"] = round(flipped/len(gp_bias), 3)

print("\n=== PILOT RESULT ===")
for kk in ("p_picks_target", "q_picks_opposite", "reversed_correctly", "any_flip"):
    v, n = summary[kk]; print(f"  {kk:<22} {v}  (n={n})")
if "of_those_target_judge_now_picks_target" in summary:
    print(f"  [decisive] of {summary['uncond_preferred_opposite_n']} tasks where UNCOND judge preferred the OPPOSITE,")
    print(f"             target-conditioned judge now picks the TARGET in {summary['of_those_target_judge_now_picks_target']:.0%}")
json.dump({"summary": summary, "rows": rows,
           "raw": {f"{tid}|{w}": results[(tid, w)] for (tid, w) in results}},
          open(OUT, "w"), indent=2)
print(f"\nsaved -> {OUT}")
