#!/usr/bin/env python3
"""Compute confidence intervals and convergent validity from multi-run results.

Reads results from profiles/analysis/runs/{level}/{backend}/run-*.json
and produces:
  - Per-condition CIs (detailed view)
  - Convergent validity table (three-anchor: self-report, blended, behavioral)
  - Method clustering analysis (where new conditions land relative to Psyche methods)

Usage:
  cd psyche/analysis
  uv run python scripts/compute_cis.py                    # detailed per-condition
  uv run python scripts/compute_cis.py --summary          # compact summary
  uv run python scripts/compute_cis.py --convergence      # three-anchor convergent validity
  uv run python scripts/compute_cis.py --level subject-sms  # filter to level
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

WORKSPACE = Path(__file__).parent.parent.parent.parent  # claudeworkspace/
RUNS_DIR = WORKSPACE / "psyche" / "profiles" / "analysis" / "runs"
PROFILE_JSON = WORKSPACE / "psyche" / "profiles" / "profile.json"
SELF_REPORT_JSON = WORKSPACE / "psyche" / "profiles" / "self-report-scored.json"
DOMAINS = ["N", "E", "O", "A", "C"]
DOMAIN_NAMES = {
    "N": "Neuroticism", "E": "Extraversion", "O": "Openness",
    "A": "Agreeableness", "C": "Conscientiousness",
}

# --- Psyche reference anchors (loaded from profile.json) ---

def load_psyche_anchors() -> dict:
    """Load all Psyche comparison anchors from profile.json and self-report-scored.json.

    Returns dict with keys:
      'blended'     — Psyche merged profile (weighted multi-method)
      'self_report' — Blended self-report score used in Psyche merge
      'sr_neo120'   — IPIP-NEO-120 only (shorter battery, noisier)
      'sr_neo300'   — IPIP-NEO-300 only (longer battery, more reliable)
      'interview'   — Structured interview estimate
      'llm_claude'  — Prior Opus corpus analysis
    Each is a {domain: score} dict.
    """
    profile = json.loads(PROFILE_JSON.read_text())
    anchors: dict[str, dict[str, float]] = {
        "blended": {},
        "self_report": {},
        "sr_neo120": {},
        "sr_neo300": {},
        "interview": {},
        "llm_claude": {},
    }

    for d in DOMAINS:
        domain_data = profile["big_five"]["domains"][d]
        anchors["blended"][d] = domain_data["final_score"]

        for est in domain_data["estimates"]:
            method = est["method"]
            if method == "self-report":
                anchors["self_report"][d] = round(est["score"], 1)
            elif method == "interview":
                anchors["interview"][d] = round(est["score"], 1)
            elif method == "llm-claude":
                anchors["llm_claude"][d] = round(est["score"], 1)

    # Load individual NEO battery scores and facets
    anchors["o6_adjusted"] = {}
    if SELF_REPORT_JSON.exists():
        sr_data = json.loads(SELF_REPORT_JSON.read_text())
        for inst, key in [("ipip-neo-120", "sr_neo120"), ("ipip-neo-300", "sr_neo300")]:
            scores = sr_data.get("results", {}).get(inst, {}).get("scores", [])
            facets_by_id = {}
            for s in scores:
                if s["scaleId"] in DOMAINS:
                    anchors[key][s["scaleId"]] = round(s["normalized"], 1)
                facets_by_id[s["scaleId"]] = round(s["normalized"], 1)

            # Compute O without O6 (Values/Liberalism) for this battery.
            # O6 uses IPIP items mapped to Costa & McCrae's "Values" facet,
            # which measures openness to re-examining social/political/religious
            # values. The items are normed on US populations and assume a
            # unidimensional liberal-conservative axis. This is not validated
            # outside an American political context — in multi-party systems
            # (e.g. Canada), high openness to political experience (voting for
            # 5 different parties across the spectrum) can score as "neutral"
            # because the items don't capture non-US political flexibility.
            o_facets = [facets_by_id.get(f"O{i}") for i in range(1, 7)]
            o_no_o6 = [f for i, f in enumerate(o_facets) if i != 5 and f is not None]
            if o_no_o6:
                anchors["o6_adjusted"][key] = round(sum(o_no_o6) / len(o_no_o6), 1)

    return anchors


# --- Data loading ---

def load_condition_runs(level_dir: Path, backend: str) -> list[dict]:
    """Load all run results for a condition."""
    backend_dir = level_dir / backend
    if not backend_dir.exists():
        return []

    results = []
    for f in sorted(backend_dir.glob("run-*-llm-*.json")):
        data = json.loads(f.read_text())
        results.append(data)
    return results


# Opus sometimes returns full domain names instead of single letters
_DOMAIN_ALIASES = {
    "neuroticism": "N", "extraversion": "E", "openness": "O",
    "agreeableness": "A", "conscientiousness": "C",
    "Neuroticism": "N", "Extraversion": "E", "Openness": "O",
    "Agreeableness": "A", "Conscientiousness": "C",
}


def extract_domain_scores(results: list[dict]) -> dict[str, list[float]]:
    """Extract per-domain scores from multiple run results.

    Handles both single-letter keys (N, E, O, A, C) and full domain name keys.
    Skips results with empty domains (corrupt/partial files).
    """
    scores: dict[str, list[float]] = {d: [] for d in DOMAINS}
    for r in results:
        bf = r.get("big_five", {})
        domains = bf.get("domains", {})
        if not domains:
            continue  # Skip corrupt/partial results

        for key, data in domains.items():
            d = _DOMAIN_ALIASES.get(key, key)
            if d in DOMAINS and isinstance(data, dict):
                score = data.get("score")
                if score is not None:
                    scores[d].append(score)
    return scores


# --- Statistics ---

def compute_ci(values: list[float]) -> tuple[float, float, float]:
    """Compute mean and 95% CI. Returns (mean, ci_lower, ci_upper)."""
    n = len(values)
    if n == 0:
        return (0.0, 0.0, 0.0)
    if n == 1:
        return (values[0], values[0], values[0])

    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1)
    sd = math.sqrt(variance)
    se = sd / math.sqrt(n)

    # t critical values for 95% CI
    t_crit = {2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 10: 2.228, 20: 2.086}
    t = t_crit.get(n - 1, 1.96)

    margin = t * se
    return (mean, mean - margin, mean + margin)


def compute_sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((x - mean) ** 2 for x in values) / (len(values) - 1))


def mean_abs_delta(means: dict[str, float], anchor: dict[str, float]) -> float:
    deltas = [abs(means[d] - anchor[d]) for d in DOMAINS if d in means and d in anchor]
    return sum(deltas) / len(deltas) if deltas else 0.0


def nearest_method(score: float, anchors: dict, domain: str) -> str:
    """Find which Psyche method the score is closest to."""
    methods = {
        "SR": anchors["self_report"].get(domain, 50),
        "Int": anchors["interview"].get(domain, 50),
        "LLM": anchors["llm_claude"].get(domain, 50),
    }
    return min(methods, key=lambda m: abs(score - methods[m]))


# --- Display functions ---

def print_condition_detail(
    level: str, backend: str, scores: dict[str, list[float]],
    anchors: dict, full_context: bool = False,
):
    """Print detailed per-condition results with three-anchor comparison."""
    n = max(len(v) for v in scores.values()) if scores else 0
    ctx = " (full-context)" if full_context else ""

    table = Table(title=f"{level} / {backend}{ctx} (n={n})")
    table.add_column("Domain", style="bold")
    table.add_column("Mean", justify="right")
    table.add_column("95% CI", justify="right")
    table.add_column("SD", justify="right")
    table.add_column("Δ SR", justify="right")
    table.add_column("Δ Blend", justify="right")
    table.add_column("Δ Intv", justify="right")
    table.add_column("Near", justify="center")
    table.add_column("Runs", justify="right", style="dim")

    for d in DOMAINS:
        vals = scores.get(d, [])
        if not vals:
            table.add_row(d, "—", *["—"] * 6, "0")
            continue

        mean, ci_lo, ci_hi = compute_ci(vals)
        sd = compute_sd(vals)

        d_sr = mean - anchors["self_report"].get(d, 50)
        d_blend = mean - anchors["blended"].get(d, 50)
        d_intv = mean - anchors["interview"].get(d, 50)
        near = nearest_method(mean, anchors, d)

        # Color by blended delta (legacy behavior)
        style = "green" if abs(d_blend) < 5 else ("yellow" if abs(d_blend) < 10 else "red")
        table.add_row(
            d,
            f"{mean:.1f}",
            f"[{ci_lo:.1f}, {ci_hi:.1f}]",
            f"{sd:.1f}",
            f"{d_sr:+.1f}",
            f"{d_blend:+.1f}",
            f"{d_intv:+.1f}",
            near,
            str(len(vals)),
            style=style,
        )

    console.print(table)


def print_summary_table(all_conditions: dict, anchors: dict):
    """Print compact summary with three-anchor deltas."""
    table = Table(title="Cross-Model Personality Evaluation Summary")
    table.add_column("Condition", style="bold")
    table.add_column("Backend", style="dim")
    table.add_column("n")
    for d in DOMAINS:
        table.add_column(d, justify="right")
    table.add_column("|Δ| SR", justify="right")
    table.add_column("|Δ| Bl", justify="right")

    # Reference rows
    table.add_row(
        "SR: NEO-120", "120-item", "—",
        *[f"{anchors['sr_neo120'].get(d, 0):.1f}" for d in DOMAINS],
        "—", "—",
        style="dim",
    )
    table.add_row(
        "SR: NEO-300", "300-item", "—",
        *[f"{anchors['sr_neo300'].get(d, 0):.1f}" for d in DOMAINS],
        "—", "—",
        style="dim",
    )
    table.add_row(
        "SR: Blended", "psychometric", "—",
        *[f"{anchors['self_report'].get(d, 0):.1f}" for d in DOMAINS],
        "—", "—",
        style="dim",
    )
    table.add_row(
        "Interview", "structured", "—",
        *[f"{anchors['interview'].get(d, 0):.1f}" for d in DOMAINS],
        "—", "—",
        style="dim",
    )
    table.add_row(
        "Psyche LLM", "opus-corpus", "—",
        *[f"{anchors['llm_claude'].get(d, 0):.1f}" for d in DOMAINS],
        "—", "—",
        style="dim",
    )
    table.add_row(
        "Psyche Blended", "multi-method", "—",
        *[f"{anchors['blended'].get(d, 0):.1f}" for d in DOMAINS],
        "—", "—",
        style="bold green",
    )
    # Separator
    table.add_section()

    for key, (scores, meta) in sorted(all_conditions.items()):
        n = max(len(v) for v in scores.values()) if scores else 0
        if n == 0:
            continue

        means = {}
        for d in DOMAINS:
            vals = scores.get(d, [])
            if vals:
                means[d] = sum(vals) / len(vals)

        mad_sr = mean_abs_delta(means, anchors["self_report"])
        mad_bl = mean_abs_delta(means, anchors["blended"])
        style = "green" if mad_bl < 5 else ("yellow" if mad_bl < 10 else "red")

        table.add_row(
            meta.get("level", key),
            meta.get("backend", "?"),
            str(n),
            *[f"{means.get(d, 0):.1f}" for d in DOMAINS],
            f"{mad_sr:.1f}",
            f"{mad_bl:.1f}",
            style=style,
        )

    console.print(table)


def print_convergence_table(all_conditions: dict, anchors: dict):
    """Print convergent validity analysis — per-domain method clustering.

    For each domain, shows where new conditions cluster relative to Psyche's
    three methods (self-report, interview, LLM-claude), with the blended
    score as reference. Helps answer: is LLM corpus inference stable across
    registers, and does it consistently track behavioral vs self-report evidence?
    """
    console.print("\n[bold cyan]═══ Convergent Validity: Method Clustering ═══[/bold cyan]")
    console.print("For each domain, shows Psyche method estimates and where", style="dim")
    console.print("new corpus conditions cluster. Near = closest Psyche method.\n", style="dim")

    # Collect condition means
    cond_means: dict[str, dict[str, float]] = {}
    for key, (scores, meta) in sorted(all_conditions.items()):
        label = meta.get("level", key)
        means = {}
        for d in DOMAINS:
            vals = scores.get(d, [])
            if vals:
                means[d] = round(sum(vals) / len(vals), 1)
        if means:
            cond_means[label] = means

    for d in DOMAINS:
        sr = anchors["self_report"].get(d, 0)
        intv = anchors["interview"].get(d, 0)
        llm = anchors["llm_claude"].get(d, 0)
        blend = anchors["blended"].get(d, 0)

        table = Table(title=f"{DOMAIN_NAMES[d]} ({d})")
        table.add_column("Source", style="bold")
        table.add_column("Score", justify="right")
        table.add_column("Δ from Blend", justify="right")
        table.add_column("Notes", style="dim")

        neo120 = anchors["sr_neo120"].get(d, 0)
        neo300 = anchors["sr_neo300"].get(d, 0)

        # Psyche methods
        table.add_row("SR: NEO-120", f"{neo120:.1f}", f"{neo120 - blend:+.1f}", "120-item battery")
        table.add_row("SR: NEO-300", f"{neo300:.1f}", f"{neo300 - blend:+.1f}", "300-item battery")

        # O6-adjusted scores for Openness only
        if d == "O":
            o6_120 = anchors["o6_adjusted"].get("sr_neo120")
            o6_300 = anchors["o6_adjusted"].get("sr_neo300")
            if o6_120 is not None:
                table.add_row("NEO-120 -O6", f"{o6_120:.1f}", f"{o6_120 - blend:+.1f}",
                              "O1-O5 only (excl Values/Liberalism)")
            if o6_300 is not None:
                table.add_row("NEO-300 -O6", f"{o6_300:.1f}", f"{o6_300 - blend:+.1f}",
                              "O1-O5 only (excl Values/Liberalism)")

        table.add_row("SR: Blended", f"{sr:.1f}", f"{sr - blend:+.1f}", "avg of both batteries")
        table.add_row("Interview", f"{intv:.1f}", f"{intv - blend:+.1f}", "structured interview")
        table.add_row("Psyche LLM", f"{llm:.1f}", f"{llm - blend:+.1f}", "prior Opus corpus run")
        table.add_row("Psyche Blended", f"{blend:.1f}", "—", "weighted merge", style="bold green")
        table.add_section()

        # New conditions
        for label, means in cond_means.items():
            score = means.get(d)
            if score is None:
                continue
            near = nearest_method(score, anchors, d)
            delta = score - blend
            style = "green" if abs(delta) < 5 else ("yellow" if abs(delta) < 10 else "red")
            table.add_row(label, f"{score:.1f}", f"{delta:+.1f}", f"nearest: {near}", style=style)

        console.print(table)

        # O6 footnote after the Openness table
        if d == "O":
            console.print("  O6 (Values/Liberalism) note: IPIP-NEO O6 items measure openness to", style="dim")
            console.print("  re-examining social/political/religious values, normed on US populations.", style="dim")
            console.print("  Not validated outside an American political context. In multi-party systems", style="dim")
            console.print("  (e.g. Canada), high political openness (voting for 5 different parties", style="dim")
            console.print("  across the spectrum) can score as neutral because the items assume a", style="dim")
            console.print("  unidimensional liberal-conservative axis. O6 scored 50.0 on both batteries.", style="dim")
            console.print("  NEO-300 -O6 (75.5) closes most of the gap to behavioral measures (83-88).", style="dim")

        console.print()

    # Domain summary: for each domain, what % of conditions cluster with behavioral evidence?
    console.print("[bold cyan]═══ Clustering Summary ═══[/bold cyan]")
    console.print("[dim]For each domain: how many conditions cluster nearest to each Psyche method.[/dim]\n")

    summary_table = Table(title="Method Clustering Counts")
    summary_table.add_column("Domain", style="bold")
    summary_table.add_column("→ Self-Report", justify="center")
    summary_table.add_column("→ Interview", justify="center")
    summary_table.add_column("→ LLM-Claude", justify="center")
    summary_table.add_column("Interpretation", style="dim")

    for d in DOMAINS:
        counts = {"SR": 0, "Int": 0, "LLM": 0}
        for label, means in cond_means.items():
            score = means.get(d)
            if score is not None:
                near = nearest_method(score, anchors, d)
                counts[near] += 1

        total = sum(counts.values())
        behavioral = counts["Int"] + counts["LLM"]
        if total > 0 and behavioral / total >= 0.8:
            interp = "behavioral convergence"
        elif total > 0 and counts["SR"] / total >= 0.5:
            interp = "self-report convergence"
        else:
            interp = "mixed"

        summary_table.add_row(
            d,
            str(counts["SR"]) if counts["SR"] else "—",
            str(counts["Int"]) if counts["Int"] else "—",
            str(counts["LLM"]) if counts["LLM"] else "—",
            interp,
        )

    console.print(summary_table)

    # Caveats
    console.print()
    console.print("Caveats:", style="dim")
    console.print("  Psyche Blended includes prior Opus LLM inference (~33% weight)", style="dim")
    console.print("  New conditions use same model (Opus) -- cannot independently validate LLM component", style="dim")
    console.print("  New conditions DO validate LLM stability across text registers", style="dim")
    console.print("  Self-Report is the only fully independent benchmark (no shared method)", style="dim")


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Compute CIs and convergent validity from multi-run results")
    parser.add_argument("--level", help="Filter to specific level")
    parser.add_argument("--summary", action="store_true", help="Compact summary table")
    parser.add_argument("--convergence", action="store_true", help="Three-anchor convergent validity analysis")
    args = parser.parse_args()

    if not RUNS_DIR.exists():
        console.print("[red]No runs directory found[/red]")
        sys.exit(1)

    anchors = load_psyche_anchors()
    all_conditions: dict[str, tuple[dict, dict]] = {}

    for level_dir in sorted(RUNS_DIR.iterdir()):
        if not level_dir.is_dir():
            continue

        level = level_dir.name
        if args.level and args.level not in level:
            continue

        full_context = "-fullctx" in level

        for backend_dir in sorted(level_dir.iterdir()):
            if not backend_dir.is_dir():
                continue
            backend = backend_dir.name

            results = load_condition_runs(level_dir, backend)
            if not results:
                continue

            scores = extract_domain_scores(results)
            meta = {"level": level, "backend": backend, "full_context": full_context}
            key = f"{level}/{backend}"
            all_conditions[key] = (scores, meta)

            if not args.summary and not args.convergence:
                print_condition_detail(level, backend, scores, anchors, full_context=full_context)
                console.print()

    if args.summary:
        print_summary_table(all_conditions, anchors)
    elif args.convergence:
        print_convergence_table(all_conditions, anchors)

    # Print overall status
    total_runs = sum(
        max(len(v) for v in scores.values())
        for scores, _ in all_conditions.values()
    )
    console.print(f"\n[bold]Total: {len(all_conditions)} conditions, {total_runs} runs[/bold]")


if __name__ == "__main__":
    main()
