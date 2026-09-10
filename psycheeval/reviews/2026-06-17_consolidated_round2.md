# Publication Review — Consolidated Round 2 (delta, gate-driven revision)

**Date**: 2026-06-17
**Document**: `reports/psycheeval_v0_3_full_pilot_2026-05-19_v03.md` (gate battery revision)
**Reviewers**: GPT-5.5 xhigh (codex), Gemini 3.1 Pro, Opus (steelman agent), **+ GPT Pro (GPT-5.5 Pro)** forward-analyst (round-2 response recovered from DOM)
**Convergence**: NOT converged — 1 unanimous MUST FIX cluster (all 4 reviewers) + 5 MUST FIX. The gate analyses themselves are confirmed correct (codex numeric audit passed); the issue is **over-promotion of Gate 3 in the prose**.

**Headline cross-reviewer signal**: all four independently flag that the revision over-reads Gate 3 — the 93% blind recovery establishes **discriminability** (partly via surface contract-echo), **not** behavioral **adaptation**, so "generation works / the bottleneck is evaluation NOT generation" is over-claimed. GPT Pro: "soften from 'generation works' to 'generation produces highly recoverable persona-distinct outputs; evaluation is the clearer bottleneck.'" Opus: "demote §11 'persona conditioning works at the generation stage.'"

---

## MUST FIX

| # | Issue (ReviewBench) | GPT Pro | Opus | GPT-5.5 | Gemini | Action |
|---|---------------------|:--:|:--:|:--:|:--:|--------|
| 1 | **"Generation works" over-reach** [VALIDITY/SUFFICIENCY] — Gate 3 = discriminability (partly surface contract-echo), not adaptation fidelity. Touches the central reframe. | ✓ | M1 | #4 | #3 | Reword everywhere (§1 callout, §1 Q2, one-line synthesis, §4.5, §5, §9, §11): "generation works" → "conditioned outputs are **blind-discriminable** (partly via contract-echo); whether the distinctness is **target-serving** is open." State Gate 3 = discriminability, not adaptation. Cut the "if anything, strengthens" move. |
| 2 | **False dichotomy "evaluation NOT generation"; §11 "safest summary no longer descriptive" is the most miscalibrated line** [VALIDITY/CLARITY] | ✓ | M2 | — | — | "evaluation is **the clearer** bottleneck; this does not clear generation of contributing." Remove "NOT generation" as settled; soften §11. |
| 3 | **Global-pole = bias vs real-quality never confronted** [VALIDITY] — global-pole may be a genuine unconditional-quality gap, not judge bias | (implied) | M3 | — | — | Add the benign reading: global-pole is consistent with both an eval bias AND a real quality gap the design can't distinguish (no ground-truth quality, no target-conditioned arm). Reframe "judge is biased" → "the unconditional contrast is not a test of target-fit by design." |
| 4 | **"Surface effect" overclaims — point estimate unchanged by adjustment** [VALIDITY] — 0.550→0.551, so not "explained by surface" | — | S6 | #2 | — | "surface effect"/"surface-explained" → "**does not survive surface control / not separable from the formatting it induces**" (mediator caveat: over-control can manufacture a null). §1, §4.1, §4.5, §5, §8. |
| 5 | **Trigger #7 attributed to "opus-as-judge" despite judge/author confound; "65.6% averages 90%/50%" mixes scopes** [VALIDITY] | ✓ | S3 | #5 | — | "opus-as-judge effect" → "**opus-judge/gpt-author cell** (judge-family OR author-family; confounded)". Remove the "aggregate 65.6% averages opus ~90%/gpt ~50%" arithmetic (mixes all-scope with cross-provider cells). §1, §4.1, §4.5, §6, §8, §11. |
| 6 | **Stale references contradict the revision** [TRANSPARENCY] | — | — | #1,#3 | #1,#2 | Fix §4.4 D3 ("trigger #8 must run" → run); §5 line 191 ("profile-specific content adds value via contract" → contradicts downgrade); TL;DR Q4 add opus-cell ladder caveat; intro line 7 #7/#8 "open before publication" → run. |

## SHOULD FIX

| # | Issue (ReviewBench) | Src | Action |
|---|---------------------|-----|--------|
| 7 | Single-coder, n=8/cell weight not flagged at first promotion [SUFFICIENCY] | Opus S1, GPT-5.5 | Add "(single-model single-pass, n=8/persona; directional, not a measured rate)" to §1 callout + §4.5 |
| 8 | dario/pawl delta-wrinkle understated (analyst-reconstructed brief; floor cell) [VALIDITY/TRANSPARENCY] | Opus S2 | "all 3 global-pole pairs sign-flip" → "**2 of 3 clean pairs sign-flip cleanly**; dario/pawl confounded by delta-form reconstruction" |
| 9 | "Matching survives surface" and "matching is global-pole" are the SAME content effect [CLARITY] | Opus S4 | Add clause: Gate-1 survival IS the Gate-2 global-pole signal, not a 2nd endorsement |
| 10 | Post-hoc status under-propagated to §5 "reclassified" / §8 FIRES [TRANSPARENCY] | Opus S5 | Prepend "(post-hoc, exploratory)" in §5; note §8 #8 firing is post-hoc mediator-laden |
| 11 | gpt-judge "at chance" → "at/below chance" (C4_WRONG vs C0 = 0.408) [CLARITY] | Gemini #4 | Fix §1 callout |
| 12 | §4.3 "benefit localizes to contract-first ordering" too causal [CLARITY] | GPT-5.5 #7 | "only detected step; mechanism unresolved" |
| 13 | §9 "shared-stylistic null largely confirms" bundles 3 distinct nulls (#7 points AWAY from cross-model sharedness) [CLARITY] | GPT-5.5 #8 | Split: surface/stylometry, judge/author-cell structure pref, global trait-pole |
| 14 | §4.1 narrative whiplash ("reliable but fragile" → instantly negated) [CLARITY] | Gemini #5 | Soften unrevised reading: "appears reliable but fragile prior to surface control" |
| 15 | C5_CONTRACT vs C5 trigger-#7 row gpt_n=16 — disclose low denominator [TRANSPARENCY] | GPT-5.5 #6 | Note small n |

## NICE TO HAVE

| # | Issue | Src |
|---|-------|-----|
| 16 | 93% CI treats n=128 coupled (64×2) judgments as independent — understates uncertainty | Opus N1 |
| 17 | State "25% = ~16 tasks" inline | Opus N2 |
| 18 | §8 tally should include "#1 partial" | Gemini #6 |
| 19 | Add a compact provenance table in §4.5 (n, source, denominators) | GPT-5.5 #9 |

## GPT Pro's constructive additions (feed v0.4, not the report body)
- Cheapest decisive next test: **de-echoed / neutral-paraphrase blind recovery** + **target-conditioned rejudging** on existing outputs (distinguishes adaptation from contract-echo; tests the eval-bottleneck claim directly).
- v0.4 #1 = target-conditioned judging ("better for persona P?"); #2 = per-judge calibration + full author×judge crossing; #3 = trait-pole-balanced persona sampling (+ decoys matched on verbosity/structure/warmth/safety); #4 = fully-crossed content×form×salience.
- Several cheap existing-data analyses (global-pole index regression; persona-fit vs general-quality 2-axis; de-echo lexical ablation; cited-basis audit of Gate 3; position residuals; task-domain moderation).
