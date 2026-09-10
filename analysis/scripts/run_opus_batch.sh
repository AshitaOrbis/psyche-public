#!/bin/bash
set -euo pipefail

# Batch runner for all Opus conditions (chunked + full-context)
# Total: 24 Opus runs (no rate limit)
#
# Usage:
#   cd psyche/analysis
#   bash scripts/run_opus_batch.sh           # run all
#   bash scripts/run_opus_batch.sh chunked   # chunked only
#   bash scripts/run_opus_batch.sh fullctx   # full-context only

cd "$(dirname "$0")/.."

MODE="${1:-all}"
BACKEND="claude"
START_TIME=$(date +%s)

log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

run_condition() {
    local level="$1"
    local run_id="$2"
    local extra_flags="${3:-}"

    log "Starting: $level run=$run_id $extra_flags"
    if uv run python scripts/analyze_narratives.py \
        --level "$level" --skip-empath --backend "$BACKEND" \
        --run-id "$run_id" $extra_flags 2>&1 | tail -5; then
        log "Completed: $level run=$run_id"
    else
        log "FAILED: $level run=$run_id (exit $?)"
    fi
    echo "---"
}

if [[ "$MODE" == "all" || "$MODE" == "chunked" ]]; then
    log "=== CHUNKED CONDITIONS (Opus) ==="

    # C1: ***REMOVED*** SMS (runs 2-3, run 1 already done)
    for run in 2 3; do
        run_condition "subject-sms" "$run"
    done

    # C3: Academic
    for run in 1 2 3; do
        run_condition "academic" "$run"
    done

    # C5: Messenger
    for run in 1 2 3; do
        run_condition "messenger" "$run"
    done

    # C7: AI Conversations
    for run in 1 2 3; do
        run_condition "ai-conv" "$run"
    done

    # C9: Mixed
    for run in 1 2 3; do
        run_condition "mixed" "$run"
    done
fi

if [[ "$MODE" == "all" || "$MODE" == "fullctx" ]]; then
    log "=== FULL-CONTEXT CONDITIONS (Opus, 1M) ==="

    # C11: ***REMOVED*** SMS full-context
    for run in 1 2 3; do
        run_condition "subject-sms" "$run" "--full-context"
    done

    # C12: Academic full-context
    for run in 1 2 3; do
        run_condition "academic" "$run" "--full-context"
    done

    # C13: Mixed full-context
    for run in 1 2 3; do
        run_condition "mixed" "$run" "--full-context"
    done
fi

END_TIME=$(date +%s)
ELAPSED=$(( END_TIME - START_TIME ))
log "=== ALL DONE === (${ELAPSED}s elapsed, $(( ELAPSED / 60 ))m)"
