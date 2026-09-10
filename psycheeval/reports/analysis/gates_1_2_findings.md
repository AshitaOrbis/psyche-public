# Existing-data gate analyses — Gate 1 (style deconfounding) + Gate 2 (sign-flip)

**Date**: 2026-06-17
**Source data**: `runs/2026-05-19_v03` pairwise (both orientations) + D3 per-output features
**Scope**: cross-provider, same-author, AB/BA both orientations. Cluster bootstrap (persona×scenario×author), 2000 resamples.
**Scripts**: `drivers/analysis/gate1_style_deconfound.py`, `drivers/analysis/gate2_signflip.py`
**Context**: GPT Pro's three pre-registered "existing-data gates" (`reviews/2026-06-16_gptpro_v0_3_forward_analysis.md`). These are the load-bearing tests for whether v0.3 shows real personalization vs shared formatting / global trait preference.

---

## Gate 1 — do the headline effects survive control for surface features?

Surface features pruned to the three with real variance — **log word count, source-packet lexical overlap, hedging/100w**. (`profile_reference_count` is 99% zero, `tailoring_marker_count` 100% zero, `refusal_safety_marker_count` 89% zero — these are dropped; their near-zero variance independently confirms **judges do not reward profile-naming or explicit tailoring markers**.) Surface-adjusted win rate = logistic intercept at ΔS=0, slot-balanced. CIs bootstrap 95%.

| Contrast | n | raw win | style-balanced subset | surface-adjusted (95% CI) | survives surface control? |
|----------|---:|--------:|----------------------:|---------------------------|---------------------------|
| **C4 > C4_WRONG** | 635 | 0.565 | 0.616 | **0.568 [0.511, 0.624]** | **YES** |
| **C3 > C4_WRONG** | 636 | 0.593 | 0.675 | **0.595 [0.539, 0.651]** | **YES** |
| C4 > C_GENERIC | 635 | 0.550 | 0.616 | 0.551 [0.495, 0.610] | **NO** (CI incl. 0.5) |
| C3 > C_GENERIC | 635 | 0.521 | 0.530 | 0.522 [0.468, 0.580] | **NO** |
| C_GENERIC > C0 | 634 | 0.702 | 0.774 | 0.729 [0.675, 0.788] | YES |
| C4_WRONG > C0 | 628 | 0.653 | 0.698 | 0.670 [0.611, 0.733] | YES |

**Gate 1 result.** Right-vs-wrong profile (matching) and contract-vs-no-profile (structure) **survive** length/overlap/hedging control. **Specificity-over-generic does NOT** — once surface is balanced, C3/C4 > C_GENERIC is indistinguishable from chance. So the modest "specificity adds an increment over a generic contract" headline (raw 57–59%) was substantially a surface effect; **downgrade it**. (Limitation: only 3 surface features; the richer cross-fitted style index GPT Pro recommended — bullets, imperatives, 2nd-person, markdown density — is the stronger test, pending Gate 1b.)

---

## Gate 2 — is "matching" real target-matching, or a global trait-pole preference?

`OPPOSITE_TRAIT_MAPPING` is reciprocal (A↔B). On A's scenarios C4=A's profile, C4_WRONG=B's profile; on B's scenarios C4=B's, C4_WRONG=A's. If matching is real, each persona's **own** profile should win on its **own** scenarios in *both* directions (sign-flip). If one profile-pole wins regardless of target, "right beats wrong" is a global preference, not matching.

Own-profile (C4) win rate vs the opposite profile (C4_WRONG), per target persona (n≈80 each):

| reciprocal pair | A own-profile win | B own-profile win | verdict |
|-----------------|------------------:|------------------:|---------|
| dario_armadillo / pawl_gram | **0.80** | 0.34 | **GLOBAL-POLE** (dario's profile wins both targets) |
| slalom_altar / emily_blender | **0.88** | 0.29 | **GLOBAL-POLE** (slalom's profile wins both) |
| calibration_goblin / high_agency_spiraler | 0.54 | 0.41 | **GLOBAL-POLE** |
| conflict_allergic_moralist / patient_craftsperson | 0.72 | 0.54 | matching (weak; craftsperson barely >0.5) |

**Gate 2 result — NEGATIVE for the matching headline.** In **3 of 4** reciprocal pairs, one persona's profile wins *regardless of which persona is the target* — a global trait-pole preference, exactly GPT Pro's falsifier ("same profile wins both directions ⇒ global preference, not matching"). The aggregate C4 > C4_WRONG ≈ 61–63% is inflated by the cases where the correct profile is the globally-preferred pole. Genuine, sign-flipping target-matching appears in **at most 1 of 4** pairs (and weakly). So the matching effect, though it survives *surface* control (Gate 1), is **largely not target-fit** — it is a content-level preference for certain trait-poles (plausibly the more agentic/assertive/structured personas).

---

## Combined reading (Gates 1 + 2)

- **Structure** (any contract > no-profile): robust to surface control. But even a *wrong* profile and a *generic* contract clear baseline, so this is "directive instruction block vs none," not personalization (and C0 is not instruction-quantity-matched — v0.4 needs `C0_STYLE_ONLY` / `C_PLACEBO_CONTRACT`).
- **Specificity over generic**: does **not** survive surface control — downgrade.
- **Matching** (right > wrong): survives surface control, but Gate 2 shows it is **mostly a global trait-pole preference, not target-matching** — downgrade from "matching matters" to "judges prefer certain profile-poles globally; genuine target-fit is weak (1/4 pairs)."
- Net: this pushes hard toward GPT Pro's adversarial conclusion. The strongest surviving claim is **structure**, which is the least personalization-relevant; the two personalization-relevant claims (specificity, matching) are each undercut by a different existing-data gate.

## Open / next

- **Gate 1b**: richer cross-fitted stylometric index (bullets, imperatives, headings, 2nd-person, markdown density, sentence length) from raw output text — strengthens Gate 1.
- **Gate 3**: blind semantic persona-alignment audit by a non-study model — does C4 raise *target* alignment (vs opposite alignment)? Would corroborate/refute Gate 2.
- These results feed the report (§1.1, §1.2, §4.1, §5, §11) and warrant a GPT Pro round-2 read + publication-review round 2.
