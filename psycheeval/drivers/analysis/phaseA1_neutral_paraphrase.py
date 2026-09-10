"""Phase A #1 — neutral-paraphrase blind recovery (the decisive echo-vs-adaptation test).

Gate 3 found blind persona recovery 0.93; Gate 3b (4-gram de-echo) held at 0.96,
ruling out *crude verbatim* copying. But the coder's bases still cite short
distinctive phrases / tone / format (#7: 33% echo-citing). This is the stronger
test: rewrite each output into a NEUTRAL house style that PRESERVES decisions /
reasoning / ordering / risk-posture / omissions but STRIPS tone / formatting /
profile-specific phrasing, then re-run the blind Gemini recovery on the
paraphrased pairs (briefs unchanged).

  recovery >= ~.75  -> persona survives surface-stripping => genuine behavioral adaptation
  recovery  -> ~.50  -> recovery was mostly surface/echo
  recovery .60-.70   -> mixed

Paraphraser: Sonnet 4.6 (non-study, non-judge) via claude CLI. Judge: gemini-3.1-pro
via agy (non-study coder), run from an EMPTY cwd for blindness (answer key stays in
/tmp, loaded only by Python for scoring — never handed to agy).

Resumable per stage. Usage (repo root):
  python3 drivers/analysis/phaseA1_neutral_paraphrase.py [paraphrase|judge|score|all]
"""
import json, os, re, subprocess, sys, time, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STAGE = sys.argv[1] if len(sys.argv) > 1 else "all"
PARA_CACHE = f"{REPO}/reports/analysis/gate1np_paraphrases.jsonl"
VERDICTS = f"{REPO}/reports/analysis/gate1np_verdicts.jsonl"
OUT = f"{REPO}/reports/analysis/gate1np_results.json"
AGY_CWD = os.path.expanduser("~/.cache/agy_blind")
os.makedirs(AGY_CWD, exist_ok=True)
PARA_WORKERS, JUDGE_WORKERS = 3, 2
RESP_CAP = 2200

tasks = json.load(open("/tmp/gate3_tasks_full.json"))
keys = json.load(open("/tmp/gate3_keys.json"))

PARA_PROMPT = """Rewrite the assistant response below into a NEUTRAL, uniform house style.

PRESERVE EXACTLY (do not change): every decision, recommendation, suggestion, and piece of advice; the reasoning and the order it is presented in; what is included and what is deliberately left out; the risk posture (cautious vs bold, hedged vs confident); every question asked; the overall stance and substance. If the response declines, challenges, or reframes the request, keep that exactly.

STRIP / NEUTRALIZE: tone and voice; ALL formatting (no bullet points, headers, bold, or numbered lists — use plain prose paragraphs only); distinctive, stylized, or signature phrasings; rhetorical tics and catchphrases. Convert wording to plain, flat, neutral phrasing.

Do NOT add, remove, or alter any substantive content, recommendation, or reasoning. Do NOT infer, describe, or hint at anything about the user's personality. Output ONLY the rewritten response as plain prose — no preamble, no commentary, no quotes.

RESPONSE TO REWRITE:
---
%s
---"""

# Gate-3 coder prompt (identical to gate3_prepare.PROMPT_TMPL) so recovery is comparable.
CODER_TMPL = """You are a behavioral-style coder. You see two PERSONA BRIEFS (behavioral guidelines for two different people) and two RESPONSES written to the same situation. Decide which persona each response was most plausibly written FOR, based on OBSERVABLE BEHAVIOR: directness vs gentleness, risk posture, depth vs brevity, validation vs problem-solving, assertiveness vs deference, boundary handling, how it opens and closes. Judge FIT to behavioral style, NOT writing quality, polish, or which response is "better". Weigh demonstrated stance over surface keyword overlap.

Each response was written for exactly one of the two personas; they need not split (both could fit the same persona better, if the text warrants it).

=== PERSONA 1 BRIEF ===
%s

=== PERSONA 2 BRIEF ===
%s

=== RESPONSE X ===
%s

=== RESPONSE Y ===
%s

Return ONLY a JSON object on one line, no prose, no markdown fences:
{"output_X_fits": 1 or 2, "output_Y_fits": 1 or 2, "confidence_0_1": <float 0-1>, "basis": "<=18 words on the behavioral axis you used"}"""

_CAP = ("usage limit", "hit your limit", "limit · resets", "rate limit", "too many requests",
        "quota", "5-hour", "429", "resource_exhausted", "exhausted")

def claude_call(prompt, model, timeout=240):
    env = os.environ.copy(); env.pop("CLAUDECODE", None)
    r = subprocess.run(["claude", "-p", "--safe-mode", "--model", model], input=prompt,
                       capture_output=True, text=True, env=env, timeout=timeout,
                       cwd=tempfile.gettempdir())
    if r.returncode != 0:
        so, se = (r.stdout or "").lower(), (r.stderr or "").lower()
        capped = any(m in so or m in se for m in _CAP) or (not so.strip() and not se.strip())
        raise RuntimeError(("CAP:" if capped else "ERR:") + f"claude rc={r.returncode}: {se[-200:] or so[-200:]}")
    return r.stdout.strip()

def agy_call(prompt, timeout=300):
    r = subprocess.run(["agy", "--model", "gemini-3.1-pro", "-p", "-"], input=prompt,
                       capture_output=True, text=True, timeout=timeout, cwd=AGY_CWD)
    out = (r.stdout or "").strip()
    if r.returncode != 0:
        se = (r.stderr or "").lower(); so = out.lower()
        capped = any(m in se or m in so for m in _CAP)
        raise RuntimeError(("QUOTA:" if capped else "ERR:") + f"agy rc={r.returncode}: {se[-200:] or out[-200:]}")
    return out

def load_jsonl(p):
    d = {}
    if os.path.exists(p):
        for l in open(p):
            l = l.strip()
            if l:
                r = json.loads(l); d[r.get("task_id"), r.get("slot")] = r if "slot" in r else None
    return d

# ---------------- STAGE 1: paraphrase ----------------
def stage_paraphrase():
    done = set()
    if os.path.exists(PARA_CACHE):
        for l in open(PARA_CACHE):
            l = l.strip()
            if l:
                r = json.loads(l); done.add((r["task_id"], r["slot"]))
    jobs = [(t, slot) for t in tasks for slot in ("X", "Y") if (t["task_id"], slot) not in done]
    print(f"[paraphrase] {len(jobs)} outputs to rewrite ({len(done)} cached), {PARA_WORKERS} workers")
    if not jobs:
        return
    fh = open(PARA_CACHE, "a")
    def one(t, slot):
        txt = (t["output_X"] if slot == "X" else t["output_Y"])[:RESP_CAP]
        for attempt in range(4):
            try:
                para = claude_call(PARA_PROMPT % txt, "claude-sonnet-4-6")
                return {"task_id": t["task_id"], "slot": slot, "text": para, "orig_len": len(txt), "para_len": len(para)}
            except Exception as e:
                if str(e).startswith("CAP:") and attempt < 3:
                    back = [60, 300, 900][attempt]; print(f"    CAP {t['task_id']}/{slot} backoff {back}s"); time.sleep(back); continue
                return {"task_id": t["task_id"], "slot": slot, "text": None, "err": str(e)[:160]}
    t0 = time.time(); n = 0; fail = 0
    with ThreadPoolExecutor(max_workers=PARA_WORKERS) as ex:
        futs = [ex.submit(one, t, s) for t, s in jobs]
        for f in as_completed(futs):
            r = f.result(); n += 1
            if r["text"] is None: fail += 1
            fh.write(json.dumps(r) + "\n"); fh.flush()
            if n % 10 == 0 or r["text"] is None:
                print(f"  [{n}/{len(jobs)}] {r['task_id']}/{r['slot']} {'OK' if r['text'] else 'FAIL '+r.get('err','')} ({time.time()-t0:.0f}s)")
    fh.close(); print(f"[paraphrase] done; {fail} failures")

def load_paraphrases():
    p = {}
    for l in open(PARA_CACHE):
        l = l.strip()
        if l:
            r = json.loads(l)
            if r["text"]: p[(r["task_id"], r["slot"])] = r["text"]
    return p

# ---------------- STAGE 2: judge (Gemini blind recovery on paraphrased pairs) ----------------
def stage_judge():
    para = load_paraphrases()
    done = set()
    if os.path.exists(VERDICTS):
        for l in open(VERDICTS):
            l = l.strip()
            if l: done.add(json.loads(l)["task_id"])
    todo = [t for t in tasks if t["task_id"] not in done
            and (t["task_id"], "X") in para and (t["task_id"], "Y") in para]
    print(f"[judge] {len(todo)} tasks to recover ({len(done)} done); {JUDGE_WORKERS} workers; cwd={AGY_CWD}")
    if not todo:
        return
    fh = open(VERDICTS, "a"); quota_hit = [False]
    def one(t):
        prompt = CODER_TMPL % (t["persona_1_brief"], t["persona_2_brief"],
                               para[(t["task_id"], "X")], para[(t["task_id"], "Y")])
        try:
            out = agy_call(prompt)
            m = re.search(r"\{.*\}", out, re.DOTALL)
            o = json.loads(m.group(0)) if m else {}
            return {"task_id": t["task_id"], "output_X_fits": o.get("output_X_fits"),
                    "output_Y_fits": o.get("output_Y_fits"), "confidence_0_1": o.get("confidence_0_1"),
                    "basis": o.get("basis", "")}
        except Exception as e:
            if str(e).startswith("QUOTA:"): quota_hit[0] = True
            return {"task_id": t["task_id"], "output_X_fits": None, "output_Y_fits": None, "err": str(e)[:160]}
    t0 = time.time(); n = 0
    with ThreadPoolExecutor(max_workers=JUDGE_WORKERS) as ex:
        futs = [ex.submit(one, t) for t in todo]
        for f in as_completed(futs):
            r = f.result(); n += 1
            fh.write(json.dumps(r) + "\n"); fh.flush()
            ok = r["output_X_fits"] in (1, 2)
            print(f"  [{n}/{len(todo)}] {r['task_id']} -> X={r['output_X_fits']} Y={r['output_Y_fits']} {'' if ok else r.get('err','')} ({time.time()-t0:.0f}s)")
    fh.close()
    if quota_hit[0]:
        print("[judge] NOTE: Gemini quota hit during run — re-run `judge` stage after reset to resume.")

# ---------------- STAGE 3: score ----------------
def wilson(k, n, z=1.96):
    import math
    if n == 0: return (None, None, None)
    p = k/n; d = 1+z*z/n; c = (p+z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return round(p, 3), round(c-h, 3), round(c+h, 3)

def stage_score():
    verds = {}
    for l in open(VERDICTS):
        l = l.strip()
        if l:
            r = json.loads(l)
            if r.get("output_X_fits") in (1, 2) and r.get("output_Y_fits") in (1, 2):
                verds[r["task_id"]] = r
    rows = []
    for tid, v in verds.items():
        if tid not in keys: continue
        k = keys[tid]; sp = {1: k["P1_persona"], 2: k["P2_persona"]}
        rows.append(int(sp[v["output_X_fits"]] == ("P" if k["X_cond"] == "C4" else "Q")))
        rows.append(int(sp[v["output_Y_fits"]] == ("P" if k["Y_cond"] == "C4" else "Q")))
    p, lo, hi = wilson(sum(rows), len(rows))
    # paraphrase length sanity
    para = load_paraphrases()
    res = {"n_tasks_judged": len(verds), "n_judgments": len(rows),
           "neutral_paraphrase_recovery": [p, lo, hi],
           "gate3_baseline": 0.93, "gate3b_deecho": 0.963,
           "n_paraphrased_outputs": len(para)}
    reading = ("genuine behavioral adaptation (>=~.75)" if p and p >= 0.75 else
               "mostly surface/echo (->.50)" if p and p <= 0.58 else "mixed (.58-.75)")
    res["reading"] = reading
    json.dump(res, open(OUT, "w"), indent=2)
    print("\n=== #1 NEUTRAL-PARAPHRASE BLIND RECOVERY ===")
    print(f"  recovery = {p} [{lo}, {hi}]  (n_judgments={len(rows)}, tasks={len(verds)})")
    print(f"  vs Gate 3 (raw) 0.93 | Gate 3b (4-gram de-echo) 0.963")
    print(f"  reading: {reading}")
    print(f"saved -> {OUT}")

if STAGE in ("paraphrase", "all"): stage_paraphrase()
if STAGE in ("judge", "all"): stage_judge()
if STAGE in ("score", "all"): stage_score()
