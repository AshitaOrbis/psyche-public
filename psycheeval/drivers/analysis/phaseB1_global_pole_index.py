"""Phase B1 — deterministic per-judge global-pole calibration index (0 LLM calls).

Per prereg_B1 §6: each persona's GLOBAL-POLE DESIRABILITY = the win-rate of
outputs generated under that persona's profile when that persona is the WRONG
profile (C4_WRONG_PROFILE side) in an unconditional C4-vs-C4_WRONG comparison.
A persona whose style the judge generically prefers wins even as the wrong
profile -> that is exactly the global-pole pull the target-conditioned judge
must overcome. Computed PER JUDGE FAMILY (pole preference is judge-specific).

Emits:
  - per-(persona, judge_fam) desirability_as_wrong (the calibration table)
  - per-(pair, judge_fam) LEAVE-ONE-OUT covariate: desirability of the pair's
    C4_WRONG persona, excluding that pair's own records (the value the
    confirmatory model joins on, so the covariate is not circular).

Source: runs/2026-05-19_v03/{pairwise_scores,pairwise_swap_scores}.jsonl
(unconditional judgments) joined to assistant_outputs by run_id.
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
def jfam(m): return "openai" if str(m).startswith("gpt") else ("anthropic" if "opus" in str(m) else "other")

outs = {}
for l in open(f"{RUN}/assistant_outputs.jsonl"):
    l = l.strip()
    if l:
        try: r = json.loads(l); outs[r["run_id"]] = r
        except: pass

# Collect, per (persona-as-wrong, judge_fam), records: (pair_id, won_bool)
# pair_id = (scenario,user,author) of the C4 target side (the pair under target-cond test)
recs = defaultdict(list)   # (wrong_persona, jf) -> [(pair_id, won)]
for fn in ("pairwise_scores.jsonl", "pairwise_swap_scores.jsonl"):
    p = f"{RUN}/{fn}"
    if not os.path.exists(p): continue
    for l in open(p):
        l = l.strip()
        if not l or '\x00' in l: continue
        try: r = json.loads(l)
        except: continue
        a = outs.get(r.get("run_id_a")); b = outs.get(r.get("run_id_b"))
        if not a or not b: continue
        ca, cb = str(a.get("condition")), str(b.get("condition"))
        if {ca, cb} != {"C4", "C4_WRONG_PROFILE"}: continue
        if a.get("output_model") != b.get("output_model"): continue
        if a.get("scenario_id") != b.get("scenario_id") or a.get("user_id") != b.get("user_id"): continue
        win = str(r.get("winner", "")).strip().upper()
        if win not in ("A", "B"): continue
        c4 = a if ca == "C4" else b
        cw = b if ca == "C4" else a
        target = c4.get("user_id")
        if target not in MAP: continue
        wrong_persona = MAP[target]            # the C4_WRONG profile persona
        cw_won = (win == "A" and a is cw) or (win == "B" and b is cw)
        jf = jfam(r.get("judge_model"))
        pair_id = f"{c4.get('scenario_id')}__{target}__{c4.get('output_model')}"
        recs[(wrong_persona, jf)].append((pair_id, bool(cw_won)))

def short(u): return u.replace("user_pfi_", "").replace("user_syn_", "").replace("_001", "")

# per-(persona, judge_fam) desirability_as_wrong
table = {}
for (persona, jf), rs in sorted(recs.items()):
    wins = sum(1 for _, w in rs if w)
    table[f"{short(persona)}__{jf}"] = {"persona": short(persona), "judge_fam": jf,
                                        "n": len(rs), "desirability_as_wrong": round(wins / len(rs), 4)}

# per-(pair, judge_fam) leave-one-out covariate
loo = {}
for (persona, jf), rs in recs.items():
    by_pair = defaultdict(list)
    for pid, w in rs: by_pair[pid].append(w)
    total_wins = sum(1 for _, w in rs if w); total_n = len(rs)
    for pid in by_pair:
        own_n = len(by_pair[pid]); own_wins = sum(1 for w in by_pair[pid] if w)
        rem_n = total_n - own_n; rem_wins = total_wins - own_wins
        loo[f"{pid}||{jf}"] = round(rem_wins / rem_n, 4) if rem_n > 0 else None

os.makedirs(f"{REPO}/data/phaseB1", exist_ok=True)
out = {"definition": "desirability_as_wrong[persona,judge_fam] = win-rate of persona's output when it is the C4_WRONG profile, unconditional judge; per-pair LOO excludes that pair's own records",
       "source": "pairwise_scores.jsonl + pairwise_swap_scores.jsonl joined to assistant_outputs",
       "per_persona_judge": table,
       "per_pair_judge_loo": loo}
json.dump(out, open(f"{REPO}/data/phaseB1/global_pole_index.json", "w"), indent=1)

print("=== global-pole desirability (win-rate as the WRONG profile), per persona x judge ===")
for k in sorted(table, key=lambda k: (table[k]["judge_fam"], -table[k]["desirability_as_wrong"])):
    t = table[k]
    print(f"  {t['judge_fam']:9s}  {t['persona']:28s}  desirability={t['desirability_as_wrong']:.3f}  (n={t['n']})")
print(f"\nper-pair LOO covariates: {len(loo)} entries")
print(f"saved -> data/phaseB1/global_pole_index.json")
