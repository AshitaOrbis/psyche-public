# Opus 4.6 Code Review -- Iteration 1
**Date:** 2026-03-20
**Scope:** full -- ~45 files reviewed across web/, tier-3-nextjs/, tier-2-astro/, and api/ + 6 test files (49 tests, all passing)

## Findings

### [CRITICAL]: Next.js ScaleScore type missing CAT fields -- silent data loss on heavy tier
**File:** tier-3-nextjs/src/lib/psyche/types.ts:70-79
**Category:** cross-file-consistency
**Confidence:** CERTAIN
**Description:** The Next.js copy of `ScaleScore` is missing four fields present in the standalone `web/src/instruments/types.ts`:
- `alpha?: number` (Cronbach's alpha)
- `theta?: number` (IRT theta estimate)
- `se?: number` (standard error of theta)
- `itemsAdministered?: number`

The standalone types.ts has these at lines 83-87. The Next.js copy stops at `itemCount`.

**Impact:** If the heavy tier is ever exposed via the Next.js deployment, CAT instrument scores would serialize without theta/se fields. Currently mitigated because only lite/standard tiers are deployed via Next.js (the assess page imports `init-standard`, not `init`), but this is a latent bug that will surface the moment heavy tier support is added. More immediately, any code that passes `InstrumentResult` objects between the two codebases (e.g., API export/import) will silently strip the CAT-specific fields due to TypeScript's structural typing.

**Suggested Fix:** Sync the Next.js types.ts to match the standalone version. Long-term, the BACKLOG note about switching to a `psyche-web` link dependency should be prioritized -- manual syncing of 21+ instrument files is unsustainable.

---

### [CRITICAL]: Next.js registry missing `isAdaptiveInstrument` function
**File:** tier-3-nextjs/src/lib/psyche/registry.ts (entire file)
**Category:** cross-file-consistency
**Confidence:** CERTAIN
**Description:** The standalone `web/src/instruments/registry.ts` exports an `isAdaptiveInstrument()` function (line 135-138). The Next.js copy only exports `registerInstrument`, `getInstrument`, `getAllInstruments`, and `getInstrumentIds`. This function is used to determine whether an instrument requires the CAT controller flow rather than standard scoring.

**Impact:** Same tier-gating as above -- currently no Next.js code calls this function because heavy tier is not deployed there. But any attempt to integrate CAT instruments into the Next.js deployment will fail silently (instruments would use the placeholder scorer and return empty results).

**Suggested Fix:** Sync the registry files or, preferably, establish a single source of truth.

---

### [HIGH]: `scoreLikert` normalization uses first item's response format, which could be wrong for mixed-format scales
**File:** web/src/scoring/engine.ts:465-469 (and identical copy at tier-3-nextjs/src/lib/psyche/engine.ts:3049-3053)
**Category:** scoring-correctness
**Confidence:** HIGH
**Description:** The normalization logic does:
```typescript
const firstItem = instrument.items.find((i) => i.scaleId === scale.id);
if (firstItem?.response.type === "likert") {
  const { min, max } = firstItem.response;
  normalized = ((raw - min) / (max - min)) * 100;
}
```
This finds the first item matching `scale.id` in the **full instrument items array** (not among the items that actually contributed to the raw score). If a scale has items with different min/max ranges (e.g., a 7-point item mixed with a 5-point item), normalization would use whichever item appears first in the definition.

**Impact:** Currently no instrument mixes Likert ranges within a single scale, so this is not producing wrong results today. However, it is a fragile assumption that will produce silently incorrect normalization the moment an instrument is added with heterogeneous response formats per scale. The fact that the raw mean includes items with different ranges while normalization uses only one item's range would produce scores outside 0-100 or compressed/expanded within it.

**Suggested Fix:** Either:
1. Assert at registration time that all items within a scale share the same response format (defensive, catches the error early), or
2. Compute normalization per-item before averaging (theoretically correct for heterogeneous scales): normalize each item's response to 0-1, then average, then multiply by 100.

---

### [HIGH]: `getNextItem` in `cat-controller.ts` double-filters on `administeredIds`
**File:** web/src/scoring/cat-controller.ts:943-953 (digest line numbering)
**Category:** grm-irt
**Confidence:** CERTAIN
**Description:** In `getNextItem()`, the item bank is filtered to exclude administered items:
```typescript
const dimBank = itemBank.filter(
  (item) => item.dimensionId === dimId && !dimSession.administeredIds.has(item.id),
);
```
Then `selectNextItem(dimBank, dimSession.theta, dimSession.administeredIds)` is called, which **also** checks `administered.has(item.id)` internally (grm-engine.ts:771). This double-filtering is redundant -- not a bug per se, but it means `selectNextItem` is always iterating over items it will never skip, doing an unnecessary Set lookup per item.

**Impact:** Performance only. With typical item banks (<100 items per dimension), this is negligible. However, it reveals a coupling issue: `selectNextItem` expects to do its own filtering but the caller already did it. If a future caller forgets the pre-filter, behavior is still correct; if a future caller passes a pre-filtered bank AND doesn't pass the administered set, `selectNextItem` would still work. So the redundancy is actually safety -- downgrading this to a code cleanliness note.

**Suggested Fix:** Either remove the pre-filter in `getNextItem` (relying on `selectNextItem` to filter) or pass `new Set()` to `selectNextItem` after pre-filtering. Document the chosen contract.

---

### [HIGH]: `autoScoreCompleted` uses `>=` comparison on response count, but instruments with duplicate itemIds would over-count
**File:** web/src/state/store.ts:1256 (digest line numbering)
**Category:** state-management
**Confidence:** MEDIUM
**Description:** The auto-score check:
```typescript
if (session.responses.length >= instrument.items.length) {
  newResults[id] = score(instrument, session);
}
```
compares `responses.length` against `instrument.items.length`. If a user navigates back and re-answers items, `recordResponse` replaces the existing response (via `findIndex` + splice at line 1137-1144), so duplicates are prevented in the active flow. However, imported data (`importData`) or seed data could contain duplicate `itemId` entries in the responses array. The `responseMap` construction in `scoreLikert`/`scoreBinary` would use the last response per itemId (Map overwrites), so scoring would still be correct -- but the `>=` check could trigger auto-scoring prematurely if `responses.length` was inflated by duplicates while unique items were actually incomplete.

**Impact:** Low in practice (import data would need to be malformed), but the check should use unique item count, not raw array length.

**Suggested Fix:**
```typescript
const uniqueResponses = new Set(session.responses.map(r => r.itemId)).size;
if (uniqueResponses >= instrument.items.length) {
```

---

### [HIGH]: `open-ended` word count counts empty strings as 1 word
**File:** web/src/instruments/open-ended.ts:48-49
**Category:** scoring-correctness
**Confidence:** CERTAIN
**Description:** The word count logic:
```typescript
return sum + r.value.trim().split(/\s+/).length;
```
When `r.value` is an empty string, `"".trim().split(/\s+/)` returns `[""]` (an array of length 1), not `[]`. So every empty-string response adds 1 to `totalWords`. The `answered` count correctly filters these out, but the `word-count` scale score will be inflated.

**Impact:** If a session has 10 responses where 5 are empty strings, `totalWords` would be `actualWords + 5`. The normalized word-count score would be slightly inflated. The word-count scale is cosmetic (not used for personality assessment), but it's misleading in the results display.

**Suggested Fix:**
```typescript
const words = r.value.trim();
return sum + (words.length > 0 ? words.split(/\s+/).length : 0);
```
The same pattern appears in `InterviewFlow.tsx` line 3778, but there it's on user-input text that's always non-empty due to validation.

---

### [MEDIUM]: PHQ-9/GAD-7 treats missing responses as 0 rather than excluding them
**File:** web/src/instruments/phq9-gad7.ts:76-84 (and identical Next.js copy)
**Category:** scoring-correctness
**Confidence:** CERTAIN
**Description:** The custom scorer for PHQ-9/GAD-7 uses:
```typescript
const r = responseMap.get(`phq9-${idx + 1}`);
return sum + (typeof r?.value === "number" ? r.value : 0);
```
If a response is missing (user skipped it), the ternary falls through to `0` -- the same value as "Not at all." This means a skipped item is scored identically to the lowest-severity response.

**Impact:** For a clinical screening tool, treating missing data as "not at all" systematically understates symptom severity. If a user completes 7/9 PHQ-9 items, the raw score is computed as if they answered "Not at all" to the 2 skipped items, and normalized against the full 27-point maximum. The `itemCount` is hardcoded to 9/7 regardless of how many were actually answered.

This contrasts with `scoreLikert`/`scoreBinary` which skip missing items entirely and compute means over only the answered items. The PHQ-9/GAD-7 custom scorer should either (a) impute missing values or (b) prorate the score, or at minimum (c) report the actual item count.

**Suggested Fix:** Option (b) -- prorate:
```typescript
let count = 0;
const phq9Sum = PHQ9_ITEMS.reduce((sum, _, idx) => {
  const r = responseMap.get(`phq9-${idx + 1}`);
  if (typeof r?.value === "number") { count++; return sum + r.value; }
  return sum;
}, 0);
const prorated = count > 0 ? (phq9Sum / count) * 9 : 0;
```
And set `itemCount: count` instead of the hardcoded `9`.

---

### [MEDIUM]: `importData` merge order gives existing data priority, which is the opposite of typical import semantics
**File:** web/src/state/store.ts:1209-1210 (digest line numbering)
**Category:** state-management
**Confidence:** HIGH
**Description:** The import function does:
```typescript
const mergedSessions = { ...data.sessions, ...currentState.sessions };
const mergedResults = { ...data.results, ...currentState.results };
```
The spread order means existing state overwrites imported data. The comment says "don't overwrite completed results" but the implementation is broader -- it prevents ANY imported data from overwriting ANY existing data, including incomplete sessions. If a user exports from device A, makes progress on device B, then imports the device A export on device B, the device B state is preserved for any overlapping instruments -- which is probably correct. But if they export from device A, corrupt their device B state, and import to recover, they'll still see the corrupted state.

**Impact:** This is a design decision, not a bug. But the semantics are unusual for an "import" operation (users typically expect imports to replace local state). The auto-score call after import (`autoScoreCompleted()`) could also behave unexpectedly if imported sessions are complete but existing ones aren't.

**Suggested Fix:** Document the merge behavior clearly in the UI (e.g., "Import will add missing instruments but won't overwrite existing progress"). Alternatively, offer a "replace" vs "merge" option.

---

### [MEDIUM]: `InstrumentRunner` completion fires on `responses.size === totalItems`, creating a race with final response render
**File:** tier-3-nextjs/src/components/psyche/InstrumentRunner.tsx (lines 3417-3421 of digest)
**Category:** state-management
**Confidence:** HIGH
**Description:** The completion effect:
```typescript
useEffect(() => {
  if (responses.size === totalItems) {
    onComplete(Array.from(responses.values()));
  }
}, [responses.size, totalItems, onComplete]);
```
This fires the `onComplete` callback as a side effect of the response state change. If the user answers the last item, the response is recorded, React re-renders, and the effect fires -- but this happens in the same render cycle where the UI should be showing the last answer's selection state. The parent (`PsycheAssess`) receives `onComplete`, advances `currentInstrumentIndex`, and may unmount the `InstrumentRunner` before the user sees visual confirmation of their last response.

**Impact:** Users may not see their last answer highlighted before the view transitions to the next instrument. The 150ms auto-advance delay (line 3429-3434) mitigates this for auto-advance mode, but in manual mode there's no delay. This is a UX issue, not a data correctness issue -- the response IS recorded.

**Suggested Fix:** Add a small delay (200-300ms) before calling `onComplete` when the last item is answered, to allow the selection state to render:
```typescript
useEffect(() => {
  if (responses.size === totalItems) {
    const timer = setTimeout(() => onComplete(Array.from(responses.values())), 250);
    return () => clearTimeout(timer);
  }
}, [responses.size, totalItems, onComplete]);
```

---

### [MEDIUM]: Session state uses `Map` for `completedInstruments` but localStorage serialization loses Map semantics
**File:** tier-3-nextjs/src/app/psyche/assess/page.tsx (around line 2571-2589 of digest)
**Category:** state-management
**Confidence:** HIGH
**Description:** The `SessionState` type uses `Map<string, ItemResponse[]>` for `completedInstruments`, but when persisting to localStorage it manually converts to a plain object:
```typescript
const storedResponses: Record<string, ItemResponse[]> = {};
for (const [instId, resps] of newCompleted.entries()) {
  storedResponses[instId] = resps;
}
```
And when restoring:
```typescript
const completedMap = new Map<string, ItemResponse[]>();
if (stored.instrumentResponses) {
  for (const [instId, resps] of Object.entries(stored.instrumentResponses)) {
    completedMap.set(instId, resps);
  }
}
```
This conversion is done correctly in all paths, but it's scattered across 3 different locations (handleInstrumentComplete, handleInterviewComplete, and the init effect). A single missing conversion point would cause a silent bug where `completedInstruments.size` returns 0 after restore.

**Impact:** Currently working, but fragile. Any new code path that saves to localStorage must remember the Map-to-Object conversion.

**Suggested Fix:** Consider using a plain `Record<string, ItemResponse[]>` throughout instead of `Map`, since the Map provides no benefit here (string keys, iteration order doesn't matter). This eliminates the conversion entirely.

---

### [MEDIUM]: `thetaToPercentile` rounds to one decimal place, losing precision for downstream consumers
**File:** web/src/scoring/grm-engine.ts:755 (digest line numbering)
**Category:** grm-irt
**Confidence:** CERTAIN
**Description:** The function returns `Math.round(cdf * 1000) / 10`, which rounds to one decimal place (e.g., 84.1, 15.9). However, `catSessionToScores` stores this as the `normalized` field:
```typescript
normalized: thetaToPercentile(dim.theta),
```
And the PsycheResults component rounds it again: `Math.round(score.normalized)`. The double rounding (first to 0.1, then to integer) is fine for display, but any downstream consumer (e.g., the report generation prompt) that expects full precision gets the pre-rounded value.

**Impact:** Minor. The report prompt receives scores that are already rounded to 0.1, which is more than sufficient for personality assessment interpretation. The rounding direction could differ by 0.05% at most.

**Suggested Fix:** No change needed for current use case. If higher precision is needed for research, return `cdf * 100` without rounding and let consumers decide their own precision.

---

### [LOW]: `selectNextItem` always selects globally most informative item, ignoring content balancing
**File:** web/src/scoring/grm-engine.ts:762-779 (digest line numbering)
**Category:** grm-irt
**Confidence:** CERTAIN
**Description:** The item selection strategy is pure maximum Fisher information at the current theta estimate. In IRT CAT literature, this is the standard approach but has known issues: (1) it tends to over-use items near the current theta, leading to "item overexposure" in repeated testing; (2) it ignores content coverage -- if all high-information items happen to be from one facet within a dimension, the respondent gets a narrow slice of the construct.

**Impact:** For a single-administration personality assessment, this is acceptable. Item exposure is irrelevant (no repeat testing), and the per-dimension structure already provides some content balancing. However, if CAT items share content domains within a dimension (e.g., all Extraversion items about parties vs. assertiveness), the assessment could systematically favor one content cluster.

**Suggested Fix:** No immediate change needed. If content balancing becomes important, consider a-stratification or shadow test approaches. Document the current strategy's limitations in the code comments.

---

### [LOW]: `word-count` scale in `open-ended` instrument is not in the `scales` array
**File:** web/src/instruments/open-ended.ts
**Category:** scoring-correctness
**Confidence:** CERTAIN
**Description:** The `open-ended` instrument defines only one scale:
```typescript
scales: [{ id: "qualitative", name: "Qualitative Responses" }],
```
But `scoreOpenEnded` returns two scores: one for `"qualitative"` and one for `"word-count"`. The `"word-count"` scale has no corresponding entry in the instrument's `scales` array. This means `scoreLikert`'s scale iteration logic (which iterates `instrument.scales`) would skip it -- but since `open-ended` uses a custom scorer, it returns the score directly.

**Impact:** The results display in PsycheResults shows the `word-count` score, but there's no metadata (name, description) registered for it. The scale is effectively phantom -- it exists in the results but not in the instrument definition. Any code that validates results against instrument scales would flag this.

**Suggested Fix:** Add `{ id: "word-count", name: "Total Word Count" }` to the `open-ended` scales array, or remove the word-count score from the result (it's cosmetic).

---

### [LOW]: `initRef` in `PsycheAssess` prevents re-initialization but doesn't account for React StrictMode double-mount
**File:** tier-3-nextjs/src/app/psyche/assess/page.tsx:2377 (digest line numbering)
**Category:** state-management
**Confidence:** MEDIUM
**Description:** The `initRef.current = true` guard at the top of the `useEffect` callback prevents double initialization. In React 18+ StrictMode (which Next.js uses by default in development), effects run twice. The ref guard prevents the second execution, which is the intended pattern. However, the first execution's async `init()` function starts but doesn't set `initRef.current = true` until the synchronous part runs -- the async API calls could still race with a StrictMode re-mount.

**Impact:** In development mode only, there could be a flash or redundant API call. In production (no StrictMode double-mount), this is fine. The guard pattern is correct for production.

**Suggested Fix:** This is fine as-is for production. No change needed.

---

### [LOW]: Rate limiting in `psyche.ts` uses in-memory Map, which resets on Cloudflare Worker restart
**File:** api/src/routes/psyche.ts:4577-4592 (digest line numbering)
**Category:** error-handling
**Confidence:** CERTAIN
**Description:** The report generation rate limit uses a module-level `Map<string, number[]>()`. Cloudflare Workers are ephemeral -- the Map resets when the Worker isolate is recycled (typically every few minutes under load, or after idle timeout). This means the "10 reports per hour" limit is per-isolate, not global.

**Impact:** Under light load (single isolate), the rate limit works as expected. Under heavy load or after restarts, the limit resets. A determined attacker could generate more than 10 reports/hour by waiting for isolate recycling. Given the DeepInfra API key cost, this is worth hardening.

**Suggested Fix:** Use Cloudflare's Durable Objects or KV store for rate limiting, or implement per-session rate limiting (which already exists: "Only 1 report per session" at line 4826-4828) and rely on session creation rate as the chokepoint.

---

### [LOW]: Astro API client differs structurally from Next.js API client
**File:** tier-2-astro/src/lib/psyche/api.ts vs tier-3-nextjs/src/lib/psyche/api.ts
**Category:** cross-file-consistency
**Confidence:** CERTAIN
**Description:** The Astro copy wraps calls in a `fetchJson` helper that throws `ApiError` on non-200 responses, while the Next.js copy returns raw `res.json()` and relies on callers to check for `data.error`. The Astro `getSession` intentionally does NOT use `fetchJson` (comment explains why), matching the Next.js behavior for that specific endpoint.

**Impact:** The two API clients have different error-handling contracts. The Astro version throws on errors (forcing callers to try/catch), while the Next.js version returns error objects inline. This is a deliberate divergence documented in the Astro code, but it means instrument or flow code cannot be shared between the two without adjusting error handling.

**Suggested Fix:** This is acceptable as a conscious design choice. Document the difference in the shared CLAUDE.md or BACKLOG.

---

## Test Coverage Gaps

### No tests for `scoreBinary`
**Category:** test-gap
**Confidence:** CERTAIN
**Description:** The `scoring.test.ts` file only tests `scoreLikert`. `scoreBinary` has zero test coverage. The Self-Monitoring-18 instrument (and its Next.js copy) depends on it. The reverse scoring logic for binary items (`value = 1 - value`) is straightforward but untested -- particularly the interaction with the `keyedTrue`/`reversed` mapping in self-monitoring-18.ts.

**Suggested Fix:** Add tests for:
- Normal binary scoring (True=1, False=0)
- Reverse binary scoring
- Mixed reversed/non-reversed items in same scale
- All-True and all-False edge cases

### No tests for PHQ-9/GAD-7 custom scorer
**Category:** test-gap
**Confidence:** CERTAIN
**Description:** The PHQ-9/GAD-7 instrument uses a custom scorer (`scorePhqGad`) that bypasses `scoreLikert`. It uses sum scoring (not mean), has hardcoded `itemCount`, and treats missing responses as 0. None of this is tested.

**Suggested Fix:** Test:
- All-zero responses (should score 0/27 and 0/21)
- Maximum responses (should score 27/27 and 21/21)
- Missing responses (current behavior: score as 0; should document or fix)
- Partial responses

### No tests for CRT-7 custom scorer
**Category:** test-gap
**Confidence:** CERTAIN
**Description:** The CRT-7 has hardcoded correct answers (`CORRECT_ANSWERS`). No tests verify that these answers are actually correct, or that edge cases (non-numeric input for numeric questions, case sensitivity for question 7) are handled.

**Suggested Fix:** Test each correct answer, boundary values (e.g., "5 cents" vs "5" for CRT-1), and the text-matching for CRT-7 (currently `"c"` matches but `"C"` also matches due to `.toLowerCase()` -- verify this is intended).

### No integration test for tier + instrument registration
**Category:** test-gap
**Confidence:** MEDIUM
**Description:** The existing `tiers.test.ts` verifies that tier logic produces correct instrument lists and that all instruments are registered. But there's no test that verifies the entire flow: tier selection -> instrument list -> scoring each instrument with simulated responses -> valid results. This end-to-end test would catch issues like the normalization heterogeneity problem described above.

### No tests for the store (`usePsycheStore`)
**Category:** test-gap
**Confidence:** CERTAIN
**Description:** The Zustand store has no test coverage. The `recordResponse` (replace-or-append logic), `resetInstrument`, `importData`, `exportData`, and `autoScoreCompleted` functions are all untested. The import/export serialization (especially the `completedAt` injection in `autoScoreCompleted`) and seed data merge logic are particularly testable.

### No tests for `scoreAdaptive`
**Category:** test-gap
**Confidence:** CERTAIN
**Description:** The `scoreAdaptive` function in `engine.ts` converts a `CATSession` into an `InstrumentResult`. While `catSessionToScores` is tested via `cat-controller.test.ts`, the wrapping `scoreAdaptive` (which adds scale name mapping) is not tested directly.

## Summary
- CRITICAL: 2 findings (Next.js type drift, Next.js registry drift)
- HIGH: 4 findings (normalization fragility, CAT double-filter, auto-score count check, open-ended word count)
- MEDIUM: 5 findings (PHQ-9 missing data handling, import merge semantics, completion race, Map serialization, theta precision)
- LOW: 5 findings (CAT item selection, phantom scale, StrictMode guard, Worker rate limit, Astro API divergence)
- TEST GAPS: 6 categories identified

## False Negatives Check

Areas I could NOT fully review due to limitations of the code digest:

1. **All 21 Next.js instrument copies** -- I only read `phq9-gad7.ts` in full. The remaining 20 instrument files under `tier-3-nextjs/src/lib/psyche/instruments/` were not included in the digest. Each could have scoring drift, item text drift, or import path differences. A diff-based comparison of all 21 files against their web/ counterparts would be needed.

2. **IPIP-NEO-300 instrument** -- Not included in the digest. This is the largest instrument (300 items, 30 facets) and uses the same `questionsData` import pattern as NEO-60/NEO-120. Facet-to-domain mapping, reverse scoring flags, and item selection logic were not reviewed.

3. **HEXACO-200 instrument** -- Not included in the digest. This is the heavy-tier upgrade from HEXACO-60. Item content, scoring logic, and facet structure were not verified.

4. **Heavy-tier extended instruments** (aot-13, ius-12, scs-26, mfq-2, frost-mps, maas, authenticity, tangney-scs, maximization, ztpi) -- Not included in the digest. Each has its own scoring logic that could contain similar issues to those found in PHQ-9/GAD-7.

5. **CAT item bank data** -- The CAT instruments (`cat-big5`, `cat-hexaco`) reference runtime-loaded GRM item banks. The actual item bank files (with discrimination and threshold parameters) were not reviewed. Invalid parameters (e.g., non-monotonic thresholds, negative discrimination) would produce incorrect IRT calculations.

6. **Database schema** -- The API route handlers reference tables (`psyche_sessions`, `psyche_responses`, `psyche_interviews`, `psyche_evaluations`) but the schema SQL was not included. Field types, constraints, and indexes could not be verified.

7. **Snyder SM-25 and Levenson IPC-24** (heavy-tier replacements for self-monitoring-18 and loc-ie4) -- Not included in the digest. These are upgraded instruments that should measure the same constructs as their lite-tier counterparts. Scoring parity was not verified.

8. **BPNS-21 and Grit-O** (heavy-tier replacements) -- Not included in the digest.

9. **ECR-R (attachment)** and **IRI-28 (empathy)** -- These are psychometrically complex instruments with reverse-scored items and multi-dimensional structures. The item definitions were not fully reviewed.
