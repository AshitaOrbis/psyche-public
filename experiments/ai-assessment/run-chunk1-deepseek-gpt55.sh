#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
LOG_DIR="$SCRIPT_DIR/logs"
STAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$RESULTS_DIR" "$LOG_DIR"

DEEPSEEK_CANONICAL="$RESULTS_DIR/openrouter-deepseek-v4-pro.json"
DEEPSEEK_CHUNK3="$RESULTS_DIR/openrouter-deepseek-v4-pro-chunk3-$STAMP.json"

if [[ -f "$DEEPSEEK_CANONICAL" ]]; then
  if [[ ! -e "$DEEPSEEK_CHUNK3" ]]; then
    cp "$DEEPSEEK_CANONICAL" "$DEEPSEEK_CHUNK3"
  fi
  rm -f "$DEEPSEEK_CANONICAL"
  echo "Archived existing DeepSeek result to $DEEPSEEK_CHUNK3"
fi

RESTORE_XTRACE=0
case "$-" in
  *x*) RESTORE_XTRACE=1; set +x ;;
esac

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  if [[ -f "$HOME/.hermes/.env" ]]; then
    OPENROUTER_API_KEY="$(awk -F= '$1=="OPENROUTER_API_KEY" {print $2; exit}' "$HOME/.hermes/.env" | tr -d '"[:space:]')"
    export OPENROUTER_API_KEY
  fi
fi

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "OPENROUTER_API_KEY is required for the DeepSeek run" >&2
  exit 1
fi

cd "$REPO_DIR"

DEEPSEEK_LOG="$LOG_DIR/deepseek-v4-pro-chunk1-$STAMP.log"
GPT55_LOG="$LOG_DIR/codex-gpt-5.5-xhigh-chunk1-$STAMP.log"

nohup env \
  OPENROUTER_API_KEY="$OPENROUTER_API_KEY" \
  PSYCHE_CHUNK_OVERRIDE=1 \
  PSYCHE_RESUME=1 \
  npx tsx experiments/ai-assessment/run.ts --model openrouter:deepseek/deepseek-v4-pro \
  >"$DEEPSEEK_LOG" 2>&1 &
DEEPSEEK_PID=$!

nohup env \
  PSYCHE_CHUNK_OVERRIDE=1 \
  PSYCHE_RESUME=1 \
  npx tsx experiments/ai-assessment/run.ts --model codex:gpt-5.5:xhigh \
  >"$GPT55_LOG" 2>&1 &
GPT55_PID=$!

echo "Started DeepSeek V4 Pro chunk-1: pid=$DEEPSEEK_PID log=$DEEPSEEK_LOG"
echo "Started Codex GPT-5.5 xhigh chunk-1: pid=$GPT55_PID log=$GPT55_LOG"
echo "$DEEPSEEK_PID" > "$LOG_DIR/deepseek-v4-pro-chunk1-$STAMP.pid"
echo "$GPT55_PID" > "$LOG_DIR/codex-gpt-5.5-xhigh-chunk1-$STAMP.pid"

if [[ "$RESTORE_XTRACE" == "1" ]]; then
  set -x
fi
