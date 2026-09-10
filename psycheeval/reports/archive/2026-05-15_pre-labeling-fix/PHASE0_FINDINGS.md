# Phase 0 — Same-data robustness audits

**Status**: complete (12/12 tasks). All findings live in `metrics_2026-04-26_v02_hard_codex_only.json` and `psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md`.

**Test coverage**: 106 tests pass (+8 new from Phase 0).

---

## What's in the analyzer now (new blocks)

All under `metrics.pairwise.*` unless noted:

| Block key | Source task | Purpose |
|---|---|---|
| `counts.same_author` / `counts.cross_author` | 0.A | Honest record-count breakdown |
| `cross_author_leak_detection` | 0.A | Surfaces the 179 Opus-C5_CONTRACT leak |
| `cluster_bootstrap_ci_cross_provider_same_author` | 0.A | Stratified by judge-author provider |
| `cluster_bootstrap_ci_same_provider_same_author` | 0.A | (companion) |
| `cluster_bootstrap_scope_counts` | 0.A | Counts for the three scopes |
| `scalar_pairwise_reconciliation_same_author` | 0.B | Per-pair paired scalar deltas + sign agreement |
| `pairwise_by_judge_same_author` | 0.C | Per-judge breakdown of every pair |
| `pairwise_by_author_same_author` | 0.C | Per-author |
| `pairwise_by_persona_same_author` | 0.C | Per-PI/PS persona |
| `leave_one_judge_out_fragility` | 0.D | + flags: flips / attenuates_5pp / ci_widens_2x |
| `leave_one_author_out_fragility` | 0.D | (companion) |
| `leave_one_persona_out_fragility` | 0.D | (companion) |
| `leave_one_family_out_fragility` | 0.D | (companion) |
| `ab_side_audit_same_author` | 0.E | Per-condition slot occupancy + per-pair slot balance |
| `scenario_family_breakdowns_same_author` | 0.F | Now rendered as forest plot with strict + point reversals |
| `length_adjusted_summary_same_author` | 0.G | "Similar"-length-bucket headline vs full + vanish flag |
| `cross_judge_redflag_predictiveness_same_author` | 0.H | Non-tautological leave-out-judge flag predictor |
| `macro_vs_micro_aggregation_same_author` | 0.I | All five macro variants vs micro |
| `condition_discoverability` | 0.L | TF-IDF + logistic; output-text → condition |
| `missingness_balance_audit` | 0.K | Complete-case scalar + cell counts |
| `rubric_lexical_overlap` *(top-level)* | 0.J | Condition prompt × rubric anchor Jaccard |

Render in the autogen markdown is added for every block; full data lives in the JSON.

---

## Verified reviewer claims

| Claim | Phase | Verdict |
|---|---|---|
| Cross-provider "same-author" labeling mixes 179 cross-author records | 0.A | ✓ Verified, leak block surfaces |
| GPT-5.4 reverses C3 vs C5_CONTRACT (~0.57) | 0.C | ✓ Exact: 0.571 [0.465, 0.672] |
| Slalom Altar persona reverses C4 vs C5_CONTRACT | 0.C | ✓ 0.657 vs 0.19–0.48 for other 3 personas |
| C4 vs C5 is OpenAI-judge-only | 0.C | ✓ Opus has 0 records on this pair |
| C5_CONTRACT > C3 CI [0.354, 0.500] touches 0.5 | 0.A | ✓ Verified; further: vanishes under length-matching (0.B, 0.G) |
| Scenario-family heterogeneity (epistemic_uncertainty reverses) | 0.F | ✓ C3 vs C5_CONTRACT: 0.643 in epistemic, 0.556 in shame |
| Pairwise channel is "mostly a red-flag detector" | 0.H | ✗ Partly true within-judge, but cross-judge predictiveness ≠ 1.0 (0.65–0.88) — flags are a signal not the whole story |

---

## New findings surfaced by the audit pass

### Most consequential

1. **GPT-Pro's scalar-pairwise contradiction is real and concentrated** (0.B): C5_CONTRACT > C3 and C5_CONTRACT > C4 are flagged ⚠ — pairwise prefers C5_CONTRACT but scalar Δ_total ≈ 0 (−0.05 and −0.23 respectively). The C5_CONTRACT > C5 finding is NOT flagged (+3.057 scalar Δ aligned with 76.8% pairwise). This isolates the publishable claim cleanly.

2. **C3 vs C5_CONTRACT advantage is judge-fragile** (0.D): drop Opus → lo_win 0.428 → 0.494 (Δ +0.066). The Opus judge carries the advantage. Drop GPT-5.4 (which alone reverses it) and it strengthens to 0.367.

3. **C3 vs C5_CONTRACT vanishes under length matching** (0.G): full lo_win 0.428 → similar-length-bucket 0.449 [0.343, 0.559] — CI includes 0.5. Three independent paths (scalar reconciliation 0.B, Opus LOO 0.D, length-matching 0.G) converge: C5_CONTRACT > C3 is not a real effect.

4. **C3 vs C5_CONTRACT IS clearer under cross-provider judges only** (0.A): CI [0.238, 0.446] — clearly C5_CONTRACT-favoring. Same-provider judges dilute toward 0.500. This is the cross-cutting nuance: there is signal under cross-provider judging, but the all-judge view doesn't show it.

5. **Cross-provider C5_CONTRACT > C3** is the only stratified version of this pair where the CI clearly excludes 0.5 in C5_CONTRACT's favor. The same-provider and all-judge versions don't.

### Strengthens C5 vs C5_CONTRACT as the Tier 1 finding

6. **C5_CONTRACT > C5 is judge-unanimous** (0.C): GPT-5.4 0.71, GPT-5.5 0.89, Opus 0.70 all favor C5_CONTRACT.

7. **C5_CONTRACT > C5 survives all leave-one-out perturbations** (0.D): no judge / author / persona / family removal flips direction or attenuates >5pp.

8. **C5_CONTRACT > C5 is family-robust** (0.F): no family causes a reversal at point estimate or strict CI level.

9. **C5_CONTRACT > C5 cannot be a "judge recognizes treatment" artifact** (0.L): TF-IDF classifier has F1=0.000 for both C5 and C5_CONTRACT — text alone doesn't carry the distinction.

10. **C5_CONTRACT > C5 is reflected in scalar deltas** (0.B): Δ_total = +3.057 across 10 dims, sign-agreement 79.4% — both channels agree.

### Cleans up two structural issues for the report

11. **Every pair is structurally A/B imbalanced** (0.E): `slot_a_is_lo_share` is 1.000 for 8 of 10 pairs, ≥0.988 for the others. C5_CONTRACT is slot B 100% of the time. AB/BA rejudging required before any margin is fully trustworthy.

12. **C4 vs C4_shuffled is wildly judge-divided** (0.D): full lo_win 0.519 flips on either GPT judge LOO (0.438 / 0.600). Headline "structure does not significantly beat shuffled" is more accurately "GPT judges disagree by 16pp on this pair".

13. **C4 vs C5 vanishes under length matching** (0.G): full 0.637 → similar-bucket 0.522, CI [0.381, 0.659] straddles 0.5. The C4 > C5 headline is also partly a length effect.

### Clean negative results (strengthens robustness section)

14. **Macro and micro aggregations agree** (0.I): all five macro variants (judge, author, persona, family, cell) within 5pp of micro. Headlines are NOT artifacts of record-count imbalance.

15. **Rubric lexical-overlap doesn't explain C5_CONTRACT** (0.J): Jaccard overlap is uniformly low (0.047–0.073); C5_CONTRACT has *lower* overlap (0.063) than C3 (0.073) and C4 (0.069).

16. **Cross-judge red-flag predictiveness is real** (0.H): P(loser more flagged | asymmetric) = 0.65–0.88 across all 10 pairs; all CIs exclude 0.5. Red flags are a signal, not within-judge artifacts. C3 vs C5_CONTRACT has the lowest predictiveness (0.648) — consistent with it being the noisiest.

### Coverage / data-quality findings

17. **Only 67.5% of outputs were scored by all 3 judges** (0.K): 1,134 complete-case / 1,680 total. The pooled scalar means carry potential selection bias; curated report should add a complete-case scalar table.

18. **C4 vs C5_CONTRACT survives length matching** (0.G): full 0.400 → similar 0.375, CI [0.267, 0.497] still excludes 0.5. The C4 vs C5_CONTRACT pair is stronger than I expected — Tier 1.5 candidate (between robust C5 vs C5_CONTRACT and fragile C3 vs C5_CONTRACT).

---

## Implications for the v0.2 curated report

### Tier 1 (publish, robust across all 12 Phase-0 audits)

- **C5_CONTRACT > C5** (76.8% pairwise, +3.057 scalar Δ, judge-unanimous, LOO-robust, family-robust, classifier-undetectable)
- **C4 > C1_padded** (68.1% pairwise, +3.084 scalar Δ, length-matching survives)
- **C0 is dominated by all profile conditions** (86.6% C4-over-C0, etc.)
- **C4 vs C5_CONTRACT** (60.0% pairwise, scalar near-tie but pairwise CI [0.267, 0.497] excludes 0.5 under length matching) — **promote from Tier 2 to Tier 1.5** based on length-matching survival.

### Tier 2 (Tier 2 ⚠⚠⚠, soften language substantially)

- **C5_CONTRACT > C3** — pairwise headline straddles 0.5 in all-judge view, scalar is dead-tied, vanishes under length matching, carried by Opus judge alone. Direction is correct only under cross-provider stratification. Language: "directionally favors C5_CONTRACT; not robust to length matching or scalar reconciliation; the effect is concentrated in Opus judging and in non-epistemic, non-shame scenario families."
- **C4 > C5** — OpenAI-judge-only (Opus n=0); vanishes under length matching.
- **C4 vs C4_shuffled** — full direction is judge-arbitrary; report as "no significant difference at all-judge pooled level; individual judges disagree by ±8pp."

### Strike

- "v0.1 PAE confound is empirically resolved in favor of absence of contract as dominant driver"
- Unqualified "tri-model cross-provider" language for non-C5_CONTRACT pairs
- "C5_CONTRACT outperforms both C3 and C4" — replace with split (one Tier 1.5, one Tier 2)

### Add as new findings

- The **A/B side imbalance** (all 10 pairs, C5_CONTRACT 100% slot B) as a methodology limitation requiring AB/BA rejudging before publication of any non-Tier-1 claim.
- The **scalar-pairwise reconciliation** as a primary methodology finding (the holistic-vs-rubric channels can diverge).
- The **stratified cross-provider C3 vs C5_CONTRACT** as the strongest version of that pair's evidence.
- The **complete-case scalar table** as a robustness check.

### Phase 1 (next, requires Opus quota): AB/BA counterbalanced rejudging

The single most decisive next experiment per all three reviewers. 200–800 Opus draws on the existing 1,680 outputs with swapped slot order. Gates whether the Tier 2 claims survive any reframing.
