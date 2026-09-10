# Critical Review: Psyche Remediation Plan

## EXECUTIVE SUMMARY

Plan Quality: **CONDITIONAL** — Safe to execute only with mandatory revisions listed below.

The current plan is not execution-safe as written. The source item list in [analysis/BACKLOG.md:167](../../analysis/BACKLOG.md#L167) mixes true deployment blockers, optional refactors, and work that cannot be verified in this workspace because the `tier-3-nextjs` and `api` repos are not present. The largest problems are:

- CAT is functionally broken against the shipped JSON banks, independent of whether the banks are synthetic.
- The shared-package rollout is not deployable as written: [`web/package.json`](../../web/package.json#L2) is still `"private": true`, exports are incomplete, and `link:` is explicitly unsafe for committed CI/Vercel use.
- The current build/package surface still ships public seed/profile assets. Local verification on 2026-03-20 showed `pnpm build` emits `dist/seed-data.json`, `dist/profile.json`, and `dist/recover.html`, and `npm pack --dry-run` would publish those plus `tests/*` and `tsconfig.tsbuildinfo`.
- The passing suite is only 49 tests across 6 files and, per [docs/TECHNICAL-ASSESSMENT-2026-03-20.md:14](../../docs/TECHNICAL-ASSESSMENT-2026-03-20.md#L14), does not cover the production CAT JSON path, `scoreBinary`, or packaging/export contracts.

## CRITICAL FINDINGS

### 1. Unmapped/Inadequately Scoped Items

Source list: [analysis/BACKLOG.md:171-184](../../analysis/BACKLOG.md#L171)

| # | Item | Properly addressed? | Gap |
| --- | --- | --- | --- |
| 1 | Extract shared `psyche-web` package | No | The plan treats this as a refactor, but the real work is package hardening and delivery-contract definition. [`web/package.json:2-13`](../../web/package.json#L2) is still private, has no `files` allow-list, and does not export `./open-ended`. The delivery matrix explicitly says committed `link:` is unsafe in CI/Vercel: [docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md:5-9](../../docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md#L5), [docs/TECHNICAL-ASSESSMENT-2026-03-20.md:283-342](../../docs/TECHNICAL-ASSESSMENT-2026-03-20.md#L283). |
| 2 | Server-side score re-computation | No | This is framed as an architectural choice, but the underlying finding is data-integrity-critical for research/reporting: [docs/reviews/iteration-1/gemini-review.md:31-37](../../docs/reviews/iteration-1/gemini-review.md#L31). The API repo is absent, so the plan has no executable scope or privacy ADR attached. |
| 3 | Replace `Map` with `Record` in `SessionState` | Partial | This repo already uses `Record` in the standalone store: [web/src/state/store.ts:11-34](../../web/src/state/store.ts#L11). The real issue lives in `tier-3-nextjs`, which is not present here. This should be a consumer-repo task with serialization tests, not a repo-wide remediation item. |
| 4 | Refactor `InstrumentRunner` into sub-components | Partial | Defer is reasonable, but the scope is consumer-specific and the consumer repo is missing. The plan should explicitly rank this behind accessibility and contract issues instead of treating it as generic cleanup: [docs/reviews/iteration-1/gemini-review.md:183-189](../../docs/reviews/iteration-1/gemini-review.md#L183). |
| 5 | CAT controller immutable state | No | The plan understates the dependency chain. `getNextItem()` and `registerResponse()` are imperative and mutate cursor, completion state, response history, and `Set`/`Map` contents: [web/src/scoring/cat-controller.ts:160-260](../../web/src/scoring/cat-controller.ts#L160), [docs/TECHNICAL-ASSESSMENT-2026-03-20.md:383-517](../../docs/TECHNICAL-ASSESSMENT-2026-03-20.md#L383). This is last-phase work, not mid-plan cleanup. |
| 6 | Durable rate limiting (KV/D1) | No | The plan says session-level limits mitigate this. The review evidence says the in-memory Worker `Map` is effectively unenforceable under cold starts/isolate churn: [docs/reviews/iteration-1/gemini-review.md:41-47](../../docs/reviews/iteration-1/gemini-review.md#L41), [docs/reviews/iteration-1/gpt54-review.md:70-76](../../docs/reviews/iteration-1/gpt54-review.md#L70). This is a pre-deploy API requirement, not optional infrastructure polish. |
| 7 | CAT item bank schema fix + reverse scoring | No | This is not blocked on real IRT parameters. The shipped JSON uses `itemId`/`itemText` while the runtime expects `id`/`text`: [web/public/item-banks/big5-grm-params.json:2-15](../../web/public/item-banks/big5-grm-params.json#L2), [web/src/scoring/grm-engine.ts:14-29](../../web/src/scoring/grm-engine.ts#L14), [web/src/components/AdaptiveTestRunner.tsx:63-70](../../web/src/components/AdaptiveTestRunner.tsx#L63). Reverse flags exist in the banks and generator, but the CAT runtime never applies them: [analysis/scripts/generate_synthetic_banks.py:53-74](../../analysis/scripts/generate_synthetic_banks.py#L53), [web/src/scoring/grm-engine.ts:27-28](../../web/src/scoring/grm-engine.ts#L27), [web/src/scoring/cat-controller.ts:209-240](../../web/src/scoring/cat-controller.ts#L209). |
| 8 | DRY refactor scoring (`scoreBinary` + `scoreLikert`) | Partial | Deferring the refactor is sensible; executing it now is not. The current suite covers only `scoreLikert`: [web/tests/scoring.test.ts:1-97](../../web/tests/scoring.test.ts#L1). There is no `scoreBinary` coverage, no `NaN` cases, no zero-valid-response assertions, and no package-contract tests to catch drift across consumers. |
| 9 | Dual state management encapsulation | Partial | This is mis-scoped to the wrong repo. The standalone app already uses Zustand `persist`: [web/src/state/store.ts:36-200](../../web/src/state/store.ts#L36). The actual problem is the `tier-3-nextjs` dual React/localStorage model described in [docs/reviews/iteration-1/gemini-review.md:133-139](../../docs/reviews/iteration-1/gemini-review.md#L133). |
| 10 | `thetaToPercentile` precision | Yes | Safe to defer. The function is tested and the impact is cosmetic: [web/src/scoring/grm-engine.ts:235-245](../../web/src/scoring/grm-engine.ts#L235), [web/tests/grm-engine.test.ts:153-179](../../web/tests/grm-engine.test.ts#L153). |
| 11 | CAT content balancing | Yes, with caveat | Safe to defer only after CAT is made functional. The current selector is simple max-information: [web/src/scoring/grm-engine.ts:251-267](../../web/src/scoring/grm-engine.ts#L251). It is a valid enhancement backlog item, not the current failure mode. |
| 12 | Seed data fetch optimization | No | This is scoped as a performance tweak, but the real issue is that sensitive/public assets still ship. `seed-data.json` and `profile.json` remain in `public/`: [web/public/seed-data.json:2](../../web/public/seed-data.json#L2), [web/public/profile.json:1](../../web/public/profile.json#L1). The standalone store only gates the fetch in production; it does not stop those files from being deployed: [web/src/state/store.ts:172-197](../../web/src/state/store.ts#L172). |

### 2. Dependency & Ordering Issues

The plan does not define formal execution phases. The only concrete sequence is the order of the 12-item list in [analysis/BACKLOG.md:173-184](../../analysis/BACKLOG.md#L173). That implied order is wrong for execution.

Proposed sequence implied by the plan:

```text
1. Shared package extraction
2. Server-side score recomputation
3. Map -> Record
4. InstrumentRunner refactor
5. CAT immutable state
6. Durable rate limiting
7. CAT schema + reverse fix
8. Scoring DRY refactor
9. Dual-state encapsulation
10. thetaToPercentile precision
11. CAT content balancing
12. Seed-data fetch optimization
```

Actual dependency graph:

```text
Public-asset removal/package hygiene
  -> any deploy, publish, or consumer rollout

Verification hardening
  -> CAT schema fix
  -> package hardening
  -> scoring refactor
  -> CAT immutable rewrite

CAT schema + reverse fix
  -> CAT immutable rewrite
  -> any CAT-specific enhancement such as content balancing

Package hardening + export surface + delivery choice
  -> tier-3-nextjs integration

Privacy ADR + API repo in scope
  -> server-side score recomputation

API repo in scope
  -> durable rate limiting
```

Incorrect ordering:

1. Item 5 before item 7 is wrong. The immutable CAT rewrite depends on a correct loader and stable item IDs first: [docs/TECHNICAL-ASSESSMENT-2026-03-20.md:603-633](../../docs/TECHNICAL-ASSESSMENT-2026-03-20.md#L603).
2. Item 8 before verification hardening is wrong. Current coverage will not protect `scoreBinary` or edge-case normalization behavior: [docs/TECHNICAL-ASSESSMENT-2026-03-20.md:14-16](../../docs/TECHNICAL-ASSESSMENT-2026-03-20.md#L14), [web/tests/scoring.test.ts:1-97](../../web/tests/scoring.test.ts#L1).
3. Item 1 is underspecified. Before consumer integration, the package needs hardening, export completion, and a committed delivery path that is not `link:`: [docs/TECHNICAL-ASSESSMENT-2026-03-20.md:283-379](../../docs/TECHNICAL-ASSESSMENT-2026-03-20.md#L283).
4. Item 12 is in the wrong class entirely. It is not late-phase performance work; it is a pre-deploy asset/privacy blocker.
5. Items 2 and 6 cannot be safely sequenced with local code refactors because the relevant `api` repo is not available in this workspace.

High-signal example:

[`web/package.json:6-13`](../../web/package.json#L6)
```json
"exports": {
  "./types": "./src/instruments/types.ts",
  "./registry": "./src/instruments/registry.ts",
  "./tiers": "./src/instruments/tiers.ts",
  "./scoring": "./src/scoring/engine.ts",
  "./init-lite": "./src/instruments/init-lite.ts",
  "./init-standard": "./src/instruments/init-standard.ts"
}
```

That export surface is not enough to remove prompt duplication, so "extract shared package" is not a single step.

### 3. High-Risk Items Marked as "Low-Risk"

1. CAT item bank schema fix + reverse scoring is materially understated. The CAT path is non-functional with the shipped banks, not merely "experimental": [docs/TECHNICAL-ASSESSMENT-2026-03-20.md:18-130](../../docs/TECHNICAL-ASSESSMENT-2026-03-20.md#L18).
2. Durable rate limiting is understated. The review evidence explicitly says the current Worker `Map` resets on cold start and isolate eviction: [docs/reviews/iteration-1/gemini-review.md:41-47](../../docs/reviews/iteration-1/gemini-review.md#L41).
3. Seed data fetch optimization is understated. The real risk is public deployment of sensitive/static data, not a wasted request: [docs/reviews/iteration-1/gpt54-review.md:10-16](../../docs/reviews/iteration-1/gpt54-review.md#L10), [web/public/seed-data.json:2](../../web/public/seed-data.json#L2).
4. Shared package extraction is understated. It is a deployment-contract migration with CI/Vercel failure modes, not just duplication cleanup: [docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md:7](../../docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md#L7), [docs/TECHNICAL-ASSESSMENT-2026-03-20.md:294-342](../../docs/TECHNICAL-ASSESSMENT-2026-03-20.md#L294).
5. Server-side score re-computation is understated. If stored scores feed research or reports, trusting client-submitted scores is not optional: [docs/reviews/iteration-1/gemini-review.md:31-37](../../docs/reviews/iteration-1/gemini-review.md#L31).

High-signal example:

[`web/src/components/AdaptiveTestRunner.tsx:63-70`](../../web/src/components/AdaptiveTestRunner.tsx#L63)
```ts
fetch(itemBankUrl)
  .then((r) => {
    if (!r.ok) throw new Error(`Failed to load item bank: ${r.status}`);
    return r.json();
  })
  .then((data: GRMItem[]) => {
    setItemBank(data);
```

This code trusts a runtime shape the shipped JSON does not satisfy.

### 4. Verification Gaps

The current suite is:

- `pnpm test`: 49 tests across 6 files, passing locally on 2026-03-20.
- Missing the exact areas the plan wants to modify: [docs/TECHNICAL-ASSESSMENT-2026-03-20.md:14-16](../../docs/TECHNICAL-ASSESSMENT-2026-03-20.md#L14).

Per executable phase, current tests would miss:

| Phase | Current suite would miss |
| --- | --- |
| Pre-phase: deployment hygiene | No test checks `dist/` or npm pack contents for `seed-data.json`, `profile.json`, `recover.html`, `tests/*`, or `tsconfig.tsbuildinfo`. |
| Phase 1: verification hardening | No coverage for `web/src/state/store.ts` import/export/rehydration logic, malformed imports, duplicate item IDs, or `autoScoreCompleted()`: [web/src/state/store.ts:131-233](../../web/src/state/store.ts#L131). |
| Phase 2: CAT schema/reverse fix | No asset-backed test loads `web/public/item-banks/*.json`; no test asserts defined `id`/`text`; no test covers reversed CAT items; no exact item-selection traces: [web/tests/cat-controller.test.ts:12-167](../../web/tests/cat-controller.test.ts#L12). |
| Phase 3: package hardening and tier-3 integration | No package-export tests, no `npm pack` audit, no clean install/build against npm or tarball, no `transpilePackages` verification, and the consumer repo is absent. |
| Phase 4: scoring refactor | `scoreBinary()` is untested, and `scoreLikert()` is only tested for three happy-path cases: [web/tests/scoring.test.ts:1-97](../../web/tests/scoring.test.ts#L1). Missing `NaN`, out-of-range, zero-valid-response, and `min === max` assertions. |
| Phase 5: CAT immutable rewrite | No test covers `Map`/`Set` serialization, duplicate `registerResponse()` calls, multi-dimension skip chains, or React contract changes in [`web/src/components/AdaptiveTestRunner.tsx`](../../web/src/components/AdaptiveTestRunner.tsx#L56). |
| Phase 6: API-side architecture | No executable evidence is available in this repo for durable rate limiting, server-side recomputation, TTL cleanup, or CORS/session-auth behavior. Those claims remain unverified here. |

### 5. Overcomplicated Approaches

1. Do not use committed `link:` as the shared-package solution. The simpler and safer solution is published npm as the committed path, `link:` only as a local override, and tarball only as fallback: [docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md:7-9](../../docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md#L7).
2. Do not do a full immutable CAT rewrite now. The simpler path is: add a loader adapter, runtime validation, and golden-trace tests; keep the imperative controller until behavior is stable.
3. Do not genericize scoring prematurely. The simpler extraction is only the shared response-map / scale-bucketing / result-assembly pieces, while keeping reversal and normalization explicit per scorer: [docs/TECHNICAL-ASSESSMENT-2026-03-20.md:270-273](../../docs/TECHNICAL-ASSESSMENT-2026-03-20.md#L270).
4. Do not spend time on `Map`-to-`Record` in this repo. The standalone store already uses `Record`; the remaining issue is in `tier-3-nextjs`, where the simpler solution is to unify persistence behind one hook/store before changing data structures.
5. Do not "optimize seed fetch." Delete sensitive/public assets from `public/`, keep only `.example` fixtures, and block them in CI. That solves the real problem instead of shaving a request.
6. Do not split `InstrumentRunner` first. If the goal is correctness, either narrow the component contract or fix the missing behavior/accessibility first; decomposition can wait.

### 6. Missing Edge Cases

1. CAT banks loaded from actual shipped JSON with `itemId`/`itemText` transport keys.
2. Reversed CAT items. The banks contain `reverse: true`, but the runtime never inverts the category before theta estimation.
3. Duplicate CAT `registerResponse()` calls for the same item ID.
4. Multi-dimension CAT skip chains where several dimensions are already complete or empty.
5. `scoreBinary()` with malformed or imported responses, including `NaN`, non-0/1 values, and zero valid responses.
6. `importData()` with structurally valid but semantically wrong payloads, duplicate responses, or oversized localStorage writes.
7. Clean-checkout package installation in a consumer repo without local relative paths.
8. Package export drift, especially missing `./open-ended` or prompt-only exports.
9. Production build/package artifact audits for sensitive files or unnecessary test/build outputs.
10. Worker cold-start/multi-region rate-limit bypass and non-research session cleanup in the API layer.

### 7. CI/Deployment Implications

1. Asset-hygiene work changes deployment gating immediately. `pnpm build` currently emits `dist/seed-data.json`, `dist/profile.json`, and `dist/recover.html`. If those files stay, every static deployment republishes them.
2. Package hardening changes release workflow. Publishing `psyche-web` requires removing `"private": true`, adding a `files` allow-list, pinning the package name, and auditing the packed artifact. `npm pack --dry-run` currently includes `public/*`, `tests/*`, and `tsconfig.tsbuildinfo`.
3. Tier-3 integration cannot rely on local success. CI must build from a clean checkout with `transpilePackages` configured and without relative `link:` dependencies: [docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md:28-38](../../docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md#L28), [docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md:124-138](../../docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md#L124).
4. CAT fixes affect shipped static assets and cacheability. Changing bank schema or adding a loader adapter requires asset versioning or cache-busting, or stale JSON can reintroduce failures.
5. Refactor-only phases provide no deployment value until test hardening lands. Running them before coverage expansion increases release risk with no operational upside.
6. API-side items are operational, not local. Durable rate limiting and server-side score validation imply DB/KV migrations, deployment coordination, and privacy/legal review. None of that is represented in the current repo.

## TOP 5 CRITICAL BLOCKERS

1. Public sensitive/static assets still ship.
   Mitigation: remove `web/public/seed-data.json` and non-example profile data from shipped assets, move dev fixtures outside `public/`, add a `files` allow-list in [`web/package.json`](../../web/package.json#L1), and add CI checks that fail if `dist/` or `npm pack --dry-run` contains PHQ/GAD seed data or identified profiles.
2. CAT is non-functional with the shipped banks.
   Mitigation: add a load-time adapter or normalize the JSON, implement CAT reverse handling, add asset-backed integration tests, and remove/disable CAT instruments from heavy-tier execution until this passes.
3. The shared-package rollout is not deployable as written.
   Mitigation: harden `psyche-web` first: publishable package identity, `files` allow-list, `./open-ended` or prompt-only export, package-contract tests, and npm as the committed delivery path. `link:` stays local-only.
4. The test suite cannot protect the planned refactors.
   Mitigation: before any DRY or immutable-state work, add tests for `scoreBinary`, store import/export/rehydration, CAT golden traces, asset-backed bank loading, and package-export/pack contents.
5. API-side trust and rate-limit controls are unresolved and not in scope here.
   Mitigation: bring the `api` and `tier-3-nextjs` repos into the remediation workspace, write an ADR for raw-response retention/server recomputation, and implement durable rate limiting before approving public/report rollout.

## REVISED EXECUTION PLAN

1. Phase 0: deployment hygiene.
   Remove sensitive/public assets from `public/`; add package `files` allow-list; verify `pnpm build` and `npm pack --dry-run` no longer ship seed/profile/recovery/test artifacts.
2. Phase 1: verification hardening.
   Add store tests, `scoreBinary` tests, asset-backed CAT loader tests, CAT trace tests, and package export/pack tests.
3. Phase 2: CAT runtime correction.
   Fix bank schema adaptation, add runtime validation, implement reverse handling, and keep CAT disabled from production-heavy workflows until the corrected path passes.
4. Phase 3: package hardening.
   Finalize package name/versioning, export surface, and committed delivery mechanism. Approve npm as default, tarball as fallback, `link:` as local override only.
5. Phase 4: cross-repo integration.
   In `tier-3-nextjs`, add `transpilePackages`, swap imports, and run clean-checkout build/test. In `api`, implement durable rate limiting and resolve the score-trust/privacy contract.
6. Phase 5: optional refactors only after the above is green.
   Scoped scoring helper extraction first. CAT immutable-state rewrite, `Map` cleanup, dual-state rework, and component decomposition remain deferred unless a demonstrated bug requires them.

## ACCEPT/DEFER DECISIONS

| Item | Decision | Reason |
| --- | --- | --- |
| Extract shared `psyche-web` package | Accept only with mandatory re-scope | Must be package hardening + delivery-contract work, not a blind refactor. |
| Server-side score re-computation | Defer pending ADR and API repo review | High importance, but not executable safely in this workspace. |
| Replace `Map` with `Record` in `SessionState` | Defer | Mis-scoped to `tier-3-nextjs`; low value until consumer state work resumes. |
| Refactor `InstrumentRunner` into sub-components | Defer | Maintainability-only. Fix correctness/accessibility first. |
| CAT controller immutable state | Defer | Wrong order. Needs corrected CAT runtime and trace tests first. |
| Durable rate limiting (KV/D1) | Accept as mandatory pre-deploy API work | This should not remain optional if report generation is public. |
| CAT item bank schema fix + reverse scoring | Accept as immediate blocking work | Current runtime is broken now. |
| DRY refactor scoring (`scoreBinary` + `scoreLikert`) | Defer until verification hardening is complete | Unsafe with present coverage. |
| Dual state management encapsulation | Defer | Consumer-specific and not verifiable here. |
| `thetaToPercentile` precision | Defer as-is | Cosmetic only. |
| CAT content balancing | Defer as-is | Legitimate enhancement, not a current blocker. |
| Seed data fetch optimization | Reject as written; replace with asset-removal work | The blocker is shipped sensitive assets, not request count. |

## VERIFICATION CHECKLIST

- `pnpm test` passes after adding new coverage, including `scoreBinary`, store import/export, CAT loader, and CAT trace tests.
- `pnpm build` produces no `dist/seed-data.json`, no non-example public profile data, and no unnecessary recovery/debug assets unless explicitly approved.
- `npm pack --dry-run` shows a hardened artifact: no `public/seed-data.json`, no `tests/*`, no `tsconfig.tsbuildinfo`, no accidental build junk.
- A test loads the real JSON bank asset and proves the first loaded item has defined `id`, `text`, `dimensionId`, and correct reverse behavior.
- A test suite exercises duplicate item IDs, malformed imports, and zero-valid-response scoring cases.
- Package export tests prove `types`, `registry`, `tiers`, `scoring`, `init-lite`, `init-standard`, and any prompt-sharing entrypoint resolve correctly.
- Clean-checkout consumer build passes using npm or committed tarball, with `transpilePackages` configured and no relative `link:` dependency in the committed lockfile.
- API-side verification exists for durable rate limiting, session cleanup policy, and either server-side recomputation or an approved alternative with explicit scope limits.
- Cross-repo execution is pinned to explicit SHAs for `psyche`, `tier-3-nextjs`, and `api` before rollout.

## RECOMMENDATION

Do not approve execution of the remediation plan as currently written.

Approve only if all of the following conditions are met:

1. The plan is re-scoped so that public asset removal, CAT runtime correction, package hardening, and verification expansion come before any optional refactor.
2. `link:` is removed as a committed production path; npm or tarball becomes the documented CI/Vercel-safe delivery mechanism.
3. CAT schema/reverse handling is treated as a functional blocker, not deferred behind immutable-state cleanup.
4. API-side items are moved into an explicit cross-repo phase with the `api` repo in scope and a written privacy/data-integrity decision.

Without those revisions, the plan should be deferred. Executing it in its current form would spend time on lower-value refactors while leaving broken CAT behavior, unsafe deployment packaging, and unverified cross-repo assumptions in place.
