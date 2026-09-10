#!/usr/bin/env bash
# Phase 1 codex pipeline driver. Waits for the C5_CONTRACT generation
# already running (PID passed as $1) to exit, then chains scoring → pairwise.
# Resume-safe: each command skips records already in the JSONL outputs.
set -euo pipefail

GEN_PID="${1:-}"
TAG="${TAG:-2026-04-26_v02_hard_codex_only}"
PILOT="v02_hard_pilot"
JUDGES="gpt-5.4,gpt-5.5-xhigh"
WORKERS=4
PAIRS="C3:C5_CONTRACT@PI,C4:C5_CONTRACT@PI,C5:C5_CONTRACT@PI"
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)/src"

echo "[$(date -Iseconds)] phase1_codex_pipeline starting" | tee -a "$LOG_DIR/phase1_chain.log"

if [[ -n "$GEN_PID" ]]; then
  echo "[$(date -Iseconds)] waiting for generation pid=$GEN_PID to exit" | tee -a "$LOG_DIR/phase1_chain.log"
  while kill -0 "$GEN_PID" 2>/dev/null; do
    sleep 60
  done
  echo "[$(date -Iseconds)] generation pid=$GEN_PID exited" | tee -a "$LOG_DIR/phase1_chain.log"
fi

# Phase 1.6: anchored scalar judging on the new C5_CONTRACT outputs. Resume-
# safe via the (run_id, judge_model) dedup key. Will only judge missing records.
echo "[$(date -Iseconds)] launching phase1.6 codex scoring" | tee -a "$LOG_DIR/phase1_chain.log"
python3 -m psycheeval.judge score \
  --tag "$TAG" \
  --pilot "$PILOT" \
  --judges "$JUDGES" \
  --rubric anchored \
  --workers "$WORKERS" \
  >> "$LOG_DIR/phase1_6_codex_score.log" 2>&1
score_rc=$?
echo "[$(date -Iseconds)] phase1.6 exit=$score_rc" | tee -a "$LOG_DIR/phase1_chain.log"

if [[ "$score_rc" -ne 0 ]]; then
  echo "[$(date -Iseconds)] aborting chain — scoring failed (see logs/phase1_6_codex_score.log)" | tee -a "$LOG_DIR/phase1_chain.log"
  exit "$score_rc"
fi

# Phase 1.7: pairwise restricted to {C3, C4, C5} comparators per locked D2.
# scope=same_author_only matches the v0.2 codex existing scope (2084 same-author
# records already in pairwise_scores.jsonl). Default is "exhaustive" which would
# generate wasteful cross-author pairs.
echo "[$(date -Iseconds)] launching phase1.7 codex pairwise (restricted scope, same_author_only)" | tee -a "$LOG_DIR/phase1_chain.log"
python3 -m psycheeval.judge pairwise \
  --tag "$TAG" \
  --pilot "$PILOT" \
  --judges "$JUDGES" \
  --workers "$WORKERS" \
  --scope same_author_only \
  --pairs "$PAIRS" \
  >> "$LOG_DIR/phase1_7_codex_pairwise.log" 2>&1
pw_rc=$?
echo "[$(date -Iseconds)] phase1.7 exit=$pw_rc" | tee -a "$LOG_DIR/phase1_chain.log"

if [[ "$pw_rc" -ne 0 ]]; then
  echo "[$(date -Iseconds)] aborting chain — pairwise failed (see logs/phase1_7_codex_pairwise.log)" | tee -a "$LOG_DIR/phase1_chain.log"
  exit "$pw_rc"
fi

echo "[$(date -Iseconds)] phase1 codex chain complete" | tee -a "$LOG_DIR/phase1_chain.log"
