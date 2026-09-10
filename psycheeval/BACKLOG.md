# PsycheEval Backlog

Deferred items and future work.

## ~~Hardening — judge cap-burn problem (P1)~~ — RESOLVED 2026-05-05

Resolved via Phase 0.1 of the v0.2 extended plan. Cap-burn handler at
`src/psycheeval/cap_burn.py`. `ClaudeCapError` raised from `llm.py` when
stderr matches one of 17 cap markers; `judge.py` wraps each call in
`CapBurnHandler.call_with_backoff` (exponential 60→300→900→1800→3600s,
max 5 attempts). Peer workers see `is_cap_aborted()` and bail without
further calls once retries are exhausted. Cap events go to
`cap_events.jsonl` (separate from `validation_warnings.jsonl`). Resume
checkpoint at `checkpoint_<phase>.json`. 19 tests in
`tests/test_cap_burn.py` exercise the protective behaviors.

## Active runbooks (read these first if returning from a session boundary)

- **`docs/v0_2_plan_extended_2026-05-05.md`** — the canonical v0.2 plan as of 2026-05-05. Locks 7 decisions (D1–D7), maps phases, sequencing, cost estimates, and risk register. Supersedes the older codex-only `docs/v0.2_plan.md` (kept for archival).
- **`reports/backlog/v02_deferred_pairwise_edges.json`** — D2 deferred-edges manifest (machine-readable). Backfillable in v0.3 without redesigning the experiment.
- **`docs/runbook_codex_only.md`** — codex-only pipeline state (P2–P5).
- **`docs/tri_model_extension_plan.md`** — the brief that started the tri-model + GPT-5.5 work.
- **`docs/v0.2_plan.md`** — original v0.2 hard-pilot plan from 2026-04-24 (codex-only era; superseded by extended plan above but kept for context).

## v0.2 execution status (2026-05-05)

Per `docs/v0_2_plan_extended_2026-05-05.md`. 7 decisions locked at planning time. Phase 0 (cap-burn fix + native analyzer port + tests) complete; 87/87 tests green. Phase 1 codex-side and Phase 2 Opus-side launched in parallel background runs at 2026-05-05 23:52.

**Phase 1 codex-side** (driver: `drivers/phase1_codex_pipeline.sh`):
- 1.5 generation: in progress (80 C5_CONTRACT outputs, 4 PI × 10 scenarios × 2 codex authors)
- 1.6 codex anchored scoring: queued behind 1.5
- 1.7 codex pairwise (restricted to {C3, C4, C5} per D2): queued behind 1.6

**Phase 2 Opus authoring** (`drivers/phase3_opus_judging_pipeline.sh` queued behind it):
- ~600 outputs needed (8 personas × 6 conditions × 10 scenarios + 4 PI × 2 PI-only × 10) — codex side existing leaves Opus author work as the gap
- Cap-burn-protected at workers=1
- Resume-safe via existing `(scenario_id, condition, output_model)` dedup

**Phase 3 Opus judging**: queued behind Phase 2.

## v0.2 implementation status (2026-04-24, original plan)

Per `docs/report_revision_brief.md` the user chose "Document + implement + run v0.2 now." Implementation is complete; execution waits on v0.1 pairwise quota window. See `docs/v0.2_plan.md` for the full pipeline.

**Complete (code/data):**

- [x] Length-control conditions `C1_padded` and `C4_shuffled` (programmatic, no LLM cost)
- [x] Anchored 0–10 judge rubric (`prompts/06b_judge_anchored.md`)
- [x] Extended red-flag taxonomy (`RedFlag` enum +6 labels per brief §21)
- [x] Harder scenarios seed file (`data/v02_hard_scenarios_seed.jsonl`, 10 entries per brief §17)
- [x] v0.2 pilot data pipeline (`psycheeval.v02_prepare` CLI, materializes 80 scenarios + 8 bundles)
- [x] Per-pilot condition routing (`config.conditions_for()`, `run.py` generalization)
- [x] Parallel execution (ThreadPoolExecutor) in `run.py` and `judge.py` (`--workers N`)
- [x] Rubric switch in `judge.py` (`--rubric anchored`, writes to `anchored_judge_scores.jsonl`)
- [x] Data models for anchored scores (`AnchoredJudgeScore`, `JudgeScoresAnchored`)

**Pending (execution + analysis):**

- [ ] Generate 1 040 v0.2 assistant outputs (`psycheeval.run --pilot v02_hard_pilot --workers 4`)
- [ ] Anchored scalar judging (2 080 calls; `--rubric anchored --workers 4`)
- [ ] Pairwise judging on v0.2 (~2 880 calls; `--workers 4`)
- [ ] Extend `analyze.py` to handle `anchored_judge_scores.jsonl` (new score-scale path)
- [ ] Add length-control delta blocks to analysis: C4 − C1_padded, C4 − C4_shuffled
- [ ] Add length-control pair preferences to pairwise block: C1 vs C1_padded, C4 vs C4_shuffled, C1_padded vs C4
- [ ] Write v0.2 report

## v0.1 post-revision cleanup (in progress)

- [x] Cross-provider judging as primary throughout `analyze.py` (brief §3)
- [x] C5 isolated to PI-only subset (brief §4)
- [x] PI-only / PS-only per-condition tables (brief §4)
- [x] All-judge means demoted to appendix (brief §3)
- [x] Curated report rewritten with brief's narrative sections, reframings, and v0.2 plan pointer
- [x] Pre-revision snapshot archived at `reports/archive/v0.1-pre-brief-revision/`
- [x] Pairwise prompt fix (controlled vocabulary for `red_flags_A`/`red_flags_B`)
- [x] Defensive `_coerce_red_flags` in `judge.py` (no-op on invalid labels)
- [ ] Regenerate v0.1 curated report once pairwise completes (to fill the "pending regeneration" section)

## v0.2 candidates extended (from brief §21–§27)

- [ ] One repeat run with different seeds to estimate run-to-run noise (brief §25)
- [ ] Small human calibration sample: 20–50 outputs, 2–3 raters, hardest scenario families (brief §18)
- [ ] Kimi K2.5 as third judge for stronger inter-judge agreement stats
- [ ] Calibration packet prepended to judge prompts (already partly addressed by anchored rubric; consider adding 3–5 worked examples inside the prompt)
- [ ] Umbrella framing paragraph connecting PsycheEval to "context disciplines for AI" (brief §27) — user said not needed for private-notes posture

## Before any public release (if posture changes)

- [ ] Ethics review section in README — who to credit, disclaimer on public-inspired aliases
- [ ] Dataset card (kit §18 template) populated for the micro-pilot
- [ ] Second-pass naming review for all aliases before any public artifact (kit §23)
- [x] Inter-judge agreement metrics implemented (pse-2): Cohen's κ on red flags + Spearman ρ on dimension scores via `compute_inter_judge_agreement` in `analyze.py`, wired into `compute_metrics` (`inter_judge_agreement_legacy`/`_anchored`) and now **surfaced in the markdown report** ("Inter-judge agreement — Cohen's κ + Spearman ρ" section in `write_report`); the κ block had been JSON-only. Tests: `tests/test_tri_model.py`, report-render assertion in `tests/test_analyzer_smoke.py`.
- [x] Halo-audit metric formalized and auto-emitted in analysis report (done in cross-provider structure; κ stats now surfaced — see above).

## Deferred from v0.1 design

- [ ] "Bad profile" condition — deliberately mis-specified profile to test whether the model can detect and override personalization errors. Would strengthen the "profile actually helps" claim by showing dose-response. (Plan §6.1)
- [ ] Publication venue decision — user chose "private notes" for v0.1. Revisit if v0.2 results warrant external publication.
- [ ] Multi-turn scenarios (brief §28 / plan §6.4) — real conversations aren't one-shot.
- [ ] Real Psyche profile closure — feed an actual Psyche-generated profile through the same scenario matrix.

## Infrastructure

- [x] CLI tests — typer app smoke tests (pse-3): `tests/test_cli.py` (14 tests) — `--help` for app + every subcommand, no-args-is-help, and dispatch tests for `judge-score`/`judge-pairwise`/`run` with mocked module functions (no network).
- [x] Cost tracking per run — track tokens in/out per call, aggregate in run manifest (pse-4): `tokens_in`/`tokens_out` added to `JudgeScore`/`AnchoredJudgeScore`/`PairwiseScore` (populated in `judge.py`); new `src/psycheeval/cost.py` aggregates author + judge tokens by phase and model, computes per-token dollar cost (priced models only; CLI-billed flagged unpriced), writes `runs/<tag>/cost_summary.json`. Wired into `run.py`/`judge.py` end-of-phase + a `psycheeval cost <tag>` CLI command. Tests: `tests/test_cost.py`.
- [ ] Deferred Opus review for DeepSeek V4 Pro author/judge runs — keep Opus out of default judge sets while Claude limits are tight; run explicit `--judges opus` jobs only as a backlog slice when quota is available.
- [x] Caching layer for persona seeds + user records — done (v0.2 reuses v0.1 seeds/records without re-generation)
- [x] Resume-on-failure for run.py and judge.py — partial runs don't lose work (de-dupe on key tuple)

## Documentation

- [x] KIT_PROVENANCE.md — what was copied verbatim from the kickstart kit vs what was adapted (pse-5): `docs/KIT_PROVENANCE.md` created (README already referenced it). Per-prompt verbatim/new status, schemas (pydantic-exported, kit §3-derived), seed banks, conditions (micro/v0.2/v0.3), scoring rubric, all code as workspace-authored.
- [ ] Migration note when schemas change — version the JSONL files
- [x] v0.2 plan — `docs/v0.2_plan.md`
- [x] Report revision brief integration — `reports/psycheeval_v0_1_micro_pilot_2026-04-20_micro.md` rewritten
