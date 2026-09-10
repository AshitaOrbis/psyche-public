#!/usr/bin/env bash
# v0.3 codex-side pipeline orchestrator.
#
# Waits for the in-flight Phase 1 generation to finish, then chains into
# scalar judging (codex side) and AB/BA pairwise judging (codex side) so
# the codex pipeline runs autonomously.
#
# Does NOT include Opus generation or judging — those burn the Claude cap
# and should be launched in a dedicated session.
#
# Usage:
#   cd ~/claudeworkspace/psyche/psycheeval
#   nohup bash drivers/run_v03_codex_pipeline.sh > logs/v03_codex_pipeline.log 2>&1 &

set -euo pipefail

TAG="${TAG:-2026-05-19_v03}"
PILOT="v03_full_pilot"
CODEX_JUDGES="gpt-5.4,gpt-5.5-xhigh"
NEW_CONDITIONS="C_GENERIC_CONTRACT,C4_WRONG_PROFILE,C5_NONPUBLIC,C5_NONPUBLIC_CONTRACT,L1,L2,L3"
WORKERS="${WORKERS:-2}"

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

cd "$(dirname "$0")/.."
export PYTHONPATH=src

# Stage 1: wait for in-flight generation to finish (if running)
echo "=== Stage 1: Wait for Phase 1 codex generation to finish ==="
GEN_PID="$(pgrep -f "psycheeval.run.*--tag $TAG" || true)"
if [ -n "$GEN_PID" ]; then
    echo "Generation in flight at PID $GEN_PID — waiting..."
    while kill -0 "$GEN_PID" 2>/dev/null; do
        N_OUTPUTS=$(wc -l < "runs/$TAG/assistant_outputs.jsonl" 2>/dev/null || echo 0)
        echo "  $(date -Iseconds) — $N_OUTPUTS outputs produced so far"
        sleep 300
    done
    echo "Generation process exited."
else
    echo "No generation in flight — assuming it is already complete."
fi

N_FINAL=$(wc -l < "runs/$TAG/assistant_outputs.jsonl" 2>/dev/null || echo 0)
echo "Generation produced $N_FINAL outputs total"

if [ "$N_FINAL" -lt 600 ]; then
    echo "WARNING: only $N_FINAL outputs produced; expected ~720. Pipeline halted."
    echo "Inspect logs/v0_3_phase1_codex.log and runs/$TAG/checkpoint_author.json."
    exit 1
fi

# Stage 2: scalar judging (codex side, anchored rubric)
echo ""
echo "=== Stage 2: Scalar judging (codex side, anchored rubric) ==="
python3 -u -m psycheeval.judge score \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges "$CODEX_JUDGES" \
    --workers "$WORKERS" \
    --rubric anchored 2>&1 | tee -a "$LOG_DIR/v03_codex_scalar.log"

# Stage 3: AB/BA mandatory pairwise (codex side)
echo ""
echo "=== Stage 3: AB/BA mandatory pairwise (codex side) ==="
echo "Pair manifest from Phase -1.1 design-lock: T1 (16 pairs) + T2 (12 pairs) = 28 types"
echo ""

# T1 pair-set (16 types)
T1_PAIRS=(
    "C_GENERIC_CONTRACT:C0"
    "C_GENERIC_CONTRACT:C3"
    "C_GENERIC_CONTRACT:C4"
    "C_GENERIC_CONTRACT:C5@PI"
    "C4_WRONG_PROFILE:C0"
    "C4_WRONG_PROFILE:C3"
    "C4_WRONG_PROFILE:C4"
    "C4_WRONG_PROFILE:C5@PI"
    "C5_NONPUBLIC:C5@PI"
    "C5_NONPUBLIC:C5_CONTRACT@PI"
    "C5_NONPUBLIC:C3@PI"
    "C5_NONPUBLIC:C4@PI"
    "C5_NONPUBLIC_CONTRACT:C5_NONPUBLIC@PI"
    "C5_NONPUBLIC_CONTRACT:C5_CONTRACT@PI"
    "C5_NONPUBLIC_CONTRACT:C3@PI"
    "C5_NONPUBLIC_CONTRACT:C4@PI"
)

# T2 ladder pair-set (12 types)
T2_PAIRS=(
    "C5:L1@PI"
    "L1:L2@PI"
    "L2:L3@PI"
    "L3:C5_CONTRACT@PI"
    "L1:C5_CONTRACT@PI"
    "L1:C5@PI"
    "L2:C5@PI"
    "L3:C5@PI"
    "L3:C5_CONTRACT@PI"
    "L1:C3@PI"
    "L2:C3@PI"
    "L3:C4@PI"
)

ALL_PAIRS="$(IFS=,; echo "${T1_PAIRS[*]} ${T2_PAIRS[*]}")"
ALL_PAIRS="${ALL_PAIRS// /,}"

echo "Pair whitelist (28 types):"
echo "$ALL_PAIRS" | tr ',' '\n' | head -30
echo ""

python3 -u -m psycheeval.judge pairwise \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges "$CODEX_JUDGES" \
    --workers "$WORKERS" \
    --pairs "$ALL_PAIRS" \
    --scope same_author_only \
    --ab-ba-mandatory 2>&1 | tee -a "$LOG_DIR/v03_codex_pairwise.log"

# Stage 4: Sentinel collection (D1, D2, D4) — codex side
echo ""
echo "=== Stage 4: Sentinel collection (codex side) ==="
echo ""
echo "--- D1: Same-orientation rejudge sentinel (10% pairwise sample) ---"
python3 -u -m psycheeval.judge same-orientation-rejudge \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges "$CODEX_JUDGES" \
    --workers "$WORKERS" \
    --pairs "$ALL_PAIRS" 2>&1 | tee -a "$LOG_DIR/v03_codex_sentinel_d1.log"

echo ""
echo "--- D4: Ternary tie/equipoise sentinel (10% pairwise sample) ---"
python3 -u -m psycheeval.judge ternary-sample \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges "$CODEX_JUDGES" \
    --workers "$WORKERS" \
    --pairs "$ALL_PAIRS" 2>&1 | tee -a "$LOG_DIR/v03_codex_sentinel_d4.log"

echo ""
echo "--- D2: Paraphrased anchored sentinel (15% scalar sample) ---"
python3 -u -m psycheeval.judge score \
    --tag "$TAG" \
    --pilot "$PILOT" \
    --judges "$CODEX_JUDGES" \
    --workers "$WORKERS" \
    --rubric paraphrased_anchored \
    --sample-pct 15 2>&1 | tee -a "$LOG_DIR/v03_codex_sentinel_d2.log"

echo ""
echo "=== Stage 5: Codex pipeline complete ==="
echo "Outputs:              $(wc -l < runs/$TAG/assistant_outputs.jsonl)"
echo "Scalar scores:        $(wc -l < runs/$TAG/anchored_judge_scores.jsonl 2>/dev/null || echo 0)"
echo "Pairwise:             $(wc -l < runs/$TAG/pairwise_scores.jsonl 2>/dev/null || echo 0)"
echo "Pairwise swap:        $(wc -l < runs/$TAG/pairwise_swap_scores.jsonl 2>/dev/null || echo 0)"
echo "D1 same-orientation:  $(wc -l < runs/$TAG/same_orientation_swap_scores.jsonl 2>/dev/null || echo 0)"
echo "D2 paraphrased:       $(wc -l < runs/$TAG/paraphrased_anchored_scores.jsonl 2>/dev/null || echo 0)"
echo "D4 ternary:           $(wc -l < runs/$TAG/pairwise_ternary_scores.jsonl 2>/dev/null || echo 0)"
echo ""
echo "Next steps (burn Claude cap):"
echo "  Opus generation:  python3 -m psycheeval.run --pilot $PILOT --tag $TAG --authors opus --conditions $NEW_CONDITIONS --workers 1"
echo "  Opus judging:     python3 -m psycheeval.judge score --tag $TAG --pilot $PILOT --judges opus --rubric anchored --workers 1"
echo "  Opus pairwise:    python3 -m psycheeval.judge pairwise --tag $TAG --pilot $PILOT --judges opus --pairs '\$ALL_PAIRS' --scope same_author_only --ab-ba-mandatory --workers 1"
