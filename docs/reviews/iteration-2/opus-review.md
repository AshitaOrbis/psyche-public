# Opus 4.6 Code Review -- Iteration 2 (Post-Remediation)

**Date:** 2026-03-20
**Scope:** Full -- logic correctness and test coverage verification
**Files reviewed:** 24 modified files, 7 test files (59 tests passing), all instrument definitions
**Method:** Traced critical code paths through refactored scoring engine, CAT controller, and store; verified each remediation fix against iteration-1 findings

---

## Findings

### [CRITICAL]: AdaptiveTestRunner discards immutable return value from registerResponse

**File:** `web/src/components/AdaptiveTestRunner.tsx:109-115`
**Category:** state-management
**Confidence:** CERTAIN

**Description:**
The CAT controller was refactored to be immutable -- `registerResponse()` now returns a new `CATSession` instead of mutating in place. However, `AdaptiveTestRunner.handleResponse` still calls `registerResponse()` and ignores the return value, then reads from the stale `sessionRef.current`:

```typescript
// Line 109-115: return value is thrown away
registerResponse(
  sessionRef.current,
  itemBank,
  currentItem.item.id,
  category,
  DEFAULT_STOPPING,
);

// Line 117-118: reads stale session -- totalItemsAdministered is still 0,
// progress reflects pre-response state
setTotalItems(sessionRef.current.totalItemsAdministered);
setProgress(getCATProgress(sessionRef.current));
```

The `registerResponse` function creates and returns a new session object with updated theta, SE, administered items, and completion status. Because the return value is discarded:
1. `sessionRef.current` never updates -- theta remains at the prior, SE never decreases
2. `totalItemsAdministered` stays at 0 forever
3. The session never completes (completion flag is on the new object)
4. `getNextItem` on line 132 uses the stale session, so the same item is selected repeatedly
5. The double-submit guard works on the *new* session (which is thrown away), so it cannot prevent re-administration

**Impact:** The entire CAT adaptive testing flow is broken. Users will see the same item repeatedly, progress bars won't update, and the assessment will never terminate. This is the most critical bug in the codebase.

**Suggested Fix:**
```typescript
const handleResponse = useCallback(
  (value: number) => {
    if (!sessionRef.current || !itemBank || !currentItem) return;
    const category = value - 1;

    // Capture the new immutable session
    const updatedSession = registerResponse(
      sessionRef.current,
      itemBank,
      currentItem.item.id,
      category,
      DEFAULT_STOPPING,
    );
    sessionRef.current = updatedSession; // <-- critical assignment

    setTotalItems(updatedSession.totalItemsAdministered);
    setProgress(getCATProgress(updatedSession));

    setTimeout(() => {
      if (!sessionRef.current || !itemBank) return;
      if (sessionRef.current.complete) {
        const result = scoreAdaptive(instrumentId, sessionRef.current);
        completeInstrument(result);
        onComplete();
        return;
      }
      const next = getNextItem(sessionRef.current, itemBank);
      setCurrentItem(next);
      if (!next) {
        const result = scoreAdaptive(instrumentId, sessionRef.current);
        completeInstrument(result);
        onComplete();
      }
    }, 200);
  },
  [itemBank, currentItem, instrumentId, completeInstrument, onComplete],
);
```

---

### [CRITICAL]: getNextItem same-session first-call does not capture returned session either

**File:** `web/src/components/AdaptiveTestRunner.tsx:97-98`
**Category:** state-management
**Confidence:** CERTAIN

**Description:**
The `getNextItem` function also returns a new session (with potentially updated `currentDimensionIndex` and completed dimensions if a dimension's item bank was exhausted). On the initialization path (line 97-98), the returned session from `getNextItem` is stored into `currentItem` (which has a `.session` field), but `sessionRef.current` is not updated:

```typescript
const next = getNextItem(session, itemBank);
setCurrentItem(next);
// sessionRef.current still holds the original session from initCATSession,
// not next.session which may have advanced dimensions
```

If any dimension has zero remaining items after filtering (e.g., all items were fixed-form exclusions), `getNextItem` marks it complete in the *returned* session but not in `sessionRef.current`. Subsequent calls operate on stale dimension state.

**Impact:** In scenarios with fixed-form item exclusion, skipped dimensions may be re-evaluated on every call, causing redundant work or incorrect session completion detection.

**Suggested Fix:**
```typescript
const next = getNextItem(session, itemBank);
if (next) {
  sessionRef.current = next.session;
}
setCurrentItem(next);
```

---

### [HIGH]: getNextItem while-loop creates Map copies without accumulating across iterations

**File:** `web/src/scoring/cat-controller.ts:167-213`
**Category:** logic-correctness
**Confidence:** HIGH

**Description:**
The `getNextItem` while-loop correctly handles the case where a dimension needs to be marked complete (empty bank or no selectable item) by creating a new Map copy. However, there is a subtle accumulation concern. Tracing the loop:

```typescript
let updatedDims = session.dimensions;  // starts as original reference

// Iteration where dimBank is empty:
updatedDims = new Map(updatedDims);  // shallow copy
updatedDims.set(dimId, { ...dimSession, complete: true });
currentIndex++;

// Next iteration where dimBank is also empty:
updatedDims = new Map(updatedDims);  // copies the *already-updated* Map -- CORRECT
updatedDims.set(dimId2, { ...dimSession2, complete: true });
```

This actually works correctly -- each `new Map(updatedDims)` copies the previously updated Map, so changes accumulate. The code is correct but the pattern is fragile. A refactoring that resets `updatedDims` to `session.dimensions` inside the loop would silently lose accumulated completions.

However, there IS a problem when the loop exits without finding an item (line 212-213): it returns `null` without propagating the accumulated dimension completions back to the caller. If two consecutive dimensions were exhausted in the same `getNextItem` call, the session still shows them as incomplete. The next `getNextItem` call will re-discover and re-copy.

**Impact:** Not a correctness bug (convergence still happens), but the session's `complete` flag is only set in `registerResponse`, not in `getNextItem`'s null-return path. If all dimensions are exhausted (no items remain in any dimension), `getNextItem` returns null but `session.complete` remains false. The caller in `AdaptiveTestRunner` handles this (lines 134-140 fall through to a graceful completion), but it relies on the "shouldn't happen" comment.

**Suggested Fix:**
When `getNextItem` returns null because all dimensions are exhausted (not because `session.complete` was already true), it should return a signal that the session needs to be marked complete, or return the updated session alongside null.

---

### [HIGH]: No test for the groupResponsesByScale / aggregateScales helper functions in isolation

**File:** `web/src/scoring/engine.ts:16-65`, `web/tests/scoring.test.ts`
**Category:** test-gap
**Confidence:** CERTAIN

**Description:**
The DRY refactor extracted `groupResponsesByScale()` and `aggregateScales()` as shared helpers. These are the load-bearing functions that both `scoreBinary` and `scoreLikert` depend on. The test suite tests the public APIs (`scoreLikert`, `scoreBinary`) which exercises the helpers indirectly, but several edge cases of the helpers themselves are untested:

1. **Duplicate responses for the same item**: `groupResponsesByScale` builds a response map with `responseMap.set(r.itemId, r)` -- later responses overwrite earlier ones. This is likely the desired behavior (last-write-wins), but no test verifies it.

2. **Items with scaleIds not in instrument.scales**: `aggregateScales` iterates `instrument.scales` and looks up `scaleItems.get(scale.id)`. If items reference a scale not in the scales array, they are silently ignored. This is correct but untested.

3. **Non-numeric response values**: `groupResponsesByScale` filters on `typeof resp.value !== "number"`, silently dropping string/text responses. This is correct for Likert/binary but there's no test documenting this behavior.

**Impact:** The helpers work correctly for all tested scenarios, but the lack of edge-case tests means future changes to these shared functions could introduce regressions that aren't caught. The existing tests would not detect a change in duplicate-response handling behavior.

**Suggested Fix:**
Add tests for:
```typescript
it("last response wins for duplicate itemIds", () => { ... });
it("items with unknown scaleId are silently excluded", () => { ... });
it("non-numeric responses are filtered out", () => { ... });
```

---

### [HIGH]: PHQ-9 proration diverges from standard clinical practice for < MIN items

**File:** `web/src/instruments/phq9-gad7.ts:548-556`
**Category:** scoring-correctness
**Confidence:** HIGH

**Description:**
The PHQ-9/GAD-7 scoring function implements proration correctly when enough items are answered (>= 7 for PHQ-9, >= 5 for GAD-7). However, when fewer than the minimum items are answered, it falls back to raw sum scoring:

```typescript
const phq9Prorated = phq9Count >= MIN_PHQ9
  ? (phq9Sum / phq9Count) * PHQ9_ITEMS.length
  : phq9Sum;  // <-- raw sum of however many were answered
```

For the incomplete case:
- `raw` is set to `phq9Sum` (the raw sum)
- `normalized` is set to `0`
- `incomplete: true` is set

The `normalized: 0` when incomplete is misleading. A user who answered 3 items all at "Nearly every day" (3 each, sum=9) would get `normalized: 0` despite highly elevated symptoms. If a downstream consumer checks `normalized` without checking the `incomplete` flag, they would miss clinical significance.

Furthermore, the `incomplete` field is added via a type assertion (`as ScaleScore & { incomplete?: boolean }`), meaning TypeScript won't enforce consumers to check it. The `ScaleScore` interface doesn't include `incomplete`, so any code typed as `ScaleScore` will not see the field.

**Impact:** Potential clinical misinterpretation. The `incomplete` flag is invisible to TypeScript consumers of `ScaleScore`. The `normalized: 0` value could mask genuine distress in a partially-completed assessment.

**Suggested Fix:**
1. Add `incomplete?: boolean` to the `ScaleScore` interface in `types.ts`
2. Consider `normalized: null` or `NaN` for incomplete scores (forces consumers to handle the case)
3. At minimum, set `normalized` to a prorated estimate even below the minimum threshold, with `incomplete: true` as a warning

---

### [MEDIUM]: selectNextItem in getNextItem receives pre-filtered bank but also receives administeredIds

**File:** `web/src/scoring/cat-controller.ts:185-196`
**Category:** logic-correctness
**Confidence:** HIGH

**Description:**
In `getNextItem`, the item bank is pre-filtered to exclude administered items:

```typescript
const dimBank = itemBank.filter(
  (item) => item.dimensionId === dimId && !dimSession.administeredIds.has(item.id),
);
```

Then `selectNextItem` is called with the pre-filtered bank AND the `administeredIds` set:

```typescript
const nextItem = selectNextItem(dimBank, dimSession.theta, dimSession.administeredIds);
```

Inside `selectNextItem`, it checks `administered.has(item.id)` again for each item. This double-filtering is redundant -- every item in `dimBank` has already been confirmed NOT in `administeredIds`. The second check always passes.

This is not a bug (it's defensive coding), but it's a performance concern for large item banks (O(n) set lookups on items that were already filtered). More importantly, it obscures the actual contract: does `selectNextItem` expect a pre-filtered bank or a full bank?

**Impact:** No functional impact. Minor performance overhead. Code clarity issue.

**Suggested Fix:**
Either pass `new Set()` (empty) to `selectNextItem` since filtering is already done, or remove the pre-filter in `getNextItem` and let `selectNextItem` handle all filtering. Pick one contract and document it.

---

### [MEDIUM]: autoScoreCompleted has a timing vulnerability with Zustand setState

**File:** `web/src/state/store.ts:1418-1447`
**Category:** state-management
**Confidence:** MEDIUM

**Description:**
`autoScoreCompleted()` reads state at the beginning (`getState()`), processes it, then reads state again before writing. Between those two reads, another state update could occur:

```typescript
function autoScoreCompleted(): void {
  const { sessions, results } = usePsycheStore.getState();  // Read 1
  // ... compute newResults ...

  if (Object.keys(newResults).length > 0) {
    const current = usePsycheStore.getState();  // Read 2 -- may differ from Read 1
    usePsycheStore.setState({
      results: { ...current.results, ...newResults },  // Merges with Read 2 state
      sessions: Object.fromEntries(
        Object.entries(current.sessions).map(...)  // Maps over Read 2 sessions
      ),
    });
  }
}
```

If a user completes an instrument between Read 1 and Read 2, the `newResults` computed from Read 1's sessions are merged into Read 2's results. This is generally safe because:
- `newResults` only contains results for sessions that had all responses but no result at Read 1 time
- The merge uses spread (`...current.results, ...newResults`), so existing results in Read 2 won't be overwritten by newResults

However, if the scoring function is slow or if `autoScoreCompleted` is called from `onRehydrateStorage` while another write is in flight, there's a theoretical window where a session could be scored with stale response data.

**Impact:** Extremely unlikely in practice (scoring is synchronous and fast), but the pattern is fragile. Zustand's `setState` is synchronous, so the real risk is from the `onRehydrateStorage` callback being called during initial hydration while the user interacts.

**Suggested Fix:**
Use a single `getState()` call and compute everything from that snapshot. The second `getState()` is unnecessary:

```typescript
function autoScoreCompleted(): void {
  const state = usePsycheStore.getState();
  const { sessions, results } = state;
  // ... compute newResults from this snapshot ...
  if (Object.keys(newResults).length > 0) {
    usePsycheStore.setState({
      results: { ...results, ...newResults },
      sessions: Object.fromEntries(
        Object.entries(sessions).map(...)
      ),
    });
  }
}
```

---

### [MEDIUM]: thetaToPercentile clamps at +/-6 but returns 0/100, not 0.01/99.99

**File:** `web/src/scoring/grm-engine.ts:241-251`
**Category:** scoring-precision
**Confidence:** MEDIUM

**Description:**
The `thetaToPercentile` function clamps extreme thetas:

```typescript
if (theta < -6) return 0;
if (theta > 6) return 100;
```

At theta = -6, the true normal CDF is approximately 0.000000001 (9.87e-10), not 0. At theta = 6, it's approximately 99.9999999. Returning exactly 0 or 100 is a reasonable engineering choice for display, but it creates a discontinuity at the boundary. For theta = -5.99, the function returns a small positive number (approximately 0.01); for theta = -6.01, it jumps to exactly 0.

For downstream consumers that use percentile for profile comparisons or report generation, the exact 0 or 100 value may be interpreted as "floor/ceiling" rather than "extreme but measurable."

The remediation correctly changed the rounding from 1 decimal to 2 decimal places (`Math.round(cdf * 10000) / 100`), which the test suite validates: theta=0 -> 50, theta=1 -> ~84, theta=-1 -> ~16, extremes clamp to 0/100.

**Impact:** Minor. The 0/100 clamp is defensible for display purposes. Only matters if a downstream consumer distinguishes between "at floor" and "near floor."

**Suggested Fix:**
Consider clamping to 0.01/99.99 for non-display uses, or document that 0 and 100 are sentinel values meaning "beyond measurement range."

---

### [MEDIUM]: CAT dimension ordering is non-deterministic (Map iteration order)

**File:** `web/src/scoring/cat-controller.ts:123-144`
**Category:** logic-correctness
**Confidence:** HIGH

**Description:**
The `dimensionOrder` array is built by iterating over `dimensionItems`, which is a `Map<string, GRMItem[]>`. The iteration order of a Map is insertion order, which depends on the order items appear in the `itemBank` array. This means:

1. The order of facet testing depends on item bank JSON ordering
2. If the item bank JSON is reordered (e.g., alphabetically sorted), the dimension order changes
3. Different item banks (big5 vs hexaco) may have different ordering conventions

This is not a bug per se -- any order works for measurement -- but it means the user experience is implicitly coupled to the item bank file's internal structure. Two users taking the same assessment with differently-ordered (but content-identical) item banks would see facets in a different sequence.

**Impact:** Non-deterministic user experience. No measurement impact (each dimension is independent). Could cause confusion if comparing assessment experiences across sessions.

**Suggested Fix:**
Sort `dimensionOrder` explicitly after building it:

```typescript
dimensionOrder.sort(); // Alphabetical: A1, A2, ..., C1, C2, ..., N1, N2, ...
```

---

### [LOW]: LikertScale keyboard handler duplicates AdaptiveTestRunner keyboard handler

**File:** `web/src/components/LikertScale.tsx:34-47`, `web/src/components/AdaptiveTestRunner.tsx:147-160`
**Category:** code-quality
**Confidence:** CERTAIN

**Description:**
Both `LikertScale` and `AdaptiveTestRunner` register global `keydown` listeners for number keys 1-5. When a Likert item is displayed in the adaptive runner, both handlers fire on the same keypress. The `LikertScale` handler calls `onChange` (which is `handleResponse`) and the `AdaptiveTestRunner` handler also calls `handleResponse`. This means each keypress triggers `handleResponse` twice.

The double-submit guard in `registerResponse` (CAT controller) would prevent the second call from actually registering a duplicate response, but:
1. It relies on the guard working correctly with the immutable pattern
2. Given the CRITICAL bug above (return value not captured), the guard doesn't actually protect -- `sessionRef.current` never updates, so `administeredIds` is always empty

Even with the CRITICAL fix applied, this double-invocation would call `registerResponse` twice: the first call returns a new session, the second call with the stale session would be caught by the guard and return the stale session. But `setTotalItems` and `setProgress` would be called with the stale session's values on the second invocation, potentially overwriting the correct values from the first invocation (depending on React batching).

**Impact:** Double handler invocation. After fixing the CRITICAL sessionRef bug, this could still cause a race condition where progress display briefly flickers or shows stale data.

**Suggested Fix:**
Either:
1. Remove the keyboard handler from `AdaptiveTestRunner` since `LikertScale` already handles it
2. Or pass a flag to `LikertScale` to suppress its keyboard handler when used in adaptive mode

---

### [LOW]: catSessionToScores skipped dimensions are silently excluded

**File:** `web/src/scoring/cat-controller.ts:321-336`
**Category:** logic-correctness
**Confidence:** HIGH

**Description:**
When a dimension is skipped during `initCATSession` (because fixed-form SE meets the threshold), it is never added to `session.dimensions`. Therefore, `catSessionToScores` will not include scores for those dimensions.

This is intentional -- the fixed-form scores are already available for those dimensions. However, there's no mechanism in `catSessionToScores` or `scoreAdaptive` to merge the CAT scores with the fixed-form scores for skipped dimensions. The caller (AdaptiveTestRunner) doesn't do this either. The result is that the adaptive instrument's `InstrumentResult` will be missing scores for any dimension that was skipped.

**Impact:** When fixed-form scores meet the SE threshold (the intended optimization path), the CAT result will have fewer dimensions than expected. Consumers that expect all 30 Big Five facets in a `cat-big5` result will find some missing. The profile dashboard would need to combine CAT results with fixed-form results to get a complete picture.

**Suggested Fix:**
Document this behavior explicitly, or have `scoreAdaptive` / `catSessionToScores` accept the `fixedFormScores` and include them for skipped dimensions (with a flag indicating "from fixed-form, not CAT").

---

### [LOW]: validateItemBank heuristic is too permissive

**File:** `web/src/scoring/cat-controller.ts:68-81`
**Category:** logic-correctness
**Confidence:** MEDIUM

**Description:**
The validation checks if all discrimination values are identical. A synthetic bank with just two different discrimination values (e.g., alternating 1.0 and 1.5) would pass validation despite being non-empirical. The check is a useful smoke test but could give false confidence.

**Impact:** Low -- the function already returns `false` with a console warning (not an error). It's advisory, not gating. But if a bank generator produces semi-random values, the warning would be suppressed even though the parameters aren't from real calibration data.

**Suggested Fix:**
Consider additional heuristics:
- Check variance of threshold parameters (real parameters have diverse thresholds)
- Check if threshold ordering is monotonic per item (already validated in item-banks.test.ts)
- Check reasonable range bounds (discrimination typically 0.3-3.0 for personality items)

---

## Summary

| Severity | Count | Key Issues |
|----------|-------|------------|
| CRITICAL | 2 | AdaptiveTestRunner ignores immutable return values from registerResponse and getNextItem |
| HIGH | 3 | Shared helper test gaps, PHQ-9 incomplete type visibility, selectNextItem double-filter |
| MEDIUM | 3 | autoScoreCompleted timing, thetaToPercentile boundary, CAT dimension ordering |
| LOW | 3 | Double keyboard handler, skipped dimension exclusion, validateItemBank heuristic |

**Overall assessment:** The scoring engine refactor (`groupResponsesByScale` / `aggregateScales`) is mathematically correct -- binary reverse scoring (1-v) and Likert reverse scoring (max+min-v) are properly preserved through the shared helper with distinct reverser lambdas. The shared normalizer pattern also preserves the distinct normalization logic (binary: raw*100, Likert: (raw-min)/(max-min)*100). The test at `scoring.test.ts:189-215` explicitly validates that the two reversers produce different results, which is excellent.

The CAT immutability refactor is well-designed at the controller level -- `registerResponse` and `getNextItem` both correctly return new session objects. The critical problem is at the integration layer: `AdaptiveTestRunner` was not updated to consume the immutable return values. This is a classic pattern when refactoring from mutable to immutable APIs -- the function signatures changed but the call sites were not all updated.

---

## Remediation Verification

For each of the 9 fixes from the iteration-1 synthesis:

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 1 | DRY scoring: extracted groupResponsesByScale() and aggregateScales() | **VERIFIED FIXED** | Helpers are correct, reverser/normalizer lambdas preserve distinct behavior. Test at scoring.test.ts:189-215 validates. |
| 2 | CAT JSON schema: itemId->id, itemText->text | **VERIFIED FIXED** | item-banks.test.ts lines 599-613 explicitly check for absence of legacy fields. JSON files match GRMItem interface. |
| 3 | thetaToPercentile: Math.round(cdf * 10000) / 100 | **VERIFIED FIXED** | grm-engine.ts:250 uses 10000/100 for 2 decimal places. Tests at grm-engine.test.ts:353-379 validate key values (50, ~84, ~16, 0, 100, symmetry). |
| 4 | Seed data fetch removal from store.ts | **VERIFIED FIXED** | store.ts no longer fetches seed-data.json or profile data. ProfileDashboard still fetches manifest.json for the dashboard view (which is appropriate -- display-only). |
| 5 | CAT controller immutable: getNextItem and registerResponse return new sessions | **VERIFIED FIXED** (controller) / **REGRESSION** (consumer) | The controller functions correctly return new immutable sessions. However, AdaptiveTestRunner.tsx does NOT consume the return values, creating a CRITICAL regression. See finding #1 above. |
| 6 | Double-submit guard: registerResponse early-returns unchanged session | **VERIFIED FIXED** | cat-controller.ts:235 checks `dimSession.administeredIds.has(itemId)` and returns `session` unchanged. Test at cat-controller.test.ts:127-140 validates same-reference return. |
| 7 | D1 rate limiting | **NOT IN SCOPE** | API/D1 code not included in this digest. Cannot verify. |
| 8 | Map->Record for completedInstruments | **NOT IN SCOPE** | tier-2/tier-3 code not included in this digest. Cannot verify. |
| 9 | InstrumentRunner sub-components extraction | **VERIFIED FIXED** | TestItemDisplay, LikertScale, ProgressBar, AdaptiveProgress extracted as presentational components. Used by both TestRunner and AdaptiveTestRunner. |

---

## Test Coverage Analysis

| Module | Coverage Status | Notes |
|--------|----------------|-------|
| `scoring/engine.ts` - scoreLikert | **Covered** | Mean, reverse, missing responses tested |
| `scoring/engine.ts` - scoreBinary | **Covered** | Mean, reverse, empty responses, reverser-difference tested |
| `scoring/engine.ts` - groupResponsesByScale | **Partially covered** | Exercised indirectly. No direct tests for edge cases (duplicates, non-numeric, unknown scaleIds) |
| `scoring/engine.ts` - aggregateScales | **Partially covered** | Exercised indirectly. No test for scales with zero matching items |
| `scoring/engine.ts` - scoreAdaptive | **Uncovered** | No direct test. Only exercised through AdaptiveTestRunner integration (which is broken) |
| `scoring/grm-engine.ts` | **Well covered** | 22 tests: category probabilities, information, theta estimation, percentile conversion, item selection |
| `scoring/cat-controller.ts` - initCATSession | **Covered** | Basic init, fixed-form skip, fixed-form prior tested |
| `scoring/cat-controller.ts` - getNextItem | **Partially covered** | Basic selection and complete-session tested. No test for exhausted-dimension-bank path or multi-dimension accumulation |
| `scoring/cat-controller.ts` - registerResponse | **Covered** | Theta update, maxItems completion, double-submit guard tested |
| `scoring/cat-controller.ts` - getCATProgress | **Covered** | Basic progress output tested |
| `scoring/cat-controller.ts` - catSessionToScores | **Covered** | Conversion with theta/se/normalized tested |
| `instruments/tiers.ts` | **Well covered** | All 3 tiers, replacement logic, registration verification tested |
| `instruments/ipip-neo-60.ts` | **Covered** | Metadata, scale structure, facet counts, neutral/max scoring tested |
| `instruments/ipip-neo-120.ts` | **Covered** | Metadata, scale structure, facet counts, scoring tested |
| `instruments/phq9-gad7.ts` | **Uncovered** | No direct test for proration logic, incomplete flag, or boundary (exactly MIN items) |
| `instruments/open-ended.ts` | **Uncovered** | No direct test for word counting or empty-string handling |
| `state/store.ts` | **Uncovered** | No tests for importData validation, autoScoreCompleted, or state transitions |
| `components/AdaptiveTestRunner.tsx` | **Uncovered** | No integration test. The CRITICAL bug would be caught by even a basic render test |
| `item-banks/*.json` | **Well covered** | Schema validation, field names, threshold ordering, legacy field absence tested |

### Critical Test Gaps

1. **AdaptiveTestRunner integration**: No test verifies that the handleResponse -> registerResponse -> sessionRef.current -> getNextItem pipeline works end-to-end. This is where the CRITICAL bug lives.

2. **PHQ-9/GAD-7**: A clinical screening instrument with custom scoring (proration, sum-not-mean) has zero dedicated tests. Given the stakes (depression/anxiety screening), this should be the most thoroughly tested scorer.

3. **store.ts**: Zero tests for state management logic. The importData function has validation logic that's untested, and autoScoreCompleted has the timing concern noted above.

4. **scoreAdaptive**: The bridge between CAT controller output and InstrumentResult format has no test, despite being the function that determines what users see for adaptive assessments.
