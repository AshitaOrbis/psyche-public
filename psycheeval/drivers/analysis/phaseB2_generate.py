"""Phase B2 Stage B — generate assistant outputs over the content x form x salience
factorial. Deterministic balanced-incomplete allocation -> ~1,650 correct-vs-opposite
pairs (~110 / form x salience cell) + a controls block (H6). Author split ~50/50
GPT-5.5 (codex, cap-free) / Opus-4.7 (claude -p, cap-bound, burns Max cap).

Usage:  python3 drivers/analysis/phaseB2_generate.py <gpt-5.5|opus>
Pairs are reconstructed later by matching content correct/opposite within
(persona, scenario, form, salience, author).
"""
import json, os, re, subprocess, sys, time, tempfile, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B2 = f"{REPO}/data/phaseB2"
AUTHOR = sys.argv[1] if len(sys.argv) > 1 else "gpt-5.5"
WORKERS = 6 if AUTHOR.startswith("gpt") else 3
TAG = AUTHOR.replace(".", "p").replace("-", "")
CKPT = f"{REPO}/reports/analysis/phaseB2_gen_{TAG}.checkpoint.jsonl"
OUT = f"{REPO}/reports/analysis/phaseB2_gen_{TAG}.json"

briefs = json.load(open(f"{B2}/persona_briefs.json"))
scenarios = json.load(open(f"{B2}/scenarios.json"))
variants = json.load(open(f"{B2}/conditioning_variants.json"))
seeds = json.load(open(f"{B2}/persona_seeds.json"))
scen_seed = {s["id"]: s for s in json.load(open(f"{B2}/scenario_seeds.json"))["scenarios"]}

# reciprocal map + persona list
RECIP = {}
PERSONAS = []
for pair in seeds["pairs"]:
    a, b = pair["personas"][0]["id"], pair["personas"][1]["id"]
    RECIP[a] = b; RECIP[b] = a; PERSONAS += [a, b]

FORMS = ["prose", "trait-list", "contract", "hidden-summary", "minimal-cue"]
SAL = ["explicit-labels", "behavioral-examples", "de-labeled"]
CELLS15 = [(f, s) for f in FORMS for s in SAL]
SCEN_IDS = sorted(scenarios.keys())
UNITS = [(p, sc) for p in PERSONAS for sc in SCEN_IDS]   # 16 x 30 = 480

# fixed instruction-matched controls (H6)
LONG_NEUTRAL = (" ".join(["The assistant should aim to be genuinely useful and to respond "
    "in good faith to what is actually being asked, taking the question seriously on its own terms."] * 8))
CTRL_TEXT = {
 "generic": variants.get("_generic||prose||explicit-labels", {}).get("text", "Help them as you would any reasonable adult."),
 "C0_STYLE_ONLY": "Be warm, clearly structured, and thorough in your reply.",
 "C_PLACEBO_CONTRACT": ("When they ask a question, answer it. When something is unclear, ask. "
    "When there are options, mention them. When there is a risk, note it. When they seem stuck, encourage them."),
 "C0_LONG_NEUTRAL": LONG_NEUTRAL,
}

def rng_for(s):
    return int(hashlib.sha1(s.encode()).hexdigest(), 16)

def conditioning_for(content, persona, form, sal):
    if content == "none": return ""
    if content == "correct": key = f"{persona}||{form}||{sal}"
    elif content == "opposite": key = f"{RECIP[persona]}||{form}||{sal}"
    elif content == "random":
        others = [p for p in PERSONAS if p != persona and p != RECIP[persona]]
        pick = others[rng_for(f"{persona}{form}{sal}rand") % len(others)]
        key = f"{pick}||{form}||{sal}"
    elif content in CTRL_TEXT: return CTRL_TEXT[content]
    else: return ""
    v = variants.get(key)
    return v["text"] if v else None

# ---- build deterministic job list ----
def build_jobs():
    jobs = []
    # primary correct-vs-opposite allocation: ~1650 pairs, stride rotation over 15 cells
    n_units = len(UNITS)
    per_unit = [3] * n_units
    for k in range(1650 - 3 * n_units):   # bump first 210 units to 4 -> total 1650 cell-assignments
        per_unit[k % n_units] += 1
    pair_idx = 0
    for ui, (persona, sc) in enumerate(UNITS):
        start = (ui * 7) % 15
        for j in range(per_unit[ui]):
            form, sal = CELLS15[(start + j) % 15]
            author = "gpt-5.5" if pair_idx % 2 == 0 else "opus"
            for content in ("correct", "opposite"):
                jobs.append({"jid": f"P{pair_idx:04d}_{content[:3]}", "kind": "primary",
                             "persona": persona, "scenario": sc, "form": form, "sal": sal,
                             "content": content, "author": author})
            pair_idx += 1
    # controls block (H6): ~150 units, correct@prose-explicit vs 5 controls
    ctrl_units = UNITS[::3][:160]   # spread sample
    for ui, (persona, sc) in enumerate(ctrl_units):
        author = "gpt-5.5" if ui % 2 == 0 else "opus"
        for content in ("correct", "generic", "C0_STYLE_ONLY", "C_PLACEBO_CONTRACT", "C0_LONG_NEUTRAL", "none"):
            jobs.append({"jid": f"C{ui:03d}_{content}", "kind": "control",
                         "persona": persona, "scenario": sc, "form": "prose", "sal": "explicit-labels",
                         "content": content, "author": author})
    return jobs

JOBS = [j for j in build_jobs() if j["author"] == AUTHOR]

WRAP = ("You are a helpful AI assistant replying to one person.{cond}\n\n"
        "The person writes:\n\n{msg}\n\nReply directly to them — no preamble, no meta-commentary.")
def render(job):
    cond = conditioning_for(job["content"], job["persona"], job["form"], job["sal"])
    if cond is None: return None
    block = f"\n\nWhat you know about this person:\n{cond}" if cond else ""
    return WRAP.format(cond=block, msg=scenarios[job["scenario"]])

_CAP = ("usage limit", "hit your limit", "limit · resets", "rate limit", "too many requests", "quota", "5-hour", "429")
def call_author(prompt, timeout=300):
    if AUTHOR.startswith("gpt"):
        cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "--color", "never",
               "-m", "gpt-5.5", "-c", 'model_reasoning_effort="medium"']
        r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0: raise RuntimeError(f"codex rc={r.returncode}: {r.stderr[-160:]}")
        return r.stdout.strip()
    env = os.environ.copy(); env.pop("CLAUDECODE", None)
    r = subprocess.run(["claude", "-p", "--safe-mode", "--model", "claude-opus-4-7"], input=prompt,
                       capture_output=True, text=True, env=env, timeout=timeout, cwd=tempfile.gettempdir())
    if r.returncode != 0:
        so, se = (r.stdout or "").lower(), (r.stderr or "").lower()
        cap = any(m in so or m in se for m in _CAP) or (not so.strip() and not se.strip())
        raise RuntimeError(("CAP:" if cap else "ERR:") + f"rc={r.returncode}: {se[-160:] or so[-160:]}")
    return r.stdout.strip()

done = {}
if os.path.exists(CKPT):
    for l in open(CKPT):
        l = l.strip()
        if l: r = json.loads(l); done[r["jid"]] = r
_OK = lambda r: bool(r.get("output"))
valid = {jid for jid, r in done.items() if _OK(r)}
todo = [j for j in JOBS if j["jid"] not in valid]
print(f"[gen {AUTHOR}] {len(JOBS)} jobs, {len(todo)} to run ({len(valid)} done), {WORKERS}w")

def one(job):
    p = render(job)
    if p is None:
        return {**job, "output": None, "error": "missing conditioning variant"}
    for attempt in range(4):
        try:
            out = call_author(p)
            if not out or len(out) < 20: raise RuntimeError("ERR:empty")
            return {**job, "output": out, "out_words": len(out.split())}
        except Exception as e:
            if str(e).startswith("CAP:") and attempt < 3: time.sleep([60, 300, 900][attempt]); continue
            if attempt < 3: time.sleep(4); continue
            return {**job, "output": None, "error": str(e)[:140]}

t0 = time.time(); ck = open(CKPT, "a")
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(one, j): j["jid"] for j in todo}
    n = 0
    for f in as_completed(futs):
        r = f.result(); done[r["jid"]] = r
        ck.write(json.dumps(r) + "\n"); ck.flush(); n += 1
        if n % 25 == 0 or n == len(todo):
            print(f"  [{n}/{len(todo)}] {r['jid']} {'OK' if r.get('output') else 'FAIL'} ({time.time()-t0:.0f}s)")
ck.close()

rows = list(done.values())
nv = sum(1 for r in rows if _OK(r))
json.dump({"author": AUTHOR, "n_jobs": len(JOBS), "n_valid": nv, "results": rows}, open(OUT, "w"), indent=1)
print(f"\n[gen {AUTHOR}] valid {nv}/{len(JOBS)}  saved -> {OUT}")
print(f"STATUS valid={nv} total={len(JOBS)}")
