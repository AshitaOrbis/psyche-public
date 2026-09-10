# Psyche — Psychometric Persona Profiling Framework

Open-source framework for constructing reliable personality profiles by triangulating validated psychometric instruments with LLM-based text analysis.

## Stack

| Component | Technology |
|-----------|-----------|
| Web App | React 19, TypeScript, Vite 6, Zustand, Recharts |
| Report Generation | GPT-5.6 Luna via OpenRouter (production, since 2026-08-05), prompt in `psyche.ts` |
| Analysis | Python 3.12, Anthropic SDK, Empath, HuggingFace (optional) |
| Package Mgr | pnpm (web), uv (analysis) |
| Testing | Vitest (web), pytest (analysis) |
| Benchmark | Python 3.12, OpenAI SDK (DeepInfra), dual-judge (Opus + GPT-5.4) |

## Commands

```bash
# Web app
cd web && pnpm dev          # Dev server
cd web && pnpm test         # Run tests
cd web && pnpm typecheck    # Type check

# Analysis
cd analysis && uv run psyche ingest all     # Ingest corpus
cd analysis && uv run psyche analyze all    # Run analysis
cd analysis && uv run psyche synthesize     # Merge into profile
cd analysis && uv run psyche report         # Generate narrative
```

## Model Versioning — psycheeval runs (IMPORTANT)

The `opus` CLI alias is **rolling**: as of 2026-06 it resolves to **Opus 4.8**, but the
v0.3 eval corpus (and every prior `psycheeval` run) was generated on **Opus 4.7**.
Continuing runs through the alias silently mixes two model versions in one dataset.

- **Pin Opus 4.7 explicitly for all eval calls** — use the full id `claude-opus-4-7`
  (verified still available 2026-06-16), never the bare `opus` alias.
  - Interactive: `claude --model claude-opus-4-7`
  - Headless run: `claude -p --model claude-opus-4-7`
- **Harness:** `src/psycheeval/llm.py` → `MODELS["opus"].resolved_id` is still `"opus"`
  (so it calls `claude -p --model opus` → 4.8). Pin it to `"claude-opus-4-7"` before
  resuming the v0.3 judge/author runs, so new outputs match the existing corpus.
- Driving this orchestrator session on 4.8 (1M ctx) is fine — only the **eval `claude -p`
  calls** must stay on 4.7.

## Architecture

### Web App (web/)
- **Instrument Engine**: Config-driven instrument definitions with generic scoring
- **Test Runner**: Single-item display, keyboard shortcuts (1-7 for Likert, T/F for binary), progress tracking
- **State**: Zustand with localStorage persistence; full JSON export/import
- **Registry**: Central instrument registry with scoring functions

### Analysis Pipeline (analysis/)
- **Corpus Parsers**: ChatGPT, Claude.ai, SMS, academic writing, Facebook
- **Methods**: LLM inference (Claude + GPT), HuggingFace, Empath, GPV values
- **Synthesis**: Weighted merge, confidence intervals, narrative generation

### Profile Schema (v4)
- Structured JSON with scores from all methods
- Confidence intervals per trait
- Extended battery: attachment, emotion regulation, empathy, self-monitoring, LOC, grit, RIASEC, BPNS, HEXACO
- Phase 4 battery: wellbeing, self-compassion, mindfulness, moral foundations, perfectionism, self-control, curiosity, authenticity, time perspective, decision style
- InstrumentManifest tracks tier and all instruments used
- Persona model: structured behavioral patterns for AI agent simulation
- Human-readable narrative report (2000-4000 words)
- Behavioral CLAUDE.md snippet (~400-600 words, if-then patterns not trait labels)

## Report Generation (Psyche Public)

Production report generation at `app.ashitaorbis.com/psyche` uses **GPT-5.6 Luna** via OpenRouter (owner ruling 2026-08-05; previously Kimi K2.5 via DeepInfra, and before that DeepSeek V3). The system prompt includes a safety clause, at prompt version 1.3.0 since the public battery became PHQ-8 on 2026-08-11.

| Component | Location |
|-----------|----------|
| Production prompt + API call | `applications/ashitaorbis/api/src/routes/psyche.ts` |
| Benchmark prompt (must stay in sync) | `benchmark/run_eval.py` SYSTEM_PROMPT constant |
| 7-model benchmark report | `benchmark/report.md` |
| Synthetic stress tests | `benchmark/synthetic/summary.md` |
| Safety clause history | `docs/EVOLUTION.md` Phase 5 |

**When modifying the system prompt**: Update both `psyche.ts` and `run_eval.py` SYSTEM_PROMPT, then re-run `benchmark/run_eval.py --phase=prepare` to regenerate `prepared_input.json`.

## Key Design Decisions

- **Instruments are config, not code**: Each instrument is a data definition + scoring function registered at import time
- **Scoring is generic**: `scoreLikert()` handles reverse scoring, normalization for any Likert instrument; `scoreBinary()` for True/False instruments
- **Privacy first**: `profiles/` and `data/raw/` are gitignored; no corpus data leaves the machine except via explicit LLM API calls
- **Methods are independent**: Each analysis method produces scores independently; synthesis merges them with reliability weighting

## Instrument Battery (Tiered)

Three assessment tiers with increasing depth. Tiers are additive with replacement logic — higher tiers substitute longer-form instruments for their shorter counterparts.

| | Lite (~260 items) | Standard (~590 items) | Heavy (~1,130+ items + CAT) |
|---|---|---|---|
| **Big Five** | IPIP-NEO-60 (60) | IPIP-NEO-300 (300) | IPIP-NEO-120 + IPIP-NEO-300 |
| **HEXACO** | — | HEXACO-60 (60) | HEXACO-200 (200) |
| **Extended** | Full battery (see below) | + SWLS, AAQ-II, Dweck ITIS, CEI-II | + Grit-O, BPNS-21, Levenson IPC-24, Snyder SM-25, + 10 heavy instruments |
| **CAT** | — | — | Big Five + HEXACO adaptive refinement (~40-60 items) |
| **Interview** | Full 10-question | Full 10-question | Full 10-question |

### Extended Battery (shared across tiers, with Heavy upgrades)

| # | Instrument | Items | Format | Measures | Heavy Replacement |
|---|-----------|-------|--------|----------|-------------------|
| 1 | CRT-7 | 7 | Numeric | Analytical thinking | — |
| 2 | NCS-18 | 18 | 5-pt Likert | Need for Cognition | — |
| 3 | Rosenberg | 10 | 4-pt Likert | Self-esteem | — |
| 4 | SD3 | 27 | 5-pt Likert | Dark Triad | — |
| 5 | PHQ-8 + GAD-7 | 15 | 4-pt Likert | Depression/anxiety | PHQ-9 + GAD-7 (16) — private battery only |
| 6 | ECR-R | 36 | 7-pt Likert | Attachment | — |
| 7 | ERQ-10 | 10 | 7-pt Likert | Emotion regulation | — |
| 8 | IRI-28 | 28 | 5-pt Likert | Empathy (4 dims) | — |
| 9 | Self-Monitoring-18 | 18 | True/False | Social flexibility | Snyder SM-25 (25) |
| 10 | LOC IE-4 | 4 | 5-pt Likert | Locus of control | Levenson IPC-24 (24) |
| 11 | Grit-S | 8 | 5-pt Likert | Perseverance + Interest | Grit-O (12) |
| 12 | RIASEC-48 | 48 | 5-pt Likert | Vocational interests | — |
| 13 | BPNS-9 | 9 | 7-pt Likert | Basic needs | BPNS-21 (21) |
| 14 | Open-Ended | 10 | Free text | Interview | — |

Total registered instruments: 39 (17 original + 6 tier + 2 CAT + 14 extended)

## Research Audit Trail

Analysis results feed a working paper (`shared/content/research/convergent-personality-assessment.md`). Maintain a clean audit trail:

### Archive Convention

**NEVER overwrite or delete analysis results.** Before re-running any analysis:

1. Archive current results to `profiles/analysis/archive/YYYY-MM-DD-{reason}/`
2. Write a `MANIFEST.md` in the archive directory documenting:
   - Date and reason for archival
   - What changed (bug fix, parameter change, new data)
   - Impact assessment (which scores changed, by how much)
   - Files included
3. Cross-reference related archives (e.g., a narrative fix archive should reference the original corpus archive if the same bug applied)

### claude-context.md history (permanent)

Separate from the `profiles/analysis/archive/` dated-run convention,
`profiles/archive/claude-context/` maintains a **permanent timestamped
history** of every generation of the behavioral-specification snippet
imported into every Claude Code session via `~/.claude/CLAUDE.md`.

Convention: one file per generation, named `YYYY-MM-DD-<method>-<model>.md`
(e.g., `2026-04-18-llm-opus-4.7.md`). `profiles/claude-context.md` is a
copy of the most recent generation. Never overwrite a file in this
directory; always add a new one. `INDEX.md` in that directory lists each
generation with byte count, method, model, and key notes.

Regenerate via `analysis/scripts/regen_claude_context.py` (writes to a
`.candidate.md` first, privacy-checks, then prints promotion commands).
Core module: `analysis/psyche_analysis/synthesis/narrative_llm.py`.

### Result Provenance

Every analysis output JSON should be self-documenting. At minimum, the output must record:
- Model used (full model ID or CLI shortname)
- Words analyzed (after all sampling/chunking, not total corpus size)
- Total corpus words (so the sampling ratio is visible)
- Number of samples / chunks
- Timestamp of analysis run
- Any truncation or sampling that occurred

### Data Integrity Issue — RESOLVED (2026-03-04)

The truncation bug in `prepare_text_chunks()` has been fixed. The pipeline now segments long samples into ~2,000-word units at word boundaries (preserving all content) and uses source-stratified round-robin chunking. The expanded corpus analysis (5 sources, 1.47M words, 13 analysis levels) is complete. See `profiles/analysis/archive/2026-03-03-pre-chunking-fix/MANIFEST.md` for the pre-fix archive and `BACKLOG.md` for the full resolution summary. Research paper updated to v2 with corrected scores.

## Development Chronicle

Major development phases are documented in `docs/EVOLUTION.md`. When adding instruments, changing scoring, modifying synthesis weights, or altering the profile schema:

1. Update `docs/EVOLUTION.md` with a new phase section documenting what changed, why, and design decisions
2. Create a git tag: `v{schema_version}.0-{descriptive-name}`
3. Note any published content that references the pre-change state
4. Update instrument counts in: README.md, CLAUDE.md battery table, docs/VALIDATION-DESIGN.md, profiles/claude-context.md

## Corpus Sources

| Source | Format | Location | Words |
|--------|--------|----------|-------|
| SMS | JSONL | data/raw/sms -> symlink | 401K |
| Facebook Messenger | JSONL | data/raw/facebook -> symlink | 413K |
| ChatGPT | JSON tree | data/raw/chatgpt -> symlink | 333K |
| Claude.ai | JSON array | data/raw/claude-ai -> symlink | 167K |
| Academic Writing | Markdown | data/raw/academic -> symlink | 151K |

Total: ~1.47M words across 5 sources, ~62K samples. Analysis output: `profiles/analysis/corpus/`.
