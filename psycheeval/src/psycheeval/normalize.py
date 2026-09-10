"""Normalize LLM-produced JSON into the shapes our pydantic models expect.

LLMs emit plausible-but-varied keys ("score" vs "score_1_to_7", "text" vs
"item", wrapping the response in an outer key like "synth_user_record", etc).
Rather than fight pydantic, we patch the dict first.
"""

from __future__ import annotations

from typing import Any

# Keys that LLMs sometimes use to wrap the response object. Unwrap if present.
_UNWRAP_KEYS = {
    "synth_user_record",
    "synthetic_user_record",
    "user_record",
    "record",
    "user",
    "profile_bundle",
    "bundle",
    "source_packet",
    "packet",
    "scenario",
}


def unwrap(data: Any) -> Any:
    """If the top-level object is a single-key wrapper, unwrap it."""
    if isinstance(data, dict) and len(data) == 1:
        only_key = next(iter(data))
        if only_key.lower() in _UNWRAP_KEYS:
            inner = data[only_key]
            if isinstance(inner, dict):
                return inner
    return data


# --- Instrument/interview item normalization --------------------------------

_ITEM_KEYS = ("item", "text", "label", "statement", "prompt", "question", "item_text")
_SCORE_KEYS = ("score_1_to_7", "score", "rating", "response", "answer_score", "value")

# Canonical 20 Likert items from prompts/02_synthetic_user_generation.md.
# If the LLM returns only {item_id, score, tag}, rehydrate text by position.
CANONICAL_LIKERT_ITEMS: list[str] = [
    "I prefer direct criticism to vague encouragement.",
    "I am comfortable staying uncertain about important questions for a long time.",
    "I tend to think in abstractions before I think in specifics.",
    "I will pursue a disagreement to its conclusion even when it's socially costly.",
    "I resent being told what I should want.",
    "Flattery sometimes lands on me even when I know it's flattery.",
    "I am harsher with myself after a failure than the situation calls for.",
    "I want my work to be larger in scope than it currently is.",
    "I can sit with a problem for weeks without forcing a resolution.",
    "Other people's suffering is a real consideration in how I decide things.",
    "I am drawn toward problems that haven't been solved yet more than problems that have.",
    "I believe older institutions and practices deserve more weight than they usually get.",
    "I trust most mainstream institutions to function reasonably well.",
    "Criticism usually makes me work harder rather than shutting me down.",
    "I tend to explain things at greater length than is strictly necessary.",
    "I often assume people understand more of what I mean than they actually do.",
    "I am sensitive to status cues, including ones I don't endorse.",
    "When a relationship breaks, I am drawn more toward repair than toward distance.",
    "I want language to be more precise than it usually is.",
    "I am comfortable when other people are emotionally expressive.",
]


def _pick_first(d: dict, keys: tuple[str, ...]) -> Any:
    for k in keys:
        if k in d:
            return d[k]
    return None


def normalize_instrument_item(raw: dict, *, index_hint: int | None = None) -> dict:
    item_text = _pick_first(raw, _ITEM_KEYS)
    score = _pick_first(raw, _SCORE_KEYS)

    # Fallback: hydrate item text from canonical list by item_id/number/index
    if item_text is None:
        item_idx = None
        for key in ("item_id", "item_number", "id", "number", "index"):
            if key in raw:
                try:
                    item_idx = int(raw[key]) - 1  # 1-indexed to 0-indexed
                    break
                except (TypeError, ValueError):
                    pass
        if item_idx is None and index_hint is not None:
            item_idx = index_hint
        if item_idx is not None and 0 <= item_idx < len(CANONICAL_LIKERT_ITEMS):
            item_text = CANONICAL_LIKERT_ITEMS[item_idx]

    if item_text is None or score is None:
        return raw  # let pydantic yell
    try:
        score = int(score)
    except (TypeError, ValueError):
        return raw
    return {"item": str(item_text), "score_1_to_7": max(1, min(7, score))}


_QUESTION_KEYS = ("question", "q", "prompt", "item")
_ANSWER_KEYS = ("answer", "a", "response", "text")


def normalize_interview_answer(raw: dict) -> dict:
    q = _pick_first(raw, _QUESTION_KEYS)
    a = _pick_first(raw, _ANSWER_KEYS)
    if q is None or a is None:
        return raw
    return {"question": str(q), "answer": str(a)}


# --- Top-level user record normalization ------------------------------------


def normalize_synth_user_record(data: dict) -> dict:
    data = unwrap(data)
    if not isinstance(data, dict):
        return data

    # Sometimes LLM puts user_artifacts fields at top level
    ua = data.get("user_artifacts")
    if not isinstance(ua, dict):
        # Try to hoist expected fields from the top level
        hoisted = {}
        for key in [
            "self_description_250w",
            "values_ranked",
            "work_style_note",
            "conflict_reaction_note",
            "bad_day_diary",
            "decision_memo",
            "writing_sample_1",
            "writing_sample_2",
            "interview_answers",
            "instrument_like_answers",
        ]:
            if key in data:
                hoisted[key] = data.pop(key)
        if hoisted:
            data["user_artifacts"] = hoisted
            ua = hoisted

    if isinstance(ua, dict):
        # Normalize instrument items (pass index hint for text rehydration)
        ili = ua.get("instrument_like_answers")
        if isinstance(ili, list):
            ua["instrument_like_answers"] = [
                normalize_instrument_item(x, index_hint=i) if isinstance(x, dict) else x
                for i, x in enumerate(ili)
            ]
        # Normalize interview answers
        ia = ua.get("interview_answers")
        if isinstance(ia, list):
            ua["interview_answers"] = [
                normalize_interview_answer(x) if isinstance(x, dict) else x for x in ia
            ]

    return data


_C_KEYS = (
    "C1_trait_labels",
    "C2_narrative",
    "C3_behavioral_contract",
    "C4_behavioral_contract_anti_sycophancy",
    "C5_source_packet_informed",
    "C5_contract",
)


def normalize_profile_bundle(data: dict) -> dict:
    data = unwrap(data)
    if not isinstance(data, dict):
        return data

    # Alias: user_id is the canonical key
    if "user_id" not in data:
        for alt in ("synth_user_id", "synthetic_user_id", "record_id"):
            if alt in data:
                data["user_id"] = data.pop(alt)
                break

    # If condition keys are at top-level, hoist them into profile_conditions
    if "profile_conditions" not in data:
        hoisted: dict = {}
        for key in _C_KEYS:
            if key in data:
                hoisted[key] = data.pop(key)
        if hoisted:
            data["profile_conditions"] = hoisted

    # Also tolerate short keys like "C1", "C2" etc.
    short_to_long = {
        "C1": "C1_trait_labels",
        "C2": "C2_narrative",
        "C3": "C3_behavioral_contract",
        "C4": "C4_behavioral_contract_anti_sycophancy",
        "C5": "C5_source_packet_informed",
        "C5_CONTRACT": "C5_contract",
    }
    if "profile_conditions" in data and isinstance(data["profile_conditions"], dict):
        pc = data["profile_conditions"]
        for short, long in short_to_long.items():
            if short in pc and long not in pc:
                pc[long] = pc.pop(short)
    else:
        # Short keys at top level
        hoisted = {}
        for short, long in short_to_long.items():
            if short in data:
                hoisted[long] = data.pop(short)
        if hoisted:
            data["profile_conditions"] = hoisted

    return data


def normalize_source_packet(data: dict) -> dict:
    return unwrap(data)


def normalize_scenario(data: dict) -> dict:
    return unwrap(data)
