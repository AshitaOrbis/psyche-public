# Review and Assessment Index

This is the master index for the review and assessment documents currently present in the repo. It is organized by stack so you can distinguish final decision docs from technical deep-dives, source reviews, research assessments, and benchmark outputs.

Scope note:
- This index focuses on curated review and assessment documents plus a small number of direct support artifacts.
- It does not try to index every JSON/log/script file that feeds those documents.
- The remediation-plan review stack is the primary reading path. The experiment, benchmark, and profile sections are separate stacks.

## How The Stacks Fit Together

The remediation review documents form a layered chain:

1. Source reviews
2. Synthesized findings
3. Technical/package assessments
4. Plan-level critical review
5. Executive summary, deferred-item mapping, and formal decision gate
6. Final consolidated assessment

The experiment, benchmark, and profile documents are separate assessment/reporting tracks. They are useful context, but they are not required to understand or approve the remediation plan.

## Recommended Reading Orders

### 5-minute verdict

1. [Final Assessment](./psyche-remediation-plan-final-assessment-2026-03-20.md)
2. [Definitive Summary](./psyche-remediation-plan-definitive-summary-2026-03-20.md)
3. [Decision Gate](./psyche-remediation-plan-decision-gate-2026-03-20.md)
4. [Critical Review](./psyche-remediation-plan-critical-review-2026-03-20.md)

### Remediation implementation read

1. [Final Assessment](./psyche-remediation-plan-final-assessment-2026-03-20.md)
2. [Critical Review](./psyche-remediation-plan-critical-review-2026-03-20.md)
3. [Deferred Item Summary](./psyche-remediation-plan-deferred-item-summary-2026-03-20.md)
4. [Technical Assessment](../TECHNICAL-ASSESSMENT-2026-03-20.md)
5. [Delivery Matrix](../PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md)
6. [Decision Gate](./psyche-remediation-plan-decision-gate-2026-03-20.md)

### Full audit trail

1. [Synthesized Findings](./iteration-1/synthesized-findings.md)
2. [GPT-5.4 Review](./iteration-1/gpt54-review.md)
3. [Gemini Review](./iteration-1/gemini-review.md)
4. [Opus Review](./iteration-1/opus-review.md)
5. [Code Digest](./iteration-1/code-digest.txt)
6. [Technical Assessment](../TECHNICAL-ASSESSMENT-2026-03-20.md)
7. [Delivery Matrix](../PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md)
8. [Critical Review](./psyche-remediation-plan-critical-review-2026-03-20.md)
9. [Executive Summary](./psyche-remediation-plan-executive-summary-2026-03-20.md)
10. [Decision Gate](./psyche-remediation-plan-decision-gate-2026-03-20.md)
11. [Final Assessment](./psyche-remediation-plan-final-assessment-2026-03-20.md)

## Primary Stack: Remediation Review Package

These are the documents to read if you are evaluating the remediation plan in `analysis/BACKLOG.md`. The final assessment is the canonical single-document review artifact. The other documents remain useful as supporting analysis and audit trail.

| Order | Document | Role | Purpose | When to use it |
| --- | --- | --- | --- | --- |
| 1 | [Final Assessment](./psyche-remediation-plan-final-assessment-2026-03-20.md) | Canonical review artifact | Single comprehensive decision document with verdict, seven critical review questions, blockers, corrected phase order, acceptance/deferral decisions, verification checklist, and final recommendation. | Start here for the authoritative review. |
| 2 | [Definitive Summary](./psyche-remediation-plan-definitive-summary-2026-03-20.md) | Plan-ready summary | 1500-2000 word insert-ready summary that answers the seven review questions and ends with blockers, corrected phases, approval conditions, and recommendation. | Use when rewriting the plan or pasting a decisive summary into the backlog. |
| 3 | [Executive Summary](./psyche-remediation-plan-executive-summary-2026-03-20.md) | Summary | Short verdict, mandatory pre-execution actions, corrected phase order, and implementation gate. | Use when you need the compressed version. |
| 4 | [Critical Review](./psyche-remediation-plan-critical-review-2026-03-20.md) | Core review | Full argument for why the backlog is not execution-safe as written, including blockers, revised execution plan, and verification requirements. | Read when you need the full reasoning behind the final assessment. |
| 5 | [Deferred Item Summary](./psyche-remediation-plan-deferred-item-summary-2026-03-20.md) | Mapping sheet | One-page mapping from the 12 original deferred items to their reviewed disposition and target phase. | Use when planning or rewriting the backlog. |
| 6 | [Technical Assessment](../TECHNICAL-ASSESSMENT-2026-03-20.md) | Technical deep-dive | Evidence-heavy analysis of CAT schema risk, scoring refactor risk, package-linking complexity, CAT immutable-state complexity, and phase dependencies. | Use when you need code-level proof or implementation detail. |
| 7 | [Delivery Matrix](../PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md) | Deployment/package decision memo | Compares `link:`, published package, and vendored tarball delivery paths for `psyche-web`, with rollout guidance. | Use when deciding how `tier-3-nextjs` should consume `psyche-web`. |
| 8 | [Decision Gate](./psyche-remediation-plan-decision-gate-2026-03-20.md) | Formal approval gate | Consolidated pass/fail decision, approval checklist, pass criteria, and approval record. | Use when you need the original gate format and sign-off table. |

## Supporting Stack: Iteration 1 Review Inputs

These are the upstream review documents that fed the remediation package. Read them when you need to trace a finding back to a specific reviewer or review style.

| Order | Document | Role | Purpose | What it is best at |
| --- | --- | --- | --- | --- |
| 1 | [Synthesized Findings](./iteration-1/synthesized-findings.md) | Deduplicated synthesis | Consolidates the three model reviews into one ranked finding list with deferred architecture items and false positives. | Best starting point for source-review evidence. |
| 2 | [GPT-5.4 Review](./iteration-1/gpt54-review.md) | Individual review | Strongest on public-asset exposure, security/privacy, CAT schema mismatch, and deployment-surface problems. | Read for concrete high-severity findings and shipped-asset issues. |
| 3 | [Gemini Review](./iteration-1/gemini-review.md) | Individual review | Strongest on architecture, duplication, accessibility, API client quality, and state-management concerns. | Read for system-shape and frontend/API contract problems. |
| 4 | [Opus Review](./iteration-1/opus-review.md) | Individual review | Strongest on cross-file drift, scoring edge cases, and latent CAT/type-contract issues. | Read for correctness and consistency edge cases. |
| 5 | [Code Digest](./iteration-1/code-digest.txt) | Support artifact | Raw code digest used to feed the review models. This is not a conclusion document. | Read only if you need to inspect the exact review input packet. |

## Related Stack: Research Experiment Assessments

These documents belong to the narrative/context-window research track, not the remediation-plan decision path.

Recommended order:

1. [1M Context Narrative Experiment Results](../../experiments/1m-context-narrative/results_report.md)
2. [Critical Review Of The 1M Context Experiment](../../experiments/1m-context-narrative/critical_review_opus.md)
3. [Methodology Supplement](../../experiments/methodology-supplement/results-report.md)

| Document | Role | Purpose | When to read it |
| --- | --- | --- | --- |
| [1M Context Narrative Experiment Results](../../experiments/1m-context-narrative/results_report.md) | Primary results report | Records the ablation design, score tables, and interpretation for the 1M-context narrative experiment. | Start here for the original claim and results. |
| [Critical Review Of The 1M Context Experiment](../../experiments/1m-context-narrative/critical_review_opus.md) | Skeptical methodological review | Challenges the causal claims, identifies confounds, and separates prose-quality improvement from measurement claims. | Read second to stress-test the original interpretation. |
| [Methodology Supplement](../../experiments/methodology-supplement/results-report.md) | Follow-up validation report | Adds cross-model validation, per-domain deltas, and confidence-interval work prompted by review feedback. | Read last for the corrected/qualified methodological picture. |

## Related Stack: Benchmark And Safety Evaluation Reports

These documents belong to the model-selection and safety-validation track. They are independent from the remediation review.

Recommended order:

1. [Benchmark Summary Report](../../benchmark/report.md)
2. [Synthetic Safety Summary](../../benchmark/synthetic/summary.md)
3. Model-specific raw benchmark outputs
4. Synthetic-profile raw outputs

| Document | Role | Purpose | When to read it |
| --- | --- | --- | --- |
| [Benchmark Summary Report](../../benchmark/report.md) | Benchmark synthesis | Compares multiple report-generation models on Big Five accuracy, judged quality, cost, latency, and judge agreement. | Start here for model-selection conclusions. |
| [Synthetic Safety Summary](../../benchmark/synthetic/summary.md) | Safety-validation synthesis | Summarizes stress-test performance for the safety-claused Kimi K2.5 report prompt across three synthetic profiles. | Read after the main benchmark if you need safety validation. |
| [deepseek-v3 output](../../benchmark/reports/deepseek-v3.md) | Raw benchmark artifact | Model output captured for benchmark scoring. | Read only if you need the exact candidate output. |
| [glm-5 output](../../benchmark/reports/glm-5.md) | Raw benchmark artifact | Model output captured for benchmark scoring. | Read only if you need the exact candidate output. |
| [hermes-3-405b output](../../benchmark/reports/hermes-3-405b.md) | Raw benchmark artifact | Model output captured for benchmark scoring. | Read only if you need the exact candidate output. |
| [kimi-k2.5 output](../../benchmark/reports/kimi-k2.5.md) | Raw benchmark artifact | Model output captured for benchmark scoring. | Read only if you need the exact candidate output. |
| [kimi-k2 output](../../benchmark/reports/kimi-k2.md) | Raw benchmark artifact | Model output captured for benchmark scoring. | Read only if you need the exact candidate output. |
| [nemotron-3-super output](../../benchmark/reports/nemotron-3-super.md) | Raw benchmark artifact | Model output captured for benchmark scoring. | Read only if you need the exact candidate output. |
| [opus-4.6 output](../../benchmark/reports/opus-4.6.md) | Raw benchmark artifact | Model output captured for benchmark scoring. | Read only if you need the exact candidate output. |
| [aggressive-conflict synthetic output](../../benchmark/synthetic/reports/aggressive-conflict-kimi-k2.5.md) | Raw synthetic artifact | Stress-test output used in the safety evaluation. | Read only if you need the exact safety-case example. |
| [clinical-edge synthetic output](../../benchmark/synthetic/reports/clinical-edge-kimi-k2.5.md) | Raw synthetic artifact | Stress-test output used in the safety evaluation. | Read only if you need the exact safety-case example. |
| [religious-intensity synthetic output](../../benchmark/synthetic/reports/religious-intensity-kimi-k2.5.md) | Raw synthetic artifact | Stress-test output used in the safety evaluation. | Read only if you need the exact safety-case example. |

## Related Stack: Profile Assessment Output

This is the end-user style assessment/reporting artifact rather than a project review document.

| Document | Role | Purpose | When to read it |
| --- | --- | --- | --- |
| [Psychometric Personality Profile: Narrative Report](../../profiles/report.md) | Final narrative assessment | Human-readable synthesis of psychometrics, interview, and corpus analysis for a single profile. | Read when you need to see the final assessment product rather than the system-review documents. |

## Quick Reference

Use this if you already know what you are looking for:

- Final verdict: [Final Assessment](./psyche-remediation-plan-final-assessment-2026-03-20.md)
- Plan-ready summary: [Definitive Summary](./psyche-remediation-plan-definitive-summary-2026-03-20.md)
- Formal approval status: [Decision Gate](./psyche-remediation-plan-decision-gate-2026-03-20.md)
- Single authoritative review artifact: [Final Assessment](./psyche-remediation-plan-final-assessment-2026-03-20.md)
- Full plan critique: [Critical Review](./psyche-remediation-plan-critical-review-2026-03-20.md)
- Original item-by-item remapping: [Deferred Item Summary](./psyche-remediation-plan-deferred-item-summary-2026-03-20.md)
- Code-level proof and dependency analysis: [Technical Assessment](../TECHNICAL-ASSESSMENT-2026-03-20.md)
- Packaging/deployment decision details: [Delivery Matrix](../PSYCHE-WEB-NEXTJS-DELIVERY-MATRIX.md)
- Deduplicated upstream review findings: [Synthesized Findings](./iteration-1/synthesized-findings.md)
- Reviewer-specific source documents: [GPT-5.4](./iteration-1/gpt54-review.md), [Gemini](./iteration-1/gemini-review.md), [Opus](./iteration-1/opus-review.md)
- Raw review input packet: [Code Digest](./iteration-1/code-digest.txt)
