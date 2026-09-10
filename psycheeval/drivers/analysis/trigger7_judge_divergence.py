"""Failure-trigger #7 (predeclared): opus-vs-OpenAI judge divergence on T1 pairs.

For each T1 headline contrast, compute the position-controlled decisive win rate
of the nominal winner condition, stratified by JUDGE family (anthropic/opus vs
openai/gpt). Flag any pair where the two judge families disagree by >15pp.

IMPORTANT confound: the scope is cross-provider, same-author (judge family !=
author family). So an opus judge only ever scores gpt-authored outputs, and a
gpt judge only ever scores opus-authored outputs. Per-judge-family stratification
is therefore CONFOUNDED with author family: a divergence could be the judge
disagreeing OR the two author families producing different-quality outputs for
that contrast. This gates "judge-unanimous" wording, which is the conservative
use regardless of which mechanism drives a divergence.
"""
import json
from collections import defaultdict
RUN = "runs/2026-05-19_v03"

def fam(m):
    if not m: return "other"
    return "openai" if m.startswith("gpt") else ("anthropic" if "opus" in m else "other")

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

# (pair_set, winner_condition) for each T1 headline contrast + inherited §6 claims
CONTRASTS = [
    ({"C_GENERIC_CONTRACT", "C0"}, "C_GENERIC_CONTRACT"),
    ({"C3", "C_GENERIC_CONTRACT"}, "C3"),
    ({"C4", "C_GENERIC_CONTRACT"}, "C4"),
    ({"C5", "C_GENERIC_CONTRACT"}, "C5"),
    ({"C4_WRONG_PROFILE", "C0"}, "C4_WRONG_PROFILE"),
    ({"C3", "C4_WRONG_PROFILE"}, "C3"),
    ({"C4", "C4_WRONG_PROFILE"}, "C4"),
    ({"C4_WRONG_PROFILE", "C5"}, "C5"),
    ({"C5", "C5_NONPUBLIC"}, "C5"),
    ({"C5_CONTRACT", "C5_NONPUBLIC_CONTRACT"}, "C5_CONTRACT"),
    # inherited §6 claims that carry strong wording ("Judge-unanimous", "Robust")
    ({"C4", "C5"}, "C4"),
    ({"C4", "C1_padded"}, "C4"),
    ({"C5_CONTRACT", "C5"}, "C5_CONTRACT"),
    ({"C4", "C4_shuffled"}, "C4"),
]

def label(pair_set, winner):
    other = [c for c in pair_set if c != winner][0]
    return f"{winner} vs {other}"

results = []
for pair_set, winner in CONTRASTS:
    by_jf = defaultdict(lambda: {"win": 0, "n": 0})
    for r in pairwise:
        a = outs.get(r["run_id_a"]); b = outs.get(r["run_id_b"])
        if not a or not b: continue
        ca, cb = str(a.get("condition")), str(b.get("condition"))
        if {ca, cb} != pair_set: continue
        if a.get("output_model") != b.get("output_model"): continue
        jf = fam(r["judge_model"]); af = fam(a.get("output_model"))
        if jf == af or jf == "other": continue
        if r["winner"] not in ("A", "B"): continue
        if ca == winner: w_slot = "A"
        elif cb == winner: w_slot = "B"
        else: continue
        won = 1 if ((r["winner"] == "A" and w_slot == "A") or (r["winner"] == "B" and w_slot == "B")) else 0
        by_jf[jf]["win"] += won; by_jf[jf]["n"] += 1
    op = by_jf["anthropic"]; oa = by_jf["openai"]
    r_op = op["win"]/op["n"] if op["n"] else None
    r_oa = oa["win"]/oa["n"] if oa["n"] else None
    div = abs(r_op - r_oa) if (r_op is not None and r_oa is not None) else None
    results.append({
        "contrast": label(pair_set, winner),
        "opus_judge_win": round(r_op, 3) if r_op is not None else None, "opus_n": op["n"],
        "gpt_judge_win": round(r_oa, 3) if r_oa is not None else None, "gpt_n": oa["n"],
        "divergence_pp": round(div*100, 1) if div is not None else None,
        "fires_gt15pp": (div is not None and div > 0.15),
    })

print(json.dumps(results, indent=2))
fired = [r["contrast"] for r in results if r["fires_gt15pp"]]
print("\n=== TRIGGER #7 SUMMARY ===")
print(f"Contrasts checked: {len(results)}")
print(f"Pairs with >15pp opus-vs-gpt divergence: {len(fired)}")
for c in fired:
    rr = next(r for r in results if r["contrast"] == c)
    print(f"  FIRES: {c}  opus={rr['opus_judge_win']} (n={rr['opus_n']})  gpt={rr['gpt_judge_win']} (n={rr['gpt_n']})  Δ={rr['divergence_pp']}pp")
if not fired:
    print("  none — no T1 pair shows >15pp judge-family divergence; 'judge-unanimous'-style wording is licensed (subject to the author-family confound note).")
