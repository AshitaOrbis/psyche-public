#!/usr/bin/env bash
# v0.3 sentinel collector — runs D1/D2/D4 after the main codex pipeline completes.
#
# Waits for the main codex orchestrator (PID 3141240) to exit, then dispatches
# the three sentinel collection passes. This is needed because the in-flight
# orchestrator was launched from an older version of the script that didn't
# include sentinel stages.
#
# Usage:
#   cd ~/claudeworkspace/psyche/psycheeval
#   nohup bash drivers/run_v03_sentinels_after.sh > logs/v03_sentinels.log 2>&1 &

set -euo pipefail

TAG="${TAG:-2026-05-19_v03}"
PILOT="v03_full_pilot"
CODEX_JUDGES="gpt-5.4,gpt-5.5-xhigh"
WORKERS="${WORKERS:-2}"
ORCHESTRATOR_PID="${ORCHESTRATOR_PID:-3141240}"

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

cd "$(dirname "$0")/.."
export PYTHONPATH=src

# Wait for the orchestrator (which runs gen -> scalar -> pairwise) to exit
echo "=== Waiting for main codex orchestrator (PID $ORCHESTRATOR_PID) to finish ==="
while kill -0 "$ORCHESTRATOR_PID" 2>/dev/null; do
    n_outputs=$(wc -l < "runs/$TAG/assistant_outputs.jsonl" 2>/dev/null || echo 0)
    n_scalar=$(wc -l < "runs/$TAG/anchored_judge_scores.jsonl" 2>/dev/null || echo 0)
    n_pw=$(wc -l < "runs/$TAG/pairwise_scores.jsonl" 2>/dev/null || echo 0)
    echo "  $(date -Iseconds) — outputs=$n_outputs, scalar=$n_scalar, pairwise=$n_pw"
    sleep 600  # poll every 10 minutes
done
echo "Main orchestrator exited."

# Pair whitelist (matches run_v03_codex_pipeline.sh)
T1_PAIRS=(
    "C_GENERIC_CONTRACT:C0" "C_GENERIC_CONTRACT:C3" "C_GENERIC_CONTRACT:C4" "C_GENERIC_CONTRACT:C5@PI"
    "C4_WRONG_PROFILE:C0" "C4_WRONG_PROFILE:C3" "C4_WRONG_PROFILE:C4" "C4_WRONG_PROFILE:C5@PI"
    "C5_NONPUBLIC:C5@PI" "C5_NONPUBLIC:C5_CONTRACT@PI" "C5_NONPUBLIC:C3@PI" "C5_NONPUBLIC:C4@PI"
    "C5_NONPUBLIC_CONTRACT:C5_NONPUBLIC@PI" "C5_NONPUBLIC_CONTRACT:C5_CONTRACT@PI"
    "C5_NONPUBLIC_CONTRACT:C3@PI" "C5_NONPUBLIC_CONTRACT:C4@PI"
)
T2_PAIRS=(
    "C5:L1@PI" "L1:L2@PI" "L2:L3@PI" "L3:C5_CONTRACT@PI"
    "L1:C5_CONTRACT@PI" "L1:C5@PI" "L2:C5@PI" "L3:C5@PI"
    "L3:C5_CONTRACT@PI" "L1:C3@PI" "L2:C3@PI" "L3:C4@PI"
)
ALL_PAIRS="$(IFS=,; echo "${T1_PAIRS[*]} ${T2_PAIRS[*]}")"
ALL_PAIRS="${ALL_PAIRS// /,}"

echo ""
echo "=== D1: Same-orientation rejudge sentinel ==="
python3 -u -m psycheeval.judge same-orientation-rejudge \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges "$CODEX_JUDGES" \
    --workers "$WORKERS" \
    --pairs "$ALL_PAIRS" 2>&1 | tee -a "$LOG_DIR/v03_codex_sentinel_d1.log"

echo ""
echo "=== D4: Ternary tie/equipoise sentinel ==="
python3 -u -m psycheeval.judge ternary-sample \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges "$CODEX_JUDGES" \
    --workers "$WORKERS" \
    --pairs "$ALL_PAIRS" 2>&1 | tee -a "$LOG_DIR/v03_codex_sentinel_d4.log"

echo ""
echo "=== D2: Paraphrased anchored sentinel ==="
python3 -u -m psycheeval.judge score \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges "$CODEX_JUDGES" \
    --workers "$WORKERS" \
    --rubric paraphrased_anchored \
    --sample-pct 15 2>&1 | tee -a "$LOG_DIR/v03_codex_sentinel_d2.log"

echo ""
echo "=== Sentinel collection complete ==="
echo "D1 same-orientation:  $(wc -l < runs/$TAG/same_orientation_swap_scores.jsonl 2>/dev/null || echo 0)"
echo "D2 paraphrased:       $(wc -l < runs/$TAG/paraphrased_anchored_scores.jsonl 2>/dev/null || echo 0)"
echo "D4 ternary:           $(wc -l < runs/$TAG/pairwise_ternary_scores.jsonl 2>/dev/null || echo 0)"
