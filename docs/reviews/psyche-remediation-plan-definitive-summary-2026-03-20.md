# Definitive Summary: Psyche Remediation Plan

This summary is the plan-ready decision document for the remediation backlog currently listed in [`analysis/BACKLOG.md`](../../analysis/BACKLOG.md). It answers the seven original review questions in one place. The conclusion is unchanged from the full review set: the remediation plan is not approvable as written. It must be re-scoped around deployment hygiene, verification hardening, CAT runtime correction, package hardening, and explicit cross-repo rollout before implementation is approved.

## 1. Unmapped Items: Which Of The 12 Are Actually Addressed?

The 12 deferred items are not equally well framed. Two are correctly deferrable as written, four are real but mis-scoped or badly sequenced, and six are framed in the wrong problem class.

| Item | Status | Definitive conclusion |
| --- | --- | --- |
| Extract shared `psyche-web` package | Not adequately addressed | This is not just duplication cleanup. It is package hardening, export-surface definition, artifact auditing, versioning, and choosing a CI-safe delivery path. |
| Server-side score re-computation | Not adequately addressed | This is a trust-boundary and privacy decision tied to the missing `api` repo. It cannot remain a vague architectural follow-up. |
| Replace `Map` with `Record` in `SessionState` | Partially addressed | The real issue is not in this repo's standalone store. It belongs in `tier-3-nextjs` and should be treated as consumer-side cleanup, not core remediation. |
| Refactor `InstrumentRunner` into sub-components | Partially addressed | This is maintainability work, not release-blocking remediation. It should stay deferred unless a concrete correctness bug requires it. |
| CAT controller immutable state | Not adequately addressed | This is late-phase work only. It depends on fixing CAT loading, schema adaptation, reverse handling, and trace stability first. |
| Durable rate limiting (KV/D1) | Not adequately addressed | This is a mandatory API pre-deploy control if public report generation remains in scope. It is not optional infrastructure polish. |
| CAT item bank schema fix + reverse scoring | Not adequately addressed | This is an immediate correctness blocker. The shipped JSON transport shape does not match runtime expectations, and reverse flags are ignored. |
| DRY refactor scoring (`scoreBinary` + `scoreLikert`) | Partially addressed | Deferral is correct for now, but only because the current test surface is too weak to protect the refactor safely. |
| Dual state management encapsulation | Partially addressed | This is also consumer-repo work, not a primary remediation item in this workspace. |
| `thetaToPercentile` precision | Correctly addressed | Safe to defer. Impact is cosmetic and already bounded by existing tests. |
| CAT content balancing | Correctly addressed with caveat | Safe to defer only after CAT works correctly with real runtime assets. |
| Seed data fetch optimization | Not adequately addressed | This is not a performance tweak. The real problem is that seed/profile/recovery artifacts still ship publicly. |

Bottom line: the plan cannot remain a flat backlog.

## 2. Dependency Gaps: What Is The Correct Order?

The original backlog order is unsafe because it starts with package extraction and refactors before it secures the deployment surface or fixes known correctness failures. The actual dependency graph is stricter:

- Deployment hygiene must happen before any deploy, publish, or consumer rollout.
- Verification hardening must happen before CAT correction, scoring refactors, or CAT-internal rewrites.
- CAT schema adaptation and reverse handling must happen before any CAT enhancement or immutable rewrite.
- Package hardening must happen before `tier-3-nextjs` consumes `psyche-web`.
- API trust decisions and durable rate limiting must happen in an explicit cross-repo phase, not as local cleanup.

The corrected order is:

1. Phase 0: deployment hygiene
2. Phase 1: verification hardening
3. Phase 2: CAT runtime correction
4. Phase 3: package hardening
5. Phase 4: cross-repo integration
6. Phase 5: optional refactors only after all blocker phases are green

This is the minimum safe sequence.

## 3. Risk Underestimation: Which "Low-Risk" Items Are Not Low Risk?

Several items were minimized because they were described as refactors, optimizations, or future hardening. That is inaccurate.

The most materially understated items are:

- `CAT item bank schema fix + reverse scoring`: this is a current functional failure, not an experimental improvement. The CAT runtime expects different field names than the shipped JSON banks provide, and reversed items are not inverted before estimation.
- `Durable rate limiting`: an in-memory Worker `Map` is not durable under cold starts, isolate churn, or multi-instance execution. If public report generation remains exposed, this is mandatory pre-deploy infrastructure.
- `Seed data fetch optimization`: the issue is not an extra request. The issue is that sensitive or non-example assets remain deployable in public build/package output.
- `Extract shared psyche-web package`: this is not harmless deduplication. It changes package identity, exports, pack contents, CI behavior, and consumer integration.
- `Server-side score re-computation`: if downstream research or reporting trusts client-submitted scores, this is a data-integrity decision, not optional architectural taste.

The plan repeatedly describes release blockers as cleanup. That framing must be corrected before approval.

## 4. Verification Gaps: What Would The Current Tests Miss?

The current passing suite is too narrow to protect the proposed work. It covers some local happy paths, but it does not cover the places where the remediation plan is most likely to fail.

Today’s tests would miss:

- Shipped artifact leaks. There is no automated assertion on `dist/` contents or `npm pack --dry-run` contents, so seed/profile/recovery files, tests, or build junk can still ship unnoticed.
- Scoring regressions outside the happy path. `scoreBinary()` lacks meaningful coverage, and edge cases like malformed values, zero valid responses, `NaN`, or normalization boundaries are not protected.
- Store import/export/rehydration failures. Malformed payloads, duplicates, rehydration problems, and persistence edge cases could break without test detection.
- CAT asset drift. No test loads the real shipped JSON bank assets used at runtime, so a schema mismatch between code and assets can remain invisible.
- CAT reverse errors. No test proves that reversed items are inverted before theta estimation, so trait estimates can be wrong while tests still pass.
- CAT behavior drift. There are no golden-trace tests that lock expected item-selection and response-history behavior after the runtime is corrected.
- Package contract failures. There are no export-surface or clean-install tests proving that `psyche-web` can be consumed safely by a downstream app.
- Cross-repo failures. There is no evidence in this repo for `tier-3-nextjs` integration, durable API rate limiting, or approved server-side trust controls.

A green local suite today does not mean the remediation work is safe to execute.

## 5. Overcomplicated Approaches: What Should Be Simplified?

The safest implementation path is narrower than the current remediation framing.

The plan should explicitly avoid these overcomplicated approaches:

- Do not use committed `link:` as the shared-package delivery mechanism. The simpler committed path is a published package, with tarball as fallback and `link:` reserved for local development only.
- Do not start with a full immutable CAT rewrite. The simpler path is to adapt or normalize the loader, validate runtime shape, implement reverse handling, and add golden-trace tests first.
- Do not genericize scoring before behavior is protected. Extract only clearly shared mechanics after tests exist; keep reversal and normalization explicit until proven stable.
- Do not spend time on `Map` to `Record` cleanup in this repo as if it were blocking work. The remaining problem is consumer-side.
- Do not "optimize seed fetch." Remove protected artifacts from shipped outputs and gate them in CI. That solves the real problem directly.
- Do not prioritize `InstrumentRunner` decomposition ahead of correctness, packaging, and deployment controls.

The issue is not scope reduction. It is sequencing and simplification.

## 6. Missing Edge Cases: Which Scenarios Remain Untested?

Several failure modes remain untested and are directly relevant to the deferred backlog:

- Real shipped CAT banks loaded with `itemId` and `itemText` transport keys instead of the runtime `id` and `text` shape.
- Reversed CAT items where `reverse: true` must be applied before estimation.
- Duplicate `registerResponse()` calls for the same CAT item.
- Multi-dimension CAT skip chains where some dimensions are already complete or empty.
- `scoreBinary()` with malformed, imported, or non-binary values, plus zero-valid-response cases.
- Normalization edge cases such as degenerate ranges or invalid intermediate values.
- Store import of structurally valid but semantically wrong payloads, including duplicate responses and persistence corruption.
- Clean-checkout consumer installation without local path assumptions.
- Package export drift, especially on prompt/open-ended entrypoints.
- Worker cold-start or multi-instance rate-limit bypass on the API side.

These are the regressions the current plan is most likely to introduce.

## 7. CI And Deployment Implications: What Changes Operationally?

The remediation plan has direct release-process consequences. Deployment hygiene becomes a gate, not a cleanup task: `pnpm build` and `npm pack --dry-run` must be audited, and CI must fail if protected assets or stray files appear. Package hardening changes the release contract: `psyche-web` needs a final identity, a `files` allow-list, a complete export surface, and a committed CI-safe delivery path. Consumer rollout must be verified from clean checkout with pinned versions or SHAs, not local path success. CAT asset changes require cache or version management so stale banks cannot reintroduce runtime failures. API-side items imply operational work outside this repo, including durable storage and an approved privacy/data-integrity decision on score trust and raw responses.

## Top 5 Critical Blockers

1. Public sensitive or non-example artifacts still ship in build/package outputs.
2. CAT is non-functional against the shipped item banks because schema adaptation and reverse handling are missing.
3. The `psyche-web` package is not yet a hardened, deployable contract.
4. The current test suite cannot protect the planned changes.
5. API-side trust controls and durable rate limiting are unresolved and cannot be approved from this repo alone.

## Corrected Phase Sequence

1. Phase 0: remove unsafe shipped artifacts and add build/pack CI gates.
2. Phase 1: add verification for scoring, store persistence, CAT asset loading, CAT traces, and package contracts.
3. Phase 2: correct CAT runtime behavior against the shipped banks.
4. Phase 3: harden `psyche-web` as a real package with an approved committed delivery path.
5. Phase 4: execute `tier-3-nextjs` and `api` rollout from explicit pinned scope.
6. Phase 5: perform optional refactors only if earlier phases are complete and there is still a demonstrated need.

## What Must Be True Before Approval

- The plan must adopt the corrected phase sequence and treat blocker phases as mandatory scope.
- Build and package outputs must no longer ship protected assets or accidental junk, and CI must enforce that rule.
- Verification must expand to cover CAT asset loading, reverse handling, golden traces, `scoreBinary`, store import/export/rehydration, and package/export contracts.
- CAT must be corrected against the shipped banks before any CAT enhancement or internal rewrite proceeds.
- `psyche-web` must be publishable and consumable through an approved committed path; committed `link:` must be removed.
- Cross-repo rollout scope must be explicit for `psyche`, `tier-3-nextjs`, and `api`, with pinned versions or SHAs.
- A written privacy/data-integrity decision must approve the score-trust model and API pre-deploy controls.
- Consumer and API verification must pass from clean-checkout conditions with no unresolved blockers.

## Final Recommendation

Do not approve the remediation plan as currently written.

Approve only after the plan is rewritten around the corrected phase order and the mandatory blocker scope is made explicit. The immediate priorities are clear: remove unsafe shipped artifacts, harden verification, fix CAT against the shipped banks, turn `psyche-web` into a real package contract, and bring the consumer/API rollout into explicit cross-repo scope. Optional refactors should remain deferred until all of that is complete. Any weaker approval would authorize work on lower-value cleanup while leaving correctness, privacy, packaging, and deployment risks unresolved.
