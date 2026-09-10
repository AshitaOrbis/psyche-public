"""Phase A #3 — global-pole-index regression (deterministic; numpy only).

Independent confirmation of Gate 2 by regression. Gate 2 showed (descriptively)
that the C4>C4_WRONG "matching" win is mostly a GLOBAL TRAIT-POLE preference,
not target-fit. This decomposes the same cross-provider/same-author
C4-vs-C4_WRONG records with a differenced logistic:

  y(anchor's output wins) ~ match_diff + pole_diff + surface_diffs + slot + judge_family

Each reciprocal pair {A,B} is oriented ANCHOR-FIRST (anchor = min(user_id)), so
the target-match term is NOT degenerate:
  match_diff   = +1 if anchor is the scenario's target (anchor=C4), else -1
  pole_diff    = desirability(anchor) - desirability(other), LEAVE-ONE-OUT
                 where desirability(P) = win rate of P's output when P is NOT the
                 target (i.e. P used as the wrong profile) -> a global-pole index
  surface_diff = D3 features (log word count, packet overlap, hedging/100w), z-scored
  slot         = was anchor's output in slot A or B (position control)
  judge_family = anthropic(1)/openai(0)

Decisive read: if beta_match shrinks toward 0 once pole_diff enters, Gate 2 is
confirmed by an independent method — the "matching" win is the global pole, not
target-fit. Run from repo root: python3 drivers/analysis/gate2_global_pole_reg.py
"""
import json, math, os, numpy as np

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
    outs[r["run_id"]] = {"cond": r.get("condition"), "author": r.get("output_model"),
                         "user": r.get("user_id"), "scn": r.get("scenario_id")}
d3 = json.load(open(f"{REPO}/reports/metrics_2026-05-19_v03.json"))["reward_hacking_diagnostics"]["per_output"]
def feat(rid):
    f = d3.get(rid)
    if not f: return None
    return np.array([math.log(max(f.get("word_count", 1) or 1, 1)),
                     float(f.get("source_packet_lexical_overlap", 0) or 0),
                     float(f.get("hedging_frequency_per_100w", 0) or 0)])

pairwise = []
for fn in ("pairwise_scores.jsonl", "pairwise_swap_scores.jsonl"):
    for l in open(f"{RUN}/{fn}"):
        l = l.strip()
        if l and '\x00' not in l:
            try: pairwise.append(json.loads(l))
            except: pass

def logistic_fit(X, y, iters=80, ridge=1e-3):
    n, p = X.shape; b = np.zeros(p)
    for _ in range(iters):
        mu = 1/(1+np.exp(-(X@b))); W = mu*(1-mu)+1e-9
        g = X.T@(y-mu)-ridge*b; H = -(X.T*W)@X-ridge*np.eye(p)
        try: step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError: break
        b -= step
        if np.max(np.abs(step)) < 1e-9: break
    return b

# ---- pass 1: collect decisive records + global desirability tallies ----------
recs = []
desir_win = {}; desir_n = {}   # P -> wins / n when P is the OPPOSITE (not target)
for r in pairwise:
    a = outs.get(r["run_id_a"]); b = outs.get(r["run_id_b"])
    if not a or not b: continue
    if tuple(sorted([str(a["cond"]), str(b["cond"])])) != ("C4", "C4_WRONG_PROFILE"): continue
    if a["author"] != b["author"]: continue
    jf = fam(r["judge_model"]); af = fam(a["author"])
    if jf == af or jf == "other": continue
    if r["winner"] not in ("A", "B"): continue
    # identify C4 (target) and C4_WRONG (opposite) sides. NOTE: both outputs share
    # the scenario's user_id (the target). The opposite POLE is the profile C4_WRONG
    # was conditioned on = MAP[target] (derived, not read from the record's user_id).
    if str(a["cond"]) == "C4": c4, cw, c4_slot = a, b, "A"; c4_rid, cw_rid = r["run_id_a"], r["run_id_b"]
    else:                       c4, cw, c4_slot = b, a, "B"; c4_rid, cw_rid = r["run_id_b"], r["run_id_a"]
    p_t = c4["user"]
    if p_t not in MAP: continue
    p_o = MAP[p_t]                       # opposite pole = reciprocal persona (C4_WRONG's profile)
    c4_won = 1 if r["winner"] == c4_slot else 0
    cw_won = 1 - c4_won
    # opposite pole p_o gets a "not target" observation (its profile, as the WRONG one, won?)
    desir_win[p_o] = desir_win.get(p_o, 0) + cw_won; desir_n[p_o] = desir_n.get(p_o, 0) + 1
    recs.append({"p_t": p_t, "p_o": p_o, "c4_rid": c4_rid, "cw_rid": cw_rid,
                 "rid_a": r["run_id_a"], "c4_slot": c4_slot, "c4_won": c4_won, "cw_won": cw_won,
                 "judge": jf, "author": c4["author"], "scn": r["scenario_id"]})

# ---- pass 2: build differenced design (anchor-first), leave-one-out pole ------
def des_loo(P, is_opposite_here, won_here):
    w, n = desir_win.get(P, 0), desir_n.get(P, 0)
    if is_opposite_here and n > 1:
        return (w - won_here) / (n - 1)
    return (w / n) if n else 0.5

rows = []
for rc in recs:
    p_t, p_o = rc["p_t"], rc["p_o"]
    anchor = min(p_t, p_o); other = p_t if anchor == p_o else p_o
    anchor_is_target = (anchor == p_t)
    # anchor's output + win
    if anchor_is_target:
        a_rid, o_rid = rc["c4_rid"], rc["cw_rid"]; a_won = rc["c4_won"]
        a_is_opp, a_won_opp = False, 0
        o_is_opp, o_won_opp = True, rc["cw_won"]     # other is the opposite here
    else:
        a_rid, o_rid = rc["cw_rid"], rc["c4_rid"]; a_won = rc["cw_won"]
        a_is_opp, a_won_opp = True, rc["cw_won"]      # anchor is the opposite here
        o_is_opp, o_won_opp = False, 0
    fa, fo = feat(a_rid), feat(o_rid)
    if fa is None or fo is None: continue
    match_diff = 1.0 if anchor_is_target else -1.0
    pole_diff = des_loo(anchor, a_is_opp, a_won_opp) - des_loo(other, o_is_opp, o_won_opp)
    slot = 1.0 if a_rid == rc["rid_a"] else 0.0     # was anchor's output in slot A?
    judge_anth = 1.0 if rc["judge"] == "anthropic" else 0.0
    cl = (frozenset((p_t, p_o)), rc["scn"], rc["author"])
    rows.append({"y": float(a_won), "match": match_diff, "pole": pole_diff,
                 "surf": fa - fo, "slot": slot, "judge": judge_anth, "cl": cl})

n = len(rows)
y = np.array([r["y"] for r in rows])
match = np.array([r["match"] for r in rows])
pole = np.array([r["pole"] for r in rows])
surf = np.vstack([r["surf"] for r in rows])
slot = np.array([r["slot"] for r in rows])
judge = np.array([r["judge"] for r in rows])
# z-score the continuous predictors (match/slot/judge kept on native scale)
polez = (pole - pole.mean()) / (pole.std() + 1e-9)
surfz = (surf - surf.mean(0)) / (surf.std(0) + 1e-9)

def fit_named(cols):
    X = np.column_stack([np.ones(n)] + [c[1] for c in cols])
    b = logistic_fit(X, y)
    return {name: round(float(coef), 3) for (name, _), coef in zip([("intercept", None)] + cols, b)}

M1 = fit_named([("match", match)])
M2 = fit_named([("match", match), ("pole_z", polez)])
M3 = fit_named([("match", match), ("pole_z", polez),
                ("surf_loglen_z", surfz[:, 0]), ("surf_overlap_z", surfz[:, 1]),
                ("surf_hedge_z", surfz[:, 2]), ("slot", slot), ("judge_anth", judge)])

# cluster bootstrap for beta_match in M1 vs M2 (the decisive shrinkage)
clusters = {}
for i, r in enumerate(rows): clusters.setdefault(r["cl"], []).append(i)
keys = list(clusters); rng = np.random.default_rng(11)
bm1, bm2, bp2 = [], [], []
for _ in range(2000):
    idx = []
    for k in rng.choice(len(keys), len(keys)): idx.extend(clusters[keys[k]])
    idx = np.array(idx)
    try:
        X1 = np.column_stack([np.ones(len(idx)), match[idx]])
        X2 = np.column_stack([np.ones(len(idx)), match[idx], polez[idx]])
        b1 = logistic_fit(X1, y[idx]); b2 = logistic_fit(X2, y[idx])
        bm1.append(b1[1]); bm2.append(b2[1]); bp2.append(b2[2])
    except Exception: pass
def ci(a):
    a = np.sort([x for x in a if x == x])
    return [round(float(np.percentile(a, 2.5)), 3), round(float(np.percentile(a, 97.5)), 3)] if len(a) > 20 else None

print(f"=== #3 GLOBAL-POLE-INDEX REGRESSION (n={n} decisive C4-vs-C4_WRONG records) ===")
print("Persona global desirability (win rate when used as the WRONG profile, i.e. NOT the target):")
for P in sorted(desir_n, key=lambda p: -desir_win[p]/desir_n[p]):
    print(f"   {short(P):<28} {desir_win[P]/desir_n[P]:.3f}  (n={desir_n[P]})")
print("\nLogistic coefficients (anchor-first differenced design; match on ±1 scale, others z/0-1):")
print(f"  M1  y ~ match                         : {M1}")
print(f"  M2  y ~ match + pole_z                : {M2}")
print(f"  M3  y ~ match + pole_z + surface+slot+judge : {M3}")
print(f"\nDECISIVE — beta_match shrinkage when global-pole enters:")
print(f"  beta_match  M1 = {M1['match']:+.3f}  [{ci(bm1)}]   (raw matching effect)")
print(f"  beta_match  M2 = {M2['match']:+.3f}  [{ci(bm2)}]   (after global-pole control)")
print(f"  beta_pole_z M2 = {M2['pole_z']:+.3f}  [{ci(bp2)}]   (global-pole effect)")
shrink = (M1['match'] - M2['match']) / M1['match'] if M1['match'] else float('nan')
print(f"  -> beta_match shrinks {100*shrink:.0f}% toward 0 once global-pole desirability is included.")

out = {"n_records": n,
       "persona_global_desirability": {short(P): round(desir_win[P]/desir_n[P], 3) for P in desir_n},
       "M1_match_only": M1, "M2_match_pole": M2, "M3_full": M3,
       "beta_match_M1": M1["match"], "beta_match_M1_ci": ci(bm1),
       "beta_match_M2": M2["match"], "beta_match_M2_ci": ci(bm2),
       "beta_pole_M2": M2["pole_z"], "beta_pole_M2_ci": ci(bp2),
       "match_shrinkage_frac_when_pole_added": round(shrink, 3)}
json.dump(out, open(f"{REPO}/reports/analysis/gate2_global_pole_reg.json", "w"), indent=2)
print("\nsaved -> reports/analysis/gate2_global_pole_reg.json")
