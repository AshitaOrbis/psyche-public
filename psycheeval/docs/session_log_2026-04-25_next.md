# Session log — 2026-04-25 (tri-model extension start)

State snapshot before kicking off Phase B–F of `tri_model_extension_plan.md`.

## Git state

- Branch: `master`
- HEAD: `9722659 Add PsycheEval v0.1 micro-pilot` (no commits ahead of upstream)
- Working tree: dirty. 28 modified tracked files + ~17 untracked paths. Includes the v0.1 brief revisions, v0.2 implementation, prompt vocabulary refactor, drift tests, analyzer extensions, and the synthetic fixture smoke test from the previous sessions. Nothing committed yet — bundling deferred per workspace rules until user says to commit.

## Test status

`PYTHONPATH=src .venv/bin/python -m pytest tests/ -q` → **29 passed**.

## Pairwise corpus (run `2026-04-20_micro`)

| Judge | Records on disk | Target | Missing |
|---|---|---|---|
| gpt-5.4 | 1 752 | 1 752 | 0 (complete) |
| opus | 888 | 1 752 | 864 |
| **Total** | **2 640** | **3 504** | **864** |

## Validation warnings

`runs/2026-04-20_micro/validation_warnings.jsonl` does not exist — no invalid red-flag labels have been logged since the prompt was rewritten to enumerate the controlled vocabulary. Pre-fix invalid labels were dropped at the time (no log file existed yet); they are recoverable from the older sequential run log at `/tmp/ps_pairwise.log` if ever needed for forensic.

## Phase A-2: GPT-5.5 xhigh probe

- **Local CLI**: codex 0.118.0 → upgraded to **0.125.0** (`npm i -g @openai/codex@latest`).
- **Auth**: ChatGPT plan (no `OPENAI_API_KEY`). 0.118.0 rejected `gpt-5.5` with a version-gate error; 0.125.0 accepts it.
- **Default reasoning effort**: `xhigh` already in `~/.codex/config.toml`; codex header confirms `reasoning effort: xhigh` on every call.
- **JSON probe**: returned `{"ok":true,"model":"Codex"}` cleanly.
- **JudgeScores-shaped probe**: returned valid `scores` (0-5 ints across all 10 dimensions) + empty `red_flags` + 2-sentence rationale. Latency ~30 s for ~7.7 k tokens.
- **Other variants tested**: `gpt-5.5-thinking`, `gpt-5.5-pro`, `gpt-5.5-instant`, `gpt5.5`, `gpt-5.4-thinking` are all rejected with "not supported when using Codex with a ChatGPT account." Use plain `gpt-5.5` only.

**Decision**: register the model as key `gpt-5.5-xhigh`, api_model `gpt-5.5`, reasoning_effort tracked in metadata as `xhigh` (sourced from codex config; not currently passed per-call by our wrapper). The internal key stays stable as `gpt-5.5-xhigh` even though codex doesn't expose a separate effort flag.

## Next steps

Continuing in order:

1. Phase A-2: GPT-5.5 xhigh probe via codex CLI.
2. Phase B-1: coverage planner + `--missing-only`.
3. Phase B-2: coverage diagnostics + Wilson intervals.
4. Phase B-3: 864 Opus pairwise backfill at workers=1.
5. Phase B-4: regenerate v0.1 metrics + curated report with the artifact-status block.

Stop conditions per `tri_model_extension_plan.md` §22 are in force.
