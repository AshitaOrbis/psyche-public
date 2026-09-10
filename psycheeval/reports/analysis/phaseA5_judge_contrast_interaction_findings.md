# Phase A #5 — judge-family × contrast interaction model

**Date**: 2026-06-28 · **Driver**: `drivers/analysis/phaseA5_judge_contrast_interaction.py` (deterministic, numpy) · **Output**: `phaseA5_judge_contrast_interaction.json`

## Purpose
Formalize trigger #7. Trigger #7 (descriptive) showed 5/11 contrasts have >15pp opus-vs-gpt judge divergence, all contract-structure contrasts. #5 tests whether the judge-family effect is **genuinely contrast-specific** (heterogeneous, concentrated in structure) vs a constant judge offset, via a pooled logistic with a contrast×judge interaction + an LR test. Cross-provider same-author, both orientations (same scope as #7). 10 contrasts covered.

## Result
- **LR test (interaction vs main-effect-only): LR = 376.4, df = 9, p ≈ 4×10⁻⁵⁷.** The judge-family effect **varies by contrast** — overwhelmingly. A constant judge offset is rejected.
- **Mean |judge gap|: structure contrasts 38.1pp (n=4) vs non-structure 6.1pp (n=6)** — a ~6× concentration.
- Largest interaction terms are all structure contrasts: C4_WRONG vs C0 (+2.88), C_GENERIC vs C0 (+2.58), C5 vs C_GENERIC (−1.11), C5 vs C4_WRONG (−0.93).

Per-contrast judge win rates (anth vs gpt):

| contrast | anth | gpt | Δpp | structure |
|---|---:|---:|---:|:--:|
| C_GENERIC_CONTRACT vs C0 | 0.906 | 0.497 | +40.9 | ✓ |
| C4_WRONG_PROFILE vs C0 | 0.901 | 0.408 | +49.2 | ✓ |
| C5 vs C_GENERIC_CONTRACT | 0.319 | 0.650 | −33.1 | ✓ |
| C5 vs C4_WRONG_PROFILE | 0.371 | 0.662 | −29.1 | ✓ |
| C4 vs C_GENERIC_CONTRACT | 0.608 | 0.491 | +11.8 | |
| C3 vs C_GENERIC_CONTRACT | 0.480 | 0.563 | −8.4 | |
| C3 vs C4_WRONG_PROFILE | 0.559 | 0.627 | −6.7 | |
| C4 vs C4_WRONG_PROFILE | 0.583 | 0.547 | +3.6 | |
| C5 vs C5_NONPUBLIC | 0.503 | 0.531 | −2.8 | |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 0.500 | 0.531 | −3.1 | |

## Reading
The opus-vs-gpt judge divergence is **specifically a contract-structure phenomenon**, not a uniform judge bias. Opus-as-judge strongly rewards *any contract over C0* (0.90 vs gpt ~0.41–0.50) **and** disfavors C5-packets relative to contracts (0.32–0.37 vs gpt ~0.65) → a coherent **"opus rewards contract scaffolding"** signal. Matching (C4 vs C4_WRONG) and public-anchor (C5 vs C5_NONPUBLIC) contrasts show small judge gaps (≤4pp) — those effects are judge-robust. This confirms and quantifies the gate-battery's "the structure floor is largely an opus-as-judge effect."

## Caveat (inherited)
Cross-provider same-author scope confounds judge-family with author-family (opus-judge only scores gpt-authored; gpt-judge only scores opus-authored). So the interaction is judge-family **or** author-family × contrast — either way it refutes "judge-unanimous." **Phase B's fully-crossed author×judge matrix resolves which.** Low decision-weight (writeup/robustness), as predicted by GPT Pro.
