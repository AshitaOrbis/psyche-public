# Opus 4.7 — Curated v0.2 Report Independent Review

**Date**: 2026-05-18
**Reviewer**: Independent Opus 4.7 senior reviewer (1M context)
**Scope**: Pre-publication critique of `psycheeval_v0_2_micro_pilot_2026-04-26_v02_hard_codex_only.md` (the curated v0.2 deliverable)
**Method**: Cross-check every numeric claim against `metrics_2026-04-26_v02_hard_codex_only.json`; verify wording against the round-2 consolidated review and Phase 2 claim ledger; standalone-reader pass on structure and completeness.

---

## TL;DR — verdict

**Ship after one focused revision pass.** The bones are solid: Tier 1 headline statistics (C5_CONTRACT > C5 at 67.7%, C4 > C5 at 68.0%, C4 > C1_padded at 62.3%, the §7 slot-B table for gpt-5.4 and gpt-5.5) all reconcile cleanly with the metrics JSON, and the wording discipline from the claim ledger is largely intact. However, I found **four concrete numeric defects**, **two wording violations**, and **several structural improvements** that should land before publication. None are show-stoppers; all are fixable in well under a day. The headline argument survives the pass.

The most important defect: **§6.1 (C5_CONTRACT vs C3) joint position+length numbers are copied from the wrong cell** — the curated report reports the C5_CONTRACT vs C4 joint estimate in both §6.1 and §6.2. The correct §6.1 joint values are `lo_win 0.500 [0.371, 0.634]` (n=80), not `44.9% / [0.298, 0.601]`. The verdict still holds ("straddles 0.5"), so the conclusion is fine — but the numbers must be corrected before any methods-paper reviewer compares against the metrics JSON. Two of the §7 Opus slot-B advantages are also wrong (off by ~3–4pp each).

---

## (A) Numeric accuracy

### Reconciliation against `metrics_2026-04-26_v02_hard_codex_only.json`

Spot-checks against the canonical metrics. ✓ = matches; ✗ = discrepancy.

| Curated location | Claim | Metric source | Status |
|---|---|---|---|
| §1, §4, §5.1 | C5_CONTRACT > C5 = 67.7% [61.7, 73.3] | `C5_vs_C5_CONTRACT.lo_win 0.3229 [0.2667, 0.3826]` → C5_CONTRACT (hi) 67.7% [61.7, 73.3] | ✓ |
| §1, §4, §5.2 | C4 > C5 = 68.0% [61.5, 74.4] | `C4_vs_C5.lo_win 0.6804 [0.6154, 0.7443]` | ✓ |
| §1, §4, §5.3 | C4 > C1_padded = 62.3% [56.1, 68.3] | `C1_padded_vs_C4.lo_win 0.3766 [0.3172, 0.4391]` → C4 (hi) 62.3% [56.1, 68.3] | ✓ |
| §1, §4, §5.5 | C4 > C4_shuffled = 57.8% [52.2, 63.7] | `C4_vs_C4_shuffled.lo_win 0.5781 [0.5219, 0.6375]` | ✓ |
| §1, §4, §6.1 | C5_CONTRACT vs C3 = 49.9% [43.4, 56.4] | `C3_vs_C5_CONTRACT.lo_win 0.5009 [0.4358, 0.5657]` → 49.9% [43.4, 56.4] | ✓ |
| §1, §4, §6.2 | C5_CONTRACT vs C4 = 51.8% [45.2, 58.7] | `C4_vs_C5_CONTRACT.lo_win 0.4818 [0.4127, 0.548]` → C5_CONTRACT (hi) 51.8% [45.2, 58.7] | ✓ |
| §5.1 | length-matched subset 35.1% C5 lo_win [0.238, 0.471] | `joint.C5_vs_C5_CONTRACT 0.3514 [0.2378, 0.4714]` | ✓ |
| §5.1 | joint position+length 64.9% [52.9, 76.2] | derived from 1−0.3514 lo_win → 64.86% [52.86, 76.22] | ✓ |
| §5.2 | C4 > C5 joint = 67.4% [54.7, 79.5], n=76 | `joint.C4_vs_C5 0.6743 [0.5469, 0.7951] n=76` | ✓ |
| §5.2 | judge unanimity gpt-5.4=0.681, gpt-5.5=0.681, Opus=0.679 | `by_judge.C4_vs_C5` → 0.6813 / 0.6813 / 0.6792 | ✓ |
| §5.1 | per-judge C5_CONTRACT > C5 (65.8% / 73.8% / 64.8%) | `by_judge.C5_vs_C5_CONTRACT` lo_win 0.3423 / 0.2619 / 0.3521 → 65.8% / 73.8% / 64.8% | ✓ |
| §5.5 | C4 > C4_shuffled "+7.8 pp above parity" | 0.578 − 0.500 = 0.078 → 7.8 pp | ✓ |
| §5.5 | C4 > C5 "+18.0 pp above parity" | 0.680 − 0.500 = 0.180 → 18.0 pp | ✓ |
| §5.5 | C5_CONTRACT > C5 "+17.7 pp above parity" | 0.677 − 0.500 = 0.177 → 17.7 pp | ✓ |
| §5.5 | C4 > C1_padded "+12.3 pp above parity" | 0.623 − 0.500 = 0.123 → 12.3 pp | ✓ |
| §3.4 / §10 | 1,784 swap records | claimed 864 (Tier A) + 800 (Tier B) + 120 Opus fill = 1,784 — internal arithmetic checks | ✓ |
| §10 audit 0.A | "179 cross-author records" | autogen `cross_author: 179` | ✓ |
| §6.1 | cross-provider C3 vs C5_CONTRACT controlled lo_win 0.457 [0.376, 0.540] | `ab_ba_by_provider_scope_same_author.C3_vs_C5_CONTRACT.cross_provider 0.4574 [0.3764, 0.5408]` | ✓ |

### Discrepancies (must fix)

| # | Curated location | Curated text | Metric source | Discrepancy |
|---|---|---|---|---|
| **D1** | §6.1 (C5_CONTRACT vs C3) | "Joint position+length: 44.9% C5_CONTRACT (CI [0.298, 0.601] straddles 0.5)" | `joint.C3_vs_C5_CONTRACT lo_win 0.5000 [0.3715, 0.6341] n=80` → C5_CONTRACT (hi) wins **50.0% [36.6, 62.9]** | **Both the 44.9% and the CI [0.298, 0.601] are from the wrong cell** (they belong to `C4_vs_C5_CONTRACT`). Replace with `50.0% [36.6, 62.9]` (n=80). Verdict ("straddles 0.5") is unchanged but the numbers must be corrected. |
| **D2** | §6.2 (C5_CONTRACT vs C4) | "Joint position+length: 45.0% C5_CONTRACT (CI [0.298, 0.601] straddles 0.5)" | `joint.C4_vs_C5_CONTRACT lo_win 0.4500 [0.2985, 0.6007] n=65` → C5_CONTRACT (hi) wins **55.0% [39.9, 70.2]** | The CI is correct in raw lo_win terms but **the percentage is labeled inversely**. "45.0% C5_CONTRACT" reports the C4 win rate, not the C5_CONTRACT win rate. Replace with "55.0% C5_CONTRACT [39.9, 70.2]". Verdict unchanged. |
| **D3** | §7 slot-B table | Opus row, C3 vs C5C cell: **+0.233** | `by_judge.C3_vs_C5_CONTRACT.opus.slot_b_advantage 0.2035` | Should be **+0.204** (off by ~3 pp). |
| **D4** | §7 slot-B table | Opus row, C4 vs C5C cell: **+0.238** | `by_judge.C4_vs_C5_CONTRACT.opus.slot_b_advantage 0.1985` | Should be **+0.199** (off by ~4 pp). The row reads as if Opus had ~+0.23 on both C3 and C4 vs C5_CONTRACT pairs, but actually only one of those is true. |
| **D5** | §3.1 corpus table | "Same-author pairwise records (originals) | 3,123 raw / 2,944 true same-author / 179 records leaked" | `counts.pairwise_scores = 3243`, autogen `same_author = 3064`, `cross_author = 179` | **Pre-Opus-fill counts** (off by exactly 120, the C4 vs C5 Opus originals). Correct: 3,243 raw / 3,064 true same-author. The 179 cross-author count remains correct. |
| **D6** | §1 TL;DR | "C5_CONTRACT > C5 ... survives a joint position + length correction (64.9% in the length-similar subset, CI [52.9, 76.2])" | This is correct, but §1.3 of round-2 consolidated review (citing GPT Pro A7) flagged that **the round-2 bundle understated edge attenuation**. The curated report does not state the attenuation magnitude (8.3 pp absolute on the win rate; 32% reduction in above-parity edge). Not a discrepancy with the metrics, but a missing comparison the reader expects. | Optional addition. See (C). |
| **D7** | §7 narrative around the per-judge table | "GPT-5.5 (xhigh): consistent strong +0.14 to +0.31 slot-B advantage. Opus 4.7: moderate +0.09 to +0.24." | GPT-5.5 actual range from per-cell: 0.138 to 0.310 (the +0.14 to +0.31 is correct). **Opus actual range: 0.094 to 0.2035** (max is ~0.20, not 0.24). | Replace "Opus 4.7: moderate +0.09 to +0.24" with "Opus 4.7: moderate +0.09 to +0.20". (Note: the *autogen ledger* says "9-24pp"; that's the source of the error and should also be cleaned up in the analyzer's `CLAIM_LEDGER_SCHEMA`.) |
| **D8** | §1, claim ledger row | "~15-17 pp slot-B preference, judge-family-specific" | Per-judge means: gpt-5.5 mean = ~23.5pp; Opus mean = ~15.9pp; gpt-5.4 mean ≈ 0pp. "15-17 pp" reads as a single summary number, but the actual per-judge means span 0 / 16 / 24 pp. | This is presentation, not arithmetic — but the "15-17" looks chosen to anchor near the Opus mean and undersells the gpt-5.5 magnitude. Recommend recharacterizing as "ranges 0 to ~31 pp depending on judge family; gpt-5.5 mean ~24 pp, Opus mean ~16 pp, gpt-5.4 near zero." |
| **D9** | §3.4 / §10 | "Per-pair AB/BA-matched cell counts after deduplication: ... C4 vs C5_CONTRACT = 288" | `ab_ba_position_audit_same_author.C4_vs_C5_CONTRACT.n_pairs_with_ab_ba = 288` ✓, but in the autogen ledger the joint position+length cell for the same pair reports n=65 in the length-similar subset (consistent). The §3.4 wall-of-text doesn't connect "288" to "65" anywhere — readers comparing §3.4 to §6.2 will be confused. | Add a parenthetical: "(of which 65 fall in the length-similar bucket used for §6.2)". |

### Wilson vs bootstrap CI side-by-side

The curated report (§3.4) says "The Wilson interval is retained side-by-side for continuity." I verified the per-pair Wilson vs bootstrap differences are negligible (<1pp on most pairs; <2pp on borderline ones). The curated report only displays bootstrap CIs in the headline tables and claim ledger, which is correct per round-2 §1.1.

One nit: §3.4 says Wilson gave "slightly tighter intervals on borderline pairs." Per the actual numbers (C3 vs C5_CONTRACT: Wilson [0.443, 0.557], bootstrap [0.436, 0.566]), Wilson is **tighter on the borderline pair by ~2pp total span**. The phrasing is accurate; the round-2 consolidated review §1.1 also confirmed verdicts preserved. Good.

---

## (B) Wording discipline

The claim ledger wording rules are largely respected. Specific verifications:

| Rule | Curated report compliance |
|---|---|
| Slot-B finding scoped to corpus, not universalized (§1.8 round-2) | ✓ §7 has explicit scope paragraph: "This is a measurement of the v0.2 corpus + the v0.2 pairwise judge prompt + the three judge models tested. It does not establish that all LLM-as-judge pipelines have ~15-17 pp slot-B preference." Solid. |
| C5_CONTRACT > C5 framed as package, not mechanism (§1.3 round-2) | ✓ §1, §5.1 both explicitly call out "mechanism not isolated" + list the 4 confounded dimensions. The exact phrase "the defensible package claim is" appears in §5.1. Compliant. |
| "Collapse" ≠ "equivalence" (GPT Pro A15) | ✓ §6.2 explicitly says: "This is **not equivalent to 'C5_CONTRACT = C4'** unless an equivalence margin is predeclared." Excellent. |
| TF-IDF F1=0 framed cautiously (round-2 §2.10) | ✓ §5.1 says "This does not rule out semantic, stylistic, length-based, or judge-internal recognizability, but it removes the simplest 'judge recognizes the treatment' artifact explanation." Compliant. |
| C4 > C4_shuffled tagged "modest" not "significant" (round-2 Tier reassignment table) | ✓ §1 Tier 1.5 explicitly uses "modest"; §5.5 explicitly contrasts "modest" with "significant" and explains the reasoning. |
| C0 dominated explicitly flagged as not-AB/BA-tested (round-2 GPT Pro A6) | ✓ §1 "Not AB/BA-tested directly"; §5.4 "the only Tier 1 finding not directly AB/BA-tested"; ledger row notes "(effect huge, not AB/BA-tested)". Compliant. |
| Cross-provider Phase 0 finding presented as demoted/superseded (§1.7 round-2) | ✓ §6.1's "cross-provider sub-finding now demoted" paragraph cites the AB/BA result directly. Not framed as competing positive verdict. Compliant. |
| Forbidden phrase "PAE empirically resolved" | ✓ §6.3 explicitly says "This wording is struck" and provides replacement framing. Clean. |
| Forbidden phrase "C5_CONTRACT outperforms both C3 and C4" | ✓ §1 Tier 2 explicitly says "original v0.2 plan, now retracted". Clean. |
| Forbidden phrase "Contract repairs source-packet fragility" | ✓ Does not appear. |
| Forbidden phrase "Coherent structure does not significantly beat shuffled" | ✓ Replaced with the positive "C4 modestly outperforms C4_shuffled" framing. |

### Wording violations / softness

| # | Section | Issue | Suggested fix |
|---|---|---|---|
| **W1** | §1 (TL;DR), §7 narrative, §11 limitations | "~15-17 pp slot-B preference, judge-family-specific" is used as the methodology headline — but this masks **judge-family-specific** in the same sentence. A reader sees "15-17 pp" and walks away thinking that's a uniform number. | Restate as: "judge-family-specific slot-B preference, with magnitudes ranging from ~0 pp (gpt-5.4) to ~14-31 pp (gpt-5.5, xhigh) to ~9-20 pp (Opus 4.7), averaging ~16 pp across the two slot-B-preferring judges." This preserves the headline while making the range visible. |
| **W2** | §5.2 "On the Phase 0 vs Phase 1 contradiction" paragraph | The phrasing "These were not contradictory; they addressed different confounds (length vs position) on different sub-samples" is on the right track per round-2 §1.6, but elides the fact that **the Phase 1 findings doc originally framed Phase 0 length-matching as 'a false negative'** — round-2 reviewers explicitly rejected that framing. The current curated text describes the resolution but does not state what was being resolved. | Add one sentence: "An earlier draft characterized the Phase 0 length-matched result as a 'false negative'; round-2 reviewers correctly noted the two corrections target orthogonal confounds, and the joint correction below resolves both simultaneously." |
| **W3** | §8 "Why AB/BA was necessary" | The framing "did we run AB/BA because we suspected a problem, or did we run it because reviewers told us to" is honest and useful. But the subsequent claim "Each of these had a confound-specific interpretation. None individually identified slot-B position bias as the unifying cause" understates §8's own audit 0.E result, which **did** flag slot-A=always-lo as "publication-blocking until AB/BA runs." | Soften to: "Three of the audits each identified a confound-specific interpretation; only 0.E, which directly measured the slot-A=always-lo structural imbalance, named position bias by construction. The remaining audits each gave a partial view that AB/BA unified." |
| **W4** | §10 audit 0.L row | "TF-IDF + logistic test accuracy 27.2% vs 12.5% chance (+14.7pp); F1=0.000 for both C5 and C5_CONTRACT" | The +14.7pp above-chance is presented without context. Is this evidence of recognizability or noise? The autogen says "a stronger classifier or judge-blind recognizability prompt could" — that caveat should travel here too. Add: "The 14.7pp above-chance accuracy reflects the classifier picking up some condition signal in *other* conditions, not C5 vs C5_CONTRACT specifically (where F1=0)." |

### No violations found

- §1 / §5.1 wording on C5_CONTRACT > C5 mechanism: compliant.
- §6 demotion language: compliant.
- §7 slot-B scope: compliant.
- §1 / §11 framing of synthetic-personas pilot: compliant.

---

## (C) Standalone readability + completeness

### What works as a standalone document

- **§1 (TL;DR)** is well-structured: tier-by-tier presentation with the methodology contribution called out as a separate tier. A methods-paper reader can read §1 alone and understand the contribution.
- **§2 (design questions → results table)** is the clearest single-section translation of "what was v0.2 for and did it work" I've seen on this project. The five-row table maps cleanly to v0.1's open questions.
- **§3 (corpus and methods)** has the right level of detail (judges, prompts, blinding key path).
- **§5–§6 tier structure** is logically coherent: Tier 1 (substantive), Tier 1.5 (modest), Tier 2 (demoted). The demotions get explicit treatment rather than being buried.
- **§7 (methodology contribution)** is presented with appropriate scope qualifiers and proper citation of position-bias prior work.
- **§8 (Why AB/BA was necessary)** is a genuinely useful audit-narrative section — uncommon in methods-paper drafts.
- **§14 (Closing)** lands the "retracted headlines are not failures" point well without being defensive (see verdict below).

### Issues that hurt the standalone read

| # | Section | Issue | Suggested fix |
|---|---|---|---|
| **R1** | §1 TL;DR | The TL;DR is ~1,000 words. For a methods-paper-style document, this is too long for §1 — a reader who wants the executive summary should be able to read it in 60 seconds. The tier-by-tier breakdown belongs in §5; §1 should contain only the headline + the methodology contribution + the "what v0.2 is not" framing. | Compress §1 to ~400 words: one paragraph for each tier (no detail), one paragraph for methodology contribution, one paragraph for "what v0.2 is not." Move the per-pair CI numbers and joint-position-length numbers down into §5–§6. |
| **R2** | Missing pre-registration discussion | A methods-paper reviewer will ask: "Was anything pre-registered? Tier-1 cutoffs? Effect-size thresholds? Equivalence margins?" The curated report mentions "the v0.2 plan" several times but never says whether the plan was registered (timestamped, hashed, public) or revised post-hoc. | Add a short "Pre-registration status" subsection under §3 or §11. State explicitly: "The v0.2 plan was authored on 2026-05-05 (`docs/v0_2_plan_extended_2026-05-05.md`) and not formally pre-registered. The seven locked decisions (D1–D7) were documented in advance; the tier-1 cutoff and equivalence margins were not pre-declared, which is why §6's collapsed pairs are framed as 'no detected preference' rather than 'equivalent.'" |
| **R3** | Missing power analysis / sample-size justification | n=288 AB/BA pairs for C3/C4 vs C5_CONTRACT and n=320 for the length-control pairs are stated, but there is no discussion of what effect size these are powered to detect. The collapsed pairs ([43.4, 56.4] CI) suggest minimum detectable effect of ~7pp — worth stating. | Add a sentence in §3.4 or §11: "With n=288 AB/BA pairs per cell, the minimum detectable effect at α=0.05 is approximately ±7 pp on the controlled lo_win rate. The collapsed C5_CONTRACT vs C3 / C4 pairs are thus consistent with absence of effects larger than ~7 pp; smaller effects cannot be ruled out." |
| **R4** | Missing effect-size language | The curated report uses "pp above parity" but no Cohen's h, no log-odds, no standardized effect size. A methods-paper reviewer will ask for at least one standardized metric (Cohen's h is natural for proportions). | Optional but recommended: add a column to the §4 claim ledger with Cohen's h for each Tier 1 pair (e.g., C5_CONTRACT > C5 at 0.677 vs 0.5 → h = 0.357, "small-to-medium"; C4 > C4_shuffled at 0.578 vs 0.5 → h = 0.157, "very small"). Reinforces the "modest" framing for Tier 1.5. |
| **R5** | Missing equivalence-bound discussion | §6.2 correctly says "not equivalent to C5_CONTRACT = C4 unless an equivalence margin is predeclared." But it does not say what such a margin *would* look like, nor whether the data could support an equivalence claim under a sensible margin. | One sentence: "Under a post-hoc equivalence margin of ±10 pp (which would be defensible for a behavioral-difference pilot), both C5_CONTRACT vs C3 (CI [43.4, 56.4]) and C5_CONTRACT vs C4 (CI [45.2, 58.7]) are within the equivalence corridor. The curated report does not claim equivalence because the margin was not pre-declared, but a future v0.3 with a pre-declared margin could make such a claim from this data." |
| **R6** | Duplication between §10 (audit catalog) and §8 (Why AB/BA was necessary) | §8's three-row table (Scalar–pairwise reconciliation / Leave-one-judge-out / Length-matched) duplicates §10 rows 0.B, 0.D, 0.G. The §10 catalog also restates "Phase 1 added 5 more blocks" which is redundant with §3.4. | Cut the §8 three-row table; replace with cross-references to §10 rows 0.B / 0.D / 0.G. Saves ~150 words without information loss. |
| **R7** | §10 catalog: some headlines are stale | Row 0.E says "structural imbalance flagged as publication-blocking until AB/BA runs" — this was Phase 0 framing. Now that AB/BA has run, this should be re-framed as resolved. | Update 0.E headline: "8 of 10 pairs have `slot_a_is_lo_share` = 1.000; other 2 ≥ 0.988; C5_CONTRACT is in slot B 100% of original-pairwise records — structural imbalance now corrected by Phase 1 AB/BA." |
| **R8** | §11 limitations: missing the "scope-limited pairwise" Opus gap | The curated report correctly notes that C0/C1/C1_padded/C3/C4/C4_shuffled pairs have 0 Opus pairwise records, but does not explicitly say *which Tier 1 verdicts* this affects. C4 > C1_padded and C4 > C4_shuffled depend on this. | Reword §11 bullet to: "The Tier 1 verdicts C4 > C1_padded and Tier 1.5 verdict C4 > C4_shuffled depend on gpt-5.4 + gpt-5.5 only; Opus has 0 pairwise records on these pairs. They are robust within OpenAI-family judging but have not been verified by Opus." |
| **R9** | Audience clarity: is this a paper or a report? | The document reads as in-between: more polished than a "report" but missing typical methods-paper components (abstract, related work, statistical methods section, acknowledgments). If the intent is a methods paper, add an abstract + related-work + dedicated methods section. If a research report, the current structure is fine but should say so up front. | Add a "Document type" line in the header: "Style: pre-publication research report. Not a paper draft; the abstract/related-work/etc. structure of a methods paper is deferred." This anticipates the question. |
| **R10** | The "v0.3 priorities" §12 is decision-quality but very long | §12 is 12 items with subsections. For a methods-paper-style document, this should be condensed to 5–6 top items with the rest deferred to a separate v0.3 plan document. The current structure dilutes the priority signal. | Cut §12 to "Tier-1 v0.3 priorities (3 items)" and reference a separate doc for the rest. |

### What a methods-paper reviewer would expect that's currently missing

1. **Pre-registration status** (R2).
2. **Power analysis / minimum detectable effect** (R3).
3. **Standardized effect size** (Cohen's h or similar) (R4).
4. **Equivalence-bound discussion** even if not claimed (R5).
5. **IRB / ethics statement** — even for synthetic-personas, modern methods-paper reviewers expect a one-liner. Add to §3 or §11: "All evaluation used synthetic personas and synthetic scenarios; no human subjects. No IRB review required."
6. **Reproducibility statement** — §10 closes with "All blocks are reproducible from `runs/2026-04-26_v02_hard_codex_only/` via `python -m psycheeval.analyze ...`. 106 tests pass." Good, but should be its own subsection.
7. **Author contributions** statement — even if the project is solo, the methods-paper convention is to note this.

### Anything repeated that could be condensed

- §3.4 "Phase 1 (2026-05-16 to 2026-05-17) ran AB/BA rejudging on all 6 headline pairs" is restated in §8 and again in the audit catalog §10.
- The list of confounded dimensions for C5_CONTRACT (contract presence / ordering / anti-mimicry / length) appears in §1, §5.1, and §6.3.
- The "1,784 swap records" total appears in the header, §3.4, and §10.
- The "67.5% complete-case coverage" appears in §3.1 footnote, §10 row 0.K, and §11.

Each of these is fine once; together they add ~500 words of repetition. Recommend single canonical statement + cross-references.

### §14 (Closing) — does it read as honest or defensive?

**Honest.** The framing "retracted headlines are not a v0.2 failure — they are a v0.2 success" is exactly the right register for this paper. A reviewer hostile to the project will read this as "they're spinning two failed hypotheses as a methodological win," but the actual argument is strong: the v0.2 *design* (C5_CONTRACT separator, anchored rubric, length controls, tri-model authoring) was specifically motivated by the v0.1 concerns that turned out to be load-bearing — and the audit pipeline caught the position-bias artifact before publication, not after.

The risk in §14 is that it reads as bullet-list summary rather than synthesis. Recommend rewriting as a single paragraph that argues the pipeline-functioning point with one concrete pivot:

> "The five-point list above hides the actual structural lesson. The two retracted headlines were not the result of a measurement that turned out to be wrong; they were the result of a measurement protocol (uncounterbalanced pairwise judging) that systematically misrepresented the underlying preferences in the corpus. The v0.2 design caught this by accident — the C5_CONTRACT separator and tri-model authoring did not specifically target position bias, but the resulting design exposed the artifact. The Phase 1 AB/BA experiment was the canonical fix, and v0.3 will run AB/BA by default."

This is what §14 is already trying to say; rewriting it as one tight paragraph would land harder.

---

## (D) Issues round-2 reviewers may have missed

These are points I did not see addressed in either the round-2 consolidated review or the Phase 2 hygiene summary. They are not blocking, but worth a Phase 3 author pass.

### D1. The Opus AB/BA Tier B coverage gap is still partly real

Round-2 §1.10 (Opus A.3 secondary) noted that Opus AB/BA on C3 vs C5_CONTRACT and C4 vs C5_CONTRACT was under-covered (Opus AB/BA n=87 / n=85 vs original n=115 / n=117). The Phase 2 hygiene pass closed the C4 vs C5 gap but **did not close these two**. The curated report does not flag this explicitly. Either:
  - Add a sentence to §11: "Opus AB/BA n on C3 vs C5_CONTRACT and C4 vs C5_CONTRACT is ~30 records below the corresponding original-pairwise n (Opus 87/85 vs original 115/117). Non-random subset effects on these two pairs cannot be ruled out without backfill."
  - OR run the ~60 Opus calls to close the gap.

The first option is cheaper and defensible.

### D2. Persona × author × condition interaction was added to the analyzer but not surfaced in the curated report

Phase 2 §A.7 added `pairwise_by_persona_x_author_same_author` to address Opus round-2 A.7 ("Slalom Altar × Opus may carry the reversal on C4 vs C5_CONTRACT"). The curated report mentions this block in §10 but does not actually discuss what it found. Either drop the §10 mention or add one sentence: "The persona × author × condition crosstab confirms that Slalom Altar × Opus contributes the reversal on C4 vs C5_CONTRACT, but the reversal does not extend to other persona × author combinations." (I have not verified this against the metrics myself; the curated report's author should.)

### D3. The 4-way decomposition is mentioned but not displayed

§7 ends with: "Within each (pair, judge) cell, the 4-way decomposition (`condition_lo_stable` / `condition_hi_stable` / `slot_A_stable` / `slot_B_stable`) shows how many AB/BA-matched pairs are condition-stable vs slot-stable. The full decomposition is rendered in the autogen scaffold under 'AB/BA per-cell decomposition by judge.'"

For a methods-paper-style document, the canonical decomposition for *at least the headline pair* (C5_CONTRACT > C5) should be rendered inline. The numbers are striking — for C5 vs C5_CONTRACT under gpt-5.5: 9 condition-lo-stable, 49 condition-hi-stable, 0 slot-A-stable, 26 slot-B-stable. That's a very legible "the slot-B preference is real but condition_hi_stable dominates" story.

### D4. No discussion of the gpt-5.4 negative slot-B advantage

The curated §7 table shows gpt-5.4 has **negative** slot-B advantage on C3 vs C5_CONTRACT (−0.036) and C4 vs C4_shuffled (−0.025). This is a striking pattern — one of three judges is essentially position-neutral. The methodology section treats this as background, but it's actually the most actionable finding for v0.3: **if you can identify which judge family is position-neutral on this protocol, use that family.** Worth a paragraph in §7 or §12.

### D5. The "force-choice" limitation note (§11) is buried

§11 mentions "A 'no meaningful difference' option (per GPT Pro C8) might reduce forced precision on the collapsed C5_CONTRACT vs C3/C4 pairs" as a one-line limitation. This is actually a **critical** point for the demoted pairs — the 49.9% / 51.8% controlled rates may reflect forced-choice noise around a true zero effect rather than a true detected null. Worth promoting to a "Limitations affecting Tier 2" subsection.

### D6. The 67.5% complete-case scalar coverage hides a missing-data analysis

§11 notes 67.5% complete-case coverage as a limitation but does not say *which judges are missing on which outputs*. If missingness is correlated with condition (e.g., longer C5_CONTRACT outputs are more likely to fail judge timeouts), pooled scalar means could be biased. A short MCAR check (per-condition missingness rates) would strengthen this. The autogen has `complete_case_scalar_anchored` — that block should be cited.

### D7. The 179 cross-author leak: was it MCAR?

§3.1 notes "179 records leaked cross-author from a missing `--scope same_author_only` on the Opus C5_CONTRACT pairwise phase (Phase 0 detection); excluded from same-author analyses." The fix is correct (exclude), but the curated report does not say whether the excluded records were a random subset of the Opus C5_CONTRACT pairwise calls or systematically distinct. If they're systematically distinct (e.g., all from a specific persona × scenario subset), exclusion could itself introduce bias. Worth a sentence noting the random-vs-systematic check.

### D8. The "scenarios may be profile-aware" limitation needs sharper framing

§11 has: "Round-2 reviewers (Codex Council, GPT Pro) flagged that scenarios were authored by the same models that participate as judges; future v0.3 should add scenarios authored blind to profile theory."

This understates the concern. The actual issue is **leakage of profile-relevant cues into scenarios**: if a scenario about "decision-making under uncertainty" was authored by a model that has seen the profile content, the scenario may be tilted to favor profile-aware responses. The current framing reads as "model overlap" when the real issue is "feature overlap." A more pointed framing: "scenarios may have been written in a way that rewards profile-legibility regardless of whether profile-legibility is actually the correct behavior."

### D9. No discussion of why the "C5_CONTRACT vs C3" collapse is the more interesting finding

The curated report treats the collapse of C5_CONTRACT vs C3 as one of two demotions. But scientifically, it is the **most interesting** finding in the demoted set: C3 is a behavioral contract with no source packet; C5_CONTRACT is a behavioral contract + source packet. If they're truly indistinguishable under controlled judging, **the source packet contributes nothing detectable**. This is a strong (if negative) result about source-packet value at this corpus scale.

§6.3 alludes to this ("v0.3 ablations are required for mechanism claims") but does not name the implication. Worth one sentence: "Under counterbalanced judging, adding the source packet to the contract (C5_CONTRACT vs C3) does not produce a detectable preference. This is consistent with two interpretations: (a) the source packet contributes nothing beyond what the contract already provides, or (b) the source packet contributes signal that this corpus + protocol cannot detect at n=288. v0.3 ablations are required to discriminate."

### D10. The cluster bootstrap cluster unit is stated once, never justified

§3.4 says cluster unit = "persona × scenario × author, 2,000 resamples." But:
- Why not just persona, or just scenario? The literature is split.
- Why 2,000 resamples? Standard but should be cited.
- The matched-pair structure (AB/BA pairs within cluster) is the actual unit of analysis; "persona × scenario × author" identifies the *unit* but the bootstrap resamples *clusters* not pairs. Worth a sentence explaining the design choice.

This is methodology-section depth that a peer reviewer will ask for.

---

## Summary table — what to fix before publication

Priority: **P0** = must fix; **P1** = should fix; **P2** = nice to fix.

| Priority | Item | Effort |
|---|---|---|
| **P0** | D1: §6.1 joint position+length numbers wrong cell | 5 min |
| **P0** | D2: §6.2 joint position+length labeling inverted | 5 min |
| **P0** | D3, D4: §7 Opus slot-B advantages (two cells off by ~3-4pp) | 5 min |
| **P0** | D5: §3.1 corpus table pre-Opus-fill counts | 5 min |
| **P1** | D7: §7 Opus range "+0.09 to +0.24" should be "+0.09 to +0.20" | 5 min |
| **P1** | W1 / D8: "~15-17 pp" headline masks per-judge variation | 15 min |
| **P1** | R1: Compress §1 TL;DR to ~400 words | 30 min |
| **P1** | R2: Add pre-registration status sentence | 10 min |
| **P1** | R3: Add power / MDE sentence | 10 min |
| **P1** | R8: Sharpen §11 scope-limited pairwise statement | 5 min |
| **P1** | (D) D1: Note Opus n gap on C3/C4 vs C5_CONTRACT | 5 min |
| **P2** | W2: §5.2 "false negative" framing acknowledgment | 10 min |
| **P2** | W3: §8 audit-narrative softening | 10 min |
| **P2** | R4: Add Cohen's h column to claim ledger | 20 min |
| **P2** | R5: Add equivalence-bound discussion | 10 min |
| **P2** | R6: Cut §8 duplication with §10 | 10 min |
| **P2** | R7: §10 audit row 0.E stale headline | 5 min |
| **P2** | R9: "Document type" header line | 2 min |
| **P2** | R10: Compress §12 v0.3 priorities | 20 min |
| **P2** | (D) D2-D9: various depth additions | 1-2h total |

Total to ship (P0 only): ~30 min.
Total to revise well (P0 + P1): ~2 hours.
Total to make this methods-paper-ready (P0 + P1 + P2): ~4-5 hours.

---

## Bottom line

The curated v0.2 report is a high-quality piece of work that has clearly absorbed the round-2 reviewer guidance. The wording discipline is excellent; the Tier 1 numbers reconcile cleanly; the methodology contribution is properly scoped; the demoted headlines are honestly treated. The four numeric defects I found (D1-D4) are mechanical and fast to fix. The structural issues (R1-R10) are quality-of-life improvements for a methods-paper audience — none would block publication.

**The §6.1 / §6.2 joint position+length numbers (D1, D2) are the single most embarrassing defect** because they would be the first thing a methods-paper reviewer checks against the metrics JSON. Fix those before anything else.

Beyond that, this report is closer to publishable than the v0.1 micro-pilot report was at the equivalent stage. The audit-pipeline narrative is unusually strong for an LLM-eval methods paper. Ship after the P0 fixes; the P1 improvements can land in a Phase 3 author pass.

— Opus 4.7, independent senior reviewer, 2026-05-18
