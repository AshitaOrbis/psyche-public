# PsycheEval

Synthetic-first evaluation of whether personality-derived user profiles
improve AI assistant behavior — especially in psychologically charged
situations where models tend to flatter, over-adapt, or misread the user.

**Status**: v0.1 in development. No results yet. See `PLAN.md`.

## What this is

PsycheEval is a companion benchmark to [Psyche](../). Psyche builds
personality profiles by triangulating validated psychometric instruments
with LLM-based text analysis. PsycheEval asks: are those profiles
load-bearing for downstream AI assistance, or decorative?

The evaluation compares assistant responses under six profile conditions:

| Code | Profile format |
|------|----------------|
| C0 | No profile |
| C1 | Trait-label profile (compact labels + estimates) |
| C2 | Narrative profile (short prose) |
| C3 | Behavioral contract (do/don't/when-X) |
| C4 | Behavioral contract + anti-sycophancy / repair clauses |
| C5 | Source-packet-informed (for public-inspired personas only) |

Two model families act as both output authors and judges: **Claude Opus 4.7**
and **GPT-5.4**. Cross-provider judging is primary; same-provider is
secondary (halo-audited).

Synthetic users come in two types:

- **Public-inspired**: fictional analogues inspired by public figures
  (essayists, founders, researchers). Aliases are deliberately wrong —
  "Slalom Altar", "Dario Armadillo", "Emily Blender" — to signal fiction.
  No fake quotes, no inferred private facts.
- **Pure synthetic**: archetypes designed to create varied evaluation
  pressure — The Calibration Goblin, The Conflict-Allergic Moralist, etc.

## Non-goals

- **Not clinical**: no diagnosis, no severity scoring, no mental-health
  stratification.
- **Not impersonation**: public-inspired personas are fictional analogues.
  No fake quotes. No inferred private facts. No claims that real people
  said generated text.
- **Not a replacement for human evaluation**: synthetic-first is the
  prerequisite to asking humans meaningful questions later, not a shortcut.
- **Not a Psyche deliverable**: Psyche produces profiles. PsycheEval tests
  whether they help downstream. Audit trails are separate.

## Repo layout

```
psycheeval/
├── PLAN.md                # execution plan
├── BACKLOG.md             # deferred work
├── prompts/               # kit §6–§13 prompts, one file each
├── schemas/               # JSON Schema exports
├── data/
│   ├── seed_bank_*.jsonl  # persona seeds
│   ├── source_packets/    # public-inspired anchor material
│   └── micro_pilot/       # generated pilot data
├── runs/YYYY-MM-DD_{tag}/ # assistant_outputs, judge_scores, pairwise_scores
├── reports/               # analysis output
├── src/psycheeval/        # Python package
└── tests/
```

## Quickstart

```bash
cd ~/claudeworkspace/psyche/psycheeval
uv venv
uv pip install -e ".[dev]"
uv run pytest                              # schema + fixture round-trip
uv run psycheeval --help                   # CLI entry point
```

Full pipeline (do not run without budget approval — see PLAN.md §2):

```bash
# Phase 1: data generation
uv run psycheeval source-hunt --pilot micro
uv run psycheeval generate-users --pilot micro
uv run psycheeval compile-profiles --pilot micro
uv run psycheeval generate-scenarios --pilot micro

# Phase 2: run + judge
uv run psycheeval run --pilot micro
uv run psycheeval judge --pilot micro
uv run psycheeval judge --pilot micro --pairwise

# Phase 3: analysis
uv run psycheeval analyze --pilot micro
```

## Licensing

- **Code** (`src/`, `tests/`): MIT. See `LICENSE`.
- **Data** (`data/`, `runs/`, `reports/`): CC-BY-4.0. See `LICENSE-DATA`.
- **Public-inspired personas**: the aliases are fictional names, and the structured
  exports do strip to alias + anchor_family — `seed_bank_public_inspired.jsonl` carries
  no real anchor name in any row. **But an alias here is not de-identification, and you
  should not rely on it as one.** Each public-inspired persona is built from a packet of
  cited public sources (`data/source_packets/*.jsonl`), and those citations link the
  anchor's own published work — their personal domain, their papers, their talks. The
  alias is therefore trivially linkable to a real person wherever the source material is
  public, and that is true of every public-inspired anchor in this repository, not an
  oversight in one of them.

  This is deliberate: the provenance is what makes a persona reproducible, and the
  anchors are public figures cited through their public work. Treat these records as
  **pseudonymous but attributable** — never as anonymous — and carry that caveat into
  anything generated from them.

  *(Corrected 2026-08-12. This section previously said only that real anchor names live
  in private metadata, which invited exactly the wrong inference about the source
  packets sitting beside it.)*

## Source of the design

Everything in `prompts/`, the seed banks, the scoring rubric, and the
experimental matrix is transcribed from the "PsycheEval Kickstart Prompt &
Plan" document. See `docs/KIT_PROVENANCE.md` for what was copied verbatim
vs adapted.

## Redactions in the captured logs

Some diagnostic text captured from run tooling under `logs/` and `runs/` has been redacted:
incidental command-line noise carried an operator-environment detail that does not belong in a
public research artifact. The rate-limit **class** each record recorded is intact.

Two consequences, stated rather than left to be inferred:

- The `stdout_len` / `stderr_len` fields beside a redacted preview describe the **published**
  text, not the original process output.
- Timestamps that were recorded with a local UTC offset are stored as the **same instant in
  UTC**. No clock value changed; only its representation.

Neither affects any result here: no analysis reads these fields.

## Citation

Not ready. Don't cite v0.1 results as evidence about real users.
