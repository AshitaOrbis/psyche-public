"""Phase B2 — expand persona seeds -> full behavioral briefs, scenario seeds ->
natural user messages. Opus-4.7 (cap-bound by design — burns Max cap). Resumable.

Outputs: data/phaseB2/persona_briefs.json, data/phaseB2/scenarios.json
"""
import json, os, re, subprocess, sys, time, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B2 = f"{REPO}/data/phaseB2"
CKPT = f"{B2}/_expand.checkpoint.jsonl"
WORKERS = 3

seeds = json.load(open(f"{B2}/persona_seeds.json"))
scen = json.load(open(f"{B2}/scenario_seeds.json"))

PBRIEF_PROMPT = """You are writing a BEHAVIORAL PROFILE BRIEF used to evaluate how well an AI assistant adapts to different people.

Write a 300-340 word brief describing how THIS specific person needs to be engaged by an assistant. Cover: the response SHAPE that serves them, what reliably ALIENATES them, their observable TELLS, and how they react when engaged well vs badly. Write it as a concrete, usable behavioral guide in the third person ("This person ..."). Be specific and grounded in behavior, NOT trait-jargon. Do NOT use section headers, bullet lists, trait-score language, or any meta-commentary about the task. Just the brief, as flowing prose.

SEED (the behavioral axis and pole this person sits on):
{seed}

Output JSON only, one line, no fences:
{{"brief": "<the 300-340 word brief>"}}"""

SCEN_PROMPT = """Rewrite the situation below as a natural, first-person message a real person would actually type to an AI assistant. 40-110 words, their voice, present tense, specific but not over-written. End where they ask for help or pose the question. No "Hi"/"Hello" boilerplate, no sign-off, no meta.

SITUATION: {seed}

Output JSON only, one line, no fences:
{{"message": "<the message>"}}"""

def call_opus(prompt, timeout=300):
    env = os.environ.copy(); env.pop("CLAUDECODE", None)
    r = subprocess.run(["claude", "-p", "--model", "claude-opus-4-7"],
                       input=prompt, capture_output=True, text=True, env=env,
                       timeout=timeout, cwd=tempfile.gettempdir())
    if r.returncode != 0:
        so, se = (r.stdout or "").lower(), (r.stderr or "").lower()
        cap = any(m in so or m in se for m in ("usage limit","hit your limit","limit · resets","rate limit","quota","5-hour","429")) or (not so.strip() and not se.strip())
        raise RuntimeError(("CAP:" if cap else "ERR:") + f"rc={r.returncode}: {se[-160:] or so[-160:]}")
    return r.stdout.strip()

def parse(text, field):
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m: return None
    try:
        o = json.loads(m.group(0)); v = o.get(field)
        return v if isinstance(v, str) and len(v) > 20 else None
    except Exception:
        return None

# jobs
jobs = []
for pair in seeds["pairs"]:
    for p in pair["personas"]:
        jobs.append(("persona", p["id"], PBRIEF_PROMPT.format(seed=json.dumps({**p, "axis": pair["axis"], "axis_description": pair["axis_description"]}, ensure_ascii=False)), "brief"))
for s in scen["scenarios"]:
    jobs.append(("scenario", s["id"], SCEN_PROMPT.format(seed=s["seed"]), "message"))

done = {}
if os.path.exists(CKPT):
    for l in open(CKPT):
        l = l.strip()
        if l: r = json.loads(l); done[(r["kind"], r["id"])] = r
todo = [j for j in jobs if (j[0], j[1]) not in done or not done[(j[0], j[1])].get("text")]
print(f"expand: {len(jobs)} items, {len(todo)} to run ({len(jobs)-len(todo)} done), {WORKERS}w")

def one(kind, jid, prompt, field):
    for attempt in range(5):
        try:
            txt = parse(call_opus(prompt), field)
            if not txt: raise RuntimeError("ERR:parse")
            return {"kind": kind, "id": jid, "text": txt, "words": len(txt.split())}
        except Exception as e:
            if str(e).startswith("CAP:") and attempt < 4:
                time.sleep([30, 120, 300, 600][attempt]); continue
            if attempt < 4: time.sleep(5); continue
            return {"kind": kind, "id": jid, "text": None, "error": str(e)[:140]}

ck = open(CKPT, "a")
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(one, k, i, p, f): i for (k, i, p, f) in todo}
    for fut in as_completed(futs):
        r = fut.result(); done[(r["kind"], r["id"])] = r
        ck.write(json.dumps(r) + "\n"); ck.flush()
        print(f"  {r['kind']}/{r['id']} -> {'OK '+str(r.get('words'))+'w' if r.get('text') else 'FAIL '+str(r.get('error'))}")
ck.close()

briefs = {i: done[("persona", i)]["text"] for (k, i) in done if k == "persona" and done[(k, i)].get("text")}
scens = {i: done[("scenario", i)]["text"] for (k, i) in done if k == "scenario" and done[(k, i)].get("text")}
json.dump(briefs, open(f"{B2}/persona_briefs.json", "w"), indent=1, ensure_ascii=False)
json.dump(scens, open(f"{B2}/scenarios.json", "w"), indent=1, ensure_ascii=False)
print(f"\npersona briefs: {len(briefs)}/16  | scenarios: {len(scens)}/30")
print(f"saved -> {B2}/persona_briefs.json , {B2}/scenarios.json")
PY = None
