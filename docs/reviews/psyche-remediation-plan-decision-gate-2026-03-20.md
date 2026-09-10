# Decision Gate: Psyche Remediation Plan

Decision status: **FAIL / NOT APPROVED**

This document is the final approval gate for the remediation plan currently represented by [`analysis/BACKLOG.md`](../../analysis/BACKLOG.md). It consolidates the original plan intent, the critical review findings, the required revisions, and the mandatory preconditions that must pass before implementation is approved.

Approval rule: this gate passes only when every mandatory condition in the checklist is checked, every pass criterion has objective evidence, and the cross-repo rollout scope is explicit for `psyche`, `tier-3-nextjs`, and `api`.

Primary source documents:

- [`analysis/BACKLOG.md`](../../analysis/BACKLOG.md)
- [`docs/reviews/psyche-remediation-plan-executive-summary-2026-03-20.md`](./psyche-remediation-plan-executive-summary-2026-03-20.md)
- [`docs/reviews/psyche-remediation-plan-critical-review-2026-03-20.md`](./psyche-remediation-plan-critical-review-2026-03-20.md)
- [`docs/TECHNICAL-ASSESSMENT-2026-03-20.md`](../TECHNICAL-ASSESSMENT-2026-03-20.md)
- [`docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md`](../PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md)

## 1. What The Original Plan Intended To Do

The original deferred remediation plan in [`analysis/BACKLOG.md`](../../analysis/BACKLOG.md) intended to address the following 12 items:

| # | Original plan item | Original framing in plan |
| --- | --- | --- |
| 1 | Extract shared `psyche-web` package | Major refactor to remove duplication |
| 2 | Server-side score re-computation | Architectural/privacy decision |
| 3 | Replace `Map` with `Record` in `SessionState` | Wide-blast-radius cleanup |
| 4 | Refactor `InstrumentRunner` into sub-components | Maintainability/testability improvement |
| 5 | CAT controller immutable state | Major API change for CAT internals |
| 6 | Durable rate limiting (KV/D1) | Infrastructure hardening |
| 7 | CAT item bank schema fix + reverse scoring | Deferred as blocked on real IRT parameters |
| 8 | DRY refactor scoring (`scoreBinary` + `scoreLikert`) | Cleanup of duplicated scoring logic |
| 9 | Dual state management encapsulation | Potential Next.js state cleanup |
| 10 | `thetaToPercentile` precision | Cosmetic precision improvement |
| 11 | CAT content balancing | CAT enhancement |
| 12 | Seed data fetch optimization | Performance tweak |

The implied execution order was the same as the backlog order above.

## 2. What The Critical Review Found

The critical review found that the plan is not execution-safe as written.

| Finding | Review conclusion |
| --- | --- |
| Ordering failure | The backlog order mixes blockers, optional refactors, and cross-repo work that cannot be safely executed in that sequence. |
| CAT failure | CAT is currently non-functional against the shipped JSON banks because the runtime expects different field names and does not apply reverse scoring. |
| Deployment/privacy blocker | Public seed/profile assets are still being shipped in build/package artifacts. |
| Packaging blocker | `psyche-web` is not yet a deployable package contract; committed `link:` is unsafe for CI/Vercel and exports are incomplete. |
| Verification blocker | Current tests do not cover the exact areas the plan wants to change, including CAT asset loading, `scoreBinary`, and package/export contracts. |
| Cross-repo blocker | `tier-3-nextjs` and `api` are not in scope here, so package rollout, durable rate limiting, and server-side score trust cannot be approved from this repo alone. |
| Scope error | Several items were mis-scoped or overstated as low-risk when they are actually blockers, especially CAT correctness, asset hygiene, packaging, and API controls. |

## 3. Specific Revisions Required Before Approval

The plan must be revised as follows before approval:

1. Replace the original backlog ordering with the reviewed phase order:
   Phase 0 deployment hygiene, Phase 1 verification hardening, Phase 2 CAT runtime correction, Phase 3 package hardening, Phase 4 cross-repo integration, Phase 5 optional refactors.
2. Reclassify public asset removal as an immediate deployment/privacy blocker, not a late optimization item.
3. Reclassify CAT schema adaptation and reverse scoring as immediate blocking work, not deferred work.
4. Re-scope shared-package work from "extract package" to "harden a publishable package contract and approved delivery path."
5. Require verification expansion before any DRY scoring refactor or CAT immutable-state rewrite.
6. Move server-side score trust and durable rate limiting into an explicit cross-repo phase with `api` and `tier-3-nextjs` included.
7. Require a written privacy/data-integrity ADR before approving API-side score recomputation or any alternative trust model.
8. Defer optional refactors such as `Map` cleanup, `InstrumentRunner` decomposition, dual-state cleanup, `thetaToPercentile` precision, and CAT content balancing until all prior gate conditions are green.

## 4. Approval Checklist

All items below must be checked for this gate to pass:

- [ ] DG-01 Revised phase order and mandatory scope adopted in the remediation plan.
- [ ] DG-02 Public sensitive/static assets removed from shipped build/package outputs, with CI enforcement.
- [ ] DG-03 Verification expanded to cover CAT asset loading, CAT traces, `scoreBinary`, store import/export/rehydration, and package/export contracts.
- [ ] DG-04 CAT runtime corrected against shipped banks, including schema adaptation/validation and reverse scoring.
- [ ] DG-05 `psyche-web` hardened as a real package with approved committed delivery path; `link:` remains local-only.
- [ ] DG-06 Cross-repo rollout scope and pinned SHAs are explicit for `psyche`, `tier-3-nextjs`, and `api`.
- [ ] DG-07 Privacy/data-integrity ADR approved and API-side trust/rate-limit work accepted as mandatory pre-deploy scope.
- [ ] DG-08 Consumer and API verification complete from clean-checkout conditions, with no unresolved gate blockers.

## 5. Pass/Fail Criteria, Responsibility, And Dates

| Gate ID | Condition | Pass criteria | Fail criteria | Responsible person/team | Target completion date |
| --- | --- | --- | --- | --- | --- |
| DG-01 | Adopt revised phase order and mandatory scope | The remediation document explicitly replaces the backlog item order with the reviewed phase order and marks deployment hygiene, verification hardening, CAT correction, package hardening, and cross-repo API work as mandatory scope. | The plan still uses the original backlog order, or any blocker is still marked as optional/deferred. | Engineering lead + Psyche maintainers | 2026-03-23 |
| DG-02 | Remove shipped sensitive/static assets and add CI gating | `pnpm build` and `npm pack --dry-run` no longer include `seed-data.json`, non-example profile data, `recover.html`, stray test assets, or build junk; CI fails on regression. | Any protected asset or stray recovery/debug artifact is still present in `dist/` or pack output, or CI does not enforce the rule. | Psyche maintainers + Release engineering | 2026-03-25 |
| DG-03 | Expand verification before refactoring | Tests exist and pass for `scoreBinary`, edge-case normalization, store import/export/rehydration, malformed imports, CAT asset-backed loading, CAT golden traces, and package export/pack contents. | Coverage remains limited to current happy paths, or refactor work begins without these tests. | QA/verification owner + Psyche maintainers | 2026-03-27 |
| DG-04 | Correct CAT runtime against shipped banks | Real bank assets load with defined `id`, `text`, and `dimensionId`; reversed CAT items are correctly handled; CAT is disabled from production-heavy flows until the corrected path passes. | Runtime still assumes the wrong bank shape, reverse flags are ignored, or CAT remains enabled without passing asset-backed tests. | Psyche maintainers | 2026-03-28 |
| DG-05 | Harden `psyche-web` package and committed delivery path | Package has final identity, `files` allow-list, required exports such as `./open-ended` if needed, package-contract tests, and uses npm as the committed path with tarball as fallback; committed `link:` is absent. | Package remains `"private": true`, exports are incomplete, pack output is not audited, or committed `link:` remains in the production path. | Psyche maintainers + Release engineering | 2026-03-31 |
| DG-06 | Make cross-repo rollout explicit | The execution plan names the exact repos in scope, pins rollout SHAs/versions, and defines the `tier-3-nextjs` integration and `api` work as explicit tracked phases. | Cross-repo work is still implied, repo SHAs are missing, or rollout assumptions are left to follow-up. | Engineering lead + `tier-3-nextjs` team + API team | 2026-03-31 |
| DG-07 | Approve privacy/data-integrity ADR and API pre-deploy controls | A written ADR defines score trust, raw-response retention/privacy implications, and approved scope; durable rate limiting is accepted as mandatory pre-deploy work. | No ADR exists, API score trust remains undecided, or durable rate limiting is still treated as optional hardening. | Privacy/research owner + API team | 2026-04-02 |
| DG-08 | Complete clean-checkout consumer/API verification | `tier-3-nextjs` builds/tests from a clean checkout with the approved dependency path and `transpilePackages` configuration; API verification exists for durable rate limiting, session cleanup policy, and server-side score handling or approved alternative. | Consumer build depends on local-only paths, API verification is absent, or any critical blocker remains open at rollout review. | `tier-3-nextjs` team + API team + Release engineering | 2026-04-04 |

## 6. Gate Decision

Current decision: **FAIL**

Reason: the reviewed prerequisites are not yet complete, and the original remediation plan cannot be approved for execution in its current form.

This gate changes to **PASS** only when:

1. All eight checklist items are checked.
2. Each item has objective evidence attached.
3. No fail criterion remains true.
4. The approvers confirm that optional refactors remain out of scope until all mandatory phases are green.

## 7. Approval Record

| Role | Name | Decision | Date |
| --- | --- | --- | --- |
| Engineering lead |  |  |  |
| Psyche maintainer |  |  |  |
| `tier-3-nextjs` owner |  |  |  |
| API owner |  |  |  |
| Privacy/research owner |  |  |  |

