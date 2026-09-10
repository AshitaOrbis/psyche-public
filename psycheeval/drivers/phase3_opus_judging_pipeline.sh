#!/usr/bin/env bash
# Phase 3 Opus judging driver. Waits for Phase 2 Opus authoring to exit
# (PID passed as $1), then runs Opus anchored scoring + restricted pairwise
# on the full v0.2 corpus. workers=1 enforced for Opus per cap-protective
# defaults. Cap-burn-protected — graceful checkpoint exit on cap exhaustion.
set -euo pipefail

OPUS_AUTHOR_PID="${1:-}"
TAG="${TAG:-2026-04-26_v02_hard_codex_only}"
PILOT="v02_hard_pilot"
WORKERS=1
PAIRS="C3:C5_CONTRACT@PI,C4:C5_CONTRACT@PI,C5:C5_CONTRACT@PI"
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)/src"

echo "[$(date -Iseconds)] phase3_opus_judging_pipeline starting" | tee -a "$LOG_DIR/phase3_chain.log"

if [[ -n "$OPUS_AUTHOR_PID" ]]; then
  echo "[$(date -Iseconds)] waiting for Opus authoring pid=$OPUS_AUTHOR_PID" | tee -a "$LOG_DIR/phase3_chain.log"
  while kill -0 "$OPUS_AUTHOR_PID" 2>/dev/null; do
    sleep 120
  done
  echo "[$(date -Iseconds)] Opus authoring pid=$OPUS_AUTHOR_PID exited" | tee -a "$LOG_DIR/phase3_chain.log"
fi

# Phase 3.1: anchored scalar judging by Opus across the full corpus.
# Existing GPT-5.4 + GPT-5.5 anchored judgments are already in the file;
# Opus only judges its own missing records. workers=1 is the cap-protective
# default for Opus (cap-burn handler engages on rc=1 cap markers).
echo "[$(date -Iseconds)] launching phase3.1 opus anchored scoring" | tee -a "$LOG_DIR/phase3_chain.log"
python3 -m psycheeval.judge score \
  --tag "$TAG" \
  --pilot "$PILOT" \
  --judges opus \
  --rubric anchored \
  --workers "$WORKERS" \
  >> "$LOG_DIR/phase3_1_opus_score.log" 2>&1
score_rc=$?
echo "[$(date -Iseconds)] phase3.1 exit=$score_rc" | tee -a "$LOG_DIR/phase3_chain.log"

# Phase 3.2: Opus pairwise on the full v0.2 corpus, restricted scope per D2.
# Even if 3.1 exits cap-aborted, we still attempt 3.2 on a separate run so
# both phases get whatever Opus quota remains in the next cap window.
# Resume on a future session would re-run this script.
echo "[$(date -Iseconds)] launching phase3.2 opus pairwise (restricted scope, same_author_only)" | tee -a "$LOG_DIR/phase3_chain.log"
python3 -m psycheeval.judge pairwise \
  --tag "$TAG" \
  --pilot "$PILOT" \
  --judges opus \
  --workers "$WORKERS" \
  --scope same_author_only \
  --pairs "$PAIRS" \
  >> "$LOG_DIR/phase3_2_opus_pairwise.log" 2>&1
pw_rc=$?
echo "[$(date -Iseconds)] phase3.2 exit=$pw_rc" | tee -a "$LOG_DIR/phase3_chain.log"

echo "[$(date -Iseconds)] phase3 opus chain finished (score_rc=$score_rc, pw_rc=$pw_rc)" | tee -a "$LOG_DIR/phase3_chain.log"
