#!/usr/bin/env bash
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src
TAG=2026-05-19_v03
PILOT=v03_full_pilot
ALL_PAIRS="C_GENERIC_CONTRACT:C0,C_GENERIC_CONTRACT:C3,C_GENERIC_CONTRACT:C4,C_GENERIC_CONTRACT:C5@PI,C4_WRONG_PROFILE:C0,C4_WRONG_PROFILE:C3,C4_WRONG_PROFILE:C4,C4_WRONG_PROFILE:C5@PI,C5_NONPUBLIC:C5@PI,C5_NONPUBLIC:C5_CONTRACT@PI,C5_NONPUBLIC:C3@PI,C5_NONPUBLIC:C4@PI,C5_NONPUBLIC_CONTRACT:C5_NONPUBLIC@PI,C5_NONPUBLIC_CONTRACT:C5_CONTRACT@PI,C5_NONPUBLIC_CONTRACT:C3@PI,C5_NONPUBLIC_CONTRACT:C4@PI,C5:L1@PI,L1:L2@PI,L2:L3@PI,L3:C5_CONTRACT@PI,L1:C5_CONTRACT@PI,L1:C5@PI,L2:C5@PI,L3:C5@PI,L3:C5_CONTRACT@PI,L1:C3@PI,L2:C3@PI,L3:C4@PI"

echo "=== D1 same-orientation rejudge (opus, full pool) $(date -Iseconds) ==="
python3 -u -m psycheeval.judge same-orientation-rejudge --tag "$TAG" --pilot "$PILOT" \
    --judges opus --workers 1 --pairs "$ALL_PAIRS"

echo "=== D4 ternary sample (opus, full pool) $(date -Iseconds) ==="
python3 -u -m psycheeval.judge ternary-sample --tag "$TAG" --pilot "$PILOT" \
    --judges opus --workers 1 --pairs "$ALL_PAIRS"

echo "=== opus sentinel full-pool collection complete $(date -Iseconds) ==="
