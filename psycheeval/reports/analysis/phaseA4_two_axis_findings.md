# Phase A #4 — two-axis re-score (general quality vs fit-to-target)

**Date**: 2026-06-28 · **Driver**: `drivers/analysis/phaseA4_two_axis.py` · **Prompt**: `prompts/07d_two_axis_scalar.md`
**Outputs**: `phaseA4_two_axis_gpt-5p5_all.json`, `phaseA4_two_axis_opus_decisive_gpt.json`
**Cost**: gpt-5.5 64 calls (cap-free) + opus-4.7 10 calls. 0 failures.

## Purpose
Distinguish "the judge is biased" from "general quality and fit-to-target genuinely trade off." For each C4-vs-C4_WRONG pair, given the scenario + the **true target P's** brief, the judge rates each output on **general_quality** (1–7) and **fit_to_person** (1–7), separately. v0.3 predicts the axes diverge: target-conditioning should move *fit* more than *quality*.

## Result

| | gpt-5.5 (all 64) | opus-4.7 (10 gpt-authored decisive cells) |
|---|---:|---:|
| mean **fit** gap (C4 − C4_WRONG) | **+1.03** | **+0.40** |
| mean **quality** gap (C4 − C4_WRONG) | **+0.34** | **−0.20** |
| fit: C4 / C4_WRONG | 6.62 / 5.59 | 5.6 / 5.2 |
| quality: C4 / C4_WRONG | 6.34 / 6.00 | 5.5 / 5.7 |
| corr(quality, fit) across outputs | 0.577 | 0.722 |
| fit_gap > quality_gap | ✓ | ✓ |

## Reading — the axes diverge, and that explains the global-pole error
Both judges rate the target-conditioned (C4) output **markedly higher on fit** than the opposite-conditioned (C4_WRONG) output, while **general quality is near-tied**. GPT-5.5: fit moves **3×** more than quality (+1.03 vs +0.34). The axes are correlated but distinct (r ≈ 0.58–0.72), so judges *can* separate them.

The Opus **decisive-cell** result is the sharpest: on exactly the cells where the v0.3 *unconditional* judge preferred the wrong/global-pole output, **quality points the wrong way (−0.20, slightly favoring the global pole) while fit points right (+0.40, favoring the target).** This is the mechanism behind the global-pole bias: the unconditional-quality judge was tracking **quality** — on which C4 and C4_WRONG are ~tied (or the pole edges ahead) — and so got tipped by the globally-preferred pole, **missing the fit difference** that actually favors the target.

## Net (with #2, #3)
- #3: a genuine target-match effect exists but is swamped by global-pole in the *unconditional* win.
- **#4: the reason it's swamped is that the unconditional-quality construct ≈ doesn't separate C4 from C4_WRONG (Δquality ≈ 0), whereas fit does (Δfit ≈ +1).**
- #2: asking the judge for *fit* (target-conditioned) recovers the target on ~67% of the decisive cells.
Together: the personalization signal is real and lives in **fit**, not general quality; the v0.3 global-pole "failure" was an unconditional-quality **instrument** missing it. Confirms #2's conclusion via an independent (scalar, two-axis) method.

## Caveats
- Opus arm is the decisive slice only (n=10) → directional; gpt arm (n=64) is the fuller estimate. Single orientation; 1–7 scalar (no AB/BA needed for scalar, but ceiling effects possible — gpt quality clusters 6.0–6.6). Phase B: larger N + per-judge calibration + the profile-stakes panel.
