# PsycheEval v0.1 — micro_pilot — run 2026-04-26_micro_tri_model (auto-generated)

> Auto-generated numeric scaffold. The human-curated narrative report lives at `psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model.md`. This file contains only tables computed from `metrics_2026-04-26_micro_tri_model.json`. Regenerating analyze.py will overwrite this file but never the curated one.

## Dataset composition

- **scenarios**: 48
- **users**: 8
- **assistant_outputs**: 648
- **judge_scores**: 1944
- **anchored_judge_scores**: 0
- **pairwise_scores**: 3456

## Primary: C0–C4 across all personas (cross-provider judged)

Every response scored by the opposite provider family's judge. C5 excluded — it exists only for public-inspired personas and is reported separately below.

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 4.062 | 3.854 | 4.188 | 4.339 | 4.010 | 3.760 | 3.812 | 4.464 | 4.406 | 4.193 | 0.297 | 192 |
| C1 | 4.240 | 4.167 | 4.417 | 4.573 | 4.198 | 3.797 | 3.943 | 4.495 | 4.599 | 4.339 | 0.234 | 192 |
| C3 | 4.422 | 4.323 | 4.484 | 4.641 | 4.370 | 3.964 | 4.104 | 4.635 | 4.724 | 4.516 | 0.208 | 192 |
| C4 | 4.396 | 4.349 | 4.490 | 4.677 | 4.333 | 4.099 | 4.167 | 4.615 | 4.719 | 4.458 | 0.167 | 192 |

## PI subset: C0–C4, public-inspired personas only (cross-provider)

Public-inspired personas under the shared condition set, for parity with the all-persona table above.

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 4.344 | 4.042 | 4.438 | 4.500 | 4.302 | 3.896 | 4.062 | 4.802 | 4.542 | 4.458 | 0.177 | 96 |
| C1 | 4.562 | 4.406 | 4.667 | 4.854 | 4.521 | 3.906 | 4.250 | 4.844 | 4.781 | 4.635 | 0.094 | 96 |
| C3 | 4.635 | 4.427 | 4.604 | 4.771 | 4.615 | 4.073 | 4.219 | 4.802 | 4.771 | 4.729 | 0.135 | 96 |
| C4 | 4.646 | 4.469 | 4.594 | 4.760 | 4.552 | 4.052 | 4.271 | 4.781 | 4.792 | 4.667 | 0.094 | 96 |

## PI subset with C5: C0–C5, public-inspired personas only (cross-provider)

This is the only valid comparison involving C5. Do NOT cross-compare C5 here against C0–C4 in the all-persona table — different persona subsets.

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 4.344 | 4.042 | 4.438 | 4.500 | 4.302 | 3.896 | 4.062 | 4.802 | 4.542 | 4.458 | 0.177 | 96 |
| C1 | 4.562 | 4.406 | 4.667 | 4.854 | 4.521 | 3.906 | 4.250 | 4.844 | 4.781 | 4.635 | 0.094 | 96 |
| C3 | 4.635 | 4.427 | 4.604 | 4.771 | 4.615 | 4.073 | 4.219 | 4.802 | 4.771 | 4.729 | 0.135 | 96 |
| C4 | 4.646 | 4.469 | 4.594 | 4.760 | 4.552 | 4.052 | 4.271 | 4.781 | 4.792 | 4.667 | 0.094 | 96 |
| C5 | 4.458 | 4.229 | 4.552 | 4.688 | 4.365 | 3.896 | 4.198 | 4.740 | 4.698 | 4.531 | 0.188 | 96 |

## PS subset: C0–C4, pure synthetic personas only (cross-provider)

Pure-synthetic personas under the shared condition set.

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 3.781 | 3.667 | 3.938 | 4.177 | 3.719 | 3.625 | 3.562 | 4.125 | 4.271 | 3.927 | 0.417 | 96 |
| C1 | 3.917 | 3.927 | 4.167 | 4.292 | 3.875 | 3.688 | 3.635 | 4.146 | 4.417 | 4.042 | 0.375 | 96 |
| C3 | 4.208 | 4.219 | 4.365 | 4.510 | 4.125 | 3.854 | 3.990 | 4.469 | 4.677 | 4.302 | 0.281 | 96 |
| C4 | 4.146 | 4.229 | 4.385 | 4.594 | 4.115 | 4.146 | 4.062 | 4.448 | 4.646 | 4.250 | 0.240 | 96 |

## Deltas: all personas, C0–C4 (cross-provider)

### C4_minus_C0

- `helpfulness`: +0.334
- `profile_fit`: +0.495
- `calibrated_challenge`: +0.302
- `anti_sycophancy`: +0.338
- `agency_support`: +0.323
- `epistemic_hygiene`: +0.339
- `emotional_accuracy`: +0.355
- `boundary_safety`: +0.151
- `non_caricature`: +0.313
- `transfer_value`: +0.265

### C4_minus_C1

- `helpfulness`: +0.156
- `profile_fit`: +0.182
- `calibrated_challenge`: +0.073
- `anti_sycophancy`: +0.104
- `agency_support`: +0.135
- `epistemic_hygiene`: +0.302
- `emotional_accuracy`: +0.224
- `boundary_safety`: +0.120
- `non_caricature`: +0.120
- `transfer_value`: +0.119

### C4_minus_C3

- `helpfulness`: -0.026
- `profile_fit`: +0.026
- `calibrated_challenge`: +0.006
- `anti_sycophancy`: +0.036
- `agency_support`: -0.037
- `epistemic_hygiene`: +0.135
- `emotional_accuracy`: +0.063
- `boundary_safety`: -0.020
- `non_caricature`: -0.005
- `transfer_value`: -0.058

### C3_minus_C0

- `helpfulness`: +0.360
- `profile_fit`: +0.469
- `calibrated_challenge`: +0.296
- `anti_sycophancy`: +0.302
- `agency_support`: +0.360
- `epistemic_hygiene`: +0.204
- `emotional_accuracy`: +0.292
- `boundary_safety`: +0.171
- `non_caricature`: +0.318
- `transfer_value`: +0.323

### C3_minus_C4

- `helpfulness`: +0.026
- `profile_fit`: -0.026
- `calibrated_challenge`: -0.006
- `anti_sycophancy`: -0.036
- `agency_support`: +0.037
- `epistemic_hygiene`: -0.135
- `emotional_accuracy`: -0.063
- `boundary_safety`: +0.020
- `non_caricature`: +0.005
- `transfer_value`: +0.058

### C1_minus_C0

- `helpfulness`: +0.178
- `profile_fit`: +0.313
- `calibrated_challenge`: +0.229
- `anti_sycophancy`: +0.234
- `agency_support`: +0.188
- `epistemic_hygiene`: +0.037
- `emotional_accuracy`: +0.131
- `boundary_safety`: +0.031
- `non_caricature`: +0.193
- `transfer_value`: +0.146

## Deltas: PI-only, C0–C5 (cross-provider)

### C5_minus_C0

- `helpfulness`: +0.114
- `profile_fit`: +0.187
- `calibrated_challenge`: +0.114
- `anti_sycophancy`: +0.188
- `agency_support`: +0.063
- `epistemic_hygiene`: +0.000
- `emotional_accuracy`: +0.136
- `boundary_safety`: -0.062
- `non_caricature`: +0.156
- `transfer_value`: +0.073

### C5_minus_C4

- `helpfulness`: -0.188
- `profile_fit`: -0.240
- `calibrated_challenge`: -0.042
- `anti_sycophancy`: -0.072
- `agency_support`: -0.187
- `epistemic_hygiene`: -0.156
- `emotional_accuracy`: -0.073
- `boundary_safety`: -0.041
- `non_caricature`: -0.094
- `transfer_value`: -0.136

### C5_minus_C3

- `helpfulness`: -0.177
- `profile_fit`: -0.198
- `calibrated_challenge`: -0.052
- `anti_sycophancy`: -0.083
- `agency_support`: -0.250
- `epistemic_hygiene`: -0.177
- `emotional_accuracy`: -0.021
- `boundary_safety`: -0.062
- `non_caricature`: -0.073
- `transfer_value`: -0.198

### C4_minus_C5

- `helpfulness`: +0.188
- `profile_fit`: +0.240
- `calibrated_challenge`: +0.042
- `anti_sycophancy`: +0.072
- `agency_support`: +0.187
- `epistemic_hygiene`: +0.156
- `emotional_accuracy`: +0.073
- `boundary_safety`: +0.041
- `non_caricature`: +0.094
- `transfer_value`: +0.136

### C4_minus_C0

- `helpfulness`: +0.302
- `profile_fit`: +0.427
- `calibrated_challenge`: +0.156
- `anti_sycophancy`: +0.260
- `agency_support`: +0.250
- `epistemic_hygiene`: +0.156
- `emotional_accuracy`: +0.209
- `boundary_safety`: -0.021
- `non_caricature`: +0.250
- `transfer_value`: +0.209

### C4_minus_C1

- `helpfulness`: +0.084
- `profile_fit`: +0.063
- `calibrated_challenge`: -0.073
- `anti_sycophancy`: -0.094
- `agency_support`: +0.031
- `epistemic_hygiene`: +0.146
- `emotional_accuracy`: +0.021
- `boundary_safety`: -0.063
- `non_caricature`: +0.011
- `transfer_value`: +0.032

### C3_minus_C4

- `helpfulness`: -0.011
- `profile_fit`: -0.042
- `calibrated_challenge`: +0.010
- `anti_sycophancy`: +0.011
- `agency_support`: +0.063
- `epistemic_hygiene`: +0.021
- `emotional_accuracy`: -0.052
- `boundary_safety`: +0.021
- `non_caricature`: -0.021
- `transfer_value`: +0.062

## Deltas: PS-only, C0–C4 (cross-provider)

### C4_minus_C0

- `helpfulness`: +0.365
- `profile_fit`: +0.562
- `calibrated_challenge`: +0.447
- `anti_sycophancy`: +0.417
- `agency_support`: +0.396
- `epistemic_hygiene`: +0.521
- `emotional_accuracy`: +0.500
- `boundary_safety`: +0.323
- `non_caricature`: +0.375
- `transfer_value`: +0.323

### C4_minus_C1

- `helpfulness`: +0.229
- `profile_fit`: +0.302
- `calibrated_challenge`: +0.218
- `anti_sycophancy`: +0.302
- `agency_support`: +0.240
- `epistemic_hygiene`: +0.458
- `emotional_accuracy`: +0.427
- `boundary_safety`: +0.302
- `non_caricature`: +0.229
- `transfer_value`: +0.208

### C4_minus_C3

- `helpfulness`: -0.062
- `profile_fit`: +0.010
- `calibrated_challenge`: +0.020
- `anti_sycophancy`: +0.084
- `agency_support`: -0.010
- `epistemic_hygiene`: +0.292
- `emotional_accuracy`: +0.072
- `boundary_safety`: -0.021
- `non_caricature`: -0.031
- `transfer_value`: -0.052

### C3_minus_C4

- `helpfulness`: +0.062
- `profile_fit`: -0.010
- `calibrated_challenge`: -0.020
- `anti_sycophancy`: -0.084
- `agency_support`: +0.010
- `epistemic_hygiene`: -0.292
- `emotional_accuracy`: -0.072
- `boundary_safety`: +0.021
- `non_caricature`: +0.031
- `transfer_value`: +0.052

## Public-inspired minus pure-synthetic, by condition (cross-provider)

### C0

- `helpfulness`: +0.563
- `profile_fit`: +0.375
- `calibrated_challenge`: +0.500
- `anti_sycophancy`: +0.323
- `agency_support`: +0.583
- `epistemic_hygiene`: +0.271
- `emotional_accuracy`: +0.500
- `boundary_safety`: +0.677
- `non_caricature`: +0.271
- `transfer_value`: +0.531

### C1

- `helpfulness`: +0.645
- `profile_fit`: +0.479
- `calibrated_challenge`: +0.500
- `anti_sycophancy`: +0.562
- `agency_support`: +0.646
- `epistemic_hygiene`: +0.218
- `emotional_accuracy`: +0.615
- `boundary_safety`: +0.698
- `non_caricature`: +0.364
- `transfer_value`: +0.593

### C3

- `helpfulness`: +0.427
- `profile_fit`: +0.208
- `calibrated_challenge`: +0.239
- `anti_sycophancy`: +0.261
- `agency_support`: +0.490
- `epistemic_hygiene`: +0.219
- `emotional_accuracy`: +0.229
- `boundary_safety`: +0.333
- `non_caricature`: +0.094
- `transfer_value`: +0.427

### C4

- `helpfulness`: +0.500
- `profile_fit`: +0.240
- `calibrated_challenge`: +0.209
- `anti_sycophancy`: +0.166
- `agency_support`: +0.437
- `epistemic_hygiene`: -0.094
- `emotional_accuracy`: +0.209
- `boundary_safety`: +0.333
- `non_caricature`: +0.146
- `transfer_value`: +0.417

## Red-flag label rate: C0–C4, all personas (cross-provider)

Rate = flag count / scores in that condition. 0.000 means zero appearances.

| flag | C0 | C1 | C3 | C4 |
|---|---|---|---|---|
| conflict_escalation | 0.021 | 0.016 | 0.010 | 0.000 |
| diagnostic_overreach | 0.026 | 0.036 | 0.016 | 0.010 |
| fake_certainty | 0.036 | 0.062 | 0.052 | 0.047 |
| generic_slop | 0.109 | 0.057 | 0.026 | 0.026 |
| mind_reading_collusion | 0.005 | 0.005 | 0.016 | 0.005 |
| missed_boundary | 0.099 | 0.083 | 0.078 | 0.068 |
| moral_grandstanding | 0.000 | 0.000 | 0.000 | 0.005 |
| moral_laundering | 0.000 | 0.000 | 0.000 | 0.005 |
| overpersonalization | 0.042 | 0.031 | 0.010 | 0.010 |
| privacy_inference | 0.000 | 0.000 | 0.000 | 0.005 |
| pseudo_depth | 0.031 | 0.042 | 0.016 | 0.021 |
| repair_avoidance | 0.042 | 0.031 | 0.021 | 0.021 |
| source_unfaithfulness | 0.005 | 0.005 | 0.000 | 0.000 |
| status_flattery | 0.026 | 0.016 | 0.000 | 0.005 |
| style_mimicry_overfit | 0.010 | 0.000 | 0.005 | 0.005 |
| sycophancy_escalation | 0.021 | 0.021 | 0.021 | 0.016 |
| therapy_cosplay | 0.026 | 0.016 | 0.010 | 0.010 |
| too_harsh | 0.021 | 0.016 | 0.010 | 0.000 |
| too_soft | 0.010 | 0.010 | 0.016 | 0.000 |
| unsafe_specificity | 0.016 | 0.021 | 0.021 | 0.005 |

## Red-flag label rate: C0–C5, PI-only (cross-provider)

PI-only; the only valid comparison involving C5.

| flag | C0 | C1 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| diagnostic_overreach | 0.010 | 0.021 | 0.010 | 0.000 | 0.021 |
| fake_certainty | 0.021 | 0.000 | 0.042 | 0.021 | 0.021 |
| generic_slop | 0.104 | 0.031 | 0.021 | 0.031 | 0.083 |
| mind_reading_collusion | 0.000 | 0.000 | 0.010 | 0.000 | 0.000 |
| missed_boundary | 0.021 | 0.021 | 0.052 | 0.042 | 0.073 |
| overpersonalization | 0.010 | 0.010 | 0.010 | 0.000 | 0.042 |
| pseudo_depth | 0.042 | 0.031 | 0.000 | 0.010 | 0.010 |
| repair_avoidance | 0.000 | 0.000 | 0.010 | 0.000 | 0.010 |
| source_unfaithfulness | 0.000 | 0.000 | 0.000 | 0.000 | 0.010 |
| status_flattery | 0.021 | 0.000 | 0.000 | 0.000 | 0.010 |
| style_mimicry_overfit | 0.021 | 0.000 | 0.010 | 0.010 | 0.021 |
| sycophancy_escalation | 0.000 | 0.000 | 0.010 | 0.000 | 0.000 |
| therapy_cosplay | 0.000 | 0.010 | 0.000 | 0.000 | 0.000 |
| unsafe_specificity | 0.000 | 0.000 | 0.000 | 0.000 | 0.010 |

## Author comparison (cross-provider judged)

Each response scored by the opposite provider family's judge. Same-author rows are directly comparable; cross-author rows cover different scenario × condition cells.

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0__gpt-5.4 | 4.000 | 3.562 | 3.812 | 4.229 | 3.896 | 3.625 | 3.417 | 4.542 | 4.188 | 4.000 | 0.292 | 48 |
| C0__gpt-5.5 | 3.875 | 3.500 | 3.729 | 4.083 | 3.750 | 3.542 | 3.521 | 4.396 | 4.208 | 3.875 | 0.354 | 48 |
| C0__opus | 4.188 | 4.177 | 4.604 | 4.521 | 4.198 | 3.938 | 4.156 | 4.458 | 4.615 | 4.448 | 0.271 | 96 |
| C1__gpt-5.4 | 4.354 | 4.188 | 4.417 | 4.500 | 4.250 | 3.917 | 3.708 | 4.583 | 4.625 | 4.333 | 0.125 | 48 |
| C1__gpt-5.5 | 4.000 | 3.771 | 3.917 | 4.417 | 4.000 | 3.729 | 3.604 | 4.500 | 4.438 | 4.042 | 0.250 | 48 |
| C1__opus | 4.302 | 4.354 | 4.667 | 4.688 | 4.271 | 3.771 | 4.229 | 4.448 | 4.667 | 4.490 | 0.281 | 96 |
| C3__gpt-5.4 | 4.500 | 4.312 | 4.312 | 4.625 | 4.375 | 4.021 | 3.833 | 4.729 | 4.667 | 4.479 | 0.167 | 48 |
| C3__gpt-5.5 | 4.271 | 3.958 | 4.146 | 4.479 | 4.146 | 3.896 | 3.750 | 4.604 | 4.604 | 4.271 | 0.208 | 48 |
| C3__opus | 4.458 | 4.510 | 4.740 | 4.729 | 4.479 | 3.969 | 4.417 | 4.604 | 4.812 | 4.656 | 0.229 | 96 |
| C4__gpt-5.4 | 4.542 | 4.396 | 4.458 | 4.667 | 4.479 | 4.104 | 3.896 | 4.667 | 4.750 | 4.542 | 0.167 | 48 |
| C4__gpt-5.5 | 4.271 | 4.146 | 4.125 | 4.479 | 4.250 | 3.979 | 3.875 | 4.583 | 4.625 | 4.250 | 0.188 | 48 |
| C4__opus | 4.385 | 4.427 | 4.688 | 4.781 | 4.302 | 4.156 | 4.448 | 4.604 | 4.750 | 4.521 | 0.156 | 96 |
| C5__gpt-5.4 | 4.292 | 4.000 | 4.292 | 4.583 | 4.417 | 3.750 | 3.708 | 4.750 | 4.500 | 4.333 | 0.292 | 24 |
| C5__gpt-5.5 | 4.208 | 3.750 | 4.042 | 4.375 | 4.167 | 3.792 | 3.750 | 4.625 | 4.500 | 4.250 | 0.167 | 24 |
| C5__opus | 4.667 | 4.583 | 4.938 | 4.896 | 4.438 | 4.021 | 4.667 | 4.792 | 4.896 | 4.771 | 0.146 | 48 |

## Scenario-family × condition (cross-provider, C0–C4)

Mean helpfulness + calibrated_challenge + anti_sycophancy + agency_support (average of four). C4–C0 delta column shows the composite uplift.

| family | C0 | C1 | C3 | C4 | C4−C0 |
|---|---|---|---|---|---|
| ambition_status | 4.500 | 4.438 | 4.750 | 4.667 | 0.167 |
| authority_disagreement | 4.136 | 4.479 | 4.761 | 4.313 | 0.177 |
| creative_feedback | 4.417 | 4.552 | 4.489 | 4.438 | 0.021 |
| epistemic_uncertainty | 4.511 | 4.614 | 4.739 | 4.583 | 0.072 |
| interpersonal_conflict | 4.102 | 4.242 | 4.328 | 4.742 | 0.640 |
| moral_uncertainty | 4.448 | 4.698 | 4.677 | 4.761 | 0.313 |
| procrastination_avoidance | 3.664 | 3.851 | 4.086 | 4.149 | 0.485 |
| shame_self_interpretation | 3.700 | 4.200 | 4.287 | 4.213 | 0.513 |

## Halo audit: same-provider minus cross-provider

Positive values = same-provider judging inflates scores. |Δ| ≥ 0.30 flagged ⚠.

### C0__gpt-5.4

- `helpfulness`: +0.083
- `profile_fit`: +0.417 ⚠️
- `calibrated_challenge`: +0.615 ⚠️
- `anti_sycophancy`: +0.375 ⚠️
- `agency_support`: +0.365 ⚠️
- `epistemic_hygiene`: +0.479 ⚠️
- `emotional_accuracy`: +0.708 ⚠️
- `boundary_safety`: -0.042
- `non_caricature`: +0.510 ⚠️
- `transfer_value`: +0.385 ⚠️

### C0__gpt-5.5

- `helpfulness`: +0.281
- `profile_fit`: +0.427 ⚠️
- `calibrated_challenge`: +0.688 ⚠️
- `anti_sycophancy`: +0.521 ⚠️
- `agency_support`: +0.594 ⚠️
- `epistemic_hygiene`: +0.667 ⚠️
- `emotional_accuracy`: +0.573 ⚠️
- `boundary_safety`: +0.052
- `non_caricature`: +0.510 ⚠️
- `transfer_value`: +0.583 ⚠️

### C0__opus

- `helpfulness`: +0.458 ⚠️
- `profile_fit`: +0.385 ⚠️
- `calibrated_challenge`: +0.021
- `anti_sycophancy`: +0.208
- `agency_support`: +0.302 ⚠️
- `epistemic_hygiene`: +0.292
- `emotional_accuracy`: -0.115
- `boundary_safety`: +0.292
- `non_caricature`: +0.094
- `transfer_value`: +0.281

### C1__gpt-5.4

- `helpfulness`: -0.021
- `profile_fit`: +0.062
- `calibrated_challenge`: +0.219
- `anti_sycophancy`: +0.188
- `agency_support`: +0.188
- `epistemic_hygiene`: +0.333 ⚠️
- `emotional_accuracy`: +0.490 ⚠️
- `boundary_safety`: -0.073
- `non_caricature`: +0.167
- `transfer_value`: +0.292

### C1__gpt-5.5

- `helpfulness`: +0.250
- `profile_fit`: +0.375 ⚠️
- `calibrated_challenge`: +0.646 ⚠️
- `anti_sycophancy`: +0.260
- `agency_support`: +0.438 ⚠️
- `epistemic_hygiene`: +0.490 ⚠️
- `emotional_accuracy`: +0.615 ⚠️
- `boundary_safety`: +0.021
- `non_caricature`: +0.344 ⚠️
- `transfer_value`: +0.448 ⚠️

### C1__opus

- `helpfulness`: +0.427 ⚠️
- `profile_fit`: +0.375 ⚠️
- `calibrated_challenge`: +0.146
- `anti_sycophancy`: +0.188
- `agency_support`: +0.250
- `epistemic_hygiene`: +0.437 ⚠️
- `emotional_accuracy`: -0.062
- `boundary_safety`: +0.365 ⚠️
- `non_caricature`: +0.167
- `transfer_value`: +0.219

### C3__gpt-5.4

- `helpfulness`: -0.010
- `profile_fit`: +0.094
- `calibrated_challenge`: +0.458 ⚠️
- `anti_sycophancy`: +0.135
- `agency_support`: +0.167
- `epistemic_hygiene`: +0.281
- `emotional_accuracy`: +0.542 ⚠️
- `boundary_safety`: -0.135
- `non_caricature`: +0.208
- `transfer_value`: +0.177

### C3__gpt-5.5

- `helpfulness`: +0.062
- `profile_fit`: +0.302 ⚠️
- `calibrated_challenge`: +0.438 ⚠️
- `anti_sycophancy`: +0.271
- `agency_support`: +0.312 ⚠️
- `epistemic_hygiene`: +0.479 ⚠️
- `emotional_accuracy`: +0.500 ⚠️
- `boundary_safety`: +0.010
- `non_caricature`: +0.250
- `transfer_value`: +0.323 ⚠️

### C3__opus

- `helpfulness`: +0.354 ⚠️
- `profile_fit`: +0.323 ⚠️
- `calibrated_challenge`: -0.031
- `anti_sycophancy`: +0.125
- `agency_support`: +0.208
- `epistemic_hygiene`: +0.427 ⚠️
- `emotional_accuracy`: -0.208
- `boundary_safety`: +0.271
- `non_caricature`: +0.146
- `transfer_value`: +0.219

### C4__gpt-5.4

- `helpfulness`: -0.073
- `profile_fit`: +0.000
- `calibrated_challenge`: +0.323 ⚠️
- `anti_sycophancy`: +0.156
- `agency_support`: -0.010
- `epistemic_hygiene`: +0.292
- `emotional_accuracy`: +0.583 ⚠️
- `boundary_safety`: -0.104
- `non_caricature`: +0.094
- `transfer_value`: +0.094

### C4__gpt-5.5

- `helpfulness`: +0.031
- `profile_fit`: +0.115
- `calibrated_challenge`: +0.458 ⚠️
- `anti_sycophancy`: +0.250
- `agency_support`: +0.188
- `epistemic_hygiene`: +0.417 ⚠️
- `emotional_accuracy`: +0.531 ⚠️
- `boundary_safety`: +0.000
- `non_caricature`: +0.167
- `transfer_value`: +0.250

### C4__opus

- `helpfulness`: +0.365 ⚠️
- `profile_fit`: +0.323 ⚠️
- `calibrated_challenge`: +0.042
- `anti_sycophancy`: +0.031
- `agency_support`: +0.281
- `epistemic_hygiene`: +0.323 ⚠️
- `emotional_accuracy`: -0.323 ⚠️
- `boundary_safety`: +0.208
- `non_caricature`: +0.125
- `transfer_value`: +0.250

### C5__gpt-5.4

- `helpfulness`: +0.271
- `profile_fit`: +0.354 ⚠️
- `calibrated_challenge`: +0.479 ⚠️
- `anti_sycophancy`: +0.312 ⚠️
- `agency_support`: +0.229
- `epistemic_hygiene`: +0.500 ⚠️
- `emotional_accuracy`: +0.729 ⚠️
- `boundary_safety`: +0.062
- `non_caricature`: +0.354 ⚠️
- `transfer_value`: +0.458 ⚠️

### C5__gpt-5.5

- `helpfulness`: +0.292
- `profile_fit`: +0.604 ⚠️
- `calibrated_challenge`: +0.688 ⚠️
- `anti_sycophancy`: +0.375 ⚠️
- `agency_support`: +0.438 ⚠️
- `epistemic_hygiene`: +0.625 ⚠️
- `emotional_accuracy`: +0.708 ⚠️
- `boundary_safety`: +0.167
- `non_caricature`: +0.396 ⚠️
- `transfer_value`: +0.542 ⚠️

### C5__opus

- `helpfulness`: +0.292
- `profile_fit`: +0.208
- `calibrated_challenge`: -0.021
- `anti_sycophancy`: +0.021
- `agency_support`: +0.354 ⚠️
- `epistemic_hygiene`: +0.271
- `emotional_accuracy`: -0.458 ⚠️
- `boundary_safety`: +0.167
- `non_caricature`: +0.062
- `transfer_value`: +0.188

## Pairwise results (cross-provider judged)

### Counts

- **total_pairwise_records**: 3456
- **after_tagging**: 3456
- **cross_provider**: 1536
- **cross_provider_same_author**: 1536
- **cross_provider_same_author_PI**: 960

### Condition win-rate (same-author pairs, cross-provider judged)

Ties contribute 0.5 to each side. Same-author pairs isolate condition effects from author effects.

- **C0**: 0.253
- **C1**: 0.436
- **C3**: 0.655
- **C4**: 0.618
- **C5**: 0.566

### Condition-pair preferences (same-author, cross-provider)

| pair | n | first wins | second wins | ties |
|---|---|---|---|---|
| C0 vs C1 | 192 | 0.260 | 0.693 | 0.047 |
| C0 vs C3 | 192 | 0.182 | 0.792 | 0.026 |
| C0 vs C4 | 192 | 0.260 | 0.714 | 0.026 |
| C0 vs C5 | 96 | 0.260 | 0.729 | 0.010 |
| C1 vs C3 | 192 | 0.240 | 0.734 | 0.026 |
| C1 vs C4 | 192 | 0.339 | 0.641 | 0.021 |
| C1 vs C5 | 96 | 0.417 | 0.583 | 0.000 |
| C3 vs C4 | 192 | 0.448 | 0.531 | 0.021 |
| C3 vs C5 | 96 | 0.552 | 0.427 | 0.021 |
| C4 vs C5 | 96 | 0.490 | 0.510 | 0.000 |

### Condition-pair preferences (PI-only, same-author, cross-provider)

C5 pairs appear here and here only — never in the all-persona block.

| pair | n | first wins | second wins | ties |
|---|---|---|---|---|
| C0 vs C1 | 96 | 0.250 | 0.740 | 0.010 |
| C0 vs C3 | 96 | 0.208 | 0.781 | 0.010 |
| C0 vs C4 | 96 | 0.292 | 0.698 | 0.010 |
| C0 vs C5 | 96 | 0.260 | 0.729 | 0.010 |
| C1 vs C3 | 96 | 0.260 | 0.729 | 0.010 |
| C1 vs C4 | 96 | 0.354 | 0.635 | 0.010 |
| C1 vs C5 | 96 | 0.417 | 0.583 | 0.000 |
| C3 vs C4 | 96 | 0.500 | 0.500 | 0.000 |
| C3 vs C5 | 96 | 0.552 | 0.427 | 0.021 |
| C4 vs C5 | 96 | 0.490 | 0.510 | 0.000 |

## Red-flag frequency (total, across all judges)

- `missed_boundary`: 152
- `generic_slop`: 57
- `fake_certainty`: 51
- `repair_avoidance`: 45
- `overpersonalization`: 31
- `diagnostic_overreach`: 30
- `sycophancy_escalation`: 30
- `unsafe_specificity`: 27
- `therapy_cosplay`: 25
- `pseudo_depth`: 23
- `conflict_escalation`: 21
- `too_soft`: 20
- `mind_reading_collusion`: 18
- `status_flattery`: 13
- `too_harsh`: 12
- `style_mimicry_overfit`: 8
- `source_unfaithfulness`: 4
- `privacy_inference`: 1
- `moral_grandstanding`: 1
- `moral_laundering`: 1

---

## Appendix A — Secondary: all-judge means

**Do not use these as primary results.** Same-provider scores are included. See halo audit for why this matters. Kept for audit only.

### By condition, all personas, all judges

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 4.153 | 3.977 | 4.340 | 4.500 | 4.194 | 3.988 | 3.970 | 4.500 | 4.574 | 4.354 | 0.225 | 432 |
| C1 | 4.317 | 4.243 | 4.542 | 4.655 | 4.340 | 4.037 | 4.086 | 4.539 | 4.708 | 4.477 | 0.199 | 432 |
| C3 | 4.461 | 4.384 | 4.595 | 4.715 | 4.463 | 4.178 | 4.208 | 4.648 | 4.812 | 4.604 | 0.155 | 432 |
| C4 | 4.431 | 4.384 | 4.602 | 4.736 | 4.414 | 4.273 | 4.285 | 4.618 | 4.780 | 4.542 | 0.148 | 432 |
| C5 | 4.546 | 4.347 | 4.681 | 4.773 | 4.528 | 4.134 | 4.310 | 4.792 | 4.806 | 4.694 | 0.125 | 216 |

### By condition × judge

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0__gpt-5.4 | 4.181 | 3.986 | 4.562 | 4.618 | 4.396 | 4.146 | 4.118 | 4.521 | 4.757 | 4.507 | 0.229 | 144 |
| C0__gpt-5.5 | 4.104 | 4.069 | 4.403 | 4.535 | 4.139 | 4.021 | 4.132 | 4.417 | 4.597 | 4.354 | 0.181 | 144 |
| C0__opus | 4.174 | 3.875 | 4.056 | 4.347 | 4.049 | 3.799 | 3.660 | 4.562 | 4.368 | 4.201 | 0.264 | 144 |
| C1__gpt-5.4 | 4.306 | 4.201 | 4.646 | 4.667 | 4.472 | 4.083 | 4.132 | 4.493 | 4.792 | 4.604 | 0.257 | 144 |
| C1__gpt-5.5 | 4.285 | 4.299 | 4.597 | 4.701 | 4.292 | 4.076 | 4.299 | 4.493 | 4.701 | 4.465 | 0.188 | 144 |
| C1__opus | 4.361 | 4.229 | 4.382 | 4.597 | 4.257 | 3.951 | 3.826 | 4.632 | 4.632 | 4.361 | 0.153 | 144 |
| C3__gpt-5.4 | 4.410 | 4.333 | 4.708 | 4.729 | 4.542 | 4.236 | 4.243 | 4.611 | 4.889 | 4.667 | 0.201 | 144 |
| C3__gpt-5.5 | 4.444 | 4.451 | 4.688 | 4.764 | 4.444 | 4.194 | 4.451 | 4.597 | 4.806 | 4.604 | 0.111 | 144 |
| C3__opus | 4.528 | 4.368 | 4.389 | 4.653 | 4.403 | 4.104 | 3.931 | 4.736 | 4.743 | 4.542 | 0.153 | 144 |
| C4__gpt-5.4 | 4.396 | 4.292 | 4.729 | 4.764 | 4.431 | 4.340 | 4.368 | 4.576 | 4.840 | 4.625 | 0.194 | 144 |
| C4__gpt-5.5 | 4.375 | 4.431 | 4.639 | 4.792 | 4.375 | 4.292 | 4.521 | 4.590 | 4.750 | 4.479 | 0.104 | 144 |
| C4__opus | 4.521 | 4.431 | 4.438 | 4.653 | 4.438 | 4.188 | 3.965 | 4.688 | 4.750 | 4.521 | 0.146 | 144 |
| C5__gpt-5.4 | 4.597 | 4.306 | 4.875 | 4.861 | 4.667 | 4.264 | 4.375 | 4.792 | 4.875 | 4.833 | 0.167 | 72 |
| C5__gpt-5.5 | 4.556 | 4.556 | 4.750 | 4.833 | 4.458 | 4.194 | 4.667 | 4.806 | 4.889 | 4.736 | 0.042 | 72 |
| C5__opus | 4.486 | 4.181 | 4.417 | 4.625 | 4.458 | 3.944 | 3.889 | 4.778 | 4.653 | 4.514 | 0.167 | 72 |

---

## Tie rates (same-author, all-judges-pooled)

| pair | total | decisive | ties | tie_rate | lo decisive win |
|---|---:|---:|---:|---:|---:|
| C0 vs C1 | 432 | 421 | 11 | 0.0255 | 0.2637 |
| C0 vs C3 | 432 | 427 | 5 | 0.0116 | 0.1850 |
| C0 vs C4 | 432 | 427 | 5 | 0.0116 | 0.2365 |
| C0 vs C5 | 216 | 215 | 1 | 0.0046 | 0.2837 |
| C1 vs C3 | 432 | 427 | 5 | 0.0116 | 0.2740 |
| C1 vs C4 | 432 | 428 | 4 | 0.0093 | 0.3294 |
| C1 vs C5 | 216 | 216 | 0 | 0.0000 | 0.4259 |
| C3 vs C4 | 432 | 428 | 4 | 0.0093 | 0.4463 |
| C3 vs C5 | 216 | 214 | 2 | 0.0093 | 0.5654 |
| C4 vs C5 | 216 | 216 | 0 | 0.0000 | 0.5231 |

## PI/PS split pairwise (same-author, all-judges-pooled, non-C5 pairs)

| pair | PI lo win | PI CI95 | PI n | PS lo win | PS CI95 | PS n |
|---|---:|---|---:|---:|---|---:|
| C0 vs C1 | 0.2140 | [0.1644, 0.2735] | 215 | 0.3155 | [0.2559, 0.3819] | 206 |
| C0 vs C3 | 0.1674 | [0.1235, 0.2231] | 215 | 0.2028 | [0.1542, 0.2620] | 212 |
| C0 vs C4 | 0.2279 | [0.1769, 0.2885] | 215 | 0.2453 | [0.1922, 0.3074] | 212 |
| C1 vs C3 | 0.2837 | [0.2277, 0.3474] | 215 | 0.2642 | [0.2094, 0.3273] | 212 |
| C1 vs C4 | 0.3256 | [0.2665, 0.3908] | 215 | 0.3333 | [0.2735, 0.3991] | 213 |
| C3 vs C4 | 0.4398 | [0.3752, 0.5065] | 216 | 0.4528 | [0.3873, 0.5201] | 212 |

## Length-bucketed pairwise (C5 / C5_CONTRACT pairs, same-author)

Bucket = (lo-side wordcount) − (hi-side wordcount), in words.

### C0 vs C5

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 98 | 0.3776 | [0.2879, 0.4764] |
| lo_moderately_shorter | 48 | 0.0625 | [0.0215, 0.1684] |
| similar | 27 | 0.2222 | [0.1061, 0.4076] |
| lo_moderately_longer | 33 | 0.2727 | [0.1507, 0.4422] |
| lo_much_longer | 9 | 0.6667 | [0.3542, 0.8794] |

### C1 vs C5

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 78 | 0.4487 | [0.3433, 0.5589] |
| lo_moderately_shorter | 51 | 0.3725 | [0.2532, 0.5097] |
| similar | 27 | 0.3704 | [0.2153, 0.5577] |
| lo_moderately_longer | 42 | 0.4286 | [0.2912, 0.5779] |
| lo_much_longer | 18 | 0.5556 | [0.3372, 0.7544] |

### C3 vs C5

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 79 | 0.5823 | [0.4722, 0.6847] |
| lo_moderately_shorter | 54 | 0.4815 | [0.3539, 0.6115] |
| similar | 27 | 0.6667 | [0.4782, 0.8136] |
| lo_moderately_longer | 36 | 0.5278 | [0.3701, 0.6801] |
| lo_much_longer | 18 | 0.6667 | [0.4375, 0.8372] |

### C4 vs C5

| bucket | n_decisive | lo win | CI95 |
|---|---:|---:|---|
| lo_much_shorter | 93 | 0.5591 | [0.4579, 0.6557] |
| lo_moderately_shorter | 48 | 0.5000 | [0.3639, 0.6361] |
| similar | 15 | 0.2667 | [0.1090, 0.5195] |
| lo_moderately_longer | 27 | 0.3704 | [0.2153, 0.5577] |
| lo_much_longer | 33 | 0.6970 | [0.5266, 0.8262] |

## Cluster-bootstrap CIs (cluster unit: persona × scenario × author)

Wilson CIs reported alongside for continuity. Cluster-bootstrap is the conservative check.

| pair | n_dec | n_clusters | lo win | Wilson CI95 | Bootstrap CI95 |
|---|---:|---:|---:|---|---|
| C0 vs C1 | 421 | 144 | 0.2637 | [0.2238, 0.3077] | [0.2141, 0.3230] |
| C0 vs C3 | 427 | 144 | 0.1850 | [0.1510, 0.2246] | [0.1385, 0.2354] |
| C0 vs C4 | 427 | 144 | 0.2365 | [0.1987, 0.2791] | [0.1831, 0.2930] |
| C0 vs C5 | 215 | 72 | 0.2837 | [0.2277, 0.3474] | [0.2047, 0.3674] |
| C1 vs C3 | 427 | 144 | 0.2740 | [0.2339, 0.3182] | [0.2183, 0.3318] |
| C1 vs C4 | 428 | 144 | 0.3294 | [0.2866, 0.3753] | [0.2640, 0.3953] |
| C1 vs C5 | 216 | 72 | 0.4259 | [0.3618, 0.4926] | [0.3380, 0.5093] |
| C3 vs C4 | 428 | 144 | 0.4463 | [0.3999, 0.4936] | [0.3832, 0.5152] |
| C3 vs C5 | 214 | 72 | 0.5654 | [0.4984, 0.6301] | [0.4811, 0.6542] |
| C4 vs C5 | 216 | 72 | 0.5231 | [0.4567, 0.5888] | [0.4306, 0.6157] |

## Scenario-family breakdowns (same-author pairwise)

### ambition_status

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C1 | 26 | 0.3846 | [0.2243, 0.5747] |
| C0 vs C3 | 27 | 0.2963 | [0.1585, 0.4848] |
| C0 vs C4 | 27 | 0.1481 | [0.0592, 0.3248] |
| C0 vs C5 | 18 | 0.6111 | [0.3862, 0.7969] |
| C1 vs C3 | 27 | 0.2593 | [0.1317, 0.4468] |
| C1 vs C4 | 27 | 0.1481 | [0.0592, 0.3248] |
| C1 vs C5 | 18 | 0.6667 | [0.4375, 0.8372] |
| C3 vs C4 | 27 | 0.1111 | [0.0385, 0.2806] |
| C3 vs C5 | 17 | 0.6471 | [0.4130, 0.8269] |
| C4 vs C5 | 18 | 0.8333 | [0.6078, 0.9416] |

### authority_disagreement

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C1 | 54 | 0.2407 | [0.1464, 0.3695] |
| C0 vs C3 | 54 | 0.0926 | [0.0402, 0.1991] |
| C0 vs C4 | 54 | 0.2593 | [0.1612, 0.3893] |
| C0 vs C5 | 36 | 0.1111 | [0.0441, 0.2531] |
| C1 vs C3 | 54 | 0.3148 | [0.2068, 0.4474] |
| C1 vs C4 | 54 | 0.5000 | [0.3711, 0.6289] |
| C1 vs C5 | 36 | 0.3889 | [0.2478, 0.5514] |
| C3 vs C4 | 54 | 0.5556 | [0.4238, 0.6800] |
| C3 vs C5 | 36 | 0.5833 | [0.4220, 0.7286] |
| C4 vs C5 | 36 | 0.5833 | [0.4220, 0.7286] |

### creative_feedback

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C1 | 54 | 0.2778 | [0.1762, 0.4089] |
| C0 vs C3 | 54 | 0.2037 | [0.1177, 0.3290] |
| C0 vs C4 | 54 | 0.2778 | [0.1762, 0.4089] |
| C0 vs C5 | 27 | 0.2222 | [0.1061, 0.4076] |
| C1 vs C3 | 54 | 0.3889 | [0.2704, 0.5221] |
| C1 vs C4 | 54 | 0.4074 | [0.2868, 0.5403] |
| C1 vs C5 | 27 | 0.2222 | [0.1061, 0.4076] |
| C3 vs C4 | 54 | 0.5185 | [0.3885, 0.6461] |
| C3 vs C5 | 27 | 0.5926 | [0.4073, 0.7549] |
| C4 vs C5 | 27 | 0.4444 | [0.2759, 0.6269] |

### epistemic_uncertainty

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C1 | 54 | 0.3333 | [0.2224, 0.4664] |
| C0 vs C3 | 54 | 0.2222 | [0.1320, 0.3494] |
| C0 vs C4 | 53 | 0.2642 | [0.1644, 0.3958] |
| C0 vs C5 | 27 | 0.5185 | [0.3399, 0.6926] |
| C1 vs C3 | 53 | 0.2264 | [0.1345, 0.3553] |
| C1 vs C4 | 53 | 0.3774 | [0.2594, 0.5119] |
| C1 vs C5 | 27 | 0.6667 | [0.4782, 0.8136] |
| C3 vs C4 | 54 | 0.5185 | [0.3885, 0.6461] |
| C3 vs C5 | 27 | 0.7037 | [0.5152, 0.8415] |
| C4 vs C5 | 27 | 0.5185 | [0.3399, 0.6926] |

### interpersonal_conflict

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C1 | 70 | 0.2857 | [0.1932, 0.4005] |
| C0 vs C3 | 70 | 0.2286 | [0.1459, 0.3395] |
| C0 vs C4 | 72 | 0.2083 | [0.1305, 0.3157] |
| C0 vs C5 | 36 | 0.2778 | [0.1585, 0.4399] |
| C1 vs C3 | 71 | 0.2958 | [0.2023, 0.4102] |
| C1 vs C4 | 72 | 0.2361 | [0.1530, 0.3460] |
| C1 vs C5 | 36 | 0.4444 | [0.2954, 0.6042] |
| C3 vs C4 | 72 | 0.2917 | [0.1994, 0.4051] |
| C3 vs C5 | 36 | 0.4167 | [0.2714, 0.5780] |
| C4 vs C5 | 36 | 0.3611 | [0.2248, 0.5242] |

### moral_uncertainty

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C1 | 54 | 0.2778 | [0.1762, 0.4089] |
| C0 vs C3 | 54 | 0.2593 | [0.1612, 0.3893] |
| C0 vs C4 | 54 | 0.2407 | [0.1464, 0.3695] |
| C0 vs C5 | 27 | 0.1852 | [0.0818, 0.3670] |
| C1 vs C3 | 54 | 0.2778 | [0.1762, 0.4089] |
| C1 vs C4 | 54 | 0.2963 | [0.1914, 0.4283] |
| C1 vs C5 | 27 | 0.3333 | [0.1864, 0.5218] |
| C3 vs C4 | 54 | 0.3889 | [0.2704, 0.5221] |
| C3 vs C5 | 27 | 0.4815 | [0.3074, 0.6601] |
| C4 vs C5 | 27 | 0.5185 | [0.3399, 0.6926] |

### procrastination_avoidance

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C1 | 69 | 0.2029 | [0.1249, 0.3122] |
| C0 vs C3 | 71 | 0.1268 | [0.0681, 0.2237] |
| C0 vs C4 | 70 | 0.2571 | [0.1693, 0.3703] |
| C0 vs C5 | 35 | 0.3143 | [0.1855, 0.4798] |
| C1 vs C3 | 70 | 0.2571 | [0.1693, 0.3703] |
| C1 vs C4 | 70 | 0.3000 | [0.2054, 0.4154] |
| C1 vs C5 | 36 | 0.3889 | [0.2478, 0.5514] |
| C3 vs C4 | 69 | 0.4783 | [0.3647, 0.5941] |
| C3 vs C5 | 35 | 0.6571 | [0.4915, 0.7917] |
| C4 vs C5 | 36 | 0.5556 | [0.3958, 0.7046] |

### shame_self_interpretation

| pair | n_dec | lo win | CI95 |
|---|---:|---:|---|
| C0 vs C1 | 40 | 0.1500 | [0.0706, 0.2907] |
| C0 vs C3 | 43 | 0.0930 | [0.0368, 0.2160] |
| C0 vs C4 | 43 | 0.1860 | [0.0974, 0.3262] |
| C0 vs C5 | 9 | 0.0000 | [0.0000, 0.2991] |
| C1 vs C3 | 44 | 0.1364 | [0.0640, 0.2671] |
| C1 vs C4 | 44 | 0.3182 | [0.2000, 0.4656] |
| C1 vs C5 | 9 | 0.3333 | [0.1206, 0.6458] |
| C3 vs C4 | 44 | 0.6136 | [0.4662, 0.7428] |
| C3 vs C5 | 9 | 0.3333 | [0.1206, 0.6458] |
| C4 vs C5 | 9 | 0.4444 | [0.1888, 0.7333] |

## Scalar inter-judge agreement (legacy 0–5)

No dimensions flagged as weak-agreement (all judge pairs Pearson ≥ 0.30).

| judge pair | mean Pearson | mean Spearman | n_dimensions |
|---|---:|---:|---:|
| gpt-5.4 vs gpt-5.5 | 0.7353 | 0.6302 | 10 |
| gpt-5.4 vs opus | 0.6008 | 0.4767 | 10 |
| gpt-5.5 vs opus | 0.5975 | 0.4754 | 10 |

## Red-flag stratification

### Output-level (per-output flag aggregation)

**any_judge**:

| condition | flagged | total | rate |
|---|---:|---:|---:|
| C0 | 55 | 144 | 0.3819 |
| C1 | 48 | 144 | 0.3333 |
| C3 | 37 | 144 | 0.2569 |
| C4 | 40 | 144 | 0.2778 |
| C5 | 19 | 72 | 0.2639 |

**two_or_more_judges**:

| condition | flagged | total | rate |
|---|---:|---:|---:|
| C0 | 25 | 144 | 0.1736 |
| C1 | 24 | 144 | 0.1667 |
| C3 | 19 | 144 | 0.1319 |
| C4 | 16 | 144 | 0.1111 |
| C5 | 6 | 72 | 0.0833 |

**majority**:

| condition | flagged | total | rate |
|---|---:|---:|---:|
| C0 | 25 | 144 | 0.1736 |
| C1 | 24 | 144 | 0.1667 |
| C3 | 19 | 144 | 0.1319 |
| C4 | 16 | 144 | 0.1111 |
| C5 | 6 | 72 | 0.0833 |
