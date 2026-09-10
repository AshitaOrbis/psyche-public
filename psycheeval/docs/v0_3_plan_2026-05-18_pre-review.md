# PsycheEval v0.3 — Plan

**Date**: 2026-05-18
**Status**: Decisions locked 2026-05-18. Ready for Phase 0 execution.
**Supersedes**: implicitly continues `docs/v0_2_plan_extended_2026-05-05.md`.

This plan inherits the structure of the v0.2 extended plan and is grounded in four inputs:

1. **The v0.2 curated report** (`reports/psycheeval_v0_2_micro_pilot_2026-04-26_v02_hard_codex_only.md`): canonical findings, retraction structure, what survives, what doesn't.
2. **The v0.2 round-2 consolidated review** (`reports/reviews/2026-05-17_consolidated_round2_review.md`): four reviewers (GPT Pro, codex-council, GPT Max, independent Opus) converged on a v0.3 priority list.
3. **The v0.2 blog post round-1 consolidated review** (`reports/reviews/2026-05-18_consolidated_round1.md`): 8-reviewer aggregation; surfaces residual methodology gaps (most consequentially the same-orientation rejudge sentinel from the Opus 4.6 steelman).
4. **The post itself** (`applications/ashitaorbis/shared/content/posts/046-psycheeval-v0_2.md`): the §7 v0.3 backlog as the public commitment.

---

## 1. Status snapshot — what v0.2 produced vs what v0.3 inherits

### What v0.2 settled (Tier 1 substantive)

| Finding | Effect size (controlled) | Scope | Status |
|---------|--------------------------|-------|--------|
| C0 dominated by every profile condition | 86.6% (C4 vs C0 first-pass) | not AB/BA-tested; effect outside position-bias corridor | settled |
| C4 > C1_padded | 62.3% controlled | OpenAI judges only | settled (length confound resolved in favor of contract) |
| C4 > C5 | 68.0% controlled | judge-unanimous (all three) | settled (after Phase 2 Opus fill) |
| C5_CONTRACT > C5 | 67.7% controlled | judge-unanimous | settled as *package* claim; mechanism unattributed |
| C4 > C4_shuffled (Tier 1.5) | 57.8% controlled | OpenAI judges only | modest |

### What v0.2 retracted

| Finding | Outcome | Why v0.3 needs to address it |
|---------|---------|------------------------------|
| C5_CONTRACT > C3 (originally 57.2%) | Collapsed under AB/BA: controlled 49.9%, CI [0.436, 0.566] | The C5_CONTRACT > C5 package claim is still load-bearing for "source packets add value when subordinated to a contract." Without C5_CONTRACT > C3, the source packet's marginal contribution is unestablished. |
| C5_CONTRACT > C4 (originally 60.0%) | Collapsed: controlled 51.8%, CI [0.413, 0.548] | Same. |

### What v0.2 added as a methodology contribution

Per-judge slot-B preference quantification: gpt-5.4 ≈0, gpt-5.5-xhigh +0.14 to +0.31, Opus +0.09 to +0.20, **corpus-scoped**. This is the bar v0.3's methodology contributions must clear (or exceed).

### What v0.2 did not address (carried into v0.3)

- **Mechanism attribution for C5_CONTRACT > C5**: four simultaneous differences (contract present, contract-first ordering, anti-mimicry rules, ~2× prompt length). Single ablation experiment can't distinguish them; needs a component-by-component decomposition.
- **Profile specificity vs generic instructions**: the C3/C4 contract benefit relative to C0/C1 may not be about *this user's* profile at all — could be "any well-structured behavioral contract." Untested.
- **Public-anchor isolation**: C5 uses public-anchor narrative (Wikipedia-style biographical prose) for PI personas. C5_CONTRACT inherits this. Whether the "source packet" effect generalizes to non-public-anchor narrative form is unisolated.
- **AB/BA decomposition into position bias and retest noise**: the controlled = mean(original, swap) estimator assumes additive symmetric position effects. A same-orientation rejudge sentinel would decompose the AB/BA flip rate. v0.2 didn't run it.
- **Real-user construct validity**: PsycheEval measures LLM-judge preferences on synthetic personas. Real-user benefit is unmeasured.
- **Rubric robustness**: anchored 0–10 rubric used fixed anchor wording. Whether paraphrased anchors reproduce the same scalar span is untested.
- **Tie / equipoise**: pairwise judges currently forced to a decisive choice. No "no meaningful difference" option.
- **Profile-realism**: all profiles are clean, complete, and synthetic. Stale, contradictory, user-edited, and compressed-profile cases unmeasured.

### Hardening — P1 backlog at v0.3 entry

| Item | Status | Block? |
|------|--------|--------|
| Cap-burn fix in `judge.py` (rc=1, burst-rate) | landed in v0.2 Phase 0.1 + 2026-05-14 | no |
| Cluster bootstrap on AB/BA controlled rate | landed in v0.2 Phase 2.1 | no |
| Claim ledger as canonical artifact | landed in v0.2 Phase 2.3 | no |
| Joint position × length correction | landed in v0.2 Phase 2.7 | no |
| Cross-provider AB/BA | landed in v0.2 Phase 2.8 | no |
| Persona × author × condition cross-tab | landed in v0.2 Phase A.7 | no |

No P1 hardening items block v0.3 execution.

---

## 2. v0.3 design decisions vs v0.2

### Authors panel: continue tri-model

GPT-5.4, GPT-5.5-xhigh, Opus 4.7 as both authors and judges. Same panel as v0.2. Re-evaluate at v0.4 if GPT-5.6 or Claude 4.8 lands during execution.

### Counterbalanced AB/BA judging is now the default

v0.2's biggest methodology learning was that retrofitting AB/BA is expensive and risky (you may have already published a retracted headline by the time you run it). For v0.3, **all pairwise judging is AB/BA from the start**. Each pairwise pair gets its swap rejudgment in the same run, not as a Phase-1 add-on.

Implication: pairwise budget per pair doubles. Build this into Phase 0 budgeting.

### Same-author scope is still the primary; cross-author is exploratory

v0.2 same-author worked well for isolating condition effects from author effects. v0.3 same-author scope continues to anchor the pairwise design. Cross-author analyses (halo audit, provider-family bias) remain exploratory secondaries.

### Anchored 0–10 rubric stays; paraphrased-anchor sentinel runs alongside

The anchored rubric's 2.42-point span on 0–10 (vs 0.8 on the v0.1 unanchored 0–5) restored measurement headroom. Don't change it. Do run a parallel **paraphrased-anchor rubric** on a small subset to test whether judges are memorizing anchor wording or genuinely interpreting the dimensions.

### Scenario set: keep v0.2's 80-scenario × 8-family set, expand if a new condition needs new prompts

v0.2's mean difficulty 3.58/5 was the right calibration. No retiring of v0.2 scenarios planned for v0.3. New conditions that require new prompts (notably `C5_NONPUBLIC` which needs 4 PS-persona source packets) get authoring time, not scenario-set changes.

---

## 3. Conditions

### Committed for v0.3 (round-2 reviewer consensus)

| Code | Tier | Description | Mechanism question it answers |
|------|------|-------------|-------------------------------|
| **C_GENERIC_CONTRACT** | T1 | Behavioral contract structurally identical to C3/C4 (if-then engagement rules, anti-sycophancy cues, calibrated challenge, agency support) but populated with **generic, non-profile-specific** language. | If `C_GENERIC > C5` ≈ `C3/C4 > C5`, the contract's value is *structure*, not *personalization*. If `C_GENERIC < C3/C4`, profile specificity is doing measurable work. Either outcome is informative. |
| **C4_WRONG_PROFILE** | T1 | C4 condition but with a *different* persona's C4 profile substituted (matched by PI/PS type so the mismatch isn't trivially detectable). | If `C4_WRONG > C5`, profile *matching* doesn't matter — any structured contract suffices. Triangulates with `C_GENERIC_CONTRACT`: `C_GENERIC` measures specificity axis; `C4_WRONG` measures matching axis. |
| **C5_NONPUBLIC** | T1 | Source-packet narrative authored *for the PS personas* (no public-anchor Wikipedia-style prose). | Isolates the public-anchor form effect from the source-packet form effect. v0.2's C5 was PI-only because the public-anchor prose only exists for PI personas. |
| **C5_NONPUBLIC_CONTRACT** | T1 | `C5_NONPUBLIC` + same behavioral contract as C5_CONTRACT. | Tests whether the C5_CONTRACT > C5 effect generalizes to non-public-anchor packets. |

### Committed for v0.3 (mechanism decomposition of C5_CONTRACT — all four run)

| Code | Tier | Description | What it isolates |
|------|------|-------------|------------------|
| **C5_CONTRACT_SHORT** | T2 | C5_CONTRACT compressed to match C3's character count (~2,518 chars). Drop redundant phrasing, preserve anti-mimicry rules and contract structure. | Tests whether the C5_CONTRACT advantage over C5 is length. C5_CONTRACT is 7,434 chars vs C5's 3,884; this brings it down to C3-equivalent. |
| **C5_CONTRACT_PACKET_FIRST** | T2 | C5_CONTRACT with source packet placed *before* the behavioral contract (reverse of the default contract-first ordering). | Tests whether contract-first ordering is doing work. |
| **C5_CONTRACT_NO_ANTIMIMICRY** | T2 | C5_CONTRACT with the explicit anti-mimicry rules ("do not imitate the writing style of the source packet") removed. | Tests whether anti-mimicry rules are doing work. |
| **C5_FACTS_ONLY** | T2 | C5 source packet stripped to bullet-point biographical facts (no narrative prose). | Tests whether the "narrative form" of the source packet matters, or whether it's just the facts. |

Decision (D1, locked 2026-05-18): run all four T2 conditions. The combinatorial decomposition is essential to attribute the C5_CONTRACT > C5 mechanism, and the per-condition cost is small relative to the v0.3 budget.

### Committed for v0.3 (judge-side hardening)

| Experiment | Description | Why |
|-----------|-------------|-----|
| **Same-orientation rejudge sentinel** | Run the same pairwise prompt twice in the *same* slot order (not swapped). Compare flip rate to AB/BA flip rate. | Decomposes AB/BA flip rate into position bias and retest noise. The Opus 4.6 steelman in the round-1 publication review made this the deepest open methodology question. |
| **Paraphrased rubric anchors** | Re-judge a 10–20% sample of v0.2 scalar outputs with paraphrased anchor wording at each rubric point. | Tests whether judges memorize anchor wording or interpret dimensions. Robustness check. |
| **Tie / equipoise pairwise option** | Add a third option to the pairwise prompt: "no meaningful difference." | Currently judges are forced to a decisive choice even on indistinguishable pairs. Equipoise option reduces noise on null pairs. |
| **50-pair human-rater calibration sample (single rater)** | 50 high-leverage pairs scored by 1 blinded human rater (the author or a collaborator). Compare to LLM-judge preferences. | Sanity-checks LLM-judge preferences against a single human reference. Inter-rater reliability is **not** computed at n_rater=1; v0.3 documents this as a methodology limitation and the result is a *one-rater alignment* statistic, not a calibrated benchmark. Adding a second rater is a v0.4 upgrade. |

### Deferred to v0.4 (long-horizon profile-realism)

| Code | Description | Why deferred |
|------|-------------|--------------|
| C4_STALE | C4 condition with profile content marked as "from 6 months ago" | Realism axis; v0.4 |
| C4_CONTRADICTORY | C4 with internal contradictions inserted | Realism axis; v0.4 |
| C4_USER_EDITED | C4 where the profile has visible user edits (corrections) | Realism axis; v0.4 |
| C4_COMPRESSED_500 / _1K / _2K | C4 profile compressed to 500 / 1k / 2k chars | Compression curve; v0.4 |
| Multi-turn extension | Profile-conditioning across 3–5 turns rather than single-turn | Substantial scope increase; v0.4 or paper |

### Deferred to a separate program (construct validity bridge)

**Real-user shadow-mode validation**: PsycheEval as it stands measures LLM-judge preferences. Bridging to a real-user outcome (preference, follow-through, expert-rated decision quality, escalation rate) requires shadow-mode deployment in a real assistant context. This is a *separate program*, not a v0.3 phase. v0.3's deliverable on this axis is a **proposal doc** describing the shadow-mode design.

---

## 4. Diagnostics — what changes vs v0.2

v0.2's analyzer landed: cluster-bootstrap CIs, joint position × length, cross-provider AB/BA, scalar–pairwise reconciliation, leave-one-out fragility, claim ledger, per-judge AB/BA stratification, persona × author × condition cross-tab, length buckets, tie rates.

v0.3 needs **two new analyzer blocks**:

| # | Block | Purpose |
|---|-------|---------|
| D1 | `_compute_same_orientation_sentinel` | Per-pair same-orientation rejudge flip rate. Subtract from AB/BA flip rate to get position-bias-net-of-retest-noise. |
| D2 | `_compute_paraphrased_anchor_consistency` | Per-judge correlation between original-anchor and paraphrased-anchor scalar scores. ICC or Spearman ρ per dimension. |

Plus **one optional block**:

| # | Block | Purpose |
|---|-------|---------|
| D3 | `_compute_human_calibration_alignment` | Per-pair human-rater preference vs LLM-judge preference. Pearson r at pair level; Cohen's κ for binary agreement. Conditioned on the human calibration sample existing. |

All existing v0.2 analyzer blocks carry forward unchanged.

---

## 5. Phased execution plan

Estimated total wall time: **3–5 weeks** depending on Opus quota and human-rater availability.

### Phase 0 — Pre-flight hardening (~6 hours)

| # | Task | Estimate |
|---|------|----------|
| 0.1 | Add `C_GENERIC_CONTRACT`, `C4_WRONG_PROFILE`, `C5_NONPUBLIC`, `C5_NONPUBLIC_CONTRACT`, `C5_CONTRACT_SHORT`, `C5_CONTRACT_PACKET_FIRST`, `C5_CONTRACT_NO_ANTIMIMICRY`, `C5_FACTS_ONLY` to `Condition` enum + `ProfileConditions` wiring | ~1.5h |
| 0.2 | Author generic contract template (C_GENERIC) — strip profile specifics from C4 template, keep structure | ~1h |
| 0.3 | Author 4 PS-persona source packets for C5_NONPUBLIC (biographical narrative for synthetic personas; meaningful authoring task) | ~2h |
| 0.4 | Author the 4 C5_CONTRACT mechanism variants (SHORT, PACKET_FIRST, NO_ANTIMIMICRY, FACTS_ONLY) as prompt-template transformations | ~1h |
| 0.5 | Build `--ab-ba-mandatory` flag for `psycheeval.run pairwise`: every pairwise call automatically gets its swap rejudgment in the same batch | ~1.5h |
| 0.6 | Implement analyzer block D1 (`_compute_same_orientation_sentinel`) | ~1h |
| 0.7 | Implement analyzer block D2 (`_compute_paraphrased_anchor_consistency`) | ~1h |
| 0.8 | Tests for new analyzer blocks (extend `test_analyzer_smoke.py`) | ~1h |

**Exit criteria**: 8 new conditions wired end-to-end, ab-ba-mandatory pairwise flag works, two new analyzer blocks produce JSON cells, tests green.

### Phase 1 — Tier-1 generation (C_GENERIC, C4_WRONG, C5_NONPUBLIC, C5_NONPUBLIC_CONTRACT)

Per condition: 80 scenarios × 8 personas × 3 authors = 1,920 outputs is upper bound. v0.2's actual cell shape was 70/condition/author = 210/condition (= ~80 scenarios × subset of personas). Use the same shape.

| # | Task | Calls | Notes |
|---|------|-------|-------|
| 1.1 | Generate `C_GENERIC_CONTRACT` outputs (codex side: gpt-5.4, gpt-5.5) | ~140 outputs | ~$5 |
| 1.2 | Generate `C4_WRONG_PROFILE` outputs (codex side) | ~140 outputs | |
| 1.3 | Generate `C5_NONPUBLIC` outputs (codex side, PS personas only — 4 PS) | ~80 outputs | |
| 1.4 | Generate `C5_NONPUBLIC_CONTRACT` outputs (codex side, PS personas only) | ~80 outputs | |
| 1.5 | Generate Opus authoring on all four T1 conditions (gated on Opus quota) | ~220 outputs | ~1 cap window |

**Phase 1 risk**: PS-only conditions (C5_NONPUBLIC, C5_NONPUBLIC_CONTRACT) reduce the per-condition cell count. Worth confirming the PS-side n is sufficient for bootstrap CI tightness before generating.

### Phase 2 — Tier-2 generation (C5_CONTRACT mechanism decomposition)

| # | Task | Calls |
|---|------|-------|
| 2.1 | Generate `C5_CONTRACT_SHORT` (PI only, parallel to C5_CONTRACT scope) | ~140 outputs |
| 2.2 | Generate `C5_CONTRACT_PACKET_FIRST` (PI only) | ~140 outputs |
| 2.3 | Generate `C5_CONTRACT_NO_ANTIMIMICRY` (PI only) | ~140 outputs |
| 2.4 | Generate `C5_FACTS_ONLY` (PI only) | ~140 outputs |
| 2.5 | Opus authoring on T2 conditions | ~280 outputs, gated on quota |

### Phase 3 — Anchored scalar judging (3 judges)

| # | Task | Scope | Calls |
|---|------|-------|-------|
| 3.1 | Anchored scalar on all Phase 1 + Phase 2 outputs | ~1,300 outputs × 3 judges | ~3,900 calls |
| 3.2 | Same-orientation sentinel on 10% subset for retest-noise baseline | ~130 calls | |
| 3.3 | Paraphrased-anchor sentinel on 15% subset for robustness | ~195 calls | |

**Phase 3 risk**: Opus judge quota — biggest risk. Stagger across cap windows.

### Phase 4 — AB/BA mandatory pairwise

AB/BA is now baked in (Phase 0.5). Every pair gets original + swap in the same batch.

Decision (D3, locked 2026-05-18): Tier 1 pair-set scope is restricted to the 4 most-informative pair types per condition. If during analysis a missing pair-type becomes load-bearing for a downstream claim, expand at Phase 6 (low marginal cost given the corpus is already authored).

| # | Task | Pair set | Calls |
|---|------|----------|-------|
| 4.1 | T1 pair-set (4 pair types per new condition): C_GENERIC vs {C0, C3, C4, C5}; C4_WRONG vs {C0, C3, C4, C5}; C5_NONPUBLIC vs {C5, C5_CONTRACT, C3, C4}; C5_NONPUBLIC_CONTRACT vs {C5_NONPUBLIC, C5_CONTRACT, C3, C4} | 16 pair types × ~75 pairs/type × 3 judges × 2 (AB+BA) = ~7,200 calls | |
| 4.2 | T2 pair-set: 4 mechanism variants each paired against C5_CONTRACT, C5, and C4 (3 pair types per T2 condition) | 12 pair types × ~75 × 3 × 2 = ~5,400 calls | |
| 4.3 | Same-orientation sentinel on a 10% subset of pairwise records (re-judge the same orientation, not swapped) | ~1,250 calls | |
| 4.4 | **Equivalence-margin TOST extension** (D5, locked 2026-05-18): additional AB/BA pairs on C5_CONTRACT vs C3 and C5_CONTRACT vs C4 to expand n from 288 to ~600 per pair. Predeclared ±5pp margin TOST test against the controlled lo_win. | 2 pair types × ~312 additional pairs/type × 3 judges × 2 (AB+BA) = ~3,750 calls | |

**Phase 4 total**: ~17,600 pairwise calls. Budget ~$280 codex + 3–4 Opus cap windows.

**Phase 4.4 design note**: predeclaration of the ±5pp equivalence margin happens *before* the Phase 4.4 generation runs (margin is documented in §8 Success Criteria below). The TOST test uses cluster bootstrap on the combined v0.2 + v0.3 corpus (n_combined ≈ 600 per pair); the test rejects each one-sided null if the corresponding cluster-bootstrap one-sided p-value falls below α=0.05. Both rejections established equivalence within ±5pp; either failure leaves "no detection / no established equivalence" as the v0.3 conclusion. The margin is justified by deployment relevance: in the shadow-mode validation context (Phase 9), a 5pp difference in pairwise win rate is small enough that engagement signal would dominate.

### Phase 5 — Human calibration sample (parallel with 3 and 4)

Decision (D2, locked 2026-05-18): single rater (the author) for v0.3. No inter-rater reliability; result is a *one-rater alignment* statistic, not a calibrated benchmark. Adding a second rater is a v0.4 upgrade.

| # | Task | Notes |
|---|------|-------|
| 5.1 | Select 50 high-leverage pairs (10 per Tier 1 mechanism question; 10 calibration-anchor pairs) | use claim-ledger as selection prior |
| 5.2 | Build a minimal rater UI (one-click forced choice + 0–10 scalar on 3 key dimensions) | Streamlit or a static HTML form persisting to JSONL is simplest |
| 5.3 | Rater (author) blinded to condition labels scores the 50 pairs | blinding via random-ID mapping; condition-decoded only at analysis time |
| 5.4 | Compute LLM-vs-human alignment | analyzer block D3: per-pair direction agreement; Pearson r between LLM scalar Δ_total and human scalar Δ_total; per-judge ICC against the human rater |

**Phase 5 limitation note for the v0.3 report**: n_rater=1 means we cannot decompose disagreement into "this LLM judge is wrong" vs "human raters disagree among themselves." Any LLM-vs-human gap is reported as a *single-rater alignment* signal, not a ground-truth gap. The v0.3 report will explicitly recommend a v0.4 expansion to ≥2 raters before any benchmark claim is published.

### Phase 6 — Analysis on completed v0.3 corpus

| # | Task |
|---|------|
| 6.1 | Run `psycheeval.analyze --tag <v0.3> --pilot v03_full` to produce `metrics_<tag>.json` with all v0.2 blocks + D1 (sentinel) + D2 (paraphrased anchors) + D3 (human alignment if available) |
| 6.2 | Generate failure cards |
| 6.3 | Generate autogen scaffold (`psycheeval_v0_3_autogen.md`) |
| 6.4 | Compute decomposed AB/BA: position-bias-net-of-retest-noise = AB/BA flip rate − same-orientation flip rate, per pair per judge |
| 6.5 | Run claim ledger against v0.3 results; identify which v0.2 retractions still need framing in v0.3 |

### Phase 7 — Curate v0.3 report

| # | Task |
|---|------|
| 7.1 | First-pass curation against the autogen scaffold (same framing rules as v0.2) |
| 7.2 | `/publication-review` 3-reviewer panel against the curated report |
| 7.3 | Apply consolidated fixes; persist all 3 review artifacts |
| 7.4 | Optional round-2 delta review |
| 7.5 | Push to the reading device for read-through |

### Phase 8 — v3 blog post

| # | Task |
|---|------|
| 8.1 | Writer session briefed with v0.3 curated report |
| 8.2 | Draft → `/writing-review` (5 perspectives) + `/publication-review` (3 reviewers) |
| 8.3 | Apply fixes |
| 8.4 | Deploy via Ashita Orbis 3-tier pipeline |

### Phase 9 — Real-user shadow-mode validation: concrete design for the Psyche public results page

Decision (D4, locked 2026-05-18): Psyche public results page at `app.ashitaorbis.com/psyche` is the shadow-mode deployment context for v0.4. v0.3's Phase 9 deliverable is the **concrete design doc + instrumentation spec + analysis plan**, ready to execute in v0.4 without re-litigating context choice.

Why this context: the user has just completed the Psyche assessment, so they have the exact profile the system will condition on. This is the cleanest possible construct-validity match: PsycheEval measures pairwise win rate over profile-conditioned outputs; the shadow-mode test asks whether the user this profile represents prefers the profile-conditioned response in a real follow-up interaction.

| # | Task | Output |
|---|------|--------|
| 9.1 | **Write `docs/shadow_mode_validation_v04_design.md`** covering: | concrete design doc |
| 9.1.a | Surface design: results-page "Ask a follow-up question" UI delta (textarea + submit; response appears inline below the profile) | UI mockup or wireframe sketch |
| 9.1.b | Routing logic: 50/50 random assignment to profile-conditioned (C4-style contract with the user's actual profile) vs generic (no profile or generic contract). Single response shown per submission; routing decision logged. | pseudocode |
| 9.1.c | Engagement instrumentation: click-through to follow-up question (highest-quality positive signal); explicit thumbs-up/down (if added); time-on-response (low signal but cheap); copy/share clicks (if surface allows); follow-up question count per session (engagement-depth proxy) | event schema |
| 9.1.d | Target sample size: ~200 sessions per arm gives 80% power to detect a 10pp engagement gap, 400 per arm for 7pp. Estimate timeline given current results-page traffic. | power analysis |
| 9.1.e | Consent: results page already has implicit consent via the assessment terms. Add a one-sentence disclosure in the results page footer: "Follow-up responses are part of an ongoing methodology study; aggregate engagement data is anonymized." Document compliance with current ashitaorbis.com privacy policy. | consent language draft |
| 9.1.f | Analysis plan: per-arm engagement rate (binary "user submitted a follow-up question after seeing the response"); Cohen's h effect size; cluster bootstrap CI on the engagement-rate difference. Map to PsycheEval's pairwise win rate: if the profile-conditioned arm wins engagement at rate p, the implied "real-user pairwise preference" is roughly p / (p + q) where q is the generic-arm engagement rate. | analysis spec |
| 9.1.g | Stopping rules and quality gates: pause if either arm shows >2σ deviation from steady-state engagement (suggests broken response generation); recompute power at n=100/arm and decide whether to extend | safety + power gates |
| 9.2 | Sketch the implementation diff against the existing `applications/ashitaorbis/api/src/routes/psyche.ts` (the current Kimi K2.5 generation path) — identify which file changes are needed to add the routing + instrumentation | technical sketch |
| 9.3 | Document the relationship between v0.3 LLM-judge findings and v0.4 shadow-mode predictions: which v0.3 Tier 1 findings, if real, should produce which engagement-rate gaps in shadow-mode? Pre-register the predictions before v0.4 launches. | prediction registration |
| 9.4 | **NOT executed in v0.3** — design + prediction registration only. Execution lands in v0.4 once the design ships review. | — |

---

## 6. Decisions (locked 2026-05-18)

| ID | Decision | Resolution |
|----|----------|------------|
| D1 | Scope of Tier 2 mechanism conditions | **Run all four** (SHORT, PACKET_FIRST, NO_ANTIMIMICRY, FACTS_ONLY). Combinatorial decomposition is essential to attribute the C5_CONTRACT > C5 mechanism. |
| D2 | Human calibration sample size | **Single rater** (author) for v0.3. No inter-rater reliability; result is a *one-rater alignment* statistic, not a calibrated benchmark. v0.3 report documents this as a methodology limitation and recommends a v0.4 expansion to ≥2 raters before any benchmark claim is published. |
| D3 | Pair-set scope for C_GENERIC_CONTRACT and C4_WRONG_PROFILE | **Limit to 4 most informative pair types per new condition**. C_GENERIC vs {C0, C3, C4, C5}; C4_WRONG vs {C0, C3, C4, C5}; C5_NONPUBLIC vs {C5, C5_CONTRACT, C3, C4}; C5_NONPUBLIC_CONTRACT vs {C5_NONPUBLIC, C5_CONTRACT, C3, C4}. Phase 6 analysis may flag a missing pair-type as load-bearing; in that case expand at low marginal cost (corpus is already authored, only new judging needed). |
| D4 | Shadow-mode validation candidate context | **Psyche public results page** at `app.ashitaorbis.com/psyche`. Cleanest construct-validity match: the user has just completed the assessment that generates the profile the system conditions on. v0.3 Phase 9 ships the concrete design + instrumentation spec + pre-registered predictions; v0.4 executes. |
| D5 | C5_CONTRACT > C3 equivalence-margin scope | **In v0.3 scope.** Predeclared ±5pp equivalence margin TOST on combined v0.2 + v0.3 corpus (n_combined ≈ 600 per pair). Phase 4.4 generates the additional AB/BA pairs (~3,750 calls). Establishes equivalence within ±5pp or reports "no detection / no established equivalence" as the v0.3 conclusion. |

The ±5pp margin is justified by deployment relevance in the shadow-mode validation context (Phase 9): a 5pp difference in pairwise win rate is small enough that real-user engagement signal would dominate over the LLM-judge preference signal. Predeclaring the margin before Phase 4.4 generation runs satisfies the TOST methodological requirement.

---

## 7. Budget rollup

Approximate, in current pricing. Revised after locking D1–D5.

| Phase | Codex side | Opus side | Wall time |
|-------|-----------|-----------|-----------|
| 0 (code work) | $0 | $0 | ~6h dev time |
| 1 (T1 generation, 4 conditions) | ~$25 | ~1 cap window | 1 day |
| 2 (T2 generation, all 4 mechanism conditions) | ~$25 | ~1 cap window | 1 day |
| 3 (anchored scalar + 2 sentinels) | ~$80 | ~2 cap windows | 3–5 days staggered |
| 4 (AB/BA pairwise + Phase 4.4 equivalence-margin TOST extension) | ~$280 | ~3–4 cap windows | 7–10 days staggered |
| 5 (human calibration, single rater) | $0 | $0 | ~1 day of rater time + UI build |
| 6 (analysis) | $0 | $0 | ~1 day |
| 7 (curate report) | ~$10 (review panel) | $0 | 2–3 days |
| 8 (v3 blog post) | ~$10 (review panel) | $0 | 2–3 days |
| 9 (shadow-mode design doc + pre-registered predictions) | $0 | $0 | ~2 days writing |

**Estimated total**: ~$430 codex + 8–10 Opus cap windows + 3–5 weeks wall time.

The biggest risk to wall time is Opus quota burn on Phase 4 (Opus pairwise on the expanded pair set + the Phase 4.4 equivalence-margin extension). Cap-window staggering (v0.2's pattern) handles this; resume-safe writes already protect against partial runs. Net wall-time delta vs original plan: +3 days from Phase 4.4, +1 day from Phase 9's design-doc expansion, offset by faster Phase 5 (single rater means no recruitment latency).

---

## 8. Success criteria

v0.3 ships when:

1. The four T1 mechanism conditions (C_GENERIC, C4_WRONG, C5_NONPUBLIC, C5_NONPUBLIC_CONTRACT) have AB/BA-controlled pairwise outcomes against their 4-pair-type scope (16 pair types total) with cluster bootstrap CIs.
2. The four T2 mechanism conditions decompose the C5_CONTRACT > C5 effect into at least *which* of the four simultaneous differences (length, ordering, anti-mimicry, narrative form) is dominant — or attribute it to "the combination," with evidence.
3. The same-orientation rejudge sentinel produces a corpus-scoped retest-noise floor that lets v0.3 report position-bias-net-of-retest-noise per judge.
4. The paraphrased-anchor robustness test confirms (or refutes) that anchored 0–10 scalar scores are stable to anchor wording.
5. The single-rater human calibration on 50 pairs produces a one-rater alignment statistic (per-pair direction agreement; Pearson r against LLM scalar Δ_total; per-judge ICC), with the n_rater=1 limitation documented and a v0.4 expansion to ≥2 raters recommended.
6. **The Phase 4.4 equivalence-margin TOST** on C5_CONTRACT vs C3 and vs C4 either establishes equivalence within ±5pp (both one-sided cluster-bootstrap p-values < 0.05) **or** reports "no detection, no established equivalence" with the underpowered-test caveat.
7. The Phase 9 shadow-mode validation design doc is written, with: UI delta against the existing `psyche.ts` route; instrumentation spec; power analysis for 80% / 7pp engagement gap; consent language; analysis plan; pre-registered predictions mapping v0.3 LLM-judge findings to v0.4 engagement gaps.

**Predeclared equivalence margin (D5)**: ±5pp on the AB/BA controlled lo_win rate, justified by shadow-mode deployment relevance (engagement signal dominates at smaller LLM-judge gaps).

v0.3 is **not** required to:
- Reach n_rater ≥ 2 on the human calibration sample (D2 limitation).
- Execute the shadow-mode validation (Phase 9 is design-only; execution is v0.4).
- Expand the Phase 4.1 pair-set beyond the 4 most-informative pair types per T1 condition (D3 — expansion happens at Phase 6 if a missing pair becomes load-bearing).

---

## 9. Notes

- v0.2 ended with a clean tier system: Tier 1 substantive, Tier 1.5 modest, retracted. v0.3 should preserve this taxonomy and extend it (Tier 1.5 may grow if any T2 mechanism conditions land in the modest range).
- The v0.2 round-1 publication review's "What This Doesn't Settle" subsection (the Opus 4.6 steelman about controlled-rate-as-truth) is the seed of the same-orientation rejudge sentinel. The sentinel is the highest-priority methodology fix because it answers the deepest published criticism.
- Construct validity (real-user shadow-mode) is the deepest open question. v0.3 ships the concrete design + pre-registered predictions for the Psyche-results-page deployment context (D4); v0.4 executes. Pre-registration of predictions is methodologically important: if v0.3's LLM-judge findings predict shadow-mode engagement gaps and the v0.4 data confirms or contradicts those predictions, that *is* the construct-validity result, win or lose.
- The Phase 4.4 equivalence-margin TOST is the cleanest closure of the v0.2 retractions. Either C5_CONTRACT and C3 are functionally equivalent within ±5pp (a real published result, not "no detection"), or the effect is real-but-small and v0.3 has the n to detect it. Both outcomes resolve the open question.
- The single-rater human calibration limitation (D2) is the weakest methodology choice in v0.3, deliberately so. The v0.4 upgrade to ≥2 raters is named as the planned fix. Don't overclaim from n_rater=1.
- If a v0.3 finding contradicts a v0.2 Tier 1 claim, the v0.2 retraction-as-success pattern is the right framing; document the contradiction in the curated report's claim ledger, not as an erratum.
