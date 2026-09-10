# Final Executive Brief: Psyche Remediation Plan

1. Is the original plan approvable as-written?  
No.

2. What is the single most dangerous assumption in the plan?  
That execution can start from the original backlog order while critical blockers are still treated as optional, deferred, or implied cross-repo follow-up. That is backwards. It would spend time on refactors while leaving broken CAT behavior, unsafe shipped assets, undeployable package delivery, and unresolved API trust/rate-limit controls in place.

3. What must change before approval?  
Replace the backlog order with the reviewed phase order. Make deployment hygiene, verification hardening, CAT runtime correction, package hardening, and cross-repo API work mandatory scope. Remove committed `link:` from the production path. Treat CAT schema/reverse handling as an immediate blocker. Make `psyche`, `tier-3-nextjs`, and `api` rollout scope explicit. Require a written privacy/data-integrity ADR before approving server-side score recomputation.

4. What is the lowest-risk way forward?  
Do the minimum necessary to make the system safe before touching optional refactors: remove shipped sensitive assets, add CI/package gates, expand tests, fix CAT against the shipped banks, harden `psyche-web` as a real package with an approved delivery path, then execute the consumer/API rollout with pinned versions and clean-checkout verification.

5. What is the approval gate?  
Approval is blocked until all eight decision-gate conditions pass with objective evidence: revised phase order adopted, shipped assets removed with CI enforcement, verification expanded, CAT corrected, package hardened, cross-repo rollout explicit, privacy/data-integrity ADR approved, and clean-checkout consumer/API verification complete.
