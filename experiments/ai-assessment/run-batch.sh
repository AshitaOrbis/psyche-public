#!/usr/bin/env bash
set -euo pipefail

# Run models sequentially through the assessment.
# Each takes ~50 min with chunk-1 for 300-item instruments.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/../.."

echo "=== Starting sequential model runs ==="
echo "$(date): Beginning batch"
echo ""

for model in "$@"; do
  echo "========================================"
  echo "$(date): Starting $model"
  echo "========================================"
  npx tsx experiments/ai-assessment/run.ts --model "$model" 2>&1
  echo ""
  echo "$(date): Completed $model"
  echo ""
  # Brief pause between models
  sleep 10
done

echo "========================================"
echo "$(date): All models complete"
echo "========================================"
