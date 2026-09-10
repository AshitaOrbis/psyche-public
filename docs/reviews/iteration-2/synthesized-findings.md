# Synthesized Findings — Iteration 2

**Date:** 2026-03-20
**Models:** Opus 4.6, Gemini 3.1 Pro, GPT-5.4
**Scope:** Full post-remediation review — verifying 9 fixes from iteration 1, finding new/regression issues
**Method:** Deduplicated by issue, cross-validated across reports, severity weighted by model agreement

---

## Actionable Findings

| # | Severity | Title | File(s) | Models | Category | Status |
|---|----------|-------|---------|--------|----------|--------|
| 1 | CRITICAL | AdaptiveTestRunner discards immutable registerResponse/getNextItem return values | AdaptiveTestRunner.tsx:97-115 | Opus+Gemini | state-management | **FIXED** |
| 2 | HIGH | Duplicate keyboard handlers: LikertScale + AdaptiveTestRunner both fire | LikertScale.tsx, AdaptiveTestRunner.tsx:147-160 | Opus+Gemini | component-design | actionable |
| 3 | HIGH | PHQ-9 `incomplete` flag invisible to TypeScript (type assertion) | phq9-gad7.ts:122,130 + types.ts | Opus | scoring-correctness | **FIXED** |
| 4 | HIGH | No test for shared helpers edge cases (duplicates, unknown scaleId, non-numeric) | scoring.test.ts | Opus | test-gap | actionable |
| 5 | HIGH | getNextItem filters full item bank O(N) per call | cat-controller.ts:181-191 | Gemini | performance | defer |
| 6 | MEDIUM | autoScoreCompleted double-getState timing concern | store.ts:198-205 | Opus | state-management | **FIXED** |
| 7 | MEDIUM | selectNextItem double-filters (bank pre-filtered + admin set) | cat-controller.ts:185-196 | Opus | code-quality | actionable |
| 8 | MEDIUM | init.ts doesn't chain through init-lite/init-standard | init.ts vs init-lite.ts/init-standard.ts | Gemini | architecture | actionable |
| 9 | MEDIUM | TestRunner doesn't use extracted TestItemDisplay | TestRunner.tsx, TestItemDisplay.tsx | Gemini | code-quality | defer |
| 10 | MEDIUM | CAT dimension ordering depends on item bank JSON order | cat-controller.ts:123-144 | Opus | logic-correctness | actionable |
| 11 | MEDIUM | scoreLikert normalizer uses inst.items.find() per scale O(S*N) | engine.ts:83-91 | Gemini | performance | defer |
| 12 | MEDIUM | thetaToPercentile returns exact 0/100 at boundary | grm-engine.ts:241-243 | Opus | scoring-precision | accept |
| 13 | LOW | catSessionToScores excludes skipped dimensions silently | cat-controller.ts:321-336 | Opus | logic-correctness | defer |
| 14 | LOW | validateItemBank heuristic too permissive | cat-controller.ts:68-81 | Opus | logic-correctness | defer |
| 15 | HIGH | R script extract_irt_params.R emits legacy itemId/itemText | extract_irt_params.R:95-97 | GPT | api-contract | **FIXED** |
| 16 | MEDIUM | importData accepts unconstrained response values | store.ts:136, engine.ts:20-50 | GPT | edge-case | defer |
| 17 | MEDIUM | getNextItem dimension exhaustion path untested | cat-controller.ts:170-195 | GPT | test-gap | actionable |

---

## Already Fixed (During Review)

| # | Finding | Fix Applied |
|---|---------|-------------|
| 1 | AdaptiveTestRunner discards immutable returns | Captured `registerResponse()` return in `sessionRef.current`; captured `getNextItem()` `.session` field |
| 3 | PHQ-9 `incomplete` type assertion | Added `incomplete?: boolean` to `ScaleScore` interface; removed `as` casts |
| 6 | autoScoreCompleted double-getState | Removed second `getState()` call; reuse initial snapshot for setState |
| 15 | R script emits legacy itemId/itemText | Updated extract_irt_params.R lines 95-97: `itemId`→`id`, `itemText`→`text` |

## Immediate Action Required

| # | Finding | Estimated Effort |
|---|---------|-----------------|
| 2 | Remove duplicate keyboard handler from LikertScale | 5 min |
| 4 | Add 3 edge-case tests for shared scoring helpers | 10 min |
| 7 | Remove redundant selectNextItem filter | 5 min |
| 8 | Refactor init.ts to chain through tier init files | 10 min |
| 10 | Sort dimensionOrder alphabetically | 1 line |

## Deferred (Performance/Architecture)

| # | Finding | Reason |
|---|---------|--------|
| 5 | O(N) item bank filtering in getNextItem | Not user-visible at current bank sizes (100-500). Fix when real SAPA banks arrive. |
| 9 | TestRunner doesn't use TestItemDisplay | Working correctly, refactor scope is large. Standalone app is secondary to tier-2/tier-3. |
| 11 | normalizer O(S*N) find() | Sub-millisecond for current instruments. |
| 13 | Skipped dimensions excluded from catSessionToScores | By design — fixed-form scores cover skipped dims. Document. |
| 14 | validateItemBank too permissive | Advisory function, not gating. Improve when real banks arrive. |

## Accepted As-Is

| # | Finding | Rationale |
|---|---------|-----------|
| 12 | thetaToPercentile exact 0/100 at boundary | Defensible for display. Extremes beyond ±6 SD are not meaningfully distinguishable. |

---

## Remediation Verification (9 Iteration-1 Fixes)

| # | Fix | Opus | Gemini | Final |
|---|-----|------|--------|-------|
| 1 | DRY scoring helpers | VERIFIED | VERIFIED | **VERIFIED** |
| 2 | CAT JSON schema | VERIFIED | VERIFIED | **VERIFIED** |
| 3 | thetaToPercentile precision | VERIFIED | VERIFIED | **VERIFIED** |
| 4 | Seed data fetch removal | VERIFIED | VERIFIED | **VERIFIED** |
| 5 | CAT immutable state | REGRESSION (consumer) | PARTIALLY FIXED | **REGRESSION → FIXED** |
| 6 | Double-submit guard | VERIFIED | VERIFIED | **VERIFIED** |
| 7 | D1 rate limiting | NOT IN SCOPE | NOT VERIFIABLE | N/A (server-side) |
| 8 | Map→Record | NOT IN SCOPE | VERIFIED (store.ts) | **VERIFIED** |
| 9 | InstrumentRunner sub-components | VERIFIED | PARTIALLY FIXED | **VERIFIED** (tier-3; standalone app is separate) |

**Regression found and fixed:** #5 — CAT controller was correctly refactored but `AdaptiveTestRunner.tsx` was not updated to capture immutable return values. Fixed during this review session.
