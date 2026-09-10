#!/usr/bin/env bash
# Opus deferred pipeline — jobs 1-3 from docs/runbook_codex_only.md
#
# These are the v0.1 + tri-model Opus deferrals that don't depend on the
# in-flight codex pipeline. v0.2 Opus jobs (4-6 in the runbook) require
# codex P3/P4/P5 to finish first because Opus authoring would invalidate
# the codex-judged corpus and require codex re-runs. Those stay deferred
# until the codex pipeline is done.
#
# Jobs (in order):
#   J1: v0.1 pairwise final 115     (claude-cli, ~2h)
#   J2: tri-model scalar (Opus on 216 new GPT-5.5 outputs)  (claude-cli, ~3h)
#   J3: tri-model pairwise, Opus judge, same-author scope   (claude-cli, ~20h)
#
# Total: 115 + 216 + 1152 = 1483 Opus calls. ~25h at workers=1 if no cap hits.
# Each job is resume-safe via canonical-key dedup. If a job hits the
# Claude Max cap mid-run, errors are caught and the script continues to
# the next job rather than fail-fast — partial progress on each phase
# is preserved.
#
# Runs concurrently with the codex pipeline (different provider / quota).
#
# Usage:
#   bash run_opus_deferred_pipeline.sh
# or in background:
#   nohup bash run_opus_deferred_pipeline.sh > /tmp/opus_deferred_driver.log 2>&1 &

set -uo pipefail  # NB: NOT -e — we want job-level errors to be tolerated

PSYCHEEVAL_DIR="$HOME/claudeworkspace/psyche/psycheeval"
PYTHON="$HOME/claudeworkspace/psyche/analysis/.venv/bin/python"
LOG_DIR="/tmp/opus_deferred_pipeline"
mkdir -p "$LOG_DIR"

cd "$PSYCHEEVAL_DIR"
export PYTHONPATH=src

ts() { date -u "+%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] $*"; }

run_job() {
  local label="$1"; shift
  log "===== $label ====="
  if "$@" 2>&1 | tee "$LOG_DIR/${label}.log"; then
    log "$label completed (resume-safe; rerun to pick up any failures)."
  else
    log "$label exited non-zero. Errors logged. Continuing to next job."
  fi
}

# --- J1: v0.1 pairwise final (115 missing Opus calls) ---
run_job "j1_v01_pairwise_final" \
  "$PYTHON" -u -m psycheeval.judge pairwise \
  --tag 2026-04-20_micro --pilot micro_pilot \
  --judges opus --workers 1 --missing-only

# --- J2: tri-model scalar — Opus on the 216 new GPT-5.5 outputs ---
run_job "j2_trimodel_scalar_opus" \
  "$PYTHON" -u -m psycheeval.judge score \
  --tag 2026-04-26_micro_tri_model --pilot micro_pilot \
  --judges opus --workers 1

# --- J3: tri-model pairwise — Opus judge, same-author scope ---
run_job "j3_trimodel_pairwise_opus" \
  "$PYTHON" -u -m psycheeval.judge pairwise \
  --tag 2026-04-26_micro_tri_model --pilot micro_pilot \
  --judges opus --workers 1 \
  --scope same_author_only --missing-only

log "===== Opus deferred pipeline (J1-J3) complete ====="
log "Per-job logs: $LOG_DIR/{j1_v01_pairwise_final,j2_trimodel_scalar_opus,j3_trimodel_pairwise_opus}.log"
log "v0.2 Opus jobs (4-6 in runbook) still deferred — depend on codex P3/P4/P5 finishing first."
