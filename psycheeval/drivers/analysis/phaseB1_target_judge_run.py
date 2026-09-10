"""Phase B1 — target-conditioned judging at FULL scale (239 pairs, AB/BA, ternary).

Generalizes the Phase A #2 runner from the 64-cell decisive bundle to the full
universe of matched C4/C4_WRONG pairs, with:
  - position counterbalancing (AB and BA orientations),
  - the ternary tie option (prompt 07c_ternary),
  - the P->Q target-swap (ask "serves the true target?" then "serves the wrong persona?"),
  - the full 3x2 author x judge cross (cross-provider primary + same-provider halo).

Persona briefs + pair construction reuse gate3_prepare's de-leaked full-brief
logic (so this stays consistent with the validated Phase A pipeline). Per-call
JSONL checkpoint so a cap-interrupted Opus run resumes. Opus pinned to
claude-opus-4-7 (matches llm.py), --safe-mode + neutral cwd for blindness.

Usage (from repo root):
  python3 drivers/analysis/phaseB1_target_judge_run.py <judge_key> <author_filter>
    judge_key:     gpt-5.5 | opus
    author_filter: all | opus_authored | gpt_authored
Cross-provider primary:  gpt-5.5 opus_authored   |  opus gpt_authored
Same-provider halo:      gpt-5.5 gpt_authored     |  opus opus_authored
(gpt-5.5 all  == one cap-free sweep covering both its cross + halo cells)
"""
import json, os, re, subprocess, sys, time, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = f"{REPO}/runs/2026-05-19_v03"
JUDGE = sys.argv[1] if len(sys.argv) > 1 else "gpt-5.5"
AUTHOR_FILTER = sys.argv[2] if len(sys.argv) > 2 else "all"
WORKERS = 6 if JUDGE.startswith("gpt") else 2
RESP_CAP = 2200
PROFILE_CAP = 4000
TAG = f"{JUDGE}_{AUTHOR_FILTER}".replace(".", "p").replace("-", "")
CKPT = f"{REPO}/reports/analysis/phaseB1_targetjudge_{TAG}.checkpoint.jsonl"
OUT = f"{REPO}/reports/analysis/phaseB1_targetjudge_{TAG}.json"

MAP = {
 "user_pfi_slalom_altar_001": "user_pfi_emily_blender_001", "user_pfi_emily_blender_001": "user_pfi_slalom_altar_001",
 "user_pfi_dario_armadillo_001": "user_pfi_pawl_gram_001", "user_pfi_pawl_gram_001": "user_pfi_dario_armadillo_001",
 "user_syn_calibration_goblin_001": "user_syn_high_agency_spiraler_001", "user_syn_high_agency_spiraler_001": "user_syn_calibration_goblin_001",
 "user_syn_conflict_allergic_moralist_001": "user_syn_patient_craftsperson_001", "user_syn_patient_craftsperson_001": "user_syn_conflict_allergic_moralist_001",
}
def short(u): return u.replace("user_pfi_", "").replace("user_syn_", "").replace("_001", "")
def fam(m):
    if not m: return "other"
    return "openai" if str(m).startswith("gpt") else ("anthropic" if "opus" in str(m) else "other")
JUDGE_FAM = "openai" if JUDGE.startswith("gpt") else "anthropic"

# ---- load corpus ----
outs = {}
for l in open(f"{RUN}/assistant_outputs.jsonl"):
    l = l.strip()
    if not l: continue
    try: r = json.loads(l)
    except: continue
    outs[r["run_id"]] = r

scen = {}
for l in open(f"{REPO}/data/v03_full_pilot/scenarios.jsonl"):
    l = l.strip()
    if l:
        r = json.loads(l); scen[r["scenario_id"]] = r

# ---- de-leaked full behavioral brief per persona (identical to gate3_prepare) ----
def prof_for(user, cond):
    for r in outs.values():
        if r.get("user_id") == user and str(r.get("condition")) == cond:
            return r.get("profile_text_supplied", "") or ""
    return ""
def deleak(t):
    t = re.sub(r'Everything in C3[, ]*plus:?', '', t)
    t = re.sub(r'\bC[0-5]\b', 'the base profile', t)
    return t.strip()
def full_brief(user):
    c4 = prof_for(user, "C4"); c3 = prof_for(user, "C3")
    if c4.lstrip().startswith("Everything in C3"):
        delta = c4.split("plus:", 1)[1] if "plus:" in c4 else c4
        full = c3.rstrip() + "\n\n" + delta.lstrip()
    else:
        full = c4
    return deleak(full)[:PROFILE_CAP]
PERSONA_BRIEF = {u: full_brief(u) for u in MAP}

# ---- build ALL matched C4 / C4_WRONG pairs (the 239-pair universe) ----
bycell = {}
for r in outs.values():
    c = str(r.get("condition"))
    if c not in ("C4", "C4_WRONG_PROFILE"): continue
    u = r.get("user_id")
    if u not in MAP: continue
    key = (r.get("scenario_id"), u, r.get("output_model"))
    bycell.setdefault(key, {})[c] = r
pairs = []
for (sid, uid, author), d in bycell.items():
    if "C4" not in d or "C4_WRONG_PROFILE" not in d: continue
    af = fam(author)
    if AUTHOR_FILTER == "opus_authored" and af != "anthropic": continue
    if AUTHOR_FILTER == "gpt_authored" and af != "openai": continue
    pairs.append({
        "pair_id": f"{sid}__{uid}__{author}",
        "scenario_id": sid, "user_id": uid, "author": author, "author_fam": af,
        "c4_text": (d["C4"].get("assistant_response", "") or "")[:RESP_CAP],
        "cw_text": (d["C4_WRONG_PROFILE"].get("assistant_response", "") or "")[:RESP_CAP],
    })
pairs.sort(key=lambda p: p["pair_id"])

TMPL = open(f"{REPO}/prompts/07c_pairwise_judge_target_conditioned_ternary.md").read().split("---", 1)[1]

def render(pair, query, orientation):
    # query: 'P' (true target) or 'Q' (wrong persona). orientation: 'AB' or 'BA'.
    tgt = pair["user_id"] if query == "P" else MAP[pair["user_id"]]
    brief = PERSONA_BRIEF[tgt]
    up = scen.get(pair["scenario_id"], {}).get("user_prompt", "(situation unavailable)")
    if orientation == "AB":   # A = C4, B = C4_WRONG
        ra, rb = pair["c4_text"], pair["cw_text"]
    else:                     # BA: A = C4_WRONG, B = C4
        ra, rb = pair["cw_text"], pair["c4_text"]
    return (TMPL.replace("`{{persona_brief}}`", brief).replace("`{{user_prompt}}`", up)
            .replace("`{{response_a}}`", ra).replace("`{{response_b}}`", rb))

_CAP = ("usage limit", "hit your limit", "limit · resets", "rate limit",
        "too many requests", "quota", "5-hour", "429")
def call_judge(prompt, timeout=420):
    if JUDGE.startswith("gpt"):
        cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "--color", "never",
               "-m", "gpt-5.5", "-c", 'model_reasoning_effort="xhigh"']
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            raise RuntimeError(f"codex rc={r.returncode}: {r.stderr[-200:]}")
        return r.stdout.strip()
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
    if not m: return None, None, None
    try:
        o = json.loads(m.group(0)); w = str(o.get("winner", "")).strip().upper()
        w = w if w in ("A", "B", "TIE") else None
        return w, o.get("confidence_0_to_1"), o.get("why", "")
    except Exception:
        return None, None, None

# enumerate jobs: per pair x query(P,Q) x orientation(AB,BA) = 4 calls
JOBS = [(p, q, o) for p in pairs for q in ("P", "Q") for o in ("AB", "BA")]

done = {}
if os.path.exists(CKPT):
    for l in open(CKPT):
        l = l.strip()
        if l:
            r = json.loads(l); done[(r["pair_id"], r["query"], r["orientation"])] = r
# A call counts as completed ONLY if it produced a valid verdict. Errored/capped
# records (winner=None) are RE-RUN on resume — critical for the cap-bound Opus
# arm, where a window closing mid-run would otherwise mark calls permanently errored.
_OK = lambda r: r.get("winner") in ("A", "B", "TIE")
valid = {k for k, r in done.items() if _OK(r)}
todo = [(p, q, o) for (p, q, o) in JOBS if (p["pair_id"], q, o) not in valid]
print(f"[{JUDGE} / {AUTHOR_FILTER}] {len(pairs)} pairs, {len(JOBS)} calls total, "
      f"{len(todo)} to run ({len(valid)} completed) , {WORKERS} workers")

def picked_cond(winner, orientation):
    if winner == "TIE" or winner is None: return "tie" if winner == "TIE" else None
    # AB: A=C4,B=C4_WRONG ; BA: A=C4_WRONG,B=C4
    if orientation == "AB":
        return "C4" if winner == "A" else "C4_WRONG"
    return "C4_WRONG" if winner == "A" else "C4"

def one(pair, query, orientation):
    for attempt in range(4):
        try:
            out = call_judge(render(pair, query, orientation))
            w, conf, why = parse_winner(out)
            pc = picked_cond(w, orientation)
            # the target output for this query: P->C4, Q->C4_WRONG
            tgt_cond = "C4" if query == "P" else "C4_WRONG"
            picked_target = (pc == tgt_cond) if pc in ("C4", "C4_WRONG") else None
            return {"pair_id": pair["pair_id"], "scenario_id": pair["scenario_id"],
                    "user_id": pair["user_id"], "author": pair["author"], "author_fam": pair["author_fam"],
                    "judge": JUDGE, "judge_fam": JUDGE_FAM, "query": query, "orientation": orientation,
                    "winner": w, "picked_cond": pc, "picked_target": picked_target,
                    "confidence": conf, "why": why}
        except Exception as e:
            msg = str(e)
            if msg.startswith("CAP:") and attempt < 3:
                back = [60, 300, 900][attempt]
                print(f"    CAP on {pair['pair_id']} {query}/{orientation}; backoff {back}s (attempt {attempt+1})")
                time.sleep(back); continue
            return {"pair_id": pair["pair_id"], "scenario_id": pair["scenario_id"],
                    "user_id": pair["user_id"], "author": pair["author"], "author_fam": pair["author_fam"],
                    "judge": JUDGE, "judge_fam": JUDGE_FAM, "query": query, "orientation": orientation,
                    "winner": None, "picked_cond": None, "picked_target": None, "error": msg[:160]}

t0 = time.time(); ckpt = open(CKPT, "a")
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(one, p, q, o): (p["pair_id"], q, o) for (p, q, o) in todo}
    n = 0
    for f in as_completed(futs):
        r = f.result(); done[(r["pair_id"], r["query"], r["orientation"])] = r
        ckpt.write(json.dumps(r) + "\n"); ckpt.flush(); n += 1
        if n % 10 == 0 or n == len(todo):
            print(f"  [{n}/{len(todo)}] {r['pair_id'][:40]} {r['query']}/{r['orientation']} -> {r['winner']} ({time.time()-t0:.0f}s)")
ckpt.close()

# ---- light aggregate (descriptive; the confirmatory model is a separate analyzer) ----
rows = list(done.values())
def rate(sel):
    v = [r["picked_target"] for r in rows if sel(r) and r["picked_target"] is not None]
    return [round(sum(v)/len(v), 3), len(v)] if v else [None, 0]
ties = sum(1 for r in rows if r.get("winner") == "TIE")
errs = sum(1 for r in rows if r.get("winner") is None)
summary = {
    "judge": JUDGE, "author_filter": AUTHOR_FILTER, "n_pairs": len(pairs), "n_calls": len(rows),
    "tie_rate": round(ties / len(rows), 3) if rows else None,
    "error_rate": round(errs / len(rows), 3) if rows else None,
    "p_picks_target_all": rate(lambda r: r["query"] == "P"),
    "q_picks_target_all": rate(lambda r: r["query"] == "Q"),
}
json.dump({"summary": summary, "results": rows}, open(OUT, "w"), indent=2)
print("\n=== descriptive summary (NOT the gate; gate uses the pre-registered model on decisive cells) ===")
print(json.dumps(summary, indent=1))
print(f"saved -> {OUT}")
n_valid = sum(1 for r in rows if _OK(r))
print(f"STATUS valid={n_valid} total={len(JOBS)}")
