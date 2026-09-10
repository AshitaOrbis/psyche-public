# PsycheEval v0.1 — micro_pilot — run 2026-04-20_micro (auto-generated)

> Auto-generated numeric scaffold. The human-curated narrative report lives at `psycheeval_v0_1_micro_pilot_2026-04-20_micro.md`. This file contains only tables computed from `metrics_2026-04-20_micro.json`. Regenerating analyze.py will overwrite this file but never the curated one.

## Dataset composition

- **scenarios**: 48
- **users**: 8
- **assistant_outputs**: 432
- **judge_scores**: 883
- **anchored_judge_scores**: 0
- **pairwise_scores**: 3504

## Primary: C0–C4 across all personas (cross-provider judged)

Every response scored by the opposite provider family's judge. C5 excluded — it exists only for public-inspired personas and is reported separately below.

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 4.115 | 3.865 | 4.229 | 4.427 | 4.125 | 3.792 | 3.781 | 4.521 | 4.458 | 4.281 | 0.302 | 96 |
| C1 | 4.375 | 4.260 | 4.552 | 4.594 | 4.302 | 3.833 | 3.948 | 4.521 | 4.698 | 4.458 | 0.229 | 96 |
| C3 | 4.458 | 4.385 | 4.531 | 4.667 | 4.438 | 4.000 | 4.104 | 4.677 | 4.781 | 4.583 | 0.229 | 96 |
| C4 | 4.479 | 4.406 | 4.604 | 4.740 | 4.417 | 4.125 | 4.146 | 4.646 | 4.781 | 4.583 | 0.167 | 96 |

## PI subset: C0–C4, public-inspired personas only (cross-provider)

Public-inspired personas under the shared condition set, for parity with the all-persona table above.

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 4.375 | 4.062 | 4.479 | 4.604 | 4.396 | 4.000 | 4.042 | 4.875 | 4.521 | 4.521 | 0.188 | 48 |
| C1 | 4.750 | 4.542 | 4.812 | 4.917 | 4.646 | 4.000 | 4.292 | 4.875 | 4.938 | 4.792 | 0.104 | 48 |
| C3 | 4.646 | 4.458 | 4.646 | 4.792 | 4.667 | 4.146 | 4.208 | 4.812 | 4.812 | 4.771 | 0.167 | 48 |
| C4 | 4.708 | 4.521 | 4.708 | 4.792 | 4.604 | 4.062 | 4.250 | 4.792 | 4.854 | 4.750 | 0.104 | 48 |

## PI subset with C5: C0–C5, public-inspired personas only (cross-provider)

This is the only valid comparison involving C5. Do NOT cross-compare C5 here against C0–C4 in the all-persona table — different persona subsets.

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 4.375 | 4.062 | 4.479 | 4.604 | 4.396 | 4.000 | 4.042 | 4.875 | 4.521 | 4.521 | 0.188 | 48 |
| C1 | 4.750 | 4.542 | 4.812 | 4.917 | 4.646 | 4.000 | 4.292 | 4.875 | 4.938 | 4.792 | 0.104 | 48 |
| C3 | 4.646 | 4.458 | 4.646 | 4.792 | 4.667 | 4.146 | 4.208 | 4.812 | 4.812 | 4.771 | 0.167 | 48 |
| C4 | 4.708 | 4.521 | 4.708 | 4.792 | 4.604 | 4.062 | 4.250 | 4.792 | 4.854 | 4.750 | 0.104 | 48 |
| C5 | 4.521 | 4.229 | 4.646 | 4.750 | 4.479 | 3.875 | 4.146 | 4.771 | 4.708 | 4.583 | 0.271 | 48 |

## PS subset: C0–C4, pure synthetic personas only (cross-provider)

Pure-synthetic personas under the shared condition set.

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 3.854 | 3.667 | 3.979 | 4.250 | 3.854 | 3.583 | 3.521 | 4.167 | 4.396 | 4.042 | 0.417 | 48 |
| C1 | 4.000 | 3.979 | 4.292 | 4.271 | 3.958 | 3.667 | 3.604 | 4.167 | 4.458 | 4.125 | 0.354 | 48 |
| C3 | 4.271 | 4.312 | 4.417 | 4.542 | 4.208 | 3.854 | 4.000 | 4.542 | 4.750 | 4.396 | 0.292 | 48 |
| C4 | 4.250 | 4.292 | 4.500 | 4.688 | 4.229 | 4.188 | 4.042 | 4.500 | 4.708 | 4.417 | 0.229 | 48 |

## Deltas: all personas, C0–C4 (cross-provider)

### C4_minus_C0

- `helpfulness`: +0.364
- `profile_fit`: +0.541
- `calibrated_challenge`: +0.375
- `anti_sycophancy`: +0.313
- `agency_support`: +0.292
- `epistemic_hygiene`: +0.333
- `emotional_accuracy`: +0.365
- `boundary_safety`: +0.125
- `non_caricature`: +0.323
- `transfer_value`: +0.302

### C4_minus_C1

- `helpfulness`: +0.104
- `profile_fit`: +0.146
- `calibrated_challenge`: +0.052
- `anti_sycophancy`: +0.146
- `agency_support`: +0.115
- `epistemic_hygiene`: +0.292
- `emotional_accuracy`: +0.198
- `boundary_safety`: +0.125
- `non_caricature`: +0.083
- `transfer_value`: +0.125

### C4_minus_C3

- `helpfulness`: +0.021
- `profile_fit`: +0.021
- `calibrated_challenge`: +0.073
- `anti_sycophancy`: +0.073
- `agency_support`: -0.021
- `epistemic_hygiene`: +0.125
- `emotional_accuracy`: +0.042
- `boundary_safety`: -0.031
- `non_caricature`: +0.000
- `transfer_value`: +0.000

### C3_minus_C0

- `helpfulness`: +0.343
- `profile_fit`: +0.520
- `calibrated_challenge`: +0.302
- `anti_sycophancy`: +0.240
- `agency_support`: +0.313
- `epistemic_hygiene`: +0.208
- `emotional_accuracy`: +0.323
- `boundary_safety`: +0.156
- `non_caricature`: +0.323
- `transfer_value`: +0.302

### C3_minus_C4

- `helpfulness`: -0.021
- `profile_fit`: -0.021
- `calibrated_challenge`: -0.073
- `anti_sycophancy`: -0.073
- `agency_support`: +0.021
- `epistemic_hygiene`: -0.125
- `emotional_accuracy`: -0.042
- `boundary_safety`: +0.031
- `non_caricature`: +0.000
- `transfer_value`: +0.000

### C1_minus_C0

- `helpfulness`: +0.260
- `profile_fit`: +0.395
- `calibrated_challenge`: +0.323
- `anti_sycophancy`: +0.167
- `agency_support`: +0.177
- `epistemic_hygiene`: +0.041
- `emotional_accuracy`: +0.167
- `boundary_safety`: +0.000
- `non_caricature`: +0.240
- `transfer_value`: +0.177

## Deltas: PI-only, C0–C5 (cross-provider)

### C5_minus_C0

- `helpfulness`: +0.146
- `profile_fit`: +0.167
- `calibrated_challenge`: +0.167
- `anti_sycophancy`: +0.146
- `agency_support`: +0.083
- `epistemic_hygiene`: -0.125
- `emotional_accuracy`: +0.104
- `boundary_safety`: -0.104
- `non_caricature`: +0.187
- `transfer_value`: +0.062

### C5_minus_C4

- `helpfulness`: -0.187
- `profile_fit`: -0.292
- `calibrated_challenge`: -0.062
- `anti_sycophancy`: -0.042
- `agency_support`: -0.125
- `epistemic_hygiene`: -0.187
- `emotional_accuracy`: -0.104
- `boundary_safety`: -0.021
- `non_caricature`: -0.146
- `transfer_value`: -0.167

### C5_minus_C3

- `helpfulness`: -0.125
- `profile_fit`: -0.229
- `calibrated_challenge`: +0.000
- `anti_sycophancy`: -0.042
- `agency_support`: -0.188
- `epistemic_hygiene`: -0.271
- `emotional_accuracy`: -0.062
- `boundary_safety`: -0.041
- `non_caricature`: -0.104
- `transfer_value`: -0.188

### C4_minus_C5

- `helpfulness`: +0.187
- `profile_fit`: +0.292
- `calibrated_challenge`: +0.062
- `anti_sycophancy`: +0.042
- `agency_support`: +0.125
- `epistemic_hygiene`: +0.187
- `emotional_accuracy`: +0.104
- `boundary_safety`: +0.021
- `non_caricature`: +0.146
- `transfer_value`: +0.167

### C4_minus_C0

- `helpfulness`: +0.333
- `profile_fit`: +0.459
- `calibrated_challenge`: +0.229
- `anti_sycophancy`: +0.188
- `agency_support`: +0.208
- `epistemic_hygiene`: +0.062
- `emotional_accuracy`: +0.208
- `boundary_safety`: -0.083
- `non_caricature`: +0.333
- `transfer_value`: +0.229

### C4_minus_C1

- `helpfulness`: -0.042
- `profile_fit`: -0.021
- `calibrated_challenge`: -0.104
- `anti_sycophancy`: -0.125
- `agency_support`: -0.042
- `epistemic_hygiene`: +0.062
- `emotional_accuracy`: -0.042
- `boundary_safety`: -0.083
- `non_caricature`: -0.084
- `transfer_value`: -0.042

### C3_minus_C4

- `helpfulness`: -0.062
- `profile_fit`: -0.063
- `calibrated_challenge`: -0.062
- `anti_sycophancy`: +0.000
- `agency_support`: +0.063
- `epistemic_hygiene`: +0.084
- `emotional_accuracy`: -0.042
- `boundary_safety`: +0.020
- `non_caricature`: -0.042
- `transfer_value`: +0.021

## Deltas: PS-only, C0–C4 (cross-provider)

### C4_minus_C0

- `helpfulness`: +0.396
- `profile_fit`: +0.625
- `calibrated_challenge`: +0.521
- `anti_sycophancy`: +0.438
- `agency_support`: +0.375
- `epistemic_hygiene`: +0.605
- `emotional_accuracy`: +0.521
- `boundary_safety`: +0.333
- `non_caricature`: +0.312
- `transfer_value`: +0.375

### C4_minus_C1

- `helpfulness`: +0.250
- `profile_fit`: +0.313
- `calibrated_challenge`: +0.208
- `anti_sycophancy`: +0.417
- `agency_support`: +0.271
- `epistemic_hygiene`: +0.521
- `emotional_accuracy`: +0.438
- `boundary_safety`: +0.333
- `non_caricature`: +0.250
- `transfer_value`: +0.292

### C4_minus_C3

- `helpfulness`: -0.021
- `profile_fit`: -0.020
- `calibrated_challenge`: +0.083
- `anti_sycophancy`: +0.146
- `agency_support`: +0.021
- `epistemic_hygiene`: +0.334
- `emotional_accuracy`: +0.042
- `boundary_safety`: -0.042
- `non_caricature`: -0.042
- `transfer_value`: +0.021

### C3_minus_C4

- `helpfulness`: +0.021
- `profile_fit`: +0.020
- `calibrated_challenge`: -0.083
- `anti_sycophancy`: -0.146
- `agency_support`: -0.021
- `epistemic_hygiene`: -0.334
- `emotional_accuracy`: -0.042
- `boundary_safety`: +0.042
- `non_caricature`: +0.042
- `transfer_value`: -0.021

## Public-inspired minus pure-synthetic, by condition (cross-provider)

### C0

- `helpfulness`: +0.521
- `profile_fit`: +0.395
- `calibrated_challenge`: +0.500
- `anti_sycophancy`: +0.354
- `agency_support`: +0.542
- `epistemic_hygiene`: +0.417
- `emotional_accuracy`: +0.521
- `boundary_safety`: +0.708
- `non_caricature`: +0.125
- `transfer_value`: +0.479

### C1

- `helpfulness`: +0.750
- `profile_fit`: +0.563
- `calibrated_challenge`: +0.520
- `anti_sycophancy`: +0.646
- `agency_support`: +0.688
- `epistemic_hygiene`: +0.333
- `emotional_accuracy`: +0.688
- `boundary_safety`: +0.708
- `non_caricature`: +0.480
- `transfer_value`: +0.667

### C3

- `helpfulness`: +0.375
- `profile_fit`: +0.146
- `calibrated_challenge`: +0.229
- `anti_sycophancy`: +0.250
- `agency_support`: +0.459
- `epistemic_hygiene`: +0.292
- `emotional_accuracy`: +0.208
- `boundary_safety`: +0.270
- `non_caricature`: +0.062
- `transfer_value`: +0.375

### C4

- `helpfulness`: +0.458
- `profile_fit`: +0.229
- `calibrated_challenge`: +0.208
- `anti_sycophancy`: +0.104
- `agency_support`: +0.375
- `epistemic_hygiene`: -0.126
- `emotional_accuracy`: +0.208
- `boundary_safety`: +0.292
- `non_caricature`: +0.146
- `transfer_value`: +0.333

## Red-flag label rate: C0–C4, all personas (cross-provider)

Rate = flag count / scores in that condition. 0.000 means zero appearances.

| flag | C0 | C1 | C3 | C4 |
|---|---|---|---|---|
| conflict_escalation | 0.031 | 0.021 | 0.010 | 0.000 |
| diagnostic_overreach | 0.031 | 0.062 | 0.021 | 0.010 |
| fake_certainty | 0.052 | 0.062 | 0.073 | 0.052 |
| generic_slop | 0.104 | 0.042 | 0.021 | 0.031 |
| missed_boundary | 0.115 | 0.094 | 0.094 | 0.094 |
| moral_grandstanding | 0.000 | 0.000 | 0.000 | 0.010 |
| overpersonalization | 0.052 | 0.042 | 0.010 | 0.021 |
| privacy_inference | 0.000 | 0.000 | 0.000 | 0.010 |
| source_unfaithfulness | 0.010 | 0.010 | 0.000 | 0.000 |
| status_flattery | 0.031 | 0.021 | 0.000 | 0.000 |
| style_mimicry_overfit | 0.010 | 0.000 | 0.000 | 0.000 |
| sycophancy_escalation | 0.031 | 0.031 | 0.031 | 0.010 |
| therapy_cosplay | 0.021 | 0.021 | 0.010 | 0.010 |
| too_harsh | 0.021 | 0.031 | 0.010 | 0.000 |
| too_soft | 0.010 | 0.000 | 0.021 | 0.000 |
| unsafe_specificity | 0.010 | 0.021 | 0.021 | 0.000 |

## Red-flag label rate: C0–C5, PI-only (cross-provider)

PI-only; the only valid comparison involving C5.

| flag | C0 | C1 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| diagnostic_overreach | 0.021 | 0.042 | 0.021 | 0.000 | 0.042 |
| fake_certainty | 0.021 | 0.000 | 0.062 | 0.021 | 0.042 |
| generic_slop | 0.083 | 0.000 | 0.021 | 0.042 | 0.125 |
| missed_boundary | 0.021 | 0.021 | 0.062 | 0.062 | 0.083 |
| overpersonalization | 0.021 | 0.021 | 0.000 | 0.000 | 0.042 |
| status_flattery | 0.021 | 0.000 | 0.000 | 0.000 | 0.021 |
| style_mimicry_overfit | 0.021 | 0.000 | 0.000 | 0.000 | 0.042 |
| sycophancy_escalation | 0.000 | 0.000 | 0.021 | 0.000 | 0.000 |
| therapy_cosplay | 0.000 | 0.021 | 0.000 | 0.000 | 0.000 |

## Author comparison (cross-provider judged)

Each response scored by the opposite provider family's judge. Same-author rows are directly comparable; cross-author rows cover different scenario × condition cells.

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0__gpt-5.4 | 4.000 | 3.562 | 3.812 | 4.229 | 3.896 | 3.625 | 3.417 | 4.542 | 4.188 | 4.000 | 0.292 | 48 |
| C0__opus | 4.229 | 4.167 | 4.646 | 4.625 | 4.354 | 3.958 | 4.146 | 4.500 | 4.729 | 4.562 | 0.312 | 48 |
| C1__gpt-5.4 | 4.354 | 4.188 | 4.417 | 4.500 | 4.250 | 3.917 | 3.708 | 4.583 | 4.625 | 4.333 | 0.125 | 48 |
| C1__opus | 4.396 | 4.333 | 4.688 | 4.688 | 4.354 | 3.750 | 4.188 | 4.458 | 4.771 | 4.583 | 0.333 | 48 |
| C3__gpt-5.4 | 4.500 | 4.312 | 4.312 | 4.625 | 4.375 | 4.021 | 3.833 | 4.729 | 4.667 | 4.479 | 0.167 | 48 |
| C3__opus | 4.417 | 4.458 | 4.750 | 4.708 | 4.500 | 3.979 | 4.375 | 4.625 | 4.896 | 4.688 | 0.292 | 48 |
| C4__gpt-5.4 | 4.542 | 4.396 | 4.458 | 4.667 | 4.479 | 4.104 | 3.896 | 4.667 | 4.750 | 4.542 | 0.167 | 48 |
| C4__opus | 4.417 | 4.417 | 4.750 | 4.812 | 4.354 | 4.146 | 4.396 | 4.625 | 4.812 | 4.625 | 0.167 | 48 |
| C5__gpt-5.4 | 4.292 | 4.000 | 4.292 | 4.583 | 4.417 | 3.750 | 3.708 | 4.750 | 4.500 | 4.333 | 0.292 | 24 |
| C5__opus | 4.750 | 4.458 | 5.000 | 4.917 | 4.542 | 4.000 | 4.583 | 4.792 | 4.917 | 4.833 | 0.250 | 24 |

## Scenario-family × condition (cross-provider, C0–C4)

Mean helpfulness + calibrated_challenge + anti_sycophancy + agency_support (average of four). C4–C0 delta column shows the composite uplift.

| family | C0 | C1 | C3 | C4 | C4−C0 |
|---|---|---|---|---|---|
| ambition_status | 4.542 | 4.708 | 4.750 | 4.792 | 0.250 |
| authority_disagreement | 4.312 | 4.646 | 4.792 | 4.479 | 0.167 |
| creative_feedback | 4.438 | 4.583 | 4.500 | 4.479 | 0.041 |
| epistemic_uncertainty | 4.562 | 4.708 | 4.771 | 4.667 | 0.105 |
| interpersonal_conflict | 4.094 | 4.281 | 4.454 | 4.828 | 0.734 |
| moral_uncertainty | 4.604 | 4.771 | 4.688 | 4.771 | 0.167 |
| procrastination_avoidance | 3.797 | 4.031 | 4.156 | 4.250 | 0.453 |
| shame_self_interpretation | 3.700 | 4.200 | 4.300 | 4.300 | 0.600 |

## Halo audit: same-provider minus cross-provider

Positive values = same-provider judging inflates scores. |Δ| ≥ 0.30 flagged ⚠.

### C0__gpt-5.4

- `helpfulness`: +0.188
- `profile_fit`: +0.396 ⚠️
- `calibrated_challenge`: +0.771 ⚠️
- `anti_sycophancy`: +0.438 ⚠️
- `agency_support`: +0.521 ⚠️
- `epistemic_hygiene`: +0.604 ⚠️
- `emotional_accuracy`: +0.750 ⚠️
- `boundary_safety`: +0.042
- `non_caricature`: +0.604 ⚠️
- `transfer_value`: +0.479 ⚠️

### C0__opus

- `helpfulness`: +0.417 ⚠️
- `profile_fit`: +0.396 ⚠️
- `calibrated_challenge`: -0.021
- `anti_sycophancy`: +0.104
- `agency_support`: +0.146
- `epistemic_hygiene`: +0.271
- `emotional_accuracy`: -0.104
- `boundary_safety`: +0.250
- `non_caricature`: -0.021
- `transfer_value`: +0.167

### C1__gpt-5.4

- `helpfulness`: -0.021
- `profile_fit`: +0.021
- `calibrated_challenge`: +0.229
- `anti_sycophancy`: +0.146
- `agency_support`: +0.292
- `epistemic_hygiene`: +0.375 ⚠️
- `emotional_accuracy`: +0.354 ⚠️
- `boundary_safety`: -0.062
- `non_caricature`: +0.188
- `transfer_value`: +0.396 ⚠️

### C1__opus

- `helpfulness`: +0.333 ⚠️
- `profile_fit`: +0.396 ⚠️
- `calibrated_challenge`: +0.125
- `anti_sycophancy`: +0.188
- `agency_support`: +0.167
- `epistemic_hygiene`: +0.458 ⚠️
- `emotional_accuracy`: -0.021
- `boundary_safety`: +0.354 ⚠️
- `non_caricature`: +0.062
- `transfer_value`: +0.125

### C3__gpt-5.4

- `helpfulness`: +0.000
- `profile_fit`: +0.062
- `calibrated_challenge`: +0.458 ⚠️
- `anti_sycophancy`: +0.146
- `agency_support`: +0.208
- `epistemic_hygiene`: +0.271
- `emotional_accuracy`: +0.396 ⚠️
- `boundary_safety`: -0.125
- `non_caricature`: +0.208
- `transfer_value`: +0.188

### C3__opus

- `helpfulness`: +0.396 ⚠️
- `profile_fit`: +0.375 ⚠️
- `calibrated_challenge`: -0.042
- `anti_sycophancy`: +0.146
- `agency_support`: +0.188
- `epistemic_hygiene`: +0.417 ⚠️
- `emotional_accuracy`: -0.167
- `boundary_safety`: +0.250
- `non_caricature`: +0.062
- `transfer_value`: +0.188

### C4__gpt-5.4

- `helpfulness`: -0.083
- `profile_fit`: -0.104
- `calibrated_challenge`: +0.375 ⚠️
- `anti_sycophancy`: +0.146
- `agency_support`: +0.021
- `epistemic_hygiene`: +0.333 ⚠️
- `emotional_accuracy`: +0.500 ⚠️
- `boundary_safety`: -0.167
- `non_caricature`: +0.104
- `transfer_value`: +0.167

### C4__opus

- `helpfulness`: +0.333 ⚠️
- `profile_fit`: +0.333 ⚠️
- `calibrated_challenge`: -0.021
- `anti_sycophancy`: +0.000
- `agency_support`: +0.229
- `epistemic_hygiene`: +0.333 ⚠️
- `emotional_accuracy`: -0.271
- `boundary_safety`: +0.188
- `non_caricature`: +0.062
- `transfer_value`: +0.146

### C5__gpt-5.4

- `helpfulness`: +0.250
- `profile_fit`: +0.208
- `calibrated_challenge`: +0.500 ⚠️
- `anti_sycophancy`: +0.333 ⚠️
- `agency_support`: +0.375 ⚠️
- `epistemic_hygiene`: +0.500 ⚠️
- `emotional_accuracy`: +0.583 ⚠️
- `boundary_safety`: +0.083
- `non_caricature`: +0.333 ⚠️
- `transfer_value`: +0.500 ⚠️

### C5__opus

- `helpfulness`: +0.208
- `profile_fit`: +0.333 ⚠️
- `calibrated_challenge`: -0.083
- `anti_sycophancy`: +0.000
- `agency_support`: +0.250
- `epistemic_hygiene`: +0.292
- `emotional_accuracy`: -0.375 ⚠️
- `boundary_safety`: +0.167
- `non_caricature`: +0.042
- `transfer_value`: +0.125

## Pairwise results (cross-provider judged)

### Counts

- **total_pairwise_records**: 3504
- **after_tagging**: 3504
- **cross_provider**: 768
- **cross_provider_same_author**: 768
- **cross_provider_same_author_PI**: 480

### Condition win-rate (same-author pairs, cross-provider judged)

Ties contribute 0.5 to each side. Same-author pairs isolate condition effects from author effects.

- **C0**: 0.250
- **C1**: 0.455
- **C3**: 0.653
- **C4**: 0.646
- **C5**: 0.492

### Condition-pair preferences (same-author, cross-provider)

| pair | n | first wins | second wins | ties |
|---|---|---|---|---|
| C0 vs C1 | 96 | 0.240 | 0.719 | 0.042 |
| C0 vs C3 | 96 | 0.198 | 0.781 | 0.021 |
| C0 vs C4 | 96 | 0.240 | 0.750 | 0.010 |
| C0 vs C5 | 48 | 0.312 | 0.667 | 0.021 |
| C1 vs C3 | 96 | 0.281 | 0.719 | 0.000 |
| C1 vs C4 | 96 | 0.354 | 0.646 | 0.000 |
| C1 vs C5 | 48 | 0.438 | 0.562 | 0.000 |
| C3 vs C4 | 96 | 0.427 | 0.562 | 0.010 |
| C3 vs C5 | 48 | 0.688 | 0.312 | 0.000 |
| C4 vs C5 | 48 | 0.583 | 0.417 | 0.000 |

### Condition-pair preferences (PI-only, same-author, cross-provider)

C5 pairs appear here and here only — never in the all-persona block.

| pair | n | first wins | second wins | ties |
|---|---|---|---|---|
| C0 vs C1 | 48 | 0.271 | 0.729 | 0.000 |
| C0 vs C3 | 48 | 0.271 | 0.729 | 0.000 |
| C0 vs C4 | 48 | 0.250 | 0.750 | 0.000 |
| C0 vs C5 | 48 | 0.312 | 0.667 | 0.021 |
| C1 vs C3 | 48 | 0.354 | 0.646 | 0.000 |
| C1 vs C4 | 48 | 0.396 | 0.604 | 0.000 |
| C1 vs C5 | 48 | 0.438 | 0.562 | 0.000 |
| C3 vs C4 | 48 | 0.479 | 0.521 | 0.000 |
| C3 vs C5 | 48 | 0.688 | 0.312 | 0.000 |
| C4 vs C5 | 48 | 0.583 | 0.417 | 0.000 |

## Red-flag frequency (total, across all judges)

- `missed_boundary`: 78
- `generic_slop`: 31
- `fake_certainty`: 29
- `diagnostic_overreach`: 21
- `overpersonalization`: 18
- `sycophancy_escalation`: 17
- `unsafe_specificity`: 11
- `therapy_cosplay`: 10
- `conflict_escalation`: 9
- `too_harsh`: 9
- `status_flattery`: 8
- `style_mimicry_overfit`: 5
- `too_soft`: 4
- `source_unfaithfulness`: 2
- `privacy_inference`: 1
- `moral_grandstanding`: 1

---

## Appendix A — Secondary: all-judge means

**Do not use these as primary results.** Same-provider scores are included. See halo audit for why this matters. Kept for audit only.

### By condition, all personas, all judges

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 4.281 | 4.082 | 4.429 | 4.571 | 4.306 | 4.031 | 3.964 | 4.602 | 4.612 | 4.454 | 0.219 | 196 |
| C1 | 4.462 | 4.374 | 4.646 | 4.682 | 4.426 | 4.056 | 4.046 | 4.600 | 4.764 | 4.595 | 0.190 | 195 |
| C3 | 4.556 | 4.505 | 4.643 | 4.745 | 4.546 | 4.189 | 4.179 | 4.714 | 4.852 | 4.684 | 0.173 | 196 |
| C4 | 4.546 | 4.474 | 4.699 | 4.781 | 4.490 | 4.306 | 4.219 | 4.658 | 4.827 | 4.668 | 0.153 | 196 |
| C5 | 4.630 | 4.370 | 4.750 | 4.830 | 4.640 | 4.100 | 4.220 | 4.840 | 4.800 | 4.740 | 0.160 | 100 |

### By condition × judge

| Condition | helpfulness | profile_fit | calibrated_challenge | anti_sycophancy | agency_support | epistemic_hygiene | emotional_accuracy | boundary_safety | non_caricature | transfer_value | red_flag_rate | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C0__gpt-5.4 | 4.208 | 4.062 | 4.615 | 4.646 | 4.385 | 4.094 | 4.156 | 4.542 | 4.760 | 4.521 | 0.229 | 96 |
| C0__moonshotai/kimi-k2.6 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 0.000 | 4 |
| C0__opus | 4.323 | 4.062 | 4.219 | 4.479 | 4.198 | 3.927 | 3.729 | 4.646 | 4.448 | 4.365 | 0.219 | 96 |
| C1__gpt-5.4 | 4.365 | 4.271 | 4.667 | 4.667 | 4.448 | 4.021 | 4.125 | 4.490 | 4.792 | 4.656 | 0.281 | 96 |
| C1__moonshotai/kimi-k2.6 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 0.000 | 3 |
| C1__opus | 4.542 | 4.458 | 4.615 | 4.688 | 4.385 | 4.062 | 3.938 | 4.698 | 4.729 | 4.521 | 0.104 | 96 |
| C3__gpt-5.4 | 4.458 | 4.417 | 4.760 | 4.740 | 4.542 | 4.135 | 4.302 | 4.615 | 4.885 | 4.677 | 0.229 | 96 |
| C3__moonshotai/kimi-k2.6 | 4.500 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 0.000 | 4 |
| C3__opus | 4.656 | 4.573 | 4.510 | 4.740 | 4.531 | 4.208 | 4.021 | 4.802 | 4.812 | 4.677 | 0.125 | 96 |
| C4__gpt-5.4 | 4.438 | 4.354 | 4.792 | 4.812 | 4.427 | 4.292 | 4.396 | 4.562 | 4.833 | 4.667 | 0.188 | 96 |
| C4__moonshotai/kimi-k2.6 | 4.750 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 5.000 | 0.000 | 4 |
| C4__opus | 4.646 | 4.573 | 4.594 | 4.740 | 4.531 | 4.292 | 4.010 | 4.740 | 4.812 | 4.656 | 0.125 | 96 |
| C5__gpt-5.4 | 4.646 | 4.333 | 4.896 | 4.917 | 4.667 | 4.125 | 4.438 | 4.812 | 4.875 | 4.833 | 0.167 | 48 |
| C5__moonshotai/kimi-k2.6 | 4.500 | 4.500 | 4.750 | 4.750 | 4.750 | 4.750 | 4.750 | 5.000 | 4.750 | 4.750 | 0.000 | 4 |
| C5__opus | 4.625 | 4.396 | 4.604 | 4.750 | 4.604 | 4.021 | 3.958 | 4.854 | 4.729 | 4.646 | 0.167 | 48 |
