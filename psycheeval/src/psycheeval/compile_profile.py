"""Compile profile bundles (C1-C5) from synthetic user records.

One call per user. Uses prompt 03_profile_compilation.md.
Output: data/{pilot}/profile_bundles.jsonl

Usage:
    uv run python -m psycheeval.compile_profile --pilot micro_pilot
"""

from __future__ import annotations

import argparse
import json

from psycheeval import config
from psycheeval.io import append_jsonl, read_jsonl, write_jsonl
from psycheeval.llm import complete, extract_json
from psycheeval.models import ProfileBundle, SourcePacket, SynthUserRecord
from psycheeval.normalize import normalize_profile_bundle


COMPILE_PROMPT_PATH = config.PROMPTS_DIR / "03_profile_compilation.md"


def compile_bundle(
    user: SynthUserRecord,
    source_packet: SourcePacket | None = None,
    *,
    model_key: str = "opus",
    temperature: float = 0.5,
) -> ProfileBundle:
    system = COMPILE_PROMPT_PATH.read_text()
    payload: dict = {"synth_user_record": user.model_dump()}
    if source_packet is not None:
        payload["source_packet"] = source_packet.model_dump()
    usr = json.dumps(payload, indent=2)

    response = complete(system=system, user=usr, model_key=model_key, temperature=temperature, timeout=600)
    data = extract_json(response.content)
    data = normalize_profile_bundle(data)

    data.setdefault("profile_bundle_id", f"bundle_{user.user_id}")
    data.setdefault("user_id", user.user_id)

    return ProfileBundle.model_validate(data)


def compile_for_pilot(
    pilot_name: str = "micro_pilot",
    *,
    model_key: str = "opus",
) -> list[ProfileBundle]:
    pilot_dir = config.pilot_dir(pilot_name)

    users_path = pilot_dir / "synthetic_user_records.jsonl"
    users = list(read_jsonl(users_path, SynthUserRecord))

    packets_path = pilot_dir / "source_packets.jsonl"
    packets_by_alias: dict[str, SourcePacket] = {}
    if packets_path.exists():
        packets_by_alias = {p.alias: p for p in read_jsonl(packets_path, SourcePacket)}

    # Load persona seeds to map user -> alias for packet lookup
    from psycheeval.models import PersonaSeed

    all_seeds: dict[str, PersonaSeed] = {}
    for path in [config.SEED_BANK_PUBLIC, config.SEED_BANK_SYNTHETIC]:
        for seed in read_jsonl(path, PersonaSeed):
            all_seeds[seed.persona_id] = seed

    out_path = pilot_dir / "profile_bundles.jsonl"
    done_user_ids: set[str] = set()
    if out_path.exists():
        for b in read_jsonl(out_path, ProfileBundle):
            done_user_ids.add(b.user_id)

    bundles: list[ProfileBundle] = []
    failures: list[tuple[str, str]] = []
    for user in users:
        if user.user_id in done_user_ids:
            print(f"  {user.user_id}: already done, skipping")
            continue
        seed = all_seeds.get(user.persona_seed_id)
        alias = seed.alias if seed else None
        packet = packets_by_alias.get(alias) if alias else None
        print(f"Compiling bundle for {alias or user.user_id}…", flush=True)
        try:
            bundle = compile_bundle(user, source_packet=packet, model_key=model_key)
            append_jsonl(out_path, bundle)
            bundles.append(bundle)
            print(f"  OK {alias or user.user_id}", flush=True)
        except Exception as e:
            msg = str(e)[:300]
            failures.append((alias or user.user_id, msg))
            print(f"  FAIL {alias or user.user_id}: {msg}", flush=True)

    print(f"Wrote {len(bundles)} profile bundles to {out_path}")
    if failures:
        print(f"Failures: {len(failures)}")
        for a, msg in failures:
            print(f"  - {a}: {msg}")
    return bundles


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pilot", default="micro_pilot")
    ap.add_argument("--model", default="opus", choices=["opus", "gpt-5.4", "kimi-k2.6"])
    args = ap.parse_args()
    compile_for_pilot(pilot_name=args.pilot, model_key=args.model)


if __name__ == "__main__":
    main()
