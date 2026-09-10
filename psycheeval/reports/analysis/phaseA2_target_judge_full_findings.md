# Phase A #2 — target-conditioned re-judging (full result)

**Date**: 2026-06-28
**Driver**: `drivers/analysis/phaseA2_target_judge_run.py` · **Prompt**: `prompts/07c_pairwise_judge_target_conditioned.md`
**Outputs**: `gate2c_target_judge_gpt-5p5_all.json` (full GPT-5.5), `gate2c_target_judge_opus_decisive_gpt.json` (Opus slice); pilot in `gate2b_target_conditioned_pilot.json`.
**Cost**: GPT-5.5-xhigh 128 calls (codex, cap-free) + Opus-4.7 20 calls (`claude -p --safe-mode --model claude-opus-4-7`). 0 parse failures, 0 cap interruptions.

## Question
Does re-judging the decisive C4-vs-C4_WRONG pairs with a **target-conditioned fit** prompt ("which serves persona P?", target-swapped to Q) flip the judgment where the v0.3 **unconditional-quality** judge showed global-pole bias? If yes, the bottleneck is the evaluation framing (fixable), not generation. **Cross-provider primary**: gpt judge ↔ opus-authored outputs; opus judge ↔ gpt-authored outputs.

## Results

**GPT-5.5 full (all 64 tasks), by provider cell:**

| metric | overall (64) | **cross-provider (24 opus-authored, PRIMARY)** | same-prov halo (40 gpt-authored) |
|---|---:|---:|---:|
| p_picks_target (for-P → P output) | 0.75 | **0.667** | 0.80 |
| q_picks_opposite (for-Q → Q output) | 0.875 | **0.917** | 0.85 |
| reversed correctly | 0.641 | **0.625** | 0.65 |
| decisive-cell target recovery | 0.556 (18) | **0.625 (8)** | 0.50 (10) |

**Opus-4.7 decisive slice (10 gpt-authored cells where unconditional preferred the opposite; cross-provider):**

| metric | value (n=10) |
|---|---:|
| p_picks_target | 0.70 |
| q_picks_opposite | 0.80 |
| reversed correctly | 0.50 |
| **decisive-cell target recovery** | **0.70 (7/10)** |

## Headline — the eval framing was a major, fixable part of the bottleneck
On the **18 decisive cells** (where the *unconditional* judge preferred the **wrong / global-pole** output), target-conditioned judging recovers the **target** in **12/18 = 67%, cross-provider** (gpt-judge/opus-authored 5/8 = 0.625; opus-judge/gpt-authored 7/10 = 0.70). Both cross-provider directions agree. So when the judge is asked "which serves *this person*?" instead of "which is better?", it picks the target output on ~two-thirds of exactly the cases where the unconditional judge had picked the global pole.

Both judges are clearly **target-sensitive** (not pole-anchored): p_picks_target and q_picks_opposite are well above the 0.5 null in every cell (q_picks_opposite reaches 0.917 cross-provider for GPT-5.5). Reversal is **stable pilot→full** (0.58 → 0.64) and **cross-provider-robust** (0.625 cross vs 0.65 same-provider → not a halo artifact).

## Important methodological note (strengthens the finding)
`judge.py` renders the v0.3 "unconditional" pairwise prompt **with `latent_ground_truth` populated** — the baseline judge already had the synthetic user's ground truth and *still* preferred the global pole. So #2's manipulation is the **fit framing + explicit target**, not supplying persona info. The bottleneck is specifically the **unconditional-quality question**, not absence of persona data — exactly what target-conditioned judging fixes.

## What it does NOT settle
Target-conditioning fixes a **majority, not all** (≈67% of decisive cells; ~33% stay on the pole or reflect genuine quality dominance). And #2 is an **evaluation-side** result — it shows the judge *can* be made fit-sensitive; it does not prove the conditioned text is *target-serving adaptation* vs surface/echo. That is #1's job.

## Caveats
- Decisive-cell n is small (8 / 10 per direction; 18 combined) → wide CIs; treat the 67% as directional.
- Single A/B orientation (bundle order, held across P/Q so reversal is unbiased); a headline-grade run should AB/BA + add a tie option + per-judge calibration (Phase B #2).
- Forced A/B; gpt-5.4-authored tasks pooled with gpt-5.5-authored under "openai".

## Gate A → B status
- **Target-conditioned judging sign-flips** ⇒ the eval-bottleneck half of the A→B "go" condition is **MET** (cross-provider, both directions).
- **Neutral-paraphrase recovery (#1)** — the generation-side half (echo vs adaptation) — remains **Gemini-quota-blocked**. #7's proxy (67% behavioral-cited recovery) leans against pure echo, suggesting #1 will not collapse to 0.50.
- **Provisional A→B read**: trending toward *"generation at least partly target-serving + evaluation was a real, fixable bottleneck"* ⇒ Phase B leads with **target-conditioned judging at scale** (per-judge calibration, fully-crossed author×judge, trait-pole-balanced sampling + decoys). Confirm once #1 runs at quota reset.
