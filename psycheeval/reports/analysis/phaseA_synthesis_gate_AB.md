# PsycheEval v0.4 — Phase A synthesis & Gate A→B verdict

**Date**: 2026-06-28
**Inputs**: Phase A tests #1–#7 (all seven; this dir). All on the frozen v0.3 corpus (`runs/2026-05-19_v03`); cross-provider primary; deterministic tests reproduce the published Gate-3 numbers from a regenerated key.

## The question Phase A had to answer
v0.3's gate battery relocated the story from generation to **evaluation**, but left **one decisive open question**: is the discriminable persona-distinctness *target-serving behavioral adaptation*, or *surface/directive-following* that the unconditional-quality judges then fail to reward for the right reasons?

## What each test contributed

| test | result | contribution |
|---|---|---|
| **#7** cited-basis audit | 67% of blind-recovery rationales cite a **behavioral** axis; only 4.7% pure-surface; 33% echo-tail | recovery is mostly behavioral, not phrase-spotting (but echo tail kept #1 needed) |
| **#6** position/orientation residuals | global-pole verdict **STABLE** across AB/BA and C4-slot splits | the global-pole effect is real, not a presentation artifact |
| **#3** global-pole regression | β_pole_z ≈ 0.85 (dominant) **but** β_match ≈ 0.31 survives (CI excludes 0) | the win is *mostly* global-pole, yet a **genuine target-match effect coexists** even under unconditional judging |
| **#2** target-conditioned re-judging | recovers the target on **12/18 = 67%** of decisive global-pole-error cells, cross-provider (both judge directions) | the unconditional-**quality** framing was a major, **fixable** evaluation cause |
| **#4** two-axis re-score | **fit_gap +1.03 vs quality_gap +0.34** (gpt); on decisive cells quality even points the *wrong* way (−0.20) while fit points right (+0.40) | the personalization signal lives in **fit, not quality** — the unconditional-quality construct can't separate C4 from C4_WRONG, so the pole tips it |
| **#5** judge×contrast interaction | LR=376, p≈4e-57; judge gap **38pp on structure contrasts vs 6pp non-structure** | the opus-vs-gpt judge divergence is **structure-specific** (opus rewards contract scaffolding), formalizing trigger #7 |
| **#1** neutral-paraphrase recovery | **0.906** after stripping tone+format+phrasing (vs 0.93 raw) — Δ −0.024 | **generation is genuinely target-serving**; the 93% is substance, not echo |

## Resolution of the open question
**Generation produces genuine, target-serving behavioral adaptation — not surface/echo.** #1 is decisive: blind recovery survives at 0.906 after a full neutral paraphrase that strips tone, formatting, and profile-specific phrasing; the persona is recoverable from the *decisions/reasoning/ordering/risk-posture*. #7 (mostly-behavioral bases) and #3 (a residual target-match signal even under the unconditional judge) converge on the same conclusion.

**The v0.3 "matching is mostly global-pole" finding is an EVALUATION-instrument artifact, not a generation failure.** #6 confirms the global-pole is real and position-robust; #3 shows it dominates the *unconditional* win; **#4 gives the mechanism** — general quality barely separates C4 from C4_WRONG (Δquality ≈ 0, even pointing toward the pole on the decisive cells), while *fit* clearly favors the target (Δfit ≈ +1), so an unconditional-quality judge is tracking the wrong axis and gets tipped by the pole; #2 shows it is **fixable** — asking "which serves *this person*?" (fit-framing) recovers the target on ~two-thirds of exactly the cells where the unconditional-quality judge had preferred the global pole; #5 localizes the residual judge-divergence to contract-structure contrasts. Note (strengthening): the v0.3 unconditional judge already had `latent_ground_truth` and still chose the pole — so the bottleneck is the *unconditional-quality question*, not absence of persona data.

## Gate A → B verdict: **GO (lead with target-conditioned judging)**
The v0.4 plan's A→B "go" condition was: *neutral-paraphrase recovery stays high **AND** target-conditioned judging sign-flips* ⇒ generation validated + evaluation bottleneck confirmed ⇒ Phase B leads with target-conditioned judging at scale.

- **Generation validated**: #1 = 0.906 (≥ .75). ✓
- **Evaluation bottleneck confirmed & fixable**: #2 = 67% target recovery on decisive cells, cross-provider. ✓

**Both halves met.** Phase B leads with **target-conditioned judging at scale** — not "better profiles."

## Phase B priorities (per the v0.4 plan, now ordered by Phase A)
1. **Target-conditioned judging as the primary mode** (prompt `07c` validated here) — with **AB/BA position-counterbalancing, a tie option, and per-judge calibration** (the Phase-A #2 run was single-orientation, forced-choice).
2. **Per-judge calibration + fully-crossed author×judge matrix** — estimate each judge family's baseline structure/global-pole preference; report per-judge, not pooled.
3. **Trait-pole-balanced persona sampling + decoys** matched on verbosity/structure/confidence/warmth/safety — so a global pole can't masquerade as matching (addresses #3's β_pole at the source).
4. **Instruction-quantity-matched C0 controls** (C0_STYLE_ONLY, C_PLACEBO_CONTRACT, C0_LONG_NEUTRAL).
5. Fully-crossed content × form × salience; profile-stakes scenario panel (high/med/low trait-divergence).

## Caveats carried into Phase B
- Decisive-cell n is small (#2: 8/10 per direction); #1's within-task judgments treated independent; single non-study coder; #2 single-orientation/forced-choice; paraphrase fidelity spot-checked not audited. None overturns the convergent direction, but Phase B should harden each (AB/BA, ≥2 coders, paraphrase-fidelity check, larger decisive N).
- Phase 5 human-rater cross-check (≥2 raters + human recode of the Gate-3 blind coding) still owed.
