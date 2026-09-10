"""Phase A #6 — position/orientation residuals for the Gate-2 global-pole.

Gate 2 found that for 3/4 reciprocal persona pairs, ONE persona's profile (C4)
wins the C4-vs-C4_WRONG contrast regardless of which persona is the target — a
global trait-pole preference, not target-matching. This script asks: does that
asymmetry survive when we split by PRESENTATION, ruling out a slot/position
artifact?

Two independent splits of the SAME cross-provider/same-author C4-vs-C4_WRONG
records used in Gate 2:
  (1) by source file:  AB = pairwise_scores.jsonl (original order),
                       BA = pairwise_swap_scores.jsonl (swapped order).
  (2) by C4 slot:      C4-in-A vs C4-in-B (was the target-conditioned output
                       presented first or second).

If the per-pair global-pole verdict (own-profile rate >0.5 for one persona and
<0.5 for its reciprocal) holds in BOTH halves of BOTH splits, the effect is not
a presentation artifact. Pure stdlib, no deps. Run from repo root.
"""
import json, os
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = f"{REPO}/runs/2026-05-19_v03"
MAP = {
 "user_pfi_slalom_altar_001": "user_pfi_emily_blender_001", "user_pfi_emily_blender_001": "user_pfi_slalom_altar_001",
 "user_pfi_dario_armadillo_001": "user_pfi_pawl_gram_001", "user_pfi_pawl_gram_001": "user_pfi_dario_armadillo_001",
 "user_syn_calibration_goblin_001": "user_syn_high_agency_spiraler_001", "user_syn_high_agency_spiraler_001": "user_syn_calibration_goblin_001",
 "user_syn_conflict_allergic_moralist_001": "user_syn_patient_craftsperson_001", "user_syn_patient_craftsperson_001": "user_syn_conflict_allergic_moralist_001",
}
def fam(m):
    if not m: return "other"
    return "openai" if m.startswith("gpt") else ("anthropic" if "opus" in m else "other")
def short(x): return x.replace('user_pfi_', '').replace('user_syn_', '').replace('_001', '')

outs = {}
for l in open(f"{RUN}/assistant_outputs.jsonl"):
    l = l.strip()
    if not l: continue
    try: r = json.loads(l)
    except: continue
    outs[r["run_id"]] = r

# tag each pairwise record with its source orientation file
recs = []
for fn, orient in (("pairwise_scores.jsonl", "AB"), ("pairwise_swap_scores.jsonl", "BA")):
    for l in open(f"{RUN}/{fn}"):
        l = l.strip()
        if l and '\x00' not in l:
            try:
                r = json.loads(l); r["_orient"] = orient; recs.append(r)
            except: pass

# per (target_user, split-cell) own-profile win counts
cells = defaultdict(lambda: defaultdict(lambda: {"win": 0, "n": 0}))  # cell_name -> user -> {win,n}
def add(cell, user, won):
    cells[cell][user]["win"] += won; cells[cell][user]["n"] += 1

for r in recs:
    a = outs.get(r["run_id_a"]); b = outs.get(r["run_id_b"])
    if not a or not b: continue
    ca, cb = str(a.get("condition")), str(b.get("condition"))
    if {ca, cb} != {"C4", "C4_WRONG_PROFILE"}: continue
    if a.get("output_model") != b.get("output_model"): continue
    jf = fam(r["judge_model"]); af = fam(a.get("output_model"))
    if jf == af or jf == "other": continue
    if r["winner"] not in ("A", "B"): continue
    if ca == "C4": t_slot = "A"; target_user = a.get("user_id")
    else: t_slot = "B"; target_user = b.get("user_id")
    if target_user not in MAP: continue
    won = 1 if r["winner"] == t_slot else 0
    add("ALL", target_user, won)
    add(f"file:{r['_orient']}", target_user, won)      # split (1): orientation file
    add(f"C4slot:{t_slot}", target_user, won)          # split (2): C4 output position

PAIRS = [("user_pfi_dario_armadillo_001", "user_pfi_pawl_gram_001"),
         ("user_pfi_slalom_altar_001", "user_pfi_emily_blender_001"),
         ("user_syn_calibration_goblin_001", "user_syn_high_agency_spiraler_001"),
         ("user_syn_conflict_allergic_moralist_001", "user_syn_patient_craftsperson_001")]

def verdict(ra, rb):
    if ra is None or rb is None: return "n/a"
    if ra > 0.5 and rb > 0.5: return "MATCHING"
    if (ra > 0.5) != (rb > 0.5): return "GLOBAL-POLE"
    return "anti-matching"

def rate(cell, u):
    d = cells[cell][u]
    return (d["win"] / d["n"] if d["n"] else None), d["n"]

SPLITS = ["ALL", "file:AB", "file:BA", "C4slot:A", "C4slot:B"]
print("=== #6 POSITION/ORIENTATION RESIDUALS of the Gate-2 global-pole ===")
print("own-profile win rate (C4 beats C4_WRONG on the persona's own scenarios); a/b = reciprocal pair\n")
hdr = f"{'reciprocal pair':<34}" + "".join(f"{s:>16}" for s in SPLITS)
print(hdr)
summary = {}
for a, b in PAIRS:
    line = f"{short(a)[:14]+'/'+short(b)[:14]:<34}"
    pair_verdicts = {}
    for s in SPLITS:
        ra, na = rate(s, a); rb, nb = rate(s, b)
        v = verdict(ra, rb)
        pair_verdicts[s] = {"a_rate": ra, "a_n": na, "b_rate": rb, "b_n": nb, "verdict": v}
        cell = f"{(ra if ra is not None else float('nan')):.2f}/{(rb if rb is not None else float('nan')):.2f}"
        line += f"{cell:>16}"
    print(line)
    # verdict row
    vline = f"{'  -> verdict':<34}" + "".join(f"{pair_verdicts[s]['verdict'][:14]:>16}" for s in SPLITS)
    print(vline)
    # n row (min cell n across the pair, per split) to flag thin cells
    nline = f"{'  -> min n/persona':<34}" + "".join(
        f"{('%d/%d' % (pair_verdicts[s]['a_n'], pair_verdicts[s]['b_n'])):>16}" for s in SPLITS)
    print(nline + "\n")
    summary[f"{short(a)}/{short(b)}"] = pair_verdicts

# robustness check: for each pair, does the ALL verdict reproduce across all 4 sub-splits?
print("=== ROBUSTNESS: does the ALL verdict hold across all 4 presentation sub-splits? ===")
robust = {}
for a, b in PAIRS:
    name = f"{short(a)}/{short(b)}"
    allv = summary[name]["ALL"]["verdict"]
    subs = [summary[name][s]["verdict"] for s in ("file:AB", "file:BA", "C4slot:A", "C4slot:B")]
    ok = all(v == allv for v in subs)
    robust[name] = {"all_verdict": allv, "subsplit_verdicts": subs, "stable_across_all_splits": ok}
    print(f"  {name:<40} ALL={allv:<13} sub={subs}  -> {'STABLE' if ok else 'NOT stable (presentation-sensitive)'}")

json.dump({"per_pair": summary, "robustness": robust},
          open(f"{REPO}/reports/analysis/gate6_position_residuals.json", "w"), indent=2)
print("\nsaved -> reports/analysis/gate6_position_residuals.json")
