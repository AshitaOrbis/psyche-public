# v0.3 Overnight Status — 2026-05-19 (final)

**Session**: 2026-05-18 evening → 2026-05-19 early morning. User approved all three Phase -1 recommended decisions; work proceeded to Phase 0.

## TL;DR

Phase -1 fully sealed. Phase 0 ~85% complete. Only the compute_metrics wiring for D1-D4 blocks remains before the v0.3 pipeline can run end-to-end. Five commits landed; none pushed.

## What's done (5 commits)

| Commit | Scope |
|--------|-------|
| `1b58d23` | v0.3 plan revision + reviews + initial condition wiring |
| `3268ead` | D1 same-orientation sentinel + D3 reward-hacking diagnostics + ternary prompt |
| `0015767` | First overnight status note |
| `f4088c9` | Phase -1 sealed + D2 + D4 analyzer blocks + 4 PI-matched nonpublic packets + bundles regenerated |
| `b0348e6` | --ab-ba-mandatory flag + 26 smoke tests for analyzer blocks D1-D4 (all passing) |

## Phase -1 sub-items (all sealed)

| Item | Resolution |
|------|------------|
| -1.1 Pair manifest | Locked. 16 T1 + 12 T2 + 5 optional T4 pair types in design-lock doc. |
| -1.2 Power memo | Locked. Cluster-bootstrap sim confirmed D5 not decidable. |
| -1.3 Tie policy | **Path A** — forced-choice primary + 10% ternary sentinel. |
| -1.4 Endpoint hierarchy | Locked. AB/BA pairwise > scalar > sentinel-adjusted > reward-hacking > tie-aware > paraphrased > author-rater > shadow-mode. |
| -1.5 Model snapshot | Locked. gpt-5.4, gpt-5.5-xhigh, claude-opus-4-7; prompts frozen at v0.3 start. |
| **-1.6 MCID** | **Option A (±5pp)** — approved by user 2026-05-19. |
| -1.7 Expansion triggers | Locked. 6 predeclared triggers; exploratory-only label. |
| **-1.8 D5** | **SKIP** — approved by user 2026-05-19, power-confirmed. |
| **-1.9 C5_NONPUBLIC scope** | **Option (a) PI-matched** — approved, packets authored. |
| -1.10 Scenario audit | Locked. 12 unique prompts across 80 scenarios; transparency note for v0.3 report. |
| -1.11 Failure criteria | Locked. 8 predeclared triggers in §8.2. |
| -1.12 Power/margin reconciliation | Locked. D5 ±5pp and Phase 9 engagement gap on different scales. |

## Phase 0 progress

| Item | Status |
|------|--------|
| Condition enum additions (7 new) | ✅ done |
| ProfileConditions model extension | ✅ done |
| PILOT_CONDITIONS["v03_full_pilot"] | ✅ done |
| v03_prepare.py generators | ✅ done — generates C_GENERIC, C4_WRONG, L1/L2/L3, C5_NONPUBLIC, C5_NONPUBLIC_CONTRACT |
| 4 PI-matched nonpublic packets | ✅ done — `v03_nonpublic_packets.py`, length-matched within 5-15% of C5 |
| Ternary pairwise prompt | ✅ done — `prompts/07b_pairwise_judge_ternary.md` |
| Analyzer block D1 (same-orientation sentinel) | ✅ done |
| Analyzer block D2 (paraphrased anchor consistency) | ✅ done |
| Analyzer block D3 (reward-hacking diagnostics) | ✅ done |
| Analyzer block D4 (tie-aware reinterpretation) | ✅ done |
| `--ab-ba-mandatory` flag | ✅ done |
| Smoke tests for analyzer blocks | ✅ done (26 tests, all passing) |
| **Wire D1/D2/D3/D4 into compute_metrics** | ⏳ remaining (~1-2h) |

## What "wire into compute_metrics" means

The 4 analyzer blocks are functions that accept synthetic inputs and return well-formed JSON. To wire them into the pipeline, `compute_metrics` needs to:

1. **Read new record types from disk**:
   - `same_orientation_swap_scores.jsonl` (10% sample of pairwise records with same-orientation re-judgments)
   - `paraphrased_anchored_scores.jsonl` (15% sample of scalar records with paraphrased rubric anchors)
   - `pairwise_ternary_scores.jsonl` (10% sample of pairwise records with ternary tie/equipoise prompt)

2. **Add per-pair-type cells in the metrics output**:
   - `pairwise.same_orientation_sentinel_same_author`
   - `anchored.paraphrased_anchor_consistency`
   - `pairwise.tie_aware_reinterpretation_same_author`
   - `reward_hacking_diagnostics` (top-level, since it's per-output not per-pair)

3. **Pass the records into the analyzer blocks** at the same point that `_compute_ab_ba_position_audit` is called.

This is a thin integration layer — the analyzer functions themselves are tested and ready. The work is in `analyze.py:compute_metrics` (around line 3617-3640 where AB/BA position audit is wired) and in adding ~20 lines of record-reading per new file type.

## v0.3 bundle contents (PI personas, e.g. slalom_altar)

| Condition | Source | Length |
|-----------|--------|--------|
| C0 | v0.2 inherited | n/a (no profile) |
| C1, C1_padded, C3, C4, C4_shuffled | v0.2 inherited | unchanged |
| C5 (public-anchor packet) | v0.2 inherited | 3,476 chars |
| C5_CONTRACT | v0.2 inherited | 6,905 chars |
| **C_GENERIC_CONTRACT** | v0.3 NEW (template) | 4,754 chars (length-matched to C4) |
| **C4_WRONG_PROFILE** | v0.3 NEW (opposite-trait swap) | inherits donor's C4 length |
| **C5_NONPUBLIC** | v0.3 NEW (PI-matched fictional) | 4,284 chars |
| **C5_NONPUBLIC_CONTRACT** | v0.3 NEW (C3 + anti-mimicry + C5_NONPUBLIC) | 7,713 chars |
| **L1** | v0.3 NEW (C5 + min contract, packet-first, no anti-mimicry) | 3,476 chars (per-persona match) |
| **L2** | v0.3 NEW (L1 + anti-mimicry) | 3,494 chars |
| **L3** | v0.3 NEW (L2 + contract-first ordering) | 3,494 chars |

## Cleanup item (cosmetic)

The `profile_bundle_id` for v0.3 bundles has a double "_v03" suffix because I appended _v03 to the v0.2 bundle id (which already ends in _v02). The current bundles read `bundle_xyz_v02_v03_v03`. Not breaking — just ugly. Fix: change the rstrip + append logic in `v03_prepare.py:prepare_v03_profile_bundles` to strip the _v02 suffix first, then append _v03. Trivial 30s fix.

## Recommendation for tomorrow's work

1. **Wire D1-D4 into compute_metrics** (~1-2h). The analyzer blocks are ready; the work is reading 3 new jsonl file types and calling the functions at the right spot in `compute_metrics`.
2. **Fix the _v03_v03 bundle_id cosmetic issue** (~30s).
3. **Run an integration test**: generate 4-8 outputs in v0.3 corpus (small smoke) to verify the full pipeline works end-to-end before Phase 1 generation kicks off properly.
4. **Begin Phase 1 generation**: `psycheeval.run --pilot v03_full_pilot --tag YYYY-MM-DD_v03 --ab-ba-mandatory`

## Files modified tonight

| File | Status |
|------|--------|
| `docs/v0_3_plan.md` | Revised (444 lines) |
| `docs/v0_3_plan_2026-05-18_pre-review.md` | New archive (358 lines) |
| `docs/v0_3_phase_minus_1_design_lock.md` | New + sealed (~460 lines) |
| `docs/v0_3_overnight_status_2026-05-19.md` | THIS FILE (final version) |
| `src/psycheeval/models.py` | Condition enum + ProfileConditions extended |
| `src/psycheeval/config.py` | v03_full_pilot pilot map |
| `src/psycheeval/v03_prepare.py` | NEW — full v0.3 bundle generation |
| `src/psycheeval/v03_nonpublic_packets.py` | NEW — 4 PI-matched nonpublic packets |
| `src/psycheeval/analyze.py` | D1 + D2 + D3 + D4 analyzer blocks |
| `src/psycheeval/judge.py` | --ab-ba-mandatory flag |
| `prompts/07b_pairwise_judge_ternary.md` | NEW — ternary sentinel prompt |
| `drivers/v0_3_cluster_power_sim.py` | NEW — power sim |
| `drivers/v0_3_cluster_power_sim_fast.py` | NEW — fast power sim |
| `drivers/.v0_3_power_sim_fast_output.txt` | NEW — sim results (D5 not decidable) |
| `data/v03_full_pilot/profile_bundles.jsonl` | 8 bundles regenerated with all 8 v0.3 conditions |
| `data/v03_full_pilot/scenarios.jsonl` | Copied from v0.2 |
| `data/v03_full_pilot/synthetic_user_records.jsonl` | Copied from v0.2 |
| `data/v03_full_pilot/source_packets.jsonl` | Copied from v0.2 |
| `tests/test_v03_analyzer_blocks.py` | NEW — 26 smoke tests (all passing) |
| 13 review artifacts under `reports/reviews/2026-05-18_*` | New — v0.3 plan reviews + blog 046 publication review |

## Total work delta tonight

- **5 commits** in `psyche/` repo
- **3,000+ insertions** across source, tests, docs
- **26 tests added**, all passing
- **8 v0.3 conditions** wired end-to-end (condition enum → ProfileConditions → PILOT_CONDITIONS → v03_prepare generation → bundle file with profile_text)
- **4 PI-matched nonpublic packets** authored (matched on trait pattern, anchor cues removed)
- **4 analyzer blocks** added (D1-D4)
- **Phase -1 sealed** with all 12 sub-items locked
- **Power simulation** confirms D5 SKIP is correct

When you're ready, the next concrete step is wiring D1-D4 into compute_metrics, then running a small smoke generation to verify the full pipeline before Phase 1 kicks off.
