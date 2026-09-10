# Supporting Documents Summary

Date: 2026-03-20

Scope:
- Human-readable supporting documents created during this review.
- Excludes machine-state files, raw JSON outputs, logs, and scripts.

| Stack | Document | File path | Purpose |
| --- | --- | --- | --- |
| Remediation review | Review and Assessment Index | `docs/reviews/README.md` | Master index for the review package, reading order, and document relationships across the remediation, experiment, benchmark, and profile stacks. |
| Remediation review | Final Assessment | `docs/reviews/psyche-remediation-plan-final-assessment-2026-03-20.md` | Canonical single-document review artifact consolidating verdict, critical questions, blockers, corrected phase order, acceptance/deferral decisions, verification checklist, and final recommendation. |
| Remediation review | Technical Assessment | `docs/TECHNICAL-ASSESSMENT-2026-03-20.md` | Evidence-heavy technical deep-dive covering CAT schema risk, scoring refactor risk, package-linking complexity, CAT immutable-state complexity, and execution dependencies. |
| Remediation review | Delivery Matrix | `docs/PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md` | Decision memo comparing `link:`, published package, and vendored tarball delivery paths for `psyche-web` consumption in `tier-3-nextjs`. |
| Remediation review | Critical Review | `docs/reviews/psyche-remediation-plan-critical-review-2026-03-20.md` | Core review of the remediation plan, including blockers, dependency/order failures, revised phase sequencing, and verification requirements. |
| Remediation review | Executive Summary | `docs/reviews/psyche-remediation-plan-executive-summary-2026-03-20.md` | Short verdict with mandatory pre-execution actions, corrected phase order, and the implementation gate. |
| Remediation review | Decision Gate | `docs/reviews/psyche-remediation-plan-decision-gate-2026-03-20.md` | Formal pass/fail approval artifact with checklist conditions, pass criteria, and approval record. |
| Remediation review | Deferred Item Summary | `docs/reviews/psyche-remediation-plan-deferred-item-summary-2026-03-20.md` | One-page mapping from the 12 original deferred backlog items to reviewed disposition, rationale, and target phase. |
| Remediation review | Final Executive Brief | `docs/reviews/psyche-remediation-plan-final-executive-brief-2026-03-20.md` | Ultra-short stakeholder brief answering the final approval questions in Q&A form. |
| Review inputs | Synthesized Findings | `docs/reviews/iteration-1/synthesized-findings.md` | Deduplicated synthesis of the three model reviews into one ranked findings list with deferred architecture items and false positives. |
| Review inputs | GPT-5.4 Review | `docs/reviews/iteration-1/gpt54-review.md` | Individual source review emphasizing public-asset exposure, privacy/security failures, CAT schema mismatch, and deployment-surface risks. |
| Review inputs | Gemini Review | `docs/reviews/iteration-1/gemini-review.md` | Individual source review emphasizing architecture, duplication, accessibility, API client quality, and state-management issues. |
| Review inputs | Opus Review | `docs/reviews/iteration-1/opus-review.md` | Individual source review emphasizing cross-file drift, scoring edge cases, latent CAT issues, and type-contract problems. |
| Review inputs | Code Digest | `docs/reviews/iteration-1/code-digest.txt` | Raw code/input packet assembled for the model reviews; useful for tracing the exact review context rather than conclusions. |
| Research support | 1M Context Narrative Experiment Results | `experiments/1m-context-narrative/results_report.md` | Original ablation report for the 1M-context narrative experiment, including research questions, conditions, score tables, and interpretation. |
| Research support | Critical Review of the 1M Context Experiment | `experiments/1m-context-narrative/critical_review_opus.md` | Skeptical methodological review challenging causal claims, confounds, and overstated interpretation in the 1M-context report. |
| Research support | Methodology Supplement | `experiments/methodology-supplement/results-report.md` | Follow-up validation report adding cross-model checks, per-domain analysis, and additional evaluation work prompted by review feedback. |
| Research support | Corpus Sample for GPT | `experiments/methodology-supplement/corpus-sample-for-gpt.txt` | Raw supporting input artifact used for the cross-model/methodology follow-up work. |
