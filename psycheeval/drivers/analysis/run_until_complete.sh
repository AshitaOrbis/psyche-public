#!/usr/bin/env bash
# Re-invoke a resumable PhaseB1 runner until it reports all calls completed.
# The runner is idempotent (resumes from its JSONL checkpoint; errored/capped
# calls are re-run). Handles long cap outages by sleeping between passes.
#
# Usage: run_until_complete.sh <logfile> <sleep_between_sec> -- <python cmd...>
set -uo pipefail
LOG="$1"; SLEEP="$2"; shift 2
[ "${1:-}" = "--" ] && shift
cd "$(dirname "$0")/../.." || exit 2

for i in $(seq 1 60); do
  echo "=== pass $i $(date -Is) ===" >> "$LOG"
  out="$("$@" 2>&1)"; echo "$out" >> "$LOG"
  status="$(printf '%s\n' "$out" | grep -oE 'STATUS valid=[0-9]+ total=[0-9]+' | tail -1)"
  valid="$(printf '%s' "$status" | grep -oE 'valid=[0-9]+' | cut -d= -f2)"
  total="$(printf '%s' "$status" | grep -oE 'total=[0-9]+' | cut -d= -f2)"
  echo "pass $i -> ${status:-NO_STATUS}" >> "$LOG"
  if [ -n "${valid:-}" ] && [ -n "${total:-}" ] && [ "$valid" -ge "$total" ]; then
    echo "COMPLETE after pass $i ($valid/$total) $(date -Is)" >> "$LOG"; exit 0
  fi
  echo "incomplete (${valid:-?}/${total:-?}); sleeping ${SLEEP}s" >> "$LOG"
  sleep "$SLEEP"
done
echo "GAVE UP after 60 passes $(date -Is)" >> "$LOG"; exit 1
