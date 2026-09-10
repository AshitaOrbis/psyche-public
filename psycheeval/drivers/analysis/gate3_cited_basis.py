"""Phase A #7 — cited-basis audit of Gate 3 (no new model calls).

Codes the 64 already-stored Gemini `basis` rationales (reports/analysis/
gate3_verdicts_g{0-3}.json) into surface vs behavioral buckets, and reports
blind-recovery split by bucket. Triages whether the v0.3 ~93% Gate-3 recovery
leans on SURFACE/echo cues (-> the neutral-paraphrase test #1 is the required
next gate) or on BEHAVIORAL stance (-> generation is plausibly target-serving,
#2 target-conditioned re-judging is the next gate).

Method: a TRANSPARENT keyword/regex rubric (auditable, reproducible, no LLM).
Single-coder limitation noted; per-item coding is emitted for human review.
Answer key (/tmp/gate3_keys.json) is regenerated deterministically by
gate3_prepare.py (SEED=20260617); this script asserts it reproduces the
published recovery (0.93) + cross-tab before coding, so the join is provably
the one Gemini judged on.

Run from repo root:  python3 drivers/analysis/gate3_prepare.py && python3 drivers/analysis/gate3_cited_basis.py
"""
import json, os, re, math
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEY = "/tmp/gate3_keys.json"
if not os.path.exists(KEY):
    raise SystemExit("Missing /tmp/gate3_keys.json — run `python3 drivers/analysis/gate3_prepare.py` first (deterministic).")
keys = json.load(open(KEY))
verdicts = {}
for g in range(4):
    for v in json.load(open(f"{REPO}/reports/analysis/gate3_verdicts_g{g}.json")):
        verdicts[v["task_id"]] = v

def wilson(k, n, z=1.96):
    if n == 0: return (None, None, None)
    p = k/n; d = 1+z*z/n
    c = (p+z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return round(p, 3), round(c-h, 3), round(c+h, 3)

# ---------------------------------------------------------------------------
# Rubric. ECHO = the discriminator the coder cited is a SURFACE lexical match:
# an explicit exact/verbatim/mirror/phrase claim, a quoted multiword span, or a
# distinctive contract TOKEN (a specific string a neutral paraphrase would strip).
# BEHAV = the coder cited an abstract behavioral/reasoning/strategy/omission axis.
# ---------------------------------------------------------------------------
ECHO_PATTERNS = [
    r"\bexact\b", r"\bexactly\b", r"verbatim", r"\bliteral", r"mirror",
    r"\bphrase", r"phrasing",
    r"(?<![\w])'[^']{4,}'",            # quoted span — lookbehind excludes possessive apostrophes (P1's/P2's)
    r"next 30 seconds", r"30-second",  # specific contract tokens ...
    r"24-hour", r"\bthursday\b", r"10 ?a\.?m", r"observable (next )?step",
    r"checkable language", r"clippable", r"see what others miss",
]
BEHAV_PATTERNS = [
    r"reversib", r"irreversib", r"confidence level", r"horizon", r"falsif",
    r"mechanism", r"assumption", r"inference layer", r"layers visible",
    r"\bagency", r"counterargument", r"tradeoff", r"load-bearing", r"\bomit",
    r"omitted", r"disclosure", r"avoidance", r"character", r"pattern",
    r"\bmenu\b", r"choices", r"repair", r"escalation", r"motive", r"premise",
    r"validation", r"praise", r"compliment", r"directness", r"material",
    r"grievance", r"residual uncertainty", r"update condition", r"strongest",
    r"can ?and ?cannot", r"smallest", r"next (move|step)", r"options",
    r"contrarian", r"universaliz", r"systematiz", r"traction", r"failure mode",
    r"\bbets?\b", r"actors", r"acknowledg", r"register",
    r"caution", r"cautious", r"good move", r"lacking", r"\bcraft", r"feedback",
    r"closing", r"expensive", r"sentiment", r"course-correction", r"draft",
]
def tags(b):
    bl = b.lower()
    echo = [p for p in ECHO_PATTERNS if re.search(p, bl)]
    behav = [p for p in BEHAV_PATTERNS if re.search(p, bl)]
    if echo and behav: bucket = "mixed"
    elif echo:         bucket = "surface"
    elif behav:        bucket = "behavioral"
    else:              bucket = "unclear"
    return bucket, bool(echo), bool(behav)

# ---- join + reproduction self-check ----------------------------------------
rows, items = [], []
ct = defaultdict(int)
for tid, v in verdicts.items():
    if tid not in keys: continue
    k = keys[tid]
    if v.get("output_X_fits") not in (1, 2) or v.get("output_Y_fits") not in (1, 2): continue
    sp = {1: k["P1_persona"], 2: k["P2_persona"]}
    xr = int(sp[v["output_X_fits"]] == ("P" if k["X_cond"] == "C4" else "Q"))
    yr = int(sp[v["output_Y_fits"]] == ("P" if k["Y_cond"] == "C4" else "Q"))
    rows += [xr, yr]
    c4_assigned = sp[v["output_X_fits"]] if k["X_cond"] == "C4" else sp[v["output_Y_fits"]]
    ct[(c4_assigned == "P", k["judge_winner_condition"] == "C4")] += 1
    bucket, echo, behav = tags(v.get("basis", ""))
    items.append({"task_id": tid, "target": k["target_persona"], "opposite": k["opposite_persona"],
                  "x_recovered": xr, "y_recovered": yr, "task_recovery": (xr+yr)/2,
                  "bucket": bucket, "echo_cue": echo, "behav_axis": behav,
                  "basis": v.get("basis", "")})

pub = json.load(open(f"{REPO}/reports/analysis/gate3_results.json"))
repro = (wilson(sum(rows), len(rows))[0] == pub["generation_steering_all"][0]
         and ct[(True, True)] == pub["cross_tab"]["genTrue_evaltargetTrue"]
         and ct[(True, False)] == pub["cross_tab"]["genTrue_evaltargetFalse"])
assert repro, "Key does NOT reproduce published gate3_results.json — aborting (stale/invalid key)."

# ---- aggregates ------------------------------------------------------------
N = len(items)
bydist = defaultdict(int)
for it in items: bydist[it["bucket"]] += 1
echo_rate = sum(it["echo_cue"] for it in items) / N
def rec_of(sub):
    js = [it["x_recovered"] for it in sub] + [it["y_recovered"] for it in sub]
    return wilson(sum(js), len(js)), len(js)

print("=== #7 CITED-BASIS AUDIT (n=%d tasks, reproduction-verified) ===" % N)
print("Bucket distribution (which cue did the coder cite to recover persona?):")
for b in ("behavioral", "mixed", "surface", "unclear"):
    n = bydist[b]
    (p, lo, hi), nj = rec_of([it for it in items if it["bucket"] == b])
    print(f"  {b:<11} {n:>2}/{N} ({100*n/N:4.1f}%)   recovery {p} [{lo},{hi}] (n_judg={nj})")
print(f"\nEXPLICIT-ECHO-CUE RATE (any verbatim/quoted/token cue cited): "
      f"{sum(it['echo_cue'] for it in items)}/{N} = {100*echo_rate:.1f}%")
(pe, le, he), ne = rec_of([it for it in items if it["echo_cue"]])
(pn, ln, hn), nn = rec_of([it for it in items if not it["echo_cue"]])
print(f"  recovery | echo-citing tasks   : {pe} [{le},{he}] (n_judg={ne})")
print(f"  recovery | non-echo tasks       : {pn} [{ln},{hn}] (n_judg={nn})")
print(f"\nPURE-behavioral (no echo cue at all): {bydist['behavioral']}/{N} = {100*bydist['behavioral']/N:.1f}%")
print(f"ANY echo reliance (surface+mixed)   : {(bydist['surface']+bydist['mixed'])}/{N} = "
      f"{100*(bydist['surface']+bydist['mixed'])/N:.1f}%")

out = {
    "method": "transparent keyword/regex rubric; single-coder (script); per-item emitted for review",
    "n_tasks": N, "reproduces_published_gate3": True,
    "bucket_distribution": dict(bydist),
    "explicit_echo_cue_rate": round(echo_rate, 3),
    "recovery_by_bucket": {b: rec_of([it for it in items if it["bucket"] == b])[0]
                            for b in ("behavioral", "mixed", "surface", "unclear")},
    "recovery_echo_vs_nonecho": {"echo": wilson(*[f([it for it in items if it["echo_cue"]]) for f in
                                  (lambda s: sum(x for it in s for x in (it["x_recovered"], it["y_recovered"])),
                                   lambda s: 2*len(s))]),
                                  "nonecho": wilson(*[f([it for it in items if not it["echo_cue"]]) for f in
                                  (lambda s: sum(x for it in s for x in (it["x_recovered"], it["y_recovered"])),
                                   lambda s: 2*len(s))])},
}
json.dump(out, open(f"{REPO}/reports/analysis/gate3_cited_basis.json", "w"), indent=2)
# per-item audit table (markdown) for human review
with open(f"{REPO}/reports/analysis/gate3_cited_basis_items.md", "w") as fh:
    fh.write("| task | target/opp | rec | bucket | echo | basis |\n|---|---|---|---|---|---|\n")
    for it in sorted(items, key=lambda x: x["task_id"]):
        fh.write(f'| {it["task_id"]} | {it["target"][:10]}/{it["opposite"][:10]} | {it["task_recovery"]:.1f} '
                 f'| {it["bucket"]} | {"Y" if it["echo_cue"] else "."} | {it["basis"]} |\n')
print("\nsaved -> reports/analysis/gate3_cited_basis.json + gate3_cited_basis_items.md")
