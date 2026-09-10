"""Generate evaluation scenarios from user records + profile bundles.

One call per user, producing 6 scenarios. Uses prompt 04_scenario_generation.md.
Output: data/{pilot}/scenarios.jsonl

Usage:
    uv run python -m psycheeval.generate_scenarios --pilot micro_pilot --n 6
"""

from __future__ import annotations

import argparse
import json

from psycheeval import config
from psycheeval.io import append_jsonl, read_jsonl, write_jsonl
from psycheeval.llm import complete, extract_json, extract_jsonl
from psycheeval.models import (
    PersonaSeed,
    ProfileBundle,
    Scenario,
    SourcePacket,
    SynthUserRecord,
)
from psycheeval.normalize import normalize_scenario


SCEN_PROMPT_PATH = config.PROMPTS_DIR / "04_scenario_generation.md"


def generate_scenarios_for_user(
    user: SynthUserRecord,
    bundle: ProfileBundle,
    source_packet: SourcePacket | None = None,
    *,
    n: int = 6,
    model_key: str = "opus",
    temperature: float = 0.8,
) -> list[Scenario]:
    system = SCEN_PROMPT_PATH.read_text() + f"\n\nGenerate exactly {n} scenarios."
    payload: dict = {
        "synth_user_record": user.model_dump(),
        "profile_bundle": bundle.model_dump(),
    }
    if source_packet is not None:
        payload["source_packet"] = source_packet.model_dump()
    usr = json.dumps(payload, indent=2)

    response = complete(system=system, user=usr, model_key=model_key, temperature=temperature, timeout=600)
    # Prefer JSONL; fall back to JSON array if the LLM returned one.
    try:
        items = extract_jsonl(response.content)
    except Exception:
        data = extract_json(response.content)
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "scenarios" in data:
            items = data["scenarios"]
        else:
            raise

    scenarios: list[Scenario] = []
    for ix, raw in enumerate(items):
        raw = normalize_scenario(raw)
        raw.setdefault("user_id", user.user_id)
        raw.setdefault(
            "scenario_id",
            f"scn_{raw.get('scenario_family', 'mixed')}_{ix:02d}_{user.user_id}",
        )
        scenarios.append(Scenario.model_validate(raw))

    return scenarios


def generate_for_pilot(
    pilot_name: str = "micro_pilot",
    *,
    n: int = 6,
    model_key: str = "opus",
) -> list[Scenario]:
    pilot_dir = config.pilot_dir(pilot_name)

    users = {u.user_id: u for u in read_jsonl(pilot_dir / "synthetic_user_records.jsonl", SynthUserRecord)}
    bundles = {b.user_id: b for b in read_jsonl(pilot_dir / "profile_bundles.jsonl", ProfileBundle)}

    packets_path = pilot_dir / "source_packets.jsonl"
    packets_by_alias: dict[str, SourcePacket] = {}
    if packets_path.exists():
        packets_by_alias = {p.alias: p for p in read_jsonl(packets_path, SourcePacket)}

    all_seeds: dict[str, PersonaSeed] = {}
    for path in [config.SEED_BANK_PUBLIC, config.SEED_BANK_SYNTHETIC]:
        for seed in read_jsonl(path, PersonaSeed):
            all_seeds[seed.persona_id] = seed

    out_path = pilot_dir / "scenarios.jsonl"
    done_user_ids: set[str] = set()
    if out_path.exists():
        for s in read_jsonl(out_path, Scenario):
            done_user_ids.add(s.user_id)

    all_scenarios: list[Scenario] = []
    failures: list[tuple[str, str]] = []
    for user_id, user in users.items():
        if user_id in done_user_ids:
            print(f"  {user_id}: already has scenarios, skipping")
            continue
        bundle = bundles.get(user_id)
        if bundle is None:
            print(f"SKIP {user_id}: no profile bundle")
            continue
        seed = all_seeds.get(user.persona_seed_id)
        packet = packets_by_alias.get(seed.alias) if seed else None
        print(f"Generating {n} scenarios for {seed.alias if seed else user_id}…", flush=True)
        try:
            scenarios = generate_scenarios_for_user(
                user, bundle, source_packet=packet, n=n, model_key=model_key
            )
            for s in scenarios:
                append_jsonl(out_path, s)
            all_scenarios.extend(scenarios)
            print(f"  OK ({len(scenarios)} scenarios)", flush=True)
        except Exception as e:
            msg = str(e)[:300]
            failures.append((seed.alias if seed else user_id, msg))
            print(f"  FAIL: {msg}", flush=True)

    print(f"Wrote {len(all_scenarios)} scenarios to {out_path}")
    if failures:
        print(f"Failures: {len(failures)}")
        for a, msg in failures:
            print(f"  - {a}: {msg}")
    return all_scenarios


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pilot", default="micro_pilot")
    ap.add_argument("--n", type=int, default=6)
    ap.add_argument("--model", default="opus", choices=["opus", "gpt-5.4", "kimi-k2.6"])
    args = ap.parse_args()
    generate_for_pilot(pilot_name=args.pilot, n=args.n, model_key=args.model)


if __name__ == "__main__":
    main()
