# Archive: v0.1 pre-brief-revision

**Archived**: 2026-04-24
**Reason**: Pre-revision snapshot taken before applying `docs/report_revision_brief.md` guidance.

## Contents

- `psycheeval_v0_1_micro_pilot_2026-04-20_micro.md` — original curated v0.1 report (one-table design, all-judge mains)
- `metrics_2026-04-20_micro.json` — original metrics (flat `by_condition`, no cross-provider primary, no PI/PS splits)

## What changed on the main branch

- `analyze.py` rewritten to emit cross-provider-judged tables as primary, PI/PS subsets, C5 isolated to PI-only, all-judge means demoted to appendix.
- Metrics JSON regenerated with new structure (`primary_cross_provider`, `secondary_all_judges`, `pairwise`).
- Curated report rewritten to integrate the brief's narrative sections, reframings, and v0.2 plan.
- Pairwise scores: brief-driven judging run added ~3500 scores that didn't exist in this snapshot (v0.1 skipped pairwise).

## Provenance note

Impact on scalar means: trivial in magnitude but material in framing. The numeric tables here included same-provider halo rows inside the main "Dimension means by condition" table, which the brief identified as the primary methodological inconsistency.
