"""End-to-end analyzer smoke test on a tiny synthetic fixture.

The fixture is generated procedurally inside the test so that changes to
the pydantic models pick up automatically without manual fixture
maintenance. The goal is to exercise every code path in
`compute_metrics`:

  - PI and PS persona types
  - shared conditions (C0, C1, C3, C4) and extended (C5) + length controls (C1_padded, C4_shuffled)
  - both rubrics (legacy JudgeScore + AnchoredJudgeScore)
  - mixed cross-provider and same-provider judge-author pairs
  - a handful of pairwise records including same-author and cross-author
  - a couple of invalid red-flag warnings for the summary counter

This is not a correctness test of the numbers; it is a structural
regression test. If compute_metrics starts throwing, or drops a block,
this catches it without needing real API data.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from psycheeval import config
from psycheeval.io import write_jsonl
from psycheeval.models import (
    AnchoredJudgeScore,
    AssistantOutput,
    Condition,
    InterviewAnswer,
    InstrumentLikeItem,
    JudgeScore,
    JudgeScores,
    JudgeScoresAnchored,
    LatentGroundTruth,
    PairwiseScore,
    PersonaSeed,
    PersonaType,
    ProfileBundle,
    ProfileConditionText,
    ProfileConditions,
    Scenario,
    ScenarioFamily,
    SourceMode,
    SynthUserRecord,
    UserArtifacts,
)


def _minimal_user_artifacts() -> UserArtifacts:
    return UserArtifacts(
        self_description_250w="A fictional synthetic user created for analyzer fixture tests.",
        values_ranked=["curiosity", "integrity", "growth"],
        work_style_note="Prefers depth to breadth.",
        conflict_reaction_note="Pauses before escalating.",
        bad_day_diary="Lorem ipsum bad day diary " * 50,
        decision_memo="Lorem ipsum decision memo " * 100,
        writing_sample_1="Sample writing paragraph one.",
        writing_sample_2="Sample writing paragraph two.",
        interview_answers=[InterviewAnswer(question="Q1", answer="A1")],
        instrument_like_answers=[InstrumentLikeItem(item="I1", score_1_to_7=5)],
    )


def _minimal_latent() -> LatentGroundTruth:
    return LatentGroundTruth(
        helpful_response_shape="Specific and agency-preserving.",
        unhelpful_response_shape="Generic or flattering.",
        preferred_challenge_style="Direct but proportionate.",
        preferred_reassurance_style="Concrete, not generic.",
        known_blind_spots=["mind-reading", "escalation tendency"],
        sycophancy_triggers=["validation bait"],
        overpersonalization_triggers=["stressful framing"],
        good_boundary_setting="Names the constraint explicitly.",
        bad_boundary_setting="Caves to pressure.",
    )


def _make_user(user_id: str, persona_seed_id: str) -> SynthUserRecord:
    return SynthUserRecord(
        user_id=user_id,
        persona_seed_id=persona_seed_id,
        generation_model="fixture",
        generation_date="2026-04-24",
        user_artifacts=_minimal_user_artifacts(),
        latent_ground_truth=_minimal_latent(),
    )


def _make_bundle(user_id: str) -> ProfileBundle:
    """Bundle populated with every condition including v0.2 length controls."""
    def pc(text: str) -> ProfileConditionText:
        return ProfileConditionText(profile_text=text, confidence_notes="fixture", source_limitations=None)

    return ProfileBundle(
        profile_bundle_id=f"bundle_{user_id}",
        user_id=user_id,
        profile_conditions=ProfileConditions(
            C1_trait_labels=pc("C1 trait labels text."),
            C3_behavioral_contract=pc("C3 behavioral contract do/dont/when text."),
            C4_behavioral_contract_anti_sycophancy=pc("C4 contract + anti-sycophancy clauses text."),
            C5_source_packet_informed=pc("C5 source packet informed text."),
            C1_padded=pc("C1 padded to C4 length text x100."),
            C4_shuffled=pc("C4 shuffled content text."),
        ),
    )


def _make_scenario(scenario_id: str, user_id: str, family: str = "interpersonal_conflict") -> Scenario:
    return Scenario(
        scenario_id=scenario_id,
        user_id=user_id,
        scenario_family=family,
        difficulty=4,
        user_prompt="fixture prompt",
        latent_need="fixture latent need",
        good_response_requirements=["req 1"],
        sycophancy_trap="trap",
        overpersonalization_trap="trap",
        boundary_notes="notes",
        expected_profile_use="fixture use",
    )


def _make_output(run_id: str, scenario_id: str, user_id: str, condition: str, author: str, profile_text: str = "") -> AssistantOutput:
    return AssistantOutput(
        run_id=run_id,
        scenario_id=scenario_id,
        user_id=user_id,
        condition=condition,
        output_model=author,
        profile_text_supplied=profile_text,
        assistant_response="fixture assistant response body.",
        temperature=0.7,
        tokens_in=1000,
        tokens_out=500,
    )


def _seed(persona_id: str, persona_type: PersonaType) -> PersonaSeed:
    return PersonaSeed(
        persona_id=persona_id,
        persona_type=persona_type,
        alias=f"Alias_{persona_id}",
        source_mode=SourceMode.FULLY_SYNTHETIC,
    )


@pytest.fixture
def synthetic_pilot(tmp_path, monkeypatch):
    """Build a minimal pilot on-disk, monkeypatch config paths to point at it,
    return the tag + pilot name for compute_metrics to consume.
    """
    data_dir = tmp_path / "data"
    runs_dir = tmp_path / "runs"
    reports_dir = tmp_path / "reports"
    seed_public = data_dir / "seed_bank_public_inspired.jsonl"
    seed_synth = data_dir / "seed_bank_pure_synthetic.jsonl"

    for d in (data_dir, runs_dir, reports_dir):
        d.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(config, "DATA_DIR", data_dir)
    monkeypatch.setattr(config, "RUNS_DIR", runs_dir)
    monkeypatch.setattr(config, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(config, "SEED_BANK_PUBLIC", seed_public)
    monkeypatch.setattr(config, "SEED_BANK_SYNTHETIC", seed_synth)

    # --- Seeds (one PI + one PS) ---
    write_jsonl(seed_public, [_seed("pfi_fixture_001", PersonaType.PUBLIC_INSPIRED)])
    write_jsonl(seed_synth, [_seed("syn_fixture_001", PersonaType.PURE_SYNTHETIC)])

    # --- Pilot data ---
    pilot_dir = data_dir / "fixture_pilot"
    pilot_dir.mkdir(parents=True, exist_ok=True)

    users = [
        _make_user("user_pi_001", "pfi_fixture_001"),
        _make_user("user_ps_001", "syn_fixture_001"),
    ]
    write_jsonl(pilot_dir / "synthetic_user_records.jsonl", users)

    write_jsonl(pilot_dir / "profile_bundles.jsonl", [_make_bundle(u.user_id) for u in users])

    scenarios = [
        _make_scenario("scn_pi_1", "user_pi_001", "interpersonal_conflict"),
        _make_scenario("scn_pi_2", "user_pi_001", "shame_self_interpretation"),
        _make_scenario("scn_ps_1", "user_ps_001", "procrastination_avoidance"),
        _make_scenario("scn_ps_2", "user_ps_001", "ambition_status"),
    ]
    write_jsonl(pilot_dir / "scenarios.jsonl", scenarios)

    # --- Run ---
    tag = "fixture_run"
    run_d = runs_dir / tag
    run_d.mkdir(parents=True, exist_ok=True)

    outputs: list[AssistantOutput] = []
    authors = ["opus", "gpt-5.4"]
    # PI user → include C5 and length controls; PS user → all except C5.
    def conds_for(sid: str) -> list[str]:
        base = ["C0", "C1", "C1_padded", "C3", "C4", "C4_shuffled"]
        return base + (["C5"] if sid.startswith("scn_pi") else [])

    run_id = 0
    for scen in scenarios:
        for cond in conds_for(scen.scenario_id):
            for author in authors:
                run_id += 1
                profile_text = "" if cond == "C0" else f"{cond} profile text fixture for {scen.user_id}."
                outputs.append(_make_output(
                    f"run_{run_id}",
                    scen.scenario_id,
                    scen.user_id,
                    cond,
                    author,
                    profile_text,
                ))
    write_jsonl(run_d / "assistant_outputs.jsonl", outputs)

    # --- Judge scores (legacy 0-5) ---
    # Two judges, each output scored by each. Opus-judged Opus = same-provider.
    judges = ["opus", "gpt-5.4"]
    legacy_scores: list[JudgeScore] = []
    anchored_scores: list[AnchoredJudgeScore] = []
    # Seed-like deterministic score pattern: cross-provider lower than same-provider to exercise halo
    for o in outputs:
        for j in judges:
            same_prov = (("opus" in o.output_model and "opus" in j) or
                         ("gpt" in o.output_model and "gpt" in j))
            base = 4 if same_prov else 3
            anchor_base = 8 if same_prov else 6
            legacy_scores.append(JudgeScore(
                judge_id=f"jl_{o.run_id}_{j}",
                judge_model=j,
                run_id=o.run_id,
                scenario_id=o.scenario_id,
                scores=JudgeScores(
                    helpfulness=base, profile_fit=base, calibrated_challenge=base,
                    anti_sycophancy=base, agency_support=base, epistemic_hygiene=base,
                    emotional_accuracy=base, boundary_safety=base, non_caricature=base,
                    transfer_value=base,
                ),
                red_flags=["generic_slop"] if o.condition == "C0" else [],
                concise_rationale="fixture rationale",
            ))
            anchored_scores.append(AnchoredJudgeScore(
                judge_id=f"ja_{o.run_id}_{j}",
                judge_model=j,
                run_id=o.run_id,
                scenario_id=o.scenario_id,
                scores=JudgeScoresAnchored(
                    helpfulness=anchor_base, profile_fit=anchor_base, calibrated_challenge=anchor_base,
                    anti_sycophancy=anchor_base, agency_support=anchor_base, epistemic_hygiene=anchor_base,
                    emotional_accuracy=anchor_base, boundary_safety=anchor_base, non_caricature=anchor_base,
                    transfer_value=anchor_base,
                ),
                red_flags=["public_archetype_echo"] if o.condition == "C5" else [],
                concise_rationale="fixture rationale",
            ))
    write_jsonl(run_d / "judge_scores.jsonl", legacy_scores)
    write_jsonl(run_d / "anchored_judge_scores.jsonl", anchored_scores)

    # --- Pairwise (just a handful, same-author within scenario) ---
    pw: list[PairwiseScore] = []
    for scen in scenarios[:2]:  # only two scenarios have pairwise in fixture
        # Find outputs grouped by author
        scen_outs = [o for o in outputs if o.scenario_id == scen.scenario_id]
        opus_outs = [o for o in scen_outs if "opus" in o.output_model]
        for a, b in [(opus_outs[0], opus_outs[-1])]:  # single pair per scenario
            for j in ["opus", "gpt-5.4"]:
                pw.append(PairwiseScore(
                    pairwise_id=f"pw_{scen.scenario_id}_{j}",
                    judge_id=f"pwj_{j}",
                    judge_model=j,
                    scenario_id=scen.scenario_id,
                    run_id_a=a.run_id,
                    run_id_b=b.run_id,
                    winner="B",
                    confidence_0_to_1=0.75,
                    why_winner_is_better="B wins in fixture",
                    failure_in_A="",
                    failure_in_B="",
                    red_flags_A=[],
                    red_flags_B=[],
                ))
    write_jsonl(run_d / "pairwise_scores.jsonl", pw)

    # --- Validation warnings fixture ---
    warnings_path = run_d / "validation_warnings.jsonl"
    with warnings_path.open("w") as fh:
        fh.write(json.dumps({
            "timestamp": "2026-04-24T00:00:00Z",
            "run_tag": tag,
            "mode": "score",
            "judge_model": "opus",
            "author_model": "gpt-5.4",
            "condition": "C4",
            "context_id": outputs[0].run_id,
            "invalid_label": "bogus free text",
        }) + "\n")

    return {"tag": tag, "pilot": "fixture_pilot", "n_outputs": len(outputs), "n_legacy": len(legacy_scores), "n_anchored": len(anchored_scores), "n_pairwise": len(pw)}


def test_compute_metrics_on_synthetic_fixture(synthetic_pilot):
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])

    # Counts reflect the fixture
    assert m["counts"]["assistant_outputs"] == synthetic_pilot["n_outputs"]
    assert m["counts"]["judge_scores"] == synthetic_pilot["n_legacy"]
    assert m["counts"]["anchored_judge_scores"] == synthetic_pilot["n_anchored"]
    assert m["counts"]["pairwise_scores"] == synthetic_pilot["n_pairwise"]

    # Both rubrics present
    assert m["scale_max_legacy"] == 5
    assert m["anchored"]["scale_max"] == 10

    # Shared conditions include length controls (fixture populates them)
    shared = set(m["shared_conditions"])
    assert {"C0", "C1", "C1_padded", "C3", "C4", "C4_shuffled"} <= shared
    # C5 is in all_conditions but NOT in shared (only PI has it)
    assert "C5" in m["all_conditions"]
    assert "C5" not in m["shared_conditions"]

    # Length-control deltas are populated in the all-personas block
    deltas = m["primary_cross_provider"]["deltas_C0C4_all_personas"]
    assert "C4_minus_C1_padded" in deltas
    assert "C4_minus_C4_shuffled" in deltas
    assert "C3_minus_C4" in deltas
    # Every delta dict has all 10 dimensions
    for pair_name, pair_dims in deltas.items():
        assert len(pair_dims) == 10, f"{pair_name} has {len(pair_dims)} dims"

    # PI-only block has C5 row
    assert "C5" in m["primary_cross_provider"]["by_condition_C0C5_PI_only"]
    assert "C4_minus_C5" in m["primary_cross_provider"]["deltas_C0C5_PI_only"]

    # Halo audit has entries for every (cond, author) cell
    halo = m["halo_audit_same_minus_cross"]
    assert len(halo) > 0
    # Fixture sets same-provider = 4, cross = 3 → halo should be ~+1 on each dim
    sample_key = next(iter(halo))
    sample_halo = halo[sample_key]
    assert all(abs(v - 1.0) < 0.2 for v in sample_halo.values()), sample_halo

    # Token summary present for every observed condition
    assert set(m["token_summary_by_condition"].keys()) == set(m["all_conditions"])
    # C0 has zero profile chars; C4 has nonzero
    assert m["token_summary_by_condition"]["C0"]["profile_chars_mean"] == 0
    assert m["token_summary_by_condition"]["C4"]["profile_chars_mean"] > 0

    # Pairwise block populated with both win-rate and pair-preference tables
    pair = m["pairwise"]
    assert pair["counts"]["total_pairwise_records"] == synthetic_pilot["n_pairwise"]
    assert "win_rate_cross_provider_same_author" in pair
    assert "pair_preference_cross_provider_same_author" in pair

    # Validation warnings are counted
    vw = m["validation_warnings_summary"]
    assert vw["count"] == 1
    assert vw["by_judge"]["opus"] == 1
    assert vw["by_label"]["bogus free text"] == 1
    assert vw["by_condition"]["C4"] == 1

    # Anchored block has parallel structure (same keys as legacy primary)
    anchored = m["anchored"]
    assert "primary_cross_provider" in anchored
    assert "deltas_C0C4_all_personas" in anchored["primary_cross_provider"]
    # Anchored scores are 0-10 scale → means should match fixture bases
    c0_means = anchored["primary_cross_provider"]["by_condition_C0C4_all_personas"]["C0"]
    assert c0_means["helpfulness"]["mean"] == 6.0  # cross-provider means = 6 in fixture


def test_write_report_does_not_crash(synthetic_pilot):
    from psycheeval.analyze import compute_metrics, write_report
    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    report_path = write_report(synthetic_pilot["tag"], m, synthetic_pilot["pilot"])
    assert report_path.exists()
    body = report_path.read_text()
    # Core sections rendered
    assert "Dataset composition" in body
    assert "Primary" in body
    # No raw Python repr fallback (would mean a dict rendered as {} in table)
    assert "dict_items" not in body
    # pse-2: inter-judge agreement (Cohen's κ on red flags) surfaced in report,
    # not just the metrics JSON. The fixture has ≥2 judges with output overlap.
    if m.get("inter_judge_agreement_legacy"):
        assert "Cohen's κ" in body
        assert "mean red-flag κ" in body


def test_native_pairwise_diagnostics_present(synthetic_pilot):
    """v0.2 native ports: tie rates, PI/PS split, length buckets,
    scenario-family breakdowns, cluster-bootstrap CIs. All must appear in
    the metrics output for downstream report generation to consume them
    without going back to ad-hoc /tmp scripts.
    """
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    pw = m["pairwise"]

    # Each of the new blocks must exist (possibly empty if fixture is sparse,
    # but the key must be present).
    for key in [
        "tie_rates_same_author",
        "pi_ps_split_same_author",
        "length_buckets_same_author",
        "scenario_family_breakdowns_same_author",
        "cluster_bootstrap_ci_same_author",
    ]:
        assert key in pw, f"pairwise.{key} missing from metrics output"

    # Cluster-bootstrap CI shape: bounded in [0, 1], non-empty, includes
    # documented fields. The "bootstrap >= wilson width" relationship holds
    # on real data where the proportion is interior to [0, 1], but can break
    # on degenerate fixtures where the proportion is at the boundary
    # (synthetic fixtures often use winner="B" uniformly, producing 0/N or
    # N/N proportions where bootstrap collapses to zero width). Real-data
    # behavior is verified separately via the v0.1 fixture spot-checks.
    for pair_key, entry in pw["cluster_bootstrap_ci_same_author"].items():
        for k in (
            "n_decisive",
            "n_clusters",
            "wilson_ci95_low",
            "wilson_ci95_high",
            "bootstrap_ci95_low",
            "bootstrap_ci95_high",
            "n_resamples",
        ):
            assert k in entry, f"{pair_key} missing key {k}"
        for ci in (
            entry["wilson_ci95_low"],
            entry["wilson_ci95_high"],
            entry["bootstrap_ci95_low"],
            entry["bootstrap_ci95_high"],
        ):
            assert 0.0 <= ci <= 1.0, f"{pair_key} CI value {ci} out of [0, 1]"
        assert entry["bootstrap_ci95_low"] <= entry["bootstrap_ci95_high"]
        assert entry["wilson_ci95_low"] <= entry["wilson_ci95_high"]


def test_stratified_cluster_bootstrap_blocks_present(synthetic_pilot):
    """2026-05-15 review fix: cluster_bootstrap_ci must be exposed in three
    explicit scopes (all-judge / cross-provider / same-provider same-author)
    plus a scope-counts block. Required so reviewers can check judge×provider
    halo on C5_CONTRACT findings."""
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    pw = m["pairwise"]

    for key in (
        "cluster_bootstrap_ci_same_author",          # all-judge (existing, kept)
        "cluster_bootstrap_ci_cross_provider_same_author",  # NEW
        "cluster_bootstrap_ci_same_provider_same_author",   # NEW
        "cluster_bootstrap_scope_counts",            # NEW
    ):
        assert key in pw, f"pairwise.{key} missing from metrics output"

    sc = pw["cluster_bootstrap_scope_counts"]
    for k in ("same_author_all_judges", "cross_provider_same_author", "same_provider_same_author"):
        assert k in sc, f"cluster_bootstrap_scope_counts.{k} missing"
        assert isinstance(sc[k], int) and sc[k] >= 0
    # Cross + same-provider must partition all-judge same-author exactly.
    assert sc["cross_provider_same_author"] + sc["same_provider_same_author"] == sc["same_author_all_judges"], (
        "cross-provider + same-provider scope counts must sum to all-judge same-author "
        f"(got xp={sc['cross_provider_same_author']} + sp={sc['same_provider_same_author']} "
        f"!= all={sc['same_author_all_judges']})"
    )


def test_cross_judge_redflag_macro_micro_blocks(synthetic_pilot):
    """2026-05-15: cross-judge red-flag predictiveness + macro-vs-micro
    aggregation blocks must appear with the expected shape."""
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    pw = m["pairwise"]

    # Cross-judge red-flag predictiveness (only if anchored scores exist)
    if "cross_judge_redflag_predictiveness_same_author" in pw:
        rf = pw["cross_judge_redflag_predictiveness_same_author"]
        for pair, e in rf.items():
            for k in ("n_decisive_pairs", "n_asymmetric_external_flags",
                      "asymmetric_rate", "p_loser_more_externally_flagged",
                      "wilson_ci95_low", "wilson_ci95_high",
                      "predictiveness_above_chance"):
                assert k in e, f"redflag[{pair}] missing {k}"
            assert isinstance(e["predictiveness_above_chance"], bool)

    # Macro vs micro
    assert "macro_vs_micro_aggregation_same_author" in pw
    mvm = pw["macro_vs_micro_aggregation_same_author"]
    for pair, e in mvm.items():
        for k in ("n_decisive", "micro_lo_decisive_win_rate",
                  "macro_judge", "macro_author", "macro_persona",
                  "macro_family", "macro_cell",
                  "macros_that_disagree_with_micro_by_5pp"):
            assert k in e, f"mvm[{pair}] missing {k}"
        assert isinstance(e["macros_that_disagree_with_micro_by_5pp"], list)


def test_rubric_overlap_missingness_discoverability_blocks(synthetic_pilot):
    """2026-05-15: rubric lexical overlap (top-level) + missingness audit +
    condition discoverability (pair_block) must appear when their inputs exist."""
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])

    # Rubric lexical overlap (top-level)
    # May be None if profile bundles not available — accept either shape
    rlo = m.get("rubric_lexical_overlap")
    if rlo:
        for cond, e in rlo.items():
            for k in ("n_unique_tokens_in_condition", "n_unique_tokens_in_rubric",
                      "n_overlapping_tokens", "jaccard_score",
                      "overlap_share_of_condition", "top_overlapping_tokens"):
                assert k in e, f"rubric_overlap[{cond}] missing {k}"
            assert 0.0 <= e["jaccard_score"] <= 1.0

    # Missingness audit
    pw = m["pairwise"]
    assert "missingness_balance_audit" in pw
    mb = pw["missingness_balance_audit"]
    for outer in ("anchored_scalar", "pairwise"):
        assert outer in mb
        assert "cell_balance_stats" in mb[outer]

    # Condition discoverability (optional, depends on sklearn + fixture size)
    if "condition_discoverability" in pw:
        cd = pw["condition_discoverability"]
        for k in ("n_train", "n_test", "n_classes", "classes",
                  "test_accuracy", "chance_baseline",
                  "accuracy_above_chance_pp", "per_class_f1",
                  "top_features_per_class"):
            assert k in cd, f"discoverability missing {k}"


def test_ab_side_audit_and_length_adjusted_blocks(synthetic_pilot):
    """2026-05-15 review fixes: A/B side audit + length-adjusted summary
    must appear as first-class blocks."""
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    pw = m["pairwise"]

    # A/B side audit
    assert "ab_side_audit_same_author" in pw
    ab = pw["ab_side_audit_same_author"]
    assert "by_condition" in ab
    assert "by_pair" in ab
    for c, e in ab["by_condition"].items():
        for k in ("n_slot_a", "n_slot_b", "n_total", "b_share"):
            assert k in e
    for pair, e in ab["by_pair"].items():
        for k in ("n_total", "n_decisive", "n_slot_a_wins", "n_slot_b_wins",
                  "slot_a_win_rate_decisive", "slot_a_is_lo_share",
                  "structurally_imbalanced",
                  "slot_a_wins_wilson_ci95_low", "slot_a_wins_wilson_ci95_high"):
            assert k in e, f"by_pair[{pair}] missing {k}"

    # Length-adjusted summary
    assert "length_adjusted_summary_same_author" in pw
    la = pw["length_adjusted_summary_same_author"]
    for pair, e in la.items():
        for k in ("n_full_decisive", "n_similar_decisive",
                  "full_lo_win_rate", "similar_lo_win_rate",
                  "similar_wilson_ci95_low", "similar_wilson_ci95_high",
                  "delta_similar_minus_full",
                  "headline_vanishes_under_length_match"):
            assert k in e, f"length_adjusted[{pair}] missing {k}"
        assert isinstance(e["headline_vanishes_under_length_match"], bool)


def test_leave_one_out_fragility_blocks_present(synthetic_pilot):
    """2026-05-15 review fix: LOO fragility (judge/author/persona/family)
    must appear as first-class blocks with Δ_from_full + flags so the
    headline robustness story is auditable."""
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    pw = m["pairwise"]

    for key in (
        "leave_one_judge_out_fragility",
        "leave_one_author_out_fragility",
        "leave_one_persona_out_fragility",
        "leave_one_family_out_fragility",
    ):
        assert key in pw, f"pairwise.{key} missing from metrics output"
        block = pw[key]
        for pair_key, p in block.items():
            for k in ("leave_out_dimension", "full_point_lo_decisive",
                      "full_n_decisive", "by_leave_out_value"):
                assert k in p, f"{key}/{pair_key} missing {k}"
            for leave_value, e in p["by_leave_out_value"].items():
                for k in ("n_decisive", "n_clusters",
                          "lo_decisive_win_rate", "delta_from_full",
                          "wilson_ci95_low", "wilson_ci95_high",
                          "bootstrap_ci95_low", "bootstrap_ci95_high",
                          "flags"):
                    assert k in e, f"{key}/{pair_key}/{leave_value} missing {k}"
                assert isinstance(e["flags"], list)


def test_stratified_pairwise_blocks_present(synthetic_pilot):
    """2026-05-15 review fix (codex-council, GPT-Max, GPT-Pro): per-judge,
    per-author, per-persona stratification of every headline pair must
    appear as first-class blocks so reviewer claims like 'GPT-5.4 reverses
    C3 vs C5_CONTRACT' can be verified without going back to JSON."""
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    pw = m["pairwise"]

    for key in (
        "pairwise_by_judge_same_author",
        "pairwise_by_author_same_author",
        "pairwise_by_persona_same_author",
    ):
        assert key in pw, f"pairwise.{key} missing from metrics output"
        block = pw[key]
        # Each pair's stratum entries must have the expected shape.
        for pair_key, strata in block.items():
            for stratum_value, s in strata.items():
                for k in (
                    "n_total", "n_decisive", "n_ties", "n_clusters",
                    "lo_decisive_win_rate",
                    "wilson_ci95_low", "wilson_ci95_high",
                    "bootstrap_ci95_low", "bootstrap_ci95_high",
                ):
                    assert k in s, f"{key}/{pair_key}/{stratum_value} missing key {k}"
                # n_decisive + n_ties == n_total
                assert s["n_decisive"] + s["n_ties"] == s["n_total"]
                if s["lo_decisive_win_rate"] is not None:
                    assert 0.0 <= s["lo_decisive_win_rate"] <= 1.0


def test_scalar_pairwise_reconciliation_block(synthetic_pilot):
    """2026-05-15 review fix (GPT Pro §A1): for every pairwise pair, match
    pairwise records with same-judge anchored scalars and surface paired
    deltas + pairwise/scalar sign agreement so contradictions between
    holistic and rubric judging are explicit."""
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    pw = m["pairwise"]

    assert "scalar_pairwise_reconciliation_same_author" in pw, (
        "scalar_pairwise_reconciliation_same_author missing from metrics output"
    )
    rec = pw["scalar_pairwise_reconciliation_same_author"]
    # Fixture has at least one pairwise record with same-judge anchored coverage.
    if rec:
        for pair_key, entry in rec.items():
            for k in (
                "n_matched", "n_decisive",
                "lo_pairwise_wins", "hi_pairwise_wins", "pairwise_ties",
                "hi_pairwise_win_rate_decisive",
                "mean_scalar_deltas_hi_minus_lo",
                "frac_dim_hi_higher", "frac_dim_lo_higher",
                "mean_total_scalar_delta",
                "max_scale_per_dim", "n_dims",
                "pairwise_scalar_sign_agreement_decisive",
                "agree_count", "disagree_count", "scalar_tie_count",
            ):
                assert k in entry, f"{pair_key} missing key {k}"
            # Self-consistency
            assert entry["lo_pairwise_wins"] + entry["hi_pairwise_wins"] + entry["pairwise_ties"] == entry["n_matched"]
            assert entry["agree_count"] + entry["disagree_count"] + entry["scalar_tie_count"] == entry["n_decisive"]
            # Scalar delta bounded by max possible (10 dims × ±10)
            assert -100.0 <= entry["mean_total_scalar_delta"] <= 100.0


def test_cross_author_leak_detection_block(synthetic_pilot):
    """2026-05-15 review fix: when cross-author pairwise records exist
    (Opus C5_CONTRACT phase scope leak), analyzer surfaces an explicit
    leak-detection block so downstream reports can not mislabel total
    pairwise counts as same-author."""
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    pw = m["pairwise"]
    leak = pw.get("cross_author_leak_detection")

    # Fixture may or may not have cross-author records depending on factory.
    # If absent, the block is omitted (presence is opt-in for non-leaky runs).
    if leak is not None:
        for k in ("n_cross_author_records", "n_total_pairwise_records", "by_judge", "by_pair", "note"):
            assert k in leak, f"cross_author_leak_detection.{k} missing"
        assert leak["n_cross_author_records"] > 0, "leak block present but count is zero"
        assert leak["n_cross_author_records"] <= leak["n_total_pairwise_records"]
        assert isinstance(leak["by_judge"], dict)
        assert isinstance(leak["by_pair"], dict)
        # Counts must be self-consistent.
        assert sum(leak["by_judge"].values()) == leak["n_cross_author_records"]
        assert sum(leak["by_pair"].values()) == leak["n_cross_author_records"]

    # The counts block must now expose same_author and cross_author totals
    # so the bundle/report cannot conflate them with total_pairwise_records.
    counts = pw["counts"]
    for k in ("total_pairwise_records", "same_author", "cross_author"):
        assert k in counts, f"pairwise.counts.{k} missing"
    assert counts["same_author"] + counts["cross_author"] == counts["total_pairwise_records"]


def test_red_flag_stratification_block(synthetic_pilot):
    """The red-flag stratification block must report by judge×condition,
    by provider-filter×condition, and by output-level threshold (any-judge,
    2+, majority). Each leaf has flagged/total/rate."""
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    rs = m["red_flag_stratification_legacy"]
    for key in ["by_judge_condition", "by_provider_filter_condition", "by_output_level_threshold"]:
        assert key in rs, f"red_flag_stratification_legacy.{key} missing"

    # by_judge_condition: judges → conditions → metrics
    for judge, by_cond in rs["by_judge_condition"].items():
        for cond, metrics in by_cond.items():
            for k in ("flagged", "total", "any_flag_rate"):
                assert k in metrics, f"red-flag judge.{judge}.{cond}.{k} missing"

    # by_output_level_threshold: levels → conditions → metrics
    for level in ("any_judge", "two_or_more_judges", "majority"):
        assert level in rs["by_output_level_threshold"], f"output-level missing: {level}"


def test_scalar_inter_judge_agreement_block(synthetic_pilot):
    """Per-dimension agreement must be reported with Pearson + Spearman
    across all judge pairs."""
    from psycheeval.analyze import compute_metrics

    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    sa = m["scalar_inter_judge_agreement_legacy"]
    for key in [
        "per_judge_dim_means",
        "per_judge_severity_offsets",
        "pairwise_correlations",
        "pairwise_mean_correlation",
        "weak_agreement_dimensions",
        "n_judges",
    ]:
        assert key in sa, f"scalar agreement key missing: {key}"
    # Means + offsets shape
    for judge, dims in sa["per_judge_dim_means"].items():
        assert "helpfulness" in dims  # canonical scalar dim
        assert isinstance(dims["helpfulness"], (int, float))
    # Correlation values must be either None or in [-1, 1]
    for pair_key, dims in sa["pairwise_correlations"].items():
        for dim, vals in dims.items():
            for stat in ("pearson", "spearman"):
                v = vals[stat]
                assert v is None or -1.0 <= v <= 1.0, (
                    f"{pair_key}.{dim}.{stat}={v} out of [-1, 1]"
                )


def test_probe_records_excluded_by_default(synthetic_pilot, capfd):
    """Records authored by non-official judges (e.g. Kimi K2.6 feasibility
    probes) MUST be excluded from canonical analysis unless include_probes=True
    is set explicitly. Fail-closed protects v0.1 canonical reports from being
    silently contaminated by exploratory side-runs.
    """
    from psycheeval import config
    from psycheeval.analyze import compute_metrics
    from psycheeval.io import write_jsonl
    from psycheeval.models import JudgeScore, JudgeScores

    run_d = config.run_dir(synthetic_pilot["tag"])

    # Inject a Kimi probe record alongside the existing fixture records
    existing = [JudgeScore.model_validate_json(line) for line in (run_d / "judge_scores.jsonl").open()]
    one = existing[0]
    probe = JudgeScore(
        judge_id="probe_kimi_001",
        judge_model="moonshotai/kimi-k2.6",
        run_id=one.run_id,
        scenario_id=one.scenario_id,
        scores=JudgeScores(
            helpfulness=5, profile_fit=5, calibrated_challenge=5,
            anti_sycophancy=5, agency_support=5, epistemic_hygiene=5,
            emotional_accuracy=5, boundary_safety=5, non_caricature=5,
            transfer_value=5,
        ),
        red_flags=[],
        concise_rationale="probe rationale (should not enter canonical analysis)",
    )
    write_jsonl(run_d / "judge_scores.jsonl", existing + [probe])

    # Default behavior: probe excluded
    m = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"])
    judge_scores_count = m["counts"]["judge_scores"]
    assert judge_scores_count == len(existing), (
        f"Probe record leaked into default analysis: expected {len(existing)} "
        f"official records, got {judge_scores_count}"
    )

    # Warning printed to stderr
    captured = capfd.readouterr()
    assert "probe" in captured.err.lower() or "kimi" in captured.err.lower(), (
        "Expected analyzer to warn about excluded probe records on stderr"
    )

    # Opt-in behavior: probe included
    m_with = compute_metrics(synthetic_pilot["tag"], synthetic_pilot["pilot"], include_probes=True)
    assert m_with["counts"]["judge_scores"] == len(existing) + 1
