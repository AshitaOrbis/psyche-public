"""Top-level CLI for PsycheEval.

Usage:
    psycheeval source-hunt --pilot micro_pilot [--fallback-only]
    psycheeval generate-users --pilot micro_pilot [--model opus]
    psycheeval compile-profiles --pilot micro_pilot [--model opus]
    psycheeval generate-scenarios --pilot micro_pilot [--n 6]
    psycheeval run --pilot micro_pilot --tag 2026-04-20_micro [--dry-run]
    psycheeval judge-score --tag 2026-04-20_micro
    psycheeval judge-pairwise --tag 2026-04-20_micro
    psycheeval analyze --tag 2026-04-20_micro
    psycheeval validate-data
"""

from __future__ import annotations

import typer

from psycheeval import analyze as analyze_mod
from psycheeval import (
    compile_profile,
    generate,
    generate_scenarios,
    judge as judge_mod,
    run as run_mod,
    source_hunt,
)

app = typer.Typer(help="PsycheEval — personality-profile evaluation for AI assistants.", no_args_is_help=True)


@app.command("source-hunt")
def cmd_source_hunt(
    pilot: str = typer.Option("micro_pilot"),
    fallback_only: bool = typer.Option(False, "--fallback-only"),
):
    source_hunt.hunt_for_pilot(pilot_name=pilot, fallback_only=fallback_only)


@app.command("generate-users")
def cmd_generate_users(
    pilot: str = typer.Option("micro_pilot"),
    model: str = typer.Option("opus"),
):
    generate.generate_for_pilot(pilot_name=pilot, model_key=model)


@app.command("compile-profiles")
def cmd_compile_profiles(
    pilot: str = typer.Option("micro_pilot"),
    model: str = typer.Option("opus"),
):
    compile_profile.compile_for_pilot(pilot_name=pilot, model_key=model)


@app.command("generate-scenarios")
def cmd_generate_scenarios(
    pilot: str = typer.Option("micro_pilot"),
    n: int = typer.Option(6),
    model: str = typer.Option("opus"),
):
    generate_scenarios.generate_for_pilot(pilot_name=pilot, n=n, model_key=model)


@app.command("run")
def cmd_run(
    pilot: str = typer.Option("micro_pilot"),
    tag: str = typer.Option(None),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    run_mod.run_pilot(pilot_name=pilot, run_tag=tag, dry_run=dry_run)


@app.command("judge-score")
def cmd_judge_score(tag: str, pilot: str = typer.Option("micro_pilot")):
    judge_mod.score_all(tag, pilot)


@app.command("judge-pairwise")
def cmd_judge_pairwise(tag: str, pilot: str = typer.Option("micro_pilot")):
    judge_mod.pairwise_all(tag, pilot)


@app.command("analyze")
def cmd_analyze(tag: str, pilot: str = typer.Option("micro_pilot")):
    import json as _json
    from psycheeval import config as _cfg

    metrics = analyze_mod.compute_metrics(tag, pilot)
    _cfg.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (_cfg.REPORTS_DIR / f"metrics_{tag}.json").write_text(_json.dumps(metrics, indent=2, default=str))
    analyze_mod.write_report(tag, metrics, pilot)
    analyze_mod.write_failure_cards(tag, pilot)


@app.command("cost")
def cmd_cost(tag: str):
    """Aggregate per-run token usage + cost into runs/<tag>/cost_summary.json."""
    import json as _json

    from psycheeval.cost import aggregate_run_cost, write_cost_summary

    path = write_cost_summary(tag)
    summary = aggregate_run_cost(tag)
    typer.echo(_json.dumps(summary["totals"], indent=2))
    typer.echo(f"Wrote {path}")


@app.command("validate-data")
def cmd_validate():
    """Schema-validate everything on disk. Fast sanity check."""
    from psycheeval import config as _cfg
    from psycheeval.io import read_jsonl
    from psycheeval.models import (
        PersonaSeed,
        ProfileBundle,
        Scenario,
        SourcePacket,
        SynthUserRecord,
    )

    checks = [
        (_cfg.SEED_BANK_PUBLIC, PersonaSeed),
        (_cfg.SEED_BANK_SYNTHETIC, PersonaSeed),
    ]
    pilot_dir = _cfg.pilot_dir("micro_pilot")
    for name, cls in [
        ("source_packets.jsonl", SourcePacket),
        ("synthetic_user_records.jsonl", SynthUserRecord),
        ("profile_bundles.jsonl", ProfileBundle),
        ("scenarios.jsonl", Scenario),
    ]:
        p = pilot_dir / name
        if p.exists():
            checks.append((p, cls))

    all_ok = True
    for path, cls in checks:
        try:
            count = sum(1 for _ in read_jsonl(path, cls))
            typer.echo(f"  {path.relative_to(_cfg.PROJECT_ROOT)} — {count} records OK")
        except Exception as e:
            typer.echo(f"  {path} FAIL: {e}", err=True)
            all_ok = False
    if not all_ok:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
