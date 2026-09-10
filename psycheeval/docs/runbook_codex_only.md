# Runbook — codex-only buildout (Opus weekly limit deferred)

**Last updated**: 2026-04-26
**Reason for codex-only mode**: Opus weekly usage limit is approaching. We're maximizing what can be built using only the OpenAI / codex-cli quota (GPT-5.4 + GPT-5.5 xhigh) and cataloguing every Opus call that gets deferred so it can be picked up cleanly when the weekly window resets.

This runbook is the source of truth. If you're returning to this work after a session boundary, read this first, then run the resume commands in priority order.

---

## What's in flight right now

| Process | What it's doing | Wall ETA | Provider |
|---|---|---|---|
| `b7mxdx4v1` | P1: GPT-5.4 + GPT-5.5 scalar judging on tri-model tag (`2026-04-26_micro_tri_model`). 864 codex calls. | ~10 h | codex-cli |

When P1 finishes, the chained codex-only pipeline (P2–P5) starts automatically via `run_codex_only_pipeline.sh` (driver waits on `pgrep -af "psycheeval.judge score.*tri_model"` to exit).

## What's been completed in codex-only mode

| Phase | Detail | Records | Status |
|---|---|---|---|
| Pre-flight | GPT-5.5 model registered, codex CLI upgraded to 0.125.0, end-to-end probe passing | – | ✅ |
| D-1 | Tri-model extension tag `2026-04-26_micro_tri_model` created with v0.1 snapshot | 432 outputs + 883 scores copied | ✅ |
| D-2 | GPT-5.5 v0.1 generation | 216 / 216 GPT-5.5 outputs (0 failed) | ✅ |
| D-3 (codex slice) | GPT-5.4 + GPT-5.5 scalar judging | 864 calls running (P1) | 🔄 |

## Phases queued in the codex-only pipeline (P2–P5)

All phases use only `gpt-5.4` and `gpt-5.5-xhigh`, both via `codex-cli`. No Opus calls. Each phase is resume-safe — restartable from any phase boundary using its existing canonical-key dedup.

### P2 — v0.1 tri-model pairwise, codex judges, same-author scope

```bash
cd ~/claudeworkspace/psyche/psycheeval && \
  PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -u \
  -m psycheeval.judge pairwise \
  --tag 2026-04-26_micro_tri_model \
  --pilot micro_pilot \
  --judges gpt-5.4,gpt-5.5-xhigh \
  --workers 2 \
  --scope same_author_only \
  --missing-only
```

Expected: 384 same-author pairs/author × 3 authors × 2 codex judges = **2 304 codex pairwise calls**.

Defers: same-author pairs × Opus judge = **1 152 Opus pairwise calls**.

### P3 — v0.2 generation, codex authors only

```bash
cd ~/claudeworkspace/psyche/psycheeval && \
  PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -u \
  -m psycheeval.run \
  --pilot v02_hard_pilot \
  --tag 2026-04-26_v02_hard_codex_only \
  --authors gpt-5.4,gpt-5.5-xhigh \
  --workers 2
```

Expected: 520 outputs / author × 2 codex authors = **1 040 codex output calls**.

Defers: 520 Opus authoring calls.

### P4 — v0.2 anchored scalar judging, codex judges only

```bash
cd ~/claudeworkspace/psyche/psycheeval && \
  PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -u \
  -m psycheeval.judge score \
  --tag 2026-04-26_v02_hard_codex_only \
  --pilot v02_hard_pilot \
  --judges gpt-5.4,gpt-5.5-xhigh \
  --workers 2 \
  --rubric anchored
```

Expected: 1 040 outputs × 2 codex judges = **2 080 anchored scalar scores**.

Defers: 1 040 Opus anchored-judge calls (also any v0.2 outputs that Opus *authored*, see P3-deferred).

### P5 — v0.2 targeted pairwise, codex judges, same-author scope

```bash
cd ~/claudeworkspace/psyche/psycheeval && \
  PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -u \
  -m psycheeval.judge pairwise \
  --tag 2026-04-26_v02_hard_codex_only \
  --pilot v02_hard_pilot \
  --judges gpt-5.4,gpt-5.5-xhigh \
  --workers 2 \
  --scope same_author_only \
  --pairs "C4:C0,C4:C1,C4:C1_padded,C4:C4_shuffled,C3:C4,C1:C1_padded,C4:C5@PI" \
  --missing-only
```

Expected per author: 6 cross-condition pairs × 80 scenarios + 1 PI-only pair × 40 scenarios = 520 pairs. × 2 codex authors × 2 codex judges = **2 080 codex pairwise calls**.

Defers: 520 same-author pairs × Opus judge = **1 040 Opus pairwise calls**.

## Total Opus calls deferred (resume order)

When the Opus weekly window resets, resume in this priority order. Higher items unlock the next analysis pass.

| # | Job | Tag / pilot | Calls | Cmd |
|---|---|---|---|---|
| 1 | v0.1 pairwise final remainder | `2026-04-20_micro` / `micro_pilot` | 115 | see [v0.1 final 115 below](#resume-1) |
| 2 | Opus judging the new GPT-5.5 outputs (v0.1) | `2026-04-26_micro_tri_model` / `micro_pilot` | 216 | see [tri-model Opus scoring below](#resume-2) |
| 3 | v0.1 tri-model pairwise — Opus judge, same-author scope | `2026-04-26_micro_tri_model` / `micro_pilot` | 1 152 | see [tri-model Opus pairwise below](#resume-3) |
| 4 | v0.2 — Opus authoring 520 outputs | `2026-04-26_v02_hard_codex_only` (or fork) / `v02_hard_pilot` | 520 | see [v0.2 Opus authoring below](#resume-4) |
| 5 | v0.2 anchored scalar — Opus judge | same | 1 040 | see [v0.2 Opus anchored below](#resume-5) |
| 6 | v0.2 targeted pairwise — Opus judge, same-author scope | same | 1 040 | see [v0.2 Opus pairwise below](#resume-6) |
| **Total** | | | **4 083 Opus calls** | |

That's roughly one full Opus weekly cycle at sustainable concurrency. Spread across two windows if needed.

### Resume commands

#### <a id="resume-1"></a>1. v0.1 pairwise final 115 records

```bash
cd ~/claudeworkspace/psyche/psycheeval && \
  PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -u \
  -m psycheeval.judge pairwise \
  --tag 2026-04-20_micro --pilot micro_pilot \
  --judges opus --workers 1 --missing-only
```

#### <a id="resume-2"></a>2. Opus judging the 216 new GPT-5.5 outputs (v0.1 tri-model)

```bash
cd ~/claudeworkspace/psyche/psycheeval && \
  PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -u \
  -m psycheeval.judge score \
  --tag 2026-04-26_micro_tri_model --pilot micro_pilot \
  --judges opus --workers 1
```

(Resume logic skips the 432 v0.1 outputs already scored by Opus in the snapshot. Only the 216 GPT-5.5-authored outputs will be judged.)

#### <a id="resume-3"></a>3. v0.1 tri-model pairwise, Opus judge, same-author scope

```bash
cd ~/claudeworkspace/psyche/psycheeval && \
  PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -u \
  -m psycheeval.judge pairwise \
  --tag 2026-04-26_micro_tri_model --pilot micro_pilot \
  --judges opus --workers 1 \
  --scope same_author_only --missing-only
```

#### <a id="resume-4"></a>4. v0.2 — Opus authoring 520 outputs

Use a fresh tag if you want a clean Opus-included v0.2; otherwise append into the same tag — resume logic dedups by `(scenario, condition, output_model)`.

```bash
cd ~/claudeworkspace/psyche/psycheeval && \
  PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -u \
  -m psycheeval.run \
  --pilot v02_hard_pilot \
  --tag 2026-04-26_v02_hard_codex_only \
  --authors opus --workers 1
```

#### <a id="resume-5"></a>5. v0.2 anchored scalar — Opus judge

```bash
cd ~/claudeworkspace/psyche/psycheeval && \
  PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -u \
  -m psycheeval.judge score \
  --tag 2026-04-26_v02_hard_codex_only --pilot v02_hard_pilot \
  --judges opus --workers 1 --rubric anchored
```

(After step 4 lands the 520 Opus-authored outputs, this same command also picks up Opus judging Opus's own outputs and the existing GPT-5.4/GPT-5.5 outputs in one pass.)

#### <a id="resume-6"></a>6. v0.2 targeted pairwise — Opus judge

```bash
cd ~/claudeworkspace/psyche/psycheeval && \
  PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -u \
  -m psycheeval.judge pairwise \
  --tag 2026-04-26_v02_hard_codex_only --pilot v02_hard_pilot \
  --judges opus --workers 1 \
  --scope same_author_only \
  --pairs "C4:C0,C4:C1,C4:C1_padded,C4:C4_shuffled,C3:C4,C1:C1_padded,C4:C5@PI" \
  --missing-only
```

## Scope decisions baked into this plan

These can be revisited later if codex-only results suggest they'd materially change the answer.

| Decision | Default chosen | When to revisit |
|---|---|---|
| Tri-model pairwise scope | same_author_only | If C3-vs-C5 / C4-vs-C5 PI-only effects shrink under tri-model scoring and you want maximum statistical power. Exhaustive triples the call count: ~7 200 codex calls + ~3 600 Opus calls. |
| v0.2 pairwise pair set | targeted whitelist (brief §15) | If targeted analysis suggests a meaningful condition pair was excluded (e.g. C5-vs-C1_padded as a "source-vs-padding" sanity check). |
| v0.2 pairwise scope | same_author_only | If we want cross-author author-effect estimation in v0.2. Exhaustive doubles the v0.2 pairwise budget. |
| v0.2 author authoring during codex-only | GPT-5.4 + GPT-5.5 only | If we want to start v0.2 generation earlier, Opus authoring is the second-cheapest deferred line item (520 Opus calls). |

## Coverage / interpretive guardrails for codex-only intermediate reports

The analyzer (post-Phase B-2) emits stratified coverage diagnostics. In codex-only mode, several cells will read as `coverage_status: "deferred-quota-bound"` rather than empty. The curated v0.1 tri-model and v0.2 reports must:

1. Not present a "primary cross-provider" headline that mixes Opus-judging-OpenAI (deferred) with OpenAI-judging-Opus (present). Frame cross-provider as **OpenAI-judging-Anthropic only** in the codex-only intermediate.
2. Use **pairwise-supported** language. Wilson 95% CIs already in `pair_preference_*` cells.
3. Treat tri-model halo as **partial** until Opus judges land — the `same_provider_minus_cross` bucket is the new tri-model contribution and only populates when GPT-5.4 and GPT-5.5 cross-judge.
4. Surface deferred Opus cells in tables explicitly as "Opus: deferred (weekly quota window)" rather than dropping the row.

## Driver script

`run_codex_only_pipeline.sh` at the project root chains P2→P5. It waits for the in-flight P1 to finish, then runs each phase in sequence. Logs in `/tmp/codex_only_pipeline/`.

## When Opus quota returns

1. Run resume-1 (v0.1 final 115). Confirm 3 504 / 3 504 v0.1 pairwise.
2. Regenerate v0.1 metrics; confirm full coverage in `pairwise_coverage.totals`.
3. Run resume-2 (216 Opus scores on tri-model GPT-5.5 outputs).
4. Run resume-3 (1 152 Opus pairwise on tri-model). After this, full tri-model halo audit is meaningful.
5. Regenerate tri-model metrics; the `same_provider_minus_cross` halo bucket lights up.
6. Run resume-4 → 5 → 6 to bring v0.2 to full tri-model coverage.
7. Final v0.2 analyzer pass; remove "DEFERRED" annotations from reports.
