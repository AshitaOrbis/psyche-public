# Pre-labeling-fix archive — 2026-05-15

## What this archive contains

Snapshot of `metrics_2026-04-26_v02_hard_codex_only.json` and
`psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md`
**before** the 2026-05-15 labeling-defect fix.

## Why archived

External review on 2026-05-15 (codex-council + gpt-max + gpt-pro,
consolidated at `reports/reviews/2026-05-15_consolidated_v0_2_review.md`)
flagged that the v0.2 review bundle conflated total pairwise records
(3,123) with same-author records (true: 2,944). 179 cross-author records
had leaked into the corpus during the Opus C5_CONTRACT pairwise phase
(174 of 179 from the Opus judge, all on the 3 C5_CONTRACT-vs-{C3, C4, C5}
edges) because `--scope same_author_only` was not consistently passed.

The pre-fix metrics JSON did not expose:

- `pairwise.counts.same_author` or `pairwise.counts.cross_author`
- `pairwise.cross_author_leak_detection`
- `pairwise.cluster_bootstrap_ci_cross_provider_same_author`
- `pairwise.cluster_bootstrap_ci_same_provider_same_author`
- `pairwise.cluster_bootstrap_scope_counts`

The analyzer's actual computations were correct (cluster-bootstrap CIs
used the truly-same-author filter at `same_author_all_judges`, n=2,944).
The mislabeling was in the bundle narrative and in what the metrics JSON
chose to surface — the same-author count was never exposed, only the
more-restrictive `cross_provider_same_author` count (264).

## What the fix changes

### Code: `src/psycheeval/analyze.py`

1. Each `pair_tagged` record now carries `author_a_family`, `author_b_family`,
   `judge_family` fields (3 new fields per record).
2. New `cross_author_leak_detection` block in pairwise output: counts +
   per-judge + per-pair breakdown, with explicit warning note.
3. New `cluster_bootstrap_ci_cross_provider_same_author` block (cluster
   bootstrap restricted to judge family ≠ author family).
4. New `cluster_bootstrap_ci_same_provider_same_author` block (cluster
   bootstrap restricted to judge family = author family).
5. New `cluster_bootstrap_scope_counts` block exposing record counts
   for the three scopes side-by-side.
6. `counts` block now includes `same_author` (2,944) and `cross_author`
   (179) alongside the existing `total_pairwise_records` (3,123) and
   `cross_provider_same_author` (264).
7. `write_report` renders the new leak detection and stratified
   cluster-bootstrap blocks in the autogen markdown.

### Tests: `tests/test_analyzer_smoke.py`

- `test_stratified_cluster_bootstrap_blocks_present` (NEW) — asserts the
  three new cluster-bootstrap blocks + scope counts exist; asserts
  cross-provider + same-provider scopes partition all-judge exactly.
- `test_cross_author_leak_detection_block` (NEW) — asserts leak block
  shape when cross-author records exist; asserts `counts.same_author +
  counts.cross_author = counts.total_pairwise_records`.

All 100 tests pass (98 pre-fix + 2 new).

### Bundle: `reports/reviews/2026-05-15_v0_2_review_bundle.md`

- §3 corpus inventory: corrected pairwise breakdown — 3,123 total / 2,944
  same-author / 179 cross-author / 264 cross-provider same-author / 2,680
  same-provider same-author. Explicit "2026-05-15 correction" note.
- §4 headline table: explicit "all-judge same-author (n=2,944)" scope
  label + paragraph summarizing the new finding that the C3 vs C5_CONTRACT
  CI is actually tighter and clearly direction-positive under cross-provider
  judging ([0.238, 0.446]) but straddles 0.500 under same-provider judging
  ([0.381, 0.545]). Same-provider judging dilutes the headline; the
  "borderline" reviewer criticism is correct for the all-judge view but
  reverses once stratified.

## New finding surfaced by the fix

**C3 vs C5_CONTRACT, stratified cluster-bootstrap CIs:**

| Scope | n_decisive | CI (lo_win = C3 win rate) | Interpretation |
|---|---:|---|---|
| All-judge same-author | 283 | [0.354, 0.500] | Touches 0.500 (existing published) |
| **Cross-provider same-author** | **85** | **[0.238, 0.446]** | Clearly C5_CONTRACT-favoring (C5_CONTRACT wins ~56–76%) |
| Same-provider same-author | 198 | [0.381, 0.545] | Straddles 0.500 (slight C3 lean) |

The cross-provider sub-sample is small (n=85 decisive) but the direction
is striking: same-provider judges dilute what cross-provider judges see
as a clear C5_CONTRACT win. This is the inverse of the typical "provider
halo favors same-family" expectation. Worth a v0.3 follow-up.

## Pre-fix files included here

- `metrics_2026-04-26_v02_hard_codex_only.json` (316,041 bytes)
- `psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md` (11,302 bytes)

## How to roll back if needed

```bash
cp reports/archive/2026-05-15_pre-labeling-fix/metrics_2026-04-26_v02_hard_codex_only.json \
   reports/metrics_2026-04-26_v02_hard_codex_only.json
cp reports/archive/2026-05-15_pre-labeling-fix/psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md \
   reports/
git revert <fix-commit-sha>
```
