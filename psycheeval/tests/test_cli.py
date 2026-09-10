"""Smoke tests for the typer CLI app.

Covers the wiring, not the work: that `--help` renders for the app and every
subcommand, and that each subcommand dispatches to its module function with
the parsed arguments. The underlying module functions are monkeypatched so
no network call, model invocation, or filesystem write happens here.

BACKLOG: pse-3 / Infrastructure "CLI tests — typer app smoke tests".
"""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from psycheeval.cli import app

runner = CliRunner()


def test_app_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    # Subcommands are listed in the top-level help.
    for cmd in (
        "source-hunt",
        "generate-users",
        "compile-profiles",
        "generate-scenarios",
        "run",
        "judge-score",
        "judge-pairwise",
        "analyze",
        "validate-data",
    ):
        assert cmd in result.stdout


def test_no_args_shows_help() -> None:
    # app is configured with no_args_is_help=True
    result = runner.invoke(app, [])
    assert result.exit_code != 0  # typer exits non-zero when only help is shown
    assert "Usage" in result.stdout or "Commands" in result.stdout


@pytest.mark.parametrize(
    "subcommand",
    [
        "source-hunt",
        "generate-users",
        "compile-profiles",
        "generate-scenarios",
        "run",
        "judge-score",
        "judge-pairwise",
        "analyze",
        "validate-data",
    ],
)
def test_subcommand_help(subcommand: str) -> None:
    result = runner.invoke(app, [subcommand, "--help"])
    assert result.exit_code == 0, result.stdout
    assert "Usage" in result.stdout


def test_judge_score_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """`judge-score` parses tag/pilot and calls judge.score_all (mocked)."""
    from psycheeval import judge as judge_mod

    captured: dict = {}

    def fake_score_all(tag: str, pilot: str):
        captured["tag"] = tag
        captured["pilot"] = pilot
        return

    monkeypatch.setattr(judge_mod, "score_all", fake_score_all)
    result = runner.invoke(app, ["judge-score", "2026-01-01_smoke", "--pilot", "micro_pilot"])
    assert result.exit_code == 0, result.stdout
    assert captured == {"tag": "2026-01-01_smoke", "pilot": "micro_pilot"}


def test_judge_pairwise_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """`judge-pairwise` parses tag/pilot and calls judge.pairwise_all (mocked)."""
    from psycheeval import judge as judge_mod

    captured: dict = {}

    def fake_pairwise_all(tag: str, pilot: str):
        captured["tag"] = tag
        captured["pilot"] = pilot
        return

    monkeypatch.setattr(judge_mod, "pairwise_all", fake_pairwise_all)
    result = runner.invoke(app, ["judge-pairwise", "2026-01-01_smoke"])
    assert result.exit_code == 0, result.stdout
    assert captured["tag"] == "2026-01-01_smoke"
    assert captured["pilot"] == "micro_pilot"  # default


def test_run_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    """`run` parses --pilot/--tag/--dry-run and calls run.run_pilot (mocked)."""
    from psycheeval import run as run_mod

    captured: dict = {}

    def fake_run_pilot(*, pilot_name: str, run_tag, dry_run: bool):
        captured["pilot_name"] = pilot_name
        captured["run_tag"] = run_tag
        captured["dry_run"] = dry_run
        return

    monkeypatch.setattr(run_mod, "run_pilot", fake_run_pilot)
    result = runner.invoke(
        app, ["run", "--pilot", "micro_pilot", "--tag", "2026-01-01_smoke", "--dry-run"]
    )
    assert result.exit_code == 0, result.stdout
    assert captured == {
        "pilot_name": "micro_pilot",
        "run_tag": "2026-01-01_smoke",
        "dry_run": True,
    }
