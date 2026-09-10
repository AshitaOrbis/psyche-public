#!/usr/bin/env python3
"""Phase 5 minimal rater CLI.

Presents one anonymized pair at a time from runs/<TAG>/human_rater_inbox.jsonl.
Rater inputs: winner (a/b/t), 0-10 scalar on 3 dimensions × 2 sides, brief
rationale. Writes to runs/<TAG>/human_rater_responses.jsonl in append mode;
resumable across sessions (skips pairs already rated by rater_pair_id).

Usage:
  python3 drivers/rater_cli.py --tag 2026-05-19_v03 [--from rp_001] [--limit 5]

Output schema (one record per rated pair):
  {
    "rater_pair_id": "rp_001",
    "winner": "A" | "B" | "tie",
    "scalar_a": {"helpfulness": 7, "profile_fit": 8, "anti_sycophancy": 7},
    "scalar_b": {"helpfulness": 6, "profile_fit": 7, "anti_sycophancy": 6},
    "rationale": "B better fits user's analytical style; A is too saccharine",
    "rated_at": "2026-05-20T01:00:00Z"
  }

Conventions:
- The rater is BLINDED: condition labels are not shown in the inbox.
- A/B side was randomized at selection time (seed=43).
- The rater is presumed to be the project author; this is a single-rater
  sanity check, not calibration (per design-lock §-1.13).
- Rate ALL 50 pairs BEFORE inspecting `metrics_<tag>.json` for those pairs.
"""

from __future__ import annotations
import argparse
import json
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path


DIMENSIONS = ["helpfulness", "profile_fit", "anti_sycophancy"]


def load_inbox(path: Path) -> list[dict]:
    if not path.exists():
        print(f"ERROR: {path} does not exist", file=sys.stderr)
        sys.exit(1)
    out = []
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def load_done(path: Path) -> set[str]:
    if not path.exists():
        return set()
    done = set()
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                done.add(rec["rater_pair_id"])
            except Exception:
                continue
    return done


def prompt_int(label: str, lo: int = 0, hi: int = 10) -> int:
    while True:
        s = input(f"  {label} [{lo}-{hi}]: ").strip()
        try:
            v = int(s)
            if lo <= v <= hi:
                return v
            print(f"    Out of range; expected {lo}-{hi}")
        except ValueError:
            print("    Not an integer")


def prompt_winner() -> str:
    while True:
        s = input("  Winner (a/b/t for tie): ").strip().lower()
        if s in ("a", "b", "t"):
            return {"a": "A", "b": "B", "t": "tie"}[s]
        print("    Expected a, b, or t")


def render(pair: dict, idx: int, total: int) -> None:
    bar = "═" * 72
    print(f"\n{bar}")
    print(f"  Pair {idx + 1} / {total}  (rater_pair_id: {pair['rater_pair_id']})")
    print(f"  scenario: {pair['scenario_id']}")
    print(bar)

    if pair.get("profile_text_shown"):
        print("\nPROFILE (this is the kind of profile shown to one or both responses):")
        print(textwrap.indent(textwrap.fill(pair["profile_text_shown"], width=78), "  "))
    else:
        print("\n(no profile shown for this pair)")

    print("\nSCENARIO PROMPT:")
    print(textwrap.indent(textwrap.fill(pair["scenario_prompt"], width=78), "  "))

    print(f"\n{'─' * 72}")
    print("RESPONSE A:")
    print(f"{'─' * 72}")
    print(textwrap.indent(pair["response_a_text"], "  "))

    print(f"\n{'─' * 72}")
    print("RESPONSE B:")
    print(f"{'─' * 72}")
    print(textwrap.indent(pair["response_b_text"], "  "))
    print(f"\n{bar}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tag", default="2026-05-19_v03")
    ap.add_argument("--root", default=".")
    ap.add_argument("--from", dest="start_from", default=None,
                    help="Resume from this rater_pair_id (e.g. rp_005)")
    ap.add_argument("--limit", type=int, default=None,
                    help="Rate at most N pairs this session")
    args = ap.parse_args()

    run_dir = Path(args.root) / "runs" / args.tag
    inbox_path = run_dir / "human_rater_inbox.jsonl"
    responses_path = run_dir / "human_rater_responses.jsonl"

    inbox = load_inbox(inbox_path)
    done = load_done(responses_path)
    print(f"Loaded {len(inbox)} pairs from inbox; {len(done)} already rated.")

    queue = [p for p in inbox if p["rater_pair_id"] not in done]
    if args.start_from:
        queue = [p for p in queue if p["rater_pair_id"] >= args.start_from]
    if args.limit:
        queue = queue[: args.limit]
    print(f"Will rate {len(queue)} pairs this session.\n")

    if not queue:
        print("Nothing to rate.")
        return 0

    print("Controls: winner=a/b/t (tie), then 0-10 scalars on 3 dims × 2 sides, "
          "then rationale. Ctrl-C to bail (partial responses are persisted).")

    for i, pair in enumerate(queue):
        render(pair, i, len(queue))
        try:
            winner = prompt_winner()
            print("\nSCORE RESPONSE A (0-10):")
            scalar_a = {d: prompt_int(d) for d in DIMENSIONS}
            print("\nSCORE RESPONSE B (0-10):")
            scalar_b = {d: prompt_int(d) for d in DIMENSIONS}
            rationale = input("\n  Rationale (one line): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nInterrupted; partial progress saved.")
            return 130

        rec = {
            "rater_pair_id": pair["rater_pair_id"],
            "winner": winner,
            "scalar_a": scalar_a,
            "scalar_b": scalar_b,
            "rationale": rationale,
            "rated_at": datetime.now(timezone.utc).isoformat(),
        }
        with responses_path.open("a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"  ✓ Saved {pair['rater_pair_id']}")

    print(f"\nDone. Session rated {len(queue)} pairs.")
    print(f"Total responses on disk: {len(load_done(responses_path))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
