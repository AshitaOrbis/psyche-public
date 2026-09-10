# Executive Summary: Psyche Remediation Plan

This summary applies to the remediation plan currently captured in [`analysis/BACKLOG.md`](../../analysis/BACKLOG.md). It should be read together with the detailed critical review: [`docs/reviews/psyche-remediation-plan-critical-review-2026-03-20.md`](./psyche-remediation-plan-critical-review-2026-03-20.md).

## Quick Verdict

Not approved as written. Approve execution only after the original `analysis/BACKLOG.md` item order is replaced with the revised phase order and the blocking deployment, CAT, packaging, verification, and cross-repo issues are made mandatory scope.

## Mandatory Pre-Execution Actions

1. Remove shipped sensitive/public assets and add package/build CI checks so `seed-data`, profile data, and stray recovery/debug artifacts are not published.
2. Fix CAT against the shipped banks by handling the bank schema correctly, applying reverse scoring, and keeping CAT out of production-heavy flows until asset-backed tests pass.
3. Harden `psyche-web` as a real deliverable package: final package identity, `files` allow-list, required exports such as `./open-ended` if needed, and npm as the committed CI/Vercel-safe path; keep `link:` local-only.
4. Expand verification before refactoring: add coverage for `scoreBinary`, store import/export/rehydration, CAT bank loading, CAT golden traces, and package export/pack contents.
5. Move API trust/rate-limit work into an explicit cross-repo phase with `api` and `tier-3-nextjs` in scope, a written privacy/data-integrity decision, and durable rate limiting as a pre-deploy requirement.

## Correct Phase Order

1. Phase 0: Deployment hygiene
2. Phase 1: Verification hardening
3. Phase 2: CAT runtime correction
4. Phase 3: Package hardening
5. Phase 4: Cross-repo integration
6. Phase 5: Optional refactors only after all prior phases are green

This replaces the original deferred-item sequence in [`analysis/BACKLOG.md`](../../analysis/BACKLOG.md), which is not execution-safe.

## Implementation-Mode Gate

Do not enter implementation mode until the revised phase order is adopted, all five pre-execution actions are accepted as mandatory scope, committed `link:` is removed from the production path, CAT schema/reverse handling is treated as an immediate blocker, and the `psyche`, `tier-3-nextjs`, and `api` rollout scope and verification gates are explicit.

## Supporting Documents

- [`docs/reviews/psyche-remediation-plan-critical-review-2026-03-20.md`](./psyche-remediation-plan-critical-review-2026-03-20.md)
- [`docs/TECHNICAL-ASSESSMENT-2026-03-20.md`](../TECHNICAL-ASSESSMENT-2026-03-20.md)
- [`docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md`](../PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md)
