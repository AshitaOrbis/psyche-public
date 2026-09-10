"""Drift-prevention tests for the RedFlag controlled vocabulary.

The failure mode these tests catch: someone extends `RedFlag` but forgets to
update a judge prompt (or vice versa), and the next batch of judges silently
produces invalid labels or misses the new categories.

All checks derive from the Python enum as the single source of truth.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from psycheeval import config
from psycheeval.judge import (
    ANCHORED_PROMPT_PATH,
    JUDGE_PROMPT_PATH,
    PAIRWISE_PROMPT_PATH,
    _substitute_red_flag_vocabulary,
)
from psycheeval.models import RED_FLAG_DESCRIPTIONS, RedFlag, render_red_flag_vocabulary


PROMPT_FILES = [JUDGE_PROMPT_PATH, ANCHORED_PROMPT_PATH, PAIRWISE_PROMPT_PATH]
SCHEMA_FILES_WITH_RED_FLAGS = [
    config.SCHEMAS_DIR / "judge_score.schema.json",
    config.SCHEMAS_DIR / "anchored_judge_score.schema.json",
    config.SCHEMAS_DIR / "pairwise_score.schema.json",
]


def test_descriptions_cover_enum_exactly_once() -> None:
    """Every RedFlag value has exactly one description; no extras."""
    enum_values = {rf.value for rf in RedFlag}
    desc_values = {rf.value for rf in RED_FLAG_DESCRIPTIONS.keys()}
    missing = enum_values - desc_values
    extra = desc_values - enum_values
    assert not missing, f"RedFlag values missing from RED_FLAG_DESCRIPTIONS: {missing}"
    assert not extra, f"RED_FLAG_DESCRIPTIONS has keys not in RedFlag: {extra}"
    # No duplicate descriptions either (keys are enum members, so this is
    # implicit, but check description strings are non-empty and distinct).
    for rf, desc in RED_FLAG_DESCRIPTIONS.items():
        assert desc.strip(), f"Empty description for {rf.value}"


def test_render_labels_only_contains_every_enum_value() -> None:
    rendered = render_red_flag_vocabulary("labels_only")
    for rf in RedFlag:
        assert f"`{rf.value}`" in rendered, f"Missing {rf.value} in labels_only render"
    # No extra labels
    rendered_labels = set(re.findall(r"`([a-z_]+)`", rendered))
    assert rendered_labels == {rf.value for rf in RedFlag}


def test_render_labels_with_descriptions_matches_enum() -> None:
    rendered = render_red_flag_vocabulary("labels_with_descriptions")
    for rf in RedFlag:
        assert f"`{rf.value}`" in rendered
        assert RED_FLAG_DESCRIPTIONS[rf] in rendered, f"Description missing for {rf.value}"


def test_render_unknown_style_errors() -> None:
    with pytest.raises(ValueError):
        render_red_flag_vocabulary("not_a_style")


def test_prompt_files_use_placeholder_not_hardcoded_list() -> None:
    """Each prompt must contain the placeholder. It must NOT contain a
    recognizable hardcoded enum-label bullet list.
    """
    placeholders = ("{{RED_FLAGS_VOCABULARY}}", "{{RED_FLAGS_VOCABULARY_WITH_DESCRIPTIONS}}")
    for path in PROMPT_FILES:
        raw = path.read_text()
        assert any(p in raw for p in placeholders), (
            f"{path.name} missing RED_FLAGS_VOCABULARY placeholder — the vocabulary "
            f"must be derived from the RedFlag enum at render time, not hardcoded"
        )
        # Heuristic drift check: count backticked snake_case labels matching
        # any enum value in the RAW prompt file. If the file hardcodes the
        # list (instead of relying on the placeholder), three or more
        # backticked enum values will appear. The placeholder itself
        # contains no backticked labels.
        hardcoded_hits = sum(1 for rf in RedFlag if f"`{rf.value}`" in raw)
        assert hardcoded_hits < 3, (
            f"{path.name} appears to hardcode the red-flag list "
            f"(found {hardcoded_hits} backticked enum labels). Replace with "
            f"the {{{{RED_FLAGS_VOCABULARY}}}} placeholder."
        )


def test_substitute_red_flag_vocabulary_covers_every_enum_value() -> None:
    """After substitution, every enum value must appear in each prompt."""
    for path in PROMPT_FILES:
        rendered = _substitute_red_flag_vocabulary(path.read_text())
        missing = [rf.value for rf in RedFlag if rf.value not in rendered]
        assert not missing, f"{path.name} render missing enum values: {missing}"


def test_substitution_is_idempotent_and_leaves_no_placeholder() -> None:
    for path in PROMPT_FILES:
        rendered = _substitute_red_flag_vocabulary(path.read_text())
        assert "{{RED_FLAGS_VOCABULARY}}" not in rendered
        assert "{{RED_FLAGS_VOCABULARY_WITH_DESCRIPTIONS}}" not in rendered
        # Re-render (idempotent — templates without placeholders are unchanged)
        assert _substitute_red_flag_vocabulary(rendered) == rendered


def test_schema_enums_match_red_flag_enum() -> None:
    """Generated JSON schemas must have an enum list identical to RedFlag.

    Guards against the case where someone edits models.py without re-running
    `psycheeval.export_schemas`, so the on-disk schemas diverge from the
    live enum.
    """
    enum_values = [rf.value for rf in RedFlag]
    for schema_path in SCHEMA_FILES_WITH_RED_FLAGS:
        assert schema_path.exists(), f"Missing schema: {schema_path}"
        schema = json.loads(schema_path.read_text())
        # RedFlag appears inside $defs; pydantic v2 names it "RedFlag".
        defs = schema.get("$defs", {}) or schema.get("definitions", {})
        rf_def = defs.get("RedFlag")
        assert rf_def is not None, f"{schema_path.name} has no RedFlag definition"
        schema_enum = rf_def.get("enum")
        assert schema_enum is not None, f"{schema_path.name} RedFlag has no enum list"
        assert list(schema_enum) == enum_values, (
            f"{schema_path.name} RedFlag enum drifted from Python enum.\n"
            f"  schema: {schema_enum}\n"
            f"  python: {enum_values}\n"
            f"  Run `uv run python -m psycheeval.export_schemas` to resync."
        )
