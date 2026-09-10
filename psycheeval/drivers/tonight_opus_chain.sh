#!/usr/bin/env bash
# One-shot Opus backfill chain. Runs Phase 2 (author) → Phase 3.1 (anchored
# scoring) → Phase 3.2 (pairwise) sequentially. STOPS on first cap-aborted
# detection so we don't waste cap-burn retry cycles re-triggering cap on
# subsequent phases — that's the contract the user asked for ("pause and
# wait to be resumed when limit is hit").
#
# Each python invocation is cap-burn-protected (post the 2026-05-10 run.py
# fix). On cap, the handler exhausts 5 retries then writes a checkpoint
# with cap_aborted=true and exits clean. This driver inspects that checkpoint
# to decide whether to advance.

set -uo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)/src"

TAG="${TAG:-2026-04-26_v02_hard_codex_only}"
PILOT="v02_hard_pilot"
RUN_DIR="runs/$TAG"
LOG_DIR="logs"
PAIRS="C3:C5_CONTRACT@PI,C4:C5_CONTRACT@PI,C5:C5_CONTRACT@PI"

CHAIN_LOG="$LOG_DIR/tonight_chain.log"
mkdir -p "$LOG_DIR"

log() { echo "[$(date -Iseconds)] $*" | tee -a "$CHAIN_LOG"; }

cap_aborted() {
  local cp="$RUN_DIR/checkpoint_$1.json"
  [[ -f "$cp" ]] || return 1
  python3 -c "import json,sys; sys.exit(0 if json.load(open('$cp')).get('cap_aborted') else 1)" \
    && return 0 || return 1
}

log "============================================================"
log "tonight_opus_chain starting (TAG=$TAG)"
log "============================================================"

# ---------- Phase 2: Opus authoring backfill ----------
log "→ Phase 2: Opus authoring (cap-protected, workers=1)"
python3 -m psycheeval.run \
  --pilot "$PILOT" \
  --tag "$TAG" \
  --authors opus \
  --workers 1 \
  >> "$LOG_DIR/phase2_opus_author.log" 2>&1
rc=$?
log "← Phase 2 exit=$rc"

if cap_aborted "author"; then
  log "Phase 2 cap-aborted — pausing chain; remaining phases will run on resume."
  log "Resume: STARTUP_DELAY=0 MAX_ITERATIONS=4 nohup bash drivers/opus_nightly_orchestrator.sh > logs/orchestrator_stdout.log 2>&1 &"
  exit 0
fi

# ---------- Phase 3.1: Opus anchored scoring backfill ----------
log "→ Phase 3.1: Opus anchored scoring (cap-protected, workers=1)"
python3 -m psycheeval.judge score \
  --tag "$TAG" \
  --pilot "$PILOT" \
  --judges opus \
  --rubric anchored \
  --workers 1 \
  >> "$LOG_DIR/phase3_1_opus_score.log" 2>&1
rc=$?
log "← Phase 3.1 exit=$rc"

if cap_aborted "score_anchored"; then
  log "Phase 3.1 cap-aborted — pausing chain; Phase 3.2 will run on resume."
  log "Resume: STARTUP_DELAY=0 MAX_ITERATIONS=4 nohup bash drivers/opus_nightly_orchestrator.sh > logs/orchestrator_stdout.log 2>&1 &"
  exit 0
fi

# ---------- Phase 3.2: Opus pairwise (restricted scope) ----------
log "→ Phase 3.2: Opus pairwise (cap-protected, workers=1, restricted to C5_CONTRACT pairs)"
python3 -m psycheeval.judge pairwise \
  --tag "$TAG" \
  --pilot "$PILOT" \
  --judges opus \
  --workers 1 \
  --scope same_author_only \
  --pairs "$PAIRS" \
  >> "$LOG_DIR/phase3_2_opus_pairwise.log" 2>&1
rc=$?
log "← Phase 3.2 exit=$rc"

if cap_aborted "pairwise"; then
  log "Phase 3.2 cap-aborted — chain done for tonight; pending records resumable."
else
  log "All Opus backfill phases completed cleanly! v0.2 Opus side is now full."
fi

log "tonight_opus_chain exiting"
