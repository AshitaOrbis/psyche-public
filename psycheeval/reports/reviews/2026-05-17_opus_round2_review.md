# PsycheEval v0.2 — Round-2 Independent Review (Opus 4.7)

**Date**: 2026-05-17
**Reviewer**: Opus 4.7 (independent; did not participate in Phase 0 or Phase 1)
**Inputs**: Round-2 bundle, Phase 1 AB/BA findings, Phase 0 findings, round-1 consolidated review, round-1 bundle, autogen scaffold (v02_hard_codex_only), canonical metrics JSON
**Goal**: Find what Phase 0 and Phase 1 missed; flag overclaims; route fixes by tier (block-publication / quick-fix / v0.3)

---

## TL;DR — top-of-report synthesis

The work done since round 1 is substantial and the headline story has materially improved: a publication-blocking dataset has become a publication-shaped dataset *plus* a publishable methodology contribution (judge-family-stratified slot-B bias). The Phase 1 AB/BA was the right experiment to run, and it was executed cleanly.

However, before the v0.2 curated report is written, **four things are not yet safe to publish as currently stated**, and three of those are fixable today on existing data without any new generation. Specifically:

1. **The Tier 1 verdict "C4 > C5 strengthens under AB/BA" (63.7% → 68.9%) is the single weakest Tier 1 finding** and is being mischaracterized. It survives AB/BA, but it (a) is OpenAI-judge-only (Opus n=0 per Phase 0 §0.C), (b) vanishes under length-matching per `length_adjusted_summary_same_author` (full 0.637 → similar 0.522 [0.381, 0.659] in the autogen at line 291), and (c) the Phase 1 findings doc waves this away as "length matching gave a false negative" without justification. There is no positive evidence the length confound is resolved; AB/BA does not control for length. This should be Tier 1.5 at most, with the length caveat surfaced, not buried.

2. **The Wilson CI on the AB/BA `controlled_lo_win_rate` is computed incorrectly** for paired-pair data — it treats each AB/BA-matched pair as a single Bernoulli trial at the rounded controlled rate (`analyze.py:654`), not as a clustered matched-pair statistic. The CIs in the headline AB/BA table are tighter than they should be, possibly by a meaningful amount on the borderline pairs (C3 vs C5_CONTRACT, C4 vs C5_CONTRACT, C4 vs C4_shuffled). This is a same-data analysis fix; ~1 day.

3. **The judge-stratified AB/BA numbers in the Phase 1 findings doc are not in the metrics JSON.** The `ab_ba_position_audit_same_author` block at `metrics:4843` reports only pooled values per pair; the per-judge slot-B table (Phase 1 findings §"Slot B advantage measured per judge") was computed offline and is not auditable from the canonical artifacts. The headline methodology contribution ("judges show ~15–17pp systematic slot-B preference, judge-family-specific") cannot be defended without making this block canonical.

4. **The C5_CONTRACT > C5 mechanism story remains overclaimed in subtle ways.** The package effect (67.7%, robust) is real. But the round-2 bundle's framing — "structured contract repairs unstructured source packet" — is a mechanism claim, not a package claim, and the v0.2 dataset cannot support it without `C_GENERIC_CONTRACT`. The Phase 1 doc §"Strike entirely" gets this right ("which *component* of C5_CONTRACT carries this … remains open"), but the round-2 bundle §5 still calls it "contract repairs source-packet fragility" verbatim. The curated report needs to pick one framing and stick to it.

The other Tier 1 claims (C0 dominated, C4 > C1_padded, C5_CONTRACT > C5, C4 > C4_shuffled with sign-correction) are defensible with the wording in the Phase 1 findings doc, modulo the CI fix.

**Net recommendation**: Spend ~3 person-days on items A.1–A.4 below before opening the report draft. Skip nothing in section B that's marked "blocking." Section C v0.3 priorities follow round-1 reviewer convergence on `C_GENERIC_CONTRACT` and `C4_WRONG_PROFILE`, but I'd add **three** fresh angles round-1 missed (C.4, C.5, C.6).

---

## (A) Issues that would block writing a defensible v0.2 report

These need to be addressed in the report draft or its underlying analysis before publication. Cited file/block/line for every claim.

### A.1 — The C4 > C5 Tier 1 verdict is the weakest Tier 1 and is being mischaracterized [BLOCKING]

**The claim** (Phase 1 findings §"Tier 1 — survives AB/BA", line 78): "C4 > C5 — original 63.7% C4 win rate, controlled estimate: 68.9% C4 wins [61.6, 75.9]. The Phase 0 length-matching 'C4 vs C5 vanishes under length matching' sub-finding *does not replicate under AB/BA*. The AB/BA-controlled estimate is actually *stronger* than the original."

**The problem**: AB/BA does not control for length. The two corrections target different confounds. Length-matching restricts to similar-length response pairs to isolate the condition effect from response-length effects; AB/BA swaps the slot to isolate the condition effect from position effects. These are orthogonal corrections. A pair can survive one and fail the other, and the dataset shows this is exactly what happens for C4 vs C5:

- `length_adjusted_summary_same_author` (autogen line 291): full lo_win 0.637 → similar lo_win 0.522, n_similar=46, CI95 [0.381, 0.659], flagged ⚠ vanishes.
- `ab_ba_position_audit_same_author.C4_vs_C5` (`metrics:4889`): controlled lo_win 0.6813, n=160, CI [0.6055, 0.7485].

The Phase 1 findings doc waves this away — line 77, "the Phase 0 length-matching … does not replicate under AB/BA" — but the only way that sentence is true is if AB/BA *did* control for length, which it doesn't. The AB/BA pool is the full 160-pair set; the length-matched pool is the 46-pair similar-bucket subset. They're not the same evidence.

What you actually have for C4 vs C5:
- Position-controlled, length-uncontrolled: C4 wins 68.9% (Tier 1 strength).
- Length-controlled, position-uncontrolled: C4 wins 52.2% (Tier 2 strength, CI touches 0.5 on either side).
- Position + length controlled: not computed.

**This pair also has zero Opus judge coverage** (`pairwise_by_judge_same_author.C4_vs_C5` shows gpt-5.4 n=80 + gpt-5.5 n=80 in the autogen at lines 429–432; Opus is absent). Round 1 (consolidated review §1.1) and Phase 0 (§0.C verified) both flagged this. The Phase 1 controlled estimate is therefore "OpenAI-judges-only, position-controlled, length-uncontrolled."

**Required fix before publication**: Run the AB/BA controlled estimate *within the similar-length bucket* for C4 vs C5. This is a same-data analysis (no new judging needed for the position correction; you already have 160 AB/BA records for this pair, and you can subset to the length-similar 46-pair bucket using the existing `_length_bucket` field). If the joint correction sustains the C4 advantage, promote to Tier 1; if it collapses, demote to Tier 1.5/2. Cost: <0.5 day.

**Stop-the-press version**: If the joint correction can't be run before report submission, the curated report's C4 > C5 sentence needs explicit "(length-uncontrolled; OpenAI-judges-only)" attribution and the headline should not characterize C4 > C5 as a robust personalization finding. The way the Phase 1 doc currently presents this ("counter to expectation … now firmly Tier 1") materially overclaims.

### A.2 — The Wilson CI on `controlled_lo_win_rate` is mis-specified [BLOCKING]

**Evidence**: `analyze.py:654`:
```python
wci_lo, wci_hi = wilson_interval(round(b["sum_lo_wins_controlled"]), n) if n else (None, None)
```

`sum_lo_wins_controlled` is a sum of per-pair scores in {0.0, 0.25, 0.5, 0.75, 1.0} (each pair gets a controlled lo-share = average of orig + swap lo-scores, where each lo-score is 0/0.5/1). The Wilson interval expects an integer count of Bernoulli successes over independent trials; this code rounds the controlled sum to the nearest integer and then computes Wilson as if n pairs were each one Bernoulli draw. That is wrong on three counts:

1. **Rounding loss**: For C3 vs C5_CONTRACT, `sum_lo_wins_controlled` should be approximately 0.5009 × 288 = 144.26. Rounded to 144, the Wilson CI is computed for (144 successes, 288 trials). The point estimate is the rounded version of the actual controlled rate, which is fine, but…

2. **Variance is wrong**: The Wilson CI on (k = 144, n = 288) computes variance assuming 288 independent Bernoulli trials at p = k/n. But each "trial" here is an AB/BA-matched pair averaged across two judgments. The two judgments are correlated (same judge, same outputs, same scenario, same author, same persona). The effective sample size is lower than n; the variance should be larger. Also, pairs are clustered by persona × scenario × author × judge cell — exactly the cluster unit used elsewhere in the analyzer (`_compute_cluster_bootstrap_pairwise`).

3. **Bound asymmetry**: With paired data, the right test is McNemar-style or a cluster bootstrap on the controlled-rate distribution. The Wilson CI on rounded counts is neither.

**Likely magnitude**: For the borderline pairs (C3 vs C5_CONTRACT, C4 vs C5_CONTRACT, C4 vs C4_shuffled), CIs are probably 10–25% wider than reported. This is precisely the regime where it matters — the Tier 1 verdict on C4 vs C4_shuffled hangs on `[0.523, 0.631]` excluding 0.5; if the corrected CI is `[0.508, 0.648]`, the verdict still holds but it's clearly in the marginal zone, not robust. The Tier 1 verdict on C1_padded vs C4 hangs on `[0.324, 0.429]` excluding 0.5; almost certainly survives any reasonable widening.

**Required fix**: Replace the `wilson_interval(round(sum), n)` call with a cluster bootstrap over the AB/BA pairs (resample pairs with replacement, recompute controlled lo win rate, report the percentile CI). Same `_persona_scenario_author` clustering convention as `_compute_cluster_bootstrap_pairwise`. Drop the Wilson CI or report both side-by-side and flag the Wilson as anti-conservative.

Cost: ~0.5 day. This is gated on publication of any controlled CI.

### A.3 — The judge-stratified AB/BA block is not canonical [BLOCKING for the methodology claim]

**The claim**: Phase 1 findings doc, §"Slot B advantage measured per judge" (lines 97–110), reports per-judge slot-B advantages (gpt-5.4 −0.036 / +0.024 / +0.112 on the three C5_CONTRACT pairs; gpt-5.5 +0.250 / +0.250 / +0.310; Opus +0.233 / +0.238 / +0.094). The standalone methodology contribution in §"New methodology finding worth publishing standalone" (lines 165–175) is built on these numbers.

**The problem**: This block is not in `metrics_2026-04-26_v02_hard_codex_only.json`. I checked `ab_ba_position_audit_same_author` (`metrics:4843` and following): it has pooled per-pair values only. There is no `ab_ba_by_judge` or analogous stratification. The autogen scaffold (line 193 onward) shows only the pooled AB/BA block; no per-judge breakdown rendered.

This means the headline methodology claim is not reproducible from the canonical artifact. A reader of the curated report cannot verify the claim that "gpt-5.5 has +25–31 pp slot-B preference" by re-running the analyzer; they'd have to dig in raw JSONL and trust an offline calculation.

**Three secondary problems** in the per-judge numbers as presented:

1. The Phase 1 doc claims "gpt-5.4 has essentially no slot-B preference on the C3 and C4 pairs" (line 105). But the same doc reports gpt-5.4 slot-B on C5 vs C5_CONTRACT at +0.112 — non-trivial. The "essentially no" claim doesn't generalize to all C5_CONTRACT pairs, only two of three.

2. The number of AB/BA records per judge per pair is in `pairwise_by_judge_same_author` originals (e.g., C3 vs C5_CONTRACT: gpt-5.4 n=84, gpt-5.5 n=84, Opus n=115 per autogen line 415–418). After AB/BA, the doc says gpt-5.4=84, gpt-5.5=84, Opus=87 (with 38 pending) for C3 vs C5_CONTRACT. **Opus AB/BA n is 87 not 115** — meaning Opus AB/BA has 28 fewer matched pairs than originals would allow. Why are 28 Opus C3-vs-C5_CONTRACT originals not AB/BA-matched? This needs explanation in the curated report or fixing by running the missing 28 swaps. If unrunnable, the Opus slot-B estimate on this pair is on a non-random subset of Opus originals, which is its own confound. (Same applies to C4 vs C5_CONTRACT: Opus AB/BA n=85, original n=117 — 32 missing.)

3. The Phase 1 doc never explains the **sign** of position bias. The convention is that slot B is favored. But for C3 vs C5_CONTRACT under gpt-5.4, the per-judge advantage is −0.036 (i.e., slot A favored). The phrase "slot-B advantage" with a negative sign is confusing. The methodology contribution paper needs explicit definition: "slot-B advantage = swap_lo_win − orig_lo_win, where C5_CONTRACT was slot B in originals; positive = slot B favored = bias toward later position."

**Required fix**: Add `ab_ba_position_audit_same_author_by_judge` block to the analyzer (~0.5 day). Render per-judge per-pair slot-B advantage with CIs. Either complete the missing Opus AB/BA records (~70 Opus calls if you want full coverage; or document the missingness pattern and stratify) or apply Opus only to its AB/BA-matched subset.

### A.4 — "C5_CONTRACT > C5" framing oscillates between package and mechanism [BLOCKING wording]

**Evidence**:
- Round-2 bundle §5 Tier 1 row 4: "Survives all 12 Phase 0 + AB/BA. Judge-unanimous. Scalar-aligned." → presented as the surviving substantive finding without mechanism framing.
- Round-2 bundle §6.A first asks: "Should we publish at all without `C_GENERIC_CONTRACT` ablation?" — implicit acknowledgment that mechanism is not settled.
- Phase 1 findings doc, §"Strike entirely" (line 153): "the question of *which* component of C5_CONTRACT carries this — contract presence, contract-first ordering, anti-mimicry language, source-packet form, or response-length — remains open."
- Phase 1 findings doc, §"Headline" (line 17): "C5_CONTRACT > C5 is the only C5_CONTRACT pairwise headline that survives position-controlled rejudging." ← framed as the headline.
- Phase 1 findings doc, §"Tier 1 — survives AB/BA" (line 79): C5 vs C5_CONTRACT "controlled estimate: 67.7% C5_CONTRACT wins. Substantial real condition preference. **The contract-repairs-source-packet phenomenon is robust to position bias.**" ← that last sentence is a mechanism claim. Position-bias-robustness ≠ mechanism evidence.

**The problem**: The dataset can support exactly one claim about this pair, which is the **package** claim: "When the source packet is paired with a behavioral contract (whether the contract is doing the work, or the contract-first ordering, or the anti-mimicry override, or the additional ~3,549 chars of profile text, or some interaction of these), the package wins decisively over the source-packet-alone condition, judge-unanimously, scalar-aligned, position-controlled." It cannot support "contract repairs source packet" because that's mechanism, and `C5` differs from `C5_CONTRACT` on at least four dimensions simultaneously (contract presence, ordering, anti-mimicry language, response-conditioning structure — and possibly response length downstream).

Round-1 GPT Pro got this right (consolidated review §1.5): "v0.2 shows source-packet-with-contract beats source-packet-without-contract; it does not isolate public-anchor, packet form, profile length, generic-contract uplift, or judge/rubric recognition." The Phase 0/1 work hasn't changed this. AB/BA doesn't change this. The robust effect is real; the mechanism is unsettled.

**Required fix**: Pick one of two paths and apply consistently:

- **Conservative path**: All references to C5_CONTRACT > C5 in the curated report use the form "the contract-supplemented source-packet package outperforms the bare source-packet" or similar. No "contract repairs packet" language. Add an explicit "Mechanism not isolated; ablations deferred to v0.3" subsection.
- **Aggressive path**: Run a minimal `C_GENERIC_CONTRACT` pilot (~80 PI generations × 3 authors = 240 outputs + judging) before publishing. This is the round-1 unanimous v0.3 priority anyway; pulling it forward unlocks a real mechanism claim. Cost is in the budget envelope (~150–200 Opus + larger codex).

I lean toward the conservative path for v0.2 (preserves publication velocity) and recommend `C_GENERIC_CONTRACT` as the lead v0.3 experiment regardless.

### A.5 — The C3 vs C5_CONTRACT cross-provider stratified finding should be downgraded, not held

**The contradiction** (round-2 bundle §6.A bullet 3, framed as an open question):
- All-judge AB/BA-controlled estimate: C5_CONTRACT wins 49.9% [44.3, 55.7] → no preference. (`metrics:4859`)
- Cross-provider stratified cluster-bootstrap: C3 wins [0.238, 0.446] → C5_CONTRACT wins ~58.4% with CI [55.4, 76.2]. (`metrics:cluster_bootstrap_ci_cross_provider_same_author`, autogen line 701)

**Phase 1's explanation** (line 110): "gpt-5.4 was the cross-provider judge for Opus-authored cells and has no position bias." So the cross-provider effect = gpt-5.4 effect on Opus-authored cells. Reasonable interpretation.

**Why I'd downgrade, not hold or report both**: The cross-provider window is n=85 on this pair — small, and entirely confounded with "gpt-5.4 judging Opus-authored outputs." If gpt-5.4 has no position bias *and* has a real condition preference for C5_CONTRACT on this subset, that's actually a positive signal; if instead gpt-5.4 has a tilt for Opus-authored outputs (orthogonal to condition), it's a different story. The current dataset can't tell which.

Worse, n=85 cross-provider isn't enough for a confident headline. The Phase 0 §0.A flagged this finding as "this nuance was not in any reviewer's original critique" — but it's a finding that emerges only after combining (a) a small cross-provider subset, (b) a particular author family, (c) a particular judge family, (d) a stratification choice. Each level of this conditioning halves your sample.

**Required fix**: Report the cross-provider finding as a hypothesis (one sentence in robustness section), not as a finding. Specifically: "Within the small cross-provider subset (n=85), the C3 vs C5_CONTRACT comparison nominally favors C5_CONTRACT (CI [0.238, 0.446]), but this is concentrated entirely in gpt-5.4 judging Opus-authored outputs, where slot-B bias is absent; the all-judge AB/BA-controlled estimate is at chance, and the cross-provider signal is observationally indistinguishable from a judge-author-family interaction."

Do not lead with this; do not treat it as Tier 1 evidence; do not strike it (it's a real subset and the autogen renders it).

### A.6 — Selection bias in scalar pooling is acknowledged but not corrected

**The finding** (Phase 0 §0.K, autogen `missingness_balance_audit`): Only 67.5% of outputs were scored by all 3 judges. Complete-case n = 1,134 / 1,680.

**The Phase 0 §"Implications" §"Add as new findings" (line 131)**: "The complete-case scalar table as a robustness check."

**What's in the autogen**: The Phase 0 doc says to add a complete-case scalar table; I don't see one rendered in the autogen. The `missingness_balance_audit` block exists in the metrics JSON but the report-side complete-case scalar means are not present. The Tier 1 scalar finding ("C5_CONTRACT scalar Δ_total +3.057 aligned with pairwise 76.8%", Phase 0 §0.B) lives on the full pool, not the complete-case pool. If missingness is concentrated in cells that disadvantage C5 vs C5_CONTRACT (e.g., judges fail/timeout more on certain conditions), the +3.057 delta could be inflated.

**Required fix**: Add a `scalar_means_complete_case` table to the autogen and confirm Δ_total holds on complete cases. If it does, this is a single supporting paragraph in the report. If it doesn't, the C5 vs C5_CONTRACT scalar headline needs caveating. Cost: <0.5 day.

### A.7 — One Phase 0 audit that should have been run but wasn't: persona-author interaction

**Evidence**: `pairwise_by_persona_same_author` exists (autogen line 527 onward). `pairwise_by_author_same_author` exists (line 450). But persona × author interaction does not.

Why this matters: Phase 0 §0.C verified that "Slalom Altar persona reverses C4 vs C5_CONTRACT to 0.657" (autogen line 634). It also showed the leave-one-author-out fragility table: `metrics:leave_one_author_out_fragility` only flags C4 vs C4_shuffled and C5 vs C5_CONTRACT, suggesting the C5_CONTRACT-edge effects are author-robust at the aggregate level.

But what if the author × persona interaction is concentrated? Specifically: does Opus-authored Slalom Altar reverse C4 vs C5_CONTRACT more strongly than GPT-authored Slalom Altar? If yes, the C5_CONTRACT effect on this persona could be carrier-author-specific, which has implications for generalization. The Phase 0 audit pass added per-author and per-persona but not the cross-tabulation.

**Required fix**: Add `pairwise_by_persona_x_author_same_author` block (~0.25 day analyzer). Use 8 personas × 3 authors = 24 cells per pair; report top-3 most extreme cells per pair. If Slalom Altar × Opus is the outlier, it's a defensible footnote; if Slalom Altar × all three authors reverses, it's a story about scenario set construction for this persona.

This is the single Phase 0 audit I would prioritize over net-new generation experiments.

---

## (B) Quick fixes before v0.2 report writing (<1 day each)

These are runnable on existing data and produce concrete additions to the curated report.

### B.1 — Joint length × position correction for C4 vs C5 [blocking, see A.1]

Same-data analysis. Restrict AB/BA-matched pairs to similar-length bucket. Recompute controlled lo_win + cluster bootstrap CI. Likely answer: somewhere between 0.52 (length-only) and 0.68 (AB/BA-only). If the joint estimate's CI includes 0.5, the Tier 1 verdict on this pair needs demotion. Cost: ~0.5 day.

### B.2 — Cluster bootstrap CI on AB/BA controlled rates [blocking, see A.2]

Replace the rounded-Wilson trick with a proper cluster bootstrap over (persona, scenario, author) units for the AB/BA-matched subset. Apply to all 6 headline pairs. Cost: ~0.5 day.

### B.3 — Add judge-stratified AB/BA to metrics + autogen [blocking, see A.3]

`_compute_ab_ba_position_audit_by_judge` analyzer block. Per-pair × per-judge: original lo_win, swapped lo_win, controlled lo_win, slot-B advantage delta, Wilson or cluster-bootstrap CI. Render per-pair sub-table in autogen. This is also what makes the standalone methodology contribution publishable. Cost: ~0.5 day.

### B.4 — Complete-case scalar table [should-fix, see A.6]

Filter `anchored_scores` to outputs scored by all 3 judges (n=1,134). Recompute the §5 scalar means table on this subset. Place side-by-side with the full-pool table. Cost: <0.25 day.

### B.5 — Persona × author cross-tabulation [should-fix, see A.7]

`pairwise_by_persona_x_author_same_author` block. Cost: <0.5 day.

### B.6 — Move scalar-pairwise reconciliation up in the report

This is currently in the autogen at line 645. For the curated report, it should be in the front matter / methodology section, because GPT Pro's discovery — that pairwise judges and anchored rubric judges can systematically disagree — is itself a major v0.2 methodology contribution alongside the slot-B bias finding. Treat it as a peer of the slot-B finding, not a footnote.

### B.7 — Pre-register Tier 1 vs Tier 2 evidence requirements in the curated report

Round-1 reviewers (consolidated §6) and Phase 1 findings doc both use Tier 1/2/3 language but with implicit criteria. The curated report should state criteria explicitly, e.g.:

- **Tier 1**: All of {(i) position-controlled CI excludes 0.5 on the same side as the original; (ii) length-matched CI excludes 0.5 on the same side OR no length confound is detected for the pair; (iii) sign-agreement with scalar Δ on the relevant dimension(s); (iv) judge-unanimous direction; (v) survives all four leave-one-out fragility checks}.
- **Tier 2**: Position-controlled CI fails (i), OR length-matched CI fails (ii), OR fewer than 2 judges agree direction.
- **Tier 3 / mechanism**: Requires ablation evidence (not present in v0.2).

Under this rubric, C4 > C5 fails (ii) and would not be Tier 1. C5_CONTRACT > C5 passes all five and is the canonical Tier 1. C4 > C1_padded passes; C4 > C4_shuffled is borderline on (v) given the leave-one-judge-out flips it (autogen line 341: "−gpt-5.4 → 0.438, `flips`"). This rubric makes the tier assignment defensible and reproducible.

### B.8 — Fix labeling that's still stale

The autogen at line 14 still says "Pairwise results (cross-provider judged)" as a section header, even though we now know most of the same-author pairwise is same-provider, not cross-provider. Round 1 §1.1 flagged this; the Phase 0 audits surfaced it; but the autogen section header itself appears not to have been updated. (I haven't traced all the headers; spot-check first.)

Similarly, the autogen line 16 has `### Counts` and line 26 has `### Condition win-rate (same-author pairs, cross-provider judged)`. If `same-author pairs, cross-provider judged` is the all-judge same-author scope (n=2,944), the label is wrong — that's the all-judge scope. The cross-provider scope is n=264. Either rename the section to "same-author, all-judge" or stratify the table to show all three scopes.

### B.9 — Forest-plot family-level reversals: report n's, not just point estimates

The scenario-family forest plot (autogen line 709) flags strict reversals (CI excludes 0.5) and point reversals separately, which is good. But on the C5 vs C5_CONTRACT pair — the Tier 1 finding — every family lo_win is ≤ 0.357 (autogen line 832–842). The point estimates are tightly clustered (0.125 to 0.357). This is unusually strong family-robustness and deserves a positive callout in the curated report, not just absence of ⚠. Concrete reversal-rate metric to report: % of families × pairs where the family-level lo_win agrees with the pooled lo_win direction. For C5 vs C5_CONTRACT this should be 8/8.

### B.10 — Quantify and report the position_flip_rate against a null

The `position_flip_rate` (autogen AB/BA table) ranges from 0.138 (C4 vs C5) to 0.330 (C3 vs C5_CONTRACT). Under "no condition preference, slot-B bias = p", flip rate would be roughly 2p(1-p). For p ≈ 0.16 (the average slot-B advantage), expected flip rate is ~0.27. The C3 vs C5_CONTRACT flip rate of 0.330 *exceeds* the bias-only prediction — meaning there's additional noise beyond pure side preference. The C4 vs C5 flip rate of 0.138 is *below* the bias-only prediction (because the condition preference is strong and flips happen mostly on near-ties). Reporting flip rate against this null clarifies which pairs are "real preference + bias" vs "bias-only + noise." Cost: trivial; framing matters.

---

## (C) v0.3 questions — including angles round 1 missed

Round 1's convergence on `C_GENERIC_CONTRACT`, `C4_WRONG_PROFILE`, `C5_NONPUBLIC`, paraphrased rubric, human calibration, and real-user shadow validation is well-aimed. I'd ratify all of those. Below: three angles round 1 didn't surface and one round-1 angle that needs reshaping.

### C.1 — Add: judge-rubric jailbreak / paraphrase as a primary v0.3 axis [round 1 named, not centered]

Round 1 named this (rank 5 in §3.2), but I'd promote it to a co-equal of `C_GENERIC_CONTRACT`. The slot-B bias finding from Phase 1 is *itself* the existence proof that judge architecture is load-bearing on the headline findings. If position changes the answer by 16pp, what does:

- Paraphrasing the rubric anchors do?
- Using a different rubric (safety-first vs personalization-first vs epistemic-first) do?
- Asking the judge to ignore verbosity unless it improves substance do?
- Showing the judge a "blind" version (no condition labels in the prompt)?
- Reducing the judge to 0-shot binary "which is better and why in 30 words" without the anchored scale?

Round 1 had this as a rank-5 affordable experiment. After Phase 1, the methodology contribution is larger than the substantive contribution, and the methodology contribution is judge-architecture-shaped. Run this in v0.3 alongside `C_GENERIC_CONTRACT`.

Cost: existing 1,680 outputs × 5 rubric variants × 1–2 judges = ~3,000–6,000 additional judge calls (codex-heavy).

### C.2 — New angle: same-judge intra-rater reliability (judge re-judging the same pair)

**Round 1 missed**: nobody asked what gpt-5.5's slot-B bias *is* — is it a stable systematic preference, or does it appear because gpt-5.5 makes near-random calls on these pairs and the side-preference is the tie-breaker?

Quick experiment: take 100 same-author pairs already judged by gpt-5.5, ask gpt-5.5 to re-judge the SAME pair with the SAME slot order. If intra-rater reliability is ~95%, slot-B preference is a stable systematic preference. If intra-rater reliability is ~60%, gpt-5.5's pairwise channel is half noise and slot-B is the tie-breaker.

This is diagnostic for v0.3 because if intra-rater reliability is low, the right intervention is "vote of 3 repeated judgments per pair" rather than "control for position bias". The C5_CONTRACT > C5 effect at 67.7% might survive position control but reflect a noise floor that ensemble voting could push above 90%.

Cost: 100 codex calls. Trivial.

### C.3 — New angle: scenarios written *blind* to profile theory

**Round 1 surfaced this** (GPT Pro §C12, "scenario construction bias"): "if scenarios were written with profile-relevant behavior in mind, profile conditions may get an artificial advantage." But the round-1 review treated this as a v3 concern. After Phase 1, this should be a v0.3 concern.

Reason: the slot-B bias finding tells us LLM judges have systematic preferences that interact with input structure. If scenarios are also constructed with profile-relevant cues, profile-conditioned outputs may match cue patterns the judges are tuned to. The cleanest test is: take 20 scenarios written purely from user-task generators (e.g., from logs of actual help requests, anonymized), score them under all 8 conditions × 8 personas, and check whether the C4 > C1_padded effect survives.

Cost: 20 new scenarios × 8 personas × 8 conditions (or subset) = 160–1,280 generations. The lower bound is in budget; the upper bound exceeds it. Pilot with 20 scenarios × 4 personas × 4 conditions = 320 generations to scope.

### C.4 — New angle: response-length budget control as a generation-side condition

**Round 1 named this** (rank 6 in §3.2: `C5_CONTRACT_SHORT`), but the framing was limited to C5_CONTRACT. The Phase 0 length-matching findings + the autogen `length_adjusted_summary_same_author` table reveal length confounds on multiple pairs:

- C1_padded vs C4: Δ_similar−full = −0.133 (C4 attenuated under length matching)
- C1 vs C1_padded: Δ = −0.154 (large attenuation)
- C1 vs C4: Δ = −0.123 (attenuation)
- C4 vs C5: Δ = −0.116 (attenuation, flagged ⚠ vanishes)

The C4 > C1_padded headline — the most-defensible round-1 finding — *also attenuates by 13 pp under length matching* (0.681 → 0.814 hi-win when the responses are similar length; effectively still excludes 0.5 but the effect size halves). This pattern across multiple pairs suggests response length is an under-controlled variable across the entire v0.2 corpus.

v0.3 should generate with explicit response-length budgets per condition (`max_tokens` matched, or instructed length matched). Otherwise every pairwise finding is partly a length finding.

Cost: re-generate ~20% of corpus with length-budget constraints. Codex-heavy.

### C.5 — New angle: which dimensions of the anchored rubric carry the C5_CONTRACT > C5 effect?

**Round 1 surfaced this** at the structural level (downweight `profile_fit`, §3.1 #13) but not as a positive analysis. The scalar Δ_total of +3.057 for C5 vs C5_CONTRACT (across 10 dimensions) doesn't tell us if the effect is concentrated in 2 dimensions or distributed across all 10. If it's concentrated in `profile_fit` and `helpfulness` while dimensions like `boundary_respect` and `non_carrying` are flat, the effect is partly tautological (C5_CONTRACT's contract explicitly instructs profile-fit and helpfulness behaviors; the rubric measures them; the judge rewards them).

This is a same-data analysis but should be the headline mechanism slice of the v0.3 report: which dimensions does C5_CONTRACT actually move? If 8/10 dimensions move, it's a quality story; if 2/10 dimensions move, it's a "rubric-prompt alignment" story.

I checked `scalar_pairwise_reconciliation_same_author.C5_vs_C5_CONTRACT` (autogen line 660): `Δ_total = +3.057, sign_agree = 0.794`. The per-dimension breakdown isn't in the autogen but should be straightforward to add. Cost: trivial analyzer extension.

### C.6 — Reshape round-1's `C4_WRONG_PROFILE` test

Round 1 framed `C4_WRONG_PROFILE` as the profile-specificity test: "If C4_WRONG_PROFILE ≈ C4_RIGHT → profile-matching is doing little user-specific work." This is correct but not rigorous enough. The cleaner design is:

- C4 (right profile) — current
- C4_WRONG_RANDOM (random other persona's profile)
- C4_WRONG_OPPOSITE (a profile that flips the load-bearing trait — e.g., if the right persona is high-agency, wrong = low-agency)

If C4_RIGHT > C4_WRONG_OPPOSITE >> C4_WRONG_RANDOM ≈ C0, profile specificity is real and the relevant trait is identifiable. If C4_RIGHT ≈ C4_WRONG_OPPOSITE ≈ C4_WRONG_RANDOM, it's a generic-prompting story. The opposite-trait variant is more diagnostic than the random variant alone.

Cost: same as round-1's plan plus an additional 80 generations × 3 authors = 240 more. Worth it.

---

## (D) Direct flaws / overclaims spotted that round 1 didn't pick up

### D.1 — Round 1 was lenient on "C0 dominated"

All three round-1 reviewers and the Phase 0 doc list "C0 dominated by all profile conditions" as Tier 1 with 86.6% C4-over-C0 effect size and treat it as uncontroversial. The autogen scenario-family forest plot for C0 vs C4 (line 713) shows lo_win 0.062 to 0.250 across all 8 families — uniformly C4-dominating. That's right; this finding is robust.

But the result is uninteresting *as a personalization claim*. C4 includes a behavioral contract (anti-sycophancy, agency-preservation, calibrated-challenge instructions). C0 is bare. So "C4 beats C0" is "any behavioral contract beats no behavioral contract." That's a result about behavioral contracts in general, not about Psyche-derived profiles. Round 1 should have flagged this as a Tier 1 finding that is *not* a Tier 1 finding about Psyche specifically. The curated report should either:

- Frame "C0 dominated" as the floor-effect baseline establishing that *something in the structured conditions* moves outputs (true and worth saying), without claiming it as personalization evidence.
- OR drop it from the Tier 1 list because every reviewer treats it as already-known.

Currently the round-2 bundle §5 lists it as the leading Tier 1 finding. That's load-bearing for the personalization narrative in a way it shouldn't be.

### D.2 — The "tri-model" framing leaks back in

Round 1 §1.1 explicitly flagged "tri-model cross-provider" framing as a publication blocker. The Phase 1 findings doc fixed most of this. But the round-2 bundle §1 still says "8 personas × 80 scenarios × 3 authors (GPT-5.4, GPT-5.5-xhigh, Opus 4.7) × varying conditions (C0–C5_CONTRACT) = 1,680 assistant outputs. 3 judges (same models, openai + anthropic provider families)." This is a 1-line summary, which is fine — but the implication is that all 1,680 outputs are judged by all 3 judges, which is what the missingness audit shows is NOT the case (only 67.5% complete). The summary should say "3 judges (incomplete tri-model coverage; 67.5% of outputs scored by all three)."

### D.3 — The Tier 1 verdict on C4 > C4_shuffled is not as clean as presented

**Phase 1 doc (line 89–91)**: "controlled estimate 57.8% C4 wins [52.3, 63.1]. The original was understating the effect because slot-A bias (which penalized C4 in slot A) was suppressing the apparent margin. Once counterbalanced, the C4 advantage becomes clear and the CI excludes 0.5 on the C4-favored side." Then: "**This is a sign-correction of the Phase 0 finding**, not a flip."

Yes, technically not a flip (51.9 → 57.8 are both lo_win > 0.5; lo = C4 here). But:
- C4 was *not* always in slot A on this pair: `A/B side audit` (autogen line 322): "C4_vs_C4_shuffled: 0.988 slot A is lo" — i.e., C4 was in slot A 98.8% of the time, not 100%. Small caveat.
- Leave-one-judge-out (autogen line 341–342): without gpt-5.4, lo_win = 0.438 (flips!); without gpt-5.5, lo_win = 0.600. The pair is judge-divided. This is verified in Phase 0 §"new finding #12" (line 85: "C4 vs C4_shuffled is wildly judge-divided").
- Persona-out for slalom_altar flips it (autogen line 358): "C4_vs_C4_shuffled, −user_pfi_slalom_altar_001, loo lo_win 0.489, `flips`".
- Family-out for epistemic_uncertainty flips it (autogen line 370): "loo lo_win 0.490, `flips`".

So: position-controlled estimate excludes 0.5, but the pair fails (v) of the Tier 1 rubric I proposed in B.7. Three different LOO perturbations flip the direction. The "Tier 1.5" framing in the Phase 1 findings doc (line 91) is more honest than the "Tier 1" framing in the round-2 bundle §5.

**Required fix**: Demote to Tier 1.5 / "directional but fragile" with explicit listing of the LOO flips.

### D.4 — The headline "C5_CONTRACT > C5: 67.7%" carries hidden author imbalance

**Evidence**: `pairwise_by_author_same_author.C5_vs_C5_CONTRACT` (autogen line 519): there's no row visible in my read at line 519 onward — let me check what's there... (I see "C5 vs C5_CONTRACT" header at 519 but content cut off in my reading window). What I observed in `pairwise_by_judge_same_author.C5_vs_C5_CONTRACT` (autogen line 444–447): gpt-5.4 n=84, gpt-5.5 n=84, opus n=119. The Opus pool is 35 records larger than each codex pool — because Opus C5_CONTRACT pairwise had higher coverage (the same path that produced the cross-author leak).

If the AB/BA-matched subset under-samples Opus (Opus AB/BA n=120 vs original n=119 → fine for this pair), the controlled estimate is well-supported. **For C3 vs C5_CONTRACT and C4 vs C5_CONTRACT**, however, Opus original n=115/117 and Opus AB/BA n=87/85 (per Phase 1 §"Tier A budget actually consumed", line 44). That's a 24% / 27% Opus under-coverage on AB/BA for those two pairs.

The C3 / C4 vs C5_CONTRACT verdicts (collapse) are not load-bearing on this — collapses are conservative. But the *pattern* of Opus under-coverage exactly on the C5_CONTRACT pairs where the per-judge slot-B advantage is large (Opus +0.233 / +0.238) means the controlled-rate estimate is computed on a sample where Opus is slightly under-represented. This biases the controlled estimate toward *more* attenuation than would otherwise be measured. In other words: if we'd completed the missing 28 + 32 Opus AB/BA cells, C3 and C4 vs C5_CONTRACT might collapse *more*, not less. That's the conservative direction — fine. But the report should not say "C3 vs C5_CONTRACT controlled estimate 49.9%" without noting "Opus AB/BA coverage incomplete on this pair (87/115 = 76%)."

### D.5 — The Phase 1 doc's "Wrong prediction" section is informative but should be in the curated report

Phase 1 findings doc, §"Option B (DONE)" (line 196–203): explicitly enumerates which predictions the analysis got right and wrong. This is unusually honest and methodologically valuable — but the curated report doesn't have a "what we predicted vs what we found" subsection. It should. Specifically the prediction failures:

- "C4 vs C5: prediction was 'still favors C4 (~56%)' — **wrong**. Actually 68.9% C4 wins, *stronger* than original."
- "The simple '+0.16 correction' estimator was too crude for the non-C5_CONTRACT pairs."

These belong in the methodology section as a "limits of our position-bias correction" subsection. The reader learns more from this than from a clean tier table.

### D.6 — Tie handling under AB/BA is underspecified

The `_compute_ab_ba_position_audit` code (lines 571–576) classifies (orig=tie OR swap=tie) → `either_tie`. The position-controlled lo score (line 619–625) gives ties 0.5. So ties are counted as half-credit for lo in the controlled estimate, but ties are excluded from the consistency/flip classification. This is two different tie conventions in the same block. Which one drives the headline rate?

For C3 vs C5_CONTRACT: n_position_consistent=186, n_position_flip=95, n_either_tie=7 (from `metrics:4859`). Controlled lo win = 0.5009. The 7 either-tie pairs contribute 7 × 0.5 = 3.5 to the controlled sum; 281 decisive pairs contribute the rest. If you redefined controlled lo win = lo_wins / (lo_wins + hi_wins) excluding ties, you'd get a slightly different number. The Phase 1 doc doesn't say which convention is reported. For sub-1% effects, this matters.

**Required fix**: The curated report should clearly state the controlled lo win rate convention (include ties as 0.5 vs exclude ties from denominator) and report both for transparency. Cost: <0.1 day.

---

## (E) Net recommendations, ranked

| # | Action | Tier | Cost | Section |
|---|---|---|---|---|
| 1 | Run joint length × position correction for C4 vs C5; demote if joint CI includes 0.5 | Blocking | 0.5d | A.1, B.1 |
| 2 | Replace Wilson CI with cluster bootstrap on AB/BA controlled rates | Blocking | 0.5d | A.2, B.2 |
| 3 | Add per-judge AB/BA block to canonical metrics + autogen | Blocking | 0.5d | A.3, B.3 |
| 4 | Choose consistent C5_CONTRACT > C5 framing (package not mechanism) throughout the report | Blocking | 0.1d | A.4 |
| 5 | Pre-register Tier 1 criteria explicitly in the report; re-tier under those criteria | Blocking | 0.25d | B.7 |
| 6 | Fix stale "cross-provider judged" autogen labels | Blocking | 0.1d | B.8, D.2 |
| 7 | Add complete-case scalar table | Should-fix | 0.25d | A.6, B.4 |
| 8 | Add persona × author cross-tabulation | Should-fix | 0.5d | A.7, B.5 |
| 9 | Demote C4 > C4_shuffled to Tier 1.5 (LOO-fragile) | Should-fix | 0.1d | D.3 |
| 10 | Caveat Opus AB/BA under-coverage on C3/C4 vs C5_CONTRACT (or run the missing ~60 Opus swaps) | Should-fix | 0.1d / 1d | D.4 |
| 11 | Add "predictions vs findings" subsection | Should-fix | 0.25d | D.5 |
| 12 | Specify tie convention for controlled lo win rate | Should-fix | 0.1d | D.6 |
| 13 | Report position_flip_rate against bias-only null | Nice-to-have | 0.1d | B.10 |
| 14 | Reframe "C0 dominated" as floor effect, not personalization evidence | Nice-to-have | 0.1d | D.1 |
| 15 | Move scalar-pairwise reconciliation to methodology front matter | Nice-to-have | 0.25d | B.6 |

Items 1–6 are the blocking set. Total ~2 person-days. Items 7–12 strengthen the report but are not blockers. Items 13–15 are framing improvements.

**For v0.3**, my ranked priority list is:

1. `C_GENERIC_CONTRACT` (round-1 consensus; most diagnostic single experiment).
2. Judge-rubric jailbreak / paraphrase variants (C.1; comes for free with existing outputs).
3. Same-judge intra-rater reliability (C.2; trivially cheap, diagnostic for whether to ensemble vs control).
4. `C4_WRONG_OPPOSITE` (C.6 reshaping of round-1's `C4_WRONG_PROFILE`).
5. Per-dimension scalar decomposition of C5_CONTRACT > C5 (C.5; same-data, diagnostic for mechanism vs rubric-prompt alignment).
6. Blind-scenario validation (C.3; bounded pilot).
7. Length-budget-matched generation (C.4; partly addresses A.1 if not fixed in v0.2).

`C5_NONPUBLIC` and `C4_WRONG_PROFILE` (random variant) drop in priority slightly relative to round 1, because the data-side question of *what* the C5_CONTRACT > C5 effect actually is (mechanism vs package vs rubric alignment) is more diagnostic of project framing than the public/non-public distinction.

Human-rater calibration belongs in a separate program (round 1's consensus position).

---

## (F) One final structural concern

Round 1 + Phase 0 + Phase 1 has been a 3-iteration loop of finding-and-fixing. The dataset is in much better shape than it was 4 days ago. But every iteration of audit-on-existing-data has the same pathology: it can only catch the kinds of issues that *show up* in the existing data. Three things the audit-on-existing-data loop *cannot* catch:

1. **Anything about the scenarios.** If the 80 scenarios systematically favor profile-conditioned outputs (round-1 GPT Pro C12), no amount of post-hoc analysis fixes it. A blind-scenario pilot (C.3) is the only way.

2. **Anything about the rubric.** The anchored rubric is itself a normative claim. If the rubric anchors phrase "good response" in ways that line up with the contract's instructions (e.g., "acknowledges agency" appears in both), the rubric-prompt halo means contract-conditioned outputs win on the rubric tautologically. Phase 0 §0.J found low lexical overlap (0.063 Jaccard for C5_CONTRACT), but lexical overlap ≠ semantic alignment. A paraphrased-anchor rerun (C.1) is the only way.

3. **Anything about the judges.** The slot-B finding is a positive demonstration that LLM judges have systematic preferences that propagate to the headline. Two more judges from two more provider families (e.g., Gemini, DeepSeek) is the only way to check whether the finding generalizes or is OpenAI+Anthropic-specific.

For the v0.2 report, items 1–3 above should explicitly appear in the "Limitations and v0.3 work" section as **what the v0.2 dataset *cannot* answer no matter how it's reanalyzed**. This is honest, sets up v0.3 as a positive program rather than a fix-list, and forecloses post-publication critique that the v0.2 paper "should have" addressed these on the same data.

---

## Citations / paths used

- `reports/reviews/2026-05-17_v0_2_review_bundle_round2.md`
- `reports/reviews/2026-05-16_phase1_ab_ba_findings.md`
- `reports/archive/2026-05-15_pre-labeling-fix/PHASE0_FINDINGS.md`
- `reports/reviews/2026-05-15_consolidated_v0_2_review.md`
- `reports/reviews/2026-05-15_v0_2_review_bundle.md`
- `reports/psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md` (lines 14, 16, 26, 193–208, 291, 322, 341–342, 358, 370, 415–418, 429–432, 444–447, 596–603, 631–634, 645–662, 701, 832–842)
- `reports/metrics_2026-04-26_v02_hard_codex_only.json` keys: `pairwise.ab_ba_position_audit_same_author` (4843), `cluster_bootstrap_ci_cross_provider_same_author`, `missingness_balance_audit`, `length_adjusted_summary_same_author`, `pairwise_by_judge_same_author`, `pairwise_by_persona_same_author`, `leave_one_judge_out_fragility`, `leave_one_author_out_fragility`, `scalar_pairwise_reconciliation_same_author`
- `src/psycheeval/analyze.py:504–675` (`_compute_ab_ba_position_audit`), 2480–2520 (probe filter), 2799–2845 (scope assembly), 2925–2942 (AB/BA invocation)

— Opus 4.7, 2026-05-17
