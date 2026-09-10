#!/usr/bin/env bash
set -euo pipefail

# Run remaining evaluation runs for CI computation
# Filtered: needs runs 3, 4 (run 1 and 2 already done)
# Long: needs runs 2, 3, 4 (run 1 already done)

ANALYSIS_DIR="$HOME/claudeworkspace/psyche/analysis"
PROFILES_DIR="$HOME/claudeworkspace/psyche/profiles/analysis"
OUTPUT_DIR="$HOME/claudeworkspace/psyche/experiments/methodology-supplement/additional-runs"
LOG="$OUTPUT_DIR/eval-runs.log"

# Unset CLAUDECODE to avoid nested session error
unset CLAUDECODE 2>/dev/null || true

cd "$ANALYSIS_DIR"

echo "$(date -Iseconds) Starting remaining evaluation runs" | tee "$LOG"

# Define remaining runs: condition run_number
RUNS=(
  "subject-filtered 3"
  "subject-filtered 4"
  "subject-long 2"
  "subject-long 3"
  "subject-long 4"
)

for entry in "${RUNS[@]}"; do
  read -r condition run_num <<< "$entry"
  short="${condition#subject-}"

  echo "$(date -Iseconds) === $condition run $run_num ===" | tee -a "$LOG"

  if uv run python scripts/analyze_narratives.py --level "$condition" --skip-empath 2>&1 | tee -a "$LOG"; then
    src="$PROFILES_DIR/narrative-${condition}-llm-claude.json"
    dst="$OUTPUT_DIR/narrative-subject-${short}-llm-claude-run${run_num}.json"
    if [ -f "$src" ]; then
      cp "$src" "$dst"
      echo "$(date -Iseconds) Saved $short run $run_num" | tee -a "$LOG"
    fi
  else
    echo "$(date -Iseconds) FAILED: $condition run $run_num" | tee -a "$LOG"
  fi
done

echo "$(date -Iseconds) All runs complete. Computing CIs..." | tee -a "$LOG"

# Compute confidence intervals
cd "$HOME/claudeworkspace/psyche"
python3 << 'PYEOF'
import json, os, math

output_dir = os.path.expanduser("~/claudeworkspace/psyche/experiments/methodology-supplement/additional-runs")
opus_gt = {"N": 51.1, "E": 28.3, "O": 88.6, "A": 36.4, "C": 61.4}
domains = ["N", "E", "O", "A", "C"]

all_results = {}

for condition in ["filtered", "long"]:
    scores_by_domain = {d: [] for d in domains}
    mean_deltas = []

    for run in range(1, 5):
        path = os.path.join(output_dir, f"narrative-subject-{condition}-llm-claude-run{run}.json")
        if os.path.exists(path):
            data = json.loads(open(path).read())
            run_deltas = []
            for d in domains:
                score = data.get("big_five", {}).get("domains", {}).get(d, {}).get("score")
                if score is not None:
                    scores_by_domain[d].append(score)
                    run_deltas.append(abs(score - opus_gt[d]))
            if run_deltas:
                mean_deltas.append(sum(run_deltas) / len(run_deltas))

    n_runs = len(mean_deltas)
    print(f"\n=== {condition} ({n_runs} runs) ===")

    # Per-domain stats
    domain_stats = {}
    for d in domains:
        scores = scores_by_domain[d]
        if len(scores) >= 2:
            mean = sum(scores) / len(scores)
            std = math.sqrt(sum((x - mean) ** 2 for x in scores) / (len(scores) - 1))
            ci = 1.96 * std / math.sqrt(len(scores))
            domain_stats[d] = {"mean": round(mean, 1), "std": round(std, 1), "ci95": round(ci, 1), "scores": scores}
            print(f"  {d}: {mean:.1f} +/- {ci:.1f} (std={std:.1f}, scores={scores})")
        elif scores:
            domain_stats[d] = {"mean": scores[0], "std": None, "ci95": None, "scores": scores}
            print(f"  {d}: {scores[0]} (single run)")

    # Mean |delta| stats
    if len(mean_deltas) >= 2:
        md_mean = sum(mean_deltas) / len(mean_deltas)
        md_std = math.sqrt(sum((x - md_mean) ** 2 for x in mean_deltas) / (len(mean_deltas) - 1))
        md_ci = 1.96 * md_std / math.sqrt(len(mean_deltas))
        print(f"  Mean |Δ|: {md_mean:.1f} +/- {md_ci:.1f} (runs: {[round(x, 1) for x in mean_deltas]})")
        delta_stats = {"mean": round(md_mean, 1), "std": round(md_std, 1), "ci95": round(md_ci, 1), "runs": [round(x, 1) for x in mean_deltas]}
    else:
        delta_stats = {"mean": mean_deltas[0] if mean_deltas else None, "runs": [round(x, 1) for x in mean_deltas]}
        print(f"  Mean |Δ|: {mean_deltas[0]:.1f} (single run)")

    all_results[condition] = {"domains": domain_stats, "mean_abs_delta": delta_stats, "n_runs": n_runs}

# Save
out_path = os.path.join(output_dir, "confidence-intervals-final.json")
with open(out_path, "w") as f:
    json.dump(all_results, f, indent=2)
print(f"\nSaved to {out_path}")
PYEOF

echo "$(date -Iseconds) Done." | tee -a "$LOG"
