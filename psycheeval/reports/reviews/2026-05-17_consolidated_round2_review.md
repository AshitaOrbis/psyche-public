# PsycheEval v0.2 — Consolidated Round-2 External Review

**Date**: 2026-05-17
**Status**: Decision-ready synthesis of four independent reviews of the Phase 0 + Phase 1 corrected dataset
**Scope**: Pre-publication critique focused on (A) remaining blockers for the v0.2 curated report, (B) quick fixes runnable in ≤1 day, (C) v0.3 questions

---

## Method

Four independent reviewers received the same round-2 bundle (`2026-05-17_v0_2_review_bundle_round2.md`, 14 KB) plus pointers to all artifacts. The bundle explicitly framed round 2 as "what did round 1 miss" rather than re-asking round-1 questions, and surfaced three specific tensions for scrutiny.

| Reviewer | Model(s) | Architecture | File (size) |
|---|---|---|---|
| **ChatGPT Pro** | GPT-5.4 Pro | Single-agent, extended reasoning | `2026-05-17_gpt-pro_round2_review.md` (32 KB) |
| **Codex Council** | 4× GPT-5.5 xhigh + Opus synth | Blind ensemble (skeptic / architect / risk-analyst / empiricist) | `2026-05-17_codex-council_round2_review.md` (16 KB) |
| **GPT Max** | 4× GPT-5.5 xhigh + Opus synth | HCOM-coordinated (peer drafts visible) | `2026-05-17_gpt-max_round2_review.md` (16 KB) |
| **Opus 4.7 subagent** | Opus 4.7 | Single-agent independent reviewer (Task tool) | `2026-05-17_opus_round2_review.md` (47 KB) |

Four reviews, three LLM families (OpenAI GPT-5.4 Pro, OpenAI GPT-5.5, Anthropic Opus). The convergence is unusually strong: all four reviewers independently flagged most of the same items.

---

## 1. Publication-blocking issues (all four reviewers convergent)

These must be addressed before writing the v0.2 curated report.

### 1.1 The Wilson CI on `controlled_lo_win_rate` is mis-specified — needs matched-pair / cluster bootstrap

**Evidence**: `analyze.py:654`:

```python
wci_lo, wci_hi = wilson_interval(round(b["sum_lo_wins_controlled"]), n) if n else (None, None)
```

The analyzer's own comment at line 652-653 admits this is "rough; for exact, would need pair-level matched test." All four reviewers independently identified this.

- **Opus** (A.2): "The Wilson CI on the AB/BA `controlled_lo_win_rate` is computed incorrectly for paired-pair data — it treats each AB/BA-matched pair as a single Bernoulli trial at the rounded controlled rate, not as a clustered matched-pair statistic. The CIs in the headline AB/BA table are tighter than they should be"
- **Codex Council** unanimous (§4 #1): "Run paired/cluster bootstrap CIs on the canonical AB/BA table. (Hours, no new data.)"
- **GPT Max** (Disagreement A): The Empiricist **actually ran** the matched-pair bootstrap and reported all six headline CIs preserve their verdicts: "C1_padded vs C4 0.623 [0.577, 0.669], C3 vs C5_CONTRACT 0.499 [0.452, 0.546], C4 vs C4_shuffled 0.578 [0.531, 0.623], C4 vs C5 0.681 [0.613, 0.747], C4 vs C5_CONTRACT 0.518 [0.471, 0.566], C5 vs C5_CONTRACT 0.677 [0.631, 0.722]." → **Verdicts hold; canonicalize the matched-pair CIs.**
- **GPT Pro** (A3): "Before writing, recompute all Tier 1 CIs using at least: 1. paired AB/BA cell bootstrap, 2. scenario-cluster bootstrap, 3. persona-cluster bootstrap, 4. scenario × persona cell bootstrap, 5. judge-cluster or judge-stratified meta-analysis, 6. author-stratified estimates."

**Action**: replace the Wilson CI with cluster bootstrap (cluster unit: persona × scenario × author, same as `_compute_cluster_bootstrap_pairwise`). Display both Wilson and bootstrap side-by-side. ~0.5 day. Note: GPT Max Empiricist's spot-check shows verdicts survive; this is a publication-hygiene fix, not a substantive risk.

### 1.2 GPT Pro caught arithmetic / count inconsistencies in the Phase 1 findings doc

**Critical new finding** unique to GPT Pro round 2:

- **Tier A count discrepancy**: Phase 1 findings says "Tier A: 873 swap-rejudge records." But the displayed table shows 288 + 288 + 288 = 864. The 873 is wrong (likely includes 9 over-coverage records); 864 is the AB/BA-matched count.

- **C1_padded vs C4 estimate inconsistency**: AB/BA table shows `controlled = 0.377`, meaning C1_padded wins 37.7% and C4 wins 62.3%. But Tier 1 summary says "66.1% C4 [59.5, 72.0]." **The 66.1% number is wrong.** Real value: 62.3%.

- **C4 vs C5 estimate inconsistency**: AB/BA table shows `controlled = 0.681` (C4 wins 68.1%). But Tier 1 summary says "68.9% C4 [61.6, 75.9]." **The 68.9% is wrong by ~1pp.** Real value: 68.1%.

**Source**: GPT Pro §A1 ("AB/BA result table and final Tier 1 summary are internally inconsistent"). I did not catch these in self-review. They are blocking because the report would inherit them.

**Action**: fix the Phase 1 findings doc's Tier 1 summary table to use the controlled lo_win rates (with the lo→hi transform stated explicitly where applicable). Add a smoke test that final report estimates == transformed AB/BA table estimates.

### 1.3 C5_CONTRACT > C5 is a package claim, not a mechanism claim

Unanimous across all four:

- **Opus** (A.4): "structured contract repairs unstructured source packet" is mechanism framing. The dataset can support exactly the **package** claim — adding the contract package to the source packet improves it — but cannot isolate which component (contract presence, ordering, anti-mimicry, profile length, or interaction) does the work.
- **Codex Council**: "C5_CONTRACT > C5 is the cleanest Tier 1 finding, but supports only a *package* claim, not a *mechanism* claim. Contract presence is confounded with ordering, anti-mimicry text, profile length, and instruction density. Mechanism attribution requires `C_GENERIC_CONTRACT` and related v0.3 ablations."
- **GPT Max**: "Forbidden until v0.3: 'contract mechanism,' 'public-anchor value,' 'profile-specificity proven.' Allowed wording: 'contract-first source-packet package beats uncontracted source packet.'"
- **GPT Pro** (A7): "Allowed claim: Adding the C5_CONTRACT wrapper to the C5 source-packet condition improves judged output quality relative to C5 alone. Not allowed: Source packets add value when subordinated to contracts. … Also not allowed without C_GENERIC_CONTRACT: The behavioral contract specifically, rather than generic instruction scaffolding, length, salience, repetition, or formatting, caused the lift."

**Also from GPT Pro (A7)**: the attenuation framing in the round-2 bundle is misstated. "76.0% → 67.7%" is an 8.3pp absolute attenuation, not 16pp. The above-parity edge shrinks from +26.0pp to +17.7pp — a 32% reduction in edge size. Still meaningful, but the round-2 bundle's "~16 pp attenuation" claim was wrong.

**Action**: Strike all mechanism language for C5_CONTRACT > C5 in the curated report. Use the package framing consistently. Fix the attenuation magnitude.

### 1.4 C5_CONTRACT vs C3 and vs C4 collapse to "no detected preference"

Unanimous. Both controlled CIs include 0.5. The original headlines must be retracted.

GPT Pro (A15) adds a critical wording precision: **"collapse" ≠ "equivalence"** unless an equivalence margin is predeclared. The correct wording is:

> "We do not detect a reliable pairwise preference between C5_CONTRACT and C3/C4 after AB/BA correction. The CIs still allow small effects in either direction. Scalar scores do not support a C5_CONTRACT advantage over C3 or C4."

### 1.5 C4 > C5 is OpenAI-judge-only — needs Opus fill OR scope qualifier

Unanimous flag: Phase 0 §0.C verified Opus has zero pairwise records for C4 vs C5. The Phase 1 AB/BA was therefore done with only GPT-5.4 + GPT-5.5 judging — and the strengthening from 63.7% → 68.9% is within an OpenAI-only judge scope.

- **Codex Council** Skeptic: "the single <1-day experiment higher value than starting a new condition." Adjudication: "do the Opus fill before curation."
- **GPT Max** architect: "broadens the scope label if it confirms; if it reverses, the report must scope down."
- **Opus** (A.1): "There is no positive evidence the length confound is resolved; AB/BA does not control for length. This should be Tier 1.5 at most, with the length caveat surfaced, not buried."
- **GPT Pro** (A5): "Correct framing: In OpenAI-family pairwise judging, C4 beats C5 after AB/BA correction. To make it Tier 1 without caveat, add Opus judging for C4 vs C5."

**Action options**:
- **Option A**: Run Opus original pairwise + AB/BA on C4 vs C5 (~160 + 160 = 320 Opus calls). Within budget. Recommended.
- **Option B**: Scope the headline to "In OpenAI-family pairwise judging, …" — ship as Tier 1 with scope.

Either option is defensible; **Option A is the strictly stronger position** and within budget. Recommended.

### 1.6 The C4 > C5 vs Phase 0 length-match contradiction is unresolved

The Phase 1 findings doc says length-matching gave "a false negative." All four reviewers reject this framing:

- **Opus** (A.1): "AB/BA does not control for length. The two corrections target different confounds. Length-matching restricts to similar-length response pairs; AB/BA swaps the slot. These are orthogonal corrections."
- **GPT Pro** (A10): "Not necessarily an analyzer bug. These are different estimands. Run … 1. full set, 2. same length-matched subset used in Phase 0, 3. non-length-matched complement, 4. regression/mixed model with length difference as covariate, 5. scenario-family and author strata inside length buckets."

What the data actually supports for C4 vs C5:
- Position-controlled, length-uncontrolled: 68.1% C4
- Length-controlled, position-uncontrolled: 52.2% C4 (CI touches 0.5)
- Position + length controlled: **not computed**

**Action**: Compute the joint position × length correction (subset AB/BA records to length-similar bucket). Cost: hours (no new data). If it survives: Tier 1. If it collapses: Tier 1.5 with explicit caveat. The Phase 1 doc's framing of "length-matching gave a false negative" must be replaced with "different confounds; joint correction below."

### 1.7 Cross-provider Phase 0 C3 vs C5_CONTRACT is now superseded — not Tier 1 evidence

The Phase 0 finding that C3 vs C5_CONTRACT "strengthens under cross-provider judging" was hypothesis-generating only. GPT Max Empiricist **directly ran the cross-provider AB/BA on this pair**: 0.543 [0.466, 0.622] for the C5_CONTRACT win — straddles 0.5. The cross-provider Phase 0 result was an artifact of GPT-5.4 having no slot-B bias, not a real preference.

All four reviewers agree this should be reported as the empirical reason the Phase 0 stratified finding is demoted, not as a competing positive verdict.

**Action**: in the curated report, the cross-provider C3 vs C5_CONTRACT result lives in a "Why AB/BA was necessary" methodology subsection, not in headlines.

### 1.8 The slot-B bias finding must be scoped to corpus, not universalized

Codex Council Skeptic + GPT Max + GPT Pro converge on this wording discipline:

**Wrong wording** (from round-2 bundle): "LLM judges show ~15–17pp systematic slot-B preference."
**Right wording** (Codex Skeptic verbatim): "In this corpus, prompt, judge set, and pairwise protocol, two of three judge configurations directly showed large later-answer / slot-B preference. GPT-5.5 and Opus showed substantial slot-B effects; GPT-5.4 showed little to none. Uncounterbalanced margins were misleading."

GPT Pro (A8) adds: "Add CIs for every judge-specific position effect. Also report a per-cell four-way decomposition: condition-stable winner / opponent-stable winner / slot-A-stable winner / slot-B-stable winner."

**Action**: per-judge slot-B CIs need to be in the analyzer (currently only point estimates exist offline; see 1.9), and the methodology section uses scoped wording.

### 1.9 Per-judge slot-B advantage table is not in metrics JSON

Opus A.3 unique blocking call: "The judge-stratified AB/BA numbers in the Phase 1 findings doc are not in the metrics JSON." The Phase 1 doc's "Slot B advantage measured per judge" table was computed offline. The methodology contribution rests on these numbers; they need to be canonical.

Convergent with Codex Council ("Add the AB/BA × judge × author × provider-scope × persona × family × length-bucket stratified table"), GPT Max ("Judge-stratified AB/BA table (pair × judge family)"), and GPT Pro (B1 #2 + B2 #3).

**Action**: add `ab_ba_position_audit_same_author_by_judge` block to analyzer. ~0.5 day.

### 1.10 Opus AB/BA on C3/C4 vs C5_CONTRACT is under-covered

Opus A.3 secondary problem: Opus AB/BA n = 87 (vs original n = 115) for C3 vs C5_CONTRACT — **28 records missing**. Same for C4 vs C5_CONTRACT (Opus AB/BA n = 85 vs original n = 117 — 32 records missing). This non-random subset confound was not addressed in Phase 1. Either run the missing ~60 Opus calls or document the missingness pattern. Other reviewers did not flag this but it's defensible.

---

## 2. Convergent quick fixes — pre-write hygiene pass

All <1 day each. Ordered by cost-benefit.

### 2.1 Canonicalize matched-pair / cluster bootstrap CIs (replaces Wilson)
Hours, no new data. See §1.1.

### 2.2 Fix Phase 1 findings doc arithmetic errors
Minutes. See §1.2 — three numbers wrong (873 count, 66.1% for C4 vs C1_padded, 68.9% for C4 vs C5).

### 2.3 Build the claim ledger table (this is the report's central artifact)

Unanimous — Codex Council Risk-Analyst, GPT Max architect, GPT Pro B1 #9.

Columns: `claim | controlled estimate | matched CI | AB/BA status | judge scope | persona scope | author scope | scalar alignment | length-audit result | allowed wording | forbidden wording | tier`.

**Function**: this replaces the current split between "Final AB/BA results" and "Final tier assignment" in the Phase 1 doc — those currently conflict (see 1.2). One source of truth.

### 2.4 Add judge-stratified AB/BA + per-cell consistency tables to analyzer

See §1.9. Plus per-cell four-way decomposition (GPT Pro A8): condition-stable / opponent-stable / slot-A-stable / slot-B-stable / unstable.

### 2.5 Add the complete-case scalar table

Unanimous — Phase 0 promised it but didn't render. With only 67.5% complete-case coverage, pooled scalar means could carry selection bias. Add `scalar_means_complete_case` table to autogen.

### 2.6 Stale-text lint + supersession table

Codex Council, GPT Max, GPT Pro all flag stale prose in the Phase 1 findings doc (the C4 vs C4_shuffled sign-correction was a known fix-in-progress; round 2 caught residual contradictions). String-lint against forbidden phrases: "PAE empirically resolved," "C5_CONTRACT outperforms C3/C4," unqualified "tri-model cross-provider," "pure position bias," "mechanism," "cannot be a recognition artifact," "contract repairs source packets."

Also: a supersession table (Phase 0 claims → Phase 1 verdicts) so readers don't have to reconcile contradictory files.

### 2.7 Joint position × length AB/BA for C4 vs C5

Hours, no new data. See §1.6.

### 2.8 Run cross-provider AB/BA C3 vs C5_CONTRACT as a published demotion

Hours — GPT Max Empiricist already ran this offline and got 0.543 [0.466, 0.622]. Canonicalize in the autogen as the empirical reason the Phase 0 cross-provider result is demoted.

### 2.9 Per-pair scalar-pairwise alignment for ALL Tier 1 pairs (not just C5_CONTRACT)

GPT Pro A12: "every Tier 1 claim needs the same scalar-pairwise alignment table." Add C4 vs C1_padded, C4 vs C5, C4 vs C4_shuffled, C4 vs C0 to the existing scalar-pairwise reconciliation block (which already exists in metrics).

### 2.10 Replace "TF-IDF F1=0 → cannot be recognition" with cautious wording

Codex Council Skeptic + GPT Pro A13 converge. Wording: "We did not find evidence that a simple TF-IDF classifier could distinguish C5 from C5_CONTRACT outputs. This does not rule out semantic or stylistic recognizability."

### 2.11 Add Opus AB/BA on C4 vs C5 (~320 Opus calls)

The single experiment that converts a scope-limited headline into a generalizable one. See §1.5. Codex Council Skeptic + GPT Max architect both endorse running this before report draft.

### 2.12 Same-orientation rejudge sentinel (50–100 pair re-judgments)

Codex Council architect (sized at 50–100), GPT Pro A2 + B2 #1, GPT Max architect. Decomposes AB/BA flip rate into "position bias" + "retest noise" — converts the methodology section from "we observed flips" to "we decomposed flips."

---

## 3. v0.3 questions — fresh angles round 1 missed

Round 1 priorities (still valid): C_GENERIC_CONTRACT, C4_WRONG_PROFILE, C5_NONPUBLIC, paraphrased rubric, human calibration, real-user shadow validation.

### Convergent new angles (multiple round-2 reviewers)

| Angle | Round-2 reviewers |
|---|---|
| **Profile freshness / staleness / contradiction** (deployment realism: real profiles will be stale, partially wrong, contradictory) | Codex Council Empiricist, GPT Max Empiricist, GPT Pro C5 |
| **Profile compression / token-cost frontier** (7,433-char C5_CONTRACT is unrealistic for deployment; compress to 500/1K/2K and report performance curve) | Codex Council Architect, GPT Max Skeptic, GPT Pro C12 |
| **Scenarios authored blind to profile theory** (current scenarios may have been written with persona content in mind, accidentally rewarding profile-legibility per se) | Codex Council Risk-Analyst+Skeptic+Architect+Empiricist all surfaced, GPT Pro C17 |
| **Contract-component ablation** (within C5_CONTRACT: generic challenge language vs anti-mimicry vs scenario hints vs ordering vs packet length — C_GENERIC_CONTRACT only answers generic-vs-specific) | Codex Council Skeptic, GPT Max Skeptic, GPT Pro C1+C2 |
| **Tie / no-difference option** for pairwise judging (forced-choice manufactures fake precision; C3/C4 vs C5_CONTRACT may be forced-choice noise) | Codex Council Skeptic, GPT Max Empiricist, GPT Pro C8 |
| **Pairwise vs scalar measure different latent constructs** (scalar-pairwise contradiction was the round-1 surprise; v0.3 should model it directly) | GPT Pro C7, GPT Max architect |
| **Same-order repeat audit** as a default protocol (not a one-off correction) — judge reliability as infrastructure | Codex Council architect, GPT Max architect, GPT Pro C9 |

### Angles unique to a single reviewer (worth considering)

- **Opus C.2** (intra-rater reliability): rejudge a small sample N=50 pairs by the SAME judge to measure noise floor — distinguishes condition effect from judge variance
- **Opus C.3** (blind scenarios): scenarios authored without seeing personas
- **Opus C.5** (which dimensions of the anchored rubric carry the C5_CONTRACT > C5 effect): dimension-by-dimension scalar decomposition would tell us if it's all `profile_fit` or distributed
- **Opus C.6** (opposite-trait wrong-profile, not just any-wrong-profile): C4_WRONG_PROFILE should use a profile that suggests opposite preferences, not a random other persona's profile
- **GPT Pro C3** (overpersonalization detection): scenarios where adaptation becomes intrusive, presumptive, or stereotyping
- **GPT Pro C4** (when to ask vs use profile): some cases, the correct behavior is to NOT use profile context
- **GPT Pro C10** (output feature mediation analysis): bullet count, empathy markers, caveats, etc. — does condition effect survive feature adjustment?
- **GPT Pro C13** (safety in sensitive domains)
- **GPT Pro C14** (multi-turn interaction)
- **GPT Pro C15** (author × judge style interaction): do judges prefer outputs that match their own family's rhetorical style? Separate from provider-family cross-judging.
- **GPT Pro C16** (harmful personalization negative controls)
- **GPT Pro C18** (predeclared primary endpoint hierarchy): pairwise vs scalar vs red-flag need a hierarchy before next data collection
- **Codex Council Risk-Analyst** (tail-risk reporting): worst-decile and red-flag rates, not just mean win rates

### v0.3 architectural recommendation (convergent)

Codex Council architect formalizes; GPT Max architect endorses: v0.3 should be **one factorial mechanism design** + **parallel profile-realism arm** + **judge-reliability arm as default infrastructure** + **construct-validity arm** (real-user shadow).

---

## 4. Tier reassignment after round 2

Tier 1 verdicts that survive ALL four round-2 reviewers:

| Pair | Original | Phase 1 controlled | Round-2 consolidated framing |
|---|---|---|---|
| **C5_CONTRACT > C5** | 76.0% | 67.7% [62.1, 72.8] | **Tier 1**, package claim only |
| **C4 > C1_padded** | 68.1% | **62.3%** [need to verify with corrected number] | **Tier 1** |
| **C4 > C5** | 63.7% | **68.1%** [need to verify with corrected number] | **Tier 1 with scope qualifier** "OpenAI-judge-pairwise" OR run Opus fill |

Round-2 modifications:

| Pair | Phase 1 status | Round-2 verdict |
|---|---|---|
| **C4 > C4_shuffled** | "Tier 1 (sign-correction)" | **Tier 1 with effect-size differentiation** — at 57.8% [52.3, 63.1] this is meaningfully smaller than the 17-19pp effects elsewhere. Codex/GPT-Max/GPT-Pro all say tag as "modest" or use claim-ledger effect-size column. Opus says "Tier 1.5". Either resolution is fine; do not let "Tier 1" launder a 7.8pp effect into peer status. |
| **C0 dominated** | Tier 1 (not AB/BA tested) | **Tier 1 with explicit "not AB/BA-controlled"** caveat (GPT Pro A6). Effect size makes it likely-robust to position bias but the exact magnitude is uncontrolled. |
| **C5_CONTRACT vs C3** | Tier 2 (collapses) | **"No detected pairwise preference under AB/BA"** — NOT "equivalence" (GPT Pro A15). |
| **C5_CONTRACT vs C4** | Tier 2 (collapses) | Same wording. |

Strike entirely (unanimous):
- "v0.1 PAE confound is empirically resolved in favor of absence of contract as dominant driver"
- "C5_CONTRACT outperforms both C3 and C4"
- "Source packets add value when subordinated to contracts"
- "Coherent structure does not significantly beat shuffled" (replaced with positive: C4 > C4_shuffled 57.8% controlled)
- "Contract repairs source-packet fragility" (mechanism language)
- "C5 vs C5_CONTRACT cannot be a recognition artifact" (TF-IDF F1=0 doesn't establish this)
- "LLM judges show ~15–17pp systematic slot-B preference" (universalized framing — scope to corpus)

---

## 5. Convergence vs divergence map

### 4-way convergence (all four reviewers)

1. Wilson CI → matched-pair / cluster bootstrap (§1.1)
2. C5_CONTRACT > C5 is package not mechanism (§1.3)
3. C5_CONTRACT vs C3/C4 collapse to no-preference (§1.4)
4. C4 > C5 needs Opus scope or fill (§1.5)
5. C4 vs C4_shuffled should be tagged as smaller-effect or "modest" Tier 1
6. Cross-provider Phase 0 C3 vs C5_CONTRACT is demoted (empirically verified by GPT Max Empiricist)
7. Slot-B finding must be corpus-scoped not universalized (§1.8)
8. Per-judge slot-B table needed in metrics (§1.9)
9. Claim ledger table is the report's central artifact (§2.3)
10. Same-orientation rejudge sentinel needed (§2.12)
11. Stale-text lint mandatory (§2.6)
12. Complete-case scalar table needed (§2.5)
13. C_GENERIC_CONTRACT + C4_WRONG_PROFILE as top v0.3 priority

### 3-way convergence (Codex Council + GPT Max + GPT Pro)

- Stale prose flagged in Phase 1 doc (line ~199-201 reference)
- C4 > C4_shuffled effect-size differentiation needed (not strict demotion)
- Empiricist matched-pair bootstrap shows verdicts preserved
- TF-IDF F1=0 wording is too strong (also flagged by Codex Council Skeptic + GPT Pro A13)

### Unique findings worth heeding

- **GPT Pro A1**: arithmetic errors in Phase 1 findings doc (873 vs 864 count, 66.1% vs 62.3% for C4 vs C1_padded, 68.9% vs 68.1% for C4 vs C5). **Blocking — fix immediately.**
- **GPT Pro A2**: AB/BA confounds position with phase drift (run same-orientation rejudge sentinel)
- **GPT Pro A7**: attenuation magnitude misstated in round-2 bundle (8.3pp absolute, not 16pp)
- **Opus A.7**: persona × author interaction not yet computed (Slalom Altar × Opus may carry the reversal)
- **Opus A.3 secondary**: Opus AB/BA n=87 vs original n=115 for C3 vs C5_CONTRACT (28 missing records; non-random subset)
- **GPT Pro A15**: "collapse" ≠ "equivalence" — needs predeclared margin if claiming equivalence
- **GPT Pro C18**: predeclared primary endpoint hierarchy needed for v0.3
- **Codex Council Risk-Analyst**: AB/BA can create false certainty if high flip rates reflect judge noise (separate from order bias) — must flag in methodology

### No genuine 4-way disagreements

The reviewers diverged only on emphasis. The Wilson CI was unanimously called a fix; Opus framed it as "anti-conservative" while GPT Max Empiricist directly showed matched-pair gives equally-tight or slightly tighter CIs and the verdicts hold. Both can be true depending on the within-pair correlation structure; both reviewers agree the fix is to publish matched-pair / cluster CIs.

---

## 6. Recommended execution order (pre-report)

Total estimated cost: **~3 person-days** + ~320 Opus calls (Tier B fill for C4 vs C5).

### Phase 2a — Same-data hygiene (Day 1)
1. Fix Phase 1 findings arithmetic errors (§1.2, §2.2) — minutes
2. Replace Wilson CI with cluster bootstrap (§1.1, §2.1) — half-day
3. Stale-text lint + supersession table (§2.6) — minutes
4. Per-pair scalar-pairwise alignment for ALL Tier 1 pairs (§2.9) — quarter-day
5. Complete-case scalar table (§2.5) — quarter-day

### Phase 2b — New analyzer blocks (Day 2)
6. Judge-stratified AB/BA + per-cell consistency tables (§1.9, §2.4) — half-day
7. Joint position × length AB/BA for C4 vs C5 (§1.6, §2.7) — quarter-day
8. Cross-provider AB/BA C3 vs C5_CONTRACT (§2.8) — quarter-day (GPT Max Empiricist already ran it offline)
9. Persona × author × condition cross-tab (Opus A.7) — quarter-day

### Phase 2c — Curated report architecture (Day 3)
10. Build claim ledger table (§2.3) — half-day
11. Write the curated report with:
   - Tier 1 controlled findings (with effect-size differentiation)
   - Explicit demotions (collapsed C5_CONTRACT vs C3/C4)
   - Methodology contribution (scoped slot-B bias)
   - "Why AB/BA was necessary" (cross-provider C3 demotion narrative)
   - Scope, limitations, v0.3 roadmap

### Optional / depending on quota
12. Opus AB/BA for C4 vs C5 (§1.5, §2.11) — ~320 Opus calls. Recommended; converts Tier 1 scope qualifier into clean Tier 1.
13. Opus AB/BA backfill for C3/C4 vs C5_CONTRACT (Opus A.3 secondary) — ~60 Opus calls

---

## 7. Source files

| File | Reviewer |
|---|---|
| `reports/reviews/2026-05-17_v0_2_review_bundle_round2.md` | Input bundle (14 KB) |
| `reports/reviews/2026-05-17_gpt-pro_round2_review.md` | ChatGPT Pro (32 KB) |
| `reports/reviews/2026-05-17_codex-council_round2_review.md` | Codex Council (16 KB) |
| `reports/reviews/2026-05-17_gpt-max_round2_review.md` | GPT Max (16 KB) |
| `reports/reviews/2026-05-17_opus_round2_review.md` | Opus 4.7 subagent (47 KB) |
| Per-persona files | `~/claudeworkspace/reports/codex-council/2026-05-17-psycheeval-v02-round2-*/persona-*.md` |

---

## 8. Bottom line

**v0.2 is publishable, but only after the 3-day pre-report hygiene pass.** The Tier 1 findings (with corrections applied) and the methodology contribution (with scoped wording) constitute a defensible report — substantially stronger than the v0.2 plan originally envisioned, because the "failures" of the original C5_CONTRACT pairwise headlines became the load-bearing methodology finding.

The arithmetic errors in the Phase 1 findings doc (§1.2) are the most surprising and most easily-fixed item. The claim ledger architecture (§2.3) is the highest-leverage structural change. The matched-pair bootstrap CI replacement (§1.1) is the canonical-numbers fix everyone wants.

No reviewer believes v0.2 should be paused for new generation experiments. All four converge on the same v0.3 priorities (C_GENERIC_CONTRACT, C4_WRONG_PROFILE) regardless.
