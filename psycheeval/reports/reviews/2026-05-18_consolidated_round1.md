# Consolidated Round 1 Review — Post 046 (PsycheEval v0.2)

**Date**: 2026-05-18
**Document**: `applications/ashitaorbis/shared/content/posts/046-psycheeval-v0_2.md` (171 lines, ~5,341 words, `draft: true`)
**Scope**: Cross-skill consolidation of `/writing-review` (5 perspectives) + `/publication-review` (3 reviewers) = **8 reviewer outputs**

---

## Reviewer Roster

| Skill | Perspective | Model | Verdict | Raw file |
|-------|------------|-------|---------|----------|
| writing-review | critic | Opus 4.7 (1M) | 4 dims Strong, 1 Needs Work (voice — em dashes), 2 Adequate | `2026-05-18_writing-review-046-critic.md` |
| writing-review | reader | Sonnet 4.6 | Worth the length; recommend moving "different mood" paragraph to position 1 | `2026-05-18_writing-review-046-reader.md` |
| writing-review | tone | Haiku 4.5 | **6.5/7** voice match (em dashes the lone fail) | `2026-05-18_writing-review-046-tone.md` |
| writing-review | technical | Codex (GPT-5.5) | 3 P0 numeric defects + 4 minor; §7 slot-B table verified clean | `2026-05-18_writing-review-046-technical.md` |
| writing-review | factcheck | Codex (GPT-5.2) | PASS WITH CAVEATS; Zheng/Shi verified; "standard correction" overstates generality | `2026-05-18_writing-review-046-factcheck.md` |
| publication-review | gpt55 | GPT-5.5 (xhigh) via Codex MCP | 11 MUST / 5 SHOULD / 2 NTH | `2026-05-18_gpt55_round1.md` |
| publication-review | gemini31 | Gemini 3.1 Pro | 4 MUST / 4 SHOULD / 1 NTH | `2026-05-18_gemini31_round1.md` |
| publication-review | opus46 | Opus 4.6 | Needs revision; "entirely artifact" overclaim + no MDE the deepest issues | `2026-05-18_opus46_round1.md` |

---

## Cross-Reviewer Consensus Map

ReviewBench category × reviewer matrix for findings flagged by 2+ reviewers. Findings flagged by 3+ reviewers are **promoted one tier** per skill convention.

### `[VALIDITY]` — Numerical / Logical Consistency (the heaviest cluster)

| # | Finding | technical | gpt55 | gemini31 | opus46 | critic | Promoted Tier |
|---|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| V1 | **AB/BA table CI direction mismatch** for C3 vs C5_CONTRACT and C4 vs C5_CONTRACT (CI stated from C5_CONTRACT-win side, table column is lo_win) | ✓ P0 #1 | ✓ #6 | ✓ #2 | — | — | **MUST FIX** |
| V2 | **Swap-record arithmetic** 864 + 800 + 240 ≠ 1,784 (Opus fill = 120 originals + 120 swaps) | ✓ P0 #2 | ✓ #4 | ✓ #3 | — | — | **MUST FIX** |
| V3 | **Length-matched n=78 conflates Phase 0.G pre-AB/BA with joint correction** (canonical joint is n=80, lo_win 0.500, CI [0.372, 0.634]) | ✓ P0 #3 | — | ✓ #4 | — | — | **MUST FIX** |
| V4 | **"Entirely a position-bias artifact" overclaim** — canonical wording is "no detected preference"; CI still allows small effects | — | implicit in #8 | — | ✓ top finding | — | **MUST FIX** |
| V5 | **"Source packet contributes essentially nothing on top" — no MDE / power analysis** to support null | — | ✓ #8 | — | ✓ top finding | — | **MUST FIX** |
| V6 | **"3 same-author judges" overreach** in §3 first-pass table — non-C5_CONTRACT rows are codex-only | — | ✓ #5 | — | — | — | MUST FIX (single but specific) |
| V7 | **Pairwise count 3,123 stale** (canonical 3,243 raw / 3,064 same-author) | ✓ #4 | ✓ #1 | — | — | — | **MUST FIX** |
| V8 | **C5 length 7,433 vs 3,476** — canonical C5 chars_mean is ~3,884 | ✓ #6 | ✓ #11 | — | — | — | **MUST FIX** |
| V9 | **C4 vs C5 stale row values** in AB/BA table if including Opus fill | — | ✓ #7 | — | — | — | MUST FIX (single but checks against canonical) |
| V10 | **"Slot_a_is_lo_share for eight of ten" — table only shows 8** (internal contradiction) | — | — | ✓ #1 | — | — | MUST FIX (single but clear contradiction) |
| V11 | **"Isn't a length effect" overclaim** — controls response-length, not prompt/profile length | — | ✓ #9 | — | — | — | MUST FIX (single but precise) |
| V12 | **Tier count in closing abstract** — "four Tier 1" should be 3 Tier 1 + 1 Tier 1.5 | — | ✓ #10 | — | — | — | MUST FIX |

### `[TRANSPARENCY]` — Citations / Reproducibility

| # | Finding | technical | gpt55 | gemini31 | opus46 | critic | factcheck | Promoted Tier |
|---|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| T1 | **Broken link with apology** on L79 (`/posts/044-what-the-wiki-router-found` + "sorry, that one's a different project") | ✓ #5 | ✓ #2 | ✓ #7 | ✓ flagged | ✓ F7 | — | **MUST FIX** |
| T2 | **Missing external citations** — Zheng 2023 needs arXiv:2306.05685, Shi 2024 needs arXiv:2406.07791 | — | ✓ #3 | — | — | — | verified targets | **MUST FIX** |
| T3 | **"Standard correction" overstates AB/BA** — should be "first-pass mitigation" per Shi et al. | — | ✓ SF#1 | — | — | — | ✓ flagged | **MUST FIX** (cross-skill) |
| T4 | **Cluster bootstrap vs Wilson CI sentence confused** — uses both methods names for what is really pooling judges hiding heterogeneity | — | ✓ SF#3 | — | — | — | — | SHOULD FIX |
| T5 | **Missing 2,000-resamples disclosure** for cluster bootstrap method | ✓ minor | — | — | — | — | — | NICE TO HAVE |
| T6 | **No per-pair n in AB/BA table** (n=320/288/etc.) | — | ✓ NTH #2 | — | — | — | — | NICE TO HAVE |

### `[CLARITY]` — Voice, Structure, Sentence-Level

| # | Finding | critic | tone | reader | gemini31 | gpt55 | technical | Promoted Tier |
|---|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| C1 | **20 em dashes** — voice-guide #1 red flag, author baseline effectively 0 | ✓ F1 #1 top | ✓ lone fail | — | ✓ #5 | ✓ NTH#1 | — | **MUST FIX** (4 reviewers) |
| C2 | **L163 95-word run-on** sentence (3.4× author baseline 28.4w) | ✓ F7 | — | — | ✓ #6 | — | — | **MUST FIX** |
| C3 | **L16 dense opening** buries the L18 mood-shift hook | ✓ F5 | — | ✓ recommended swap | ✓ #9 | — | — | **MUST FIX** |
| C4 | **Section transitions** — "Three Audits" + "AB/BA Experiment" share one arc; 7 H2 in 5,300w is upper bound | ✓ F7 | — | — | ✓ #8 | — | — | SHOULD FIX |
| C5 | **"Same neighborhood as C5 vs C5_CONTRACT — 57.2% and 60.0%"** is numerically sloppy (C5 vs C5_CONTRACT was 76.0%) | — | — | — | — | ✓ SF#2 | — | SHOULD FIX |

### `[SUFFICIENCY]` — Evidence Depth

| # | Finding | gpt55 | opus46 | Promoted Tier |
|---|---------|:---:|:---:|:---:|
| S1 | **C4 > C5 "every dimension I have hands on"** overreaches — supports pairwise, scalar-total, per-judge, joint length-position but not "every dimension" | ✓ SF#4 | — | SHOULD FIX |

### `[CONTRIBUTION]` — Originality

| # | Finding | critic | opus46 | Net |
|---|---------|:---:|:---:|:---:|
| O1 | The audit-pipeline-as-headline reframing is the post's genuinely novel claim, distinct from prior position-bias literature (cited correctly) | ✓ F3 Strong | implicit in steelman | **STRENGTH** |
| O2 | Per-judge slot-B quantification on tri-model corpus is corpus-scoped novelty; self-restraint on universalizing is rhetorically right | ✓ F3 Strong | — | **STRENGTH** |
| O3 | L171 closing aphorism subversion ("pipelines that don't retract aren't catching their headlines") is the post's single best landing | ✓ F6 Strong | — | **STRENGTH** |

---

## STEELMAN — Where the post is weakest (from opus46)

> The "controlled lo_win = mean of original and swap" is itself a contestable measurement that assumes additive symmetric position effects orthogonal to condition signal. The post's own v0.3 list (L163) names the same-orientation rejudge sentinel as the experiment that would decompose AB/BA flip rate into position bias and retest noise — meaning the post leans on a number that the post itself agrees is not yet decomposed.

This is the deepest weakness a hostile reviewer would attack. The retraction framing assumes AB/BA-controlled is the "true" rate, but a future same-orientation rejudge could show that what we're calling position bias has a retest-noise component too. The post should at minimum acknowledge this — preferably in the §7 methodology contribution section.

---

## Final Tiered Action List

### MUST FIX (15 items — 4 promoted from multi-reviewer consensus)

**Numerical / Logical (must verify against canonical metrics before publishing):**

1. **V1: CI direction in §4 table for C3 and C4 vs C5_CONTRACT rows.** Either flip the controlled values to C5_CONTRACT-win basis to match the existing CIs, or replace CIs with the lo_win-basis values (C3 row [0.436, 0.566]; C4 row [0.413, 0.548]).
2. **V2: Swap-record arithmetic.** Change "Opus fill added 240 more" to "Opus fill added 120 originals + 120 swap rejudgments" so 864 + 800 + 120 = 1,784 reconciles.
3. **V3: §3 length-matched audit clarification.** Either label "(Phase 0.G pre-AB/BA length-only audit)" or replace with the canonical joint-corrected n=80 / lo_win 0.500 / CI [0.372, 0.634].
4. **V4: "Entirely a position-bias artifact" → softer wording.** Change to "no detected pairwise preference under AB/BA correction; CI still permits small effects in either direction." Apply at L18, ~L96, ~L143.
5. **V5: Add MDE / power note** for the null-result claims (V4 + L141 "source packet contributes essentially nothing"). The 288-record AB/BA pairs have an MDE of roughly ±7pp — a true 53% C5_CONTRACT advantage would be invisible. Acknowledge this explicitly.
6. **V6: §3 first-pass table "across 3 same-author judges" overreach.** Add per-row scope or rewrite the caption to "across same-author judges (judge scope varies by row; see report §X for per-row coverage)."
7. **V7: Pairwise count.** "3,123" → "3,243 raw pairwise records (3,064 true same-author after excluding 179 cross-author leaks)."
8. **V8: C5 length number.** "7,433 chars vs 3,476" → verify against canonical: C5 profile_chars_mean is ~3,884, not 3,476. Either correct or define the alternate length basis being used.
9. **V9: C4 vs C5 row in AB/BA table.** Confirm whether row values include the Opus fill. Canonical post-fill: original 0.6259, swapped 0.7357, controlled 0.6804.
10. **V10: "Eight of ten condition-pair types" pair-type count.** Reconcile against the table — either list all ten types explicitly, or rewrite to "eight of the eight AB/BA-tested pair types (and ≥0.988 across the broader corpus)."
11. **V11: "Isn't a length effect" overclaim.** Rewrite to "not explained by response-length imbalance in the matched subset" — the joint correction holds response-length constant, not prompt/profile length, and the next paragraph admits C5_CONTRACT is roughly 2× the C5 prompt length.
12. **V12: Tier count in closing abstract.** "four survived as Tier 1 condition preferences" → "three Tier 1 plus one Tier 1.5 modest preference (C4 > C4_shuffled) survived; two collapsed."

**Citations / Reproducibility:**

13. **T1: Cut the broken link + apology at L79.** Either remove the link entirely, replace with the correct PsycheEval review artifact path (`reports/reviews/2026-05-15_consolidated_v0_2_review.md`), or strip to "summarized in the round-1 consolidated review (see project repository)." The apology phrase itself is publication-blocking.
14. **T2: Add arXiv links to Zheng/Shi citations.** Zheng et al. (2023): arXiv:2306.05685. Shi et al. (2024): arXiv:2406.07791.
15. **T3: "Standard correction" → "standard first-pass mitigation."** AB/BA reduces position bias; it doesn't fully debias. Per Shi et al.

**Voice (4-reviewer consensus on em dashes):**

16. **C1: Em-dash sweep.** Replace 20 unicode `—` with colons (definitional appositive), parentheses (asides), semicolons (compound clauses), or sentence breaks. Mechanical, ~30 minutes. The critic and tone reviewer both flagged this as the single highest-leverage edit.
17. **C2: L163 95-word run-on.** Break "Fourth and beyond: contract-component ablation (packet-first ordering, anti-mimicry on/off, facts-only packet, length-matched C5_CONTRACT_SHORT), paraphrased rubric anchors..." into a bulleted list or short sentences.
18. **C3: L16 opening density.** Either compress L16 to 3 sentences or swap the order with L18 so the mood-shift / retraction declaration hooks first.

### SHOULD FIX (5 items)

19. **T4: Cluster-bootstrap-vs-Wilson sentence.** Rewrite to "the pooled cluster bootstrap hid judge heterogeneity by averaging across judges into a single interval that didn't reflect the underlying disagreement."
20. **C4: Consider merging "Three Independent Audits" and "The AB/BA Experiment" sections.** They share one narrative arc; the H2 boundary breaks continuity.
21. **C5: "Same neighborhood as C5 vs C5_CONTRACT — 57.2% and 60.0%"** — C5 vs C5_CONTRACT was 76.0%. Rewrite to "above parity but materially weaker than the C5 vs C5_CONTRACT pair."
22. **S1: "Behavioral contract beats source-packet-without-contract on every dimension I have hands on"** — replace "every dimension" with the actual axes (pairwise, scalar-total, per-judge, joint length-position).
23. **Add C4 vs C4_shuffled scope qualifier** — "OpenAI-judges-only" or "(gpt-5.4 + gpt-5.5 only)" — otherwise reads parallel to all-three-judge C4 vs C5.

### NICE TO HAVE (3 items)

24. **T5: Add "2,000 bootstrap resamples" disclosure** to the methodology footnote.
25. **T6: Add per-pair n column** to the AB/BA table (n=320, 288, 320, 280, 288, 288).
26. **Steelman acknowledgment:** at most one sentence in §7 noting that "controlled = mean(original, swap)" assumes additive position effects and the same-orientation rejudge sentinel (named in v0.3 list) is the experiment that would decompose AB/BA flip rate into position bias and retest noise.

---

## Convergence Signal

This is **round 1**. The MUST FIX count (15 + 3 voice = 18) is high but most items are single-sentence edits keyed to specific lines. No structural rewrites required. The argument is genuinely strong (all reviewers agree); the issues are precision and surface register.

**Estimated fix-pass time**: ~2 hours including verification against canonical metrics.

**Expected round 2**: Once the P0 numerical defects are resolved and the em-dash sweep is done, round 2 should converge to mostly SHOULD FIX / NICE TO HAVE items. The convergence target is ≤3 MUST FIX in round 2.

---

## Findings Unique to Single Reviewers (preserved here so they aren't lost during consolidation)

- **opus46**: Power-analysis / MDE absence on null claims (V5) — only Opus surfaced this explicitly; the post leans on the null to support the structural claim "contract is doing most of the work" without quantifying detection floor.
- **opus46**: Controlled-rate-as-truth assumption — the steelman section above.
- **technical**: Internal curated-report inconsistency on C5_CONTRACT char count (7,433 in this post vs 6,905 in the canonical report). Suggests the canonical report and the post drifted; verify before fixing the post.
- **gpt55**: Tier count overclaim in the closing abstract (V12) — only GPT-5.5 noticed.
- **gemini31**: "Eight of ten" pair-type contradiction (V10) — Gemini's sentence-level lens caught the internal pointer that the other reviewers missed.
- **critic**: Aphorism-subversion is underused in the middle (only L151 and L171 land it); not a defect, but a craft observation that single-reviewer surfaced.
- **reader**: Reading time is earned despite length; condition-label scaffolding (C0/C1/C3/C4/C5 abbrev) should be reintroduced early for readers who haven't seen v0.1.

---

## Next Step

The user should decide whether to:

(a) **Apply all MUST FIX items now** as a single revision pass before clearing `draft: true`. Estimated time ~2 hours. Round 2 review optional after that.
(b) **Apply only the numerical defects** (V1-V12, T1-T2) and defer the voice / structural items to a separate pass.
(c) **Hand off to a copy-editor pass** for the voice items (em dashes, run-ons, opening) and apply the numerical fixes separately.

Recommendation: (a). The voice and numerical issues compound — a reader who hits an em dash early may also notice the CI inversion later. Fixing both in one pass is cheaper than two rounds.
