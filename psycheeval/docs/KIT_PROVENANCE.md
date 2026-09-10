# Kit Provenance

What in this repo was copied **verbatim** from the design kit versus **adapted**
or **newly written** for this workspace.

The design kit is the **"PsycheEval Kickstart Prompt & Plan"** document, archived
at `~/claudeworkspace/psyche/inbox/psycheeval_kickstart_prompt_plan.md` (committed
to history in `d9007c5`). It is a complete research-design artifact: master prompt,
six object schemas, the full prompt set, persona seed banks, scoring rubric, and
the experimental matrix. References below of the form "kit §N" point at sections of
that document; many source files also carry an inline `Source: kit §N` header.

This is a provenance record, not a license. License terms are in `LICENSE`
(code, MIT) and `LICENSE-DATA` (data, CC-BY-4.0); see also README "Licensing".

## Legend

- **Verbatim** — transcribed from the kit with at most cosmetic edits (the
  `Source:` header, whitespace, fenced code formatting). The wording the LLM
  sees is the kit's.
- **Adapted** — derived from a kit section but materially changed for this
  workspace (workspace-specific decisions, model pinning, added clauses).
- **New** — has no kit counterpart; written during v0.2/v0.3 work or as
  workspace tooling.

## Prompts (`prompts/`)

| File | Origin | Status | Notes |
|------|--------|--------|-------|
| `00_master.md` | kit §1 | Verbatim | Research-lead master/system prompt. |
| `01_source_packet_ingestion.md` | kit §7 | Verbatim | Public-anchor source ingestion. |
| `02_synthetic_user_generation.md` | kit §6 | Verbatim | Synthetic user record generation. |
| `03_profile_compilation.md` | kit §8 | Verbatim | C1–C4 profile-condition compilation. |
| `04_scenario_generation.md` | kit §9 | Verbatim | Per-persona scenario generation. |
| `05_assistant_response.md` | kit §10 | Verbatim | Prompt given to the model under test. |
| `06_judge.md` | kit §11 | Verbatim | Blind single-response 0–5 rubric. |
| `07_pairwise_judge.md` | kit §12 | Verbatim | Blind forced-choice pairwise. |
| `08_analysis.md` | kit §13 | Verbatim | Optional qualitative analysis aid; `analyze.py` computes the quantitative metrics instead. |
| `06b_judge_anchored.md` | brief §13/§14/§21 | New (v0.2) | Anchored 0–10 rubric. From the v0.2 report-revision brief (`docs/report_revision_brief.md`), not the kit. |
| `06c_judge_anchored_paraphrased.md` | v0.3 plan §3.3 | New (v0.3) | Paraphrased-anchor sentinel (R12 / D2). |
| `07b_pairwise_judge_ternary.md` | v0.3 plan §3.3 | New (v0.3) | Ternary tie/equipoise pairwise variant. |

## Schemas (`schemas/`)

Derived from the kit §3 object definitions, then **exported from the pydantic
models** in `src/psycheeval/models.py` via `src/psycheeval/export_schemas.py`.
The pydantic models are the source of truth; the `.schema.json` files are
generated. Status: **Adapted** — the six core object shapes (`persona_seed`,
`source_packet`, `synth_user_record`, `profile_bundle`, `scenario`,
`assistant_output`, `judge_score`, `pairwise_score`) follow kit §3, but
`anchored_judge_score.schema.json` is a v0.2 addition with no kit counterpart,
and several models gained workspace-specific optional fields (tri-model halo
metadata, token counts) that are **not** in the kit.

## Persona seed banks (`data/seed_bank_*.jsonl`)

- `seed_bank_public_inspired.jsonl` — **Adapted** from kit §4. The aliases and
  archetypes follow the kit's public-inspired design, but the specific anchor
  selection, raw source packets, and any `*_raw.jsonl` descriptions are
  workspace-generated (see PLAN.md §2.4 source-hunting workflow). Privacy
  posture: real anchor names live in private internal metadata only.
- `seed_bank_pure_synthetic.jsonl` — **Verbatim/Adapted** from kit §5. The
  pure-synthetic archetypes (Calibration Goblin, Conflict-Allergic Moralist,
  etc.) are the kit's; field formatting matches the pydantic `PersonaSeed` model.

## Experimental matrix / conditions (`src/psycheeval/config.py`)

- `micro_pilot` conditions (C0/C1/C3/C4 + C5 for public-inspired) — **Adapted**
  from kit §16.1.
- `v02_hard_pilot` (adds C1_padded, C4_shuffled length controls; C5_CONTRACT) —
  **New (v0.2)**, from the report-revision brief.
- `v03_full_pilot` (C_GENERIC_CONTRACT, C4_WRONG_PROFILE, C5_NONPUBLIC*,
  L1–L3 ablation ladder) — **New (v0.3)**, from the v0.3 plan.

## Scoring rubric

The 10 scoring dimensions and the red-flag taxonomy are **Adapted** from kit
§11. The 0–5 legacy rubric (`JudgeScores`) is the kit's; the 0–10 anchored
rubric (`JudgeScoresAnchored`) and the extended red-flag labels are v0.2/v0.3
additions per the brief (BACKLOG.md "Anchored 0–10 judge rubric").

## Code (`src/psycheeval/`, `tests/`)

**New** — all Python is workspace-authored. The kit specified prompts, schemas,
and the experimental design; it did not ship an implementation. The pydantic
models follow kit §3 shapes (Adapted, see Schemas above); everything else
(`run.py`, `judge.py`, `analyze.py`, `cap_burn.py`, `llm.py`, the CLI, the
v02/v03 prepare pipelines, all tests) is original.

## Documentation

- `PLAN.md` — **Adapted** from the kit; it resolves the workspace-specific
  decisions the kit deferred to the user (PLAN.md §1.1–§1.9) and maps the kit
  into concrete execution steps.
- `README.md`, `BACKLOG.md`, `docs/*` (including this file) — **New**.
