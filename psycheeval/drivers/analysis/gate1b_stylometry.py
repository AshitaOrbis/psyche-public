"""Gate 1b (GPT Pro #1, stronger form): re-run the surface-control deconfounding
with a RICHER stylometric index extracted directly from raw output text, not just
the 3 D3 features.

Stylometric features per output (deterministic, from assistant_response):
  log_word_count, bullet_lines_per_100w, heading_lines_per_100w,
  imperative_starts_frac, second_person_per_100w, markdown_marker_per_100w,
  mean_sentence_len, bold_emphasis_per_100w, numbered_list_per_100w.

These capture exactly the "directive/scaffolded/contract-like" surface that the
shared-formatting-preference null predicts judges reward. If a headline contrast
survives controlling for ALL of these (logistic intercept at dS=0, slot-balanced,
cluster bootstrap), the effect is not explained by directive formatting. If it
vanishes, it was surface.

Caveat (GPT Pro): surface features are post-treatment mediators; controlling them
is a conservative adversarial diagnosis (does the effect survive even net of the
formatting it induces?), not a clean causal estimate.
"""
import json, math, re, numpy as np
RUN = "runs/2026-05-19_v03"

BULLET_RE = re.compile(r'^\s*[-*•]\s+', re.M)
NUM_RE = re.compile(r'^\s*\d+[.)]\s+', re.M)
HEAD_RE = re.compile(r'^\s*(#{1,6}\s+|\*\*[^*]+\*\*\s*:?\s*$)', re.M)
BOLD_RE = re.compile(r'\*\*[^*]+\*\*|__[^_]+__')
MD_MARK_RE = re.compile(r'[*#`|>_]')
SECOND_RE = re.compile(r'\b(you|your|yours|yourself)\b', re.I)
SENT_SPLIT = re.compile(r'[.!?]+(?:\s|$)')
# crude imperative detector: line/sentence starts with a base-form verb
IMPERATIVE_VERBS = set("""acknowledge ask avoid be begin build choose consider
create describe do dont don't ensure explain find focus give go handle hold keep
lead let list look make name note offer pick place put reach remember reply say
send set show start state stay stop take tell think try use validate verify write
engage name match anchor treat respect prioritize lean default open""".split())

def feats_from_text(t):
    if not t: return None
    words = re.findall(r"\b\w+\b", t)
    w = max(len(words), 1)
    bullets = len(BULLET_RE.findall(t))
    nums = len(NUM_RE.findall(t))
    heads = len(HEAD_RE.findall(t))
    bolds = len(BOLD_RE.findall(t))
    md = len(MD_MARK_RE.findall(t))
    second = len(SECOND_RE.findall(t))
    sents = [s for s in SENT_SPLIT.split(t) if s.strip()]
    nsent = max(len(sents), 1)
    mean_sent = w / nsent
    # imperative fraction: of non-empty lines, how many start with an imperative verb
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    imp = 0
    for ln in lines:
        m = re.match(r'^[-*•\d.)\s]*([A-Za-z\']+)', ln)
        if m and m.group(1).lower() in IMPERATIVE_VERBS:
            imp += 1
    imp_frac = imp / max(len(lines), 1)
    return np.array([
        math.log(w),
        bullets / w * 100,
        heads / w * 100,
        imp_frac,
        second / w * 100,
        md / w * 100,
        mean_sent,
        bolds / w * 100,
        nums / w * 100,
    ])

def fam(m):
    if not m: return "other"
    return "openai" if m.startswith("gpt") else ("anthropic" if "opus" in m else "other")

def logistic_fit(X, y, iters=80, ridge=1e-2):
    n, p = X.shape; b = np.zeros(p)
    for _ in range(iters):
        mu = 1/(1+np.exp(-(X@b))); W = mu*(1-mu)+1e-9
        g = X.T@(y-mu) - ridge*b; H = -(X.T*W)@X - ridge*np.eye(p)
        try: step = np.linalg.solve(H, g)
        except np.linalg.LinAlgError: break
        b -= step
        if np.max(np.abs(step)) < 1e-9: break
    return b

def main():
    outs = {}
    for l in open(f"{RUN}/assistant_outputs.jsonl"):
        l = l.strip()
        if not l: continue
        try: r = json.loads(l)
        except: continue
        outs[r["run_id"]] = r
    # precompute stylometry
    sty = {}
    for rid, r in outs.items():
        f = feats_from_text(r.get("assistant_response", ""))
        if f is not None: sty[rid] = f

    pairwise = []
    for fn in ("pairwise_scores.jsonl", "pairwise_swap_scores.jsonl"):
        for l in open(f"{RUN}/{fn}"):
            l = l.strip()
            if l and '\x00' not in l:
                try: pairwise.append(json.loads(l))
                except: pass

    contrasts = [(("C4", "C4_WRONG_PROFILE"), "C4"), (("C3", "C4_WRONG_PROFILE"), "C3"),
                 (("C4", "C_GENERIC_CONTRACT"), "C4"), (("C3", "C_GENERIC_CONTRACT"), "C3"),
                 (("C_GENERIC_CONTRACT", "C0"), "C_GENERIC_CONTRACT"),
                 (("C4_WRONG_PROFILE", "C0"), "C4_WRONG_PROFILE")]

    def build(pair, target):
        pk = tuple(sorted(pair)); rows = []
        for r in pairwise:
            ca = outs.get(r["run_id_a"]); cb = outs.get(r["run_id_b"])
            if not ca or not cb: continue
            if tuple(sorted([str(ca["condition"]), str(cb["condition"])])) != pk: continue
            if ca.get("output_model") != cb.get("output_model"): continue
            jf = fam(r["judge_model"]); af = fam(ca.get("output_model"))
            if jf == af or jf == "other": continue
            if r["winner"] not in ("A", "B"): continue
            if str(ca["condition"]) == target: t_rid, c_rid, t_slot = r["run_id_a"], r["run_id_b"], "A"
            elif str(cb["condition"]) == target: t_rid, c_rid, t_slot = r["run_id_b"], r["run_id_a"], "B"
            else: continue
            ft, fc = sty.get(t_rid), sty.get(c_rid)
            if ft is None or fc is None: continue
            won = 1.0 if ((r["winner"] == "A" and t_slot == "A") or (r["winner"] == "B" and t_slot == "B")) else 0.0
            cl = (ca.get("user_id"), r["scenario_id"], ca.get("output_model"))
            rows.append((won, ft-fc, 1.0 if t_slot == "B" else 0.0, cl))
        return rows

    def estimates(rows):
        y = np.array([r[0] for r in rows]); dS = np.vstack([r[1] for r in rows]); slot = np.array([r[2] for r in rows])
        mu = dS.mean(0); sd = dS.std(0)+1e-9; dz = (dS-mu)/sd
        raw = y.mean()
        X = np.column_stack([np.ones(len(y)), slot, dz])
        b = logistic_fit(X, y)
        adj = 1/(1+math.exp(-(b[0]+0.5*b[1])))
        return raw, adj

    def cluster_boot(rows, B=2000, seed=11):
        clusters = {}
        for r in rows: clusters.setdefault(r[3], []).append(r)
        keys = list(clusters); rng = np.random.default_rng(seed)
        raws, adjs = [], []
        for _ in range(B):
            samp = []
            for k in rng.choice(len(keys), len(keys)): samp.extend(clusters[keys[k]])
            try:
                raw, adj = estimates(samp); raws.append(raw); adjs.append(adj)
            except Exception: pass
        def ci(a):
            a = np.sort([x for x in a if x == x])
            return [round(float(np.percentile(a, 2.5)), 3), round(float(np.percentile(a, 97.5)), 3)] if len(a) > 20 else None
        return ci(raws), ci(adjs)

    res = []
    for pair, target in contrasts:
        rows = build(pair, target)
        if len(rows) < 30:
            res.append({"contrast": f"{target} vs {[x for x in pair if x != target][0]}", "n": len(rows), "note": "insufficient"}); continue
        raw, adj = estimates(rows)
        raw_ci, adj_ci = cluster_boot(rows)
        res.append({"contrast": f"{target} vs {[x for x in pair if x != target][0]}", "n": len(rows),
                    "raw_win": round(raw, 3), "raw_ci": raw_ci,
                    "stylo_adjusted_win": round(adj, 3), "stylo_adjusted_ci": adj_ci,
                    "survives_rich_surface_control": (adj_ci is not None and adj_ci[0] > 0.5)})
    print(json.dumps(res, indent=2))
    json.dump(res, open("reports/analysis/gate1b_results.json", "w"), indent=2)

if __name__ == "__main__":
    main()
