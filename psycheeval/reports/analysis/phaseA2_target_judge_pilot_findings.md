# Phase A #2 — target-conditioned re-judging: GPT-5.5 target-swap PILOT

**Date**: 2026-06-28
**Driver**: `drivers/analysis/phaseA2_target_judge_pilot.py` · **Prompt**: `prompts/07c_pairwise_judge_target_conditioned.md`
**Output**: `reports/analysis/gate2b_target_conditioned_pilot.json`
**Cost**: 24 GPT-5.5-xhigh calls via codex CLI (~96 s wall, 4 workers). **Zero Opus cap.**

## Purpose
The v0.3 unconditional-quality pairwise judge rewarded a global trait-pole, not fit-to-target (gate battery). This pilot tests whether a **target-conditioned fit** prompt fixes that, by re-judging the same decisive C4-vs-C4_WRONG pairs (Gate-3 bundle) and asking twice per pair — "which better serves persona **P**?" then "...persona **Q**?" (target swap, same pair, blind to condition, A/B order held constant). A fit-sensitive judge **reverses** its pick when the named target flips; a global-pole judge does not.

**Note on the v0.3 baseline**: `judge.py` renders the "unconditional" pairwise prompt **with `latent_ground_truth` populated** — the v0.3 judge already had the user's ground truth and still preferred the global pole. So #2's real manipulation is the **fit framing + explicit target**, not merely supplying persona info; this is a new judge construct, compared to v0.3 at the outcome level (not a one-variable delta).

## Pre-registered subset
12 tasks = the 2 lowest-task_id tasks per persona across the 3 **global-pole** pairs (dario/pawl, slalom/emily, goblin/spiraler). 12 × 2 questions = 24 calls.

## Result (GPT-5.5-xhigh, n=12)

| metric | value | reading |
|---|---:|---|
| **p_picks_target** (for-P → P-conditioned output) | **0.75** | judge favors the target's output when asked about the target |
| **q_picks_opposite** (for-Q → Q-conditioned output) | **0.833** | and the opposite's output when asked about the opposite |
| **reversed_correctly** (flips P↔Q in the right direction) | **0.583** | majority of pairs are fit-sensitive |
| **any_flip** | **0.583** | every flip that occurred was in the *correct* direction (no wrong-way flips) |
| **decisive cells**: of 4 tasks where the *unconditional* judge preferred the **opposite**, target-conditioned now picks the **target** | **0.75 (3/4)** | direct evidence the eval framing was a major part of the bottleneck |

Both p_picks_target (0.75) and q_picks_opposite (0.833) are well above the 0.5 null → the judge is genuinely responding to the named target, not anchored to one output.

## Texture (per-task)
- **7/12 reverse correctly.** The 5 non-reversers stay on one output for both questions — but the "stuck" output is **mixed** (some stuck on the target-conditioned output, some on the opposite), i.e. the residual non-reversal is **partly genuine quality dominance of one response, not pure pole-stickiness**.
- The one decisive-cell **miss** is **t016 (pawl as target)** — pawl is the most-dominated pole (global desirability 0.20, #3); the hardest case for fit to override quality/pole.

## Verdict — GO (validates the prompt; escalate)
GPT-5.5 reverses well above null and recovers 3/4 of the decisive global-pole-error cells. Per GPT Pro's staging rule ("if GPT-5.5 reverses on the pilot, escalate; else don't spend Opus"), this **clears the bar**. Target-conditioning fixes a **majority, not all,** of the global-pole bias — consistent with #3 (a residual genuine target-match effect existed even under the unconditional judge; target-conditioning amplifies it).

## Caveats (do not over-read)
- **n=12** → wide CIs (reversed_correctly 0.583 ≈ [0.32, 0.81]; the decisive 3/4 is anecdotal).
- Pilot ran GPT-5.5 on all subset tasks **regardless of author**, mixing same-provider (halo risk) and cross-provider records. The full run must **split judge by author** (gpt judges opus-authored, opus judges gpt-authored) to keep cross-provider primary.
- Single A/B orientation (bundle order); reversal is robust to this (order held across P/Q), but a headline run should AB/BA. Forced A/B (no tie).

## Indicated next steps
1. **Expand GPT-5.5 to the full task set** (all 64, cross-provider split) — cap-free; tightens the estimate and covers all 18 decisive cells.
2. **Opus-4.7 arm on the decisive slice** (cross-provider primary) — the headline target-conditioned signal. Needs cap-safe execution (llm.py + cap_burn ⇒ the venv) and spends Opus cap.
3. Feeds the **Gate A→B** decision: high reversal + #1 (neutral-paraphrase, Gemini-gated) staying high ⇒ generation validated + eval bottleneck confirmed ⇒ Phase B leads with target-conditioned judging at scale.
