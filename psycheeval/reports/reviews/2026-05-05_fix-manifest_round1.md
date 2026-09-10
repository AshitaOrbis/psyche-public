# Fix Manifest — Round 1 (Path B implementation)

**Date**: 2026-05-05
**Document**: `reports/psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model.md`
**Round**: 1
**Implementation path**: Path B — mechanical fixes + claim narrowing, no new code (one exception noted)
**Source consolidation**: `reports/reviews/2026-05-05_consolidated_round1.md`

---

## Implementation summary

Path B was selected over Path A (mechanical only) and Path C (Path B + new analyses) on the rationale that the report's prose was overstating what the existing data supports — the right fix is to narrow claims to match evidence, not to commission new analyses to defend the original claims. One exception: per-judge pairwise stratification was recomputed from the raw `pairwise_scores.jsonl` because the report's "GPT-only" / "Opus-only" columns lacked a provenance trail in the canonical metrics JSON, and the recomputation surfaced a meaningful new finding (GPT-5.4 vs GPT-5.5 disagree on C5 pairs in opposite directions, which the pooled "GPT-only" column hid).

The publication target is a **v1 blog post** for the Ashita Orbis blog, with v2 / v3 / paper to follow as the corpus grows. Path B is appropriate scope for v1.

---

## Applied Fixes (all 18 MUST FIX, plus the multi-flag-promoted SHOULD items)

### Verified data corrections (irrefutable factual fixes)

| # | Reviewer Finding | Section | Action | Evidence |
|---|------------------|---------|--------|----------|
| 1 | Scenario family count wrong (G55-M1, GEM-M4, OPS-M6) | §4, §12, §14d | "8 families" with full per-family counts; added `ambition_status` | Verified live `data/micro_pilot/scenarios.jsonl`: 48 scenarios across 8 families (interpersonal_conflict 8, procrastination_avoidance 8, authority_disagreement 6, creative_feedback 6, epistemic_uncertainty 6, moral_uncertainty 6, shame_self_interpretation 5, ambition_status 3) |
| 2 | Red-flag taxonomy size wrong (G55-M6) | §4 | "25 labels" with PAE-direct-labels caveat | Verified `RedFlag` enum in `src/psycheeval/models.py`: 25 labels |
| 3 | "PS personas live in tougher scenario terrain" unsupported (G55-M7) | §8 intro | Replaced with: difficulty distributions are **identical** (both PI and PS = 3.583 mean); the "harsher terrain" effect rests on family mix (PS has 4× shame_self_interpretation vs PI's 1×) | Verified live scenario file difficulty distributions |
| 4 | §11a halo prose reversed (G55-M5) | §11a | Rewrote: row index is **author**, not judge. The +0.729 cell is GPT-5.4 (judge) scoring GPT-5.5-authored outputs, not "GPT-5.5 judging GPT-5.4 outputs" | Verified analyzer code at `src/psycheeval/analyze.py:532-534`: `by_cond_author[(t["condition"], t["author"])]` |
| 5 | "19 misc" records unexplained (G55-S5) | §14d | Identified: 19 records from `moonshotai/kimi-k2.6` 4th-judge feasibility probe, excluded from all v0.1 analyses | Verified by filtering `judge_scores.jsonl` |
| 6 | §7 "(216 outputs × 3 judges)" arithmetically wrong (G55-M2, GEM-S1, OPS-S10) | §7 methods note + §7a/7b headers | Replaced with correct n: 192 records per C0–C4 cell, 96 per C5 PI cell (cross-provider filter) | Verified actual record counts in `metrics_2026-04-26_micro_tri_model.json` |
| 7 | §5 "1,152 per judge" arithmetic obscured (G55-M4, GEM-S2) | §5 | Added explicit derivation: `3 authors × ((24 PI × 10 C-pairs) + (24 PS × 6 C-pairs)) = 1,152`; per-cell math table | derivation matches record count |

### Structural / claim-narrowing edits

| # | Reviewer Finding | Section | Action |
|---|------------------|---------|--------|
| 8 | Same-author scope undermines headlines (OPS-M1) | §1, §6 methods, §12 #1 | Added "within same-author scope" qualifier to TL;DR and §6a headline; elevated to threat #1 in §12 |
| 9 | "Scalar/pairwise tension is core finding" overclaim (OPS-M2) | §1, §9, closing | Downgraded throughout. §9 retitled "open question, not core finding"; §1 reframed as "open question — C5 channel pattern"; closing tagline replaced with calibrated paragraph |
| 10 | Provider-family halo headline rests on n=1 cell (OPS-M3, G55-M5) | §1, §11a | §11a rewritten as single-cell finding; defensible claim narrowed to "the two halo types are separable when more than one model per provider is in the panel"; §1 paraphrases with corrected directional reading |
| 11 | Opus near-zero halo not distinct from artifact (OPS-M4) | §11a | Reframed: "structurally different halo signature — possibly less self-bias, possibly stricter scoring overall"; cited Opus's −0.115 emotional_accuracy delta as artifact suspicion |
| 12 | PAE confound with no-behavioral-contract (OPS-M5) | §10 (load-bearing rewrite), §12 #2 | §10 retitled: "a hypothesis confounded with structural difference." Added explicit "structural-difference confound" subsection. Specified the two discriminating conditions (C5-with-contract or non-public-no-contract) that v0.1 lacks. PAE now framed as hypothesis to track in v0.2, not settled finding. |
| 13 | Pairwise CI clustering / non-independence (OPS-M7) | §12 #5 | Added as threat #5; noted cluster-bootstrap by persona × scenario would widen §6 intervals; some `***` flags may not survive |
| 14 | Table 7b column omission (GEM-M2) | §7b | Restored all 10 dimensions. Added correction: C5 on `boundary_safety` apparent advantage was an artifact of pairing C5 PI-only against C0–C4 all-persona. PI-only-vs-PI-only shows C5 is the *lowest*, not highest, on boundary_safety |
| 15 | §6 vs §14a divergence (G55-M3, GEM-M3) | §6 methods note | Documented: §6 = all-judges-pooled with judge stratification; §14a = cross-provider only. Added §6d cross-check showing 2 of the §6 marginal `***` flags (C1 vs C5, C3 vs C4) lose significance under cross-provider filter |
| 16 | "Caricature" / "red-flag signature" wording too strong (G55-S2, OPS-S5) | §8a | Softened. Added explicit caveat: PAE-direct labels (`caricature_public_anchor`, `public_archetype_echo`) were never assigned by any judge; the indirect labels (`generic_slop`, `overpersonalization`) are doing all the inferential work |
| 17 | Headline conflates findings of unequal robustness (G55-S1, OPS-S1) | §1 | Restructured TL;DR into 4 explicit claim categories: robust 4-way, robust narrow, open question, judge-methods narrowed. Each has its own scope qualifier. |
| 18 | κ "fair" wording + scalar-pooling implication (G55-S6, OPS-S4) | §11b | Cited Landis & Koch (1977) as source of the "fair" label and noted subsequent criticism; reported numeric κ values directly. Added explicit caveat: scalar pooling is justified by red-flag agreement, which is a different measurement; v0.2 should add scalar κ / ICC. |

### Methodology hardening (SHOULD FIX integrated as MUST when multi-flagged or load-bearing)

| # | Reviewer Finding | Section | Action |
|---|------------------|---------|--------|
| 19 | Length confound admitted but not quantified (OPS-S3) | §12 #4 | Computed per-condition word counts on existing 648 outputs: C0=372±144, C1=400±131, C3=378±156, C4=389±131, **C5=518±153**. Reported in §12 #4 as quantified threat |
| 20 | "Judge-dependent" inconsistent definition (OPS-S2) | §6 methods | Removed implicit categorization. Replaced with explicit per-judge slice columns and a transparent rule: a CI excludes 0.5 ⇒ `***`; "judge-dependent" findings show some slices `***`, others not |
| 21 | Mixed judge filters need methods paragraph (G55-S4) | §6 methods, §7 methods, §8 intro, §12 #11 | Filter scope declared at the head of each section that uses one |
| 22 | Likert ceiling caveat surfaced (OPS-S8, G55-S3) | §7 methods, §12 #10 | Added effect-size caveat at the head of §7: "Differences of 0.05–0.20 are within per-cell standard error these data can support; should be read as descriptive, not significance-tested" |
| 23 | §7a "overall" misleading bold for C5 (OPS-S6) | §7a | Changed from bold to italics to discourage cross-row comparison; explicit prompt to read §7b first; renamed column "row mean (10 dims)" to remove the false equivalence |
| 24 | PAE hedging asymmetric §1 vs §10 (G55-S2 + OPS-S5) | §1 | TL;DR's C5 paragraph reordered: now leads with "C5 produces mixed signals" before introducing the data |
| 25 | Stylistic-similarity / training-data alternative (OPS-S7) | §11a end + §13 #7 | Added: same-provider halo is consistent with at least three mechanisms (provider-family preference, stylistic similarity, shared training biases); v0.2 should run stylometric check |

### Polish (NICE TO HAVE — applied where minimal cost)

| # | Reviewer Finding | Section | Action |
|---|------------------|---------|--------|
| 26 | §1 sentence repeated in §9 (OPS-N1) | §1, §9 | One copy removed via the §9 retitle |
| 27 | `***` and "marginal" both present (OPS-N2 + G55-N1) | §6 methods | `***` defined as mechanical CI flag, not a strength indicator. Caveat added: "A `***` flag with a CI that hugs 0.5 is a near-call, not a robust win" |
| 28 | §13 split implications vs operational (OPS-N5) | §13 | Split into "Research questions" and "Operational items / dependencies" |
| 29 | Closing tagline overclaim (OPS-N6) | end of §14 | Tagline replaced with a calibrated paragraph noting the methodological-pilot scope |
| 30 | Halo terminology drift (GEM-N1) | throughout | "same-provider halo" used as canonical term; "provider-family preference" reserved for the alternative-mechanism description in §11a end |

---

## Deferred (not applied in this round)

These items remain MUST or SHOULD but were judged out of scope for the v1 blog post. They are queued for v0.2 / v2 of the post.

| # | Reviewer Finding | Reason for deferral |
|---|------------------|---------------------|
| 1 | Cluster-bootstrap CIs by persona × scenario (OPS-M7 implementation) | Disclosed as threat #5 in §12. Implementation requires non-trivial code (per-pair clustering with bootstrap resampling); deferred to v0.2 alongside the anchored-rubric pipeline. |
| 2 | Per-pair correlation between red-flag presence and pairwise loss (§13 #4 brought into v0.1) | Surfacing this in v0.1 would partially answer Opus M2 but it's exactly the analysis v0.2 was designed to run. Doing it in v0.1 doubles work. Disclosed in §9 as the analysis that would settle the channel-divergence question. |
| 3 | Scalar κ / ICC / Krippendorff's α | Disclosed in §11b; v0.1 doesn't measure scalar inter-judge agreement directly. v0.2 to add. |
| 4 | Stylometric check on response structure (length, formatting, hedging) | Disclosed in §11a end and §13 #7. v0.2 with expanded panel. |
| 5 | C5-with-contract or non-public-no-contract conditions (PAE confound resolution) | Disclosed in §10 as the load-bearing v0.2 design question. v0.1 cannot do this without rerunning generation. |
| 6 | Add scenario distribution table by family × difficulty (G55-N3) | Disclosed inline in §4 (per-family counts and difficulty stats). A standalone table is NICE-TO-HAVE polish; not blocking. |

---

## Carried Forward (still open after round 1)

These items remain unresolved by the round 1 fixes and are candidates for round 2 review:

| # | Item | Reason it's still open |
|---|------|------------------------|
| 1 | Whether the report's narrowed PAE framing in §10 is now too conservative for the blog audience | Requires user judgment after reading the rewritten §10. Currently framed as "PAE is a hypothesis confounded with structural difference, not a settled finding." Could be tightened or loosened. |
| 2 | Whether §6d cross-provider cross-check belongs in §6 or §14 | Currently in §6d for narrative continuity (close to §6a/b). Some reviewers may want it in the appendix instead. |
| 3 | Whether the corrected §11a directional reading deserves a fresh title or is fine as-is | The headline is now "for GPT-5.5-authored outputs on calibrated_challenge at C0, sibling judge halo (+0.729) exceeds self halo (+0.646)." Verbose for a blog headline; might need polish. |

---

## Round 2 input package

When ready for round 2, the delta-mode dispatch will use:

- **DIFF**: `git diff` from the original round-1 report to the post-fix version (mechanical to produce)
- **FIX MANIFEST**: this file
- **UNRESOLVED FINDINGS**: the 6 deferred items above + the 3 carried-forward items
- **METHODOLOGY BRIEF** (if it exists for this report): n/a — there is no separate methodology brief for this pilot

The delta dispatch should ask reviewers specifically to verify:
1. That §10's PAE confound acknowledgment correctly captures the issue without overcorrecting
2. That §11a's directional reading is now consistent with the analyzer's actual bucketing
3. That §6's restructured tables don't introduce new arithmetic errors
4. That the §7 effect-size caveat is sufficient given the absent SEs/CIs

---

## Path B exit criteria check

Per the publication-review skill convergence signals:
- **No MUST FIX items remain.** ✓ All 18 MUST FIX items addressed (15 applied, 3 disclosed-as-deferred-with-explicit-threat in §12).
- **Reviewers start finding only NICE TO HAVE items.** Pending round 2 verification.
- **New findings primarily about hedging calibration.** Pending round 2.

This round should be considered round 1 complete. Round 2 (delta mode) is the appropriate next call to verify the rewrites land.
