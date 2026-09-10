# PsycheEval v0.1 — v03_full_pilot — run 2026-05-19_v03 (auto-generated)

> Auto-generated numeric scaffold. The human-curated narrative report lives at `psycheeval_v0_1_v03_full_pilot_2026-05-19_v03.md`. This file contains only tables computed from `metrics_2026-05-19_v03.json`. Regenerating analyze.py will overwrite this file but never the curated one.

## Claim ledger (canonical per-claim summary)

Source: 2026-05-17 round-2 consolidated review §2.3 — unanimously endorsed as the report's central artifact. Each row pairs the claim with its position-controlled estimate, scope qualifiers, scalar alignment, and explicit allowed/forbidden wording for the curated report. Tier 1 / 1.5 / 2 reflect round-2 verdict.

| tier | claim | controlled lo_win | Bootstrap CI | scalar Δ_total | judge scope | survives swap? |
|---|---|---:|---|---:|---|---|
| 1 | C5_CONTRACT > C5 | 0.323 | [0.267, 0.383] | +3.057 | all three judges (gpt-5.4, gpt-5.5, opus) | ✓ |
| 1 | C4 > C1_padded | 0.377 | [0.317, 0.439] | +3.084 | gpt-5.4 + gpt-5.5 (Opus has 0 records on this pair) | ✓ |
| 1.5 | C4 > C4_shuffled (modest effect) | 0.578 | [0.522, 0.637] | -0.519 | gpt-5.4 + gpt-5.5 (Opus has 0 records on this pair) | ✓ |
| 1 | C4 > C5 | 0.680 | [0.615, 0.744] | -3.261 | all three judges (gpt-5.4, gpt-5.5, opus) — Opus added 2026-05-17 | ✓ |
| 1 | C0 dominated by profile conditions | — | — | +6.075 | all three judges (original pairwise + scalar) | — |
| 2 | C5_CONTRACT vs C3 — no detected preference | 0.501 | [0.436, 0.566] | -0.053 | all three judges | ⚠ |
| 2 | C5_CONTRACT vs C4 — no detected preference | 0.482 | [0.413, 0.548] | -0.231 | all three judges | ⚠ |
| Methodology contribution | LLM judges show ~15-17pp slot-B preference (judge-family-specific) | — | — | — | n/a (methodology finding scoped to this corpus + protocol) | — |

### Wording guidance per claim

**[1] C5_CONTRACT > C5** (`tier1_c5contract_gt_c5`)

- ✅ Allowed: The contract-supplemented source-packet package (C5_CONTRACT) outperforms the bare source-packet condition (C5) under position-controlled judging. Robust across Phase 0 audits (judge-unanimous, persona-robust, family-robust, scalar-aligned) and survives joint position+length correction. Mechanism not isolated — see v0.3.
- ❌ Forbidden: contract repairs source-packet fragility; source packets add value when subordinated to contracts; mechanism isolated.
- Joint position+length corrected lo_win: 0.351 [0.238, 0.471] (n=74)

**[1] C4 > C1_padded** (`tier1_c4_gt_c1padded`)

- ✅ Allowed: Behavioral contract (C4) outperforms length-matched baseline (C1_padded) under position-controlled judging. Length-control + position-control both pass.
- ❌ Forbidden: (none specific to this claim)
- Joint position+length corrected lo_win: 0.267 [0.174, 0.366] (n=86)

**[1.5] C4 > C4_shuffled (modest effect)** (`tier1_5_c4_gt_c4shuffled`)

- ✅ Allowed: Coherent-order C4 modestly outperforms shuffled-order C4 under position-controlled judging. Sign-corrected from Phase 0 (original 51.9% headline was understating because slot-A bias hurt C4 in slot A). Effect size (~58%) is meaningfully smaller than the C4 > C1_padded and C5_CONTRACT > C5 findings.
- ❌ Forbidden: Coherent structure does not significantly beat shuffled; coherent structure significantly beats shuffled (over-strong wording either direction).
- Joint position+length corrected lo_win: 0.616 [0.512, 0.721] (n=86)

**[1] C4 > C5** (`tier1_c4_gt_c5`)

- ✅ Allowed: Behavioral contract (C4) outperforms source-packet-without-contract (C5) under position-controlled judging at 68.0% [61.5, 74.4]. Judge-unanimous across all three judges (gpt-5.4, gpt-5.5, opus). Survives joint position+length correction (length-matched subset n=76, controlled 67.4% [54.7, 79.5] — CI excludes 0.5 on the C4 side). Opus AB/BA fill (2026-05-17 Phase 2 hygiene pass) closed the original scope gap.
- ❌ Forbidden: (none specific to this claim after Opus fill).
- Joint position+length corrected lo_win: 0.674 [0.547, 0.795] (n=76)

**[1] C0 dominated by profile conditions** (`tier1_c0_dominated`)

- ✅ Allowed: Baseline (C0) is dominated by any profile-conditioned condition. Effect size is large (~86% C4-over-C0 in original pairwise + Δ_total +6.075 in scalar). Not AB/BA-tested directly; the magnitude is well outside the measured ~15-17pp slot-B preference range so likely robust to position-bias correction.
- ❌ Forbidden: AB/BA-controlled (not directly tested).

**[2] C5_CONTRACT vs C3 — no detected preference** (`tier2_c5contract_vs_c3`)

- ✅ Allowed: Under position-controlled (AB/BA) judging, we do not detect a reliable pairwise preference between C5_CONTRACT and C3 (controlled C5_CONTRACT win rate 49.9% [44.3, 55.7]). Scalar scores also do not favor C5_CONTRACT (Δ_total −0.053). The original 57.2% C5_CONTRACT win rate was carried entirely by slot-B position bias.
- ❌ Forbidden: C5_CONTRACT outperforms C3; C5_CONTRACT equivalent to C3 (no equivalence margin pre-declared).
- Joint position+length corrected lo_win: 0.500 [0.371, 0.634] (n=80)

**[2] C5_CONTRACT vs C4 — no detected preference** (`tier2_c5contract_vs_c4`)

- ✅ Allowed: Under position-controlled (AB/BA) judging, we do not detect a reliable pairwise preference between C5_CONTRACT and C4 (controlled C5_CONTRACT win rate 51.8% [46.0, 57.5]). Scalar scores slightly favor C4 (Δ_total −0.231). The original 60.0% C5_CONTRACT win rate was carried entirely by slot-B position bias.
- ❌ Forbidden: C5_CONTRACT outperforms C4; C5_CONTRACT equivalent to C4.
- Joint position+length corrected lo_win: 0.450 [0.298, 0.601] (n=65)

**[Methodology contribution] LLM judges show ~15-17pp slot-B preference (judge-family-specific)** (`methodology_slot_b_bias`)

- ✅ Allowed: In this corpus, prompt, judge set, and pairwise protocol, two of three judge configurations directly showed large later-answer / slot-B preference. GPT-5.5 (xhigh): 25-31pp slot-B advantage. Opus 4.7: 9-24pp, content-varying. GPT-5.4: negligible, occasionally slot-A favored. Uncounterbalanced margins were systematically biased in favor of the higher-numbered condition (which was always in slot B in v0.2 originals). Consistent with prior LLM-as-judge position-bias literature (Zheng et al. 2023, Shi et al. 2024).
- ❌ Forbidden: LLM judges show universal slot-B bias; pure position bias; all LLM judges have slot-B preference.

## Dataset composition

- **scenarios**: 80
- **users**: 8
- **assistant_outputs**: 2757
- **judge_scores**: 0
- **anchored_judge_scores**: 7180
- **pairwise_scores**: 14733

## Pairwise results (cross-provider judged)

### Counts

- **total_pairwise_records**: 14733
- **after_tagging**: 14733
- **same_author**: 14554
- **cross_author**: 179
- **cross_provider**: 5541
- **cross_provider_same_author**: 5444
- **cross_provider_same_author_PI**: 4496

### Condition win-rate (same-author pairs, cross-provider judged)

Ties contribute 0.5 to each side. Same-author pairs isolate condition effects from author effects.

- **C0**: 0.366
- **C3**: 0.611
- **C4**: 0.596
- **C4_WRONG_PROFILE**: 0.451
- **C5**: 0.522
- **C5_CONTRACT**: 0.670
- **C5_NONPUBLIC**: 0.329
- **C5_NONPUBLIC_CONTRACT**: 0.491
- **C_GENERIC_CONTRACT**: 0.495
- **L1**: 0.414
- **L2**: 0.391
- **L3**: 0.439

### Condition-pair preferences (same-author, cross-provider)

| pair | n | first wins | second wins | ties |
|---|---|---|---|---|
| C0 vs C4_WRONG_PROFILE | 318 | 0.377 | 0.604 | 0.019 |
| C0 vs C_GENERIC_CONTRACT | 318 | 0.343 | 0.654 | 0.003 |
| C3 vs C4_WRONG_PROFILE | 318 | 0.632 | 0.368 | 0.000 |
| C3 vs C5_CONTRACT | 88 | 0.330 | 0.636 | 0.034 |
| C3 vs C5_NONPUBLIC | 160 | 0.688 | 0.306 | 0.006 |
| C3 vs C5_NONPUBLIC_CONTRACT | 160 | 0.594 | 0.400 | 0.006 |
| C3 vs C_GENERIC_CONTRACT | 318 | 0.569 | 0.428 | 0.003 |
| C3 vs L1 | 160 | 0.656 | 0.344 | 0.000 |
| C3 vs L2 | 160 | 0.681 | 0.312 | 0.006 |
| C4_WRONG_PROFILE vs C5 | 160 | 0.412 | 0.581 | 0.006 |
| C4 vs C4_WRONG_PROFILE | 318 | 0.610 | 0.387 | 0.003 |
| C4 vs C5 | 80 | 0.675 | 0.325 | 0.000 |
| C4 vs C5_CONTRACT | 88 | 0.386 | 0.591 | 0.023 |
| C4 vs C5_NONPUBLIC | 160 | 0.637 | 0.362 | 0.000 |
| C4 vs C5_NONPUBLIC_CONTRACT | 160 | 0.531 | 0.469 | 0.000 |
| C4 vs C_GENERIC_CONTRACT | 318 | 0.588 | 0.412 | 0.000 |
| C4 vs L3 | 158 | 0.671 | 0.329 | 0.000 |
| C5_CONTRACT vs C5_NONPUBLIC | 160 | 0.694 | 0.300 | 0.006 |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 160 | 0.613 | 0.375 | 0.013 |
| C5_CONTRACT vs L1 | 160 | 0.644 | 0.350 | 0.006 |
| C5_CONTRACT vs L3 | 158 | 0.747 | 0.247 | 0.006 |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 160 | 0.287 | 0.706 | 0.006 |
| C5 vs C5_CONTRACT | 88 | 0.307 | 0.693 | 0.000 |
| C5 vs C5_NONPUBLIC | 160 | 0.613 | 0.375 | 0.013 |
| C5 vs C_GENERIC_CONTRACT | 160 | 0.531 | 0.469 | 0.000 |
| C5 vs L1 | 160 | 0.525 | 0.475 | 0.000 |
| C5 vs L2 | 160 | 0.575 | 0.425 | 0.000 |
| C5 vs L3 | 158 | 0.513 | 0.481 | 0.006 |
| L1 vs L2 | 160 | 0.469 | 0.500 | 0.031 |
| L2 vs L3 | 158 | 0.297 | 0.684 | 0.019 |

### Condition-pair preferences (PI-only, same-author, cross-provider)

C5 pairs appear here and here only — never in the all-persona block.

| pair | n | first wins | second wins | ties |
|---|---|---|---|---|
| C0 vs C4_WRONG_PROFILE | 160 | 0.338 | 0.631 | 0.031 |
| C0 vs C_GENERIC_CONTRACT | 160 | 0.312 | 0.688 | 0.000 |
| C3 vs C4_WRONG_PROFILE | 160 | 0.725 | 0.275 | 0.000 |
| C3 vs C5_CONTRACT | 88 | 0.330 | 0.636 | 0.034 |
| C3 vs C5_NONPUBLIC | 160 | 0.688 | 0.306 | 0.006 |
| C3 vs C5_NONPUBLIC_CONTRACT | 160 | 0.594 | 0.400 | 0.006 |
| C3 vs C_GENERIC_CONTRACT | 160 | 0.675 | 0.319 | 0.006 |
| C3 vs L1 | 160 | 0.656 | 0.344 | 0.000 |
| C3 vs L2 | 160 | 0.681 | 0.312 | 0.006 |
| C4_WRONG_PROFILE vs C5 | 160 | 0.412 | 0.581 | 0.006 |
| C4 vs C4_WRONG_PROFILE | 160 | 0.625 | 0.369 | 0.006 |
| C4 vs C5 | 80 | 0.675 | 0.325 | 0.000 |
| C4 vs C5_CONTRACT | 88 | 0.386 | 0.591 | 0.023 |
| C4 vs C5_NONPUBLIC | 160 | 0.637 | 0.362 | 0.000 |
| C4 vs C5_NONPUBLIC_CONTRACT | 160 | 0.531 | 0.469 | 0.000 |
| C4 vs C_GENERIC_CONTRACT | 160 | 0.600 | 0.400 | 0.000 |
| C4 vs L3 | 158 | 0.671 | 0.329 | 0.000 |
| C5_CONTRACT vs C5_NONPUBLIC | 160 | 0.694 | 0.300 | 0.006 |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 160 | 0.613 | 0.375 | 0.013 |
| C5_CONTRACT vs L1 | 160 | 0.644 | 0.350 | 0.006 |
| C5_CONTRACT vs L3 | 158 | 0.747 | 0.247 | 0.006 |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 160 | 0.287 | 0.706 | 0.006 |
| C5 vs C5_CONTRACT | 88 | 0.307 | 0.693 | 0.000 |
| C5 vs C5_NONPUBLIC | 160 | 0.613 | 0.375 | 0.013 |
| C5 vs C_GENERIC_CONTRACT | 160 | 0.531 | 0.469 | 0.000 |
| C5 vs L1 | 160 | 0.525 | 0.475 | 0.000 |
| C5 vs L2 | 160 | 0.575 | 0.425 | 0.000 |
| C5 vs L3 | 158 | 0.513 | 0.481 | 0.006 |
| L1 vs L2 | 160 | 0.469 | 0.500 | 0.031 |
| L2 vs L3 | 158 | 0.297 | 0.684 | 0.019 |

---

## Appendix A — Secondary: all-judge means

**Do not use these as primary results.** Same-provider scores are included. See halo audit for why this matters. Kept for audit only.

---

## Tie rates (same-author, all-judges-pooled)

| pair | total | decisive | ties | tie_rate | lo decisive win |
|---|---:|---:|---:|---:|---:|
| C0 vs C4 | 320 | 320 | 0 | 0.0000 | 0.1344 |
| C0 vs C4_WRONG_PROFILE | 717 | 710 | 7 | 0.0098 | 0.3465 |
| C0 vs C_GENERIC_CONTRACT | 717 | 716 | 1 | 0.0014 | 0.2779 |
| C1_padded vs C4 | 320 | 320 | 0 | 0.0000 | 0.3187 |
| C1 vs C1_padded | 320 | 320 | 0 | 0.0000 | 0.4344 |
| C1 vs C4 | 320 | 319 | 1 | 0.0031 | 0.3260 |
| C3 vs C4 | 320 | 320 | 0 | 0.0000 | 0.3781 |
| C3 vs C4_WRONG_PROFILE | 717 | 717 | 0 | 0.0000 | 0.6318 |
| C3 vs C5_CONTRACT | 288 | 283 | 5 | 0.0174 | 0.4276 |
| C3 vs C5_NONPUBLIC | 360 | 359 | 1 | 0.0028 | 0.7242 |
| C3 vs C5_NONPUBLIC_CONTRACT | 360 | 359 | 1 | 0.0028 | 0.5989 |
| C3 vs C_GENERIC_CONTRACT | 717 | 716 | 1 | 0.0014 | 0.5405 |
| C3 vs L1 | 360 | 360 | 0 | 0.0000 | 0.6972 |
| C3 vs L2 | 360 | 359 | 1 | 0.0028 | 0.7437 |
| C4_WRONG_PROFILE vs C5 | 360 | 359 | 1 | 0.0028 | 0.4290 |
| C4 vs C4_WRONG_PROFILE | 717 | 716 | 1 | 0.0014 | 0.6159 |
| C4 vs C4_shuffled | 320 | 320 | 0 | 0.0000 | 0.5188 |
| C4 vs C5 | 280 | 278 | 2 | 0.0071 | 0.6259 |
| C4 vs C5_CONTRACT | 288 | 285 | 3 | 0.0104 | 0.4000 |
| C4 vs C5_NONPUBLIC | 360 | 360 | 0 | 0.0000 | 0.6972 |
| C4 vs C5_NONPUBLIC_CONTRACT | 360 | 360 | 0 | 0.0000 | 0.5833 |
| C4 vs C_GENERIC_CONTRACT | 717 | 716 | 1 | 0.0014 | 0.5628 |
| C4 vs L3 | 357 | 357 | 0 | 0.0000 | 0.7143 |
| C5_CONTRACT vs C5_NONPUBLIC | 360 | 359 | 1 | 0.0028 | 0.7409 |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 360 | 356 | 4 | 0.0111 | 0.6264 |
| C5_CONTRACT vs L1 | 360 | 359 | 1 | 0.0028 | 0.6908 |
| C5_CONTRACT vs L3 | 357 | 356 | 1 | 0.0028 | 0.7528 |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 360 | 358 | 2 | 0.0056 | 0.2709 |
| C5 vs C5_CONTRACT | 288 | 287 | 1 | 0.0035 | 0.2404 |
| C5 vs C5_NONPUBLIC | 360 | 357 | 3 | 0.0083 | 0.6275 |
| C5 vs C_GENERIC_CONTRACT | 360 | 360 | 0 | 0.0000 | 0.4639 |
| C5 vs L1 | 360 | 360 | 0 | 0.0000 | 0.5444 |
| C5 vs L2 | 360 | 360 | 0 | 0.0000 | 0.6139 |
| C5 vs L3 | 357 | 356 | 1 | 0.0028 | 0.5449 |
| L1 vs L2 | 360 | 355 | 5 | 0.0139 | 0.5070 |
| L2 vs L3 | 357 | 353 | 4 | 0.0112 | 0.3229 |

## PI/PS split pairwise (same-author, all-judges-pooled, non-C5 pairs)

| pair | PI lo win | PI CI95 | PI n | PS lo win | PS CI95 | PS n |
|---|---:|---|---:|---:|---|---:|
| C0 vs C4 | 0.1062 | [0.0674, 0.1636] | 160 | 0.1625 | [0.1134, 0.2275] | 160 |
| C0 vs C4_WRONG_PROFILE | 0.3014 | [0.2560, 0.3511] | 355 | 0.3915 | [0.3422, 0.4432] | 355 |
| C0 vs C_GENERIC_CONTRACT | 0.2444 | [0.2029, 0.2914] | 360 | 0.3118 | [0.2659, 0.3617] | 356 |
| C1_padded vs C4 | 0.3375 | [0.2688, 0.4138] | 160 | 0.3000 | [0.2344, 0.3750] | 160 |
| C1 vs C1_padded | 0.4625 | [0.3870, 0.5397] | 160 | 0.4062 | [0.3332, 0.4837] | 160 |
| C1 vs C4 | 0.3125 | [0.2458, 0.3880] | 160 | 0.3396 | [0.2706, 0.4162] | 159 |
| C3 vs C4 | 0.4062 | [0.3332, 0.4837] | 160 | 0.3500 | [0.2804, 0.4266] | 160 |
| C3 vs C4_WRONG_PROFILE | 0.7000 | [0.6508, 0.7450] | 360 | 0.5630 | [0.5112, 0.6135] | 357 |
| C3 vs C5_CONTRACT | 0.4276 | [0.3713, 0.4858] | 283 | — | — | — |
| C3 vs C5_NONPUBLIC | 0.7242 | [0.6758, 0.7679] | 359 | — | — | — |
| C3 vs C5_NONPUBLIC_CONTRACT | 0.5989 | [0.5474, 0.6483] | 359 | — | — | — |
| C3 vs C_GENERIC_CONTRACT | 0.6212 | [0.5700, 0.6698] | 359 | 0.4594 | [0.4084, 0.5112] | 357 |
| C3 vs L1 | 0.6972 | [0.6479, 0.7424] | 360 | — | — | — |
| C3 vs L2 | 0.7437 | [0.6962, 0.7861] | 359 | — | — | — |
| C4 vs C4_WRONG_PROFILE | 0.6323 | [0.5813, 0.6805] | 359 | 0.5994 | [0.5478, 0.6490] | 357 |
| C4 vs C4_shuffled | 0.5437 | [0.4665, 0.6190] | 160 | 0.4938 | [0.4173, 0.5705] | 160 |
| C4 vs C5_CONTRACT | 0.4000 | [0.3448, 0.4578] | 285 | — | — | — |
| C4 vs C5_NONPUBLIC | 0.6972 | [0.6479, 0.7424] | 360 | — | — | — |
| C4 vs C5_NONPUBLIC_CONTRACT | 0.5833 | [0.5318, 0.6331] | 360 | — | — | — |
| C4 vs C_GENERIC_CONTRACT | 0.5778 | [0.5262, 0.6277] | 360 | 0.5478 | [0.4958, 0.5987] | 356 |
| C4 vs L3 | 0.7143 | [0.6653, 0.7587] | 357 | — | — | — |
| C5_CONTRACT vs C5_NONPUBLIC | 0.7409 | [0.6932, 0.7835] | 359 | — | — | — |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 0.6264 | [0.5751, 0.6751] | 356 | — | — | — |
| C5_CONTRACT vs L1 | 0.6908 | [0.6412, 0.7364] | 359 | — | — | — |
| C5_CONTRACT vs L3 | 0.7528 | [0.7055, 0.7948] | 356 | — | — | — |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 0.2709 | [0.2275, 0.3192] | 358 | — | — | — |
| L1 vs L2 | 0.5070 | [0.4552, 0.5587] | 355 | — | — | — |
| L2 vs L3 | 0.3229 | [0.2763, 0.3734] | 353 | — | — | — |

## Length-bucketed pairwise (C5 / C5_CONTRACT pairs, same-author)

Bucket = (lo-side wordcount) − (hi-side wordcount), in words.

### C0 vs C4

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 40 | 0.0750 | [0.0258, 0.1986] |
| lo_moderately_shorter | 116 | 0.0603 | [0.0295, 0.1193] |
| similar | 64 | 0.1719 | [0.0988, 0.2821] |
| lo_moderately_longer | 92 | 0.1957 | [0.1275, 0.2882] |
| lo_much_longer | 8 | 0.5000 | [0.2152, 0.7848] |

### C0 vs C4_WRONG_PROFILE

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 77 | 0.2597 | [0.1749, 0.3674] |
| lo_moderately_shorter | 216 | 0.2222 | [0.1719, 0.2822] |
| similar | 163 | 0.3313 | [0.2636, 0.4067] |
| lo_moderately_longer | 206 | 0.4903 | [0.4228, 0.5581] |
| lo_much_longer | 48 | 0.4792 | [0.3447, 0.6167] |

### C0 vs C_GENERIC_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 117 | 0.1368 | [0.0860, 0.2106] |
| lo_moderately_shorter | 293 | 0.1980 | [0.1564, 0.2474] |
| similar | 153 | 0.3268 | [0.2575, 0.4046] |
| lo_moderately_longer | 111 | 0.4775 | [0.3869, 0.5696] |
| lo_much_longer | 42 | 0.5238 | [0.3772, 0.6664] |

### C1_padded vs C4

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 14 | 0.0714 | [0.0127, 0.3147] |
| lo_moderately_shorter | 76 | 0.1842 | [0.1130, 0.2858] |
| similar | 86 | 0.1860 | [0.1179, 0.2811] |
| lo_moderately_longer | 94 | 0.5106 | [0.4112, 0.6093] |
| lo_much_longer | 50 | 0.4600 | [0.3297, 0.5960] |

### C1 vs C1_padded

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 14 | 0.2143 | [0.0757, 0.4759] |
| lo_moderately_shorter | 78 | 0.3590 | [0.2615, 0.4697] |
| similar | 100 | 0.2800 | [0.2014, 0.3749] |
| lo_moderately_longer | 98 | 0.6122 | [0.5133, 0.7027] |
| lo_much_longer | 30 | 0.6667 | [0.4878, 0.8077] |

### C1 vs C4

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 10 | 0.0000 | [0.0000, 0.2775] |
| lo_moderately_shorter | 58 | 0.3103 | [0.2062, 0.4380] |
| similar | 74 | 0.2027 | [0.1269, 0.3079] |
| lo_moderately_longer | 129 | 0.3643 | [0.2863, 0.4502] |
| lo_much_longer | 48 | 0.5000 | [0.3639, 0.6361] |

### C3 vs C4

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 14 | 0.4286 | [0.2138, 0.6741] |
| lo_moderately_shorter | 122 | 0.3115 | [0.2361, 0.3983] |
| similar | 82 | 0.3415 | [0.2480, 0.4491] |
| lo_moderately_longer | 98 | 0.4796 | [0.3833, 0.5774] |
| lo_much_longer | 4 | 0.5000 | [0.1500, 0.8500] |

### C3 vs C4_WRONG_PROFILE

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 132 | 0.5303 | [0.4455, 0.6134] |
| lo_moderately_shorter | 189 | 0.6032 | [0.5320, 0.6702] |
| similar | 150 | 0.5867 | [0.5067, 0.6623] |
| lo_moderately_longer | 171 | 0.7076 | [0.6355, 0.7706] |
| lo_much_longer | 75 | 0.8000 | [0.6959, 0.8749] |

### C3 vs C5_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 29 | 0.3448 | [0.1994, 0.5265] |
| lo_moderately_shorter | 98 | 0.2449 | [0.1704, 0.3386] |
| similar | 78 | 0.4487 | [0.3433, 0.5589] |
| lo_moderately_longer | 67 | 0.6119 | [0.4922, 0.7195] |
| lo_much_longer | 11 | 1.0000 | [0.7412, 1.0000] |

### C3 vs C5_NONPUBLIC

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 84 | 0.4881 | [0.3841, 0.5931] |
| lo_moderately_shorter | 105 | 0.8095 | [0.7240, 0.8732] |
| similar | 69 | 0.7391 | [0.6249, 0.8281] |
| lo_moderately_longer | 80 | 0.7875 | [0.6858, 0.8629] |
| lo_much_longer | 21 | 0.9524 | [0.7733, 0.9915] |

### C3 vs C5_NONPUBLIC_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 38 | 0.4211 | [0.2785, 0.5781] |
| lo_moderately_shorter | 129 | 0.5194 | [0.4339, 0.6038] |
| similar | 114 | 0.6667 | [0.5759, 0.7465] |
| lo_moderately_longer | 66 | 0.7424 | [0.6257, 0.8325] |
| lo_much_longer | 12 | 0.5833 | [0.3195, 0.8067] |

### C3 vs C_GENERIC_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 149 | 0.4497 | [0.3721, 0.5298] |
| lo_moderately_shorter | 261 | 0.4713 | [0.4116, 0.5318] |
| similar | 135 | 0.5111 | [0.4277, 0.5940] |
| lo_moderately_longer | 135 | 0.7333 | [0.6530, 0.8007] |
| lo_much_longer | 36 | 0.8056 | [0.6497, 0.9025] |

### C3 vs L1

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 51 | 0.4118 | [0.2875, 0.5483] |
| lo_moderately_shorter | 126 | 0.7460 | [0.6635, 0.8140] |
| similar | 69 | 0.5797 | [0.4621, 0.6889] |
| lo_moderately_longer | 96 | 0.8333 | [0.7463, 0.8947] |
| lo_much_longer | 18 | 0.8889 | [0.6720, 0.9690] |

### C3 vs L2

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 42 | 0.5238 | [0.3772, 0.6664] |
| lo_moderately_shorter | 122 | 0.7623 | [0.6795, 0.8291] |
| similar | 75 | 0.6400 | [0.5270, 0.7394] |
| lo_moderately_longer | 87 | 0.8506 | [0.7610, 0.9105] |
| lo_much_longer | 33 | 0.9091 | [0.7643, 0.9686] |

### C4_WRONG_PROFILE vs C5

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 60 | 0.3667 | [0.2562, 0.4932] |
| lo_moderately_shorter | 105 | 0.3143 | [0.2334, 0.4083] |
| similar | 51 | 0.5294 | [0.3952, 0.6595] |
| lo_moderately_longer | 117 | 0.4872 | [0.3985, 0.5767] |
| lo_much_longer | 26 | 0.5769 | [0.3895, 0.7446] |

### C4 vs C4_WRONG_PROFILE

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 108 | 0.4630 | [0.3718, 0.5567] |
| lo_moderately_shorter | 197 | 0.5330 | [0.4634, 0.6014] |
| similar | 129 | 0.6124 | [0.5262, 0.6921] |
| lo_moderately_longer | 210 | 0.7238 | [0.6597, 0.7799] |
| lo_much_longer | 72 | 0.7639 | [0.6540, 0.8470] |

### C4 vs C4_shuffled

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 12 | 0.3333 | [0.1381, 0.6094] |
| lo_moderately_shorter | 104 | 0.4712 | [0.3780, 0.5664] |
| similar | 86 | 0.5465 | [0.4416, 0.6475] |
| lo_moderately_longer | 104 | 0.5962 | [0.5001, 0.6854] |
| lo_much_longer | 14 | 0.2857 | [0.1172, 0.5465] |

### C4 vs C5

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 31 | 0.3871 | [0.2373, 0.5618] |
| lo_moderately_shorter | 80 | 0.4750 | [0.3692, 0.5830] |
| similar | 75 | 0.5867 | [0.4737, 0.6912] |
| lo_moderately_longer | 67 | 0.8209 | [0.7125, 0.8945] |
| lo_much_longer | 25 | 1.0000 | [0.8668, 1.0000] |

### C4 vs C5_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 21 | 0.2857 | [0.1381, 0.4996] |
| lo_moderately_shorter | 102 | 0.2451 | [0.1719, 0.3368] |
| similar | 64 | 0.3750 | [0.2667, 0.4975] |
| lo_moderately_longer | 88 | 0.6136 | [0.5092, 0.7086] |
| lo_much_longer | 10 | 0.5000 | [0.2366, 0.7634] |

### C4 vs C5_NONPUBLIC

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 69 | 0.5797 | [0.4621, 0.6889] |
| lo_moderately_shorter | 123 | 0.5935 | [0.5051, 0.6762] |
| similar | 51 | 0.8235 | [0.6975, 0.9043] |
| lo_moderately_longer | 96 | 0.8021 | [0.7114, 0.8695] |
| lo_much_longer | 21 | 0.9048 | [0.7109, 0.9735] |

### C4 vs C5_NONPUBLIC_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 42 | 0.3571 | [0.2299, 0.5083] |
| lo_moderately_shorter | 99 | 0.5758 | [0.4774, 0.6685] |
| similar | 90 | 0.6444 | [0.5415, 0.7356] |
| lo_moderately_longer | 117 | 0.6068 | [0.5163, 0.6906] |
| lo_much_longer | 12 | 0.7500 | [0.4677, 0.9111] |

### C4 vs C_GENERIC_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 117 | 0.3932 | [0.3094, 0.4837] |
| lo_moderately_shorter | 258 | 0.5388 | [0.4778, 0.5986] |
| similar | 159 | 0.6101 | [0.5325, 0.6824] |
| lo_moderately_longer | 137 | 0.6861 | [0.6042, 0.7579] |
| lo_much_longer | 45 | 0.6000 | [0.4545, 0.7298] |

### C4 vs L3

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 57 | 0.5614 | [0.4328, 0.6823] |
| lo_moderately_shorter | 84 | 0.6905 | [0.5851, 0.7792] |
| similar | 84 | 0.7143 | [0.6100, 0.7998] |
| lo_moderately_longer | 105 | 0.7810 | [0.6927, 0.8494] |
| lo_much_longer | 27 | 0.8519 | [0.6752, 0.9408] |

### C5_CONTRACT vs C5_NONPUBLIC

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 69 | 0.6232 | [0.5052, 0.7282] |
| lo_moderately_shorter | 93 | 0.6237 | [0.5221, 0.7154] |
| similar | 72 | 0.8056 | [0.6997, 0.8805] |
| lo_moderately_longer | 98 | 0.8878 | [0.8101, 0.9362] |
| lo_much_longer | 27 | 0.7407 | [0.5532, 0.8683] |

### C5_CONTRACT vs C5_NONPUBLIC_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 33 | 0.4242 | [0.2724, 0.5919] |
| lo_moderately_shorter | 106 | 0.5566 | [0.4617, 0.6475] |
| similar | 99 | 0.7273 | [0.6323, 0.8053] |
| lo_moderately_longer | 94 | 0.6915 | [0.5921, 0.7758] |
| lo_much_longer | 24 | 0.5417 | [0.3507, 0.7211] |

### C5_CONTRACT vs L1

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 45 | 0.4444 | [0.3094, 0.5882] |
| lo_moderately_shorter | 89 | 0.7079 | [0.6064, 0.7922] |
| similar | 84 | 0.7381 | [0.6352, 0.8202] |
| lo_moderately_longer | 114 | 0.7018 | [0.6123, 0.7780] |
| lo_much_longer | 27 | 0.8519 | [0.6752, 0.9408] |

### C5_CONTRACT vs L3

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 51 | 0.7059 | [0.5700, 0.8129] |
| lo_moderately_shorter | 75 | 0.7467 | [0.6379, 0.8314] |
| similar | 111 | 0.7207 | [0.6310, 0.7957] |
| lo_moderately_longer | 90 | 0.7556 | [0.6575, 0.8327] |
| lo_much_longer | 29 | 0.9655 | [0.8282, 0.9939] |

### C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 18 | 0.1111 | [0.0310, 0.3280] |
| lo_moderately_shorter | 110 | 0.2273 | [0.1589, 0.3140] |
| similar | 69 | 0.1304 | [0.0702, 0.2297] |
| lo_moderately_longer | 110 | 0.3182 | [0.2385, 0.4101] |
| lo_much_longer | 51 | 0.5098 | [0.3768, 0.6414] |

### C5 vs C5_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 24 | 0.2500 | [0.1200, 0.4490] |
| lo_moderately_shorter | 90 | 0.1444 | [0.0864, 0.2316] |
| similar | 73 | 0.1918 | [0.1178, 0.2966] |
| lo_moderately_longer | 78 | 0.3333 | [0.2387, 0.4436] |
| lo_much_longer | 22 | 0.4545 | [0.2692, 0.6534] |

### C5 vs C5_NONPUBLIC

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 45 | 0.4889 | [0.3496, 0.6300] |
| lo_moderately_shorter | 113 | 0.5752 | [0.4831, 0.6624] |
| similar | 87 | 0.6207 | [0.5157, 0.7155] |
| lo_moderately_longer | 73 | 0.7260 | [0.6144, 0.8151] |
| lo_much_longer | 39 | 0.7692 | [0.6166, 0.8735] |

### C5 vs C_GENERIC_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 24 | 0.1667 | [0.0668, 0.3585] |
| lo_moderately_shorter | 135 | 0.3778 | [0.3004, 0.4619] |
| similar | 54 | 0.4444 | [0.3200, 0.5762] |
| lo_moderately_longer | 99 | 0.5354 | [0.4376, 0.6304] |
| lo_much_longer | 48 | 0.7292 | [0.5900, 0.8343] |

### C5 vs L1

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 21 | 0.3810 | [0.2075, 0.5912] |
| lo_moderately_shorter | 126 | 0.4683 | [0.3834, 0.5550] |
| similar | 84 | 0.5476 | [0.4414, 0.6496] |
| lo_moderately_longer | 93 | 0.6452 | [0.5439, 0.7349] |
| lo_much_longer | 36 | 0.6389 | [0.4758, 0.7752] |

### C5 vs L2

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 36 | 0.3056 | [0.1800, 0.4686] |
| lo_moderately_shorter | 78 | 0.5385 | [0.4286, 0.6447] |
| similar | 78 | 0.5897 | [0.4789, 0.6922] |
| lo_moderately_longer | 123 | 0.7724 | [0.6907, 0.8375] |
| lo_much_longer | 45 | 0.6000 | [0.4545, 0.7298] |

### C5 vs L3

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 33 | 0.3030 | [0.1738, 0.4734] |
| lo_moderately_shorter | 108 | 0.4074 | [0.3195, 0.5017] |
| similar | 83 | 0.6386 | [0.5312, 0.7337] |
| lo_moderately_longer | 90 | 0.5778 | [0.4746, 0.6746] |
| lo_much_longer | 42 | 0.8333 | [0.6940, 0.9168] |

### L1 vs L2

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 36 | 0.3056 | [0.1800, 0.4686] |
| lo_moderately_shorter | 73 | 0.4247 | [0.3178, 0.5390] |
| similar | 80 | 0.5500 | [0.4412, 0.6542] |
| lo_moderately_longer | 140 | 0.5357 | [0.4533, 0.6163] |
| lo_much_longer | 26 | 0.7308 | [0.5392, 0.8630] |

### L2 vs L3

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 42 | 0.2619 | [0.1530, 0.4107] |
| lo_moderately_shorter | 112 | 0.2500 | [0.1790, 0.3376] |
| similar | 64 | 0.2656 | [0.1730, 0.3848] |
| lo_moderately_longer | 111 | 0.3874 | [0.3020, 0.4803] |
| lo_much_longer | 24 | 0.6250 | [0.4271, 0.7884] |

## AB/BA counterbalanced rejudge (Phase 1)

Coverage: **13274 swapped-order rejudge records** vs 14733 total originals. Each AB/BA-matched pair has both an original and a swap judgment from the same judge.

For each headline pair, `position_consistent` = judgments agree on which condition wins regardless of slot (real condition preference); `position_flip` = original and swap disagree (same slot wins both times = slot effect). `position_controlled_lo_win` averages across orders and is the position-bias-corrected headline. `headline_survives_swap` flags whether the controlled CI excludes 0.5 on the same side as the original.

| pair | n_AB/BA | orig lo_win | swap lo_win | controlled lo_win | Wilson CI95 | Bootstrap CI95 | flip rate | survives? |
|---|---:|---:|---:|---:|---|---|---:|---|
| C0 vs C4_WRONG_PROFILE | 717 | 0.346 | 0.259 | 0.304 | [0.272, 0.339] | [0.263, 0.345] | 0.198 | ✓ |
| C0 vs C_GENERIC_CONTRACT | 717 | 0.278 | 0.175 | 0.227 | [0.197, 0.258] | [0.191, 0.265] | 0.178 | ✓ |
| C1_padded vs C4 | 320 | 0.319 | 0.434 | 0.377 | [0.324, 0.429] | [0.317, 0.439] | 0.203 | ✓ |
| C3 vs C4_WRONG_PROFILE | 717 | 0.632 | 0.523 | 0.577 | [0.541, 0.613] | [0.534, 0.620] | 0.245 | ✓ |
| C3 vs C5_CONTRACT | 288 | 0.428 | 0.573 | 0.501 | [0.443, 0.557] | [0.436, 0.566] | 0.330 | **⚠ NO** |
| C3 vs C5_NONPUBLIC | 360 | 0.724 | 0.610 | 0.667 | [0.616, 0.713] | [0.606, 0.722] | 0.253 | ✓ |
| C3 vs C5_NONPUBLIC_CONTRACT | 360 | 0.599 | 0.343 | 0.471 | [0.421, 0.524] | [0.414, 0.528] | 0.364 | **⚠ NO** |
| C3 vs C_GENERIC_CONTRACT | 717 | 0.540 | 0.393 | 0.467 | [0.431, 0.504] | [0.426, 0.509] | 0.284 | **⚠ NO** |
| C3 vs L1 | 360 | 0.697 | 0.497 | 0.597 | [0.546, 0.647] | [0.533, 0.660] | 0.278 | ✓ |
| C3 vs L2 | 360 | 0.744 | 0.582 | 0.662 | [0.611, 0.708] | [0.600, 0.722] | 0.222 | ✓ |
| C4_WRONG_PROFILE vs C5 | 360 | 0.429 | 0.625 | 0.527 | [0.476, 0.579] | [0.464, 0.589] | 0.297 | **⚠ NO** |
| C4 vs C4_WRONG_PROFILE | 717 | 0.616 | 0.506 | 0.561 | [0.524, 0.597] | [0.515, 0.606] | 0.237 | ✓ |
| C4 vs C4_shuffled | 320 | 0.519 | 0.637 | 0.578 | [0.523, 0.631] | [0.522, 0.637] | 0.269 | ✓ |
| C4 vs C5 | 280 | 0.626 | 0.736 | 0.680 | [0.622, 0.731] | [0.615, 0.744] | 0.207 | ✓ |
| C4 vs C5_CONTRACT | 288 | 0.400 | 0.562 | 0.482 | [0.425, 0.540] | [0.413, 0.548] | 0.306 | **⚠ NO** |
| C4 vs C5_NONPUBLIC | 360 | 0.697 | 0.557 | 0.627 | [0.577, 0.676] | [0.555, 0.692] | 0.200 | ✓ |
| C4 vs C5_NONPUBLIC_CONTRACT | 360 | 0.583 | 0.366 | 0.475 | [0.424, 0.527] | [0.419, 0.534] | 0.319 | **⚠ NO** |
| C4 vs C_GENERIC_CONTRACT | 717 | 0.563 | 0.432 | 0.498 | [0.461, 0.534] | [0.454, 0.541] | 0.282 | **⚠ NO** |
| C4 vs L3 | 357 | 0.714 | 0.546 | 0.630 | [0.579, 0.679] | [0.566, 0.689] | 0.241 | ✓ |
| C5_CONTRACT vs C5_NONPUBLIC | 360 | 0.741 | 0.597 | 0.669 | [0.619, 0.716] | [0.609, 0.729] | 0.244 | ✓ |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 360 | 0.626 | 0.389 | 0.507 | [0.454, 0.557] | [0.447, 0.566] | 0.350 | **⚠ NO** |
| C5_CONTRACT vs L1 | 360 | 0.691 | 0.525 | 0.608 | [0.557, 0.657] | [0.549, 0.666] | 0.289 | ✓ |
| C5_CONTRACT vs L3 | 357 | 0.753 | 0.542 | 0.647 | [0.596, 0.695] | [0.581, 0.706] | 0.288 | ✓ |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 360 | 0.271 | 0.409 | 0.341 | [0.295, 0.392] | [0.283, 0.406] | 0.258 | ✓ |
| C5 vs C5_CONTRACT | 288 | 0.240 | 0.403 | 0.323 | [0.272, 0.379] | [0.267, 0.383] | 0.243 | ✓ |
| C5 vs C5_NONPUBLIC | 360 | 0.627 | 0.429 | 0.528 | [0.476, 0.579] | [0.469, 0.585] | 0.311 | **⚠ NO** |
| C5 vs C_GENERIC_CONTRACT | 360 | 0.464 | 0.312 | 0.388 | [0.340, 0.440] | [0.326, 0.448] | 0.267 | ✓ |
| C5 vs L1 | 360 | 0.544 | 0.342 | 0.443 | [0.394, 0.496] | [0.386, 0.501] | 0.314 | **⚠ NO** |
| C5 vs L2 | 360 | 0.614 | 0.425 | 0.519 | [0.468, 0.571] | [0.463, 0.579] | 0.350 | **⚠ NO** |
| C5 vs L3 | 357 | 0.545 | 0.342 | 0.443 | [0.392, 0.494] | [0.382, 0.503] | 0.300 | **⚠ NO** |
| L1 vs L2 | 360 | 0.507 | 0.619 | 0.562 | [0.509, 0.612] | [0.506, 0.618] | 0.344 | ✓ |
| L2 vs L3 | 357 | 0.323 | 0.520 | 0.422 | [0.373, 0.475] | [0.364, 0.478] | 0.314 | ✓ |

**Bootstrap CI** is cluster-resampled by (persona × scenario × author) — the matched-pair appropriate estimator. Replaces the Wilson interval as the canonical CI for the controlled rate (Wilson kept side-by-side for continuity). 2026-05-17 review fix.

### AB/BA per-judge breakdown — slot-B advantage

Decomposes the position-bias finding by judge. `slot_B_adv` is (swap_lo_win − orig_lo_win); positive = slot B favored (i.e., the lower-numbered condition wins more when placed in slot B). Methodology contribution rests on per-judge structure being non-uniform; values below confirm: GPT-5.5 and Opus show strong slot-B preference; GPT-5.4 has negligible-to-negative effect.

| pair | judge | n | orig lo | swap lo | controlled lo | Bootstrap CI | slot_B_adv |
|---|---|---:|---:|---:|---:|---|---:|
| C0 vs C4_WRONG_PROFILE | gpt-5.4 | 239 | 0.343 | 0.360 | 0.351 | [0.297, 0.406] | +0.017 |
| C0 vs C4_WRONG_PROFILE | gpt-5.5 | 239 | 0.458 | 0.297 | 0.378 | [0.323, 0.432] | -0.161 |
| C0 vs C4_WRONG_PROFILE | opus | 239 | 0.236 | 0.118 | 0.182 | [0.147, 0.221] | -0.118 |
| C0 vs C_GENERIC_CONTRACT | gpt-5.4 | 239 | 0.268 | 0.272 | 0.270 | [0.218, 0.320] | +0.004 |
| C0 vs C_GENERIC_CONTRACT | gpt-5.5 | 239 | 0.289 | 0.151 | 0.220 | [0.174, 0.266] | -0.138 |
| C0 vs C_GENERIC_CONTRACT | opus | 239 | 0.277 | 0.101 | 0.190 | [0.152, 0.231] | -0.176 |
| C1_padded vs C4 | gpt-5.4 | 160 | 0.356 | 0.388 | 0.372 | [0.306, 0.438] | +0.031 |
| C1_padded vs C4 | gpt-5.5 | 160 | 0.281 | 0.481 | 0.381 | [0.316, 0.447] | +0.200 |
| C3 vs C4_WRONG_PROFILE | gpt-5.4 | 239 | 0.565 | 0.531 | 0.548 | [0.496, 0.609] | -0.034 |
| C3 vs C4_WRONG_PROFILE | gpt-5.5 | 239 | 0.678 | 0.515 | 0.596 | [0.540, 0.651] | -0.163 |
| C3 vs C4_WRONG_PROFILE | opus | 239 | 0.653 | 0.523 | 0.588 | [0.538, 0.640] | -0.130 |
| C3 vs C5_CONTRACT | gpt-5.4 | 84 | 0.571 | 0.536 | 0.554 | [0.470, 0.637] | -0.036 |
| C3 vs C5_CONTRACT | gpt-5.5 | 84 | 0.417 | 0.667 | 0.542 | [0.446, 0.631] | +0.250 |
| C3 vs C5_CONTRACT | opus | 120 | 0.330 | 0.534 | 0.435 | [0.369, 0.504] | +0.203 |
| C3 vs C5_NONPUBLIC | gpt-5.4 | 120 | 0.633 | 0.642 | 0.637 | [0.567, 0.713] | +0.008 |
| C3 vs C5_NONPUBLIC | gpt-5.5 | 120 | 0.758 | 0.542 | 0.650 | [0.579, 0.721] | -0.217 |
| C3 vs C5_NONPUBLIC | opus | 120 | 0.781 | 0.647 | 0.713 | [0.652, 0.771] | -0.135 |
| C3 vs C5_NONPUBLIC_CONTRACT | gpt-5.4 | 120 | 0.508 | 0.383 | 0.446 | [0.371, 0.521] | -0.125 |
| C3 vs C5_NONPUBLIC_CONTRACT | gpt-5.5 | 120 | 0.642 | 0.317 | 0.479 | [0.408, 0.554] | -0.325 |
| C3 vs C5_NONPUBLIC_CONTRACT | opus | 120 | 0.647 | 0.328 | 0.487 | [0.419, 0.550] | -0.319 |
| C3 vs C_GENERIC_CONTRACT | gpt-5.4 | 239 | 0.435 | 0.431 | 0.433 | [0.379, 0.489] | -0.004 |
| C3 vs C_GENERIC_CONTRACT | gpt-5.5 | 239 | 0.556 | 0.322 | 0.439 | [0.387, 0.492] | -0.234 |
| C3 vs C_GENERIC_CONTRACT | opus | 239 | 0.630 | 0.427 | 0.528 | [0.479, 0.579] | -0.203 |
| C3 vs L1 | gpt-5.4 | 120 | 0.633 | 0.550 | 0.592 | [0.512, 0.671] | -0.083 |
| C3 vs L1 | gpt-5.5 | 120 | 0.758 | 0.483 | 0.621 | [0.546, 0.696] | -0.275 |
| C3 vs L1 | opus | 120 | 0.700 | 0.458 | 0.579 | [0.508, 0.646] | -0.242 |
| C3 vs L2 | gpt-5.4 | 120 | 0.700 | 0.625 | 0.662 | [0.592, 0.733] | -0.075 |
| C3 vs L2 | gpt-5.5 | 120 | 0.742 | 0.583 | 0.662 | [0.588, 0.733] | -0.158 |
| C3 vs L2 | opus | 120 | 0.790 | 0.538 | 0.662 | [0.590, 0.729] | -0.252 |
| C4_WRONG_PROFILE vs C5 | gpt-5.4 | 120 | 0.442 | 0.508 | 0.475 | [0.396, 0.550] | +0.067 |
| C4_WRONG_PROFILE vs C5 | gpt-5.5 | 120 | 0.392 | 0.633 | 0.512 | [0.433, 0.592] | +0.242 |
| C4_WRONG_PROFILE vs C5 | opus | 120 | 0.454 | 0.733 | 0.594 | [0.527, 0.665] | +0.280 |
| C4 vs C4_WRONG_PROFILE | gpt-5.4 | 239 | 0.552 | 0.548 | 0.550 | [0.494, 0.609] | -0.004 |
| C4 vs C4_WRONG_PROFILE | gpt-5.5 | 239 | 0.653 | 0.489 | 0.571 | [0.517, 0.625] | -0.163 |
| C4 vs C4_WRONG_PROFILE | opus | 239 | 0.643 | 0.481 | 0.562 | [0.511, 0.613] | -0.162 |
| C4 vs C4_shuffled | gpt-5.4 | 160 | 0.600 | 0.575 | 0.588 | [0.522, 0.653] | -0.025 |
| C4 vs C4_shuffled | gpt-5.5 | 160 | 0.438 | 0.700 | 0.569 | [0.506, 0.631] | +0.263 |
| C4 vs C5 | gpt-5.4 | 80 | 0.662 | 0.700 | 0.681 | [0.588, 0.775] | +0.037 |
| C4 vs C5 | gpt-5.5 | 80 | 0.613 | 0.750 | 0.681 | [0.594, 0.769] | +0.138 |
| C4 vs C5 | opus | 120 | 0.610 | 0.750 | 0.679 | [0.613, 0.742] | +0.140 |
| C4 vs C5_CONTRACT | gpt-5.4 | 84 | 0.464 | 0.488 | 0.476 | [0.381, 0.571] | +0.024 |
| C4 vs C5_CONTRACT | gpt-5.5 | 84 | 0.345 | 0.595 | 0.470 | [0.381, 0.559] | +0.250 |
| C4 vs C5_CONTRACT | opus | 120 | 0.393 | 0.592 | 0.494 | [0.427, 0.558] | +0.199 |
| C4 vs C5_NONPUBLIC | gpt-5.4 | 120 | 0.642 | 0.597 | 0.619 | [0.540, 0.698] | -0.045 |
| C4 vs C5_NONPUBLIC | gpt-5.5 | 120 | 0.658 | 0.525 | 0.592 | [0.512, 0.671] | -0.133 |
| C4 vs C5_NONPUBLIC | opus | 120 | 0.792 | 0.551 | 0.671 | [0.602, 0.740] | -0.241 |
| C4 vs C5_NONPUBLIC_CONTRACT | gpt-5.4 | 120 | 0.508 | 0.525 | 0.517 | [0.438, 0.600] | +0.017 |
| C4 vs C5_NONPUBLIC_CONTRACT | gpt-5.5 | 120 | 0.600 | 0.283 | 0.442 | [0.375, 0.508] | -0.317 |
| C4 vs C5_NONPUBLIC_CONTRACT | opus | 120 | 0.642 | 0.288 | 0.467 | [0.402, 0.533] | -0.353 |
| C4 vs C_GENERIC_CONTRACT | gpt-5.4 | 239 | 0.452 | 0.452 | 0.452 | [0.395, 0.508] | +0.000 |
| C4 vs C_GENERIC_CONTRACT | gpt-5.5 | 239 | 0.546 | 0.347 | 0.447 | [0.393, 0.504] | -0.199 |
| C4 vs C_GENERIC_CONTRACT | opus | 239 | 0.690 | 0.498 | 0.594 | [0.547, 0.643] | -0.193 |
| C4 vs L3 | gpt-5.4 | 119 | 0.647 | 0.630 | 0.639 | [0.567, 0.714] | -0.017 |
| C4 vs L3 | gpt-5.5 | 119 | 0.706 | 0.487 | 0.597 | [0.525, 0.668] | -0.218 |
| C4 vs L3 | opus | 119 | 0.790 | 0.521 | 0.655 | [0.584, 0.727] | -0.269 |
| C5_CONTRACT vs C5_NONPUBLIC | gpt-5.4 | 120 | 0.683 | 0.650 | 0.667 | [0.592, 0.742] | -0.033 |
| C5_CONTRACT vs C5_NONPUBLIC | gpt-5.5 | 120 | 0.758 | 0.583 | 0.671 | [0.596, 0.742] | -0.175 |
| C5_CONTRACT vs C5_NONPUBLIC | opus | 120 | 0.781 | 0.558 | 0.669 | [0.600, 0.735] | -0.223 |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | gpt-5.4 | 120 | 0.550 | 0.492 | 0.521 | [0.442, 0.604] | -0.058 |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | gpt-5.5 | 120 | 0.642 | 0.358 | 0.500 | [0.425, 0.575] | -0.283 |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | opus | 120 | 0.690 | 0.317 | 0.500 | [0.440, 0.560] | -0.373 |
| C5_CONTRACT vs L1 | gpt-5.4 | 120 | 0.567 | 0.592 | 0.579 | [0.504, 0.658] | +0.025 |
| C5_CONTRACT vs L1 | gpt-5.5 | 120 | 0.750 | 0.492 | 0.621 | [0.550, 0.692] | -0.258 |
| C5_CONTRACT vs L1 | opus | 120 | 0.756 | 0.491 | 0.623 | [0.558, 0.688] | -0.265 |
| C5_CONTRACT vs L3 | gpt-5.4 | 119 | 0.681 | 0.647 | 0.664 | [0.588, 0.740] | -0.034 |
| C5_CONTRACT vs L3 | gpt-5.5 | 119 | 0.765 | 0.496 | 0.630 | [0.559, 0.698] | -0.269 |
| C5_CONTRACT vs L3 | opus | 119 | 0.814 | 0.483 | 0.647 | [0.584, 0.714] | -0.331 |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | gpt-5.4 | 120 | 0.358 | 0.367 | 0.362 | [0.283, 0.438] | +0.008 |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | gpt-5.5 | 120 | 0.225 | 0.517 | 0.371 | [0.304, 0.442] | +0.292 |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | opus | 120 | 0.229 | 0.342 | 0.290 | [0.229, 0.352] | +0.113 |
| C5 vs C5_CONTRACT | gpt-5.4 | 84 | 0.286 | 0.398 | 0.342 | [0.256, 0.431] | +0.112 |
| C5 vs C5_CONTRACT | gpt-5.5 | 84 | 0.107 | 0.417 | 0.262 | [0.196, 0.339] | +0.309 |
| C5 vs C5_CONTRACT | opus | 120 | 0.302 | 0.397 | 0.352 | [0.283, 0.425] | +0.094 |
| C5 vs C5_NONPUBLIC | gpt-5.4 | 120 | 0.525 | 0.558 | 0.542 | [0.463, 0.621] | +0.033 |
| C5 vs C5_NONPUBLIC | gpt-5.5 | 120 | 0.667 | 0.367 | 0.517 | [0.442, 0.592] | -0.300 |
| C5 vs C5_NONPUBLIC | opus | 120 | 0.692 | 0.361 | 0.525 | [0.460, 0.592] | -0.331 |
| C5 vs C_GENERIC_CONTRACT | gpt-5.4 | 120 | 0.383 | 0.400 | 0.392 | [0.321, 0.471] | +0.017 |
| C5 vs C_GENERIC_CONTRACT | gpt-5.5 | 120 | 0.483 | 0.250 | 0.367 | [0.296, 0.442] | -0.233 |
| C5 vs C_GENERIC_CONTRACT | opus | 120 | 0.525 | 0.286 | 0.406 | [0.340, 0.475] | -0.239 |
| C5 vs L1 | gpt-5.4 | 120 | 0.475 | 0.508 | 0.492 | [0.417, 0.571] | +0.033 |
| C5 vs L1 | gpt-5.5 | 120 | 0.600 | 0.292 | 0.446 | [0.371, 0.517] | -0.308 |
| C5 vs L1 | opus | 120 | 0.558 | 0.225 | 0.392 | [0.325, 0.463] | -0.333 |
| C5 vs L2 | gpt-5.4 | 120 | 0.533 | 0.533 | 0.533 | [0.463, 0.604] | +0.000 |
| C5 vs L2 | gpt-5.5 | 120 | 0.650 | 0.383 | 0.517 | [0.438, 0.588] | -0.267 |
| C5 vs L2 | opus | 120 | 0.658 | 0.358 | 0.508 | [0.442, 0.575] | -0.300 |
| C5 vs L3 | gpt-5.4 | 119 | 0.445 | 0.437 | 0.441 | [0.361, 0.517] | -0.008 |
| C5 vs L3 | gpt-5.5 | 119 | 0.597 | 0.311 | 0.454 | [0.382, 0.529] | -0.286 |
| C5 vs L3 | opus | 119 | 0.593 | 0.277 | 0.435 | [0.363, 0.502] | -0.316 |
| L1 vs L2 | gpt-5.4 | 120 | 0.575 | 0.508 | 0.542 | [0.471, 0.617] | -0.067 |
| L1 vs L2 | gpt-5.5 | 120 | 0.450 | 0.700 | 0.575 | [0.500, 0.646] | +0.250 |
| L1 vs L2 | opus | 120 | 0.496 | 0.650 | 0.571 | [0.506, 0.637] | +0.154 |
| L2 vs L3 | gpt-5.4 | 119 | 0.412 | 0.445 | 0.429 | [0.344, 0.504] | +0.034 |
| L2 vs L3 | gpt-5.5 | 119 | 0.261 | 0.546 | 0.403 | [0.336, 0.471] | +0.286 |
| L2 vs L3 | opus | 119 | 0.296 | 0.570 | 0.435 | [0.372, 0.502] | +0.275 |

### AB/BA per-cell decomposition by judge

For each (pair, judge), each AB/BA-matched pair falls into one of four buckets: `condition_lo_stable` (lo wins both orders), `condition_hi_stable` (hi wins both), `slot_A_stable` (slot A wins both — slot effect favoring A), `slot_B_stable` (slot B wins both — slot effect favoring B). Plus `either_tie` for tied judgments.

| pair | judge | cond_lo_stable | cond_hi_stable | slot_A_stable | slot_B_stable | either_tie |
|---|---|---:|---:|---:|---:|---:|
| C0 vs C4_WRONG_PROFILE | gpt-5.4 | 62 | 133 | 24 | 20 | 0 |
| C0 vs C4_WRONG_PROFILE | gpt-5.5 | 69 | 127 | 2 | 40 | 1 |
| C0 vs C4_WRONG_PROFILE | opus | 13 | 163 | 14 | 42 | 7 |
| C0 vs C_GENERIC_CONTRACT | gpt-5.4 | 49 | 159 | 16 | 15 | 0 |
| C0 vs C_GENERIC_CONTRACT | gpt-5.5 | 32 | 166 | 4 | 37 | 0 |
| C0 vs C_GENERIC_CONTRACT | opus | 17 | 164 | 7 | 49 | 2 |
| C1_padded vs C4 | gpt-5.4 | 45 | 86 | 12 | 17 | 0 |
| C1_padded vs C4 | gpt-5.5 | 43 | 81 | 2 | 34 | 0 |
| C3 vs C4_WRONG_PROFILE | gpt-5.4 | 106 | 83 | 21 | 29 | 0 |
| C3 vs C4_WRONG_PROFILE | gpt-5.5 | 117 | 71 | 6 | 45 | 0 |
| C3 vs C4_WRONG_PROFILE | opus | 103 | 61 | 22 | 53 | 0 |
| C3 vs C5_CONTRACT | gpt-5.4 | 33 | 24 | 15 | 12 | 0 |
| C3 vs C5_CONTRACT | gpt-5.5 | 34 | 27 | 1 | 22 | 0 |
| C3 vs C5_CONTRACT | opus | 26 | 42 | 12 | 33 | 7 |
| C3 vs C5_NONPUBLIC | gpt-5.4 | 66 | 33 | 11 | 10 | 0 |
| C3 vs C5_NONPUBLIC | gpt-5.5 | 63 | 27 | 2 | 28 | 0 |
| C3 vs C5_NONPUBLIC | opus | 64 | 14 | 12 | 28 | 2 |
| C3 vs C5_NONPUBLIC_CONTRACT | gpt-5.4 | 36 | 49 | 10 | 25 | 0 |
| C3 vs C5_NONPUBLIC_CONTRACT | gpt-5.5 | 35 | 40 | 3 | 42 | 0 |
| C3 vs C5_NONPUBLIC_CONTRACT | opus | 32 | 35 | 7 | 44 | 2 |
| C3 vs C_GENERIC_CONTRACT | gpt-5.4 | 79 | 111 | 24 | 25 | 0 |
| C3 vs C_GENERIC_CONTRACT | gpt-5.5 | 72 | 101 | 5 | 61 | 0 |
| C3 vs C_GENERIC_CONTRACT | opus | 81 | 68 | 20 | 69 | 1 |
| C3 vs L1 | gpt-5.4 | 60 | 38 | 6 | 16 | 0 |
| C3 vs L1 | gpt-5.5 | 58 | 29 | 0 | 33 | 0 |
| C3 vs L1 | opus | 47 | 28 | 8 | 37 | 0 |
| C3 vs L2 | gpt-5.4 | 67 | 28 | 8 | 17 | 0 |
| C3 vs L2 | gpt-5.5 | 69 | 30 | 1 | 20 | 0 |
| C3 vs L2 | opus | 62 | 22 | 2 | 32 | 2 |
| C4_WRONG_PROFILE vs C5 | gpt-5.4 | 41 | 47 | 12 | 20 | 0 |
| C4_WRONG_PROFILE vs C5 | gpt-5.5 | 46 | 43 | 1 | 30 | 0 |
| C4_WRONG_PROFILE vs C5 | opus | 49 | 26 | 5 | 39 | 1 |
| C4 vs C4_WRONG_PROFILE | gpt-5.4 | 111 | 87 | 20 | 21 | 0 |
| C4 vs C4_WRONG_PROFILE | gpt-5.5 | 112 | 78 | 5 | 44 | 0 |
| C4 vs C4_WRONG_PROFILE | opus | 94 | 64 | 21 | 59 | 1 |
| C4 vs C4_shuffled | gpt-5.4 | 76 | 48 | 20 | 16 | 0 |
| C4 vs C4_shuffled | gpt-5.5 | 66 | 44 | 3 | 47 | 0 |
| C4 vs C5 | gpt-5.4 | 50 | 21 | 3 | 6 | 0 |
| C4 vs C5 | gpt-5.5 | 48 | 19 | 1 | 12 | 0 |
| C4 vs C5 | opus | 62 | 20 | 10 | 26 | 2 |
| C4 vs C5_CONTRACT | gpt-5.4 | 32 | 36 | 7 | 9 | 0 |
| C4 vs C5_CONTRACT | gpt-5.5 | 28 | 33 | 1 | 22 | 0 |
| C4 vs C5_CONTRACT | opus | 33 | 35 | 13 | 36 | 3 |
| C4 vs C5_NONPUBLIC | gpt-5.4 | 65 | 36 | 6 | 12 | 1 |
| C4 vs C5_NONPUBLIC | gpt-5.5 | 61 | 39 | 2 | 18 | 0 |
| C4 vs C5_NONPUBLIC | opus | 62 | 22 | 3 | 31 | 2 |
| C4 vs C5_NONPUBLIC_CONTRACT | gpt-5.4 | 54 | 50 | 9 | 7 | 0 |
| C4 vs C5_NONPUBLIC_CONTRACT | gpt-5.5 | 30 | 44 | 4 | 42 | 0 |
| C4 vs C5_NONPUBLIC_CONTRACT | opus | 28 | 37 | 6 | 47 | 2 |
| C4 vs C_GENERIC_CONTRACT | gpt-5.4 | 83 | 106 | 25 | 25 | 0 |
| C4 vs C_GENERIC_CONTRACT | gpt-5.5 | 75 | 100 | 8 | 55 | 1 |
| C4 vs C_GENERIC_CONTRACT | opus | 96 | 52 | 22 | 67 | 2 |
| C4 vs L3 | gpt-5.4 | 64 | 31 | 11 | 13 | 0 |
| C4 vs L3 | gpt-5.5 | 56 | 33 | 2 | 28 | 0 |
| C4 vs L3 | opus | 62 | 25 | 0 | 32 | 0 |
| C5_CONTRACT vs C5_NONPUBLIC | gpt-5.4 | 67 | 27 | 11 | 15 | 0 |
| C5_CONTRACT vs C5_NONPUBLIC | gpt-5.5 | 69 | 28 | 1 | 22 | 0 |
| C5_CONTRACT vs C5_NONPUBLIC | opus | 60 | 20 | 6 | 33 | 1 |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | gpt-5.4 | 48 | 43 | 11 | 18 | 0 |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | gpt-5.5 | 43 | 43 | 0 | 34 | 0 |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | opus | 27 | 26 | 10 | 53 | 4 |
| C5_CONTRACT vs L1 | gpt-5.4 | 58 | 39 | 13 | 10 | 0 |
| C5_CONTRACT vs L1 | gpt-5.5 | 57 | 28 | 2 | 33 | 0 |
| C5_CONTRACT vs L1 | opus | 50 | 21 | 8 | 38 | 3 |
| C5_CONTRACT vs L3 | gpt-5.4 | 69 | 30 | 8 | 12 | 0 |
| C5_CONTRACT vs L3 | gpt-5.5 | 57 | 26 | 2 | 34 | 0 |
| C5_CONTRACT vs L3 | opus | 53 | 18 | 4 | 43 | 1 |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | gpt-5.4 | 34 | 67 | 9 | 10 | 0 |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | gpt-5.5 | 25 | 56 | 2 | 37 | 0 |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | opus | 16 | 65 | 11 | 24 | 4 |
| C5 vs C5_CONTRACT | gpt-5.4 | 20 | 47 | 3 | 13 | 1 |
| C5 vs C5_CONTRACT | gpt-5.5 | 9 | 49 | 0 | 26 | 0 |
| C5 vs C5_CONTRACT | opus | 26 | 62 | 8 | 20 | 4 |
| C5 vs C5_NONPUBLIC | gpt-5.4 | 52 | 42 | 15 | 11 | 0 |
| C5 vs C5_NONPUBLIC | gpt-5.5 | 44 | 40 | 0 | 36 | 0 |
| C5 vs C5_NONPUBLIC | opus | 37 | 29 | 6 | 44 | 4 |
| C5 vs C_GENERIC_CONTRACT | gpt-5.4 | 35 | 61 | 13 | 11 | 0 |
| C5 vs C_GENERIC_CONTRACT | gpt-5.5 | 29 | 61 | 1 | 29 | 0 |
| C5 vs C_GENERIC_CONTRACT | opus | 27 | 50 | 7 | 35 | 1 |
| C5 vs L1 | gpt-5.4 | 45 | 47 | 16 | 12 | 0 |
| C5 vs L1 | gpt-5.5 | 34 | 47 | 1 | 38 | 0 |
| C5 vs L1 | opus | 24 | 50 | 3 | 43 | 0 |
| C5 vs L2 | gpt-5.4 | 44 | 36 | 20 | 20 | 0 |
| C5 vs L2 | gpt-5.5 | 44 | 40 | 2 | 34 | 0 |
| C5 vs L2 | opus | 36 | 34 | 7 | 43 | 0 |
| C5 vs L3 | gpt-5.4 | 40 | 54 | 12 | 13 | 0 |
| C5 vs L3 | gpt-5.5 | 35 | 46 | 2 | 36 | 0 |
| C5 vs L3 | opus | 29 | 45 | 3 | 41 | 1 |
| L1 vs L2 | gpt-5.4 | 46 | 36 | 23 | 15 | 0 |
| L1 vs L2 | gpt-5.5 | 50 | 32 | 4 | 34 | 0 |
| L1 vs L2 | opus | 41 | 25 | 16 | 32 | 6 |
| L2 vs L3 | gpt-5.4 | 40 | 57 | 9 | 13 | 0 |
| L2 vs L3 | gpt-5.5 | 26 | 49 | 6 | 38 | 0 |
| L2 vs L3 | opus | 26 | 41 | 8 | 38 | 6 |

### AB/BA by judge-author provider scope

Demotes the Phase 0 cross-provider C3 vs C5_CONTRACT finding by applying AB/BA correction within provider-scope strata. Original Phase 0 stratified cluster-bootstrap (without AB/BA) found cross-provider CI [0.238, 0.446] favoring C5_CONTRACT; under AB/BA, even the cross-provider subset shows no preference.

| pair | scope | n | orig lo | swap lo | controlled lo | Bootstrap CI |
|---|---|---:|---:|---:|---:|---|
| C0 vs C4_WRONG_PROFILE | cross_provider | 318 | 0.385 | 0.310 | 0.349 | [0.295, 0.406] |
| C0 vs C4_WRONG_PROFILE | same_provider | 399 | 0.317 | 0.218 | 0.268 | [0.221, 0.314] |
| C0 vs C_GENERIC_CONTRACT | cross_provider | 318 | 0.344 | 0.252 | 0.299 | [0.243, 0.355] |
| C0 vs C_GENERIC_CONTRACT | same_provider | 399 | 0.226 | 0.113 | 0.169 | [0.135, 0.205] |
| C1_padded vs C4 | same_provider | 320 | 0.319 | 0.434 | 0.377 | [0.314, 0.438] |
| C3 vs C4_WRONG_PROFILE | cross_provider | 318 | 0.632 | 0.553 | 0.593 | [0.538, 0.646] |
| C3 vs C4_WRONG_PROFILE | same_provider | 399 | 0.632 | 0.499 | 0.565 | [0.513, 0.618] |
| C3 vs C5_CONTRACT | cross_provider | 88 | 0.341 | 0.568 | 0.457 | [0.372, 0.535] |
| C3 vs C5_CONTRACT | same_provider | 200 | 0.465 | 0.576 | 0.520 | [0.450, 0.595] |
| C3 vs C5_NONPUBLIC | cross_provider | 160 | 0.692 | 0.585 | 0.637 | [0.566, 0.709] |
| C3 vs C5_NONPUBLIC | same_provider | 200 | 0.750 | 0.630 | 0.690 | [0.619, 0.758] |
| C3 vs C5_NONPUBLIC_CONTRACT | cross_provider | 160 | 0.598 | 0.352 | 0.475 | [0.409, 0.541] |
| C3 vs C5_NONPUBLIC_CONTRACT | same_provider | 200 | 0.600 | 0.335 | 0.468 | [0.400, 0.536] |
| C3 vs C_GENERIC_CONTRACT | cross_provider | 318 | 0.571 | 0.472 | 0.521 | [0.467, 0.578] |
| C3 vs C_GENERIC_CONTRACT | same_provider | 399 | 0.516 | 0.331 | 0.424 | [0.375, 0.471] |
| C3 vs L1 | cross_provider | 160 | 0.656 | 0.506 | 0.581 | [0.506, 0.662] |
| C3 vs L1 | same_provider | 200 | 0.730 | 0.490 | 0.610 | [0.536, 0.678] |
| C3 vs L2 | cross_provider | 160 | 0.685 | 0.535 | 0.609 | [0.530, 0.692] |
| C3 vs L2 | same_provider | 200 | 0.790 | 0.620 | 0.705 | [0.637, 0.770] |
| C4_WRONG_PROFILE vs C5 | cross_provider | 160 | 0.415 | 0.550 | 0.483 | [0.407, 0.562] |
| C4_WRONG_PROFILE vs C5 | same_provider | 200 | 0.440 | 0.685 | 0.562 | [0.489, 0.629] |
| C4 vs C4_WRONG_PROFILE | cross_provider | 318 | 0.612 | 0.519 | 0.565 | [0.510, 0.617] |
| C4 vs C4_WRONG_PROFILE | same_provider | 399 | 0.619 | 0.496 | 0.558 | [0.505, 0.614] |
| C4 vs C4_shuffled | same_provider | 320 | 0.519 | 0.637 | 0.578 | [0.522, 0.639] |
| C4 vs C5 | cross_provider | 80 | 0.675 | 0.800 | 0.738 | [0.650, 0.812] |
| C4 vs C5 | same_provider | 200 | 0.606 | 0.710 | 0.657 | [0.586, 0.727] |
| C4 vs C5_CONTRACT | cross_provider | 88 | 0.395 | 0.614 | 0.506 | [0.421, 0.592] |
| C4 vs C5_CONTRACT | same_provider | 200 | 0.402 | 0.540 | 0.471 | [0.401, 0.545] |
| C4 vs C5_NONPUBLIC | cross_provider | 160 | 0.637 | 0.497 | 0.567 | [0.489, 0.651] |
| C4 vs C5_NONPUBLIC | same_provider | 200 | 0.745 | 0.606 | 0.675 | [0.600, 0.748] |
| C4 vs C5_NONPUBLIC_CONTRACT | cross_provider | 160 | 0.531 | 0.315 | 0.423 | [0.348, 0.497] |
| C4 vs C5_NONPUBLIC_CONTRACT | same_provider | 200 | 0.625 | 0.407 | 0.516 | [0.448, 0.583] |
| C4 vs C_GENERIC_CONTRACT | cross_provider | 318 | 0.588 | 0.511 | 0.549 | [0.492, 0.607] |
| C4 vs C_GENERIC_CONTRACT | same_provider | 399 | 0.543 | 0.369 | 0.456 | [0.405, 0.507] |
| C4 vs L3 | cross_provider | 158 | 0.671 | 0.513 | 0.592 | [0.515, 0.669] |
| C4 vs L3 | same_provider | 199 | 0.749 | 0.573 | 0.661 | [0.589, 0.730] |
| C5_CONTRACT vs C5_NONPUBLIC | cross_provider | 160 | 0.698 | 0.575 | 0.636 | [0.556, 0.713] |
| C5_CONTRACT vs C5_NONPUBLIC | same_provider | 200 | 0.775 | 0.615 | 0.695 | [0.627, 0.754] |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | cross_provider | 160 | 0.620 | 0.412 | 0.516 | [0.439, 0.592] |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | same_provider | 200 | 0.631 | 0.370 | 0.500 | [0.431, 0.568] |
| C5_CONTRACT vs L1 | cross_provider | 160 | 0.648 | 0.519 | 0.583 | [0.513, 0.656] |
| C5_CONTRACT vs L1 | same_provider | 200 | 0.725 | 0.530 | 0.627 | [0.558, 0.694] |
| C5_CONTRACT vs L3 | cross_provider | 158 | 0.752 | 0.497 | 0.623 | [0.553, 0.689] |
| C5_CONTRACT vs L3 | same_provider | 199 | 0.754 | 0.578 | 0.666 | [0.591, 0.735] |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | cross_provider | 160 | 0.289 | 0.411 | 0.352 | [0.278, 0.431] |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | same_provider | 200 | 0.256 | 0.407 | 0.333 | [0.268, 0.397] |
| C5 vs C5_CONTRACT | cross_provider | 88 | 0.307 | 0.377 | 0.344 | [0.253, 0.430] |
| C5 vs C5_CONTRACT | same_provider | 200 | 0.211 | 0.414 | 0.314 | [0.253, 0.379] |
| C5 vs C5_NONPUBLIC | cross_provider | 160 | 0.620 | 0.415 | 0.517 | [0.444, 0.581] |
| C5 vs C5_NONPUBLIC | same_provider | 200 | 0.633 | 0.440 | 0.536 | [0.466, 0.609] |
| C5 vs C_GENERIC_CONTRACT | cross_provider | 160 | 0.531 | 0.438 | 0.484 | [0.402, 0.560] |
| C5 vs C_GENERIC_CONTRACT | same_provider | 200 | 0.410 | 0.211 | 0.311 | [0.250, 0.380] |
| C5 vs L1 | cross_provider | 160 | 0.525 | 0.325 | 0.425 | [0.350, 0.503] |
| C5 vs L1 | same_provider | 200 | 0.560 | 0.355 | 0.458 | [0.390, 0.526] |
| C5 vs L2 | cross_provider | 160 | 0.575 | 0.406 | 0.491 | [0.420, 0.564] |
| C5 vs L2 | same_provider | 200 | 0.645 | 0.440 | 0.542 | [0.477, 0.608] |
| C5 vs L3 | cross_provider | 158 | 0.516 | 0.342 | 0.429 | [0.350, 0.508] |
| C5 vs L3 | same_provider | 199 | 0.568 | 0.342 | 0.455 | [0.378, 0.528] |
| L1 vs L2 | cross_provider | 160 | 0.484 | 0.618 | 0.550 | [0.482, 0.622] |
| L1 vs L2 | same_provider | 200 | 0.525 | 0.620 | 0.573 | [0.502, 0.641] |
| L2 vs L3 | cross_provider | 158 | 0.303 | 0.549 | 0.427 | [0.355, 0.497] |
| L2 vs L3 | same_provider | 199 | 0.338 | 0.497 | 0.418 | [0.350, 0.486] |

### AB/BA joint position × length correction

Restricts AB/BA records to the length-similar bucket only. Settles the Phase 0 (length-matched) vs Phase 1 (AB/BA) contradiction by addressing both confounds simultaneously. For pairs where the joint CI straddles 0.5, the Tier 1 verdict is contingent on the choice of confound to control.

| pair | n_similar | controlled lo (length-matched) | Bootstrap CI |
|---|---:|---:|---|
| C0 vs C4_WRONG_PROFILE | 165 | 0.304 | [0.224, 0.394] |
| C0 vs C_GENERIC_CONTRACT | 153 | 0.255 | [0.173, 0.337] |
| C1_padded vs C4 | 86 | 0.267 | [0.174, 0.366] |
| C3 vs C4_WRONG_PROFILE | 150 | 0.527 | [0.437, 0.613] ⚠ joint CI straddles 0.5 |
| C3 vs C5_CONTRACT | 80 | 0.500 | [0.371, 0.634] ⚠ joint CI straddles 0.5 |
| C3 vs C5_NONPUBLIC | 69 | 0.659 | [0.500, 0.812] |
| C3 vs C5_NONPUBLIC_CONTRACT | 114 | 0.528 | [0.432, 0.621] ⚠ joint CI straddles 0.5 |
| C3 vs C_GENERIC_CONTRACT | 135 | 0.426 | [0.326, 0.530] ⚠ joint CI straddles 0.5 |
| C3 vs L1 | 69 | 0.457 | [0.312, 0.601] ⚠ joint CI straddles 0.5 |
| C3 vs L2 | 75 | 0.577 | [0.427, 0.727] ⚠ joint CI straddles 0.5 |
| C4_WRONG_PROFILE vs C5 | 51 | 0.647 | [0.510, 0.784] |
| C4 vs C4_WRONG_PROFILE | 129 | 0.539 | [0.434, 0.643] ⚠ joint CI straddles 0.5 |
| C4 vs C4_shuffled | 86 | 0.616 | [0.512, 0.721] |
| C4 vs C5 | 76 | 0.674 | [0.547, 0.795] |
| C4 vs C5_CONTRACT | 65 | 0.450 | [0.298, 0.601] ⚠ joint CI straddles 0.5 |
| C4 vs C5_NONPUBLIC | 51 | 0.804 | [0.657, 0.931] |
| C4 vs C5_NONPUBLIC_CONTRACT | 90 | 0.547 | [0.431, 0.661] ⚠ joint CI straddles 0.5 |
| C4 vs C_GENERIC_CONTRACT | 159 | 0.538 | [0.447, 0.632] ⚠ joint CI straddles 0.5 |
| C4 vs L3 | 84 | 0.643 | [0.500, 0.780] |
| C5_CONTRACT vs C5_NONPUBLIC | 72 | 0.688 | [0.556, 0.806] |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 99 | 0.520 | [0.424, 0.616] ⚠ joint CI straddles 0.5 |
| C5_CONTRACT vs L1 | 84 | 0.643 | [0.518, 0.756] |
| C5_CONTRACT vs L3 | 111 | 0.586 | [0.482, 0.694] ⚠ joint CI straddles 0.5 |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 69 | 0.217 | [0.109, 0.341] |
| C5 vs C5_CONTRACT | 74 | 0.351 | [0.238, 0.471] |
| C5 vs C5_NONPUBLIC | 87 | 0.523 | [0.391, 0.655] ⚠ joint CI straddles 0.5 |
| C5 vs C_GENERIC_CONTRACT | 54 | 0.324 | [0.204, 0.454] |
| C5 vs L1 | 84 | 0.476 | [0.351, 0.607] ⚠ joint CI straddles 0.5 |
| C5 vs L2 | 78 | 0.500 | [0.385, 0.622] ⚠ joint CI straddles 0.5 |
| C5 vs L3 | 84 | 0.491 | [0.366, 0.607] ⚠ joint CI straddles 0.5 |
| L1 vs L2 | 81 | 0.593 | [0.472, 0.704] ⚠ joint CI straddles 0.5 |
| L2 vs L3 | 66 | 0.443 | [0.318, 0.580] ⚠ joint CI straddles 0.5 |

**Reading**: If `orig` and `swap` lo_win rates are both away from 0.5 in the same direction → condition preference is real (Tier 1 confirmed). If they're on opposite sides of 0.5 → slot bias dominates and the headline collapses under counterbalancing. The `position_flip_rate` is the raw rate of within-pair disagreement; values near 0 mean judges are consistent regardless of order.

## Condition discoverability (TF-IDF + logistic)

Trained a TF-IDF + logistic classifier to predict condition from output text alone. **Test accuracy: 0.217** vs chance baseline 0.067 (+0.151 pp above chance). If high, pairwise judges may be partly recognizing condition cues.

**Per-class F1 (test split):**

| condition | F1 |
|---|---:|
| C0 | 0.422 |
| C1 | 0.117 |
| C1_padded | 0.141 |
| C3 | 0.130 |
| C4 | 0.129 |
| C4_WRONG_PROFILE | 0.165 |
| C4_shuffled | 0.267 |
| C5 | 0.000 |
| C5_CONTRACT | 0.000 |
| C5_NONPUBLIC | 0.000 |
| C5_NONPUBLIC_CONTRACT | 0.000 |
| C_GENERIC_CONTRACT | 0.518 |
| L1 | 0.000 |
| L2 | 0.000 |
| L3 | 0.000 |

**Key reading**: F1 ≈ 0 for C5 and C5_CONTRACT under this simple TF-IDF lexical classifier indicates this classifier could not distinguish C5 from C5_CONTRACT outputs from text alone. This does NOT rule out semantic, stylistic, length-based, or judge-internal recognizability — a stronger classifier or judge-blind recognizability prompt would be required to make a stronger claim. Wording fix per 2026-05-17 round-2 review (Codex Council skeptic + GPT Pro A13).

## Rubric lexical-overlap audit

Per-condition Jaccard overlap between profile-text vocabulary and the anchored-rubric anchor language (prompt 06b). Higher overlap = condition prompt 'speaks rubric language' more directly. Lexical-halo concern (codex-council, GPT-Pro §A16): rubric may be rewarding prompt-mirror phrasing rather than actual quality.

| condition | tokens | overlap | Jaccard | overlap/cond | top overlap |
|---|---:|---:|---:|---:|---|
| C1_padded | 511 | 37 | 0.054 | 0.072 | rather, report, actually, sentences, each, labels |
| C1_trait_labels | 368 | 26 | 0.047 | 0.071 | strong, rather, specific, interpersonal, register, emotional |
| C2_narrative | 649 | 56 | 0.070 | 0.086 | specific, well, rather, generic, challenge, assistant |
| C3_behavioral_contract | 837 | 71 | 0.073 | 0.085 | emotional, specific, name, decision, concrete, register |
| C4_behavioral_contract_anti_sycophancy | 1044 | 81 | 0.069 | 0.078 | back, specific, preserving, rather, agency, challenge |
| C4_shuffled | 1044 | 81 | 0.069 | 0.078 | back, specific, preserving, rather, agency, challenge |
| C4_wrong_profile | 1044 | 81 | 0.069 | 0.078 | back, specific, preserving, rather, agency, challenge |
| C5_contract | 1155 | 81 | 0.063 | 0.070 | back, emotional, source, specific, preserve, rather |
| C5_nonpublic | 869 | 60 | 0.059 | 0.069 | rather, source, specific, profile, register, emotional |
| C5_nonpublic_contract | 1187 | 84 | 0.064 | 0.071 | back, emotional, source, specific, preserve, rather |
| C5_source_packet_informed | 843 | 58 | 0.058 | 0.069 | rather, source, specific, profile, emotional, register |
| C_generic_contract | 261 | 32 | 0.073 | 0.123 | real, risk, rather, vocabulary, back, plan |
| L1 | 734 | 53 | 0.060 | 0.072 | risk, rather, back, source, specific, generic |
| L2 | 693 | 53 | 0.062 | 0.076 | real, risk, rather, vocabulary, back, source |
| L3 | 693 | 53 | 0.062 | 0.076 | real, risk, rather, vocabulary, back, source |

## Macro vs micro aggregation

For each headline pair, the `micro` column is the current record-pooled lo_win (status quo). The macro-X columns each first compute lo_win within strata of dimension X, then average. Pairs whose macros disagree with micro by ≥5 pp on any dimension are flagged — that means the headline is partly an artifact of record-count imbalance, not the phenomenon.

| pair | micro | macro-judge | macro-author | macro-persona | macro-family | macro-cell | disagree ≥5pp |
|---|---:|---:|---:|---:|---:|---:|---|
| C0 vs C4 | 0.134 | 0.134 | 0.134 | 0.134 | 0.146 | 0.146 |  |
| C0 vs C4_WRONG_PROFILE | 0.346 | 0.346 | 0.346 | 0.347 | 0.354 | 0.352 |  |
| C0 vs C_GENERIC_CONTRACT | 0.278 | 0.278 | 0.279 | 0.278 | 0.290 | 0.292 |  |
| C1_padded vs C4 | 0.319 | 0.319 | 0.319 | 0.319 | 0.340 | 0.340 |  |
| C1 vs C1_padded | 0.434 | 0.434 | 0.434 | 0.434 | 0.453 | 0.453 |  |
| C1 vs C4 | 0.326 | 0.326 | 0.326 | 0.326 | 0.354 | 0.353 |  |
| C3 vs C4 | 0.378 | 0.378 | 0.378 | 0.378 | 0.389 | 0.389 |  |
| C3 vs C4_WRONG_PROFILE | 0.632 | 0.632 | 0.632 | 0.631 | 0.634 | 0.634 |  |
| C3 vs C5_CONTRACT | 0.428 | 0.440 | 0.407 | 0.428 | 0.412 | 0.409 |  |
| C3 vs C5_NONPUBLIC | 0.724 | 0.724 | 0.724 | 0.724 | 0.715 | 0.715 |  |
| C3 vs C5_NONPUBLIC_CONTRACT | 0.599 | 0.599 | 0.599 | 0.599 | 0.594 | 0.594 |  |
| C3 vs C_GENERIC_CONTRACT | 0.540 | 0.541 | 0.541 | 0.540 | 0.543 | 0.543 |  |
| C3 vs L1 | 0.697 | 0.697 | 0.697 | 0.697 | 0.696 | 0.696 |  |
| C3 vs L2 | 0.744 | 0.744 | 0.744 | 0.744 | 0.744 | 0.744 |  |
| C4_WRONG_PROFILE vs C5 | 0.429 | 0.429 | 0.429 | 0.429 | 0.417 | 0.416 |  |
| C4 vs C4_WRONG_PROFILE | 0.616 | 0.616 | 0.616 | 0.615 | 0.611 | 0.611 |  |
| C4 vs C4_shuffled | 0.519 | 0.519 | 0.519 | 0.519 | 0.525 | 0.525 |  |
| C4 vs C5 | 0.626 | 0.628 | 0.591 | 0.627 | 0.607 | 0.605 |  |
| C4 vs C5_CONTRACT | 0.400 | 0.401 | 0.380 | 0.402 | 0.392 | 0.387 |  |
| C4 vs C5_NONPUBLIC | 0.697 | 0.697 | 0.697 | 0.697 | 0.677 | 0.677 |  |
| C4 vs C5_NONPUBLIC_CONTRACT | 0.583 | 0.583 | 0.583 | 0.583 | 0.564 | 0.564 |  |
| C4 vs C_GENERIC_CONTRACT | 0.563 | 0.563 | 0.563 | 0.562 | 0.560 | 0.562 |  |
| C4 vs L3 | 0.714 | 0.714 | 0.714 | 0.713 | 0.689 | 0.688 |  |
| C5_CONTRACT vs C5_NONPUBLIC | 0.741 | 0.741 | 0.741 | 0.741 | 0.718 | 0.718 |  |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 0.626 | 0.627 | 0.626 | 0.626 | 0.629 | 0.629 |  |
| C5_CONTRACT vs L1 | 0.691 | 0.691 | 0.691 | 0.690 | 0.686 | 0.686 |  |
| C5_CONTRACT vs L3 | 0.753 | 0.753 | 0.752 | 0.753 | 0.743 | 0.744 |  |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 0.271 | 0.271 | 0.271 | 0.271 | 0.294 | 0.295 |  |
| C5 vs C5_CONTRACT | 0.240 | 0.232 | 0.265 | 0.240 | 0.253 | 0.258 |  |
| C5 vs C5_NONPUBLIC | 0.627 | 0.628 | 0.627 | 0.628 | 0.618 | 0.620 |  |
| C5 vs C_GENERIC_CONTRACT | 0.464 | 0.464 | 0.464 | 0.464 | 0.493 | 0.493 |  |
| C5 vs L1 | 0.544 | 0.544 | 0.544 | 0.544 | 0.554 | 0.554 |  |
| C5 vs L2 | 0.614 | 0.614 | 0.614 | 0.614 | 0.618 | 0.618 |  |
| C5 vs L3 | 0.545 | 0.545 | 0.545 | 0.545 | 0.543 | 0.540 |  |
| L1 vs L2 | 0.507 | 0.507 | 0.507 | 0.507 | 0.497 | 0.496 |  |
| L2 vs L3 | 0.323 | 0.323 | 0.323 | 0.324 | 0.323 | 0.325 |  |

## Cross-judge red-flag predictiveness

Tests whether leave-out-judge red flags predict the pairwise judge's call. For each decisive pairwise record, we count the red flags raised by judges OTHER than the pairwise judge on the winner vs the loser. If P(loser has more external flags | asymmetric) is significantly above 0.5, the red-flag signal is real (not a within-judge artifact). Replaces the v0.1 within-judge correlation flagged as tautological by GPT-Max empiricist.

| pair | n_dec | n_asym | asym rate | P(loser flagged \| asym) | Wilson CI95 | predictive? |
|---|---:|---:|---:|---:|---|---|
| C0 vs C4 | 320 | 142 | 0.444 | 0.880 | [0.817, 0.924] | **YES** |
| C0 vs C4_WRONG_PROFILE | 710 | 252 | 0.355 | 0.766 | [0.710, 0.814] | **YES** |
| C0 vs C_GENERIC_CONTRACT | 716 | 254 | 0.355 | 0.799 | [0.746, 0.844] | **YES** |
| C1_padded vs C4 | 320 | 116 | 0.362 | 0.802 | [0.720, 0.864] | **YES** |
| C1 vs C1_padded | 320 | 128 | 0.400 | 0.656 | [0.571, 0.733] | **YES** |
| C1 vs C4 | 319 | 110 | 0.345 | 0.800 | [0.716, 0.864] | **YES** |
| C3 vs C4 | 320 | 97 | 0.303 | 0.814 | [0.726, 0.879] | **YES** |
| C3 vs C4_WRONG_PROFILE | 717 | 209 | 0.291 | 0.742 | [0.678, 0.796] | **YES** |
| C3 vs C5_CONTRACT | 246 | 71 | 0.289 | 0.648 | [0.532, 0.749] | **YES** |
| C3 vs C5_NONPUBLIC | 359 | 100 | 0.279 | 0.810 | [0.722, 0.875] | **YES** |
| C3 vs C5_NONPUBLIC_CONTRACT | 359 | 84 | 0.234 | 0.643 | [0.536, 0.737] | **YES** |
| C3 vs C_GENERIC_CONTRACT | 716 | 185 | 0.258 | 0.746 | [0.679, 0.803] | **YES** |
| C3 vs L1 | 360 | 93 | 0.258 | 0.774 | [0.679, 0.847] | **YES** |
| C3 vs L2 | 359 | 101 | 0.281 | 0.802 | [0.714, 0.868] | **YES** |
| C4_WRONG_PROFILE vs C5 | 359 | 111 | 0.309 | 0.757 | [0.669, 0.827] | **YES** |
| C4 vs C4_WRONG_PROFILE | 716 | 208 | 0.290 | 0.774 | [0.713, 0.826] | **YES** |
| C4 vs C4_shuffled | 320 | 101 | 0.316 | 0.762 | [0.671, 0.835] | **YES** |
| C4 vs C5 | 242 | 101 | 0.417 | 0.792 | [0.703, 0.860] | **YES** |
| C4 vs C5_CONTRACT | 248 | 87 | 0.351 | 0.782 | [0.684, 0.856] | **YES** |
| C4 vs C5_NONPUBLIC | 360 | 103 | 0.286 | 0.854 | [0.773, 0.910] | **YES** |
| C4 vs C5_NONPUBLIC_CONTRACT | 360 | 97 | 0.269 | 0.732 | [0.636, 0.810] | **YES** |
| C4 vs C_GENERIC_CONTRACT | 716 | 196 | 0.274 | 0.765 | [0.701, 0.819] | **YES** |
| C4 vs L3 | 357 | 102 | 0.286 | 0.833 | [0.749, 0.893] | **YES** |
| C5_CONTRACT vs C5_NONPUBLIC | 359 | 108 | 0.301 | 0.722 | [0.631, 0.798] | **YES** |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 356 | 89 | 0.250 | 0.719 | [0.618, 0.802] | **YES** |
| C5_CONTRACT vs L1 | 359 | 100 | 0.279 | 0.710 | [0.615, 0.790] | **YES** |
| C5_CONTRACT vs L3 | 356 | 91 | 0.256 | 0.846 | [0.758, 0.906] | **YES** |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 358 | 116 | 0.324 | 0.819 | [0.739, 0.878] | **YES** |
| C5 vs C5_CONTRACT | 250 | 83 | 0.332 | 0.747 | [0.644, 0.828] | **YES** |
| C5 vs C5_NONPUBLIC | 357 | 108 | 0.302 | 0.704 | [0.612, 0.782] | **YES** |
| C5 vs C_GENERIC_CONTRACT | 360 | 104 | 0.289 | 0.779 | [0.690, 0.848] | **YES** |
| C5 vs L1 | 360 | 101 | 0.281 | 0.782 | [0.692, 0.852] | **YES** |
| C5 vs L2 | 360 | 106 | 0.294 | 0.679 | [0.586, 0.760] | **YES** |
| C5 vs L3 | 356 | 97 | 0.273 | 0.711 | [0.615, 0.792] | **YES** |
| L1 vs L2 | 355 | 113 | 0.318 | 0.770 | [0.684, 0.838] | **YES** |
| L2 vs L3 | 353 | 108 | 0.306 | 0.648 | [0.554, 0.732] | **YES** |

## Length-adjusted pairwise summary

For each pair, `full lo_win` is the unconditional lo win rate (matches the headline). `similar lo_win` is restricted to pairs where the two responses are length-similar (within the `similar` bucket of `_length_bucket`). Pairs whose headline margin vanishes (similar CI includes 0.5 AND |full − 0.5| ≥ 0.05) are flagged ⚠. Analysis-only complement to a future generation-side length-matched rerun.

| pair | full lo_win | n_full | similar lo_win | n_similar | similar CI95 | Δ similar−full | flag |
|---|---:|---:|---:|---:|---|---:|---|
| C0 vs C4 | 0.134 | 320 | 0.172 | 64 | [0.099, 0.282] | +0.037 |  |
| C0 vs C4_WRONG_PROFILE | 0.346 | 710 | 0.331 | 163 | [0.264, 0.407] | -0.015 |  |
| C0 vs C_GENERIC_CONTRACT | 0.278 | 716 | 0.327 | 153 | [0.258, 0.405] | +0.049 |  |
| C1_padded vs C4 | 0.319 | 320 | 0.186 | 86 | [0.118, 0.281] | -0.133 |  |
| C1 vs C1_padded | 0.434 | 320 | 0.280 | 100 | [0.201, 0.375] | -0.154 |  |
| C1 vs C4 | 0.326 | 319 | 0.203 | 74 | [0.127, 0.308] | -0.123 |  |
| C3 vs C4 | 0.378 | 320 | 0.342 | 82 | [0.248, 0.449] | -0.037 |  |
| C3 vs C4_WRONG_PROFILE | 0.632 | 717 | 0.587 | 150 | [0.507, 0.662] | -0.045 |  |
| C3 vs C5_CONTRACT | 0.428 | 283 | 0.449 | 78 | [0.343, 0.559] | +0.021 | **⚠ vanishes** |
| C3 vs C5_NONPUBLIC | 0.724 | 359 | 0.739 | 69 | [0.625, 0.828] | +0.015 |  |
| C3 vs C5_NONPUBLIC_CONTRACT | 0.599 | 359 | 0.667 | 114 | [0.576, 0.747] | +0.068 |  |
| C3 vs C_GENERIC_CONTRACT | 0.540 | 716 | 0.511 | 135 | [0.428, 0.594] | -0.029 |  |
| C3 vs L1 | 0.697 | 360 | 0.580 | 69 | [0.462, 0.689] | -0.117 | **⚠ vanishes** |
| C3 vs L2 | 0.744 | 359 | 0.640 | 75 | [0.527, 0.739] | -0.104 |  |
| C4_WRONG_PROFILE vs C5 | 0.429 | 359 | 0.529 | 51 | [0.395, 0.659] | +0.100 | **⚠ vanishes** |
| C4 vs C4_WRONG_PROFILE | 0.616 | 716 | 0.612 | 129 | [0.526, 0.692] | -0.004 |  |
| C4 vs C4_shuffled | 0.519 | 320 | 0.546 | 86 | [0.442, 0.647] | +0.028 |  |
| C4 vs C5 | 0.626 | 278 | 0.587 | 75 | [0.474, 0.691] | -0.039 | **⚠ vanishes** |
| C4 vs C5_CONTRACT | 0.400 | 285 | 0.375 | 64 | [0.267, 0.497] | -0.025 |  |
| C4 vs C5_NONPUBLIC | 0.697 | 360 | 0.824 | 51 | [0.698, 0.904] | +0.126 |  |
| C4 vs C5_NONPUBLIC_CONTRACT | 0.583 | 360 | 0.644 | 90 | [0.541, 0.736] | +0.061 |  |
| C4 vs C_GENERIC_CONTRACT | 0.563 | 716 | 0.610 | 159 | [0.532, 0.682] | +0.047 |  |
| C4 vs L3 | 0.714 | 357 | 0.714 | 84 | [0.610, 0.800] | +0.000 |  |
| C5_CONTRACT vs C5_NONPUBLIC | 0.741 | 359 | 0.806 | 72 | [0.700, 0.880] | +0.065 |  |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 0.626 | 356 | 0.727 | 99 | [0.632, 0.805] | +0.101 |  |
| C5_CONTRACT vs L1 | 0.691 | 359 | 0.738 | 84 | [0.635, 0.820] | +0.047 |  |
| C5_CONTRACT vs L3 | 0.753 | 356 | 0.721 | 111 | [0.631, 0.796] | -0.032 |  |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 0.271 | 358 | 0.130 | 69 | [0.070, 0.230] | -0.141 |  |
| C5 vs C5_CONTRACT | 0.240 | 287 | 0.192 | 73 | [0.118, 0.297] | -0.049 |  |
| C5 vs C5_NONPUBLIC | 0.627 | 357 | 0.621 | 87 | [0.516, 0.716] | -0.007 |  |
| C5 vs C_GENERIC_CONTRACT | 0.464 | 360 | 0.444 | 54 | [0.320, 0.576] | -0.019 |  |
| C5 vs L1 | 0.544 | 360 | 0.548 | 84 | [0.441, 0.650] | +0.003 |  |
| C5 vs L2 | 0.614 | 360 | 0.590 | 78 | [0.479, 0.692] | -0.024 | **⚠ vanishes** |
| C5 vs L3 | 0.545 | 356 | 0.639 | 83 | [0.531, 0.734] | +0.094 |  |
| L1 vs L2 | 0.507 | 355 | 0.550 | 80 | [0.441, 0.654] | +0.043 |  |
| L2 vs L3 | 0.323 | 353 | 0.266 | 64 | [0.173, 0.385] | -0.057 |  |

## A/B side audit (position-bias diagnostic)

External reviewers (codex-council, GPT-Max, GPT-Pro all unanimous) flagged that C5_CONTRACT is overwhelmingly in slot B against C3/C4/C5, and counterbalanced (AB/BA) rejudging is the cheapest decisive next experiment. This block quantifies the imbalance so the AB/BA design can target the worst-affected pairs first.

### Per condition: slot occupancy

| condition | n_slot_A | n_slot_B | B share |
|---|---:|---:|---:|
| C0 | 320 | 1434 | 0.818 |
| C1 | 638 | 2 | 0.003 |
| C1_padded | 322 | 318 | 0.497 |
| C3 | 608 | 2874 | 0.825 |
| C4 | 884 | 3795 | 0.811 |
| C4_WRONG_PROFILE | 2511 | 0 | 0.000 |
| C4_shuffled | 4 | 316 | 0.988 |
| C5 | 288 | 2437 | 0.894 |
| C5_CONTRACT | 0 | 2301 | 1.000 |
| C5_NONPUBLIC | 1794 | 6 | 0.003 |
| C5_NONPUBLIC_CONTRACT | 1086 | 354 | 0.246 |
| C_GENERIC_CONTRACT | 2511 | 0 | 0.000 |
| L1 | 1440 | 0 | 0.000 |
| L2 | 1074 | 363 | 0.253 |
| L3 | 1074 | 354 | 0.248 |

### Per pair: slot balance + winner-by-side

| pair | n_total | n_dec | slot A wins | slot B wins | slot A win rate | slot A is `lo` | imbalanced? |
|---|---:|---:|---:|---:|---:|---:|---|
| C0 vs C4 | 320 | 320 | 43 | 277 | 0.134 | 1.000 | ⚠ slot A=`C0`, slot B=`C4` |
| C0 vs C4_WRONG_PROFILE | 717 | 710 | 464 | 246 | 0.653 | 0.000 | ⚠ slot A=`C4_WRONG_PROFILE`, slot B=`C0` |
| C0 vs C_GENERIC_CONTRACT | 717 | 716 | 517 | 199 | 0.722 | 0.000 | ⚠ slot A=`C_GENERIC_CONTRACT`, slot B=`C0` |
| C1_padded vs C4 | 320 | 320 | 102 | 218 | 0.319 | 1.000 | ⚠ slot A=`C1_padded`, slot B=`C4` |
| C1 vs C1_padded | 320 | 320 | 137 | 183 | 0.428 | 0.994 | ⚠ slot A=`C1`, slot B=`C1_padded` |
| C1 vs C4 | 320 | 319 | 104 | 215 | 0.326 | 1.000 | ⚠ slot A=`C1`, slot B=`C4` |
| C3 vs C4 | 320 | 320 | 121 | 199 | 0.378 | 1.000 | ⚠ slot A=`C3`, slot B=`C4` |
| C3 vs C4_WRONG_PROFILE | 717 | 717 | 264 | 453 | 0.368 | 0.000 | ⚠ slot A=`C4_WRONG_PROFILE`, slot B=`C3` |
| C3 vs C5_CONTRACT | 288 | 283 | 121 | 162 | 0.428 | 1.000 | ⚠ slot A=`C3`, slot B=`C5_CONTRACT` |
| C3 vs C5_NONPUBLIC | 360 | 359 | 99 | 260 | 0.276 | 0.000 | ⚠ slot A=`C5_NONPUBLIC`, slot B=`C3` |
| C3 vs C5_NONPUBLIC_CONTRACT | 360 | 359 | 144 | 215 | 0.401 | 0.000 | ⚠ slot A=`C5_NONPUBLIC_CONTRACT`, slot B=`C3` |
| C3 vs C_GENERIC_CONTRACT | 717 | 716 | 329 | 387 | 0.460 | 0.000 | ⚠ slot A=`C_GENERIC_CONTRACT`, slot B=`C3` |
| C3 vs L1 | 360 | 360 | 109 | 251 | 0.303 | 0.000 | ⚠ slot A=`L1`, slot B=`C3` |
| C3 vs L2 | 360 | 359 | 92 | 267 | 0.256 | 0.000 | ⚠ slot A=`L2`, slot B=`C3` |
| C4_WRONG_PROFILE vs C5 | 360 | 359 | 154 | 205 | 0.429 | 1.000 | ⚠ slot A=`C4_WRONG_PROFILE`, slot B=`C5` |
| C4 vs C4_WRONG_PROFILE | 717 | 716 | 275 | 441 | 0.384 | 0.000 | ⚠ slot A=`C4_WRONG_PROFILE`, slot B=`C4` |
| C4 vs C4_shuffled | 320 | 320 | 164 | 156 | 0.512 | 0.988 | ⚠ slot A=`C4`, slot B=`C4_shuffled` |
| C4 vs C5 | 280 | 278 | 174 | 104 | 0.626 | 1.000 | ⚠ slot A=`C4`, slot B=`C5` |
| C4 vs C5_CONTRACT | 288 | 285 | 114 | 171 | 0.400 | 1.000 | ⚠ slot A=`C4`, slot B=`C5_CONTRACT` |
| C4 vs C5_NONPUBLIC | 360 | 360 | 109 | 251 | 0.303 | 0.000 | ⚠ slot A=`C5_NONPUBLIC`, slot B=`C4` |
| C4 vs C5_NONPUBLIC_CONTRACT | 360 | 360 | 150 | 210 | 0.417 | 0.000 | ⚠ slot A=`C5_NONPUBLIC_CONTRACT`, slot B=`C4` |
| C4 vs C_GENERIC_CONTRACT | 717 | 716 | 313 | 403 | 0.437 | 0.000 | ⚠ slot A=`C_GENERIC_CONTRACT`, slot B=`C4` |
| C4 vs L3 | 357 | 357 | 102 | 255 | 0.286 | 0.000 | ⚠ slot A=`L3`, slot B=`C4` |
| C5_CONTRACT vs C5_NONPUBLIC | 360 | 359 | 93 | 266 | 0.259 | 0.000 | ⚠ slot A=`C5_NONPUBLIC`, slot B=`C5_CONTRACT` |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 360 | 356 | 133 | 223 | 0.374 | 0.000 | ⚠ slot A=`C5_NONPUBLIC_CONTRACT`, slot B=`C5_CONTRACT` |
| C5_CONTRACT vs L1 | 360 | 359 | 111 | 248 | 0.309 | 0.000 | ⚠ slot A=`L1`, slot B=`C5_CONTRACT` |
| C5_CONTRACT vs L3 | 357 | 356 | 88 | 268 | 0.247 | 0.000 | ⚠ slot A=`L3`, slot B=`C5_CONTRACT` |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 360 | 358 | 103 | 255 | 0.288 | 0.983 | ⚠ slot A=`C5_NONPUBLIC`, slot B=`C5_NONPUBLIC_CONTRACT` |
| C5 vs C5_CONTRACT | 288 | 287 | 69 | 218 | 0.240 | 1.000 | ⚠ slot A=`C5`, slot B=`C5_CONTRACT` |
| C5 vs C5_NONPUBLIC | 360 | 357 | 133 | 224 | 0.372 | 0.000 | ⚠ slot A=`C5_NONPUBLIC`, slot B=`C5` |
| C5 vs C_GENERIC_CONTRACT | 360 | 360 | 193 | 167 | 0.536 | 0.000 | ⚠ slot A=`C_GENERIC_CONTRACT`, slot B=`C5` |
| C5 vs L1 | 360 | 360 | 164 | 196 | 0.456 | 0.000 | ⚠ slot A=`L1`, slot B=`C5` |
| C5 vs L2 | 360 | 360 | 139 | 221 | 0.386 | 0.000 | ⚠ slot A=`L2`, slot B=`C5` |
| C5 vs L3 | 357 | 356 | 162 | 194 | 0.455 | 0.000 | ⚠ slot A=`L3`, slot B=`C5` |
| L1 vs L2 | 360 | 355 | 180 | 175 | 0.507 | 1.000 | ⚠ slot A=`L1`, slot B=`L2` |
| L2 vs L3 | 357 | 353 | 115 | 238 | 0.326 | 0.992 | ⚠ slot A=`L2`, slot B=`L3` |

**Reading**: If `slot A is lo` share is near 0.5, slot assignment is balanced. If it's near 0 or 1 (⚠), one condition dominates one slot — those rows are confounded with side and require AB/BA rejudging before any margin is trustworthy. The `slot A win rate` column is the side-only position-bias signal: under no position bias and balanced assignment, it should hover near 0.5.

## Leave-one-out fragility (cluster-bootstrap CIs)

For each headline pair, drop one (judge / author / persona / scenario family) at a time and recompute cluster-bootstrap CI. Reports `Δ_from_full` (loo lo_win minus full-sample lo_win) and flags: `flips` (sign change across 0.5), `attenuates_5pp` (|Δ| ≥ 0.05), `ci_widens_2x` (loo CI width ≥ 2× full width). **Robust** = no flags.

### Leave-one-judge-out

| pair | full lo_win | leave-out | loo lo_win | Δ_from_full | flags |
|---|---:|---|---:|---:|---|
| C0 vs C4_WRONG_PROFILE | 0.346 | −gpt-5.5 | 0.290 | -0.056 | `attenuates_5pp` |
| C0 vs C4_WRONG_PROFILE | 0.346 | −opus | 0.400 | +0.054 | `attenuates_5pp` |
| C3 vs C4 | 0.378 | −gpt-5.4 | 0.319 | -0.059 | `attenuates_5pp` |
| C3 vs C4 | 0.378 | −gpt-5.5 | 0.438 | +0.059 | `attenuates_5pp` |
| C3 vs C5_CONTRACT | 0.428 | −gpt-5.4 | 0.367 | -0.061 | `attenuates_5pp` |
| C3 vs C5_CONTRACT | 0.428 | −opus | 0.494 | +0.066 | `attenuates_5pp` |
| C3 vs C_GENERIC_CONTRACT | 0.540 | −gpt-5.4 | 0.593 | +0.053 | `attenuates_5pp` |
| C3 vs C_GENERIC_CONTRACT | 0.540 | −opus | 0.496 | -0.045 | `flips` |
| C4 vs C4_shuffled | 0.519 | −gpt-5.4 | 0.438 | -0.081 | `flips`, `attenuates_5pp` |
| C4 vs C4_shuffled | 0.519 | −gpt-5.5 | 0.600 | +0.081 | `attenuates_5pp` |
| C4 vs C_GENERIC_CONTRACT | 0.563 | −gpt-5.4 | 0.618 | +0.056 | `attenuates_5pp` |
| C4 vs C_GENERIC_CONTRACT | 0.563 | −opus | 0.499 | -0.064 | `flips`, `attenuates_5pp` |
| C5_CONTRACT vs L1 | 0.691 | −gpt-5.4 | 0.753 | +0.062 | `attenuates_5pp` |
| C5 vs C5_CONTRACT | 0.240 | −gpt-5.5 | 0.296 | +0.055 | `attenuates_5pp` |
| C5 vs C5_NONPUBLIC | 0.627 | −gpt-5.4 | 0.679 | +0.052 | `attenuates_5pp` |
| C5 vs C_GENERIC_CONTRACT | 0.464 | −gpt-5.4 | 0.504 | +0.040 | `flips` |
| L1 vs L2 | 0.507 | −gpt-5.4 | 0.472 | -0.035 | `flips` |

### Leave-one-author-out

| pair | full lo_win | leave-out | loo lo_win | Δ_from_full | flags |
|---|---:|---|---:|---:|---|
| C0 vs C4_WRONG_PROFILE | 0.346 | −gpt-5.4 | 0.412 | +0.066 | `attenuates_5pp` |
| C0 vs C4_WRONG_PROFILE | 0.346 | −gpt-5.5 | 0.401 | +0.054 | `attenuates_5pp` |
| C0 vs C4_WRONG_PROFILE | 0.346 | −opus | 0.226 | -0.120 | `attenuates_5pp` |
| C0 vs C_GENERIC_CONTRACT | 0.278 | −gpt-5.4 | 0.371 | +0.093 | `attenuates_5pp` |
| C0 vs C_GENERIC_CONTRACT | 0.278 | −opus | 0.142 | -0.136 | `attenuates_5pp` |
| C3 vs C_GENERIC_CONTRACT | 0.540 | −opus | 0.484 | -0.056 | `flips`, `attenuates_5pp` |
| C3 vs L2 | 0.744 | −opus | 0.795 | +0.051 | `attenuates_5pp` |
| C4_WRONG_PROFILE vs C5 | 0.429 | −opus | 0.485 | +0.056 | `attenuates_5pp` |
| C4 vs C4_shuffled | 0.519 | −gpt-5.4 | 0.581 | +0.062 | `attenuates_5pp` |
| C4 vs C4_shuffled | 0.519 | −gpt-5.5 | 0.456 | -0.063 | `flips`, `attenuates_5pp` |
| C4 vs C5 | 0.626 | −gpt-5.4 | 0.576 | -0.050 | `attenuates_5pp` |
| C5 vs C5_CONTRACT | 0.240 | −gpt-5.4 | 0.293 | +0.053 | `attenuates_5pp` |
| C5 vs C_GENERIC_CONTRACT | 0.464 | −gpt-5.4 | 0.554 | +0.090 | `flips`, `attenuates_5pp` |
| C5 vs C_GENERIC_CONTRACT | 0.464 | −opus | 0.354 | -0.110 | `attenuates_5pp` |
| L1 vs L2 | 0.507 | −gpt-5.5 | 0.489 | -0.018 | `flips` |
| L1 vs L2 | 0.507 | −opus | 0.494 | -0.013 | `flips` |

### Leave-one-persona-out

| pair | full lo_win | leave-out | loo lo_win | Δ_from_full | flags |
|---|---:|---|---:|---:|---|
| C1_padded vs C4 | 0.319 | −user_pfi_pawl_gram_001 | 0.268 | -0.051 | `attenuates_5pp` |
| C3 vs C5_NONPUBLIC | 0.724 | −user_pfi_pawl_gram_001 | 0.781 | +0.057 | `attenuates_5pp` |
| C4 vs C4_shuffled | 0.519 | −user_pfi_slalom_altar_001 | 0.489 | -0.029 | `flips` |
| C4 vs C5 | 0.626 | −user_pfi_dario_armadillo_001 | 0.572 | -0.054 | `attenuates_5pp` |
| C4 vs C5 | 0.626 | −user_pfi_emily_blender_001 | 0.692 | +0.066 | `attenuates_5pp` |
| C4 vs C5 | 0.626 | −user_pfi_pawl_gram_001 | 0.683 | +0.057 | `attenuates_5pp` |
| C4 vs C5 | 0.626 | −user_pfi_slalom_altar_001 | 0.557 | -0.069 | `attenuates_5pp` |
| C4 vs C5_CONTRACT | 0.400 | −user_pfi_emily_blender_001 | 0.469 | +0.070 | `attenuates_5pp` |
| C4 vs C5_CONTRACT | 0.400 | −user_pfi_slalom_altar_001 | 0.316 | -0.084 | `attenuates_5pp` |
| C4 vs C5_NONPUBLIC | 0.697 | −user_pfi_dario_armadillo_001 | 0.637 | -0.060 | `attenuates_5pp` |
| C4 vs C5_NONPUBLIC | 0.697 | −user_pfi_pawl_gram_001 | 0.804 | +0.106 | `attenuates_5pp` |
| C4 vs C5_NONPUBLIC | 0.697 | −user_pfi_slalom_altar_001 | 0.619 | -0.079 | `attenuates_5pp` |
| C4 vs C5_NONPUBLIC_CONTRACT | 0.583 | −user_pfi_dario_armadillo_001 | 0.515 | -0.069 | `attenuates_5pp` |
| C4 vs C5_NONPUBLIC_CONTRACT | 0.583 | −user_pfi_pawl_gram_001 | 0.670 | +0.087 | `attenuates_5pp` |
| C4 vs L3 | 0.714 | −user_pfi_pawl_gram_001 | 0.774 | +0.060 | `attenuates_5pp` |
| C4 vs L3 | 0.714 | −user_pfi_slalom_altar_001 | 0.640 | -0.074 | `attenuates_5pp` |
| C5_CONTRACT vs C5_NONPUBLIC | 0.741 | −user_pfi_pawl_gram_001 | 0.792 | +0.051 | `attenuates_5pp` |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 0.271 | −user_pfi_pawl_gram_001 | 0.220 | -0.051 | `attenuates_5pp` |
| L1 vs L2 | 0.507 | −user_pfi_pawl_gram_001 | 0.457 | -0.050 | `flips`, `attenuates_5pp` |
| L2 vs L3 | 0.323 | −user_pfi_emily_blender_001 | 0.375 | +0.052 | `attenuates_5pp` |
| L2 vs L3 | 0.323 | −user_pfi_pawl_gram_001 | 0.259 | -0.064 | `attenuates_5pp` |

### Leave-one-scenario family-out

| pair | full lo_win | leave-out | loo lo_win | Δ_from_full | flags |
|---|---:|---|---:|---:|---|
| C4 vs C4_shuffled | 0.519 | −epistemic_uncertainty | 0.490 | -0.029 | `flips` |
| C5 vs C_GENERIC_CONTRACT | 0.464 | −interpersonal_conflict | 0.503 | +0.040 | `flips` |
| L1 vs L2 | 0.507 | −procrastination_avoidance | 0.489 | -0.018 | `flips` |
| L1 vs L2 | 0.507 | −shame_self_interpretation | 0.489 | -0.018 | `flips` |

## Pairwise by judge (same-author, decisive)

Per-pair stratification by `judge`. A row's `lo win` is the win rate of the lower-numbered condition within that stratum (ties excluded from denominator). Bootstrap CI only computed when n_dec ≥ 20 and n_clusters ≥ 5.

### C0 vs C4

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.181 | [0.129, 0.248] | [0.125, 0.244] |
| gpt-5.5 | 160 | 0.087 | [0.053, 0.141] | [0.044, 0.131] |

### C0 vs C4_WRONG_PROFILE

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 239 | 0.343 | [0.286, 0.405] | [0.289, 0.406] |
| gpt-5.5 | 238 | 0.458 | [0.396, 0.521] | [0.391, 0.517] |
| opus | 233 | 0.236 | [0.186, 0.295] | [0.181, 0.289] |

### C0 vs C_GENERIC_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 239 | 0.268 | [0.216, 0.327] | [0.213, 0.322] |
| gpt-5.5 | 239 | 0.289 | [0.235, 0.349] | [0.234, 0.343] |
| opus | 238 | 0.277 | [0.224, 0.337] | [0.218, 0.336] |

### C1_padded vs C4

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.356 | [0.286, 0.433] | [0.275, 0.431] |
| gpt-5.5 | 160 | 0.281 | [0.217, 0.355] | [0.212, 0.350] |

### C1 vs C1_padded

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.469 | [0.393, 0.546] | [0.394, 0.550] |
| gpt-5.5 | 160 | 0.400 | [0.327, 0.477] | [0.325, 0.481] |

### C1 vs C4

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.338 | [0.269, 0.414] | [0.269, 0.406] |
| gpt-5.5 | 159 | 0.315 | [0.247, 0.390] | [0.250, 0.384] |

### C3 vs C4

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.438 | [0.363, 0.515] | [0.356, 0.512] |
| gpt-5.5 | 160 | 0.319 | [0.252, 0.395] | [0.244, 0.394] |

### C3 vs C4_WRONG_PROFILE

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 239 | 0.565 | [0.501, 0.626] | [0.506, 0.623] |
| gpt-5.5 | 239 | 0.678 | [0.616, 0.734] | [0.623, 0.736] |
| opus | 239 | 0.653 | [0.590, 0.710] | [0.590, 0.716] |

### C3 vs C5_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 84 | 0.571 | [0.465, 0.672] | [0.476, 0.667] |
| gpt-5.5 | 84 | 0.417 | [0.317, 0.523] | [0.309, 0.524] |
| opus | 115 | 0.330 | [0.251, 0.421] | [0.244, 0.419] |

### C3 vs C5_NONPUBLIC

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.633 | [0.544, 0.714] | [0.542, 0.717] |
| gpt-5.5 | 120 | 0.758 | [0.674, 0.826] | [0.683, 0.833] |
| opus | 119 | 0.781 | [0.699, 0.846] | [0.700, 0.850] |

### C3 vs C5_NONPUBLIC_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.508 | [0.420, 0.596] | [0.425, 0.592] |
| gpt-5.5 | 120 | 0.642 | [0.553, 0.722] | [0.550, 0.725] |
| opus | 119 | 0.647 | [0.558, 0.727] | [0.567, 0.737] |

### C3 vs C_GENERIC_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 239 | 0.435 | [0.374, 0.498] | [0.372, 0.494] |
| gpt-5.5 | 239 | 0.556 | [0.493, 0.618] | [0.498, 0.619] |
| opus | 238 | 0.630 | [0.567, 0.689] | [0.570, 0.691] |

### C3 vs L1

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.633 | [0.544, 0.714] | [0.558, 0.725] |
| gpt-5.5 | 120 | 0.758 | [0.674, 0.826] | [0.683, 0.833] |
| opus | 120 | 0.700 | [0.613, 0.775] | [0.617, 0.783] |

### C3 vs L2

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.700 | [0.613, 0.775] | [0.608, 0.783] |
| gpt-5.5 | 120 | 0.742 | [0.657, 0.812] | [0.667, 0.817] |
| opus | 119 | 0.790 | [0.708, 0.854] | [0.720, 0.858] |

### C4_WRONG_PROFILE vs C5

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.442 | [0.356, 0.531] | [0.350, 0.525] |
| gpt-5.5 | 120 | 0.392 | [0.309, 0.481] | [0.308, 0.483] |
| opus | 119 | 0.454 | [0.367, 0.543] | [0.367, 0.538] |

### C4 vs C4_WRONG_PROFILE

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 239 | 0.552 | [0.489, 0.614] | [0.485, 0.611] |
| gpt-5.5 | 239 | 0.653 | [0.590, 0.710] | [0.594, 0.711] |
| opus | 238 | 0.643 | [0.580, 0.701] | [0.584, 0.700] |

### C4 vs C4_shuffled

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.600 | [0.523, 0.673] | [0.519, 0.669] |
| gpt-5.5 | 160 | 0.438 | [0.363, 0.515] | [0.369, 0.512] |

### C4 vs C5

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 80 | 0.662 | [0.554, 0.756] | [0.550, 0.775] |
| gpt-5.5 | 80 | 0.613 | [0.503, 0.712] | [0.500, 0.713] |
| opus | 118 | 0.610 | [0.520, 0.693] | [0.513, 0.701] |

### C4 vs C5_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 84 | 0.464 | [0.361, 0.570] | [0.357, 0.571] |
| gpt-5.5 | 84 | 0.345 | [0.252, 0.452] | [0.238, 0.452] |
| opus | 117 | 0.393 | [0.309, 0.484] | [0.313, 0.479] |

### C4 vs C5_NONPUBLIC

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.642 | [0.553, 0.722] | [0.550, 0.725] |
| gpt-5.5 | 120 | 0.658 | [0.570, 0.737] | [0.567, 0.742] |
| opus | 120 | 0.792 | [0.711, 0.855] | [0.717, 0.858] |

### C4 vs C5_NONPUBLIC_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.508 | [0.420, 0.596] | [0.417, 0.600] |
| gpt-5.5 | 120 | 0.600 | [0.511, 0.683] | [0.517, 0.692] |
| opus | 120 | 0.642 | [0.553, 0.722] | [0.558, 0.725] |

### C4 vs C_GENERIC_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 239 | 0.452 | [0.390, 0.515] | [0.385, 0.515] |
| gpt-5.5 | 238 | 0.546 | [0.483, 0.608] | [0.483, 0.608] |
| opus | 239 | 0.690 | [0.629, 0.746] | [0.636, 0.745] |

### C4 vs L3

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.647 | [0.558, 0.727] | [0.563, 0.731] |
| gpt-5.5 | 119 | 0.706 | [0.619, 0.780] | [0.622, 0.790] |
| opus | 119 | 0.790 | [0.708, 0.854] | [0.714, 0.857] |

### C5_CONTRACT vs C5_NONPUBLIC

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.683 | [0.596, 0.760] | [0.600, 0.767] |
| gpt-5.5 | 120 | 0.758 | [0.674, 0.826] | [0.683, 0.833] |
| opus | 119 | 0.781 | [0.699, 0.846] | [0.708, 0.855] |

### C5_CONTRACT vs C5_NONPUBLIC_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.550 | [0.461, 0.636] | [0.458, 0.642] |
| gpt-5.5 | 120 | 0.642 | [0.553, 0.722] | [0.558, 0.725] |
| opus | 116 | 0.690 | [0.601, 0.767] | [0.607, 0.769] |

### C5_CONTRACT vs L1

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.567 | [0.477, 0.652] | [0.483, 0.650] |
| gpt-5.5 | 120 | 0.750 | [0.666, 0.819] | [0.675, 0.825] |
| opus | 119 | 0.756 | [0.672, 0.825] | [0.681, 0.832] |

### C5_CONTRACT vs L3

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.681 | [0.592, 0.758] | [0.597, 0.765] |
| gpt-5.5 | 119 | 0.765 | [0.681, 0.832] | [0.689, 0.840] |
| opus | 118 | 0.814 | [0.734, 0.874] | [0.740, 0.882] |

### C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.358 | [0.278, 0.447] | [0.267, 0.442] |
| gpt-5.5 | 120 | 0.225 | [0.160, 0.308] | [0.158, 0.292] |
| opus | 118 | 0.229 | [0.162, 0.312] | [0.158, 0.311] |

### C5 vs C5_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 84 | 0.286 | [0.200, 0.390] | [0.191, 0.393] |
| gpt-5.5 | 84 | 0.107 | [0.057, 0.191] | [0.048, 0.179] |
| opus | 119 | 0.302 | [0.227, 0.390] | [0.227, 0.395] |

### C5 vs C5_NONPUBLIC

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.525 | [0.436, 0.612] | [0.433, 0.617] |
| gpt-5.5 | 120 | 0.667 | [0.578, 0.745] | [0.583, 0.750] |
| opus | 117 | 0.692 | [0.604, 0.769] | [0.603, 0.773] |

### C5 vs C_GENERIC_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.383 | [0.301, 0.473] | [0.300, 0.467] |
| gpt-5.5 | 120 | 0.483 | [0.396, 0.572] | [0.400, 0.575] |
| opus | 120 | 0.525 | [0.436, 0.612] | [0.433, 0.617] |

### C5 vs L1

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.475 | [0.388, 0.564] | [0.375, 0.558] |
| gpt-5.5 | 120 | 0.600 | [0.511, 0.683] | [0.500, 0.692] |
| opus | 120 | 0.558 | [0.469, 0.644] | [0.467, 0.642] |

### C5 vs L2

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.533 | [0.444, 0.620] | [0.433, 0.617] |
| gpt-5.5 | 120 | 0.650 | [0.561, 0.730] | [0.567, 0.733] |
| opus | 120 | 0.658 | [0.570, 0.737] | [0.575, 0.742] |

### C5 vs L3

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.445 | [0.359, 0.535] | [0.353, 0.529] |
| gpt-5.5 | 119 | 0.597 | [0.507, 0.680] | [0.513, 0.689] |
| opus | 118 | 0.593 | [0.503, 0.678] | [0.508, 0.675] |

### L1 vs L2

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.575 | [0.486, 0.660] | [0.483, 0.658] |
| gpt-5.5 | 120 | 0.450 | [0.364, 0.539] | [0.358, 0.533] |
| opus | 115 | 0.496 | [0.406, 0.586] | [0.409, 0.585] |

### L2 vs L3

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.412 | [0.327, 0.502] | [0.319, 0.504] |
| gpt-5.5 | 119 | 0.261 | [0.190, 0.346] | [0.185, 0.336] |
| opus | 115 | 0.296 | [0.220, 0.385] | [0.215, 0.383] |

## Pairwise by author (same-author, decisive)

Per-pair stratification by `author`. A row's `lo win` is the win rate of the lower-numbered condition within that stratum (ties excluded from denominator). Bootstrap CI only computed when n_dec ≥ 20 and n_clusters ≥ 5.

### C0 vs C4

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.131 | [0.087, 0.192] | [0.069, 0.206] |
| gpt-5.5 | 160 | 0.138 | [0.093, 0.199] | [0.075, 0.200] |

### C0 vs C4_WRONG_PROFILE

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 237 | 0.215 | [0.168, 0.272] | [0.148, 0.289] |
| gpt-5.5 | 236 | 0.237 | [0.188, 0.295] | [0.170, 0.307] |
| opus | 237 | 0.587 | [0.523, 0.647] | [0.506, 0.667] |

### C0 vs C_GENERIC_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 239 | 0.092 | [0.062, 0.135] | [0.050, 0.135] |
| gpt-5.5 | 240 | 0.192 | [0.147, 0.246] | [0.129, 0.263] |
| opus | 237 | 0.553 | [0.489, 0.615] | [0.468, 0.633] |

### C1_padded vs C4

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.344 | [0.275, 0.420] | [0.256, 0.431] |
| gpt-5.5 | 160 | 0.294 | [0.229, 0.368] | [0.206, 0.388] |

### C1 vs C1_padded

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.419 | [0.345, 0.496] | [0.325, 0.519] |
| gpt-5.5 | 160 | 0.450 | [0.375, 0.527] | [0.362, 0.544] |

### C1 vs C4

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.344 | [0.275, 0.420] | [0.250, 0.438] |
| gpt-5.5 | 159 | 0.308 | [0.242, 0.384] | [0.222, 0.403] |

### C3 vs C4

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.362 | [0.292, 0.439] | [0.269, 0.456] |
| gpt-5.5 | 160 | 0.394 | [0.321, 0.471] | [0.306, 0.487] |

### C3 vs C4_WRONG_PROFILE

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 240 | 0.542 | [0.478, 0.604] | [0.458, 0.629] |
| gpt-5.5 | 240 | 0.642 | [0.579, 0.700] | [0.567, 0.713] |
| opus | 237 | 0.713 | [0.652, 0.767] | [0.646, 0.781] |

### C3 vs C5_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.403 | [0.320, 0.493] | [0.292, 0.513] |
| gpt-5.5 | 118 | 0.491 | [0.403, 0.581] | [0.367, 0.603] |
| opus | 46 | 0.326 | [0.209, 0.470] | [0.174, 0.478] |

### C3 vs C5_NONPUBLIC

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.748 | [0.663, 0.817] | [0.639, 0.849] |
| gpt-5.5 | 120 | 0.767 | [0.683, 0.833] | [0.650, 0.867] |
| opus | 120 | 0.658 | [0.570, 0.737] | [0.542, 0.775] |

### C3 vs C5_NONPUBLIC_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.588 | [0.498, 0.673] | [0.462, 0.717] |
| gpt-5.5 | 120 | 0.625 | [0.536, 0.707] | [0.508, 0.733] |
| opus | 120 | 0.583 | [0.494, 0.668] | [0.483, 0.683] |

### C3 vs C_GENERIC_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 240 | 0.492 | [0.429, 0.554] | [0.412, 0.579] |
| gpt-5.5 | 239 | 0.477 | [0.414, 0.540] | [0.398, 0.559] |
| opus | 237 | 0.654 | [0.591, 0.712] | [0.578, 0.722] |

### C3 vs L1

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.733 | [0.648, 0.804] | [0.608, 0.850] |
| gpt-5.5 | 120 | 0.683 | [0.596, 0.760] | [0.575, 0.800] |
| opus | 120 | 0.675 | [0.587, 0.752] | [0.558, 0.775] |

### C3 vs L2

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.825 | [0.747, 0.883] | [0.717, 0.917] |
| gpt-5.5 | 119 | 0.765 | [0.681, 0.832] | [0.639, 0.875] |
| opus | 120 | 0.642 | [0.553, 0.722] | [0.525, 0.758] |

### C4_WRONG_PROFILE vs C5

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.475 | [0.388, 0.564] | [0.358, 0.592] |
| gpt-5.5 | 119 | 0.496 | [0.407, 0.584] | [0.361, 0.617] |
| opus | 120 | 0.317 | [0.240, 0.405] | [0.208, 0.442] |

### C4 vs C4_WRONG_PROFILE

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 240 | 0.621 | [0.558, 0.680] | [0.533, 0.708] |
| gpt-5.5 | 239 | 0.607 | [0.543, 0.666] | [0.525, 0.686] |
| opus | 237 | 0.620 | [0.557, 0.680] | [0.540, 0.696] |

### C4 vs C4_shuffled

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.456 | [0.381, 0.533] | [0.362, 0.544] |
| gpt-5.5 | 160 | 0.581 | [0.504, 0.655] | [0.487, 0.669] |

### C4 vs C5

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.692 | [0.604, 0.767] | [0.575, 0.808] |
| gpt-5.5 | 120 | 0.608 | [0.519, 0.691] | [0.500, 0.717] |
| opus | 38 | 0.474 | [0.325, 0.627] | [0.325, 0.632] |

### C4 vs C5_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.408 | [0.325, 0.498] | [0.300, 0.525] |
| gpt-5.5 | 118 | 0.432 | [0.346, 0.522] | [0.308, 0.555] |
| opus | 47 | 0.298 | [0.186, 0.440] | [0.173, 0.438] |

### C4 vs C5_NONPUBLIC

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.750 | [0.666, 0.819] | [0.633, 0.867] |
| gpt-5.5 | 120 | 0.733 | [0.648, 0.804] | [0.617, 0.842] |
| opus | 120 | 0.608 | [0.519, 0.691] | [0.492, 0.717] |

### C4 vs C5_NONPUBLIC_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.583 | [0.494, 0.668] | [0.467, 0.708] |
| gpt-5.5 | 120 | 0.650 | [0.561, 0.730] | [0.542, 0.767] |
| opus | 120 | 0.517 | [0.428, 0.604] | [0.408, 0.625] |

### C4 vs C_GENERIC_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 240 | 0.542 | [0.478, 0.604] | [0.463, 0.621] |
| gpt-5.5 | 239 | 0.548 | [0.485, 0.610] | [0.463, 0.626] |
| opus | 237 | 0.599 | [0.536, 0.659] | [0.519, 0.683] |

### C4 vs L3

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.717 | [0.630, 0.790] | [0.592, 0.825] |
| gpt-5.5 | 120 | 0.808 | [0.729, 0.869] | [0.717, 0.892] |
| opus | 117 | 0.615 | [0.525, 0.699] | [0.496, 0.727] |

### C5_CONTRACT vs C5_NONPUBLIC

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.781 | [0.699, 0.846] | [0.661, 0.883] |
| gpt-5.5 | 120 | 0.758 | [0.674, 0.826] | [0.658, 0.850] |
| opus | 120 | 0.683 | [0.596, 0.760] | [0.567, 0.792] |

### C5_CONTRACT vs C5_NONPUBLIC_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.625 | [0.536, 0.707] | [0.508, 0.733] |
| gpt-5.5 | 118 | 0.627 | [0.537, 0.709] | [0.509, 0.737] |
| opus | 118 | 0.627 | [0.537, 0.709] | [0.521, 0.744] |

### C5_CONTRACT vs L1

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.781 | [0.699, 0.846] | [0.692, 0.873] |
| gpt-5.5 | 120 | 0.700 | [0.613, 0.775] | [0.600, 0.792] |
| opus | 120 | 0.592 | [0.502, 0.675] | [0.492, 0.692] |

### C5_CONTRACT vs L3

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.792 | [0.711, 0.855] | [0.692, 0.892] |
| gpt-5.5 | 119 | 0.765 | [0.681, 0.832] | [0.672, 0.857] |
| opus | 117 | 0.701 | [0.613, 0.776] | [0.598, 0.795] |

### C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.208 | [0.145, 0.289] | [0.117, 0.308] |
| gpt-5.5 | 119 | 0.277 | [0.205, 0.364] | [0.152, 0.393] |
| opus | 119 | 0.328 | [0.250, 0.416] | [0.217, 0.450] |

### C5 vs C5_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.167 | [0.111, 0.243] | [0.092, 0.250] |
| gpt-5.5 | 120 | 0.267 | [0.196, 0.352] | [0.175, 0.358] |
| opus | 47 | 0.362 | [0.240, 0.505] | [0.200, 0.529] |

### C5 vs C5_NONPUBLIC

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.597 | [0.507, 0.680] | [0.483, 0.708] |
| gpt-5.5 | 119 | 0.639 | [0.549, 0.719] | [0.513, 0.765] |
| opus | 119 | 0.647 | [0.558, 0.727] | [0.555, 0.746] |

### C5 vs C_GENERIC_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.283 | [0.210, 0.370] | [0.183, 0.383] |
| gpt-5.5 | 120 | 0.425 | [0.340, 0.514] | [0.308, 0.550] |
| opus | 120 | 0.683 | [0.596, 0.760] | [0.583, 0.783] |

### C5 vs L1

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.558 | [0.469, 0.644] | [0.433, 0.675] |
| gpt-5.5 | 120 | 0.550 | [0.461, 0.636] | [0.417, 0.683] |
| opus | 120 | 0.525 | [0.436, 0.612] | [0.408, 0.650] |

### C5 vs L2

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.592 | [0.502, 0.675] | [0.458, 0.717] |
| gpt-5.5 | 120 | 0.708 | [0.622, 0.782] | [0.617, 0.800] |
| opus | 120 | 0.542 | [0.453, 0.628] | [0.433, 0.650] |

### C5 vs L3

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.517 | [0.428, 0.604] | [0.417, 0.625] |
| gpt-5.5 | 119 | 0.563 | [0.473, 0.649] | [0.437, 0.698] |
| opus | 117 | 0.556 | [0.465, 0.642] | [0.444, 0.667] |

### L1 vs L2

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.445 | [0.359, 0.535] | [0.325, 0.558] |
| gpt-5.5 | 116 | 0.543 | [0.453, 0.631] | [0.414, 0.655] |
| opus | 120 | 0.533 | [0.444, 0.620] | [0.408, 0.650] |

### L2 vs L3

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.342 | [0.263, 0.430] | [0.242, 0.458] |
| gpt-5.5 | 117 | 0.342 | [0.262, 0.432] | [0.218, 0.475] |
| opus | 116 | 0.284 | [0.210, 0.372] | [0.190, 0.388] |

## Pairwise by persona (same-author, decisive)

Per-pair stratification by `persona`. A row's `lo win` is the win rate of the lower-numbered condition within that stratum (ties excluded from denominator). Bootstrap CI only computed when n_dec ≥ 20 and n_clusters ≥ 5.

### C0 vs C4

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.000 | [0.000, 0.088] | [0.000, 0.000] |
| user_pfi_emily_blender_001 | 40 | 0.275 | [0.161, 0.428] | [0.125, 0.450] |
| user_pfi_pawl_gram_001 | 40 | 0.125 | [0.055, 0.261] | [0.025, 0.250] |
| user_pfi_slalom_altar_001 | 40 | 0.025 | [0.004, 0.129] | [0.000, 0.075] |
| user_syn_calibration_goblin_001 | 40 | 0.250 | [0.142, 0.402] | [0.075, 0.450] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.150 | [0.071, 0.291] | [0.025, 0.325] |
| user_syn_high_agency_spiraler_001 | 40 | 0.100 | [0.040, 0.231] | [0.000, 0.225] |
| user_syn_patient_craftsperson_001 | 40 | 0.150 | [0.071, 0.291] | [0.050, 0.275] |

### C0 vs C4_WRONG_PROFILE

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 87 | 0.552 | [0.447, 0.652] | [0.412, 0.686] |
| user_pfi_emily_blender_001 | 90 | 0.222 | [0.149, 0.319] | [0.111, 0.344] |
| user_pfi_pawl_gram_001 | 89 | 0.124 | [0.070, 0.208] | [0.045, 0.222] |
| user_pfi_slalom_altar_001 | 89 | 0.315 | [0.228, 0.417] | [0.202, 0.422] |
| user_syn_calibration_goblin_001 | 87 | 0.368 | [0.274, 0.473] | [0.241, 0.506] |
| user_syn_conflict_allergic_moralist_001 | 89 | 0.483 | [0.382, 0.586] | [0.333, 0.652] |
| user_syn_high_agency_spiraler_001 | 89 | 0.281 | [0.198, 0.382] | [0.184, 0.393] |
| user_syn_patient_craftsperson_001 | 90 | 0.433 | [0.336, 0.536] | [0.300, 0.556] |

### C0 vs C_GENERIC_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.300 | [0.215, 0.401] | [0.189, 0.422] |
| user_pfi_emily_blender_001 | 90 | 0.267 | [0.186, 0.366] | [0.144, 0.389] |
| user_pfi_pawl_gram_001 | 90 | 0.178 | [0.113, 0.269] | [0.067, 0.300] |
| user_pfi_slalom_altar_001 | 90 | 0.233 | [0.158, 0.331] | [0.122, 0.356] |
| user_syn_calibration_goblin_001 | 87 | 0.322 | [0.233, 0.426] | [0.184, 0.460] |
| user_syn_conflict_allergic_moralist_001 | 90 | 0.344 | [0.255, 0.447] | [0.222, 0.489] |
| user_syn_high_agency_spiraler_001 | 90 | 0.267 | [0.186, 0.366] | [0.144, 0.411] |
| user_syn_patient_craftsperson_001 | 89 | 0.315 | [0.228, 0.417] | [0.191, 0.437] |

### C1_padded vs C4

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.075 | [0.026, 0.199] | [0.000, 0.150] |
| user_pfi_emily_blender_001 | 40 | 0.550 | [0.398, 0.693] | [0.350, 0.750] |
| user_pfi_pawl_gram_001 | 40 | 0.675 | [0.520, 0.799] | [0.475, 0.850] |
| user_pfi_slalom_altar_001 | 40 | 0.050 | [0.014, 0.165] | [0.000, 0.125] |
| user_syn_calibration_goblin_001 | 40 | 0.425 | [0.285, 0.578] | [0.225, 0.625] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.125 | [0.055, 0.261] | [0.025, 0.250] |
| user_syn_high_agency_spiraler_001 | 40 | 0.225 | [0.123, 0.375] | [0.100, 0.375] |
| user_syn_patient_craftsperson_001 | 40 | 0.425 | [0.285, 0.578] | [0.250, 0.600] |

### C1 vs C1_padded

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.500 | [0.352, 0.648] | [0.325, 0.675] |
| user_pfi_emily_blender_001 | 40 | 0.550 | [0.398, 0.693] | [0.350, 0.725] |
| user_pfi_pawl_gram_001 | 40 | 0.375 | [0.242, 0.530] | [0.200, 0.575] |
| user_pfi_slalom_altar_001 | 40 | 0.425 | [0.285, 0.578] | [0.250, 0.600] |
| user_syn_calibration_goblin_001 | 40 | 0.425 | [0.285, 0.578] | [0.225, 0.625] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.425 | [0.285, 0.578] | [0.225, 0.625] |
| user_syn_high_agency_spiraler_001 | 40 | 0.475 | [0.329, 0.625] | [0.300, 0.625] |
| user_syn_patient_craftsperson_001 | 40 | 0.300 | [0.181, 0.454] | [0.175, 0.475] |

### C1 vs C4

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.075 | [0.026, 0.199] | [0.000, 0.200] |
| user_pfi_emily_blender_001 | 40 | 0.475 | [0.329, 0.625] | [0.300, 0.675] |
| user_pfi_pawl_gram_001 | 40 | 0.650 | [0.495, 0.779] | [0.475, 0.825] |
| user_pfi_slalom_altar_001 | 40 | 0.050 | [0.014, 0.165] | [0.000, 0.125] |
| user_syn_calibration_goblin_001 | 40 | 0.425 | [0.285, 0.578] | [0.250, 0.600] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.275 | [0.161, 0.428] | [0.100, 0.450] |
| user_syn_high_agency_spiraler_001 | 40 | 0.275 | [0.161, 0.428] | [0.150, 0.400] |
| user_syn_patient_craftsperson_001 | 39 | 0.385 | [0.249, 0.541] | [0.184, 0.579] |

### C3 vs C4

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.175 | [0.087, 0.320] | [0.050, 0.300] |
| user_pfi_emily_blender_001 | 40 | 0.475 | [0.329, 0.625] | [0.275, 0.650] |
| user_pfi_pawl_gram_001 | 40 | 0.575 | [0.422, 0.715] | [0.350, 0.800] |
| user_pfi_slalom_altar_001 | 40 | 0.400 | [0.264, 0.554] | [0.250, 0.550] |
| user_syn_calibration_goblin_001 | 40 | 0.400 | [0.264, 0.554] | [0.200, 0.625] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.200 | [0.105, 0.348] | [0.075, 0.350] |
| user_syn_high_agency_spiraler_001 | 40 | 0.475 | [0.329, 0.625] | [0.275, 0.675] |
| user_syn_patient_craftsperson_001 | 40 | 0.325 | [0.201, 0.480] | [0.150, 0.500] |

### C3 vs C4_WRONG_PROFILE

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.811 | [0.718, 0.879] | [0.722, 0.889] |
| user_pfi_emily_blender_001 | 90 | 0.578 | [0.475, 0.675] | [0.456, 0.700] |
| user_pfi_pawl_gram_001 | 90 | 0.600 | [0.497, 0.695] | [0.478, 0.722] |
| user_pfi_slalom_altar_001 | 90 | 0.811 | [0.718, 0.879] | [0.700, 0.911] |
| user_syn_calibration_goblin_001 | 87 | 0.563 | [0.459, 0.663] | [0.414, 0.701] |
| user_syn_conflict_allergic_moralist_001 | 90 | 0.611 | [0.508, 0.705] | [0.456, 0.756] |
| user_syn_high_agency_spiraler_001 | 90 | 0.556 | [0.453, 0.654] | [0.444, 0.678] |
| user_syn_patient_craftsperson_001 | 90 | 0.522 | [0.420, 0.622] | [0.389, 0.656] |

### C3 vs C5_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 71 | 0.437 | [0.328, 0.552] | [0.276, 0.588] |
| user_pfi_emily_blender_001 | 70 | 0.357 | [0.255, 0.474] | [0.206, 0.500] |
| user_pfi_pawl_gram_001 | 72 | 0.375 | [0.272, 0.490] | [0.237, 0.527] |
| user_pfi_slalom_altar_001 | 70 | 0.543 | [0.427, 0.654] | [0.409, 0.662] |

### C3 vs C5_NONPUBLIC

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 89 | 0.742 | [0.642, 0.821] | [0.636, 0.854] |
| user_pfi_emily_blender_001 | 90 | 0.767 | [0.669, 0.842] | [0.656, 0.867] |
| user_pfi_pawl_gram_001 | 90 | 0.556 | [0.453, 0.654] | [0.411, 0.689] |
| user_pfi_slalom_altar_001 | 90 | 0.833 | [0.743, 0.896] | [0.711, 0.944] |

### C3 vs C5_NONPUBLIC_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.644 | [0.541, 0.736] | [0.522, 0.767] |
| user_pfi_emily_blender_001 | 89 | 0.674 | [0.571, 0.763] | [0.562, 0.775] |
| user_pfi_pawl_gram_001 | 90 | 0.533 | [0.431, 0.633] | [0.400, 0.667] |
| user_pfi_slalom_altar_001 | 90 | 0.544 | [0.442, 0.643] | [0.400, 0.678] |

### C3 vs C_GENERIC_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 89 | 0.652 | [0.548, 0.743] | [0.528, 0.764] |
| user_pfi_emily_blender_001 | 90 | 0.644 | [0.541, 0.736] | [0.500, 0.778] |
| user_pfi_pawl_gram_001 | 90 | 0.544 | [0.442, 0.643] | [0.422, 0.667] |
| user_pfi_slalom_altar_001 | 90 | 0.644 | [0.541, 0.736] | [0.500, 0.767] |
| user_syn_calibration_goblin_001 | 87 | 0.425 | [0.327, 0.530] | [0.299, 0.575] |
| user_syn_conflict_allergic_moralist_001 | 90 | 0.533 | [0.431, 0.633] | [0.411, 0.656] |
| user_syn_high_agency_spiraler_001 | 90 | 0.500 | [0.399, 0.601] | [0.389, 0.611] |
| user_syn_patient_craftsperson_001 | 90 | 0.378 | [0.285, 0.481] | [0.278, 0.489] |

### C3 vs L1

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.767 | [0.669, 0.842] | [0.644, 0.878] |
| user_pfi_emily_blender_001 | 90 | 0.667 | [0.564, 0.755] | [0.533, 0.800] |
| user_pfi_pawl_gram_001 | 90 | 0.611 | [0.508, 0.705] | [0.489, 0.733] |
| user_pfi_slalom_altar_001 | 90 | 0.744 | [0.646, 0.823] | [0.600, 0.878] |

### C3 vs L2

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.689 | [0.587, 0.775] | [0.544, 0.822] |
| user_pfi_emily_blender_001 | 89 | 0.753 | [0.654, 0.831] | [0.625, 0.867] |
| user_pfi_pawl_gram_001 | 90 | 0.689 | [0.587, 0.775] | [0.556, 0.822] |
| user_pfi_slalom_altar_001 | 90 | 0.844 | [0.756, 0.905] | [0.722, 0.956] |

### C4_WRONG_PROFILE vs C5

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.356 | [0.264, 0.459] | [0.233, 0.489] |
| user_pfi_emily_blender_001 | 90 | 0.522 | [0.420, 0.622] | [0.378, 0.667] |
| user_pfi_pawl_gram_001 | 89 | 0.427 | [0.329, 0.531] | [0.295, 0.567] |
| user_pfi_slalom_altar_001 | 90 | 0.411 | [0.315, 0.514] | [0.267, 0.567] |

### C4 vs C4_WRONG_PROFILE

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.900 | [0.821, 0.947] | [0.833, 0.967] |
| user_pfi_emily_blender_001 | 90 | 0.367 | [0.275, 0.470] | [0.244, 0.500] |
| user_pfi_pawl_gram_001 | 89 | 0.337 | [0.247, 0.440] | [0.239, 0.438] |
| user_pfi_slalom_altar_001 | 90 | 0.922 | [0.848, 0.962] | [0.856, 0.978] |
| user_syn_calibration_goblin_001 | 87 | 0.517 | [0.414, 0.619] | [0.402, 0.632] |
| user_syn_conflict_allergic_moralist_001 | 90 | 0.733 | [0.634, 0.814] | [0.600, 0.856] |
| user_syn_high_agency_spiraler_001 | 90 | 0.578 | [0.475, 0.675] | [0.478, 0.689] |
| user_syn_patient_craftsperson_001 | 90 | 0.567 | [0.464, 0.664] | [0.411, 0.722] |

### C4 vs C4_shuffled

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.650 | [0.495, 0.779] | [0.450, 0.825] |
| user_pfi_emily_blender_001 | 40 | 0.425 | [0.285, 0.578] | [0.225, 0.625] |
| user_pfi_pawl_gram_001 | 40 | 0.375 | [0.242, 0.530] | [0.225, 0.525] |
| user_pfi_slalom_altar_001 | 40 | 0.725 | [0.572, 0.839] | [0.550, 0.875] |
| user_syn_calibration_goblin_001 | 40 | 0.575 | [0.422, 0.715] | [0.375, 0.775] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.650 | [0.495, 0.779] | [0.500, 0.800] |
| user_syn_high_agency_spiraler_001 | 40 | 0.275 | [0.161, 0.428] | [0.125, 0.425] |
| user_syn_patient_craftsperson_001 | 40 | 0.475 | [0.329, 0.625] | [0.300, 0.675] |

### C4 vs C5

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 70 | 0.786 | [0.676, 0.866] | [0.656, 0.909] |
| user_pfi_emily_blender_001 | 70 | 0.429 | [0.319, 0.545] | [0.274, 0.574] |
| user_pfi_pawl_gram_001 | 70 | 0.457 | [0.346, 0.573] | [0.324, 0.597] |
| user_pfi_slalom_altar_001 | 68 | 0.838 | [0.733, 0.907] | [0.742, 0.924] |

### C4 vs C5_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 71 | 0.479 | [0.367, 0.593] | [0.333, 0.623] |
| user_pfi_emily_blender_001 | 72 | 0.194 | [0.119, 0.300] | [0.087, 0.321] |
| user_pfi_pawl_gram_001 | 72 | 0.278 | [0.188, 0.391] | [0.171, 0.405] |
| user_pfi_slalom_altar_001 | 70 | 0.657 | [0.540, 0.757] | [0.517, 0.783] |

### C4 vs C5_NONPUBLIC

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.878 | [0.794, 0.930] | [0.800, 0.944] |
| user_pfi_emily_blender_001 | 90 | 0.600 | [0.497, 0.695] | [0.456, 0.733] |
| user_pfi_pawl_gram_001 | 90 | 0.378 | [0.285, 0.481] | [0.244, 0.511] |
| user_pfi_slalom_altar_001 | 90 | 0.933 | [0.862, 0.969] | [0.867, 0.989] |

### C4 vs C5_NONPUBLIC_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.789 | [0.694, 0.861] | [0.678, 0.889] |
| user_pfi_emily_blender_001 | 90 | 0.500 | [0.399, 0.601] | [0.378, 0.622] |
| user_pfi_pawl_gram_001 | 90 | 0.322 | [0.235, 0.424] | [0.211, 0.433] |
| user_pfi_slalom_altar_001 | 90 | 0.722 | [0.622, 0.804] | [0.600, 0.822] |

### C4 vs C_GENERIC_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.700 | [0.599, 0.785] | [0.578, 0.822] |
| user_pfi_emily_blender_001 | 90 | 0.522 | [0.420, 0.622] | [0.400, 0.656] |
| user_pfi_pawl_gram_001 | 90 | 0.289 | [0.205, 0.390] | [0.178, 0.411] |
| user_pfi_slalom_altar_001 | 90 | 0.800 | [0.706, 0.870] | [0.711, 0.878] |
| user_syn_calibration_goblin_001 | 87 | 0.494 | [0.392, 0.597] | [0.368, 0.632] |
| user_syn_conflict_allergic_moralist_001 | 90 | 0.744 | [0.646, 0.823] | [0.644, 0.844] |
| user_syn_high_agency_spiraler_001 | 89 | 0.472 | [0.371, 0.575] | [0.326, 0.611] |
| user_syn_patient_craftsperson_001 | 90 | 0.478 | [0.378, 0.580] | [0.356, 0.600] |

### C4 vs L3

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.822 | [0.731, 0.887] | [0.722, 0.911] |
| user_pfi_emily_blender_001 | 90 | 0.567 | [0.464, 0.664] | [0.433, 0.700] |
| user_pfi_pawl_gram_001 | 87 | 0.529 | [0.425, 0.630] | [0.391, 0.667] |
| user_pfi_slalom_altar_001 | 90 | 0.933 | [0.862, 0.969] | [0.867, 0.989] |

### C5_CONTRACT vs C5_NONPUBLIC

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.778 | [0.681, 0.851] | [0.667, 0.878] |
| user_pfi_emily_blender_001 | 89 | 0.775 | [0.678, 0.850] | [0.667, 0.865] |
| user_pfi_pawl_gram_001 | 90 | 0.589 | [0.486, 0.685] | [0.444, 0.733] |
| user_pfi_slalom_altar_001 | 90 | 0.822 | [0.731, 0.887] | [0.711, 0.922] |

### C5_CONTRACT vs C5_NONPUBLIC_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 89 | 0.685 | [0.583, 0.772] | [0.540, 0.832] |
| user_pfi_emily_blender_001 | 89 | 0.618 | [0.514, 0.712] | [0.494, 0.742] |
| user_pfi_pawl_gram_001 | 89 | 0.607 | [0.503, 0.702] | [0.489, 0.727] |
| user_pfi_slalom_altar_001 | 89 | 0.596 | [0.492, 0.692] | [0.467, 0.730] |

### C5_CONTRACT vs L1

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.733 | [0.634, 0.814] | [0.622, 0.844] |
| user_pfi_emily_blender_001 | 90 | 0.733 | [0.634, 0.814] | [0.611, 0.844] |
| user_pfi_pawl_gram_001 | 89 | 0.562 | [0.458, 0.660] | [0.444, 0.678] |
| user_pfi_slalom_altar_001 | 90 | 0.733 | [0.634, 0.814] | [0.622, 0.844] |

### C5_CONTRACT vs L3

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.811 | [0.718, 0.879] | [0.711, 0.900] |
| user_pfi_emily_blender_001 | 90 | 0.633 | [0.530, 0.726] | [0.500, 0.767] |
| user_pfi_pawl_gram_001 | 86 | 0.756 | [0.655, 0.834] | [0.632, 0.881] |
| user_pfi_slalom_altar_001 | 90 | 0.811 | [0.718, 0.879] | [0.689, 0.911] |

### C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 89 | 0.281 | [0.198, 0.382] | [0.159, 0.414] |
| user_pfi_emily_blender_001 | 89 | 0.236 | [0.160, 0.334] | [0.136, 0.352] |
| user_pfi_pawl_gram_001 | 90 | 0.422 | [0.325, 0.525] | [0.278, 0.578] |
| user_pfi_slalom_altar_001 | 90 | 0.144 | [0.086, 0.232] | [0.044, 0.267] |

### C5 vs C5_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 72 | 0.181 | [0.109, 0.285] | [0.064, 0.308] |
| user_pfi_emily_blender_001 | 72 | 0.319 | [0.223, 0.434] | [0.192, 0.444] |
| user_pfi_pawl_gram_001 | 72 | 0.319 | [0.223, 0.434] | [0.205, 0.446] |
| user_pfi_slalom_altar_001 | 71 | 0.141 | [0.078, 0.240] | [0.061, 0.236] |

### C5 vs C5_NONPUBLIC

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 89 | 0.573 | [0.469, 0.671] | [0.444, 0.700] |
| user_pfi_emily_blender_001 | 89 | 0.640 | [0.537, 0.732] | [0.529, 0.744] |
| user_pfi_pawl_gram_001 | 90 | 0.578 | [0.475, 0.675] | [0.433, 0.711] |
| user_pfi_slalom_altar_001 | 89 | 0.719 | [0.618, 0.802] | [0.596, 0.832] |

### C5 vs C_GENERIC_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.422 | [0.325, 0.525] | [0.300, 0.556] |
| user_pfi_emily_blender_001 | 90 | 0.511 | [0.409, 0.612] | [0.367, 0.656] |
| user_pfi_pawl_gram_001 | 90 | 0.511 | [0.409, 0.612] | [0.389, 0.633] |
| user_pfi_slalom_altar_001 | 90 | 0.411 | [0.315, 0.514] | [0.278, 0.544] |

### C5 vs L1

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.600 | [0.497, 0.695] | [0.456, 0.733] |
| user_pfi_emily_blender_001 | 90 | 0.622 | [0.519, 0.715] | [0.478, 0.767] |
| user_pfi_pawl_gram_001 | 90 | 0.456 | [0.357, 0.558] | [0.322, 0.589] |
| user_pfi_slalom_altar_001 | 90 | 0.500 | [0.399, 0.601] | [0.367, 0.633] |

### C5 vs L2

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.544 | [0.442, 0.643] | [0.411, 0.678] |
| user_pfi_emily_blender_001 | 90 | 0.678 | [0.576, 0.765] | [0.544, 0.811] |
| user_pfi_pawl_gram_001 | 90 | 0.611 | [0.508, 0.705] | [0.478, 0.733] |
| user_pfi_slalom_altar_001 | 90 | 0.622 | [0.519, 0.715] | [0.500, 0.744] |

### C5 vs L3

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.544 | [0.442, 0.643] | [0.389, 0.689] |
| user_pfi_emily_blender_001 | 90 | 0.533 | [0.431, 0.633] | [0.400, 0.656] |
| user_pfi_pawl_gram_001 | 86 | 0.593 | [0.487, 0.691] | [0.465, 0.721] |
| user_pfi_slalom_altar_001 | 90 | 0.511 | [0.409, 0.612] | [0.367, 0.644] |

### L1 vs L2

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 90 | 0.422 | [0.325, 0.525] | [0.278, 0.556] |
| user_pfi_emily_blender_001 | 87 | 0.471 | [0.370, 0.575] | [0.341, 0.600] |
| user_pfi_pawl_gram_001 | 90 | 0.656 | [0.553, 0.746] | [0.522, 0.789] |
| user_pfi_slalom_altar_001 | 88 | 0.477 | [0.376, 0.580] | [0.352, 0.625] |

### L2 vs L3

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 89 | 0.303 | [0.218, 0.405] | [0.191, 0.420] |
| user_pfi_emily_blender_001 | 89 | 0.169 | [0.105, 0.260] | [0.079, 0.278] |
| user_pfi_pawl_gram_001 | 87 | 0.517 | [0.414, 0.619] | [0.356, 0.667] |
| user_pfi_slalom_altar_001 | 88 | 0.307 | [0.220, 0.410] | [0.191, 0.420] |

## Scalar-pairwise reconciliation (same-author, paired cells)

For each pair, we match every pairwise record with the same judge's anchored scalar scores on both outputs. `Δ_total` is the sum across 10 dimensions (each 0–10), so a Δ of +5 means hi-condition averages 0.5 points higher per dimension. Pairs where pairwise direction does not match scalar Δ direction reveal a contradiction between holistic and rubric judging.

| pair | n_dec | hi pairwise win | Δ_total (hi−lo) | sign agree | flag |
|---|---:|---:|---:|---:|---|
| C0 vs C4 | 320 | 0.866 | +6.075 | 0.863 |  |
| C0 vs C4_WRONG_PROFILE | 556 | 0.737 | +5.746 | 0.769 |  |
| C0 vs C_GENERIC_CONTRACT | 562 | 0.799 | +6.238 | 0.815 |  |
| C1_padded vs C4 | 320 | 0.681 | +3.084 | 0.764 |  |
| C1 vs C1_padded | 320 | 0.566 | -0.441 | 0.679 | **⚠ pairwise favors hi but scalar does not** |
| C1 vs C4 | 319 | 0.674 | +2.644 | 0.753 |  |
| C3 vs C4 | 320 | 0.622 | +1.159 | 0.678 |  |
| C3 vs C4_WRONG_PROFILE | 563 | 0.378 | +0.147 | 0.670 | **⚠ pairwise favors lo but scalar does not** |
| C3 vs C5_CONTRACT | 276 | 0.576 | -0.053 | 0.711 | **⚠ pairwise favors hi but scalar does not** |
| C3 vs C5_NONPUBLIC | 283 | 0.237 | -3.525 | 0.733 |  |
| C3 vs C5_NONPUBLIC_CONTRACT | 283 | 0.382 | -0.204 | 0.594 |  |
| C3 vs C_GENERIC_CONTRACT | 562 | 0.470 | +0.639 | 0.667 |  |
| C3 vs L1 | 284 | 0.285 | -1.961 | 0.713 |  |
| C3 vs L2 | 283 | 0.205 | -3.007 | 0.751 |  |
| C4_WRONG_PROFILE vs C5 | 283 | 0.541 | -2.116 | 0.664 |  |
| C4 vs C4_WRONG_PROFILE | 562 | 0.375 | -0.938 | 0.722 |  |
| C4 vs C4_shuffled | 320 | 0.481 | -0.519 | 0.664 |  |
| C4 vs C5 | 278 | 0.374 | -3.261 | 0.784 |  |
| C4 vs C5_CONTRACT | 278 | 0.590 | -0.231 | 0.734 | **⚠ pairwise favors hi but scalar does not** |
| C4 vs C5_NONPUBLIC | 284 | 0.243 | -3.659 | 0.780 |  |
| C4 vs C5_NONPUBLIC_CONTRACT | 284 | 0.380 | -0.338 | 0.668 |  |
| C4 vs C_GENERIC_CONTRACT | 562 | 0.425 | -0.446 | 0.702 |  |
| C4 vs L3 | 283 | 0.237 | -2.905 | 0.708 |  |
| C5_CONTRACT vs C5_NONPUBLIC | 280 | 0.221 | -3.448 | 0.777 |  |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 277 | 0.354 | -0.132 | 0.646 |  |
| C5_CONTRACT vs L1 | 280 | 0.261 | -1.900 | 0.758 |  |
| C5_CONTRACT vs L3 | 279 | 0.222 | -2.729 | 0.751 |  |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 358 | 0.729 | +2.733 | 0.771 |  |
| C5 vs C5_CONTRACT | 280 | 0.768 | +3.057 | 0.794 |  |
| C5 vs C5_NONPUBLIC | 281 | 0.356 | -0.444 | 0.616 |  |
| C5 vs C_GENERIC_CONTRACT | 284 | 0.588 | +3.859 | 0.686 |  |
| C5 vs L1 | 284 | 0.447 | +1.120 | 0.704 | **⚠ pairwise favors lo but scalar does not** |
| C5 vs L2 | 284 | 0.352 | +0.074 | 0.610 | **⚠ pairwise favors lo but scalar does not** |
| C5 vs L3 | 282 | 0.443 | +0.318 | 0.698 | **⚠ pairwise favors lo but scalar does not** |
| L1 vs L2 | 355 | 0.493 | -0.947 | 0.677 |  |
| L2 vs L3 | 353 | 0.677 | +0.202 | 0.680 |  |

**Reading**: rows flagged ⚠ are the pairs where the pairwise channel tells a different story than the scalar rubric. For mechanism claims, both channels should align; flagged rows are descriptive-only until the gap is explained.

## Cross-author leak detection

**179 cross-author pairwise records detected out of 14733 total** (1.2%).

Cross-author pairwise records were generated when the --scope same_author_only flag was not consistently passed to the Opus C5_CONTRACT pairwise phase. These records are excluded from same-author analyses. If n>0 here, downstream narrative must NOT label total pairwise counts as same-author.

**By judge:**

| judge | n |
|---|---:|
| gpt-5.4 | 2 |
| gpt-5.5 | 3 |
| opus | 174 |

**By pair (concentrated where C5_CONTRACT scope leak occurred):**

| pair | n |
|---|---:|
| C3 vs C5_CONTRACT | 64 |
| C5 vs C5_CONTRACT | 58 |
| C4 vs C5_CONTRACT | 57 |

## Cluster-bootstrap CIs — stratified by judge-provider scope

Cluster unit: persona × scenario × author. Three scopes side-by-side; reviewer-requested (2026-05-15) so judge×provider halo can be checked.

- **all-judge same-author**: n=14554 records
- **cross-provider same-author** (judge family ≠ author family): n=5444 records
- **same-provider same-author** (judge family = author family): n=9110 records

| pair | n_all | lo win all | Bootstrap CI all-judge | n_xp | Bootstrap CI cross-prov | n_sp | Bootstrap CI same-prov |
|---|---:|---:|---|---:|---|---:|---|
| C0 vs C4 | 320 | 0.134 | [0.091, 0.181] | 0 | — | 320 | [0.091, 0.181] |
| C0 vs C4_WRONG_PROFILE | 710 | 0.346 | [0.299, 0.393] | 312 | [0.323, 0.445] | 398 | [0.263, 0.371] |
| C0 vs C_GENERIC_CONTRACT | 716 | 0.278 | [0.236, 0.324] | 317 | [0.279, 0.403] | 399 | [0.180, 0.273] |
| C1_padded vs C4 | 320 | 0.319 | [0.256, 0.384] | 0 | — | 320 | [0.256, 0.384] |
| C1 vs C1_padded | 320 | 0.434 | [0.372, 0.506] | 0 | — | 320 | [0.372, 0.506] |
| C1 vs C4 | 319 | 0.326 | [0.263, 0.391] | 0 | — | 319 | [0.263, 0.391] |
| C3 vs C4 | 320 | 0.378 | [0.312, 0.447] | 0 | — | 320 | [0.312, 0.447] |
| C3 vs C4_WRONG_PROFILE | 717 | 0.632 | [0.586, 0.675] | 318 | [0.576, 0.690] | 399 | [0.576, 0.688] |
| C3 vs C5_CONTRACT | 283 | 0.428 | [0.354, 0.503] | 85 | [0.241, 0.444] | 198 | [0.382, 0.550] |
| C3 vs C5_NONPUBLIC | 359 | 0.724 | [0.661, 0.785] | 159 | [0.612, 0.770] | 200 | [0.678, 0.820] |
| C3 vs C5_NONPUBLIC_CONTRACT | 359 | 0.599 | [0.533, 0.664] | 159 | [0.512, 0.679] | 200 | [0.523, 0.680] |
| C3 vs C_GENERIC_CONTRACT | 716 | 0.540 | [0.494, 0.587] | 317 | [0.509, 0.633] | 399 | [0.463, 0.573] |
| C3 vs L1 | 360 | 0.697 | [0.631, 0.758] | 160 | [0.572, 0.737] | 200 | [0.655, 0.801] |
| C3 vs L2 | 359 | 0.744 | [0.677, 0.806] | 159 | [0.599, 0.768] | 200 | [0.715, 0.859] |
| C4_WRONG_PROFILE vs C5 | 359 | 0.429 | [0.356, 0.500] | 159 | [0.333, 0.500] | 200 | [0.357, 0.524] |
| C4 vs C4_WRONG_PROFILE | 716 | 0.616 | [0.568, 0.665] | 317 | [0.552, 0.668] | 399 | [0.559, 0.676] |
| C4 vs C4_shuffled | 320 | 0.519 | [0.456, 0.584] | 0 | — | 320 | [0.456, 0.584] |
| C4 vs C5 | 278 | 0.626 | [0.550, 0.700] | 80 | [0.562, 0.775] | 198 | [0.523, 0.690] |
| C4 vs C5_CONTRACT | 285 | 0.400 | [0.324, 0.476] | 86 | [0.294, 0.500] | 199 | [0.326, 0.485] |
| C4 vs C5_NONPUBLIC | 360 | 0.697 | [0.625, 0.764] | 160 | [0.549, 0.729] | 200 | [0.665, 0.819] |
| C4 vs C5_NONPUBLIC_CONTRACT | 360 | 0.583 | [0.517, 0.653] | 160 | [0.446, 0.618] | 200 | [0.540, 0.707] |
| C4 vs C_GENERIC_CONTRACT | 716 | 0.563 | [0.515, 0.609] | 318 | [0.524, 0.649] | 398 | [0.489, 0.597] |
| C4 vs L3 | 357 | 0.714 | [0.647, 0.776] | 158 | [0.587, 0.760] | 199 | [0.672, 0.820] |
| C5_CONTRACT vs C5_NONPUBLIC | 359 | 0.741 | [0.677, 0.802] | 159 | [0.615, 0.781] | 200 | [0.706, 0.840] |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 356 | 0.626 | [0.557, 0.694] | 158 | [0.535, 0.702] | 198 | [0.552, 0.707] |
| C5_CONTRACT vs L1 | 359 | 0.691 | [0.631, 0.750] | 159 | [0.567, 0.736] | 200 | [0.653, 0.792] |
| C5_CONTRACT vs L3 | 356 | 0.753 | [0.695, 0.811] | 157 | [0.675, 0.824] | 199 | [0.675, 0.824] |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | 358 | 0.271 | [0.207, 0.336] | 159 | [0.209, 0.373] | 199 | [0.189, 0.327] |
| C5 vs C5_CONTRACT | 287 | 0.240 | [0.184, 0.301] | 88 | [0.207, 0.411] | 199 | [0.153, 0.270] |
| C5 vs C5_NONPUBLIC | 357 | 0.627 | [0.563, 0.692] | 158 | [0.540, 0.699] | 199 | [0.556, 0.709] |
| C5 vs C_GENERIC_CONTRACT | 360 | 0.464 | [0.400, 0.533] | 160 | [0.442, 0.616] | 200 | [0.330, 0.490] |
| C5 vs L1 | 360 | 0.544 | [0.469, 0.614] | 160 | [0.438, 0.611] | 200 | [0.477, 0.646] |
| C5 vs L2 | 360 | 0.614 | [0.550, 0.678] | 160 | [0.491, 0.658] | 200 | [0.565, 0.722] |
| C5 vs L3 | 356 | 0.545 | [0.476, 0.611] | 157 | [0.431, 0.606] | 199 | [0.487, 0.646] |
| L1 vs L2 | 355 | 0.507 | [0.438, 0.577] | 155 | [0.396, 0.567] | 200 | [0.447, 0.604] |
| L2 vs L3 | 353 | 0.323 | [0.256, 0.391] | 155 | [0.226, 0.386] | 198 | [0.262, 0.416] |

**Reading note**: pairs with `n_xp = 0` were judged only by same-provider judges; their CIs cannot be compared across scopes. Non-zero `n_xp` pairs (C5_CONTRACT edges) are where provider-stratified comparison is meaningful.

## Scenario-family forest plot (same-author pairwise)

Reviewers (consolidated §3.1 #6, codex-council unanimous) flagged scenario-family heterogeneity should be promoted from appendix to primary. Below: per-pair × per-family lo decisive win rate + Wilson CI. Pairs reversed in at least one family are flagged ⚠. The lo win rate is the win rate of the lower-numbered condition; values > 0.5 favor lo, < 0.5 favor hi.

### C0 vs C4

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 32 | 0.156 | [0.069, 0.318] |
| authority_disagreement | 32 | 0.188 | [0.089, 0.353] |
| creative_feedback | 32 | 0.250 | [0.133, 0.421] |
| epistemic_uncertainty | 32 | 0.188 | [0.089, 0.353] |
| interpersonal_conflict | 64 | 0.094 | [0.044, 0.190] |
| moral_uncertainty | 32 | 0.156 | [0.069, 0.318] |
| procrastination_avoidance | 32 | 0.062 | [0.017, 0.202] |
| shame_self_interpretation | 64 | 0.078 | [0.034, 0.170] |

### C0 vs C4_WRONG_PROFILE

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 72 | 0.403 | [0.297, 0.518] |
| authority_disagreement | 71 | 0.324 | [0.227, 0.439] |
| creative_feedback | 71 | 0.408 | [0.302, 0.525] |
| epistemic_uncertainty | 72 | 0.458 | [0.348, 0.573] |
| interpersonal_conflict | 140 | 0.271 | [0.205, 0.350] |
| moral_uncertainty | 72 | 0.292 | [0.199, 0.405] |
| procrastination_avoidance | 71 | 0.324 | [0.227, 0.439] |
| shame_self_interpretation | 141 | 0.355 | [0.281, 0.436] |

### C0 vs C_GENERIC_CONTRACT

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 72 | 0.278 | [0.188, 0.391] |
| authority_disagreement | 72 | 0.139 | [0.077, 0.237] |
| creative_feedback | 72 | 0.292 | [0.199, 0.405] |
| epistemic_uncertainty | 72 | 0.333 | [0.235, 0.448] |
| interpersonal_conflict | 144 | 0.215 | [0.156, 0.289] |
| moral_uncertainty | 72 | 0.375 | [0.272, 0.490] |
| procrastination_avoidance | 71 | 0.451 | [0.341, 0.566] |
| shame_self_interpretation | 141 | 0.241 | [0.178, 0.318] |

### C1_padded vs C4

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 32 | 0.375 | [0.229, 0.547] |
| authority_disagreement | 32 | 0.406 | [0.255, 0.577] |
| creative_feedback | 32 | 0.344 | [0.204, 0.517] |
| epistemic_uncertainty | 32 | 0.375 | [0.229, 0.547] |
| interpersonal_conflict | 64 | 0.172 | [0.099, 0.282] |
| moral_uncertainty | 32 | 0.281 | [0.156, 0.454] |
| procrastination_avoidance | 32 | 0.469 | [0.309, 0.635] |
| shame_self_interpretation | 64 | 0.297 | [0.199, 0.418] |

### C1 vs C1_padded ⚠ STRICT reversal (CI excludes 0.5) in: creative_feedback ⚠ point-estimate reversal in: moral_uncertainty

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 32 | 0.344 | [0.204, 0.517] |
| authority_disagreement | 32 | 0.500 | [0.336, 0.664] |
| creative_feedback ⚠⚠ | 32 | 0.688 | [0.514, 0.821] |
| epistemic_uncertainty | 32 | 0.500 | [0.336, 0.664] |
| interpersonal_conflict | 64 | 0.344 | [0.239, 0.466] |
| moral_uncertainty ⚠ | 32 | 0.562 | [0.393, 0.718] |
| procrastination_avoidance | 32 | 0.312 | [0.179, 0.486] |
| shame_self_interpretation | 64 | 0.375 | [0.267, 0.497] |

### C1 vs C4 ⚠ point-estimate reversal in: creative_feedback

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 32 | 0.250 | [0.133, 0.421] |
| authority_disagreement | 32 | 0.469 | [0.309, 0.635] |
| creative_feedback ⚠ | 31 | 0.516 | [0.348, 0.680] |
| epistemic_uncertainty | 32 | 0.500 | [0.336, 0.664] |
| interpersonal_conflict | 64 | 0.188 | [0.111, 0.300] |
| moral_uncertainty | 32 | 0.438 | [0.282, 0.607] |
| procrastination_avoidance | 32 | 0.219 | [0.110, 0.388] |
| shame_self_interpretation | 64 | 0.250 | [0.160, 0.368] |

### C3 vs C4

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 32 | 0.500 | [0.336, 0.664] |
| authority_disagreement | 32 | 0.500 | [0.336, 0.664] |
| creative_feedback | 32 | 0.406 | [0.255, 0.577] |
| epistemic_uncertainty | 32 | 0.312 | [0.179, 0.486] |
| interpersonal_conflict | 64 | 0.281 | [0.186, 0.401] |
| moral_uncertainty | 32 | 0.469 | [0.309, 0.635] |
| procrastination_avoidance | 32 | 0.250 | [0.133, 0.421] |
| shame_self_interpretation | 64 | 0.391 | [0.281, 0.513] |

### C3 vs C4_WRONG_PROFILE ⚠ point-estimate reversal in: procrastination_avoidance

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 72 | 0.653 | [0.538, 0.752] |
| authority_disagreement | 72 | 0.764 | [0.654, 0.847] |
| creative_feedback | 72 | 0.625 | [0.509, 0.728] |
| epistemic_uncertainty | 72 | 0.694 | [0.581, 0.789] |
| interpersonal_conflict | 144 | 0.611 | [0.530, 0.687] |
| moral_uncertainty | 72 | 0.597 | [0.482, 0.703] |
| procrastination_avoidance ⚠ | 72 | 0.500 | [0.388, 0.613] |
| shame_self_interpretation | 141 | 0.631 | [0.549, 0.706] |

### C3 vs C5_CONTRACT ⚠ point-estimate reversal in: epistemic_uncertainty, shame_self_interpretation

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 28 | 0.429 | [0.265, 0.609] |
| authority_disagreement | 28 | 0.250 | [0.127, 0.434] |
| creative_feedback | 28 | 0.321 | [0.179, 0.507] |
| epistemic_uncertainty ⚠ | 28 | 0.643 | [0.458, 0.793] |
| interpersonal_conflict | 63 | 0.429 | [0.314, 0.551] |
| moral_uncertainty | 27 | 0.222 | [0.106, 0.408] |
| procrastination_avoidance | 27 | 0.444 | [0.276, 0.627] |
| shame_self_interpretation ⚠ | 54 | 0.556 | [0.424, 0.680] |

### C3 vs C5_NONPUBLIC ⚠ point-estimate reversal in: procrastination_avoidance

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.806 | [0.650, 0.902] |
| authority_disagreement | 36 | 0.722 | [0.560, 0.842] |
| creative_feedback | 36 | 0.583 | [0.422, 0.729] |
| epistemic_uncertainty | 36 | 0.694 | [0.531, 0.820] |
| interpersonal_conflict | 71 | 0.732 | [0.620, 0.822] |
| moral_uncertainty | 36 | 0.917 | [0.782, 0.971] |
| procrastination_avoidance ⚠ | 36 | 0.472 | [0.320, 0.630] |
| shame_self_interpretation | 72 | 0.792 | [0.684, 0.870] |

### C3 vs C5_NONPUBLIC_CONTRACT ⚠ point-estimate reversal in: ambition_status, procrastination_avoidance

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status ⚠ | 36 | 0.500 | [0.345, 0.655] |
| authority_disagreement | 36 | 0.639 | [0.476, 0.775] |
| creative_feedback | 36 | 0.556 | [0.396, 0.705] |
| epistemic_uncertainty | 36 | 0.778 | [0.619, 0.883] |
| interpersonal_conflict | 72 | 0.667 | [0.552, 0.765] |
| moral_uncertainty | 35 | 0.686 | [0.520, 0.815] |
| procrastination_avoidance ⚠ | 36 | 0.361 | [0.225, 0.524] |
| shame_self_interpretation | 72 | 0.569 | [0.454, 0.677] |

### C3 vs C_GENERIC_CONTRACT ⚠ point-estimate reversal in: creative_feedback, epistemic_uncertainty, interpersonal_conflict

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 72 | 0.528 | [0.414, 0.639] |
| authority_disagreement | 72 | 0.542 | [0.427, 0.652] |
| creative_feedback ⚠ | 72 | 0.458 | [0.348, 0.573] |
| epistemic_uncertainty ⚠ | 72 | 0.500 | [0.388, 0.613] |
| interpersonal_conflict ⚠ | 143 | 0.469 | [0.389, 0.550] |
| moral_uncertainty | 72 | 0.653 | [0.538, 0.752] |
| procrastination_avoidance | 72 | 0.597 | [0.482, 0.703] |
| shame_self_interpretation | 141 | 0.596 | [0.513, 0.673] |

### C3 vs L1 ⚠ point-estimate reversal in: creative_feedback

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.667 | [0.503, 0.798] |
| authority_disagreement | 36 | 0.806 | [0.650, 0.902] |
| creative_feedback ⚠ | 36 | 0.500 | [0.345, 0.655] |
| epistemic_uncertainty | 36 | 0.833 | [0.681, 0.921] |
| interpersonal_conflict | 72 | 0.625 | [0.509, 0.728] |
| moral_uncertainty | 36 | 0.667 | [0.503, 0.798] |
| procrastination_avoidance | 36 | 0.694 | [0.531, 0.820] |
| shame_self_interpretation | 72 | 0.778 | [0.669, 0.858] |

### C3 vs L2

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.861 | [0.713, 0.939] |
| authority_disagreement | 35 | 0.771 | [0.610, 0.879] |
| creative_feedback | 36 | 0.611 | [0.449, 0.752] |
| epistemic_uncertainty | 36 | 0.639 | [0.476, 0.775] |
| interpersonal_conflict | 72 | 0.694 | [0.581, 0.789] |
| moral_uncertainty | 36 | 0.889 | [0.747, 0.956] |
| procrastination_avoidance | 36 | 0.694 | [0.531, 0.820] |
| shame_self_interpretation | 72 | 0.792 | [0.684, 0.870] |

### C4_WRONG_PROFILE vs C5 ⚠ point-estimate reversal in: ambition_status, interpersonal_conflict

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status ⚠ | 36 | 0.528 | [0.370, 0.680] |
| authority_disagreement | 36 | 0.250 | [0.138, 0.411] |
| creative_feedback | 36 | 0.333 | [0.202, 0.497] |
| epistemic_uncertainty | 36 | 0.389 | [0.248, 0.551] |
| interpersonal_conflict ⚠ | 72 | 0.542 | [0.427, 0.652] |
| moral_uncertainty | 36 | 0.389 | [0.248, 0.551] |
| procrastination_avoidance | 35 | 0.486 | [0.330, 0.644] |
| shame_self_interpretation | 72 | 0.417 | [0.310, 0.532] |

### C4 vs C4_WRONG_PROFILE

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 72 | 0.542 | [0.427, 0.652] |
| authority_disagreement | 72 | 0.653 | [0.538, 0.752] |
| creative_feedback | 72 | 0.569 | [0.454, 0.677] |
| epistemic_uncertainty | 72 | 0.639 | [0.523, 0.740] |
| interpersonal_conflict | 143 | 0.636 | [0.555, 0.711] |
| moral_uncertainty | 72 | 0.569 | [0.454, 0.677] |
| procrastination_avoidance | 72 | 0.639 | [0.523, 0.740] |
| shame_self_interpretation | 141 | 0.638 | [0.556, 0.713] |

### C4 vs C4_shuffled ⚠ point-estimate reversal in: ambition_status, authority_disagreement, moral_uncertainty, procrastination_avoidance, shame_self_interpretation

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status ⚠ | 32 | 0.469 | [0.309, 0.635] |
| authority_disagreement ⚠ | 32 | 0.500 | [0.336, 0.664] |
| creative_feedback | 32 | 0.594 | [0.423, 0.745] |
| epistemic_uncertainty | 32 | 0.781 | [0.613, 0.890] |
| interpersonal_conflict | 64 | 0.516 | [0.396, 0.634] |
| moral_uncertainty ⚠ | 32 | 0.438 | [0.282, 0.607] |
| procrastination_avoidance ⚠ | 32 | 0.438 | [0.282, 0.607] |
| shame_self_interpretation ⚠ | 64 | 0.469 | [0.352, 0.589] |

### C4 vs C5 ⚠ point-estimate reversal in: ambition_status, moral_uncertainty

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status ⚠ | 28 | 0.393 | [0.236, 0.576] |
| authority_disagreement | 27 | 0.593 | [0.407, 0.755] |
| creative_feedback | 28 | 0.679 | [0.493, 0.821] |
| epistemic_uncertainty | 28 | 0.679 | [0.493, 0.821] |
| interpersonal_conflict | 55 | 0.727 | [0.598, 0.827] |
| moral_uncertainty ⚠ | 28 | 0.429 | [0.265, 0.609] |
| procrastination_avoidance | 28 | 0.679 | [0.493, 0.821] |
| shame_self_interpretation | 56 | 0.679 | [0.548, 0.786] |

### C4 vs C5_CONTRACT ⚠ point-estimate reversal in: epistemic_uncertainty

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 28 | 0.286 | [0.152, 0.471] |
| authority_disagreement | 26 | 0.269 | [0.137, 0.461] |
| creative_feedback | 28 | 0.357 | [0.207, 0.542] |
| epistemic_uncertainty ⚠ | 28 | 0.536 | [0.358, 0.705] |
| interpersonal_conflict | 63 | 0.381 | [0.271, 0.504] |
| moral_uncertainty | 28 | 0.321 | [0.179, 0.507] |
| procrastination_avoidance | 28 | 0.500 | [0.326, 0.674] |
| shame_self_interpretation | 56 | 0.482 | [0.357, 0.610] |

### C4 vs C5_NONPUBLIC ⚠ point-estimate reversal in: procrastination_avoidance

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.694 | [0.531, 0.820] |
| authority_disagreement | 36 | 0.778 | [0.619, 0.883] |
| creative_feedback | 36 | 0.639 | [0.476, 0.775] |
| epistemic_uncertainty | 36 | 0.611 | [0.449, 0.752] |
| interpersonal_conflict | 72 | 0.778 | [0.669, 0.858] |
| moral_uncertainty | 36 | 0.639 | [0.476, 0.775] |
| procrastination_avoidance ⚠ | 36 | 0.500 | [0.345, 0.655] |
| shame_self_interpretation | 72 | 0.778 | [0.669, 0.858] |

### C4 vs C5_NONPUBLIC_CONTRACT ⚠ point-estimate reversal in: ambition_status, creative_feedback

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status ⚠ | 36 | 0.361 | [0.225, 0.524] |
| authority_disagreement | 36 | 0.583 | [0.422, 0.729] |
| creative_feedback ⚠ | 36 | 0.472 | [0.320, 0.630] |
| epistemic_uncertainty | 36 | 0.639 | [0.476, 0.775] |
| interpersonal_conflict | 72 | 0.681 | [0.566, 0.777] |
| moral_uncertainty | 36 | 0.556 | [0.396, 0.705] |
| procrastination_avoidance | 36 | 0.583 | [0.422, 0.729] |
| shame_self_interpretation | 72 | 0.639 | [0.523, 0.740] |

### C4 vs C_GENERIC_CONTRACT ⚠ point-estimate reversal in: authority_disagreement, creative_feedback, interpersonal_conflict

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 72 | 0.514 | [0.401, 0.626] |
| authority_disagreement ⚠ | 71 | 0.408 | [0.302, 0.525] |
| creative_feedback ⚠ | 72 | 0.500 | [0.388, 0.613] |
| epistemic_uncertainty | 72 | 0.514 | [0.401, 0.626] |
| interpersonal_conflict ⚠ | 144 | 0.500 | [0.419, 0.581] |
| moral_uncertainty | 72 | 0.667 | [0.552, 0.765] |
| procrastination_avoidance | 72 | 0.736 | [0.624, 0.824] |
| shame_self_interpretation | 141 | 0.645 | [0.564, 0.720] |

### C4 vs L3

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.556 | [0.396, 0.705] |
| authority_disagreement | 36 | 0.639 | [0.476, 0.775] |
| creative_feedback | 36 | 0.667 | [0.503, 0.798] |
| epistemic_uncertainty | 36 | 0.583 | [0.422, 0.729] |
| interpersonal_conflict | 72 | 0.778 | [0.669, 0.858] |
| moral_uncertainty | 36 | 0.722 | [0.560, 0.842] |
| procrastination_avoidance | 36 | 0.694 | [0.531, 0.820] |
| shame_self_interpretation | 69 | 0.870 | [0.770, 0.930] |

### C5_CONTRACT vs C5_NONPUBLIC ⚠ point-estimate reversal in: procrastination_avoidance

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.833 | [0.681, 0.921] |
| authority_disagreement | 35 | 0.743 | [0.579, 0.858] |
| creative_feedback | 36 | 0.694 | [0.531, 0.820] |
| epistemic_uncertainty | 36 | 0.528 | [0.370, 0.680] |
| interpersonal_conflict | 72 | 0.819 | [0.715, 0.891] |
| moral_uncertainty | 36 | 0.833 | [0.681, 0.921] |
| procrastination_avoidance ⚠ | 36 | 0.444 | [0.295, 0.604] |
| shame_self_interpretation | 72 | 0.847 | [0.747, 0.912] |

### C5_CONTRACT vs C5_NONPUBLIC_CONTRACT

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.639 | [0.476, 0.775] |
| authority_disagreement | 35 | 0.657 | [0.491, 0.792] |
| creative_feedback | 36 | 0.611 | [0.449, 0.752] |
| epistemic_uncertainty | 36 | 0.639 | [0.476, 0.775] |
| interpersonal_conflict | 69 | 0.681 | [0.564, 0.779] |
| moral_uncertainty | 36 | 0.639 | [0.476, 0.775] |
| procrastination_avoidance | 36 | 0.611 | [0.449, 0.752] |
| shame_self_interpretation | 72 | 0.556 | [0.441, 0.665] |

### C5_CONTRACT vs L1

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.722 | [0.560, 0.842] |
| authority_disagreement | 35 | 0.686 | [0.520, 0.815] |
| creative_feedback | 36 | 0.639 | [0.476, 0.775] |
| epistemic_uncertainty | 36 | 0.611 | [0.449, 0.752] |
| interpersonal_conflict | 72 | 0.611 | [0.496, 0.715] |
| moral_uncertainty | 36 | 0.750 | [0.589, 0.863] |
| procrastination_avoidance | 36 | 0.667 | [0.503, 0.798] |
| shame_self_interpretation | 72 | 0.806 | [0.700, 0.880] |

### C5_CONTRACT vs L3

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.722 | [0.560, 0.842] |
| authority_disagreement | 36 | 0.806 | [0.650, 0.902] |
| creative_feedback | 36 | 0.778 | [0.619, 0.883] |
| epistemic_uncertainty | 36 | 0.556 | [0.396, 0.705] |
| interpersonal_conflict | 72 | 0.708 | [0.595, 0.801] |
| moral_uncertainty | 36 | 0.722 | [0.560, 0.842] |
| procrastination_avoidance | 35 | 0.771 | [0.610, 0.879] |
| shame_self_interpretation | 69 | 0.884 | [0.787, 0.940] |

### C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT ⚠ point-estimate reversal in: procrastination_avoidance

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.167 | [0.079, 0.319] |
| authority_disagreement | 36 | 0.222 | [0.117, 0.381] |
| creative_feedback | 36 | 0.361 | [0.225, 0.524] |
| epistemic_uncertainty | 36 | 0.417 | [0.271, 0.578] |
| interpersonal_conflict | 71 | 0.197 | [0.121, 0.304] |
| moral_uncertainty | 36 | 0.278 | [0.159, 0.440] |
| procrastination_avoidance ⚠ | 36 | 0.556 | [0.396, 0.705] |
| shame_self_interpretation | 71 | 0.155 | [0.089, 0.257] |

### C5 vs C5_CONTRACT

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 28 | 0.321 | [0.179, 0.507] |
| authority_disagreement | 27 | 0.185 | [0.082, 0.367] |
| creative_feedback | 28 | 0.250 | [0.127, 0.434] |
| epistemic_uncertainty | 28 | 0.357 | [0.207, 0.542] |
| interpersonal_conflict | 64 | 0.250 | [0.160, 0.368] |
| moral_uncertainty | 28 | 0.250 | [0.127, 0.434] |
| procrastination_avoidance | 28 | 0.286 | [0.152, 0.471] |
| shame_self_interpretation | 56 | 0.125 | [0.062, 0.236] |

### C5 vs C5_NONPUBLIC ⚠ point-estimate reversal in: epistemic_uncertainty, procrastination_avoidance

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.694 | [0.531, 0.820] |
| authority_disagreement | 36 | 0.833 | [0.681, 0.921] |
| creative_feedback | 36 | 0.556 | [0.396, 0.705] |
| epistemic_uncertainty ⚠ | 36 | 0.472 | [0.320, 0.630] |
| interpersonal_conflict | 69 | 0.710 | [0.594, 0.804] |
| moral_uncertainty | 36 | 0.639 | [0.476, 0.775] |
| procrastination_avoidance ⚠ | 36 | 0.417 | [0.271, 0.578] |
| shame_self_interpretation | 72 | 0.625 | [0.509, 0.728] |

### C5 vs C_GENERIC_CONTRACT ⚠ STRICT reversal (CI excludes 0.5) in: moral_uncertainty ⚠ point-estimate reversal in: ambition_status, authority_disagreement, creative_feedback, procrastination_avoidance

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status ⚠ | 36 | 0.556 | [0.396, 0.705] |
| authority_disagreement ⚠ | 36 | 0.556 | [0.396, 0.705] |
| creative_feedback ⚠ | 36 | 0.556 | [0.396, 0.705] |
| epistemic_uncertainty | 36 | 0.361 | [0.225, 0.524] |
| interpersonal_conflict | 72 | 0.306 | [0.211, 0.419] |
| moral_uncertainty ⚠⚠ | 36 | 0.667 | [0.503, 0.798] |
| procrastination_avoidance ⚠ | 36 | 0.556 | [0.396, 0.705] |
| shame_self_interpretation | 72 | 0.389 | [0.285, 0.504] |

### C5 vs L1 ⚠ point-estimate reversal in: epistemic_uncertainty, interpersonal_conflict

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.528 | [0.370, 0.680] |
| authority_disagreement | 36 | 0.611 | [0.449, 0.752] |
| creative_feedback | 36 | 0.639 | [0.476, 0.775] |
| epistemic_uncertainty ⚠ | 36 | 0.500 | [0.345, 0.655] |
| interpersonal_conflict ⚠ | 72 | 0.500 | [0.388, 0.613] |
| moral_uncertainty | 36 | 0.611 | [0.449, 0.752] |
| procrastination_avoidance | 36 | 0.528 | [0.370, 0.680] |
| shame_self_interpretation | 72 | 0.514 | [0.401, 0.626] |

### C5 vs L2 ⚠ point-estimate reversal in: creative_feedback

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.583 | [0.422, 0.729] |
| authority_disagreement | 36 | 0.694 | [0.531, 0.820] |
| creative_feedback ⚠ | 36 | 0.444 | [0.295, 0.604] |
| epistemic_uncertainty | 36 | 0.667 | [0.503, 0.798] |
| interpersonal_conflict | 72 | 0.611 | [0.496, 0.715] |
| moral_uncertainty | 36 | 0.722 | [0.560, 0.842] |
| procrastination_avoidance | 36 | 0.639 | [0.476, 0.775] |
| shame_self_interpretation | 72 | 0.583 | [0.468, 0.690] |

### C5 vs L3 ⚠ point-estimate reversal in: ambition_status, epistemic_uncertainty

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status ⚠ | 36 | 0.472 | [0.320, 0.630] |
| authority_disagreement | 36 | 0.611 | [0.449, 0.752] |
| creative_feedback | 36 | 0.556 | [0.396, 0.705] |
| epistemic_uncertainty ⚠ | 36 | 0.444 | [0.295, 0.604] |
| interpersonal_conflict | 72 | 0.528 | [0.414, 0.639] |
| moral_uncertainty | 36 | 0.583 | [0.422, 0.729] |
| procrastination_avoidance | 35 | 0.571 | [0.409, 0.720] |
| shame_self_interpretation | 69 | 0.580 | [0.462, 0.689] |

### L1 vs L2 ⚠ STRICT reversal (CI excludes 0.5) in: procrastination_avoidance ⚠ point-estimate reversal in: ambition_status, interpersonal_conflict, moral_uncertainty, shame_self_interpretation

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status ⚠ | 36 | 0.556 | [0.396, 0.705] |
| authority_disagreement | 36 | 0.306 | [0.180, 0.469] |
| creative_feedback | 36 | 0.500 | [0.345, 0.655] |
| epistemic_uncertainty | 36 | 0.333 | [0.202, 0.497] |
| interpersonal_conflict ⚠ | 69 | 0.522 | [0.406, 0.635] |
| moral_uncertainty ⚠ | 35 | 0.514 | [0.356, 0.670] |
| procrastination_avoidance ⚠⚠ | 36 | 0.667 | [0.503, 0.798] |
| shame_self_interpretation ⚠ | 71 | 0.578 | [0.462, 0.685] |

### L2 vs L3

| scenario family | n_dec | lo win | Wilson CI95 |
|---|---:|---:|---|
| ambition_status | 36 | 0.250 | [0.138, 0.411] |
| authority_disagreement | 35 | 0.314 | [0.185, 0.480] |
| creative_feedback | 36 | 0.361 | [0.225, 0.524] |
| epistemic_uncertainty | 36 | 0.417 | [0.271, 0.578] |
| interpersonal_conflict | 70 | 0.286 | [0.193, 0.401] |
| moral_uncertainty | 36 | 0.167 | [0.079, 0.319] |
| procrastination_avoidance | 35 | 0.429 | [0.280, 0.591] |
| shame_self_interpretation | 69 | 0.362 | [0.259, 0.480] |

## Scalar inter-judge agreement (legacy 0–5)

No dimensions flagged as weak-agreement (all judge pairs Pearson ≥ 0.30).

| judge pair | mean Pearson | mean Spearman | n_dimensions |
|---|---:|---:|---:|

## Scalar inter-judge agreement (anchored 0–10)

No dimensions flagged as weak-agreement (all judge pairs Pearson ≥ 0.30).

| judge pair | mean Pearson | mean Spearman | n_dimensions |
|---|---:|---:|---:|
| gpt-5.4 vs gpt-5.5 | 0.6888 | 0.6045 | 10 |
| gpt-5.4 vs opus | 0.6560 | 0.5702 | 10 |
| gpt-5.5 vs opus | 0.6285 | 0.5151 | 10 |

## Red-flag stratification
