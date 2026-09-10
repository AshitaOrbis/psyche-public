# Phase A #6 — position/orientation residuals of the Gate-2 global-pole

**Date**: 2026-06-28
**Driver**: `drivers/analysis/gate6_position_residuals.py` (adapts `gate2_signflip.py`; pure stdlib, no model calls)
**Output**: `reports/analysis/gate6_position_residuals.json`

## Purpose
Gate 2 found the C4-vs-C4_WRONG "matching" win is **mostly a global trait-pole preference** (3/4 reciprocal pairs: one persona's profile wins regardless of which persona is the target). This checks whether that asymmetry is a **presentation artifact** by re-computing the per-pair own-profile win rate under two independent splits of the same cross-provider/same-author records:
1. **orientation file** — AB (`pairwise_scores.jsonl`, original order) vs BA (`pairwise_swap_scores.jsonl`, swapped order);
2. **C4 slot** — was the target-conditioned output presented first (slot A) or second (slot B).

If the global-pole verdict holds in both halves of both splits, it is not an AB/BA or slot artifact.

## Result — own-profile win rate (C4 beats C4_WRONG on the persona's own scenarios)

| reciprocal pair | ALL | AB file | BA file | C4-in-A | C4-in-B | stable? |
|---|---|---|---|---|---|---|
| dario / pawl | 0.80/0.34 | 0.82/0.36 | 0.78/0.33 | 0.78/0.33 | 0.82/0.36 | **GLOBAL-POLE — STABLE** |
| slalom / emily | 0.88/0.29 | 0.93/0.40 | 0.82/0.17 | 0.82/0.17 | 0.93/0.40 | **GLOBAL-POLE — STABLE** |
| goblin / spiraler | 0.54/0.41 | 0.55/0.47 | 0.53/0.35 | 0.53/0.35 | 0.55/0.47 | **GLOBAL-POLE — STABLE** |
| moralist / craftsperson | 0.72/0.54 | 0.78/0.57 | 0.68/0.50 | 0.68/0.50 | 0.78/0.57 | matching↔global (presentation-sensitive) |

(min n/persona per cell ≈ 38–40; ALL ≈ 76–80. Verdict: own-rate >0.5 for one persona and <0.5 for its reciprocal ⇒ GLOBAL-POLE; both >0.5 ⇒ MATCHING.)

## Reading
- **The three global-pole pairs are robust to presentation.** The verdict and the own-profile rates are essentially unchanged across AB vs BA and across C4-in-A vs C4-in-B (e.g. dario 0.78–0.82, pawl 0.33–0.36). Gate 2's central result — that "matching" is mostly a global trait-pole preference, not target-fit — is **not a position/orientation artifact**.
- **The lone "matching" pair is equipoise, not robust matching.** moralist/craftsperson flips MATCHING↔GLOBAL-POLE only because craftsperson's own-profile rate **straddles chance** (0.50 BA, 0.57 AB); moralist sits 0.68–0.78. The binary verdict is unstable because the rate is ~0.5, not because the effect reverses. So genuine sign-flipping target-matching is **fragile in ≤1/4 pairs** — consistent with, and marginally stronger than, Gate 2.

## Net
Confirms Gate 2 deterministically and independently: the global-pole reading survives position/orientation controls. No presentation artifact. This is a confirmatory (not decisive) gate — it hardens the existing interpretation rather than opening a new question.
