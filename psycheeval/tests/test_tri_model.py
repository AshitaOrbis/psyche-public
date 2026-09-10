"""Tests for the GPT-5.5 / tri-model extension surface.

Covers:
- model registry has the tri-model entry with full metadata
- coverage planner returns expected record counts under different scopes
- judge↔author relation classifier handles exact_self / same_provider / cross_provider
- Wilson confidence intervals are computed correctly
- pre/post-tri-model analyzer halo buckets behave as documented
"""

from __future__ import annotations

import math

import pytest

from psycheeval import config
from psycheeval.analyze import (
    RELATION_CROSS_PROVIDER,
    RELATION_EXACT_SELF,
    RELATION_SAME_PROVIDER,
    RELATION_UNKNOWN,
    _judge_author_relation,
    _model_family,
    _provider_family,
    wilson_interval,
)
from psycheeval.judge import (
    PAIRWISE_SCOPE_EXHAUSTIVE,
    PAIRWISE_SCOPE_SAME_AUTHOR_ONLY,
    build_pairwise_plan,
    observed_pairwise_keys,
    pairwise_coverage_diagnostics,
)
from psycheeval.llm import MODELS


# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------


def test_model_registry_includes_gpt55_xhigh() -> None:
    spec = MODELS.get("gpt-5.5-xhigh")
    assert spec is not None, "gpt-5.5-xhigh must be registered"
    assert spec.provider == "codex-cli"
    assert spec.resolved_id == "gpt-5.5"


def test_gpt55_has_provider_family_and_reasoning_effort() -> None:
    spec = MODELS["gpt-5.5-xhigh"]
    assert spec.provider_family == "openai"
    assert spec.model_family == "gpt-5.5"
    assert spec.reasoning_effort == "xhigh"


def test_existing_gpt54_carries_family_metadata() -> None:
    """v0.1 GPT-5.4 entry was extended in the same change; ensure it didn't lose
    the back-fill or its xhigh effort matching past behaviour.
    """
    spec = MODELS["gpt-5.4"]
    assert spec.provider_family == "openai"
    assert spec.model_family == "gpt-5.4"
    assert spec.reasoning_effort == "xhigh"


def test_opus_registry_carries_family_metadata() -> None:
    spec = MODELS["opus"]
    assert spec.provider_family == "anthropic"
    assert spec.model_family == "claude-opus"


def test_deepseek_v4_pro_registry_is_openrouter_opt_in() -> None:
    spec = MODELS.get("deepseek-v4-pro")
    assert spec is not None, "deepseek-v4-pro must be explicitly registered"
    assert spec.provider == "openrouter-api"
    assert spec.resolved_id == "deepseek/deepseek-v4-pro"
    assert spec.provider_family == "deepseek"
    assert spec.model_family == "deepseek-v4-pro"


def test_default_judges_exclude_opus() -> None:
    assert "opus" not in config.JUDGE_MODELS
    assert config.OPUS_DEFERRED_JUDGE_MODELS == ["opus"]


# ---------------------------------------------------------------------------
# Model-family / provider parsing fallback
# ---------------------------------------------------------------------------


def test_model_family_string_parsing() -> None:
    assert _model_family("opus") == "claude-opus"
    assert _model_family("gpt-5.4") == "gpt-5.4"
    assert _model_family("gpt-5.5") == "gpt-5.5"
    assert _model_family("kimi-k2.6") == "kimi"
    assert _model_family("") == "unknown"


def test_provider_family_string_parsing() -> None:
    assert _provider_family("opus") == "anthropic"
    assert _provider_family("gpt-5.5") == "openai"
    assert _provider_family("kimi-k2.6") == "other"


# ---------------------------------------------------------------------------
# Judge↔author relation classifier
# ---------------------------------------------------------------------------


def test_relation_exact_self_same_model() -> None:
    assert _judge_author_relation("opus", "opus") == RELATION_EXACT_SELF
    assert _judge_author_relation("gpt-5.4", "gpt-5.4") == RELATION_EXACT_SELF


def test_relation_same_provider_different_model() -> None:
    assert _judge_author_relation("gpt-5.4", "gpt-5.5") == RELATION_SAME_PROVIDER
    assert _judge_author_relation("gpt-5.5", "gpt-5.4") == RELATION_SAME_PROVIDER


def test_relation_cross_provider() -> None:
    assert _judge_author_relation("opus", "gpt-5.4") == RELATION_CROSS_PROVIDER
    assert _judge_author_relation("opus", "gpt-5.5") == RELATION_CROSS_PROVIDER
    assert _judge_author_relation("gpt-5.5", "opus") == RELATION_CROSS_PROVIDER


def test_relation_metadata_fields_take_precedence() -> None:
    """When provider/family metadata is supplied explicitly it should be used
    instead of string parsing — guards against renamed model aliases.
    """
    rel = _judge_author_relation(
        "weird-alias-1",
        "weird-alias-2",
        output_provider_family="openai",
        output_model_family="gpt-5.4",
        judge_provider_family="openai",
        judge_model_family="gpt-5.5",
    )
    assert rel == RELATION_SAME_PROVIDER


def test_relation_unknown_when_provider_unrecognized() -> None:
    rel = _judge_author_relation("mystery-model", "another-mystery")
    assert rel == RELATION_UNKNOWN


# ---------------------------------------------------------------------------
# Wilson interval
# ---------------------------------------------------------------------------


def test_wilson_interval_zero_n() -> None:
    assert wilson_interval(0, 0) == (0.0, 0.0)


def test_wilson_interval_unanimous() -> None:
    """100% wins out of 10 should NOT have CI (1.0, 1.0) — Wilson tightens
    near boundaries but never degenerates."""
    lo, hi = wilson_interval(10, 10)
    assert hi == 1.0  # clipped
    assert 0.6 < lo < 1.0


def test_wilson_interval_balanced() -> None:
    """50% wins out of 100 should bracket 0.5 with a small margin."""
    lo, hi = wilson_interval(50, 100)
    assert lo < 0.5 < hi
    # known textbook value: ~0.404, ~0.596
    assert abs(lo - 0.404) < 0.01
    assert abs(hi - 0.596) < 0.01


def test_wilson_interval_known_value() -> None:
    """65 wins out of 100 → ~(0.554, 0.738)."""
    lo, hi = wilson_interval(65, 100)
    assert abs(lo - 0.554) < 0.01
    assert abs(hi - 0.738) < 0.01


# ---------------------------------------------------------------------------
# Coverage planner: deterministic counts on the v0.1 fixture
# ---------------------------------------------------------------------------


def _v01_pilot_present() -> bool:
    from psycheeval import config
    return (config.RUNS_DIR / "2026-04-20_micro" / "assistant_outputs.jsonl").exists()


pytestmark_skip_if_no_v01 = pytest.mark.skipif(
    not _v01_pilot_present(),
    reason="v0.1 pilot data not present — coverage planner test needs it",
)


@pytestmark_skip_if_no_v01
def test_planner_v01_two_model_exhaustive_count() -> None:
    """Brief §6: v0.1 expected pairwise records = 3504 with two judges."""
    plan, diag = build_pairwise_plan(
        "2026-04-20_micro",
        "micro_pilot",
        judges=["opus", "gpt-5.4"],
        scope=PAIRWISE_SCOPE_EXHAUSTIVE,
    )
    assert diag["expected_records"] == 3504, (
        f"v0.1 two-model exhaustive should produce 3504 records, got {diag['expected_records']}"
    )


@pytestmark_skip_if_no_v01
def test_planner_v01_one_judge_count_halves() -> None:
    plan, diag = build_pairwise_plan(
        "2026-04-20_micro",
        "micro_pilot",
        judges=["opus"],
        scope=PAIRWISE_SCOPE_EXHAUSTIVE,
    )
    assert diag["expected_records"] == 1752


@pytestmark_skip_if_no_v01
def test_planner_same_author_only_smaller_than_exhaustive() -> None:
    plan_e, diag_e = build_pairwise_plan(
        "2026-04-20_micro",
        "micro_pilot",
        judges=["opus", "gpt-5.4"],
        scope=PAIRWISE_SCOPE_EXHAUSTIVE,
    )
    plan_s, diag_s = build_pairwise_plan(
        "2026-04-20_micro",
        "micro_pilot",
        judges=["opus", "gpt-5.4"],
        scope=PAIRWISE_SCOPE_SAME_AUTHOR_ONLY,
    )
    assert diag_s["expected_records"] < diag_e["expected_records"]
    assert diag_s["filtered_scope"] > 0


@pytestmark_skip_if_no_v01
def test_coverage_diagnostics_strata_complete() -> None:
    plan, _ = build_pairwise_plan(
        "2026-04-20_micro",
        "micro_pilot",
        judges=["opus", "gpt-5.4"],
        scope=PAIRWISE_SCOPE_EXHAUSTIVE,
    )
    observed, _ = observed_pairwise_keys("2026-04-20_micro")
    cov = pairwise_coverage_diagnostics(plan, observed)
    # Every section is present and has at least one stratum
    for section_name in (
        "by_judge",
        "by_condition_pair",
        "by_persona_type_pair",
        "by_judge_condition_pair",
        "by_judge_author_pair",
        "by_same_vs_cross_author",
    ):
        assert section_name in cov
        assert len(cov[section_name]) > 0
    # Coverage percent is between 0 and 100 in stratum sections (skip the
    # top-level judge_status_summary which is a dict-of-lists, not cells).
    stratum_sections = (
        "by_judge",
        "by_condition_pair",
        "by_persona_type_pair",
        "by_judge_condition_pair",
        "by_judge_author_pair",
        "by_same_vs_cross_author",
    )
    for section_name in stratum_sections:
        for cell in cov[section_name].values():
            assert 0.0 <= cell["coverage_pct"] <= 100.0
            assert cell["expected"] >= cell["observed"]
            assert cell["quota_status"] in {"complete", "partial", "deferred", "empty"}


# ---------------------------------------------------------------------------
# Pair-whitelist parsing (already exists; sanity-check tri-model alias works)
# ---------------------------------------------------------------------------


def test_pair_whitelist_accepts_tri_model_targeted_set() -> None:
    """The brief's v0.2 targeted whitelist must parse without errors."""
    from psycheeval.judge import _parse_pair_whitelist
    spec = "C4:C0,C4:C1,C4:C1_padded,C4:C4_shuffled,C3:C4,C1:C1_padded,C4:C5@PI"
    parsed = _parse_pair_whitelist(spec)
    assert ("C0", "C4", False) in parsed
    assert ("C4", "C5", True) in parsed
    assert ("C1", "C1_padded", False) in parsed
    assert ("C4", "C4_shuffled", False) in parsed


# ---------------------------------------------------------------------------
# Cohen's κ (binary red-flag agreement)
# ---------------------------------------------------------------------------


def test_cohen_kappa_perfect_agreement() -> None:
    from psycheeval.analyze import cohen_kappa_binary
    pairs = [(True, True), (True, True), (False, False), (False, False)]
    assert cohen_kappa_binary(pairs) == 1.0


def test_cohen_kappa_perfect_disagreement_negative() -> None:
    from psycheeval.analyze import cohen_kappa_binary
    pairs = [(True, False), (False, True), (True, False), (False, True)]
    k = cohen_kappa_binary(pairs)
    assert k is not None and k < 0


def test_cohen_kappa_chance_agreement_near_zero() -> None:
    """A 2x2 table with equal cells should produce κ near 0."""
    from psycheeval.analyze import cohen_kappa_binary
    pairs = [(True, True), (True, False), (False, True), (False, False)]
    assert cohen_kappa_binary(pairs) == 0.0


def test_cohen_kappa_empty_returns_none() -> None:
    from psycheeval.analyze import cohen_kappa_binary
    assert cohen_kappa_binary([]) is None


def test_cohen_kappa_constant_returns_none() -> None:
    """If both raters return the same constant, κ is undefined."""
    from psycheeval.analyze import cohen_kappa_binary
    assert cohen_kappa_binary([(False, False)] * 50) is None


# ---------------------------------------------------------------------------
# Spearman ρ
# ---------------------------------------------------------------------------


def test_spearman_perfect_positive() -> None:
    from psycheeval.analyze import spearman_rho
    assert spearman_rho([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == 1.0


def test_spearman_perfect_negative() -> None:
    from psycheeval.analyze import spearman_rho
    assert spearman_rho([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) == -1.0


def test_spearman_undefined_on_constant_input() -> None:
    from psycheeval.analyze import spearman_rho
    assert spearman_rho([3, 3, 3, 3], [1, 2, 3, 4]) is None


def test_spearman_undefined_on_short_input() -> None:
    from psycheeval.analyze import spearman_rho
    assert spearman_rho([1], [2]) is None
    assert spearman_rho([], []) is None


# ---------------------------------------------------------------------------
# Inter-judge agreement end-to-end on synthetic records
# ---------------------------------------------------------------------------


def _make_legacy_score(run_id: str, judge: str, dim_value: int, red_flags: list[str]):
    from psycheeval.models import JudgeScore, JudgeScores
    return JudgeScore(
        judge_id=f"j_{judge}_{run_id}",
        judge_model=judge,
        run_id=run_id,
        scenario_id=f"scn_{run_id}",
        scores=JudgeScores(
            helpfulness=dim_value, profile_fit=dim_value, calibrated_challenge=dim_value,
            anti_sycophancy=dim_value, agency_support=dim_value, epistemic_hygiene=dim_value,
            emotional_accuracy=dim_value, boundary_safety=dim_value, non_caricature=dim_value,
            transfer_value=dim_value,
        ),
        red_flags=red_flags,
        concise_rationale="fixture",
    )


def test_inter_judge_agreement_perfect() -> None:
    """Two judges scoring identically should produce ρ = 1.0 on every dim
    and κ = 1.0 on every label that varies (None on constant labels)."""
    from psycheeval.analyze import compute_inter_judge_agreement
    from psycheeval.models import RedFlag
    scores = []
    # 8 outputs, both judges identical
    for i in range(8):
        for j in ("opus", "gpt-5.4"):
            flags = ["generic_slop"] if i < 4 else []
            scores.append(_make_legacy_score(f"r{i}", j, dim_value=(i % 5), red_flags=flags))
    out = compute_inter_judge_agreement(
        scores,
        label_vocab=[rf.value for rf in RedFlag],
        score_dimensions=["helpfulness"],
    )
    pair_key = next(iter(out))
    assert out[pair_key]["n_overlap"] == 8
    assert out[pair_key]["mean_dimension_spearman_rho"] == 1.0
    # generic_slop κ should be 1.0 (perfect)
    assert out[pair_key]["per_label_kappa"]["generic_slop"]["kappa"] == 1.0


def test_inter_judge_agreement_disagreement() -> None:
    """Two judges in disagreement on red-flag presence should produce κ < 1."""
    from psycheeval.analyze import compute_inter_judge_agreement
    from psycheeval.models import RedFlag
    scores = []
    for i in range(8):
        # Judge A flags first half; Judge B flags second half — perfect anti-correlation
        a_flags = ["generic_slop"] if i < 4 else []
        b_flags = [] if i < 4 else ["generic_slop"]
        scores.append(_make_legacy_score(f"r{i}", "opus", dim_value=i % 5, red_flags=a_flags))
        scores.append(_make_legacy_score(f"r{i}", "gpt-5.4", dim_value=i % 5, red_flags=b_flags))
    out = compute_inter_judge_agreement(
        scores,
        label_vocab=[rf.value for rf in RedFlag],
        score_dimensions=["helpfulness"],
    )
    pair_key = next(iter(out))
    assert out[pair_key]["per_label_kappa"]["generic_slop"]["kappa"] is not None
    assert out[pair_key]["per_label_kappa"]["generic_slop"]["kappa"] < 0  # worse than chance


def test_quota_status_classification() -> None:
    """Cell-level quota_status: complete / partial / deferred / empty."""
    from collections import Counter
    from psycheeval.judge import pairwise_coverage_diagnostics

    # Simulate a small plan with three judges and known observed records.
    plan = []
    for j in ("opus", "gpt-5.4", "gpt-5.5-xhigh"):
        for i in range(4):
            plan.append({
                "scenario_id": f"s{i}",
                "user_id": "u",
                "persona_type": "pure_synthetic",
                "judge_model": j,
                "author_a": "opus",
                "author_b": "opus",
                "cond_a": "C0",
                "cond_b": "C1",
                "run_id_a": f"a{i}",
                "run_id_b": f"b{i}",
                "canonical_key": (f"a{i}", f"b{i}", j),
            })
    # Observed: all 4 for gpt-5.4, 2 for gpt-5.5-xhigh, none for opus
    observed = set()
    for i in range(4):
        observed.add((f"a{i}", f"b{i}", "gpt-5.4"))
    for i in range(2):
        observed.add((f"a{i}", f"b{i}", "gpt-5.5-xhigh"))
    cov = pairwise_coverage_diagnostics(plan, observed)
    by_judge = cov["by_judge"]
    assert by_judge["gpt-5.4"]["quota_status"] == "complete"
    assert by_judge["gpt-5.5-xhigh"]["quota_status"] == "partial"
    assert by_judge["opus"]["quota_status"] == "deferred"
    assert cov["judge_status_summary"]["complete"] == ["gpt-5.4"]
    assert cov["judge_status_summary"]["partial"] == ["gpt-5.5-xhigh"]
    assert cov["judge_status_summary"]["deferred"] == ["opus"]


def test_inter_judge_agreement_no_overlap_skipped() -> None:
    """If two judges share zero outputs, the pair is omitted (not crashed)."""
    from psycheeval.analyze import compute_inter_judge_agreement
    from psycheeval.models import RedFlag
    scores = [
        _make_legacy_score("r1", "opus", 5, []),
        _make_legacy_score("r2", "gpt-5.4", 5, []),
        _make_legacy_score("r3", "gpt-5.5", 5, []),
    ]
    out = compute_inter_judge_agreement(
        scores,
        label_vocab=[rf.value for rf in RedFlag],
        score_dimensions=["helpfulness"],
    )
    assert out == {}
