# Deferred Item Summary: Psyche Remediation Plan

One-page mapping of the 12 original deferred items from [`analysis/BACKLOG.md`](../../analysis/BACKLOG.md) to their reviewed disposition under the revised phase order. `Properly addressed?` mirrors the judgment in [`psyche-remediation-plan-critical-review-2026-03-20.md`](./psyche-remediation-plan-critical-review-2026-03-20.md). `Target phase` follows the revised sequence in [`psyche-remediation-plan-executive-summary-2026-03-20.md`](./psyche-remediation-plan-executive-summary-2026-03-20.md) and [`psyche-remediation-plan-decision-gate-2026-03-20.md`](./psyche-remediation-plan-decision-gate-2026-03-20.md).

| # | Original deferred item | Current status in plan | Properly addressed? | Risk level | Recommended action | Key blocker if any | Target phase |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Extract shared `psyche-web` package | Re-scoped as mandatory package hardening and delivery-contract work, not a blind refactor | No | High | Implement now | Package is still not publishable/deploy-safe: incomplete exports, no `files` allow-list, committed `link:` unsafe | Phase 3/4 |
| 2 | Server-side score re-computation | Moved into explicit cross-repo/API scope pending privacy and trust decisions | No | High | Defer | `api` repo is not in scope and no privacy/data-integrity ADR is approved | Phase 4 |
| 3 | Replace `Map` with `Record` in `SessionState` | Deferred as consumer-repo cleanup, not a core remediation item here | Partial | Medium | Defer | Remaining issue lives in `tier-3-nextjs`; serialization tests are absent there | Deferred |
| 4 | Refactor `InstrumentRunner` into sub-components | Deferred as lower-priority maintainability work | Partial | Low | Defer | Consumer repo is not present and correctness/accessibility work ranks ahead of decomposition | Deferred |
| 5 | CAT controller immutable state | Deferred to optional refactor scope after CAT correctness is stable | No | Medium | Defer | CAT loader/schema correctness and trace coverage must land first | Phase 5 |
| 6 | Durable rate limiting (KV/D1) | Reclassified as mandatory pre-deploy API control, not optional hardening | No | High | Implement now | `api` repo is out of scope and no durable backing store rollout is defined | Phase 4 |
| 7 | CAT item bank schema fix + reverse scoring | Reclassified as immediate blocking CAT work | No | High | Implement now | Shipped bank schema does not match runtime expectations and reverse flags are ignored | Phase 2 |
| 8 | DRY refactor scoring (`scoreBinary` + `scoreLikert`) | Deferred until verification hardening is complete | Partial | Medium | Defer | Current tests do not cover `scoreBinary`, edge cases, or contract drift | Phase 5 |
| 9 | Dual state management encapsulation | Deferred as consumer-specific cleanup outside this repo's blocking scope | Partial | Medium | Defer | Actual dual-state issue is in `tier-3-nextjs`, which is not available here | Deferred |
| 10 | `thetaToPercentile` precision | Deferred as-is; remains cosmetic | Yes | Low | Accept as-is | None | Deferred |
| 11 | CAT content balancing | Deferred as a legitimate enhancement after CAT is functional | Yes, with caveat | Low | Defer | CAT must be corrected and validated before balancing work has value | Deferred |
| 12 | Seed data fetch optimization | Original item rejected as framed; replaced by immediate asset-removal/privacy work | No | High | Implement now | Real blocker is shipped public seed/profile/recovery artifacts, not fetch overhead | Phase 0 |
