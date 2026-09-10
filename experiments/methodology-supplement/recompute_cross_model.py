#!/usr/bin/env python3
"""Recompute cross-model analysis from corrected GPT-5.4 evaluations.

Reads the 4 narrative GPT evaluation files + Opus/GPT corpus GTs,
recomputes experiment1 and experiment2 JSONs, and prints a summary
of changes vs the old (flawed) data.

Usage:
    cd psyche/experiments/methodology-supplement
    uv run python recompute_cross_model.py
"""

import json
from pathlib import Path

PROFILES = Path(__file__).parent.parent.parent / "profiles" / "analysis"
SUPPLEMENT = Path(__file__).parent

# Ground truths
OPUS_GT = {"N": 51.1, "E": 28.3, "O": 88.6, "A": 36.4, "C": 61.4}
GPT_GT = {"N": 69.0, "E": 36.0, "O": 91.0, "A": 52.0, "C": 55.0}

# Merged profile (from 39 instruments + interview)
# The subject's merged Big Five ground truth is PRIVATE. It is read at runtime
# from a gitignored file (psyche/benchmark/ground_truth.json — see
# benchmark/.gitignore); the committed fallback is a synthetic midpoint profile
# so this script stays runnable from a public checkout. Anything computed
# against the fallback is a placeholder, not the subject's data.
_GT_FILE = Path.home() / "claudeworkspace/psyche/benchmark/ground_truth.json"
MERGED_GT = (json.loads(_GT_FILE.read_text()) if _GT_FILE.exists()
             else {"N": 50.0, "E": 50.0, "O": 50.0, "A": 50.0, "C": 50.0})

CONDITIONS = {
    "old": "narrative-subject-llm-gpt54.json",
    "1m": "narrative-subject-1m-llm-gpt54.json",
    "filtered": "narrative-subject-filtered-llm-gpt54.json",
    "long": "narrative-subject-long-llm-gpt54.json",
}

DOMAINS = ["N", "E", "O", "A", "C"]


def load_gpt_scores(condition: str) -> dict[str, float]:
    """Load GPT domain scores for a condition."""
    path = PROFILES / CONDITIONS[condition]
    data = json.loads(path.read_text())
    return {d: data["big_five"]["domains"][d]["score"] for d in DOMAINS}


def load_opus_scores(condition: str) -> dict[str, float]:
    """Load Opus domain scores for a condition."""
    suffix = {"old": "subject", "1m": "subject-1m", "filtered": "subject-filtered", "long": "subject-long"}
    path = PROFILES / f"narrative-{suffix[condition]}-llm-claude.json"
    data = json.loads(path.read_text())
    return {d: data["big_five"]["domains"][d]["score"] for d in DOMAINS}


def compute_deltas(eval_scores: dict, gt: dict) -> dict:
    """Compute per-domain deltas and mean absolute delta."""
    deltas = {d: round(eval_scores[d] - gt[d], 1) for d in DOMAINS}
    abs_deltas = {d: round(abs(deltas[d]), 1) for d in DOMAINS}
    mean_abs = round(sum(abs_deltas.values()) / len(DOMAINS), 1)
    return {"deltas": deltas, "abs_deltas": abs_deltas, "mean_abs_delta": mean_abs}


def main():
    # Check all files exist
    missing = []
    for cond, fname in CONDITIONS.items():
        if not (PROFILES / fname).exists():
            missing.append(cond)
    if missing:
        print(f"ERROR: Missing GPT files for: {missing}")
        print("Run remaining conditions first:")
        level_map = {"old": "subject", "1m": "subject-1m", "filtered": "subject-filtered", "long": "subject-long"}
        for m in missing:
            print(f"  uv run python scripts/analyze_narratives.py --level {level_map[m]} --skip-empath --backend codex")
        return

    # Load all GPT scores
    gpt_scores = {cond: load_gpt_scores(cond) for cond in CONDITIONS}
    opus_scores = {cond: load_opus_scores(cond) for cond in CONDITIONS}

    print("=" * 70)
    print("CORRECTED GPT-5.4 Narrative Evaluations")
    print("=" * 70)

    # Print GPT scores table
    print("\nGPT-5.4 Domain Scores:")
    print(f"{'Condition':>12} {'N':>6} {'E':>6} {'O':>6} {'A':>6} {'C':>6}")
    for cond in CONDITIONS:
        s = gpt_scores[cond]
        print(f"{cond:>12} {s['N']:6.1f} {s['E']:6.1f} {s['O']:6.1f} {s['A']:6.1f} {s['C']:6.1f}")

    # Experiment 1: GPT eval vs GPT GT
    print("\n--- Experiment 1: GPT eval vs GPT GT ---")
    gpt_vs_gpt_gt = {}
    for cond in CONDITIONS:
        result = compute_deltas(gpt_scores[cond], GPT_GT)
        gpt_vs_gpt_gt[cond] = result
        print(f"{cond:>12}: mean |Δ| = {result['mean_abs_delta']}")

    # Rankings
    gpt_ranking = sorted(CONDITIONS.keys(), key=lambda c: gpt_vs_gpt_gt[c]["mean_abs_delta"])
    opus_vs_opus_gt = {}
    for cond in CONDITIONS:
        opus_vs_opus_gt[cond] = compute_deltas(opus_scores[cond], OPUS_GT)
    opus_ranking = sorted(CONDITIONS.keys(), key=lambda c: opus_vs_opus_gt[c]["mean_abs_delta"])

    print(f"\nOpus ranking (best→worst): {opus_ranking}")
    print(f"GPT ranking  (best→worst): {gpt_ranking}")
    print(f"Rankings {'AGREE' if opus_ranking == gpt_ranking else 'DISAGREE'}")

    # Check if old GPT rankings were: old > long > filtered > 1m
    old_gpt_ranking = ["old", "long", "filtered", "1m"]
    print(f"\nOld (flawed) GPT ranking: {old_gpt_ranking}")
    print(f"New (corrected) GPT ranking: {gpt_ranking}")
    print(f"Rankings {'CHANGED' if old_gpt_ranking != gpt_ranking else 'UNCHANGED'}")

    # Experiment 2: Per-domain deltas
    print("\n--- Experiment 2: Per-Domain Deltas ---")

    # GPT eval vs Opus GT
    gpt_vs_opus_gt = {}
    for cond in CONDITIONS:
        gpt_vs_opus_gt[cond] = compute_deltas(gpt_scores[cond], OPUS_GT)

    # GPT eval vs Merged GT
    gpt_vs_merged_gt = {}
    for cond in CONDITIONS:
        gpt_vs_merged_gt[cond] = compute_deltas(gpt_scores[cond], MERGED_GT)
        print(f"{cond:>12} vs merged GT: mean |Δ| = {gpt_vs_merged_gt[cond]['mean_abs_delta']}")

    # Opus eval vs Merged GT (unchanged, for comparison)
    opus_vs_merged_gt = {}
    for cond in CONDITIONS:
        opus_vs_merged_gt[cond] = compute_deltas(opus_scores[cond], MERGED_GT)

    # C bias analysis
    print("\n--- C Bias Check ---")
    for cond in CONDITIONS:
        c_delta_vs_gpt_gt = gpt_vs_gpt_gt[cond]["deltas"]["C"]
        c_delta_vs_merged = gpt_vs_merged_gt[cond]["deltas"]["C"]
        print(f"{cond:>12}: C vs GPT GT = {c_delta_vs_gpt_gt:+.1f}, C vs merged = {c_delta_vs_merged:+.1f}")

    # N comparison (the robust finding)
    print("\n--- N Inflation Check (should agree across evaluators) ---")
    for cond in CONDITIONS:
        opus_n = opus_vs_opus_gt[cond]["deltas"]["N"]
        gpt_n = gpt_vs_gpt_gt[cond]["deltas"]["N"]
        print(f"{cond:>12}: Opus N delta = {opus_n:+.1f}, GPT N delta = {gpt_n:+.1f}")

    # Write experiment1 JSON
    exp1 = {
        "experiment": "cross_model_ground_truth",
        "date": "2026-03-19",
        "note": "CORRECTED: GPT evaluations rerun through proper pipeline with system prompt, full chunking",
        "gpt54_corpus_gt": GPT_GT,
        "opus_corpus_gt": OPUS_GT,
        "merged_gt": MERGED_GT,
        "gt_difference": {d: round(GPT_GT[d] - OPUS_GT[d], 1) for d in DOMAINS},
        "gpt_eval_vs_gpt_gt": gpt_vs_gpt_gt,
        "opus_ranking": opus_ranking,
        "gpt_ranking": gpt_ranking,
    }

    # Write experiment2 JSON
    exp2 = {
        "experiment": "per_domain_deltas",
        "date": "2026-03-19",
        "note": "CORRECTED: GPT evaluations rerun through proper pipeline",
        "opus_eval_vs_opus_gt": opus_vs_opus_gt,
        "opus_eval_vs_merged_gt": opus_vs_merged_gt,
        "gpt_eval_vs_opus_gt": gpt_vs_opus_gt,
        "gpt_eval_vs_merged_gt": gpt_vs_merged_gt,
    }

    # Save
    exp1_path = SUPPLEMENT / "experiment1-cross-model-gt.json"
    exp2_path = SUPPLEMENT / "experiment2-per-domain-deltas.json"

    exp1_path.write_text(json.dumps(exp1, indent=2))
    exp2_path.write_text(json.dumps(exp2, indent=2))

    print(f"\nSaved: {exp1_path}")
    print(f"Saved: {exp2_path}")

    # Summary of what changed
    print("\n" + "=" * 70)
    print("SUMMARY: What Changed")
    print("=" * 70)
    if gpt_ranking == opus_ranking:
        print("*** RANKINGS NOW AGREE — ranking inversion was a prompting artifact ***")
        print("Outcome B: Remove 'evaluator-dependent' qualification. STRENGTHENS claims.")
    elif gpt_ranking[0] != "old":
        print("*** RANKINGS PARTIALLY ALIGN — old is no longer GPT's best ***")
        print("Outcome C: Partial revision needed.")
    else:
        print("*** RANKINGS STILL INVERT — prompting wasn't the cause ***")
        print("Outcome A: Keep current framing, note prompting was fixed.")


if __name__ == "__main__":
    main()
