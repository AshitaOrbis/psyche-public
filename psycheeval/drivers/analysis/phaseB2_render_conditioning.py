"""Phase B2 Stage A — render each persona brief into Form x Salience conditioning
variants (the author's profile input). 16 personas x 5 forms x 3 saliences = 240,
plus a generic-control persona x 5 forms. Opus-4.7 (cap-burn). Resumable.

The variant text is later dropped into the author's system prompt; content level
(correct/opposite/random) just selects WHICH persona's variant to use, so the
primary correct-vs-opposite contrast is length/form/salience matched by construction.

Output: data/phaseB2/conditioning_variants.json  (key "pid||form||salience")
"""
import json, os, re, subprocess, time, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B2 = f"{REPO}/data/phaseB2"
CKPT = f"{B2}/_conditioning.checkpoint.jsonl"
WORKERS = 3

briefs = json.load(open(f"{B2}/persona_briefs.json"))
GENERIC = ("This is a generic person with no distinguishing engagement preferences. "
           "Help them the way you would help any reasonable adult: clear, accurate, "
           "appropriately thorough, respectful of their autonomy.")
briefs["_generic"] = GENERIC

FORMS = {
 "prose": "as 2-3 flowing paragraphs of behavioral guidance.",
 "trait-list": "as a bulleted list of 6-10 concrete behavioral directives (what to do, what to avoid).",
 "contract": "as 6-10 if-then rules, each of the form 'When <situation>, <do this>.'",
 "hidden-summary": "as a tight 60-90 word summary the assistant should INTERNALIZE but never quote or reference. Begin with exactly: [Internalize the following about the person; do not mention or quote it.]",
 "minimal-cue": "as a single one-sentence cue capturing the core of how to engage this person.",
}
SAL = {
 "explicit-labels": "Name the preference explicitly (e.g. 'This person prefers X and is alienated by Y').",
 "behavioral-examples": "Convey it ONLY through 2-3 brief example exchange snippets (a user line, then the kind of reply that fits). Do NOT name the underlying preference in words.",
 "de-labeled": "Give ONLY the calibrated do/avoid behavior. Strip out the trait/preference NAME and any 'because they are X' — no labels, no examples, just what to do and not do.",
}

PROMPT = """You are converting a behavioral profile into a specific FORMAT and SALIENCE for use as an AI assistant's conditioning.

SOURCE PROFILE:
{brief}

Produce the profile {form_spec}
Salience rule: {sal_spec}

Keep it faithful to the source behavior. Output JSON only, one line, no fences:
{{"variant": "<the rendered conditioning>"}}"""

def call_opus(prompt, timeout=240):
    env = os.environ.copy(); env.pop("CLAUDECODE", None)
    r = subprocess.run(["claude", "-p", "--model", "claude-opus-4-7"], input=prompt,
                       capture_output=True, text=True, env=env, timeout=timeout, cwd=tempfile.gettempdir())
    if r.returncode != 0:
        so, se = (r.stdout or "").lower(), (r.stderr or "").lower()
        cap = any(m in so or m in se for m in ("usage limit","hit your limit","limit · resets","rate limit","quota","5-hour","429")) or (not so.strip() and not se.strip())
        raise RuntimeError(("CAP:" if cap else "ERR:") + f"rc={r.returncode}: {se[-160:] or so[-160:]}")
    return r.stdout.strip()

def parse(t):
    m = re.search(r"\{.*\}", t, re.DOTALL)
    if not m: return None
    try:
        v = json.loads(m.group(0)).get("variant")
        return v if isinstance(v, str) and len(v) > 10 else None
    except Exception: return None

jobs = []
for pid in briefs:
    forms = FORMS
    sals = SAL
    if pid == "_generic":
        # generic control: 5 forms at explicit-labels only (it has nothing to de-label)
        for f in FORMS: jobs.append((pid, f, "explicit-labels"))
    else:
        for f in FORMS:
            for s in SAL: jobs.append((pid, f, s))

done = {}
if os.path.exists(CKPT):
    for l in open(CKPT):
        l = l.strip()
        if l: r = json.loads(l); done[(r["pid"], r["form"], r["sal"])] = r
todo = [j for j in jobs if j not in done or not done[j].get("text")]
print(f"render: {len(jobs)} variants, {len(todo)} to run ({len(jobs)-len(todo)} done), {WORKERS}w")

def one(pid, form, sal):
    p = PROMPT.format(brief=briefs[pid], form_spec=FORMS[form], sal_spec=SAL[sal])
    for attempt in range(5):
        try:
            v = parse(call_opus(p))
            if not v: raise RuntimeError("ERR:parse")
            return {"pid": pid, "form": form, "sal": sal, "text": v, "words": len(v.split())}
        except Exception as e:
            if str(e).startswith("CAP:") and attempt < 4: time.sleep([30,120,300,600][attempt]); continue
            if attempt < 4: time.sleep(5); continue
            return {"pid": pid, "form": form, "sal": sal, "text": None, "error": str(e)[:140]}

ck = open(CKPT, "a")
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(one, *j): j for j in todo}
    n = 0
    for fut in as_completed(futs):
        r = fut.result(); done[(r["pid"], r["form"], r["sal"])] = r
        ck.write(json.dumps(r) + "\n"); ck.flush(); n += 1
        if n % 20 == 0 or n == len(todo): print(f"  [{n}/{len(todo)}] {r['pid']}|{r['form']}|{r['sal']} {'OK' if r.get('text') else 'FAIL'}")
ck.close()

variants = {f"{r['pid']}||{r['form']}||{r['sal']}": {"text": r["text"], "words": r["words"]}
            for r in done.values() if r.get("text")}
json.dump(variants, open(f"{B2}/conditioning_variants.json", "w"), indent=1, ensure_ascii=False)
fails = [k for k, v in done.items() if not v.get("text")]
print(f"\nrendered {len(variants)} variants  | failures: {len(fails)} {fails[:5]}")
print(f"saved -> {B2}/conditioning_variants.json")
