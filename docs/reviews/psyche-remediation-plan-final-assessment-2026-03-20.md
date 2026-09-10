# Final Assessment: Psyche Remediation Plan

**Verdict: Not approved as written. Approve only after the plan is re-scoped around deployment hygiene, verification hardening, CAT runtime correction, package hardening, and explicit cross-repo consumer/API validation.**

This document is the single authoritative review artifact for the remediation plan currently represented in [`analysis/BACKLOG.md`](../../analysis/BACKLOG.md). It consolidates the conclusions from the executive summary, critical review, deferred-item mapping, technical assessment, delivery matrix, and decision gate into one approval document.

## Table of Contents

1. Review Basis
2. Critical Review Question 1: Is the original plan approvable as written?
3. Critical Review Question 2: Which backlog items are mis-scoped, unmapped, or inadequately addressed?
4. Critical Review Question 3: Is the proposed execution order safe, and what is the corrected phase sequence?
5. Critical Review Question 4: Which items are being understated or incorrectly treated as low-risk?
6. Critical Review Question 5: What verification gaps make implementation unsafe today?
7. Critical Review Question 6: What is the lowest-risk implementation strategy, and which approaches should be avoided?
8. Critical Review Question 7: What CI, deployment, and cross-repo gates must pass before implementation?
9. Top 5 Blockers
10. Corrected Phase Sequence
11. Acceptance And Deferral Decisions
12. Verification Checklist Before Implementation
13. Final Recommendation

## Review Basis

This assessment is based on the following primary evidence set:

- The source remediation backlog in [`analysis/BACKLOG.md`](../../analysis/BACKLOG.md)
- The code-level dependency and risk review in [`docs/TECHNICAL-ASSESSMENT-2026-03-20.md`](../TECHNICAL-ASSESSMENT-2026-03-20.md)
- The package delivery decision memo in [`docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md`](../PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md)
- The plan-level critique in [`docs/reviews/psyche-remediation-plan-critical-review-2026-03-20.md`](./psyche-remediation-plan-critical-review-2026-03-20.md)
- The original approval gate in [`docs/reviews/psyche-remediation-plan-decision-gate-2026-03-20.md`](./psyche-remediation-plan-decision-gate-2026-03-20.md)
- The backlog-item remapping in [`docs/reviews/psyche-remediation-plan-deferred-item-summary-2026-03-20.md`](./psyche-remediation-plan-deferred-item-summary-2026-03-20.md)
- The upstream review synthesis and source reviews in [`docs/reviews/iteration-1/synthesized-findings.md`](./iteration-1/synthesized-findings.md), [`docs/reviews/iteration-1/gpt54-review.md`](./iteration-1/gpt54-review.md), [`docs/reviews/iteration-1/gemini-review.md`](./iteration-1/gemini-review.md), and [`docs/reviews/iteration-1/opus-review.md`](./iteration-1/opus-review.md)

Scope limits that materially affect this decision:

- The `tier-3-nextjs` repo is not present in this workspace.
- The `api` repo is not present in this workspace.
- Any approval that depends on consumer integration, API trust controls, or durable rate limiting cannot be fully granted from this repo alone.

## Critical Review Question 1: Is the original plan approvable as written?

**Answer: No.**

The original plan is not execution-safe as written because it starts from the wrong assumptions and the wrong order. The backlog in [`analysis/BACKLOG.md`](../../analysis/BACKLOG.md) mixes immediate blockers, optional refactors, and cross-repo work that is not verifiable in this workspace. That causes the plan to prioritize maintainability and cleanup work ahead of correctness, deployment safety, and release gating.

The decisive problems are:

- CAT is currently non-functional against the shipped JSON banks because the runtime expects a different schema and does not apply reverse scoring.
- Static/public artifacts that should not ship are still being emitted in build and package outputs.
- `psyche-web` is not yet a deployable shared-package contract, and the currently discussed `link:` path is explicitly unsafe as a committed CI/Vercel solution.
- The current test surface does not cover the exact areas the plan proposes to change.
- The consumer-repo and API-repo portions of the plan are still implied follow-up rather than explicit in-scope rollout phases.

The result is straightforward: approving the original plan would authorize work on lower-value refactors while leaving broken CAT behavior, unsafe deployment artifacts, incomplete package contracts, and unresolved API trust/rate-limit controls in place.

## Critical Review Question 2: Which backlog items are mis-scoped, unmapped, or inadequately addressed?

**Answer: Several of the 12 deferred items are framed in the wrong problem class.**

The main scoping errors fall into four groups.

### A. Items framed as optional cleanup that are actually immediate blockers

- `CAT item bank schema fix + reverse scoring`
  This is not blocked on real IRT parameters. The shipped bank format does not match runtime expectations, and reverse flags exist but are ignored in CAT execution.
- `Seed data fetch optimization`
  This is not a performance tweak. The real issue is that seed/profile/recovery artifacts are still being shipped publicly.
- `Durable rate limiting (KV/D1)`
  This is not optional infrastructure polish if public report generation remains in scope. The current in-memory Worker `Map` is not durable enough to enforce real limits.
- `Extract shared psyche-web package`
  This is not simply a refactor to remove duplication. It is package hardening, export-surface definition, artifact auditing, and committed delivery-path selection.
- `Server-side score re-computation`
  This is not a loose architecture idea. It is a data-integrity and privacy-contract decision that becomes material if downstream reporting trusts client-submitted scores.

### B. Items mis-scoped to this repo when the remaining work is actually in another repo

- `Replace Map with Record in SessionState`
  The standalone store already uses `Record`. The remaining concern is in `tier-3-nextjs`, which is not present here.
- `Dual state management encapsulation`
  The real dual-state issue also lives in `tier-3-nextjs`, not in this repo's current standalone state model.
- `Refactor InstrumentRunner into sub-components`
  This is consumer-specific maintainability work and should not be treated as core remediation work in this repository.

### C. Items that are real but sequenced too early

- `CAT controller immutable state`
  This should not start until the CAT loader, runtime schema handling, reverse scoring, and golden-trace tests are stable.
- `DRY refactor scoring (scoreBinary + scoreLikert)`
  This is reasonable only after verification hardening lands, because the current test surface cannot safely protect that refactor.

### D. Items that are correctly deferred

- `thetaToPercentile precision`
  Cosmetic and safe to defer.
- `CAT content balancing`
  Legitimate enhancement, but only after CAT is functional.

The practical consequence is that the backlog cannot be executed as a flat list. It must be reclassified into blockers, mandatory rollout phases, and true deferrals.

## Critical Review Question 3: Is the proposed execution order safe, and what is the corrected phase sequence?

**Answer: No. The original backlog order is not safe for execution.**

The original implied order starts with shared-package extraction and several refactors before it addresses deployment hygiene, verification expansion, and CAT correctness. That ordering fails the dependency graph.

The critical dependency corrections are:

- Deployment hygiene must precede any deploy, package publish, or consumer rollout.
- Verification hardening must precede CAT correction, scoring refactors, and CAT internal rewrites.
- CAT schema adaptation and reverse handling must precede any CAT-specific enhancement or internal rewrite.
- Package hardening must precede `tier-3-nextjs` consumption.
- API trust and durable rate limiting must be handled in an explicit cross-repo phase, not as local cleanup in this repo.

The corrected execution sequence is:

1. Phase 0: Deployment hygiene
2. Phase 1: Verification hardening
3. Phase 2: CAT runtime correction
4. Phase 3: Package hardening
5. Phase 4: Cross-repo integration
6. Phase 5: Optional refactors only after all earlier phases are green

This phase order is not cosmetic. It is the minimum sequence that aligns the work with actual risk and dependency boundaries.

## Critical Review Question 4: Which items are being understated or incorrectly treated as low-risk?

**Answer: The plan materially understates several high-risk items.**

The most serious understatements are:

1. `CAT item bank schema fix + reverse scoring`
   This is not an experimental quality issue. It is a current functional correctness failure on the shipped CAT path.
2. `Durable rate limiting`
   This is not optional hardening. An in-memory Worker `Map` does not provide reliable protection under cold starts, isolate churn, or multi-instance execution.
3. `Seed data fetch optimization`
   This is not about an extra request. It is about public shipping of sensitive/static assets that should not be exposed.
4. `Extract shared psyche-web package`
   This is not low-risk duplication cleanup. It changes the release contract, package surface, CI behavior, and consumer integration path.
5. `Server-side score re-computation`
   This is not merely architectural taste. If downstream reporting or research trusts client-submitted scores, this becomes a trust-boundary decision.

The core pattern is that several items were minimized because they were framed as refactors or enhancements. They are actually release blockers, trust-boundary decisions, or deployment-surface risks.

## Critical Review Question 5: What verification gaps make implementation unsafe today?

**Answer: The current verification surface is too narrow to protect the planned changes.**

The passing suite is materially smaller than the risk surface it is expected to protect. It does not cover several critical execution paths and artifact contracts.

The highest-value missing verification areas are:

| Area | What is missing | Why it matters |
| --- | --- | --- |
| Deployment/package artifact audits | No automated assertion on `dist/` contents or `npm pack --dry-run` contents | Unsafe assets and junk files can still ship unnoticed |
| Store import/export/rehydration | No robust coverage for malformed payloads, duplicates, rehydration behavior, or import/export edge cases | State corruption and persistence regressions would not be caught |
| `scoreBinary()` and scoring edge cases | No meaningful coverage for malformed values, zero-valid-response cases, or normalization edge conditions | A scoring refactor would be effectively unguarded |
| CAT bank loading from real shipped assets | No test loads the actual JSON bank artifacts used at runtime | Schema drift between code and assets remains invisible |
| CAT reverse behavior | No test proves reversed CAT items are inverted correctly before estimation | CAT trait estimates can be wrong even if loading succeeds |
| CAT golden traces | No stable item-selection/response-trace assertions against the corrected runtime | CAT controller changes could silently alter behavior |
| Package export and install contract | No tests for export surface, pack contents, or clean consumer installation | Shared-package rollout can break after publish or in CI |
| Consumer/API integration verification | No local evidence for `tier-3-nextjs` integration, durable rate limiting, or server-side trust controls | Cross-repo approvals remain speculative |

Until those gaps are closed, the current suite gives a false sense of safety. It confirms only that the existing happy paths still pass, not that the remediation work is protected.

## Critical Review Question 6: What is the lowest-risk implementation strategy, and which approaches should be avoided?

**Answer: Use the smallest path that makes the system safe first, and explicitly avoid large speculative refactors.**

The lowest-risk path is:

1. Remove unsafe shipped assets and add artifact/pack gating.
2. Expand verification around the real risk areas.
3. Correct CAT against the shipped banks with schema adaptation, validation, and reverse handling.
4. Harden `psyche-web` as a real package with an approved committed delivery path.
5. Execute the consumer/API rollout only after the cross-repo scope is explicit and verifiable.
6. Leave cleanup refactors for the end unless a concrete bug forces them earlier.

Approaches that should be explicitly avoided at this stage:

- Do not use committed `link:` as the production delivery path.
- Do not start with a full immutable CAT rewrite.
- Do not genericize scoring before the current scoring behavior is fully protected by tests.
- Do not spend time on `Map` to `Record` cleanup in this repo as if it were a blocker.
- Do not treat public-asset exposure as "seed fetch optimization."
- Do not prioritize `InstrumentRunner` decomposition ahead of correctness and release-surface fixes.

The review conclusion is not "do less." It is "do the mandatory safety work before the optional design work."

## Critical Review Question 7: What CI, deployment, and cross-repo gates must pass before implementation?

**Answer: Implementation should not be approved until the mandatory gate conditions are explicit and evidenced.**

The required gate conditions are:

| Gate | Required condition |
| --- | --- |
| DG-01 | The remediation plan adopts the revised phase order and marks blocker phases as mandatory scope |
| DG-02 | Build/package outputs no longer ship protected assets or stray recovery/debug/test artifacts, and CI enforces that rule |
| DG-03 | Verification expands to cover CAT asset loading, CAT traces, `scoreBinary`, store import/export/rehydration, and package/export contracts |
| DG-04 | CAT is corrected against the shipped banks, including schema adaptation/validation and reverse handling |
| DG-05 | `psyche-web` is hardened as a real package with an approved committed delivery mechanism; `link:` is local-only |
| DG-06 | Cross-repo rollout scope is explicit for `psyche`, `tier-3-nextjs`, and `api`, with pinned versions or SHAs |
| DG-07 | A privacy/data-integrity ADR is approved and API trust/rate-limit controls are accepted as mandatory pre-deploy work |
| DG-08 | Consumer and API verification complete from clean-checkout conditions with no unresolved blocker remaining |

If any of these conditions remain open, approval should remain blocked. The missing `tier-3-nextjs` and `api` repos are not a documentation gap. They are a real decision constraint.

## Top 5 Blockers

| Priority | Blocker | Why it blocks approval | Required mitigation |
| --- | --- | --- | --- |
| 1 | Public sensitive/static assets still ship | A deployment can still publish seed/profile/recovery artifacts that should not be exposed | Remove them from shipped assets, keep only non-shipping examples, add `files` allow-list and CI artifact checks |
| 2 | CAT is non-functional with the shipped banks | Runtime shape mismatch and ignored reverse flags make the current CAT path unsafe | Add schema adaptation or normalize assets, validate at load time, implement reverse handling, and verify with asset-backed tests |
| 3 | The shared-package rollout is not deployable as written | The package is not yet a hardened, publishable contract and committed `link:` is unsafe | Finalize package identity, export surface, pack allow-list, and approved committed delivery path |
| 4 | The test suite cannot protect the planned refactors | The planned code changes are not covered where failures are most likely | Expand verification before any DRY scoring or CAT-internal refactor begins |
| 5 | API-side trust and durable rate-limit controls are unresolved and out of scope here | Approval depends on behavior that cannot be proven from this repo alone | Bring the `api` and consumer repos into scope, approve the ADR, and implement durable controls before rollout |

## Corrected Phase Sequence

| Phase | Objective | Must be true before exiting the phase |
| --- | --- | --- |
| Phase 0: Deployment hygiene | Remove unsafe shipped artifacts and tighten package/build outputs | `pnpm build` and `npm pack --dry-run` are clean, and CI enforces the allowed artifact set |
| Phase 1: Verification hardening | Add the tests and artifact checks needed to safely change the system | Risk-bearing paths are covered: scoring, store import/export, CAT asset loading, CAT traces, package exports, pack contents |
| Phase 2: CAT runtime correction | Make CAT function correctly with the shipped banks | Real bank assets load correctly, reverse scoring is applied, and CAT remains out of heavy production use until this is green |
| Phase 3: Package hardening | Turn `psyche-web` into a real release contract | Package identity, exports, allow-list, versioning, and approved committed delivery path are all finalized |
| Phase 4: Cross-repo integration | Validate the consumer and API rollout in the actual dependent repos | `tier-3-nextjs` and `api` integration passes from clean checkout with pinned versions and explicit rollout scope |
| Phase 5: Optional refactors | Execute only the non-blocking maintainability work that still matters after rollout safety is established | All prior phases are green and there is still a demonstrated reason to do the refactor |

The important correction is not only the phase order. It is the rule that no optional refactor begins before the blocker phases are complete.

## Acceptance And Deferral Decisions

| Original backlog item | Decision | Rationale | Target phase |
| --- | --- | --- | --- |
| Extract shared `psyche-web` package | Accept only with mandatory re-scope | This must be package hardening and delivery-contract work, not a blind refactor | Phase 3 and Phase 4 |
| Server-side score re-computation | Defer pending ADR and API-repo review | High importance, but not safely executable or approvable from this repo alone | Phase 4 |
| Replace `Map` with `Record` in `SessionState` | Defer | Mis-scoped here; the remaining issue is consumer-side | Deferred |
| Refactor `InstrumentRunner` into sub-components | Defer | Maintainability-only and lower priority than correctness/release work | Deferred |
| CAT controller immutable state | Defer | Wrong order until CAT correctness and trace stability are proven | Phase 5 |
| Durable rate limiting (KV/D1) | Accept as mandatory pre-deploy API work | Cannot remain optional if public report/API use continues | Phase 4 |
| CAT item bank schema fix + reverse scoring | Accept as immediate blocking work | This is a current correctness failure, not a future enhancement | Phase 2 |
| DRY refactor scoring (`scoreBinary` + `scoreLikert`) | Defer until verification hardening is complete | Unsafe under current coverage | Phase 5 |
| Dual state management encapsulation | Defer | Consumer-specific and not verifiable here | Deferred |
| `thetaToPercentile` precision | Defer as-is | Cosmetic only | Deferred |
| CAT content balancing | Defer as-is | Valid enhancement, but only after CAT is functional | Deferred |
| Seed data fetch optimization | Reject as framed and replace with asset-removal/privacy work | The real blocker is shipped public artifacts, not request count | Phase 0 |

## Verification Checklist Before Implementation

Implementation should not begin until the following checklist is green or explicitly incorporated into the first approved phase with ownership and evidence expectations:

- [ ] The remediation plan document has been rewritten to use the corrected phase sequence rather than the original backlog order.
- [ ] `pnpm build` does not emit `seed-data`, non-example profile data, or stray recovery/debug assets unless those artifacts are explicitly approved and documented.
- [ ] `npm pack --dry-run` produces a hardened package with no protected assets, no `tests/*`, no `tsconfig.tsbuildinfo`, and no accidental build junk.
- [ ] CI enforces artifact-hygiene and pack-hygiene checks so the deployment/package surface cannot silently regress.
- [ ] Tests exist for `scoreBinary`, edge-case normalization, zero-valid-response handling, and malformed inputs.
- [ ] Tests exist for store import/export/rehydration, malformed payloads, duplicate response handling, and persistence edge cases.
- [ ] At least one test loads the real shipped CAT JSON bank asset and proves the loaded runtime items have defined `id`, `text`, and `dimensionId`.
- [ ] Tests prove reversed CAT items are handled correctly before trait estimation.
- [ ] CAT golden-trace tests exist so future controller changes can be compared against stable expected behavior.
- [ ] Package export tests prove all required public entrypoints resolve correctly for consumer usage.
- [ ] Clean-checkout consumer verification exists for the approved package delivery path, with no committed relative `link:` dependency.
- [ ] Cross-repo rollout scope is explicit for `psyche`, `tier-3-nextjs`, and `api`, with pinned versions or SHAs.
- [ ] A written privacy/data-integrity ADR has been approved for server-side score trust and raw-response handling.
- [ ] API-side verification exists for durable rate limiting, session cleanup, and the approved score-trust model.

## Final Recommendation

**Decision status: FAIL / NOT APPROVED**

The remediation plan should not be approved in its current form.

Approval should be granted only if all of the following become true:

1. The original flat backlog order is replaced by the corrected mandatory phase sequence.
2. Public-asset removal, verification hardening, CAT runtime correction, package hardening, and cross-repo API/consumer rollout are treated as mandatory scope rather than optional follow-up.
3. `link:` is removed as a committed production delivery path and replaced by an approved CI-safe package strategy.
4. CAT schema adaptation and reverse handling are treated as immediate blocking correctness work.
5. The `tier-3-nextjs` and `api` repos are brought into explicit rollout scope with pinned versions, clean-checkout verification, and approved trust/privacy decisions.
6. Optional refactors remain deferred until all blocker phases are green.

The lowest-risk forward path is clear: fix what is unsafe to ship, prove the behavior with the right tests, harden the package contract, then execute the cross-repo rollout. Everything else is secondary.
