"""Tests for the C5_CONTRACT v0.2 condition.

C5_CONTRACT is the contract-first wrapper around the C5 source packet
introduced in v0.2 per the locked D1 decision (2026-05-05). It tests
whether v0.1 C5 scalar/red-flag fragility came from the source packet
itself (PAE) or from the absence of behavioral contract (the v0.1 §10
confound).

These tests verify the integration is wired end-to-end:
- Condition enum has C5_CONTRACT
- ProfileConditions has C5_contract field
- v02_prepare programmatically builds the C5_CONTRACT text
- run.py manifest builder produces C5_CONTRACT tasks for PI personas
- run.py manifest builder does NOT produce C5_CONTRACT tasks for PS personas
- Normalize layer accepts the alternate "C5_CONTRACT" short key
"""

from __future__ import annotations

import json

from psycheeval import config
from psycheeval.models import (
    Condition,
    ProfileBundle,
    ProfileConditions,
    ProfileConditionText,
)
from psycheeval.normalize import normalize_profile_bundle
from psycheeval.v02_prepare import build_c5_contract


def test_condition_enum_has_c5_contract():
    assert Condition.C5_CONTRACT == "C5_CONTRACT"


def test_profile_conditions_has_c5_contract_field():
    pc = ProfileConditions()
    # Field must exist and default to None
    assert hasattr(pc, "C5_contract")
    assert pc.C5_contract is None


def test_build_c5_contract_orders_contract_first():
    """The synthesis must follow D1: contract first, then anti-mimicry rules,
    then source packet. This ordering is load-bearing for the experiment."""
    c3 = "Do not validate without checking."
    c5 = "User is influenced by a public commentator known for fast moral judgments."
    text = build_c5_contract(c3, c5)
    contract_idx = text.index("[BEHAVIORAL CONTRACT]")
    rules_idx = text.index("PRIORITY RULES")
    packet_idx = text.index("[SOURCE PACKET")
    assert contract_idx < rules_idx < packet_idx, (
        f"C5_CONTRACT ordering wrong: contract={contract_idx} rules={rules_idx} packet={packet_idx}"
    )
    # Both inputs must appear in the output
    assert c3 in text
    assert c5 in text
    # Anti-mimicry rules must be present
    assert "do not perform" in text.lower()
    assert "imitate" in text.lower() or "mimic" in text.lower()


def test_v02_pilot_bundles_have_c5_contract_for_pi_personas():
    """After v02_prepare runs, the on-disk profile_bundles.jsonl should have
    C5_contract populated for the 4 PI personas and None for the 4 PS
    personas."""
    pilot_dir = config.pilot_dir("v02_hard_pilot")
    bundles_path = pilot_dir / "profile_bundles.jsonl"
    if not bundles_path.exists():
        # v02_prepare hasn't been run on this checkout — skip rather than fail
        # because the test environment may not have the v0.2 pilot materialized
        import pytest
        pytest.skip(f"{bundles_path} not present; run psycheeval.v02_prepare first")

    bundles = [ProfileBundle.model_validate_json(l) for l in bundles_path.open()]
    pi_with_contract = 0
    ps_without_contract = 0
    for b in bundles:
        is_pi = "_pfi_" in b.user_id
        has_c5_contract = (
            b.profile_conditions.C5_contract is not None
            and bool(b.profile_conditions.C5_contract.profile_text.strip())
        )
        if is_pi:
            assert has_c5_contract, f"PI persona {b.user_id} missing C5_contract"
            pi_with_contract += 1
        else:
            assert not has_c5_contract, (
                f"PS persona {b.user_id} should NOT have C5_contract — "
                f"PS personas have no public anchor and should not have the source packet"
            )
            ps_without_contract += 1

    assert pi_with_contract == 4, f"expected 4 PI personas with C5_contract, got {pi_with_contract}"
    assert ps_without_contract == 4, f"expected 4 PS personas without C5_contract, got {ps_without_contract}"


def test_pilot_conditions_includes_c5_contract():
    """C5_CONTRACT must be in the v02_hard_pilot public_extra so the manifest
    builder picks it up."""
    conds = config.conditions_for("v02_hard_pilot")
    assert "C5_CONTRACT" in conds["public_extra"]
    assert "C5_CONTRACT" not in conds["core"]  # PI-only by design


def test_normalize_accepts_short_c5_contract_key():
    """The normalize layer must map the short condition key 'C5_CONTRACT' to
    the long ProfileConditions field name 'C5_contract'."""
    raw = {
        "user_id": "user_test_001",
        "profile_bundle_id": "test_bundle",
        "C5_CONTRACT": {
            "profile_text": "test contract+packet text",
            "confidence_notes": "test",
        },
    }
    normalized = normalize_profile_bundle(raw)
    assert "profile_conditions" in normalized
    pc = normalized["profile_conditions"]
    assert "C5_contract" in pc
    assert pc["C5_contract"]["profile_text"] == "test contract+packet text"


def test_build_manifest_produces_c5_contract_for_pi_only():
    """End-to-end: build_manifest with v02_hard_pilot should yield C5_CONTRACT
    rows only for PI personas, equal in count to PI-personas × scenarios."""
    from psycheeval.run import build_manifest
    pilot_dir = config.pilot_dir("v02_hard_pilot")
    if not (pilot_dir / "profile_bundles.jsonl").exists():
        import pytest
        pytest.skip("v02_hard_pilot not materialized")

    manifest = build_manifest("v02_hard_pilot", authors=["gpt-5.4"])
    c5c = [t for t in manifest if t["condition"] == "C5_CONTRACT"]
    assert len(c5c) > 0, "manifest produced no C5_CONTRACT rows"
    for t in c5c:
        assert "_pfi_" in t["user_id"], (
            f"C5_CONTRACT row produced for PS persona {t['user_id']}"
        )
    # Expected: 4 PI personas × 10 scenarios per persona × 1 author = 40
    assert len(c5c) == 40, f"expected 40 C5_CONTRACT manifest rows, got {len(c5c)}"
