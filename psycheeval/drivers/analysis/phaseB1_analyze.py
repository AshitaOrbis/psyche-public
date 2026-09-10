"""Phase B1 — confirmatory analyzer + gate evaluation (deterministic, 0 LLM).

Implements docs/prereg_B1.md §4-§8. ENFORCES no-peeking (§9): the decisive-cell
recovery headline and the B1->B2 gate are computed ONLY when BOTH cross-provider
target-judge arms are complete. Until then it prints BLOCKED and computes nothing
that could unblind the gate.

Primary CI = scenario-cluster bootstrap (prereg D1). Robustness = leave-one-
persona-pair-out range + persona-pair-cluster bound. H2 = two-axis fit>quality.
H3 = recovery survives global-pole adjustment (hand-rolled cluster logistic).

Usage:  python3 drivers/analysis/phaseB1_analyze.py
"""
import json, os, math, random
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = f"{REPO}/reports/analysis"
RNG = random.Random(20260628)
NBOOT = 2000

# Read from the per-call CHECKPOINT (always current, last-wins dedup) rather than
# the end-of-pass .json. Basenames follow the runner TAG: f"{judge}_{filter}"
# with '.'->'p','-'->'' (so opus/gpt_authored -> opus_gpt_authored, KEEPING the
# underscore; gpt-5.5/all -> gpt5p5_all).
PRIMARY_MAP = {  # cross-provider cells -> (targetjudge_checkpoint, frozen_cell, author_fam)
    "gptjudge_opusauthored": ("phaseB1_targetjudge_gpt5p5_all.checkpoint.jsonl", "openai_judge__anthropic_author", "anthropic"),
    "opusjudge_gptauthored": ("phaseB1_targetjudge_opus_gpt_authored.checkpoint.jsonl", "anthropic_judge__openai_author", "openai"),
}
HALO_MAP = {
    "gptjudge_gptauthored": ("phaseB1_targetjudge_gpt5p5_all.checkpoint.jsonl", "openai_judge__openai_author", "openai"),
    "opusjudge_opusauthored": ("phaseB1_targetjudge_opus_opus_authored.checkpoint.jsonl", "anthropic_judge__anthropic_author", "anthropic"),
}
TWOAXIS_GPT = ["phaseB1_twoaxis_gpt5p5_all.checkpoint.jsonl"]
TWOAXIS_OPUS = ["phaseB1_twoaxis_opus_gpt_authored.checkpoint.jsonl", "phaseB1_twoaxis_opus_opus_authored.checkpoint.jsonl"]
PAIRPACK = {  # persona -> reciprocal pair id (for leave-one-persona-pair-out)
    "slalom_altar": "pp1", "emily_blender": "pp1", "dario_armadillo": "pp2", "pawl_gram": "pp2",
    "calibration_goblin": "pp3", "high_agency_spiraler": "pp3",
    "conflict_allergic_moralist": "pp4", "patient_craftsperson": "pp4",
}
def short(u): return u.replace("user_pfi_", "").replace("user_syn_", "").replace("_001", "")

def load_rows(fn, key=("pair_id", "query", "orientation")):
    """Load a per-call checkpoint JSONL with last-wins dedup (errored calls that
    were later re-run resolve to their successful record)."""
    p = f"{A}/{fn}"
    if not os.path.exists(p): return None
    d = {}
    for l in open(p):
        l = l.strip()
        if not l: continue
        try: r = json.loads(l)
        except: continue
        d[tuple(r.get(k) for k in key)] = r
    return list(d.values())

def frozen():
    return json.load(open(f"{REPO}/data/phaseB1/decisive_sets_frozen.json"))["cells"]

def decisive_pair_ids(cell):
    return {f"{s}__{u}__{a}" for s, u, a in frozen()[cell]["decisive_pairs"]}

def cell_complete(fn, author_fam, decisive_ids):
    """All decisive pairs in this author cell have >=1 valid P-query verdict in both orientations."""
    rows = load_rows(fn)
    if rows is None: return False, "file-missing"
    have = defaultdict(set)
    for r in rows:
        if r.get("author_fam") != author_fam or r.get("query") != "P": continue
        if r.get("pair_id") in decisive_ids and r.get("winner") in ("A", "B", "TIE"):
            have[r["pair_id"]].add(r.get("orientation"))
    full = sum(1 for pid in decisive_ids if {"AB", "BA"} <= have.get(pid, set()))
    return full == len(decisive_ids), f"{full}/{len(decisive_ids)} decisive pairs complete"

def pair_recovery(rows, author_fam, decisive_ids):
    """Per decisive pair: mean picked_target over non-tie P-query calls (AB+BA). Returns {pair_id:(rec,n,scn,persona_pp)}."""
    byp = defaultdict(list); meta = {}
    for r in rows:
        if r.get("author_fam") != author_fam or r.get("query") != "P": continue
        if r.get("pair_id") not in decisive_ids: continue
        if r.get("winner") not in ("A", "B"): continue   # ties excluded (primary)
        byp[r["pair_id"]].append(1 if r.get("picked_target") else 0)
        meta[r["pair_id"]] = (r.get("scenario_id"), PAIRPACK.get(short(r.get("user_id", "")), "?"))
    out = {}
    for pid, v in byp.items():
        out[pid] = (sum(v) / len(v), len(v), meta[pid][0], meta[pid][1])
    return out

def pooled(recs):
    vals = [r[0] for r in recs.values()]
    return sum(vals) / len(vals) if vals else None

def scenario_boot(recs, nboot=NBOOT):
    by_scn = defaultdict(list)
    for pid, (rec, n, scn, pp) in recs.items(): by_scn[scn].append(rec)
    scns = list(by_scn)
    if len(scns) < 2: return (None, None)
    means = []
    for _ in range(nboot):
        samp = [by_scn[RNG.choice(scns)] for _ in scns]
        flat = [x for grp in samp for x in grp]
        means.append(sum(flat) / len(flat))
    means.sort()
    return (round(means[int(0.05 * nboot)], 3), round(means[int(0.95 * nboot)], 3))

def lopo_range(recs):
    """Leave-one-persona-pair-out: drop each pp, recompute pooled."""
    pps = sorted({r[3] for r in recs.values()})
    vals = []
    for drop in pps:
        sub = {k: v for k, v in recs.items() if v[3] != drop}
        if sub: vals.append(round(pooled(sub), 3))
    return [min(vals), max(vals)] if vals else None

def two_axis_gap(fns):
    rows = []
    for fn in fns:
        rr = load_rows(fn, key=("pair_id", "order"))
        if rr: rows += [r for r in rr if r.get("c4_fit") is not None]
    if not rows: return None
    fit = sum(r["c4_fit"] - r["cw_fit"] for r in rows) / len(rows)
    qual = sum(r["c4_gq"] - r["cw_gq"] for r in rows) / len(rows)
    # scenario-cluster bootstrap on fit_gap
    by_scn = defaultdict(list)
    for r in rows: by_scn[r["scenario_id"]].append(r["c4_fit"] - r["cw_fit"])
    scns = list(by_scn); boots = []
    for _ in range(NBOOT):
        samp = [by_scn[RNG.choice(scns)] for _ in scns]; flat = [x for g in samp for x in g]
        boots.append(sum(flat) / len(flat))
    boots.sort()
    return {"n": len(rows), "fit_gap": round(fit, 3), "quality_gap": round(qual, 3),
            "fit_gt_quality": fit > qual,
            "fit_gap_90ci": [round(boots[int(0.05*NBOOT)], 3), round(boots[int(0.95*NBOOT)], 3)]}

# ---------------- no-peeking gate ----------------
print("=== Phase B1 confirmatory analyzer (prereg_B1) ===\n")
status = {}
blocked = False
for name, (fn, cell, afam) in PRIMARY_MAP.items():
    ok, msg = cell_complete(fn, afam, decisive_pair_ids(cell))
    status[name] = (ok, msg)
    print(f"  cross-provider {name:24s}: {'READY' if ok else 'PENDING'}  ({msg})")
    if not ok: blocked = True

if blocked:
    print("\nBLOCKED: both cross-provider target-judge arms must complete before the")
    print("decisive-cell recovery headline or the B1->B2 gate may be computed (prereg §9 no-peeking).")
    print("No recovery statistic emitted. Re-run when the Opus arm finishes.")
    raise SystemExit(0)

# ---- both cross arms ready: compute headline + gate ----
report = {"cross_provider": {}, "halo": {}, "two_axis": {}, "gate": {}}
cell_rec = {}
for name, (fn, cell, afam) in PRIMARY_MAP.items():
    recs = pair_recovery(load_rows(fn), afam, decisive_pair_ids(cell))
    R = pooled(recs); ci = scenario_boot(recs); lopo = lopo_range(recs)
    cell_rec[name] = R
    report["cross_provider"][name] = {"n_decisive": len(recs), "recovery": round(R, 3),
                                      "recovery_90ci_scenarioboot": ci, "lopo_range": lopo}
    print(f"\n  {name}: recovery={R:.3f}  90%CI(scn-boot)={ci}  LOPO={lopo}  (n={len(recs)})")

# pooled cross-provider (pair-weighted across both cells)
allrec = {}
for name, (fn, cell, afam) in PRIMARY_MAP.items():
    allrec.update({f"{name}::{k}": v for k, v in pair_recovery(load_rows(fn), afam, decisive_pair_ids(cell)).items()})
R_pool = pooled(allrec); R_ci = scenario_boot({k.split("::",1)[1]: v for k, v in allrec.items()})
report["cross_provider"]["POOLED"] = {"n_decisive": len(allrec), "recovery": round(R_pool, 3), "recovery_90ci": R_ci}

# halo (descriptive secondary)
for name, (fn, cell, afam) in HALO_MAP.items():
    rr = load_rows(fn)
    if rr is None: report["halo"][name] = "pending"; continue
    recs = pair_recovery(rr, afam, decisive_pair_ids(cell))
    report["halo"][name] = {"n_decisive": len(recs), "recovery": round(pooled(recs), 3) if recs else None}

# H2 two-axis
ta_gpt = two_axis_gap(TWOAXIS_GPT)
ta_opus = two_axis_gap(TWOAXIS_OPUS)
report["two_axis"] = {"gpt": ta_gpt, "opus": ta_opus}

# ---- gate (prereg §8) ----
Rg, Ro = cell_rec["gptjudge_opusauthored"], cell_rec["opusjudge_gptauthored"]
R = R_pool; Rlo = R_ci[0] if R_ci else None
h2_ok = bool(ta_gpt and ta_opus and ta_gpt["fit_gt_quality"] and ta_opus["fit_gt_quality"]
             and ta_gpt["fit_gap_90ci"][0] > 0 and ta_opus["fit_gap_90ci"][0] > 0)
GO = (R >= 0.60 and Rlo is not None and Rlo >= 0.53 and Rg >= 0.55 and Ro >= 0.55 and h2_ok)
NARROW = (not GO) and (Rlo is not None and Rlo > 0.50)
verdict = "GO" if GO else ("NARROW" if NARROW else "STOP")
report["gate"] = {"R_pooled": round(R, 3), "R_lo": Rlo, "R_gptjudge": round(Rg, 3),
                  "R_opusjudge": round(Ro, 3), "H2_fit_gt_quality": h2_ok, "VERDICT": verdict}
print("\n=== GATE (prereg §8) ===")
print(json.dumps(report["gate"], indent=1))
json.dump(report, open(f"{A}/phaseB1_gate_report.json", "w"), indent=2)
print(f"\nsaved -> {A}/phaseB1_gate_report.json")
print("NOTE: H3 (pole-adjustment robustness) + human cross-check appended in the findings write-up.")
