"""LLM helper tests — pure functions only, no API calls."""

from __future__ import annotations

import pytest

from psycheeval.llm import extract_json, extract_jsonl, JSONExtractionError


def test_extract_json_direct():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_with_fence():
    content = """Here is the JSON:
```json
{"a": 1, "b": [2, 3]}
```
That's it."""
    assert extract_json(content) == {"a": 1, "b": [2, 3]}


def test_extract_json_bare_fence():
    content = """```
{"x": "y"}
```"""
    assert extract_json(content) == {"x": "y"}


def test_extract_json_bracket_scanning():
    content = "The result is {\"name\": \"Slalom\", \"score\": 3} and that's all."
    assert extract_json(content) == {"name": "Slalom", "score": 3}


def test_extract_json_failure():
    with pytest.raises(JSONExtractionError):
        extract_json("not json at all")


def test_extract_jsonl_basic():
    content = '{"a": 1}\n{"a": 2}\n{"a": 3}\n'
    items = extract_jsonl(content)
    assert len(items) == 3
    assert items[0] == {"a": 1}
    assert items[2] == {"a": 3}


def test_extract_jsonl_with_fence():
    content = """```jsonl
{"a": 1}
{"a": 2}
```"""
    items = extract_jsonl(content)
    assert len(items) == 2


def test_extract_jsonl_empty_lines_ignored():
    content = '{"a": 1}\n\n{"a": 2}\n\n'
    items = extract_jsonl(content)
    assert len(items) == 2
