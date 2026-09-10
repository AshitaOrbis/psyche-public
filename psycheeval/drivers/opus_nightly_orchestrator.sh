#!/usr/bin/env bash
# Opus nightly orchestrator. Loops Phase 2 (Opus authoring) → Phase 3
# (Opus anchored scoring + restricted pairwise) up to N iterations,
# sleeping the configured cap-window duration between iterations to
# catch fresh Anthropic-Max 5h cap windows. Resume-safe — each invocation
# only generates / judges records still missing from the JSONL outputs.
#
# Stop conditions:
#   1. Coverage is complete (no missing records after a phase)
#   2. Max iterations reached (default 3 → covers ~15 hours of cap windows)
#   3. A non-cap error keeps recurring (we exit so a human can investigate)
#
# Telemetry: each iteration's exit codes + checkpoint summaries are appended
# to logs/opus_nightly_orchestrator.log. The user can `tail` this on wake-up
# to see what happened overnight.
set -uo pipefail

TAG="${TAG:-2026-04-26_v02_hard_codex_only}"
PILOT="v02_hard_pilot"
WORKERS=1
PAIRS="C3:C5_CONTRACT@PI,C4:C5_CONTRACT@PI,C5:C5_CONTRACT@PI"
MAX_ITERATIONS="${MAX_ITERATIONS:-3}"
CAP_WINDOW_SLEEP="${CAP_WINDOW_SLEEP:-18000}"  # 5h
STARTUP_DELAY="${STARTUP_DELAY:-21600}"  # 6h: lets the existing one-shot Phase 2+3 chain finish iteration 1 first, AND ensures iteration 2 starts in a fresh cap window even if iteration 1 just hit cap.
LOG_DIR="logs"
mkdir -p "$LOG_DIR"

cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)/src"

LOG="$LOG_DIR/opus_nightly_orchestrator.log"

log() {
  echo "[$(date -Iseconds)] $*" | tee -a "$LOG"
}

run_authoring() {
  log "→ launching Opus authoring (workers=$WORKERS)"
  python3 -m psycheeval.run \
    --pilot "$PILOT" \
    --tag "$TAG" \
    --authors opus \
    --workers "$WORKERS" \
    >> "$LOG_DIR/phase2_opus_author.log" 2>&1
  local rc=$?
  log "← opus authoring exit=$rc"
  return $rc
}

run_anchored_scoring() {
  log "→ launching Opus anchored scoring (workers=$WORKERS)"
  python3 -m psycheeval.judge score \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges opus \
    --rubric anchored \
    --workers "$WORKERS" \
    >> "$LOG_DIR/phase3_1_opus_score.log" 2>&1
  local rc=$?
  log "← opus anchored scoring exit=$rc"
  return $rc
}

run_pairwise() {
  log "→ launching Opus pairwise (restricted scope, same_author_only, workers=$WORKERS)"
  python3 -m psycheeval.judge pairwise \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges opus \
    --workers "$WORKERS" \
    --scope same_author_only \
    --pairs "$PAIRS" \
    >> "$LOG_DIR/phase3_2_opus_pairwise.log" 2>&1
  local rc=$?
  log "← opus pairwise exit=$rc"
  return $rc
}

cap_aborted_in_checkpoint() {
  local phase="$1"
  local cp="runs/$TAG/checkpoint_$phase.json"
  [[ -f "$cp" ]] || return 1
  python3 -c "
import json, sys
data = json.load(open('$cp'))
sys.exit(0 if data.get('cap_aborted') else 1)
" && return 0 || return 1
}

iteration_summary() {
  local i="$1"
  log "=== iteration $i summary ==="
  for cp in runs/"$TAG"/checkpoint_*.json; do
    [[ -f "$cp" ]] && python3 -c "
import json
d = json.load(open('$cp'))
print(f'  {\"$cp\".split(\"/\")[-1]}: completed={d[\"completed_count\"]} '
      f'pending={d[\"pending_count\"]} cap_aborted={d[\"cap_aborted\"]} '
      f'cap_events={d[\"cap_event_count\"]}')
" | tee -a "$LOG"
  done
}

log "============================================================"
log "Opus nightly orchestrator starting (max_iter=$MAX_ITERATIONS, sleep=${CAP_WINDOW_SLEEP}s, startup_delay=${STARTUP_DELAY}s)"
log "============================================================"

if [[ "$STARTUP_DELAY" -gt 0 ]]; then
  log "startup delay: sleeping ${STARTUP_DELAY}s before iteration 1 — gives any existing one-shot Opus driver chain time to finish iteration 1 and ensures iteration 1 here starts in a fresh cap window."
  sleep "$STARTUP_DELAY"
  log "startup delay complete; proceeding to iteration 1"
fi

ITER=1
while [[ "$ITER" -le "$MAX_ITERATIONS" ]]; do
  log "----- iteration $ITER / $MAX_ITERATIONS -----"

  run_authoring
  authoring_rc=$?

  run_anchored_scoring
  scoring_rc=$?

  run_pairwise
  pairwise_rc=$?

  iteration_summary "$ITER"

  # If no phase was cap-aborted, we're done.
  any_cap=false
  cap_aborted_in_checkpoint "score_anchored" && any_cap=true
  cap_aborted_in_checkpoint "pairwise" && any_cap=true

  if [[ "$any_cap" == "false" ]]; then
    log "no cap aborts in iteration $ITER — orchestrator exiting"
    exit 0
  fi

  if [[ "$ITER" -lt "$MAX_ITERATIONS" ]]; then
    log "cap aborts seen; sleeping ${CAP_WINDOW_SLEEP}s before next iteration"
    sleep "$CAP_WINDOW_SLEEP"
  fi

  ITER=$((ITER + 1))
done

log "max iterations ($MAX_ITERATIONS) reached — orchestrator exiting"
exit 0
