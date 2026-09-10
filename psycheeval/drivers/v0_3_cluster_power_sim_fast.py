#!/usr/bin/env python3
"""
v0.3 Phase -1.2 — Cluster-bootstrap power simulation for D5 equivalence-margin TOST.

Uses v0.2 AB/BA controlled lo_win observed values + per-pair n_clusters to estimate:
- Expected power for ±3pp, ±5pp, ±7pp equivalence margins
- Cluster-resampled CIs (cluster unit: persona × scenario × author)
- Whether ±5pp is decidable at conditional 80% power

Run from psyche/psycheeval/.
Output: drivers/.v0_3_power_sim_output.txt
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path


METRICS_PATH = Path("reports/metrics_2026-04-26_v02_hard_codex_only.json")

D5_PAIRS = ["C3_vs_C5_CONTRACT", "C4_vs_C5_CONTRACT"]
MARGINS_PP = [3, 5, 7]
N_BOOTSTRAP = 500
N_SIMS = 100
SEED = 20260518


def _load_v02_ab_ba():
    metrics = json.loads(METRICS_PATH.read_text())
    return metrics["pairwise"]["ab_ba_position_audit_same_author"]


def _cluster_bootstrap_ci(cluster_records: list[list[int]], n_resamples: int, rng: random.Random) -> tuple[float, float, float]:
    """
    Cluster bootstrap on a binary outcome.

    cluster_records: list of clusters, each containing a list of binary outcomes (1=lo_wins).
    Resampling unit is the cluster, not the individual record.

    Returns (point, ci_low, ci_high).
    """
    n_clusters = len(cluster_records)
    flat = [v for cl in cluster_records for v in cl]
    n_total = len(flat)
    point = sum(flat) / n_total if n_total else 0.5

    means = []
    for _ in range(n_resamples):
        # Resample clusters with replacement
        sample_clusters = [cluster_records[rng.randrange(n_clusters)] for _ in range(n_clusters)]
        sample_flat = [v for cl in sample_clusters for v in cl]
        if sample_flat:
            means.append(sum(sample_flat) / len(sample_flat))
        else:
            means.append(0.5)
    means.sort()
    ci_low = means[int(0.025 * n_resamples)]
    ci_high = means[int(0.975 * n_resamples)]
    return point, ci_low, ci_high


def _simulate_pair_under_truth(
    n_clusters: int,
    records_per_cluster: int,
    true_lo_win_rate: float,
    cluster_icc: float,
    rng: random.Random,
) -> list[list[int]]:
    """
    Simulate cluster-correlated binary outcomes.

    cluster_icc: intra-cluster correlation. 0 = independent records within cluster.
                 ~0.3 = moderate clustering.
    Each cluster gets a cluster-specific mean drawn from Beta(α, β) chosen so the
    overall expected rate is true_lo_win_rate with given ICC.
    """
    # Beta-binomial trick: for binary outcomes, ICC = 1 / (1 + α + β) approximately
    # We pick α and β so that mean = true_lo_win_rate and ICC ≈ desired
    if cluster_icc <= 0:
        # Independent
        return [
            [1 if rng.random() < true_lo_win_rate else 0 for _ in range(records_per_cluster)]
            for _ in range(n_clusters)
        ]

    # For ICC = 1/(α+β+1), α+β = (1-ICC)/ICC
    sum_ab = (1 - cluster_icc) / cluster_icc
    alpha = true_lo_win_rate * sum_ab
    beta_param = (1 - true_lo_win_rate) * sum_ab

    clusters = []
    for _ in range(n_clusters):
        # Beta-distributed cluster mean
        cluster_mean = _sample_beta(alpha, beta_param, rng)
        cluster_outcomes = [1 if rng.random() < cluster_mean else 0 for _ in range(records_per_cluster)]
        clusters.append(cluster_outcomes)
    return clusters


def _sample_beta(alpha: float, beta_p: float, rng: random.Random) -> float:
    """Sample from Beta(α, β) using two gamma samples."""
    # rng.gammavariate(α, 1) is built-in
    x = rng.gammavariate(alpha, 1.0) if alpha > 0 else 0.0
    y = rng.gammavariate(beta_p, 1.0) if beta_p > 0 else 0.0
    return x / (x + y) if (x + y) > 0 else 0.5


def _tost_decision(cluster_records: list[list[int]], margin_pp: float, n_resamples: int, rng: random.Random) -> bool:
    """
    TOST via cluster bootstrap. Equivalence established within ±margin if the cluster-bootstrap
    95% CI for lo_win is fully inside [0.5 - margin, 0.5 + margin].
    """
    margin = margin_pp / 100.0
    _, ci_low, ci_high = _cluster_bootstrap_ci(cluster_records, n_resamples, rng)
    return (ci_low > 0.5 - margin) and (ci_high < 0.5 + margin)


def estimate_power(
    n_clusters: int,
    records_per_cluster: int,
    true_lo_win_rate: float,
    margin_pp: float,
    cluster_icc: float,
    n_sims: int = N_SIMS,
    n_bootstrap: int = N_BOOTSTRAP,
    seed: int = SEED,
) -> dict:
    """Estimate probability that cluster-bootstrap TOST rejects under stated truth."""
    rng = random.Random(seed)
    decisions = []
    for _ in range(n_sims):
        clusters = _simulate_pair_under_truth(
            n_clusters=n_clusters,
            records_per_cluster=records_per_cluster,
            true_lo_win_rate=true_lo_win_rate,
            cluster_icc=cluster_icc,
            rng=rng,
        )
        decisions.append(_tost_decision(clusters, margin_pp, n_bootstrap, rng))

    point = sum(decisions) / n_sims
    se = math.sqrt(point * (1 - point) / n_sims) if 0 < point < 1 else 0
    return {
        "true_lo_win_rate": true_lo_win_rate,
        "margin_pp": margin_pp,
        "n_clusters": n_clusters,
        "records_per_cluster": records_per_cluster,
        "total_n": n_clusters * records_per_cluster,
        "cluster_icc": cluster_icc,
        "power_estimate": point,
        "power_ci_low": max(0, point - 1.96 * se),
        "power_ci_high": min(1, point + 1.96 * se),
    }


def main():
    if not METRICS_PATH.exists():
        print(f"ERROR: metrics file not found at {METRICS_PATH}")
        print(f"Run from psyche/psycheeval/ directory.")
        sys.exit(1)

    ab_ba = _load_v02_ab_ba()

    print("v0.3 Cluster-Bootstrap Power Simulation for D5 TOST")
    print("=" * 80)
    print(f"Source: {METRICS_PATH}")
    print(f"Pairs analyzed: {D5_PAIRS}")
    print(f"Margins: {MARGINS_PP} pp")
    print(f"Bootstrap resamples per CI: {N_BOOTSTRAP}")
    print(f"Power simulations per scenario: {N_SIMS}")
    print()
    print("ICC scenarios: 0.0 (no clustering, optimistic) and 0.30 (moderate clustering, realistic)")
    print()

    for pair_id in D5_PAIRS:
        print(f"\n{'=' * 80}")
        print(f"## {pair_id}")
        print(f"{'=' * 80}")
        pair_data = ab_ba[pair_id]
        n_records_v02 = pair_data["n_pairs_with_ab_ba"]
        n_clusters_v02 = pair_data["n_clusters"]
        records_per_cluster = n_records_v02 // n_clusters_v02 if n_clusters_v02 else 2
        observed_controlled = pair_data["position_controlled_lo_win_rate"]
        ci_low = pair_data.get("controlled_bootstrap_ci95_low")
        ci_high = pair_data.get("controlled_bootstrap_ci95_high")

        print(f"v0.2 observed: n_records={n_records_v02}, n_clusters={n_clusters_v02}, "
              f"records/cluster={records_per_cluster}")
        print(f"  controlled_lo_win={observed_controlled:.4f}, CI=[{ci_low:.4f}, {ci_high:.4f}]")
        print(f"  Distance from 0.5: {abs(observed_controlled - 0.5) * 100:.2f}pp\n")

        # Test power at v0.2 alone and v0.2+v0.3 expansions
        # n_clusters: 120 (v0.2 alone), 240 (1x v0.3 add), 360 (2x v0.3 add)
        for n_clusters_test in [n_clusters_v02, 240, 360, 500]:
            total_n = n_clusters_test * records_per_cluster
            print(f"  n_clusters={n_clusters_test} (total_n={total_n}):")
            for icc in [0.0, 0.30]:
                for margin in MARGINS_PP:
                    # Power AT true equivalence (lo_win == 0.5) — best case
                    power_at_zero = estimate_power(
                        n_clusters=n_clusters_test,
                        records_per_cluster=records_per_cluster,
                        true_lo_win_rate=0.5,
                        margin_pp=margin,
                        cluster_icc=icc,
                    )
                    print(f"    ICC={icc:.2f}, margin±{margin}pp, true=0.5: "
                          f"power = {power_at_zero['power_estimate']:.1%} "
                          f"[{power_at_zero['power_ci_low']:.1%}, {power_at_zero['power_ci_high']:.1%}]")
                print()

    print("\n" + "=" * 80)
    print("INTERPRETATION GUIDE")
    print("=" * 80)
    print("- 'power if true=0.5' = best-case power: probability of declaring equivalence")
    print("  when the truth is exactly equivalent. <80% means even ideal conditions can't")
    print("  decide equivalence at that margin / n / ICC.")
    print("- ICC=0.0 (no clustering): each record is fully independent. Optimistic upper bound.")
    print("- ICC=0.30 (moderate clustering): realistic for persona x scenario x author cell structure.")
    print("- Compare power across n_clusters columns to see how much expansion improves decidability.")
    print("- D5 'decidable' = power at chosen margin reaches >=80% under realistic ICC.")
    print()


if __name__ == "__main__":
    main()
