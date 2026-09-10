"""Run the assistant-under-test pipeline.

Materializes a run manifest (scenario × condition × author) and executes each
row, producing AssistantOutput records. Resumable: if an output file already
contains a row for a given (scenario_id, condition, output_model), that row
is skipped.

Usage:
    uv run python -m psycheeval.run --pilot micro_pilot --tag 2026-04-20_micro
    uv run python -m psycheeval.run --pilot micro_pilot --tag 2026-04-20_micro --dry-run
"""

from __future__ import annotations

import argparse
import json
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path

from psycheeval import config
from psycheeval.cap_burn import CapBurnHandler
from psycheeval.completeness import (
    StageCell,
    StageIncompleteError,
    enforce_complete,
    stage_status,
    write_stage_status,
)
from psycheeval.io import append_jsonl, read_jsonl, write_jsonl
from psycheeval.llm import MODELS, ClaudeCapError, complete
from psycheeval.models import (
    AssistantOutput,
    Condition,
    PersonaSeed,
    ProfileBundle,
    Scenario,
)
from psycheeval.personas import PUBLIC_INSPIRED, persona_type_index


RESPONSE_PROMPT_PATH = config.PROMPTS_DIR / "05_assistant_response.md"


#: Condition → the ``ProfileConditions`` field that carries its profile text.
#: ``None`` means the condition needs no profile (C0, the no-profile control).
#: A condition absent from this map is not a condition this harness knows how
#: to generate.
CONDITION_FIELD_MAP: dict[str, str | None] = {
    "C0": None,  # always available
    "C1": "C1_trait_labels",
    "C2": "C2_narrative",
    "C3": "C3_behavioral_contract",
    "C4": "C4_behavioral_contract_anti_sycophancy",
    "C5": "C5_source_packet_informed",
    "C1_padded": "C1_padded",
    "C4_shuffled": "C4_shuffled",
    "C5_CONTRACT": "C5_contract",
    # v0.3 additions
    "C_GENERIC_CONTRACT": "C_generic_contract",
    "C4_WRONG_PROFILE": "C4_wrong_profile",
    "C5_NONPUBLIC": "C5_nonpublic",
    "C5_NONPUBLIC_CONTRACT": "C5_nonpublic_contract",
    "L1": "L1",
    "L2": "L2",
    "L3": "L3",
}


class ManifestPreflightError(RuntimeError):
    """The configured experiment cannot be generated as specified."""

    def __init__(self, pilot_name: str, message: str, defects: list[dict] | None = None) -> None:
        self.pilot_name = pilot_name
        self.defects = defects or []
        detail = ""
        if self.defects:
            shown = self.defects[:10]
            detail = "\n  " + "\n  ".join(
                f"{d.get('scenario_id', '-')} / {d.get('user_id', '-')} / "
                f"{d.get('condition', '-')}: {d['reason']}"
                for d in shown
            )
            if len(self.defects) > len(shown):
                detail += f"\n  … and {len(self.defects) - len(shown)} more"
        super().__init__(f"preflight failed for pilot {pilot_name!r}: {message}{detail}")


def _condition_value(condition: Condition | str) -> str:
    return condition.value if hasattr(condition, "value") else str(condition)


def _profile_text_for_condition(bundle: ProfileBundle, condition: Condition) -> str:
    """Pull profile text for a given condition. C0 returns the empty string.

    Every other condition MUST resolve to populated profile text. Returning ""
    for a missing or unknown condition silently downgrades a treatment row to
    the no-profile control prompt — the row is then labelled as a treatment,
    counted as one, and analysed as one, while having received exactly what C0
    receives. Raise instead; the manifest preflight is what decides which cells
    are legitimately absent.
    """
    cond_val = _condition_value(condition)
    if cond_val == "C0":
        return ""
    if cond_val not in CONDITION_FIELD_MAP:
        raise ValueError(
            f"Unknown condition {cond_val!r} — not one of {sorted(CONDITION_FIELD_MAP)}"
        )
    field_name = CONDITION_FIELD_MAP[cond_val]
    pc = getattr(bundle.profile_conditions, field_name, None) if field_name else None
    if pc is None:
        raise ValueError(
            f"Condition {cond_val!r} has no profile text for user {bundle.user_id!r} "
            f"(bundle field {field_name!r} is empty). A treatment row must never "
            f"fall back to the C0 prompt."
        )
    return pc.profile_text


def _render_prompt(scenario: Scenario, profile_text: str, condition: str) -> tuple[str, str]:
    template = RESPONSE_PROMPT_PATH.read_text()
    # Condition is NOT revealed to the author model — the author sees only
    # profile_text (empty for C0). `condition` is passed here only for logging.
    user_rendered = (
        template
        .replace("`{{condition}}`", "(withheld from you; respond without inferring it)")
        .replace("`{{profile_text_or_empty_for_C0}}`", profile_text or "(no profile provided)")
        .replace("`{{user_prompt}}`", scenario.user_prompt)
    )
    return ("You are an AI assistant being evaluated.", user_rendered)


def build_manifest(
    pilot_name: str = "micro_pilot",
    *,
    authors: list[str] | None = None,
    condition_whitelist: set[str] | None = None,
    scenario_limit: int = 0,
    strict: bool = True,
) -> list[dict]:
    """Produce a list of (scenario, condition, author) rows, fail-closed.

    The pilot's core conditions apply to every persona. The extra conditions
    apply to personas of one declared type — ``public_extra_persona_type``,
    defaulting to ``public_inspired``, because those are the personas with a
    source packet behind them. Optionality is therefore a property of the
    persona type, declared in the pilot config; it is NOT inferred from
    whether a bundle field happens to be populated, which is how a partial or
    malformed bundle used to remove treatment cells without a word.

    Args:
        condition_whitelist: if set, only conditions in this set are dispatched.
            Useful for v0.3 Phase 1/2 where only new conditions need generation.
            It narrows what is GENERATED, not what the pilot must contain — the
            preflight still checks the whole matrix.
        scenario_limit: if >0, dispatch only the first N scenarios (sorted by
            scenario_id). Useful for smoke tests.
        strict: fail on any cell the pilot configures but cannot produce. Set
            False only to deliberately run a reduced matrix; the dropped cells
            are printed either way.

    Raises:
        ManifestPreflightError: on an unknown condition (always), or on a
            missing bundle / missing treatment field when ``strict``.
    """
    authors = authors or config.AUTHOR_MODELS
    pilot_dir = config.pilot_dir(pilot_name)

    scenarios = list(read_jsonl(pilot_dir / "scenarios.jsonl", Scenario))
    if scenario_limit > 0:
        scenarios = sorted(scenarios, key=lambda s: s.scenario_id)[:scenario_limit]
    bundles = {b.user_id: b for b in read_jsonl(pilot_dir / "profile_bundles.jsonl", ProfileBundle)}

    conds = config.conditions_for(pilot_name)
    core_conds = list(conds["core"])
    public_extra = list(conds["public_extra"])
    extra_persona_type = conds.get("public_extra_persona_type", PUBLIC_INSPIRED)

    # An unrecognised condition name is a configuration error, not a cell to
    # drop: nothing downstream can render or interpret it. Always fatal.
    unknown = [c for c in core_conds + public_extra if c not in CONDITION_FIELD_MAP]
    if unknown:
        raise ManifestPreflightError(
            pilot_name,
            f"unknown condition(s) {sorted(unknown)}; known: {sorted(CONDITION_FIELD_MAP)}",
        )

    persona_types = persona_type_index(pilot_name)

    manifest: list[dict] = []
    defects: list[dict] = []
    for scenario in scenarios:
        bundle = bundles.get(scenario.user_id)
        if bundle is None:
            defects.append({
                "scenario_id": scenario.scenario_id,
                "user_id": scenario.user_id,
                "condition": "*",
                "reason": "no profile bundle for this scenario's user",
            })
            continue

        ptype = persona_types.get(scenario.user_id)
        # Extras are required for the declared persona type and legitimately
        # absent for every other — that is the whole of their optionality.
        expected_conds = list(core_conds)
        if ptype == extra_persona_type:
            expected_conds += public_extra
        elif ptype is None and public_extra:
            defects.append({
                "scenario_id": scenario.scenario_id,
                "user_id": scenario.user_id,
                "condition": "*",
                "reason": (
                    "persona type unknown (no seed for this user), so whether the "
                    f"{extra_persona_type} extras apply cannot be decided"
                ),
            })

        for condition in expected_conds:
            field_name = CONDITION_FIELD_MAP[condition]
            if field_name and getattr(bundle.profile_conditions, field_name, None) is None:
                defects.append({
                    "scenario_id": scenario.scenario_id,
                    "user_id": scenario.user_id,
                    "condition": condition,
                    "reason": f"bundle field {field_name!r} is empty",
                })
                continue
            if condition_whitelist is not None and condition not in condition_whitelist:
                continue
            for author in authors:
                manifest.append(
                    {
                        "scenario_id": scenario.scenario_id,
                        "user_id": scenario.user_id,
                        "condition": condition,
                        "output_model": author,
                    }
                )

    if defects:
        for d in defects:
            print(
                f"  PREFLIGHT {d['scenario_id']} / {d['user_id']} / "
                f"{d['condition']}: {d['reason']}"
            )
        if strict:
            raise ManifestPreflightError(
                pilot_name,
                f"{len(defects)} configured cell(s) cannot be generated",
                defects,
            )
        print(
            f"  --allow-incomplete-matrix: generating a REDUCED matrix "
            f"({len(defects)} configured cells dropped). Condition effects from "
            f"this run are not balanced."
        )
    return manifest


def run_one(row: dict, scenario: Scenario, bundle: ProfileBundle) -> AssistantOutput:
    profile_text = _profile_text_for_condition(bundle, row["condition"])
    system, user = _render_prompt(scenario, profile_text, row["condition"])

    response = complete(
        system=system,
        user=user,
        model_key=row["output_model"],
        temperature=0.7,
        timeout=300,
    )

    spec = MODELS.get(row["output_model"])
    output_wrapper = spec.provider if spec else response.raw.get("provider", "unknown")

    return AssistantOutput(
        run_id=str(uuid.uuid4()),
        scenario_id=scenario.scenario_id,
        user_id=scenario.user_id,
        condition=row["condition"],
        output_model=response.model_resolved,
        output_provider_family=response.provider_family,
        output_model_family=response.model_family,
        output_reasoning_effort=response.reasoning_effort,
        output_wrapper=output_wrapper,
        profile_text_supplied=profile_text,
        assistant_response=response.content,
        temperature=0.7,
        tokens_in=response.prompt_tokens,
        tokens_out=response.completion_tokens,
        generated_at=datetime.now(UTC),
    )


def run_pilot(
    pilot_name: str = "micro_pilot",
    run_tag: str | None = None,
    *,
    dry_run: bool = False,
    authors: list[str] | None = None,
    workers: int = 1,
    condition_whitelist: set[str] | None = None,
    scenario_limit: int = 0,
    allow_partial: bool = False,
    strict_manifest: bool = True,
) -> Path:
    """Generate every manifest row, then assert the matrix is whole.

    Raises:
        ManifestPreflightError: before any model call, if the pilot configures
            a treatment cell it cannot produce (and ``strict_manifest``).
        StageIncompleteError: unless every manifest row produced an output
            record (or ``allow_partial`` is set). Without this the author
            stage printed ``Done.`` and exited 0 with rows missing.
    """
    run_tag = run_tag or f"{datetime.now(UTC).date().isoformat()}_{pilot_name}"
    run_d = config.run_dir(run_tag)
    run_d.mkdir(parents=True, exist_ok=True)

    pilot_dir = config.pilot_dir(pilot_name)
    scenarios = {s.scenario_id: s for s in read_jsonl(pilot_dir / "scenarios.jsonl", Scenario)}
    bundles = {b.user_id: b for b in read_jsonl(pilot_dir / "profile_bundles.jsonl", ProfileBundle)}

    # Preflight FIRST: a cell the pilot configures but cannot produce stops
    # the run before a single model call is billed.
    manifest = build_manifest(
        pilot_name,
        authors=authors,
        condition_whitelist=condition_whitelist,
        scenario_limit=scenario_limit,
        strict=strict_manifest,
    )
    manifest_path = run_d / "run_manifest.jsonl"
    with manifest_path.open("w") as fh:
        for row in manifest:
            fh.write(json.dumps(row) + "\n")

    outputs_path = run_d / "assistant_outputs.jsonl"

    done: set[tuple[str, str, str]] = set()
    if outputs_path.exists():
        for out in read_jsonl(outputs_path, AssistantOutput):
            done.add((out.scenario_id, str(out.condition), out.output_model))

    print(f"Run tag: {run_tag}")
    print(f"Manifest: {len(manifest)} rows, {len(done)} already complete, workers={workers}")

    if dry_run:
        print("--dry-run: skipping execution.")
        return run_d

    blinding_key_path = run_d / "blinding_key.json"
    if not blinding_key_path.exists():
        _emit_blinding_key(manifest, blinding_key_path)

    # Build todo list up front
    todo: list[dict] = []
    expected_cells: list[StageCell] = []
    unresolved: list[dict] = []
    for row in manifest:
        if row["scenario_id"] not in scenarios or row["user_id"] not in bundles:
            # A manifest row nothing can satisfy. Recorded, not skipped
            # silently — it is a hole in the matrix like any other.
            unresolved.append({
                "scenario_id": row["scenario_id"],
                "user_id": row["user_id"],
                "condition": row["condition"],
                "output_model": row["output_model"],
                "reason": (
                    "no scenario" if row["scenario_id"] not in scenarios else "no profile bundle"
                ),
            })
            continue
        expected_cells.append(StageCell(
            key=(row["scenario_id"], row["condition"], row["output_model"]),
            author=row["output_model"],
            condition=row["condition"],
            scenario=row["scenario_id"],
        ))
        key = (row["scenario_id"], row["condition"], row["output_model"])
        resolved = _resolve_author_name(row["output_model"])
        key_resolved = (row["scenario_id"], row["condition"], resolved)
        if key in done or key_resolved in done:
            continue
        todo.append(row)

    # Cap-burn handler wraps every model call. The earlier author path was
    # NOT protected — when Anthropic's claude -p hit its 5h cap, it returned
    # rc=1 with empty stderr; the worker just caught the exception and moved
    # on, burning the rest of the cap window on rc=1 spins. With the handler
    # wired here (matching the judge.py pattern), cap is now detected and
    # the run exits cleanly with a checkpoint after retries are exhausted.
    cap_handler = CapBurnHandler(run_tag=run_tag, phase="author")
    resume_cmd = (
        f"uv run python -m psycheeval.run --pilot {pilot_name} --tag {run_tag} "
        f"--authors {','.join(authors or config.AUTHOR_MODELS)} --workers {workers}"
    )

    write_lock = threading.Lock()
    print_lock = threading.Lock()
    completed = {"n": 0, "failed": 0, "cap_aborted": 0}

    def _do_one(row):
        scenario = scenarios[row["scenario_id"]]
        bundle = bundles[row["user_id"]]
        return run_one(row, scenario, bundle)

    def _process(row):
        record_key = f"{row['scenario_id']}:{row['condition']}:{row['output_model']}"
        if cap_handler.is_cap_aborted():
            with print_lock:
                completed["cap_aborted"] += 1
            return
        try:
            output = cap_handler.call_with_backoff(
                lambda: _do_one(row),
                record_key=record_key,
                judge_model=row["output_model"],  # we re-use the field name; here it identifies the author
            )
            with write_lock:
                append_jsonl(outputs_path, output)
            cap_handler.record_success(record_key)
            with print_lock:
                completed["n"] += 1
                if completed["n"] % 10 == 0 or completed["n"] < 10:
                    print(
                        f"  {completed['n']}/{len(todo)} ok  "
                        f"(failed={completed['failed']}, "
                        f"cap_events={cap_handler.cap_event_count})",
                        flush=True,
                    )
        except ClaudeCapError:
            with print_lock:
                completed["failed"] += 1
                print(
                    f"  CAP {row['scenario_id'][:30]} {row['condition']} {row['output_model']} "
                    f"(retries exhausted; cap_events.jsonl written)",
                    flush=True,
                )
        except Exception as e:
            with print_lock:
                completed["failed"] += 1
                print(
                    f"  ERR {row['scenario_id']} {row['condition']} {row['output_model']}: {str(e)[:200]}",
                    flush=True,
                )

    if workers <= 1:
        for i, row in enumerate(todo, 1):
            if cap_handler.is_cap_aborted():
                with print_lock:
                    completed["cap_aborted"] = len(todo) - i + 1
                break
            print(f"  {i}/{len(todo)} {row['scenario_id']} · {row['condition']} · {row['output_model']}")
            _process(row)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_process, r) for r in todo]
            for _ in as_completed(futures):
                pass

    pending_after = len(todo) - completed["n"]
    cp_path = cap_handler.write_checkpoint(
        pending_count=pending_after,
        suggested_resume_command=resume_cmd,
    )
    if cap_handler.is_cap_aborted():
        print(
            f"CAP-ABORTED. {completed['n']} succeeded, {completed['failed']} failed, "
            f"{completed['cap_aborted']} skipped after cap. Checkpoint: {cp_path}. "
            f"Resume with: {resume_cmd}"
        )
    else:
        print(
            f"Done. {completed['n']} succeeded, {completed['failed']} failed. "
            f"Outputs at {outputs_path}. Checkpoint: {cp_path}"
        )
    _refresh_cost_summary(run_tag)

    # Expected vs observed, read back off disk.
    observed: set[tuple[str, str, str]] = set()
    if outputs_path.exists():
        for out in read_jsonl(outputs_path, AssistantOutput):
            observed.add((out.scenario_id, str(out.condition), out.output_model))

    status = stage_status(
        stage="author",
        run_tag=run_tag,
        expected=expected_cells,
        is_observed=lambda c: (
            c.key in observed
            or (c.key[0], c.key[1], _resolve_author_name(c.key[2])) in observed
        ),
        failed=completed["failed"],
        cap_aborted=completed["cap_aborted"],
        unresolved=unresolved,
        allow_partial=allow_partial,
        extra={"outputs_path": str(outputs_path), "resume_command": resume_cmd},
    )
    write_stage_status(run_d, status)
    enforce_complete(status, allow_partial=allow_partial)
    return run_d


def _refresh_cost_summary(run_tag: str) -> None:
    """Best-effort per-run cost rollup (pse-4). Never fails the run."""
    try:
        from psycheeval.cost import write_cost_summary

        path = write_cost_summary(run_tag)
        print(f"Cost summary: {path}")
    except Exception as e:  # cost tracking must never break the pipeline
        print(f"  (cost summary skipped: {e})")


def _resolve_author_name(model_key: str) -> str:
    from psycheeval.llm import MODELS
    spec = MODELS.get(model_key)
    return spec.resolved_id if spec else model_key


def _emit_blinding_key(manifest: list[dict], path: Path) -> None:
    """Randomly map conditions → letters per scenario, authors → letters per row.

    Stored separately; never shown to the judge.
    """
    import random

    rng = random.Random(42)  # reproducible

    # Per-scenario condition blinding
    by_scenario_conds: dict[str, dict[str, str]] = {}
    for row in manifest:
        sid = row["scenario_id"]
        by_scenario_conds.setdefault(sid, {})
        if row["condition"] not in by_scenario_conds[sid]:
            pass  # filled below
    for sid, conds_map in by_scenario_conds.items():
        conds_in_scenario = sorted({r["condition"] for r in manifest if r["scenario_id"] == sid})
        letters = list("ABCDEF")
        rng.shuffle(letters)
        for cond, letter in zip(conds_in_scenario, letters, strict=False):
            conds_map[cond] = letter

    # Per-scenario author blinding (same idea)
    by_scenario_authors: dict[str, dict[str, str]] = {}
    for sid in by_scenario_conds:
        authors_in_scenario = sorted({r["output_model"] for r in manifest if r["scenario_id"] == sid})
        letters = list("XYZW")
        rng.shuffle(letters)
        by_scenario_authors[sid] = dict(zip(authors_in_scenario, letters, strict=False))

    path.write_text(
        json.dumps(
            {"condition_blinding": by_scenario_conds, "author_blinding": by_scenario_authors},
            indent=2,
            sort_keys=True,
        )
    )
    print(f"Wrote blinding key to {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pilot", default="micro_pilot")
    ap.add_argument("--tag", default=None, help="Run tag (default: {date}_{pilot})")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--authors",
        default=",".join(config.AUTHOR_MODELS),
        help="Comma-separated author model keys",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of concurrent author calls. 1 = sequential (default).",
    )
    ap.add_argument(
        "--conditions",
        default="",
        help=(
            "Comma-separated condition whitelist (e.g. 'C_GENERIC_CONTRACT,L1,L2'). "
            "If empty (default), all pilot conditions are dispatched. Useful for v0.3 "
            "Phase 1/2 generation where only new conditions need to be authored."
        ),
    )
    ap.add_argument(
        "--allow-incomplete-matrix",
        action="store_true",
        help=(
            "Generate even though the pilot configures treatment cells that "
            "cannot be produced (a missing profile bundle, an empty treatment "
            "field). Off by default: a silently reduced matrix biases condition "
            "effects while leaving valid-looking JSONL behind."
        ),
    )
    ap.add_argument(
        "--allow-partial",
        action="store_true",
        help=(
            "Accept a generation pass that did not produce every manifest row. "
            "Without this flag a short run exits nonzero instead of printing "
            "'Done.' and returning 0. Either way the gaps are written to "
            "runs/{tag}/stage_status_author.json."
        ),
    )
    ap.add_argument(
        "--scenario-limit",
        type=int,
        default=0,
        help=(
            "If >0, dispatch only the first N scenarios (sorted by scenario_id). "
            "Useful for smoke tests; default 0 = all scenarios."
        ),
    )
    args = ap.parse_args()
    condition_whitelist = (
        {c.strip() for c in args.conditions.split(",") if c.strip()}
        if args.conditions else None
    )
    try:
        run_pilot(
            pilot_name=args.pilot,
            run_tag=args.tag,
            dry_run=args.dry_run,
            authors=args.authors.split(","),
            workers=args.workers,
            condition_whitelist=condition_whitelist,
            scenario_limit=args.scenario_limit,
            allow_partial=args.allow_partial,
            strict_manifest=not args.allow_incomplete_matrix,
        )
    except ManifestPreflightError as e:
        print(f"\nMANIFEST PREFLIGHT FAILED: {e}")
        raise SystemExit(2) from e
    except StageIncompleteError as e:
        # Exit nonzero so `set -euo pipefail` drivers stop here rather than
        # judging an incomplete generation matrix.
        print(f"\nSTAGE INCOMPLETE: {e}")
        raise SystemExit(2) from e


if __name__ == "__main__":
    main()
