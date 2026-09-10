#!/usr/bin/env python3
"""Parallel generation of synthetic user records with Kimi K2.6."""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from psycheeval import config
from psycheeval.io import append_jsonl, read_jsonl
from psycheeval.llm import OpenRouterAPIError, complete, extract_json
from psycheeval.models import PersonaSeed, SourcePacket, SynthUserRecord
from psycheeval.normalize import normalize_synth_user_record


def generate_one(
    seed: PersonaSeed,
    source_packet: SourcePacket | None = None,
    *,
    model_key: str = "kimi-k2.6",
    max_retries: int = 2,
) -> SynthUserRecord | None:
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
            print(f"    {seed.alias}: API error (attempt {attempt+1}): {e}")
            continue

        if not response.content.strip():
            print(f"    {seed.alias}: Empty response (attempt {attempt+1})")
            continue

        try:
            data = extract_json(response.content)
            data = normalize_synth_user_record(data)
        except Exception as e:
            print(f"    {seed.alias}: JSON parse/normalize failed (attempt {attempt+1}): {e}")
            debug_path = Path(f"/tmp/kimi_fail_{seed.alias.replace(' ', '_')}_{attempt}.txt")
            debug_path.write_text(response.content)
            continue

        data.setdefault("user_id", f"user_{seed.persona_id}")
        data.setdefault("persona_seed_id", seed.persona_id)
        data.setdefault("generation_model", response.model_resolved)
        data.setdefault("generation_date", date.today().isoformat())

        return SynthUserRecord.model_validate(data)

    print(f"    {seed.alias}: FAILED after {max_retries} attempts")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", default="micro_pilot_kimi")
    ap.add_argument("--model", default="kimi-k2.6")
    ap.add_argument("--workers", type=int, default=2, help="Concurrent generation workers")
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

    # Remove malformed/incomplete file if it exists
    if out_path.exists():
        # Validate existing records
        valid = []
        try:
            for rec in read_jsonl(out_path, SynthUserRecord):
                if rec.user_id and rec.persona_seed_id:
                    valid.append(rec)
        except Exception:
            valid = []
        if len(valid) < 3:
            print(f"Existing file has only {len(valid)} valid records. Starting fresh.")
            out_path.unlink()
            valid = []
        else:
            print(f"Found {len(valid)} valid records. Resuming...")
    else:
        valid = []

    done_ids = {rec.persona_seed_id for rec in valid}

    # Build task list
    tasks = []
    for persona_id in targets:
        if persona_id in done_ids:
            continue
        seed = all_public.get(persona_id) or all_synth.get(persona_id)
        if seed is None:
            continue
        packet = packets_by_alias.get(seed.alias)
        tasks.append((seed, packet))

    print(f"Generating {len(tasks)} personas with {args.workers} workers...")

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_to_seed = {
            executor.submit(generate_one, seed, packet, model_key=args.model): seed
            for seed, packet in tasks
        }

        for future in as_completed(future_to_seed):
            seed = future_to_seed[future]
            try:
                record = future.result()
                if record is not None:
                    append_jsonl(out_path, record)
                    print(f"  OK {seed.alias}", flush=True)
                else:
                    print(f"  FAIL {seed.alias}", flush=True)
            except Exception as e:
                print(f"  FAIL {seed.alias}: {e}", flush=True)

    # Count final results
    final_count = sum(1 for _ in read_jsonl(out_path, SynthUserRecord))
    print(f"\nDone. Total valid records: {final_count}")


if __name__ == "__main__":
    main()
