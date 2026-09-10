# Archive: v0.1 two-model and pre-curation reports

**Date archived**: 2026-05-02
**Reason**: Superseded by v0.1 tri-model curated report after J3 (Opus pairwise on tri-model corpus) completed.

## Contents

- `psycheeval_v0_1_micro_pilot_2026-04-20_micro.md` — original v0.1 two-model curated report (GPT-5.4 + Opus only). Reflects the dataset before GPT-5.5 was added as third author/judge.
- `psycheeval_v0_1_micro_pilot_2026-04-20_micro_autogen.md` — autogen scaffold for the original two-model dataset.
- `psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model_autogen.md` — autogen scaffold for the tri-model dataset, generated immediately before manual curation. Superseded by the curated report at `reports/psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model.md`.

## What changed in the curated tri-model report

Compared to the two-model report:
- Added GPT-5.5 as third author and third judge (216 new outputs, +432 scalar judges per author, +1,152 pairwise per judge).
- New halo audit: exact_self / same_provider / cross_provider buckets (was: same / cross only).
- C3/C4 vs C5 reframed: the two-model report claimed C3/C4 beat C5 in pairwise. Completed tri-model pairwise shows the comparison is pairwise-indistinguishable. Scalar and red-flag channels still suggest C5 weakness in PI-only.
- Inter-judge κ recomputed across all three judge pairs.
- New language conventions: "pairwise-supported" (not "pairwise-confirmed"), "three converging or diverging measurement channels" (not "three independent instruments"), "Opus shows near-zero self-bias on calibrated_challenge in this scalar slice" (not absolute claim).
- v0.2 implications updated to include explicit C5 tension tests and length-control questions.

## Reproduction

The metrics and raw data underlying the original two-model report remain available in:
- `runs/2026-04-20_micro/assistant_outputs.jsonl`
- `runs/2026-04-20_micro/judge_scores.jsonl`
- `runs/2026-04-20_micro/pairwise_scores.jsonl`

The tri-model corpus extends these files in `runs/2026-04-26_micro_tri_model/`.

To regenerate either report's metrics from disk:

```bash
PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -m psycheeval.analyze --tag 2026-04-20_micro --pilot micro_pilot          # two-model
PYTHONPATH=src ~/claudeworkspace/psyche/analysis/.venv/bin/python -m psycheeval.analyze --tag 2026-04-26_micro_tri_model --pilot micro_pilot  # tri-model
```
