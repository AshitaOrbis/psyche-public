#!/usr/bin/env bash
set -euo pipefail
# Run Gemini Pro with chunk-15 to stay under rate limits.
# Pro's rate limit can't handle 630 individual calls.
cd "$(dirname "$0")/../.."

# Temporarily override CHUNK_SIZE for this run
export PSYCHE_CHUNK_OVERRIDE=15

echo "=== Gemini Pro (chunk-15 override) ==="
echo "$(date): Starting"
npx tsx experiments/ai-assessment/run.ts --model gemini:pro 2>&1
echo "$(date): Completed"
