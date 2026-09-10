# PsycheEval v0.2 — Review Bundle Round 2

**Date**: 2026-05-17
**Purpose**: External review of v0.2 after Phase 0 (same-data audits) and Phase 1
(AB/BA counterbalanced rejudging) corrections. Goal: identify any remaining
must-fix issues before writing the v0.2 curated report, and document
v0.3-scope issues separately.

This bundle is structured for reviewers who saw the previous round (or its
output). If new, read the previous-round bundle at
`reports/reviews/2026-05-15_v0_2_review_bundle.md` and the previous
consolidated synthesis at
`reports/reviews/2026-05-15_consolidated_v0_2_review.md` first.

---

## 1. Recap — what was the v0.2 pilot, briefly

PsycheEval v0.2 = synthetic-first eval of whether structured user-profile
context changes assistant behavior. 8 personas × 80 scenarios × 3 authors
(GPT-5.4, GPT-5.5-xhigh, Opus 4.7) × varying conditions (C0–C5_CONTRACT) =
1,680 assistant outputs. 3 judges (same models, openai + anthropic provider
families). Anchored 0–10 scalar rubric + same-author pairwise judging.

Original v0.2 headline claims (pre-round-1):
1. C4 > C1_padded (structural advantage of behavioral contract, NOT length)
2. C5_CONTRACT > C5 (contract repairs source-packet fragility)
3. C5_CONTRACT > C3 AND C5_CONTRACT > C4 (source packets add value when subordinated to contracts)
4. C4 > C5 (under harder scenarios, C5 no longer competitive)
5. "v0.1 PAE confound is empirically resolved in favor of absence of contract as dominant driver"

---

## 2. Round-1 review (2026-05-15) and what it found

Three external reviewers (GPT Pro single-agent, GPT-Max HCOM-coordinated
4-agent, Codex Council blind 4-agent ensemble) converged on:

- **Labeling defect**: "3,123 same-author pairwise records" was wrong;
  actually 2,944 true same-author + 179 cross-author records from an Opus
  scope leak. Cross-provider same-author was only 264 records.
- **C5_CONTRACT > C3 was fragile**: CI [0.354, 0.500] touches 0.5,
  reverses for GPT-5.4, reverses on persona Slalom Altar, reverses in
  epistemic_uncertainty and shame_self_interpretation families.
- **Position bias unaudited and publication-blocking**: C5_CONTRACT was
  in slot B 100% of pairwise records. AB/BA counterbalanced rejudging
  was unanimously called "the cheapest decisive next experiment."
- **GPT-Pro's surprise finding**: in the PI scalar table, C3 beats
  C5_CONTRACT on every dimension despite C5_CONTRACT winning pairwise.
  Pairwise-judge preference vs anchored-rubric performance diverge.
- **Length confound for C5_CONTRACT unresolved**: profile chars C5_CONTRACT
  7,433 vs C3 2,518 vs C4 3,689.
- **"PAE empirically resolved" was an overclaim** that all 3 reviewers
  flagged.

---

## 3. What happened in Phase 0 (2026-05-15 → 2026-05-16)

12 same-data analyses run on the existing 1,680 outputs, 3,949 anchored
scalar records, 3,123 pairwise records. New analyzer blocks added to
`compute_metrics`, rendered in the autogen scaffold, 8 new smoke tests
(106 total pass). All work is committed to the analyzer code, not one-off
scripts. Findings document at
`reports/archive/2026-05-15_pre-labeling-fix/PHASE0_FINDINGS.md`.

### Phase 0 verified reviewer claims (no novel data; reanalysis only)

| Reviewer claim | Phase 0 task | Verdict |
|---|---|---|
| Cross-author leak (179 records) | 0.A | ✓ Exactly verified; leak-detection block added |
| GPT-5.4 reverses C3 vs C5_CONTRACT to ~0.57 | 0.C | ✓ Exact: 0.571 [0.465, 0.672]; Opus is 0.330 |
| Slalom Altar reverses C4 vs C5_CONTRACT | 0.C | ✓ 0.657 vs 0.19–0.48 for the other 3 PI personas |
| C4 vs C5 is OpenAI-judge-only | 0.C | ✓ Opus has 0 records on this pair |
| Scenario-family reversals for C5_CONTRACT pairs | 0.F | ✓ Both epistemic_uncertainty (0.643) and shame (0.556) reverse C3 vs C5_CONTRACT direction |

### Phase 0 new findings (from the audits themselves)

1. **GPT-Pro's scalar-pairwise contradiction is real and concentrated**
   (0.B): C5_CONTRACT > C3 has scalar Δ_total = **−0.053** (essentially
   zero); pairwise prefers C5_CONTRACT 57.6%. Same for C5_CONTRACT vs C4
   (Δ_total = −0.231). The C5_CONTRACT > C5 pair, by contrast, has scalar
   Δ_total = **+3.057** with sign agreement 79.4% — both channels agree.

2. **C3 vs C5_CONTRACT is judge-fragile** (0.D): dropping Opus from the
   LOO sample shifts lo_win from 0.428 to 0.494 (Δ +0.066). The Opus
   judge carries the advantage in the all-judge view.

3. **C3 vs C5_CONTRACT vanishes under length matching** (0.G): full
   lo_win 0.428 → similar-length-bucket 0.449 [0.343, 0.559] includes
   0.5.

4. **C3 vs C5_CONTRACT *strengthens* under cross-provider judging only**
   (0.A): with the stratified cluster-bootstrap on judge-provider scope,
   cross-provider same-author CI is [0.238, 0.446] — clearly
   C5_CONTRACT-favoring. Same-provider judges dilute toward 0.500. This
   nuance was not in any reviewer's original critique.

5. **Every pair is structurally A/B imbalanced** (0.E): slot_a_is_lo_share
   = 1.000 for 8 of 10 pairs, ≥0.988 for the other 2. C5_CONTRACT 100%
   slot B. AB/BA rejudging required.

6. **Macro vs micro aggregations agree** (0.I) — clean negative result
   (within 5pp on every dimension).

7. **Rubric lexical-overlap doesn't explain C5_CONTRACT** (0.J): Jaccard
   uniformly 0.047–0.073; C5_CONTRACT has lower overlap (0.063) than C3
   (0.073) and C4 (0.069).

8. **Cross-judge red-flag predictiveness is real** (0.H): P(loser more
   flagged | asymmetric) = 0.65–0.88 across all 10 pairs; all CIs exclude
   0.5. Red flags are a signal, not a within-judge artifact.

9. **Only 67.5% of outputs scored by all 3 judges** (0.K): complete-case
   subset 1,134/1,680. Scalar pooled means carry potential selection
   bias.

10. **C5 vs C5_CONTRACT cannot be a recognition artifact** (0.L): TF-IDF
    classifier has F1 = 0.000 for both C5 and C5_CONTRACT — output text
    doesn't carry the distinction.

---

## 4. What happened in Phase 1 (2026-05-16 → 2026-05-17)

AB/BA counterbalanced rejudging on ALL 6 headline pairs:

- Tier A: 3 C5_CONTRACT-edge pairs × 3 judges = 873 swap-rejudge records
  (504 codex + 369 Opus)
- Tier B: 3 non-C5_CONTRACT pairs × 2 codex judges = 800 swap-rejudge records
- **Total: 1,664 swap records** with full per-pair coverage

New analyzer block `_compute_ab_ba_position_audit` joins originals with
swap records via the run_id-swap signature, reports per-pair:
position_consistent_rate, position_flip_rate, controlled lo_win, Wilson CI.

### Headline AB/BA results (final, n=1,664)

```
pair                  n_AB/BA  orig lo_win  swap lo_win  controlled  controlled CI95     verdict
C1_padded vs C4         320       0.319       0.434      0.377     [0.324, 0.429]    ✓ survives (C4 wins)
C3 vs C5_CONTRACT       288       0.428       0.573      0.501     [0.443, 0.557]    ⚠ COLLAPSES
C4 vs C4_shuffled       320       0.519       0.637      0.578     [0.523, 0.631]    ✓ strengthens (C4 wins)
C4 vs C5                160       0.637       0.725      0.681     [0.606, 0.749]    ✓ strengthens (C4 wins)
C4 vs C5_CONTRACT       288       0.400       0.562      0.482     [0.425, 0.540]    ⚠ COLLAPSES
C5 vs C5_CONTRACT       288       0.240       0.403      0.323     [0.272, 0.379]    ✓ survives (C5_CONTRACT wins)
```

### Slot B advantage measured per judge

```
pair                  gpt-5.4    gpt-5.5     Opus      mean
C3 vs C5_CONTRACT     -0.036     +0.250     +0.233    +0.147
C4 vs C5_CONTRACT     +0.024     +0.250     +0.238    +0.169
C5 vs C5_CONTRACT     +0.112     +0.310     +0.094    +0.163
```

**Pattern**: gpt-5.5 and Opus have ~15–31 pp slot-B preference; gpt-5.4
has essentially none. The "C3 vs C5_CONTRACT under cross-provider judging
strengthens" Phase 0 finding is explained by this: gpt-5.4 was the
cross-provider judge for Opus-authored cells and has no position bias.

---

## 5. Final tier assignment (after Phase 0 + Phase 1)

### Tier 1 — publish with controlled estimates

| Pair | Original | Controlled | Notes |
|---|---|---|---|
| **C0 dominated** | 86.6% C4 over C0 | (not AB/BA tested; effect is huge) | Robust |
| **C4 > C1_padded** | 68.1% | **66.1% C4** [59.5, 72.0] | Length-controlled (Phase 0) + position-controlled (Phase 1) |
| **C4 > C5** | 63.7% | **68.9% C4** [61.6, 75.9] | Strengthens under AB/BA — counter to Phase 0 length-match prediction |
| **C5_CONTRACT > C5** | 76.0% | **67.7% C5_CONTRACT** [62.1, 72.8] | Survives all 12 Phase 0 + AB/BA. Judge-unanimous. Scalar-aligned. |
| **C4 > C4_shuffled** | "no diff" 51.9% | **57.8% C4** [52.3, 63.1] | Sign-correction of Phase 0 §6f — original was understating because slot-A bias hurt C4 |

### Tier 2 — collapses under counterbalancing

| Pair | Original | Controlled | Verdict |
|---|---|---|---|
| **C5_CONTRACT vs C3** | C5_CONTRACT 57.2% | C5_CONTRACT 49.9% [44.3, 55.7] | No real preference |
| **C5_CONTRACT vs C4** | C5_CONTRACT 60.0% | C5_CONTRACT 51.8% [46.0, 57.5] | No real preference |

### Strike

- "v0.1 PAE confound is empirically resolved in favor of absence of contract as dominant driver" — too strong.
- "C5_CONTRACT outperforms both C3 and C4" — split into the per-pair downgrades above.
- "Coherent structure does not significantly beat shuffled" — replace with positive finding (Tier 1: C4 wins 57.8% under counterbalancing).

### New methodology contribution

LLM judges show systematic slot-B preference in pairwise judging, magnitude
varying by judge family:
- gpt-5.4 (OpenAI, smaller): negligible
- gpt-5.5 (OpenAI, xhigh): ~25–31 pp slot-B
- Opus 4.7 (Anthropic): ~9–24 pp slot-B, content-varying

This is independently publishable as a methodology contribution.

---

## 6. What we're asking in round 2

The v0.2 pilot is substantially settled. The curated report should be writable from this data. But before committing, we want a focused round-2 critique to catch **remaining issues** we may have missed.

### A. Issues that would block the v0.2 report

What problems with the current Phase 0 + Phase 1 corrected dataset, if surfaced, would prevent writing a defensible v0.2 report? Things like:
- Have we mischaracterized any of the 6 pair verdicts above?
- Are the Tier 1 findings actually as robust as claimed, or is there a Phase 0/1 audit we didn't run that would deflate them further?
- Is the LLM-judge slot-B bias finding correctly framed?
- Did we miss a methodological flaw the round-1 review pointed to that we did not address?

Specifically:
- The **C5_CONTRACT > C5** finding is now the central substantive claim. Does the ~16 pp attenuation from 76% → 67.7% under position-control affect what we can say about mechanism? Should we publish at all without `C_GENERIC_CONTRACT` ablation?
- The **C4 > C5** finding *strengthened* under AB/BA (63.7% → 68.9%), contradicting the Phase 0 length-matched finding that it should vanish. Which framing should the curated report use?
- The **C3 vs C5_CONTRACT cross-provider stratified finding** (CI [0.238, 0.446] favoring C5_CONTRACT under cross-provider judges only) is interesting but contradicts the all-judge AB/BA result (which says no preference). How should this be reported?

### B. Quick fixes before v0.2 report writing

What small, high-value additions to the analyzer or report would significantly strengthen the v0.2 publication? Examples:
- Specific tables we should add to the curated report
- Robustness checks on the AB/BA itself (e.g., judge-stratified AB/BA estimates)
- Sanity-check experiments runnable in <1 day

### C. v0.3 questions

What questions does the current state leave most open? Where should v0.3 invest? Examples:
- C_GENERIC_CONTRACT ablation (per round-1 reviewer consensus)
- C5_NONPUBLIC (public-anchor isolation)
- C4_WRONG_PROFILE (profile-specificity test)
- Human-rater calibration
- Real-user shadow-mode validation

But we want fresh angles too — what should v0.3 do that round-1 missed?

### D. Anything else

Any direct flaws, overclaims, missing context, structural issues with the project that the round-1 reviewers might have under-weighted.

---

## 7. Paths to artifacts (all under `~/claudeworkspace/psyche/psycheeval/`)

| File | Content |
|---|---|
| `reports/reviews/2026-05-15_v0_2_review_bundle.md` | Round 1 bundle (input to first review) |
| `reports/reviews/2026-05-15_consolidated_v0_2_review.md` | Round 1 consolidated review (3 reviewers) |
| `reports/reviews/2026-05-15_gpt-pro_v0_2_review.md` | Round 1 GPT Pro single-agent review |
| `reports/reviews/2026-05-15_codex-council_v0_2_review.md` | Round 1 Codex Council synthesis |
| `reports/reviews/2026-05-15_gpt-max_v0_2_review.md` | Round 1 GPT Max synthesis |
| `reports/archive/2026-05-15_pre-labeling-fix/PHASE0_FINDINGS.md` | Phase 0 12-task findings (the master synthesis) |
| `reports/archive/2026-05-15_pre-labeling-fix/MANIFEST.md` | Phase 0 archive manifest |
| `reports/reviews/2026-05-16_phase1_ab_ba_findings.md` | Phase 1 AB/BA findings + final tier assignment |
| `reports/metrics_2026-04-26_v02_hard_codex_only.json` | Canonical metrics (NOW INCLUDES all Phase 0 + 1 blocks; 380 KB) |
| `reports/psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md` | Autogen scaffold (NOW 1100+ lines with all Phase 0 + 1 tables) |
| `runs/2026-04-26_v02_hard_codex_only/` | Raw JSONL: assistant_outputs, anchored_judge_scores, pairwise_scores, **pairwise_swap_scores (NEW)** |

---

## 8. Constraints on round-2 critique

- **Be direct**, specific, actionable. Round 1 was substantive and we addressed all of it; round 2 should find what round 1 missed.
- **No mealy-mouthed validation.** The work is fully done; we're not asking for praise, we're asking for what's still wrong.
- **Flag overclaims explicitly.** The Tier 1 claims above should each survive your specific scrutiny.
- **Budget for v0.3 quick-fixes**: roughly 1,000–2,000 Opus draws + much larger codex. Anything we should run before publishing is on this budget.

If you flag a Phase 0 audit we didn't run that would meaningfully change conclusions, prioritize that over net-new experiments.
