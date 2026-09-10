#!/usr/bin/env bash
# Wait for Stage A (conditioning variants) to finish, then launch both B2
# generation chains (gpt cap-free + opus cap-bound). Detached.
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 2
D=drivers/analysis

while pgrep -f phaseB2_render_conditioning.py >/dev/null || [ ! -f data/phaseB2/conditioning_variants.json ]; do
  sleep 20
done
sleep 3
echo "Stage A complete $(date -Is); launching B2 generation chains"
setsid bash -c "exec bash $D/run_phaseB2_gen.sh gpt"  > logs/phaseB2_gen_gpt_chain.log  2>&1 < /dev/null &
setsid bash -c "exec bash $D/run_phaseB2_gen.sh opus" > logs/phaseB2_gen_opus_chain.log 2>&1 < /dev/null &
echo "launched gpt + opus generation chains $(date -Is)"
