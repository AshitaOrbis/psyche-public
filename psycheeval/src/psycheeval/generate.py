"""Generate SynthUserRecord objects from PersonaSeeds.

One call per persona. Uses prompt 02_synthetic_user_generation.md.
Output: data/{pilot}/synthetic_user_records.jsonl

Usage:
    uv run python -m psycheeval.generate --pilot micro_pilot --model opus
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from psycheeval import config
from psycheeval.io import append_jsonl, read_jsonl, write_jsonl
from psycheeval.llm import complete, extract_json
from psycheeval.models import PersonaSeed, SourcePacket, SynthUserRecord
from psycheeval.normalize import normalize_synth_user_record


GEN_PROMPT_PATH = config.PROMPTS_DIR / "02_synthetic_user_generation.md"


def generate_user(
    seed: PersonaSeed,
    source_packet: SourcePacket | None = None,
    *,
    model_key: str = "opus",
    temperature: float = 0.8,
) -> SynthUserRecord:
    system = GEN_PROMPT_PATH.read_text()
    payload: dict = {"persona_seed": seed.model_dump()}
    if source_packet is not None:
        payload["source_packet"] = source_packet.model_dump()
    user = json.dumps(payload, indent=2)

    response = complete(
        system=system,
        user=user,
        model_key=model_key,
        temperature=temperature,
        timeout=600,
    )
    data = extract_json(response.content)
    data = normalize_synth_user_record(data)

    # Fill in provenance fields if the LLM omitted them
    data.setdefault("user_id", f"user_{seed.persona_id}")
    data.setdefault("persona_seed_id", seed.persona_id)
    data.setdefault("generation_model", response.model_resolved)
    data.setdefault("generation_date", date.today().isoformat())

    return SynthUserRecord.model_validate(data)


def generate_for_pilot(
    pilot_name: str = "micro_pilot",
    *,
    model_key: str = "opus",
) -> list[SynthUserRecord]:
    pilot_dir = config.pilot_dir(pilot_name)
    pilot_dir.mkdir(parents=True, exist_ok=True)

    # Load seeds
    all_public = {s.persona_id: s for s in read_jsonl(config.SEED_BANK_PUBLIC, PersonaSeed)}
    all_synth = {s.persona_id: s for s in read_jsonl(config.SEED_BANK_SYNTHETIC, PersonaSeed)}

    # Load any source packets (keyed by persona_id via alias lookup)
    packets_path = pilot_dir / "source_packets.jsonl"
    packets_by_alias: dict[str, SourcePacket] = {}
    if packets_path.exists():
        packets_by_alias = {p.alias: p for p in read_jsonl(packets_path, SourcePacket)}

    targets = config.MICRO_PILOT_PUBLIC_INSPIRED + config.MICRO_PILOT_PURE_SYNTHETIC
    out_path = pilot_dir / "synthetic_user_records.jsonl"

    # Resume: skip personas already written
    done_ids: set[str] = set()
    if out_path.exists():
        for rec in read_jsonl(out_path, SynthUserRecord):
            done_ids.add(rec.persona_seed_id)

    records: list[SynthUserRecord] = []
    failures: list[tuple[str, str]] = []

    for persona_id in targets:
        if persona_id in done_ids:
            print(f"  {persona_id}: already done, skipping")
            continue
        seed = all_public.get(persona_id) or all_synth.get(persona_id)
        if seed is None:
            print(f"SKIP: {persona_id} not in any seed bank")
            continue

        packet = packets_by_alias.get(seed.alias)
        print(f"Generating {seed.alias}…", flush=True)
        try:
            record = generate_user(seed, source_packet=packet, model_key=model_key)
            append_jsonl(out_path, record)
            records.append(record)
            print(f"  OK {seed.alias}", flush=True)
        except Exception as e:
            msg = str(e)[:300]
            failures.append((seed.alias, msg))
            print(f"  FAIL {seed.alias}: {msg}", flush=True)

    print(f"Wrote {len(records)} user records to {out_path}")
    if failures:
        print(f"Failures: {len(failures)}")
        for alias, msg in failures:
            print(f"  - {alias}: {msg}")
    return records


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pilot", default="micro_pilot")
    ap.add_argument("--model", default="opus", choices=["opus", "gpt-5.4", "kimi-k2.6"])
    args = ap.parse_args()
    generate_for_pilot(pilot_name=args.pilot, model_key=args.model)


if __name__ == "__main__":
    main()
