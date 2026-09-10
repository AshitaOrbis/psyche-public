# Fix Manifest — Publication Review Round 2 (delta)

**Date**: 2026-06-17
**Document**: `reports/psycheeval_v0_3_full_pilot_2026-05-19_v03.md`
**Reviewers**: GPT-5.5 (codex), Gemini 3.1 Pro, Opus steelman, GPT Pro (forward-analyst, round-2)
**Consolidated**: `reviews/2026-06-17_consolidated_round2.md`. Full revision diff: `reviews/2026-06-17_report_full_revision.diff`.

The round-2 panel confirmed the gate analyses are numerically correct (codex audit passed) but found the **prose over-promoted Gate 3** — "generation works / bottleneck is evaluation NOT generation" over-reads a single-coder, n=8/cell, 2-way attribution result that partly detects surface contract-echo. All four reviewers converged on this. Corrective pass applied.

## Applied (MUST FIX)

| # | Finding (reviewers) | Action |
|---|---------------------|--------|
| 1 | "Generation works" over-reach (GPT Pro, Opus M1/M2, GPT-5.5 #4, Gemini #3) | Reworded §1 callout, §1 Q2, one-line synthesis, §4.5 table+synthesis, §5, §9, §11: "generation works / target-distinct text" → "outputs are **blind-discriminable** (partly via contract-echo); target-*serving* adaptation is open." Gate 3 = discriminability, not adaptation. Cut "if anything, strengthens." |
| 2 | False dichotomy + §11 "safest summary no longer descriptive" (Opus M2) | "bottleneck is evaluation, NOT generation" → "evaluation is the **clearer** bottleneck; does not clear generation." Rewrote §11; removed the miscalibrated line. |
| 3 | Global-pole = bias vs real-quality unexamined (Opus M3) | Added the benign reading throughout (§1, §4.1, §4.5, §5): global-pole is consistent with a judge bias **or** a real unconditional-quality gap the design cannot distinguish. |
| 4 | "Surface effect" overclaims (point estimate unchanged) (GPT-5.5 #2, Opus S6) | "surface effect"/"surface-explained" → "does not survive surface control / not separable from the formatting it induces"; added the mediator-direction caveat (over-control can manufacture a null). §1, §4.1, §4.3, §4.4 D3, §4.5, §5, §8. |
| 5 | Trigger #7 opus-as-judge confound; 65.6%-averaging scope-mix (GPT Pro, Opus S3, GPT-5.5 #5) | "opus-as-judge effect" → "**opus-judge/gpt-author cell**" everywhere (§1, §4.1, §4.3, §4.5, §5, §6, §8, §11); removed the "65.6% averages 90%/50%" arithmetic; foregrounded the judge/author confound. |
| 6 | Stale references (GPT-5.5 #1/#3, Gemini #1/#2) | Intro line 7 (#7/#8 "open"→run); §4.4 D3 ("trigger #8 must run"→run); §5 line 191 (profile-specific-content-adds-value→contradiction removed); TL;DR Q4 (added opus-cell ladder caveat). |

## Applied (SHOULD FIX)

| # | Finding | Action |
|---|---------|--------|
| 7 | Single-coder n=8 weight at first promotion (Opus S1) | Added "(single-model single-pass, n=8/persona; directional, not a measured rate)" to §1 callout + §4.5 |
| 8 | dario/pawl delta-wrinkle understated (Opus S2) | "all 3 global-pole pairs sign-flip" → "**2 of 3 clean pairs**; dario/pawl confounded by delta-form reconstruction" (§4.5 table) |
| 9 | "matching survives" = same as global-pole (Opus S4) | Added reconciling clause in §1 Q2 + §4.1: the surviving Gate-1 signal IS the Gate-2 global-pole, not a 2nd endorsement |
| 10 | Post-hoc status propagation (Opus S5) | Prepended "(post-hoc, exploratory)" to §5 downgrade bullets; §8 #8 noted as post-hoc mediator-laden |
| 11 | gpt-judge "at chance"→"at/below" (Gemini #4) | §1 callout now "at or below chance" |
| 12 | §4.3 "localizes" too causal (GPT-5.5 #7) | "benefit localizes to contract-first ordering" → "only detected step; mechanism unresolved" (§6 prose) |
| 13 | §9 "shared-stylistic largely confirms" bundling (GPT-5.5 #8) | Split into 3 distinct nulls; noted #7 points *against* cross-model sharedness |
| 14 | §4.1 narrative whiplash (Gemini #5) | Softened unrevised reading to "appears reliable but fragile prior to surface control" |
| 15 | C5_CONTRACT vs C5 gpt_n=16 disclosure (GPT-5.5 #6) | Disclosed in §6 + §8 #7 rows |

## Applied (NICE TO HAVE)
- 93% CI coupling (Opus N1) — noted in §4.5 ("treats 64×2 coupled judgments as independent, so optimistic").
- "25% = ~16 tasks" inline (Opus N2) — §4.5.
- §10 expanded with GPT Pro's cheap existing-data tests (de-echo recovery, target-conditioned re-judging, global-pole-index regression, 2-axis fit-vs-quality).

## Deferred / carried forward
- §8 tally "#1 partial" (Gemini #6) — already present ("#1 is PARTIAL"); no change.
- Full §4.5 provenance table (GPT-5.5 #9) — n/denominators added inline; standalone table deferred (NICE).
- The actual de-echo + target-conditioned-judging analyses (GPT Pro's decisive tests) — these are v0.4 work (§10 #0/#1), not report edits.
- Phase 5 single-rater (trigger #3) — still open.
