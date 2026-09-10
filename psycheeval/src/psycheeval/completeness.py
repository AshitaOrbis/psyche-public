"""Stage completeness accounting — the antidote to exit-0-on-partial.

Every long-running stage in this harness (author generation, scalar judging,
pairwise judging, rejudge passes) is a fan-out over an expected matrix whose
workers catch per-record exceptions, count them, and carry on. That is the
right behaviour *during* the fan-out — one bad record should not throw away a
thousand good ones — but it is a lie at the end of it: the stage prints
``Done.``, returns a path, and exits 0 whether it produced every record it
promised or half of them.

A driver running under ``set -euo pipefail`` cannot tell those two apart, so a
systematically incomplete matrix (a broken model key knocking out one whole
judge family is the historical case — see
``logs/v03_codex_pipeline.log.broken_gpt55_key``) flows into analysis as if it
were complete.

The honest completion test is expected-versus-observed over the matrix, broken
down by the dimensions that make the matrix *balanced* — judge, author,
condition, scenario — not "the worker pool drained without raising". This
module computes that, writes it next to the run artifacts so it is visible
after the fact, and raises unless the caller explicitly asked for partial.

Usage::

    cells = [StageCell(key=(run_id, judge), judge=judge, author=..., ...)]
    status = stage_status(
        stage="score_anchored", run_tag=tag, expected=cells,
        is_observed=lambda c: c.key in observed_keys,
        failed=counters["failed"], cap_aborted=counters["cap_aborted"],
    )
    write_stage_status(run_dir, status)
    enforce_complete(status, allow_partial=allow_partial)
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

#: How many missing cells to name in the status file. The counts are exact;
#: this only bounds the illustrative list.
MISSING_SAMPLE_LIMIT = 25


@dataclass(frozen=True)
class StageCell:
    """One cell of a stage's expected output matrix.

    ``key`` identifies the record the cell must produce (whatever tuple the
    stage uses to dedupe on resume). The remaining fields are the breakdown
    dimensions; leave them ``None`` when a stage has no such axis.
    """

    key: tuple[str, ...]
    judge: str | None = None
    author: str | None = None
    condition: str | None = None
    scenario: str | None = None


class StageIncompleteError(RuntimeError):
    """A stage finished without producing its whole expected matrix."""

    def __init__(self, status: dict) -> None:
        self.status = status
        super().__init__(
            f"stage {status.get('stage')!r} incomplete: "
            f"{status.get('observed_count')}/{status.get('expected_count')} records observed, "
            f"{status.get('missing_count')} missing "
            f"(failed={status.get('failed')}, cap_aborted={status.get('cap_aborted')}, "
            f"unresolved={len(status.get('unresolved') or [])}). "
            f"Re-run to fill the gaps, or pass --allow-partial to accept it."
        )


def _breakdown(
    expected: Sequence[StageCell],
    observed_flags: Sequence[bool],
    attr: str,
) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for cell, seen in zip(expected, observed_flags, strict=True):
        name = getattr(cell, attr)
        if name is None:
            continue
        row = out.setdefault(name, {"expected": 0, "observed": 0, "missing": 0})
        row["expected"] += 1
        if seen:
            row["observed"] += 1
        else:
            row["missing"] += 1
    return dict(sorted(out.items()))


def stage_status(
    *,
    stage: str,
    run_tag: str,
    expected: Sequence[StageCell],
    is_observed: Callable[[StageCell], bool],
    failed: int = 0,
    cap_aborted: int = 0,
    unresolved: Sequence[dict] | None = None,
    allow_partial: bool = False,
    extra: dict | None = None,
) -> dict:
    """Compare the expected matrix against what actually landed on disk.

    ``is_observed`` is evaluated against the records the stage really wrote
    (re-read from the output file), not against in-memory success counters —
    a record counted as written but lost to a write failure is still missing.

    ``unresolved`` carries rows the stage dropped *before* dispatch (a missing
    scenario or user, say). Those are silent drops too, so a non-empty list
    makes the stage incomplete.
    """
    observed_flags = [is_observed(c) for c in expected]
    observed_count = sum(observed_flags)
    missing = [c for c, seen in zip(expected, observed_flags, strict=True) if not seen]
    unresolved_rows = list(unresolved or [])

    status = {
        "stage": stage,
        "run_tag": run_tag,
        "generated_at": datetime.now(UTC).isoformat(),
        "expected_count": len(expected),
        "observed_count": observed_count,
        "missing_count": len(missing),
        "failed": failed,
        "cap_aborted": cap_aborted,
        "unresolved": unresolved_rows,
        "allow_partial": allow_partial,
        "by_judge": _breakdown(expected, observed_flags, "judge"),
        "by_author": _breakdown(expected, observed_flags, "author"),
        "by_condition": _breakdown(expected, observed_flags, "condition"),
        "by_scenario": _breakdown(expected, observed_flags, "scenario"),
        "missing_sample": [list(c.key) for c in missing[:MISSING_SAMPLE_LIMIT]],
        "missing_sample_truncated": len(missing) > MISSING_SAMPLE_LIMIT,
    }
    complete = not missing and not unresolved_rows
    status["complete"] = complete
    status["status"] = "COMPLETE" if complete else "PARTIAL"
    if extra:
        status.update(extra)
    return status


def stage_status_path(run_dir: Path, stage: str) -> Path:
    return run_dir / f"stage_status_{stage}.json"


def write_stage_status(run_dir: Path, status: dict) -> Path:
    """Persist the status next to the run artifacts. Always overwritten —
    the latest attempt is what the matrix looks like now."""
    path = stage_status_path(run_dir, status["stage"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status, indent=2, sort_keys=True))
    return path


def _wholly_missing(breakdown: dict[str, dict[str, int]]) -> list[str]:
    return [k for k, v in breakdown.items() if v["expected"] > 0 and v["observed"] == 0]


def summarize(status: dict) -> str:
    """One-screen human summary. Printed on both the complete and partial paths."""
    lines = [
        f"{status['stage']}: {status['status']} — "
        f"{status['observed_count']}/{status['expected_count']} records "
        f"({status['missing_count']} missing, failed={status['failed']}, "
        f"cap_aborted={status['cap_aborted']}, "
        f"unresolved={len(status.get('unresolved') or [])})"
    ]
    for axis in ("by_judge", "by_author", "by_condition"):
        gaps = {k: v for k, v in status.get(axis, {}).items() if v["missing"]}
        if gaps:
            detail = ", ".join(f"{k} {v['observed']}/{v['expected']}" for k, v in gaps.items())
            lines.append(f"  {axis.removeprefix('by_')} gaps: {detail}")
    for axis in ("by_judge", "by_author", "by_condition"):
        dead = _wholly_missing(status.get(axis, {}))
        if dead:
            lines.append(
                f"  ENTIRE {axis.removeprefix('by_')} family produced nothing: {', '.join(dead)}"
            )
    scenario_gaps = sum(1 for v in status.get("by_scenario", {}).values() if v["missing"])
    if scenario_gaps:
        lines.append(f"  scenarios with gaps: {scenario_gaps}")
    return "\n".join(lines)


def enforce_complete(status: dict, *, allow_partial: bool) -> None:
    """Raise unless the matrix is whole (or partial was explicitly requested)."""
    print(summarize(status))
    if status["complete"]:
        return
    if allow_partial:
        print(
            "  --allow-partial: accepting an INCOMPLETE matrix. Downstream analysis "
            "of this run is not balanced; the stage status file records the gaps."
        )
        return
    raise StageIncompleteError(status)
