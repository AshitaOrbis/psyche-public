#!/usr/bin/env bash
# B2 generation chains. Arg: gpt | opus
#   gpt  -> codex author, cap-free, short retry sleeps
#   opus -> claude -p author, cap-bound, 30-min inter-pass sleeps (rides cap window)
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 2
D=drivers/analysis
WHO="${1:-gpt}"
if [ "$WHO" = "gpt" ]; then
  bash "$D/run_until_complete.sh" logs/phaseB2_gen_gpt.log 120 -- python3 "$D/phaseB2_generate.py" gpt-5.5
else
  bash "$D/run_until_complete.sh" logs/phaseB2_gen_opus.log 1800 -- python3 "$D/phaseB2_generate.py" opus
fi
echo "B2 gen ($WHO) DONE $(date -Is)"
