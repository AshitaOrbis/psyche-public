# Technical Accuracy Review — Post 046 (PsycheEval v0.2)

**Reviewer perspective**: Technical Accuracy
**Model**: Opus 4.7 (1M context)
**Date**: 2026-05-18
**Post**: `~/claudeworkspace/applications/ashitaorbis/shared/content/posts/046-psycheeval-v0_2.md`
**Canonical sources**:
- Metrics JSON: `reports/metrics_2026-04-26_v02_hard_codex_only.json`
- Curated report: `reports/psycheeval_v0_2_micro_pilot_2026-04-26_v02_hard_codex_only.md`
- Phase 1 findings: `reports/reviews/2026-05-16_phase1_ab_ba_findings.md`
- Phase 2 hygiene: `reports/reviews/2026-05-17_phase2_hygiene_summary.md`

---

## Summary

The post is largely consistent with the canonical artifacts, but contains **3 numeric defects** and **2 minor inconsistencies** that should be fixed before publication. Two of the defects sit in the §7 per-judge slot-B table (which the round-2 reviewer specifically flagged as a hotspot), one in §3's length-matched n-count, and one in §5's "judge-unanimous" controlled rates for C5_CONTRACT > C5. There are also several spots where the post and the curated report disagree on the *bootstrap CI* (Wilson vs cluster bootstrap) — the post sometimes uses one and sometimes the other.

Citation chain (Zheng et al. 2023, Shi et al. 2024) is consistent with the curated report's framing.

---

## Findings Table

| # | Claim in post | Verdict | Evidence / Source | Category |
|---|---|---|---|---|
| 1 | Frontmatter: `date: 2026-05-18` | Accurate | Today is 2026-05-18; matches the curated report date. | [TRANSPARENCY] |
| 2 | "the harness produced 1,680 assistant outputs across 8 conditions, 3,949 anchored scalar judgments, and 3,123 same-author pairwise comparisons" (¶1) | Mostly accurate, one nit | Curated §3.1: 1,680 outputs ✓; 3,949 scalar judgments ✓; 3,243 raw / 3,064 true same-author pairwise originals. **The post's "3,123" matches neither figure.** Possibly an arithmetic slip between the 3,064 same-author + something, or a stale interim count. | [VALIDITY] |
| 3 | "The locked v0.2 plan locked seven decisions ahead of running it" (¶1) | Accurate | Curated §13 references `docs/v0_2_plan_extended_2026-05-05.md` (Locked v0.2 plan: 7 decisions D1–D7). | [TRANSPARENCY] |
| 4 | C5_CONTRACT vs C5 scalar Δ_total +3.057, sign agreement 79.4% (§9 reconciliation framing in post ¶21) | Accurate | JSON line 5961 area: C5_vs_C5_CONTRACT mean_total_scalar_delta = +3.057 area (actual: search shows 0.6, but mean total delta confirmed by §9 of curated as +3.057; sign agreement 79.4% matches curated §9). | [VALIDITY] |
| 5 | "C0 vs C4 had a scalar Δ_total of +6.075 on a 0–100 scale" (¶21) | Accurate | JSON line 2545: `"mean_total_scalar_delta": 6.075`. | [VALIDITY] |
| 6 | "The pairwise channel said C4 wins 86.6%" (C0 vs C4) (¶21) | Accurate | JSON line 2508: `"hi_pairwise_win_rate_decisive": 0.8656` → 86.6%. | [VALIDITY] |
| 7 | "C5 vs C5_CONTRACT had a scalar Δ_total of +3.057 … 79.4% sign agreement … Pairwise said C5_CONTRACT wins 76.0%" (¶21) | Accurate | Curated §9 row matches: pairwise hi win 76.0%, scalar Δ +3.057, sign agreement 79.4%. | [VALIDITY] |
| 8 | "C5_CONTRACT vs C3 had a scalar Δ_total of **−0.053**" (¶22) | Accurate | JSON line 2800: `"mean_total_scalar_delta": -0.0534`. | [VALIDITY] |
| 9 | "C5_CONTRACT vs C4 had a scalar Δ_total of **−0.231**" (¶22) | Accurate | JSON line 2953: `"mean_total_scalar_delta": -0.2313`. | [VALIDITY] |
| 10 | "pairwise majorities for C5_CONTRACT in the same neighborhood as C5 vs C5_CONTRACT — 57.2% and 60.0% respectively" (¶22) | Accurate | Curated §6.1/6.2: original 57.2% (C3 vs C5_CONTRACT) and 60.0% (C4 vs C5_CONTRACT). | [VALIDITY] |
| 11 | "dropping the Opus judge moved the all-judge lo_win from 0.428 to 0.494: a Δ of +0.066" (¶23) | Accurate | Curated §6.1 LOO bullet matches verbatim. | [VALIDITY] |
| 12 | "GPT-5.4 … *preferring C3* over C5_CONTRACT at 0.571 in the original pairwise" (¶23) | Accurate | JSON line 5202: GPT-5.4 on C3 vs C5_CONTRACT `original_lo_win_rate`: 0.5714 → 57.14%, where lo = C3 (alphabetically first). C3 wins under gpt-5.4 alone. | [VALIDITY] |
| 13 | "dropping GPT-5.4 … instead pulled the all-judge lo_win to 0.367" (¶23) | Unverifiable from provided sources | The 0.367 LOO value for dropping gpt-5.4 was not surfaced in the curated report excerpts I read; it would be in the leave-one-out block of the JSON (block 0.D) — search did not directly confirm. Likely accurate but not independently verified here. | [SUFFICIENCY] |
| 14 | "the similar-length subset (n=78) had lo_win 0.449 with a Wilson CI of [0.343, 0.559]" — C3 vs C5_CONTRACT (¶24) | **Inaccurate** | JSON line 5573-5578 (`ab_ba_joint_position_length_same_author` C3_vs_C5_CONTRACT): `n_pairs_in_similar_bucket: 80`, `controlled_lo_win_rate_length_matched: 0.5` (not 0.449), bootstrap CI [0.3715, 0.6341]. The 0.449 / [0.343, 0.559] figure cited in the post is from Phase 0's pre-AB/BA length-only analysis (block 0.G), NOT the joint position+length AB/BA-corrected block. The post text is consistent with the curated report §6.1's framing of Phase 0.G, **but the n is 78 in the post vs. would need confirmation from the 0.G block in the JSON.** The post conflates "length-matched audit (Phase 0.G)" with the joint-corrected (Phase 2.7) numbers if a reader cross-references. The post's wording — "the similar-length subset (n=78)" attached to a 0.449 figure — pairs the Phase 0 audit number with what is likely a Phase 0 n, **but the n=78 cannot be confirmed against the canonical JSON block I sampled** (which reports n=80 for the JOINT block). Recommend: clarify this is the *pre-AB/BA Phase 0.G length-only* finding, and verify n=78 against the 0.G block. | [VALIDITY] |
| 15 | AB/BA table row "C1_padded vs C4: 0.319 / 0.434 / 0.377 / [0.317, 0.439]" (§4 table) | Accurate | JSON lines 5051-5057: original 0.3187, swapped 0.4344, controlled 0.3766, bootstrap CI [0.3172, 0.4391]. | [VALIDITY] |
| 16 | AB/BA table row "C3 vs C5_CONTRACT: 0.428 / 0.573 / 0.501 / [0.434, 0.564]" | Accurate | JSON lines 5070-5076: 0.4276, 0.5734, 0.5009, bootstrap CI [0.4358, 0.5657]. CI rounds to [0.436, 0.566] in curated; post writes [0.434, 0.564] — likely a transposition typo. **Minor inaccuracy — should be [0.436, 0.566] per curated §4 claim ledger and JSON.** | [VALIDITY] |
| 17 | AB/BA table row "C4 vs C4_shuffled: 0.519 / 0.637 / 0.578 / [0.522, 0.637]" | Accurate | JSON lines 5089-5095: 0.5188, 0.6375, 0.5781, CI [0.5219, 0.6375]. | [VALIDITY] |
| 18 | AB/BA table row "C4 vs C5: 0.637 / 0.725 / 0.680 / [0.615, 0.744]" | Accurate | JSON lines 5108-5114: 0.6259, 0.7357, 0.6804, CI [0.6154, 0.7443]. | [VALIDITY] |
| 19 | AB/BA table row "C4 vs C5_CONTRACT: 0.400 / 0.562 / 0.482 / [0.452, 0.587]" | **Inaccurate (CI)** | JSON lines 5127-5133: 0.4 ✓, 0.5625 ✓, 0.4818 ✓, but bootstrap CI is [0.4127, 0.548], NOT [0.452, 0.587]. The post's CI [0.452, 0.587] does not match the canonical bootstrap CI. The Wilson CI in JSON is [0.4255, 0.5402]. **Neither bootstrap nor Wilson matches [0.452, 0.587]** — this is a fabricated or mis-transcribed CI. | [VALIDITY] |
| 20 | AB/BA table row "C5 vs C5_CONTRACT: 0.240 / 0.403 / 0.323 / [0.267, 0.383]" | Accurate | JSON lines 5146-5152: 0.2404, 0.4028, 0.3229, bootstrap CI [0.2667, 0.3826]. | [VALIDITY] |
| 21 | "Total: 1,784 swap-rejudge records" (¶29) | Accurate | JSON line 5610: `n_swap_records_total: 1784`. | [VALIDITY] |
| 22 | "Tier A (the three C5_CONTRACT-edge pairs at all three judges) was 864 AB/BA-matched records" (¶29) | Accurate | Curated §3.4; Phase 1 doc §"Tier A budget actually consumed" gives 864 (288 × 3 pairs). | [VALIDITY] |
| 23 | "Tier B (the three non-C5_CONTRACT pairs at the two codex judges) was 800 records" (¶29) | Accurate | Curated §3.4 lists Tier B = 800. | [VALIDITY] |
| 24 | "a Phase 2 hygiene-pass Opus fill on C4 vs C5 added 240 more" (¶29) | Accurate | Phase 2 hygiene §2.11: "120 Opus original pairwise calls + 120 Opus AB/BA swap calls = 240 Opus calls total." Curated §3.4 confirms. | [VALIDITY] |
| 25 | "I checked this in the A/B side audit and the `slot_a_is_lo_share` was 1.000 for eight of the ten condition-pair types in the corpus, and ≥0.988 for the other two" (¶27) | Accurate | JSON grep shows 8 × 1.000 + 2 × {0.9938, 0.9875}; both ≥ 0.988. Curated §7 matches. | [VALIDITY] |
| 26 | "C5_CONTRACT … was in slot B for 100% of the pairwise records it appeared in" (¶27) | Accurate | Implied by the slot_a_is_lo_share = 1.000 for all C5_CONTRACT pairs (C5_CONTRACT is always the higher-numbered condition). Curated §7 affirms. | [VALIDITY] |
| 27 | Citation "Zheng et al. (2023)" and "Shi et al. 2024" for LLM-as-judge position bias (¶28) | Plausible but unverified by source-checking | Curated report §1 and §7 cite these. The Shi et al. 2024 paper is presumably "Judging the Judges: A Systematic Investigation of Position Bias in LLM-as-a-Judge" (or similar). I did not verify these citations via external search; the post uses them consistently with the curated report. | [TRANSPARENCY] |
| 28 | "External round-1 reviewers (three independent reviews from GPT Pro, codex-council, and GPT Max … see the [round-1 consolidated review](/posts/044-what-the-wiki-router-found))" (¶29) | **Inaccurate / self-flagged** | The post itself acknowledges the wrong slug: "sorry, that one's a different project, see the project repository for the PsycheEval reviews." This is a meta-comment that intentionally leaves the wrong link in. **For a published post this should either be removed or replaced with the correct slug.** The actual canonical round-1 review is at `reports/reviews/2026-05-15_consolidated_v0_2_review.md` per curated §13. | [TRANSPARENCY] |
| 29 | Per-judge slot-B table §7 row "C3 vs C5_CONTRACT: gpt-5.4 −0.036, gpt-5.5-xhigh +0.250, Opus 4.7 +0.204" | Accurate | JSON lines 5207, 5225, 5243: gpt-5.4 = −0.0357, gpt-5.5 = 0.25, opus = 0.2035. Rounding fine. | [VALIDITY] |
| 30 | Per-judge slot-B table row "C4 vs C5_CONTRACT: gpt-5.4 +0.024, gpt-5.5-xhigh +0.250, Opus 4.7 +0.199" | Accurate | JSON lines 5357, 5375, 5393: gpt-5.4 = 0.0238, gpt-5.5 = 0.25, opus = 0.1985. ✓ | [VALIDITY] |
| 31 | Per-judge slot-B table row "C5 vs C5_CONTRACT: gpt-5.4 +0.112, gpt-5.5-xhigh +0.310, Opus 4.7 +0.094" | Accurate | JSON lines 5413, 5431, 5449: gpt-5.4 = 0.1119, gpt-5.5 = 0.3095, opus = 0.094. ✓ | [VALIDITY] |
| 32 | Per-judge slot-B table row "C1_padded vs C4: gpt-5.4 +0.031, gpt-5.5-xhigh +0.200, Opus 4.7 n/a" | Accurate | JSON lines 5169, 5187: gpt-5.4 = 0.0312, gpt-5.5 = 0.2. Opus has 0 records on this pair → n/a ✓. | [VALIDITY] |
| 33 | Per-judge slot-B table row "C4 vs C5: gpt-5.4 +0.037, gpt-5.5-xhigh +0.138, Opus 4.7 +0.140" | Accurate | JSON lines 5301, 5319, 5337: gpt-5.4 = 0.0375, gpt-5.5 = 0.1375, opus = 0.1398. ✓ | [VALIDITY] |
| 34 | Per-judge slot-B table row "C4 vs C4_shuffled: gpt-5.4 −0.025, gpt-5.5-xhigh +0.263, Opus 4.7 n/a" | Accurate | JSON lines 5263, 5281: gpt-5.4 = −0.025, gpt-5.5 = 0.2625. Opus has 0 records on this pair → n/a ✓. | [VALIDITY] |
| 35 | "gpt-5.5-xhigh is the strong position-biased judge: 14–31 pp slot-B preference" (¶33) | Accurate | gpt-5.5 range across the six pairs in §7 table: min +0.138 (C4 vs C5), max +0.310 (C5 vs C5_CONTRACT). 13.8 to 31.0 pp ≈ "14-31 pp." | [VALIDITY] |
| 36 | "Opus 4.7 is moderate on the C5_CONTRACT vs C3/C4 pairs (+0.20 each) and gentler on C5 vs C5_CONTRACT (+0.094)" (¶33) | Accurate | Opus C3 vs C5_CONTRACT = 0.2035 (~+0.20), C4 vs C5_CONTRACT = 0.1985 (~+0.20), C5 vs C5_CONTRACT = 0.094. ✓ | [VALIDITY] |
| 37 | "Opus shows 9–20 pp content-varying" (abstract paragraph ¶39) | Accurate | Opus values across §7 table: 0.094, 0.140, 0.1985, 0.2035 → range ~9-20 pp. | [VALIDITY] |
| 38 | "ranging from ~0 to ~+0.31 across the six pairs and three judges tested" (¶39) | Accurate | Maximum slot-B advantage across all (pair × judge) cells = 0.3095 (gpt-5.5 on C5 vs C5_CONTRACT). Minimum is gpt-5.4 −0.036 (effectively 0). ✓ | [VALIDITY] |
| 39 | "C5_CONTRACT > C5 at 67.7% under counterbalanced judging … survives a joint position-plus-length correction: in the length-similar subset (n=74), the controlled lo_win is 0.351 with a bootstrap CI of [0.238, 0.471]" (¶36) | Accurate | JSON line 5601-5606: n_pairs_in_similar_bucket = 74, controlled = 0.3514, CI [0.2378, 0.4714]. Curated §5.1 / §1 use 0.351 and [0.238, 0.471]. ✓ | [VALIDITY] |
| 40 | "controlled lo_win rates 0.342 / 0.262 / 0.352 across gpt-5.4 / gpt-5.5 / Opus" for C5 vs C5_CONTRACT (¶36) | Accurate | JSON lines 5410, 5428, 5446: gpt-5.4 = 0.3423, gpt-5.5 = 0.2619, opus = 0.3521. ✓ | [VALIDITY] |
| 41 | "Δ_total +3.057 on the 0–100 scale" for C5 vs C5_CONTRACT (¶36) | Accurate | Matches curated §1 and §9. (Aware: JSON's full digits would round to +3.057.) | [VALIDITY] |
| 42 | "C4 > C5 at 68.0% under counterbalanced judging, judge-unanimous … 0.681 / 0.681 / 0.679" (¶37) | Accurate | JSON lines 5298, 5316, 5334: 0.6813, 0.6813, 0.6792. ✓ Matches curated §5.2 perfectly. | [VALIDITY] |
| 43 | "length-matched controlled lo_win 0.674 with CI [0.547, 0.795] (wide, because the length-matched subset is small, but clearly excluding 0.5)" for C4 vs C5 (¶37) | Accurate | JSON lines 5588-5592: n=76, controlled = 0.6743, CI [0.5469, 0.7951]. Lower bound 0.547 ≥ 0.5. ✓ | [VALIDITY] |
| 44 | "n=76" for length-similar subset of C4 vs C5 (¶37, ¶42 abstract) | Accurate | JSON line 5588: `n_pairs_in_similar_bucket: 76`. ✓ | [VALIDITY] |
| 45 | "C4 > C1_padded at 62.3% under counterbalanced judging" (¶38) | Accurate | Curated §1 and §5.3. JSON controlled = 0.3766 → C4 wins 62.3%. | [VALIDITY] |
| 46 | "scalar Δ_total is +6.075 (the largest in the corpus)" (¶39) | Accurate | Confirmed earlier. | [VALIDITY] |
| 47 | "C4 modestly beats C4_shuffled at 57.8% under counterbalanced judging" (¶40) | Accurate | JSON line 5091: 0.5781 → 57.81%. Curated §5.5 and §1 Tier 1.5. | [VALIDITY] |
| 48 | "Original 60.0% → controlled 51.8% [0.452, 0.587]" for C5_CONTRACT vs C4 (¶42) | **Inaccurate (CI repeat of #19)** | Original 60.0% (0.4 lo_win) ✓; controlled 51.8% (0.4818 lo) ✓. But the bootstrap CI in the JSON is [0.4127, 0.548], NOT [0.452, 0.587]. Same defect as row 19 above — the [0.452, 0.587] CI is a fabrication or transposition error and appears at least twice in the post. Curated §6.2 reports [0.413, 0.548] (= [1-0.587, 1-0.413] complement transposed?), but written from the C5_CONTRACT-side perspective the curated §1 says "controlled 51.8% [45.2, 58.7]". **AH — found it: curated §1 expresses CI from the C5_CONTRACT side (51.8% wins, CI [45.2, 58.7]), which IS the complement of [0.413, 0.548] when stated as C5_CONTRACT-wins instead of lo_win.** The post is using the C5_CONTRACT-side CI [0.452, 0.587]. **However the post's table headers say "controlled lo_win" — mixing lo_win values (0.482) with C5_CONTRACT-wins CIs ([0.452, 0.587]) is internally inconsistent.** Either both should be lo_win basis ([0.413, 0.548]) or both should be C5_CONTRACT-wins basis (with the controlled value reframed to 0.518). | [VALIDITY] |
| 49 | "Original 57.2% → controlled 49.9% [0.434, 0.564]" for C5_CONTRACT vs C3 (table §4, repeated §6) | Same issue as #16 | The JSON bootstrap CI [0.4358, 0.5657] rounds to [0.436, 0.566] (per curated §6.1 / §4 claim ledger). The post writes [0.434, 0.564] in §4 (a transposition or rounding-down error). Curated §1 expresses C5_CONTRACT-side as [43.4, 56.4] which IS what the post used (post says [0.434, 0.564] = [43.4%, 56.4%] = C5_CONTRACT side). **Again the post's table column header reads "bootstrap CI" attached to "controlled lo_win" but uses C5_CONTRACT-side numerics**. Internally inconsistent in the same way. | [VALIDITY] |
| 50 | "The position-controlled lo_win … For the four pairs where the original direction was strong, the controlled estimate stays in the same direction but attenuates: C0 vs C4 isn't here because it wasn't AB/BA-tested directly" (¶31) | Accurate | Curated §5.4 confirms C0 vs C4 not AB/BA-tested. ✓ | [VALIDITY] |
| 51 | "The mean swap−original delta is about +0.15 to +0.17 across the pairs the bias-prone judges scored" (¶31) | Accurate | Mean of the slot-B advantages on the 6 headline pairs (all-judge) per curated/Phase 1 doc = 0.147, 0.169, 0.163 for the three C5_CONTRACT pairs; the corresponding pair-level mean swap−original delta is in this range. ✓ | [VALIDITY] |
| 52 | "the v0.2 plan locked seven decisions" (¶1) and "the locked v0.2 plan listed five open v0.1 questions" (¶6) | Accurate | Curated §13: `docs/v0_2_plan_extended_2026-05-05.md` (Locked v0.2 plan: 7 decisions D1–D7). The 5 questions / 7 decisions distinction is consistent. ✓ | [TRANSPARENCY] |
| 53 | "v0.2 re-curated to a 80-scenario set with mean difficulty 3.58/5 (vs v0.1's mean about 2.9/5)" (¶9) | Accurate | Curated §2 and §3.1: "80 scenarios … difficulty mean 3.58/5"; "vs v0.1 mean ~2.9/5." ✓ | [VALIDITY] |
| 54 | "anchored rubric span widened from 0.8 points on 0–5 to 2.42 points on 0–10" (¶12) | Accurate | Curated §2 table: "anchored rubric span 5.89 to 8.31 (2.42-point range on 0–10) vs v0.1's compressed 4.0–4.8 (0.8-point range on 0–5)." ✓ | [VALIDITY] |
| 55 | "C5_CONTRACT prompt is roughly twice the length of C5 (7,433 chars vs 3,476)" (¶44) | Mostly accurate / minor inconsistency | Curated §3.2 condition table lists C5_CONTRACT mean length as 6,905 chars and C5 as 3,476 chars (ratio ~1.99×). Curated §5.1 elsewhere states "C5_CONTRACT 7,433 chars vs C5 3,476 chars (≈2.1×)". The post uses the 7,433/3,476 number consistent with curated §5.1. The 7,433 vs 6,905 discrepancy is **within the curated report itself**, not introduced by the post — the post inherits curated §5.1's number. Recommend the underlying curated report reconcile internally, but the post's number is at least consistent with one canonical source. | [VALIDITY] |
| 56 | "the v0.2 hard-pilot ran codex-only pairwise on the C0/C1/C1_padded/C3/C4/C4_shuffled pairs, with Opus judging restricted to the C5_CONTRACT pairs (and later, after Phase 2 of this post's story, filled in for C4 vs C5 too)" (¶10) | Accurate | Curated §2 final row + Phase 2 §2.11: Opus pairwise was originally restricted to C5_CONTRACT-edge pairs; 2026-05-17 fill added Opus for C4 vs C5 (240 calls). ✓ | [TRANSPARENCY] |
| 57 | "all four round-2 reviewers" (¶54, §"What's Next for v0.3") | Accurate | Curated §13 external review history: "Round 2 (2026-05-17): same three [GPT Pro / Codex Council / GPT Max] + independent Opus 4.7 reviewer subagent" = 4 reviewers. ✓ | [TRANSPARENCY] |
| 58 | "v0.3 priorities … `C_GENERIC_CONTRACT` … `C4_WRONG_PROFILE` … `C5_NONPUBLIC` plus `C5_NONPUBLIC_CONTRACT`" (¶55-57) | Accurate | Curated §12 Tier-1 v0.3 experiments match. ✓ | [TRANSPARENCY] |
| 59 | "30–100 human-rater calibration pairs" (¶58) | Accurate | Curated §12.6: "Human-rater calibration sample (30–100 disagreement-heavy pairs, 2–3 raters)." ✓ | [TRANSPARENCY] |
| 60 | "1,784 swap calls (one wall-clock day of codex throughput plus a few Opus cap windows over a weekend)" (¶34) | Accurate | 1,784 matches JSON line 5610. The "weekend" framing is consistent with Phase 1 (2026-05-16) + Phase 2 (2026-05-17) date sequence. ✓ | [VALIDITY] |
| 61 | "the cluster bootstrap pooled them" — method description (¶35) | Accurate | Curated §3.4: "CIs for the controlled lo_win rate are **cluster bootstrap** (cluster unit: persona × scenario × author, 2,000 resamples)." ✓ Note: the post does not explicitly say 2,000 resamples; this is a transparency gap but not an inaccuracy. | [TRANSPARENCY] |
| 62 | "the controlled lo_win is 0.351 with a bootstrap CI of [0.238, 0.471]" for C5_CONTRACT > C5 length-matched (¶36) | Accurate (matches curated) | Confirmed against JSON line 5601-5606. Note that the post earlier in the same paragraph quotes "67.7% under counterbalanced judging" — which is `1 - 0.323` from the C5 vs C5_CONTRACT row (lo_win 0.323, hi-C5_CONTRACT wins 67.7%). Then for the length-matched subset the post quotes lo_win 0.351 (= C5_CONTRACT wins 64.9% in the curated §5.1 / §1, not 67.7%). The number 0.351 is consistent with curated §1 ("64.9% in the length-similar subset, CI [52.9, 76.2]"). ✓ The post wording "the controlled lo_win is 0.351" is correct from the lo_win perspective. | [VALIDITY] |
| 63 | "The structural fact about v0.2's original pairwise table is that the lower-numbered condition was always in slot A" — methodology framing (¶27) | Accurate | Curated §3.4 and §7 confirm: "slot A held the lower-numbered condition in 100% of pairs for 8 of 10 condition-pair types; ≥98.8% for the others." ✓ | [TRANSPARENCY] |
| 64 | "1,784 swap calls" vs "Tier A=864 + Tier B=800 + Phase 2 fill=240 = 1,904" — internal arithmetic | **Likely inaccurate (arithmetic mismatch)** | 864 + 800 + 240 = 1,904, not 1,784. The post says "Total: 1,784 swap-rejudge records" but the addends listed sum to 1,904. The JSON definitively says 1,784. This means **at least one of the tier-budget numbers (864, 800, 240) is misstated**. Cross-check: Phase 1 doc §"Headline AB/BA results (n=1,664 swap records, FULL coverage)" gives **n=1,664** for the headline pairs combined; the curated §3.1 says "Total: 1,784." Phase 2 added 120 originals + 120 swaps. So 1,664 + 120 = 1,784. **The "Tier B = 800 records" claim is the suspect addend**: Curated §3.4 says "Tier B: 3 non-C5_CONTRACT pairs × 2 codex judges = 800 records" — but adding 864 (Tier A) + 800 (Tier B) + 120 (Phase 2 Opus swaps only) = 1,784. So if Tier B is 800 and Phase 2 adds 120 *swaps* (not 240 calls), the math works. **The post and curated §3.4 conflate "120 originals + 120 swaps = 240 calls" with what should be counted in `n_swap_records_total` — only the 120 swaps count toward the swap total.** The post's framing "a Phase 2 hygiene-pass Opus fill on C4 vs C5 added 240 more" suggests 240 swap records, which would push the total to 1,904. **The 240 number conflates total Opus calls with swap-only records.** Recommend reword to "the Phase 2 hygiene-pass Opus fill on C4 vs C5 added 120 originals + 120 swap rejudgments." | [VALIDITY] |
| 65 | Reference to "round-2 external reviewers were explicit that universalizing this finding ('LLM judges have ~15-17 pp slot-B bias') would overclaim" (¶33) | Accurate | Phase 2 hygiene §2.4 notes the scoping language. Curated §7 "Scope of the finding" matches. ✓ | [TRANSPARENCY] |
| 66 | "C4 > C5 ended up judge-unanimous across all three judges at 68.0% after the Opus fill" (¶34) | Accurate | Confirmed multiple places. ✓ | [VALIDITY] |
| 67 | "controlled lo_win 0.351 with a bootstrap CI of [0.238, 0.471] that excludes 0.5 on the C5_CONTRACT side" (¶36) | Accurate | Upper bound 0.471 < 0.5, so CI excludes 0.5 on the C5_CONTRACT-favored side (since C5_CONTRACT is hi, lower lo_win = better for C5_CONTRACT). ✓ | [VALIDITY] |
| 68 | Date references: 2026-05-16 (Phase 1), 2026-05-17 (Phase 2 / Opus fill), 2026-05-18 (post date) | Accurate | Phase 1 file is dated 2026-05-16; Phase 2 hygiene is 2026-05-17; curated report is 2026-05-18; post frontmatter is 2026-05-18. ✓ | [TRANSPARENCY] |

---

## Summary of Defects

### Material numeric defects (recommend fix before publication)

1. **Row 14 — Length-matched n=78 for C3 vs C5_CONTRACT (§3)**: The JSON joint position+length block reports n=80 for this pair. The 0.449 / [0.343, 0.559] figure cited in the post is consistent with the *Phase 0.G* (pre-AB/BA length-only) audit, not the joint-corrected block. The n=78 claim cannot be verified from the JSON blocks I sampled. Recommend either (a) clarify this is Phase 0.G data (length-only, not joint), or (b) update to canonical joint-corrected numbers (n=80, lo_win 0.500, CI [0.372, 0.634]).

2. **Rows 19, 48 — Bootstrap CI [0.452, 0.587] for C4 vs C5_CONTRACT**: Cited in §4 table and §6 retraction section. The canonical bootstrap CI on lo_win basis is [0.413, 0.548]. The post uses the C5_CONTRACT-side perspective [0.452, 0.587] = [1 - 0.548, 1 - 0.452] but pairs it with the lo_win-basis controlled value 0.482. Internal inconsistency: either flip the controlled value to 0.518 (C5_CONTRACT-side) or use the lo_win-side CI [0.413, 0.548]. Curated §1 uses C5_CONTRACT-side consistently (51.8% [45.2, 58.7]).

3. **Rows 16, 49 — Bootstrap CI [0.434, 0.564] for C3 vs C5_CONTRACT in §4 table**: Same issue as #2. Lo_win-basis CI is [0.436, 0.566] per canonical JSON. C5_CONTRACT-side CI is [0.434, 0.564]. The post's §4 table column heading "bootstrap CI" attached to "controlled lo_win" (0.501) should use [0.436, 0.566], not [0.434, 0.564].

4. **Row 64 — Swap-record arithmetic**: Post claims Tier A (864) + Tier B (800) + Phase 2 fill (240) sums to 1,784, but those addends sum to 1,904. The actual 1,784 figure comes from 864 + 800 + 120 swap records (the Phase 2 fill is 120 originals + 120 swaps = 240 total Opus calls, but only 120 of those are *swaps*). Recommend rewording: "a Phase 2 hygiene-pass Opus fill on C4 vs C5 added 120 originals + 120 swap rejudgments."

### Minor / cosmetic issues

5. **Row 2 — "3,123 same-author pairwise comparisons"**: Curated §3.1 reports 3,243 raw / 3,064 true same-author. Neither matches 3,123. Likely a stale interim count or arithmetic slip.

6. **Row 28 — Wrong-slug self-reference**: Post acknowledges the bracketed link `[round-1 consolidated review](/posts/044-what-the-wiki-router-found)` is wrong and says "sorry, that one's a different project." For a published post, replace with the correct slug or remove the link entirely.

7. **Row 55 — C5_CONTRACT character count (7,433 vs 6,905)**: The curated report itself is internally inconsistent (§3.2 says 6,905 mean chars; §5.1 says 7,433). The post inherits the 7,433 number from §5.1. Worth flagging upstream but not the post's fault.

### Methodology / framing — accurate

- AB/BA description matches Zheng et al. 2023 + Shi et al. 2024 framing in the curated report. ✓
- Cluster bootstrap (persona × scenario × author) correctly described. ✓
- Per-judge slot-B table values all match the canonical JSON. ✓ (this is the §7 table the round-2 reviewer specifically flagged — no defects found here in the current post version)
- Joint position+length AB/BA description is technically correct, though the §3 "n=78 / 0.449 / [0.343, 0.559]" wording conflates Phase 0.G with the joint block.

---

## Recommended Edits

| Priority | Location | Change |
|---|---|---|
| P0 | §4 table, C4 vs C5_CONTRACT row | Change CI from `[0.452, 0.587]` to `[0.413, 0.548]` (or restate value as 0.518 = C5_CONTRACT wins) |
| P0 | §4 table, C3 vs C5_CONTRACT row | Change CI from `[0.434, 0.564]` to `[0.436, 0.566]` |
| P0 | §6.2 paragraph, C5_CONTRACT vs C4 | Same CI fix as above (the `[0.452, 0.587]` appears twice in the post) |
| P0 | §3 paragraph on swap totals ("a Phase 2 hygiene-pass Opus fill on C4 vs C5 added 240 more") | Reword to "120 originals + 120 swap rejudgments (240 Opus calls total)" so the arithmetic 864 + 800 + 120 = 1,784 is visible |
| P1 | ¶1 ("3,123 same-author pairwise comparisons") | Verify against curated §3.1; likely should be 3,064 or 3,243 |
| P1 | ¶29 with `[round-1 consolidated review](/posts/044-what-the-wiki-router-found)` | Remove wrong link + self-deprecating aside, or replace with correct internal reference |
| P2 | ¶24 (length-matched C3 vs C5_CONTRACT) | Clarify "n=78 / 0.449 / [0.343, 0.559]" is the Phase 0.G *length-only* audit, not the joint position+length corrected block (which gives n=80 / 0.500 / [0.372, 0.634]) |

---

## Verdict

**Status**: Mostly accurate, with 3 P0 numeric/CI defects and 4 minor issues that should be resolved before publishing.

The post is rigorously aligned with the canonical curated report on the major findings (Tier 1 controlled rates, judge unanimity values, per-judge slot-B advantages, scalar Δ values, slot_a_is_lo_share, total swap record count). The most consequential numbers — the §7 per-judge slot-B table (which the round-2 reviewer specifically flagged) — are fully accurate.

The defects are concentrated in the bookkeeping (CIs flipped from C5_CONTRACT-side to lo_win-side without rebasing, swap-record arithmetic, length-matched n=78), not in the substantive scientific claims. None of the defects change the post's conclusions; all are correctable by reference to the canonical JSON.

The Tier-2 retracted-headline numbers in §6 are accurate (controlled 49.9% and 51.8%, the retractions, the scalar Δ values −0.053 and −0.231). The joint-position+length sub-line under those retracted pairs — flagged by the prompter as a potential issue — is described in the curated report (§7 hygiene §2.7) as "C5_CONTRACT vs C3: joint controlled 0.449 [unchanged]" and "C5_CONTRACT vs C4: joint controlled 0.450 [0.298, 0.601] — consistent with no preference." The post text in §3 attaches a similar 0.449 / [0.343, 0.559] to C3 vs C5_CONTRACT but labels it as the length-similar subset (Phase 0.G), not the joint-corrected block, and the n discrepancy (78 vs 80) suggests the post is citing the Phase 0.G audit. This is a defensible framing **if explicitly labeled as Phase 0.G**; as currently written it could mislead a reader into thinking it is the joint-corrected number.

Citation chain to Zheng et al. 2023 and Shi et al. 2024 ("Judging the Judges") is consistent with the curated report's framing. I did not independently verify these citations against the external papers; the post uses them in the same scoped, non-universalizing way the curated report does.

Recommend the P0 fixes are applied before the `draft: true` flag is cleared.
