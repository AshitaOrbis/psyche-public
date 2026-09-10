#!/usr/bin/env python3
"""Phase 5 human-rater pair selection (predeclared selection rule per
docs/v0_3_phase_minus_1_design_lock.md §-1.13).

Deterministic. Produces a 50-pair manifest from v0.3 pairwise records
plus v0.2 calibration anchors. Anonymizes condition labels and randomizes
A/B side per pair. Output is meant to be consumed by drivers/rater_cli.py.

Selection (predeclared, seed=42):
  - 32 pairs from v0.3 Tier 1 (16 pair types × 2 each, stratified by
    judge_model and user_id within each pair type)
  - 8 pairs from v0.3 Tier 2 ladder PRIMARY (4 steps × 2 each)
  - 10 pairs from v0.2 calibration anchors (unanimous 3-of-3 v0.2
    pairwise records spread across 4 v0.2 PRIMARY pair types)

A/B side anonymization seed=43.

The rater CLI / sheet sees only:
  rater_pair_id, scenario_id, scenario_prompt, profile_text_shown,
  response_a_text, response_b_text

All `_` prefixed fields are reserved for the D5 analyzer to re-join
the rater's responses against LLM-judge results post-rating.

Usage:
  PYTHONPATH=src python3 drivers/select_human_rater_pairs.py \
      --v03-tag 2026-05-19_v03 \
      --v02-tag 2026-04-26_v02_hard_codex_only \
      --pilot v03_full_pilot \
      --v02-pilot v02_hard_pilot

Outputs:
  runs/<v03-tag>/human_rater_inbox.jsonl     — 50 anonymized pairs
  runs/<v03-tag>/human_rater_manifest.md     — selection summary
"""

from __future__ import annotations
import argparse
import json
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# Predeclared frozen rule constants — DO NOT CHANGE post-lock.
SEED_PAIR_SELECTION = 42
SEED_AB_ANONYMIZATION = 43
N_T1 = 32       # 16 pair types × 2
N_T2 = 8        #  4 ladder steps × 2
N_V02_ANCHOR = 10
N_TOTAL = N_T1 + N_T2 + N_V02_ANCHOR  # 50

# v0.3 Tier 1 pair types (set of unordered {lo, hi})
T1_PAIR_TYPES: list[tuple[str, str]] = [
    ("C_GENERIC_CONTRACT", "C0"),
    ("C_GENERIC_CONTRACT", "C3"),
    ("C_GENERIC_CONTRACT", "C4"),
    ("C_GENERIC_CONTRACT", "C5"),
    ("C4_WRONG_PROFILE", "C0"),
    ("C4_WRONG_PROFILE", "C3"),
    ("C4_WRONG_PROFILE", "C4"),
    ("C4_WRONG_PROFILE", "C5"),
    ("C5_NONPUBLIC", "C5"),
    ("C5_NONPUBLIC", "C5_CONTRACT"),
    ("C5_NONPUBLIC", "C3"),
    ("C5_NONPUBLIC", "C4"),
    ("C5_NONPUBLIC_CONTRACT", "C5_NONPUBLIC"),
    ("C5_NONPUBLIC_CONTRACT", "C5_CONTRACT"),
    ("C5_NONPUBLIC_CONTRACT", "C3"),
    ("C5_NONPUBLIC_CONTRACT", "C4"),
]
assert len(T1_PAIR_TYPES) == 16

# v0.3 Tier 2 ladder PRIMARY (4 consecutive steps)
T2_LADDER_STEPS: list[tuple[str, str]] = [
    ("C5", "L1"),               # L0 → L1: contract presence
    ("L1", "L2"),               # L1 → L2: anti-mimicry
    ("L2", "L3"),               # L2 → L3: contract-first ordering
    ("L3", "C5_CONTRACT"),      # L3 → L4: expanded length
]
assert len(T2_LADDER_STEPS) == 4

# v0.2 calibration anchors (unanimous-3-of-3 v0.2 PRIMARY pair types)
V02_ANCHOR_PAIR_TYPES: list[tuple[str, str]] = [
    ("C4", "C0"),
    ("C4", "C5"),
    ("C5_CONTRACT", "C5"),
    ("C4", "C1_padded"),
]


def normalize_pair(a: str, b: str) -> tuple[str, str]:
    """Canonical sorted form of an unordered pair, for grouping."""
    return tuple(sorted((a, b)))


def load_outputs(path: Path) -> dict[str, dict]:
    """run_id → {condition, user_id, scenario_id, output_text}."""
    if not path.exists():
        print(f"  WARN: {path} does not exist", file=sys.stderr)
        return {}
    outputs: dict[str, dict] = {}
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            run_id = rec.get("run_id")
            if not run_id:
                continue
            outputs[run_id] = {
                "condition": rec.get("condition") or rec.get("condition_raw"),
                "user_id": rec.get("user_id"),
                "scenario_id": rec.get("scenario_id"),
                "output_text": rec.get("output_text") or rec.get("content") or "",
                "output_model": rec.get("output_model") or rec.get("author_model"),
            }
    return outputs


def load_scenarios(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    out = {}
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            sid = rec.get("scenario_id")
            if sid:
                out[sid] = rec
    return out


def load_profile_bundles(path: Path) -> dict[tuple[str, str], dict]:
    """(user_id, condition) → profile fields actually shown to the author."""
    if not path.exists():
        return {}
    out = {}
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            uid = rec.get("user_id")
            conds = rec.get("conditions") or {}
            if not isinstance(conds, dict):
                continue
            for cond_key, cond_payload in conds.items():
                if cond_payload is None:
                    continue
                if isinstance(cond_payload, dict):
                    text = cond_payload.get("text", "")
                else:
                    text = str(cond_payload)
                out[(uid, cond_key)] = {"text": text}
    return out


def select_v03_t1(
    pairwise_records: list[dict],
    outputs: dict[str, dict],
    rng: random.Random,
) -> list[dict]:
    """Sample 2 pairs per T1 pair type, stratified by (judge, user_id)."""
    by_pair_type: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for pw in pairwise_records:
        ra, rb = pw.get("run_id_a"), pw.get("run_id_b")
        if not ra or not rb:
            continue
        a_meta, b_meta = outputs.get(ra), outputs.get(rb)
        if a_meta is None or b_meta is None:
            continue
        cond_a, cond_b = a_meta["condition"], b_meta["condition"]
        if cond_a is None or cond_b is None:
            continue
        canon = normalize_pair(cond_a, cond_b)
        if canon in {normalize_pair(*p) for p in T1_PAIR_TYPES}:
            if pw.get("winner") == "tie":
                continue
            by_pair_type[canon].append(pw)

    chosen: list[dict] = []
    shortfall_pair_types: list[str] = []
    for pair_type in T1_PAIR_TYPES:
        canon = normalize_pair(*pair_type)
        bucket = by_pair_type.get(canon, [])
        if len(bucket) < 2:
            shortfall_pair_types.append(f"{canon[0]} vs {canon[1]} (have {len(bucket)})")
            chosen.extend(bucket)  # take what we have
            continue
        # Stratify by (judge_model, user_id)
        stratum_keys = sorted(
            {(pw.get("judge_model", ""), outputs[pw["run_id_a"]]["user_id"])
             for pw in bucket}
        )
        # Pick 2 stratum cells deterministically; one record from each
        sample_strata = rng.sample(stratum_keys, min(2, len(stratum_keys)))
        per_stratum: list[dict] = []
        for strat in sample_strata:
            in_strat = [pw for pw in bucket
                        if (pw.get("judge_model", ""),
                            outputs[pw["run_id_a"]]["user_id"]) == strat]
            per_stratum.append(rng.choice(in_strat))
        # If only 1 stratum was available, draw a second record from same bucket
        while len(per_stratum) < 2 and len(bucket) > len(per_stratum):
            candidate = rng.choice(bucket)
            if candidate not in per_stratum:
                per_stratum.append(candidate)
        chosen.extend(per_stratum[:2])

    return chosen, shortfall_pair_types


def select_v03_t2(
    pairwise_records: list[dict],
    outputs: dict[str, dict],
    rng: random.Random,
) -> list[dict]:
    """Sample 2 pairs per T2 ladder step."""
    by_step: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for pw in pairwise_records:
        ra, rb = pw.get("run_id_a"), pw.get("run_id_b")
        a_meta, b_meta = outputs.get(ra), outputs.get(rb)
        if not (a_meta and b_meta):
            continue
        cond_a, cond_b = a_meta["condition"], b_meta["condition"]
        if cond_a is None or cond_b is None:
            continue
        canon = normalize_pair(cond_a, cond_b)
        if canon in {normalize_pair(*p) for p in T2_LADDER_STEPS}:
            if pw.get("winner") == "tie":
                continue
            by_step[canon].append(pw)

    chosen: list[dict] = []
    shortfall: list[str] = []
    for step in T2_LADDER_STEPS:
        canon = normalize_pair(*step)
        bucket = by_step.get(canon, [])
        if len(bucket) < 2:
            shortfall.append(f"{canon[0]} vs {canon[1]} (have {len(bucket)})")
            chosen.extend(bucket)
            continue
        chosen.extend(rng.sample(bucket, 2))
    return chosen, shortfall


def select_v02_anchors(
    v02_pairwise: list[dict],
    v02_outputs: dict[str, dict],
    rng: random.Random,
) -> list[dict]:
    """10 unanimous-3-of-3 v0.2 pairs spread across 4 v0.2 PRIMARY pair types."""
    canon_anchor_set = {normalize_pair(*p) for p in V02_ANCHOR_PAIR_TYPES}
    # Build (scenario_id, run_id_a, run_id_b) → list of (judge, winner)
    by_pair_judge: dict[tuple[str, str, str], list[tuple[str, str]]] = defaultdict(list)
    for pw in v02_pairwise:
        sid = pw.get("scenario_id")
        ra, rb = pw.get("run_id_a"), pw.get("run_id_b")
        if not (sid and ra and rb):
            continue
        # canonical pairwise key sorts run_ids so AB/BA collapse
        key = (sid, *tuple(sorted((ra, rb))))
        winner_raw = pw.get("winner")
        if winner_raw == "tie":
            continue
        # Normalize winner: A means run_id_a wins. After sort, label by absolute run_id
        actual_winner_run = ra if winner_raw == "A" else rb if winner_raw == "B" else None
        if actual_winner_run is None:
            continue
        judge = pw.get("judge_model", "")
        by_pair_judge[key].append((judge, actual_winner_run))

    # Filter to pairs where 3 distinct judges agreed unanimously
    unanimous_pairs: list[dict] = []
    for (sid, run_x, run_y), entries in by_pair_judge.items():
        judges = sorted({j for j, _ in entries})
        if len(judges) < 3:
            continue
        winners_per_judge: dict[str, set] = defaultdict(set)
        for j, w in entries:
            winners_per_judge[j].add(w)
        # Each judge must have a single consistent winner across its AB/BA records
        if any(len(s) != 1 for s in winners_per_judge.values()):
            continue
        single_winners = {next(iter(s)) for s in winners_per_judge.values()}
        if len(single_winners) != 1:
            continue  # not unanimous
        # Verify pair is in our anchor set
        a_meta = v02_outputs.get(run_x)
        b_meta = v02_outputs.get(run_y)
        if not (a_meta and b_meta):
            continue
        canon = normalize_pair(a_meta["condition"], b_meta["condition"])
        if canon not in canon_anchor_set:
            continue
        # Use the first pairwise record arbitrarily as the anchor record
        anchor_pw = next(
            (pw for pw in v02_pairwise
             if pw.get("scenario_id") == sid
             and tuple(sorted((pw.get("run_id_a", ""), pw.get("run_id_b", "")))) == (run_x, run_y)),
            None,
        )
        if anchor_pw is None:
            continue
        unanimous_pairs.append({"pw": anchor_pw, "canon": canon})

    # Spread across 4 anchor pair types: ~2-3 per type
    by_canon: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for rec in unanimous_pairs:
        by_canon[rec["canon"]].append(rec)

    chosen: list[dict] = []
    shortfall: list[str] = []
    per_type_target = N_V02_ANCHOR // len(V02_ANCHOR_PAIR_TYPES)  # 2 per type, 2 extra
    extras = N_V02_ANCHOR - per_type_target * len(V02_ANCHOR_PAIR_TYPES)  # 2
    for i, pair_type in enumerate(V02_ANCHOR_PAIR_TYPES):
        target = per_type_target + (1 if i < extras else 0)
        canon = normalize_pair(*pair_type)
        bucket = by_canon.get(canon, [])
        if len(bucket) < target:
            shortfall.append(
                f"v02 anchor {canon[0]} vs {canon[1]} (have {len(bucket)}, want {target})"
            )
            chosen.extend([r["pw"] for r in bucket])
            continue
        sample = rng.sample(bucket, target)
        chosen.extend([r["pw"] for r in sample])
    return chosen, shortfall


def anonymize_and_render(
    pw: dict,
    stratum: str,
    outputs: dict[str, dict],
    scenarios: dict[str, dict],
    bundles: dict,
    rater_id: int,
    ab_rng: random.Random,
) -> Optional[dict]:
    ra, rb = pw["run_id_a"], pw["run_id_b"]
    a_meta = outputs.get(ra)
    b_meta = outputs.get(rb)
    if not (a_meta and b_meta):
        return None
    scenario = scenarios.get(a_meta["scenario_id"], {})
    scenario_prompt = (
        scenario.get("prompt_text")
        or scenario.get("user_message")
        or scenario.get("prompt")
        or ""
    )
    a_text = a_meta["output_text"]
    b_text = b_meta["output_text"]
    # Profile text shown — use the condition with the more substantive profile
    # (e.g., if pair is C0 vs C3, show C3's profile)
    profile_text = ""
    bundle_a = bundles.get((a_meta["user_id"], a_meta["condition"]), {}).get("text", "")
    bundle_b = bundles.get((b_meta["user_id"], b_meta["condition"]), {}).get("text", "")
    profile_text = bundle_a if len(bundle_a) >= len(bundle_b) else bundle_b

    # A/B side anonymization
    flip = ab_rng.random() < 0.5
    if flip:
        a_text, b_text = b_text, a_text

    return {
        "rater_pair_id": f"rp_{rater_id:03d}",
        "stratum": stratum,
        "scenario_id": a_meta["scenario_id"],
        "scenario_prompt": scenario_prompt,
        "profile_text_shown": profile_text,
        "response_a_text": a_text,
        "response_b_text": b_text,
        "_a_is_original_a": not flip,
        "_original_run_id_a": ra,
        "_original_run_id_b": rb,
        "_original_condition_a": a_meta["condition"],
        "_original_condition_b": b_meta["condition"],
        "_user_id": a_meta["user_id"],
        "_judge_model": pw.get("judge_model"),
        "_llm_winner": pw.get("winner"),
        "_pair_type": normalize_pair(a_meta["condition"], b_meta["condition"]),
        "_corpus": "v0.2" if stratum == "v02_anchor" else "v0.3",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--v03-tag", default="2026-05-19_v03")
    ap.add_argument("--v02-tag", default="2026-04-26_v02_hard_codex_only")
    ap.add_argument("--pilot", default="v03_full_pilot")
    ap.add_argument("--v02-pilot", default="v02_hard_pilot")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()

    root = Path(args.root)
    v03_run_dir = root / "runs" / args.v03_tag
    v02_run_dir = root / "runs" / args.v02_tag
    v03_pilot_dir = root / "pilots" / args.pilot
    v02_pilot_dir = root / "pilots" / args.v02_pilot
    if not v03_pilot_dir.exists():
        v03_pilot_dir = root / "data" / args.pilot
    if not v02_pilot_dir.exists():
        v02_pilot_dir = root / "data" / args.v02_pilot

    v03_pw_path = v03_run_dir / "pairwise_scores.jsonl"
    v02_pw_path = v02_run_dir / "pairwise_scores.jsonl"
    v03_outputs_path = v03_run_dir / "assistant_outputs.jsonl"
    v02_outputs_path = v02_run_dir / "assistant_outputs.jsonl"
    v03_scenarios_path = v03_pilot_dir / "scenarios.jsonl"
    v02_scenarios_path = v02_pilot_dir / "scenarios.jsonl"
    v03_bundles_path = v03_pilot_dir / "profile_bundles.jsonl"
    v02_bundles_path = v02_pilot_dir / "profile_bundles.jsonl"

    print(f"Loading v0.3 from {v03_run_dir}")
    v03_outputs = load_outputs(v03_outputs_path)
    v03_scenarios = load_scenarios(v03_scenarios_path)
    v03_bundles = load_profile_bundles(v03_bundles_path)
    v03_pw = []
    if v03_pw_path.exists():
        with v03_pw_path.open() as fh:
            for line in fh:
                line = line.strip()
                if line:
                    v03_pw.append(json.loads(line))
    print(f"  v0.3: {len(v03_outputs)} outputs, {len(v03_pw)} pairwise records")

    print(f"Loading v0.2 from {v02_run_dir}")
    v02_outputs = load_outputs(v02_outputs_path)
    v02_scenarios = load_scenarios(v02_scenarios_path)
    v02_bundles = load_profile_bundles(v02_bundles_path)
    v02_pw = []
    if v02_pw_path.exists():
        with v02_pw_path.open() as fh:
            for line in fh:
                line = line.strip()
                if line:
                    v02_pw.append(json.loads(line))
    print(f"  v0.2: {len(v02_outputs)} outputs, {len(v02_pw)} pairwise records")

    if not v03_pw:
        print("ERROR: v0.3 pairwise_scores.jsonl is empty or missing. "
              "Cannot select v0.3 pairs. Re-run after pairwise judging completes.",
              file=sys.stderr)
        return 1

    rng = random.Random(SEED_PAIR_SELECTION)
    t1_pairs, t1_short = select_v03_t1(v03_pw, v03_outputs, rng)
    t2_pairs, t2_short = select_v03_t2(v03_pw, v03_outputs, rng)
    v02_pairs, v02_short = select_v02_anchors(v02_pw, v02_outputs, rng)

    print(f"\nSelected: T1={len(t1_pairs)}/32, T2={len(t2_pairs)}/8, "
          f"v02={len(v02_pairs)}/10")
    for short in t1_short + t2_short + v02_short:
        print(f"  SHORTFALL: {short}")

    # Anonymize + render
    ab_rng = random.Random(SEED_AB_ANONYMIZATION)
    inbox: list[dict] = []
    rater_id = 1
    for pw in t1_pairs:
        rec = anonymize_and_render(
            pw, "T1", v03_outputs, v03_scenarios, v03_bundles, rater_id, ab_rng,
        )
        if rec:
            inbox.append(rec)
            rater_id += 1
    for pw in t2_pairs:
        rec = anonymize_and_render(
            pw, "T2", v03_outputs, v03_scenarios, v03_bundles, rater_id, ab_rng,
        )
        if rec:
            inbox.append(rec)
            rater_id += 1
    for pw in v02_pairs:
        rec = anonymize_and_render(
            pw, "v02_anchor", v02_outputs, v02_scenarios, v02_bundles, rater_id, ab_rng,
        )
        if rec:
            inbox.append(rec)
            rater_id += 1

    out_path = v03_run_dir / "human_rater_inbox.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as fh:
        for rec in inbox:
            # Cast tuple back to list for JSON
            rec["_pair_type"] = list(rec["_pair_type"])
            fh.write(json.dumps(rec) + "\n")
    print(f"\nWrote {len(inbox)} anonymized pairs to {out_path}")

    # Manifest
    manifest_path = v03_run_dir / "human_rater_manifest.md"
    now = datetime.now(timezone.utc).isoformat()
    by_stratum: dict[str, int] = defaultdict(int)
    by_pair_type: dict[tuple, int] = defaultdict(int)
    for rec in inbox:
        by_stratum[rec["stratum"]] += 1
        by_pair_type[tuple(rec["_pair_type"])] += 1
    with manifest_path.open("w") as fh:
        fh.write(f"# Phase 5 human-rater pair manifest\n\n")
        fh.write(f"**Generated**: {now}\n")
        fh.write(f"**v0.3 tag**: `{args.v03_tag}`\n")
        fh.write(f"**v0.2 tag**: `{args.v02_tag}`\n")
        fh.write(f"**Selection rule**: docs/v0_3_phase_minus_1_design_lock.md §-1.13\n")
        fh.write(f"**Seeds**: pair selection={SEED_PAIR_SELECTION}, "
                 f"A/B anonymization={SEED_AB_ANONYMIZATION}\n")
        fh.write(f"**Total selected**: {len(inbox)} / target {N_TOTAL}\n\n")
        fh.write("## By stratum\n\n")
        for s in ("T1", "T2", "v02_anchor"):
            target = {"T1": N_T1, "T2": N_T2, "v02_anchor": N_V02_ANCHOR}[s]
            fh.write(f"- **{s}**: {by_stratum[s]} / {target}\n")
        fh.write("\n## By pair type\n\n")
        for pt, n in sorted(by_pair_type.items()):
            fh.write(f"- `{pt[0]}` vs `{pt[1]}`: {n}\n")
        if t1_short or t2_short or v02_short:
            fh.write("\n## Shortfalls\n\n")
            for short in t1_short + t2_short + v02_short:
                fh.write(f"- {short}\n")
        fh.write("\n## Next step\n\n")
        fh.write("Run `drivers/rater_cli.py` to rate the 50 pairs.\n")
    print(f"Wrote manifest to {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
