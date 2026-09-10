"""Gate 1 (GPT Pro #1/#2 + publication-review trigger #8): do the headline
condition effects survive control for D3 surface features?

For each target contrast, on cross-provider same-author pairwise records (both
AB and BA orientations), y = target wins (decisive). Surface features pruned to
the three with real variance: log word_count, source_packet_lexical_overlap,
hedging_per_100w (profile_reference_count/tailoring/refusal are ~constant-zero
-> dropped; their near-zero variance is itself the finding that judges do not
reward profile-naming). Inference via cluster bootstrap (cluster = persona x
scenario x author), 2000 resamples.

Reports per contrast: position-controlled raw win rate; style-balanced-subset
win rate (|dz length|,|dz overlap| < 0.5); surface-adjusted win rate (logistic
intercept at dS=0, slot-balanced). CIs are bootstrap 95%.
"""
import json, math, numpy as np
RUN="runs/2026-05-19_v03"
FEATS=["word_count","source_packet_lexical_overlap","hedging_frequency_per_100w"]

def load_outputs():
    o={}
    for line in open(f"{RUN}/assistant_outputs.jsonl"):
        line=line.strip()
        if not line: continue
        try: r=json.loads(line)
        except: continue
        o[r["run_id"]]={"cond":r.get("condition"),"author":r.get("output_model"),
                        "user":r.get("user_id"),"scn":r.get("scenario_id")}
    return o
def load_d3():
    return json.load(open("reports/metrics_2026-05-19_v03.json"))["reward_hacking_diagnostics"]["per_output"]
def fam(m):
    if not m: return "other"
    return "openai" if m.startswith("gpt") else ("anthropic" if "opus" in m else "other")
def feat(d3,rid):
    f=d3.get(rid)
    if not f: return None
    return np.array([math.log(max(f.get("word_count",1) or 1,1)),
                     float(f.get("source_packet_lexical_overlap",0) or 0),
                     float(f.get("hedging_frequency_per_100w",0) or 0)])

def logistic_fit(X,y,iters=60,ridge=1e-3):
    n,p=X.shape; b=np.zeros(p)
    for _ in range(iters):
        mu=1/(1+np.exp(-(X@b))); W=mu*(1-mu)+1e-9
        g=X.T@(y-mu)-ridge*b; H=-(X.T*W)@X-ridge*np.eye(p)
        try: step=np.linalg.solve(H,g)
        except np.linalg.LinAlgError: break
        b-=step
        if np.max(np.abs(step))<1e-9: break
    return b

def build_rows(pair,target,outputs,d3,pairwise):
    rows=[]
    pk=tuple(sorted(pair))
    for r in pairwise:
        ca=outputs.get(r["run_id_a"]); cb=outputs.get(r["run_id_b"])
        if not ca or not cb: continue
        if tuple(sorted([str(ca["cond"]),str(cb["cond"])]))!=pk: continue
        if ca["author"]!=cb["author"]: continue
        jf=fam(r["judge_model"]); af=fam(ca["author"])
        if jf==af or jf=="other": continue
        if r["winner"] not in ("A","B"): continue
        if str(ca["cond"])==target: t_rid,c_rid,t_slot=r["run_id_a"],r["run_id_b"],"A"
        elif str(cb["cond"])==target: t_rid,c_rid,t_slot=r["run_id_b"],r["run_id_a"],"B"
        else: continue
        ft,fc=feat(d3,t_rid),feat(d3,c_rid)
        if ft is None or fc is None: continue
        won=1.0 if ((r["winner"]=="A" and t_slot=="A") or (r["winner"]=="B" and t_slot=="B")) else 0.0
        cl=(ca["user"],r["scenario_id"],ca["author"])
        rows.append((won, ft-fc, 1.0 if t_slot=="B" else 0.0, cl))
    return rows

def estimates(rows):
    y=np.array([r[0] for r in rows]); dS=np.vstack([r[1] for r in rows]); slot=np.array([r[2] for r in rows])
    mu=dS.mean(0); sd=dS.std(0)+1e-9; dz=(dS-mu)/sd
    # position-controlled raw: average win rate within slot then mean (here mean over both slots)
    raw=y.mean()
    bal=(np.abs(dz[:,0])<0.5)&(np.abs(dz[:,1])<0.5)
    balrate=y[bal].mean() if bal.sum()>=10 else np.nan
    X=np.column_stack([np.ones(len(y)),slot,dz])
    b=logistic_fit(X,y)
    adj=1/(1+math.exp(-(b[0]+0.5*b[1])))
    return raw,balrate,adj,b,bal.sum()

def cluster_boot(rows,B=2000,seed=7):
    clusters={}
    for r in rows: clusters.setdefault(r[3],[]).append(r)
    keys=list(clusters); rng=np.random.default_rng(seed)
    out={"raw":[],"bal":[],"adj":[]}
    for _ in range(B):
        samp=[]
        for k in rng.choice(len(keys),len(keys)): samp.extend(clusters[keys[k]])
        try:
            raw,bal,adj,_,_=estimates(samp); out["raw"].append(raw); out["bal"].append(bal); out["adj"].append(adj)
        except Exception: pass
    def ci(a):
        a=[x for x in a if not (x!=x)]; a=np.sort(a)
        return [round(float(np.percentile(a,2.5)),3),round(float(np.percentile(a,97.5)),3)] if len(a)>20 else None
    return {k:ci(v) for k,v in out.items()}

def main():
    outputs=load_outputs(); d3=load_d3()
    pairwise=[]
    for fn in ("pairwise_scores.jsonl","pairwise_swap_scores.jsonl"):
        for l in open(f"{RUN}/{fn}"):
            l=l.strip()
            if l and '\x00' not in l:
                try: pairwise.append(json.loads(l))
                except: pass
    contrasts=[(("C4","C4_WRONG_PROFILE"),"C4"),(("C3","C4_WRONG_PROFILE"),"C3"),
               (("C4","C_GENERIC_CONTRACT"),"C4"),(("C3","C_GENERIC_CONTRACT"),"C3"),
               (("C0","C_GENERIC_CONTRACT"),"C_GENERIC_CONTRACT"),(("C0","C4_WRONG_PROFILE"),"C4_WRONG_PROFILE")]
    res=[]
    for pair,target in contrasts:
        rows=build_rows(pair,target,outputs,d3,pairwise)
        if len(rows)<30:
            res.append({"contrast":f"{target} vs {[x for x in pair if x!=target][0]}","n":len(rows),"note":"insufficient"}); continue
        raw,bal,adj,b,baln=estimates(rows); cis=cluster_boot(rows)
        res.append({"contrast":f"{target} vs {[x for x in pair if x!=target][0]}","n":len(rows),
            "raw_win":round(raw,3),"raw_ci":cis["raw"],
            "style_balanced_win":round(float(bal),3),"style_balanced_n":int(baln),"style_balanced_ci":cis["bal"],
            "surface_adjusted_win":round(adj,3),"surface_adjusted_ci":cis["adj"],
            "coef_logLen":round(b[2],3),"coef_lexOverlap":round(b[3],3),"coef_hedging":round(b[4],3),"slot_coef":round(b[1],3),
            "survives": (cis["adj"] is not None and cis["adj"][0]>0.5)})
    print(json.dumps(res,indent=2))
if __name__=="__main__": main()
