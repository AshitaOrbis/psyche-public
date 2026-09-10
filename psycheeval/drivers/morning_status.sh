#!/usr/bin/env bash
# Morning status: prints a one-page summary of what happened overnight.
# Safe to run anytime; pure read-only.
set -uo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)/src"

TAG="${TAG:-2026-04-26_v02_hard_codex_only}"
RUN_DIR="runs/$TAG"

echo "==================================================================="
echo "PsycheEval v0.2 — morning status @ $(date -Iseconds)"
echo "==================================================================="
echo ""

echo "## Active processes"
echo ""
ps -ef | grep -E "psycheeval|drivers/" | grep -v grep | awk '{printf "  PID %-8s %s\n", $2, substr($0, index($0, $8))}' || echo "  (none — all phases idle)"
echo ""

echo "## Corpus state (counts)"
echo ""
python3 - <<'EOF'
import json
from collections import Counter
from pathlib import Path

run_dir = Path("runs/2026-04-26_v02_hard_codex_only")

def load(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in path.open()]

out = load(run_dir / "assistant_outputs.jsonl")
sc = load(run_dir / "anchored_judge_scores.jsonl")
sc_legacy = load(run_dir / "judge_scores.jsonl")
pw = load(run_dir / "pairwise_scores.jsonl")
cap_events = load(run_dir / "cap_events.jsonl")

print(f"  outputs:           {len(out):>6}  ({dict(Counter(o['output_model'] for o in out))})")
print(f"    by condition:    {dict(Counter(o['condition'] for o in out))}")
print(f"  anchored scores:   {len(sc):>6}  ({dict(Counter(s['judge_model'] for s in sc))})")
print(f"  legacy scores:     {len(sc_legacy):>6}  ({dict(Counter(s['judge_model'] for s in sc_legacy))})")
print(f"  pairwise:          {len(pw):>6}  ({dict(Counter(p['judge_model'] for p in pw))})")
print(f"  cap events:        {len(cap_events):>6}")
EOF
echo ""

echo "## Cap events (most recent 5)"
echo ""
if [ -s "$RUN_DIR/cap_events.jsonl" ]; then
    tail -5 "$RUN_DIR/cap_events.jsonl" | python3 -c "
import json, sys
for line in sys.stdin:
    e = json.loads(line)
    print(f\"  {e['timestamp']}  {e['judge_model']}  attempt={e['backoff_attempt']}  rc={e['returncode']}\")
"
else
    echo "  (none — clean run)"
fi
echo ""

echo "## Checkpoints"
echo ""
shopt -s nullglob
ckpts=("$RUN_DIR"/checkpoint_*.json)
if [ ${#ckpts[@]} -eq 0 ]; then
    echo "  (none — no phase has hit cap exhaustion or completed)"
else
    for cp in "${ckpts[@]}"; do
        python3 -c "
import json
d = json.load(open('$cp'))
status = 'CAP-ABORTED' if d['cap_aborted'] else 'CLEAN'
print(f\"  {'$cp'.split('/')[-1]}: {status}\")
print(f\"    completed={d['completed_count']} pending={d['pending_count']} cap_events={d['cap_event_count']}\")
print(f\"    last successful: {d['last_successful_record_id']}\")
print(f\"    timestamp: {d['timestamp']}\")
print(f\"    resume: {d['suggested_resume_command']}\")
"
    done
fi
echo ""

echo "## Recent log tails"
echo ""
for log in logs/phase1_5_codex_gen.log logs/phase1_6_codex_score.log logs/phase1_7_codex_pairwise.log logs/phase2_opus_author.log logs/phase3_1_opus_score.log logs/phase3_2_opus_pairwise.log logs/opus_nightly_orchestrator.log; do
    if [ -s "$log" ]; then
        echo "### $log (last 3 lines)"
        tail -3 "$log" | sed 's/^/  /'
        echo ""
    fi
done

echo "==================================================================="
echo "Next steps if cap-aborted:"
echo "  Opus quota refreshes ~5h after the first cap event."
echo "  Re-run the suggested_resume_command from the relevant checkpoint."
echo "  Or: orchestrator is sleeping 6h from start, will auto-resume."
echo "==================================================================="
