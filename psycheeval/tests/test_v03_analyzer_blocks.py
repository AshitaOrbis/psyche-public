"""Smoke tests for v0.3 analyzer blocks D1, D2, D3, D4.

These tests verify the blocks return well-formed output on synthetic inputs.
They are NOT meant to test statistical correctness — that requires integration
with the full pipeline. They catch crashes, schema regressions, and obvious
arithmetic errors.

Run from psyche/psycheeval/:
    PYTHONPATH=src python3 -m pytest tests/test_v03_analyzer_blocks.py -v
"""

from __future__ import annotations

import pytest
from types import SimpleNamespace

from psycheeval.analyze import (
    _compute_same_orientation_sentinel,
    _compute_paraphrased_anchor_consistency,
    _compute_reward_hacking_diagnostics,
    _compute_tie_aware_reinterpretation,
    _spearman_rho,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pair_tagged(scn, run_a, run_b, judge, winner, cond_a, cond_b):
    """Build a pair_tagged_same_author entry matching the analyzer expectation."""
    rec = SimpleNamespace(
        scenario_id=scn,
        run_id_a=run_a,
        run_id_b=run_b,
        judge_model=judge,
        winner=winner,  # "A" | "B" | "no_meaningful_difference" | "tie"
    )
    # compute_metrics builds pair_tagged entries with the pairwise record under
    # key "ps" (not "record"); the D1/D4 blocks read p["ps"]. Match that here.
    return {"ps": rec, "cond_a": cond_a, "cond_b": cond_b}


def _make_pair_record(scn, run_a, run_b, judge, winner):
    return SimpleNamespace(
        scenario_id=scn, run_id_a=run_a, run_id_b=run_b,
        judge_model=judge, winner=winner,
    )


# ---------------------------------------------------------------------------
# Spearman rho tests
# ---------------------------------------------------------------------------


def test_spearman_perfect_positive():
    assert abs(_spearman_rho([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) - 1.0) < 1e-9


def test_spearman_perfect_negative():
    assert abs(_spearman_rho([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) - (-1.0)) < 1e-9


def test_spearman_insufficient_data_returns_none():
    assert _spearman_rho([1, 2], [1, 2]) is None
    assert _spearman_rho([], []) is None


def test_spearman_mismatched_lengths():
    assert _spearman_rho([1, 2, 3], [1, 2]) is None


def test_spearman_all_ties_returns_none():
    # All x are identical → denominator is zero
    assert _spearman_rho([5, 5, 5, 5], [1, 2, 3, 4]) is None


# ---------------------------------------------------------------------------
# D1 — Same-orientation sentinel
# ---------------------------------------------------------------------------


def test_d1_empty_inputs():
    result = _compute_same_orientation_sentinel([], [])
    assert result == {}


def test_d1_no_matched_rejudgments():
    pair_tagged = [_make_pair_tagged("s1", "r_a", "r_b", "gpt-5.4", "A", "C5", "C5_CONTRACT")]
    result = _compute_same_orientation_sentinel(pair_tagged, [])
    assert result == {}


def test_d1_perfect_consistency():
    pair_tagged = [
        _make_pair_tagged(f"s{i}", f"a{i}", f"b{i}", "gpt-5.4", "A", "C5", "C5_CONTRACT")
        for i in range(4)
    ]
    rejudges = [
        _make_pair_record(f"s{i}", f"a{i}", f"b{i}", "gpt-5.4", "A")
        for i in range(4)
    ]
    result = _compute_same_orientation_sentinel(pair_tagged, rejudges)
    pair_id = "C5_vs_C5_CONTRACT"
    assert pair_id in result
    assert result[pair_id]["n_pairs_with_same_orientation"] == 4
    assert result[pair_id]["n_winner_flip"] == 0
    assert result[pair_id]["same_orientation_flip_rate"] == 0.0


def test_d1_some_flips():
    pair_tagged = [
        _make_pair_tagged(f"s{i}", f"a{i}", f"b{i}", "gpt-5.4", "A", "C5", "C5_CONTRACT")
        for i in range(4)
    ]
    rejudges = [
        _make_pair_record("s0", "a0", "b0", "gpt-5.4", "A"),
        _make_pair_record("s1", "a1", "b1", "gpt-5.4", "A"),
        _make_pair_record("s2", "a2", "b2", "gpt-5.4", "A"),
        _make_pair_record("s3", "a3", "b3", "gpt-5.4", "B"),  # flip
    ]
    result = _compute_same_orientation_sentinel(pair_tagged, rejudges)
    pair_id = "C5_vs_C5_CONTRACT"
    assert result[pair_id]["same_orientation_flip_rate"] == 0.25


def test_d1_per_judge_breakdown():
    pair_tagged = [
        _make_pair_tagged("s1", "a1", "b1", "gpt-5.4", "A", "C5", "C5_CONTRACT"),
        _make_pair_tagged("s1", "a1", "b1", "opus", "A", "C5", "C5_CONTRACT"),
    ]
    rejudges = [
        _make_pair_record("s1", "a1", "b1", "gpt-5.4", "A"),
        _make_pair_record("s1", "a1", "b1", "opus", "B"),
    ]
    result = _compute_same_orientation_sentinel(pair_tagged, rejudges)
    pair_id = "C5_vs_C5_CONTRACT"
    by_judge = result[pair_id]["by_judge"]
    assert by_judge["gpt-5.4"]["same_orientation_flip_rate"] == 0.0
    assert by_judge["opus"]["same_orientation_flip_rate"] == 1.0
    assert result[pair_id]["per_judge_spread"] == 1.0


# ---------------------------------------------------------------------------
# D2 — Paraphrased anchor consistency
# ---------------------------------------------------------------------------


def _make_anchored_score(oid, judge, **dims):
    # Mirror the real AnchoredJudgeScore shape: keyed by run_id, dimensions
    # nested under .scores. (The earlier fixture used assistant_output_id +
    # top-level dims, which masked a join bug in the D2 block — it returned
    # no_paraphrased_records on real records.)
    return SimpleNamespace(run_id=oid, judge_model=judge, scores=SimpleNamespace(**dims))


def test_d2_empty_inputs():
    result = _compute_paraphrased_anchor_consistency([], [])
    assert result["n_matched"] == 0
    assert result["status"] == "no_paraphrased_records"


def test_d2_no_paraphrased_records():
    orig = [_make_anchored_score("o1", "gpt-5.4", helpfulness=7.0)]
    result = _compute_paraphrased_anchor_consistency(orig, [])
    assert result["n_matched"] == 0


def test_d2_perfect_match_no_shift():
    dims = ["helpfulness", "profile_fit", "calibrated_challenge"]
    orig = [
        _make_anchored_score(f"o{i}", "gpt-5.4", helpfulness=5+i*0.5,
                              profile_fit=5+i*0.5, calibrated_challenge=5+i*0.5)
        for i in range(5)
    ]
    para = [
        _make_anchored_score(f"o{i}", "gpt-5.4", helpfulness=5+i*0.5,
                              profile_fit=5+i*0.5, calibrated_challenge=5+i*0.5)
        for i in range(5)
    ]
    result = _compute_paraphrased_anchor_consistency(orig, para, dimensions=dims)
    assert result["n_matched"] == 5
    assert result["corpus_mean_shift"] == 0.0
    assert result["corpus_mean_rank_corr"] == 1.0


def test_d2_systematic_upward_shift():
    dims = ["helpfulness"]
    orig = [_make_anchored_score(f"o{i}", "gpt-5.4", helpfulness=3+i) for i in range(5)]
    para = [_make_anchored_score(f"o{i}", "gpt-5.4", helpfulness=4+i) for i in range(5)]
    result = _compute_paraphrased_anchor_consistency(orig, para, dimensions=dims)
    assert result["n_matched"] == 5
    assert abs(result["corpus_mean_shift"] - 1.0) < 0.01
    assert abs(result["corpus_mean_rank_corr"] - 1.0) < 0.01


def test_d2_threshold_crossing():
    dims = ["helpfulness"]
    orig = [_make_anchored_score(f"o{i}", "gpt-5.4", helpfulness=v) for i, v in enumerate([4.5, 4.9, 5.5, 5.1])]
    para = [_make_anchored_score(f"o{i}", "gpt-5.4", helpfulness=v) for i, v in enumerate([5.5, 4.9, 4.5, 5.1])]
    result = _compute_paraphrased_anchor_consistency(orig, para, dimensions=dims)
    helpfulness = result["per_judge"]["gpt-5.4"]["helpfulness"]
    assert helpfulness["threshold_crossing_count"] == 2


# ---------------------------------------------------------------------------
# D3 — Reward-hacking diagnostics
# ---------------------------------------------------------------------------


def _make_output(oid, response, profile_text="", condition="C0"):
    return SimpleNamespace(
        output_id=oid,
        assistant_response=response,
        profile_text_supplied=profile_text,
        condition=condition,
    )


def test_d3_empty_inputs():
    result = _compute_reward_hacking_diagnostics([])
    assert result["per_output"] == {}
    assert result["per_condition_summary"] == {}


def test_d3_word_count():
    outputs = [_make_output("o1", "hello world this is a response")]
    result = _compute_reward_hacking_diagnostics(outputs)
    assert result["per_output"]["o1"]["word_count"] == 6


def test_d3_profile_reference_detection():
    outputs = [
        _make_output("o1", "Given your profile, you tend to overthink. Your pattern suggests caution."),
        _make_output("o2", "Here is a generic answer with no profile-specific language."),
    ]
    result = _compute_reward_hacking_diagnostics(outputs)
    assert result["per_output"]["o1"]["profile_reference_count"] >= 2
    assert result["per_output"]["o2"]["profile_reference_count"] == 0


def test_d3_tailoring_marker_detection():
    outputs = [
        _make_output("o1", "I'm tailoring this to you specifically. In your case, the answer differs."),
        _make_output("o2", "Generic answer."),
    ]
    result = _compute_reward_hacking_diagnostics(outputs)
    assert result["per_output"]["o1"]["tailoring_marker_count"] >= 2
    assert result["per_output"]["o2"]["tailoring_marker_count"] == 0


def test_d3_lexical_overlap_with_profile():
    profile_text = "The user values directness, autonomy, intellectual rigor."
    outputs = [
        _make_output("o1", "Directness and autonomy matter here; intellectual rigor wins.",
                     profile_text=profile_text, condition="C5"),
        _make_output("o2", "Simple direct answer with no overlap.",
                     profile_text=profile_text, condition="C5"),
    ]
    result = _compute_reward_hacking_diagnostics(outputs)
    overlap_1 = result["per_output"]["o1"]["source_packet_lexical_overlap"]
    overlap_2 = result["per_output"]["o2"]["source_packet_lexical_overlap"]
    assert overlap_1 > overlap_2


def test_d3_per_condition_summary():
    outputs = [
        _make_output("o1", "Response one " * 20, condition="C4"),
        _make_output("o2", "Response two " * 30, condition="C4"),
        _make_output("o3", "Short", condition="C0"),
    ]
    result = _compute_reward_hacking_diagnostics(outputs)
    c4 = result["per_condition_summary"]["C4"]
    c0 = result["per_condition_summary"]["C0"]
    assert c4["n"] == 2
    assert c0["n"] == 1
    assert c4["mean_word_count"] > c0["mean_word_count"]


# ---------------------------------------------------------------------------
# D4 — Tie-aware reinterpretation
# ---------------------------------------------------------------------------


def test_d4_empty_inputs():
    result = _compute_tie_aware_reinterpretation([], [])
    assert result["n_matched"] == 0
    assert result["status"] == "no_ternary_records"


def test_d4_no_ternary_matches():
    pair_tagged = [_make_pair_tagged("s1", "a", "b", "gpt-5.4", "A", "C5", "C5_CONTRACT")]
    result = _compute_tie_aware_reinterpretation(pair_tagged, [])
    assert result["n_matched"] == 0


def test_d4_no_ties_in_ternary():
    pair_tagged = [
        _make_pair_tagged(f"s{i}", f"a{i}", f"b{i}", "gpt-5.4", "B", "C5", "C5_CONTRACT")
        for i in range(2)
    ]
    ternary = [
        _make_pair_record(f"s{i}", f"a{i}", f"b{i}", "gpt-5.4", "B")
        for i in range(2)
    ]
    result = _compute_tie_aware_reinterpretation(pair_tagged, ternary)
    pair_id = "C5_vs_C5_CONTRACT"
    assert result["by_pair"][pair_id]["tie_rate"] == 0.0
    # C5 is "lo" (alphabetically); winner=B means cond_b=C5_CONTRACT wins, so lo never wins
    assert result["by_pair"][pair_id]["forced_choice_lo_win_rate"] == 0.0
    assert result["by_pair"][pair_id]["ternary_lo_win_rate_excl_ties"] == 0.0


def test_d4_high_tie_rate_triggers_failure_signal():
    pair_tagged = [
        _make_pair_tagged(f"s{i}", f"a{i}", f"b{i}", "gpt-5.4", "B", "C5", "C5_CONTRACT")
        for i in range(4)
    ]
    ternary = [
        _make_pair_record("s0", "a0", "b0", "gpt-5.4", "B"),
        _make_pair_record("s1", "a1", "b1", "gpt-5.4", "no_meaningful_difference"),
        _make_pair_record("s2", "a2", "b2", "gpt-5.4", "no_meaningful_difference"),
        _make_pair_record("s3", "a3", "b3", "gpt-5.4", "B"),
    ]
    result = _compute_tie_aware_reinterpretation(pair_tagged, ternary)
    pair_id = "C5_vs_C5_CONTRACT"
    assert result["by_pair"][pair_id]["tie_rate"] == 0.5
    assert result["by_pair"][pair_id]["n_equipoise_ternary"] == 2


def test_d4_pair_id_canonical_ordering():
    pair_tagged = [
        _make_pair_tagged("s1", "a1", "b1", "gpt-5.4", "A", "C5_CONTRACT", "C5"),
    ]
    ternary = [_make_pair_record("s1", "a1", "b1", "gpt-5.4", "A")]
    result = _compute_tie_aware_reinterpretation(pair_tagged, ternary)
    assert "C5_vs_C5_CONTRACT" in result["by_pair"]


# ---------------------------------------------------------------------------
# D5 — human-rater alignment (single-rater sanity check)
# ---------------------------------------------------------------------------

from psycheeval.analyze import _compute_human_rater_alignment


def _make_anchored_score_d5(run_id: str, judge: str, total: float):
    s = SimpleNamespace()
    s.run_id = run_id
    s.judge_model = judge
    # Spread `total` evenly across 10 dims
    per_dim = total / 10
    s.scores = {f"d{i}": per_dim for i in range(10)}
    return s


def _make_pw_record(scenario_id, run_a, run_b, judge, winner):
    return SimpleNamespace(
        scenario_id=scenario_id,
        run_id_a=run_a,
        run_id_b=run_b,
        judge_model=judge,
        winner=winner,
    )


def test_d5_returns_stub_when_no_responses():
    out = _compute_human_rater_alignment([], [], [], [])
    assert out["status"] == "not_run"
    assert "interpretation_guard" in out


def test_d5_returns_stub_when_responses_present_but_inbox_empty():
    out = _compute_human_rater_alignment(
        [],
        [{"rater_pair_id": "rp_001", "winner": "A", "scalar_a": {}, "scalar_b": {}}],
        [],
        [],
    )
    assert out["status"] == "not_run"


def test_d5_agreement_when_rater_matches_llm_majority():
    inbox = [{
        "rater_pair_id": "rp_001",
        "_original_run_id_a": "ra1",
        "_original_run_id_b": "rb1",
        "_a_is_original_a": True,
        "scenario_id": "s1",
        "stratum": "T1",
        "_pair_type": ["C3", "C4"],
    }]
    responses = [{
        "rater_pair_id": "rp_001",
        "winner": "A",
        "scalar_a": {"helpfulness": 8, "profile_fit": 8, "anti_sycophancy": 8},
        "scalar_b": {"helpfulness": 5, "profile_fit": 5, "anti_sycophancy": 5},
    }]
    pairwise = [
        _make_pw_record("s1", "ra1", "rb1", "gpt-5.4", "A"),
        _make_pw_record("s1", "ra1", "rb1", "gpt-5.5", "A"),
        _make_pw_record("s1", "ra1", "rb1", "opus", "B"),  # 2 vs 1 majority A
    ]
    anchored = [
        _make_anchored_score_d5("ra1", "gpt-5.4", 8.0),
        _make_anchored_score_d5("rb1", "gpt-5.4", 5.0),
    ]
    out = _compute_human_rater_alignment(inbox, responses, pairwise, anchored)
    assert out["status"] == "computed"
    assert out["n_pairs_rated"] == 1
    assert out["n_decisive_pairs"] == 1
    assert out["agreement_rate"] == 1.0


def test_d5_anonymization_inversion_works():
    """If A/B was flipped at selection (a_is_original_a=False), rater 'A'
    means the ORIGINAL B; we should record the rater-orig winner as B."""
    inbox = [{
        "rater_pair_id": "rp_002",
        "_original_run_id_a": "ra2",
        "_original_run_id_b": "rb2",
        "_a_is_original_a": False,  # FLIPPED
        "scenario_id": "s2",
        "stratum": "T1",
        "_pair_type": ["C3", "C4"],
    }]
    responses = [{
        "rater_pair_id": "rp_002",
        "winner": "A",  # rater says shown-A is best; but shown-A = original-B
        "scalar_a": {"helpfulness": 8, "profile_fit": 8, "anti_sycophancy": 8},
        "scalar_b": {"helpfulness": 5, "profile_fit": 5, "anti_sycophancy": 5},
    }]
    pairwise = [_make_pw_record("s2", "ra2", "rb2", "gpt-5.4", "B")]
    anchored = [
        _make_anchored_score_d5("ra2", "gpt-5.4", 5.0),
        _make_anchored_score_d5("rb2", "gpt-5.4", 8.0),
    ]
    out = _compute_human_rater_alignment(inbox, responses, pairwise, anchored)
    # Rater's "A" (shown) → original B. LLM winner is B. So they agree.
    assert out["n_decisive_pairs"] == 1
    assert out["agreement_rate"] == 1.0


def test_d5_disagreement_recorded():
    inbox = [{
        "rater_pair_id": "rp_003",
        "_original_run_id_a": "ra3",
        "_original_run_id_b": "rb3",
        "_a_is_original_a": True,
        "scenario_id": "s3",
        "stratum": "T1",
        "_pair_type": ["C3", "C4"],
    }]
    responses = [{
        "rater_pair_id": "rp_003",
        "winner": "A",
        "scalar_a": {"helpfulness": 8, "profile_fit": 8, "anti_sycophancy": 8},
        "scalar_b": {"helpfulness": 5, "profile_fit": 5, "anti_sycophancy": 5},
    }]
    pairwise = [
        _make_pw_record("s3", "ra3", "rb3", "gpt-5.4", "B"),
        _make_pw_record("s3", "ra3", "rb3", "gpt-5.5", "B"),
    ]
    anchored = [
        _make_anchored_score_d5("ra3", "gpt-5.4", 5.0),
        _make_anchored_score_d5("rb3", "gpt-5.4", 8.0),
    ]
    out = _compute_human_rater_alignment(inbox, responses, pairwise, anchored)
    assert out["agreement_rate"] == 0.0
