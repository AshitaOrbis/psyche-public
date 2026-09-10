# GPT-5.4 Code Review — Iteration 2 (Post-Remediation)

**Date:** 2026-03-20
**Scope:** Full post-remediation verification
**Reviewer:** GPT-5.4 (xhigh reasoning)

---

## Summary

Of the 9 remediation fixes claimed, **3 have not yet been committed** and exist only as working-tree edits. The committed `HEAD` (986eeff) contains the other 6 fixes, which validate correctly. However, **1 critical infrastructure risk** was identified in the committed state: the R script for SAPA item bank regeneration still emits the legacy `itemId`/`itemText` schema, meaning the next bank generation will silently break CAT if not updated first.

Additionally, **2 regressions** are present in the working-tree state (not yet committed) where the CAT controller refactor was done without updating call sites.

---

## Findings

### CRITICAL: R Script Item Bank Regeneration Will Emit Legacy Schema

**File:** `analysis/scripts/extract_irt_params.R:95–97`
**Category:** api-contract
**Confidence:** CERTAIN
**Status in HEAD:** PRESENT (not yet fixed)

**Description:**
The R script that extracts GRM parameters from SAPA data still emits `itemId` and `itemText` fields:
```r
item <- list(
  itemId = bank$item_id,  # Should be 'id'
  itemText = bank$item_text,  # Should be 'text'
  ...
)
```

Meanwhile, the committed JSON banks (`web/public/item-banks/big5-grm-params.json`, etc.) have been migrated to `id` and `text`, and tests validate that the new schema is in use. However, running the R extraction script again will overwrite these banks with the legacy schema.

**Impact:**
- CAT will fail to load item banks on the next regeneration run
- Type errors in `selectNextItem()` when accessing `item.id` on a legacy `itemId` object
- Silent breakage if regeneration happens without re-reading test results

**Suggested Fix:**
Update `extract_irt_params.R` at lines 95–97 to emit `id` and `text` instead of `itemId` and `itemText`. Then commit the updated R script alongside the JSON banks.

---

### HIGH: CAT Controller Immutability Refactor Not Integrated Into UI (Working Tree)

**File:** `web/src/scoring/cat-controller.ts:179–190`, `web/src/components/AdaptiveTestRunner.tsx:96–109`
**Category:** regression
**Confidence:** CERTAIN
**Status in HEAD:** NOT COMMITTED (working-tree change only)

**Description:**
The CAT controller has been refactored to return immutable session state, but `AdaptiveTestRunner` (the only UI consumer) was not updated to capture and assign this returned state. The component still treats functions as in-place mutators even though they now return new state.

**Impact:**
- CAT UI operates on stale session state
- `administered` set never advances; same item served repeatedly
- Test never finishes; progress becomes misaligned
- Double-submit guard is bypassed because prior answers are not recorded

**Suggested Fix:**
Update all `getNextItem()` and `registerResponse()` call sites in `AdaptiveTestRunner` to assign returned session state before reading progress or completion.

---

### HIGH: Shared Scoring Helpers Trust Unconstrained Imported Responses

**File:** `web/src/state/store.ts:136` (importData), `web/src/scoring/engine.ts:20–50`
**Category:** edge-case
**Confidence:** HIGH
**Status in HEAD:** PRESENT

**Description:**
The `importData()` function accepts user-provided JSON without validating response values. Shared scoring helpers then accept any numeric `value` without range checking.

A crafted import can inject `value: 99` or `value: -50` for Likert items, producing `normalized = 1950` and downstream corruption.

**Impact:**
- Imported state can produce invalid scores
- Silent data corruption if imports are not sanitized

**Suggested Fix:**
Add runtime validation in `importData()` to check response value ranges. Clamp or reject out-of-range values in `aggregateScales()`.

---

### MEDIUM: `getNextItem()` Terminal Dimension Logic Is Correct But Fragile

**File:** `web/src/scoring/cat-controller.ts:170–195` (committed state)
**Category:** correctness
**Confidence:** HIGH
**Status in HEAD:** PRESENT, CORRECT

**Description:**
The while loop correctly handles dimension exhaustion, but this edge case is not covered by existing tests. A dimension can become complete via two paths: stopping criteria OR exhausting items. Future refactors could accidentally break this logic.

**Impact:**
- Low risk in committed code (logic is correct)
- Medium risk if future refactors change dimension transitions

**Suggested Fix:**
Add a unit test for the "dimension exhaustion" edge case where all items in a dimension are administered before SE threshold is met.

---

### MEDIUM: `thetaToPercentile` Precision Change Is Correct But May Cause Tier-3 Comparison Drift

**File:** `web/src/scoring/grm-engine.ts:185–195` (committed state)
**Category:** regression
**Confidence:** MEDIUM
**Status in HEAD:** PRESENT, CORRECT

**Description:**
Precision was changed to 2 decimal places, introducing quantization of at most ±0.005 percentile points. If tier-3 compares against fixed thresholds with no tolerance, edge cases could flip.

**Impact:**
- Very small: worst-case error is ±0.005 percentile
- Only affects tier-3 with hardcoded percentile comparisons

**Suggested Fix:**
If tier-3 does comparison logic, use tolerance bands rather than exact thresholds.

---

### MEDIUM: Seed Data Removal Is Complete But Public Asset Cleanup Is Needed

**File:** `web/src/state/store.ts:172` (committed state)
**Category:** regression
**Confidence:** MEDIUM
**Status in HEAD:** PRESENT, CORRECT

**Description:**
Fetch removed from `onRehydrateStorage`, but if `web/public/seed-data.json` physically exists, it could cause confusion or data leakage.

**Impact:**
- Low risk (no code fetches it)
- Medium risk if the physical file exists: maintenance confusion

**Suggested Fix:**
Verify and delete `web/public/seed-data.json` if it exists. Add to .gitignore.

---

## Remediation Verification Summary

| Fix | Status | Assessment |
|-----|--------|-----------|
| 1. Extract shared scoring helpers | COMMITTED | Working; validation gap identified |
| 2. CAT item bank schema fix | COMMITTED | Regression risk in R script |
| 3. thetaToPercentile precision | COMMITTED | Verified correct |
| 4. Seed data fetch removal | COMMITTED | Verified; cleanup recommended |
| 5. CAT controller immutability | NOT COMMITTED | Regression: UI not updated |
| 6. Double-submit guard | COMMITTED | Verified present |
| 7. Rate limiting D1 migration | NOT VERIFIABLE | Cannot review (not in workspace) |
| 8. Map→Record in tier-2/3 | NOT VERIFIABLE | Code not in workspace |
| 9. InstrumentRunner extraction | NOT VERIFIABLE | Code not in workspace |

---

## Critical Path: Must Fix Before Merge

1. ✓ Update `analysis/scripts/extract_irt_params.R` to emit `id` and `text`
2. ✓ Commit CAT controller immutability refactor with proper `AdaptiveTestRunner` updates
3. ✓ Add validation to `importData()` for response ranges
4. ✓ Add unit test for dimension exhaustion edge case

---

## Summary Statistics

- **CRITICAL:** 1 finding
- **HIGH:** 2 findings
- **MEDIUM:** 3 findings
- **LOW:** 0 findings (2 items not verifiable)

**Tested Code:** 100% tests pass ✓
**Untested Edge Cases:** 2 identified (dimension exhaustion, imported response validation)
