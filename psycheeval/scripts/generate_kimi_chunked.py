#!/usr/bin/env python3
"""Chunked generation of synthetic user records with Kimi K2.6.

Resumes from existing output. Processes one persona at a time to avoid
losing progress on timeout/interruption.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from psycheeval import config
from psycheeval.io import append_jsonl, read_jsonl
from psycheeval.llm import OpenRouterAPIError, complete, extract_json
from psycheeval.models import PersonaSeed, SourcePacket, SynthUserRecord
from psycheeval.normalize import normalize_synth_user_record
from datetime import date


def generate_user(
    seed: PersonaSeed,
    source_packet: SourcePacket | None = None,
    *,
    model_key: str = "kimi-k2.6",
    max_retries: int = 3,
) -> SynthUserRecord:
    system = (config.PROMPTS_DIR / "02_synthetic_user_generation.md").read_text()
    payload: dict = {"persona_seed": seed.model_dump()}
    if source_packet is not None:
        payload["source_packet"] = source_packet.model_dump()
    user = json.dumps(payload, indent=2)

    for attempt in range(max_retries):
        try:
            response = complete(
                system=system,
                user=user,
                model_key=model_key,
                temperature=0.8,
                timeout=300,
            )
        except Exception as e:
            print(f"    API error (attempt {attempt+1}): {e}")
            continue

        if not response.content.strip():
            print(f"    Empty response (attempt {attempt+1})")
            continue

        try:
            data = extract_json(response.content)
            data = normalize_synth_user_record(data)
        except Exception as e:
            print(f"    JSON parse/normalize failed (attempt {attempt+1}): {e}")
            debug_path = Path(f"/tmp/kimi_fail_{seed.alias.replace(' ', '_')}_{attempt}.txt")
            debug_path.write_text(response.content)
            print(f"    Saved raw response to {debug_path}")
            continue

        data.setdefault("user_id", f"user_{seed.persona_id}")
        data.setdefault("persona_seed_id", seed.persona_id)
        data.setdefault("generation_model", response.model_resolved)
        data.setdefault("generation_date", date.today().isoformat())

        return SynthUserRecord.model_validate(data)

    raise RuntimeError(f"Failed to generate {seed.alias} after {max_retries} attempts")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", default="micro_pilot_kimi")
    ap.add_argument("--model", default="kimi-k2.6")
    args = ap.parse_args()

    pilot_dir = config.pilot_dir(args.pilot)
    pilot_dir.mkdir(parents=True, exist_ok=True)

    all_public = {s.persona_id: s for s in read_jsonl(config.SEED_BANK_PUBLIC, PersonaSeed)}
    all_synth = {s.persona_id: s for s in read_jsonl(config.SEED_BANK_SYNTHETIC, PersonaSeed)}

    packets_path = pilot_dir / "source_packets.jsonl"
    packets_by_alias: dict[str, SourcePacket] = {}
    if packets_path.exists():
        packets_by_alias = {p.alias: p for p in read_jsonl(packets_path, SourcePacket)}

    targets = config.MICRO_PILOT_PUBLIC_INSPIRED + config.MICRO_PILOT_PURE_SYNTHETIC
    out_path = pilot_dir / "synthetic_user_records.jsonl"

    done_ids: set[str] = set()
    if out_path.exists():
        for rec in read_jsonl(out_path, SynthUserRecord):
            done_ids.add(rec.persona_seed_id)
        print(f"Found {len(done_ids)} existing records. Resuming...")

    records = []
    failures = []

    for persona_id in targets:
        if persona_id in done_ids:
            print(f"SKIP {persona_id}: already done")
            continue

        seed = all_public.get(persona_id) or all_synth.get(persona_id)
        if seed is None:
            print(f"SKIP {persona_id}: not in any seed bank")
            continue

        packet = packets_by_alias.get(seed.alias)
        print(f"Generating {seed.alias}…", flush=True)
        try:
            record = generate_user(seed, source_packet=packet, model_key=args.model)
            append_jsonl(out_path, record)
            records.append(record)
            print(f"  OK {seed.alias}", flush=True)
        except Exception as e:
            msg = str(e)[:300]
            failures.append((seed.alias, msg))
            print(f"  FAIL {seed.alias}: {msg}", flush=True)

    print(f"\nWrote {len(records)} new records to {out_path}")
    if failures:
        print(f"Failures: {len(failures)}")
        for alias, msg in failures:
            print(f"  - {alias}: {msg}")


if __name__ == "__main__":
    main()
