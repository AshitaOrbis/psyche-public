# Methodology Supplement: Cross-Model Validation and Per-Domain Analysis

**Date:** 2026-03-19
**Posts affected:** 030-what-ai-learns-about-you, 038-where-to-spend-your-context-window
**Prompted by:** Publication review Round 2 identified genuine methodological gaps

## Summary

Three experiments address methodological concerns raised during publication review:

1. **Cross-model ground truth** — GPT-5.4 as independent evaluator
2. **Per-domain deltas** — Disaggregated Big Five analysis against merged profile
3. **Additional runs for CIs** — Confidence intervals for filtered/long conditions (pending)

## Experiment 1: Cross-Model Ground Truth

### Design

The original experiments used Opus to both generate the corpus ground truth AND evaluate narratives against it. This creates a potential confound: we may be measuring Opus self-consistency rather than narrative quality.

**Fix:** Run GPT-5.4 on the same corpus to produce an independent ground truth, then compare narrative evaluations against it.

### Ground Truth Comparison

| Domain | Opus GT | GPT-5.4 GT | Merged Profile | Δ (GPT-Opus) |
|--------|---------|------------|----------------|--------------|
| N | 51.1 | 69.0 | — | +17.9 |
| E | 28.3 | 36.0 | — | +7.7 |
| O | 88.6 | 91.0 | — | +2.4 |
| A | 36.4 | 52.0 | — | +15.6 |
| C | 61.4 | 55.0 | — | -6.4 |

_The merged-profile column is withheld: it is the subject's private ground-truth
vector. The GT-difference column compares the two model-derived ground truths and
is unaffected._

Mean |GT difference|: 10.0 points

**Key observations:**
- O agrees closely (+2.4), consistent with the strongest signal in the corpus
- N and A show large disagreements (17.9 and 15.6 points)
- GPT-5.4's GT is closer to the merged profile for A and C; Opus's is closer for N
  and E (the merged-profile values are withheld — private subject data)

### Cross-Model Evaluation Rankings

**Opus evals vs Opus GT (self-consistent):**

| Condition | N | E | O | A | C | Mean |Δ| |
|-----------|---|---|---|---|---|---------|
| old | +23.9 | -3.6 | +2.7 | +19.3 | +7.6 | **11.4** |
| 1m | +3.9 | +2.7 | +2.4 | +4.3 | +6.3 | **3.9** |
| filtered | +3.7 | -0.7 | +2.8 | +1.8 | +0.2 | **1.8** |
| long | -1.1 | -2.8 | +1.9 | +0.4 | -2.9 | **1.8** |

Ranking: filtered = long (1.8) > 1m (3.9) > old (11.4)

**GPT evals vs GPT GT (self-consistent) — CORRECTED 2026-03-19:**

*GPT evaluations rerun through the same pipeline as Opus (system prompt included, full chunking, all chunks succeeded). The ranking order is unchanged from the original ad-hoc evaluations, confirming the inversion is a genuine model difference, not a prompting artifact.*

| Condition | N | E | O | A | C | Mean |Δ| |
|-----------|---|---|---|---|---|---------|
| old | +13.7 | +6.0 | -2.3 | +9.3 | +22.3 | **10.7** |
| 1m | -9.7 | +18.7 | -1.0 | +7.0 | +28.3 | **12.9** |
| filtered | -13.6 | +10.8 | -4.6 | +6.6 | +27.0 | **12.5** |
| long | -15.0 | +8.5 | -4.8 | +6.5 | +23.0 | **11.6** |

Ranking: old (10.7) > long (11.6) > filtered (12.5) > 1m (12.9)

### Critical Finding: Ranking Inversion

The rankings **disagree** between evaluators:
- Opus: filtered/long best, old worst (supports "planning outperforms generation")
- GPT: old best, 1m worst (inverts the thesis)

**Root cause analysis:** GPT-5.4 shows a systematic C inflation of +22-28 points across ALL narrative conditions relative to its own corpus GT. This single domain dominates the mean |Δ| metric and flattens meaningful between-condition differences. The C inflation likely reflects a difference in how GPT-5.4 interprets narrative text vs corpus text for Conscientiousness signals. This finding persists after correcting the GPT evaluation methodology (original evaluations used ad-hoc prompting without the system prompt; corrected evaluations use the identical pipeline as Opus).

**Implication for the post:** The "planning outperforms generation" finding is evaluator-dependent. It holds under Opus self-evaluation but not under GPT-5.4 self-evaluation. The post must:
1. Report this disagreement transparently
2. Qualify the finding as "Opus-evaluated" rather than universal
3. Note that O (the most agreed-upon domain between evaluators) shows minimal condition differences, meaning the strongest personality signal transfers regardless of context strategy

## Experiment 2: Per-Domain Deltas Against Merged Profile

### Design

Mean |Δ| can hide dimension-level failures. This experiment disaggregates into individual N, E, O, A, C deltas for all conditions against the merged profile (the most comprehensive ground truth, incorporating 39 instruments + interview).

### Results: Opus Evaluations vs Merged Profile

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

### Results: GPT Evaluations vs Merged Profile (CORRECTED)

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

### Key Findings

1. **O is consistently +7 to +11 points across ALL conditions and BOTH evaluators.** The narrative generation process systematically inflates apparent Openness relative to the merged profile. This is likely because narratives are inherently "open" text (creative, exploratory), introducing a structural bias.

2. **The "old" condition's N inflation is the clearest signal.** Both evaluators agree the old narrative dramatically overshoots Neuroticism. This is the most robust finding — it holds across evaluators and is the largest single-domain effect.

3. **A shows an evaluator-dependent pattern.** Opus eval: old is close to the merged GT, but 1m/filtered/long undershoot it; GPT eval: all conditions overshoot modestly. (Magnitudes withheld — they are deltas against private subject data.) This suggests Opus and GPT disagree specifically on Agreeableness interpretation in narratives.

4. **C is the most evaluator-dependent domain.** GPT-5.4 systematically scores narratives far higher on Conscientiousness than Opus does, regardless of condition. (Per-domain magnitudes against the merged profile are withheld — private subject data.)

5. **Against the merged profile, condition ranking partially aligns.** GPT ranking vs merged profile (long < filtered < 1m < old; magnitudes withheld) **agrees** with the Opus ranking direction, unlike the GPT-vs-GPT-GT ranking which inverts. This suggests the ranking inversion is specific to the GPT GT benchmark, not to GPT's narrative evaluations per se.

## Experiment 3: Additional Runs for Filtered/Long CIs

**Status:** Partially complete. One additional run completed for filtered condition.

The data so far:
- Old: 4 runs, mean |Δ| = 11.4 (vs Opus GT), 95% CI available
- 1M: 4 runs, mean |Δ| = 3.9 (vs Opus GT), 95% CI available
- Filtered: 2 runs, mean |Δ| = 1.8 and 2.7
- Long: 1 run, mean |Δ| = 1.8 (no CI)

### Filtered Run 2 Results

| Domain | Run 1 | Run 2 | Δ |
|--------|-------|-------|---|
| N | 54.8 | 54.8 | 0.0 |
| E | 27.6 | 26.4 | -1.2 |
| O | 91.4 | 90.8 | -0.6 |
| A | 38.2 | 38.0 | -0.2 |
| C | 61.6 | 57.4 | -4.2 |
| Mean |Δ| | 1.8 | 2.7 | +0.9 |

**Key observation:** The variance concentrates almost entirely in C (4.2-point swing), while N is perfectly stable. This is consistent with the cross-model finding that C is the most evaluator-sensitive domain. The 1.8 from Run 1 was on the favorable end of the distribution; the true expected mean |Δ| for filtered is likely ~2.2, which is still well below the 1M pipeline's 3.9 and dramatically below the old pipeline's 11.4.

Remaining: 2 more filtered runs and 3 long runs needed for full CIs. Script at `run_additional_evals.sh`.

## Implications for Posts 030 and 038

All items below have been implemented in both posts as of Round 3 publication review (2026-03-19).

### Implemented (Round 3)

1. **Cross-model evaluation results reported** — ranking inversion disclosed, C inflation root cause explained
2. **Per-domain delta tables added** — both Opus-GT and merged-GT disaggregation in post 030
3. **O inflation flagged** — qualified as "against the merged profile" (not "both evaluators")
4. **N signal reframed** — improvement story centers on N correction as evaluator-robust finding
5. **GPT-5.4 corpus GT added** — three-benchmark comparison (Opus corpus, GPT corpus, merged profile)
6. **Planning-vs-generation claim qualified** — "evaluator-dependent," "suggestive rather than established"
7. **Terminology cleaned** — "reference profile" for Opus corpus inference, "ground truth" reserved for merged profile
8. **CI methodology clarified** — "four re-evaluations of the same text, bounding evaluator scoring variance"
9. **"8 of 10" reframed** — EVOLVED now distinguished from CONSISTENT
10. **Digital exhaust thesis softened** — N=1 and entanglement caveats re-inserted
11. **Filtered Run 2 data incorporated** — 1.8 acknowledged as optimistic, second run 2.7

### Implemented (Round 4)

12. **A "reduces" reframed** — acknowledged A reverses direction against merged profile (overcorrection, not reduction)
13. **"Ground truth" → "reference profile"** — comprehensive cleanup across both posts for model-derived profiles
14. **038 intro thesis qualified** — "under certain evaluation conditions" and "Under Opus self-evaluation"
15. **Word count mismatch fixed** — Long condition correctly described as ~28,000 (exceeding old's 24,000) in both posts
16. **Single-run → updated** — filtered now correctly described as 2-run in both posts
17. **"Statistical significance" → "non-overlapping evaluator CIs"** — clearer about what the intervals measure
18. **"Old and new" disambiguated** — "best-performing new condition (filtered)" instead of ambiguous "new"
19. **Ablation etymology trimmed** — Latin derivation removed

### Remaining

- CIs for filtered/long (2 more filtered runs + 3 long runs needed)
- E CI bounds not yet provided (claim removed from post 038)

### Implemented (CI Revision)

20. **All conditions now have 4 runs with CIs** — filtered 2.4 ± 0.4, long 1.7 ± 0.3
21. **"Writing context adds noise" hypothesis REFUTED** — long (full context) outperforms filtered (restricted)
22. **Three-factor interpretation replaces binary thesis** — planning context (dominant) > output length (secondary) > writing context (small positive)
23. **Post 038 intro, "What the Ablation Reveals", generalization, and conclusion fully rewritten** to reflect CI data
24. **Post 030 "Uncomfortable Implication" → "What the Ablation Reveals"** — rewritten for nuanced interpretation
25. **All tables updated** with CI-backed numbers (2.4 and 1.7 replace 1.8)
26. **Description of 038 updated** — no longer claims "matters for planning but not for generation"

### Convergence Assessment

All evaluation runs complete. Posts revised to reflect CI-backed data which substantially changed the interpretation. The strong "planning > generation" thesis from single-run data is replaced with a three-factor model. Ready for final publication review.

## Data Files

| File | Contents |
|------|----------|
| `experiment1-cross-model-gt.json` | GPT-5.4 corpus GT scores and ranking comparison |
| `experiment2-per-domain-deltas.json` | All per-domain deltas for all conditions × evaluators × GTs |
| `corpus-sample-for-gpt.txt` | The corpus sample sent to GPT-5.4 |
| `additional-runs/` | Additional evaluation run results (when complete) |
| `run_additional_evals.sh` | Script for Experiment 3 additional runs |
