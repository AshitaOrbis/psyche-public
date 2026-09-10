"""Gate 3b prepare — DE-ECHOED blind recovery (GPT Pro round-2 "cheapest decisive test").

Gate 3 found 93% blind recovery, but the coder's bases often cite surface
CONTRACT-ECHO (the output repeating the contract's phrasing), so the 93% may be
discriminability via echo, not behavioral adaptation. This re-runs the identical
blind audit with each output's verbatim contract-echo MASKED, so any surviving
recovery must come from behavioral content (decisions / reasoning / stance), not
from repeated contract language.

De-echo (deterministic, lexical): for each output, mask every maximal run of >=4
consecutive words that also appears as a 4-gram in THAT output's own conditioning
contract (profile_text_supplied), plus a small set of trait/anchor words. Masked
spans -> "[...]". Substantive content not present in the contract is preserved.

Interpretation (GPT Pro): recovery stays >=~.75 -> behavioral adaptation; collapses
toward .50 -> mostly contract-echo; .60-.70 -> mixed.

Briefs shown to the coder are the SAME full de-leaked persona briefs as Gate 3
(unchanged) — only the OUTPUTS are de-echoed.
"""
import json, random, re
from collections import defaultdict
RUN = "runs/2026-05-19_v03"
N_PER_TARGET = 8
PROFILE_CAP = 4000
RESP_CAP = 2600        # de-echoed text expands slightly with [...] markers
NGRAM = 4
SEED = 20260617        # SAME seed as Gate 3 -> same task sampling/order for paired comparison

MAP = {
 "user_pfi_slalom_altar_001": "user_pfi_emily_blender_001", "user_pfi_emily_blender_001": "user_pfi_slalom_altar_001",
 "user_pfi_dario_armadillo_001": "user_pfi_pawl_gram_001", "user_pfi_pawl_gram_001": "user_pfi_dario_armadillo_001",
 "user_syn_calibration_goblin_001": "user_syn_high_agency_spiraler_001", "user_syn_high_agency_spiraler_001": "user_syn_calibration_goblin_001",
 "user_syn_conflict_allergic_moralist_001": "user_syn_patient_craftsperson_001", "user_syn_patient_craftsperson_001": "user_syn_conflict_allergic_moralist_001",
}
TRAIT_WORDS = set("""direct gentle assertive deferential agentic cautious risk-averse risk-seeking
concrete terse expansive blunt warm cold skeptical validating boundary accommodation contrarian
conscientious spontaneous humble confident careful""".split())
def short(u): return u.replace("user_pfi_", "").replace("user_syn_", "").replace("_001", "")
def fam(m):
    if not m: return "other"
    return "openai" if m.startswith("gpt") else ("anthropic" if "opus" in m else "other")

def norm_words(t):
    return re.findall(r"[A-Za-z']+", (t or "").lower())

def deecho(output, contract):
    """Mask >=NGRAM-word spans of output that appear in contract; mask trait words. Returns (masked_text, frac_masked)."""
    if not output: return output, 0.0
    cwords = norm_words(contract)
    cgrams = set()
    for i in range(len(cwords) - NGRAM + 1):
        cgrams.add(tuple(cwords[i:i+NGRAM]))
    # tokenize output keeping offsets of word tokens
    toks = list(re.finditer(r"[A-Za-z']+", output))
    owords = [m.group(0).lower() for m in toks]
    mask = [False]*len(owords)
    for i in range(len(owords) - NGRAM + 1):
        if tuple(owords[i:i+NGRAM]) in cgrams:
            for j in range(i, i+NGRAM): mask[j] = True
    for i, w in enumerate(owords):
        if w in TRAIT_WORDS: mask[i] = True
    # rebuild output, replacing maximal masked runs with [...]
    out = []
    last = 0
    i = 0
    n_masked = sum(mask)
    while i < len(toks):
        if mask[i]:
            # start of a masked run; emit text before it, then a single marker, skip the run
            out.append(output[last:toks[i].start()])
            j = i
            while j < len(toks) and mask[j]: j += 1
            out.append("[…]")
            last = toks[j-1].end()
            i = j
        else:
            i += 1
    out.append(output[last:])
    masked_text = "".join(out)
    masked_text = re.sub(r"(\s*\[…\]\s*){2,}", " […] ", masked_text)  # collapse adjacent markers
    return masked_text.strip(), (n_masked/max(len(owords),1))

# ---- load
outs = {}
for l in open(f"{RUN}/assistant_outputs.jsonl"):
    l = l.strip()
    if not l: continue
    try: r = json.loads(l)
    except: continue
    outs[r["run_id"]] = r

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

cand = defaultdict(list); seen = set()
for r in pairwise:
    a = outs.get(r["run_id_a"]); b = outs.get(r["run_id_b"])
    if not a or not b: continue
    ca, cb = str(a.get("condition")), str(b.get("condition"))
    if {ca, cb} != {"C4", "C4_WRONG_PROFILE"}: continue
    if a.get("output_model") != b.get("output_model"): continue
    jf = fam(r["judge_model"]); af = fam(a.get("output_model"))
    if jf == af or jf == "other": continue
    if r["winner"] not in ("A", "B"): continue
    c4 = a if ca == "C4" else b; cw = b if ca == "C4" else a
    target = c4.get("user_id")
    if target not in MAP: continue
    key = tuple(sorted([c4["run_id"], cw["run_id"]]))
    if key in seen: continue
    seen.add(key)
    cand[target].append({"c4_run": c4["run_id"], "cw_run": cw["run_id"],
                         "scenario_id": r["scenario_id"], "author": c4.get("output_model"),
                         "judge_winner_condition": ca if r["winner"] == "A" else cb})

rng = random.Random(SEED)
PROMPT_TMPL = """You are a behavioral-style coder. You see two PERSONA BRIEFS (behavioral guidelines for two different people) and two RESPONSES written to the same situation. Some phrases in the responses have been redacted as "[…]" — IGNORE the redactions and judge only the remaining visible behavior. Decide which persona each response was most plausibly written FOR, based on OBSERVABLE BEHAVIORAL CHOICES: what it recommends, its reasoning priorities, risk posture, what it includes vs omits, how it opens and closes, directness vs gentleness, assertiveness vs deference. Judge FIT to behavioral style, NOT writing quality or which response is "better".

Each response was written for exactly one of the two personas; they need not split.

=== PERSONA 1 BRIEF ===
{p1}

=== PERSONA 2 BRIEF ===
{p2}

=== RESPONSE X ===
{ox}

=== RESPONSE Y ===
{oy}

Return ONLY a JSON object on one line, no prose, no markdown fences:
{{"output_X_fits": 1 or 2, "output_Y_fits": 1 or 2, "confidence_0_1": <float 0-1>, "basis": "<=18 words on the behavioral choice you used"}}"""

import os
os.makedirs("reports/analysis/gate3b_prompts", exist_ok=True)
keys = {}; tasks = []; tid = 0; mask_fracs = []
for target in sorted(cand):
    items = cand[target][:]; rng.shuffle(items); picks = items[:N_PER_TARGET]
    for it in picks:
        c4 = outs[it["c4_run"]]; cw = outs[it["cw_run"]]
        # de-echo each output against its OWN conditioning contract
        oc4, f4 = deecho((c4.get("assistant_response","") or ""), (c4.get("profile_text_supplied","") or ""))
        ocw, fw = deecho((cw.get("assistant_response","") or ""), (cw.get("profile_text_supplied","") or ""))
        mask_fracs += [f4, fw]
        oc4 = oc4[:RESP_CAP]; ocw = ocw[:RESP_CAP]
        swap_out = rng.random() < 0.5; swap_persona = rng.random() < 0.5
        if swap_out: outX, outY, X_cond, Y_cond = ocw, oc4, "C4_WRONG", "C4"
        else: outX, outY, X_cond, Y_cond = oc4, ocw, "C4", "C4_WRONG"
        if swap_persona: P1, P2, P1p, P2p = PERSONA_BRIEF[MAP[target]], PERSONA_BRIEF[target], "Q", "P"
        else: P1, P2, P1p, P2p = PERSONA_BRIEF[target], PERSONA_BRIEF[MAP[target]], "P", "Q"
        g = tid // 16
        fn = f"reports/analysis/gate3b_prompts/g{g}_t{tid:03d}.txt"
        open(fn, "w").write(PROMPT_TMPL.format(p1=P1, p2=P2, ox=outX, oy=outY))
        keys[f"t{tid:03d}"] = {"group": g, "X_cond": X_cond, "Y_cond": Y_cond, "P1_persona": P1p, "P2_persona": P2p,
                               "target_persona": short(target), "opposite_persona": short(MAP[target]),
                               "judge_winner_condition": it["judge_winner_condition"]}
        tid += 1

json.dump(keys, open("/tmp/gate3b_keys.json", "w"), indent=2)
import statistics as st
ngroups = (tid + 15)//16
print(f"Wrote {tid} de-echoed prompt files -> reports/analysis/gate3b_prompts/ (groups g0..g{ngroups-1})")
print(f"mean fraction of output words masked as contract-echo: {st.mean(mask_fracs):.3f} (median {st.median(mask_fracs):.3f}, max {max(mask_fracs):.3f})")
print("keys -> /tmp/gate3b_keys.json. Briefs unchanged from Gate 3; only outputs de-echoed.")
for g in range(ngroups):
    print(f"  group g{g}: {sum(1 for k in keys.values() if k['group']==g)} tasks")
