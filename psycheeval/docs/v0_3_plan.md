# PsycheEval v0.3 — Plan (Revised)

**Date**: 2026-05-18 (revised)
**Status**: Pre-Phase -1. Decisions revised after consolidated external review.
**Pre-review version archived at**: `docs/v0_3_plan_2026-05-18_pre-review.md`
**Supersedes**: implicitly continues `docs/v0_2_plan_extended_2026-05-05.md`.

## Revision provenance

This revision incorporates 15 findings from a 3-reviewer round (codex-council 4-persona blind ensemble + gpt-max 4-persona HCOM ensemble + GPT-5.5 Pro single-Pro-tier) consolidated at `reports/reviews/2026-05-18_consolidated_v0_3_plan_review.md`. The pre-review plan locked 5 decisions (D1–D5); 4 have been materially revised here (D1, D2, D4, D5); D3 carried with predeclared expansion triggers.

The single most consequential revision is **GP1**: pre-review Tier 2 conditions did not include a contract-presence ablation, so the design could not "decompose" the C5_CONTRACT > C5 mechanism it claimed to. T2 is now a 5-step ablation ladder that isolates contract presence as a distinct axis.

This plan inherits the structure of the v0.2 extended plan and is grounded in four canonical inputs:

1. **v0.2 curated report** (`reports/psycheeval_v0_2_micro_pilot_2026-04-26_v02_hard_codex_only.md`)
2. **v0.2 round-2 consolidated review** (`reports/reviews/2026-05-17_consolidated_round2_review.md`)
3. **v0.2 blog post round-1 publication review** (`reports/reviews/2026-05-18_consolidated_round1.md`)
4. **v0.3 plan pre-review consolidated review** (`reports/reviews/2026-05-18_consolidated_v0_3_plan_review.md`) — the source of this revision

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
| C5_CONTRACT > C3 (originally 57.2%) | Collapsed under AB/BA: controlled 49.9%, CI [0.436, 0.566] | Source packet's marginal contribution beyond contract is unestablished; closing this loop is publication-relevant |
| C5_CONTRACT > C4 (originally 60.0%) | Collapsed: controlled 51.8%, CI [0.413, 0.548] | Same |

### What v0.2 added as a methodology contribution

Per-judge slot-B preference quantification, corpus-scoped: gpt-5.4 ≈0, gpt-5.5-xhigh +0.14 to +0.31, Opus 4.7 +0.09 to +0.20.

### What v0.2 leaves for v0.3

- **Mechanism attribution for C5_CONTRACT > C5** — the four simultaneous differences: (1) contract presence, (2) contract-first ordering, (3) anti-mimicry rules, (4) prompt length (7,434 vs 3,884 chars)
- **Profile specificity vs generic instructions** (C_GENERIC_CONTRACT)
- **Public-anchor isolation** (C5_NONPUBLIC + PI-matched variant)
- **AB/BA decomposition into position bias + retest noise** (same-orientation rejudge sentinel)
- **Real-user construct validity** (Phase 9 design + executable smoke test)
- **Rubric robustness** (paraphrased anchors)
- **Tie / equipoise pairwise option**
- **Profile-realism stress test** (sparse, contradictory, overly-detailed, emotionally-sensitive)
- **Adversarial profile robustness** (prompt injection, hidden instructions, flattery-of-delusions)
- **Judge reward-hacking diagnostics** (per-output length, profile-reference count, hedging, lexical overlap)
- **Equivalence-margin TOST on collapsed pairs** — adaptive branch, not default (see D5 below)

### Hardening status at v0.3 entry

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

## 2. Design decisions vs v0.2

### Authors panel: continue tri-model
GPT-5.4, GPT-5.5-xhigh, Opus 4.7 as both authors and judges. Same panel as v0.2.

### Counterbalanced AB/BA judging is now the default
v0.3's biggest methodology learning from v0.2 is that retrofitting AB/BA is expensive. **All pairwise judging is AB/BA from the start**; pairwise budget per pair doubles.

### Forced-choice for v0.2-compatible analyses; ternary tie/equipoise as a separate Phase 0 sentinel
**GP3 / cross-reviewer consensus**: introducing tie/equipoise in v0.3 while v0.2 was forced-choice breaks any pooled TOST estimand. Phase 0 design-lock decides which judging prompt is canonical:
- **Path A** (preferred): keep v0.2-style forced-choice as the primary pairwise prompt for v0.3 generation; run tie/equipoise as a **separate 10% sentinel** to estimate the tie rate and the fraction of "no meaningful difference" pairs.
- **Path B** (more expensive): switch v0.3 to ternary; rejudge the relevant v0.2 pairs under ternary before any pooled analysis.

Phase -1 documents the choice and locks the v0.2+v0.3 combination rule before generation.

### Same-author scope still primary
Same-author for the headline inferential design; cross-author exploratory.

### Anchored 0–10 rubric stays; paraphrased-anchor sentinel runs in parallel
The 2.42-point span on 0–10 (vs v0.1's 0.8-point on 0–5) restored measurement headroom. Don't change the primary rubric. Run paraphrased-anchor sentinel on 15% subset.

### Scenario set: keep v0.2's 80-scenario × 8-family set; add a pre-flight contamination/staleness audit
Pre-flight scenario audit (legibility, contamination) added to Phase -1. New conditions that require new prompts (C5_NONPUBLIC PS packets, PI-matched nonpublic packets, adversarial profiles, realism stress profiles) get authoring time, not scenario-set changes.

---

## 3. Conditions

### 3.1 Committed Tier 1 — personalization probes (round-2 reviewer consensus)

| Code | Description | Mechanism question | Length-match target |
|------|-------------|--------------------|--------------------|
| **C_GENERIC_CONTRACT** | Behavioral contract structurally identical to C3/C4 but populated with *generic*, non-profile-specific language. **Match C4 on length, structure, readability** (R10). | If `C_GENERIC > C5` ≈ `C3/C4 > C5`, contract value is *structure*, not *personalization*. | C4 (~4,519 chars) |
| **C4_WRONG_PROFILE** | C4 with a *different* persona's C4 profile substituted. **Mapping: opposite-trait / opposite-need substitution within the same PI/PS type**, not random any-other (R10 / gpt-max risk-analyst). | Tests *matching* axis; paired with C_GENERIC triangulates personalization. | C4 (~4,519 chars) |
| **C5_NONPUBLIC** | **Decision pending Phase -1 (R2)**: choose between (a) author PI-matched nonpublic packets so the comparison stays within-population, or (b) narrow the claim to "PS-only synthetic-packet behavior" with no public-anchor isolation. **Pre-review version had a pairability bug**: PS-only packets compared against PI-only C5/C5_CONTRACT would confound public-anchor with persona scope. | Public-anchor effect, if R2(a); PS source-packet behavior if R2(b). | C5 (~3,884 chars) |
| **C5_NONPUBLIC_CONTRACT** | C5_NONPUBLIC + same contract as C5_CONTRACT. Same R2 decision applies. | Whether C5_CONTRACT > C5 generalizes to non-public-anchor packets. | C5_CONTRACT (~7,434 chars) |

### 3.2 Committed Tier 2 — C5_CONTRACT mechanism ablation ladder (R6 / GP1)

The pre-review T2 conditions did **not** isolate the four v0.2 confounds (contract presence, contract-first ordering, anti-mimicry, length) — they substituted "facts-only" for "contract presence" and length-matched to the wrong target. **Revised T2 is a 5-condition ablation ladder** keyed to the four named v0.2 confounds:

| # | Code | Description | What's added vs prior step | Length |
|---|------|-------------|----------------------------|--------|
| L0 | C5 (existing baseline) | Source packet only, no contract | — | 3,884 chars |
| L1 | **C5_MINCONTRACT_PACKET_FIRST_NOMIMICRY** | C5 + minimal behavioral contract, packet-first ordering, no anti-mimicry, length-matched to C5 | **contract presence** (the previously-missing axis) | ~3,884 chars (length-matched, R7 / GP2) |
| L2 | **C5_MINCONTRACT_PACKET_FIRST_ANTIMIMICRY** | L1 + anti-mimicry rules | **anti-mimicry** | ~3,884 chars |
| L3 | **C5_MINCONTRACT_CONTRACT_FIRST_ANTIMIMICRY** | L2 with contract-first ordering | **contract-first ordering** | ~3,884 chars |
| L4 | C5_CONTRACT (existing) | Full v0.2 C5_CONTRACT | **expanded length** (~7,434 chars; the only step that adds length) | 7,434 chars |

This is still a single path through condition space (not a full factorial), so it does not identify pairwise interactions. The success criterion is downgraded accordingly (see §8): **"screen which component additions visibly damage the package effect when removed"** rather than "decompose mechanism."

The pre-review C5_FACTS_ONLY condition is **dropped** as not addressing the four v0.2 confounds. If narrative-form-vs-facts becomes a v0.4 priority, it returns as a separate question with its own contract-preserving design.

The pre-review C5_CONTRACT_SHORT condition is **dropped** in favor of L4 (where length is the only difference from L3); the pre-review version compressed to C3's length (~2,518 chars), which is shorter than C5 itself and so does not isolate the C5_CONTRACT vs C5 length confound (R7 / GP2).

### 3.3 Committed judge-side hardening

| Item | Scope | Rationale |
|------|-------|-----------|
| **Same-orientation rejudge sentinel** | Sample 10% of pairwise records; rejudge the same orientation | Decomposes AB/BA flip rate into position bias + retest noise. Address the Opus 4.6 steelman from v0.2 blog post round 1. Per-judge/per-pair heterogeneity reported alongside corpus-scope subtraction (R11). |
| **Paraphrased rubric anchors** | Sample 15% of scalar records; rejudge with paraphrased anchor wording | Test rubric robustness. Pilot in Phase 0 before full Phase 3 generation to catch distribution shifts. |
| **Tie / equipoise pairwise option** | **Separate ternary sentinel, not the primary pairwise prompt** (see §2 Path A) | Estimates the rate at which judges would prefer "no meaningful difference" if allowed. Lets the v0.3 report quote a tie-aware reinterpretation of forced-choice numbers without breaking v0.2 comparability. |
| **50-pair human-rater calibration sample** | 50 high-leverage pairs; **single rater (author), blinded to condition labels and to LLM-judge results** (R8/D2) | Author-rater sanity check. Reported as "one-rater alignment statistic," not calibration. v0.4 upgrade to ≥2 raters named in this plan as the planned fix. |

### 3.4 Committed Phase 9 instrumentation conditions (R5)

The Phase 9 shadow-mode design ships an executable artifact in v0.3 (not just a design doc). New conditions are **routing variants** at the Psyche public results page:

| Variant | Description |
|---------|-------------|
| `RESULTS_GENERIC` | Standard results-page response (no profile conditioning) |
| `RESULTS_CONTRACT` | Results-page response with C4-style behavioral contract using the user's actual profile |

The Phase 9 MVP randomizes between these two for follow-up question responses. Not powered for an effect; designed to validate routing + instrumentation + engagement endpoint quality.

### 3.5 Optional (NICE TO HAVE) v0.3 conditions

Stretch goals; cut first if budget tightens.

| Code | Description | Source |
|------|-------------|--------|
| **Adversarial profile slice** | 4–8 profiles with prompt injection, hidden instructions, flattery-of-delusions trigger, contradictory identity claims | R13 / GP4 |
| **Realism stress profiles** | Sparse, contradictory, overly-detailed, emotionally-sensitive, irrelevant-facts, misleading-but-plausible | R15 / GP6 |

Each is tested against C0 / C3 / C4 / C5 / C5_CONTRACT pair-types. PI scope only.

### 3.6 Deferred to v0.4

- Long-horizon profile-realism (stale, user-edited, profile compression curve at 500/1k/2k chars)
- Multi-turn extension
- Real-user shadow-mode execution (Phase 9 in v0.3 ships the design + a tiny smoke test; powered execution waits for v0.4)
- Inter-rater reliability with ≥2 human raters

---

## 4. Diagnostics — analyzer blocks

All v0.2 blocks carry forward unchanged. v0.3 adds:

| # | Block | Purpose |
|---|-------|---------|
| **D1** | `_compute_same_orientation_sentinel` | Per-pair same-orientation rejudge flip rate. Subtract from AB/BA flip rate to get position-bias-net-of-retest-noise. **Report per-judge / per-pair heterogeneity, not just corpus-scope mean** (R11). |
| **D2** | `_compute_paraphrased_anchor_consistency` | Per-judge ICC + Spearman ρ between original-anchor and paraphrased-anchor scalar scores. Distinguish mean-shift / rank-stability / threshold-crossing effects. |
| **D3** | `_compute_reward_hacking_diagnostics` (R14 / GP5) | Per-output: word/char length, profile-reference count, tailoring-phrase markers ("I'm tailoring this," "given your profile"), hedging frequency, lexical overlap with source packet, refusal/safety markers. Test whether judge preference survives after controlling for these per-condition. |
| **D4** | `_compute_tie_aware_reinterpretation` | Cross-prompt comparison: forced-choice lo_win vs ternary lo_win on the 10% tie sentinel sample. Estimate the corpus-scoped tie rate. |
| **D5 (optional)** | `_compute_human_calibration_alignment` | Per-pair direction agreement between author-rater and LLM judges; Pearson r at pair level; flagged as one-rater statistic, not calibration. |

---

## 5. Phased execution plan

Estimated total wall time: **4–6 weeks** (extended from pre-review 3–5 weeks by Phase -1 + Phase 9 executable artifact).

### Phase −1 — Design-lock (R1)
**No LLM calls. Pre-generation predeclaration.** This phase is the largest single revision from the pre-review plan.

| # | Artifact | Deliverable |
|---|----------|-------------|
| -1.1 | **Fixed pair manifest** | Every primary contrast labeled: PRIMARY-CONFIRMATORY, SECONDARY-CONFIRMATORY, EXPLORATORY-ONLY, NOT-TESTED. Each pair: condition_lo, condition_hi, judge scope (3 judges or codex-only), persona scope (PI/PS/all), expected n. |
| -1.2 | **Per-cell n table + cluster-level power memo** | For every primary contrast, expected n_pairs (cluster unit = persona × scenario × author) and cluster-resampling power simulation from existing v0.2 AB/BA data. Special focus on PS-only conditions (C5_NONPUBLIC scope decision) and D5 equivalence-margin power. |
| -1.3 | **Tie policy** | Path A (forced-choice primary + ternary sentinel, recommended) vs Path B (ternary primary + v0.2 rejudge) chosen and locked. Tie-record handling in TOST: counted as 0.5 / modeled separately / excluded. |
| -1.4 | **Endpoint hierarchy** | When pairwise / scalar / tie-aware / human-rater / shadow-mode signals conflict, which wins for each headline claim. |
| -1.5 | **Model snapshot freeze** | Exact judge model IDs, version-pinning, cap-window stratification policy, prompt-version freeze before any pooling with v0.2. |
| -1.6 | **MCID justification independent of unexecuted shadow-mode** | The pre-review plan justified ±5pp via Phase 9 deployment relevance; Phase 9 was design-only — circular. Phase -1 either (a) sets MCID from prior literature / project priors with no shadow-mode dependency, or (b) demotes D5 to "no detection, no equivalence" framing only. |
| -1.7 | **Phase 6 expansion triggers (predeclared)** | What specific data pattern triggers a pair-set expansion, separated from headline claims, labeled exploratory only. |
| -1.8 | **D5 decision ledger** | Which specific v0.3 report claim or v0.4 decision the equivalence result is load-bearing for. If no claim depends on it, D5 doesn't run. |
| -1.9 | **C5_NONPUBLIC scope decision** | R2 fork: PI-matched nonpublic packets (preserves within-population comparison; ~4h authoring) vs narrow PS-only claim (loses public-anchor isolation). |
| -1.10 | **Scenario-set audit** | Spot-check the 80-scenario set for contamination, staleness, profile-legibility cues. Address gpt-max/empiricist flag. |
| -1.11 | **Failure criteria (R10 / GP7)** | What would cause each headline claim to be downgraded? Predeclared as symmetric to success criteria (see §8). |
| -1.12 | **Phase 9 power / D5 margin reconciliation (R9 / GP3)** | The pre-review plan had Phase 9 power at 7pp and D5 margin at 5pp — internal contradiction. Phase -1 sets both consistently. |

**Phase -1 exit criteria**: design-lock doc reviewed against pre-review consolidated review; all 12 sub-items signed off; cluster-power simulation shows D5 is decidable OR D5 is demoted; C5_NONPUBLIC pairability resolved.

**Cost**: ~2 days writing + ~4h cluster-power simulation code. Zero LLM calls.

### Phase 0 — Pre-flight code hardening (~8 hours)

| # | Task | Estimate |
|---|------|----------|
| 0.1 | Add `C_GENERIC_CONTRACT`, `C4_WRONG_PROFILE`, `C5_NONPUBLIC`, `C5_NONPUBLIC_CONTRACT`, plus T2 ladder (L1, L2, L3) and optional adversarial/realism conditions to `Condition` enum + `ProfileConditions` wiring | ~2h |
| 0.2 | Author generic contract template (C_GENERIC) — strip profile specifics from C4 template, length-match to C4 | ~1h |
| 0.3 | Author 4 PS-persona source packets for C5_NONPUBLIC (or PI-matched nonpublic packets per Phase -1.9 decision) | ~3h |
| 0.4 | Author T2 ladder prompt templates (L1/L2/L3) — minimal contract, length-matched to C5 (R7 / GP2) | ~1.5h |
| 0.5 | Build `--ab-ba-mandatory` flag for `psycheeval.run pairwise`: every pairwise call gets its swap rejudgment in the same batch | ~1.5h |
| 0.6 | Implement analyzer blocks D1, D2, D3, D4 (D5 optional, conditional on rater sample existing) | ~2.5h |
| 0.7 | Tests for new analyzer blocks + condition wiring | ~1h |
| 0.8 | (NICE TO HAVE) Author 4–8 adversarial profiles + 6 realism stress profiles (R13, R15) | ~3h |

**Exit criteria**: 8 base + optional adversarial/realism conditions wired end-to-end, ab-ba-mandatory flag works, four new analyzer blocks produce JSON cells, tests green.

### Phase 1 — Tier-1 generation (C_GENERIC, C4_WRONG, C5_NONPUBLIC, C5_NONPUBLIC_CONTRACT)

| # | Task | Calls |
|---|------|-------|
| 1.1 | Generate `C_GENERIC_CONTRACT` outputs (codex side) | ~140 outputs |
| 1.2 | Generate `C4_WRONG_PROFILE` outputs (codex side) — opposite-trait/opposite-need mapping (R10) | ~140 outputs |
| 1.3 | Generate `C5_NONPUBLIC` outputs (codex side, per Phase -1.9 scope decision) | ~80 outputs |
| 1.4 | Generate `C5_NONPUBLIC_CONTRACT` outputs (codex side) | ~80 outputs |
| 1.5 | Opus authoring on all four T1 conditions | ~220 outputs, ~1 cap window |
| 1.6 | **(R11) Smoke test before full generation**: 1 persona × 5 scenarios × all new conditions × all judges. Catch broken wiring, mismatch artifacts, C5_NONPUBLIC public-anchor leakage, judge prompt confusion before spending full Phase 1 budget. | ~50 outputs + ~150 judging calls; ~$5 |

### Phase 2 — Tier-2 ablation ladder generation (L1, L2, L3)

L0 (C5) and L4 (C5_CONTRACT) already exist in v0.2 corpus. Phase 2 generates the three intermediate steps.

| # | Task | Calls |
|---|------|-------|
| 2.1 | Generate L1 (minimal contract, packet-first, no anti-mimicry, length-matched to C5) — codex side | ~140 outputs |
| 2.2 | Generate L2 (L1 + anti-mimicry) — codex side | ~140 outputs |
| 2.3 | Generate L3 (L2 + contract-first ordering, length-matched to C5) — codex side | ~140 outputs |
| 2.4 | Opus authoring on T2 ladder | ~210 outputs, gated on quota |

### Phase 3 — Anchored scalar judging + sentinels (3 judges)

| # | Task | Calls |
|---|------|-------|
| 3.1 | Anchored scalar on all Phase 1 + Phase 2 outputs | ~3,000 calls (~1,000 outputs × 3 judges) |
| 3.2 | Same-orientation sentinel on 10% subset of pairwise records (Phase 4 records pre-sample) | ~1,250 calls |
| 3.3 | Paraphrased-anchor sentinel on 15% subset for robustness | ~450 calls |
| 3.4 | (R11) Paraphrased-anchor pilot on tiny subset BEFORE Phase 3.3 — catch distribution shifts that would invalidate the 15% sample | ~30 calls |
| 3.5 | Reward-hacking diagnostics on all outputs (D3 — programmatic, no LLM calls beyond what's already there) | $0 |

### Phase 4 — AB/BA mandatory pairwise (forced-choice primary)

AB/BA baked in (Phase 0.5). Every pair gets original + swap in the same batch.

D3 pair-set scope (locked, with predeclared expansion triggers from Phase -1.7):

| # | Task | Pair set | Calls |
|---|------|----------|-------|
| 4.1 | T1 pair-set (4 pair types per new condition): C_GENERIC vs {C0, C3, C4, C5}; C4_WRONG vs {C0, C3, C4, C5}; C5_NONPUBLIC vs {C5, C5_CONTRACT, C3, C4}; C5_NONPUBLIC_CONTRACT vs {C5_NONPUBLIC, C5_CONTRACT, C3, C4} | 16 pair types × ~75 pairs/type × 3 judges × 2 (AB+BA) | ~7,200 calls |
| 4.2 | T2 ladder pair-set: each ladder step vs neighbors (L0-L1, L1-L2, L2-L3, L3-L4) | 4 pair types × ~75 × 3 × 2 | ~1,800 calls |
| 4.3 | T2 anchor pair-set: each ladder step vs C5 and C5_CONTRACT (to anchor effect sizes against existing v0.2 endpoints) | 8 pair types × ~75 × 3 × 2 | ~3,600 calls |
| 4.4 | **Phase 4.4 — D5 adaptive equivalence-margin TOST** (R3 / consensus): runs **only** if Phase -1.8 D5 decision ledger names a load-bearing claim AND Phase -1.2 cluster-power simulation says ±5pp (or revised margin from -1.6) is decidable at conditional power ≥80%. Two sub-modes: | | |
| 4.4a | (Adaptive default) If gate fails: skip Phase 4.4 entirely; v0.3 report frames as "no detection, no established equivalence" with the underpowered-test caveat. | 0 | $0 |
| 4.4b | (Adaptive run) If gate passes: tie-aware rejudge of *only the two collapsed edges* (C5_CONTRACT vs C3, C5_CONTRACT vs C4) using the ternary prompt + AB/BA + same-orientation sentinel. Tests whether forced-choice manufactured pseudo-preferences in v0.2. **Empiricist's preferred cheaper alternative to broad TOST expansion.** | 2 pair types × ~200 pairs × 3 judges × 2 (AB+BA) | ~2,400 calls |

**Phase 4 total**: 
- If 4.4 skipped: ~12,600 pairwise calls. Budget ~$200 codex + 3–4 Opus cap windows.
- If 4.4 runs (4.4b): ~15,000 pairwise calls. Budget ~$240 codex + 3–4 Opus cap windows.

### Phase 5 — Human rater sample (parallel with 3 and 4)

Decision (D2 revised, R8): single rater = **author-rater sanity check**, NOT calibration.

| # | Task | Notes |
|---|------|-------|
| 5.1 | Select 50 high-leverage pairs (10 per Tier 1 mechanism question; 10 for T2 ladder steps; 10 calibration-anchor pairs) | Selection rule predeclared in Phase -1.7 |
| 5.2 | Build a minimal rater UI (one-click forced choice + 0–10 scalar on 3 key dimensions, single page, JSONL persistence) | Streamlit or static HTML |
| 5.3 | **Rater (author) scores 50 pairs BEFORE inspecting model-judge results for those pairs.** Random-ID condition mapping; condition-decoded only at analysis time. (R11 sequencing fix) | Blinding via random ID; no peeking |
| 5.4 | Compute one-rater alignment statistic: per-pair direction agreement; Pearson r between LLM scalar Δ_total and author scalar Δ_total | analyzer block D5 |

**v0.3 report wording**: "author-rater sanity check, n=1, not a calibration benchmark." v0.4 upgrade to ≥2 raters named as the planned fix. The plan does NOT use this as construct-validity evidence.

### Phase 6 — Analysis (with predeclared expansion triggers from Phase -1.7)

| # | Task |
|---|------|
| 6.1 | Run `psycheeval.analyze --tag <v0.3> --pilot v03_full` to produce `metrics_<tag>.json` with all v0.2 blocks + D1 + D2 + D3 + D4 (+ D5 if rater sample exists) |
| 6.2 | Generate failure cards |
| 6.3 | Generate autogen scaffold (`psycheeval_v0_3_autogen.md`) |
| 6.4 | Compute decomposed AB/BA: position-bias-net-of-retest-noise = AB/BA flip rate − same-orientation flip rate, per pair per judge. **Report heterogeneity, not just corpus-scope mean** (R11). |
| 6.5 | T2 ladder analysis: marginal Δ per ladder step. Predeclared interpretation: which step adds the most to the C5_CONTRACT package effect. **Wording**: "marginal contribution of each ladder step," NOT "mechanism decomposition." |
| 6.6 | Reward-hacking diagnostics: per-condition output length, profile-reference count, hedging, source-packet lexical overlap. Test whether judge preference survives after controlling for these (regression with diagnostic as covariate). |
| 6.7 | **Predeclared exploratory expansion (if triggered per Phase -1.7)**: add specific pair types flagged in Phase -1.7 triggers. Reported **exploratory only**, not in headline claims. |

### Phase 7 — Curate v0.3 report

| # | Task |
|---|------|
| 7.1 | First-pass curation against autogen scaffold; framing rules carry forward from v0.2 (banned phrases, required scope qualifiers, claim ledger as canonical artifact) |
| 7.2 | `/publication-review` 3-reviewer panel against the curated report |
| 7.3 | Apply consolidated fixes; persist all 3 review artifacts |
| 7.4 | Optional round-2 delta review |
| 7.5 | Push to the reading device for read-through |

### Phase 8 — v3 blog post

Decision: **defer Phase 8 if the report frames anything as deployment-relevant** (R5 / GPT Pro). If the v0.3 report is purely a methods/process post — fine. If it implies real-user benefit — wait until Phase 9 shadow-mode smoke test data is in hand.

| # | Task |
|---|------|
| 8.1 | Writer session briefed with v0.3 curated report |
| 8.2 | Draft → `/writing-review` (5 perspectives) + `/publication-review` (3 reviewers) |
| 8.3 | Apply fixes |
| 8.4 | Deploy via Ashita Orbis 3-tier pipeline |

### Phase 9 — Shadow-mode validation: executable artifact (R5 / cross-reviewer consensus)

**Major revision**: pre-review plan made Phase 9 design-doc-only with execution deferred to v0.4. Revised Phase 9 ships an **executable artifact in v0.3** — not powered for an effect, but verified-readiness so D5's deployment-relevance justification (if D5 runs) is not circular.

Decision (D4 revised): Psyche public results page at `app.ashitaorbis.com/psyche`.

| # | Task | Deliverable |
|---|------|-------------|
| 9.1 | **Phase 9 design doc** at `docs/shadow_mode_validation_v04_design.md` covering: UI delta against `applications/ashitaorbis/api/src/routes/psyche.ts`; routing logic (50/50 random assignment between `RESULTS_GENERIC` and `RESULTS_CONTRACT`); engagement instrumentation (follow-up question click-through, thumbs-up/down, time-on-response, copy/share); power analysis (set power target consistent with D5 MCID per Phase -1.12); consent language draft; analysis plan mapping engagement gaps to PsycheEval pairwise win rate. | Design doc |
| 9.2 | **Phase 9 MVP execution**: implement the routing + logging behind a feature flag in `psyche.ts`. Add event schema (8–10 event types: route assigned, response shown, response continued, follow-up submitted, thumbs reaction, page exit, time-on-response samples, error). | Live but flag-gated infrastructure |
| 9.3 | **Smoke test (NOT powered for effect)**: enable flag for the author + 5–10 internal users; run for 1 week; verify routing works, events are captured, response variants render correctly, no latency/error regressions. | Verified instrumentation |
| 9.4 | **Pre-registered predictions**: write down v0.3's LLM-judge findings (which conditions beat which, and by how much) and the engagement-gap predictions that would follow if construct validity holds. **This is what makes v0.4 falsifiable.** If v0.4 sees engagement gap X and v0.3 predicted Y, the gap \|X − Y\| is the construct-validity metric. | Pre-reg doc |
| 9.5 | Real-user powered execution remains v0.4 — not in v0.3 scope. | v0.4 |

Phase 9 cost: ~2–3 days build + 1 week smoke test wall time. No new LLM calls.

---

## 6. Decisions (revised 2026-05-18 post-review)

| ID | Pre-review decision | Revised resolution | Rationale |
|----|---------------------|---------------------|-----------|
| **D1** | All four T2 mechanism conditions (SHORT, PACKET_FIRST, NO_ANTIMIMICRY, FACTS_ONLY); "combinatorial decomposition essential" | **Replaced with 5-step ablation ladder** (L0–L4) that includes contract-presence axis. Drop C5_FACTS_ONLY and original C5_CONTRACT_SHORT. Length-matched to C5, not C3. Success criterion reframed from "decompose mechanism" to "screen component additions." | R6 / GP1 + R4 / consensus: pre-review T2 missed contract-presence axis entirely; length target was wrong. |
| **D2** | Single rater (author) for v0.3 with v0.4 upgrade to ≥2 raters; called "calibration" | **Renamed to "author-rater sanity check"**; explicit n=1 limitation; not used as construct-validity evidence; v0.4 upgrade still planned. Rater sequenced *before* inspecting model results. | R8 / cross-reviewer consensus: n=1 cannot estimate inter-rater reliability, "calibration" is the wrong word. |
| **D3** | 4 most informative pair types per T1 condition; Phase 6 expansion if missing pair becomes load-bearing | **Carried, with predeclared expansion triggers from Phase -1.7**. Triggered expansions reported exploratory only, not in headline claims. | R9 / consensus: prevents post-hoc fishing. |
| **D4** | Psyche public results page; v0.3 design-doc only; v0.4 executes | **v0.3 ships executable artifact** — feature-flagged routing + instrumentation + smoke test + pre-registered predictions. Powered execution still v0.4. | R5 / cross-reviewer consensus: design-doc alone makes D5 margin justification circular; pre-registration of v0.3→v0.4 predictions makes v0.4 falsifiable. |
| **D5** | Predeclared ±5pp TOST on combined v0.2+v0.3 corpus; ~3,750 additional pairs | **Demoted from locked to adaptive branch.** Runs only if Phase -1 gates pass: (1) named load-bearing claim in D5 decision ledger; (2) cluster-power simulation shows ±5pp (or revised margin) decidable at ≥80% conditional power; (3) tie/forced-choice estimand unified; (4) MCID justified independent of unexecuted shadow-mode. **Fallback**: tie-aware rejudge of only the two collapsed edges (~2,400 calls vs ~3,750), Empiricist's preferred cheaper alternative. | R3 / cross-reviewer consensus: even ideal n=600 gives only ~58% power for ±5pp at true zero; clustering makes it worse; pre-review ±5pp justification was circular through Phase 9. |

The ±5pp margin (D5) is **no longer justified by Phase 9 deployment relevance alone**. Phase -1.6 establishes an MCID from prior literature / project priors with no shadow-mode dependency; if that justification fails, D5 demotes to "no detection / no established equivalence" framing without spending any 4.4b budget.

---

## 7. Budget rollup (revised)

| Phase | Codex side | Opus side | Wall time |
|-------|-----------|-----------|-----------|
| **-1** (design-lock) | $0 | $0 | ~2 days writing + 4h power sim |
| 0 (code + condition wiring) | $0 | $0 | ~8h dev (10h+ if adversarial/realism conditions also authored) |
| 1 (T1 generation + smoke test) | ~$30 | ~1 cap window | 1 day |
| 2 (T2 ladder generation, 3 conditions) | ~$20 | ~1 cap window | 1 day |
| 3 (scalar + sentinels + reward-hacking diagnostics) | ~$70 | ~2 cap windows | 3–5 days staggered |
| 4 (AB/BA pairwise) — **no D5** | ~$200 | ~3 cap windows | 5–7 days staggered |
| 4 (AB/BA pairwise) — **with D5 adaptive 4.4b** | ~$240 | ~3–4 cap windows | 7–10 days staggered |
| 5 (human rater, single) | $0 | $0 | ~1 day rater time + UI build |
| 6 (analysis) | $0 | $0 | ~1 day |
| 7 (curate report) | ~$10 (review panel) | $0 | 2–3 days |
| 8 (v3 blog post — deferred if results aren't methods-only) | ~$10 (review panel) | $0 | 2–3 days |
| 9 (shadow-mode design + MVP execution + pre-reg) | $0 (no LLM) | $0 | ~3 days build + 1 week smoke test wall |
| Optional adversarial / realism slice | ~$30 generation + ~$80 judging | ~1 cap window | 2 days staggered |

**Estimated total**:
- Without D5 4.4b and without adversarial/realism: ~$340 codex + 7–9 Opus cap windows + 4–6 weeks wall time
- With D5 4.4b: ~$380 codex + 7–10 Opus cap windows + 5–7 weeks wall time
- With D5 4.4b + adversarial/realism: ~$490 codex + 8–11 Opus cap windows + 6–8 weeks wall time

The biggest risk to wall time remains Opus quota burn on Phase 4 + Phase 3. Cap-window staggering handles this. Phase -1 adds ~2 days but pays for itself by preventing rework on the pre-review design errors.

---

## 8. Success and Failure criteria

### Success criteria

v0.3 ships when:

1. **T1 conditions**: C_GENERIC_CONTRACT, C4_WRONG_PROFILE, C5_NONPUBLIC, C5_NONPUBLIC_CONTRACT have AB/BA-controlled pairwise outcomes against their 16-pair-type scope with cluster bootstrap CIs and length/prompt-quality matching audited.
2. **T2 ablation ladder**: L0 → L1 → L2 → L3 → L4 marginal Δ per step reported. The headline claim is **which component additions visibly contribute to the C5_CONTRACT package effect**, not "mechanism decomposition." Interaction effects acknowledged as path-dependent.
3. **Same-orientation sentinel**: corpus-scoped retest-noise floor produced; per-judge, per-pair heterogeneity reported. v0.3 quotes position-bias-net-of-retest-noise per judge with uncertainty.
4. **Paraphrased-anchor sentinel**: confirms or refutes that anchored 0–10 scalar scores are stable to anchor wording. Mean-shift, rank-stability, and threshold-crossing reported separately.
5. **Reward-hacking diagnostics**: per-condition output length, profile-reference count, hedging frequency, source-packet lexical overlap. Judge-preference regression with diagnostics as covariates reported.
6. **Tie-aware reinterpretation**: 10% ternary sentinel produces a corpus-scoped tie rate; forced-choice headlines are re-quoted with the tie-aware fraction visible.
7. **Author-rater sanity check** (NOT calibration): 50 pairs scored; one-rater alignment statistic reported; n=1 limitation explicit.
8. **Phase 4.4 D5 outcome** (one of):
   - **Skipped** if Phase -1 gates failed: report frames C5_CONTRACT vs C3/C4 as "no detection, no established equivalence."
   - **Established equivalence** within the predeclared margin (Phase -1.6) if 4.4b passes both one-sided cluster-bootstrap tests at α=0.05.
   - **No equivalence established** if 4.4b ran but at least one one-sided test failed — reported honestly with the cluster-power caveat.
9. **Phase 9 deliverable**: shadow-mode design doc + executable artifact + smoke test demonstrating routing/logging/instrumentation works + pre-registered v0.3→v0.4 predictions.

v0.3 is NOT required to: reach n_rater ≥ 2 on calibration; execute powered shadow-mode validation; expand the Phase 4.1 pair-set beyond 4 per T1 condition unless predeclared expansion triggers fire.

### Failure criteria (R10 / GP7)

Predeclared at Phase -1.11. Any of the following **downgrades** the relevant headline claim from confirmatory to exploratory or removes it entirely:

| Trigger | Claim affected | Downgrade |
|---------|----------------|-----------|
| Paraphrased-anchor sentinel produces ≥0.5 SD mean-shift or changes condition rankings at any judge | All scalar-based claims | Downgrade to "anchored 0–10 rubric is anchor-sensitive; v0.3 results should not be compared to v0.2 scalar without rubric re-calibration." |
| Tie rate in ternary sentinel exceeds 25% on a C5_CONTRACT-edge pair | C5_CONTRACT > C5 package claim | Downgrade to "tie-aware reinterpretation shows substantial equipoise; package claim is weaker than forced-choice suggests." |
| Author-rater direction agreement with LLM-judges < 60% on the 50-pair sample | Any claim that quotes LLM-judge preference as a meaningful preference proxy | Report as "LLM-judge / author-rater divergence is substantial; v0.4 multi-rater calibration is required before benchmark claims." |
| C4_WRONG_PROFILE wins against C_GENERIC at >55% | Personalization claim | Downgrade: "profile mismatch does not measurably harm responses; profile-matching contribution is below detection." |
| C5_NONPUBLIC (Phase -1.9 option a: PI-matched) shows behavior indistinguishable from C5 | Public-anchor effect | "Public-anchor narrative form has no detectable effect over PI-matched nonpublic packets at this n; v0.4 stronger anchor-leakage controls required." |
| Same-orientation sentinel flip rate ≥ AB/BA flip rate on >50% of pairs | Same-orientation-net-of-noise interpretation | "AB/BA decomposition is unstable in this corpus; position-bias-net estimates should be reported as descriptive only, not as a corrected estimator." |
| Opus and OpenAI judges diverge by >0.15 on any T1 controlled lo_win | Judge-unanimous wording on that pair | Downgrade to "modest preference with judge-family divergence; cross-family pooling is not justified at this pair." |
| Reward-hacking diagnostic regression shows >50% of judge-preference effect explained by output length / profile-reference count alone | Mechanism claim for any condition pair | "Judge preference is partially explained by surface features; mechanism attribution requires controlling for these covariates." |

If ≥3 failure triggers fire, the v0.3 report opens with a "what didn't work" section before any headline claim. This is symmetric to the v0.2 retraction-as-success pattern.

---

## 9. Notes

- v0.2 ended with a clean tier system: Tier 1 substantive, Tier 1.5 modest, retracted. v0.3 preserves this taxonomy.
- The v0.2 round-1 publication review's "What This Doesn't Settle" subsection (the Opus 4.6 steelman) is the seed of the same-orientation rejudge sentinel; it remains the highest-priority methodology fix.
- Construct validity (real-user shadow-mode) is the deepest open question. v0.3 ships executable infrastructure + pre-registered predictions; v0.4 executes powered validation. Pre-registration of predictions is methodologically important: it makes v0.4 falsifiable in a way that no synthetic-personas extension can.
- The Phase 4.4 adaptive TOST closes the v0.2 retraction loop **if cluster-level power says it's decidable**; otherwise v0.3 honestly reports "no detection / no established equivalence" without spending the budget. **Defaulting to skip is the prior; running 4.4b is the conditional branch.**
- The single-rater human calibration (D2) is the weakest deliberate methodology choice in v0.3, deliberately so. The v0.4 upgrade to ≥2 raters is named as the planned fix. **Don't overclaim from n_rater=1.**
- If a v0.3 finding contradicts a v0.2 Tier 1 claim, the v0.2 retraction-as-success pattern is the right framing; document the contradiction in the curated report's claim ledger, not as an erratum.
- **GP4 / R13 (adversarial robustness) and GP6 / R15 (realism stress test)** are optional in v0.3 because they're authoring-intensive and not strictly required to answer the v0.3 personalization / mechanism questions. They're scoped as NICE TO HAVE precisely because cutting them first if budget tightens is a clean cut. v0.4+ work targeting deployment readiness should treat them as required.

---

## 10. Review trail

| Document | Path |
|----------|------|
| Pre-review version (locked 2026-05-18 morning) | `docs/v0_3_plan_2026-05-18_pre-review.md` |
| Consolidated 3-reviewer review (this revision is based on) | `reports/reviews/2026-05-18_consolidated_v0_3_plan_review.md` |
| GPT Pro raw review (29,141 chars, recovered from server history) | `reports/reviews/2026-05-18_gpt-pro_v0_3_plan_review.md` |
| Codex-council raw + synthesis | `~/claudeworkspace/reports/codex-council/2026-05-19-psycheeval-v0-3-plan-review-20260519T055031Z/` |
| GPT Max raw + synthesis (HCOM-coordinated) | `~/claudeworkspace/reports/codex-council/2026-05-19-psycheeval-v0-3-plan-review-gptmax-20260519T055022Z/` |
| Original review bundle sent to reviewers | `reports/reviews/2026-05-18_v0_3_plan_review_bundle.md` |

The pre-review plan's locked decisions and the post-review revisions are tracked in §6. Future reviewers can audit by diffing this plan against `docs/v0_3_plan_2026-05-18_pre-review.md`.
