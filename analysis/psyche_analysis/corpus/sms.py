"""Parser for SMS/chat normalized JSONL."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import os

import orjson

from .types import TextSample


# Names that represent the user (self).
# Real names are intentionally NOT hardcoded (this repo is public). Set
# PSYCHE_SELF_NAMES as a comma-separated list (e.g. "First,First Last") to
# match messages exported with your real name as the speaker. "Me" and the
# SMS type=2 (sent) heuristic always apply.
SELF_NAMES = {"Me"} | {
    n.strip() for n in os.environ.get("PSYCHE_SELF_NAMES", "").split(",") if n.strip()
}


def parse_sms(path: Path) -> list[TextSample]:
    """Parse normalized.jsonl into TextSamples.

    Format: JSONL with keys: id, ts, speaker, text, thread_id
    Only includes messages from self (speaker matching SELF_NAMES or type=2 sent).
    """
    samples: list[TextSample] = []

    with open(path, "rb") as f:
        for line in f:
            if not line.strip():
                continue

            msg = orjson.loads(line)
            text = msg.get("text", "")
            if not text or len(text.split()) < 3:
                continue

            speaker = msg.get("speaker", "")
            meta = msg.get("meta", {})
            raw_attrs = meta.get("raw_attrs", {})

            # SMS type=2 means sent (from self)
            is_self = (
                speaker in SELF_NAMES
                or raw_attrs.get("type") == "2"
            )

            ts_str = msg.get("ts")
            ts = datetime.fromisoformat(ts_str) if ts_str else None

            samples.append(
                TextSample(
                    id=f"sms-{msg.get('id', '')}",
                    source="sms",
                    author="self" if is_self else speaker,
                    timestamp=ts,
                    text=text,
                )
            )

    return samples
