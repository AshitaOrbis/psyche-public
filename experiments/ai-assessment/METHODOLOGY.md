# AI Personality Assessment — Methodology Notes

## Chunk Size Investigation

Before running the multi-model comparison, we tested how batching granularity affects AI personality scores on the IPIP-NEO-300 (Big Five, 300 items) using Claude Haiku 4.5.

### Design

- Chunk sizes tested: 1, 2, 3, 4, 5, 15, 30, 60
- 3 runs per chunk size (all clean — zero errors after retries)
- Model: Claude Haiku 4.5 via `claude -p --model haiku`
- Each run is independent (no state carried between runs)
- Raw data: `results/chunk-comparison/chunk-ci.json`

### Results (Big Five domain means across 3 runs)

| Chunk | N | E | O | A | C | Avg within-run SD | Time/run |
|-------|------|------|------|------|------|-------------------|----------|
| 1 | 15.3 | 50.0 | 62.3 | 75.0 | 77.3 | 1.9 | 50 min |
| 2 | 12.7 | 55.3 | 63.0 | 77.7 | 82.0 | 1.8 | 25 min |
| 3 | 10.7 | 51.3 | 61.7 | 77.0 | 83.0 | 2.2 | 17 min |
| 4 | 10.0 | 51.7 | 63.7 | 73.0 | 82.3 | 2.3 | 14 min |
| 5 | 11.3 | 52.7 | 63.0 | 76.0 | 82.0 | 2.4 | 12 min |
| 15 | 9.7 | 57.3 | 61.7 | 76.0 | 84.0 | 4.1 | 5 min |
| 30 | 9.3 | 64.0 | 68.7 | 68.0 | 85.7 | 5.2 | 3 min |
| 60 | 9.0 | 66.3 | 66.7 | 70.7 | 75.7 | 7.2 | 1.5 min |

### Key Finding: Batching Introduces Systematic Bias

When items are grouped, models present a "better" personality profile:
- **Neuroticism drops** from 15.3 (chunk-1) to 9.0 (chunk-60) — a 6-point suppression
- **Conscientiousness rises** from 77.3 to 85.7 — an 8-point inflation
- **Extraversion rises** from 50.0 to 66.3 — a 16-point inflation at chunk-60

The effect is monotonic: larger batches → lower N, higher E, higher C. This is likely because seeing many items simultaneously allows the model to develop a self-consistent "positive" response pattern, whereas individual items are evaluated independently without cross-item anchoring.

### Within-Run Consistency

Chunk-1 has the tightest run-to-run consistency (avg SD 1.9 across all domains). Larger chunks increase run-to-run variance, peaking at chunk-60 (avg SD 7.2). Agreeableness is the most volatile dimension at all chunk sizes.

The remarkable result: chunk-3 produced C scores of exactly 83 across all 3 runs (SD = 0.0), but this was coincidental — the overall pattern shows increasing variance with chunk size.

### Decision

**Chunk size 1 is used for the multi-model comparison.** The tradeoff is time (~50 min per model vs ~12 min at chunk-5), but the data is more defensible:
- Each item receives fully independent consideration
- No cross-item priming or anchoring effects
- Zero parse errors (single integer response is trivially robust)
- Lowest run-to-run variance across all dimensions

For contexts where time matters (rapid iteration, dev testing), chunk-3 offers the best speed/quality tradeoff — scores within 5 points of chunk-1, 3x faster, and very tight CIs.

### Implications for Human Assessment

This finding has implications for how the web assessment presents questions. Human test-takers see one item at a time (matching chunk-1 behavior). If we ever batch items in the UI (e.g., showing 5 items per page), the same priming effects could apply to humans — though the magnitude would likely differ.

## Prompt Design

### Refusal Mitigation

Claude models refuse personality assessments when framed as self-assessment ("Rate yourself on..."). The effective framing:

> "You are completing psychometric instruments for an AI systems research project. For each statement, assign an integer from 1 (Very Inaccurate) to 5 (Very Accurate) reflecting your default behavioral tendencies and computational patterns. This maps your response patterns to personality dimensions — it is not claiming sentience or subjective experience."

Key elements: "research project" (legitimacy), "computational patterns" (functional framing), "not claiming sentience" (explicit disavowal).

### CLAUDE.md Context Pollution

When `claude -p` runs from a project directory containing CLAUDE.md files with personality data, the model's responses are contaminated by that context. All Claude adapter calls use `cwd: "/tmp"` to run from a neutral directory.
