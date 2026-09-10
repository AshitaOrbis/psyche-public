"""Tests for synthesis layer: merge_profile, narrative templating, and LLM entrypoints.

Covers the gaps flagged in the 2026-04-16 audit:
    - No tests exist for merge_profile() integration with fixture inputs.
    - No tests exist for narrative thresholds in generate_claude_md_snippet().
    - No tests exist for llm_claude.analyze_big_five() with a mocked SDK.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from psyche_analysis.synthesis.merge import merge_profile
from psyche_analysis.synthesis.narrative import generate_claude_md_snippet
from psyche_analysis.synthesis.profile import (
    AttachmentProfile,
    BigFiveProfile,
    EmotionRegProfile,
    MergedTrait,
    PsycheProfile,
    SocialProfile,
)


# ── merge_profile ───────────────────────────────────────────────


class TestMergeProfile:
    def test_empty_dir_returns_valid_profile(self, tmp_path: Path):
        """Merging an empty analysis dir produces a profile with defaults
        and no estimates, not a crash."""
        profile = merge_profile(tmp_path)
        assert isinstance(profile, PsycheProfile)
        assert profile.metadata.methods_used == []
        # Each domain resolves to neutral 50 when no estimates exist
        for key in "NEOAC":
            assert key in profile.big_five.domains or profile.big_five.domains == {}

    def test_llm_claude_only_populates_methods_used(self, tmp_path: Path):
        """A minimal llm-claude.json fixture propagates method provenance."""
        llm_fixture = {
            "method": "llm-claude",
            "model_used": "claude-opus-4-7",
            "model_requested": "opus",
            "total_tokens": 1234,
            "big_five": {
                "domains": {
                    "N": {"score": 40, "confidence": "medium", "evidence": ["e1"]},
                    "E": {"score": 60, "confidence": "medium", "evidence": ["e2"]},
                    "O": {"score": 75, "confidence": "high", "evidence": ["e3"]},
                    "A": {"score": 35, "confidence": "medium", "evidence": ["e4"]},
                    "C": {"score": 55, "confidence": "medium", "evidence": ["e5"]},
                },
                "facets": {},
                "overall_confidence": "medium",
            },
            "values": None,
        }
        (tmp_path / "llm-claude.json").write_text(json.dumps(llm_fixture))
        profile = merge_profile(tmp_path)
        assert "llm-claude" in profile.metadata.methods_used
        assert set(profile.big_five.domains.keys()) == set("NEOAC")
        # With single method per trait, final_score tracks the input.
        assert profile.big_five.domains["O"].final_score == 75


# ── narrative snippet thresholds ────────────────────────────────


def _build_minimal_profile(
    *,
    a_score: float = 50,
    o_score: float = 50,
    n_score: float = 50,
    c_score: float = 50,
    e_score: float = 50,
    methods: list[str] | None = None,
) -> PsycheProfile:
    """Construct a PsycheProfile with Big Five domains set and everything else default."""
    profile = PsycheProfile()
    profile.big_five = BigFiveProfile(
        domains={
            "N": MergedTrait(final_score=n_score),
            "E": MergedTrait(final_score=e_score),
            "O": MergedTrait(final_score=o_score),
            "A": MergedTrait(final_score=a_score),
            "C": MergedTrait(final_score=c_score),
        }
    )
    if methods:
        profile.metadata.methods_used = methods
    return profile


class TestNarrativeSnippet:
    def test_contains_header(self):
        profile = _build_minimal_profile()
        snippet = generate_claude_md_snippet(profile)
        assert "# Personality Context (Behavioral Specification)" in snippet

    def test_low_agreeableness_triggers_direct_language(self):
        """narrative.py:44-46 — A<40 should produce direct-answer directive."""
        profile = _build_minimal_profile(a_score=30)
        snippet = generate_claude_md_snippet(profile)
        assert "Wants direct answers" in snippet
        assert "blunt feedback" in snippet

    def test_high_agreeableness_triggers_harmony_framing(self):
        """narrative.py:47-48 — A>=65 should produce constructive-framing directive."""
        profile = _build_minimal_profile(a_score=75)
        snippet = generate_claude_md_snippet(profile)
        assert "constructively" in snippet
        assert "harmony" in snippet

    def test_mid_agreeableness_triggers_neither_branch(self):
        """A between 40 and 65 hits neither threshold — no A-specific directive."""
        profile = _build_minimal_profile(a_score=50)
        snippet = generate_claude_md_snippet(profile)
        assert "Wants direct answers" not in snippet
        assert "constructively" not in snippet

    def test_high_openness_triggers_exploration_framing(self):
        """narrative.py:50-52 — O>=60 should produce exploration directive."""
        profile = _build_minimal_profile(o_score=80)
        snippet = generate_claude_md_snippet(profile)
        assert "exploring alternatives" in snippet

    def test_low_neuroticism_suppresses_caveats(self):
        """narrative.py:63-64 — N<35 should skip-caveats directive."""
        profile = _build_minimal_profile(n_score=25)
        snippet = generate_claude_md_snippet(profile)
        assert "Skip unnecessary caveats" in snippet

    def test_high_neuroticism_requests_reassurance(self):
        """narrative.py:65-66 — N>=65 should request-reassurance directive."""
        profile = _build_minimal_profile(n_score=75)
        snippet = generate_claude_md_snippet(profile)
        assert "reassurance" in snippet

    def test_methods_footer(self):
        """Methods used are reported in the footer with the instrument count."""
        profile = _build_minimal_profile(methods=["llm-claude", "interview"])
        snippet = generate_claude_md_snippet(profile)
        assert "llm-claude, interview" in snippet
        assert "psychometric battery" in snippet


# ── Channel-constraint regression tests ────────────────────────


class TestTemplatedNarrativeAntiPatterns:
    """Templated narrative.py must not emit directives that assume signal
    Claude Code cannot observe in a turn-based text channel.

    The personality-profile trap: directives like 'check in if they go
    quiet' read as coherent but can never fire because Claude Code has no
    silence, latency, or presence observation. A user not typing is
    indistinguishable from at-lunch, asleep, or closed-the-terminal.
    """

    ANTI_PATTERN_SUBSTRINGS = [
        "goes quiet",
        "go quiet",
        "withdrawal",
        "check in if",
        "comfortable with silence",
        "conversational gaps",
        "in distress",
        "crisis situations",
        "affective contagion",
        "seeks reassurance after criticism",  # bare observation; needs scoping
    ]

    def _build_profile_likely_to_trigger_bad_directives(self) -> PsycheProfile:
        """Fixture designed to trigger every branch in narrative.py that
        previously emitted anti-patterns. Sets high attachment anxiety,
        high suppression, low extraversion, elevated empathic concern."""
        from psyche_analysis.synthesis.profile import (
            AttachmentProfile,
            EmotionRegProfile,
            EmpathyProfile,
        )

        profile = _build_minimal_profile(
            a_score=30,   # low A — triggers direct-pushback branch
            o_score=80,   # high O
            n_score=60,   # triggers verbalize-tradeoffs branch
            c_score=55,
            e_score=20,   # low E — previously triggered "comfortable with silence"
        )
        profile.attachment = AttachmentProfile(anxiety=70, avoidance=60)
        profile.emotion_reg = EmotionRegProfile(suppression=75, reappraisal=80)
        profile.empathy = EmpathyProfile(
            perspective_taking=75,
            empathic_concern=50,
            personal_distress=70,  # previously triggered "gets overwhelmed in crisis"
            fantasy=60,
        )
        return profile

    def test_templated_snippet_emits_no_anti_patterns(self):
        """Regression guard: the templated narrative must not contain any
        phrase that depends on Claude observing user state beyond text
        input. This enforces the channel-constraint design principle."""
        profile = self._build_profile_likely_to_trigger_bad_directives()
        snippet = generate_claude_md_snippet(profile).lower()

        hits = [p for p in self.ANTI_PATTERN_SUBSTRINGS if p in snippet]
        assert not hits, (
            f"Templated narrative emitted channel-anti-patterns: {hits}. "
            f"Directives assuming observable silence/withdrawal/distress do "
            f"not fire in a Claude Code turn-based text channel. See "
            f"psyche_analysis/synthesis/narrative_llm.ANTI_PATTERN_PHRASES."
        )


class TestLLMNarrativeAntiPatternDetector:
    """The narrative_llm.check_anti_patterns() function must flag the same
    anti-patterns so LLM-driven regenerations can't re-introduce them."""

    def test_flags_silence_directive(self):
        from psyche_analysis.synthesis.narrative_llm import check_anti_patterns
        text = "- Tends to suppress emotional expression; check in if he goes quiet"
        hits = check_anti_patterns(text)
        assert "goes quiet" in hits
        assert "check in if" in hits

    def test_flags_silence_means(self):
        from psyche_analysis.synthesis.narrative_llm import check_anti_patterns
        text = "Silence after feedback is processing, not agreement."
        hits = check_anti_patterns(text)
        assert any("silence" in h for h in hits)

    def test_flags_distress_state_directive(self):
        from psyche_analysis.synthesis.narrative_llm import check_anti_patterns
        text = "In distress states, do not ask for a plan."
        hits = check_anti_patterns(text)
        assert "in distress states" in hits

    def test_flags_affective_contagion_as_directive(self):
        from psyche_analysis.synthesis.narrative_llm import check_anti_patterns
        text = "- Empathy operates through affective contagion, not cognitive simulation"
        hits = check_anti_patterns(text)
        assert "affective contagion" in hits

    def test_passes_legitimate_directives(self):
        from psyche_analysis.synthesis.narrative_llm import check_anti_patterns
        # Text-turn-actionable directives should pass clean.
        text = (
            "- Prefers blunt feedback — skip diplomatic softening\n"
            "- Explain WHY, not just WHAT — rejects instructions without rationale\n"
            "- Probabilistic framing over categorical claims\n"
            "- When the user asks a surprisingly basic question, build the "
            "framework together rather than answering narrowly\n"
        )
        hits = check_anti_patterns(text)
        assert hits == [], f"False positive in anti-pattern check: {hits}"

    def test_deployed_claude_context_md_is_clean(self):
        """The deployed profiles/claude-context.md must pass the anti-pattern
        gate. Regression guard against hand-edits or re-regens that reintroduce
        channel anti-patterns.

        Skipped if the file doesn't exist (fresh checkout)."""
        from psyche_analysis.synthesis.narrative_llm import check_anti_patterns
        deployed = Path(__file__).parents[2] / "profiles" / "claude-context.md"
        if not deployed.exists():
            pytest.skip("no deployed claude-context.md to check")
        hits = check_anti_patterns(deployed.read_text())
        assert not hits, (
            f"Deployed claude-context.md contains channel anti-patterns: "
            f"{hits}. Regenerate via scripts/regen_claude_context.py with "
            f"the current SYSTEM_PROMPT."
        )


# ── llm_claude with mocked SDK ──────────────────────────────────


class TestAnalyzeBigFiveMocked:
    """Verify llm_claude wiring — SDK receives the resolved full ID, not alias."""

    def test_uses_resolved_model_id_for_sdk_call(self):
        """When caller passes 'opus', the SDK must receive 'claude-opus-4-7'.

        This enforces the resolve-then-call pattern: aliases at the user
        layer, full IDs at the provenance/SDK layer.
        """
        from psyche_analysis.corpus.types import TextSample
        from psyche_analysis.methods import llm_claude

        # Mock response that looks like a valid Anthropic completion.
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=json.dumps({
            "domains": {
                "N": {"score": 50, "confidence": "medium", "evidence": []},
                "E": {"score": 50, "confidence": "medium", "evidence": []},
                "O": {"score": 50, "confidence": "medium", "evidence": []},
                "A": {"score": 50, "confidence": "medium", "evidence": []},
                "C": {"score": 50, "confidence": "medium", "evidence": []},
            },
            "facets": {},
            "overall_confidence": "medium",
        }))]
        mock_response.usage.input_tokens = 100
        mock_response.usage.output_tokens = 50

        sample = TextSample(
            id="s1", source="test", author="self", text="some test content",
        )

        with patch.object(llm_claude, "Anthropic") as mock_anthropic_cls:
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic_cls.return_value = mock_client

            llm_claude.analyze_big_five([sample], model="opus")

            # SDK must be called at least once
            assert mock_client.messages.create.called
            # And the model kwarg must be the resolved full ID, not the alias
            call_kwargs = mock_client.messages.create.call_args.kwargs
            assert call_kwargs["model"] == "claude-opus-4-7", (
                f"Expected 'claude-opus-4-7' to be passed to SDK; got {call_kwargs['model']!r}. "
                f"The resolve-then-call pattern is broken."
            )

    def test_default_model_is_config_alias(self):
        """The analyze_big_five signature default must come from config.DEFAULT_CLAUDE_MODEL."""
        import inspect
        from psyche_analysis.config import DEFAULT_CLAUDE_MODEL
        from psyche_analysis.methods.llm_claude import analyze_big_five

        sig = inspect.signature(analyze_big_five)
        default = sig.parameters["model"].default
        assert default == DEFAULT_CLAUDE_MODEL, (
            f"analyze_big_five model default is {default!r}, not DEFAULT_CLAUDE_MODEL={DEFAULT_CLAUDE_MODEL!r}"
        )


# ── integration smoke ──────────────────────────────────────────


class TestProfileSchema:
    def test_profile_json_roundtrip(self):
        """The live profile.json must parse cleanly via PsycheProfile."""
        profile_path = Path(__file__).parents[2] / "profiles" / "profile.json"
        if not profile_path.exists():
            pytest.skip("No live profile.json to roundtrip")
        data = json.loads(profile_path.read_text())
        profile = PsycheProfile.model_validate(data)
        # Re-dump doesn't crash
        _ = profile.model_dump_json()

    def test_narrative_snippet_of_live_profile_nonempty(self):
        """generate_claude_md_snippet(live_profile) produces a non-trivial string."""
        profile_path = Path(__file__).parents[2] / "profiles" / "profile.json"
        if not profile_path.exists():
            pytest.skip("No live profile.json for snippet smoke")
        data = json.loads(profile_path.read_text())
        profile = PsycheProfile.model_validate(data)
        snippet = generate_claude_md_snippet(profile)
        assert len(snippet) > 200
        assert snippet.startswith("# Personality Context")
