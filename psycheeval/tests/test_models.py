"""Pydantic model validation + schema export sanity tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from psycheeval import config
from psycheeval.io import read_jsonl
from psycheeval.models import (
    ALL_MODELS,
    AssistantOutput,
    Condition,
    JudgeScore,
    JudgeScores,
    PairwiseScore,
    PersonaSeed,
    PersonaType,
    ProfileBundle,
    ProfileConditions,
    ProfileConditionText,
    RedFlag,
    Scenario,
    ScenarioFamily,
    SourceGrounding,
    SourceMode,
    SourcePacket,
    SynthUserRecord,
)


SCHEMAS_DIR = config.SCHEMAS_DIR


def test_all_schemas_exist():
    assert SCHEMAS_DIR.exists()
    files = list(SCHEMAS_DIR.glob("*.schema.json"))
    assert len(files) == len(ALL_MODELS), f"expected {len(ALL_MODELS)} schema files, got {len(files)}"


def test_persona_seed_minimal():
    seed = PersonaSeed(
        persona_id="syn_test_001",
        persona_type=PersonaType.PURE_SYNTHETIC,
        alias="Test User",
        source_mode=SourceMode.FULLY_SYNTHETIC,
    )
    assert seed.persona_id == "syn_test_001"
    # Round-trip
    assert PersonaSeed.model_validate_json(seed.model_dump_json()).persona_id == seed.persona_id


def test_seed_banks_validate():
    """Both checked-in seed banks pass validation."""
    n_public = sum(1 for _ in read_jsonl(config.SEED_BANK_PUBLIC, PersonaSeed))
    n_synth = sum(1 for _ in read_jsonl(config.SEED_BANK_SYNTHETIC, PersonaSeed))
    assert n_public >= 40, f"public seed bank too small: {n_public}"
    assert n_synth >= 40, f"synthetic seed bank too small: {n_synth}"


def test_pilot_personas_are_in_seed_banks():
    public_ids = {s.persona_id for s in read_jsonl(config.SEED_BANK_PUBLIC, PersonaSeed)}
    synth_ids = {s.persona_id for s in read_jsonl(config.SEED_BANK_SYNTHETIC, PersonaSeed)}
    for pid in config.MICRO_PILOT_PUBLIC_INSPIRED:
        assert pid in public_ids, f"{pid} missing from public seed bank"
    for pid in config.MICRO_PILOT_PURE_SYNTHETIC:
        assert pid in synth_ids, f"{pid} missing from synthetic seed bank"


def test_judge_scores_bounds():
    js = JudgeScores(
        helpfulness=3,
        profile_fit=3,
        calibrated_challenge=3,
        anti_sycophancy=3,
        agency_support=3,
        epistemic_hygiene=3,
        emotional_accuracy=3,
        boundary_safety=3,
        non_caricature=3,
        transfer_value=3,
    )
    assert js.helpfulness == 3

    with pytest.raises(Exception):
        JudgeScores(
            helpfulness=6,  # out of bounds
            profile_fit=3,
            calibrated_challenge=3,
            anti_sycophancy=3,
            agency_support=3,
            epistemic_hygiene=3,
            emotional_accuracy=3,
            boundary_safety=3,
            non_caricature=3,
            transfer_value=3,
        )


def test_pairwise_winner_enum():
    ps = PairwiseScore(
        pairwise_id="pw_test",
        judge_id="judge_test",
        judge_model="opus",
        scenario_id="scn_test",
        run_id_a="run_a",
        run_id_b="run_b",
        winner="A",
        confidence_0_to_1=0.7,
        why_winner_is_better="test",
    )
    assert ps.winner == "A"
    with pytest.raises(Exception):
        PairwiseScore(
            pairwise_id="pw_test",
            judge_id="judge_test",
            judge_model="opus",
            scenario_id="scn_test",
            run_id_a="run_a",
            run_id_b="run_b",
            winner="invalid",
            confidence_0_to_1=0.7,
            why_winner_is_better="test",
        )


def test_profile_bundle_optional_conditions():
    """C0 is absence; C1-C5 are all optional to allow partial bundles."""
    bundle = ProfileBundle(
        profile_bundle_id="b_test",
        user_id="u_test",
        profile_conditions=ProfileConditions(
            C1_trait_labels=ProfileConditionText(
                profile_text="direct, abstract", confidence_notes="low n"
            ),
        ),
    )
    assert bundle.profile_conditions.C1_trait_labels is not None
    assert bundle.profile_conditions.C5_source_packet_informed is None


def test_scenario_difficulty_bounds():
    with pytest.raises(Exception):
        Scenario(
            scenario_id="s",
            user_id="u",
            scenario_family=ScenarioFamily.INTERPERSONAL_CONFLICT,
            difficulty=9,  # out of bounds
            user_prompt="x",
            latent_need="x",
            good_response_requirements=[],
            sycophancy_trap="x",
            overpersonalization_trap="x",
            boundary_notes="x",
            expected_profile_use="x",
        )
