"""Persona-type lookup for a pilot's synthetic users.

Which conditions apply to which persona is a property of the persona's *type*
(public-inspired personas carry a source packet; pure-synthetic ones cannot),
so the generation preflight needs the type per user. This is the pilot-scoped
version of the index judge.py builds for pairwise PI gating.
"""

from __future__ import annotations

from psycheeval import config
from psycheeval.io import read_jsonl
from psycheeval.models import PersonaSeed, SynthUserRecord

PUBLIC_INSPIRED = "public_inspired"


def seed_type_index() -> dict[str, str]:
    """persona_seed.persona_id → persona_type, across both seed banks."""
    index: dict[str, str] = {}
    for path in (config.SEED_BANK_PUBLIC, config.SEED_BANK_SYNTHETIC):
        if not path.exists():
            continue
        for seed in read_jsonl(path, PersonaSeed):
            index[seed.persona_id] = str(seed.persona_type)
    return index


def persona_type_index(pilot_name: str) -> dict[str, str]:
    """synthetic_user_record.user_id → persona_type, for one pilot."""
    seeds = seed_type_index()
    users_path = config.pilot_dir(pilot_name) / "synthetic_user_records.jsonl"
    if not users_path.exists():
        return {}
    index: dict[str, str] = {}
    for user in read_jsonl(users_path, SynthUserRecord):
        ptype = seeds.get(user.persona_seed_id)
        if ptype is not None:
            index[user.user_id] = ptype
    return index
