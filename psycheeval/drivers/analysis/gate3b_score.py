"""Gate 3b scoring — de-echoed blind recovery vs Gate 3 baseline.

Same recovery metric as gate3_score.py, on the de-echoed outputs. Reports overall
recovery, C4 vs C4_WRONG, per-target, and the head-to-head delta vs Gate 3 (0.93).
High recovery after de-echo => recovery is not driven by verbatim contract-echo;
collapse toward 0.5 => it was.
"""
import json, math
from collections import defaultdict

keys = json.load(open("/tmp/gate3b_keys.json"))
verdicts = {}
for g in range(4):
    fn = f"reports/analysis/gate3b_verdicts_g{g}.json"
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

rows = []
for tid, v in verdicts.items():
    if tid not in keys: continue
    if v.get("output_X_fits") not in (1, 2) or v.get("output_Y_fits") not in (1, 2): continue
    k = keys[tid]
    sp = {1: k["P1_persona"], 2: k["P2_persona"]}
    for slot_key, cond_key in (("output_X_fits", "X_cond"), ("output_Y_fits", "Y_cond")):
        assigned = sp[v[slot_key]]
        true_p = "P" if k[cond_key] == "C4" else "Q"
        rows.append({"cond": k[cond_key], "target": k["target_persona"],
                     "recovered": int(assigned == true_p)})

n_tasks = len({tid for tid in verdicts if tid in keys})
allrec = [r["recovered"] for r in rows]
print(f"Gate 3b (DE-ECHOED) — scored {len(verdicts)} verdicts, {len(rows)} output-judgments\n")
p, lo, hi = wilson(sum(allrec), len(allrec))
print("=== de-echoed blind recovery ===")
print(f"  All outputs:      {p} [{lo}, {hi}]  (n={len(allrec)})   [Gate 3 baseline: 0.93]")
for cond in ("C4", "C4_WRONG"):
    sub = [r["recovered"] for r in rows if r["cond"] == cond]
    pp, l, h = wilson(sum(sub), len(sub))
    base = {"C4": 0.953, "C4_WRONG": 0.906}[cond]
    print(f"  {cond:<9} outputs:{pp} [{l}, {h}]  (n={len(sub)})   [Gate 3: {base}]")

per_t = defaultdict(lambda: {"rec": 0, "n": 0})
for r in rows:
    if r["cond"] == "C4":
        per_t[r["target"]]["rec"] += r["recovered"]; per_t[r["target"]]["n"] += 1
print("\n=== per-target C4 (own-profile) de-echoed alignment ===")
for t in sorted(per_t):
    d = per_t[t]; pp, l, h = wilson(d["rec"], d["n"])
    print(f"  {t:<32} {pp} [{l},{h}]  (n={d['n']})")

delta = (sum(allrec)/len(allrec)) - 0.93 if allrec else None
print(f"\n=== INTERPRETATION ===")
if delta is not None:
    print(f"  de-echoed recovery {sum(allrec)/len(allrec):.3f} vs Gate 3 0.930  (Δ {delta:+.3f})")
    print("  >=~0.75 -> recovery survives verbatim-echo removal (behavioral content, not crude copying)")
    print("  toward 0.50 -> recovery was contract-echo")
    print("  NOTE: only ~1.2% of output words were maskable as verbatim 4-gram echo, so this")
    print("  test rules out CRUDE COPYING only; paraphrased/stylistic echo needs the neutral-")
    print("  paraphrase test (v0.4 decisive).")
out = {"recovery_all": wilson(sum(allrec), len(allrec)),
       "recovery_C4": wilson(sum(r["recovered"] for r in rows if r["cond"]=="C4"), sum(1 for r in rows if r["cond"]=="C4")),
       "recovery_C4_WRONG": wilson(sum(r["recovered"] for r in rows if r["cond"]=="C4_WRONG"), sum(1 for r in rows if r["cond"]=="C4_WRONG")),
       "gate3_baseline_all": 0.93, "n_tasks": n_tasks}
json.dump(out, open("reports/analysis/gate3b_results.json", "w"), indent=2)
print("\nsaved -> reports/analysis/gate3b_results.json")
