"""Source-hunting for public-inspired personas.

Workflow per the PsycheEval plan §2.4:

1. If `data/source_packets/{alias}_raw.jsonl` exists, use it (this is the
   handoff point for an external codex-researcher run — launched from a
   Claude Code session via the subagent, written to disk for this script
   to pick up).
2. Otherwise, call GPT-5.4 directly with a retrieval-style prompt. This is
   the "high-level public reputation fallback" path — it produces a
   `raw_sources` list where `url` is best-effort (may be empty or
   approximate). These packets get `source_grounding: "low"`.
3. Either way, feed `raw_sources` through the kit §7 ingestion prompt to
   produce a structured `SourcePacket`.

Usage:
    uv run python -m psycheeval.source_hunt --pilot micro --fallback-only

The `--fallback-only` flag skips step 1 and always uses GPT-5.4. Useful for
a fast first pass before running external codex-researcher.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from psycheeval import config
from psycheeval.io import read_jsonl, write_jsonl
from psycheeval.llm import complete, extract_json
from psycheeval.models import PersonaSeed, SourceGrounding, SourcePacket


HUNT_SYSTEM = """You are a research assistant gathering public material about a named public figure.

Return a list of 3-8 representative public items (essays, interviews, talks, papers, posts) that illustrate this person's characteristic worldview, rhetorical posture, and decision style.

For each item include:
- url (if you know a real, verifiable URL; otherwise empty string)
- source_type (essay, interview, talk, paper, post, book, etc.)
- short_description (1-2 sentences)
- representative_excerpt (≤80 words, a phrase or short sentence illustrating their voice — do NOT fabricate. If you aren't confident it's a real quote, write "" and describe the theme instead.)

Do not invent URLs. Do not fabricate quotes. Do not infer private life, health, relationships, or unpublished beliefs.

Return JSON with this shape:
{
  "sources": [{"url": "...", "source_type": "...", "short_description": "...", "representative_excerpt": "..."}, ...],
  "coverage_note": "one sentence on what dimensions of this person's public output are represented and what isn't"
}
"""


def hunt_sources_gpt(anchor: str, anchor_family: str) -> list[dict]:
    """Call GPT-5.4 to surface known public material for an anchor."""
    user = (
        f"Public figure: {anchor}\n"
        f"Anchor family: {anchor_family}\n\n"
        "Gather representative public material per the system prompt."
    )
    response = complete(
        system=HUNT_SYSTEM,
        user=user,
        model_key="gpt-5.4",
        temperature=0.3,
    )
    data = extract_json(response.content)
    if isinstance(data, dict) and "sources" in data:
        return data["sources"]
    if isinstance(data, list):
        return data
    return []


INGEST_PROMPT_PATH = config.PROMPTS_DIR / "01_source_packet_ingestion.md"


def ingest_to_packet(seed: PersonaSeed, raw_sources: list[dict]) -> SourcePacket:
    """Feed raw_sources through the kit §7 ingestion prompt to build a SourcePacket."""
    system = INGEST_PROMPT_PATH.read_text()
    user = json.dumps(
        {
            "alias": seed.alias,
            "internal_public_anchor": seed.internal_public_anchor,
            "anchor_family": seed.anchor_family,
            "raw_sources": raw_sources,
        },
        indent=2,
    )

    # Use Opus for ingestion — it's less prone to cheerful fabrication under a
    # "be rigorous about what you don't know" prompt.
    response = complete(system=system, user=user, model_key="opus", temperature=0.3)
    data = extract_json(response.content)

    # Fill defaults that the LLM may omit
    data.setdefault("source_packet_id", f"sp_{seed.alias.lower().replace(' ', '_').replace('-', '_')}_001")
    data.setdefault("alias", seed.alias)
    data.setdefault("internal_public_anchor", seed.internal_public_anchor)
    data.setdefault("source_count", len(raw_sources))
    data.setdefault("raw_sources", raw_sources)

    # Grounding: high if 3+ sources with non-empty URLs, medium if 1-2 or
    # only descriptions, low otherwise.
    if "source_grounding" not in data:
        real_urls = sum(1 for s in raw_sources if s.get("url"))
        if real_urls >= 3:
            data["source_grounding"] = SourceGrounding.HIGH
        elif real_urls >= 1:
            data["source_grounding"] = SourceGrounding.MEDIUM
        else:
            data["source_grounding"] = SourceGrounding.LOW

    return SourcePacket.model_validate(data)


def hunt_for_pilot(pilot_name: str = "micro_pilot", fallback_only: bool = False) -> list[SourcePacket]:
    pilot_out = config.pilot_dir(pilot_name)
    pilot_out.mkdir(parents=True, exist_ok=True)
    config.SOURCE_PACKETS_DIR.mkdir(parents=True, exist_ok=True)

    all_public = {s.persona_id: s for s in read_jsonl(config.SEED_BANK_PUBLIC, PersonaSeed)}

    target_ids = config.MICRO_PILOT_PUBLIC_INSPIRED
    packets: list[SourcePacket] = []

    for persona_id in target_ids:
        if persona_id not in all_public:
            print(f"  SKIP: {persona_id} not in public seed bank", file=sys.stderr)
            continue
        seed = all_public[persona_id]
        alias_slug = seed.alias.lower().replace(" ", "_").replace("-", "_")

        raw_path = config.SOURCE_PACKETS_DIR / f"{alias_slug}_raw.jsonl"
        raw_sources: list[dict] = []

        if not fallback_only and raw_path.exists():
            with raw_path.open() as fh:
                raw_sources = [json.loads(line) for line in fh if line.strip()]
            print(f"  {seed.alias}: loaded {len(raw_sources)} sources from {raw_path.name}")
        else:
            print(f"  {seed.alias}: calling GPT-5.4 for high-level public reputation…")
            raw_sources = hunt_sources_gpt(
                anchor=seed.internal_public_anchor or seed.alias,
                anchor_family=seed.anchor_family or "",
            )
            # Persist raw to disk for audit trail
            with raw_path.open("w") as fh:
                for s in raw_sources:
                    fh.write(json.dumps(s) + "\n")

        packet = ingest_to_packet(seed, raw_sources)
        packets.append(packet)
        print(f"    grounding={packet.source_grounding}, count={packet.source_count}")

    out_path = pilot_out / "source_packets.jsonl"
    n = write_jsonl(out_path, packets)
    print(f"Wrote {n} source packets to {out_path}")
    return packets


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pilot", default="micro_pilot", help="Pilot name (default: micro_pilot)")
    ap.add_argument(
        "--fallback-only",
        action="store_true",
        help="Skip pre-retrieved raw sources; always call GPT-5.4",
    )
    args = ap.parse_args()
    hunt_for_pilot(pilot_name=args.pilot, fallback_only=args.fallback_only)


if __name__ == "__main__":
    main()
