#!/usr/bin/env bash
# Codex-only pipeline driver — runs P2-P5 sequentially using GPT-5.4 + GPT-5.5
# only. No Opus calls. Each phase uses the existing resume logic, so the script
# is restartable from any phase boundary; killed phases pick up where they left
# off the next time the script runs.
#
# Phases:
#   P2: v0.1 tri-model pairwise (codex judges, same-author scope)
#   P3: v0.2 generation (codex authors)
#   P4: v0.2 anchored scalar scoring (codex judges)
#   P5: v0.2 targeted pairwise (codex judges, same-author scope, brief whitelist)
#
# Source of truth for what's deferred and resume order:
#   docs/runbook_codex_only.md
#
# Usage:
#   bash run_codex_only_pipeline.sh
# or in background with stdout teed to a log:
#   nohup bash run_codex_only_pipeline.sh > /tmp/codex_only_pipeline.log 2>&1 &

set -euo pipefail

PSYCHEEVAL_DIR="$HOME/claudeworkspace/psyche/psycheeval"
PYTHON="$HOME/claudeworkspace/psyche/analysis/.venv/bin/python"
LOG_DIR="/tmp/codex_only_pipeline"
mkdir -p "$LOG_DIR"

cd "$PSYCHEEVAL_DIR"
export PYTHONPATH=src

TRI_TAG="2026-04-26_micro_tri_model"
V02_TAG="2026-04-26_v02_hard_codex_only"
CODEX_JUDGES="gpt-5.4,gpt-5.5-xhigh"
V02_PAIRS="C4:C0,C4:C1,C4:C1_padded,C4:C4_shuffled,C3:C4,C1:C1_padded,C4:C5@PI"

ts() { date -u "+%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] $*"; }

# --- Wait for any in-flight scalar judging on the tri-model tag (P1) ---
log "Checking for in-flight P1 (tri-model scalar judging)..."
while pgrep -af "psycheeval.judge score.*${TRI_TAG}" >/dev/null 2>&1; do
  log "P1 still running; sleeping 60s..."
  sleep 60
done
log "P1 not running. Proceeding."

# --- P2 ---
log "===== P2: v0.1 tri-model pairwise (codex judges, same-author scope) ====="
"$PYTHON" -u -m psycheeval.judge pairwise \
  --tag "$TRI_TAG" \
  --pilot micro_pilot \
  --judges "$CODEX_JUDGES" \
  --workers 2 \
  --scope same_author_only \
  --missing-only 2>&1 | tee "$LOG_DIR/p2.log"
log "P2 complete."

# --- P3 ---
log "===== P3: v0.2 generation (codex authors only) ====="
"$PYTHON" -u -m psycheeval.run \
  --pilot v02_hard_pilot \
  --tag "$V02_TAG" \
  --authors "$CODEX_JUDGES" \
  --workers 2 2>&1 | tee "$LOG_DIR/p3.log"
log "P3 complete."

# --- P4 ---
log "===== P4: v0.2 anchored scalar scoring (codex judges only) ====="
"$PYTHON" -u -m psycheeval.judge score \
  --tag "$V02_TAG" \
  --pilot v02_hard_pilot \
  --judges "$CODEX_JUDGES" \
  --workers 2 \
  --rubric anchored 2>&1 | tee "$LOG_DIR/p4.log"
log "P4 complete."

# --- P5 ---
log "===== P5: v0.2 targeted pairwise (codex judges, same-author scope) ====="
"$PYTHON" -u -m psycheeval.judge pairwise \
  --tag "$V02_TAG" \
  --pilot v02_hard_pilot \
  --judges "$CODEX_JUDGES" \
  --workers 2 \
  --scope same_author_only \
  --pairs "$V02_PAIRS" \
  --missing-only 2>&1 | tee "$LOG_DIR/p5.log"
log "P5 complete."

# --- Final analyze ---
log "===== Regenerating metrics for tri-model + v0.2-codex-only tags ====="
"$PYTHON" -m psycheeval.analyze --tag "$TRI_TAG" --pilot micro_pilot 2>&1 | tee "$LOG_DIR/analyze_tri.log"
"$PYTHON" -m psycheeval.analyze --tag "$V02_TAG" --pilot v02_hard_pilot 2>&1 | tee "$LOG_DIR/analyze_v02.log"

log "===== Codex-only pipeline complete ====="
log "Tri-model metrics: reports/metrics_${TRI_TAG}.json"
log "v0.2 codex-only metrics: reports/metrics_${V02_TAG}.json"
log "Deferred Opus work: see docs/runbook_codex_only.md"
