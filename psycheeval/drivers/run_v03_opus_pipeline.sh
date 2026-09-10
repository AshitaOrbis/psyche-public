#!/usr/bin/env bash
# v0.3 Opus-side judging pipeline orchestrator.
#
# Runs in parallel with the codex-side orchestrator. Burns the Claude
# 5-hour usage cap window. cap_handler in psycheeval.judge pauses and
# resumes automatically when a cap is detected.
#
# Order: scalar anchored -> AB/BA pairwise -> sentinels D1/D4/D2.
#
# Usage:
#   cd ~/claudeworkspace/psyche/psycheeval
#   nohup bash drivers/run_v03_opus_pipeline.sh > logs/v03_opus_pipeline.log 2>&1 &

set -euo pipefail

TAG="${TAG:-2026-05-19_v03}"
PILOT="v03_full_pilot"
WORKERS="${WORKERS:-1}"

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

cd "$(dirname "$0")/.."
export PYTHONPATH=src

# Pair manifest (matches run_v03_codex_pipeline.sh — must stay in sync)
T1_PAIRS=(
    "C_GENERIC_CONTRACT:C0"
    "C_GENERIC_CONTRACT:C3"
    "C_GENERIC_CONTRACT:C4"
    "C_GENERIC_CONTRACT:C5@PI"
    "C4_WRONG_PROFILE:C0"
    "C4_WRONG_PROFILE:C3"
    "C4_WRONG_PROFILE:C4"
    "C4_WRONG_PROFILE:C5@PI"
    "C5_NONPUBLIC:C5@PI"
    "C5_NONPUBLIC:C5_CONTRACT@PI"
    "C5_NONPUBLIC:C3@PI"
    "C5_NONPUBLIC:C4@PI"
    "C5_NONPUBLIC_CONTRACT:C5_NONPUBLIC@PI"
    "C5_NONPUBLIC_CONTRACT:C5_CONTRACT@PI"
    "C5_NONPUBLIC_CONTRACT:C3@PI"
    "C5_NONPUBLIC_CONTRACT:C4@PI"
)
T2_PAIRS=(
    "C5:L1@PI"
    "L1:L2@PI"
    "L2:L3@PI"
    "L3:C5_CONTRACT@PI"
    "L1:C5_CONTRACT@PI"
    "L1:C5@PI"
    "L2:C5@PI"
    "L3:C5@PI"
    "L3:C5_CONTRACT@PI"
    "L1:C3@PI"
    "L2:C3@PI"
    "L3:C4@PI"
)
ALL_PAIRS="$(IFS=,; echo "${T1_PAIRS[*]} ${T2_PAIRS[*]}")"
ALL_PAIRS="${ALL_PAIRS// /,}"

echo "=== v0.3 Opus pipeline — $(date -Iseconds) ==="
echo "TAG=$TAG  PILOT=$PILOT  WORKERS=$WORKERS"
echo ""

# Stage 1: Opus anchored scalar
echo "=== Stage 1: Opus anchored scalar ==="
python3 -u -m psycheeval.judge score \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges opus \
    --workers "$WORKERS" \
    --rubric anchored 2>&1 | tee -a "$LOG_DIR/v03_opus_scalar.log"

# Stage 2: Opus AB/BA pairwise
echo ""
echo "=== Stage 2: Opus AB/BA pairwise ==="
python3 -u -m psycheeval.judge pairwise \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges opus \
    --workers "$WORKERS" \
    --pairs "$ALL_PAIRS" \
    --scope same_author_only \
    --ab-ba-mandatory 2>&1 | tee -a "$LOG_DIR/v03_opus_pairwise.log"

# Stage 3: Opus sentinels (D1, D4, D2)
echo ""
echo "=== Stage 3: Opus D1 same-orientation rejudge ==="
python3 -u -m psycheeval.judge same-orientation-rejudge \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges opus \
    --workers "$WORKERS" \
    --pairs "$ALL_PAIRS" 2>&1 | tee -a "$LOG_DIR/v03_opus_sentinel_d1.log"

echo ""
echo "=== Stage 4: Opus D4 ternary sentinel ==="
python3 -u -m psycheeval.judge ternary-sample \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges opus \
    --workers "$WORKERS" \
    --pairs "$ALL_PAIRS" 2>&1 | tee -a "$LOG_DIR/v03_opus_sentinel_d4.log"

echo ""
echo "=== Stage 5: Opus D2 paraphrased anchored sentinel ==="
python3 -u -m psycheeval.judge score \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges opus \
    --workers "$WORKERS" \
    --rubric paraphrased_anchored \
    --sample-pct 15 2>&1 | tee -a "$LOG_DIR/v03_opus_sentinel_d2.log"

echo ""
echo "=== v0.3 Opus pipeline complete — $(date -Iseconds) ==="
echo "Opus scalar:          $(grep -c '"judge_model":"opus"' runs/$TAG/anchored_judge_scores.jsonl 2>/dev/null || echo 0)"
echo "Opus pairwise:        $(grep -c '"judge_model":"opus"' runs/$TAG/pairwise_scores.jsonl 2>/dev/null || echo 0)"
echo "Opus pairwise swap:   $(grep -c '"judge_model":"opus"' runs/$TAG/pairwise_swap_scores.jsonl 2>/dev/null || echo 0)"
echo "Opus same-orient:     $(grep -c '"judge_model":"opus"' runs/$TAG/same_orientation_swap_scores.jsonl 2>/dev/null || echo 0)"
echo "Opus ternary:         $(grep -c '"judge_model":"opus"' runs/$TAG/pairwise_ternary_scores.jsonl 2>/dev/null || echo 0)"
echo "Opus paraphrased:     $(grep -c '"judge_model":"opus"' runs/$TAG/paraphrased_anchored_scores.jsonl 2>/dev/null || echo 0)"
