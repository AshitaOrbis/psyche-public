# Context Contamination Audit — CLAUDE.md Profile Leakage into "Blind" Evaluations

**Date**: 2026-06-09
**Discovered by**: Fable 5 (Claude Code), during reconnaissance for the Fable Review Framework
**Status**: Confirmed empirically; forward fix deployed; no retroactive re-runs (superseded by Fable re-derivation — see Remediation Decision)

---

## Summary

Every evaluative `claude -p` invocation made by this project before 2026-06-09 ran **non-blind**: the Claude Code harness silently injected the subject's psychometric profile — including ground-truth trait scores — into the model's context via `~/.claude/CLAUDE.md` memory loading. Evaluations that were designed as blind personality inference (narrative scoring, psycheeval judging) therefore had the answer key in context.

The `codex exec` (GPT) backend and the OpenAI-SDK/DeepInfra paths were never affected, so an uncontaminated comparison arm exists in the historical data.

## Mechanism

1. `claude -p` is not a raw model call. By default it boots the full Claude Code harness, which loads `~/.claude/CLAUDE.md` (global user memory) into context — the same as an interactive session.
2. Since at least **2026-02-27** (earliest snapshot in the `~/.claude` config git history; the import predates the repo), the global CLAUDE.md has contained a "User Profile" section importing `psyche/profiles/claude-context.md` — the subject's full behavioral specification, which after 2026-03-09 includes explicit trait scores, score discrepancies, and interpretive findings.
3. None of the project's CLI call sites passed an isolation flag:
   - `analysis/scripts/analyze_corpus.py` — `--system-prompt` only (replaces the system prompt; does **not** suppress memory injection)
   - `analysis/scripts/analyze_narratives.py` — same pattern
   - `psycheeval/src/psycheeval/llm.py` — completely bare `claude -p --model opus`
   - `benchmark/run_eval.py` — bare invocation for both candidate generation and Opus judging

## Empirical Verification (2026-06-09)

- A canary call through the exact pre-fix invocation pattern (cwd = `psyche/analysis`, `--system-prompt` set) answered **YES** and quoted the profile's interpersonal-pattern passage and the Agreeableness self-report/corpus discrepancy figures verbatim.
- The same canary through `claude -p --safe-mode` from a neutral cwd answered **NO** (residual context: user email + current date only — neither carries trait information).
- Negative control retained as a test: the canary must FAIL through a non-isolated call and PASS through the isolated path. Both confirmed.

## Blast Radius

| Run class | Date(s) | Contamination | Severity |
|---|---|---|---|
| Canonical corpus analysis (`profiles/analysis/llm-claude.json`, provenance `claude-opus-via-claude-cli`) | 2026-03-04 | Profile-derived preference bullets in CLAUDE.md; the full spec import was likely dangling (claude-context.md first generated 2026-03-09) | **Mild** — trait-suggestive characterizations, no scores |
| Narrative scoring runs incl. the 24-run Opus batch (`run_opus_batch.sh`) and the 1M-context experiment evaluations | post-2026-03-09 | Full profile incl. exact ground-truth Big Five scores | **High** — evaluator scoring narratives against ground truth could see the ground truth |
| psycheeval v0.2/v0.3 Opus judging | 2026-05/06 | Full profile of the subject, while judging *synthetic* personas, none of them the subject | **Low–moderate** — bias vector, not an answer key (corrected 2026-08-03, see note below) |
| Benchmark Opus judge + Opus candidate generation (mostly synthetic profiles) | 2026-03 | Full profile of the subject, while judging/generating for *other* profiles | **Low–moderate** — bias vector, not an answer key |
| claude-context regen, narrative report generation | various | Profile in context | **None** — these are non-blind by design; the profile is their explicit input |
| All `codex exec` (GPT-5.4) runs; all OpenAI-SDK/DeepInfra calls | all | None — these paths load no CLAUDE.md | **Clean** |

## Implications for Existing Conclusions

1. **1M-context narrative experiment**: the headline calibration finding (new pipeline's N estimate landing within ~4 points of ground truth vs the old pipeline's ~24-point miss) is confounded by anchoring — the Opus evaluator could see the ground-truth value while scoring. The Opus critical review of 2026-03-16 identified four confounds (architecture, model version, word count, evaluator–generator overlap) but missed this fifth. The clean GPT-5.4 evaluation arm in the same experiment partially survives; any future use of the Opus numbers must carry this caveat.
2. **psycheeval v0.2/v0.3**: Opus-judge results are non-blind; codex-judge results are clean. Cross-judge agreement statistics computed across the two arms mix a contaminated and a clean judge. **Severity corrected 2026-08-03 from High to Low–moderate** per the 2026-07-27 psyche presentation ruling (item 5): psycheeval scores only synthetic personas — 50 `pure_synthetic`/`fully_synthetic` seeds in `psycheeval/data/seed_bank_pure_synthetic.jsonl` plus 46 `public_inspired` ones in `seed_bank_public_inspired.jsonl` disclosed as "fictionalized public-figure-inspired synthetic user; not the real person" — none of which is the subject, and no psycheeval prompt or dataset embeds the subject's profile, so the leaked scores are not an answer key for anything these runs judge. That is structurally the same case as the benchmark row above, which this audit already graded Low–moderate for exactly that reason; grading the two rows differently was an internal inconsistency, and the review findings that inherited the High rating (Sol's F16/F-046) inherit the correction with it. The mixed-arm agreement statistic is unaffected — that problem is about combining a contaminated judge with a clean one, whatever the contamination's severity.
3. **Canonical corpus scores** (`llm-claude.json`): mildly affected. The Big Five/values scores were inferred with profile-derived preference text (not scores) in context. Treat the published LLM-method scores as having a small unquantified anchoring risk.
4. **Research paper**: the methods section's blindness claim ("blind inference without self-report data") needs a correction note wherever it covers Claude-CLI-backed runs.

## Remediation Decision (2026-06-09)

Per the project owner: **no retroactive Opus re-runs.** The planned Fable 5 re-derivation (Fable Review Framework, Phase 1) supersedes them — it re-derives corpus scores under verified isolation, with multiple runs for error bars. This audit document plus call-site comments serve as the permanent record. The historical results remain archived untouched per the project's archive-don't-delete convention.

## Forward Protocol (deployed 2026-06-09)

- New module `analysis/psyche_analysis/isolation.py`: `call_claude_isolated()` (uses `--safe-mode` + neutral cwd; `--bare` is unusable on the Max plan because it refuses OAuth), `verify_isolation()` canary, `isolation_provenance()` fragment for output JSON.
- Patched to isolated invocation: `analyze_corpus.py` (+ canary before each LLM batch, + `isolation` provenance fields, + `--run-id`), `analyze_narratives.py`, `psycheeval/llm.py`, `benchmark/run_eval.py` (both Opus call sites).
- Intentionally NOT isolated: `narrative_llm.py` / `regen_claude_context.py` (the profile is their explicit input).
- Every isolated batch must be preceded by one `verify_isolation()` call; every output JSON from isolated runs must embed `isolation_provenance()`.
