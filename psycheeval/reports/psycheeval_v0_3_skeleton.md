# PsycheEval v0.3 — full-pilot tri-model report (SKELETON)

**Status**: SKELETON. Pre-staged 2026-05-19 while v0.3 generation/judging is still in flight.
Fill in `[PLACEHOLDER]` markers once `metrics_<v0.3-tag>.json` exists. All numbers must come from the canonical metrics JSON, not be hand-entered.

**Tag**: `2026-05-19_v03` (preliminary). Final tag may differ depending on Opus-fill timing.
**Supersedes**: v0.2 hard-pilot report (`psycheeval_v0_2_micro_pilot_2026-04-26_v02_hard_codex_only.md`).
**Date**: `<COMPLETION_DATE>`

---

## 1. TL;DR

v0.3 was designed to answer four mechanism questions and one methodology question that v0.2 surfaced. The mechanism questions were locked at Phase -1 (2026-05-19):

1. **Does profile *specificity* matter, or just *contract structure*?** Tested by `C_GENERIC_CONTRACT` vs `C3`/`C4`.
2. **Does profile *matching* matter, or any well-structured contract?** Tested by `C4_WRONG_PROFILE` vs `C3`/`C4`.
3. **Is the source-packet effect about public-anchor narrative or just narrative form?** Tested by `C5_NONPUBLIC` vs `C5` (within-PI-persona, same trait pattern).
4. **What inside the C5_CONTRACT package is doing the work — contract presence, ordering, anti-mimicry, or length?** Tested by the L1/L2/L3 ablation ladder.

The methodology question:

5. **How much of the AB/BA flip rate is position bias vs retest noise?** Tested by the same-orientation rejudge sentinel (D1), plus the paraphrased-anchor sentinel (D2) and tie/equipoise ternary sentinel (D4).

**v0.3 answers** (fill in once analyzed):

1. **C_GENERIC vs C3/C4**: [PLACEHOLDER]
2. **C4_WRONG vs C3/C4**: [PLACEHOLDER]
3. **C5_NONPUBLIC vs C5 (PI-matched)**: [PLACEHOLDER]
4. **L0 → L1 → L2 → L3 → L4 ablation ladder**: [PLACEHOLDER — marginal contribution per step]
5. **Same-orientation flip rate / retest noise floor**: [PLACEHOLDER — corpus-scope mean; per-judge spread]

**Methodology improvements over v0.2:**
- AB/BA judging is mandatory by default (no retrofit)
- Same-orientation rejudge sentinel decomposes AB/BA flip rate
- Paraphrased rubric anchors test scalar anchor-sensitivity
- Ternary tie/equipoise sentinel surfaces forced-choice artifact rates
- Reward-hacking diagnostics control for output length, profile-references, hedging, lexical overlap with source packet
- Cluster-bootstrap CIs throughout (carried from v0.2)
- Phase -1 design-lock predeclared all primary contrasts, expansion triggers, failure criteria, and MCID before generation

**What v0.3 is not.** Still a synthetic-personas methodology pilot. The Phase 9 shadow-mode design doc (`docs/shadow_mode_validation_v04_design.md`) names what construct-validity bridge would look like; v0.4 executes it.

---

## 2. What changed from v0.2

| Axis | v0.2 | v0.3 |
|------|------|------|
| Authors | gpt-5.4, gpt-5.5-xhigh, Opus 4.7 | same (no change) |
| Judges | same | same |
| Scenarios | 80 | same |
| Personas | 8 (4 PI, 4 PS) | same |
| Conditions | 8 | 8 + 7 new = **15** |
| New T1 conditions | — | C_GENERIC_CONTRACT, C4_WRONG_PROFILE, C5_NONPUBLIC, C5_NONPUBLIC_CONTRACT |
| New T2 ablation ladder | — | L1, L2, L3 (between C5 = L0 and C5_CONTRACT = L4) |
| AB/BA | retrofitted in Phase 1 | mandatory from start (`--ab-ba-mandatory`) |
| Sentinels | none | same-orientation (D1), paraphrased anchor (D2), ternary (D4) |
| Analyzer blocks | 17 | + 4 (D1, D2, D3, D4) = **21** |
| Pre-declared pair manifest | partial | full (Phase -1.1: 16 T1 + 12 T2 pair types) |
| Failure criteria | implicit | 8 predeclared (Phase -1.11) |
| D5 equivalence-margin TOST | proposed | **SKIPPED** (power-confirmed undecidable; -1.8) |

---

## 3. Corpus and methods

### 3.1 Corpus counts
| Element | v0.2 | v0.3 |
|---------|------|------|
| Personas | 8 | same |
| Scenarios | 80 | same |
| Authors | 3 | same |
| Conditions | 8 | 15 |
| Assistant outputs (new in v0.3) | 1,680 | [PLACEHOLDER] (~1,080 new for 7 conditions) |
| Anchored scalar scores | 3,949 | [PLACEHOLDER] |
| Same-author pairwise | 3,243 raw / 3,064 same-author | [PLACEHOLDER] |
| AB/BA swap records | 1,784 | [PLACEHOLDER] |
| D1 same-orientation sample | — | [PLACEHOLDER] (10% of pairwise) |
| D2 paraphrased anchor sample | — | [PLACEHOLDER] (15% of scalar) |
| D4 ternary sample | — | [PLACEHOLDER] (10% of pairwise) |

### 3.2 v0.3 condition descriptions

| Code | Description | Persona scope |
|------|-------------|---------------|
| C_GENERIC_CONTRACT | Structurally-C3-like, generic language, length-matched to C4 | all 8 |
| C4_WRONG_PROFILE | C4 with opposite-trait persona's profile substituted | all 8 |
| C5_NONPUBLIC | PI-matched fictional biographical narrative (no public anchor) | PI 4 |
| C5_NONPUBLIC_CONTRACT | C5_NONPUBLIC + anti-mimicry contract wrapper | PI 4 |
| L1 | C5 + minimal contract, packet-first, no anti-mimicry, length-matched to C5 | PI 4 |
| L2 | L1 + anti-mimicry rules | PI 4 |
| L3 | L2 with contract-first ordering (reversed) | PI 4 |
| (L0 = C5, L4 = C5_CONTRACT) | inherited from v0.2 | PI 4 |

### 3.3 Judges + judging
3 judges: `gpt-5.4`, `gpt-5.5-xhigh`, `opus` (Anthropic 4.7).
Anchored 0–10 rubric (06b) for primary scalar. Paraphrased anchored rubric (06c) for D2 sentinel. Forced-choice pairwise (07) for primary. Ternary tie/equipoise (07b) for D4 sentinel.

### 3.4 Pair manifest (Phase -1.1, predeclared)

T1 (16 pair types): C_GENERIC × {C0, C3, C4, C5}; C4_WRONG × {C0, C3, C4, C5}; C5_NONPUBLIC × {C5, C5_CONTRACT, C3, C4}; C5_NONPUBLIC_CONTRACT × {C5_NONPUBLIC, C5_CONTRACT, C3, C4}.

T2 (12 pair types): L0=C5 ↔ L1 ↔ L2 ↔ L3 ↔ L4=C5_CONTRACT consecutive; L1/L2/L3 vs C5 and C5_CONTRACT anchors; L1 vs C3, L2 vs C3, L3 vs C4.

---

## 4. Findings — Tier 1 substantive (v0.3)

[PLACEHOLDER]

### 4.1 Personalization probes
- C_GENERIC vs C3: [PLACEHOLDER — does profile specificity matter?]
- C_GENERIC vs C4: [PLACEHOLDER]
- C4_WRONG vs C3/C4: [PLACEHOLDER — does profile matching matter?]

### 4.2 Public-anchor isolation
- C5_NONPUBLIC vs C5 (PI-matched): [PLACEHOLDER — public-anchor effect when trait pattern held constant]
- C5_NONPUBLIC_CONTRACT vs C5_CONTRACT: [PLACEHOLDER — public-anchor effect with contract held constant]

### 4.3 C5_CONTRACT mechanism ablation ladder
- L0 → L1: marginal contribution of **contract presence**
- L1 → L2: marginal contribution of **anti-mimicry rules**
- L2 → L3: marginal contribution of **contract-first ordering**
- L3 → L4: marginal contribution of **expanded length**

Success criterion per v0.3 plan §8 is "screen which component additions visibly contribute" — NOT "decompose dominant mechanism." Single-path; interactions not identified.

### 4.4 Sentinel reads
- Same-orientation flip rate (D1): [PLACEHOLDER]
- Paraphrased anchor consistency (D2): [PLACEHOLDER]
- Reward-hacking diagnostics regression (D3): [PLACEHOLDER]
- Ternary tie rate (D4): [PLACEHOLDER]

---

## 5. Findings — Tier 1.5 / Tier 2 retractions

[PLACEHOLDER]

If any v0.3 headline collapses under triangulation, document the retraction; carry forward v0.2's retraction-as-success pattern.

---

## 6. Inherited v0.2 findings (carried over)

- C0 dominated by every profile condition: [PLACEHOLDER]
- C4 > C1_padded: [PLACEHOLDER] (v0.2 had 62.3% controlled)
- C4 > C5: [PLACEHOLDER] (v0.2 had 68.0% judge-unanimous)
- C5_CONTRACT > C5: [PLACEHOLDER] (v0.2 had 67.7% judge-unanimous; v0.3 ablation ladder unpacks)
- C4 > C4_shuffled (Tier 1.5): [PLACEHOLDER] (v0.2 had 57.8%)
- C5_CONTRACT vs C3 / C4 (retracted in v0.2): D5 SKIPPED per Phase -1.8

---

## 7. Methodology contribution

[PLACEHOLDER]

Expected wording: "v0.2's methodology contribution was per-judge slot-B preference quantification. v0.3 extends this with:
- Same-orientation rejudge sentinel decomposing AB/BA flip rate
- Paraphrased rubric anchors testing anchor-sensitivity
- Tie-aware reinterpretation showing forced-choice equipoise rates
- Reward-hacking diagnostics regression
- Pre-declared pair manifest at Phase -1 eliminating post-hoc expansion confound"

Numbers to fill:
- Same-orientation flip rate vs AB/BA flip rate
- Paraphrased anchor Spearman ρ per judge
- Tie rate distribution
- Reward-hacking regression coefficients

---

## 8. Failure-trigger checks (Phase -1.11)

| # | Trigger | Status | Effect if fires |
|---|---------|--------|-----------------|
| 1 | Paraphrased anchor ≥0.5 SD mean shift OR rank changes | [TBD] | All scalar claims downgraded |
| 2 | Tie rate > 25% on C5_CONTRACT-edge pair | [TBD] | Pair claim downgraded |
| 3 | Author-rater agreement < 60% | [TBD] | LLM-judge claims flagged |
| 4 | C4_WRONG wins against C_GENERIC > 55% | [TBD] | Personalization claim downgraded |
| 5 | C5_NONPUBLIC indistinguishable from C5 (effect < 5pp) | [TBD] | Public-anchor downgraded |
| 6 | Same-orientation flip ≥ AB/BA flip on >50% pairs | [TBD] | AB/BA decomposition descriptive only |
| 7 | Opus vs OpenAI divergence > 0.15 on T1 pair | [TBD] | Judge-unanimous wording dropped |
| 8 | Reward-hacking: >50% of preference from length+profile-refs | [TBD] | Mechanism requires covariate model |

If ≥3 fire: open report with "what didn't work" section.

---

## 9. Limitations

- Single-rater human calibration (D2 plan): n=1 ≠ inter-rater reliability
- Same-orientation sentinel at 10% may have limited per-pair power for failure trigger #6
- T2 ladder is single-path; interaction effects not identified
- C5_NONPUBLIC packets authored by human; style differences from public-anchor packets could be confounding
- Shadow-mode validation deferred to v0.4

---

## 10. v0.4 priorities

1. **Shadow-mode validation** at Psyche public results page per `docs/shadow_mode_validation_v04_design.md`
2. **≥2-rater human calibration** for inter-rater reliability
3. **Long-horizon profile-realism conditions** (stale, contradictory, user-edited, compressed)
4. **Multi-turn interaction tests**
5. **Adversarial profile robustness** (GP4 / R13)
6. **Equivalence-margin TOST** (revisit with shadow-mode MCID calibration)

---

## 11. Closing

[PLACEHOLDER]

---

## Appendices

A. Claim ledger [PLACEHOLDER auto-generated]
B. Cluster-bootstrap CI methodology (see v0.2 appendix)
C. Full per-pair AB/BA tables [PLACEHOLDER]
D. Review provenance:
   - v0.3 plan: `docs/v0_3_plan.md`
   - Phase -1 design-lock: `docs/v0_3_phase_minus_1_design_lock.md`
   - 3-reviewer consolidated review: `reports/reviews/2026-05-18_consolidated_v0_3_plan_review.md`
   - Phase 9 design doc: `docs/shadow_mode_validation_v04_design.md`

---

## Sign-off checklist

- [ ] All `[PLACEHOLDER]` markers replaced from canonical metrics JSON
- [ ] Failure-trigger checks performed (§8)
- [ ] Limitations section reviewed
- [ ] Claim ledger appended
- [ ] /publication-review 3-reviewer panel run
- [ ] HTML export to the reading device
