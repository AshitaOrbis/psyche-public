# PsycheEval v0.2 — Phase 2 Hygiene Pass Summary

**Date**: 2026-05-17
**Status**: Complete (13 of 13 items)
**Trigger**: Round-2 consolidated review (4 reviewers; convergence on 13 publication-blocking issues)
**Tests**: 106 pass

---

## Headline

The Phase 2 hygiene pass took the v0.2 dataset from "publishable after fixes"
to "ready to write the curated report." All 13 round-2 unanimous fixes
landed. Two findings shifted Tier assignments:

1. **C4 > C5 promoted from Tier 1.5 (scope-limited) to clean Tier 1** after the Opus AB/BA fill (240 Opus calls, zero cap events, zero failures). Now judge-unanimous: gpt-5.4=0.681, gpt-5.5=0.681, opus=0.679. Joint position+length CI [0.547, 0.795] excludes 0.5 — only such joint-corrected Tier 1 pair besides C5_CONTRACT > C5.

2. **C5_CONTRACT > C5 remains the most robust Tier 1**: position-controlled 67.7% [62.1, 72.8] cluster bootstrap, scalar-aligned (+3.057), judge-unanimous, family-robust, joint position+length corrected [0.238, 0.471] still excludes 0.5.

The curated v0.2 report can now be written from a fully-audited dataset.

---

## The 13 hygiene fixes

### 2.0 — Phase 1 findings doc arithmetic errors [GPT Pro A1]

Three errors caught by GPT Pro:
- "873 Tier A records" → corrected to 864 (288 × 3 C5_CONTRACT pairs)
- C4 vs C1_padded "66.1% C4 [59.5, 72.0]" → corrected to **62.3% [57.1, 67.6]**
- C4 vs C5 "68.9% C4 [61.6, 75.9]" → corrected to **68.1% [60.6, 74.9]** (and later updated to 68.0% after Opus fill)

### 2.1 — Wilson CI → cluster bootstrap on AB/BA controlled rate [unanimous]

`analyze.py:654` had Wilson on rounded fractional sum. Replaced with cluster bootstrap (cluster unit: persona × scenario × author, matching `_compute_cluster_bootstrap_pairwise`). Wilson kept side-by-side for transparency.

**Result**: All 6 verdicts hold. Bootstrap CIs slightly wider on borderline pairs (e.g. C3 vs C5_CONTRACT: Wilson [0.443, 0.557] vs bootstrap [0.436, 0.566]). GPT Max Empiricist had spot-checked this offline and reported "verdicts preserved" — confirmed.

### 2.3 — Claim ledger as central report artifact [unanimous]

New `CLAIM_LEDGER_SCHEMA` constant + `_build_claim_ledger` function. 8 rows: 5 Tier 1, 1 Tier 1.5, 2 Tier 2, 1 Methodology contribution. Each row carries:
- controlled lo_win + bootstrap CI
- scalar delta + sign agreement
- judge scope, author scope
- joint position+length CI where applicable
- explicit **allowed wording** and **forbidden wording**

Rendered in autogen as the report's central source-of-truth (replaces the split between "Final AB/BA" and "Final tier assignment").

### 2.4 — Per-judge AB/BA stratification [unanimous]

New `ab_ba_position_audit_same_author_by_judge` block. The methodology contribution ("LLM judges show ~15-17pp slot-B preference, judge-family-specific") is now reproducible from the metrics JSON, not offline. Also includes per-(pair, judge) four-way decomposition (`condition_lo_stable`, `condition_hi_stable`, `slot_A_stable`, `slot_B_stable`, `either_tie`).

**Confirmed**: GPT-5.4 sometimes shows NEGATIVE slot-B advantage (slot-A favored) — particularly on C3 vs C5_CONTRACT (-0.036). GPT-5.5 consistent +0.20 to +0.31; Opus consistent +0.09 to +0.24.

### 2.5 — Complete-case scalar table [unanimous]

`complete_case_scalar_anchored` top-level block. 1,134 / 1,680 outputs (67.5%) scored by all 3 judges. Per-condition scalar means computed on this strict subset for comparison with pooled means.

### 2.6 — Stale-text lint + supersession table [Codex Council, GPT Max, GPT Pro]

Removed forbidden phrases from analyzer output and autogen:
- "pure position bias" → "slot effect"
- "cannot be a recognition artifact" → "does not rule out semantic/stylistic recognizability"

Phase 1 findings doc retains forbidden phrases only inside legitimate "strike entirely" meta-references.

### 2.7 — Joint position × length AB/BA [Opus A.1, GPT Pro A10]

New `ab_ba_joint_position_length_same_author` block. Subsets AB/BA records to the length-similar bucket, computes controlled lo_win in this intersection.

**Critical results**:
- **C4 vs C5**: joint controlled 67.4% [0.547, 0.795] — survives (after Opus fill); previously straddled 0.5 with codex-only data [0.457, 0.783]
- **C5_CONTRACT > C5**: joint controlled 0.351 [0.238, 0.471] — clearly excludes 0.5
- **C5_CONTRACT vs C3**: joint controlled 0.449 [unchanged] — consistent with no preference
- **C5_CONTRACT vs C4**: joint controlled 0.450 [0.298, 0.601] — consistent with no preference

### 2.8 — Cross-provider AB/BA C3 vs C5_CONTRACT [unanimous]

New `ab_ba_by_provider_scope_same_author` block. Stratifies AB/BA records by judge-author provider relationship.

**Critical result**: Cross-provider AB/BA for C3 vs C5_CONTRACT = 0.457 [0.376, 0.540] — straddles 0.5. **Phase 0 cross-provider finding is empirically demoted** under counterbalancing. GPT Max Empiricist's offline result (0.543 hi-win = 0.457 lo-win) canonicalized.

### 2.9 — Scalar-pairwise alignment for all Tier 1 pairs [GPT Pro A12]

Verified that existing `scalar_pairwise_reconciliation_same_author` covers all 5 Tier 1 pairs. All show pairwise+scalar sign agreement:
- C0 vs C4: scalar Δ +6.075 (agree, 86%)
- C5_CONTRACT vs C5: +3.057 (agree, 79%)
- C4 vs C1_padded: +3.084 (agree, 76%)
- C4 vs C5: -3.261 (= C5 lower in scalar; consistent with C4 winning; agree)
- C4 vs C4_shuffled: -0.519 (weak agree, 66%)

### 2.10 — TF-IDF recognition wording [Codex Council, GPT Pro A13]

Replaced over-strong "cannot be a recognition artifact" with nuanced: "this simple TF-IDF lexical classifier could not distinguish C5 from C5_CONTRACT outputs from text alone. This does NOT rule out semantic, stylistic, length-based, or judge-internal recognizability."

### A.7 — Persona × author cross-tabulation [Opus A.7]

New `pairwise_by_persona_x_author_same_author` block. Phase 0 had per-persona and per-author separately but not the interaction. Enables testing whether persona-specific reversals (e.g. Slalom Altar × Opus on C4 vs C5_CONTRACT) are carrier-author-specific.

### 2.11 — Opus C4 vs C5 fill [Codex Council Skeptic, GPT Max architect]

**Most consequential structural fix.** Phase 0 §0.C had confirmed Opus has 0 records on C4 vs C5 — Phase 1 AB/BA for this pair was therefore OpenAI-judge-only.

Ran: 120 Opus original pairwise calls + 120 Opus AB/BA swap calls = **240 Opus calls total**. Zero cap events. Zero failures.

**Result**: C4 vs C5 promoted from Tier 1.5 (scope-limited) to clean Tier 1:
- Position-controlled lo_win: 0.680 [0.615, 0.744]
- **Judge-unanimous**: gpt-5.4=0.681, gpt-5.5=0.681, opus=0.679
- **Joint position+length corrected**: 0.674 [0.547, 0.795] — excludes 0.5

This is the single best validation of the round-2 reviewer recommendation: running 240 Opus calls converted a scope-limited Tier 1.5 verdict into the dataset's cleanest, judge-unanimous, jointly-corrected Tier 1 finding.

---

## Final tier assignment

| Tier | Pair | Controlled lo_win | Bootstrap CI | Joint length+position CI | Judge scope | Wording |
|---|---|---|---|---|---|---|
| **1** | **C5_CONTRACT > C5** | 0.323 | [0.267, 0.383] | [0.238, 0.471] ✓ | all 3 judges | Package claim only; mechanism deferred to v0.3 |
| **1** | **C4 > C5** | 0.680 | [0.615, 0.744] | [0.547, 0.795] ✓ | all 3 judges | Judge-unanimous (after Opus fill) |
| **1** | **C4 > C1_padded** | 0.377 | [0.317, 0.439] | n/a | gpt-5.4 + gpt-5.5 | Length-controlled + position-controlled |
| **1** | **C0 dominated** | (not AB/BA tested) | (effect huge) | n/a | all 3 judges | Effect outside slot-B preference range |
| **1.5** | C4 > C4_shuffled (modest) | 0.578 | [0.522, 0.637] | (close to CI boundary) | gpt-5.4 + gpt-5.5 | Sign-corrected from Phase 0; modest effect |
| **2** | C5_CONTRACT vs C3 — no preference | 0.501 | [0.436, 0.566] | (straddles 0.5) | all 3 judges | Position-bias-confounded original |
| **2** | C5_CONTRACT vs C4 — no preference | 0.482 | [0.413, 0.548] | (straddles 0.5) | all 3 judges | Position-bias-confounded original |
| **Methodology** | LLM slot-B preference | (see per-judge block) | (per-judge bootstrap CIs) | n/a | scoped to this corpus | Not universalized |

Tier 1 went from 4 pairs (mixed scope) to **4 pairs with clean coverage** after the Opus C4 vs C5 fill. Tier 1.5 went from 2 pairs to 1.

---

## What the curated report can now claim

### Strong (Tier 1)

- **C5_CONTRACT > C5**: 67.7% under position-controlled judging across all 3 judges. Survives joint position+length correction (67.6% C5_CONTRACT wins in length-matched subset). Judge-unanimous. Persona-robust. Family-robust. Scalar-aligned. Mechanism not isolated (v0.3 question).
- **C4 > C5**: 68.0% under position-controlled judging, judge-unanimous across all 3 judges. Survives joint position+length correction (67.4% in length-matched subset).
- **C4 > C1_padded**: 62.3% under position-controlled judging. (gpt-5.4 + gpt-5.5 only; Opus n=0 on this pair.) Length-control + position-control both pass.
- **C0 dominated by any profile condition**: pairwise 86.6% C4-over-C0, scalar Δ +6.075. Not AB/BA-tested but the magnitude is well beyond the measured slot-B preference range.

### Modest (Tier 1.5)

- **C4 > C4_shuffled**: 57.8% under position-controlled judging. Sign-corrected from Phase 0 (original 51.9% was understating because slot-A bias hurt C4). Tag as smaller effect than Tier 1.

### Demoted (Tier 2 — no detected preference under counterbalancing)

- **C5_CONTRACT vs C3**: controlled 49.9% [44.3, 55.7]. Position-bias-confounded original.
- **C5_CONTRACT vs C4**: controlled 51.8% [46.0, 57.5]. Position-bias-confounded original.

### Methodology contribution

- LLM pairwise judges in this corpus + protocol show ~15-17pp slot-B preference, judge-family-specific (gpt-5.4 negligible / occasionally slot-A; gpt-5.5 25-31pp; Opus 9-24pp). Wording scoped to corpus.

---

## What's deferred to v0.3 (per round-2 reviewer consensus)

| Priority | Experiment | Tests |
|---|---|---|
| 1 | `C_GENERIC_CONTRACT` | Whether C5_CONTRACT > C5 is "contract" or "generic high-quality prompting" |
| 1 | `C4_WRONG_PROFILE` | Whether the contract benefit is profile-specific or generic |
| 2 | `C5_NONPUBLIC` + `C5_NONPUBLIC_CONTRACT` | Isolate public-anchor effect from packet form |
| 2 | Contract component ablation | Ordering / anti-mimicry / packet form / length within C5_CONTRACT |
| 3 | Profile freshness / staleness | Deployment realism |
| 3 | Profile compression curve | Token-cost frontier |
| 3 | Paraphrased anchored rubric | Rubric robustness |
| 3 | Same-orientation rejudge sentinel | Decompose position bias from retest noise |
| 3 | Human-rater calibration | 30-100 disagreement-heavy pairs |
| 4 | Real-user shadow validation | Construct validity centerpiece |
| 4 | Scenarios authored blind to profile theory | Benchmark construction validity |

---

## Files modified

| File | Change |
|---|---|
| `src/psycheeval/analyze.py` | 5 new functions (`_compute_ab_ba_position_audit_by_judge`, `_compute_ab_ba_by_provider_scope`, `_compute_ab_ba_joint_position_length`, `_compute_pairwise_by_persona_x_author`, `_compute_complete_case_scalar`, `_build_claim_ledger`); cluster bootstrap on AB/BA controlled rate; CLAIM_LEDGER_SCHEMA constant; wording fixes for "pure position bias" and "cannot be a recognition artifact" |
| `reports/reviews/2026-05-16_phase1_ab_ba_findings.md` | Arithmetic corrections (873→864, 66.1%→62.3%, 68.9%→68.1%→68.0%); C4 vs C5 promotion narrative |
| `reports/metrics_2026-04-26_v02_hard_codex_only.json` | Now includes claim_ledger, 4 new AB/BA stratifications, complete_case_scalar |
| `reports/psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md` | Claim ledger renders at top; new AB/BA per-judge / per-scope / joint-correction tables; updated discoverability wording |
| `runs/2026-04-26_v02_hard_codex_only/pairwise_scores.jsonl` | +120 Opus C4 vs C5 originals |
| `runs/2026-04-26_v02_hard_codex_only/pairwise_swap_scores.jsonl` | +120 Opus C4 vs C5 swaps |

---

## What's next

Curated v0.2 report. The claim ledger in the autogen is the central artifact;
the curated report should:

1. Lead with the methodology contribution (slot-B preference quantification)
2. Present Tier 1 findings using the claim ledger's allowed wording
3. Explicitly retract the original C5_CONTRACT > C3 and C5_CONTRACT > C4 headlines, citing the AB/BA correction
4. Use the "Why AB/BA was necessary" subsection to fold in the cross-provider Phase 0 demotion
5. State limitations + v0.3 priorities

Expected length: 8-15 pages for a methodology pilot paper or 4000-6000 words for a long-form blog post.
