"""Gate 3 prepare (GPT Pro #4): blind semantic persona-alignment audit.

Decisive separation of WHERE personalization (fails): generation vs evaluation.

For C4-vs-C4_WRONG decisive cross-provider same-author pairwise records:
  - C4 output was generated under the TARGET persona P's behavioral contract.
  - C4_WRONG output (same scenario, same author) was generated under the
    OPPOSITE persona Q's contract.
A non-study model (Gemini 3.1 Pro) is shown BOTH contracts (relabelled, order
randomized) and BOTH outputs (order randomized), blind to condition, and asked
to assign each output to the contract it best embodies (behaviour, not polish).

If Gemini recovers the generating contract (>50%), the AUTHOR steered the text
toward the target -> generation works; the study-judge's failure to reward the
target (Gate 2 global-pole) is an EVALUATION-side bias. If Gemini is at chance,
generation also fails (profiles don't produce target-distinct text).

Cross-tab with the study-judge winner separates the two stories cleanly.
"""
import json, random, re
from collections import defaultdict
RUN = "runs/2026-05-19_v03"
N_PER_TARGET = 8
PROFILE_CAP = 4000
RESP_CAP = 2200
SEED = 20260617

MAP = {
 "user_pfi_slalom_altar_001": "user_pfi_emily_blender_001", "user_pfi_emily_blender_001": "user_pfi_slalom_altar_001",
 "user_pfi_dario_armadillo_001": "user_pfi_pawl_gram_001", "user_pfi_pawl_gram_001": "user_pfi_dario_armadillo_001",
 "user_syn_calibration_goblin_001": "user_syn_high_agency_spiraler_001", "user_syn_high_agency_spiraler_001": "user_syn_calibration_goblin_001",
 "user_syn_conflict_allergic_moralist_001": "user_syn_patient_craftsperson_001", "user_syn_patient_craftsperson_001": "user_syn_conflict_allergic_moralist_001",
}
def short(u): return u.replace("user_pfi_", "").replace("user_syn_", "").replace("_001", "")
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

# ---- Build a uniform, de-leaked FULL behavioral brief per persona. -----------
# Most personas' C4 is full standalone; pawl_gram's C4 is delta-form ("Everything
# in C3, plus:"), so reconstruct it = C3 base + delta. Strip study tokens (C3/C4,
# "Everything in C3, plus") so the blind coder cannot match on condition artifacts
# or on profile completeness. Both P and Q briefs are then format-matched.
def prof_for(user, cond):
    for r in outs.values():
        if r.get("user_id") == user and str(r.get("condition")) == cond:
            return r.get("profile_text_supplied", "") or ""
    return ""
def deleak(t):
    t = re.sub(r'Everything in C3[, ]*plus:?', '', t)
    t = re.sub(r'\bC[0-5]\b', 'the base profile', t)
    return t.strip()
def full_brief(user):
    c4 = prof_for(user, "C4"); c3 = prof_for(user, "C3")
    if c4.lstrip().startswith("Everything in C3"):
        delta = c4.split("plus:", 1)[1] if "plus:" in c4 else c4
        full = c3.rstrip() + "\n\n" + delta.lstrip()
    else:
        full = c4
    return deleak(full)[:PROFILE_CAP]
PERSONA_BRIEF = {u: full_brief(u) for u in MAP}

pairwise = []
for fn in ("pairwise_scores.jsonl", "pairwise_swap_scores.jsonl"):
    for l in open(f"{RUN}/{fn}"):
        l = l.strip()
        if l and '\x00' not in l:
            try: pairwise.append(json.loads(l))
            except: pass

# collect candidate C4-vs-C4_WRONG decisive records, keyed by target persona
cand = defaultdict(list)
seen_pairwise = set()
for r in pairwise:
    a = outs.get(r["run_id_a"]); b = outs.get(r["run_id_b"])
    if not a or not b: continue
    ca, cb = str(a.get("condition")), str(b.get("condition"))
    if {ca, cb} != {"C4", "C4_WRONG_PROFILE"}: continue
    if a.get("output_model") != b.get("output_model"): continue
    jf = fam(r["judge_model"]); af = fam(a.get("output_model"))
    if jf == af or jf == "other": continue
    if r["winner"] not in ("A", "B"): continue
    c4 = a if ca == "C4" else b
    cw = b if ca == "C4" else a
    target = c4.get("user_id")
    if target not in MAP: continue
    # dedupe on the unordered output pair (avoid AB and BA of same pair both entering)
    key = tuple(sorted([c4["run_id"], cw["run_id"]]))
    if key in seen_pairwise: continue
    seen_pairwise.add(key)
    # study-judge winner condition
    win_cond = ca if r["winner"] == "A" else cb
    cand[target].append({
        "c4_run": c4["run_id"], "cw_run": cw["run_id"],
        "scenario_id": r["scenario_id"], "author": c4.get("output_model"),
        "judge_winner_condition": win_cond,
    })

rng = random.Random(SEED)
tasks = []
tid = 0
for target in sorted(cand):
    items = cand[target][:]
    rng.shuffle(items)
    picks = items[:N_PER_TARGET]
    opp = MAP[target]
    for it in picks:
        c4 = outs[it["c4_run"]]; cw = outs[it["cw_run"]]
        # uniform full briefs by persona identity (NOT the stored per-output fragment)
        P_brief = PERSONA_BRIEF[target]              # target's own behavioral brief
        Q_brief = PERSONA_BRIEF[MAP[target]]         # opposite persona's behavioral brief
        out_c4 = (c4.get("assistant_response", "") or "")[:RESP_CAP]
        out_cw = (cw.get("assistant_response", "") or "")[:RESP_CAP]
        # randomize output order (X/Y) and persona-label order (1/2)
        swap_out = rng.random() < 0.5
        swap_persona = rng.random() < 0.5
        if swap_out:
            outX, outY = out_cw, out_c4; X_cond, Y_cond = "C4_WRONG", "C4"
        else:
            outX, outY = out_c4, out_cw; X_cond, Y_cond = "C4", "C4_WRONG"
        if swap_persona:
            P1_brief, P2_brief = Q_brief, P_brief; P1_persona, P2_persona = "Q", "P"
        else:
            P1_brief, P2_brief = P_brief, Q_brief; P1_persona, P2_persona = "P", "Q"
        tasks.append({
            "task_id": f"t{tid:03d}", "target_persona": short(target), "opposite_persona": short(opp),
            "scenario_id": it["scenario_id"], "author": it["author"],
            "judge_winner_condition": it["judge_winner_condition"],
            "_key": {"X_cond": X_cond, "Y_cond": Y_cond, "P1_persona": P1_persona, "P2_persona": P2_persona},
            "persona_1_brief": P1_brief, "persona_2_brief": P2_brief,
            "output_X": outX, "output_Y": outY,
        })
        tid += 1

PROMPT_TMPL = """You are a behavioral-style coder. You see two PERSONA BRIEFS (behavioral guidelines for two different people) and two RESPONSES written to the same situation. Decide which persona each response was most plausibly written FOR, based on OBSERVABLE BEHAVIOR: directness vs gentleness, risk posture, depth vs brevity, validation vs problem-solving, assertiveness vs deference, boundary handling, how it opens and closes. Judge FIT to behavioral style, NOT writing quality, polish, or which response is "better". Weigh demonstrated stance over surface keyword overlap.

Each response was written for exactly one of the two personas; they need not split (both could fit the same persona better, if the text warrants it).

=== PERSONA 1 BRIEF ===
{p1}

=== PERSONA 2 BRIEF ===
{p2}

=== RESPONSE X ===
{ox}

=== RESPONSE Y ===
{oy}

Return ONLY a JSON object on one line, no prose, no markdown fences:
{{"output_X_fits": 1 or 2, "output_Y_fits": 1 or 2, "confidence_0_1": <float 0-1>, "basis": "<=18 words on the behavioral axis you used"}}"""

import os
os.makedirs("reports/analysis/gate3_prompts", exist_ok=True)
keys = {}
GROUP_SIZE = 16
for i, t in enumerate(tasks):
    g = i // GROUP_SIZE
    fn = f"reports/analysis/gate3_prompts/g{g}_{t['task_id']}.txt"
    open(fn, "w").write(PROMPT_TMPL.format(p1=t["persona_1_brief"], p2=t["persona_2_brief"],
                                           ox=t["output_X"], oy=t["output_Y"]))
    keys[t["task_id"]] = {"group": g, "X_cond": t["_key"]["X_cond"], "Y_cond": t["_key"]["Y_cond"],
                          "P1_persona": t["_key"]["P1_persona"], "P2_persona": t["_key"]["P2_persona"],
                          "target_persona": t["target_persona"], "opposite_persona": t["opposite_persona"],
                          "scenario_id": t["scenario_id"], "author": t["author"],
                          "judge_winner_condition": t["judge_winner_condition"]}

# Keys + full tasks go to /tmp ONLY (Gemini's workspace root is .../psyche and it
# WILL autonomously read answer-bearing files there; /tmp is out of its reach).
json.dump(keys, open("/tmp/gate3_keys.json", "w"), indent=2)
json.dump(tasks, open("/tmp/gate3_tasks_full.json", "w"), indent=2)
# Remove any earlier answer-bearing artifacts from the workspace.
for stale in ["reports/analysis/gate3_tasks.json"] + \
             [f"reports/analysis/gate3_tasks_{a}__{b}.json" for a, b in
              [("slalom_altar","emily_blender"),("dario_armadillo","pawl_gram"),
               ("calibration_goblin","high_agency_spiraler"),("conflict_allergic_moralist","patient_craftsperson")]]:
    if os.path.exists(stale): os.remove(stale)

ngroups = (len(tasks) + GROUP_SIZE - 1) // GROUP_SIZE
print(f"Wrote {len(tasks)} de-identified prompt files -> reports/analysis/gate3_prompts/ (groups g0..g{ngroups-1})")
print("Answer keys -> /tmp/gate3_keys.json (out of Gemini's reach). Workspace holds NO answers.")
print("per-target counts:", {short(k): min(len(v), N_PER_TARGET) for k, v in sorted(cand.items())})
for g in range(ngroups):
    print(f"  group g{g}: {sum(1 for kk in keys.values() if kk['group']==g)} tasks")
