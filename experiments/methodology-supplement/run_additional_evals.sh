#!/usr/bin/env bash
set -euo pipefail

# Run 3 additional Opus evaluations for filtered and long conditions
# to produce confidence intervals matching old/1M methodology.
# Existing results are preserved as run-1.

ANALYSIS_DIR="$HOME/claudeworkspace/psyche/analysis"
PROFILES_DIR="$HOME/claudeworkspace/psyche/profiles/analysis"
OUTPUT_DIR="$HOME/claudeworkspace/psyche/experiments/methodology-supplement/additional-runs"

mkdir -p "$OUTPUT_DIR"

# Copy existing single-run results as run-1
for condition in filtered long; do
    src="$PROFILES_DIR/narrative-subject-${condition}-llm-claude.json"
    if [ -f "$src" ]; then
        cp "$src" "$OUTPUT_DIR/narrative-subject-${condition}-llm-claude-run1.json"
        echo "Preserved existing $condition result as run-1"
    fi
done

# Run 3 additional evaluations for each condition
for run in 2 3 4; do
    for condition in subject-filtered subject-long; do
        echo "=== Running $condition evaluation run $run ==="

        cd "$ANALYSIS_DIR"

        # Run the analysis (skip empath, LLM only)
        if uv run python scripts/analyze_narratives.py --level "$condition" --skip-empath 2>&1; then
            # Move the result to numbered file
            short="${condition#subject-}"  # filtered or long
            src="$PROFILES_DIR/narrative-${condition}-llm-claude.json"
            dst="$OUTPUT_DIR/narrative-subject-${short}-llm-claude-run${run}.json"
            if [ -f "$src" ]; then
                cp "$src" "$dst"
                echo "Saved run $run for $short to $dst"
            fi
        else
            echo "FAILED: $condition run $run"
        fi

        echo "---"
    done
done

echo "All additional runs complete. Computing CIs..."

# Compute confidence intervals
cd "$HOME/claudeworkspace/psyche"
python3 -c "
import json, os, math

output_dir = '$OUTPUT_DIR'
domains = ['N', 'E', 'O', 'A', 'C']

for condition in ['filtered', 'long']:
    scores_by_domain = {d: [] for d in domains}

    for run in range(1, 5):
        path = os.path.join(output_dir, f'narrative-subject-{condition}-llm-claude-run{run}.json')
        if os.path.exists(path):
            data = json.loads(open(path).read())
            for d in domains:
                score = data.get('big_five', {}).get('domains', {}).get(d, {}).get('score')
                if score is not None:
                    scores_by_domain[d].append(score)

    print(f'=== {condition} (n={len(scores_by_domain[\"N\"])} runs) ===')
    result = {}
    for d in domains:
        scores = scores_by_domain[d]
        if len(scores) >= 2:
            mean = sum(scores) / len(scores)
            std = math.sqrt(sum((x - mean) ** 2 for x in scores) / (len(scores) - 1))
            ci = 1.96 * std / math.sqrt(len(scores))
            result[d] = {'mean': round(mean, 1), 'std': round(std, 1), 'ci95': round(ci, 1), 'scores': scores}
            print(f'  {d}: {mean:.1f} +/- {ci:.1f} (std={std:.1f}, scores={scores})')
        else:
            result[d] = {'mean': scores[0] if scores else None, 'std': None, 'ci95': None, 'scores': scores}
            print(f'  {d}: {scores[0] if scores else \"N/A\"} (single run, no CI)')

    with open(os.path.join(output_dir, f'{condition}-confidence-intervals.json'), 'w') as f:
        json.dump(result, f, indent=2)

print('Done. CI results saved.')
"
