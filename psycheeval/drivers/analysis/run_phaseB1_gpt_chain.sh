#!/usr/bin/env bash
# Cap-FREE GPT/codex chain: target-conditioned (mop-up) -> two-axis, full 239 x all authors.
# Waits for any already-running target-judge gpt arm first (avoid double-runs on one checkpoint).
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 2
D=drivers/analysis

while pgrep -f 'phaseB1_target_judge_run.py gpt-5.5 all' >/dev/null; do sleep 30; done

bash "$D/run_until_complete.sh" logs/phaseB1_gpt_targetjudge.log 120 -- \
     python3 "$D/phaseB1_target_judge_run.py" gpt-5.5 all
bash "$D/run_until_complete.sh" logs/phaseB1_gpt_twoaxis.log 120 -- \
     python3 "$D/phaseB1_two_axis_run.py" gpt-5.5 all
echo "GPT chain DONE $(date -Is)"
