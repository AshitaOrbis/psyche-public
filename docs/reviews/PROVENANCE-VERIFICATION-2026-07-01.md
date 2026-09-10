# Model Provenance Verification & Fix — 2026-07-01

Companion to `context-contamination-audit-2026-06-09.md`. That audit closed a
*context*-leak in `claude -p` blind calls. This note closes a *model-identity*
observability gap in the same call path, found while verifying which model
generated the June 2026 Fable review material.

## The gap

Blind scoring runs invoke `claude -p --safe-mode --model <alias>`
(`analysis/scripts/analyze_corpus.py`). Claude Code's harness can silently
substitute a fallback model mid-call — e.g. a `model_refusal_fallback` swaps a
model whose safety filter trips for a different one, which then produces the
whole response. The pipeline recorded only the **requested alias**
(`isolation.py` stored the CLI alias; nothing captured the resolved id), so a
substitution left no trace in the output JSON. The runtime banner and session
labels also report the requested model, not the substitute — per-message
`"model"` stamps in the session JSONL transcripts are the only ground truth.

Concretely, in the 2026-06-10 Phase 1 blind Fable re-derivation, **5 of 48
blind-scoring calls silently ran on the fallback model** while every run JSON
recorded `"model": "fable"`. Run-specific mapping and impact live with the
(repo-ignored) data at `profiles/analysis/corpus/DATA-QUALITY-2026-07-01.md`;
the recorded conclusions were assessed there and none were overturned.

## The fix

`analysis/psyche_analysis/isolation.py` and
`analysis/scripts/analyze_corpus.py`:

- `call_claude_isolated()` now runs with `--output-format json` and reads the
  envelope's `modelUsage` map, which is keyed by the **resolved** full model
  id(s) that actually billed tokens. A fallback surfaces as an unrequested id
  (or an extra id) in that map.
- An optional `capture` dict returns per-call `requested_model`,
  `resolved_models`, `fallback_detected`, and `session_id` without changing the
  function's text return value (backward compatible with all existing callers).
- `run_level()` folds these across a run into the output provenance:
  `resolved_models`, `fallback_detected`, `llm_calls`, and
  `llm_calls_with_fallback`.

A silent model substitution can no longer pass unrecorded: any future run JSON
whose `fallback_detected` is true is flagged at the source.

## Verification

- `pytest` (analysis suite) green after the change.
- `_call_provenance()` unit-checked against clean, single-model-fallback, and
  dual-model-billed envelopes.
- Live `claude -p --output-format json` call confirmed `modelUsage` is keyed by
  the resolved id and that the `capture` dict is populated end-to-end.
