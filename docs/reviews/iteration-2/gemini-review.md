# Gemini 3.1 Pro Code Review — Iteration 2 (Post-Remediation)

**Date:** 2026-03-20
**Scope:** Full — architecture and performance verification
**Reviewer:** Gemini 3.1 Pro (via Claude Opus 4.6 orchestration)
**Codebase:** Psyche psychometric assessment framework (web/)

---

## Findings

### [CRITICAL]: AdaptiveTestRunner discards immutable registerResponse return value

**File:** `web/src/components/AdaptiveTestRunner.tsx:109-115`
**Category:** react-patterns
**Confidence:** CERTAIN

**Description:** The `handleResponse` callback calls `registerResponse(sessionRef.current, ...)` but discards the returned new `CATSession`. The immutable refactor in iteration 1 changed `registerResponse` from mutating in place to returning a new session object. However, `AdaptiveTestRunner` was never updated to capture and store this return value. Lines 109-115:

```typescript
registerResponse(
  sessionRef.current,
  itemBank,
  currentItem.item.id,
  category,
  DEFAULT_STOPPING,
);
// Return value discarded — sessionRef.current still points to stale state
```

Lines 117-118 then read from `sessionRef.current` which was never updated:

```typescript
setTotalItems(sessionRef.current.totalItemsAdministered);  // Always 0
setProgress(getCATProgress(sessionRef.current));             // Always initial state
```

**Impact:** The adaptive testing feature is completely broken. The CAT session never advances — theta is never updated, items are never marked as administered, the session never completes. Users will see the same item repeatedly or get stuck. This is a regression introduced by the immutable state refactor.

**Suggested Fix:** Either (a) capture the return value and assign it to `sessionRef.current`, or (b) migrate from `useRef` to `useState` for proper React state management. Option (b) is preferred:

```typescript
const [session, setSession] = useState<CATSession | null>(null);

const handleResponse = useCallback((value: number) => {
  if (!session || !itemBank || !currentItem) return;
  const category = value - 1;
  const newSession = registerResponse(session, itemBank, currentItem.item.id, category, DEFAULT_STOPPING);
  setSession(newSession);
}, [session, itemBank, currentItem]);

useEffect(() => {
  if (!session || !itemBank) return;
  setProgress(getCATProgress(session));
  setTotalItems(session.totalItemsAdministered);
  if (session.complete) {
    const result = scoreAdaptive(instrumentId, session);
    completeInstrument(result);
    onComplete();
    return;
  }
  const timer = setTimeout(() => {
    const next = getNextItem(session, itemBank);
    setCurrentItem(next);
    if (!next) { /* handle graceful completion */ }
  }, 200);
  return () => clearTimeout(timer);
}, [session, itemBank]);
```

---

### [HIGH]: Duplicate global keyboard listeners between LikertScale and parent components

**File:** `web/src/components/LikertScale.tsx:18-22` and `web/src/components/AdaptiveTestRunner.tsx:147-160`
**Category:** component-design
**Confidence:** CERTAIN

**Description:** `LikertScale` registers its own global `keydown` listener on `window` (lines 18-22 of LikertScale.tsx). Simultaneously, `AdaptiveTestRunner` registers a separate global `keydown` listener for keys 1-5 (lines 147-160). When `AdaptiveTestRunner` renders `TestItemDisplay` which renders `LikertScale`, both listeners fire on the same keypress.

The same pattern exists in `TestRunner.tsx` — it has its own Likert keyboard handling via the arrow key navigation effect, plus `LikertScale` adds another.

**Impact:** Each key press triggers two event handlers. While the current behavior may appear to work (both call the same callback chain), this is fragile. Race conditions between the two handlers could cause double-response registration. The `handleLikertResponse` callback in TestRunner and the `onChange` callback in LikertScale are the same function reference passed down, so both handlers call it — potentially causing double auto-advance.

**Suggested Fix:** Remove the `useEffect` keyboard handler from `LikertScale.tsx` entirely. Make `LikertScale` a purely visual component. Centralize all keyboard handling in the parent component (`TestRunner` or `AdaptiveTestRunner`) which has full context about the current item type.

---

### [HIGH]: getNextItem filters full item bank on every call — O(N) per item

**File:** `web/src/scoring/cat-controller.ts:84-86` (in getNextItem)
**Category:** performance
**Confidence:** CERTAIN

**Description:** Every call to `getNextItem` runs `itemBank.filter(item => item.dimensionId === dimId && ...)` which scans the entire item bank array. For a Big Five CAT with 30 facets and ~300+ items in the bank, this runs 300+ comparisons per item selection.

Additionally, `selectNextItem` (called from `getNextItem`) receives the filtered `dimBank` but also receives `dimSession.administeredIds` — yet the bank was already filtered to exclude administered items, making the `administered` Set check partially redundant.

**Impact:** With typical item banks (100-500 items) and ~60-120 items administered per session, the total filtering work is O(items_administered * bank_size). Not a user-visible performance issue at current scale, but poor algorithmic design that would degrade with larger banks.

**Suggested Fix:** Pre-group items by dimension in `initCATSession` and store a `Map<string, GRMItem[]>` in the `CATSession` object. `getNextItem` then retrieves the dimension's items in O(1) and only needs to filter out administered items from the smaller per-dimension array.

---

### [MEDIUM]: init.ts duplicates all imports from init-lite.ts and init-standard.ts

**File:** `web/src/instruments/init.ts` vs `web/src/instruments/init-lite.ts` and `web/src/instruments/init-standard.ts`
**Category:** architecture
**Confidence:** CERTAIN

**Description:** `init.ts` individually imports all 39 instruments using phase-based comments. Meanwhile, `init-lite.ts` and `init-standard.ts` were created as tier-based registration files that import subsets. These files are completely parallel — `init.ts` does not import or chain through `init-lite.ts`/`init-standard.ts`.

The app (`App.tsx`) imports `init.ts`. The tier-based files (`init-lite.ts`, `init-standard.ts`) are exported in `package.json` for external consumers but create a maintenance burden — any new instrument must be added to both `init.ts` AND the appropriate tier init file.

**Impact:** Risk of instruments being registered in one file but not the other, leading to subtle bugs where an instrument works in the standalone app but not when consumed as a library (or vice versa). Also makes the codebase harder to understand — two different registration strategies for the same instruments.

**Suggested Fix:** Refactor `init.ts` to chain through the tier files:

```typescript
// init.ts — register ALL instruments via tier chain
import "./init-standard";  // includes init-lite
import "./ipip-neo-120";
import "./hexaco-200";
// ... only Heavy-tier additions
import "./cat-big5";
import "./cat-hexaco";
// ... Phase 6 Heavy instruments
```

---

### [MEDIUM]: TestRunner does not use TestItemDisplay — inconsistent rendering

**File:** `web/src/components/TestRunner.tsx` and `web/src/components/TestItemDisplay.tsx`
**Category:** code-quality
**Confidence:** CERTAIN

**Description:** `TestItemDisplay` was extracted as a shared component for rendering item text + response widgets. `AdaptiveTestRunner` correctly uses it (line 214). However, `TestRunner` renders all item types inline — Likert via `<LikertScale />`, binary with inline buttons, numeric with inline `<input>`, and text with inline `<textarea>`. This creates two different code paths for the same visual output.

`TestItemDisplay` only supports `likert` and `binary` response types. It doesn't handle `numeric` or `text`, which may be why `TestRunner` doesn't use it — but this means the extraction is incomplete.

**Impact:** Visual inconsistencies between fixed-form and adaptive test runners. Bug fixes to item rendering need to be applied in two places. The inline binary button rendering in `TestRunner` (lines 2298-2328) duplicates the binary rendering in `TestItemDisplay` (lines 2485-2515) almost character-for-character.

**Suggested Fix:** Extend `TestItemDisplay` to support all 4 response types (`likert`, `binary`, `numeric`, `text`), then refactor `TestRunner` to delegate item rendering to `TestItemDisplay`. This reduces `TestRunner` to orchestration logic only.

---

### [MEDIUM]: PHQ-9/GAD-7 builds its own response map instead of using shared helpers

**File:** `web/src/instruments/phq9-gad7.ts:524-579`
**Category:** code-quality
**Confidence:** CERTAIN

**Description:** The `scorePhqGad` function constructs its own `Map(session.responses.map(...))` and iterates items manually, duplicating the response-mapping logic that `groupResponsesByScale` already provides. This was the exact pattern that the DRY refactor was meant to eliminate.

The reason it doesn't use the shared helpers is legitimate — PHQ-9/GAD-7 uses **sum scoring with proration** rather than mean scoring, and has a minimum-items threshold per subscale. The shared `aggregateScales` hardcodes `mean = sum / count` which is wrong for clinical sum-scored instruments.

**Impact:** No functional bug, but a missed opportunity. The response grouping logic (building a map, iterating items, checking for numeric values) is duplicated. If `groupResponsesByScale` were used for just the grouping step, the proration logic could still be custom.

**Suggested Fix:** Either (a) export `groupResponsesByScale` and use it in `scorePhqGad` for the grouping step while keeping custom aggregation, or (b) accept the duplication as justified by the fundamentally different scoring model (sum vs. mean, proration, minimum-items thresholds, incomplete flags). Option (b) is reasonable — the PHQ-9/GAD-7 scoring is sufficiently different that forcing it through the shared pipeline would create awkward abstractions.

**Recommendation:** Accept as-is. The clinical scoring model is legitimately different. Document the decision with a brief comment.

---

### [MEDIUM]: scoreLikert normalizer uses inst.items.find() per scale — O(S*N) lookup

**File:** `web/src/scoring/engine.ts:583-591` (normalizer lambda in scoreLikert)
**Category:** performance
**Confidence:** CERTAIN

**Description:** The normalizer lambda passed to `aggregateScales` calls `inst.items.find((i) => i.scaleId === scaleId)` for every scale to determine the Likert min/max. This scans the entire items array per scale. For NEO-300 with 30 facet scales + 5 domain scales, this runs 35 * 300 = 10,500 comparisons.

**Impact:** Not user-visible at current scale (sub-millisecond), but architecturally wasteful. The `aggregateScales` function already has the items for each scale — the normalizer just can't access them because of the function signature.

**Suggested Fix:** Change `aggregateScales`'s normalizer signature to pass the items array directly:

```typescript
normalizer: (raw: number, items: { item: Item; value: number }[]) => number,
```

Then the normalizer can access `items[0]?.item.response` instead of re-scanning the full list.

---

### [LOW]: registerResponse uses itemBank.find() for item lookup — O(N) per response

**File:** `web/src/scoring/cat-controller.ts:1128` (in registerResponse)
**Category:** performance
**Confidence:** CERTAIN

**Description:** `registerResponse` calls `itemBank.find((i) => i.id === itemId)` which is a linear scan. This runs once per response, so total work is O(items_administered * bank_size).

**Impact:** Negligible at current bank sizes (100-500 items). Would become relevant only with item banks of 1,000+ items.

**Suggested Fix:** Create a `Map<string, GRMItem>` index during `initCATSession` for O(1) lookups. This can be combined with the dimension-grouping optimization.

---

### [LOW]: Session completion check creates temporary array

**File:** `web/src/scoring/cat-controller.ts:1180`
**Category:** performance
**Confidence:** CERTAIN

**Description:** `[...newDims.values()].every((d) => d.complete)` creates a temporary array from the Map values iterator solely to call `.every()`. This runs on every response registration.

**Impact:** Negligible — Map sizes are 5-30 dimensions. The allocation is tiny.

**Suggested Fix:** Replace with a `for...of` loop over `newDims.values()`:

```typescript
let allComplete = true;
for (const d of newDims.values()) {
  if (!d.complete) { allComplete = false; break; }
}
```

Or add a `completedDimensionCount` to `CATSession` and check `count === dimensionOrder.length`.

---

### [LOW]: registerInstrument validation iterates items per scale — O(S*N) at registration

**File:** `web/src/instruments/registry.ts:19-37`
**Category:** performance
**Confidence:** CERTAIN

**Description:** `registerInstrument` runs `instrument.items.filter((i) => i.scaleId === scale.id)` for every scale during validation. For NEO-300 this is 35 * 300 = 10,500 comparisons at startup.

**Impact:** Registration is a one-time cost at module load. Not a runtime concern. However, the same items-per-scale grouping could be pre-computed and cached if this validation becomes a bottleneck with more instruments.

**Suggested Fix:** No immediate fix needed. If startup performance becomes an issue, group items by scaleId once and iterate the groups.

---

### [INFO]: AdaptiveProgress SE convergence formula may not render intuitively

**File:** `web/src/components/AdaptiveProgress.tsx:30`
**Category:** component-design
**Confidence:** MEDIUM

**Description:** The SE progress bar width is computed as:

```typescript
const seProgress = Math.min(1, (1 - dim.se / Math.max(dim.se, targetSE * 3)));
```

When `dim.se > targetSE * 3`, the denominator becomes `dim.se`, so the formula becomes `1 - 1 = 0`. When `dim.se === targetSE`, it becomes `1 - targetSE / (targetSE * 3) = 1 - 0.333 = 0.667`. When `dim.se === 0`, it becomes `1 - 0 = 1.0`.

This means the bar reaches only ~67% when the stopping criterion is met, jumping to 100% only when the dimension is marked complete. Users may wonder why the bar isn't full when SE has reached the target.

**Impact:** Visual-only. No functional effect.

**Suggested Fix:** Consider a simpler formula like `Math.min(1, targetSE / dim.se)` which reaches 100% exactly when SE meets the threshold.

---

### [INFO]: init-lite.ts and init-standard.ts are exported in package.json but have no tests verifying their registration

**File:** `web/package.json:48-49`, `web/tests/tiers.test.ts`
**Category:** code-quality
**Confidence:** HIGH

**Description:** `package.json` exports `init-lite` and `init-standard` for external consumers. The tier tests in `tiers.test.ts` import `./init` (the full registration file), not the tier-specific files. There are no tests that verify `init-lite.ts` alone registers exactly the 15 lite instruments, or that `init-standard.ts` registers exactly the 20 standard instruments.

**Impact:** If someone imports `psyche-web/init-lite` and expects only lite instruments to be registered, there's no test validating that contract.

**Suggested Fix:** Add tier-specific registration tests:

```typescript
// tests/init-lite.test.ts
import "../src/instruments/init-lite";
import { getInstrumentIds } from "../src/instruments/registry";
import { getInstrumentsForTier } from "../src/instruments/tiers";

it("init-lite registers exactly the lite tier instruments", () => {
  const registered = getInstrumentIds();
  const expected = getInstrumentsForTier("lite");
  expect(registered.sort()).toEqual(expected.sort());
});
```

---

## Summary

| Severity | Count | Key Themes |
|----------|-------|------------|
| CRITICAL | 1 | AdaptiveTestRunner discards immutable session return value — CAT is broken |
| HIGH | 2 | Duplicate keyboard listeners; O(N) item bank filtering per CAT item selection |
| MEDIUM | 4 | Parallel init files; TestItemDisplay underutilized; PHQ-9 bypasses shared helpers; normalizer O(S*N) |
| LOW | 3 | Linear item lookup in registerResponse; temporary array in completion check; registration validation cost |
| INFO | 2 | SE progress formula visual quirk; missing tier-specific registration tests |

**Architecture assessment:** The `groupResponsesByScale`/`aggregateScales` DRY refactor is well-designed. The abstraction level is correct — they extract the common pattern (response mapping + grouping + aggregation) while allowing scoring-strategy-specific behavior through the `reverser` and `normalizer` function parameters. The PHQ-9/GAD-7 not using them is a justifiable exception due to fundamentally different scoring semantics (clinical sum-scoring with proration).

**Performance assessment:** The immutable CAT refactor introduces expected overhead (`new Map()` per response, spread operators for Set construction). These are acceptable for the session sizes involved (5-30 dimensions, 60-120 total items). The real performance concern is the repeated linear scanning of the full item bank in `getNextItem` and `registerResponse`, which could be eliminated with pre-grouped indexes.

**React patterns assessment:** The critical finding is the `sessionRef.current` / immutable return value mismatch. This is a classic pitfall when converting from mutable to immutable patterns — the consumer was not updated to match the new contract.

---

## Remediation Verification

| # | Fix | Status | Notes |
|---|-----|--------|-------|
| 1 | DRY scoring refactor (groupResponsesByScale + aggregateScales) | **VERIFIED FIXED** | Helpers are well-designed with proper abstraction. Both scoreLikert and scoreBinary use them correctly. |
| 2 | CAT item bank JSON schema fix (itemId->id, itemText->text) | **VERIFIED FIXED** | Test in `item-banks.test.ts` explicitly asserts no legacy fields exist. Schema matches GRMItem interface. |
| 3 | thetaToPercentile precision fix | **VERIFIED FIXED** | Now uses `Math.round(cdf * 10000) / 100` for two decimal places. Clamping at +/-6 instead of +/-7. Tests verify theta=0->50, theta=1->~84, symmetry. |
| 4 | Seed data fetch removal from onRehydrateStorage | **VERIFIED FIXED** | `onRehydrateStorage` now only calls `autoScoreCompleted()`. No network fetch on rehydration. |
| 5 | CAT controller immutable state refactor | **PARTIALLY FIXED** | `registerResponse` and `getNextItem` correctly return new sessions. **However, `AdaptiveTestRunner` discards the return value (CRITICAL bug).** The immutable contract is correct at the controller level but broken at the consumer level. |
| 6 | Double-submit guard in registerResponse | **VERIFIED FIXED** | `dimSession.administeredIds.has(itemId)` check returns unchanged session reference on duplicate. Test confirms `session2 === session` (same reference). |
| 7 | D1-backed rate limiting (server-side) | **NOT VERIFIABLE** | Server-side change not included in code digest. Cannot verify from client code alone. |
| 8 | Map->Record conversion in SessionState | **VERIFIED FIXED** | `store.ts` uses `Record<string, InstrumentSession>` and `Record<string, InstrumentResult>` — compatible with JSON serialization for Zustand persist. |
| 9 | InstrumentRunner extracted into sub-components | **PARTIALLY FIXED** | `LikertScale` is properly extracted and used by both runners. `TestItemDisplay` is extracted but only used by `AdaptiveTestRunner`, not `TestRunner`. Binary, numeric, and text response types remain inline in `TestRunner`. `ProgressBar` is extracted. `AdaptiveProgress` is extracted. The extraction is partial — 3 of the claimed 5 sub-components are used consistently. |
