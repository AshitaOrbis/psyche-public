"""Phase A #5 — judge-family x contrast interaction model (deterministic, numpy).

Formalizes trigger #7. Trigger #7 showed 5/11 contrasts have >15pp opus-vs-gpt
judge divergence, all of them contract-structure contrasts. #5 tests this with a
pooled logistic: is the judge-family effect genuinely CONTRAST-SPECIFIC
(heterogeneous, concentrated in structure contrasts) vs a constant judge offset?

  y(treatment condition wins) ~ C(contrast) + judge_anth + C(contrast):judge_anth + slot

LR test (interaction vs main-effect-only) answers "does the judge effect vary by
contrast?"; the per-contrast interaction coefs + descriptive judge gaps show WHERE.
Cross-provider same-author, both orientations (same scope as trigger #7).
Run from repo root.  (numpy on system python3; no venv.)
"""
import json, math, os, numpy as np
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN = f"{REPO}/runs/2026-05-19_v03"
def fam(m): return "openai" if str(m).startswith("gpt") else ("anthropic" if "opus" in str(m) else "other")

outs = {}
for l in open(f"{RUN}/assistant_outputs.jsonl"):
    l = l.strip()
    if not l: continue
    try: r = json.loads(l)
    except: continue
    outs[r["run_id"]] = r
pairwise = []
for fn in ("pairwise_scores.jsonl", "pairwise_swap_scores.jsonl"):
    for l in open(f"{RUN}/{fn}"):
        l = l.strip()
        if l and '\x00' not in l:
            try: pairwise.append(json.loads(l))
            except: pass

# structure contrasts flagged for the "concentration" read
STRUCT = {"C_GENERIC_CONTRACT vs C0", "C4_WRONG_PROFILE vs C0", "C5_CONTRACT vs C5",
          "C5 vs C_GENERIC_CONTRACT", "C5 vs C4_WRONG_PROFILE"}
CONTRASTS = [
    ({"C_GENERIC_CONTRACT", "C0"}, "C_GENERIC_CONTRACT"), ({"C3", "C_GENERIC_CONTRACT"}, "C3"),
    ({"C4", "C_GENERIC_CONTRACT"}, "C4"), ({"C5", "C_GENERIC_CONTRACT"}, "C5"),
    ({"C4_WRONG_PROFILE", "C0"}, "C4_WRONG_PROFILE"), ({"C3", "C4_WRONG_PROFILE"}, "C3"),
    ({"C4", "C4_WRONG_PROFILE"}, "C4"), ({"C4_WRONG_PROFILE", "C5"}, "C5"),
    ({"C5", "C5_NONPUBLIC"}, "C5"), ({"C5_CONTRACT", "C5_NONPUBLIC_CONTRACT"}, "C5_CONTRACT"),
]
def lab(ps, w): return f"{w} vs {[c for c in ps if c != w][0]}"

# build rows; keep only contrasts with BOTH judge families present
recs = defaultdict(list)
for ps, w in CONTRASTS:
    name = lab(ps, w)
    for r in pairwise:
        a = outs.get(r["run_id_a"]); b = outs.get(r["run_id_b"])
        if not a or not b: continue
        ca, cb = str(a.get("condition")), str(b.get("condition"))
        if {ca, cb} != ps: continue
        if a.get("output_model") != b.get("output_model"): continue
        jf = fam(r["judge_model"]); af = fam(a.get("output_model"))
        if jf == af or jf == "other": continue
        if r["winner"] not in ("A", "B"): continue
        w_slot = "A" if ca == w else "B"
        won = 1.0 if r["winner"] == w_slot else 0.0
        recs[name].append({"y": won, "judge_anth": 1.0 if jf == "anthropic" else 0.0,
                           "slot": 1.0 if w_slot == "A" else 0.0})
covered = [n for n in recs if len({r["judge_anth"] for r in recs[n]}) == 2]
print(f"contrasts covered (both judge families): {len(covered)}")

# descriptive per-contrast judge gap
print("\nper-contrast judge-family win gap (anth - gpt):")
desc = {}
for n in covered:
    rs = recs[n]
    a = [r["y"] for r in rs if r["judge_anth"] == 1]; g = [r["y"] for r in rs if r["judge_anth"] == 0]
    gap = (sum(a)/len(a)) - (sum(g)/len(g))
    desc[n] = {"anth": round(sum(a)/len(a), 3), "gpt": round(sum(g)/len(g), 3), "gap_pp": round(gap*100, 1),
               "n_anth": len(a), "n_gpt": len(g), "structure": n in STRUCT}
    print(f"  {n:<38} anth={desc[n]['anth']:.3f} gpt={desc[n]['gpt']:.3f} Δ={desc[n]['gap_pp']:+.1f}pp"
          f"  {'[structure]' if desc[n]['structure'] else ''}")

# pooled design
idx = {n: i for i, n in enumerate(sorted(covered))}
rows = [(r, idx[n]) for n in covered for r in recs[n]]
y = np.array([r["y"] for r, _ in rows])
ci = np.array([c for _, c in rows]); slot = np.array([r["slot"] for r, _ in rows]); ja = np.array([r["judge_anth"] for r, _ in rows])
K = len(covered)
# contrast dummies (ref = contrast 0)
D = np.zeros((len(rows), K - 1))
for r, c in enumerate(ci):
    if c >= 1: D[r, c - 1] = 1.0

def logistic_fit(X, y, iters=100, ridge=1e-3):
    n, p = X.shape; b = np.zeros(p)
    for _ in range(iters):
        mu = 1/(1+np.exp(-(X@b))); W = mu*(1-mu)+1e-9
        g = X.T@(y-mu)-ridge*b; H = -(X.T*W)@X-ridge*np.eye(p)
        try: step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError: break
        b -= step
        if np.max(np.abs(step)) < 1e-9: break
    return b
def ll(X, b, y):
    mu = np.clip(1/(1+np.exp(-(X@b))), 1e-9, 1-1e-9)
    return float(np.sum(y*np.log(mu)+(1-y)*np.log(1-mu)))

# main-effect model: intercept + dummies + judge_anth + slot
Xm = np.column_stack([np.ones(len(rows)), D, ja, slot])
bm = logistic_fit(Xm, y); llm = ll(Xm, bm, y)
# interaction model: + dummy_i * judge_anth
INT = D * ja[:, None]
Xi = np.column_stack([np.ones(len(rows)), D, ja, slot, INT])
bi = logistic_fit(Xi, y); lli = ll(Xi, bi, y)
lr = 2*(lli - llm); df = K - 1
# chi2 survival via series? use simple Wilson-Hilferty approx for p-value
def chi2_sf(x, k):
    # Wilson–Hilferty normal approximation
    if x <= 0: return 1.0
    z = ((x/k)**(1/3) - (1 - 2/(9*k))) / math.sqrt(2/(9*k))
    return 0.5*math.erfc(z/math.sqrt(2))
p_lr = chi2_sf(lr, df)

# interaction coefs back to contrast names (ref contrast has interaction 0 by construction)
ref = sorted(covered)[0]
int_coefs = {}
names_sorted = sorted(covered)
for j, n in enumerate(names_sorted[1:], start=0):
    int_coefs[n] = round(float(bi[1 + (K - 1) + 2 + j]), 3)  # after [intercept, K-1 dummies, judge, slot]

print(f"\nmain-effect judge_anth coef = {round(float(bm[K]), 3)} (constant judge offset)")
print(f"LR test (interaction vs main-effect): LR={round(lr,1)}, df={df}, p≈{p_lr:.1e}")
print(f"  -> judge effect {'VARIES by contrast (heterogeneous)' if p_lr < 0.05 else 'does NOT significantly vary'}")
print(f"interaction coefs (deviation of judge_anth effect from ref contrast '{ref}'):")
for n in names_sorted[1:]:
    print(f"  {n:<38} {int_coefs[n]:+.3f}  {'[structure]' if n in STRUCT else ''}")

# structure vs non-structure mean |gap|
struct_gaps = [abs(desc[n]["gap_pp"]) for n in covered if desc[n]["structure"]]
non_gaps = [abs(desc[n]["gap_pp"]) for n in covered if not desc[n]["structure"]]
print(f"\nmean |judge gap|: structure contrasts = {np.mean(struct_gaps):.1f}pp (n={len(struct_gaps)}) | "
      f"non-structure = {np.mean(non_gaps):.1f}pp (n={len(non_gaps)})")

out = {"n_records": len(rows), "contrasts_covered": covered,
       "per_contrast_judge_gap": desc,
       "main_effect_judge_anth_coef": round(float(bm[K]), 3),
       "LR_interaction_vs_main": round(lr, 2), "df": df, "p_value": p_lr,
       "judge_effect_contrast_specific": p_lr < 0.05,
       "interaction_coefs_vs_ref": {"ref_contrast": ref, **int_coefs},
       "mean_abs_gap_structure_pp": round(float(np.mean(struct_gaps)), 1),
       "mean_abs_gap_nonstructure_pp": round(float(np.mean(non_gaps)), 1)}
json.dump(out, open(f"{REPO}/reports/analysis/phaseA5_judge_contrast_interaction.json", "w"), indent=2)
print("\nsaved -> reports/analysis/phaseA5_judge_contrast_interaction.json")
