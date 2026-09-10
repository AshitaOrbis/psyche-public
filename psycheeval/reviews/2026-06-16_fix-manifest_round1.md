# Fix Manifest — Round 1

**Date**: 2026-06-16
**Document**: `reports/psycheeval_v0_3_full_pilot_2026-05-19_v03.md`

## Applied Fixes

| # | Reviewer finding | Action |
|---|------------------|--------|
| C1 | Ladder "localizes" overclaim (GPT/Gem/Opus) | §1.4, §4.3 reading, §11 reworded: "only single-step addition that reaches detection in this one ordering"; not-detected ≠ null (equivalence skipped); ordering-vs-threshold not separable in single-path design |
| C2 | Public-anchor "isolates genuine ... distinct from narrative form" overclaim (GPT/Gem/Opus) | §1.3, §4.2 downgraded to "consistent with a public-anchor contribution"; both confounds (style + content-not-held-constant) surfaced in-line |
| C3 | "mechanism" wording vs unrun trigger #8 (GPT/Opus) | §4.3/§11 → "preference-pattern"; causal mechanism explicitly gated on #8 regression |
| C4 | Ladder orientation inverted: TL;DR complements §4.3 (GPT/Gem) | §1.4 now uses the +feature side (L1 47.5%, L2 51.6%, L3 69.7%), matching §4.3 |
| C5 | §6 header AB/BA contradiction + "C0 dominated" grammar (GPT/Gem) | Retitled "AB/BA position-controlled where tested"; C0 row "C0 was dominated", flagged as the only non-position-controlled row |
| C6 | D2 "646 (15% of scalar)" ≠ 9% (GPT) | §3.1 + §4.4 D2: "646 (≈9% of pooled scalar; 15% of the v0.3-run scalar pool at collection time)" |
| C7 | Disclose identical 62.0% (Gem/Opus) | §4.2 blockquote footnote: verified coincidence of marginal totals, independent records, 58.8% cell agreement; not independent evidence |
| S8 | Cross-provider ≠ anti-halo (Opus) | §4 intro reworded; new §9 limitation (self-preference vs shared cross-model stylistic priors) |
| S9 | Multiplicity near-threshold (GPT/Opus) | §4 intro multiplicity paragraph; near-threshold contrasts labelled reliable-but-fragile |
| S10 | "62% ≫ 5pp" loose; pp-vs-win-rate (GPT/Gem) | §8 trigger #5 reworded (12pp above chance; CI-lower-bound caution) |
| S11 | "<3 fired" premature (GPT) | §8 summary reworded: completed vs open checks; gate not final until #3/#7/#8 close |
| S12 | C0 not instruction-quantity-matched (Opus) | §4.1 reading scoped to "directive instruction block vs none" |
| S13 | Near-zero profile-refs double-edged (Opus) | §4.4 D3 reframed as open question, not purely exculpatory |
| S14 | Specificity increment fragile (Opus/GPT) | §4.1 reading: "reliable but fragile (lower bounds 51.6/53.3)", C5 null noted |
| S15 | §5 "no headline collapsed" vs trigger #1 (Opus) | §5 scoped to pairwise headlines; scalar claims flagged |
| S16 | Bootstrap CIs as primary (GPT) | §4 intro: bootstrap CIs reported alongside Wilson, agree within ~1pp |
| S17 | trigger #6 "(no fire)" wording (Gem) | §8 trigger #6 → "PASS — no fire (provisional)" |
| N18 | PI-only n foregrounding (Opus) | §4 intro: §4.2/§4.3 families are PI-only, n≈120, wider CIs |
| N19 | Name the "measures nothing" null (Opus) | New §9 lead limitation: the strongest skeptical reading + which sentinels (don't) constrain it |
| N20 | "wrong profile beats baseline" foregrounded (Opus) | §4.1 reading: ≥half the over-baseline advantage is matching-independent |
| N21 | D1 "without swapping" clarity (Gem) | §4.4 D1 → "without swapping the Slot A / Slot B prompt order" |

## Deferred / Carried Forward (curation TODOs, gate publication)

| # | Item | Reason |
|---|------|--------|
| T1 | Trigger #7 — opus vs codex per-judge divergence on T1 pairs | Gates "judge-unanimous" wording; data-analysis curation step, not a review fix |
| T2 | Trigger #8 — reward-hacking covariate logistic regression | Gates causal "mechanism" wording; predeclared analysis not yet run |
| T3 | Phase 5 single-rater sanity check (trigger #3) | Toolkit ready; full pool now available |
| T4 | Opus D1/D4 full-pool sentinel re-sample | Running in background; §4.4 cells finalize on completion |
| T5 | Phase-pooling batch/version note; full Zheng/Shi cites; metrics commit hash | Transparency polish (GPT S2/S5) — round 2 |
| T6 | Round-2 delta review | Verify fixes introduced no regressions, after T1–T4 close |
