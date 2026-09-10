"""Tests for tier-aware merge pipeline."""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import pytest

from psyche_analysis.synthesis.merge import (
    INSTRUMENT_RELIABILITY,
    METHOD_WEIGHTS,
    _detect_tier,
    _theta_to_100,
    merge_profile,
)
from psyche_analysis.synthesis.profile import PsycheProfile


# ── Tier detection ──────────────────────────────────────────────


class TestTierDetection:
    def test_default_is_standard(self):
        assert _detect_tier(None) == "standard"
        assert _detect_tier({}) == "standard"

    def test_explicit_tier_in_export(self):
        assert _detect_tier({"selectedTier": "lite"}) == "lite"
        assert _detect_tier({"selectedTier": "heavy"}) == "heavy"

    def test_lite_from_neo60(self):
        data = {"results": {"ipip-neo-60": {"scores": []}}}
        assert _detect_tier(data) == "lite"

    def test_standard_from_neo300(self):
        data = {"results": {"ipip-neo-300": {"scores": []}}}
        assert _detect_tier(data) == "standard"

    def test_heavy_from_instruments(self):
        heavy_insts = (
            "hexaco-200", "grit-o", "bpns-21", "levenson-ipc-24", "snyder-sm-25", "cat-big5", "cat-hexaco",
            "aot-13", "ius-12", "scs-26", "mfq-2", "frost-mps", "maas", "authenticity", "tangney-scs", "maximization", "ztpi",
        )
        for inst in heavy_insts:
            data = {"results": {inst: {"scores": []}}}
            assert _detect_tier(data) == "heavy", f"Failed to detect heavy from {inst}"

    def test_standard_from_new_instruments(self):
        for inst in ("swls", "aaq-ii", "dweck-itis", "cei-ii"):
            data = {"results": {inst: {"scores": []}}}
            assert _detect_tier(data) == "standard", f"Failed to detect standard from {inst}"

    def test_explicit_overrides_heuristic(self):
        data = {"selectedTier": "lite", "results": {"ipip-neo-300": {"scores": []}}}
        assert _detect_tier(data) == "lite"


# ── Theta to 100 conversion ────────────────────────────────────


class TestThetaConversion:
    def test_zero_is_50(self):
        assert _theta_to_100(0.0) == 50.0

    def test_positive_theta(self):
        result = _theta_to_100(1.0)
        assert 83.0 <= result <= 85.0  # Normal CDF(1) ≈ 84.13

    def test_negative_theta(self):
        result = _theta_to_100(-1.0)
        assert 15.0 <= result <= 17.0  # Normal CDF(-1) ≈ 15.87

    def test_extreme_high(self):
        assert _theta_to_100(7.0) == 100.0

    def test_extreme_low(self):
        assert _theta_to_100(-7.0) == 0.0

    def test_symmetry(self):
        pos = _theta_to_100(1.5)
        neg = _theta_to_100(-1.5)
        assert abs((pos + neg) - 100.0) < 0.5

    def test_two_sigma(self):
        result = _theta_to_100(2.0)
        assert 97.0 <= result <= 98.0  # Normal CDF(2) ≈ 97.72


# ── Instrument reliability constants ───────────────────────────


class TestReliabilityConstants:
    def test_neo_ordering(self):
        """NEO-300 > NEO-120 > NEO-60 in reliability."""
        assert INSTRUMENT_RELIABILITY["ipip-neo-300"]["alpha"] > INSTRUMENT_RELIABILITY["ipip-neo-120"]["alpha"]
        assert INSTRUMENT_RELIABILITY["ipip-neo-120"]["alpha"] > INSTRUMENT_RELIABILITY["ipip-neo-60"]["alpha"]

    def test_all_alphas_in_range(self):
        for inst_id, data in INSTRUMENT_RELIABILITY.items():
            assert 0.0 < data["alpha"] <= 1.0, f"{inst_id} alpha out of range"

    def test_heavy_replacements_higher_reliability(self):
        """Heavy tier instruments should have >= reliability than their lite counterparts."""
        pairs = [
            ("grit-o", "grit-s"),
            ("bpns-21", "bpns-9"),
            ("hexaco-200", "hexaco-60"),
            ("levenson-ipc-24", "loc-ie4"),
        ]
        for heavy, lite in pairs:
            assert INSTRUMENT_RELIABILITY[heavy]["alpha"] >= INSTRUMENT_RELIABILITY[lite]["alpha"], \
                f"{heavy} should have higher alpha than {lite}"


# ── v2 backwards compatibility ──────────────────────────────────


class TestBackwardsCompat:
    def test_v2_json_loads_as_v4(self):
        """A v2 profile (no manifest, no new fields) should load into v4 schema."""
        v2_data = {
            "version": 2,
            "big_five": {"domains": {}, "facets": {}},
            "values": {"values": {}},
            "clinical": {},
            "cognitive": {},
            "dark_triad": {},
            "attachment": {},
            "emotion_reg": {},
            "empathy": {},
            "social": {},
            "grit": {},
            "vocational": {},
            "needs": {},
            "hexaco": {},
            "persona": {},
            "metadata": {"methods_used": ["llm-claude", "self-report"]},
            "narrative": "old narrative",
            "claude_md_snippet": "old snippet",
        }
        profile = PsycheProfile.model_validate(v2_data)
        assert profile.version == 2
        assert profile.manifest.tier == "standard"  # default
        assert profile.manifest.instruments == []
        assert profile.hexaco.facets == {}
        assert profile.grit.overall is None
        assert profile.needs.autonomy_frustration is None
        assert profile.social.loc_powerful_others is None
        # Phase 4 fields should have defaults
        assert profile.wellbeing.life_satisfaction is None
        assert profile.self_compassion.total is None
        assert profile.decision_style.growth_mindset is None
        assert profile.time_perspective.future is None

    def test_v3_json_loads_as_v4(self):
        """A v3 profile (no Phase 4 fields) should load into v4 schema."""
        v3_data = {
            "version": 3,
            "big_five": {"domains": {}, "facets": {}},
            "values": {"values": {}},
            "manifest": {"tier": "heavy", "instruments": []},
        }
        profile = PsycheProfile.model_validate(v3_data)
        assert profile.version == 3
        assert profile.manifest.tier == "heavy"
        # Phase 4 fields default to None
        assert profile.wellbeing.life_satisfaction is None
        assert profile.moral_foundations.care is None
        assert profile.perfectionism.organization is None

    def test_v4_roundtrip(self):
        """A v4 profile should serialize and deserialize cleanly."""
        profile = PsycheProfile(version=4)
        profile.manifest.tier = "heavy"
        profile.hexaco.facets = {"HH1": 65.0, "HH2": 70.0}
        profile.grit.overall = 72.0
        profile.needs.autonomy_frustration = 30.0
        profile.wellbeing.life_satisfaction = 78.5
        profile.decision_style.growth_mindset = 85.0
        profile.moral_foundations.care = 90.0
        profile.time_perspective.future = 72.0
        profile.self_compassion.total = 65.0

        json_str = profile.model_dump_json()
        restored = PsycheProfile.model_validate_json(json_str)
        assert restored.version == 4
        assert restored.manifest.tier == "heavy"
        assert restored.hexaco.facets == {"HH1": 65.0, "HH2": 70.0}
        assert restored.grit.overall == 72.0
        assert restored.needs.autonomy_frustration == 30.0
        assert restored.wellbeing.life_satisfaction == 78.5
        assert restored.decision_style.growth_mindset == 85.0
        assert restored.moral_foundations.care == 90.0
        assert restored.time_perspective.future == 72.0
        assert restored.self_compassion.total == 65.0


# ── Merge pipeline integration ──────────────────────────────────


class TestMergeIntegration:
    def test_empty_analysis_dir(self, tmp_path: Path):
        """Merge with no analysis files produces a valid profile."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()
        profile = merge_profile(analysis_dir)
        assert isinstance(profile, PsycheProfile)
        assert profile.version == 4

    def test_tier_override(self, tmp_path: Path):
        """Explicit tier param sets manifest tier."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()
        profile = merge_profile(analysis_dir, tier="heavy")
        assert profile.manifest.tier == "heavy"

    def test_self_report_populates_manifest(self, tmp_path: Path):
        """Self-report with instrument results populates the manifest."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()

        self_report = {
            "selectedTier": "lite",
            "results": {
                "ipip-neo-60": {
                    "instrumentId": "ipip-neo-60",
                    "scores": [
                        {"scaleId": "N", "raw": 30, "normalized": 50, "itemCount": 12},
                        {"scaleId": "E", "raw": 30, "normalized": 50, "itemCount": 12},
                        {"scaleId": "O", "raw": 30, "normalized": 50, "itemCount": 12},
                        {"scaleId": "A", "raw": 30, "normalized": 50, "itemCount": 12},
                        {"scaleId": "C", "raw": 30, "normalized": 50, "itemCount": 12},
                    ],
                },
            },
        }
        sr_path = tmp_path / "export.json"
        sr_path.write_text(json.dumps(self_report))

        profile = merge_profile(analysis_dir, self_report_path=sr_path)
        assert profile.manifest.tier == "lite"
        # Should have recorded the instrument
        inst_ids = [r.instrument_id for r in profile.manifest.instruments]
        assert "ipip-neo-60" in inst_ids


# ── CAT score extraction ──────────────────────────────────────


class TestCATExtraction:
    def test_cat_big5_populates_facet_scores(self, tmp_path: Path):
        """CAT Big Five results should produce facet scores with cat field."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()

        self_report = {
            "selectedTier": "heavy",
            "results": {
                "cat-big5": {
                    "instrumentId": "cat-big5",
                    "scores": [
                        {"scaleId": "N1", "raw": 0, "normalized": 65, "itemCount": 5,
                         "theta": 0.5, "se": 0.25},
                        {"scaleId": "E1", "raw": 0, "normalized": 70, "itemCount": 5,
                         "theta": 1.0, "se": 0.28},
                    ],
                },
            },
        }
        sr_path = tmp_path / "export.json"
        sr_path.write_text(json.dumps(self_report))

        profile = merge_profile(analysis_dir, self_report_path=sr_path)
        # CAT instrument should be in manifest
        inst_ids = [r.instrument_id for r in profile.manifest.instruments]
        assert "cat-big5" in inst_ids

        # Facet scores should have cat values
        facet_map = {fs.facet_id: fs for fs in profile.big_five.facet_scores}
        assert "N1" in facet_map
        assert facet_map["N1"].cat is not None
        assert 68.0 <= facet_map["N1"].cat <= 70.0  # theta=0.5 -> ~69.1
        assert facet_map["N1"].cat_se == 0.25

    def test_cat_hexaco_populates_domain_scores(self, tmp_path: Path):
        """CAT HEXACO with low SE should update domain scores."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()

        self_report = {
            "selectedTier": "heavy",
            "results": {
                "cat-hexaco": {
                    "instrumentId": "cat-hexaco",
                    "scores": [
                        {"scaleId": "hh", "raw": 0, "normalized": 60, "itemCount": 8,
                         "theta": 0.3, "se": 0.20},
                        {"scaleId": "em", "raw": 0, "normalized": 55, "itemCount": 8,
                         "theta": -0.2, "se": 0.22},
                        {"scaleId": "hh_sincerity", "raw": 0, "normalized": 65, "itemCount": 4,
                         "theta": 0.5, "se": 0.30},
                    ],
                },
            },
        }
        sr_path = tmp_path / "export.json"
        sr_path.write_text(json.dumps(self_report))

        profile = merge_profile(analysis_dir, self_report_path=sr_path)
        inst_ids = [r.instrument_id for r in profile.manifest.instruments]
        assert "cat-hexaco" in inst_ids

        # Domain with low SE should be updated
        assert profile.hexaco.honesty_humility is not None
        assert 61.0 <= profile.hexaco.honesty_humility <= 62.0  # theta=0.3 -> ~61.8

        # Facet should be stored with cat_ prefix
        assert "cat_hh_sincerity" in profile.hexaco.facets

    def test_cat_hexaco_high_se_does_not_override(self, tmp_path: Path):
        """CAT HEXACO with high SE should NOT override existing domain scores."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()

        self_report = {
            "selectedTier": "heavy",
            "results": {
                "hexaco-60": {
                    "instrumentId": "hexaco-60",
                    "scores": [
                        {"scaleId": "hh", "raw": 30, "normalized": 75.0, "itemCount": 10},
                    ],
                },
                "cat-hexaco": {
                    "instrumentId": "cat-hexaco",
                    "scores": [
                        {"scaleId": "hh", "raw": 0, "normalized": 60, "itemCount": 5,
                         "theta": 0.3, "se": 0.45},  # High SE -> don't override
                    ],
                },
            },
        }
        sr_path = tmp_path / "export.json"
        sr_path.write_text(json.dumps(self_report))

        profile = merge_profile(analysis_dir, self_report_path=sr_path)
        # hexaco-60 score should remain (CAT SE too high to override)
        assert profile.hexaco.honesty_humility == 75.0

    def test_cat_reliability_constants(self):
        """CAT instruments should have highest reliability."""
        assert INSTRUMENT_RELIABILITY["cat-big5"]["alpha"] == 0.95
        assert INSTRUMENT_RELIABILITY["cat-hexaco"]["alpha"] == 0.95
        assert INSTRUMENT_RELIABILITY["cat-big5"]["alpha"] > INSTRUMENT_RELIABILITY["ipip-neo-300"]["alpha"]


# ── Phase 4 instrument extraction ─────────────────────────────


class TestPhase4Extraction:
    def test_phase4_reliability_entries_exist(self):
        """All 14 new instruments should have reliability entries."""
        new_instruments = [
            "swls", "aaq-ii", "dweck-itis", "cei-ii",
            "aot-13", "ius-12", "scs-26", "mfq-2",
            "frost-mps", "maas", "authenticity", "tangney-scs",
            "maximization", "ztpi",
        ]
        for inst_id in new_instruments:
            assert inst_id in INSTRUMENT_RELIABILITY, f"Missing reliability entry for {inst_id}"
            assert 0.0 < INSTRUMENT_RELIABILITY[inst_id]["alpha"] <= 1.0

    def test_swls_extraction(self, tmp_path: Path):
        """SWLS populates wellbeing.life_satisfaction."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()
        self_report = {
            "selectedTier": "standard",
            "results": {
                "swls": {
                    "instrumentId": "swls",
                    "scores": [{"scaleId": "life_satisfaction", "raw": 28, "normalized": 76.7, "itemCount": 5}],
                },
            },
        }
        sr_path = tmp_path / "export.json"
        sr_path.write_text(json.dumps(self_report))
        profile = merge_profile(analysis_dir, self_report_path=sr_path)
        assert profile.wellbeing.life_satisfaction == 76.7

    def test_scs26_total_computation(self, tmp_path: Path):
        """SCS-26 total is computed from subscale averages with negative reversal."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()
        self_report = {
            "selectedTier": "heavy",
            "results": {
                "scs-26": {
                    "instrumentId": "scs-26",
                    "scores": [
                        {"scaleId": "self_kindness", "raw": 20, "normalized": 75.0, "itemCount": 5},
                        {"scaleId": "self_judgment", "raw": 10, "normalized": 25.0, "itemCount": 5},
                        {"scaleId": "common_humanity", "raw": 12, "normalized": 50.0, "itemCount": 4},
                        {"scaleId": "isolation", "raw": 8, "normalized": 25.0, "itemCount": 4},
                        {"scaleId": "mindfulness", "raw": 14, "normalized": 62.5, "itemCount": 4},
                        {"scaleId": "over_identification", "raw": 6, "normalized": 12.5, "itemCount": 4},
                    ],
                },
            },
        }
        sr_path = tmp_path / "export.json"
        sr_path.write_text(json.dumps(self_report))
        profile = merge_profile(analysis_dir, self_report_path=sr_path)
        assert profile.self_compassion.self_kindness == 75.0
        assert profile.self_compassion.self_judgment == 25.0
        # Total = mean(75, 100-25, 50, 100-25, 62.5, 100-12.5)
        # = mean(75, 75, 50, 75, 62.5, 87.5) = 425/6 ≈ 70.8
        assert profile.self_compassion.total is not None
        assert 70.0 <= profile.self_compassion.total <= 71.0

    def test_decision_style_aggregation(self, tmp_path: Path):
        """Decision style profile aggregates AAQ-II, Dweck, AOT, IUS, and Maximization."""
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()
        self_report = {
            "selectedTier": "heavy",
            "results": {
                "aaq-ii": {"instrumentId": "aaq-ii", "scores": [
                    {"scaleId": "psychological_flexibility", "raw": 14, "normalized": 66.7, "itemCount": 7},
                ]},
                "dweck-itis": {"instrumentId": "dweck-itis", "scores": [
                    {"scaleId": "growth_mindset", "raw": 36, "normalized": 80.0, "itemCount": 8},
                ]},
                "aot-13": {"instrumentId": "aot-13", "scores": [
                    {"scaleId": "open_minded_thinking", "raw": 55, "normalized": 64.6, "itemCount": 13},
                ]},
                "ius-12": {"instrumentId": "ius-12", "scores": [
                    {"scaleId": "prospective", "raw": 18, "normalized": 39.3, "itemCount": 7},
                    {"scaleId": "inhibitory", "raw": 10, "normalized": 31.3, "itemCount": 5},
                ]},
                "maximization": {"instrumentId": "maximization", "scores": [
                    {"scaleId": "high_standards", "raw": 20, "normalized": 55.6, "itemCount": 5},
                    {"scaleId": "alternative_search", "raw": 15, "normalized": 38.9, "itemCount": 4},
                    {"scaleId": "decision_difficulty", "raw": 12, "normalized": 29.2, "itemCount": 4},
                ]},
            },
        }
        sr_path = tmp_path / "export.json"
        sr_path.write_text(json.dumps(self_report))
        profile = merge_profile(analysis_dir, self_report_path=sr_path)

        assert profile.decision_style.psychological_flexibility == 66.7
        assert profile.decision_style.growth_mindset == 80.0
        assert profile.decision_style.open_minded_thinking == 64.6
        assert profile.decision_style.uncertainty_prospective == 39.3
        assert profile.decision_style.uncertainty_inhibitory == 31.3
        assert profile.decision_style.uncertainty_intolerance is not None
        assert profile.decision_style.high_standards == 55.6
        assert profile.decision_style.maximizing_total is not None


# ── Method weights invariants ──────────────────────────────────


class TestMethodWeights:
    """Guards against the silent-drift bug where METHOD_WEIGHTS summed to 0.92.

    The runtime code at _merge_estimates() renormalizes by total_weight, so
    weights never produced broken scores — but they drifted from documented
    intent. These tests enforce documented-vs-behavior alignment.
    """

    def test_weights_sum_to_one(self):
        total = sum(METHOD_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9, (
            f"METHOD_WEIGHTS sum to {total}, not 1.0. "
            f"This causes documented proportions to drift from effective "
            f"behavior after runtime renormalization."
        )

    def test_excluded_methods_have_zero_weight(self):
        # Empath is excluded by design (language register vs personality).
        # An explicit 0.0 entry documents the exclusion and prevents any
        # future caller that produces empath estimates from contributing.
        assert METHOD_WEIGHTS.get("empath") == 0.0

    def test_no_weights_for_unimplemented_methods(self):
        # Guards against llm-gpt-style dead weights: a weight with no
        # corresponding source module can never contribute, making the
        # listed weight effectively a comment, not a computation.
        implemented = {"self-report", "interview", "llm-claude", "huggingface", "empath"}
        extras = set(METHOD_WEIGHTS.keys()) - implemented
        assert not extras, (
            f"Unexpected method keys in METHOD_WEIGHTS: {extras}. "
            f"Every key must correspond to an implemented method or be "
            f"explicitly excluded (weight=0)."
        )

    def test_all_non_zero_weights_are_positive(self):
        # No negative weights; no NaN; sanity floor for each contributor.
        for method, weight in METHOD_WEIGHTS.items():
            assert weight >= 0.0, f"{method} has negative weight {weight}"
            assert weight == weight, f"{method} weight is NaN"  # NaN check
