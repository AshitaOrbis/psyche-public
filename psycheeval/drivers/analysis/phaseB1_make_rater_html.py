"""Build a self-contained, mobile-first HTML rater tool from the human-rater inbox.

One item per screen, big A/Tie/B buttons (AskUserQuestion-style), scrollable
context cards, progress + localStorage resume, and a copy-paste answer code at
the end. No server, no app installs (opens in Chrome on a phone).
"""
import json, os, html

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INBOX = f"{REPO}/runs/2026-05-19_v03/phaseB1_human_rater_inbox.jsonl"
OUT = f"{REPO}/runs/2026-05-19_v03/phaseB1_rater.html"

items = []
for l in open(INBOX):
    l = l.strip()
    if l:
        r = json.loads(l)
        items.append({"id": r["item_id"], "profile": r["person_profile"],
                      "situation": r["situation"], "A": r["response_A"], "B": r["response_B"]})

DATA = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")

PAGE = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>PsycheEval — fit rater</title>
<style>
:root{--bg:#0e1116;--card:#171c24;--card2:#1d242e;--ink:#e6edf3;--mut:#9aa7b4;--line:#2b3440;
--a:#2f81f7;--tie:#6e7681;--b:#d29922;--good:#238636;}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
#top{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 14px}
#bar{height:6px;background:var(--card2);border-radius:3px;overflow:hidden;margin-top:8px}
#fill{height:100%;width:0;background:var(--good);transition:width .2s}
.wrap{max-width:760px;margin:0 auto;padding:14px 14px 120px}
h2{font-size:14px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut);margin:18px 0 6px}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;white-space:pre-wrap;word-wrap:break-word}
.scroll{max-height:34vh;overflow:auto}
.resp{background:var(--card2)}
.tag{display:inline-block;font-weight:700;padding:2px 10px;border-radius:999px;font-size:13px;margin-bottom:8px}
.tagA{background:rgba(47,129,247,.18);color:#79b8ff;border:1px solid #2f81f7}
.tagB{background:rgba(210,153,34,.18);color:#e3b341;border:1px solid #d29922}
.q{font-weight:600;margin:18px 4px 4px}
#btns{position:fixed;left:0;right:0;bottom:0;background:linear-gradient(180deg,rgba(14,17,22,0),var(--bg) 22%);
padding:14px;display:flex;gap:8px;max-width:760px;margin:0 auto}
button.choice{flex:1;border:0;border-radius:14px;padding:16px 8px;font-size:15px;font-weight:700;color:#fff}
.cA{background:var(--a)}.cT{background:var(--tie)}.cB{background:var(--b)}
button.choice:active{filter:brightness(1.25)}
#nav{display:flex;justify-content:space-between;align-items:center;margin-top:6px;color:var(--mut);font-size:14px}
#nav a{color:var(--a);text-decoration:none;padding:6px 4px}
.cur{outline:3px solid #fff;outline-offset:1px}
#done{display:none}
textarea{width:100%;min-height:130px;background:var(--card);color:var(--ink);border:1px solid var(--line);
border-radius:10px;padding:10px;font:14px ui-monospace,monospace}
button.big{width:100%;border:0;border-radius:12px;padding:15px;font-size:16px;font-weight:700;color:#fff;background:var(--good);margin-top:10px}
.hint{color:var(--mut);font-size:14px}
input#rater{width:100%;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:12px;font-size:16px;margin-top:6px}
</style></head><body>
<div id="top"><div id="hd"><b id="cnt">—</b> <span class="hint" id="ans"></span><div id="bar"><div id="fill"></div></div></div></div>
<div class="wrap">
 <div id="start">
   <h2>Before you begin</h2>
   <div class="box">You'll see <b id="n0"></b> short cases. Each shows <b>one person</b> (their behavioural profile), <b>their situation</b>, and <b>two assistant replies</b>. Pick the reply that <b>better serves THAT person</b> — fits how <i>they</i> need to be engaged — not which is generally better-written. "Equal" is allowed but use it sparingly. Your answers save on this phone as you go; you can close and resume.</div>
   <h2>Your name / initials (labels your answers)</h2>
   <input id="rater" placeholder="e.g. RP" autocomplete="off">
   <button class="big" onclick="begin()">Start rating</button>
 </div>

 <div id="card" style="display:none">
   <h2>Who this person is</h2><div class="box scroll" id="profile"></div>
   <h2>Their situation</h2><div class="box" id="situation"></div>
   <h2>Response A</h2><div class="box resp scroll"><span class="tag tagA">A</span><div id="rA"></div></div>
   <h2>Response B</h2><div class="box resp scroll"><span class="tag tagB">B</span><div id="rB"></div></div>
   <div class="q">Which reply better <u>serves this person</u>?</div>
   <div id="nav"><a onclick="go(-1)">‹ Back</a><span id="pos"></span><a onclick="skipFwd()">Skip ›</a></div>
 </div>

 <div id="done">
   <h2>Done — send your answers back</h2>
   <div class="box">Tap <b>Copy</b>, then paste this into the Claude chat. (You can keep editing answers with Back if you missed any.)</div>
   <textarea id="code" readonly></textarea>
   <button class="big" onclick="copyCode()" id="copyb">Copy answers</button>
   <div class="hint" id="copied"></div>
 </div>
</div>

<div id="btns" style="display:none">
  <button class="choice cA" onclick="pick('A')">A fits better</button>
  <button class="choice cT" onclick="pick('T')">Equal</button>
  <button class="choice cB" onclick="pick('B')">B fits better</button>
</div>

<script>
const ITEMS = __DATA__;
const KEY = "psycheval_b1_rater_v1";
let st = JSON.parse(localStorage.getItem(KEY) || "{}");
if(!st.ans) st.ans = {};
let i = 0;
const $ = id => document.getElementById(id);
function save(){ localStorage.setItem(KEY, JSON.stringify(st)); }
function begin(){
  st.rater = ($("rater").value || "anon").trim(); save();
  $("start").style.display="none"; $("card").style.display="block"; $("btns").style.display="flex";
  i = ITEMS.findIndex(x => !(x.id in st.ans)); if(i<0) i=0; render();
}
function render(){
  const it = ITEMS[i];
  $("profile").textContent = it.profile;
  $("situation").textContent = it.situation;
  $("rA").textContent = it.A; $("rB").textContent = it.B;
  document.querySelectorAll('.box.scroll').forEach(e=>e.scrollTop=0);
  const done = Object.keys(st.ans).length;
  $("cnt").textContent = "Case " + (i+1) + " / " + ITEMS.length;
  $("ans").textContent = done + " answered";
  $("pos").textContent = (st.ans[it.id] ? "your pick: " + ({A:'A',B:'B',T:'Equal'}[st.ans[it.id]]) : "");
  $("fill").style.width = (100*done/ITEMS.length) + "%";
  document.querySelectorAll('.choice').forEach(b=>b.classList.remove('cur'));
  if(st.ans[it.id]){ const m={A:'.cA',B:'.cB',T:'.cT'}[st.ans[it.id]]; document.querySelector(m).classList.add('cur'); }
  window.scrollTo(0,0);
}
function pick(v){ st.ans[ITEMS[i].id]=v; save(); setTimeout(()=>go(1),120); }
function go(d){ i+=d; if(i>=ITEMS.length){ return finish(); } if(i<0) i=0; render(); }
function skipFwd(){ go(1); }
function finish(){
  $("card").style.display="none"; $("btns").style.display="none"; $("done").style.display="block";
  const parts = ITEMS.filter(x=>st.ans[x.id]).map(x=>x.id+"="+st.ans[x.id]);
  $("code").value = "PHASEB1HR|rater="+(st.rater||"anon")+"|"+parts.join("|");
  const miss = ITEMS.length - Object.keys(st.ans).length;
  $("copied").textContent = miss? (miss+" case(s) still unanswered — use Back if you want to fill them."):"All "+ITEMS.length+" answered.";
  $("cnt").textContent="Done"; $("ans").textContent=Object.keys(st.ans).length+" answered"; $("fill").style.width="100%";
}
function copyCode(){ const t=$("code"); t.select(); document.execCommand('copy');
  navigator.clipboard&&navigator.clipboard.writeText(t.value); $("copied").textContent="Copied — paste it into the Claude chat."; }
$("n0").textContent = ITEMS.length;
// resume straight into the deck if already started
if(st.rater){ $("rater").value = st.rater; }
</script></body></html>"""

html_out = PAGE.replace("__DATA__", DATA)
open(OUT, "w").write(html_out)
print(f"wrote {len(items)} items -> {OUT}  ({len(html_out)//1024} KB)")
