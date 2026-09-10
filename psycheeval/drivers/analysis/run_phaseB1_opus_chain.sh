#!/usr/bin/env bash
# Cap-BOUND Opus-4.7 chain (pinned claude-opus-4-7). Order per prereg_B1 §9:
#   1. target-conditioned, cross-provider PRIMARY (gpt-authored, 160 pairs)
#   2. target-conditioned, same-provider HALO    (opus-authored, 79 pairs)
#   3. two-axis cross-primary, then two-axis halo
# 30-min inter-pass sleep rides the rolling 5h cap window; the runner's internal
# backoff handles short caps, the wrapper handles long outages. Fully resumable.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 2
D=drivers/analysis
S=1800

bash "$D/run_until_complete.sh" logs/phaseB1_opus_tj_crossprimary.log $S -- \
     python3 "$D/phaseB1_target_judge_run.py" opus gpt_authored
bash "$D/run_until_complete.sh" logs/phaseB1_opus_tj_halo.log $S -- \
     python3 "$D/phaseB1_target_judge_run.py" opus opus_authored
bash "$D/run_until_complete.sh" logs/phaseB1_opus_twoaxis_cross.log $S -- \
     python3 "$D/phaseB1_two_axis_run.py" opus gpt_authored
bash "$D/run_until_complete.sh" logs/phaseB1_opus_twoaxis_halo.log $S -- \
     python3 "$D/phaseB1_two_axis_run.py" opus opus_authored
echo "OPUS chain DONE $(date -Is)"
