"""Run-manifest shape test without touching network."""

from __future__ import annotations

import pytest

from psycheeval import config
from psycheeval.run import build_manifest, _profile_text_for_condition
from psycheeval.models import (
    ProfileBundle,
    ProfileConditions,
    ProfileConditionText,
    Condition,
)


def test_profile_text_empty_for_C0():
    bundle = ProfileBundle(
        profile_bundle_id="b",
        user_id="u",
        profile_conditions=ProfileConditions(
            C1_trait_labels=ProfileConditionText(
                profile_text="direct, abstract", confidence_notes="ok"
            ),
        ),
    )
    assert _profile_text_for_condition(bundle, "C0") == ""
    assert _profile_text_for_condition(bundle, Condition.C0) == ""


def test_profile_text_for_C1():
    bundle = ProfileBundle(
        profile_bundle_id="b",
        user_id="u",
        profile_conditions=ProfileConditions(
            C1_trait_labels=ProfileConditionText(
                profile_text="the trait labels text", confidence_notes="ok"
            ),
        ),
    )
    assert _profile_text_for_condition(bundle, "C1") == "the trait labels text"


def test_profile_text_missing_raises():
    """Superseded 2026-08-16: this used to assert "" — the C0 prompt — for a
    treatment whose profile text was absent, which is how a row labelled C3
    could be authored with no profile at all. Full cover:
    tests/test_manifest_preflight.py."""
    bundle = ProfileBundle(
        profile_bundle_id="b",
        user_id="u",
        profile_conditions=ProfileConditions(),
    )
    with pytest.raises(ValueError, match="C3"):
        _profile_text_for_condition(bundle, "C3")
