#!/usr/bin/env bash
# Run the analyzer on whatever v0.2 data has accumulated so far.
# Useful overnight: even with partial Opus authoring/judging, the existing
# codex side has full coverage and the new C5_CONTRACT codex outputs land
# alongside it. Native diagnostics regenerate. Probe records are excluded
# fail-closed (per Phase 0 work).
set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH="$(pwd)/src"

TAG="${TAG:-2026-04-26_v02_hard_codex_only}"
PILOT="v02_hard_pilot"

echo "[$(date -Iseconds)] running analyzer on tag=$TAG (partial data ok)"
python3 -m psycheeval.analyze --tag "$TAG" --pilot "$PILOT" 2>&1

echo ""
echo "Outputs:"
echo "  reports/metrics_${TAG}.json         (canonical metrics)"
echo "  reports/psycheeval_v0_1_${PILOT}_${TAG}_autogen.md  (regenerated scaffold)"
echo "  reports/failure_cards_${TAG}.md     (12 worst-failure exemplars)"
echo ""
echo "Native v0.2 diagnostic blocks now included in metrics JSON:"
echo "  - pairwise.tie_rates_same_author"
echo "  - pairwise.pi_ps_split_same_author"
echo "  - pairwise.length_buckets_same_author (C5/C5_CONTRACT pairs)"
echo "  - pairwise.scenario_family_breakdowns_same_author"
echo "  - pairwise.cluster_bootstrap_ci_same_author"
echo "  - red_flag_stratification_legacy / _anchored"
echo "  - scalar_inter_judge_agreement_legacy / _anchored"
