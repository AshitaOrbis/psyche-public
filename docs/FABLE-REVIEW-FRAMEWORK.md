# Fable Review Framework

A structured protocol for re-running the Psyche profiling program through Fable 5 (`claude-fable-5`), designed 2026-06-09. Goal: produce insights the prior Opus-generation review passes structurally could not, while fixing the methodological hole they shared (see `reviews/context-contamination-audit-2026-06-09.md`).

## Why a new framework instead of re-running the old pipeline

Four classes of prior Opus review work exist, each with a distinct ceiling:

| Prior pass | Artifact | Structural limit |
|---|---|---|
| Corpus scoring (Opus 4.6) | `profiles/analysis/llm-claude.json` | Scoring-shaped: numbers + quotes inside the Big Five/Schwartz ontology; no interpretation |
| Narrative report (Opus, 2026-03-06) | `profiles/report.md` | Downstream synthesis of already-merged scores — can decorate the profile, cannot disagree with it |
| Behavioral spec generations (Opus 4.7, 1M ctx) | `profiles/claude-context.md` + archive | Output-constrained to actionable directives; insight incidental |
| Critical methodology review (Opus 4.6) | `experiments/1m-context-narrative/critical_review_opus.md` | Scoped to one experiment, not the person-model or pipeline at large |

The shared gaps: **no pass was ever licensed to challenge the standing profile against raw evidence**, no pass looked **outside the instruments' ontology**, every estimate was a **single run** (no error bars), and every Claude-CLI evaluative pass was **non-blind** (context contamination).

## Execution decisions (locked 2026-06-09)

1. **No retroactive Opus re-runs.** Fable runs are the fresh data; isolation is now enforced at every call site.
2. **Phase 3 is interactive** — run by Fable inside Claude Code sessions in this project directory, with the owner able to correct/redirect (this is how the highest-value prior insight, the empathy-channel correction, actually emerged).
3. **The framework ends with a Fable generation of `claude-context.md`**, archived per `profiles/archive/claude-context/INDEX.md` lineage convention.

## Isolation protocol (applies to every blind phase)

- All blind calls go through `psyche_analysis.isolation.call_claude_isolated()` — `claude -p --safe-mode`, neutral cwd. (`--bare` refuses Max-plan OAuth; `--safe-mode` authenticates and strips all CLAUDE.md/memory/skills/hooks.)
- One `verify_isolation()` canary precedes each batch; it must answer NO. The canary is a real detector: it answers YES through a non-isolated invocation (verified both directions 2026-06-09).
- Residual accepted leakage: user email + current date (no trait information).
- Output JSON from isolated runs embeds `isolation_provenance()`.
- In-session Fable subagents (Agent tool) are **never** used for blind work — they inherit the project context, including the profile. They are fine for non-blind interpretive work.

## Phases

### Phase 0 — Decontamination + provenance baseline ✅ (completed 2026-06-09)

- Contamination audit written: `docs/reviews/context-contamination-audit-2026-06-09.md`
- `isolation.py` module created; all four evaluative call sites patched; canary verified in both directions
- `analyze_corpus.py` gained `--run-id` (repeat runs without overwriting) and model-derived method ids (`--model fable` → saves as `llm-fable`)

### Phase 1 — Blind re-derivation (`llm-fable`)

Fable scores the corpus with zero profile knowledge, matching the canonical run's chunking for comparability.

```bash
cd analysis
uv run python scripts/analyze_corpus.py --level full --model fable --skip-empath --run-id 1
uv run python scripts/analyze_corpus.py --level full --model fable --skip-empath --run-id 2
uv run python scripts/analyze_corpus.py --level full --model fable --skip-empath --run-id 3
```

- Outputs: `profiles/analysis/corpus/full-llm-fable-run{1,2,3}.json` (canonical `llm-claude.json` untouched, per archive convention)
- **3 runs minimum** — the single-run/no-error-bars criticism from the Opus critical review applies to all prior estimates
- Analysis deliverable: per-domain mean ± range across runs; deltas vs `llm-claude.json` (Opus, mildly contaminated) and vs self-report/interview. Doubles as the model-robustness comparison the research paper has had on backlog
- Optional secondary condition: source-level runs (e.g. `sms`, `ai`, `academic`) to test whether the source-effects findings replicate under Fable

### Phase 2 — Adversarial claim audit

Decompose the standing interpretive artifacts into discrete claims; adjudicate each against raw evidence.

1. **Extraction** (in-session, non-blind): pull every distinct empirical/interpretive claim from `profiles/report.md`, `profiles/claude-context.md`, and the profile-insights memory layer into `profiles/fable-review/<date>/claims.json`. Expected ~60–100 claims. Schema per claim: `id`, `source_artifact`, `claim_text`, `claim_type` (score | mechanism | behavioral-prediction | interpretive-frame), `depends_on_scores`.
2. **Evidence bundling**: for each claim, assemble the relevant raw material (corpus excerpts via search, interview segments, instrument scores it depends on).
3. **Adjudication** (isolated, batched): Fable receives claim + evidence bundle — *not* the rest of the profile — and returns verdict `confirm | refute | refine | insufficient-evidence`, with quotes, confidence, and (for `refine`) the corrected formulation.
4. Deliverable: verdict table + a "contested claims" shortlist for Phase 3 discussion.

User-corrections from prior sessions (e.g. the empathy-channel correction) are treated as claims like any other — they get audited, not assumed.

### Phase 3 — Open-ended insight hunt (centerpiece, interactive)

Full-context, non-blind, run by Fable in interactive sessions from this directory. Prompt philosophy follows the trust-framing lesson from `profiles/archive/claude-context/INDEX.md`: describe the situation and license judgment; do not enumerate rules — rigid prescription measurably narrowed Opus 4.7's output.

Standing instructions for the hunt:

- **License to leave the ontology.** The 39-instrument battery defines what was *measured*, not what is *true*. Propose constructs, mechanisms, and patterns the battery has no scale for.
- **The temporal axis is non-negotiable.** The corpus spans 2008-2026; the review must treat its documented life-phase boundaries as real structure rather than a flat bag of text. _(The specific boundaries, including a health-category one, are withheld here and live with the private profile — they are not publishable context.)_
- **Method-divergence points are drill sites, not noise.** Self-report vs corpus vs interview disagreements (largest: Agreeableness) are where the most informative structure lives.
- **Every insight must pass the actionability-or-falsifiability test**: statement + supporting evidence (quoted) + confidence estimate + at least one falsifiable behavioral prediction or observable consequence. Insights failing the test are discussion notes, not findings.
- **Disagreement with the standing profile is in-scope and expected.** The profile's interpretive layer (including its framing metaphors) is input to be tested, not ground truth.

Deliverable: `profiles/fable-review/<date>/insights.md` — each insight tagged `extends | tensions-with | replaces | novel` relative to the standing profile.

### Phase 4 — Synthesis

1. **Fable review report**: `profiles/fable-review/<date>/report.md` — integrates Phase 1 deltas, Phase 2 verdicts, Phase 3 insights. Does **not** replace `profiles/report.md`; it sits beside it as a second-generation review.
2. **Profile/synthesis updates**: any Phase 2 `refute`/`refine` verdicts the owner accepts get applied to the canonical profile with the standard archive-first convention (`profiles/analysis/archive/<date>-fable-review/MANIFEST.md`).
3. **Behavioral spec regen**: `uv run --with anthropic python scripts/regen_claude_context.py fable` → candidate → privacy + anti-pattern checks → owner promotes → new row in `profiles/archive/claude-context/INDEX.md` as the first Fable-generation entry.
4. **Paper hooks**: Phase 1 = model-robustness section; Phase 0 = methods correction note; Phase 2/3 = discussion material.

## State tracking

`profiles/fable-review/state.json` — phase status, run ids completed, decisions taken. Sessions resume from it. (Created on first Phase 1 run.)

## Provenance & archival rules (inherited, restated)

- Never overwrite or delete prior results; Fable outputs are a new method layer (`llm-fable`), not a replacement for `llm-claude`
- Every output JSON self-documents: model, isolation, words analyzed, sampling ratio, timestamp, run id
- `profiles/` remains gitignored; nothing in this framework changes what leaves the machine
- The standing "use Opus for corpus analysis" convention is explicitly superseded for this framework by owner decision (2026-06-09); Opus-era results remain the archived baseline
