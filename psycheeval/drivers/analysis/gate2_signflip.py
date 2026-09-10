"""Gate 2 (GPT Pro #3): is 'matching' true target-matching, or a global
preference for one trait-pole regardless of target?

OPPOSITE_TRAIT_MAPPING is reciprocal (A<->B). On A's scenarios, C4 uses A's
profile and C4_WRONG uses B's profile; on B's scenarios, C4 uses B's and
C4_WRONG uses A's. If matching is real, the *target's own* profile should win
on its own scenarios in BOTH directions (sign-flip). If one profile (pole)
wins regardless of target, the C4>C4_WRONG result is a global trait preference,
not matching.

Test: for each reciprocal persona pair (A,B), on the C4-vs-C4_WRONG contrast,
compute the win rate of A's-profile-output when the target scenario belongs to
A (should win if matching) vs when target belongs to B (should LOSE if
matching). Cross-provider, same-author, both orientations.
"""
import json
from collections import defaultdict
RUN="runs/2026-05-19_v03"
MAP={
 "user_pfi_slalom_altar_001":"user_pfi_emily_blender_001","user_pfi_emily_blender_001":"user_pfi_slalom_altar_001",
 "user_pfi_dario_armadillo_001":"user_pfi_pawl_gram_001","user_pfi_pawl_gram_001":"user_pfi_dario_armadillo_001",
 "user_syn_calibration_goblin_001":"user_syn_high_agency_spiraler_001","user_syn_high_agency_spiraler_001":"user_syn_calibration_goblin_001",
 "user_syn_conflict_allergic_moralist_001":"user_syn_patient_craftsperson_001","user_syn_patient_craftsperson_001":"user_syn_conflict_allergic_moralist_001",
}
def fam(m):
    if not m: return "other"
    return "openai" if m.startswith("gpt") else ("anthropic" if "opus" in m else "other")
outs={}
for l in open(f"{RUN}/assistant_outputs.jsonl"):
    l=l.strip()
    if not l: continue
    try: r=json.loads(l)
    except: continue
    outs[r["run_id"]]=r

pairwise=[]
for fn in ("pairwise_scores.jsonl","pairwise_swap_scores.jsonl"):
    for l in open(f"{RUN}/{fn}"):
        l=l.strip()
        if l and '\x00' not in l:
            try: pairwise.append(json.loads(l))
            except: pass

# For each C4 vs C4_WRONG record: target scenario belongs to persona = the user_id of the C4 output
# (C4 = correct profile for that scenario's persona). The C4_WRONG output uses the OPPOSITE persona's profile.
# Win = does the target-persona's-own-profile (C4) beat the opposite-profile (C4_WRONG)?
# Stratify by the target persona to see if some personas' profiles always win.
per_target=defaultdict(lambda:{"target_win":0,"n":0})
for r in pairwise:
    a=outs.get(r["run_id_a"]); b=outs.get(r["run_id_b"])
    if not a or not b: continue
    ca,cb=str(a.get("condition")),str(b.get("condition"))
    if {ca,cb}!={"C4","C4_WRONG_PROFILE"}: continue
    if a.get("output_model")!=b.get("output_model"): continue
    jf=fam(r["judge_model"]); af=fam(a.get("output_model"))
    if jf==af or jf=="other": continue
    if r["winner"] not in ("A","B"): continue
    # the C4 side = target persona's own profile
    if ca=="C4": t_slot="A"; target_user=a.get("user_id")
    else: t_slot="B"; target_user=b.get("user_id")
    won = 1 if ((r["winner"]=="A" and t_slot=="A") or (r["winner"]=="B" and t_slot=="B")) else 0
    per_target[target_user]["target_win"]+=won; per_target[target_user]["n"]+=1

print("Per-target-persona: does the persona's OWN profile (C4) beat the opposite profile (C4_WRONG)?")
print(f"{'persona':<42}{'opp':<42}{'own-profile win rate':>22}  n")
# group reciprocal pairs
seen=set()
global_pref=[]
for u in sorted(per_target):
    opp=MAP.get(u,"?")
    d=per_target[u]; rate=d['target_win']/d['n'] if d['n'] else None
    print(f"{u:<42}{opp:<42}{rate:>22.3f}  {d['n']}")
print()
print("SIGN-FLIP CHECK per reciprocal pair: if matching is real, BOTH personas' own-profile win rate > 0.5.")
print("If a pole wins globally, one side > 0.5 and the other < 0.5 (the same profile wins both directions).")
for u in sorted(per_target):
    opp=MAP.get(u)
    if not opp or (opp,u) in seen or u not in per_target or opp not in per_target: continue
    seen.add((u,opp))
    ra=per_target[u]['target_win']/per_target[u]['n']
    rb=per_target[opp]['target_win']/per_target[opp]['n']
    # matching: both own-profiles win (>0.5). global: one own-profile wins, other's own-profile loses (<0.5)
    verdict = "MATCHING (both own-profiles win)" if (ra>0.5 and rb>0.5) else ("GLOBAL-POLE (one profile wins both targets)" if (ra>0.5)!=(rb>0.5) else "both own-profiles LOSE (anti-matching)")
    short=lambda x:x.replace('user_pfi_','').replace('user_syn_','').replace('_001','')
    print(f"  {short(u)} own={ra:.2f}  |  {short(opp)} own={rb:.2f}  ->  {verdict}")
