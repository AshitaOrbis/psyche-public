"""Phase B1 — H3: does target-recovery survive adjusting for the global-pole index?

prereg_B1 H3/§8: if H1 passes but recovery vanishes once the deterministic
global-pole index is adjusted for, the verdict is capped at NARROW. Tests that
the target-conditioned pick is NOT merely the judge following the globally
preferred pole.

Full-universe P-query (non-tie) observations across the TWO cross-provider cells.
Outcome: picked_target. Covariate: pole_z = z-scored desirability_as_wrong of the
pair's C4_WRONG persona (per judge family, leave-one-out) = the pole pull AWAY
from the target. Hand-rolled IRLS logistic; scenario-cluster bootstrap CI on the
adjusted (mean-pole) recovery. Also prints descriptive full-universe secondaries.
"""
import json, os, math, random
from collections import defaultdict, Counter

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = f"{REPO}/reports/analysis"
RNG = random.Random(20260629); NBOOT = 2000

def short(u): return u.replace("user_pfi_", "").replace("user_syn_", "").replace("_001", "")
POLE = json.load(open(f"{REPO}/data/phaseB1/global_pole_index.json"))["per_pair_judge_loo"]

def load(fn):
    p = f"{A}/{fn}"; d = {}
    for l in open(p):
        l = l.strip()
        if l:
            r = json.loads(l); d[(r.get("pair_id"), r.get("query"), r.get("orientation"))] = r
    return list(d.values())

CELLS = [("phaseB1_targetjudge_gpt5p5_all.checkpoint.jsonl", "anthropic", "openai"),    # gpt judge, opus-authored
         ("phaseB1_targetjudge_opus_gpt_authored.checkpoint.jsonl", "openai", "anthropic")]  # opus judge, gpt-authored

# build P-query non-tie observations with pole covariate
ys, poles, scns = [], [], []
desc = defaultdict(Counter)  # descriptive: per query, picked_target / tie / n
for fn, author_fam, judge_fam in CELLS:
    for r in load(fn):
        if r.get("author_fam") != author_fam: continue
        q = r.get("query"); w = r.get("winner")
        desc[q]["n"] += 1
        if w == "TIE": desc[q]["tie"] += 1
        if w in ("A", "B") and r.get("picked_target") is not None:
            desc[q]["nontie"] += 1
            if r.get("picked_target"): desc[q]["picked_target"] += 1
        if q != "P" or w not in ("A", "B"): continue
        key = f"{r['pair_id']}||{judge_fam}"
        pv = POLE.get(key)
        if pv is None: continue
        ys.append(1.0 if r.get("picked_target") else 0.0)
        poles.append(pv); scns.append(r["pair_id"].split("__")[0])

n = len(ys)
mp = sum(poles) / n; sd = (sum((p - mp) ** 2 for p in poles) / n) ** 0.5 or 1.0
pz = [(p - mp) / sd for p in poles]

def irls(y, x1):
    # logistic y ~ 1 + x1, Newton-Raphson
    b0, b1 = 0.0, 0.0
    for _ in range(50):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for yi, xi in zip(y, x1):
            eta = b0 + b1 * xi; p = 1 / (1 + math.exp(-eta)); w = p * (1 - p)
            g0 += (yi - p); g1 += (yi - p) * xi
            h00 += w; h01 += w * xi; h11 += w * xi * xi
        det = h00 * h11 - h01 * h01
        if abs(det) < 1e-9: break
        db0 = (h11 * g0 - h01 * g1) / det; db1 = (-h01 * g0 + h00 * g1) / det
        b0 += db0; b1 += db1
        if abs(db0) + abs(db1) < 1e-8: break
    return b0, b1

b0, b1 = irls(ys, pz)
inv = lambda e: 1 / (1 + math.exp(-e))
rec_meanpole = inv(b0)            # adjusted recovery at mean pole
rec_hi1 = inv(b0 + b1 * 1)        # at +1 SD pole pull-away
rec_hi2 = inv(b0 + b1 * 2)        # at +2 SD

# scenario-cluster bootstrap on adjusted mean-pole recovery
by_scn = defaultdict(list)
for yi, xi, s in zip(ys, pz, scns): by_scn[s].append((yi, xi))
scn_keys = list(by_scn); boots = []
for _ in range(NBOOT):
    Y, X = [], []
    for _ in scn_keys:
        for yi, xi in by_scn[RNG.choice(scn_keys)]: Y.append(yi); X.append(xi)
    bb0, _ = irls(Y, X); boots.append(inv(bb0))
boots.sort(); ci = (round(boots[int(0.05 * NBOOT)], 3), round(boots[int(0.95 * NBOOT)], 3))

unadj = sum(ys) / n
H3_pass = ci[0] > 0.50
out = {"n_obs": n, "unadjusted_recovery": round(unadj, 3),
       "pole_coef_b1": round(b1, 3),
       "adjusted_recovery_at_mean_pole": round(rec_meanpole, 3),
       "adjusted_recovery_90ci_scenboot": ci,
       "recovery_at_+1SD_pole": round(rec_hi1, 3), "recovery_at_+2SD_pole": round(rec_hi2, 3),
       "H3_PASS_recovery_survives_pole_adjustment": H3_pass}
print("=== H3: recovery vs global-pole adjustment (full-universe P-query, cross-provider) ===")
print(json.dumps(out, indent=1))
print("\n=== descriptive full-universe secondaries (cross-provider cells) ===")
for q in ("P", "Q"):
    c = desc[q]; nt = c["nontie"]
    pt = round(c["picked_target"] / nt, 3) if nt else None
    print(f"  query={q}: n={c['n']} tie_rate={round(c['tie']/c['n'],3)} "
          f"picks_target(non-tie)={pt} (n_nontie={nt})")
json.dump(out, open(f"{A}/phaseB1_h3.json", "w"), indent=1)
print(f"\nsaved -> {A}/phaseB1_h3.json")
