# Cross-Model Personality Evaluation: Complete Results (v3)

**Date:** 2026-03-29
**Supersedes:** results-report-v2.md (2026-03-25, pre-replication)

## Executive Summary

78+ evaluation runs across factorial corpus, replicated 2×2 generation confound, and 6 follow-up experiments reveal four headline findings:

1. **Evaluator dominance is ~7×, not 3×.** Under replication, the evaluator effect (12.4 pts) dwarfs the generator effect (1.8 pts, formally negligible under equivalence testing).
2. **Full-context polarization is a text-volume effect, not temporal anchoring.** Shuffling message order reproduces the same bias. A debiased prompt eliminates it for SMS but NOT for academic or mixed registers — the fix is register-specific.
3. **Planning-dominance thesis holds cross-model.** Both Opus and GPT rank the old pipeline as worst and all 1M-planned conditions as substantially better. The fine-grained secondary rankings (filtered vs long vs 1m) remain evaluator-specific.
4. **O stability is an aggregation artifact.** O5 Ideas at ceiling (range 7.5) masks O4 Actions varying by 28.2 points across registers.

## Data Inventory

| Dataset | Total Runs | Models |
|---------|-----------|--------|
| Factorial corpus (chunked) | 30 | Opus + GPT |
| Factorial corpus (full-context) | 9 | Opus |
| E1 anchoring ablation | 12 | Opus |
| E5 debiased prompt (SMS) | 3 | Opus |
| R2 debiased prompt (academic, mixed) | 3+ | Opus |
| R5 temporal windows (half, three-quarter) | 4+ | Opus |
| Replicated 2×2 generation confound | 11 | Opus + GPT |
| R1 GPT narrative evals (all 4 conditions) | 12 | GPT |
| R6 narrative debiased eval | 3 | Opus |
| R9 differential personality replication | 3 | Opus |
| **Total** | **86+** | |

## Finding 1: Evaluator Dominance (7×)

### Replicated 2×2 (2-3 runs per cell)

| Generator | Evaluator | N | E | O | A | C | |Δ| vs Psyche |
|:---------:|:---------:|:---:|:---:|:---:|:---:|:---:|:---:|
| Opus | Opus | 75.7 | 24.5 | 89.5 | 43.0 | 54.8 | — |
| Opus | GPT | 81.2 | 41.4 | 86.7 | 59.0 | 79.3 | — |
| GPT | Opus | 75.1 | 24.6 | 90.2 | 45.1 | 56.3 | — |
| GPT | GPT | 78.9 | 39.7 | 85.9 | 62.3 | 74.1 | — |

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

- **Generator effect:** 1.8 pts mean (ROPE test: inside ±3-pt equivalence bound → NEGLIGIBLE)
- **Evaluator effect:** 12.4 pts mean
- **Ratio:** 6.8×
- **Critical correction:** Original single-run Opus→Opus had A=55.7, C=69.0 (outliers). Replicated: A=43.0, C=54.8. The "large A/C generator effects" reported in v2 were noise.

### Variance Decomposition (30 chunked corpus runs)

| Domain | η² Evaluator | η² Register | η² Residual | GPT−Opus bias |
|--------|:-----------:|:-----------:|:-----------:|:------------:|
| N | 0.156 | 0.836 | 0.008 | +8.3 |
| E | 0.773 | 0.188 | 0.039 | +15.3 |
| O | 0.096 | 0.780 | 0.124 | -2.8 |
| A | 0.334 | 0.603 | 0.064 | +10.6 |
| C | 0.398 | 0.600 | 0.002 | +19.2 |

Evaluator is the dominant source of variance for E (77%). Register dominates for N (84%) and O (78%). C and A are split.

### Evaluator Calibration

Leave-one-register-out calibration: mean held-out RMSE = 3.6 pts → CALIBRATABLE. Per-domain additive bias correction from 4 training registers predicts the 5th register within 3.6 pts. However, bias-corrected GPT rankings still don't match Opus rankings for narrative conditions — there are interaction effects beyond additive bias.

## Finding 2: Full-Context Polarization Mechanism

### Anchoring Ablation (personal-sms, Opus)

| Condition | N | E | O | A | C | |Δ| |
|-----------|:---:|:---:|:---:|:---:|:---:|:---:|
| Chunked | 53.1 | 30.0 | 87.8 | 38.3 | 39.6 | — |
| FC ordered | 60.0 | 26.0 | 91.3 | 37.3 | 43.0 | — |
| FC shuffled | 62.0 | 26.0 | 92.0 | 38.0 | 37.5 | — |
| FC debiased | 53.3 | 29.0 | 86.7 | 39.3 | 39.3 | — |

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

**Shuffled ≈ ordered:** Text volume drives the effect, not temporal anchoring.
**Debiased ≈ chunked (SMS only):** Prompt instruction eliminates polarization for SMS.

### Debiased Prompt Generalization (R2)

| Register | Chunked |Δ| | FC |Δ| | FC debiased |Δ| | Mitigation? |
|----------|:-------:|:----:|:---------------:|:-----------:|
| SMS | — | — | — | YES |
| Academic | — | — | — | **NO** |
| Mixed | — | — | — | NO |

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

The debiased prompt is SMS-specific. Academic full-context pathology involves a deeper failure mode than attentional anchoring — likely related to how 150K words of formal writing overwhelms the personality inference prompt.

### Temporal Windows (R5)

| Slice | N | E | A | |Δ| |
|-------|:---:|:---:|:---:|:---:|
| First 25% | 56.8 | 27.8 | 37.8 | — |
| First 50% | 49.3 | 29.4 | 40.0 | — |
| First 75% | 52.8 | 30.1 | 38.9 | — |
| Full chunked | 53.1 | 30.0 | 38.3 | — |
| Last 25% | 47.6 | 36.4 | 43.2 | — |

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

Scores vary across temporal slices of the same corpus: the last quarter reads highest on E (36.4, +6.4 vs full) and A (43.2, +4.9), the first quarter highest on N (56.8), the middle lowest (N=49.3). _Withheld: the earlier draft read these slice differences as genuine change in the subject's life and relationship over time. That is a biographical inference about a private individual rather than a methodology result, and it is not published here. What the numbers support is that temporal slicing of a corpus moves the inferred profile — which is the finding this section is for._

## Finding 3: Cross-Model Narrative Rankings (R1)

| Condition | Opus |Δ| | GPT |Δ| |
|-----------|:-------:|:------:|
| long | — | — |
| filtered | — | — |
| 1m | — | — |
| old | — | — |

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

Opus ranking: filtered < long = 1m < old
GPT ranking: long < filtered < 1m < old

**Both agree:** old is worst; all 1M-planned conditions are substantially better.
**Both disagree:** on filtered vs long vs 1m ordering.

The planning-dominance thesis (old >> new) holds cross-model. The secondary rankings (output length, writing context) remain evaluator-specific — exactly as the posts hedge.

## Finding 4: Facet-Level Structure

### Evaluator Bias Concentrates in Specific Subfacets

| Facet | GPT−Opus bias | Domain |
|-------|:------------:|:------:|
| C6 Deliberation | +25.3 | C |
| C2 Order | +23.5 | C |
| E1 Warmth | +18.6 | E |
| E6 Positive Emotions | +16.8 | E |
| A6 Tender-mindedness | +15.6 | A |
| O5 Ideas | +0.2 | O |

GPT reads all text as more deliberate, orderly, warm, and emotionally positive. O5 Ideas is dead flat — the strongest cross-model agreement in the entire dataset.

### O Stability Is an Aggregation Artifact

| O Facet | Range across registers |
|---------|:---------------------:|
| O4 Actions | 28.2 |
| O2 Aesthetics | 15.4 |
| O1 Fantasy | 14.4 |
| O3 Feelings | 11.7 |
| O6 Values | 9.1 |
| O5 Ideas | 7.5 |

Domain-level O stability (range 13.9) is driven by O5 Ideas at ceiling (87-95 everywhere). O4 Actions varies 28.2 points — comparable to N and C ranges.

### Cross-Register Transportability

Mean pairwise profile correlation r = 0.861 (HIGH). The same latent personality shows through all registers despite large surface-level differences. Register effects are offsets on a stable core, not different personalities.

## Finding 5: N Genre Effect

SMS corpus N = 53.1. Narrative N (replicated) = 75.7. Genre uplift = +22.6 points.
Posts cited "+13 to +20" — **needs correction to "+18 to +24"**.

## Corrections to Published Posts

| Claim | Old (v2) | Corrected (v3) |
|-------|----------|----------------|
| Evaluator/generator ratio | 3× | ~7× |
| Evaluator effect | 5.6 pts | 12.4 pts |
| Generator effect | 1.9 pts (non-zero) | 1.8 pts (NEGLIGIBLE under ROPE) |
| 2×2 cells | 10.7/16.3/8.8/14.4 | 8.9/15.5/8.8/14.1 |
| GPT-gen scores closest | Yes (8.8 vs 10.7) | No (8.8 vs 8.9, indistinguishable) |
| N genre range | +13 to +20 | +18 to +24 |
| Debiased prompt claim | "eliminates FC polarization" | "eliminates FC polarization FOR SMS; does not generalize to academic or mixed registers" |

## Finding 6: Debiased Prompt Does Not Transfer to Narrative Evaluation (R6)

Evaluating the "long" narrative with the debiased prompt produced |Δ|=8.2 vs 8.4 without it — no meaningful difference. Narratives are curated literary text without the extreme salience variation that drives corpus full-context polarization. The debiased prompt solves a corpus-evaluation problem, not a narrative-evaluation problem.

## Finding 7: Differential Personality Signal Is Stable Under Replication (R9)

The interlocutor perspective (arc 2) was re-evaluated 3 times. The result that matters
methodologically is the *stability*: both replicated domains moved by less than 3 points across
re-evaluations, so the differential signal is not an artifact of a single run.

_Withheld: the interlocutor rows measure another private individual from the subject's
correspondence. No owner ruling reaches other people's derived personal data (DECISIONS
`SP-owner-psychometrics-public`, 2026-08-23, explicit carve-out), so their values, the
replication deltas that recover them, and the interlocutor-vs-subject gap are not published
here. This matches the treatment of the same rows in `analysis/BACKLOG.md`._

The model produces a measurably different profile from a different narrator's perspective rather
than echoing a default. Nothing here should be read as a validated measurement of another
person's personality: these are LLM estimates of narratives written from those perspectives.

## Finding 8: Generation Variance Is Small (R4)

A second 1M narrative was generated from identical pipeline inputs (same message archive, discovery artifacts, outline, voice profile) using `claude -p --model opus`, writing chapters sequentially with full 640K-token context per chapter. The second narrative (25,132 words, 256 citations) was evaluated with 4 Opus runs.

| Metric | Original 1M | R4 (second gen) |
|--------|:-----------:|:---------------:|
| Mean |Δ| vs Opus ref | 3.9 [3.4, 4.4] | 3.9 [3.3, 4.4] |
| Mean |Δ| vs Psyche | — | — |
| N | 55.0 | 58.5 (+3.5) |
| E | 31.0 | 26.9 (-4.1) |
| O | 91.0 | 92.0 (+1.0) |
| A | 40.7 | 37.2 (-3.5) |
| C | 67.7 | 55.2 (-12.5) |

The R4 mean |Δ| (3.9) is identical to the original and squarely inside its CI [3.4, 4.4]. Four of five domains shift by less than 4.1 points. Conscientiousness shows a larger shift (-12.5) but this does not affect the aggregate metric. The pipeline produces stable personality signal: **the CIs reported in the posts are approximately valid for total uncertainty (generation + evaluation combined).**

Generation variance across domains averages 4.9 points, while within-run evaluator variance averages 0.9 points. Generation variance is the larger source of uncertainty but does not change the pipeline's aggregate fidelity score.

## Future Work
- **F1-F4:** Cross-subject validation, conformity-anxiety disambiguation, human-rated anchors (require external data)
- **GPT full-context ablation** — test if FC polarization is evaluator-general
- **Corpus-level values analysis** — extend beyond Big Five to Schwartz Values

## Data Files

| File | Content |
|------|---------|
| `variance-decomposition.json` | A1 ANOVA + ROPE test |
| `interaction-analysis.json` | A2 evaluator×register + A3 transportability |
| `calibration-analysis.json` | A4 leave-one-out + A7 corrected rankings |
| `replicated-2x2-cis.json` | A5 confidence intervals |
| `register-matched-evaluation.json` | A6 SMS-reference |Δ| |
| `facet-analysis.json` | E4 + A8 facet decomposition |
| `experiment5-followup-ablations.json` | E1-E6 + R2/R5 results |
| `cross-model-factorial-results.json` | All 39 corpus means |
