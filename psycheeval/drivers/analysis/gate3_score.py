"""Gate 3 scoring: blind semantic persona-alignment audit.

Reads Gemini's blind verdicts (which persona each output fits) + the held-out
answer keys (/tmp/gate3_keys.json) and computes whether GENERATION steers text
toward the target persona, decisively separating it from the EVALUATION-side
global-pole bias Gate 2 found.

Key mapping: a verdict says output_X_fits in {1,2}, output_Y_fits in {1,2}
(persona slots). key.P1_persona / P2_persona map slot->{P=target, Q=opposite}.
key.X_cond / Y_cond map slot->{C4=target-conditioned, C4_WRONG=opposite-conditioned}.
An output is "recovered" if Gemini assigned it to the persona that actually
conditioned it (C4->target P; C4_WRONG->opposite Q).
"""
import json, math
from collections import defaultdict

keys = json.load(open("/tmp/gate3_keys.json"))
verdicts = {}
for g in range(4):
    fn = f"reports/analysis/gate3_verdicts_g{g}.json"
    try:
        for v in json.load(open(fn)):
            verdicts[v["task_id"]] = v
    except FileNotFoundError:
        print(f"WARN: {fn} missing")

def wilson(k, n, z=1.96):
    if n == 0: return (None, None, None)
    p = k/n; d = 1+z*z/n
    c = (p+z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return round(p, 3), round(c-h, 3), round(c+h, 3)

# slot (1/2) -> persona label (P/Q) and -> condition; then recovery per output
rows = []  # one per output judgment
for tid, v in verdicts.items():
    if tid not in keys: continue
    k = keys[tid]
    if v.get("output_X_fits") not in (1, 2) or v.get("output_Y_fits") not in (1, 2):
        continue  # parse fail
    slot_persona = {1: k["P1_persona"], 2: k["P2_persona"]}  # -> 'P' or 'Q'
    # output X
    x_assigned_persona = slot_persona[v["output_X_fits"]]      # P or Q
    x_true_persona = "P" if k["X_cond"] == "C4" else "Q"
    rows.append({"tid": tid, "cond": k["X_cond"], "target": k["target_persona"],
                 "opposite": k["opposite_persona"], "recovered": int(x_assigned_persona == x_true_persona),
                 "assigned": x_assigned_persona, "judge_winner": k["judge_winner_condition"]})
    # output Y
    y_assigned_persona = slot_persona[v["output_Y_fits"]]
    y_true_persona = "P" if k["Y_cond"] == "C4" else "Q"
    rows.append({"tid": tid, "cond": k["Y_cond"], "target": k["target_persona"],
                 "opposite": k["opposite_persona"], "recovered": int(y_assigned_persona == y_true_persona),
                 "assigned": y_assigned_persona, "judge_winner": k["judge_winner_condition"]})

n_tasks = len({r["tid"] for r in rows})
print(f"Scored {n_tasks} tasks, {len(rows)} output-judgments "
      f"({len(verdicts)} verdicts collected, {len(verdicts)-n_tasks} parse-fail/missing-key).\n")

# 1) Overall generation-steering: recovery across all outputs
allrec = [r["recovered"] for r in rows]
p, lo, hi = wilson(sum(allrec), len(allrec))
print("=== (1) GENERATION STEERING — does blind Gemini recover the conditioning persona? ===")
print(f"  All outputs:        {p} [{lo}, {hi}]  (n={len(allrec)})   (>0.5 => authors steer text toward the conditioned persona)")
for cond in ("C4", "C4_WRONG"):
    sub = [r["recovered"] for r in rows if r["cond"] == cond]
    pp, l, h = wilson(sum(sub), len(sub))
    print(f"  {cond:<9} outputs:  {pp} [{l}, {h}]  (n={len(sub)})")

# 2) Text-level sign-flip per target persona: of the C4 (target-conditioned)
#    outputs, how often is the C4 output assigned to the TARGET persona?
print("\n=== (2) TEXT-LEVEL alignment of the C4 (own-profile) output, per target persona ===")
print("  (analogue of Gate 2 'own-profile win rate', but blind Gemini on ALIGNMENT not preference)")
per_t = defaultdict(lambda: {"rec": 0, "n": 0})
for r in rows:
    if r["cond"] == "C4":
        per_t[r["target"]]["rec"] += r["recovered"]; per_t[r["target"]]["n"] += 1
for t in sorted(per_t):
    d = per_t[t]; pp, l, h = wilson(d["rec"], d["n"])
    print(f"  {t:<32} {pp} [{l},{h}]  (n={d['n']})")

# 3) Reciprocal-pair sign-flip vs Gate 2
GATE2 = {  # judge-level own-profile win rate from gate2 (for the comparison table)
    "dario_armadillo": 0.80, "pawl_gram": 0.34, "slalom_altar": 0.88, "emily_blender": 0.29,
    "calibration_goblin": 0.54, "high_agency_spiraler": 0.41,
    "conflict_allergic_moralist": 0.72, "patient_craftsperson": 0.54}
PAIRS = [("slalom_altar", "emily_blender"), ("dario_armadillo", "pawl_gram"),
         ("calibration_goblin", "high_agency_spiraler"), ("conflict_allergic_moralist", "patient_craftsperson")]
print("\n=== (3) DECISIVE: text-level alignment (Gate 3) vs judge preference (Gate 2), per reciprocal pair ===")
print(f"  {'pair':<46}{'G3 textA':>9}{'G3 textB':>9}   {'G2 judgeA':>9}{'G2 judgeB':>9}  reading")
for a, b in PAIRS:
    ga = per_t[a]["rec"]/per_t[a]["n"] if per_t[a]["n"] else float('nan')
    gb = per_t[b]["rec"]/per_t[b]["n"] if per_t[b]["n"] else float('nan')
    g2a, g2b = GATE2[a], GATE2[b]
    text_flip = (ga > 0.5 and gb > 0.5)
    judge_flip = (g2a > 0.5 and g2b > 0.5)
    if text_flip and not judge_flip:
        reading = "GEN works / EVAL global-pole-biased"
    elif text_flip and judge_flip:
        reading = "both target-fit"
    elif not text_flip:
        reading = "GEN also weak (text not target-distinct)"
    else:
        reading = "mixed"
    print(f"  {a+' / '+b:<46}{ga:>9.2f}{gb:>9.2f}   {g2a:>9.2f}{g2b:>9.2f}  {reading}")

# 4) Gen-vs-eval cross-tab on C4-vs-C4_WRONG tasks
print("\n=== (4) GEN x EVAL cross-tab (per task) ===")
ct = defaultdict(int)
for tid, v in verdicts.items():
    if tid not in keys: continue
    if v.get("output_X_fits") not in (1, 2) or v.get("output_Y_fits") not in (1, 2): continue
    k = keys[tid]
    slot_persona = {1: k["P1_persona"], 2: k["P2_persona"]}
    # did Gemini recover the C4 output to target?  (gen)
    if k["X_cond"] == "C4":
        c4_assigned = slot_persona[v["output_X_fits"]]
    else:
        c4_assigned = slot_persona[v["output_Y_fits"]]
    gen_ok = (c4_assigned == "P")
    eval_target = (k["judge_winner_condition"] == "C4")  # study judge preferred the target-conditioned output
    ct[(gen_ok, eval_target)] += 1
tot = sum(ct.values())
print(f"  (n={tot} tasks)")
print(f"  gen recovers target  & judge prefers target : {ct[(True,True)]:>3}  ({100*ct[(True,True)]/tot:.0f}%)  target-fit rewarded")
print(f"  gen recovers target  & judge prefers OPPOSITE: {ct[(True,False)]:>3}  ({100*ct[(True,False)]/tot:.0f}%)  EVAL-side global-pole bias (gen worked)")
print(f"  gen MISSES target    & judge prefers target  : {ct[(False,True)]:>3}  ({100*ct[(False,True)]/tot:.0f}%)  judge right w/o clear text steering")
print(f"  gen MISSES target    & judge prefers OPPOSITE : {ct[(False,False)]:>3}  ({100*ct[(False,False)]/tot:.0f}%)  no target signal either side")

out = {
    "n_tasks": n_tasks, "n_output_judgments": len(rows),
    "generation_steering_all": wilson(sum(allrec), len(allrec)),
    "recovery_C4": wilson(sum(r["recovered"] for r in rows if r["cond"]=="C4"), sum(1 for r in rows if r["cond"]=="C4")),
    "recovery_C4_WRONG": wilson(sum(r["recovered"] for r in rows if r["cond"]=="C4_WRONG"), sum(1 for r in rows if r["cond"]=="C4_WRONG")),
    "per_target_C4_alignment": {t: wilson(per_t[t]["rec"], per_t[t]["n"]) for t in per_t},
    "gate2_judge_winrate": GATE2,
    "cross_tab": {f"gen{g}_evaltarget{e}": ct[(g,e)] for g in (True,False) for e in (True,False)},
}
json.dump(out, open("reports/analysis/gate3_results.json", "w"), indent=2)
print("\nsaved -> reports/analysis/gate3_results.json")
