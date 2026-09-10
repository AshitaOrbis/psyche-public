# PsycheEval v0.3 Plan — Review Bundle

**Date**: 2026-05-18
**For**: GPT Pro, GPT Max, Codex Council
**Stage**: pre-execution review; plan locked 2026-05-18 but feedback can still revise before Phase 0 starts

This bundle gives reviewers the context to evaluate the v0.3 plan in lineage with v0.1 and v0.2. The reviewers are asked to identify (1) what the v0.3 plan misses, (2) where it overcommits, (3) what cheaper alternatives might better answer the open construct-validity question, and (4) whether the locked decisions (D1–D5) are well-calibrated against budget and v0.4 deferrals.

---

## Lineage: v0.1 → v0.2 → v0.3

### v0.1 (micro-pilot, 2026-04-20)
- Two-model authors+judges (gpt-5.4, Opus 4.7). 7 conditions × 8 personas × 80 scenarios.
- Surfaced 5 open questions: (1) PAE confound vs absence-of-contract for C5; (2) length confound for C4 > C1; (3) scalar ceiling (4.0–4.8 on 0–5); (4) scenarios too easy; (5) same-author scope generalization.
- v0.1 review found 4 cumulative review rounds of substantive fixes; final report curated under "Path B" framing rules (banned phrases, scope qualifiers, halo reframing).

### v0.2 (hard pilot, 2026-04-26 → 2026-05-18)
- Tri-model authors+judges (gpt-5.4, gpt-5.5-xhigh, Opus 4.7). 8 conditions including new `C5_CONTRACT`, length controls (`C1_padded`, `C4_shuffled`), anchored 0–10 rubric, harder 80-scenario set (mean difficulty 3.58/5).
- 1,680 outputs, 3,949 anchored scalar judgments, 3,243 raw pairwise records (3,064 true same-author).
- Two review rounds (Phase 0 + Phase 1 AB/BA + Phase 2 hygiene). Round 2 consolidated review (GPT Pro + codex-council + GPT Max + independent Opus 4.7) converged on a v0.3 priority list.
- v0.2 ships:
  - **Tier 1 (substantive, AB/BA-controlled)**: C5_CONTRACT > C5 at 67.7% [61.7, 73.3]; C4 > C5 at 68.0% [61.5, 74.4] judge-unanimous; C4 > C1_padded at 62.3% [56.1, 68.3]; C0 dominated by every profile condition.
  - **Tier 1.5 (modest)**: C4 > C4_shuffled at 57.8% [52.2, 63.7].
  - **Retracted**: C5_CONTRACT vs C3 (orig 57.2% → controlled 49.9% [43.4, 56.4]); C5_CONTRACT vs C4 (orig 60.0% → controlled 51.8% [45.2, 58.7]). Both straddle 0.5; the original headlines were carried by judge-family-specific slot-B bias.
  - **Methodology contribution**: per-judge slot-B preference quantification, corpus-scoped. gpt-5.4 ≈0, gpt-5.5-xhigh +0.14 to +0.31, Opus 4.7 +0.09 to +0.20.
- Blog post 046 (PsycheEval v0.2) shipped 2026-05-18 after 8-reviewer round-1 publication review and a single Write-pass MUST FIX revision applying 18 numerical/citation/voice fixes.

### Round-2 review consensus on v0.3 priorities (the seed of this plan)
Four reviewers, three LLM families, two architecture patterns (single-agent + 4-agent ensembles) converged on:
1. **C_GENERIC_CONTRACT** (highest priority) — generic contract vs personalized to test profile specificity
2. **C4_WRONG_PROFILE** — paired with C_GENERIC, triangulates personalization (matching axis vs specificity axis)
3. **C5_NONPUBLIC + C5_NONPUBLIC_CONTRACT** — isolates public-anchor effect from source-packet form
4. Contract-component ablation (C5_CONTRACT_SHORT, packet-first ordering, anti-mimicry on/off, facts-only)
5. Same-orientation rejudge sentinel (decomposes AB/BA flip rate into position bias + retest noise)
6. Paraphrased rubric anchors (robustness)
7. 30–100 human-rater calibration sample
8. Tie / equipoise pairwise option
9. Real-user shadow-mode validation as construct-validity bridge

---

## v0.2 Curated Report (executive sections — full report at `psyche/psycheeval/reports/psycheeval_v0_2_micro_pilot_2026-04-26_v02_hard_codex_only.md`, 471 lines)

### v0.2 §1 TL;DR (verbatim, key numbers only)

**Tier 1 (surviving substantive claims, position-bias-controlled, cluster-bootstrapped):**
- C5_CONTRACT > C5: 67.7% controlled [61.7, 73.3]. Judge-unanimous. Per-judge controlled lo_win: gpt-5.4=0.342, gpt-5.5=0.262, Opus=0.352 (lower-is-C5; all exclude 0.5 on the C5_CONTRACT side). Joint position+length correction holds. Mechanism not isolated — C5_CONTRACT differs from C5 on ≥4 dimensions: contract presence, contract-first ordering, anti-mimicry rules, prompt length (7,434 vs 3,884 chars).
- C4 > C5: 68.0% controlled [61.5, 74.4] judge-unanimous (gpt-5.4=0.681, gpt-5.5=0.681, Opus=0.679). Length-position joint correction holds at 67.4% [54.7, 79.5].
- C4 > C1_padded: 62.3% controlled [56.1, 68.3]. OpenAI judges only.
- C0 dominated by every profile condition. Pairwise C4>C0 at 86.6% original; scalar Δ_total +6.075 (largest in corpus). Not AB/BA-tested directly; effect outside position-bias corridor.

**Tier 1.5**: C4 > C4_shuffled at 57.8% controlled [52.2, 63.7], OpenAI judges only.

**Retracted (Tier 2 originals, now "no detection"):**
- C5_CONTRACT vs C3: original 57.2% → controlled 49.9% [43.4, 56.4]. Scalar Δ_total −0.053.
- C5_CONTRACT vs C4: original 60.0% → controlled 51.8% [45.2, 58.7]. Scalar Δ_total −0.231.

**Methodology contribution**: per-judge slot-B preference quantification on the AB/BA-tested pairs:

| pair | gpt-5.4 | gpt-5.5-xhigh | Opus 4.7 |
|---|---:|---:|---:|
| C3 vs C5_CONTRACT | −0.036 | +0.250 | +0.204 |
| C4 vs C5_CONTRACT | +0.024 | +0.250 | +0.199 |
| C5 vs C5_CONTRACT | +0.112 | +0.310 | +0.094 |
| C1_padded vs C4 | +0.031 | +0.200 | n/a |
| C4 vs C5 | +0.037 | +0.138 | +0.140 |
| C4 vs C4_shuffled | −0.025 | +0.263 | n/a |

Corpus-scoped. Direction-consistent with Zheng 2023 / Shi 2024. Contribution is the per-judge quantification on a tri-model corpus with same-author controls.

### v0.2 §6 — What survives, what doesn't (key reading)

The four-pair set surviving + retracting around C5_CONTRACT supports this cleanest reading: **the contract is doing most of the work; the source packet, when subordinated to a contract, contributes nothing detectable on top of it.** (CI permits ±7pp at n≈288 per pair; no equivalence margin predeclared so this is "no detection," not "established equivalence.")

### v0.2 §11 — What v0.3 needs to address

- Mechanism attribution for C5_CONTRACT > C5 (the 4 simultaneous differences)
- Profile specificity vs generic instructions (C_GENERIC_CONTRACT)
- Public-anchor isolation (C5_NONPUBLIC)
- AB/BA decomposition into position bias + retest noise (same-orientation sentinel)
- Real-user construct validity
- Rubric robustness (paraphrased anchors)
- Tie / equipoise pairwise option
- Profile-realism (deferred to v0.4)

---

## v0.3 Plan (full text, verbatim from `psyche/psycheeval/docs/v0_3_plan.md`)

The full v0.3 plan follows below. Reviewers should evaluate this plan as written; it is what would be executed if approved.

### v0.3 §1 — Status snapshot
[file: `psyche/psycheeval/docs/v0_3_plan.md` §1]

What v0.2 settled (Tier 1): C0 dominated; C4 > C1_padded; C4 > C5 judge-unanimous; C5_CONTRACT > C5 as package claim; C4 > C4_shuffled modest. What v0.2 retracted: C5_CONTRACT > C3 and > C4. What v0.2 left for v0.3: mechanism attribution, profile specificity, public-anchor isolation, AB/BA decomposition into position bias + retest noise, real-user construct validity, rubric robustness, tie/equipoise option, profile-realism.

### v0.3 §2 — Design decisions vs v0.2

- Tri-model panel continues (gpt-5.4, gpt-5.5-xhigh, Opus 4.7) as both authors and judges
- **AB/BA is now mandatory and default** (Phase 0.5 builds `--ab-ba-mandatory` flag for `psycheeval.run pairwise`). Every pairwise call gets its swap rejudgment in the same batch
- Same-author scope remains primary; cross-author exploratory
- Anchored 0–10 rubric stays; paraphrased-anchor sentinel runs alongside
- Scenario set unchanged from v0.2 (80 scenarios, mean difficulty 3.58/5); new conditions that need new prompts (notably C5_NONPUBLIC for PS personas) get authoring time, not scenario-set changes

### v0.3 §3 — Conditions

**Committed Tier 1 (round-2 reviewer consensus):**

| Code | Description | Mechanism question |
|---|---|---|
| C_GENERIC_CONTRACT | Behavioral contract structurally identical to C3/C4 but populated with generic, non-profile-specific language | Tests whether contract value is structure vs personalization |
| C4_WRONG_PROFILE | C4 with another persona's C4 profile substituted (matched by PI/PS type) | Tests matching axis; paired with C_GENERIC triangulates personalization |
| C5_NONPUBLIC | Source-packet narrative for PS personas (no public-anchor prose) | Isolates public-anchor effect from source-packet form |
| C5_NONPUBLIC_CONTRACT | C5_NONPUBLIC + same contract as C5_CONTRACT | Tests whether C5_CONTRACT > C5 generalizes to non-public-anchor packets |

**Committed Tier 2 (mechanism decomposition of C5_CONTRACT — all four, per D1):**

| Code | Description | Isolates |
|---|---|---|
| C5_CONTRACT_SHORT | Compressed to C3's char count (~2,518 chars vs 7,434) | Length |
| C5_CONTRACT_PACKET_FIRST | Source packet before contract | Ordering |
| C5_CONTRACT_NO_ANTIMIMICRY | Anti-mimicry rules removed | Anti-mimicry effect |
| C5_FACTS_ONLY | Source packet stripped to bullet-point facts | Narrative form vs facts |

**Committed judge-side hardening:**
- Same-orientation rejudge sentinel (per pair, sample at 10%): decomposes AB/BA flip rate
- Paraphrased rubric anchors (sample at 15%): rubric robustness
- Tie / equipoise pairwise option: lets judges express no-meaningful-difference
- 50-pair human-rater calibration sample (single rater, per D2): one-rater alignment statistic with v0.4 expansion noted

### v0.3 §4 — Diagnostics

Two new analyzer blocks:
- D1: `_compute_same_orientation_sentinel` — per-pair same-orientation rejudge flip rate. Subtract from AB/BA flip rate to get position-bias-net-of-retest-noise
- D2: `_compute_paraphrased_anchor_consistency` — per-judge ICC / Spearman ρ between original-anchor and paraphrased-anchor scalar scores

Optional: D3 `_compute_human_calibration_alignment` — per-pair human-rater preference vs LLM-judge preference (conditional on the sample existing)

### v0.3 §5 — Phased execution plan

| Phase | Estimate | Deliverable |
|-------|---------|-------------|
| 0 — Pre-flight hardening | ~6h dev | 8 new conditions wired, ab-ba-mandatory flag, two new analyzer blocks, tests green |
| 1 — Tier-1 generation (4 new conditions) | ~$25 codex + ~1 Opus cap window, 1 day | ~440 outputs total |
| 2 — Tier-2 generation (4 mechanism conditions, PI only) | ~$25 + ~1 Opus cap window, 1 day | ~560 outputs total |
| 3 — Anchored scalar judging + sentinels | ~$80 + ~2 Opus cap windows, 3–5 days | ~4,225 calls (3,900 scalar + 130 same-orientation 10% + 195 paraphrased 15%) |
| 4 — AB/BA mandatory pairwise + Phase 4.4 equivalence-margin TOST | ~$280 + ~3–4 Opus cap windows, 7–10 days | ~17,600 pairwise calls (7,200 T1 + 5,400 T2 + 1,250 sentinel + 3,750 Phase 4.4 equivalence-margin extension on C5_CONTRACT vs C3 / C4) |
| 5 — Human calibration (single rater) | ~1 day rater time + UI build | 50 pairs scored; LLM-vs-human alignment statistic |
| 6 — Analysis on v0.3 corpus | ~1 day | `metrics_<v0.3>.json` with all v0.2 blocks + D1 + D2 + D3 |
| 7 — Curate v0.3 report | 2–3 days | Curated v0.3 report through `/publication-review` 3-reviewer panel |
| 8 — v3 blog post | 2–3 days | Blog post through `/writing-review` (5 perspectives) + `/publication-review` (3 reviewers) |
| 9 — Shadow-mode validation design doc | ~2 days writing | Concrete design + pre-registered predictions for Psyche public results page (executable in v0.4) |

**Estimated total**: ~$430 codex + 8–10 Opus cap windows + 3–5 weeks wall time.

### v0.3 §6 — Decisions locked 2026-05-18

| ID | Decision | Resolution |
|----|----------|------------|
| D1 | Scope of Tier 2 mechanism conditions | **All four** (SHORT, PACKET_FIRST, NO_ANTIMIMICRY, FACTS_ONLY). Combinatorial decomposition essential. |
| D2 | Human calibration sample | **Single rater** (author) for v0.3. n_rater=1 acknowledged limitation; v0.4 upgrade to ≥2 raters. |
| D3 | Pair-set scope for T1 conditions | **4 most informative pair types per new condition** (16 pair types total). Expansion at Phase 6 if a missing pair becomes load-bearing. |
| D4 | Shadow-mode validation candidate context | **Psyche public results page** at `app.ashitaorbis.com/psyche`. v0.3 ships concrete design + pre-registered predictions; v0.4 executes. |
| D5 | C5_CONTRACT > C3 equivalence-margin scope | **In v0.3 scope.** Predeclared ±5pp equivalence margin TOST on combined v0.2+v0.3 corpus (n_combined ≈ 600 per pair). Phase 4.4 generates ~3,750 additional AB/BA pairs. |

The ±5pp margin (D5) is justified by deployment relevance in shadow-mode validation (Phase 9): a 5pp difference in pairwise win rate is small enough that real-user engagement signal would dominate.

### v0.3 §8 — Success criteria

v0.3 ships when:
1. The 4 T1 mechanism conditions have AB/BA-controlled pairwise outcomes against their 4-pair-type scope (16 pair types) with cluster bootstrap CIs.
2. The 4 T2 mechanism conditions decompose the C5_CONTRACT > C5 effect into at least *which* of the 4 simultaneous differences is dominant — or attribute to "the combination," with evidence.
3. Same-orientation sentinel produces a corpus-scoped retest-noise floor; v0.3 reports position-bias-net-of-retest-noise per judge.
4. Paraphrased-anchor test confirms or refutes that anchored 0–10 scalar scores are stable to anchor wording.
5. Single-rater human calibration on 50 pairs produces a one-rater alignment statistic with the n_rater=1 limitation documented.
6. Phase 4.4 TOST: either establishes ±5pp equivalence (both one-sided cluster-bootstrap p < 0.05) or reports "no detection / no established equivalence" honestly.
7. Phase 9 shadow-mode design doc is written with: UI delta against `psyche.ts`, instrumentation spec, 80%/7pp power analysis, consent language, analysis plan, pre-registered predictions linking v0.3 LLM-judge findings to v0.4 engagement gaps.

v0.3 is **not** required to: reach n_rater ≥ 2; execute shadow-mode validation (Phase 9 is design-only); expand the Phase 4.1 pair-set beyond the 4 most-informative per T1 condition.

---

## What we want from the review

(A) **Plan-level critique**: what gaps, overcommits, or miscalibrations does the v0.3 plan have? Anything missed? Anything that should be cut or deferred?

(B) **Decision audit (D1–D5)**: are the locked decisions well-calibrated against budget and v0.4 deferrals? Where would you push back?

(C) **Sequencing critique**: phase ordering (0 → 1 → 2 → 3‖4‖5 → 6 → 7 → 8 + 9 parallel) — is this the right order? What dependencies are missing or over-specified?

(D) **Cheaper alternatives**: any of the v0.3 goals achievable at substantially lower cost via a different design? Especially: is the Phase 4.4 TOST the right way to settle C5_CONTRACT vs C3/C4, or is there a cheaper test that produces an equally publishable result?

(E) **Construct validity bridge depth**: the Psyche results-page shadow-mode (D4) is the v0.3 commitment, but only as design-doc for v0.4 execution. Is this the right pacing, or should v0.3 push harder on this axis (e.g., scale-down execution of a minimal MVP shadow-mode in v0.3)?

(F) **The deepest open question**: anything *not* on the v0.3 plan that should be, especially in the construct-validity / generalization / adversarial-robustness regions? What v0.4+ horizons does v0.3 lock in or close off prematurely?

Focus your critique on substance over surface. Be direct and specific. The plan author has been through 2 review rounds on v0.1 and v0.2 already and is calibrated for blunt criticism over diplomacy.

---

## Pointers (full files reviewers may read if their toolset allows)

- v0.2 canonical report: `~/claudeworkspace/psyche/psycheeval/reports/psycheeval_v0_2_micro_pilot_2026-04-26_v02_hard_codex_only.md` (471 lines)
- v0.2 canonical metrics: `~/claudeworkspace/psyche/psycheeval/reports/metrics_2026-04-26_v02_hard_codex_only.json`
- v0.3 plan: `~/claudeworkspace/psyche/psycheeval/docs/v0_3_plan.md` (358 lines)
- v0.2 round-2 consolidated review (origin of round-2 consensus): `~/claudeworkspace/psyche/psycheeval/reports/reviews/2026-05-17_consolidated_round2_review.md`
- v0.2 blog post: `~/claudeworkspace/applications/ashitaorbis/shared/content/posts/046-psycheeval-v0_2.md`
- v0.2 blog post round-1 publication review (the source of Phase 4.4 equivalence-margin commitment, via the Opus 4.6 steelman): `~/claudeworkspace/psyche/psycheeval/reports/reviews/2026-05-18_consolidated_round1.md`
