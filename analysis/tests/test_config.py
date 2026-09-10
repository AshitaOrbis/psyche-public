"""Tests for psyche_analysis.config model alias resolution."""

from __future__ import annotations

import importlib


def test_default_model_is_opus_alias(monkeypatch):
    monkeypatch.delenv("PSYCHE_CLAUDE_MODEL", raising=False)
    from psyche_analysis import config
    importlib.reload(config)
    assert config.DEFAULT_CLAUDE_MODEL == "opus"


def test_env_override_with_alias(monkeypatch):
    monkeypatch.setenv("PSYCHE_CLAUDE_MODEL", "sonnet")
    from psyche_analysis import config
    importlib.reload(config)
    assert config.DEFAULT_CLAUDE_MODEL == "sonnet"


def test_env_override_with_full_id(monkeypatch):
    monkeypatch.setenv("PSYCHE_CLAUDE_MODEL", "claude-sonnet-4-6")
    from psyche_analysis import config
    importlib.reload(config)
    assert config.DEFAULT_CLAUDE_MODEL == "claude-sonnet-4-6"


def test_resolve_alias_opus():
    from psyche_analysis.config import resolve_model_id
    assert resolve_model_id("opus") == "claude-opus-4-7"


def test_resolve_alias_sonnet():
    from psyche_analysis.config import resolve_model_id
    assert resolve_model_id("sonnet") == "claude-sonnet-4-6"


def test_resolve_alias_haiku():
    from psyche_analysis.config import resolve_model_id
    assert resolve_model_id("haiku") == "claude-haiku-4-5"


def test_resolve_passes_through_full_id():
    from psyche_analysis.config import resolve_model_id
    assert resolve_model_id("claude-opus-4-7") == "claude-opus-4-7"
    assert resolve_model_id("claude-opus-4-6") == "claude-opus-4-6"


def test_resolve_passes_through_unknown_string():
    # Unknown aliases / future models surface the error at the SDK
    # rather than silently mapping to something wrong.
    from psyche_analysis.config import resolve_model_id
    assert resolve_model_id("claude-opus-4-8") == "claude-opus-4-8"
    assert resolve_model_id("future-model-xyz") == "future-model-xyz"


def test_test_env_cleanup_restores_default(monkeypatch):
    # Ensure module reload mechanics don't bleed between tests.
    monkeypatch.setenv("PSYCHE_CLAUDE_MODEL", "haiku")
    from psyche_analysis import config
    importlib.reload(config)
    assert config.DEFAULT_CLAUDE_MODEL == "haiku"

    monkeypatch.delenv("PSYCHE_CLAUDE_MODEL", raising=False)
    importlib.reload(config)
    assert config.DEFAULT_CLAUDE_MODEL == "opus"
