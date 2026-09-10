"""Per-run cost / token tracking (pse-4).

Aggregates token usage across every phase of a run (author generation +
judging) into a single cost summary written to ``cost_summary.json`` in the
run directory. Token counts come from the per-record ``tokens_in`` /
``tokens_out`` fields populated by ``run.py`` (authors) and ``judge.py``
(judges); dollar estimates use the per-token rates on ``MODELS``.

Notes / caveats:

- Tokens are **best-effort**. The Claude CLI path does not surface token
  counts at all, and the Codex CLI path only scrapes a single (output) count
  from stderr. So author/judge rows using those providers contribute to the
  call count but not (or only partially) to token totals. Only the
  OpenRouter API path returns both prompt and completion tokens reliably.
- Dollar cost is only computed for models that carry ``cost_in_per_mtok`` /
  ``cost_out_per_mtok`` rates (despite the ``_per_mtok`` suffix the stored
  values are **per token**). CLI-billed models (claude/codex, billed against
  a subscription quota rather than per token) have no rates and contribute
  ``null`` cost.
- Resumable / idempotent: rebuilt from the on-disk jsonl each call, so it is
  safe to re-run after partial phases.
"""

from __future__ import annotations

import json
from pathlib import Path

from psycheeval import config
from psycheeval.io import read_jsonl
from psycheeval.llm import MODELS
from psycheeval.models import (
    AnchoredJudgeScore,
    AssistantOutput,
    JudgeScore,
    PairwiseScore,
)

# (filename, pydantic model, phase label, model-id attribute) for every output
# file that carries token counts. Files that don't exist for a given run are
# skipped silently.
_PHASE_FILES: list[tuple[str, type, str, str]] = [
    ("assistant_outputs.jsonl", AssistantOutput, "author", "output_model"),
    ("judge_scores.jsonl", JudgeScore, "judge_legacy", "judge_model"),
    ("anchored_judge_scores.jsonl", AnchoredJudgeScore, "judge_anchored", "judge_model"),
    ("paraphrased_anchored_scores.jsonl", AnchoredJudgeScore, "judge_paraphrased", "judge_model"),
    ("pairwise_scores.jsonl", PairwiseScore, "pairwise", "judge_model"),
    ("pairwise_swap_scores.jsonl", PairwiseScore, "pairwise_swap", "judge_model"),
    ("pairwise_ternary_scores.jsonl", PairwiseScore, "pairwise_ternary", "judge_model"),
    ("same_orientation_swap_scores.jsonl", PairwiseScore, "pairwise_same_orient", "judge_model"),
]


def _rates_for(model_id: str) -> tuple[float | None, float | None]:
    """Per-token (in, out) cost for a resolved-or-key model id, or (None, None).

    Records store ``judge_model`` / ``output_model`` as the resolved id (e.g.
    ``moonshotai/kimi-k2.6``), so match against both the MODELS key and the
    resolved id.
    """
    for spec in MODELS.values():
        if model_id in (spec.key, spec.resolved_id):
            return spec.cost_in_per_mtok, spec.cost_out_per_mtok
    return None, None


def _new_acc() -> dict:
    return {
        "calls": 0,
        "tokens_in": 0,
        "tokens_out": 0,
        "calls_missing_tokens": 0,
        "calls_unpriced": 0,  # model has no per-token rate (e.g. CLI-billed)
        "cost_usd": 0.0,
        "cost_known": False,
    }


def aggregate_run_cost(run_tag: str) -> dict:
    """Build the cost summary for ``run_tag`` from on-disk jsonl. Pure read."""
    run_d = config.run_dir(run_tag)

    by_phase: dict[str, dict] = {}
    by_model: dict[str, dict] = {}

    for filename, model_cls, phase, model_attr in _PHASE_FILES:
        path = run_d / filename
        if not path.exists():
            continue
        for rec in read_jsonl(path, model_cls):
            model_id = getattr(rec, model_attr, None) or "unknown"
            t_in = getattr(rec, "tokens_in", None)
            t_out = getattr(rec, "tokens_out", None)
            cost_in, cost_out = _rates_for(model_id)

            for bucket, key in ((by_phase, phase), (by_model, model_id)):
                acc = bucket.setdefault(key, _new_acc())
                acc["calls"] += 1
                if t_in is None and t_out is None:
                    acc["calls_missing_tokens"] += 1
                acc["tokens_in"] += t_in or 0
                acc["tokens_out"] += t_out or 0
                if cost_in is not None and cost_out is not None:
                    acc["cost_usd"] += (t_in or 0) * cost_in + (t_out or 0) * cost_out
                    acc["cost_known"] = True
                else:
                    acc["calls_unpriced"] += 1

    def _finalize(bucket: dict) -> dict:
        out: dict = {}
        for key, acc in sorted(bucket.items()):
            out[key] = {
                "calls": acc["calls"],
                "tokens_in": acc["tokens_in"],
                "tokens_out": acc["tokens_out"],
                "tokens_total": acc["tokens_in"] + acc["tokens_out"],
                "calls_missing_tokens": acc["calls_missing_tokens"],
                "calls_unpriced": acc["calls_unpriced"],
                # None when no row in this bucket had a priced model.
                "cost_usd": round(acc["cost_usd"], 6) if acc["cost_known"] else None,
            }
        return out

    phases = _finalize(by_phase)
    models = _finalize(by_model)

    total_calls = sum(p["calls"] for p in phases.values())
    total_in = sum(p["tokens_in"] for p in phases.values())
    total_out = sum(p["tokens_out"] for p in phases.values())
    total_unpriced = sum(p["calls_unpriced"] for p in phases.values())
    priced_costs = [p["cost_usd"] for p in phases.values() if p["cost_usd"] is not None]
    total_cost = round(sum(priced_costs), 6) if priced_costs else None

    return {
        "run_tag": run_tag,
        "totals": {
            "calls": total_calls,
            "tokens_in": total_in,
            "tokens_out": total_out,
            "tokens_total": total_in + total_out,
            "calls_unpriced": total_unpriced,
            # None means no priced model appeared at all. cost_is_partial means
            # a dollar total exists but excludes some calls whose model is
            # CLI-billed (no per-token rate), so the figure is a lower bound.
            "cost_usd": total_cost,
            "cost_is_partial": total_cost is not None and total_unpriced > 0,
        },
        "by_phase": phases,
        "by_model": models,
    }


def write_cost_summary(run_tag: str) -> Path:
    """Aggregate and write ``cost_summary.json`` into the run directory."""
    summary = aggregate_run_cost(run_tag)
    run_d = config.run_dir(run_tag)
    run_d.mkdir(parents=True, exist_ok=True)
    out_path = run_d / "cost_summary.json"
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True))
    return out_path
