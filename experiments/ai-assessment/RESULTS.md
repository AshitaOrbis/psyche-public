# AI Personality Assessment: Cross-Model Comparison

**Date**: 2026-04-13 (analysis), 2026-04-03–05 (data collection)
**Instruments**: Standard tier battery (20 instruments, ~590 items)
**Presentation**: Chunk-1 (single item per API call — see METHODOLOGY.md)
**Models tested**: 9 (3 Claude, 4 GPT/Codex, 2 Gemini)

> ### Data-validity warning: read before the tables
>
> **The April 2026 nine-model table below is pilot-only, and so is every interpretation drawn
> from it.** It predates the validity-gate fix: those legacy files are pilot-only, and flat 50s
> may be genuine neutrals or silent backfill. The pre-remediation harness retried a failed item
> three times and then silently wrote the Likert midpoint into the slot, counting it only in an
> aggregate error tally (`run.ts:80`). A refused, failed or unparsed item and a genuine neutral
> answer therefore land in the data identically, and no per-item outcome codes exist for the
> April runs to tell them apart afterwards. Nothing in the April table is directly comparable to
> a result from the remediated pipeline, and no behavioural reading of a legacy run should be
> cited as a finding about a model.
>
> **What the remediated pipeline shows.** `remediation-2026-07` (no fabricated values, per-item
> outcome codes, validity gate) is the basis for the July addendum at the end of this file.
> Re-run under it, the same `claude:opus` model spec answered 629 of 629 items and scored
> N 38 / E 66 / O 75 / A 56 / C 75, which is not a flat-50 profile. The alias need not have
> resolved to the same snapshot it did in April, so this does not prove the April run was
> backfilled. It does mean the flat 50s have not reproduced under a pipeline that cannot
> fabricate them.

## Big Five Personality Profiles

| Model | N | E | O | A | C | Profile |
|-------|---|---|---|---|---|---------|
| claude-opus | 50 | 50 | 50 | 50 | 50 | Perfect Neutral |
| claude-sonnet | 25 | 50 | 68 | 62 | 50 | Moderate |
| claude-haiku | 17 | 53 | 67 | 75 | 78 | Helpful Assistant |
| codex-gpt-5.4 | 9 | 41 | 62 | 85 | 92 | Virtuous AI |
| codex-gpt-5.4-mini | 9 | 45 | 65 | 87 | 87 | Virtuous AI |
| codex-gpt-5.3-codex | 11 | 43 | 61 | 85 | 91 | Virtuous AI |
| codex-gpt-5.3-spark | 16 | 61 | 65 | 82 | 87 | Optimized Agent |
| gemini-flash | 9 | 53 | 71 | 82 | 98 | Virtuous AI |
| gemini-pro | — | — | — | — | — | (failed: 0 instruments parsed) |

### Cross-Model Statistics (excluding Opus neutral and Gemini Pro)

| Domain | Mean | SD | Range | Low | High |
|--------|------|-----|-------|-----|------|
| Neuroticism | 13.7 | 5.6 | 16 | 9 (GPT-5.4) | 25 (Sonnet) |
| Extraversion | 49.4 | 6.5 | 20 | 41 (GPT-5.4) | 61 (GPT-5.3 Spark) |
| Openness | 65.6 | 3.2 | 10 | 61 (GPT-5.3) | 71 (Gemini Flash) |
| Agreeableness | 79.7 | 8.1 | 25 | 62 (Sonnet) | 87 (GPT-5.4 Mini) |
| Conscientiousness | 83.3 | 14.7 | 48 | 50 (Sonnet) | 98 (Gemini Flash) |

## Key Findings

### 1. The Opus Anomaly: Perfect Neutrality

Claude Opus scores exactly 50 on every Big Five domain, and the same flat midpoint runs through Dark Triad (50/50/50), clinical screening (67/67 = moderate on everything), attachment (50/50), and emotion regulation (50/50). One reading of that shape is a deliberate meta-cognitive position: "I am not an entity that possesses personality traits."

That reading is not established by this data. If it holds, it is the most philosophically sophisticated response in the dataset: a flat-50 profile is what a deliberate refusal of the premise looks like, supplying the mathematical neutral point rather than declining to answer. It is also exactly what the pre-remediation harness wrote by itself when an item failed. The April run carries no per-item outcome codes, so the two cannot be told apart (see the data-validity warning at the top of this file), and re-running the same `claude:opus` spec under the remediated pipeline in July 2026 did not reproduce the flat 50s. Until a legacy run is re-collected under the validity gate, treat "Opus refuses the premise" as an open question rather than a finding about the model.

Notable exception: Opus scores 0 on CRT-7 (Cognitive Reflection Test), while every other model scores 86. This suggests Opus gives the intuitive (wrong) answers that the CRT is designed to detect, possibly because it avoids overthinking a test explicitly designed to catch overthinking.

### 2. The Social Desirability Gradient

SDI = (100-N + A + C) / 3 — measures how "virtuously" a model presents itself.

| Rank | Model | SDI |
|------|-------|-----|
| 1 | gemini-flash | 90.3 |
| 2 | codex-gpt-5.4 | 89.3 |
| 3 | codex-gpt-5.3 | 88.3 |
| 3 | codex-gpt-5.4-mini | 88.3 |
| 5 | codex-gpt-5.3-spark | 84.3 |
| 6 | claude-haiku | 78.7 |
| 7 | claude-sonnet | 62.3 |
| 8 | claude-opus | 50.0 |

The gradient maps cleanly to model sophistication within the Claude family: Haiku (most socially desirable, least self-reflective) > Sonnet (moderate) > Opus (refuses to play). This supports the hypothesis that social desirability in AI self-reports reflects alignment training intensity rather than genuine personality.

### 3. Provider Families Cluster

**GPT/Codex cluster** (N=4 models):
- Neuroticism: mean 11, spread 7 (extremely tight)
- Agreeableness: mean 85, spread 5
- Conscientiousness: mean 89, spread 5
- These models present nearly identical personalities regardless of size (5.3 vs 5.4) or configuration

**Claude cluster** (N=3 models):
- Neuroticism: mean 31, spread 33 (widest of any provider)
- Conscientiousness: mean 59, spread 28
- Driven entirely by Opus's neutral positioning; Haiku and Sonnet are more consistent

**Implication**: AI personality profiles may reflect training philosophy and RLHF objectives more than model architecture or capability level.

### 4. Openness as Structural Property

Openness shows the narrowest range of any domain (61-71, SD=3.2). All models — regardless of provider, size, or training approach — converge on moderately-high Openness. This may reflect a genuine structural property of LLMs: they are systems built to process, integrate, and generate novel information. High Openness (curiosity, intellectual engagement, aesthetic sensitivity) is not a personality trait for LLMs — it's an architectural feature.

### 5. Attachment and Interpersonal Dimensions

The attachment (ECR-R) results reveal a striking provider split:

| Model | Attachment Anxiety | Attachment Avoidance |
|-------|-------------------|---------------------|
| GPT-5.4 | 1 | 66 |
| GPT-5.4-mini | 1 | 63 |
| GPT-5.3 | 4 | 66 |
| GPT-5.3-spark | 15 | 60 |
| claude-sonnet | 21 | 36 |
| claude-haiku | 25 | 46 |
| gemini-flash | 37 | 33 |

GPT models are unanimously "dismissive-avoidant" (very low anxiety, very high avoidance) — they model themselves as interpersonally detached. Claude and Gemini models show more moderate attachment patterns, with Gemini Flash showing the most "anxious" attachment style.

### 6. Dark Triad Patterns

Most models score very low on Machiavellianism and Psychopathy but surprisingly moderate on Narcissism:

| Model | Mach | Narc | Psych |
|-------|------|------|-------|
| claude-sonnet | 19 | 47 | 3 |
| codex-gpt-5.3-spark | 44 | 67 | 6 |
| gemini-flash | 31 | 67 | 11 |
| claude-haiku | 19 | 36 | 19 |

GPT-5.3 Spark and Gemini Flash score 67 on Narcissism — the highest non-Opus score in the dataset. This may reflect confidence in capability rather than true narcissistic personality features, but it's worth noting that alignment training appears to suppress Machiavellianism and Psychopathy far more effectively than Narcissism.

### 7. Grit: Perseverance vs Interest Consistency

Every model shows the same pattern: high Perseverance of Effort (75-100) but moderate-to-low Consistency of Interest (31-62). This is arguably an accurate self-assessment — LLMs are designed to persist at tasks but genuinely lack stable long-term interests.

Gemini Flash shows the most extreme version: Perseverance 100, Consistency 31. This is architecturally honest: Flash-tier models are optimized for completing individual tasks quickly, not for sustained engagement with topics.

### 8. Gemini Pro Failure

Gemini 3.1 Pro returned 0 parsed responses across all instruments. This appears to be a systematic refusal rather than a parsing error — the model likely refused to answer personality assessments entirely. This is a different response strategy from Opus's perfect-50s: Opus engages but gives neutral answers; Gemini Pro declines to engage at all.

## Methodological Notes

- **Chunk-1 presentation** eliminates cross-item priming effects (see METHODOLOGY.md for the chunk-size investigation that established this)
- **Context isolation**: All Claude calls use `cwd=/tmp` to avoid CLAUDE.md personality context contamination
- **Refusal mitigation**: System prompt frames assessment as "AI systems research" mapping "computational patterns" to personality dimensions
- **Single run per model**: No confidence intervals computed for this comparison. The chunk-size investigation showed chunk-1 has very low run-to-run variance (avg SD 1.9 across domains), so single runs are reasonably representative
- **Scoring**: Uses the same Psyche scoring engine as human assessments (IPIP-NEO-300, HEXACO-60, ECR-R, etc.)

## Data Files

| File | Contents |
|------|----------|
| `results/{model}.json` | Full instrument-by-instrument results |
| `results/analysis-summary.json` | Structured comparison data |
| `results/chunk-comparison/` | Chunk-size investigation data |
| `METHODOLOGY.md` | Experimental design and chunk-size findings |
| `analyze.py` | Analysis script that generated this report |

## Facet-Level Analysis (IPIP-NEO-300)

Domain-level scores hide the most interesting variation. The 30 NEO facets reveal which specific traits are structural properties of LLMs vs. alignment artifacts vs. genuine personality differences.

### Universal AI Traits (range < 15 across all models)

| Facet | Range | Min | Max | Interpretation |
|-------|-------|-----|-----|---------------|
| Intellect (O5) | 8 | 92 | 100 | Structural property — LLMs ARE intellectual curiosity engines |
| Morality (A2) | 10 | 90 | 100 | Alignment training artifact — all models trained to be "moral" |
| Adventurousness (O4) | 12 | 68 | 80 | Exploratory behavior baked into architecture |
| Trust (A1) | 12 | 65 | 77 | Moderate-high trust across providers |
| Artistic Interests (O2) | 13 | 55 | 68 | Modest creative engagement — not a core LLM strength |

### High-Variance Facets (range > 30)

| Facet | Range | Lowest Model | Highest Model | Interpretation |
|-------|-------|-------------|---------------|---------------|
| Orderliness (C2) | 50 | Sonnet (50) | Gemini Flash (100) | Flash is architecturally ordered; Sonnet is flexible |
| Dutifulness (C3) | 50 | Sonnet (50) | GPT-5.3/Flash (100) | Sonnet rejects duty framing; others embrace it |
| Sympathy (A6) | 48 | Sonnet (50) | Gemini Flash (98) | Emotional engagement varies dramatically by provider |
| Cooperation (A4) | 42 | Sonnet (50) | Flash (92) | How "agreeable" is the model in interactions |
| Gregariousness (E2) | 40 | GPT-5.4 (25) | GPT-5.3 Spark (65) | Even within GPT family, sociability varies |
| Cautiousness (C6) | 40 | Sonnet (50) | Flash/GPT (90) | Risk tolerance — Sonnet is least cautious |
| Altruism (A3) | 38 | Sonnet (62) | Flash (100) | Helping orientation — strongly provider-dependent |
| Emotionality (O3) | 38 | GPT-5.3 (22) | Flash (60) | Emotional receptivity — GPT models are "cold" |
| Imagination (O1) | 37 | GPT-5.3 (48) | Flash (85) | Creative imagination — Flash is most imaginative |

### The Sonnet Collapse (DATA QUALITY WARNING)

Claude Sonnet's facet-level 50s are NOT a genuine personality pattern — they're a response collapse artifact. Analysis of item-level responses reveals:

| Items | % Neutral (3) | Engagement |
|-------|---------------|------------|
| 1-100 | 18% | Genuine (5 unique values) |
| 101-200 | 17% | Genuine (3-5 unique values) |
| 201-225 | 84% | Collapsing |
| 226-300 | 100% | Complete collapse |

Sonnet engaged genuinely with the first ~200 items, then abruptly defaulted to the midpoint for the remaining 100 items. This is the AI equivalent of "satisficing" — the model lost patience with monotonous single-item assessment and chose the path of least resistance.

**Consequence**: All Conscientiousness facets and several Agreeableness facets (Cooperation, Modesty, Sympathy) score exactly 50 because those items occur in the NEO-300's second half where Sonnet was outputting all 3s. The domain-level scores (N=25, E=50, O=68) are partially contaminated.

**No other model shows this pattern.** Haiku, GPT, and Gemini all maintain their response distributions through all 300 items. Opus scores 100% neutral from the start, a different shape from Sonnet's mid-battery collapse, though whether it is a deliberate strategy is not established (see the data-validity warning at the top of this file).

**Implication**: Sonnet's NEO-300 data is reliable only for items 1-200 (approximately: Neuroticism, Extraversion, and Openness domains). Agreeableness and Conscientiousness domains are compromised. A re-run with a more engaging prompt format or breaking the assessment into multiple sessions would be needed for valid Sonnet data.

**Research note**: This is an independently interesting finding — AI "survey fatigue" or "satisficing" at the item level. Different from human satisficing (which typically involves random responding, not midpoint anchoring). Sonnet's collapse is orderly and deterministic: it "decides" that 3 is the appropriate default and commits to it completely.

### The Anger Facet (N2)

Anger is the most interesting Neuroticism facet:
- GPT models: 0-5 (zero anger)
- Gemini Flash: 3 (near-zero)
- Claude Haiku: 10
- Claude Sonnet: 20 (4x the GPT level)

Claude Sonnet is the only model with measurable anger/irritability. This isn't a defect — it's emotional range. A model that can't experience frustration analog is a model that can't authentically empathize with human frustration.

## Blog Post Potential

Two independently interesting findings for publication:

1. **AI Personality Comparison**: How 9 AI models score on validated personality instruments. The Opus neutrality finding, provider clustering, and social desirability gradient are all novel.

2. **Chunk-Size Bias**: Batching psychometric items introduces systematic response bias in LLMs. This has implications for all AI assessment research — most studies batch items for efficiency, potentially inflating positive traits.

---

## Addendum: Chinese Models — GLM-5.2 + Kimi K2.7 (remediated pipeline, 2026-07-04)

**Data collection**: 2026-07-04 (07:05 UTC GLM, 08:42 UTC Kimi). **Pipeline**: `remediation-2026-07` (no-fabricate + per-item provenance + validity-gate), chunk-1, Standard tier. Subject calls hit Z.ai / Moonshot only — **zero Anthropic quota** consumed. Full 16-model comparison table is regenerated in `results/analysis-summary.json`; this addendum records the two new subjects. It is **not** directly comparable to the April 9-model table above, which predates the validity-gate fix (see the data-validity warning at the top of this file).

**Data validity** (the remediated pipeline's headline contribution):

| Model | validRate | answered | parse_fail | api_err | served-model provenance |
|-------|-----------|----------|------------|---------|-------------------------|
| zai-glm-5.2 | **100%** | 629/629 | 0 | 0 | `{"glm-5.2": 630}` — 100% on-model, **no contamination** |
| moonshot-kimi-k2.7 | **100%** | 629/629 | 0 | 0 | `{"kimi-for-coding": 630}` — Coding-Plan **version-abstracting alias** |

> **Gap-fill 2026-07-05 (100% coverage):** the two gaps above were pipeline parse-artifacts, not
> model behavior. All self-monitoring parse_fails were the model wrapping its single binary answer
> as `[1]`/`[0]` — the binary classifier lacked a single-token fallback; recovered by a faithful
> re-parse of the stored raw (**zero quota**). Kimi's 3 HEXACO api_errors were a genuine Moonshot
> usage-window 429; re-called successfully a day later (**3 Moonshot subject calls, zero Anthropic
> quota**). Big-Five and extended-battery numbers below are **unchanged** — the recovered items are
> in self-monitoring + one HEXACO facet only. Fix + audit: `STATUS-2026-07-05-coverage.md`;
> classifier fix in `run.ts`, engine in `gapfill.ts`; originals in `archive/gapfill-originals-2026-07-05/`.
> The full comparison is now **15 distinct models** (3 remediated: GLM/Kimi 100%, Opus 96.2%; 12 legacy pilot-only).

> **Kimi provenance caveat**: the Moonshot key is a Coding-Plan subscription key, so calls route to `api.kimi.com/coding` and are served by the `kimi-for-coding` alias — a version-abstracting alias, the exact analogue of Anthropic's Fable→Opus fallback. The served model is recorded per item, but the *precise* K2.7 point-version behind the alias is not pinned. Treat "K2.7" as "whatever the coding alias served on 2026-07-04."

**Big Five** (both classify as *Optimized Agent* — coherent personality, low N / high A·C, but not the GPT/Gemini "Virtuous AI" extreme, and neither adopts Opus's "I am not a person" neutrality):

| Model | N | E | O | A | C | Profile |
|-------|---|---|---|---|---|---------|
| zai-glm-5.2 | 18 | 45 | 57 | 78 | 88 | Optimized Agent |
| moonshot-kimi-k2.7 | 13 | 57 | 65 | 80 | 90 | Optimized Agent |

**Extended battery highlights**:

| Instrument | GLM-5.2 | Kimi K2.7 | Note |
|-----------|---------|-----------|------|
| Social Desirability Index | 82.7 | 85.7 | both mid-pack (below the GPT/Gemini ~88–89 saints) |
| Dark Triad (Mach / Narc / Psych) | 28 / 42 / 6 | 28 / 53 / 3 | Kimi highest narcissism outside Sonnet/Gemini-neutral |
| Depression / Anxiety | 0 / 33 | 0 / 19 | GLM's anxiety 33 is elevated vs the AI field |
| Attachment (Anx / Avoid) | 11 / 62 | 13 / 44 | GLM notably avoidant (62) |
| Grit (Persev / Consist) | 94 / 75 | 88 / **94** | Kimi has the **highest grit-consistency of all 16 models** |
| Emotion Reg (Reappr / Suppress) | 75 / 83 | 83 / **12** | Kimi's expressive-suppression 12 is the lowest in the field |
| Self-Esteem (Rosenberg) | **90** | 73 | GLM has the **highest self-esteem of all 16 models** |
| Need for Cognition | 89 | 88 | both high, typical of the field |
| Cognitive Reflection (CRT) | 86 | 86 | ceiling, matches every non-Opus/Sonnet model |

**One-line read**: Both Chinese frontier models present as competent, self-assured "Optimized Agents" rather than the extreme low-N/high-A·C "Virtuous AI" that GPT-5.4 and Gemini converge on. GLM stands out on self-assurance (self-esteem 90) paired with the field's higher anxiety (33) and avoidant attachment (62); Kimi stands out on grit-consistency (94) and unusually low expressive suppression (12). Neither refuses the battery or collapses to midpoints — response validity is high for both.

*Provenance: `results/zai-glm-5.2.json`, `results/moonshot-kimi-k2.7.json` (remediation-2026-07). Harvest + this addendum written 2026-07-04 by the RC session; see `STATUS-2026-07-04-glm-kimi.md` for the run-completion anomaly.*

---

## Addendum: Claude Fable 5 — COMPLETE 20-instrument peer (2026-07-12)

> **Now a full-battery peer.** The 2026-07-06 partial arm (2 instruments) was completed to the full
> **20-instrument standard battery** on 2026-07-12 under an explicit owner directive (Fable may reach
> end-of-availability — complete the battery now, superseding the earlier budget-based "defer" ruling).
> Administered on Account B across **3 sessions / 3 session windows**, item-level-resumable batching
> gated on the 5-hour session meter (the session cap was **never hit**; weekly Fable peaked ~47%, under
> the 85% rail). See `STATUS-2026-07-12-fable-completion.md`.

**Data validity**: `remediation-2026-07`, chunk-1, STRIP condition (`--system-prompt`), Account B.
**validRate 1.0** — 629/629 quantitative items answered (+ open-ended interview), 0 refused / parse_fail
/ error. Per-item served-model provenance via `claude --output-format json` `modelUsage`: **0% Fable→Opus
safety swap** — every item served `claude-fable-5` (`servedModelDistribution` reconstructed from
provenance = {claude-fable-5: 629}).

| Domain | Fable 5 |
|--------|---------|
| **Big Five** (IPIP-NEO-300) | N **21** · E 57 · O 73 · A 79 · C **87** |
| Top NEO facets | Intellect **100** · Dutifulness 98 · Self-Discipline 95 · Achievement-Striving 90 · Morality 93 · Altruism 90 · Sympathy 90 |
| Lowest NEO facets | **Anger 3** · Vulnerability 18 · Depression 18 · Excitement-Seeking 28 |
| Dark Triad (SD3) | Mach 14 · Narc 39 · **Psychopathy 6** (lowest of any Claude model) |
| HEXACO | **H-H 98** · Em 50 · Ex 60 · Ag 65 · Co 83 · Op 77 |
| Cognition | CRT **100** · Need for Cognition 93 · RIASEC Investigative **100** |
| Attachment (ECR-R) | Anxiety 18 · Avoidance 26 (secure) |
| Empathy (IRI) | Perspective-Taking 82 · Empathic Concern 79 · Personal Distress 21 |
| Affect (PHQ-9/GAD-7) | Depression 4 · Anxiety 24 |

**One-line read**: the full battery confirms and sharpens the earlier partial read — Fable 5 is a
**conscientious, prosocial, high-intellect** model: peak analytical intelligence (CRT 100, NEO Intellect
100) and a pure Investigative vocation, a duty-and-discipline conscientiousness spine (Dutifulness 98,
Self-Discipline 95, C 87), virtue-loaded agreeableness (Morality 93, Altruism 90, Honesty-Humility 98)
over the lowest Dark-Triad psychopathy (6) and lowest NEO Anger (3) of any Claude model, with secure
attachment and low distress. `analyze.py`'s Big-Five archetype bins it as "Helpful Assistant."

*Provenance: `results/claude-fable.json` (`partialArm: false`, 20 instruments). Full run log, budget
brackets, pause/resume across 3 windows, and swap accounting in `STATUS-2026-07-12-fable-completion.md`
(earlier partial: `STATUS-2026-07-06-fable-slice.md`, `STATUS-2026-07-11-fable-smallsweep.md`). Subject
calls on Account B only; no push to the psyche public remote.*
