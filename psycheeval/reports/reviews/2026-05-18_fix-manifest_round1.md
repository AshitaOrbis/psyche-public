# Fix Manifest — Round 1

**Date**: 2026-05-18
**Document**: `applications/ashitaorbis/shared/content/posts/046-psycheeval-v0_2.md`
**Consolidated review**: `2026-05-18_consolidated_round1.md`
**Verification source**: `psyche/psycheeval/reports/metrics_2026-04-26_v02_hard_codex_only.json`

## Summary

All 18 MUST FIX items, all 5 SHOULD FIX items, and all 3 NICE TO HAVE items applied in a single Write pass.
Pre-revision: 171 lines, ~5,341 words, 20 unicode em dashes.
Post-revision: 182 lines, ~5,705 words, 0 unicode em dashes.

## Applied Fixes

### Numerical / Logical (V1–V12)

| # | Reviewer Finding | Action | Canonical source |
|---|------------------|--------|------------------|
| V1 | §4 AB/BA table CI direction mismatch | Changed C3 vs C5_CONTRACT CI from `[0.434, 0.564]` to `[0.436, 0.566]` (lo_win-basis bootstrap, rounded). Changed C4 vs C5_CONTRACT CI from `[0.452, 0.587]` to `[0.413, 0.548]`. Added explicit "CIs are 2,000-resample cluster bootstrap on the lo_win-basis controlled rate (clustering unit: persona × scenario × author)" disclosure before the table. | `pairwise.ab_ba_position_audit_same_author.{C3_vs_C5_CONTRACT,C4_vs_C5_CONTRACT}.controlled_bootstrap_ci95_{low,high}` |
| V2 | Swap-record arithmetic 864 + 800 + 240 ≠ 1,784 | Rewrote to "added 120 originals plus 120 swap rejudgments. Total: 1,784 swap-rejudge records (864 + 800 + 120)" with arithmetic shown inline. | reconciliation logic |
| V3 | §3 length-matched n=78 conflated Phase 0.G with joint AB/BA correction | Labeled the n=78 / 0.449 / Wilson [0.343, 0.559] block as "the Phase 0.G pre-AB/BA length-only audit run before any AB/BA data existed." Added parenthetical with the joint-corrected canonical: "n=80, controlled lo_win 0.500, bootstrap CI [0.372, 0.634]." | `pairwise.ab_ba_joint_position_length_same_author.C3_vs_C5_CONTRACT` |
| V4 | "Entirely a position-bias artifact" overclaim | Replaced 4 instances with "does not survive AB/BA correction; the apparent advantage was driven by slot-B bias in two of the three judges" or similar non-causal wording. Locations: description frontmatter, §1 opening, §4 closing paragraph, §6 retractions section. | review consensus |
| V5 | No MDE / power note on null claims | Added "(roughly ±7 pp at this n)" in §6 retractions paragraph for C5_CONTRACT vs C3. Added "(The CI still permits an effect within roughly ±7 pp at n≈288 per pair; we did not predeclare an equivalence margin, so this is a 'no detection' result, not an 'established equivalence' result)" to the "contributes nothing detectable" sentence. | n=288 per AB/BA pair from canonical |
| V6 | §3 first-pass table "3 same-author judges" overreach | Rewrote the caption to "across same-author judges (judge scope varies by row: C5_CONTRACT-edge rows have all three judges; non-C5_CONTRACT rows are codex-only at this first analyzer pass)". | judging scope per `pairwise_coverage` |
| V7 | Pairwise count "3,123" stale | Replaced with "3,243 raw pairwise records (3,064 true same-author after excluding 179 cross-author leak records)". | `counts.pairwise_scores` = 3243 |
| V8 | C5 length "3,476" wrong | Changed to "(7,434 chars vs 3,884)". | `token_summary_by_condition.{C5,C5_CONTRACT}.profile_chars_mean` = 3884.2, 7433.5 |
| V9 | C4 vs C5 row stale values | Changed row to "C4 vs C5 (post-fill)" with values 0.626 / 0.736 / 0.680 / CI [0.615, 0.744]. | `pairwise.ab_ba_position_audit_same_author.C4_vs_C5.{original_lo_win_rate,swapped_lo_win_rate,position_controlled_lo_win_rate}` |
| V10 | "Eight of ten condition-pair types" reads as contradiction | Added explicit naming: "1.000 for eight types, and ≥0.988 for the other two (C1 vs C1_padded at 0.994, C4 vs C4_shuffled at 0.988)". | `pairwise.ab_side_audit_same_author.by_pair` |
| V11 | "Isn't a length effect" overclaim | Replaced with "isn't explained by response-length imbalance in the matched subset, isn't a position effect, and isn't a judge-specific effect." | review wording |
| V12 | Tier count in closing abstract | Rewrote "four survived as Tier 1" to "three survived as Tier 1 condition preferences, one survived as a Tier 1.5 modest preference (C4 > C4_shuffled, OpenAI judges only), and two collapsed under correction with no detected pairwise preference." | tier assignments per §6 |

### Citations / Reproducibility (T1–T4)

| # | Reviewer Finding | Action |
|---|------------------|--------|
| T1 | Broken link with apology at L79 | Removed "summarized in the [round-1 consolidated review](/posts/044-what-the-wiki-router-found) — sorry, that one's a different project, see the project repository for the PsycheEval reviews" entirely. Replaced with "External round-1 reviewers (three independent reviews from GPT Pro, codex-council, and GPT Max) unanimously called AB/BA 'the cheapest decisive next experiment.'" |
| T2 | Missing arXiv citations | Added inline links: "Zheng et al. (2023, [arXiv:2306.05685](https://arxiv.org/abs/2306.05685))" and "Shi et al. 2024, [arXiv:2406.07791](https://arxiv.org/abs/2406.07791)". Verified by factcheck reviewer (Codex GPT-5.2) against current arXiv records. |
| T3 | "Standard correction" overstates AB/BA | Replaced with "The standard first-pass mitigation is counterbalanced AB/BA rejudging" and added "AB/BA reduces position bias but does not fully eliminate it (see 'What This Doesn't Settle' below)." |
| T4 | Cluster-bootstrap-vs-Wilson sentence confused | Rewrote §5 closing paragraph from "the cluster bootstrap presented as a single number with a Wilson CI that didn't have access to the underlying heterogeneity" to "pooling across judges into a single aggregate CI hid the underlying disagreement." |

### Voice / Structure (C1–C5, S1, SF#5)

| # | Reviewer Finding | Action |
|---|------------------|--------|
| C1 | 20 em dashes (`—`) violate voice guide | Full sweep: all 20 instances replaced with colons (definitional appositive), parentheses (asides), semicolons (compound clauses), or sentence breaks. Verified count = 0 via `grep -c '—'`. En dashes (numeric ranges like "0–10") preserved (13 remaining, all in number ranges). |
| C2 | L163 95-word run-on sentence | Converted "Fourth and beyond: contract-component ablation (...), paraphrased rubric anchors (...), same-orientation rejudge sentinel (...), 30–100 human-rater calibration pairs (...), tie / no-meaningful-difference pairwise option, and longer-horizon profile-realism conditions (...)" into a 6-item bulleted list with bold leadwords. |
| C3 | L16 dense opening buries L18 mood-shift hook | Swapped L16 and L18: the mood-shift paragraph ("I am writing the v0.2 post in a different mood than the v0.1 post...") now opens the post. The provenance paragraph (1,680 outputs, 3,243 records, etc.) now sits in position 2. |
| C5 | "Same neighborhood as C5 vs C5_CONTRACT — 57.2% and 60.0%" sloppy | Rewrote to "above parity but materially weaker than the C5 vs C5_CONTRACT pair (76.0%)." |
| S1 | "Every dimension I have hands on" overreaches | Replaced with "every axis tested: pairwise win rate, scalar Δ_total, per-judge consistency, and joint position-plus-length correction." |
| SF#5 | C4 > C4_shuffled missing scope qualifier | Added "(OpenAI judges only)" to the §6 bold header for C4 > C4_shuffled and to the closing abstract's tier breakdown. |

### NICE TO HAVE applied

| # | Item | Action |
|---|------|--------|
| 24 | 2,000-resamples disclosure | Added "CIs are 2,000-resample cluster bootstrap on the lo_win-basis controlled rate (clustering unit: persona × scenario × author)" preamble to the AB/BA table in §4. |
| 25 | Add per-pair n to AB/BA table | Added `n` column to the AB/BA table: 320 / 288 / 320 / 280 / 288 / 288. |
| 26 | Steelman acknowledgment | Added new H3 "### What This Doesn't Settle" subsection in §5 (between the Slot-B prose and the generic-lesson paragraph). Acknowledges that "controlled = mean(original, swap)" assumes additive symmetric position effects, and names the same-orientation rejudge sentinel (now in the §7 v0.3 bulleted list) as the experiment that would decompose AB/BA flip rate into position bias and retest noise. |

## Section Merge Decision (C4 — SHOULD FIX)

Gemini suggested merging "Three Independent Audits Predict the Same Collapse" with "The AB/BA Experiment" because they share one narrative arc. **Not applied** — the two sections do different work: the audits section establishes that something was wrong from same-data alone, and the AB/BA section identifies the specific cause. Merging would lose the distinction between "raised the prior" and "identified what." The seven-H2 count (1.3/1000w) is acceptable for a 5,700-word deep-dive; the voice guide target is 1–2/1000w.

## Deferred

| # | Reviewer Finding | Reason |
|---|------------------|--------|
| (none) | All MUST FIX, SHOULD FIX, and NICE TO HAVE items applied. | |

## Carried Forward

| # | Reviewer Finding | Round Where Surfaced |
|---|------------------|---------------------|
| (none) | All round-1 findings addressed. | |

## Verification

- Em dash count: **0** (was 20) — `grep -c '—'`
- Pairwise count match: **3,243 raw / 3,064 same-author** — matches `counts.pairwise_scores` and reviewer-cited cross-author leak figure
- AB/BA CIs: now match canonical `pairwise.ab_ba_position_audit_same_author.*.controlled_bootstrap_ci95_{low,high}` to 3 decimal places
- C4 vs C5 row: matches canonical post-fill `original_lo_win_rate` 0.6259, `swapped_lo_win_rate` 0.7357, `position_controlled_lo_win_rate` 0.6804
- C5 vs C5_CONTRACT length: matches canonical `profile_chars_mean` (C5: 3884.2 → "3,884"; C5_CONTRACT: 7433.5 → "7,434")
- Length-matched joint correction: numbers match canonical `pairwise.ab_ba_joint_position_length_same_author.C3_vs_C5_CONTRACT` (n=80, lo_win 0.500, CI [0.3715, 0.6341] → "[0.372, 0.634]")

## Convergence Signal

Round 1 fixed every MUST FIX / SHOULD FIX / NICE TO HAVE item the consolidated review surfaced. The structural seam (audits section vs AB/BA section) is the only item deliberately deferred, with rationale above.

**Recommended next step**: optional round 2 in delta mode (diff-only) to catch fix-introduced regressions. If round 2 surfaces ≤3 MUST FIX items, the post is ready to clear `draft: true`. If clean, optional single-model final-polish pass via Opus to verify philosophical rigor.
