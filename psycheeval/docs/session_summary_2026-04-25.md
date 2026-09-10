# PsycheEval — Session Summary

**Date**: 2026-04-25
**Run tag**: `2026-04-20_micro`
**Posture**: private notes / internal audit trail
**Scope**: v0.1 brief integration + v0.2 implementation + critical drift fix

---

## TL;DR

The pilot's central claim is now testable on multiple instruments and lands the same way on each:

> **Behavioural contracts (C3, C4) outperform source-packet personas (C5) under the cleanest comparison the pilot supports — same author, cross-provider judge, head-to-head pairwise. C3 vs C5 = 65.6% / 34.4%; C4 vs C5 = 57.6% / 42.4%. Even on home turf (PI-only with high-grounding source packets), the same ordering holds. C4's anti-sycophancy clauses give a small marginal lift over C3 in pairwise terms (56.6% / 42.1%), not a transformative one. The v0.1 finding worth carrying into v0.2: source packets may induce public-archetype echo — recognizably coherent but less scenario-specific, more generic responses.**

This session also fixed a load-bearing drift risk in the prompt vocabulary (the v0.2 +6 red-flag labels would have silently failed to propagate) and shipped an analyzer extension that handles both 0–5 and 0–10 rubrics so v0.2 can run cleanly.

---

## 1. Bug fixed: pairwise prompt vs RedFlag enum drift

**Problem**: The first pairwise judging run failed validation on essentially every record. Both judges returned free-text descriptions like `"length without proportional added signal"` in the `red_flags_A` / `red_flags_B` arrays, which the `PairwiseScore` Pydantic model rejected as enum-invalid. The pairwise prompt (`07_pairwise_judge.md`) had never enumerated valid label names. Compounding this: the v0.2 brief adds 6 new labels, so even hardcoded lists in `06_judge.md` and the new anchored prompt would have drifted away from the Python `RedFlag` enum without anyone noticing until the data was already corrupted.

**Fix**:

1. `RedFlag` enum is now the single source of truth (24 labels: 18 v0.1 + 6 v0.2).
2. `RED_FLAG_DESCRIPTIONS` dict pairs a one-line description with each label.
3. `render_red_flag_vocabulary(style)` emits the controlled vocabulary in either `labels_only` or `labels_with_descriptions` form.
4. All three prompt files now use `{{RED_FLAGS_VOCABULARY}}` / `{{RED_FLAGS_VOCABULARY_WITH_DESCRIPTIONS}}` placeholders. `_substitute_red_flag_vocabulary()` fills them at render time.
5. `_coerce_red_flags()` now returns `(valid, invalid)` rather than just dropping invalid labels. Invalid labels are appended to `runs/<tag>/validation_warnings.jsonl` with judge / author / condition / label / context-id / timestamp — thread-safe via a global lock. Nothing is silently erased.
6. **Drift-prevention tests** (`tests/test_prompt_vocabulary.py`, 8 tests):
   - Descriptions cover the enum exactly once (no missing, no extras).
   - Each renderer emits every enum value.
   - Each prompt file contains the placeholder and **cannot** contain ≥3 backticked enum labels (catches re-introduction of hardcoded lists).
   - Substitution leaves no placeholder behind and is idempotent.
   - JSON schema enums for `JudgeScore`, `AnchoredJudgeScore`, `PairwiseScore` must match `RedFlag` exactly (fails CI if someone edits `models.py` without rerunning `psycheeval.export_schemas`).

**Result**: 0 validation errors across all subsequent judge runs. Future enum changes propagate to every prompt automatically.

---

## 2. Pairwise restart with parallelism

**Problem**: At ~37s per call sequential, the 3 504 pairwise calls would have taken ~6 days.

**Fix**: Added `ThreadPoolExecutor` parallelism + `--workers N` flag to both `score_all` and `pairwise_all`. Writes serialized through a lock; resume state is pre-computed once before the pool starts.

**Outcome**:

- GPT-5.4-as-judge: 1 752 / 1 752 records — **complete**.
- Opus-as-judge: hit Claude Max usage cap during the burst (4 workers was too aggressive). 888 / 1 752 records on disk after a 2-worker backfill recovered another 357. Final coverage: **75% of the ideal 3 504 (2 640 pairwise records)**.
- Cross-provider same-author pairs in the dataset: 583. PI-only same-author cross-provider: 333. These are the cells that drive the pairwise findings below.

---

## 3. Pairwise findings (the load-bearing v0.1 result)

All numbers below are cross-provider judged + same-author paired, which is the cleanest comparison the pilot supports. Ties split 0.5 / 0.5 in win-rates.

### Per-condition win-rate (all personas)

| Condition | Win rate | Read |
|---|---|---|
| C0 | 0.274 | No-profile baseline; gets clobbered |
| C1 | 0.430 | Bare trait labels — better than C0, worse than any structured profile |
| **C3** | **0.645** | Behavioural contract — highest in the dataset |
| **C4** | **0.638** | Contract + anti-sycophancy clauses — within noise of C3 |
| C5 | 0.523 | Source-packet-informed — beats baseline / labels but loses to either contract |

### Condition-pair preferences (head-to-head)

| Pair | n | First wins | Second wins | Ties |
|---|---|---|---|---|
| C0 vs C1 | 75 | 0.280 | **0.693** | 0.027 |
| C0 vs C3 | 75 | 0.227 | **0.747** | 0.027 |
| C0 vs C4 | 76 | 0.263 | **0.724** | 0.013 |
| C0 vs C5 | 33 | 0.303 | **0.667** | 0.030 |
| C1 vs C3 | 75 | 0.253 | **0.747** | 0.000 |
| C1 vs C4 | 75 | 0.360 | **0.640** | 0.000 |
| C1 vs C5 | 33 | 0.364 | **0.636** | 0.000 |
| **C3 vs C4** | 76 | 0.421 | **0.566** | 0.013 |
| **C3 vs C5** | 32 | **0.656** | 0.344 | 0.000 |
| **C4 vs C5** | 33 | **0.576** | 0.424 | 0.000 |

### What the pairwise data actually shows

1. **Every profile beats no-profile.** C0 loses every head-to-head by 36–52 points. The simplest result is the most secure: adding any user profile is better than adding none.
2. **Behavioural contracts beat source-packet personas head-to-head.** C3 vs C5 = 31-point margin to C3. C4 vs C5 = 15-point margin to C4. The cross-provider + same-author design is the cleanest comparison the pilot supports, and the direction is unambiguous: when the same author writes a response under a behavioural contract vs the same author writing under a source packet, the cross-provider judge prefers the behavioural-contract response more often than the reverse.
3. **C4 beats C3 narrowly.** 14-point margin. The anti-sycophancy / motive-uncertainty / repair clauses produce a real but modest pairwise lift over plain C3. The margin is smaller than C3-over-C5 (31 points), suggesting the load-bearing variable is "is there a behavioural contract at all," not "are there anti-sycophancy clauses on top." v0.2 will pressure-test this with the C4_shuffled length-control: if C4_shuffled also beats C3 by ~14 points, the C4-over-C3 lift is from added text, not from clause structure.

### PI-only sharpens the C5 picture

Within the public-inspired subset (where the source packets were actually built), the same ordering holds:

| Pair | n | First wins | Second wins |
|---|---|---|---|
| **C3 vs C4** | 33 | 0.515 | 0.485 |
| **C3 vs C5** | 32 | **0.656** | 0.344 |
| **C4 vs C5** | 33 | **0.576** | 0.424 |

Two reads worth carrying:

- **C3 vs C4 within PI is essentially a tie** (51.5% / 48.5%). The C4 lift over C3 in the all-persona block is being driven by pure-synthetic personas, where anti-sycophancy clauses help more, not by public-inspired ones. Public-inspired personas already produce more challenge-flavored baseline responses, so the explicit anti-sycophancy clauses have less marginal room.
- **C5 still loses to C3 by 31 points and to C4 by 15 points within PI-only — the home turf where the source packet was actually built for these personas.** This is the strongest evidence in the pilot for the public-archetype-echo hypothesis: even where source packets ought to look best, behavioural contracts win.

---

## 4. The C5 / public-archetype-echo synthesis

The v0.1 finding with the largest framing implications. Pulled together because it shows up on three converging measurement channels (note: scalar scores, red-flag labels, and pairwise preferences reuse the same outputs/scenarios/authors/judges, so they are not statistically independent):

1. **Scalar means (cross-provider, PI-only)**: C5 − C4 ranges from −0.021 (`boundary_safety`) to −0.292 (`profile_fit`). C5 is worse than C4 on every dimension and red-flag rate jumps from 0.104 at C4 to 0.271 at C5.
2. **Red-flag pattern (PI-only)**: `generic_slop` climbs from 0.042 at C4 to 0.125 at C5 — a 3× increase. `style_mimicry_overfit` appears only at C0 and C5, never at C1/C3/C4. `overpersonalization`, `diagnostic_overreach`, `fake_certainty`, and `missed_boundary` all tick up at C5 relative to C4. The failure modes C4 suppresses are the ones C5 reintroduces.
3. **Pairwise (PI-only, cross-provider, same-author)**: C5 loses to C3 by 31 points and to C4 by 15 points, head-to-head.

**Hypothesis**: source packets help the model locate a familiar public voice and then produce advice in that voice rather than advice *to this user in this scenario*. "Founder-type advice," "rationalist-voice advice," "linguistic-rigor advice" looks coherent (which is why same-provider judges over-credit it: GPT-judging-GPT at C5 inflated interpretive-dimension scores by +0.500 to +0.583) but it's less scenario-specific and less personalized than a behavioural contract.

**One concrete example**: the failure cards include a `source_unfaithfulness` instance at C5 — a Pawl Gram scenario where the model produced unsolicited citations-from-memory that weren't in the actual source packet. That is exactly the public-archetype-echo mechanism, in vitro.

**Implication for v0.2**: source packets need to be translated into behavioural constraints before the author sees them, rather than fed through as worldview fuel. The kit §7 ingestion prompt rework is the v0.2-§8 candidate. The new red-flag label `public_archetype_echo` operationalizes the hypothesis directly so v0.2 can falsify it rather than infer it.

---

## 5. v0.1 report restructure (per brief)

The pre-revision report mixed same-provider and cross-provider judges in the main "Dimension means by condition" table — the brief's primary methodological flag. The restructure:

- **Primary tables: cross-provider judged only.** Every Opus output scored by GPT-5.4 judge; every GPT-5.4 output scored by Opus judge. Same-provider scores excluded.
- **All-judge means demoted to Appendix A**, clearly labeled secondary.
- **C5 isolated to PI-only subset.** Never compared against global C0–C4 means.
- **PI-only and PS-only per-condition tables added.**
- **Narrative sections added**: "What PsycheEval is testing," "How to read this pilot," "What this pilot can and cannot show," explicit C4 framing as a behavioural contract, fictionalized-public-anchor reframing for the public-inspired personas, softened claim language per brief §9 + §26, expanded ceiling-effect discussion, dedicated C5 / public-archetype-echo synthesis section.
- **Pairwise section** populated with the tables above.
- **Pre-revision snapshot** archived at `reports/archive/v0.1-pre-brief-revision/` with a MANIFEST.

The cross-provider numbers are materially different from the old all-judge numbers in the right direction. C4 − C0 deltas are *larger* than the pre-revision report claimed (profile_fit +0.541 vs old +0.402; helpfulness +0.364 vs old +0.276). The halo was suppressing apparent improvement at the bottom of the rubric and inflating it at C5.

---

## 6. v0.2 implementation status

Per the brief's "Document + implement + run v0.2 now" choice, the full pipeline is in place. **Code: complete. Execution: queued (waiting on quota window).**

### Done (code/data)

| Piece | Status |
|---|---|
| `Condition.C1_PADDED`, `C4_SHUFFLED` | added to enum |
| `RedFlag` +6 labels (mind_reading_collusion, repair_avoidance, identity_locking, public_archetype_echo, moral_laundering, pseudo_depth) | added |
| `prompts/06b_judge_anchored.md` (0–10 anchored rubric per brief §14) | written |
| `data/v02_hard_scenarios_seed.jsonl` (10 hand-crafted scenarios per brief §17) | written |
| `psycheeval.v02_prepare` — programmatic C1_padded + C4_shuffled builder | written + executed (80 scenarios + 8 bundles materialized) |
| `config.PILOT_CONDITIONS` + `conditions_for()` | added |
| `run.py` per-pilot condition routing + `--workers N` | added |
| `judge.py` `--rubric anchored --workers N --pairs <whitelist>` | added |
| `AnchoredJudgeScore` / `JudgeScoresAnchored` models + schema export | added |
| Anchored-scores analyzer path (compute_metrics handles 0–5 and 0–10 in parallel; scales never mix) | added |
| Length-control delta blocks (C4−C1, C4−C1_PADDED, C4−C4_SHUFFLED, C4−C5 PI-only, C3−C4) | added |
| Token / character summary by condition | added |
| Targeted pairwise scope (`--pairs "C4:C0,C4:C1,C4:C1_padded,C4:C4_shuffled,C3:C4,C1:C1_padded,C4:C5@PI"`) | added |
| Synthetic fixture + analyzer end-to-end smoke test (procedural fixture, exercises every code path including length controls and v0.2 anchored block) | added |
| Drift-prevention test suite | 8/8 passing |

**Test suite: 29/29 passing.**

### v0.2 dry-run manifest

`psycheeval.run --pilot v02_hard_pilot --tag 2026-04-25_v02_hard --dry-run` reports **1 040 outputs** to generate (PI: 560, PS: 480; 80 scenarios × 6 core conditions + 1 PI extra × 2 authors).

### Pending (execution)

```bash
# Already prepared:
uv run python -m psycheeval.v02_prepare

# Queued (~3h at 4 workers, modulo Claude Max windows):
uv run python -m psycheeval.run --pilot v02_hard_pilot --tag 2026-04-25_v02_hard --workers 4

# Anchored scalar judging (~3-4h at 4 workers):
uv run python -m psycheeval.judge score \
  --tag 2026-04-25_v02_hard --pilot v02_hard_pilot \
  --judges opus,gpt-5.4 --workers 4 --rubric anchored

# Targeted pairwise (~3-4h at 4 workers; smaller than v0.1's all-pairs because the whitelist cuts the scope):
uv run python -m psycheeval.judge pairwise \
  --tag 2026-04-25_v02_hard --pilot v02_hard_pilot \
  --judges opus,gpt-5.4 --workers 4 \
  --pairs "C4:C0,C4:C1,C4:C1_padded,C4:C4_shuffled,C3:C4,C1:C1_padded,C4:C5@PI"

# Analyze:
uv run python -m psycheeval.analyze --tag 2026-04-25_v02_hard --pilot v02_hard_pilot
```

**Recommendation**: start v0.2 generation when there's a clean Claude Max window (avoid contending with any v0.1 backfill). Worker count of 4 is the sweet spot for GPT-5.4; consider 2 for Opus to avoid the burst-cap that hit pairwise.

---

## 7. Open items / next session

1. **Opus pairwise backfill remainder.** 864 records still missing. The two backfill bursts each hit the Claude Max window. A third pass at 1–2 workers, ideally outside peak hours, should complete it. The current 75% coverage is enough for the v0.1 conclusions above; running it to 100% would mostly tighten error bars on the per-condition cells, not change directions.
2. **v0.2 generation + judging.** Pipeline is ready. Estimated total wall time: ~10–14 hours of active LLM call time spread across whatever windows are available.
3. **Inter-judge agreement stats.** Cohen's κ on red-flag labels and Spearman on dimension scores between Opus and GPT-5.4. Not blocking but worth adding to the v0.1 report once the Opus backfill is complete.
4. **Human calibration sample.** Brief §18: 20–50 outputs, 2–3 raters, hardest scenario families. Tracked in BACKLOG.md as a v0.2-or-later candidate.
5. **Not committed.** Working tree has all the above plus earlier session work. Holding off on `git commit` until you say to bundle.

---

## 8. Changed files / new files

```
NEW  psycheeval/docs/v0.2_plan.md
NEW  psycheeval/docs/session_summary_2026-04-25.md  ← this file
NEW  psycheeval/data/v02_hard_scenarios_seed.jsonl
NEW  psycheeval/data/v02_hard_pilot/                (scenarios + bundles + user records)
NEW  psycheeval/prompts/06b_judge_anchored.md
NEW  psycheeval/src/psycheeval/v02_prepare.py
NEW  psycheeval/tests/test_prompt_vocabulary.py
NEW  psycheeval/tests/test_analyzer_smoke.py
NEW  psycheeval/reports/archive/v0.1-pre-brief-revision/  (snapshot + MANIFEST)
NEW  psycheeval/schemas/anchored_judge_score.schema.json

MOD  psycheeval/BACKLOG.md
MOD  psycheeval/prompts/06_judge.md            (placeholder + drift instructions)
MOD  psycheeval/prompts/07_pairwise_judge.md   (placeholder + drift instructions)
MOD  psycheeval/reports/psycheeval_v0_1_micro_pilot_2026-04-20_micro.md  (full restructure + pairwise tables)
MOD  psycheeval/reports/metrics_2026-04-20_micro.json  (cross-provider primary + anchored block)
MOD  psycheeval/src/psycheeval/analyze.py      (refactored; 0–5 and 0–10 paths)
MOD  psycheeval/src/psycheeval/config.py       (per-pilot condition map)
MOD  psycheeval/src/psycheeval/judge.py        (workers, rubric, pairs whitelist, validation warnings)
MOD  psycheeval/src/psycheeval/models.py       (Condition + RedFlag + AnchoredJudgeScore + RED_FLAG_DESCRIPTIONS + render_red_flag_vocabulary)
MOD  psycheeval/src/psycheeval/run.py          (parallel + per-pilot conditions)
```

**Test suite**: 29 / 29 passing (11 model tests + 3 manifest tests + 8 LLM helper tests + 8 prompt vocabulary tests + 2 analyzer smoke tests, with the original 5 + 3 carried forward).
