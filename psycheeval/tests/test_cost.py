"""Tests for per-run cost / token aggregation (pse-4)."""

from __future__ import annotations

import json

import pytest

from psycheeval import config
from psycheeval.cost import aggregate_run_cost, write_cost_summary
from psycheeval.io import write_jsonl
from psycheeval.llm import MODELS
from psycheeval.models import (
    AssistantOutput,
    Condition,
    JudgeScore,
    JudgeScores,
    PairwiseScore,
)


def _scores(v: int = 3) -> JudgeScores:
    return JudgeScores(
        helpfulness=v,
        profile_fit=v,
        calibrated_challenge=v,
        anti_sycophancy=v,
        agency_support=v,
        epistemic_hygiene=v,
        emotional_accuracy=v,
        boundary_safety=v,
        non_caricature=v,
        transfer_value=v,
    )


@pytest.fixture
def run_with_tokens(tmp_path, monkeypatch):
    """A run dir with author + judge + pairwise records carrying token counts."""
    runs_dir = tmp_path / "runs"
    monkeypatch.setattr(config, "RUNS_DIR", runs_dir)
    tag = "2026-01-01_costtest"
    run_d = config.run_dir(tag)
    run_d.mkdir(parents=True, exist_ok=True)

    # Author outputs: one priced (kimi), one CLI-billed (opus, no token counts).
    kimi_id = MODELS["kimi-k2.6"].resolved_id
    outputs = [
        AssistantOutput(
            run_id="r1", scenario_id="s1", user_id="u1", condition=Condition.C0,
            output_model=kimi_id, profile_text_supplied="",
            assistant_response="hi", tokens_in=100, tokens_out=200,
        ),
        AssistantOutput(
            run_id="r2", scenario_id="s1", user_id="u1", condition=Condition.C1,
            output_model="opus", profile_text_supplied="x",
            assistant_response="hello", tokens_in=None, tokens_out=None,
        ),
    ]
    write_jsonl(run_d / "assistant_outputs.jsonl", outputs)

    # Judge scores (priced kimi judge).
    judge = JudgeScore(
        judge_id="j1", judge_model=kimi_id, run_id="r1", scenario_id="s1",
        scores=_scores(), concise_rationale="ok", tokens_in=50, tokens_out=80,
    )
    write_jsonl(run_d / "judge_scores.jsonl", [judge])

    # Pairwise (priced kimi judge).
    pair = PairwiseScore(
        pairwise_id="p1", judge_id="j1", judge_model=kimi_id, scenario_id="s1",
        run_id_a="r1", run_id_b="r2", winner="A", confidence_0_to_1=0.7,
        why_winner_is_better="clearer", tokens_in=300, tokens_out=10,
    )
    write_jsonl(run_d / "pairwise_scores.jsonl", [pair])

    return tag


def test_aggregate_phases_and_totals(run_with_tokens):
    summary = aggregate_run_cost(run_with_tokens)

    assert summary["run_tag"] == run_with_tokens
    totals = summary["totals"]
    assert totals["calls"] == 4  # 2 author + 1 judge + 1 pairwise
    assert totals["tokens_in"] == 100 + 0 + 50 + 300
    assert totals["tokens_out"] == 200 + 0 + 80 + 10
    assert totals["tokens_total"] == totals["tokens_in"] + totals["tokens_out"]

    # Author phase: one record had no token counts -> counted as missing.
    author = summary["by_phase"]["author"]
    assert author["calls"] == 2
    assert author["calls_missing_tokens"] == 1
    assert author["tokens_in"] == 100


def test_dollar_cost_uses_per_token_rates(run_with_tokens):
    summary = aggregate_run_cost(run_with_tokens)
    spec = MODELS["kimi-k2.6"]

    # Only the kimi rows are priced. opus author row contributes no dollar cost.
    expected = (
        (100 + 50 + 300) * spec.cost_in_per_mtok
        + (200 + 80 + 10) * spec.cost_out_per_mtok
    )
    assert summary["totals"]["cost_usd"] == pytest.approx(round(expected, 6))
    # Author phase mixes a priced kimi row and an unpriced opus row -> still a
    # known (partial) cost for the phase.
    assert summary["by_phase"]["author"]["cost_usd"] is not None
    # The run total is partial because the opus author row has no per-token rate.
    assert summary["totals"]["cost_is_partial"] is True


def test_by_model_grouping(run_with_tokens):
    summary = aggregate_run_cost(run_with_tokens)
    kimi_id = MODELS["kimi-k2.6"].resolved_id
    assert kimi_id in summary["by_model"]
    assert "opus" in summary["by_model"]
    assert summary["by_model"]["opus"]["cost_usd"] is None  # CLI-billed, no rate


def test_write_cost_summary_roundtrip(run_with_tokens):
    path = write_cost_summary(run_with_tokens)
    assert path.exists()
    loaded = json.loads(path.read_text())
    assert loaded["run_tag"] == run_with_tokens
    assert loaded["totals"]["calls"] == 4


def test_empty_run_returns_zero_totals(tmp_path, monkeypatch):
    runs_dir = tmp_path / "runs"
    monkeypatch.setattr(config, "RUNS_DIR", runs_dir)
    tag = "2026-01-01_empty"
    (runs_dir / tag).mkdir(parents=True, exist_ok=True)
    summary = aggregate_run_cost(tag)
    assert summary["totals"]["calls"] == 0
    assert summary["totals"]["cost_usd"] is None
    assert summary["by_phase"] == {}
