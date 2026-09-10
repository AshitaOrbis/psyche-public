# Cross-Model Personality Evaluation: Factorial Results

**Date:** 2026-03-25
**Supersedes:** results-report.md (2026-03-19, pre-rework)

## Executive Summary

39 corpus evaluation runs (24 Opus, 15 GPT) across 5 source registers, plus a 2×2 narrative generation experiment, reveal that **evaluator model bias dominates all other factors** in LLM-based personality inference. GPT-5.4 systematically inflates E (+15.3), C (+19.2), A (+10.6), and N (+8.3) relative to Opus 4.6 across every register. The generation confound (who wrote the narrative) accounts for <2 points of mean delta, while the evaluation confound (who reads it) accounts for 5-8 points.

## Design

### Corpus Evaluation (39 runs)

**Axis 1 — Cross-model (chunked):** 5 sources × 2 models × 3 runs = 30 runs
**Axis 2 — Context effect (Opus only):** 3 sources × full-context × 3 runs = 9 runs

| Source | Samples | Words | Register |
|--------|---------|-------|----------|
| Personal SMS | 7,029 | 134K | Private text messages |
| Academic | 114 | 151K | Formal essays and papers |
| Messenger | 32,461 | 413K | Casual Facebook conversations |
| AI Conversations | 7,949 | 508K | Analytical (ChatGPT + Claude) |
| Mixed (stratified) | ~4,300 | ~100K | Proportional from all 4 sources |

### Narrative 2×2 (4 conditions)

{Opus-generated, GPT-generated} × {Opus-evaluated, GPT-evaluated} on the arc 2 first-person narrative, using identical pipeline inputs (outlines, briefs, voice profiles, canonical facts).

## Results

### Finding 1: GPT Systematically Inflates E and C

Across all 5 source registers, GPT-5.4 scores higher than Opus on every domain except O:

| Bias (GPT − Opus) | N | E | O | A | C |
|--------------------|:---:|:---:|:---:|:---:|:---:|
| Personal SMS | +8.6 | +22.8 | -1.3 | +19.2 | +22.8 |
| Academic | +4.1 | +9.6 | -1.5 | +7.6 | +17.4 |
| Messenger | +11.0 | +13.9 | -2.5 | +4.7 | +20.4 |
| AI Conversations | +7.7 | +15.1 | -4.7 | +11.1 | +17.3 |
| Mixed | +10.3 | +15.1 | -4.0 | +10.3 | +18.3 |
| **Mean bias** | **+8.3** | **+15.3** | **-2.8** | **+10.6** | **+19.2** |

O is the only domain where models agree (mean bias -2.8). This is consistent with O being the strongest corpus signal and the most robustly inferred trait in the literature.

The E inflation is particularly striking on Personal SMS (+22.8) — GPT reads personal texting as extraverted behavior, while Opus does not. This may reflect different training-derived associations between conversational warmth and Extraversion.

The C inflation is the most consistent bias (+17-23 across all registers). GPT appears to interpret structured, coherent writing as evidence of Conscientiousness regardless of content.

### Finding 2: Register Effects Are Real and Large

Within each model, personality scores vary substantially by source:

**Opus (chunked):**

| Source | N | E | O | A | C | |Δ| vs Psyche |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| Personal SMS | 53.1 | 30.0 | 87.8 | 38.3 | 39.6 | — |
| Academic | 46.8 | 33.3 | 78.9 | 42.5 | 57.7 | — |
| Messenger | 66.2 | 24.8 | 85.9 | 32.5 | 30.9 | — |
| AI Conv | 40.0 | 33.6 | 83.8 | 35.8 | 63.4 | — |
| Mixed | 54.9 | 32.2 | 83.5 | 36.4 | 37.7 | — |
| **Psyche GT** | — | — | — | — | — | — |

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

Key register effects:
- **Messenger N inflation** (66.2 vs 53.1 SMS): Casual Facebook conversations from an earlier era read as more neurotic. _Withheld: the earlier draft read this register difference as evidence of a genuinely more anxious period in the subject's life. That is a biographical inference about a private individual rather than a register effect, and it is not published here._
- **AI Conv low N** (40.0): Analytical conversations with AI present a calmer, more regulated persona
- **AI Conv high C** (63.4): Structured AI prompting reads as conscientious
- **SMS low C** (39.6): Texting style — terse, fragmented — reads as low conscientiousness even when the content is not

These are genuine register/context effects, not measurement error. The same person presents differently across communication contexts. The Psyche merged profile (from self-report instruments) should not be treated as universal ground truth for every register.

### Finding 3: Full-Context Hurts More Than It Helps (Opus)

| Source | Chunked |Δ| | Full-ctx |Δ| | Difference |
|--------|:---:|:---:|:---:|
| Personal SMS | — | — | +0.8 (worse) |
| Academic | — | — | +10.0 (much worse) |
| Mixed | — | — | +3.7 (worse) |

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._ The difference column is a difference of two withheld
quantities and carries no information about the profile itself.

Full-context is worse on all three sources. The academic result is dramatic — N jumps from 47 to 72, E drops from 33 to 14, C drops from 58 to 38. With the entire academic corpus visible, Opus appears to over-weight emotional/introspective passages and under-weight the structured, competent writing that chunked sampling captures proportionally.

**Interpretation:** Chunking provides natural diversification of the text signal. Full-context allows the model to develop a singular narrative interpretation that may anchor on salient passages rather than sampling broadly. For personality inference, chunked evaluation is more robust than full-context.

### Finding 4: Evaluator Dominates Generator in the 2×2

| Generator | Evaluator | N | E | O | A | C | |Δ| vs Psyche |
|:---------:|:---------:|:---:|:---:|:---:|:---:|:---:|:---:|
| Opus | Opus | 75.0 | 24.7 | 91.3 | 55.7 | 69.0 | — |
| GPT | Opus | 74.0 | 24.8 | 91.2 | 44.0 | 55.2 | — |
| Opus | GPT | 82.7 | 42.0 | 88.7 | 61.3 | 77.3 | — |
| GPT | GPT | 77.5 | 41.5 | 84.2 | 64.0 | 75.0 | — |

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

**Within-evaluator variance** (same evaluator, different generator):
- Opus reading: 1.9 pts difference
- GPT reading: 1.9 pts difference

**Cross-evaluator variance** (same generator, different evaluator):
- Opus narrative: 5.6 pts difference
- GPT narrative: 5.6 pts difference

(The underlying |Δ|-vs-Psyche values are withheld; the differences between them are not
a function of the private profile.)

The evaluator effect (5.6 pts) is 3× the generator effect (1.9 pts). **Who reads the narrative matters far more than who wrote it.** The personality signal in the text is largely model-agnostic; what changes is the evaluator's systematic biases.

Notably, the GPT-generated narrative evaluated by Opus is the closest to Psyche GT of any condition — closer than the Opus-generated narrative evaluated by Opus (magnitudes withheld). This suggests GPT may produce narratives that encode personality signal more transparently, even though GPT's own evaluation of them is less accurate.

### Finding 5: O Is the Universal Anchor

Across all conditions — both models, all registers, chunked and full-context, generated and evaluated — Openness scores cluster between 77 and 92. This 15-point range compares to N (40-83), E (14-53), A (30-64), and C (31-81).

O is the most robustly inferred trait because:
1. It has the strongest textual signal (word choice, topic selection, intellectual curiosity)
2. Both models agree on it (mean bias only -2.8)
3. It survives register shifts (high O appears in both academic writing and casual texts)
4. It survives the narrative transformation (both generators produce high-O narratives from high-O source data)

## Confidence Intervals

All runs showed tight within-condition CIs (±0.1 to ±4.9, median ±0.7), confirming that between-condition and between-model differences are systematic, not sampling noise.

## Implications

1. **Cross-model validation is not straightforward.** GPT and Opus have systematic, register-independent biases. Comparing narrative scores against different model GTs produces contradictory rankings (the original problem that prompted this rework).

2. **The fairest comparison uses each model's own corpus GT.** Opus narratives should be compared against Opus corpus GT; GPT narratives against GPT corpus GT. Cross-model comparison requires bias correction.

3. **Register matters.** Personal SMS is the natural comparison for arc 2 narratives. Academic GT is inappropriate for evaluating narratives generated from SMS data.

4. **Chunked > full-context for personality inference.** The diversification effect of chunked sampling outweighs the contextual coherence of full-context evaluation.

5. **The generation confound is small.** The core finding of personality signal preservation through narrative transformation is robust to generator model choice. Both Opus and GPT narratives encode similar personality signal when read by the same evaluator.

## Data

Full results: `cross-model-factorial-results.json`
Individual runs: `profiles/analysis/runs/{source}/{backend}/run-{NN}-llm-*.json`
GPT narrative: `voice-clone/narratives/experiments/gpt-generation/author_first_person.md` (subject first-person perspective, arc 2)
