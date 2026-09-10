"""Judge pipeline: score assistant outputs and pairwise comparisons.

Two modes:
- `score`: per-response scoring using prompt 06_judge.md
- `pairwise`: side-by-side comparison using prompt 07_pairwise_judge.md

Both modes blind the judge to (a) the condition and (b) the author model.
The blinding key lives in `runs/{tag}/blinding_key.json`.

Usage:
    uv run python -m psycheeval.judge score --tag 2026-04-20_micro
    uv run python -m psycheeval.judge pairwise --tag 2026-04-20_micro
"""

from __future__ import annotations

import argparse
import itertools
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
from psycheeval.io import append_jsonl, read_jsonl
from psycheeval.llm import ClaudeCapError, complete, extract_json
from psycheeval.models import (
    AnchoredJudgeScore,
    AssistantOutput,
    JudgeScore,
    JudgeScores,
    JudgeScoresAnchored,
    PairwiseScore,
    PersonaSeed,
    RedFlag,
    Scenario,
    SynthUserRecord,
    render_red_flag_vocabulary,
)


JUDGE_PROMPT_PATH = config.PROMPTS_DIR / "06_judge.md"
ANCHORED_PROMPT_PATH = config.PROMPTS_DIR / "06b_judge_anchored.md"
PAIRWISE_PROMPT_PATH = config.PROMPTS_DIR / "07_pairwise_judge.md"
PAIRWISE_TERNARY_PROMPT_PATH = config.PROMPTS_DIR / "07b_pairwise_judge_ternary.md"
ANCHORED_PARAPHRASED_PROMPT_PATH = config.PROMPTS_DIR / "06c_judge_anchored_paraphrased.md"

_VALID_RED_FLAGS: frozenset[str] = frozenset(rf.value for rf in RedFlag)

# Global lock for appending to validation_warnings.jsonl from worker threads.
_WARNING_LOCK = threading.Lock()


def _substitute_red_flag_vocabulary(template: str) -> str:
    """Fill the ``{{RED_FLAGS_VOCABULARY}}`` / `_WITH_DESCRIPTIONS` tokens
    with content derived from the RedFlag enum. Tests enforce that prompts
    never contain a hardcoded label list that could drift from the enum.
    """
    return (
        template
        .replace("{{RED_FLAGS_VOCABULARY_WITH_DESCRIPTIONS}}", render_red_flag_vocabulary("labels_with_descriptions"))
        .replace("{{RED_FLAGS_VOCABULARY}}", render_red_flag_vocabulary("labels_only"))
    )


def _warnings_path(run_tag: str) -> Path:
    return config.run_dir(run_tag) / "validation_warnings.jsonl"


def _record_invalid_red_flags(
    invalid_labels: list[str],
    *,
    run_tag: str,
    mode: str,
    judge_model: str,
    author_model: str | None,
    condition: str | None,
    context_id: str,
) -> None:
    """Append one JSONL record per invalid label to validation_warnings.jsonl.

    Structured so aggregating by (judge, author, condition, label) is trivial
    in post-hoc analysis without re-reading full judge responses.
    """
    if not invalid_labels:
        return
    path = _warnings_path(run_tag)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    lines: list[str] = []
    for label in invalid_labels:
        lines.append(json.dumps({
            "timestamp": now,
            "run_tag": run_tag,
            "mode": mode,  # "score" | "pairwise"
            "judge_model": judge_model,
            "author_model": author_model,
            "condition": condition,
            "context_id": context_id,
            "invalid_label": label,
        }))
    with _WARNING_LOCK:
        with path.open("a") as fh:
            for line in lines:
                fh.write(line + "\n")


def _coerce_red_flags(raw) -> tuple[list[str], list[str]]:
    """Split a red-flags response into (valid, invalid) lists.

    Judges occasionally return free-text descriptions instead of enum labels
    (e.g. "length without proportional added signal"). Dropping invalid
    labels keeps the record parseable; free-text observations still land in
    `failure_in_A` / `failure_in_B` / `concise_rationale`. Invalid labels are
    returned separately so callers can persist them to
    ``validation_warnings.jsonl`` — the evidence of mismatch is preserved,
    not silently erased.
    """
    if not isinstance(raw, list):
        return [], []
    valid: list[str] = []
    invalid: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            invalid.append(repr(item))
        elif item in _VALID_RED_FLAGS:
            valid.append(item)
        else:
            invalid.append(item)
    return valid, invalid


def _render_judge_prompt(
    scenario: Scenario,
    user: SynthUserRecord,
    response_text: str,
    *,
    rubric: str = "legacy",
) -> tuple[str, str]:
    if rubric == "paraphrased_anchored":
        path = ANCHORED_PARAPHRASED_PROMPT_PATH
    elif rubric == "anchored":
        path = ANCHORED_PROMPT_PATH
    else:
        path = JUDGE_PROMPT_PATH
    template = _substitute_red_flag_vocabulary(path.read_text())
    usr = (
        template
        .replace("`{{latent_ground_truth}}`", json.dumps(user.latent_ground_truth.model_dump(), indent=2))
        .replace("`{{scenario_object}}`", json.dumps(scenario.model_dump(), indent=2, default=str))
        .replace("`{{assistant_response}}`", response_text)
    )
    return ("You are a blind PsycheEval judge.", usr)


def _render_pairwise_prompt(
    scenario: Scenario, user: SynthUserRecord, resp_a: str, resp_b: str,
    *,
    prompt_path: Path | None = None,
) -> tuple[str, str]:
    template = _substitute_red_flag_vocabulary((prompt_path or PAIRWISE_PROMPT_PATH).read_text())
    usr = (
        template
        .replace("`{{latent_ground_truth}}`", json.dumps(user.latent_ground_truth.model_dump(), indent=2))
        .replace("`{{scenario_object}}`", json.dumps(scenario.model_dump(), indent=2, default=str))
        .replace("`{{response_a}}`", resp_a)
        .replace("`{{response_b}}`", resp_b)
    )
    return ("You are a blind PsycheEval pairwise judge.", usr)


def score_one(
    scenario: Scenario,
    user: SynthUserRecord,
    output: AssistantOutput,
    *,
    judge_model: str,
    rubric: str = "legacy",
    run_tag: str | None = None,
) -> JudgeScore | AnchoredJudgeScore:
    system, usr = _render_judge_prompt(scenario, user, output.assistant_response, rubric=rubric)
    response = complete(system=system, user=usr, model_key=judge_model, temperature=0.2, timeout=300)
    data = extract_json(response.content)

    valid_flags, invalid_flags = _coerce_red_flags(data.get("red_flags", []))
    if invalid_flags and run_tag:
        _record_invalid_red_flags(
            invalid_flags,
            run_tag=run_tag,
            mode="score",
            judge_model=response.model_resolved,
            author_model=output.output_model,
            condition=str(output.condition),
            context_id=output.run_id,
        )

    common_kwargs = dict(
        judge_id=f"judge_{judge_model}_{uuid.uuid4().hex[:8]}",
        judge_model=response.model_resolved,
        judge_provider_family=response.provider_family,
        judge_model_family=response.model_family,
        judge_reasoning_effort=response.reasoning_effort,
        run_id=output.run_id,
        scenario_id=scenario.scenario_id,
        condition_blinded=True,
        author_blinded=True,
        red_flags=valid_flags,
        concise_rationale=data.get("concise_rationale", ""),
        best_feature=data.get("best_feature"),
        worst_feature=data.get("worst_feature"),
        one_sentence_improvement=data.get("one_sentence_improvement"),
        tokens_in=response.prompt_tokens,
        tokens_out=response.completion_tokens,
        judged_at=datetime.now(UTC),
    )

    if rubric in ("anchored", "paraphrased_anchored"):
        scores = JudgeScoresAnchored.model_validate(data["scores"])
        return AnchoredJudgeScore(scores=scores, **common_kwargs)

    scores = JudgeScores.model_validate(data["scores"])
    return JudgeScore(scores=scores, **common_kwargs)


def pairwise_one(
    scenario: Scenario,
    user: SynthUserRecord,
    out_a: AssistantOutput,
    out_b: AssistantOutput,
    *,
    judge_model: str,
    run_tag: str | None = None,
    prompt_path: Path | None = None,
) -> PairwiseScore:
    system, usr = _render_pairwise_prompt(
        scenario, user, out_a.assistant_response, out_b.assistant_response,
        prompt_path=prompt_path,
    )
    response = complete(system=system, user=usr, model_key=judge_model, temperature=0.2, timeout=300)
    data = extract_json(response.content)

    pair_id = f"pw_{uuid.uuid4().hex[:12]}"
    valid_a, invalid_a = _coerce_red_flags(data.get("red_flags_A", []))
    valid_b, invalid_b = _coerce_red_flags(data.get("red_flags_B", []))
    if run_tag:
        if invalid_a:
            _record_invalid_red_flags(
                invalid_a,
                run_tag=run_tag,
                mode="pairwise_A",
                judge_model=response.model_resolved,
                author_model=out_a.output_model,
                condition=str(out_a.condition),
                context_id=f"{pair_id}:A:{out_a.run_id}",
            )
        if invalid_b:
            _record_invalid_red_flags(
                invalid_b,
                run_tag=run_tag,
                mode="pairwise_B",
                judge_model=response.model_resolved,
                author_model=out_b.output_model,
                condition=str(out_b.condition),
                context_id=f"{pair_id}:B:{out_b.run_id}",
            )

    return PairwiseScore(
        pairwise_id=pair_id,
        judge_id=f"judge_{judge_model}",
        judge_model=response.model_resolved,
        judge_provider_family=response.provider_family,
        judge_model_family=response.model_family,
        judge_reasoning_effort=response.reasoning_effort,
        scenario_id=scenario.scenario_id,
        run_id_a=out_a.run_id,
        run_id_b=out_b.run_id,
        winner=data.get("winner", "tie"),
        confidence_0_to_1=float(data.get("confidence_0_to_1", 0.5)),
        why_winner_is_better=data.get("why_winner_is_better", ""),
        failure_in_A=data.get("failure_in_A", ""),
        failure_in_B=data.get("failure_in_B", ""),
        red_flags_A=valid_a,
        red_flags_B=valid_b,
        tokens_in=response.prompt_tokens,
        tokens_out=response.completion_tokens,
        judged_at=datetime.now(UTC),
    )


def score_all(
    run_tag: str,
    pilot_name: str = "micro_pilot",
    *,
    judges: list[str] | None = None,
    workers: int = 1,
    rubric: str = "legacy",
    sample_pct: float = 100.0,
    seed: int = 20260520,
    allow_partial: bool = False,
) -> Path:
    """Score every assistant output under each judge.

    rubric: "legacy" → uses 06_judge.md (0-5 scale), writes judge_scores.jsonl.
            "anchored" → uses 06b_judge_anchored.md (0-10 scale),
                         writes anchored_judge_scores.jsonl.
            "paraphrased_anchored" → uses 06c_judge_anchored_paraphrased.md
                         (0-10 scale, reworded anchors), writes
                         paraphrased_anchored_scores.jsonl. v0.3 D2 sentinel.

    sample_pct: if <100, deterministically samples this fraction of
        (output, judge) pairs. Used for paraphrased sentinel at 15%.

    allow_partial: accept a matrix with missing records. Off by default —
        without it a stage that lost records raises ``StageIncompleteError``
        instead of returning a path a driver would read as success.

    Raises:
        StageIncompleteError: unless every expected (output, judge) record is
            present on disk when the stage ends (or ``allow_partial`` is set).
    """
    import random as _random
    judges = judges or config.JUDGE_MODELS
    run_d = config.run_dir(run_tag)
    pilot_dir = config.pilot_dir(pilot_name)

    scenarios = {s.scenario_id: s for s in read_jsonl(pilot_dir / "scenarios.jsonl", Scenario)}
    users = {u.user_id: u for u in read_jsonl(pilot_dir / "synthetic_user_records.jsonl", SynthUserRecord)}

    outputs = list(read_jsonl(run_d / "assistant_outputs.jsonl", AssistantOutput))
    if rubric == "paraphrased_anchored":
        scores_filename = "paraphrased_anchored_scores.jsonl"
    elif rubric == "anchored":
        scores_filename = "anchored_judge_scores.jsonl"
    else:
        scores_filename = "judge_scores.jsonl"
    scores_path = run_d / scores_filename
    score_model = AnchoredJudgeScore if rubric in ("anchored", "paraphrased_anchored") else JudgeScore

    done: set[tuple[str, str]] = set()
    if scores_path.exists():
        for js in read_jsonl(scores_path, score_model):
            done.add((js.run_id, js.judge_model))

    candidates = []
    already_done: list[tuple[AssistantOutput, str]] = []
    unresolved: list[dict] = []
    for output in outputs:
        scenario = scenarios.get(output.scenario_id)
        user = users.get(output.user_id)
        if scenario is None or user is None:
            # Not a free skip: this output can never be judged, so the matrix
            # it belongs to can never be balanced. Surfaced in stage status.
            unresolved.append({
                "run_id": output.run_id,
                "scenario_id": output.scenario_id,
                "user_id": output.user_id,
                "reason": "no scenario" if scenario is None else "no user record",
            })
            continue
        for judge_model in judges:
            resolved = _resolve(judge_model)
            if (output.run_id, judge_model) in done or (output.run_id, resolved) in done:
                already_done.append((output, judge_model))
                continue
            candidates.append((scenario, user, output, judge_model))

    if sample_pct < 100.0:
        rng = _random.Random(seed)
        n_keep = max(1, int(len(candidates) * sample_pct / 100.0))
        candidates = sorted(candidates, key=lambda c: (c[2].run_id, c[3]))
        candidates = rng.sample(candidates, min(n_keep, len(candidates)))

    todo = candidates

    # The expected matrix is what this invocation is accountable for: records
    # already on disk plus the ones dispatched now (sampling deliberately
    # narrows the second half; it must not narrow the first).
    expected_cells = [
        StageCell(
            key=(o.run_id, jm),
            judge=jm,
            author=o.output_model,
            condition=str(o.condition),
            scenario=o.scenario_id,
        )
        for o, jm in already_done + [(c[2], c[3]) for c in todo]
    ]

    total = len(outputs) * len(judges)
    print(f"Scoring {total} total, {len(done)} done, {len(todo)} pending, workers={workers}")

    cap_handler = CapBurnHandler(run_tag=run_tag, phase=f"score_{rubric}")
    resume_cmd = (
        f"uv run python -m psycheeval.judge score --tag {run_tag} "
        f"--pilot {pilot_name} --judges {','.join(judges)} --workers {workers} "
        f"--rubric {rubric}"
    )

    write_lock = threading.Lock()
    print_lock = threading.Lock()
    completed = {"n": 0, "failed": 0, "cap_aborted": 0}

    def _do_one(scenario, user, output, judge_model):
        return score_one(
            scenario, user, output,
            judge_model=judge_model, rubric=rubric, run_tag=run_tag,
        )

    def _process(task):
        scenario, user, output, judge_model = task
        record_key = f"{output.run_id}:{judge_model}"
        if cap_handler.is_cap_aborted():
            with print_lock:
                completed["cap_aborted"] += 1
            return
        try:
            js = cap_handler.call_with_backoff(
                lambda: _do_one(scenario, user, output, judge_model),
                record_key=record_key,
                judge_model=judge_model,
            )
            with write_lock:
                append_jsonl(scores_path, js)
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
        except ClaudeCapError as e:
            # Already logged by cap_handler. After exhaustion, peers will see
            # is_cap_aborted() and bail. Don't print the full stderr to console
            # because we already wrote it to cap_events.jsonl.
            with print_lock:
                completed["failed"] += 1
                print(
                    f"  CAP {output.scenario_id[:30]} judge={judge_model} "
                    f"(retries exhausted; cap_events.jsonl written)",
                    flush=True,
                )
        except Exception as e:  # non-cap errors propagate to log only
            with print_lock:
                completed["failed"] += 1
                print(
                    f"  ERR {output.scenario_id[:30]} judge={judge_model}: {str(e)[:200]}",
                    flush=True,
                )

    if workers <= 1:
        for i, t in enumerate(todo, 1):
            if cap_handler.is_cap_aborted():
                with print_lock:
                    completed["cap_aborted"] = len(todo) - i + 1
                break
            scenario, user, output, judge_model = t
            print(f"  {i}/{len(todo)} {output.scenario_id[:30]}… · judge={judge_model}")
            _process(t)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_process, t) for t in todo]
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
            f"Scores at {scores_path}. Checkpoint: {cp_path}"
        )
    _refresh_cost_summary(run_tag)

    # Expected vs observed, read back off disk — in-memory success counters
    # cannot see a record that was counted but never landed.
    observed: set[tuple[str, str]] = set()
    if scores_path.exists():
        for js in read_jsonl(scores_path, score_model):
            observed.add((js.run_id, js.judge_model))

    status = stage_status(
        stage=f"score_{rubric}",
        run_tag=run_tag,
        expected=expected_cells,
        is_observed=lambda c: (
            c.key in observed or (c.key[0], _resolve(c.key[1])) in observed
        ),
        failed=completed["failed"],
        cap_aborted=completed["cap_aborted"],
        unresolved=unresolved,
        allow_partial=allow_partial,
        extra={"scores_path": str(scores_path), "resume_command": resume_cmd},
    )
    write_stage_status(run_d, status)
    enforce_complete(status, allow_partial=allow_partial)
    return scores_path


def _refresh_cost_summary(run_tag: str) -> None:
    """Best-effort per-run cost rollup (pse-4). Never fails the judge run."""
    try:
        from psycheeval.cost import write_cost_summary

        path = write_cost_summary(run_tag)
        print(f"Cost summary: {path}")
    except Exception as e:  # cost tracking must never break the pipeline
        print(f"  (cost summary skipped: {e})")


def _parse_pair_whitelist(spec: str) -> set[tuple[str, str, bool]]:
    """Parse a ``--pairs`` CLI argument into a canonical whitelist.

    Accepts comma-separated items of the form ``"COND_A:COND_B"`` or
    ``"COND_A:COND_B@PI"`` (PI-only). Order within a pair is normalized to
    sorted order so ``C4:C0`` and ``C0:C4`` both canonicalize to the same
    tuple. Returns a set of ``(cond_low, cond_high, pi_only)`` triples.
    """
    out: set[tuple[str, str, bool]] = set()
    for raw in (s.strip() for s in spec.split(",")):
        if not raw:
            continue
        pi_only = False
        body = raw
        if "@" in body:
            body, tag = body.rsplit("@", 1)
            tag = tag.strip().upper()
            if tag == "PI":
                pi_only = True
            else:
                raise ValueError(f"Unknown pair tag {tag!r} in {raw!r} (only @PI is supported)")
        if ":" not in body:
            raise ValueError(f"Pair {raw!r} must contain ':' (e.g. C4:C0)")
        a, b = (s.strip() for s in body.split(":", 1))
        if not a or not b:
            raise ValueError(f"Empty side in pair {raw!r}")
        lo, hi = sorted([a, b])
        out.add((lo, hi, pi_only))
    return out


def _persona_type_for_user(user_id: str, seed_index: dict[str, str]) -> str | None:
    """Look up persona_type for a user_id via a pre-built index."""
    return seed_index.get(user_id)


def _build_persona_type_index() -> dict[str, str]:
    """Map synthetic_user_record.user_id → persona_seed.persona_type."""
    seeds: dict[str, PersonaSeed] = {}
    for path in [config.SEED_BANK_PUBLIC, config.SEED_BANK_SYNTHETIC]:
        for seed in read_jsonl(path, PersonaSeed):
            seeds[seed.persona_id] = seed
    index: dict[str, str] = {}
    for pilot_dir in [config.pilot_dir("micro_pilot"), config.pilot_dir("v02_hard_pilot")]:
        users_path = pilot_dir / "synthetic_user_records.jsonl"
        if not users_path.exists():
            continue
        for u in read_jsonl(users_path, SynthUserRecord):
            seed = seeds.get(u.persona_seed_id)
            if seed is not None:
                index[u.user_id] = seed.persona_type
    return index


PAIRWISE_SCOPE_EXHAUSTIVE = "exhaustive"
PAIRWISE_SCOPE_SAME_AUTHOR_ONLY = "same_author_only"
PAIRWISE_SCOPES = (PAIRWISE_SCOPE_EXHAUSTIVE, PAIRWISE_SCOPE_SAME_AUTHOR_ONLY)


def build_pairwise_plan(
    run_tag: str,
    pilot_name: str = "micro_pilot",
    *,
    judges: list[str] | None = None,
    pair_whitelist: set[tuple[str, str, bool]] | None = None,
    scope: str = PAIRWISE_SCOPE_EXHAUSTIVE,
) -> tuple[list[dict], dict]:
    """Enumerate every expected pairwise record and return (tasks, diagnostics).

    Each task dict has stable, deterministic keys derived from the
    assistant_outputs file ordering and the judge / author / condition
    metadata. The canonical key is ``(run_id_a, run_id_b, resolved_judge_model)``,
    matching what `pairwise_one` writes to disk.

    Scope:
      - "exhaustive": every within-scenario pair (matches v0.1 behaviour).
      - "same_author_only": pairs whose two outputs were produced by the same
        author. Cleaner for condition effects.

    The returned diagnostics dict tags filter reasons (whitelist miss, PI-only
    miss, scope miss) so callers can report what was excluded.
    """
    if scope not in PAIRWISE_SCOPES:
        raise ValueError(f"Unknown pair scope {scope!r}; must be one of {PAIRWISE_SCOPES}")
    judges = judges or config.JUDGE_MODELS
    run_d = config.run_dir(run_tag)
    pilot_dir = config.pilot_dir(pilot_name)

    scenarios = {s.scenario_id: s for s in read_jsonl(pilot_dir / "scenarios.jsonl", Scenario)}
    users = {u.user_id: u for u in read_jsonl(pilot_dir / "synthetic_user_records.jsonl", SynthUserRecord)}
    outputs = list(read_jsonl(run_d / "assistant_outputs.jsonl", AssistantOutput))

    persona_type_idx = _build_persona_type_index()
    by_scen: dict[str, list[AssistantOutput]] = {}
    for o in outputs:
        by_scen.setdefault(o.scenario_id, []).append(o)

    tasks: list[dict] = []
    filtered_whitelist = 0
    filtered_pi_only = 0
    filtered_scope = 0
    for sid, outs in by_scen.items():
        scen = scenarios.get(sid)
        if scen is None:
            continue
        user = users.get(scen.user_id)
        if user is None:
            continue
        ptype = persona_type_idx.get(scen.user_id)
        for a, b in itertools.combinations(outs, 2):
            cond_a = str(a.condition)
            cond_b = str(b.condition)
            # Scope filter
            if scope == PAIRWISE_SCOPE_SAME_AUTHOR_ONLY and a.output_model != b.output_model:
                filtered_scope += 1
                continue
            # Whitelist filter
            if pair_whitelist is not None:
                lo, hi = sorted([cond_a, cond_b])
                match_any = False
                match_requires_pi = False
                for w_lo, w_hi, w_pi in pair_whitelist:
                    if (lo, hi) == (w_lo, w_hi):
                        match_any = True
                        match_requires_pi = w_pi
                        break
                if not match_any:
                    filtered_whitelist += 1
                    continue
                if match_requires_pi and ptype != "public_inspired":
                    filtered_pi_only += 1
                    continue
            for judge_model in judges:
                resolved_judge_model = _resolve(judge_model)
                tasks.append({
                    "scenario_id": sid,
                    "user_id": scen.user_id,
                    "persona_type": ptype,
                    "judge_model": judge_model,
                    "author_a": a.output_model,
                    "author_b": b.output_model,
                    "cond_a": cond_a,
                    "cond_b": cond_b,
                    "run_id_a": a.run_id,
                    "run_id_b": b.run_id,
                    "canonical_key": (a.run_id, b.run_id, resolved_judge_model),
                    "_scenario_obj": scen,
                    "_user_obj": user,
                    "_out_a": a,
                    "_out_b": b,
                })

    diag = {
        "scope": scope,
        "judges": list(judges),
        "expected_records": len(tasks),
        "filtered_scope": filtered_scope,
        "filtered_whitelist": filtered_whitelist,
        "filtered_pi_only": filtered_pi_only,
    }
    return tasks, diag


def _pairwise_cell(task: dict, key: tuple[str, ...] | None = None) -> StageCell:
    """One planned pairwise record as a completeness cell.

    Author and condition are the *pair*, sorted, so the breakdown answers
    "which comparison lost records", not "which side of it".
    """
    return StageCell(
        key=key or tuple(task["canonical_key"]),
        judge=task["judge_model"],
        author="|".join(sorted([task["author_a"], task["author_b"]])),
        condition="|".join(sorted([task["cond_a"], task["cond_b"]])),
        scenario=task["scenario_id"],
    )


def observed_pairwise_keys(run_tag: str) -> tuple[set[tuple[str, str, str]], int]:
    """Return (canonical-key set, total record count) from disk."""
    out_path = config.run_dir(run_tag) / "pairwise_scores.jsonl"
    keys: set[tuple[str, str, str]] = set()
    n = 0
    if out_path.exists():
        for ps in read_jsonl(out_path, PairwiseScore):
            keys.add((ps.run_id_a, ps.run_id_b, ps.judge_model))
            n += 1
    return keys, n


def pairwise_coverage_diagnostics(plan: list[dict], observed: set[tuple[str, str, str]]) -> dict:
    """Stratified expected-vs-observed counts. Used by --missing-only and analyzer."""
    from collections import Counter, defaultdict
    by_judge_exp: Counter = Counter()
    by_judge_obs: Counter = Counter()
    by_pair_exp: Counter = Counter()
    by_pair_obs: Counter = Counter()
    by_persona_pair_exp: Counter = Counter()
    by_persona_pair_obs: Counter = Counter()
    by_judge_pair_exp: Counter = Counter()
    by_judge_pair_obs: Counter = Counter()
    by_judge_author_exp: Counter = Counter()
    by_judge_author_obs: Counter = Counter()
    same_vs_cross_exp: Counter = Counter()
    same_vs_cross_obs: Counter = Counter()

    for t in plan:
        lo, hi = sorted([t["cond_a"], t["cond_b"]])
        pair_label = f"{lo}_vs_{hi}"
        ptype = t["persona_type"] or "unknown"
        same_author = t["author_a"] == t["author_b"]
        same_label = "same_author" if same_author else "cross_author"

        by_judge_exp[t["judge_model"]] += 1
        by_pair_exp[pair_label] += 1
        by_persona_pair_exp[(ptype, pair_label)] += 1
        by_judge_pair_exp[(t["judge_model"], pair_label)] += 1
        by_judge_author_exp[(t["judge_model"], t["author_a"], t["author_b"])] += 1
        same_vs_cross_exp[same_label] += 1

        if t["canonical_key"] in observed:
            by_judge_obs[t["judge_model"]] += 1
            by_pair_obs[pair_label] += 1
            by_persona_pair_obs[(ptype, pair_label)] += 1
            by_judge_pair_obs[(t["judge_model"], pair_label)] += 1
            by_judge_author_obs[(t["judge_model"], t["author_a"], t["author_b"])] += 1
            same_vs_cross_obs[same_label] += 1

    def _quota_status(observed: int, expected: int) -> str:
        """Classify a stratum cell by observed/expected ratio.

        - "complete":           observed == expected (all expected records on disk)
        - "partial":            0 < observed < expected (mid-flight or quota-paused)
        - "deferred":           observed == 0 with expected > 0 (no calls run yet —
                                typically a quota-bound judge family in codex-only mode)
        - "empty":              expected == 0 (no work in this stratum)
        """
        if expected <= 0:
            return "empty"
        if observed == 0:
            return "deferred"
        if observed >= expected:
            return "complete"
        return "partial"

    def _zip(exp: Counter, obs: Counter, key_fmt) -> dict:
        out: dict[str, dict] = {}
        for k, e in sorted(exp.items()):
            o = obs.get(k, 0)
            label = key_fmt(k)
            out[label] = {
                "expected": e,
                "observed": o,
                "missing": e - o,
                "coverage_pct": round(100 * o / e, 1) if e else 0.0,
                "quota_status": _quota_status(o, e),
            }
        return out

    diag = {
        "by_judge": _zip(by_judge_exp, by_judge_obs, lambda k: k),
        "by_condition_pair": _zip(by_pair_exp, by_pair_obs, lambda k: k),
        "by_persona_type_pair": _zip(
            by_persona_pair_exp, by_persona_pair_obs, lambda k: f"{k[0]}__{k[1]}"
        ),
        "by_judge_condition_pair": _zip(
            by_judge_pair_exp, by_judge_pair_obs, lambda k: f"{k[0]}__{k[1]}"
        ),
        "by_judge_author_pair": _zip(
            by_judge_author_exp,
            by_judge_author_obs,
            lambda k: f"{k[0]}__{k[1]}_x_{k[2]}",
        ),
        "by_same_vs_cross_author": _zip(
            same_vs_cross_exp, same_vs_cross_obs, lambda k: k
        ),
    }

    # Top-level quota-status summary: judges grouped by completion class.
    # Lets reports headline "Opus: deferred (weekly quota window)" without the
    # reader having to scan a coverage table.
    judge_status_summary: dict[str, list[str]] = {
        "complete": [],
        "partial": [],
        "deferred": [],
    }
    for j_label, j_cell in diag["by_judge"].items():
        status = j_cell["quota_status"]
        if status in judge_status_summary:
            judge_status_summary[status].append(j_label)
    diag["judge_status_summary"] = judge_status_summary
    return diag


def _print_coverage_diagnostics(diag: dict, planner_diag: dict, observed_count: int) -> None:
    """Pretty-print stratified coverage to stdout for --missing-only mode."""
    print("=" * 72)
    print("Pairwise coverage diagnostics")
    print("=" * 72)
    print(f"Scope: {planner_diag['scope']}")
    print(f"Judges: {', '.join(planner_diag['judges'])}")
    print(f"Expected (planner-derived): {planner_diag['expected_records']}")
    print(f"Observed on disk:           {observed_count}")
    print(f"Filtered by scope:          {planner_diag['filtered_scope']}")
    print(f"Filtered by whitelist:      {planner_diag['filtered_whitelist']}")
    print(f"Filtered by PI-only flag:   {planner_diag['filtered_pi_only']}")
    print()
    # Top-level summary (judges by quota class)
    summary = diag.get("judge_status_summary", {})
    if summary:
        print("-- judge_status_summary --")
        for status_label, judge_list in summary.items():
            print(f"  {status_label}: {', '.join(judge_list) if judge_list else '(none)'}")
        print()
    # Stratified cells
    stratum_sections = (
        "by_judge",
        "by_condition_pair",
        "by_persona_type_pair",
        "by_judge_condition_pair",
        "by_judge_author_pair",
        "by_same_vs_cross_author",
    )
    for section_name in stratum_sections:
        section = diag.get(section_name, {})
        if not section:
            continue
        print(f"-- {section_name} --")
        for k, v in section.items():
            marker = " " if v["missing"] == 0 else "*"
            qstat = v.get("quota_status", "")
            qstr = f" [{qstat}]" if qstat and qstat != "complete" else ""
            print(f"  {marker} {k}: {v['observed']}/{v['expected']}  ({v['coverage_pct']}%) missing={v['missing']}{qstr}")
        print()


def pairwise_swap_rejudge(
    run_tag: str,
    pilot_name: str = "micro_pilot",
    *,
    judges: list[str] | None = None,
    workers: int = 1,
    pair_whitelist: set[tuple[str, str, bool]] | None = None,
    allow_partial: bool = False,
) -> Path:
    """AB/BA counterbalanced rejudging — re-call pairwise with A/B swapped.

    Source: 2026-05-15 external review (all 3 reviewers unanimous). Existing
    pairwise records have lo-numbered condition almost always in slot A and
    hi in slot B (Phase 0.E confirmed slot_a_is_lo_share ≥ 0.988 for all 10
    pairs). To disambiguate position bias from condition preference, this
    function reads every existing pairwise record matching the filter and
    re-judges the same pair with run_id_a/run_id_b SWAPPED.

    Output: pairwise_swap_scores.jsonl (separate file; same PairwiseScore
    schema). Analyzer joins via the run_id-swap signature: a swap of
    (scenario_id, run_id_a=X, run_id_b=Y, judge=J) is the record with
    (scenario_id, run_id_a=Y, run_id_b=X, judge=J).

    Cap-burn protected. Resumable via the existing canonical-key dedup
    against the swap output file.
    """
    judges = judges or config.JUDGE_MODELS
    run_d = config.run_dir(run_tag)
    pilot_dir = config.pilot_dir(pilot_name)
    swap_path = run_d / "pairwise_swap_scores.jsonl"
    original_path = run_d / "pairwise_scores.jsonl"
    if not original_path.exists():
        print(f"No pairwise_scores.jsonl at {original_path}; nothing to rejudge.")
        return swap_path

    scenarios = {s.scenario_id: s for s in read_jsonl(pilot_dir / "scenarios.jsonl", Scenario)}
    users = {u.user_id: u for u in read_jsonl(pilot_dir / "synthetic_user_records.jsonl", SynthUserRecord)}
    outputs_by_run = {o.run_id: o for o in read_jsonl(run_d / "assistant_outputs.jsonl", AssistantOutput)}

    originals = list(read_jsonl(original_path, PairwiseScore))

    # Already-swapped: detected by canonical key (scenario, run_a, run_b, judge)
    # on the swap output file
    already_swapped: set[tuple[str, str, str, str]] = set()
    if swap_path.exists():
        for ps in read_jsonl(swap_path, PairwiseScore):
            already_swapped.add(
                (ps.scenario_id, ps.run_id_a, ps.run_id_b, ps.judge_model)
            )

    # Map resolved-id → spec-key (for back-translating stored judge_model values
    # to invoke complete() with the right model_key). gpt-5.5 (resolved) →
    # gpt-5.5-xhigh (spec), etc.
    from psycheeval.llm import MODELS as _MODELS
    resolved_to_spec: dict[str, str] = {}
    for spec_key, spec in _MODELS.items():
        resolved_to_spec.setdefault(spec.resolved_id, spec_key)
    # Build accepted set: includes both spec keys and their resolved ids
    accepted_judge_ids: set[str] = set(judges)
    for j in list(judges):
        spec = _MODELS.get(j)
        if spec:
            accepted_judge_ids.add(spec.resolved_id)

    todo: list[dict] = []
    expected_cells: list[StageCell] = []
    unresolved: list[dict] = []
    for orig in originals:
        # Filter to target judges (accept both spec key and resolved id)
        if orig.judge_model not in accepted_judge_ids:
            continue
        out_a_orig = outputs_by_run.get(orig.run_id_a)
        out_b_orig = outputs_by_run.get(orig.run_id_b)
        if not out_a_orig or not out_b_orig:
            continue
        # Optionally filter by condition pair whitelist
        if pair_whitelist:
            ca, cb = str(out_a_orig.condition), str(out_b_orig.condition)
            ordered = tuple(sorted([ca, cb]))
            persona_type_id = out_a_orig.user_id  # PI check via prefix
            is_pi = persona_type_id.startswith("user_pfi_")
            matched = False
            for w in pair_whitelist:
                wa, wb, pi_only = w
                if {wa, wb} == {ca, cb} and (not pi_only or is_pi):
                    matched = True
                    break
            if not matched:
                continue
        # Same-author only (AB/BA in v0.2 is constrained to same-author)
        if out_a_orig.output_model != out_b_orig.output_model:
            continue
        scenario = scenarios.get(orig.scenario_id)
        user = users.get(out_a_orig.user_id)
        if scenario is None or user is None:
            unresolved.append({
                "pairwise_id": orig.pairwise_id,
                "scenario_id": orig.scenario_id,
                "user_id": out_a_orig.user_id,
                "reason": "no scenario" if scenario is None else "no user record",
            })
            continue
        # SWAPPED key: (scenario_id, run_a_swap=run_id_b, run_b_swap=run_id_a, judge)
        swap_key = (orig.scenario_id, orig.run_id_b, orig.run_id_a, orig.judge_model)
        # Every eligible original owes a swap record, whether it already has
        # one or is dispatched below.
        expected_cells.append(StageCell(
            key=swap_key,
            judge=orig.judge_model,
            author=out_a_orig.output_model,
            condition="|".join(sorted([str(out_a_orig.condition), str(out_b_orig.condition)])),
            scenario=orig.scenario_id,
        ))
        if swap_key in already_swapped:
            continue
        # Translate resolved id back to spec key for complete() call.
        # If orig.judge_model is already a spec key, use as-is.
        invoke_key = orig.judge_model
        if orig.judge_model not in _MODELS:
            invoke_key = resolved_to_spec.get(orig.judge_model, orig.judge_model)

        todo.append({
            "scenario": scenario,
            "user": user,
            "out_a_swapped": out_b_orig,  # NOTE: swap here
            "out_b_swapped": out_a_orig,
            "judge_model": invoke_key,
            "original_pairwise_id": orig.pairwise_id,
            "swap_key": swap_key,
        })

    total_originals = len(originals)
    print(
        f"Pairwise swap-rejudge: "
        f"originals={total_originals}  "
        f"target_judges={','.join(judges)}  "
        f"already_swapped={len(already_swapped)}  "
        f"pending={len(todo)}  "
        f"workers={workers}"
    )

    cap_handler = CapBurnHandler(run_tag=run_tag, phase="pairwise_swap")
    pair_filter_arg = (
        f" --pairs {','.join(f'{a}:{b}' + ('@PI' if pi else '') for (a, b, pi) in pair_whitelist)}"
        if pair_whitelist else ""
    )
    resume_cmd = (
        f"uv run python -m psycheeval.judge pairwise-swap --tag {run_tag} "
        f"--pilot {pilot_name} --judges {','.join(judges)} --workers {workers}"
        f"{pair_filter_arg}"
    )

    write_lock = threading.Lock()
    print_lock = threading.Lock()
    completed = {"n": 0, "failed": 0, "cap_aborted": 0}

    def _do_one(task):
        return pairwise_one(
            task["scenario"],
            task["user"],
            task["out_a_swapped"],
            task["out_b_swapped"],
            judge_model=task["judge_model"],
            run_tag=run_tag,
        )

    def _process(task):
        record_key = (
            f"swap:{task['scenario'].scenario_id}:{task['judge_model']}:"
            f"{task['out_a_swapped'].run_id}__vs__{task['out_b_swapped'].run_id}"
        )
        if cap_handler.is_cap_aborted():
            with print_lock:
                completed["cap_aborted"] += 1
            return
        try:
            ps = cap_handler.call_with_backoff(
                lambda: _do_one(task),
                record_key=record_key,
                judge_model=task["judge_model"],
            )
            with write_lock:
                append_jsonl(swap_path, ps)
            cap_handler.record_success(record_key)
            with print_lock:
                completed["n"] += 1
                if completed["n"] % 10 == 0 or completed["n"] < 10:
                    print(
                        f"  {completed['n']}/{len(todo)} ok "
                        f"(failed={completed['failed']}, "
                        f"cap_events={cap_handler.cap_event_count})",
                        flush=True,
                    )
        except ClaudeCapError:
            with print_lock:
                completed["failed"] += 1
                print(
                    f"  CAP {task['scenario'].scenario_id[:30]} judge={task['judge_model']} "
                    f"(retries exhausted; cap_events.jsonl written)",
                    flush=True,
                )
        except Exception as e:
            with print_lock:
                completed["failed"] += 1
                print(
                    f"  ERR {task['scenario'].scenario_id[:30]} judge={task['judge_model']}: {str(e)[:200]}",
                    flush=True,
                )

    if workers <= 1:
        for i, t in enumerate(todo, 1):
            if cap_handler.is_cap_aborted():
                with print_lock:
                    completed["cap_aborted"] = len(todo) - i + 1
                break
            _process(t)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_process, t) for t in todo]
            for _ in as_completed(futures):
                pass

    print(
        f"Pairwise swap-rejudge done: completed={completed['n']}/{len(todo)}, "
        f"failed={completed['failed']}, cap_aborted={completed['cap_aborted']}, "
        f"cap_events={cap_handler.cap_event_count}"
    )
    if completed["cap_aborted"] > 0:
        print(f"\n  Resume: {resume_cmd}\n")

    observed_after: set[tuple[str, str, str, str]] = set()
    if swap_path.exists():
        for ps in read_jsonl(swap_path, PairwiseScore):
            observed_after.add((ps.scenario_id, ps.run_id_a, ps.run_id_b, ps.judge_model))
    status = stage_status(
        stage="pairwise_swap",
        run_tag=run_tag,
        expected=expected_cells,
        is_observed=lambda c: c.key in observed_after,
        failed=completed["failed"],
        cap_aborted=completed["cap_aborted"],
        unresolved=unresolved,
        allow_partial=allow_partial,
        extra={"out_path": str(swap_path), "resume_command": resume_cmd},
    )
    write_stage_status(run_d, status)
    enforce_complete(status, allow_partial=allow_partial)
    return swap_path


def _pairwise_subset_rejudge(
    run_tag: str,
    pilot_name: str,
    *,
    judges: list[str] | None,
    workers: int,
    pair_whitelist: set[tuple[str, str, bool]] | None,
    sample_pct: float,
    seed: int,
    output_filename: str,
    prompt_path: Path,
    phase_name: str,
    cli_command: str,
    record_key_prefix: str,
    allow_partial: bool = False,
) -> Path:
    """Shared subset-rejudge driver for D1 (same-orientation) and D4 (ternary).

    Reads existing pairwise records, samples sample_pct deterministically,
    re-judges with the given prompt_path. Writes to runs/{tag}/{output_filename}.

    For D1: prompt_path = 07_pairwise_judge.md, output_filename = same_orientation_swap_scores.jsonl
    For D4: prompt_path = 07b_pairwise_judge_ternary.md, output_filename = pairwise_ternary_scores.jsonl

    Cap-burn protected. Resumable via canonical-key dedup.
    """
    import random

    judges = judges or config.JUDGE_MODELS
    run_d = config.run_dir(run_tag)
    pilot_dir = config.pilot_dir(pilot_name)
    out_path = run_d / output_filename
    original_path = run_d / "pairwise_scores.jsonl"
    if not original_path.exists():
        print(f"No pairwise_scores.jsonl at {original_path}; nothing to rejudge.")
        return out_path

    scenarios = {s.scenario_id: s for s in read_jsonl(pilot_dir / "scenarios.jsonl", Scenario)}
    users = {u.user_id: u for u in read_jsonl(pilot_dir / "synthetic_user_records.jsonl", SynthUserRecord)}
    outputs_by_run = {o.run_id: o for o in read_jsonl(run_d / "assistant_outputs.jsonl", AssistantOutput)}

    originals = list(read_jsonl(original_path, PairwiseScore))

    # Already-rejudged: detected by canonical key on the output file.
    # Note: SAME orientation, so the key is identical to the original.
    already_done: set[tuple[str, str, str, str]] = set()
    if out_path.exists():
        for ps in read_jsonl(out_path, PairwiseScore):
            already_done.add(
                (ps.scenario_id, ps.run_id_a, ps.run_id_b, ps.judge_model)
            )

    from psycheeval.llm import MODELS as _MODELS
    resolved_to_spec: dict[str, str] = {}
    for spec_key, spec in _MODELS.items():
        resolved_to_spec.setdefault(spec.resolved_id, spec_key)
    accepted_judge_ids: set[str] = set(judges)
    for j in list(judges):
        spec = _MODELS.get(j)
        if spec:
            accepted_judge_ids.add(spec.resolved_id)

    # First, build the eligible-records list (pre-sampling)
    eligible: list[PairwiseScore] = []
    for orig in originals:
        if orig.judge_model not in accepted_judge_ids:
            continue
        out_a_orig = outputs_by_run.get(orig.run_id_a)
        out_b_orig = outputs_by_run.get(orig.run_id_b)
        if not out_a_orig or not out_b_orig:
            continue
        if pair_whitelist:
            ca, cb = str(out_a_orig.condition), str(out_b_orig.condition)
            persona_type_id = out_a_orig.user_id
            is_pi = persona_type_id.startswith("user_pfi_")
            matched = False
            for w in pair_whitelist:
                wa, wb, pi_only = w
                if {wa, wb} == {ca, cb} and (not pi_only or is_pi):
                    matched = True
                    break
            if not matched:
                continue
        if out_a_orig.output_model != out_b_orig.output_model:
            continue
        if scenarios.get(orig.scenario_id) is None or users.get(out_a_orig.user_id) is None:
            continue
        eligible.append(orig)

    # Deterministic sampling at sample_pct
    rng = random.Random(seed)
    n_total = len(eligible)
    n_sample = max(1, int(n_total * sample_pct / 100.0))
    sampled = sorted(eligible, key=lambda r: r.pairwise_id) if hasattr(eligible[0] if eligible else None, 'pairwise_id') else eligible
    sampled = rng.sample(sampled, min(n_sample, n_total)) if n_total > 0 else []

    todo: list[dict] = []
    expected_cells: list[StageCell] = []
    for orig in sampled:
        out_a_orig = outputs_by_run[orig.run_id_a]
        out_b_orig = outputs_by_run[orig.run_id_b]
        scenario = scenarios[orig.scenario_id]
        user = users[out_a_orig.user_id]
        canonical_key = (orig.scenario_id, orig.run_id_a, orig.run_id_b, orig.judge_model)
        # The sample IS the expected matrix here — every sampled record owes a
        # rejudgment, already done or dispatched below.
        expected_cells.append(StageCell(
            key=canonical_key,
            judge=orig.judge_model,
            author=out_a_orig.output_model,
            condition="|".join(sorted([str(out_a_orig.condition), str(out_b_orig.condition)])),
            scenario=orig.scenario_id,
        ))
        if canonical_key in already_done:
            continue
        invoke_key = orig.judge_model if orig.judge_model in _MODELS else resolved_to_spec.get(orig.judge_model, orig.judge_model)
        todo.append({
            "scenario": scenario,
            "user": user,
            "out_a": out_a_orig,
            "out_b": out_b_orig,
            "judge_model": invoke_key,
            "original_pairwise_id": orig.pairwise_id,
            "canonical_key": canonical_key,
        })

    print(
        f"{phase_name} sentinel: "
        f"originals={len(originals)}  eligible={n_total}  sample_pct={sample_pct}  "
        f"sampled={n_sample}  already_done={len(already_done)}  "
        f"pending={len(todo)}  workers={workers}"
    )

    cap_handler = CapBurnHandler(run_tag=run_tag, phase=phase_name)
    pair_filter_arg = (
        f" --pairs {','.join(f'{a}:{b}' + ('@PI' if pi else '') for (a, b, pi) in pair_whitelist)}"
        if pair_whitelist else ""
    )
    resume_cmd = (
        f"uv run python -m psycheeval.judge {cli_command} --tag {run_tag} "
        f"--pilot {pilot_name} --judges {','.join(judges)} --workers {workers}"
        f"{pair_filter_arg}"
    )

    write_lock = threading.Lock()
    print_lock = threading.Lock()
    completed = {"n": 0, "failed": 0, "cap_aborted": 0}

    def _do_one(task):
        # SAME orientation re-judge: out_a stays out_a, out_b stays out_b.
        # The prompt may differ (07 forced-choice or 07b ternary).
        return pairwise_one(
            task["scenario"],
            task["user"],
            task["out_a"],
            task["out_b"],
            judge_model=task["judge_model"],
            run_tag=run_tag,
            prompt_path=prompt_path,
        )

    def _process(task):
        record_key = (
            f"{record_key_prefix}:{task['scenario'].scenario_id}:{task['judge_model']}:"
            f"{task['out_a'].run_id}__vs__{task['out_b'].run_id}"
        )
        if cap_handler.is_cap_aborted():
            with print_lock:
                completed["cap_aborted"] += 1
            return
        try:
            ps = cap_handler.call_with_backoff(
                lambda: _do_one(task),
                record_key=record_key,
                judge_model=task["judge_model"],
            )
            with write_lock:
                append_jsonl(out_path, ps)
            cap_handler.record_success(record_key)
            with print_lock:
                completed["n"] += 1
                if completed["n"] % 10 == 0 or completed["n"] < 10:
                    print(
                        f"  {completed['n']}/{len(todo)} ok "
                        f"(failed={completed['failed']}, "
                        f"cap_events={cap_handler.cap_event_count})",
                        flush=True,
                    )
        except ClaudeCapError:
            with print_lock:
                completed["failed"] += 1
                print(
                    f"  CAP {task['scenario'].scenario_id[:30]} judge={task['judge_model']} "
                    f"(retries exhausted)",
                    flush=True,
                )
        except Exception as e:
            with print_lock:
                completed["failed"] += 1
                print(
                    f"  ERR {task['scenario'].scenario_id[:30]} judge={task['judge_model']}: {str(e)[:200]}",
                    flush=True,
                )

    if workers <= 1:
        for i, t in enumerate(todo, 1):
            if cap_handler.is_cap_aborted():
                with print_lock:
                    completed["cap_aborted"] = len(todo) - i + 1
                break
            _process(t)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_process, t) for t in todo]
            for _ in as_completed(futures):
                pass

    print(
        f"{phase_name} done: completed={completed['n']}/{len(todo)}, "
        f"failed={completed['failed']}, cap_aborted={completed['cap_aborted']}, "
        f"cap_events={cap_handler.cap_event_count}"
    )
    if completed["cap_aborted"] > 0:
        print(f"\n  Resume: {resume_cmd}\n")

    observed_after: set[tuple[str, str, str, str]] = set()
    if out_path.exists():
        for ps in read_jsonl(out_path, PairwiseScore):
            observed_after.add((ps.scenario_id, ps.run_id_a, ps.run_id_b, ps.judge_model))
    status = stage_status(
        stage=phase_name,
        run_tag=run_tag,
        expected=expected_cells,
        is_observed=lambda c: c.key in observed_after,
        failed=completed["failed"],
        cap_aborted=completed["cap_aborted"],
        allow_partial=allow_partial,
        extra={"out_path": str(out_path), "resume_command": resume_cmd},
    )
    write_stage_status(run_d, status)
    enforce_complete(status, allow_partial=allow_partial)
    return out_path


def pairwise_same_orientation_rejudge(
    run_tag: str,
    pilot_name: str = "micro_pilot",
    *,
    judges: list[str] | None = None,
    workers: int = 1,
    pair_whitelist: set[tuple[str, str, bool]] | None = None,
    sample_pct: float = 10.0,
    seed: int = 20260519,
    allow_partial: bool = False,
) -> Path:
    """Same-orientation rejudge sentinel for D1 (v0.3 Phase 3.2 / R11).

    Re-judges existing pairwise records WITHOUT swapping slot order using
    the standard forced-choice prompt. Any winner change = retest noise.
    Sampled at sample_pct (default 10%).

    Output: same_orientation_swap_scores.jsonl
    """
    return _pairwise_subset_rejudge(
        run_tag=run_tag,
        pilot_name=pilot_name,
        judges=judges,
        workers=workers,
        pair_whitelist=pair_whitelist,
        sample_pct=sample_pct,
        seed=seed,
        output_filename="same_orientation_swap_scores.jsonl",
        prompt_path=PAIRWISE_PROMPT_PATH,
        phase_name="same_orientation_rejudge",
        cli_command="same-orientation-rejudge",
        record_key_prefix="same_orient",
        allow_partial=allow_partial,
    )


def pairwise_ternary_sample(
    run_tag: str,
    pilot_name: str = "micro_pilot",
    *,
    judges: list[str] | None = None,
    workers: int = 1,
    pair_whitelist: set[tuple[str, str, bool]] | None = None,
    sample_pct: float = 10.0,
    seed: int = 20260520,
    allow_partial: bool = False,
) -> Path:
    """Ternary tie/equipoise pairwise sentinel for D4 (v0.3 Phase 4 / R12).

    Re-judges existing pairwise records using the ternary prompt at
    07b_pairwise_judge_ternary.md (which allows winner = "no_meaningful_difference").
    Same orientation as the original (NOT a swap).

    The D4 analyzer block joins these against the original forced-choice
    records to estimate the corpus-scoped tie rate per pair.

    Sampled at sample_pct (default 10%). Failure trigger #2: tie rate >25%
    on a C5_CONTRACT-edge pair downgrades that pair's package claim.

    Output: pairwise_ternary_scores.jsonl
    """
    return _pairwise_subset_rejudge(
        run_tag=run_tag,
        pilot_name=pilot_name,
        judges=judges,
        workers=workers,
        pair_whitelist=pair_whitelist,
        sample_pct=sample_pct,
        seed=seed,
        output_filename="pairwise_ternary_scores.jsonl",
        prompt_path=PAIRWISE_TERNARY_PROMPT_PATH,
        phase_name="ternary_sample",
        cli_command="ternary-sample",
        record_key_prefix="ternary",
        allow_partial=allow_partial,
    )


def pairwise_all(
    run_tag: str,
    pilot_name: str = "micro_pilot",
    *,
    judges: list[str] | None = None,
    workers: int = 1,
    pair_whitelist: set[tuple[str, str, bool]] | None = None,
    scope: str = PAIRWISE_SCOPE_EXHAUSTIVE,
    missing_only: bool = False,
    allow_partial: bool = False,
) -> Path:
    """Pairwise judging. Set workers>1 to run judge calls concurrently.

    pair_whitelist: condition-pair filter; ``None`` = every pair.
    scope: "exhaustive" (default, v0.1 behaviour) or "same_author_only".
    missing_only: print stratified coverage diagnostics before dispatch.
        The behaviour is the same either way — completed records are always
        skipped via the canonical key — but the diagnostic surfaces what
        coverage looks like after the run plan is computed.
    allow_partial: accept a plan that did not complete (see ``score_all``).

    Raises:
        StageIncompleteError: unless every planned record is on disk when the
            stage ends (or ``allow_partial`` is set).
    """
    judges = judges or config.JUDGE_MODELS
    run_d = config.run_dir(run_tag)
    out_path = run_d / "pairwise_scores.jsonl"

    plan, planner_diag = build_pairwise_plan(
        run_tag, pilot_name, judges=judges, pair_whitelist=pair_whitelist, scope=scope,
    )
    observed, observed_count = observed_pairwise_keys(run_tag)

    if missing_only:
        cov = pairwise_coverage_diagnostics(plan, observed)
        _print_coverage_diagnostics(cov, planner_diag, observed_count)

    # Build todo list: every planned task whose canonical key isn't observed yet
    todo: list[dict] = []
    for t in plan:
        canon = t["canonical_key"]
        # also accept the resolved-judge variant of the canonical key
        resolved_canon = (canon[0], canon[1], _resolve(canon[2]))
        if canon in observed or resolved_canon in observed:
            continue
        todo.append(t)

    print(
        f"Pairwise: scope={scope}  expected={len(plan)}  observed={observed_count}  "
        f"pending={len(todo)}  workers={workers}"
    )

    cap_handler = CapBurnHandler(run_tag=run_tag, phase="pairwise")
    pair_filter_arg = (
        f" --pairs {','.join(f'{a}:{b}' + ('@PI' if pi else '') for (a, b, pi) in pair_whitelist)}"
        if pair_whitelist else ""
    )
    resume_cmd = (
        f"uv run python -m psycheeval.judge pairwise --tag {run_tag} "
        f"--pilot {pilot_name} --judges {','.join(judges)} --workers {workers} "
        f"--scope {scope}{pair_filter_arg}"
    )

    write_lock = threading.Lock()
    print_lock = threading.Lock()
    completed = {"n": 0, "failed": 0, "cap_aborted": 0}

    def _do_one(task):
        return pairwise_one(
            task["_scenario_obj"],
            task["_user_obj"],
            task["_out_a"],
            task["_out_b"],
            judge_model=task["judge_model"],
            run_tag=run_tag,
        )

    def _process(task):
        record_key = (
            f"{task['scenario_id']}:{task['judge_model']}:"
            f"{task['_out_a'].run_id}__vs__{task['_out_b'].run_id}"
        )
        if cap_handler.is_cap_aborted():
            with print_lock:
                completed["cap_aborted"] += 1
            return
        try:
            ps = cap_handler.call_with_backoff(
                lambda: _do_one(task),
                record_key=record_key,
                judge_model=task["judge_model"],
            )
            with write_lock:
                append_jsonl(out_path, ps)
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
                    f"  CAP {task['scenario_id'][:30]} judge={task['judge_model']} "
                    f"(retries exhausted; cap_events.jsonl written)",
                    flush=True,
                )
        except Exception as e:
            with print_lock:
                completed["failed"] += 1
                print(
                    f"  ERR {task['scenario_id'][:30]} judge={task['judge_model']}: {str(e)[:200]}",
                    flush=True,
                )

    if workers <= 1:
        for i, t in enumerate(todo, 1):
            if cap_handler.is_cap_aborted():
                with print_lock:
                    completed["cap_aborted"] = len(todo) - i + 1
                break
            print(f"  {i}/{len(todo)} {t['scenario_id'][:30]}… judge={t['judge_model']}")
            _process(t)
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_process, t) for t in todo]
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
            f"Pairwise at {out_path}. Checkpoint: {cp_path}"
        )
    _refresh_cost_summary(run_tag)

    observed_after, _ = observed_pairwise_keys(run_tag)
    status = stage_status(
        stage="pairwise",
        run_tag=run_tag,
        expected=[_pairwise_cell(t) for t in plan],
        is_observed=lambda c: c.key in observed_after,
        failed=completed["failed"],
        cap_aborted=completed["cap_aborted"],
        allow_partial=allow_partial,
        extra={
            "out_path": str(out_path),
            "resume_command": resume_cmd,
            "planner": planner_diag,
        },
    )
    write_stage_status(run_d, status)
    enforce_complete(status, allow_partial=allow_partial)
    return out_path


def _resolve(model_key: str) -> str:
    from psycheeval.llm import MODELS
    spec = MODELS.get(model_key)
    return spec.resolved_id if spec else model_key


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["score", "pairwise", "pairwise-swap",
                                       "same-orientation-rejudge", "ternary-sample"])
    ap.add_argument("--tag", required=True)
    ap.add_argument("--pilot", default="micro_pilot")
    ap.add_argument(
        "--judges",
        default=",".join(config.JUDGE_MODELS),
        help="Comma-separated judge model keys",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of concurrent judge calls. 1 = sequential (default).",
    )
    ap.add_argument(
        "--rubric",
        choices=["legacy", "anchored", "paraphrased_anchored"],
        default="legacy",
        help="Judge rubric: legacy (0-5, 06_judge.md), anchored (0-10, 06b_judge_anchored.md), "
             "or paraphrased_anchored (0-10, 06c_judge_anchored_paraphrased.md, D2 sentinel). "
             "Pairwise ignores this flag.",
    )
    ap.add_argument(
        "--sample-pct",
        type=float,
        default=100.0,
        help="Score score subset percentage. Default 100. v0.3 D2 paraphrased sentinel uses 15.",
    )
    ap.add_argument(
        "--pairs",
        default="",
        help=(
            "Pairwise only: comma-separated condition-pair whitelist. Examples: "
            "'C4:C0,C4:C1,C3:C4' or 'C4:C5@PI,C4:C1_padded'. '@PI' restricts "
            "that pair to public-inspired personas. Empty = every within-scenario pair."
        ),
    )
    ap.add_argument(
        "--scope",
        choices=PAIRWISE_SCOPES,
        default=PAIRWISE_SCOPE_EXHAUSTIVE,
        help=(
            "Pairwise scope. 'exhaustive' (default) judges every within-scenario pair. "
            "'same_author_only' restricts to pairs where both outputs share an author — "
            "cleaner for condition effects."
        ),
    )
    ap.add_argument(
        "--missing-only",
        action="store_true",
        help=(
            "Pairwise only: print stratified expected-vs-observed coverage diagnostics "
            "before dispatch. Behaviour is unchanged (the canonical-key resume always "
            "skips completed records); the flag exposes what coverage actually is."
        ),
    )
    ap.add_argument(
        "--allow-partial",
        action="store_true",
        help=(
            "Accept a stage that did not produce its whole expected matrix. "
            "Without this flag a stage missing records exits nonzero instead of "
            "printing 'Done.' and returning 0 — a driver must be able to tell a "
            "complete matrix from one missing an entire judge family. Either way "
            "the gaps are written to runs/{tag}/stage_status_{stage}.json."
        ),
    )
    ap.add_argument(
        "--ab-ba-mandatory",
        action="store_true",
        help=(
            "Pairwise mode only: after the forced-choice pairwise pass completes, "
            "automatically dispatch the AB/BA swap-rejudgment pass with the same "
            "judges/scope/pair-whitelist. v0.3 default per Phase -1.3 (Path A). "
            "Reduces the v0.2 problem where retrofitting AB/BA was a separate phase."
        ),
    )
    args = ap.parse_args()
    judges = args.judges.split(",")
    try:
        if args.mode == "score":
            score_all(
                args.tag,
                args.pilot,
                judges=judges,
                workers=args.workers,
                rubric=args.rubric,
                sample_pct=args.sample_pct,
                allow_partial=args.allow_partial,
            )
        elif args.mode == "pairwise":
            whitelist = _parse_pair_whitelist(args.pairs) if args.pairs else None
            pairwise_all(
                args.tag,
                args.pilot,
                judges=judges,
                workers=args.workers,
                pair_whitelist=whitelist,
                scope=args.scope,
                missing_only=args.missing_only,
                allow_partial=args.allow_partial,
            )
            if args.ab_ba_mandatory:
                print("\n=== --ab-ba-mandatory: dispatching AB/BA swap rejudgment ===")
                pairwise_swap_rejudge(
                    args.tag,
                    args.pilot,
                    judges=judges,
                    workers=args.workers,
                    pair_whitelist=whitelist,
                    allow_partial=args.allow_partial,
                )
                print("=== AB/BA swap rejudgment complete ===")
        elif args.mode == "pairwise-swap":
            whitelist = _parse_pair_whitelist(args.pairs) if args.pairs else None
            pairwise_swap_rejudge(
                args.tag,
                args.pilot,
                judges=judges,
                workers=args.workers,
                pair_whitelist=whitelist,
                allow_partial=args.allow_partial,
            )
        elif args.mode == "same-orientation-rejudge":
            whitelist = _parse_pair_whitelist(args.pairs) if args.pairs else None
            pairwise_same_orientation_rejudge(
                args.tag,
                args.pilot,
                judges=judges,
                workers=args.workers,
                pair_whitelist=whitelist,
                allow_partial=args.allow_partial,
            )
        else:  # ternary-sample
            whitelist = _parse_pair_whitelist(args.pairs) if args.pairs else None
            pairwise_ternary_sample(
                args.tag,
                args.pilot,
                judges=judges,
                workers=args.workers,
                pair_whitelist=whitelist,
                allow_partial=args.allow_partial,
            )
    except StageIncompleteError as e:
        # Exit nonzero so `set -euo pipefail` drivers stop here rather than
        # feeding an unbalanced matrix to analysis.
        print(f"\nSTAGE INCOMPLETE: {e}")
        raise SystemExit(2) from e


if __name__ == "__main__":
    main()
