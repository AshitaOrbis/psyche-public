# Fix Manifest — gate-driven revision (between pub-review round 1 and round 2)

**Date**: 2026-06-17
**Document**: `reports/psycheeval_v0_3_full_pilot_2026-05-19_v03.md`
**Baseline**: commit `e6cb9c2` (post round-1 fixes + §4.4/§9 finalization)
**Driver**: existing-data gate battery (Gates 1, 1b, 2, 3 + failure-triggers #7/#8) — `reports/analysis/gate_battery_findings.md`. These are the GPT Pro forward-analysis gates run on the existing corpus; they materially revise three of the four headline readings.

## New analysis run (all on existing v0.3 corpus, cross-provider same-author, cluster bootstrap)

| Gate | Script | Result |
|------|--------|--------|
| 1 (surface deconfound; trigger #8) | `drivers/analysis/gate1_style_deconfound.py` | Specificity (C3/C4 > C_GENERIC) does NOT survive surface control; matching & structure do |
| 1b (9-feature stylometric) | `drivers/analysis/gate1b_stylometry.py` | Confirms Gate 1 with richer index |
| 2 (reciprocal sign-flip) | `drivers/analysis/gate2_signflip.py` | 3/4 reciprocal pairs are global-pole, not target-matching |
| 3 (blind persona-alignment, Gemini non-study) | `gate3_prepare.py` + 4 subagents + `gate3_score.py` | 93% blind recovery → generation produces target-distinct text; failure is at evaluation |
| #7 (judge divergence) | `trigger7_judge_divergence.py` | Fires on 5/11 contract-structure contrasts; structure floor is largely opus-as-judge |

## Applied edits to the report

| # | Section | Change | Rationale |
|---|---------|--------|-----------|
| 1 | §1 TL;DR | Added "Gate-battery update (read first)" callout; reworded mechanism answers Q1 (specificity → surface) and Q2 (matching → global-pole; structure → opus-as-judge; generation works); rewrote one-line synthesis to "bottleneck is evaluation, not generation" | three of four readings materially revised by gates |
| 2 | §4.1 table + reading | Softened two table reading cells (C3>C_GENERIC "does not survive surface control"; C3>C4_WRONG "mostly global-pole"); added "Gate-battery correction" paragraph | internal consistency with §4.5; remove stale "reliable increment" |
| 3 | §4.3 ladder | Updated stale trigger-#8 reference (now run); noted contract-first jump is plausibly the opus-as-judge structure preference | trigger #8 closed; connect to #7 |
| 4 | §4.5 (NEW) | Added "Existing-data gate battery" section: results table + decisive synthesis (gen-vs-eval) | central new content |
| 5 | §5 retractions | Reclassified specificity (surface), matching (global-pole), structure (opus-as-judge) as downgrades; kept public-anchor (D4) | honest non-results accounting |
| 6 | §6 inherited | Softened "Judge-unanimous" on C4>C5 (coverage gap); flagged C5_CONTRACT>C5 fires #7 | trigger #7 |
| 7 | §8 triggers | #7 TODO→FIRES; #8 TODO→FIRES(partial); updated summary ("three fired", ≥3 threshold met) | predeclared triggers now run |
| 8 | §9 limitations | Updated "strongest skeptical reading" bullet: gate battery now targets the shared-stylistic null and largely confirms it; generation is the one place the null is refuted; added gate-self-limitations | the null is no longer "unconstrained" |
| 9 | §10 v0.4 | Reprioritized to lead with judge-side fixes (target-conditioned judging, per-judge calibration, trait-pole-balanced sampling, instruction-quantity-matched C0) | gates move bottleneck to evaluation |
| 10 | §11 closing | Rewrote from the gate-corrected reading | closing must reflect §4.5 |
| 11 | Sign-off | #7/#8 + gate battery checked; round-2 / GPT-Pro-round-2 noted pending | tracking |

## Carried forward / still open

| Item | Status |
|------|--------|
| Trigger #3 (Phase 5 single-rater) | Open — toolkit ready, not run |
| GPT Pro round-2 on gate results | In flight (`reports/reviews/2026-06-17_gptpro_round2_prompt.md`) |
| Ladder-specific deconfounding | Deferred to v0.4 (noted §4.3) |
| Gate 3 human cross-check (single non-study coder now) | Deferred to v0.4 (noted §10.5) |

## Round-1 findings status (for reference)

All 7 MUST FIX + SHOULD FIX items from `2026-06-16_consolidated_round1.md` were applied in commit `3aa7946` and finalized in `47f16c4`/`e6cb9c2`. The gate revision does not reopen them; several are reinforced (e.g., round-1 SHOULD-FIX #8 "cross-provider ≠ anti-halo" and #12 "C0 not instruction-quantity-matched" are now empirically substantiated by trigger #7 and the §10 C0-control plan).
