# Phase A #3 — global-pole-index regression

**Date**: 2026-06-28
**Driver**: `drivers/analysis/gate2_global_pole_reg.py` (deterministic; numpy only — runs on system python3, no venv)
**Output**: `reports/analysis/gate2_global_pole_reg.json`

## Purpose
Independent (regression) confirmation of Gate 2's descriptive sign-flip finding ("matching" is mostly a global trait-pole preference, not target-fit). On the same 635 cross-provider/same-author **C4-vs-C4_WRONG** decisive records, decompose the win with a **differenced logistic**, oriented **anchor-first** (anchor = min(user_id) of each reciprocal pair) so the target-match term is not degenerate:

`y(anchor's output wins) ~ match_diff(±1) + pole_diff(z) + surface(z) + slot + judge_family`

where `pole_diff = desirability(anchor) − desirability(other)`, leave-one-out, and `desirability(P)` = win rate of P's profile when it is used as the **wrong** profile (P is not the target) — a global-pole index. **Pre-registered decisive read (v0.4 plan #3): if β_match shrinks toward 0 once global-pole desirability enters, Gate 2 is confirmed.**

## Result (n=635)

**Persona global desirability** (win rate of the profile when used as the WRONG one, i.e. not the target):

| pole | desirability | | pole | desirability |
|---|---:|---|---|---:|
| slalom_altar | 0.713 | | high_agency_spiraler | 0.461 |
| dario_armadillo | 0.658 | | patient_craftsperson | 0.275 |
| calibration_goblin | 0.588 | | pawl_gram | 0.200 |
| conflict_allergic_moralist | 0.463 | | emily_blender | 0.125 |

Spread **0.125 → 0.713**: some poles win even as decoys, others lose even when correct. (Maps onto Gate 2: slalom/dario/goblin = the globally-preferred poles in their pairs.)

**Logistic coefficients** (match on ±1 scale; pole/surface z-scored; slot/judge 0–1):

| model | β_match | β_pole_z | other |
|---|---:|---:|---|
| M1  `y ~ match` | **+0.264** [0.04, 0.49] | — | — |
| M2  `y ~ match + pole` | **+0.308** [0.08, 0.55] | **+0.847** [0.61, 1.10] | — |
| M3  `+ surface + slot + judge` | **+0.319** | +0.815 | slot −0.45, judge_anth −0.23, surf small + |

(CIs: cluster bootstrap, cluster = reciprocal-pair × scenario × author, 2000 resamples.)

## Reading — refines Gate 2, does not cleanly confirm it
1. **The global-pole effect is real and dominant.** β_pole_z ≈ 0.85 is the largest coefficient and the desirability spread (0.125–0.713) is huge. The C4-vs-C4_WRONG outcome is driven mostly by *which pole you are*, not by being the target. This strongly supports Gate 2's core.
2. **But a genuine target-match effect survives, controlling for the pole.** β_match ≈ 0.31 (±1 scale ⇒ ~+15pp for being the target vs the opposite, holding pole constant); its bootstrap CI excludes 0 and it is robust through surface/slot/judge controls. So the matching contrast is **mostly, but not purely**, global-pole.
3. **The pre-registered "β_match → 0" prediction did NOT hold** (β_match was stable, +17% if anything). Reason: the **anchor-first design orthogonalizes match (varies within pair) from pole (constant within pair)**, so adding pole cannot absorb match — and the data then reveal the two as *coexisting* effects rather than one masquerading as the other. This is a cleaner separation than the raw-correlated regression the plan envisaged, and its verdict is **both effects are present, pole ≫ match.**

## Consistency with Gate 2's per-pair verdicts
No contradiction. Gate 2's binary "GLOBAL-POLE" call fires when the **pole gap exceeds the match effect** within a pair. The pole gaps in the 3 global-pole pairs (e.g. slalom 0.713 vs emily 0.125) dwarf the ~+15pp match effect, so the dominant pole wins both directions → "GLOBAL-POLE," exactly as Gate 2 found. The small β_match is why the small-gap pairs (goblin/spiraler 0.588/0.461; moralist/craftsperson 0.463/0.275) are the borderline/weak-matching ones.

## Caveats
- β_pole rests on **8 persona-level desirability estimates** (4 reciprocal pairs); cluster bootstrap resamples records but the pole signal is identified across few clusters. Magnitude robust, precision optimistic.
- This is the **unconditional** judge's faint detection of target-fit (β_match), mostly drowned by the global pole — consistent with Gate 3 (text is target-distinct) and #7 (recovery mostly behavioral). It strengthens the case that **target-conditioned judging (#2) would amplify the residual target signal** the unconditional judge barely registers.
