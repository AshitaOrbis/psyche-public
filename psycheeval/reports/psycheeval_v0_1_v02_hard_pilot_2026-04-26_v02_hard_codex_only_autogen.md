# PsycheEval v0.1 — v02_hard_pilot — run 2026-04-26_v02_hard_codex_only (auto-generated)

> Auto-generated numeric scaffold. The human-curated narrative report lives at `psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only.md`. This file contains only tables computed from `metrics_2026-04-26_v02_hard_codex_only.json`. Regenerating analyze.py will overwrite this file but never the curated one.

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
- **assistant_outputs**: 1680
- **judge_scores**: 0
- **anchored_judge_scores**: 3949
- **pairwise_scores**: 3243

## Pairwise results (cross-provider judged)

### Counts

- **total_pairwise_records**: 3243
- **after_tagging**: 3243
- **same_author**: 3064
- **cross_author**: 179
- **cross_provider**: 441
- **cross_provider_same_author**: 344
- **cross_provider_same_author_PI**: 344

### Condition win-rate (same-author pairs, cross-provider judged)

Ties contribute 0.5 to each side. Same-author pairs isolate condition effects from author effects.

- **C3**: 0.347
- **C4**: 0.530
- **C5**: 0.315
- **C5_CONTRACT**: 0.650

### Condition-pair preferences (same-author, cross-provider)

| pair | n | first wins | second wins | ties |
|---|---|---|---|---|
| C3 vs C5_CONTRACT | 88 | 0.330 | 0.636 | 0.034 |
| C4 vs C5 | 80 | 0.675 | 0.325 | 0.000 |
| C4 vs C5_CONTRACT | 88 | 0.386 | 0.591 | 0.023 |
| C5 vs C5_CONTRACT | 88 | 0.307 | 0.693 | 0.000 |

### Condition-pair preferences (PI-only, same-author, cross-provider)

C5 pairs appear here and here only — never in the all-persona block.

| pair | n | first wins | second wins | ties |
|---|---|---|---|---|
| C3 vs C5_CONTRACT | 88 | 0.330 | 0.636 | 0.034 |
| C4 vs C5 | 80 | 0.675 | 0.325 | 0.000 |
| C4 vs C5_CONTRACT | 88 | 0.386 | 0.591 | 0.023 |
| C5 vs C5_CONTRACT | 88 | 0.307 | 0.693 | 0.000 |

---

## Appendix A — Secondary: all-judge means

**Do not use these as primary results.** Same-provider scores are included. See halo audit for why this matters. Kept for audit only.

---

## Tie rates (same-author, all-judges-pooled)

| pair | total | decisive | ties | tie_rate | lo decisive win |
|---|---:|---:|---:|---:|---:|
| C0 vs C4 | 320 | 320 | 0 | 0.0000 | 0.1344 |
| C1_padded vs C4 | 320 | 320 | 0 | 0.0000 | 0.3187 |
| C1 vs C1_padded | 320 | 320 | 0 | 0.0000 | 0.4344 |
| C1 vs C4 | 320 | 319 | 1 | 0.0031 | 0.3260 |
| C3 vs C4 | 320 | 320 | 0 | 0.0000 | 0.3781 |
| C3 vs C5_CONTRACT | 288 | 283 | 5 | 0.0174 | 0.4276 |
| C4 vs C4_shuffled | 320 | 320 | 0 | 0.0000 | 0.5188 |
| C4 vs C5 | 280 | 278 | 2 | 0.0071 | 0.6259 |
| C4 vs C5_CONTRACT | 288 | 285 | 3 | 0.0104 | 0.4000 |
| C5 vs C5_CONTRACT | 288 | 287 | 1 | 0.0035 | 0.2404 |

## PI/PS split pairwise (same-author, all-judges-pooled, non-C5 pairs)

| pair | PI lo win | PI CI95 | PI n | PS lo win | PS CI95 | PS n |
|---|---:|---|---:|---:|---|---:|
| C0 vs C4 | 0.1062 | [0.0674, 0.1636] | 160 | 0.1625 | [0.1134, 0.2275] | 160 |
| C1_padded vs C4 | 0.3375 | [0.2688, 0.4138] | 160 | 0.3000 | [0.2344, 0.3750] | 160 |
| C1 vs C1_padded | 0.4625 | [0.3870, 0.5397] | 160 | 0.4062 | [0.3332, 0.4837] | 160 |
| C1 vs C4 | 0.3125 | [0.2458, 0.3880] | 160 | 0.3396 | [0.2706, 0.4162] | 159 |
| C3 vs C4 | 0.4062 | [0.3332, 0.4837] | 160 | 0.3500 | [0.2804, 0.4266] | 160 |
| C3 vs C5_CONTRACT | 0.4276 | [0.3713, 0.4858] | 283 | — | — | — |
| C4 vs C4_shuffled | 0.5437 | [0.4665, 0.6190] | 160 | 0.4938 | [0.4173, 0.5705] | 160 |
| C4 vs C5_CONTRACT | 0.4000 | [0.3448, 0.4578] | 285 | — | — | — |

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

### C3 vs C5_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 29 | 0.3448 | [0.1994, 0.5265] |
| lo_moderately_shorter | 98 | 0.2449 | [0.1704, 0.3386] |
| similar | 78 | 0.4487 | [0.3433, 0.5589] |
| lo_moderately_longer | 67 | 0.6119 | [0.4922, 0.7195] |
| lo_much_longer | 11 | 1.0000 | [0.7412, 1.0000] |

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

### C5 vs C5_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 24 | 0.2500 | [0.1200, 0.4490] |
| lo_moderately_shorter | 90 | 0.1444 | [0.0864, 0.2316] |
| similar | 73 | 0.1918 | [0.1178, 0.2966] |
| lo_moderately_longer | 78 | 0.3333 | [0.2387, 0.4436] |
| lo_much_longer | 22 | 0.4545 | [0.2692, 0.6534] |

## AB/BA counterbalanced rejudge (Phase 1)

Coverage: **1784 swapped-order rejudge records** vs 3243 total originals. Each AB/BA-matched pair has both an original and a swap judgment from the same judge.

For each headline pair, `position_consistent` = judgments agree on which condition wins regardless of slot (real condition preference); `position_flip` = original and swap disagree (same slot wins both times = slot effect). `position_controlled_lo_win` averages across orders and is the position-bias-corrected headline. `headline_survives_swap` flags whether the controlled CI excludes 0.5 on the same side as the original.

| pair | n_AB/BA | orig lo_win | swap lo_win | controlled lo_win | Wilson CI95 | Bootstrap CI95 | flip rate | survives? |
|---|---:|---:|---:|---:|---|---|---:|---|
| C1_padded vs C4 | 320 | 0.319 | 0.434 | 0.377 | [0.324, 0.429] | [0.317, 0.439] | 0.203 | ✓ |
| C3 vs C5_CONTRACT | 288 | 0.428 | 0.573 | 0.501 | [0.443, 0.557] | [0.436, 0.566] | 0.330 | **⚠ NO** |
| C4 vs C4_shuffled | 320 | 0.519 | 0.637 | 0.578 | [0.523, 0.631] | [0.522, 0.637] | 0.269 | ✓ |
| C4 vs C5 | 280 | 0.626 | 0.736 | 0.680 | [0.622, 0.731] | [0.615, 0.744] | 0.207 | ✓ |
| C4 vs C5_CONTRACT | 288 | 0.400 | 0.562 | 0.482 | [0.425, 0.540] | [0.413, 0.548] | 0.306 | **⚠ NO** |
| C5 vs C5_CONTRACT | 288 | 0.240 | 0.403 | 0.323 | [0.272, 0.379] | [0.267, 0.383] | 0.243 | ✓ |

**Bootstrap CI** is cluster-resampled by (persona × scenario × author) — the matched-pair appropriate estimator. Replaces the Wilson interval as the canonical CI for the controlled rate (Wilson kept side-by-side for continuity). 2026-05-17 review fix.

### AB/BA per-judge breakdown — slot-B advantage

Decomposes the position-bias finding by judge. `slot_B_adv` is (swap_lo_win − orig_lo_win); positive = slot B favored (i.e., the lower-numbered condition wins more when placed in slot B). Methodology contribution rests on per-judge structure being non-uniform; values below confirm: GPT-5.5 and Opus show strong slot-B preference; GPT-5.4 has negligible-to-negative effect.

| pair | judge | n | orig lo | swap lo | controlled lo | Bootstrap CI | slot_B_adv |
|---|---|---:|---:|---:|---:|---|---:|
| C1_padded vs C4 | gpt-5.4 | 160 | 0.356 | 0.388 | 0.372 | [0.306, 0.441] | +0.031 |
| C1_padded vs C4 | gpt-5.5 | 160 | 0.281 | 0.481 | 0.381 | [0.319, 0.447] | +0.200 |
| C3 vs C5_CONTRACT | gpt-5.4 | 84 | 0.571 | 0.536 | 0.554 | [0.458, 0.643] | -0.036 |
| C3 vs C5_CONTRACT | gpt-5.5 | 84 | 0.417 | 0.667 | 0.542 | [0.452, 0.631] | +0.250 |
| C3 vs C5_CONTRACT | opus | 120 | 0.330 | 0.534 | 0.435 | [0.367, 0.502] | +0.203 |
| C4 vs C4_shuffled | gpt-5.4 | 160 | 0.600 | 0.575 | 0.588 | [0.519, 0.653] | -0.025 |
| C4 vs C4_shuffled | gpt-5.5 | 160 | 0.438 | 0.700 | 0.569 | [0.506, 0.628] | +0.263 |
| C4 vs C5 | gpt-5.4 | 80 | 0.662 | 0.700 | 0.681 | [0.581, 0.769] | +0.037 |
| C4 vs C5 | gpt-5.5 | 80 | 0.613 | 0.750 | 0.681 | [0.588, 0.775] | +0.138 |
| C4 vs C5 | opus | 120 | 0.610 | 0.750 | 0.679 | [0.613, 0.746] | +0.140 |
| C4 vs C5_CONTRACT | gpt-5.4 | 84 | 0.464 | 0.488 | 0.476 | [0.381, 0.571] | +0.024 |
| C4 vs C5_CONTRACT | gpt-5.5 | 84 | 0.345 | 0.595 | 0.470 | [0.375, 0.554] | +0.250 |
| C4 vs C5_CONTRACT | opus | 120 | 0.393 | 0.592 | 0.494 | [0.427, 0.562] | +0.199 |
| C5 vs C5_CONTRACT | gpt-5.4 | 84 | 0.286 | 0.398 | 0.342 | [0.253, 0.431] | +0.112 |
| C5 vs C5_CONTRACT | gpt-5.5 | 84 | 0.107 | 0.417 | 0.262 | [0.191, 0.339] | +0.309 |
| C5 vs C5_CONTRACT | opus | 120 | 0.302 | 0.397 | 0.352 | [0.283, 0.423] | +0.094 |

### AB/BA per-cell decomposition by judge

For each (pair, judge), each AB/BA-matched pair falls into one of four buckets: `condition_lo_stable` (lo wins both orders), `condition_hi_stable` (hi wins both), `slot_A_stable` (slot A wins both — slot effect favoring A), `slot_B_stable` (slot B wins both — slot effect favoring B). Plus `either_tie` for tied judgments.

| pair | judge | cond_lo_stable | cond_hi_stable | slot_A_stable | slot_B_stable | either_tie |
|---|---|---:|---:|---:|---:|---:|
| C1_padded vs C4 | gpt-5.4 | 45 | 86 | 12 | 17 | 0 |
| C1_padded vs C4 | gpt-5.5 | 43 | 81 | 2 | 34 | 0 |
| C3 vs C5_CONTRACT | gpt-5.4 | 33 | 24 | 15 | 12 | 0 |
| C3 vs C5_CONTRACT | gpt-5.5 | 34 | 27 | 1 | 22 | 0 |
| C3 vs C5_CONTRACT | opus | 26 | 42 | 12 | 33 | 7 |
| C4 vs C4_shuffled | gpt-5.4 | 76 | 48 | 20 | 16 | 0 |
| C4 vs C4_shuffled | gpt-5.5 | 66 | 44 | 3 | 47 | 0 |
| C4 vs C5 | gpt-5.4 | 50 | 21 | 3 | 6 | 0 |
| C4 vs C5 | gpt-5.5 | 48 | 19 | 1 | 12 | 0 |
| C4 vs C5 | opus | 62 | 20 | 10 | 26 | 2 |
| C4 vs C5_CONTRACT | gpt-5.4 | 32 | 36 | 7 | 9 | 0 |
| C4 vs C5_CONTRACT | gpt-5.5 | 28 | 33 | 1 | 22 | 0 |
| C4 vs C5_CONTRACT | opus | 33 | 35 | 13 | 36 | 3 |
| C5 vs C5_CONTRACT | gpt-5.4 | 20 | 47 | 3 | 13 | 1 |
| C5 vs C5_CONTRACT | gpt-5.5 | 9 | 49 | 0 | 26 | 0 |
| C5 vs C5_CONTRACT | opus | 26 | 62 | 8 | 20 | 4 |

### AB/BA by judge-author provider scope

Demotes the Phase 0 cross-provider C3 vs C5_CONTRACT finding by applying AB/BA correction within provider-scope strata. Original Phase 0 stratified cluster-bootstrap (without AB/BA) found cross-provider CI [0.238, 0.446] favoring C5_CONTRACT; under AB/BA, even the cross-provider subset shows no preference.

| pair | scope | n | orig lo | swap lo | controlled lo | Bootstrap CI |
|---|---|---:|---:|---:|---:|---|
| C1_padded vs C4 | same_provider | 320 | 0.319 | 0.434 | 0.377 | [0.312, 0.438] |
| C3 vs C5_CONTRACT | cross_provider | 88 | 0.341 | 0.568 | 0.457 | [0.376, 0.541] |
| C3 vs C5_CONTRACT | same_provider | 200 | 0.465 | 0.576 | 0.520 | [0.446, 0.590] |
| C4 vs C4_shuffled | same_provider | 320 | 0.519 | 0.637 | 0.578 | [0.517, 0.637] |
| C4 vs C5 | cross_provider | 80 | 0.675 | 0.800 | 0.738 | [0.650, 0.819] |
| C4 vs C5 | same_provider | 200 | 0.606 | 0.710 | 0.657 | [0.582, 0.730] |
| C4 vs C5_CONTRACT | cross_provider | 88 | 0.395 | 0.614 | 0.506 | [0.418, 0.591] |
| C4 vs C5_CONTRACT | same_provider | 200 | 0.402 | 0.540 | 0.471 | [0.398, 0.544] |
| C5 vs C5_CONTRACT | cross_provider | 88 | 0.307 | 0.377 | 0.344 | [0.261, 0.436] |
| C5 vs C5_CONTRACT | same_provider | 200 | 0.211 | 0.414 | 0.314 | [0.251, 0.378] |

### AB/BA joint position × length correction

Restricts AB/BA records to the length-similar bucket only. Settles the Phase 0 (length-matched) vs Phase 1 (AB/BA) contradiction by addressing both confounds simultaneously. For pairs where the joint CI straddles 0.5, the Tier 1 verdict is contingent on the choice of confound to control.

| pair | n_similar | controlled lo (length-matched) | Bootstrap CI |
|---|---:|---:|---|
| C1_padded vs C4 | 86 | 0.267 | [0.174, 0.366] |
| C3 vs C5_CONTRACT | 80 | 0.500 | [0.371, 0.634] ⚠ joint CI straddles 0.5 |
| C4 vs C4_shuffled | 86 | 0.616 | [0.512, 0.721] |
| C4 vs C5 | 76 | 0.674 | [0.547, 0.795] |
| C4 vs C5_CONTRACT | 65 | 0.450 | [0.298, 0.601] ⚠ joint CI straddles 0.5 |
| C5 vs C5_CONTRACT | 74 | 0.351 | [0.238, 0.471] |

**Reading**: If `orig` and `swap` lo_win rates are both away from 0.5 in the same direction → condition preference is real (Tier 1 confirmed). If they're on opposite sides of 0.5 → slot bias dominates and the headline collapses under counterbalancing. The `position_flip_rate` is the raw rate of within-pair disagreement; values near 0 mean judges are consistent regardless of order.

## Condition discoverability (TF-IDF + logistic)

Trained a TF-IDF + logistic classifier to predict condition from output text alone. **Test accuracy: 0.272** vs chance baseline 0.125 (+0.147 pp above chance). If high, pairwise judges may be partly recognizing condition cues.

**Per-class F1 (test split):**

| condition | F1 |
|---|---:|
| C0 | 0.528 |
| C1 | 0.173 |
| C1_padded | 0.237 |
| C3 | 0.265 |
| C4 | 0.163 |
| C4_shuffled | 0.344 |
| C5 | 0.000 |
| C5_CONTRACT | 0.000 |

**Key reading**: F1 ≈ 0 for C5 and C5_CONTRACT under this simple TF-IDF lexical classifier indicates this classifier could not distinguish C5 from C5_CONTRACT outputs from text alone. This does NOT rule out semantic, stylistic, length-based, or judge-internal recognizability — a stronger classifier or judge-blind recognizability prompt would be required to make a stronger claim. Wording fix per 2026-05-17 round-2 review (Codex Council skeptic + GPT Pro A13).

## Rubric lexical-overlap audit

Per-condition Jaccard overlap between profile-text vocabulary and the anchored-rubric anchor language (prompt 06b). Higher overlap = condition prompt 'speaks rubric language' more directly. Lexical-halo concern (codex-council, GPT-Pro §A16): rubric may be rewarding prompt-mirror phrasing rather than actual quality.

| condition | tokens | overlap | Jaccard | overlap/cond | top overlap |
|---|---:|---:|---:|---:|---|
| C1_padded | 511 | 37 | 0.054 | 0.072 | rather, help, actually, profile, useful, responses |
| C1_trait_labels | 368 | 26 | 0.047 | 0.071 | strong, rather, specific, register, interpersonal, generic |
| C2_narrative | 649 | 56 | 0.070 | 0.086 | specific, well, rather, generic, without, assistant |
| C3_behavioral_contract | 837 | 71 | 0.073 | 0.085 | name, decision, specific, emotional, concrete, register |
| C4_behavioral_contract_anti_sycophancy | 1044 | 81 | 0.069 | 0.078 | name, preserving, agency, challenge, specific, rather |
| C4_shuffled | 1044 | 81 | 0.069 | 0.078 | name, preserving, agency, challenge, specific, rather |
| C5_contract | 1155 | 81 | 0.063 | 0.070 | name, decision, anchor, profile, emotional, register |
| C5_source_packet_informed | 843 | 58 | 0.058 | 0.069 | rather, specific, profile, source, emotional, register |

## Macro vs micro aggregation

For each headline pair, the `micro` column is the current record-pooled lo_win (status quo). The macro-X columns each first compute lo_win within strata of dimension X, then average. Pairs whose macros disagree with micro by ≥5 pp on any dimension are flagged — that means the headline is partly an artifact of record-count imbalance, not the phenomenon.

| pair | micro | macro-judge | macro-author | macro-persona | macro-family | macro-cell | disagree ≥5pp |
|---|---:|---:|---:|---:|---:|---:|---|
| C0 vs C4 | 0.134 | 0.134 | 0.134 | 0.134 | 0.146 | 0.146 |  |
| C1_padded vs C4 | 0.319 | 0.319 | 0.319 | 0.319 | 0.340 | 0.340 |  |
| C1 vs C1_padded | 0.434 | 0.434 | 0.434 | 0.434 | 0.453 | 0.453 |  |
| C1 vs C4 | 0.326 | 0.326 | 0.326 | 0.326 | 0.354 | 0.353 |  |
| C3 vs C4 | 0.378 | 0.378 | 0.378 | 0.378 | 0.389 | 0.389 |  |
| C3 vs C5_CONTRACT | 0.428 | 0.440 | 0.407 | 0.428 | 0.412 | 0.409 |  |
| C4 vs C4_shuffled | 0.519 | 0.519 | 0.519 | 0.519 | 0.525 | 0.525 |  |
| C4 vs C5 | 0.626 | 0.628 | 0.591 | 0.627 | 0.607 | 0.605 |  |
| C4 vs C5_CONTRACT | 0.400 | 0.401 | 0.380 | 0.402 | 0.392 | 0.387 |  |
| C5 vs C5_CONTRACT | 0.240 | 0.232 | 0.265 | 0.240 | 0.253 | 0.258 |  |

## Cross-judge red-flag predictiveness

Tests whether leave-out-judge red flags predict the pairwise judge's call. For each decisive pairwise record, we count the red flags raised by judges OTHER than the pairwise judge on the winner vs the loser. If P(loser has more external flags | asymmetric) is significantly above 0.5, the red-flag signal is real (not a within-judge artifact). Replaces the v0.1 within-judge correlation flagged as tautological by GPT-Max empiricist.

| pair | n_dec | n_asym | asym rate | P(loser flagged \| asym) | Wilson CI95 | predictive? |
|---|---:|---:|---:|---:|---|---|
| C0 vs C4 | 320 | 142 | 0.444 | 0.880 | [0.817, 0.924] | **YES** |
| C1_padded vs C4 | 320 | 116 | 0.362 | 0.802 | [0.720, 0.864] | **YES** |
| C1 vs C1_padded | 320 | 128 | 0.400 | 0.656 | [0.571, 0.733] | **YES** |
| C1 vs C4 | 319 | 110 | 0.345 | 0.800 | [0.716, 0.864] | **YES** |
| C3 vs C4 | 320 | 97 | 0.303 | 0.814 | [0.726, 0.879] | **YES** |
| C3 vs C5_CONTRACT | 246 | 71 | 0.289 | 0.648 | [0.532, 0.749] | **YES** |
| C4 vs C4_shuffled | 320 | 101 | 0.316 | 0.762 | [0.671, 0.835] | **YES** |
| C4 vs C5 | 242 | 101 | 0.417 | 0.792 | [0.703, 0.860] | **YES** |
| C4 vs C5_CONTRACT | 248 | 87 | 0.351 | 0.782 | [0.684, 0.856] | **YES** |
| C5 vs C5_CONTRACT | 250 | 83 | 0.332 | 0.747 | [0.644, 0.828] | **YES** |

## Length-adjusted pairwise summary

For each pair, `full lo_win` is the unconditional lo win rate (matches the headline). `similar lo_win` is restricted to pairs where the two responses are length-similar (within the `similar` bucket of `_length_bucket`). Pairs whose headline margin vanishes (similar CI includes 0.5 AND |full − 0.5| ≥ 0.05) are flagged ⚠. Analysis-only complement to a future generation-side length-matched rerun.

| pair | full lo_win | n_full | similar lo_win | n_similar | similar CI95 | Δ similar−full | flag |
|---|---:|---:|---:|---:|---|---:|---|
| C0 vs C4 | 0.134 | 320 | 0.172 | 64 | [0.099, 0.282] | +0.037 |  |
| C1_padded vs C4 | 0.319 | 320 | 0.186 | 86 | [0.118, 0.281] | -0.133 |  |
| C1 vs C1_padded | 0.434 | 320 | 0.280 | 100 | [0.201, 0.375] | -0.154 |  |
| C1 vs C4 | 0.326 | 319 | 0.203 | 74 | [0.127, 0.308] | -0.123 |  |
| C3 vs C4 | 0.378 | 320 | 0.342 | 82 | [0.248, 0.449] | -0.037 |  |
| C3 vs C5_CONTRACT | 0.428 | 283 | 0.449 | 78 | [0.343, 0.559] | +0.021 | **⚠ vanishes** |
| C4 vs C4_shuffled | 0.519 | 320 | 0.546 | 86 | [0.442, 0.647] | +0.028 |  |
| C4 vs C5 | 0.626 | 278 | 0.587 | 75 | [0.474, 0.691] | -0.039 | **⚠ vanishes** |
| C4 vs C5_CONTRACT | 0.400 | 285 | 0.375 | 64 | [0.267, 0.497] | -0.025 |  |
| C5 vs C5_CONTRACT | 0.240 | 287 | 0.192 | 73 | [0.118, 0.297] | -0.049 |  |

## A/B side audit (position-bias diagnostic)

External reviewers (codex-council, GPT-Max, GPT-Pro all unanimous) flagged that C5_CONTRACT is overwhelmingly in slot B against C3/C4/C5, and counterbalanced (AB/BA) rejudging is the cheapest decisive next experiment. This block quantifies the imbalance so the AB/BA design can target the worst-affected pairs first.

### Per condition: slot occupancy

| condition | n_slot_A | n_slot_B | B share |
|---|---:|---:|---:|
| C0 | 320 | 0 | 0.000 |
| C1 | 638 | 2 | 0.003 |
| C1_padded | 322 | 318 | 0.497 |
| C3 | 608 | 0 | 0.000 |
| C4 | 884 | 1284 | 0.592 |
| C4_shuffled | 4 | 316 | 0.988 |
| C5 | 288 | 280 | 0.493 |
| C5_CONTRACT | 0 | 864 | 1.000 |

### Per pair: slot balance + winner-by-side

| pair | n_total | n_dec | slot A wins | slot B wins | slot A win rate | slot A is `lo` | imbalanced? |
|---|---:|---:|---:|---:|---:|---:|---|
| C0 vs C4 | 320 | 320 | 43 | 277 | 0.134 | 1.000 | ⚠ slot A=`C0`, slot B=`C4` |
| C1_padded vs C4 | 320 | 320 | 102 | 218 | 0.319 | 1.000 | ⚠ slot A=`C1_padded`, slot B=`C4` |
| C1 vs C1_padded | 320 | 320 | 137 | 183 | 0.428 | 0.994 | ⚠ slot A=`C1`, slot B=`C1_padded` |
| C1 vs C4 | 320 | 319 | 104 | 215 | 0.326 | 1.000 | ⚠ slot A=`C1`, slot B=`C4` |
| C3 vs C4 | 320 | 320 | 121 | 199 | 0.378 | 1.000 | ⚠ slot A=`C3`, slot B=`C4` |
| C3 vs C5_CONTRACT | 288 | 283 | 121 | 162 | 0.428 | 1.000 | ⚠ slot A=`C3`, slot B=`C5_CONTRACT` |
| C4 vs C4_shuffled | 320 | 320 | 164 | 156 | 0.512 | 0.988 | ⚠ slot A=`C4`, slot B=`C4_shuffled` |
| C4 vs C5 | 280 | 278 | 174 | 104 | 0.626 | 1.000 | ⚠ slot A=`C4`, slot B=`C5` |
| C4 vs C5_CONTRACT | 288 | 285 | 114 | 171 | 0.400 | 1.000 | ⚠ slot A=`C4`, slot B=`C5_CONTRACT` |
| C5 vs C5_CONTRACT | 288 | 287 | 69 | 218 | 0.240 | 1.000 | ⚠ slot A=`C5`, slot B=`C5_CONTRACT` |

**Reading**: If `slot A is lo` share is near 0.5, slot assignment is balanced. If it's near 0 or 1 (⚠), one condition dominates one slot — those rows are confounded with side and require AB/BA rejudging before any margin is trustworthy. The `slot A win rate` column is the side-only position-bias signal: under no position bias and balanced assignment, it should hover near 0.5.

## Leave-one-out fragility (cluster-bootstrap CIs)

For each headline pair, drop one (judge / author / persona / scenario family) at a time and recompute cluster-bootstrap CI. Reports `Δ_from_full` (loo lo_win minus full-sample lo_win) and flags: `flips` (sign change across 0.5), `attenuates_5pp` (|Δ| ≥ 0.05), `ci_widens_2x` (loo CI width ≥ 2× full width). **Robust** = no flags.

### Leave-one-judge-out

| pair | full lo_win | leave-out | loo lo_win | Δ_from_full | flags |
|---|---:|---|---:|---:|---|
| C3 vs C4 | 0.378 | −gpt-5.4 | 0.319 | -0.059 | `attenuates_5pp` |
| C3 vs C4 | 0.378 | −gpt-5.5 | 0.438 | +0.059 | `attenuates_5pp` |
| C3 vs C5_CONTRACT | 0.428 | −gpt-5.4 | 0.367 | -0.061 | `attenuates_5pp` |
| C3 vs C5_CONTRACT | 0.428 | −opus | 0.494 | +0.066 | `attenuates_5pp` |
| C4 vs C4_shuffled | 0.519 | −gpt-5.4 | 0.438 | -0.081 | `flips`, `attenuates_5pp` |
| C4 vs C4_shuffled | 0.519 | −gpt-5.5 | 0.600 | +0.081 | `attenuates_5pp` |
| C5 vs C5_CONTRACT | 0.240 | −gpt-5.5 | 0.296 | +0.055 | `attenuates_5pp` |

### Leave-one-author-out

| pair | full lo_win | leave-out | loo lo_win | Δ_from_full | flags |
|---|---:|---|---:|---:|---|
| C4 vs C4_shuffled | 0.519 | −gpt-5.4 | 0.581 | +0.062 | `attenuates_5pp` |
| C4 vs C4_shuffled | 0.519 | −gpt-5.5 | 0.456 | -0.063 | `flips`, `attenuates_5pp` |
| C4 vs C5 | 0.626 | −gpt-5.4 | 0.576 | -0.050 | `attenuates_5pp` |
| C5 vs C5_CONTRACT | 0.240 | −gpt-5.4 | 0.293 | +0.053 | `attenuates_5pp` |

### Leave-one-persona-out

| pair | full lo_win | leave-out | loo lo_win | Δ_from_full | flags |
|---|---:|---|---:|---:|---|
| C1_padded vs C4 | 0.319 | −user_pfi_pawl_gram_001 | 0.268 | -0.051 | `attenuates_5pp` |
| C4 vs C4_shuffled | 0.519 | −user_pfi_slalom_altar_001 | 0.489 | -0.029 | `flips` |
| C4 vs C5 | 0.626 | −user_pfi_dario_armadillo_001 | 0.572 | -0.054 | `attenuates_5pp` |
| C4 vs C5 | 0.626 | −user_pfi_emily_blender_001 | 0.692 | +0.066 | `attenuates_5pp` |
| C4 vs C5 | 0.626 | −user_pfi_pawl_gram_001 | 0.683 | +0.057 | `attenuates_5pp` |
| C4 vs C5 | 0.626 | −user_pfi_slalom_altar_001 | 0.557 | -0.069 | `attenuates_5pp` |
| C4 vs C5_CONTRACT | 0.400 | −user_pfi_emily_blender_001 | 0.469 | +0.070 | `attenuates_5pp` |
| C4 vs C5_CONTRACT | 0.400 | −user_pfi_slalom_altar_001 | 0.316 | -0.084 | `attenuates_5pp` |

### Leave-one-scenario family-out

| pair | full lo_win | leave-out | loo lo_win | Δ_from_full | flags |
|---|---:|---|---:|---:|---|
| C4 vs C4_shuffled | 0.519 | −epistemic_uncertainty | 0.490 | -0.029 | `flips` |

## Pairwise by judge (same-author, decisive)

Per-pair stratification by `judge`. A row's `lo win` is the win rate of the lower-numbered condition within that stratum (ties excluded from denominator). Bootstrap CI only computed when n_dec ≥ 20 and n_clusters ≥ 5.

### C0 vs C4

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.181 | [0.129, 0.248] | [0.125, 0.244] |
| gpt-5.5 | 160 | 0.087 | [0.053, 0.141] | [0.044, 0.131] |

### C1_padded vs C4

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.356 | [0.286, 0.433] | [0.287, 0.431] |
| gpt-5.5 | 160 | 0.281 | [0.217, 0.355] | [0.212, 0.350] |

### C1 vs C1_padded

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.469 | [0.393, 0.546] | [0.388, 0.550] |
| gpt-5.5 | 160 | 0.400 | [0.327, 0.477] | [0.325, 0.481] |

### C1 vs C4

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.338 | [0.269, 0.414] | [0.263, 0.412] |
| gpt-5.5 | 159 | 0.315 | [0.247, 0.390] | [0.245, 0.386] |

### C3 vs C4

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.438 | [0.363, 0.515] | [0.356, 0.506] |
| gpt-5.5 | 160 | 0.319 | [0.252, 0.395] | [0.256, 0.394] |

### C3 vs C5_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 84 | 0.571 | [0.465, 0.672] | [0.464, 0.667] |
| gpt-5.5 | 84 | 0.417 | [0.317, 0.523] | [0.309, 0.524] |
| opus | 115 | 0.330 | [0.251, 0.421] | [0.248, 0.414] |

### C4 vs C4_shuffled

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.600 | [0.523, 0.673] | [0.525, 0.675] |
| gpt-5.5 | 160 | 0.438 | [0.363, 0.515] | [0.362, 0.519] |

### C4 vs C5

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 80 | 0.662 | [0.554, 0.756] | [0.562, 0.775] |
| gpt-5.5 | 80 | 0.613 | [0.503, 0.712] | [0.512, 0.713] |
| opus | 118 | 0.610 | [0.520, 0.693] | [0.517, 0.701] |

### C4 vs C5_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 84 | 0.464 | [0.361, 0.570] | [0.357, 0.571] |
| gpt-5.5 | 84 | 0.345 | [0.252, 0.452] | [0.250, 0.441] |
| opus | 117 | 0.393 | [0.309, 0.484] | [0.308, 0.487] |

### C5 vs C5_CONTRACT

| judge | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 84 | 0.286 | [0.200, 0.390] | [0.191, 0.381] |
| gpt-5.5 | 84 | 0.107 | [0.057, 0.191] | [0.048, 0.179] |
| opus | 119 | 0.302 | [0.227, 0.390] | [0.225, 0.390] |

## Pairwise by author (same-author, decisive)

Per-pair stratification by `author`. A row's `lo win` is the win rate of the lower-numbered condition within that stratum (ties excluded from denominator). Bootstrap CI only computed when n_dec ≥ 20 and n_clusters ≥ 5.

### C0 vs C4

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.131 | [0.087, 0.192] | [0.069, 0.212] |
| gpt-5.5 | 160 | 0.138 | [0.093, 0.199] | [0.081, 0.200] |

### C1_padded vs C4

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.344 | [0.275, 0.420] | [0.250, 0.438] |
| gpt-5.5 | 160 | 0.294 | [0.229, 0.368] | [0.206, 0.375] |

### C1 vs C1_padded

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.419 | [0.345, 0.496] | [0.331, 0.512] |
| gpt-5.5 | 160 | 0.450 | [0.375, 0.527] | [0.356, 0.544] |

### C1 vs C4

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.344 | [0.275, 0.420] | [0.250, 0.438] |
| gpt-5.5 | 159 | 0.308 | [0.242, 0.384] | [0.225, 0.394] |

### C3 vs C4

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.362 | [0.292, 0.439] | [0.269, 0.456] |
| gpt-5.5 | 160 | 0.394 | [0.321, 0.471] | [0.300, 0.487] |

### C3 vs C5_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 119 | 0.403 | [0.320, 0.493] | [0.299, 0.517] |
| gpt-5.5 | 118 | 0.491 | [0.403, 0.581] | [0.387, 0.602] |
| opus | 46 | 0.326 | [0.209, 0.470] | [0.179, 0.480] |

### C4 vs C4_shuffled

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 160 | 0.456 | [0.381, 0.533] | [0.356, 0.544] |
| gpt-5.5 | 160 | 0.581 | [0.504, 0.655] | [0.487, 0.662] |

### C4 vs C5

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.692 | [0.604, 0.767] | [0.575, 0.800] |
| gpt-5.5 | 120 | 0.608 | [0.519, 0.691] | [0.500, 0.725] |
| opus | 38 | 0.474 | [0.325, 0.627] | [0.308, 0.632] |

### C4 vs C5_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.408 | [0.325, 0.498] | [0.292, 0.533] |
| gpt-5.5 | 118 | 0.432 | [0.346, 0.522] | [0.308, 0.558] |
| opus | 47 | 0.298 | [0.186, 0.440] | [0.178, 0.429] |

### C5 vs C5_CONTRACT

| author | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| gpt-5.4 | 120 | 0.167 | [0.111, 0.243] | [0.092, 0.258] |
| gpt-5.5 | 120 | 0.267 | [0.196, 0.352] | [0.183, 0.358] |
| opus | 47 | 0.362 | [0.240, 0.505] | [0.209, 0.531] |

## Pairwise by persona (same-author, decisive)

Per-pair stratification by `persona`. A row's `lo win` is the win rate of the lower-numbered condition within that stratum (ties excluded from denominator). Bootstrap CI only computed when n_dec ≥ 20 and n_clusters ≥ 5.

### C0 vs C4

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.000 | [0.000, 0.088] | [0.000, 0.000] |
| user_pfi_emily_blender_001 | 40 | 0.275 | [0.161, 0.428] | [0.125, 0.475] |
| user_pfi_pawl_gram_001 | 40 | 0.125 | [0.055, 0.261] | [0.025, 0.250] |
| user_pfi_slalom_altar_001 | 40 | 0.025 | [0.004, 0.129] | [0.000, 0.075] |
| user_syn_calibration_goblin_001 | 40 | 0.250 | [0.142, 0.402] | [0.075, 0.450] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.150 | [0.071, 0.291] | [0.025, 0.300] |
| user_syn_high_agency_spiraler_001 | 40 | 0.100 | [0.040, 0.231] | [0.000, 0.225] |
| user_syn_patient_craftsperson_001 | 40 | 0.150 | [0.071, 0.291] | [0.050, 0.275] |

### C1_padded vs C4

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.075 | [0.026, 0.199] | [0.000, 0.175] |
| user_pfi_emily_blender_001 | 40 | 0.550 | [0.398, 0.693] | [0.350, 0.725] |
| user_pfi_pawl_gram_001 | 40 | 0.675 | [0.520, 0.799] | [0.475, 0.850] |
| user_pfi_slalom_altar_001 | 40 | 0.050 | [0.014, 0.165] | [0.000, 0.125] |
| user_syn_calibration_goblin_001 | 40 | 0.425 | [0.285, 0.578] | [0.250, 0.625] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.125 | [0.055, 0.261] | [0.025, 0.250] |
| user_syn_high_agency_spiraler_001 | 40 | 0.225 | [0.123, 0.375] | [0.100, 0.375] |
| user_syn_patient_craftsperson_001 | 40 | 0.425 | [0.285, 0.578] | [0.250, 0.600] |

### C1 vs C1_padded

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.500 | [0.352, 0.648] | [0.325, 0.650] |
| user_pfi_emily_blender_001 | 40 | 0.550 | [0.398, 0.693] | [0.350, 0.725] |
| user_pfi_pawl_gram_001 | 40 | 0.375 | [0.242, 0.530] | [0.200, 0.575] |
| user_pfi_slalom_altar_001 | 40 | 0.425 | [0.285, 0.578] | [0.250, 0.600] |
| user_syn_calibration_goblin_001 | 40 | 0.425 | [0.285, 0.578] | [0.250, 0.625] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.425 | [0.285, 0.578] | [0.250, 0.600] |
| user_syn_high_agency_spiraler_001 | 40 | 0.475 | [0.329, 0.625] | [0.300, 0.650] |
| user_syn_patient_craftsperson_001 | 40 | 0.300 | [0.181, 0.454] | [0.150, 0.475] |

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
| user_syn_patient_craftsperson_001 | 39 | 0.385 | [0.249, 0.541] | [0.200, 0.579] |

### C3 vs C4

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.175 | [0.087, 0.320] | [0.075, 0.300] |
| user_pfi_emily_blender_001 | 40 | 0.475 | [0.329, 0.625] | [0.275, 0.675] |
| user_pfi_pawl_gram_001 | 40 | 0.575 | [0.422, 0.715] | [0.375, 0.775] |
| user_pfi_slalom_altar_001 | 40 | 0.400 | [0.264, 0.554] | [0.250, 0.575] |
| user_syn_calibration_goblin_001 | 40 | 0.400 | [0.264, 0.554] | [0.200, 0.600] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.200 | [0.105, 0.348] | [0.050, 0.375] |
| user_syn_high_agency_spiraler_001 | 40 | 0.475 | [0.329, 0.625] | [0.275, 0.675] |
| user_syn_patient_craftsperson_001 | 40 | 0.325 | [0.201, 0.480] | [0.175, 0.500] |

### C3 vs C5_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 71 | 0.437 | [0.328, 0.552] | [0.281, 0.603] |
| user_pfi_emily_blender_001 | 70 | 0.357 | [0.255, 0.474] | [0.206, 0.515] |
| user_pfi_pawl_gram_001 | 72 | 0.375 | [0.272, 0.490] | [0.244, 0.529] |
| user_pfi_slalom_altar_001 | 70 | 0.543 | [0.427, 0.654] | [0.418, 0.657] |

### C4 vs C4_shuffled

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 40 | 0.650 | [0.495, 0.779] | [0.475, 0.825] |
| user_pfi_emily_blender_001 | 40 | 0.425 | [0.285, 0.578] | [0.225, 0.625] |
| user_pfi_pawl_gram_001 | 40 | 0.375 | [0.242, 0.530] | [0.225, 0.525] |
| user_pfi_slalom_altar_001 | 40 | 0.725 | [0.572, 0.839] | [0.550, 0.875] |
| user_syn_calibration_goblin_001 | 40 | 0.575 | [0.422, 0.715] | [0.375, 0.750] |
| user_syn_conflict_allergic_moralist_001 | 40 | 0.650 | [0.495, 0.779] | [0.475, 0.800] |
| user_syn_high_agency_spiraler_001 | 40 | 0.275 | [0.161, 0.428] | [0.150, 0.425] |
| user_syn_patient_craftsperson_001 | 40 | 0.475 | [0.329, 0.625] | [0.275, 0.650] |

### C4 vs C5

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 70 | 0.786 | [0.676, 0.866] | [0.657, 0.897] |
| user_pfi_emily_blender_001 | 70 | 0.429 | [0.319, 0.545] | [0.275, 0.568] |
| user_pfi_pawl_gram_001 | 70 | 0.457 | [0.346, 0.573] | [0.314, 0.603] |
| user_pfi_slalom_altar_001 | 68 | 0.838 | [0.733, 0.907] | [0.746, 0.919] |

### C4 vs C5_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 71 | 0.479 | [0.367, 0.593] | [0.353, 0.625] |
| user_pfi_emily_blender_001 | 72 | 0.194 | [0.119, 0.300] | [0.086, 0.309] |
| user_pfi_pawl_gram_001 | 72 | 0.278 | [0.188, 0.391] | [0.171, 0.406] |
| user_pfi_slalom_altar_001 | 70 | 0.657 | [0.540, 0.757] | [0.522, 0.771] |

### C5 vs C5_CONTRACT

| persona | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---|---|
| user_pfi_dario_armadillo_001 | 72 | 0.181 | [0.109, 0.285] | [0.059, 0.306] |
| user_pfi_emily_blender_001 | 72 | 0.319 | [0.223, 0.434] | [0.203, 0.446] |
| user_pfi_pawl_gram_001 | 72 | 0.319 | [0.223, 0.434] | [0.203, 0.457] |
| user_pfi_slalom_altar_001 | 71 | 0.141 | [0.078, 0.240] | [0.064, 0.239] |

## Scalar-pairwise reconciliation (same-author, paired cells)

For each pair, we match every pairwise record with the same judge's anchored scalar scores on both outputs. `Δ_total` is the sum across 10 dimensions (each 0–10), so a Δ of +5 means hi-condition averages 0.5 points higher per dimension. Pairs where pairwise direction does not match scalar Δ direction reveal a contradiction between holistic and rubric judging.

| pair | n_dec | hi pairwise win | Δ_total (hi−lo) | sign agree | flag |
|---|---:|---:|---:|---:|---|
| C0 vs C4 | 320 | 0.866 | +6.075 | 0.863 |  |
| C1_padded vs C4 | 320 | 0.681 | +3.084 | 0.764 |  |
| C1 vs C1_padded | 320 | 0.566 | -0.441 | 0.679 | **⚠ pairwise favors hi but scalar does not** |
| C1 vs C4 | 319 | 0.674 | +2.644 | 0.753 |  |
| C3 vs C4 | 320 | 0.622 | +1.159 | 0.678 |  |
| C3 vs C5_CONTRACT | 276 | 0.576 | -0.053 | 0.711 | **⚠ pairwise favors hi but scalar does not** |
| C4 vs C4_shuffled | 320 | 0.481 | -0.519 | 0.664 |  |
| C4 vs C5 | 278 | 0.374 | -3.261 | 0.784 |  |
| C4 vs C5_CONTRACT | 278 | 0.590 | -0.231 | 0.734 | **⚠ pairwise favors hi but scalar does not** |
| C5 vs C5_CONTRACT | 280 | 0.768 | +3.057 | 0.794 |  |

**Reading**: rows flagged ⚠ are the pairs where the pairwise channel tells a different story than the scalar rubric. For mechanism claims, both channels should align; flagged rows are descriptive-only until the gap is explained.

## Cross-author leak detection

**179 cross-author pairwise records detected out of 3243 total** (5.5%).

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

- **all-judge same-author**: n=3064 records
- **cross-provider same-author** (judge family ≠ author family): n=344 records
- **same-provider same-author** (judge family = author family): n=2720 records

| pair | n_all | lo win all | Bootstrap CI all-judge | n_xp | Bootstrap CI cross-prov | n_sp | Bootstrap CI same-prov |
|---|---:|---:|---|---:|---|---:|---|
| C0 vs C4 | 320 | 0.134 | [0.094, 0.181] | 0 | — | 320 | [0.094, 0.181] |
| C1_padded vs C4 | 320 | 0.319 | [0.256, 0.388] | 0 | — | 320 | [0.256, 0.388] |
| C1 vs C1_padded | 320 | 0.434 | [0.369, 0.500] | 0 | — | 320 | [0.369, 0.500] |
| C1 vs C4 | 319 | 0.326 | [0.262, 0.392] | 0 | — | 319 | [0.262, 0.392] |
| C3 vs C4 | 320 | 0.378 | [0.309, 0.447] | 0 | — | 320 | [0.309, 0.447] |
| C3 vs C5_CONTRACT | 283 | 0.428 | [0.353, 0.496] | 85 | [0.238, 0.446] | 198 | [0.381, 0.546] |
| C4 vs C4_shuffled | 320 | 0.519 | [0.456, 0.584] | 0 | — | 320 | [0.456, 0.584] |
| C4 vs C5 | 278 | 0.626 | [0.549, 0.701] | 80 | [0.575, 0.775] | 198 | [0.521, 0.688] |
| C4 vs C5_CONTRACT | 285 | 0.400 | [0.330, 0.476] | 86 | [0.291, 0.500] | 199 | [0.328, 0.485] |
| C5 vs C5_CONTRACT | 287 | 0.240 | [0.183, 0.305] | 88 | [0.213, 0.411] | 199 | [0.152, 0.274] |

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

## Scalar inter-judge agreement (legacy 0–5)

No dimensions flagged as weak-agreement (all judge pairs Pearson ≥ 0.30).

| judge pair | mean Pearson | mean Spearman | n_dimensions |
|---|---:|---:|---:|

## Scalar inter-judge agreement (anchored 0–10)

No dimensions flagged as weak-agreement (all judge pairs Pearson ≥ 0.30).

| judge pair | mean Pearson | mean Spearman | n_dimensions |
|---|---:|---:|---:|
| gpt-5.4 vs gpt-5.5 | 0.6969 | 0.6234 | 10 |
| gpt-5.4 vs opus | 0.6579 | 0.5956 | 10 |
| gpt-5.5 vs opus | 0.6317 | 0.5310 | 10 |

## Red-flag stratification
