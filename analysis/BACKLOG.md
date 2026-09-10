# Psyche Analysis Backlog

Deferred improvements and future experiments.

## ~~Critical: Re-Run Original Corpus LLM Analysis~~ COMPLETED

**Status**: COMPLETED — 2026-03-04
**Archive**: `profiles/analysis/archive/2026-03-03-pre-chunking-fix/`

### Resolution

Fixed three compounding bugs (per-sample truncation, max_samples limit, chunk budget). Expanded corpus from 3 to 5 sources (311K → 1.47M words) by adding SMS old-phone data and Facebook Messenger conversations. Ran full 13-level analysis (per-source, per-era, per-medium, full corpus).

**Key results:**

| Dimension | Old | New | Delta |
|-----------|-----|-----|-------|
| N | 62 | 51.1 | -10.9 |
| E | 18 | 28.3 | +10.3 |
| O | 92 | 88.6 | -3.4 |
| A | 32 | 36.4 | +4.4 |
| C | 38 | 61.4 | **+23.4** |

C shift (+23.4) was the truncation bug's primary casualty — academic papers (high C signal) were truncated to 2K words. The analysis also produced 13 levels of per-source, temporal, and per-medium comparisons. Research paper updated to v2 with all corrected scores, new Sections 3.8-3.9, and Appendix A.

**Output files**: `profiles/analysis/corpus/{level}-llm-claude.json`, `{level}-empath.json`, `comparison-summary.json`

### Cascading Effects (all addressed in paper v2)

- Table 4 merged scores recalculated
- Table 7 / S6 deltas recalculated (tighter range: 7.2-11.6 vs old 10.2-15.0)
- Self-enhancement analysis rewritten (C and N enhancement were partially artifact)
- Signal preservation pattern clarified (preserved O/E, amplified N, genre-inflated A, bracketed C)
- Differential personality experiment baseline updated in this BACKLOG

---

## Future Experiments

### ~~Differential Personality Across Narrative Perspectives~~ COMPLETED

**Status**: COMPLETED — 2026-03-19
**Cost**: ~$3-4 (6 levels x Opus LLM inference, ~50 min total)
**Output files**: `profiles/analysis/narrative-{v2-contact-a,v2-third-person,v2-dual-pov,contact-b-contact-b,contact-b-third-person,contact-b-dual-pov}-{llm-claude,empath}.json`

### Results

| Level | N | E | O | A | C | Mean |Δ| | Category |
|-------|-----|-----|-----|-----|-----|---------|----------|
| Original corpus | 51.1 | 28.3 | 88.6 | 36.4 | 61.4 | — | Baseline |
| v2-contact-a | — | — | — | — | — | — | Interlocutor (different person) — withheld |
| contact-b-contact-b | — | — | — | — | — | — | Interlocutor (different person) — withheld |
| v2-third-person | 63.7 | 26.7 | 89.7 | 35.7 | 64.0 | **3.7** | Third-person (about the author) |
| contact-b-third-person | 71.0 | 24.5 | 90.0 | 38.0 | 60.0 | **5.6** | Third-person (about the author) |
| v2-dual-pov | — | — | — | — | — | — | Dual PoV (blended, contains an interlocutor) — withheld |
| contact-b-dual-pov | — | — | — | — | — | — | Dual PoV (blended, contains an interlocutor) — withheld |
_Withheld: the two interlocutor rows measure other private individuals from the subject's correspondence. No owner ruling reaches other people's derived personal data (DECISIONS `SP-owner-psychometrics-public`, 2026-08-23, explicit carve-out), so their values and the quantities that recover them are not published here. The author-perspective rows are retained under that same ruling._

### Verdict: **Signal preservation supported** (Decision Matrix row 1)

Interlocutor profiles differ from the author by more than the author-vs-author variance, while third-person profiles about the author stay close (3.7, 5.6). _The interlocutor magnitudes, the dual-PoV values and the per-domain claim about an interlocutor are withheld — see the note above. Nothing here should be read as a validated measurement of another person's personality: these are LLM estimates of narratives written from those perspectives._

The N inflation (+13 to +20) across all perspectives is likely a systematic Opus bias (first-person narrative genre effect), but E, O, A, C all show perspective-dependent differentiation.

**Paper impact**: Strengthens signal preservation claim. Add as Section 3.8 or Experiment 2, upgrade "suggestive" to "supported."

### Motivation from Initial Results

The the author PoV narrative analysis (Section 3.7 of the research paper) produced a pattern of extreme trait preservation (O, E) with moderate trait mean-regression (A, C, N). However, the results cannot distinguish between two explanations:

1. **Signal preservation**: Narrative generation genuinely encodes personality signal, with extreme traits surviving transformation better than moderate ones
2. **Model-invariant output**: Opus produces similar personality profiles regardless of input, and the observed pattern reflects LLM inference biases rather than preserved signal

The differential experiment directly tests this: if interlocutor PoV files produce the SAME Big Five profile as the author PoV files, explanation #2 is supported and the "convergence" finding in the paper is substantially weakened.

### Input Files

Run the same LLM inference + Empath pipeline on ALL perspective files from the voice-clone narratives:

| File | Expected Personality | Reference Scores |
|------|---------------------|-----------------|
| `v2/author_first_person.md` | the author's personality (v2) | Already done: N=48-76, E=26-28, O=88 |
| `contact-b/author_first_person.md` | the author's personality (v3) | Already done: N=82, E=28, O=83 |
| `v2/contact-a_first_person.md` | (withheld — interlocutor input) | Should differ from the author if signal preserved |
| `contact-b/contact-b_first_person.md` | (withheld — interlocutor input) | Should differ from the author if signal preserved |
| `v2/third_person_account.md` | Opus's authorial voice / blended | May reveal Opus's "default" personality |
| `contact-b/third_person_account.md` | Opus's authorial voice / blended | Should correlate with v2 third-person |
| `v2/dual_pov_relationship.md` | Blended (both perspectives) | Should approximate average of pure PoVs |
| `contact-b/dual_pov_relationship.md` | Blended (both perspectives) | Should approximate average of pure PoVs |

### Hypotheses

1. Interlocutor PoV files should produce DIFFERENT Big Five scores than the author PoV files (different person -> different personality)
2. Third-person files should produce a blended signal (between the author and interlocutor, plus Opus's authorial tendencies)
3. Dual PoV should correlate with an average of the two pure PoV personalities
4. **Critical confound test**: If ALL perspectives produce the SAME personality -> Opus has a fixed "voice" regardless of intended perspective -> the convergent assessment paper's findings are substantially weakened

### Decision Matrix

| Outcome | Paper Impact | Action |
|---------|-------------|--------|
| Interlocutors differ from the author | Strengthens signal preservation claim | Add as Section 3.8, upgrade "suggestive" to "supported" |
| All perspectives same profile | Serious confound | Reframe Section 3.7 as methodological limitation, downgrade claims |
| Third-person = Opus default, PoVs differ | Mixed — signal preservation for PoV, but Opus leaks its personality into omniscient narration | Nuanced discussion in Section 4 |
| Partial differentiation | Most likely outcome | Quantify degree of differentiation, discuss implications |

### Implementation

Extend `analyze_narratives.py` with additional levels for each perspective file. The infrastructure already supports arbitrary file/source combinations via the `LEVEL_CONFIGS` dict.

### Quantitative Baseline from Initial Results

For reference, the the author PoV analysis produced these scores:

| Level | N | E | O | A | C | Words | Mean Δ |
|-------|---|---|---|---|---|-------|--------|
| Original corpus (corrected) | 51.1 | 28.3 | 88.6 | 36.4 | 61.4 | 101,005 | — |
| v2 (full) | 78 | 27 | 89 | 52 | 54 | 32,927 | 10.3 |
| v2-early | 76 | 26 | 88 | 49 | 47 | 24,998 | 11.0 |
| v3 | 75 | 25 | 91 | 56 | 69 | 23,876 | 11.4 |
| v2+v3 | 75 | 26 | 88 | 50 | 58 | 40,055 | 8.8 |

The interlocutor PoV scores need to differ by *more* than the within-the author variance (~8-11 mean Δ against the corrected baseline) to support differentiation. A critical finding would be if ALL perspective files produce essentially the same profile (within ~5 points per dimension), which would indicate model-invariant output rather than genuine personality encoding.

---

## PR 2: Computerized Adaptive Testing (CAT)

**Status**: Planned — depends on PR 1 (tiered battery, now complete)

### Components

1. **R Script**: `analysis/scripts/extract_irt_params.R` — One-time SAPA data extraction of GRM parameters from Harvard Dataverse (~500K respondents)
2. **GRM Engine**: `web/src/scoring/grm-engine.ts` — TypeScript Graded Response Model implementation (category probabilities, Fisher information, EAP theta estimation)
3. **CAT Controller**: `web/src/scoring/cat-controller.ts` — Per-facet adaptive testing with SE-based stopping (target SE < 0.30, min 3 items, max 10 items per facet)
4. **AdaptiveTestRunner**: `web/src/components/AdaptiveTestRunner.tsx` — UI for adaptive item presentation with convergence progress bars
5. **Item Banks**: `web/public/item-banks/big5-grm-params.json`, `hexaco-grm-params.json` — SAPA-calibrated IRT parameters
6. **CAT Instrument Definitions**: `web/src/instruments/cat-big5.ts`, `cat-hexaco.ts`
7. **Scoring Integration**: `scoreAdaptive()` in `web/src/scoring/engine.ts`
8. **Analysis Pipeline**: CAT score extraction in `merge.py` using `_theta_to_100()`

### Key Design Decisions

- CAT runs AFTER fixed-form (NEO-300/HEXACO-200), using fixed-form theta as informative prior
- Per-facet CAT: 30 independent mini-CATs for Big Five, 24 for HEXACO
- Fixed-form items excluded from CAT item pool (prevents response anchoring)
- Heavy tier only (Lite/Standard don't use CAT)

---

## ~~R4: Bound Generation Variance~~ COMPLETED (2026-04-04)

Second 1M narrative generated from identical pipeline inputs (same messages, discovery, outline, voice profile). Evaluated with 4 Opus runs. Result: mean |Δ| = 3.9 — identical to original (3.9), inside CI [3.4, 4.4]. CIs are valid for total uncertainty. Generation variance averages 4.9 pts across domains (C showed -12.5 shift, other domains <4.1). Output: `voice-clone/narratives/experiments/r4-second-generation/`.

---

## AI Model Personality Comparison

**Status**: In progress — chunk size investigation complete, multi-model runs pending.
**Location**: `experiments/ai-assessment/`

Running 8 AI models through the Standard tier battery (~590 items) to compare their default personality profiles. Models answer "as themselves" (not role-playing as a human). Each item is presented individually (chunk size 1) — see `experiments/ai-assessment/METHODOLOGY.md` for the chunk size investigation that established this as the optimal approach.

**Chunk size finding**: Batching items introduces systematic bias — N drops 6 points and C rises 8 points between chunk-1 and chunk-60. The effect is monotonic and likely caused by cross-item priming in batched presentations.

Models: Claude Opus/Sonnet/Haiku, GPT-5.4 (xhigh), GPT-5.4 (medium), GPT-5.3 Instant, Gemini 3.1 Pro, Gemini Flash.

**Blog post potential**: How different AI models "see themselves" on validated personality instruments. The chunk size bias finding is independently interesting (implications for how AI assessment methodology affects results).

---

## New-Run Experiments (from v4 analysis)

### ~~NEW-N-DEBIAS: Targeted N-Debiased Prompt~~ COMPLETED (2026-04-14)

3 Opus runs. N inflation reduced from +24 to +15 (38% reduction, 95% CI [12, 18]). Mean |Δ| improved from 11.4 to 6.2 (46%, CI [5.1, 7.4]). Other domains unaffected. Prompt should be default for narrative evaluation. Full results: `experiments/methodology-supplement/new-experiments-results.md`.

### ~~NEW-8: Third-Person Replication~~ COMPLETED (2026-04-14)

3 Opus runs. Mean |Δ| = 7.1 (SD=0.3, CI [6.2, 8.0]). Third-person delta highly stable and below interlocutor delta (10.7-12.3). Supports model-as-simulator claim. Full results: `experiments/methodology-supplement/new-experiments-results.md`.

### ~~NEW-1: Academic Slice/Shuffle Debias Test~~ COMPLETED (2026-04-14)

3 conditions: first-quarter slice, shuffled, debiased-prompt. Finding: temporal ordering creates extreme bias (chronological mean |Δ|=12.5 vs shuffled 5.3). Shuffle ≈ debiased prompt (both ~5.5). The debiased prompt doesn't fail on academic — the prior comparison used the wrong baseline. Core mechanism: long-range narrative arc construction, not register-local cues. Full analysis: `experiments/methodology-supplement/new-experiments-results.md`.

---

## Potential Improvements

### Empath Calibration Overhaul

The current `50 + raw * 2000` calibration produces a 5.8-point spread across all Big Five domains (effectively no differentiation). Root cause analysis in `empath-evaluation.json` identifies this as primarily a calibration issue compounded by missing categories in the mapping.

Options:
- Empirical recalibration against known personality benchmarks
- Replace linear scaling with percentile mapping
- Accept Empath as a negative finding (methodological limitation) and document it

### LLM Inference Model Comparison

Run the same narrative analysis with multiple models (Sonnet, Opus, GPT-5) to test model-robustness of personality inference. The current implementation already supports `--model` parameter changes.

---

## Deferred Codebase Remediation Items

Items from the 3-model codebase review (GPT-5.4, Gemini 3.1 Pro, Opus 4.6). Most resolved in the second remediation pass (2026-03-20).

### Completed (Second Remediation Pass)

| Item | Resolution | Review Finding |
|------|-----------|----------------|
| Extract shared `psyche-web` package | Tier-3 now imports via `@psyche/*` tsconfig path + prebuild sync script. ~28 duplicate files deleted. | #3 |
| Replace `Map` with `Record` in `SessionState` | Converted in both tier-2 and tier-3. Removed Map↔Record serialization code. | #20 |
| Refactor `InstrumentRunner` into sub-components | Extracted 5 presentational components (LikertScale, BinaryButtons, MultipleChoice, NumericInput, QuestionProgress) in both tiers. | Gemini |
| CAT controller immutable state | `getNextItem` returns `{ item, dimensionId, session }`. `registerResponse` returns new `CATSession`. Double-submit guard added. | #21 |
| Durable rate limiting (D1) | Replaced in-memory `Map` with `psyche_rate_limits` D1 table. Cleanup in `cleanupSessions()`. | #12 |
| CAT item bank schema fix + reverse scoring | JSON fields renamed `itemId`→`id`, `itemText`→`text`. Generator updated. JSON loading test added. | #6, #7 |
| DRY refactor scoring (`scoreBinary` + `scoreLikert`) | Extracted `groupResponsesByScale()` and `aggregateScales()` shared helpers. `scoreBinary` tests added. | #17 |
| `thetaToPercentile` precision | Changed to 2 decimal places (`Math.round(cdf * 10000) / 100`). | #31 |
| Seed data fetch removal | Removed dev-only fetch block from `onRehydrateStorage`. | #30 |

### Architectural Decision: Accepted

| Item | Rationale | Review Finding |
|------|-----------|----------------|
| Server-side score re-computation | Privacy contract prevents this. Item responses only flow server-side at consent level 2 (research). Scores computed client-side at consent level 1 are trusted. Re-computing would require either always storing responses (breaking privacy) or a complex ephemeral flow. Current approach is correct for a privacy-first tool. | #16 |

### Completed (Third Remediation Pass — 2026-03-20)

| Item | Resolution | Review Finding |
|------|-----------|----------------|
| O(N) item bank filtering in `getNextItem` | Pre-grouped items by dimension in `CATSession` via `dimensionItems` ReadonlyMap. O(1) dimension lookup. | I2-#5 |
| `scoreLikert` normalizer O(S*N) `find()` | Changed `aggregateScales` normalizer to receive `firstItem` directly instead of full instrument. Eliminates per-scale linear scan. | I2-#11 |
| `importData` accepts unconstrained values | Added response sanitization (reject non-finite numbers, missing itemIds) and score clamping ([0,100]). Uses `structuredClone` to avoid mutating live state. | I2-#16 |
| `catSessionToScores` excludes skipped dims | Added optional `fixedFormScores` parameter to merge fixed-form scores for CAT-skipped facets. `scoreAdaptive` passes through. | I2-#13 |
| `validateItemBank` heuristic too permissive | Added JSDoc documenting what it does NOT check (threshold diversity, discrimination range, cross-validation). | I2-#14 |

### Remaining Deferred

| Item | Reason | Review Finding |
|------|--------|----------------|
| CAT content balancing | Needs real item banks with actual item text and content categorization. Synthetic banks have placeholder text. Implement when SAPA-calibrated banks are available. | I1-#32 |
| Dual state management encapsulation | Manual `saveToStorage`/`loadFromStorage` works correctly. Zustand persist for Next.js carries medium-high risk (SSR hydration timing, 3-path init flow). Defer indefinitely. | I1-#23 |
| TestRunner / TestItemDisplay unification | Low value — standalone app is secondary to deployed tier-2/tier-3 apps. Would add complexity for small reuse gain. | I2-#9 |
