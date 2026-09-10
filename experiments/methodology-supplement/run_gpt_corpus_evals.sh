#!/usr/bin/env bash
set -euo pipefail

# Run GPT-5.4 (codex) corpus evaluations for cross-model comparison
# 5 sources × 3 runs = 15 total runs (chunked only, no full-context for GPT)
# Rate-limited: codex has ~10-15 calls per window, each run needs ~5-13 chunks
# Expect to need multiple sessions to complete all 15 runs

ANALYSIS_DIR="$HOME/claudeworkspace/psyche/analysis"
RUNS_DIR="$HOME/claudeworkspace/psyche/profiles/analysis/runs"
LOG="$HOME/claudeworkspace/psyche/experiments/methodology-supplement/gpt-eval-runs.log"

# Unset CLAUDECODE to avoid nested session error
unset CLAUDECODE 2>/dev/null || true

cd "$ANALYSIS_DIR"

echo "$(date -Iseconds) Starting GPT corpus evaluation runs" | tee -a "$LOG"

# All conditions: source × run_id
# Order by smallest first (subject-sms ~5 chunks) to get early results
CONDITIONS=(
  "subject-sms 1"
  "subject-sms 2"
  "subject-sms 3"
  "mixed 1"
  "mixed 2"
  "mixed 3"
  "academic 1"
  "academic 2"
  "academic 3"
  "messenger 1"
  "messenger 2"
  "messenger 3"
  "ai-conv 1"
  "ai-conv 2"
  "ai-conv 3"
)

completed=0
failed=0

for entry in "${CONDITIONS[@]}"; do
  read -r level run_num <<< "$entry"

  # Check if this run already exists
  outfile="$RUNS_DIR/$level/codex/run-$(printf '%02d' "$run_num")-llm-claude.json"
  if [ -f "$outfile" ]; then
    echo "$(date -Iseconds) SKIP: $level run $run_num (already exists)" | tee -a "$LOG"
    ((completed++))
    continue
  fi

  echo "$(date -Iseconds) === $level run $run_num (codex/GPT-5.4) ===" | tee -a "$LOG"

  if uv run python scripts/analyze_narratives.py \
    --level "$level" \
    --skip-empath \
    --backend codex \
    --run-id "$run_num" 2>&1 | tee -a "$LOG"; then
    echo "$(date -Iseconds) DONE: $level run $run_num" | tee -a "$LOG"
    ((completed++))
  else
    echo "$(date -Iseconds) FAILED: $level run $run_num (likely rate limit)" | tee -a "$LOG"
    ((failed++))
    # On rate limit failure, wait 30s then continue to next
    # The script is designed to be re-run — it skips completed runs
    echo "$(date -Iseconds) Waiting 30s before next attempt..." | tee -a "$LOG"
    sleep 30
  fi
done

echo "$(date -Iseconds) Session complete: $completed done, $failed failed" | tee -a "$LOG"
echo "Re-run this script to continue from where it left off (completed runs are skipped)"
