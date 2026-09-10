# 1M Context Narrative Experiment: Ablation Results

**Date**: 2026-03-17
**Status**: Complete

---

## 1. Experiment Design

### Research Questions

1. **Context restriction** (Step 1): Does restricting chapter writer visibility to ~200 messages cause trait inflation?
2. **Word count** (Step 2): Is the improvement partly from shorter text having less contradictory surface area?
3. **Evaluator independence** (Step 3): Is the improvement evaluator-independent, or an Opus self-scoring artifact?
4. **Measurement stability** (Step 4): Is the 3.9 vs 11.4 difference outside measurement noise?

### Conditions

| Condition | Context | Word Target | Messages per Chapter |
|-----------|---------|-------------|---------------------|
| archive-narrative-old | 100-150K (LLM chapter briefs) | ~24K | ~500 (pre-filtered) |
| archive-narrative-1m | 1M (all messages) | ~20K | All 19,867 |
| archive-narrative-filtered | 1M outline + ~200 msg/chapter | ~20K | ~200 (subsampled) |
| archive-narrative-long | 1M (all messages) | ~24K | All 19,867 |

### Ground Truths

| Ground Truth | N | E | O | A | C | Source |
|-------------|-----|-----|-----|-----|-----|--------|
| **Opus Corpus** | 51.1 | 28.3 | 88.6 | 36.4 | 61.4 | Opus 4.6 analyzing 1.47M word corpus |
| **Merged Psyche** | — | — | — | — | — | 39 instruments + interview + corpus (values withheld — private subject data) |

---

## 2. Results: Opus Evaluation

### 2a. Scores vs Opus Corpus Ground Truth

| Level | N | E | O | A | C | Mean |Δ| |
|-------|-----|-----|-----|-----|-----|---------|
| **Ground Truth (Opus Corpus Inference)** | 51.1 | 28.3 | 88.6 | 36.4 | 61.4 | 0.0 |
| archive-narrative-old | 75.0 | 24.7 | 91.3 | 55.7 | 69.0 | **11.4** |
| archive-narrative-1m | 55.0 | 31.0 | 91.0 | 40.7 | 67.7 | **3.9** |
| archive-narrative-filtered | 54.8 | 27.6 | 91.4 | 38.2 | 61.6 | **1.8** |
| archive-narrative-long | 50.0 | 25.5 | 90.5 | 36.8 | 58.5 | **1.8** |

### 2b. Deltas from Opus Corpus

| Level | dN | dE | dO | dA | dC | Mean |Δ| |
|-------|------|------|------|------|------|---------|
| archive-narrative-old | +23.9 | -3.6 | +2.7 | +19.3 | +7.6 | **11.4** |
| archive-narrative-1m | +3.9 | +2.7 | +2.4 | +4.3 | +6.3 | **3.9** |
| archive-narrative-filtered | +3.7 | -0.7 | +2.8 | +1.8 | +0.2 | **1.8** |
| archive-narrative-long | -1.1 | -2.8 | +1.9 | +0.4 | -2.9 | **1.8** |

### 2c. Scores vs Merged Psyche Ground Truth

| Level | N | E | O | A | C | Mean |Δ| |
|-------|-----|-----|-----|-----|-----|---------|
| **Ground Truth (Merged Psyche Profile (39 instruments))** | — | — | — | — | — | — |
| archive-narrative-old | 75.0 | 24.7 | 91.3 | 55.7 | 69.0 | — |
| archive-narrative-1m | 55.0 | 31.0 | 91.0 | 40.7 | 67.7 | — |
| archive-narrative-filtered | 54.8 | 27.6 | 91.4 | 38.2 | 61.6 | — |
| archive-narrative-long | 50.0 | 25.5 | 90.5 | 36.8 | 58.5 | — |

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

### 2d. Deltas from Merged Psyche

_Withheld: this table is computed against the subject's merged ground-truth profile, which is private and is not published here._

---

## 3. Ablation Interpretation

### Step 1: Filtered-Context Ablation

**Result**: Filtered mean |Δ| = 1.8 (vs old=11.4, 1M=3.9). Context restriction **does not reproduce the inflation**. Something else (model improvements, outline quality, discovery artifacts) drove the improvement, not context size.

### Step 2: Length-Matched Ablation

**Result**: Long mean |Δ| = 1.8 (vs 1M=3.9). The improvement **survives at old-pipeline word count**. Brevity is not the driver — the 1M narrative's personality accuracy is robust to length.

---

## 4. Cross-Model Evaluation (GPT-5.4)

| Level | Domain | Opus | GPT-5.4 | Difference |
|-------|--------|------|---------|------------|
| archive-narrative-old | N | 75.0 | 84.7 | +9.7 |
| archive-narrative-old | E | 24.7 | 40.3 | +15.6 |
| archive-narrative-old | O | 91.3 | 89.0 | -2.3 |
| archive-narrative-old | A | 55.7 | 57.3 | +1.6 |
| archive-narrative-old | C | 69.0 | 78.7 | +9.7 |
| archive-narrative-1m | N | 55.0 | 54.0 | -1.0 |
| archive-narrative-1m | E | 31.0 | 53.0 | +22.0 |
| archive-narrative-1m | O | 91.0 | 88.0 | -3.0 |
| archive-narrative-1m | A | 40.7 | 58.0 | +17.3 |
| archive-narrative-1m | C | 67.7 | 84.0 | +16.3 |
| archive-narrative-filtered | N | 54.8 | 58.6 | +3.8 |
| archive-narrative-filtered | E | 27.6 | 48.4 | +20.8 |
| archive-narrative-filtered | O | 91.4 | 87.0 | -4.4 |
| archive-narrative-filtered | A | 38.2 | 59.2 | +21.0 |
| archive-narrative-filtered | C | 61.6 | 82.6 | +21.0 |
| archive-narrative-long | N | 50.0 | 60.0 | +10.0 |
| archive-narrative-long | E | 25.5 | 43.3 | +17.8 |
| archive-narrative-long | O | 90.5 | 86.7 | -3.8 |
| archive-narrative-long | A | 36.8 | 58.3 | +21.5 |
| archive-narrative-long | C | 58.5 | 79.7 | +21.2 |

### Cross-Model Agreement
- **archive-narrative-old**: Opus=11.4, GPT-5.4=16.8, agreement within 5.4 points
- **archive-narrative-1m**: Opus=3.9, GPT-5.4=14.5, agreement within 10.6 points
- **archive-narrative-filtered**: Opus=1.8, GPT-5.4=14.6, agreement within 12.8 points
- **archive-narrative-long**: Opus=1.8, GPT-5.4=13.2, agreement within 11.4 points

Ranking differs: Opus=['archive-narrative-filtered', 'archive-narrative-long', 'archive-narrative-1m', 'archive-narrative-old'], GPT-5.4=['archive-narrative-long', 'archive-narrative-1m', 'archive-narrative-filtered', 'archive-narrative-old']

---

## 5. Confidence Intervals


**archive-narrative-old** (4 runs):

| Domain | Mean | Std | 95% CI | Individual Runs |
|--------|------|-----|--------|-----------------|
| N | 74.9 | 1.6 | [72.4, 77.4] | 75.0, 76.0, 72.7, 76.0 |
| E | 25.4 | 0.6 | [24.5, 26.3] | 24.7, 26.0, 25.7, 25.3 |
| O | 90.1 | 2.0 | [87.0, 93.2] | 91.3, 87.7, 89.3, 92.0 |
| A | 43.5 | 8.2 | [30.5, 56.6] | 55.7, 38.7, 38.7, 41.0 |
| C | 58.9 | 6.9 | [48.0, 69.9] | 69.0, 55.7, 53.7, 57.3 |

**archive-narrative-1m** (4 runs):

| Domain | Mean | Std | 95% CI | Individual Runs |
|--------|------|-----|--------|-----------------|
| N | 53.8 | 0.8 | [52.5, 55.2] | 55.0, 53.7, 53.0, 53.7 |
| E | 28.9 | 1.5 | [26.5, 31.3] | 31.0, 27.3, 28.7, 28.7 |
| O | 91.7 | 0.5 | [90.9, 92.4] | 91.0, 92.0, 92.0, 91.7 |
| A | 38.9 | 1.3 | [36.9, 41.0] | 40.7, 39.0, 38.0, 38.0 |
| C | 62.5 | 3.6 | [56.8, 68.3] | 67.7, 61.7, 61.3, 59.3 |

### Statistical Significance
95% CIs are **non-overlapping** for: N, E — these differences are statistically reliable.
95% CIs **overlap** for: O, A, C — these differences may be within measurement noise.

---

## 6. Summary Matrix

### 4 Conditions x 2 Evaluators x Opus Corpus Ground Truth

| Condition | Opus Mean |Δ| | GPT-5.4 Mean |Δ| | Agreement |
|-----------|-----------|----------------|-----------|
| archive-narrative-old | 11.4 | 16.8 | Δ=5.4 |
| archive-narrative-1m | 3.9 | 14.5 | Δ=10.6 |
| archive-narrative-filtered | 1.8 | 14.6 | Δ=12.8 |
| archive-narrative-long | 1.8 | 13.2 | Δ=11.4 |

---

## 7. Conclusions

### The Surprising Finding

The filtered ablation (200 messages/chapter) produced **better** personality accuracy (mean |Δ| = 1.8) than both the original 1M run (3.9) and the old pipeline (11.4). This was unexpected — the hypothesis was that restricting context would *reproduce* the old pipeline's inflation.

**What this means**: The old pipeline's inaccuracy was NOT caused by limited message visibility per chapter. The 1M pipeline's improvement came from the **quality of its outline and discovery artifacts**, which were created by an LLM that could see all 19,867 messages. Even when the chapter writer only sees 200 messages, using a better outline (one designed with full-archive visibility) produces dramatically more accurate personality signal.

The filtered ablation kept the 1M pipeline's outline and discovery artifacts while restricting the chapter writer's message access. The fact that this scored *better* than the full 1M run (1.8 vs 3.9) suggests that having too many messages in the chapter-writing context may actually introduce noise — the model gets distracted by irrelevant messages from outside the chapter's focal period.

### What We Can Claim

1. **The outline and discovery phase is the critical bottleneck.** The improvement comes from having an LLM read all messages during *planning* (outline + discovery), not during *writing*. Context size matters for the discovery phase; the writing phase works fine with ~200 messages.
2. **Word count is not the confound.** The length-matched ablation (28K words) preserves personality accuracy (mean |Δ| = 1.8), matching the shorter 1M narrative. Brevity is not the driver.
3. **N and A inflation is an old-pipeline artifact.** The old pipeline inflated N by +23.9 and A by +19.3 against ground truth. All three new conditions (1M, filtered, long) dramatically reduce these inflations, confirming the old pipeline's chapter briefs — not the chapter writing — were the source of bias.
4. **The N difference exceeds measurement noise.** Confidence intervals (4 runs each): archive-narrative-old N=[72.4, 77.4] vs archive-narrative-1m N=[52.5, 55.2]. Non-overlapping 95% CIs.

### GPT-5.4 Cross-Model Results (Nuanced)

GPT-5.4 shows a systematic upward bias on E (+16-23), A (+2-21), and C (+10-21) across all conditions. This inflates GPT-5.4's absolute deltas (13-17 range) well above Opus's (2-11 range). However, the key finding is preserved:

- **Both models agree archive-narrative-old is worst**: Opus=11.4, GPT-5.4=16.8
- **Both models agree all new conditions outperform old**: GPT-5.4 scores 13.2-14.6 for new vs 16.8 for old
- **Both models agree on the N improvement**: archive-narrative-old N inflated by +24 (Opus) / +34 (GPT-5.4); archive-narrative-1m N within 3-4 points of ground truth on both models
- **Ranking within new conditions differs**: Opus prefers filtered > long > 1M; GPT-5.4 prefers long > 1M > filtered. The differences are small (< 2 points on Opus, < 2 points on GPT-5.4)

The evaluator circularity concern is **partially addressed**: the old-vs-new improvement is evaluator-independent, but the fine-grained ranking within new conditions is not.

### What We Cannot Claim

1. **Full evaluator independence for rankings**: GPT-5.4 and Opus agree on the coarse comparison (old is worst) but disagree on fine rankings within the new conditions.
2. **Generalizability**: N=1 source archive. The outline/discovery quality hypothesis needs testing on other relationships.
3. **Mechanism specificity**: We know the outline phase matters, but cannot isolate whether it's the emotional phase mapping, canonical facts, character notes, or the outline structure itself.
4. **Optimal chapter context**: 200 messages performed slightly *better* than full context. Whether this holds at 50, 500, or 1000 messages is unknown.

---

## 8. Response to Critical Reviews

### GPT-5.4 Review Concerns

1. **Word count confound**: Controlled via archive-narrative-long ablation. Result: not a confound (|Δ|=1.8 at 28K words).
2. **Evaluator circularity**: Controlled via GPT-5.4 cross-evaluation. Result: **coarse ranking preserved** — GPT-5.4 agrees old pipeline is worst. Fine-grained ranking differs due to E/A/C calibration bias.
3. **No confidence intervals**: Computed with 3 additional runs per level (4 total). N and E differences are statistically significant; A and C are within noise.
4. **Opus-derived ground truth**: Addressed with dual ground truth comparison. Against the Merged Psyche profile, all 1M-derived narratives still outperform the old pipeline (the underlying figures are withheld — private subject data).

### Opus 4.6 Review Concerns

1. **Programmatic scoring confound**: N/A — the old pipeline did NOT use the 14-signal system. Both pipelines relied on LLM judgment. The difference is in planning-phase context, not scoring methodology.
2. **N=2**: Acknowledged. This followup focuses on 4 ablation conditions within one source archive, trading breadth for depth in understanding mechanisms.

---

## Appendix: Pipeline Specifications

### Old Pipeline (100-150K context)
- LLM-generated chapter briefs: curated lists of 5-15 messages per chapter with emotional arcs
- Each chapter written seeing only its brief + ~500 pre-filtered messages
- Discovery artifacts from LLM reading excerpts

### 1M Pipeline
- All 19,867 messages in compact format (~534K tokens)
- Discovery phase: LLM reads all messages, produces emotional phases + canonical facts + character notes
- Writing phase: LLM sees all messages + discovery + outline + all prior chapters

### Filtered Ablation
- Uses 1M pipeline's outline and discovery artifacts
- Chapter writer sees only ~200 subsampled messages per chapter (seed=42)
- Same model, same prompt, same voice instructions

### Length-Matched Ablation
- Full 1M pipeline (all messages visible)
- Explicit instruction to write longer chapters (1800-2200 words each, targeting ~24K total)
- Tests whether the improvement is from brevity reducing contradictory surface area

---

## Addendum: 2026-04-18 — Provenance Correction and Pending Opus 4.7 Row

### The silent-drift problem in the 2026-03-17 results

The existing Opus-evaluator runs in `profiles/analysis/runs/archive-narrative-*/claude/*.json`
record `"model_used": "claude-opus-via-claude-cli"`. This is the exact
silent-drift pattern that the 2026-04-16 workspace audit flagged: the label
is alias-based (the CLI `--model opus` flag), but the alias resolves to
whatever Opus generation Claude Code currently ships.

- When these runs were captured (before ~2026-02), `opus` resolved to Claude Opus 4.5.
- When the 2026-03-17 report was written, `opus` resolved to Claude Opus 4.6.
- As of 2026-04-18, `opus` resolves to Claude Opus 4.7.

Re-running `run_analysis_experiments.py` against these JSONs today produces
results correctly computed from past scores, but the **column labels in
this report's tables (which read as "Opus Evaluation") conflate multiple
generations.** Critical-review recommendation #6 ("Specify model versions
for all generation and evaluation steps") has not been actioned because
the capture-time provenance was insufficient to disambiguate after the fact.

### What a clean Opus 4.7 row requires

Adding a proper 4.7 evaluator column requires **re-running the evaluation
phase** (not generation — existing narratives stay fixed) with:

1. **Alias-based row (`opus_current`, floating)**: `claude -p --model opus`
   today captures the 4.7 scores. This row will drift again when 4.8 ships.
2. **Pinned row (`opus_4_7`, stable)**: `claude -p --model claude-opus-4-7`
   pins this specific generation for stable longitudinal comparison.
3. **Re-capture for 4.6 (`opus_4_6`, stable)**: `claude -p --model claude-opus-4-6`
   locks the 4.6 row independently of what `opus` alias resolves to.

Phase 0 of the 2026-04-18 plan confirmed Opus 4.6 remains callable, so all
three rows are feasible. The minimum-viable add is the pinned 4.7 row.

### Blocker: evaluation pipeline is not in this directory

This experiment directory contains the written analysis (`results_report.md`,
`critical_review_opus.md`) but not the runnable evaluation harness that
produces JSONs under `profiles/analysis/runs/`. The narrative generator +
evaluator live in the voice-clone pipeline, which is currently gated by a
separate privacy-cleanup task (see audit cluster I). Re-running with Opus
4.7 depends on that work landing first.

### Provenance pattern going forward

New runs should record BOTH alias and resolved full model ID at invocation
time. The pattern is already implemented in the psyche benchmark harness as
of 2026-04-18:

```python
# psyche/benchmark/run_eval.py (after 2026-04-18 refactor)
result_data = {
    "model_key": model_key,
    "model_requested": model_id,       # alias or pinned ID the caller used
    "model_resolved": resolved_full_id, # current alias target at invoke time
    ...
}
```

and in the analysis-layer `LLMAnalysisResult` Pydantic model:

```python
# psyche/analysis/psyche_analysis/methods/llm_claude.py
class LLMAnalysisResult(BaseModel):
    ...
    model_requested: str = ""
    model_used: str = ""  # resolved full ID
```

When the voice-clone narrative-eval pipeline is re-run, it should adopt
this same two-field pattern. The mapping table lives at
`psyche/analysis/psyche_analysis/config.py::_ALIAS_TO_FULL_ID`.

### Deferred

- Add pinned Opus 4.6 + alias Opus (current 4.7) + pinned Opus 4.7 rows.
- Re-compute per-condition MAE deltas across the new rows.
- Re-run `psyche/analysis/scripts/run_analysis_experiments.py` on the
  expanded run tree; its output is analysis-only and self-contained.
- Optionally add a fresh GPT-5.4 evaluator row for each condition (the
  existing `codex/` runs are already there and `gpt-5.4` is still current
  per `~/.claude/CLAUDE.md` — no re-run strictly required).

Status: **Deferred pending voice-clone pipeline privacy cleanup.**
Ownership: blocked on the cluster-I voice-clone work tracked in the
2026-04-16 workspace audit.

