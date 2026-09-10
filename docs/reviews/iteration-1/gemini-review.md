# Gemini 3.1 Pro Code Review -- Iteration 1
**Date:** 2026-03-20
**Scope:** full -- ~35 files reviewed (code digest, 4982 lines)
**Reviewer:** Gemini 3.1 Pro via Claude Opus 4.6 orchestration
**Method:** Code digest split into 4 sections (core lib, React components, API/server, IRT/CAT), each analyzed independently, then synthesized with cross-validation

---

## Findings

### [CRITICAL]: No Error Checking in Next.js API Client
**File:** tier-3-nextjs/src/lib/psyche/api.ts (all functions)
**Category:** code-quality
**Confidence:** CERTAIN
**Description:** Every function in the Next.js API client returns `res.json()` without checking `res.ok`. A 404, 500, or any HTTP error resolves as a successful promise. Callers must manually inspect every response object for an `error` property, and forgetting to do so causes silent failures or runtime errors when accessing properties like `sessionData.id` on an error object.
**Impact:** A server outage or expired session produces confusing behavior instead of clear error messages. The assess page does check `sessionData.error` in some places but not all (e.g., `api.saveResponses` is fire-and-forget with `.catch(() => {})`).
**Suggested Fix:** Adopt the Astro client's `fetchJson` wrapper pattern that checks `res.ok` and throws a typed `ApiError`. Better yet, extract a single shared API client used by both Next.js and Astro deployments to eliminate the duplication entirely.

---

### [CRITICAL]: Code Duplication Across Three Deployment Targets
**File:** web/src/instruments/ vs tier-3-nextjs/src/lib/psyche/ vs tier-2-astro/src/lib/psyche/
**Category:** duplication
**Confidence:** CERTAIN
**Description:** The core library (types.ts, registry.ts, tiers.ts, engine.ts, all instrument definitions, init files, API client) is manually copied across three codebases: the standalone Vite app, the Next.js integration, and the Astro integration. The Next.js copy already drifts -- its `ScaleScore` type lacks `theta`, `se`, and `itemsAdministered` fields present in the standalone version. The API clients differ in error handling approach. The `init.ts` files differ in which instruments they register. Comments like `// Synced from psyche/web/src/instruments/tiers.ts -- must stay in sync` and `// BACKLOG: Switch to psyche-web link dependency` acknowledge the problem.
**Impact:** Bug fixes must be applied in 3 places. Scoring logic drift means the same instrument could produce different results in different deployments. Type mismatches between standalone and Next.js create invisible correctness bugs.
**Suggested Fix:** Extract the core library into a shared package (private npm package, workspace link, or git submodule). Both deployment targets import from the single source. This is already noted in the BACKLOG -- it should be prioritized.

---

### [CRITICAL]: Client-Computed Scores Trusted by Server
**File:** api/src/routes/psyche.ts (`saveScores`), tier-3-nextjs/src/lib/psyche/api.ts (`saveScores`)
**Category:** architecture
**Confidence:** CERTAIN
**Description:** The `saveScores` endpoint accepts client-computed scores and stores them directly in the database without any server-side validation or re-computation. A user can intercept the fetch request and submit arbitrary scores.
**Impact:** All stored scores are untrustworthy for research purposes. This undermines the stated goal of feeding results into a research paper. The report generation prompt then uses these potentially-manipulated scores.
**Suggested Fix:** Move scoring to the server, or at minimum validate that submitted scores are consistent with stored raw responses. Given that raw responses are only stored with consent level 2 (research opt-in), server-side re-scoring would require storing responses at consent level 1 as well (or computing scores from responses before discarding them).

---

### [HIGH]: In-Memory Rate Limiting Lost on Restart
**File:** api/src/routes/psyche.ts:4576-4593
**Category:** architecture
**Confidence:** CERTAIN
**Description:** The `reportRateMap` is an in-memory `Map` that tracks report generation requests. On a Cloudflare Worker, this state is ephemeral -- it resets on every deployment, cold start, or isolate eviction (which can happen frequently). The 10-requests-per-hour limit is effectively unenforceable.
**Impact:** An attacker could generate unlimited reports by waiting for isolate recycling, or by targeting different edge locations. Each report costs money via the DeepInfra API call.
**Suggested Fix:** Use Cloudflare KV, Durable Objects, or the D1 database itself for rate limiting state. A simple approach: store a `report_count` and `report_window_start` column on the session, or a separate rate-limit table.

---

### [HIGH]: Missing Accessibility Features in InstrumentRunner
**File:** tier-3-nextjs/src/components/psyche/InstrumentRunner.tsx
**Category:** accessibility
**Confidence:** CERTAIN
**Description:** Several WCAG violations:
1. The progress bar (`div` with percentage width) has no ARIA attributes -- screen readers cannot determine assessment progress. Needs `role="progressbar"`, `aria-valuenow`, `aria-valuemin="0"`, `aria-valuemax="100"`.
2. The Likert scale buttons lack `role="radiogroup"` on their container and `role="radio"` + `aria-checked` on individual buttons. Screen readers see them as generic buttons with no indication of which is selected or that they form a mutually exclusive group.
3. Focus is not programmatically managed when advancing between questions. After answering, keyboard/screen reader users lose their place and must navigate back to the question area.
4. Keyboard shortcut hints ("Press 1-5 on keyboard") are hidden on mobile (`hidden md:block`) with no `sr-only` alternative.
**Impact:** The assessment is difficult to impossible to complete for screen reader users. Given the 260-1130 item count, poor focus management makes keyboard-only completion extremely tedious.
**Suggested Fix:**
- Add `role="progressbar"` with appropriate ARIA attributes to progress bars
- Wrap Likert options in `role="radiogroup"` with `aria-labelledby` pointing to the question text
- After advancing to a new question, programmatically focus the question text or first interactive element via `useRef` + `useEffect`
- Use `sr-only` class for keyboard hints instead of `hidden md:block`

---

### [HIGH]: Monolithic Instrument Loading (Bundle Size)
**File:** web/src/instruments/init.ts, tier-3-nextjs/src/lib/psyche/init-standard.ts
**Category:** performance
**Confidence:** HIGH
**Description:** All instrument definitions are eagerly loaded via side-effect imports. The `init.ts` file imports all 39 instruments unconditionally. Each instrument file contains its full item text (e.g., IPIP-NEO-300 has 300 items with full text strings, HEXACO-60 has 60 items, RIASEC-48 has 48 items). The Lite tier loads ~15 instruments but ships the code for all of them if `init.ts` is used.
**Impact:** The JavaScript bundle includes hundreds of KB of static string data that may never be needed. Users taking the Lite tier still download Standard and Heavy tier instruments. The tiered init files (`init-lite.ts`, `init-standard.ts`) partially mitigate this for the Next.js integration, but the standalone app's `init.ts` loads everything.
**Suggested Fix:** The tiered init files are the right pattern -- ensure all entry points use them. For further optimization, consider lazy-loading instrument definitions via dynamic `import()` when the user starts a specific instrument, rather than at page load. The registry would need to support async instrument resolution.

---

### [HIGH]: Unsafe JSON.parse in importData Without Validation
**File:** web/src/state/store.ts:1204-1215
**Category:** code-quality
**Confidence:** CERTAIN
**Description:** `importData` calls `JSON.parse(json)` without a try-catch and performs no schema validation on the result. If the user imports a malformed file, the application crashes. If the file has unexpected property types (e.g., `sessions` is a string instead of an object), the state becomes corrupted.
**Impact:** A user importing an old or corrupted export file crashes the application. There is no recovery path -- the user must clear localStorage manually.
**Suggested Fix:** Wrap in try-catch, validate the parsed structure matches the expected schema (at minimum check types of `sessions` and `results` are objects), and show a user-facing error message on failure.

---

### [MEDIUM]: DRY Violation Between scoreBinary and scoreLikert
**File:** web/src/scoring/engine.ts:378-486
**Category:** code-quality
**Confidence:** CERTAIN
**Description:** `scoreBinary` and `scoreLikert` share ~80% identical code: building a response map, grouping items by scale, computing mean scores per scale, and constructing the result object. The only differences are: (1) binary uses `1 - value` for reversal vs Likert uses `max + min - value`, and (2) binary normalizes as `raw * 100` vs Likert normalizes as `((raw - min) / (max - min)) * 100`. This is duplicated again in the Next.js copy at `tier-3-nextjs/src/lib/psyche/engine.ts`.
**Impact:** A bug fix in one scoring function may not be applied to the other. The pattern is repeated in 2 codebases (6 total instances of this logic across standalone + Next.js, scoring + binary + Likert).
**Suggested Fix:** Extract common logic into a shared `scoreGeneric` function that takes a reversal strategy and normalization strategy as parameters. Both `scoreBinary` and `scoreLikert` become thin wrappers.

---

### [MEDIUM]: Expensive Computations on Every Render in Assess Page
**File:** tier-3-nextjs/src/app/psyche/assess/page.tsx:2717-2721
**Category:** performance
**Confidence:** HIGH
**Description:** The assess page calls `getAllInstruments()` and `getInstrumentsForTier(tier)` on every render (inside the component body, outside any `useMemo`). These iterate the full registry and perform Set operations respectively. While not catastrophically expensive, they run on every state update (every response, every phase change).
**Impact:** Minor performance overhead. Each re-render iterates the 20+ registered instruments unnecessarily. More significant on low-end mobile devices during rapid keyboard input.
**Suggested Fix:** Wrap both calls in `useMemo`:
```typescript
const allRegistered = useMemo(() => getAllInstruments(), []);
const tierIds = useMemo(() => getInstrumentsForTier(tier).filter(id => id !== 'open-ended'), [tier]);
```

---

### [MEDIUM]: CAT Controller Mutates Session State Directly
**File:** web/src/scoring/cat-controller.ts (getNextItem, registerResponse)
**Category:** react-patterns
**Confidence:** HIGH
**Description:** Both `getNextItem` and `registerResponse` directly mutate the `CATSession` object passed to them (e.g., `session.currentDimensionIndex++`, `dimSession.complete = true`, `dimSession.administered.push(response)`). React's reconciliation relies on immutable state updates to detect changes and trigger re-renders.
**Impact:** If a React component holds a CATSession in state and passes it to these functions, React will not detect the mutation and the UI will not update. The developer must manually create a new state reference after calling these functions, which is error-prone.
**Suggested Fix:** Refactor the controller functions to be pure -- accept the current state, return a new state object. Alternatively, use Immer to allow mutation-style code that produces immutable updates. This would also make the CAT state serializable for localStorage persistence.

---

### [MEDIUM]: Weak Type Safety in Server Route Handler
**File:** api/src/routes/psyche.ts
**Category:** code-quality
**Confidence:** CERTAIN
**Description:** Database rows are typed as `Record<string, unknown>` and accessed via unsafe `as` casts throughout: `session.consent_given as number`, `session.expires_at as string`, `session.scores_json as string`. There are no runtime checks that these fields exist or have the expected types. If a database migration changes a column name or type, the error manifests at runtime, not compile time.
**Impact:** Subtle bugs from type mismatches are invisible to the TypeScript compiler. A `null` value in `consent_given` cast to `number` could cause `< 2` to behave unexpectedly (null < 2 is false in JS, but the intent may differ).
**Suggested Fix:** Define typed interfaces for database entities and validate at the database boundary using Zod or a similar runtime validation library.

---

### [MEDIUM]: Dual State Management (React + localStorage) in Assess Page
**File:** tier-3-nextjs/src/app/psyche/assess/page.tsx
**Category:** architecture
**Confidence:** HIGH
**Description:** The assess page maintains session state in both React `useState` (with a `Map`-based `completedInstruments`) and localStorage (serialized as plain objects via `saveToStorage`). These two sources can diverge if a localStorage write fails silently (quota exceeded, private browsing) while React state has already updated.
**Impact:** The user sees their progress in the current session, but refreshing the page loses it. There is no feedback to the user that persistence failed.
**Suggested Fix:** Encapsulate the dual-state pattern in a custom hook that ensures consistency, or use a single Zustand store with the `persist` middleware (similar to the standalone app's approach). If localStorage write fails, show a non-blocking warning.

---

### [MEDIUM]: Session ID as Sole Authentication
**File:** api/src/routes/psyche.ts (all endpoints)
**Category:** architecture
**Confidence:** HIGH
**Description:** Session endpoints are authenticated solely by knowing the UUID session ID in the URL path. There is no additional token, cookie, or signature. UUIDs are cryptographically random (via `crypto.randomUUID()`), making brute-force impractical, but the ID can leak through browser history, referrer headers, or shared URLs.
**Impact:** If a session ID is exposed, anyone can view scores, generate a report, or withdraw consent for that session. The 7-day TTL and anonymous design limit the blast radius, but it is still a privacy concern for an assessment containing sensitive psychological data (PHQ-9 depression scores, Dark Triad, attachment style).
**Suggested Fix:** For the current anonymous design, this is an acceptable tradeoff -- adding auth would require accounts, which contradicts the privacy-first design. Mitigations: set `Referrer-Policy: no-referrer` on the assess page, use POST for session creation (already done), and avoid putting session IDs in URL paths visible in browser history (use a short-lived cookie or header instead).

---

### [MEDIUM]: Missing `text` Response Handler for Open-Ended in InstrumentRunner
**File:** tier-3-nextjs/src/components/psyche/InstrumentRunner.tsx
**Category:** code-quality
**Confidence:** HIGH
**Description:** The InstrumentRunner renders handlers for `likert`, `binary`, `numeric`, and `multiple-choice` response types, but has no handler for the `text` response type. The open-ended instrument uses `{ type: "text", minWords: 30 }`. If InstrumentRunner were used for the open-ended instrument, it would render a blank question with no input.
**Impact:** Currently mitigated because the assess page separates open-ended into its own InterviewFlow component. However, this creates a hidden assumption: InstrumentRunner cannot handle all instrument types despite accepting a generic `Instrument` prop. This is a type-level lie.
**Suggested Fix:** Either add a `text` response type handler to InstrumentRunner (textarea with word count validation), or narrow the `InstrumentRunner` props type to exclude text-type instruments (e.g., `instrument: QuantitativeInstrument`).

---

### [LOW]: Normalization Assumes Uniform Response Format Within Scale
**File:** web/src/scoring/engine.ts:465-469
**Category:** code-quality
**Confidence:** MEDIUM
**Description:** `scoreLikert` normalizes scale scores using the `min` and `max` from the first item found for that scale (`instrument.items.find((i) => i.scaleId === scale.id)`). This assumes all items on the same scale share the same response format. If a scale mixed 5-point and 7-point Likert items, normalization would be incorrect.
**Impact:** Currently no instruments in the battery mix response formats within a scale, so this is not an active bug. However, the assumption is undocumented and could cause incorrect scores if a future instrument violates it.
**Suggested Fix:** Add a comment documenting the assumption. Optionally, add a validation check at instrument registration time that verifies all items on a scale share the same response format.

---

### [LOW]: `isAdaptiveInstrument` Uses Unsafe Type Check
**File:** web/src/instruments/registry.ts:135-138
**Category:** code-quality
**Confidence:** CERTAIN
**Description:** `isAdaptiveInstrument` checks `"adaptive" in reg.instrument` with a cast to `Record<string, unknown>`. The `Instrument` interface does not include an `adaptive` property, so this is a runtime duck-type check that bypasses TypeScript's type system.
**Impact:** If the `adaptive` property were renamed or removed from the CAT instrument definitions, this function would silently return `false` with no compiler warning.
**Suggested Fix:** Add `adaptive?: boolean` to the `Instrument` interface in types.ts, then remove the cast.

---

### [LOW]: InstrumentRunner Component is Monolithic
**File:** tier-3-nextjs/src/components/psyche/InstrumentRunner.tsx
**Category:** react-patterns
**Confidence:** MEDIUM
**Description:** InstrumentRunner handles state management, keyboard shortcuts, progress display, auto-advance logic, and rendering for 4 different response types (Likert, binary, numeric, multiple-choice) all in a single ~350-line component.
**Impact:** Readability and testability are reduced. Adding a new response type requires modifying the entire component. Response-type-specific logic (e.g., Likert label rendering, numeric input handling) cannot be tested in isolation.
**Suggested Fix:** Extract response type renderers into separate components: `LikertResponse`, `BinaryResponse`, `NumericResponse`, `MultipleChoiceResponse`. Extract the keyboard handler into a custom hook `useInstrumentKeyboard`. The main InstrumentRunner becomes a controller that delegates rendering.

---

### [LOW]: Interview Prompts Duplicated Between open-ended.ts and InterviewFlow.tsx
**File:** web/src/instruments/open-ended.ts:1636-1646, tier-3-nextjs/src/components/psyche/InterviewFlow.tsx:3741-3752
**Category:** duplication
**Confidence:** CERTAIN
**Description:** The 10 interview prompts are defined independently in both the `open-ended` instrument definition and the `InterviewFlow` component. If a prompt is edited in one location, the other becomes stale.
**Impact:** A prompt mismatch would cause the interview responses to be scored against different prompts than were actually presented, or create confusion in the report generation.
**Suggested Fix:** Define prompts once (in `open-ended.ts` or a shared constants file) and import them in InterviewFlow.

---

### [LOW]: Seed Data Fetch on Every Hydration
**File:** web/src/state/store.ts:1221-1241
**Category:** performance
**Confidence:** MEDIUM
**Description:** The Zustand store's `onRehydrateStorage` callback fetches `/seed-data.json` on every page load. If the seed data does not exist (404), the fetch still fires and the error is silently swallowed. If seed data has already been merged, the comparison logic (`seedSessionCount > currentSessionCount`) prevents re-merging, but the network request still occurs.
**Impact:** An unnecessary network request on every page load. Minor performance impact, but adds noise to server logs and network waterfall.
**Suggested Fix:** Use a flag in localStorage (e.g., `psyche-seed-merged: true`) to skip the fetch after first successful merge. Alternatively, check for the seed file's existence with a HEAD request first.

---

## Gemini False Positives (Corrected During Synthesis)

The following findings were raised by Gemini but determined to be incorrect or misleading during cross-validation:

1. **"Critical Bug in `itemInformation` -- omits `a^2` term"**: FALSE POSITIVE. The code does multiply by `a * a` on line 629 (`return a * a * info`). Gemini misread the function, likely because the `a^2` multiplication happens at the return statement rather than inside the loop. The mathematical implementation is correct.

2. **"Counter-intuitive `importData` merge order"**: DESIGN DECISION, NOT BUG. The merge order `{ ...data.sessions, ...currentState.sessions }` prioritizes current state over imported data. The inline comment explicitly states `"don't overwrite completed results"`. This is intentional -- a user who has made progress since their last export should not lose that progress by importing an older file.

3. **"`scoreBinary` reversal bug -- `1 - value` assumes 0/1"**: SPECULATIVE, NOT A BUG. Binary responses in this system are always 0 or 1 (see `InstrumentRunner.tsx` where binary buttons map to `val = idx === 0 ? 1 : 0`). The reversal `1 - value` is correct for this value domain. The suggestion to "treat binary as 2-point Likert" is unnecessary complexity.

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 3 |
| HIGH | 4 |
| MEDIUM | 7 |
| LOW | 5 |

**Top 3 priorities for remediation:**
1. Extract shared library package to eliminate 3-way code duplication (addresses CRITICAL duplication + HIGH bundle size)
2. Add error handling to Next.js API client (addresses CRITICAL error handling gap)
3. Add accessibility attributes to InstrumentRunner (addresses HIGH a11y violations)

---

## False Negatives Check

Areas that could NOT be fully reviewed due to code digest limitations:

1. **Instrument data correctness**: Only 5 of 39 instrument definitions were included in the digest. Reverse-scoring correctness, item text accuracy, and scale assignments for the remaining 34 instruments were not verified.
2. **GRM item bank data**: The actual JSON files containing IRT parameters (discrimination, thresholds) for the CAT instruments were not included. Parameter validity, threshold ordering, and dimensional alignment could not be checked.
3. **CSS/responsive design**: Only Tailwind classes were visible. Actual rendering, responsive breakpoints, and dark/light mode support were not tested.
4. **Test coverage**: No test files were included in the digest. Coverage of scoring edge cases, CAT stopping criteria, and state management cannot be assessed.
5. **Build configuration**: Vite/Next.js/Astro build configs were not included. Tree-shaking effectiveness, code splitting, and actual bundle sizes are unknown.
6. **Database schema**: The D1 schema was not included. Foreign key constraints, indexes, and cascade delete behavior for consent withdrawal could not be verified.
7. **CORS configuration**: API server CORS headers were not visible. Cross-origin request handling between the frontend domains and `api.ashitaorbis.com` was not reviewed.
8. **Astro components**: Only the Astro API client was included. The Astro equivalents of InstrumentRunner, ConsentFlow, etc., were not reviewed for feature parity or accessibility.
9. **MCPSetupGuide clipboard fallback**: The `document.execCommand('copy')` fallback is deprecated and may not work in all browsers. Not verified whether the primary `navigator.clipboard.writeText` path is sufficient.
10. **InterviewFlow word count validation**: The 500-word soft limit uses `maxWords + 50` buffer, but the server-side limit is 50KB raw body size. The relationship between word count and byte size for non-ASCII text was not analyzed.
