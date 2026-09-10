"""Phase B1 — score human-rater codes against the key + the LLM judges.

Reads one or more 'PHASEB1HR|rater=...|hr_000=A|...' codes (from stdin, or file
paths as argv), grades each rater's fit picks vs the frozen target, computes
human<->LLM-judge agreement on the same pairs, and (>=2 raters) inter-rater
agreement. The rater HTML never contains the key, so this is a genuine check.

Usage:
  pbpaste | python3 drivers/analysis/phaseB1_score_human.py
  python3 drivers/analysis/phaseB1_score_human.py codes.txt
"""
import json, os, re, sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = f"{REPO}/reports/analysis"
KEY = json.load(open(f"{REPO}/runs/2026-05-19_v03/phaseB1_human_rater_key.SECRET.json"))
KEY = {k["item_id"]: k for k in KEY}

# LLM judge per cross-provider cell
JUDGE_FILE = {"openai_judge__anthropic_author": "phaseB1_targetjudge_gpt5p5_all.checkpoint.jsonl",
              "anthropic_judge__openai_author": "phaseB1_targetjudge_opus_gpt_authored.checkpoint.jsonl"}
def load_ck(fn):
    d = {}
    for l in open(f"{A}/{fn}"):
        l = l.strip()
        if l:
            r = json.loads(l); d[(r.get("pair_id"), r.get("query"), r.get("orientation"))] = r
    return list(d.values())
# per pair_id: LLM majority picked_target on the P-query
LLM = {}
for cell, fn in JUDGE_FILE.items():
    byp = defaultdict(list)
    for r in load_ck(fn):
        if r.get("query") == "P" and r.get("winner") in ("A", "B"):
            byp[r["pair_id"]].append(1 if r.get("picked_target") else 0)
    for pid, v in byp.items():
        LLM[pid] = sum(v) / len(v) > 0.5

def parse(text):
    out = {}
    for m in re.finditer(r"PHASEB1HR\|rater=([^|]*)\|(.+)", text):
        rater = m.group(1).strip() or "anon"
        ans = {}
        for tok in m.group(2).split("|"):
            if "=" in tok:
                k, v = tok.split("=", 1); ans[k.strip()] = v.strip().upper()
        out[rater] = ans
    return out

text = ""
if len(sys.argv) > 1:
    for p in sys.argv[1:]: text += open(p).read() + "\n"
else:
    text = sys.stdin.read()
raters = parse(text)
if not raters:
    print("No PHASEB1HR codes found. Paste the code(s) from the rater tool."); raise SystemExit(1)

per_rater = {}
for rater, ans in raters.items():
    n = dec = dec_hit = hit = ties = agree = agree_n = 0
    picks = {}  # item -> target?(bool) for inter-rater
    for iid, ch in ans.items():
        k = KEY.get(iid)
        if not k: continue
        if ch == "T": ties += 1; continue
        slot = ch  # 'A' or 'B'
        human_target = (slot == k["target_slot"])
        n += 1; hit += human_target; picks[iid] = human_target
        if k["decisive"]: dec += 1; dec_hit += human_target
        pid = f"{k['scenario_id']}__{k['user_id']}__{k['author']}"
        if pid in LLM:
            agree_n += 1; agree += (human_target == LLM[pid])
    per_rater[rater] = {"answered_nontie": n, "ties": ties,
                        "human_recovery_all": round(hit / n, 3) if n else None,
                        "human_recovery_decisive": round(dec_hit / dec, 3) if dec else None,
                        "n_decisive": dec,
                        "agreement_with_LLM_judge": round(agree / agree_n, 3) if agree_n else None,
                        "picks": picks}

print("=== HUMAN RATER SCORING (vs frozen target + LLM judge) ===")
for rater, s in per_rater.items():
    print(f"\n[{rater}] answered {s['answered_nontie']} (+{s['ties']} ties)")
    print(f"  human recovery — all: {s['human_recovery_all']}   decisive: {s['human_recovery_decisive']} (n={s['n_decisive']})")
    print(f"  agreement with the LLM judge: {s['agreement_with_LLM_judge']}")
    print(f"  (LLM judge decisive recovery for reference: 0.636 pooled cross-provider)")

# inter-rater (>=2)
names = list(per_rater)
if len(names) >= 2:
    print("\n=== INTER-RATER (pairwise, on shared non-tie items) ===")
    for x in range(len(names)):
        for y in range(x + 1, len(names)):
            a, b = per_rater[names[x]]["picks"], per_rater[names[y]]["picks"]
            shared = set(a) & set(b)
            if not shared: continue
            agree = sum(1 for i in shared if a[i] == b[i]) / len(shared)
            # Cohen kappa on target?(bool)
            pa = agree
            pax = sum(a[i] for i in shared) / len(shared); pbx = sum(b[i] for i in shared) / len(shared)
            pe = pax * pbx + (1 - pax) * (1 - pbx)
            kappa = (pa - pe) / (1 - pe) if pe < 1 else 1.0
            print(f"  {names[x]} vs {names[y]}: {len(shared)} shared, %agree={round(agree,3)}, Cohen κ={round(kappa,3)}")
print("\nNote: human–LLM agreement >~0.6 supports judge validity; κ<0.40 between humans flags task ambiguity (prereg §10).")
