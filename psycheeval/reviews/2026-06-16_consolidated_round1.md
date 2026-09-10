# Publication Review — Consolidated Round 1

**Date**: 2026-06-16
**Document**: `reports/psycheeval_v0_3_full_pilot_2026-05-19_v03.md`
**Reviewers**: GPT-5.5 xhigh (codex), Gemini 3.1 Pro, Opus (steelman Agent)
**Convergence**: NOT converged — 7 MUST FIX (3 flagged by ≥2 reviewers). Round 2 recommended after fixes.

Cross-reviewer note: the three deepest findings are reviewer-unique — Opus owns the two strongest (ladder-localization is logically unsupportable; cross-provider ≠ anti-halo), GPT owns the numeric catches (D2 denominator, multiplicity), Gemini owns the consistency catches (orientation inversion, duplicate-62%). The identical-62% "bug" (Gemini) was traced to a genuine coincidence (independent records, 58.8% cell agreement) — disclosure, not data fix.

---

## MUST FIX

| # | Issue (ReviewBench) | GPT | Gem | Opus | Action |
|---|---------------------|-----|-----|------|--------|
| 1 | **Ladder "localizes to contract-first ordering" overclaims** [VALIDITY] — single-path, two *not-detected* steps, D5 equivalence deliberately skipped → "ruling out steps 1–2" is unestablished; L2→L3 confounded with accumulated structure/interactions. claim (d) | M6 | M3 | M2 | Reword §1, §4.3, §11: "the only single-step addition that reaches detection in this one ladder ordering; ordering-vs-threshold-crossing not separable in a single-path design" |
| 2 | **Public-anchor "isolates a genuine ... distinct from narrative form" overclaims** [VALIDITY] — contract not held constant in *content*; human-authorship style confound (§9) not ruled out. claim (c) | M3 | S1 | M1 | Downgrade §1, §4.2 to "consistent with a public-anchor contribution; residual style confound the design cannot rule out" |
| 3 | **"Mechanism" wording deployed while trigger #8 regression is an admitted TODO** [TRANSPARENCY/VALIDITY] — §4.3/§11 assert what §8 says is unlicensed. all claims | S6 | — | M3 | §4.3/§11 "mechanism" → "preference-pattern"; keep #8 as the gate; OR run the regression |
| 4 | **Ladder orientation inverted: TL;DR §1 reports complements of §4.3** [CLARITY] — 52.5/48.4 vs 47.5/51.6. claim (d) | M5 | M1 | — | Make §1 orientation match §4.3 (+feature side) |
| 5 | **§6 header "AB/BA-controlled" contradicts C0 row "not AB/BA-tested directly"; "C0 dominated" grammar** [CLARITY] | M10 | M4 | (S9) | Retitle §6 "carried over (AB/BA-controlled where tested)"; fix C0 wording to "C0 was dominated" |
| 6 | **D2 "646 (15% of scalar)" ≠ 646/7,180 ≈ 9%** [TRANSPARENCY] — denominator mismatch. sentinel coverage | M7 | — | — | State actual coverage (646 re-scores; ≈9% of pooled scalar; 15% referred to per-judge collection-time pool) |
| 7 | **Disclose the identical 62.0% [54.3,69.2] on two contrasts** [TRANSPARENCY] — verified coincidence (independent records, 58.8% cell agreement), not a bug. claim (c) | — | M2 | S8 | Add footnote in §4.2 |

## SHOULD FIX

| # | Issue (ReviewBench) | Src | Action |
|---|---------------------|-----|--------|
| 8 | **Cross-provider ≠ anti-halo** [VALIDITY] — controls self-preference, not shared cross-model stylistic priors (directive/front-loaded text); whole win structure could be shared formatting preference | Opus S4 | Soften §4 "conservative anti-halo scope"; add §9 limitation |
| 9 | **Multiplicity across 26 pairs** [VALIDITY] — near-threshold claims (CI low 51.6, 53.3, 50.7) need a note/primary-family declaration | GPT M2, Opus S6 | Add multiplicity note; soften "reliably" on near-threshold pairs |
| 10 | **"#5 PASS (effect 62% ≫ 5pp)" loose; "win rate" vs "pp" drift** [CLARITY] — 62% = 12pp above chance; define the trigger-#5 threshold | GPT M4, Gem S2 | Reword trigger #5; define pp vs win-rate |
| 11 | **"<3 fired" premature** while #3/#7/#8 open [VALIDITY] | GPT M9 | "of the completed checks, none fired; #3/#7/#8 open" |
| 12 | **C0 not instruction-quantity-matched** [VALIDITY] — "structure carries the floor" may restate "more instructions → better output" | Opus S7 | Scope to "directive instruction block (vs none); not separated from instruction-quantity" |
| 13 | **Near-zero profile refs is double-edged** [TRANSPARENCY] — what are judges responding to if winners aren't more profile-grounded? | Opus S5 | Flag as open question, not purely exculpatory |
| 14 | **Specificity increment fragile** (CI lows 51.6/53.3 + C5 null) [VALIDITY/SUFFICIENCY] — soften "reliably beats" | Opus S6, GPT S1 | Soften; report increment uncertainty where possible |
| 15 | **§5 "No headline collapsed" vs trigger #1 PARTIAL** [CLARITY] | Opus S9 | Scope §5 to pairwise headlines; flag scalar claims with trigger-#1 |
| 16 | **Present cluster-bootstrap CIs as primary alongside Wilson** [VALIDITY] | GPT M1 | Add bootstrap CI line (already referenced in App. B) |
| 17 | **§8 trigger #6 "PASS (provisional)" ambiguous; phase-pooling batch account; reference completeness** [TRANSPARENCY/CLARITY] | GPT S2/S5, Gem S3 | "(no fire)"; add pooling/version note; full Zheng/Shi cites + metrics commit |

## NICE TO HAVE

| # | Issue | Src |
|---|-------|-----|
| 18 | Foreground PI-only n≈120 for §4.2/§4.3 families (wider CIs by construction) | Opus N10 |
| 19 | Add an "alternative hypothesis" paragraph naming the "measures nothing" null + which sentinels (don't) constrain it | Opus N11 |
| 20 | Foreground "wrong profile beats baseline" as a limit on the personalization framing (≥half the over-baseline advantage is matching-independent) | Opus N12 |
| 21 | D1 "without swapping" → "without swapping the Slot A/B prompt order" | Gem N1 |
