"""Phase B1 — two-axis (general_quality vs fit_to_person) at FULL scale.

Standing secondary metric (prereg_B1 H2). For each of the 239 matched
C4/C4_WRONG pairs, given the scenario + the TRUE target P's brief, the judge
rates each output on general_quality (1-7) and fit_to_person (1-7), separately
(prompt 07d). Run in BOTH X/Y orders (C4-first and C4_WRONG-first) to cancel
order effects = 2 calls / pair / judge. Full 3x2 author x judge cross.

Reuses the de-leaked full-brief construction + pair build from the target-judge
runner. Resumable per-call checkpoint. Opus pinned to claude-opus-4-7.

Usage:  python3 drivers/analysis/phaseB1_two_axis_run.py <gpt-5.5|opus> <all|opus_authored|gpt_authored>
"""
import json, os, re, subprocess, sys, time, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = f"{REPO}/runs/2026-05-19_v03"
JUDGE = sys.argv[1] if len(sys.argv) > 1 else "gpt-5.5"
AUTHOR_FILTER = sys.argv[2] if len(sys.argv) > 2 else "all"
WORKERS = 6 if JUDGE.startswith("gpt") else 2
RESP_CAP = 2200; PROFILE_CAP = 4000
TAG = f"{JUDGE}_{AUTHOR_FILTER}".replace(".", "p").replace("-", "")
CKPT = f"{REPO}/reports/analysis/phaseB1_twoaxis_{TAG}.checkpoint.jsonl"
OUT = f"{REPO}/reports/analysis/phaseB1_twoaxis_{TAG}.json"

MAP = {
 "user_pfi_slalom_altar_001": "user_pfi_emily_blender_001", "user_pfi_emily_blender_001": "user_pfi_slalom_altar_001",
 "user_pfi_dario_armadillo_001": "user_pfi_pawl_gram_001", "user_pfi_pawl_gram_001": "user_pfi_dario_armadillo_001",
 "user_syn_calibration_goblin_001": "user_syn_high_agency_spiraler_001", "user_syn_high_agency_spiraler_001": "user_syn_calibration_goblin_001",
 "user_syn_conflict_allergic_moralist_001": "user_syn_patient_craftsperson_001", "user_syn_patient_craftsperson_001": "user_syn_conflict_allergic_moralist_001",
}
def fam(m): return "openai" if str(m).startswith("gpt") else ("anthropic" if "opus" in str(m) else "other")
JUDGE_FAM = "openai" if JUDGE.startswith("gpt") else "anthropic"

outs = {}
for l in open(f"{RUN}/assistant_outputs.jsonl"):
    l = l.strip()
    if l:
        try: r = json.loads(l); outs[r["run_id"]] = r
        except: pass

def prof_for(user, cond):
    for r in outs.values():
        if r.get("user_id") == user and str(r.get("condition")) == cond:
            return r.get("profile_text_supplied", "") or ""
    return ""
def deleak(t):
    t = re.sub(r'Everything in C3[, ]*plus:?', '', t); t = re.sub(r'\bC[0-5]\b', 'the base profile', t)
    return t.strip()
def full_brief(user):
    c4 = prof_for(user, "C4"); c3 = prof_for(user, "C3")
    if c4.lstrip().startswith("Everything in C3"):
        delta = c4.split("plus:", 1)[1] if "plus:" in c4 else c4; full = c3.rstrip() + "\n\n" + delta.lstrip()
    else: full = c4
    return deleak(full)[:PROFILE_CAP]
PERSONA_BRIEF = {u: full_brief(u) for u in MAP}

scen = {}
for l in open(f"{REPO}/data/v03_full_pilot/scenarios.jsonl"):
    l = l.strip()
    if l: r = json.loads(l); scen[r["scenario_id"]] = r

bycell = {}
for r in outs.values():
    c = str(r.get("condition"))
    if c in ("C4", "C4_WRONG_PROFILE") and r.get("user_id") in MAP:
        bycell.setdefault((r.get("scenario_id"), r.get("user_id"), r.get("output_model")), {})[c] = r
pairs = []
for (sid, uid, author), d in bycell.items():
    if "C4" not in d or "C4_WRONG_PROFILE" not in d: continue
    af = fam(author)
    if AUTHOR_FILTER == "opus_authored" and af != "anthropic": continue
    if AUTHOR_FILTER == "gpt_authored" and af != "openai": continue
    pairs.append({"pair_id": f"{sid}__{uid}__{author}", "scenario_id": sid, "user_id": uid,
                  "author": author, "author_fam": af,
                  "c4_text": (d["C4"].get("assistant_response", "") or "")[:RESP_CAP],
                  "cw_text": (d["C4_WRONG_PROFILE"].get("assistant_response", "") or "")[:RESP_CAP]})
pairs.sort(key=lambda p: p["pair_id"])

TMPL = open(f"{REPO}/prompts/07d_two_axis_scalar.md").read().split("---", 1)[1]

def render(pair, order):
    brief = PERSONA_BRIEF[pair["user_id"]]   # TRUE target P
    up = scen.get(pair["scenario_id"], {}).get("user_prompt", "(situation unavailable)")
    if order == "C4_first": rx, ry = pair["c4_text"], pair["cw_text"]
    else:                   rx, ry = pair["cw_text"], pair["c4_text"]
    return (TMPL.replace("`{{persona_brief}}`", brief).replace("`{{user_prompt}}`", up)
            .replace("`{{response_x}}`", rx).replace("`{{response_y}}`", ry))

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
        raise RuntimeError(("CAP:" if capped else "ERR:") + f"claude rc={r.returncode}: {se[-200:] or so[-200:]}")
    return r.stdout.strip()

def parse(text, order):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m: return None
    try:
        o = json.loads(m.group(0))
        X, Y = o.get("X", {}), o.get("Y", {})
        # map X/Y back to condition by order
        if order == "C4_first":
            c4, cw = X, Y
        else:
            c4, cw = Y, X
        return {"c4_gq": c4.get("general_quality"), "c4_fit": c4.get("fit_to_person"),
                "cw_gq": cw.get("general_quality"), "cw_fit": cw.get("fit_to_person")}
    except Exception:
        return None

JOBS = [(p, o) for p in pairs for o in ("C4_first", "CW_first")]
done = {}
if os.path.exists(CKPT):
    for l in open(CKPT):
        l = l.strip()
        if l: r = json.loads(l); done[(r["pair_id"], r["order"])] = r
# Re-run incomplete/errored calls on resume (cap-bound Opus safety).
_OK = lambda r: r.get("c4_fit") is not None
valid = {k for k, r in done.items() if _OK(r)}
todo = [(p, o) for (p, o) in JOBS if (p["pair_id"], o) not in valid]
print(f"[{JUDGE} / {AUTHOR_FILTER}] {len(pairs)} pairs, {len(JOBS)} calls, {len(todo)} to run ({len(valid)} completed), {WORKERS}w")

def one(pair, order):
    for attempt in range(4):
        try:
            sc = parse(call(render(pair, order)), order)
            rec = {"pair_id": pair["pair_id"], "scenario_id": pair["scenario_id"], "user_id": pair["user_id"],
                   "author": pair["author"], "author_fam": pair["author_fam"], "judge": JUDGE,
                   "judge_fam": JUDGE_FAM, "order": order}
            rec.update(sc or {"c4_gq": None, "c4_fit": None, "cw_gq": None, "cw_fit": None})
            return rec
        except Exception as e:
            msg = str(e)
            if msg.startswith("CAP:") and attempt < 3:
                time.sleep([60, 300, 900][attempt]); continue
            return {"pair_id": pair["pair_id"], "scenario_id": pair["scenario_id"], "user_id": pair["user_id"],
                    "author": pair["author"], "author_fam": pair["author_fam"], "judge": JUDGE,
                    "judge_fam": JUDGE_FAM, "order": order, "c4_gq": None, "c4_fit": None,
                    "cw_gq": None, "cw_fit": None, "error": msg[:160]}

t0 = time.time(); ckpt = open(CKPT, "a")
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(one, p, o): (p["pair_id"], o) for (p, o) in todo}
    n = 0
    for f in as_completed(futs):
        r = f.result(); done[(r["pair_id"], r["order"])] = r
        ckpt.write(json.dumps(r) + "\n"); ckpt.flush(); n += 1
        if n % 20 == 0 or n == len(todo):
            print(f"  [{n}/{len(todo)}] {time.time()-t0:.0f}s")
ckpt.close()

rows = [r for r in done.values() if r.get("c4_fit") is not None]
def gap(field_c4, field_cw):
    v = [r[field_c4] - r[field_cw] for r in rows]
    return round(sum(v) / len(v), 3) if v else None
summary = {"judge": JUDGE, "author_filter": AUTHOR_FILTER, "n_pairs": len(pairs), "n_scored": len(rows),
           "fit_gap_C4_minus_CW": gap("c4_fit", "cw_fit"), "quality_gap_C4_minus_CW": gap("c4_gq", "cw_gq")}
json.dump({"summary": summary, "results": list(done.values())}, open(OUT, "w"), indent=2)
print("\n=== two-axis descriptive summary ===")
print(json.dumps(summary, indent=1))
print(f"saved -> {OUT}")
print(f"STATUS valid={len(rows)} total={len(JOBS)}")
