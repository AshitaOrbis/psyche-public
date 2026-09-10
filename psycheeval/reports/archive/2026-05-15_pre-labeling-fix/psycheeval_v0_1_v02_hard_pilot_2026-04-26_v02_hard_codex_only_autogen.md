# PsycheEval v0.1 — v02_hard_pilot — run 2026-04-26_v02_hard_codex_only (auto-generated)

> Auto-generated numeric scaffold. The human-curated narrative report lives at `psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only.md`. This file contains only tables computed from `metrics_2026-04-26_v02_hard_codex_only.json`. Regenerating analyze.py will overwrite this file but never the curated one.

## Dataset composition

- **scenarios**: 80
- **users**: 8
- **assistant_outputs**: 1680
- **judge_scores**: 0
- **anchored_judge_scores**: 3949
- **pairwise_scores**: 3123

## Pairwise results (cross-provider judged)

### Counts

- **total_pairwise_records**: 3123
- **after_tagging**: 3123
- **cross_provider**: 361
- **cross_provider_same_author**: 264
- **cross_provider_same_author_PI**: 264

### Condition win-rate (same-author pairs, cross-provider judged)

Ties contribute 0.5 to each side. Same-author pairs isolate condition effects from author effects.

- **C3**: 0.347
- **C4**: 0.398
- **C5**: 0.307
- **C5_CONTRACT**: 0.650

### Condition-pair preferences (same-author, cross-provider)

| pair | n | first wins | second wins | ties |
|---|---|---|---|---|
| C3 vs C5_CONTRACT | 88 | 0.330 | 0.636 | 0.034 |
| C4 vs C5_CONTRACT | 88 | 0.386 | 0.591 | 0.023 |
| C5 vs C5_CONTRACT | 88 | 0.307 | 0.693 | 0.000 |

### Condition-pair preferences (PI-only, same-author, cross-provider)

C5 pairs appear here and here only — never in the all-persona block.

| pair | n | first wins | second wins | ties |
|---|---|---|---|---|
| C3 vs C5_CONTRACT | 88 | 0.330 | 0.636 | 0.034 |
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
| C4 vs C5 | 160 | 160 | 0 | 0.0000 | 0.6375 |
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

### C3 vs C5_CONTRACT

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 29 | 0.3448 | [0.1994, 0.5265] |
| lo_moderately_shorter | 98 | 0.2449 | [0.1704, 0.3386] |
| similar | 78 | 0.4487 | [0.3433, 0.5589] |
| lo_moderately_longer | 67 | 0.6119 | [0.4922, 0.7195] |
| lo_much_longer | 11 | 1.0000 | [0.7412, 1.0000] |

### C4 vs C5

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 12 | 0.2500 | [0.0889, 0.5323] |
| lo_moderately_shorter | 46 | 0.5000 | [0.3612, 0.6388] |
| similar | 46 | 0.5217 | [0.3814, 0.6588] |
| lo_moderately_longer | 40 | 0.9000 | [0.7695, 0.9604] |
| lo_much_longer | 16 | 1.0000 | [0.8064, 1.0000] |

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

## Cluster-bootstrap CIs (cluster unit: persona × scenario × author)

Wilson CIs reported alongside for continuity. Cluster-bootstrap is the conservative check.

| pair | n_dec | n_clusters | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---:|---|---|
| C0 vs C4 | 320 | 160 | 0.1344 | [0.1013, 0.1761] | [0.0938, 0.1812] |
| C1_padded vs C4 | 320 | 160 | 0.3187 | [0.2701, 0.3717] | [0.2562, 0.3875] |
| C1 vs C1_padded | 320 | 160 | 0.4344 | [0.3812, 0.4891] | [0.3688, 0.5000] |
| C1 vs C4 | 319 | 160 | 0.3260 | [0.2769, 0.3793] | [0.2618, 0.3918] |
| C3 vs C4 | 320 | 160 | 0.3781 | [0.3267, 0.4324] | [0.3094, 0.4469] |
| C3 vs C5_CONTRACT | 283 | 120 | 0.4276 | [0.3713, 0.4858] | [0.3542, 0.5000] |
| C4 vs C4_shuffled | 320 | 160 | 0.5188 | [0.4641, 0.5729] | [0.4562, 0.5844] |
| C4 vs C5 | 160 | 80 | 0.6375 | [0.5606, 0.7080] | [0.5437, 0.7312] |
| C4 vs C5_CONTRACT | 285 | 120 | 0.4000 | [0.3448, 0.4578] | [0.3287, 0.4722] |
| C5 vs C5_CONTRACT | 287 | 120 | 0.2404 | [0.1946, 0.2931] | [0.1828, 0.3031] |

## Scenario-family breakdowns (same-author pairwise)

### ambition_status

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C4 | 32 | 0.1562 | [0.0686, 0.3175] |
| C1_padded vs C4 | 32 | 0.3750 | [0.2293, 0.5475] |
| C1 vs C1_padded | 32 | 0.3438 | [0.2041, 0.5169] |
| C1 vs C4 | 32 | 0.2500 | [0.1325, 0.4211] |
| C3 vs C4 | 32 | 0.5000 | [0.3363, 0.6637] |
| C3 vs C5_CONTRACT | 28 | 0.4286 | [0.2651, 0.6093] |
| C4 vs C4_shuffled | 32 | 0.4688 | [0.3087, 0.6355] |
| C4 vs C5 | 16 | 0.1875 | [0.0659, 0.4301] |
| C4 vs C5_CONTRACT | 28 | 0.2857 | [0.1525, 0.4706] |
| C5 vs C5_CONTRACT | 28 | 0.3214 | [0.1793, 0.5066] |

### authority_disagreement

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C4 | 32 | 0.1875 | [0.0889, 0.3531] |
| C1_padded vs C4 | 32 | 0.4062 | [0.2552, 0.5774] |
| C1 vs C1_padded | 32 | 0.5000 | [0.3363, 0.6637] |
| C1 vs C4 | 32 | 0.4688 | [0.3087, 0.6355] |
| C3 vs C4 | 32 | 0.5000 | [0.3363, 0.6637] |
| C3 vs C5_CONTRACT | 28 | 0.2500 | [0.1268, 0.4336] |
| C4 vs C4_shuffled | 32 | 0.5000 | [0.3363, 0.6637] |
| C4 vs C5 | 16 | 0.6250 | [0.3864, 0.8152] |
| C4 vs C5_CONTRACT | 26 | 0.2692 | [0.1370, 0.4608] |
| C5 vs C5_CONTRACT | 27 | 0.1852 | [0.0818, 0.3670] |

### creative_feedback

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C4 | 32 | 0.2500 | [0.1325, 0.4211] |
| C1_padded vs C4 | 32 | 0.3438 | [0.2041, 0.5169] |
| C1 vs C1_padded | 32 | 0.6875 | [0.5143, 0.8205] |
| C1 vs C4 | 31 | 0.5161 | [0.3484, 0.6803] |
| C3 vs C4 | 32 | 0.4062 | [0.2552, 0.5774] |
| C3 vs C5_CONTRACT | 28 | 0.3214 | [0.1793, 0.5066] |
| C4 vs C4_shuffled | 32 | 0.5938 | [0.4226, 0.7448] |
| C4 vs C5 | 16 | 0.6250 | [0.3864, 0.8152] |
| C4 vs C5_CONTRACT | 28 | 0.3571 | [0.2071, 0.5417] |
| C5 vs C5_CONTRACT | 28 | 0.2500 | [0.1268, 0.4336] |

### epistemic_uncertainty

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C4 | 32 | 0.1875 | [0.0889, 0.3531] |
| C1_padded vs C4 | 32 | 0.3750 | [0.2293, 0.5475] |
| C1 vs C1_padded | 32 | 0.5000 | [0.3363, 0.6637] |
| C1 vs C4 | 32 | 0.5000 | [0.3363, 0.6637] |
| C3 vs C4 | 32 | 0.3125 | [0.1795, 0.4857] |
| C3 vs C5_CONTRACT | 28 | 0.6429 | [0.4583, 0.7929] |
| C4 vs C4_shuffled | 32 | 0.7812 | [0.6125, 0.8898] |
| C4 vs C5 | 16 | 0.9375 | [0.7167, 0.9889] |
| C4 vs C5_CONTRACT | 28 | 0.5357 | [0.3581, 0.7047] |
| C5 vs C5_CONTRACT | 28 | 0.3571 | [0.2071, 0.5417] |

### interpersonal_conflict

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C4 | 64 | 0.0938 | [0.0437, 0.1898] |
| C1_padded vs C4 | 64 | 0.1719 | [0.0988, 0.2821] |
| C1 vs C1_padded | 64 | 0.3438 | [0.2392, 0.4660] |
| C1 vs C4 | 64 | 0.1875 | [0.1106, 0.2997] |
| C3 vs C4 | 64 | 0.2812 | [0.1859, 0.4013] |
| C3 vs C5_CONTRACT | 63 | 0.4286 | [0.3140, 0.5514] |
| C4 vs C4_shuffled | 64 | 0.5156 | [0.3958, 0.6337] |
| C4 vs C5 | 32 | 0.8125 | [0.6469, 0.9111] |
| C4 vs C5_CONTRACT | 63 | 0.3810 | [0.2712, 0.5044] |
| C5 vs C5_CONTRACT | 64 | 0.2500 | [0.1601, 0.3682] |

### moral_uncertainty

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C4 | 32 | 0.1562 | [0.0686, 0.3175] |
| C1_padded vs C4 | 32 | 0.2812 | [0.1556, 0.4537] |
| C1 vs C1_padded | 32 | 0.5625 | [0.3933, 0.7183] |
| C1 vs C4 | 32 | 0.4375 | [0.2817, 0.6067] |
| C3 vs C4 | 32 | 0.4688 | [0.3087, 0.6355] |
| C3 vs C5_CONTRACT | 27 | 0.2222 | [0.1061, 0.4076] |
| C4 vs C4_shuffled | 32 | 0.4375 | [0.2817, 0.6067] |
| C4 vs C5 | 16 | 0.4375 | [0.2310, 0.6682] |
| C4 vs C5_CONTRACT | 28 | 0.3214 | [0.1793, 0.5066] |
| C5 vs C5_CONTRACT | 28 | 0.2500 | [0.1268, 0.4336] |

### procrastination_avoidance

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C4 | 32 | 0.0625 | [0.0173, 0.2015] |
| C1_padded vs C4 | 32 | 0.4688 | [0.3087, 0.6355] |
| C1 vs C1_padded | 32 | 0.3125 | [0.1795, 0.4857] |
| C1 vs C4 | 32 | 0.2188 | [0.1102, 0.3875] |
| C3 vs C4 | 32 | 0.2500 | [0.1325, 0.4211] |
| C3 vs C5_CONTRACT | 27 | 0.4444 | [0.2759, 0.6269] |
| C4 vs C4_shuffled | 32 | 0.4375 | [0.2817, 0.6067] |
| C4 vs C5 | 16 | 0.6250 | [0.3864, 0.8152] |
| C4 vs C5_CONTRACT | 28 | 0.5000 | [0.3263, 0.6737] |
| C5 vs C5_CONTRACT | 28 | 0.2857 | [0.1525, 0.4706] |

### shame_self_interpretation

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C4 | 64 | 0.0781 | [0.0338, 0.1702] |
| C1_padded vs C4 | 64 | 0.2969 | [0.1991, 0.4177] |
| C1 vs C1_padded | 64 | 0.3750 | [0.2667, 0.4975] |
| C1 vs C4 | 64 | 0.2500 | [0.1601, 0.3682] |
| C3 vs C4 | 64 | 0.3906 | [0.2806, 0.5131] |
| C3 vs C5_CONTRACT | 54 | 0.5556 | [0.4238, 0.6800] |
| C4 vs C4_shuffled | 64 | 0.4688 | [0.3518, 0.5893] |
| C4 vs C5 | 32 | 0.6562 | [0.4831, 0.7959] |
| C4 vs C5_CONTRACT | 56 | 0.4821 | [0.3567, 0.6099] |
| C5 vs C5_CONTRACT | 56 | 0.1250 | [0.0619, 0.2363] |

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
