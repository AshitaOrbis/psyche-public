# PsycheEval v0.3 — Phase -1 Design-Lock

**Date**: 2026-05-18 (initial draft) / 2026-05-19 (decisions sealed)
**Status**: **ALL SUB-ITEMS LOCKED**. Phase -1 sealed; Phase 0 in progress.
**Plan reference**: `docs/v0_3_plan.md` Phase -1 (R1 from consolidated review)
**Cluster-power simulation output**: `drivers/.v0_3_power_sim_fast_output.txt`

## TL;DR — Phase -1 sealed 2026-05-19

| Sub-item | Status | Resolution |
|----------|--------|------------|
| -1.1 Pair manifest | **LOCKED** | T1 (16 pairs) + T2 (12 pairs) + optional T4 (5 pairs); see §-1.1 below |
| -1.2 n table + power memo | **LOCKED** | Power sim confirms D5 not decidable; see §-1.2 below |
| -1.3 Tie policy | **LOCKED — Path A** | Forced-choice primary + ternary sentinel at 10% subset |
| -1.4 Endpoint hierarchy | **LOCKED** | AB/BA pairwise → scalar → sentinel-adjusted → reward-hacking → tie-aware → paraphrased → author-rater → shadow-mode |
| -1.5 Model snapshot freeze | **LOCKED** | gpt-5.4, gpt-5.5-xhigh, claude-opus-4-7; prompts frozen at v0.3 generation |
| **-1.6 MCID justification** | **LOCKED — Option A (±5pp)** ✅ | Approved 2026-05-19. Justified by inter-judge spread + cluster-bootstrap CI half-width + LLM-as-judge literature convention. No Phase 9 circularity. |
| -1.7 Expansion triggers | **LOCKED** | 6 predeclared expansion triggers; exploratory-only labeling |
| **-1.8 D5 decision ledger** | **LOCKED — SKIP D5** ✅ | Approved 2026-05-19. Power sim confirms ±5pp not decidable at v0.3 budgets. C5_CONTRACT vs C3/C4 frames as "no detection, no established equivalence." |
| **-1.9 C5_NONPUBLIC scope** | **LOCKED — Option (a)** ✅ | Approved 2026-05-19. PI-matched nonpublic packets authored; 4 packets in `src/psycheeval/v03_nonpublic_packets.py`; C5_NONPUBLIC + C5_NONPUBLIC_CONTRACT bundles regenerated. |
| -1.10 Scenario audit | **LOCKED** | 12 unique prompt texts across 80 scenarios — flagged as transparency requirement for v0.3 report |
| -1.11 Failure criteria | **LOCKED** | 8 predeclared failure triggers (§8.2 of v0.3 plan) |
| -1.12 Power/margin reconciliation | **LOCKED** | D5 ±5pp decoupled from Phase 9 engagement gap; different scales |

**Phase -1 sealed**. All decisions documented and traceable. Phase 0 condition wiring + analyzer blocks D1–D4 are landed (see latest commits).

---

## -1.1 Fixed pair manifest

Every primary contrast labeled `PRIMARY-CONFIRMATORY`, `SECONDARY-CONFIRMATORY`, `EXPLORATORY-ONLY`, or `NOT-TESTED`. Pre-declared before generation. Phase 6 may add `EXPLORATORY-ONLY` rows only if predeclared expansion triggers fire (-1.7); never add `PRIMARY-CONFIRMATORY` rows post hoc.

### Tier 1 — Personalization probes (locked)

| # | Pair | Label | Judge scope | Persona scope | Expected n_clusters | Headline claim it supports |
|---|------|-------|-------------|---------------|--------------------:|---------------------------|
| T1-01 | C_GENERIC vs C0 | PRIMARY | 3 judges | all 8 | ~80 (8 personas × 10 scenarios) | Generic-contract dominates no-profile |
| T1-02 | C_GENERIC vs C3 | PRIMARY | 3 judges | all 8 | ~80 | Profile-specificity adds value over generic |
| T1-03 | C_GENERIC vs C4 | PRIMARY | 3 judges | all 8 | ~80 | Profile-specificity adds value over generic (with scenario hints) |
| T1-04 | C_GENERIC vs C5 | PRIMARY | 3 judges | PI-only 4 | ~40 | Generic contract vs source-packet, contract present |
| T1-05 | C4_WRONG vs C0 | PRIMARY | 3 judges | all 8 | ~80 | Wrong-profile dominates no-profile (sanity check) |
| T1-06 | C4_WRONG vs C3 | PRIMARY | 3 judges | all 8 | ~80 | Wrong-profile underperforms right-profile (matching axis) |
| T1-07 | C4_WRONG vs C4 | PRIMARY | 3 judges | all 8 | ~80 | Wrong-profile underperforms right-profile (matching axis, with scenario hints) |
| T1-08 | C4_WRONG vs C5 | PRIMARY | 3 judges | PI-only 4 | ~40 | Wrong-profile + matching vs source-packet |
| T1-09 | C5_NONPUBLIC vs C5 | PRIMARY | 3 judges | per -1.9 | TBD by -1.9 | Public-anchor isolation (if -1.9 (a)) or PS-only narrative form (if -1.9 (b)) |
| T1-10 | C5_NONPUBLIC vs C5_CONTRACT | PRIMARY | 3 judges | per -1.9 | TBD by -1.9 | Public-anchor + contract isolation |
| T1-11 | C5_NONPUBLIC vs C3 | SECONDARY | 3 judges | per -1.9 | TBD by -1.9 | Source-packet narrative vs contract-only (no public anchor) |
| T1-12 | C5_NONPUBLIC vs C4 | SECONDARY | 3 judges | per -1.9 | TBD by -1.9 | Same as T1-11, with scenario hints |
| T1-13 | C5_NONPUBLIC_CONTRACT vs C5_NONPUBLIC | PRIMARY | 3 judges | per -1.9 | TBD by -1.9 | C5_CONTRACT > C5 generalization to non-public packets |
| T1-14 | C5_NONPUBLIC_CONTRACT vs C5_CONTRACT | PRIMARY | 3 judges | per -1.9 | TBD by -1.9 | Public-anchor effect when contract is held constant |
| T1-15 | C5_NONPUBLIC_CONTRACT vs C3 | SECONDARY | 3 judges | per -1.9 | TBD by -1.9 | Non-public packet + contract vs contract-only |
| T1-16 | C5_NONPUBLIC_CONTRACT vs C4 | SECONDARY | 3 judges | per -1.9 | TBD by -1.9 | Same as T1-15, with scenario hints |

### Tier 2 — C5_CONTRACT ablation ladder (locked)

| # | Pair | Label | Judge scope | Persona scope | Expected n_clusters | Claim |
|---|------|-------|-------------|---------------|--------------------:|-------|
| T2-01 | L0 (C5) vs L1 | PRIMARY | 3 judges | PI-only 4 | ~40 | Marginal contribution of contract presence |
| T2-02 | L1 vs L2 | PRIMARY | 3 judges | PI-only 4 | ~40 | Marginal contribution of anti-mimicry |
| T2-03 | L2 vs L3 | PRIMARY | 3 judges | PI-only 4 | ~40 | Marginal contribution of contract-first ordering |
| T2-04 | L3 vs L4 (C5_CONTRACT) | PRIMARY | 3 judges | PI-only 4 | ~40 | Marginal contribution of expanded length |
| T2-05 | L1 vs C5_CONTRACT | SECONDARY | 3 judges | PI-only 4 | ~40 | Cumulative effect of L2+L3+L4 components |
| T2-06 | L1 vs C5 | SECONDARY | 3 judges | PI-only 4 | ~40 | Effect of contract presence alone (anchor to T2-01) |
| T2-07 | L2 vs C5 | SECONDARY | 3 judges | PI-only 4 | ~40 | Effect of contract + anti-mimicry |
| T2-08 | L3 vs C5 | SECONDARY | 3 judges | PI-only 4 | ~40 | Effect of contract + anti-mimicry + contract-first |
| T2-09 | L3 vs C5_CONTRACT | SECONDARY | 3 judges | PI-only 4 | ~40 | Pure length effect (everything else held constant — anchor to T2-04) |
| T2-10 | L1 vs C3 | SECONDARY | 3 judges | PI-only 4 | ~40 | L1 (C5 + minimal contract, packet-first, length-matched-to-C5) vs C3 (contract-only) |
| T2-11 | L2 vs C3 | SECONDARY | 3 judges | PI-only 4 | ~40 | L2 vs C3 |
| T2-12 | L3 vs C4 | SECONDARY | 3 judges | PI-only 4 | ~40 | L3 (contract-first, packet, anti-mimicry, length-matched) vs C4 (contract + hints) |

### Tier 3 — D5 adaptive (run only if -1.8 + -1.2 gates pass)

| # | Pair | Label | Judge scope | Persona scope | Expected n_clusters | Claim |
|---|------|-------|-------------|---------------|--------------------:|-------|
| T3-01 | C5_CONTRACT vs C3 (D5) | PRIMARY-CONDITIONAL | 3 judges | PI-only 4 | ~240 (v0.2 120 + v0.3 120) | Equivalence within ±MCID (-1.6) |
| T3-02 | C5_CONTRACT vs C4 (D5) | PRIMARY-CONDITIONAL | 3 judges | PI-only 4 | ~240 | Equivalence within ±MCID (-1.6) |

**Conditional on Phase -1.8 + Phase -1.2 gates**. If gates fail: skip and report "no detection, no established equivalence" framing.

### Optional NICE TO HAVE — adversarial + realism slice

| # | Pair | Label | Judge scope | Persona scope | Expected n_clusters | Claim |
|---|------|-------|-------------|---------------|--------------------:|-------|
| T4-01 | C4_ADVERSARIAL vs C4 | EXPLORATORY | 3 judges | adversarial-4 | ~40 | Adversarial profile robustness (GP4 / R13) |
| T4-02 | C4_ADVERSARIAL vs C0 | EXPLORATORY | 3 judges | adversarial-4 | ~40 | Same |
| T4-03 | C4_REALISM_SPARSE vs C4 | EXPLORATORY | 3 judges | realism-6 | ~60 | Sparse-profile robustness (GP6 / R15) |
| T4-04 | C4_REALISM_CONTRADICTORY vs C4 | EXPLORATORY | 3 judges | realism-6 | ~60 | Contradictory-profile robustness |
| T4-05 | C4_REALISM_OVERLY_DETAILED vs C4 | EXPLORATORY | 3 judges | realism-6 | ~60 | Overly-detailed-profile robustness |

### Pair-set summary

| Tier | # pair types | Total clusters expected | AB/BA records (×2 judges × 2 swap) |
|------|-------------:|-------------------------|------------------------------------|
| T1 | 16 | ~1,000 cluster-pairs | ~12,000 AB/BA records (3 judges) |
| T2 | 12 | ~480 cluster-pairs | ~5,760 AB/BA records (3 judges) |
| T3 (adaptive) | 2 | ~480 cluster-pairs combined | ~5,760 (or 0 if skipped) |
| T4 (optional) | 5 | ~260 cluster-pairs | ~3,120 (or 0 if skipped) |

**Total without T3 or T4**: ~17,760 AB/BA records, matches §7 budget rollup for "without D5 4.4b".

---

## -1.2 Per-cell n table + cluster-bootstrap power memo

Computed via `drivers/v0_3_cluster_power_sim.py`. **See full output at `drivers/.v0_3_power_sim_output.txt`**. The simulation uses cluster-bootstrap (not Wilson) on synthetic binary AB/BA records with two ICC scenarios: 0.0 (optimistic, no intra-cluster correlation) and 0.30 (moderate, realistic for persona × scenario × author).

### Key power findings (computed; full output at `drivers/.v0_3_power_sim_fast_output.txt`)

The simulator tested power at three margins (±3pp, ±5pp, ±7pp) and four n_clusters scenarios (v0.2 alone n=240, 2× n=480, 3× n=720, 4× n=1000) for the two D5 pairs (C3_vs_C5_CONTRACT, C4_vs_C5_CONTRACT) under two ICC scenarios (0.0 optimistic, 0.30 realistic).

**Summary — power to declare equivalence under true equipoise (lo_win=0.5):**

| n_clusters | n_records | ICC | ±3pp | ±5pp | ±7pp |
|-----------:|----------:|----:|-----:|-----:|-----:|
| 120 (v0.2 alone) | 240 | 0.00 | 0% | 0% | 11% |
| 120 (v0.2 alone) | 240 | 0.30 | 0% | 0% | 0% |
| 240 (1× v0.3 add) | 480 | 0.00 | 0% | 19% | 72% |
| 240 (1× v0.3 add) | 480 | 0.30 | 0% | 1% | 57% |
| 360 (2× v0.3 add) | 720 | 0.00 | 0% | 50% | 93% |
| 360 (2× v0.3 add) | 720 | 0.30 | 0% | 22% | 80% |
| 500 (3× v0.3 add) | 1000 | 0.00 | 0% | 77% | 99% |
| 500 (3× v0.3 add) | 1000 | 0.30 | 0% | 59% | 97% |

### Critical finding: ±5pp is not decidable at any v0.3-feasible budget

- **±3pp**: 0% power at every scenario. Margin is too tight for cluster-bootstrap CI at any n the v0.3 budget can afford.
- **±5pp under realistic ICC=0.30**: only **59% power at n_clusters=500** (n_records=1000, ~4× v0.2's pair n). This is below the 80% threshold and would require nearly 5× expansion to reach decidable.
- **±7pp under realistic ICC=0.30**: reaches 80% at n_clusters=360 (2× expansion, n_records=720). Decidable but on a margin below the inter-judge spread floor (~5pp), making the equivalence claim methodologically uninformative.

### Implications for D5 (-1.8)

The pre-review D5 plan (Phase 4.4, ~3,750 additional pairs to expand from v0.2's n_clusters=120 to ~240) would land **below the 1× expansion row**: still ~1% power at ±5pp / ICC=0.30. The power simulation directly confirms the consolidated review's prediction that D5 is overcommitted at the pre-review margin and budget.

**Three coherent decision branches now have evidence**:

1. **Skip D5 entirely** (Empiricist + Skeptic recommendation): power says ±5pp is undecidable at reasonable budget. v0.3 frames C5_CONTRACT vs C3/C4 as "no detection, no established equivalence" — same as the v0.2 report. This is the **recommended default** in -1.8.
2. **Run D5 at ±7pp under ICC=0.30** (loose margin, decidable): n_clusters=360 reaches 80% power. But ±7pp is below the inter-judge spread floor; "equivalence within ±7pp" is methodologically uninformative since the measurement system has ~±5pp resolution. Not recommended.
3. **Run D5 at ±5pp with a much bigger expansion**: would need n_clusters ≥ 600-800 (~3,500-5,000 additional pairs × 3 judges = ~16,000-22,000 calls). Outside v0.3 budget.

**Updated -1.8 recommendation: skip D5 entirely** — the power simulation confirms it's not decidable at v0.3-feasible budgets and the residual question (whether C5_CONTRACT vs C3/C4 is "really equivalent" or just "no detection") is better served by v0.3's T2 mechanism ablation ladder, which directly answers the question of what C5_CONTRACT does that C3/C4 doesn't.

### Per-cell n table for v0.3 primary contrasts

| Pair type | Persona scope | n_personas | n_scenarios/persona | n_authors | n_clusters | n_records (AB+BA) |
|-----------|--------------|------------:|--------------------:|----------:|-----------:|------------------:|
| T1 all-persona pairs | all 8 | 8 | 10 | 3 | 240 | 480 |
| T1 PI-only pairs | PI 4 | 4 | 10 | 3 | 120 | 240 |
| T2 ladder pairs | PI 4 | 4 | 10 | 3 | 120 | 240 |
| T3 D5 pairs (combined v0.2+v0.3) | PI 4 | 4 | 10 | 3 | 240 | 480 |
| T4 optional pairs | adversarial-4 or realism-6 | 4-6 | 10 | 3 | 120-180 | 240-360 |

Note: per-pair n_records is what one judge contributes. Multiply by 3 judges for total AB/BA records per pair type. Cluster bootstrap unit is persona × scenario × author (not multiplied by judge — judges are pooled).

---

## -1.3 Tie policy — LOCKED as Path A

**Decision**: Forced-choice pairwise prompt is the **primary** v0.3 prompt (matches v0.2). Tie/equipoise is a **separate ternary sentinel** on a 10% subset.

**Rationale**:
- Preserves comparability with v0.2 corpus for any pooled analyses (especially D5 TOST if it runs)
- The ternary sentinel still surfaces the tie rate without contaminating headline numbers
- If the sentinel reveals tie rate >25% on a critical pair, Phase 6 (or §8.2 failure criteria) downgrades that pair's claim
- Path B (ternary primary + v0.2 rejudge) was estimated at ~1,500 additional v0.2 rejudge calls; Path A saves that budget

**Implementation**:
- Forced-choice prompt: existing `psycheeval/prompts/07_pairwise_judge.md` (unchanged)
- Ternary prompt: new `prompts/07b_pairwise_judge_ternary.md` (Phase 0 work)
- Sentinel sampling: 10% stratified by pair type, AB/BA-mandatory (every ternary record gets swap rejudgment)

**Tie-record handling in pooled analyses** (if D5 runs):
- Ternary sentinel records are NOT pooled with forced-choice for TOST
- TOST uses forced-choice only; ternary sentinel produces a sensitivity statistic reported alongside

---

## -1.4 Endpoint hierarchy — LOCKED

When signals conflict, the order for each headline claim is:

| Priority | Signal | Why this priority |
|---------:|--------|-------------------|
| 1 | AB/BA-controlled pairwise (forced-choice primary) with cluster-bootstrap CI | Most v0.2-comparable; primary inference signal |
| 2 | Anchored scalar Δ_total with cluster-bootstrap CI | Independent signal; v0.2 retraction was driven by scalar–pairwise mismatch |
| 3 | Same-orientation sentinel-adjusted controlled rate (D1 block) | Position-bias-net-of-retest-noise, but flagged as descriptive (R11) |
| 4 | Reward-hacking-controlled pairwise (D3 block regression) | Judge preference after surface-feature covariates |
| 5 | Tie-aware ternary lo_win on 10% sentinel (D4 block) | Sensitivity check; flag if tie rate >25% |
| 6 | Paraphrased-anchor scalar (D2 block) | Robustness check on scalar |
| 7 | Author-rater direction agreement (D5 block, n=1) | Sanity check only, NOT calibration |
| 8 | Shadow-mode engagement gap (v0.4, not v0.3) | The construct-validity bridge |

**Conflict rules**:
- Pairwise vs scalar disagree on direction → headline claim is downgraded to "channel-mismatch ambiguity" and held back from the Tier 1 list
- Same-orientation noise floor exceeds AB/BA flip rate → claim from that pair is downgraded to descriptive only
- Author-rater disagrees with judge majority on >40% of pairs → flagged in the v0.3 report's limitations section, NOT used to invalidate judge claims (n=1 limitation)
- Tie rate on the ternary sentinel >25% on a critical pair → forced-choice headline for that pair is annotated with "tie-aware reinterpretation suggests substantial equipoise"

---

## -1.5 Model snapshot freeze — LOCKED

All judging and authoring uses these exact model IDs for the entire v0.3 run. Re-running with different IDs invalidates v0.2 + v0.3 pooling.

| Role | Model ID | Reasoning effort | Provider | Pin source |
|------|----------|------------------|----------|------------|
| Author | `gpt-5.4` | default | OpenAI | matches v0.2 |
| Author | `gpt-5.5-xhigh` | xhigh | OpenAI | matches v0.2 |
| Author | `claude-opus-4-7` | default | Anthropic | matches v0.2 |
| Judge | same as authors | same | same | same |

**Cap-window stratification**: every judging call records the cap window it was made in (timestamp bucket). v0.2 used persona × scenario × author × judge × cap_window as the diagnostic cell unit; v0.3 carries this forward. The analyzer reports per-cap-window judge preference rates as a sentinel for model drift.

**Prompt freeze**: all v0.3 prompts (06b_judge_anchored.md, 07_pairwise_judge.md, new 07b_pairwise_judge_ternary.md) are committed to git before Phase 1 generation. Hash recorded in metrics JSON.

**Model drift sentinel**: if per-cap-window judge preference rates deviate by >5pp from the v0.2 baseline on common conditions, the analyzer flags model drift in `validation_warnings.jsonl`. Mid-run rerouting if drift confirmed.

---

## -1.6 MCID justification — **DEFER → DECISION NEEDED**

**The problem**: pre-review plan justified the ±5pp TOST margin via Phase 9 deployment relevance. Phase 9 was design-only. The justification was circular. This Phase -1 sub-item closes the loop by establishing the MCID **independent of any unexecuted shadow-mode**.

### Recommended default: ±5pp with prior-literature justification

The ±5pp margin can be defended without leaning on Phase 9 if we ground it in:
1. **Inter-judge disagreement floor**: v0.2 showed gpt-5.4 vs gpt-5.5 vs Opus controlled-rate spread of roughly ±5pp on the same pairs. Any effect smaller than the inter-judge floor is below the resolution of the measurement system, regardless of deployment context.
2. **Cluster-bootstrap CI half-width baseline**: at v0.2's n=288 per pair, the 95% CI half-width was roughly ±6pp on near-equipoise pairs. ±5pp is just inside that resolution. Tighter (±3pp) would require multiplying n by 3-4x; looser (±7pp) is below the inter-judge spread.
3. **Methodological convention**: equivalence-margin literature in LLM-as-judge work typically uses ±5pp as a round-number floor. Cites Liu et al. 2024 / Chiang et al. 2023 conventions.

### Three options for the user

**Option A (recommended): ±5pp, justified by inter-judge spread + measurement resolution + literature convention.** Phase 9 retroactively informs but is not load-bearing.

**Option B: ±3pp tight margin, deployment-aspirational.** Pre-commits to a tighter equivalence claim that would be more publishable but requires n_clusters ≥500 per pair (likely outside v0.3 budget). Skip D5 in v0.3 entirely; defer equivalence to v0.4 with shadow-mode data.

**Option C: ±7pp loose margin, conservative.** ±7pp is below the inter-judge spread, so equivalence at this margin is uninformative. Effectively says "we don't claim equivalence; we claim no detection." If chosen, just demote D5 entirely.

### Recommendation
**Go with Option A**. The justification is defensible without Phase 9, the n required is achievable in v0.3 (per -1.2 power sim), and the methodological convention is publishable.

### Decision (user fills in)

```
[ ] Option A (±5pp, inter-judge + CI half-width + literature convention) — RECOMMENDED
[ ] Option B (±3pp tight, defer D5 to v0.4)
[ ] Option C (±7pp loose, demote D5 entirely)
```

---

## -1.7 Phase 6 expansion triggers — LOCKED

Pre-declared. Phase 6 may add `EXPLORATORY-ONLY` rows to the pair manifest if (and only if) one of these triggers fires. Triggered expansions are **never** promoted to PRIMARY-CONFIRMATORY for v0.3 headline claims.

| # | Trigger | Expansion |
|---|---------|-----------|
| E-01 | T1-09 (C5_NONPUBLIC vs C5) controlled lo_win straddles 0.5 with CI half-width >10pp | Add T1-12-extended: C5_NONPUBLIC vs C5 stratified by persona pair (within-persona vs cross-persona comparison if -1.9 allowed) |
| E-02 | T2-01 (L0 vs L1) shows null effect (effect <5pp from 0.5) | Add T2-13: pure C5 baseline with NO contract markers vs L0, to verify L0 isn't already partially contracted |
| E-03 | C_GENERIC beats C3/C4 by >10pp | Add T1-extended: C_GENERIC vs C_GENERIC_SHORT (length-controlled variant) |
| E-04 | C4_WRONG ≈ C0 in any T1 contrast | Add T1-extended: C4_WRONG with a different mismatch mapping strategy (random mismatch vs opposite-trait mismatch) |
| E-05 | Same-orientation sentinel flip rate ≥80% of AB/BA flip rate on >50% of pairs | Add diagnostic block: per-judge retest reliability at scalar (not pairwise) |
| E-06 | Per-judge controlled lo_win disagreement >0.15 on any PRIMARY pair | Add per-judge cluster-bootstrap subset analysis (3 separate CIs reported instead of pooled) |

**No other expansion triggers may add manifest rows.** Phase 6 analysis can re-slice existing pairs (by persona, family, length bucket) without triggering, since those slices were already part of the v0.2 diagnostic structure.

---

## -1.8 D5 decision ledger — **DEFER → DECISION NEEDED**

**The question**: Does any v0.3 report claim or v0.4 decision require an established equivalence result on C5_CONTRACT vs C3 or vs C4? If yes, D5 (Phase 4.4b) runs. If no, D5 is skipped and the report frames as "no detection, no established equivalence."

### Why this matters

The v0.2 report retracted the C5_CONTRACT > C3 and > C4 headlines with "no detection." The blog post round-1 publication review flagged that "no detection ≠ established equivalence" — the CIs still permit small effects. Establishing equivalence requires Phase 4.4b (tie-aware rejudge of just the collapsed edges, ~2,400 calls).

**The cost**: ~$40 codex + 1 Opus cap window if 4.4b runs.
**The information gain**: convert "no detection" → "established equivalence within ±MCID" for two specific pairs.

### When is equivalence load-bearing?

Equivalence is load-bearing for v0.3 if (and only if) one of these claims appears in the v0.3 report:
1. "C5_CONTRACT is functionally interchangeable with C3 for deployment" — implies equivalence
2. "Source packets contribute no marginal value over contracts" — needs equivalence to support the "no marginal value" framing
3. "The v0.2 retraction is settled, not provisional" — needs equivalence

If none of those claims appear, **D5 isn't load-bearing**. The "no detection" framing is honest and sufficient.

### Recommendation (strengthened by -1.2 power findings)

**SKIP D5 in v0.3** — the power simulation confirms ±5pp is undecidable. Reasoning:
- **Power evidence**: at realistic ICC=0.30, even 3× v0.3 expansion (~$200 extra) gives only 59% power at ±5pp. To reach 80% power at ±5pp would require ~5× expansion (outside v0.3 budget).
- v0.3 already has 5 mechanism-decomposition conditions in the T2 ablation ladder that more directly answer the "what does C5_CONTRACT do that C5 doesn't" question
- The blog post 046 already shipped with "no detection" wording and reviewers accepted it
- Equivalence is more interesting **after** v0.3 mechanism ablations clarify what we're claiming equivalence about
- v0.4 with shadow-mode + tighter ICC estimates is the better home for equivalence claims
- ~$40 + 1 cap window is small budget savings, but the bigger gain is not pre-committing to an equivalence margin before knowing what the mechanism work will surface

### Decision (user fills in)

```
[X] Skip D5 (Phase 4.4b) entirely; v0.3 retains "no detection" framing — RECOMMENDED (power-confirmed)
[ ] Run D5 (Phase 4.4b) at ±7pp loose margin (decidable but methodologically uninformative)
[ ] Run D5 unconditionally with much bigger expansion (outside v0.3 budget)
```

---

## -1.9 C5_NONPUBLIC scope decision — **DEFER → DECISION NEEDED**

**The bug being fixed**: pre-review plan defined C5_NONPUBLIC for PS personas only but paired against PI-only C5 and C5_CONTRACT (R2 / consensus). The comparison confounded public-anchor effect with persona-population scope.

### Two paths

**(a) PI-matched nonpublic packets** (cleaner, more authoring):
- Author 4 nonpublic source packets for the same 4 PI personas
- These are biographical narrative prose for the existing PI personas, but without referencing public sources
- Pair C5_NONPUBLIC vs C5 within-persona: same persona, public packet vs nonpublic packet
- **Cost**: ~4-6h authoring (need to write 4 biographical narratives that match the existing PI personas' established traits without using public facts about the inspiring real people)
- **Benefit**: Clean public-anchor isolation. The headline claim becomes "public-anchor narrative form has [no effect / a small effect / a large effect] over a matched nonpublic narrative on the same persona."

**(b) PS-only narrow claim** (cheaper, less informative):
- Keep C5_NONPUBLIC at PS personas only
- Drop the C5_NONPUBLIC vs C5 / C5_CONTRACT pairs from the manifest entirely
- New headline: "PS-only synthetic-narrative source packets behave [similar to / different from] PI source packets when contract is held constant"
- **Cost**: ~1h authoring (4 simple PS packet narratives)
- **Benefit**: tests whether the source-packet effect generalizes to non-PI personas at all. Doesn't isolate public-anchor.

### Recommendation

**Option (a) PI-matched authoring** if v0.3 has authoring budget. The 4-6h is small relative to the v0.3 timeline, and the public-anchor isolation is one of the v0.3 plan's stated load-bearing questions.

**Option (b)** if you'd rather minimize authoring overhead and accept that public-anchor isolation slips to v0.4.

### Decision (user fills in)

```
[ ] Option (a) PI-matched nonpublic packets (4-6h authoring, public-anchor isolated) — RECOMMENDED
[ ] Option (b) PS-only narrow claim (1h authoring, public-anchor deferred to v0.4)
```

---

## -1.10 Scenario-set audit — LOCKED (findings)

Pre-flight check of `data/v02_hard_pilot/scenarios.jsonl` (80 scenarios) for contamination, staleness, and profile-legibility. v0.3 inherits the v0.2 scenario set; no changes proposed unless the audit surfaces blocking issues.

### Audit findings

| Concern | Finding | Severity | Action |
|---------|---------|---------|--------|
| **Scenario family balance** | 8 families: ambition_status (8), authority_disagreement (8), creative_feedback (8), epistemic_uncertainty (8), interpersonal_conflict (16), moral_uncertainty (8), procrastination_avoidance (8), shame_self_interpretation (16) | LOW | Acceptable. Two families (interpersonal_conflict, shame_self_interpretation) have 2x the others — acknowledge in v0.3 analysis but no fix needed |
| **Difficulty distribution** | 40 scenarios at difficulty 4, 40 at difficulty 5. **Mean difficulty = 4.5**, not 3.58 as quoted in v0.2 report §1. The "3.58" figure is stale. | LOW | Update v0.3 report to quote actual mean difficulty 4.5 |
| **Unique prompt count** | 80 scenarios but **only 12 unique `user_prompt` texts** (1-2 per family). Same prompt text reused across multiple users per family (e.g., 8 users × 1 prompt for ambition_status). | **MEDIUM** | Same-prompt-different-user is by design (controls for prompt while varying persona), but should be **explicitly documented** in v0.3 report as a methodological choice. The 12-unique-prompt count is the true "stimulus variety" denominator. |
| **Profile-legibility** | Reading 5 random scenarios: prompts are deliberately ambiguous about ground-truth correct response (e.g., "Help me write a message that makes them understand how cruel they are" — the latent need is to NOT write that message). Profile-conditioning should help identify the right action; the prompts don't telegraph it. | LOW | No fix needed. Acknowledge in v0.3 report. |
| **Contamination** | Prompts don't reference public figures, IDs, or external systems. No obvious training-data overlap. | LOW | No fix. |
| **Staleness** | All scenarios authored 2026-04 era. Current relative to v0.3 timing. | LOW | No fix. |

### Audit conclusion

**No blocking issues**. The MEDIUM finding (12 unique prompt texts across 80 scenarios) is a transparency issue, not a correctness issue: v0.3 should explicitly state in §3 of the curated report that the corpus has 80 user-scenario pairs but 12 unique prompts. This makes the cluster unit (persona × scenario × author, where "scenario" is the user-scenario pair) honest.

### Recommendation for v0.4+

Consider expanding to 25-30 unique prompts before the formal paper. The current "8 family × 1 prompt × 8 users" design has prompt-as-fixed-effect concerns that adding prompt variety per family would address.

---

## -1.11 Failure criteria — LOCKED (from §8.2 of revised plan)

Predeclared at the same level of detail as success criteria. Any of the 8 triggers in §8.2 of `v0_3_plan.md` downgrades the relevant headline claim from confirmatory to exploratory or removes it entirely. **Repeated here verbatim for the design-lock record**:

1. Paraphrased-anchor sentinel produces ≥0.5 SD mean-shift or changes condition rankings at any judge → all scalar claims downgraded.
2. Tie rate in ternary sentinel exceeds 25% on a C5_CONTRACT-edge pair → that pair's package claim is downgraded.
3. Author-rater direction agreement <60% on the 50-pair sample → all LLM-judge preference claims annotated with divergence warning.
4. C4_WRONG_PROFILE wins against C_GENERIC at >55% → personalization claim downgraded ("profile mismatch does not measurably harm responses").
5. C5_NONPUBLIC (if -1.9 (a) is chosen) shows behavior indistinguishable from C5 → public-anchor effect downgraded.
6. Same-orientation sentinel flip rate ≥AB/BA flip rate on >50% of pairs → AB/BA decomposition unstable; position-bias-net estimates are descriptive only.
7. Opus and OpenAI judges diverge by >0.15 on any T1 controlled lo_win → judge-unanimous wording dropped on that pair.
8. Reward-hacking diagnostic regression shows >50% of judge-preference effect explained by output length / profile-reference count alone → mechanism claim for that pair requires the covariate-controlled model.

**If ≥3 failure triggers fire**: the v0.3 report opens with a "what didn't work" section before any headline claim. Symmetric to v0.2's retraction-as-success pattern.

---

## -1.12 Phase 9 power / D5 margin reconciliation — LOCKED pending -1.6

Pre-review plan had Phase 9 power at "80% / 7pp engagement gap" and D5 margin at "±5pp pairwise win rate." These were quoted as independent. They are not independent: D5 used Phase 9 deployment relevance to justify ±5pp; Phase 9 used its own 7pp target. **The two numbers should be consistent.**

### Reconciliation

- D5 margin (-1.6 decision): proposed ±5pp on LLM pairwise win rate
- Phase 9 engagement gap: real-user engagement-rate Δ that is "deployment-relevant"
- **These are different scales**. A 5pp LLM pairwise win rate gap does not equal a 5pp real-user engagement gap.

**Decision**: decouple them.

| Metric | Scale | Margin | Justification |
|--------|-------|--------|---------------|
| D5 TOST | LLM pairwise lo_win rate, 0-100% | ±5pp (per -1.6 Option A) | Inter-judge spread floor + cluster-bootstrap CI half-width + literature convention |
| Phase 9 engagement target | real-user engagement rate, 0-100% | not yet calibrated | Set at 80% power for whatever engagement-rate Δ is feasible at expected v0.4 traffic (~10pp at n=200/arm) |

**The Phase 9 design doc (Phase 9.1) explicitly states**: the LLM-judge pairwise margin and the real-user engagement gap are different metrics; v0.4's pre-registered predictions are the bridge between them, and the bridge's validity is what shadow-mode is testing.

This removes the circular justification: D5's ±5pp is no longer pinned to Phase 9; Phase 9's engagement gap is a separate concept that v0.4 will measure.

---

## Remaining work — Phase 0 (after user decisions on -1.6, -1.8, -1.9)

Once the three deferred decisions are made:

| Phase 0 sub-task | Status | Estimate |
|------------------|--------|----------|
| Add 8 base conditions + optional 2 (adversarial, realism) to `Condition` enum | autonomous | 30 min |
| Author C_GENERIC template (strip C4 profile specifics) | autonomous | 1 h |
| Author T2 ladder templates L1, L2, L3 | autonomous | 1.5 h |
| Author C5_NONPUBLIC packets per -1.9 decision | requires -1.9 | 4-6 h (option a) or 1 h (option b) |
| Optional adversarial profiles | autonomous | 2 h |
| Optional realism stress profiles | autonomous | 2 h |
| Build `--ab-ba-mandatory` flag | autonomous | 1.5 h |
| Implement analyzer blocks D1-D4 | autonomous | 2.5 h |
| Author ternary `07b_pairwise_judge_ternary.md` | autonomous | 30 min |
| Tests for new wiring + analyzer blocks | autonomous | 1.5 h |

**Total autonomous Phase 0 work I can do tonight: ~10-12 hours of focused work**. I will start with everything that doesn't depend on -1.9 and produce code changes ready to commit. The C5_NONPUBLIC authoring waits for the -1.9 decision.

---

## -1.13 Phase 5 human-rater selection rule — LOCKED 2026-05-19 afternoon

**Predeclared before observing v0.3 pairwise data.** Single author-rater sanity check; n=1; NOT calibration (per Phase 5 / R8). Rule fixed before pairwise scores produced to prevent post-hoc effect-driven sampling.

### Sampling target: 50 pairs

| Stratum | n | Source | Selection within stratum |
|---------|---|--------|--------------------------|
| **T1 PRIMARY pair types** (16 types) | 32 | v0.3 pairwise records | 2 pairs per pair-type; deterministic seed=42; stratify by (judge, persona); skip pair-type only if it has <2 records |
| **T2 PRIMARY ladder steps** (4 steps: L0vL1, L1vL2, L2vL3, L3vL4) | 8 | v0.3 pairwise records | 2 pairs per ladder step; same deterministic stratification |
| **v0.2 calibration anchors** (high-confidence v0.2 pairs) | 10 | v0.2 pairwise records | Sample from pairs where all 3 v0.2 judges agreed on winner (3-of-3 unanimous); spread across {C4 vs C0, C4 vs C5, C5_CONTRACT vs C5, C4 vs C1_padded}; deterministic seed=42 |
| **Total** | **50** | | |

### Stratification details (within-stratum)

1. Within each pair-type, group records by `(judge_model, user_id)` cell.
2. Sample uniformly across cells using `random.Random(seed=42)`.
3. **Skip records where `winner == "tie"`** (rater can't sanity-check what the judge couldn't decide).
4. If a stratum has fewer records than its target n, take all available records and note the shortfall in the manifest.

### Pair anonymization

The rater MUST be blinded to:
- The condition labels (presented as "Response A" and "Response B" with random A/B assignment per pair, seed=43)
- The author model
- The LLM judges' verdicts
- The pair-type membership

Rater sees: scenario prompt, profile (if any — depends on condition; the rater knows the condition exists but not which), Response A, Response B. Rater records: winner (A/B/tie), 0-10 scalar on 3 dimensions (helpfulness, profile_fit, anti_sycophancy), brief rationale.

### Rater's blinding to LLM-judge results

Per R11 (sequencing fix): rater scores all 50 pairs BEFORE the metric JSON for those pairs is consulted. Operationally: the selection script writes the 50-pair manifest to `runs/<TAG>/human_rater_inbox.jsonl` (with anonymized A/B). The rater CLI consumes it, writes `runs/<TAG>/human_rater_responses.jsonl`. The analyzer (D5 block) joins these post-hoc against the LLM-judge results.

### What v0.3 reports

The D5 analyzer block computes:
- Per-pair direction agreement: fraction of pairs where rater winner matches majority LLM-judge winner (3 judges)
- Pearson r between rater scalar Δ (3-dim mean) and LLM scalar Δ (10-dim mean from anchored_judge_scores)
- Bootstrap 95% CI on the agreement rate (n=50, single rater)

**Reporting language**: "author-rater sanity check, n=1, NOT a calibration benchmark." v0.4 upgrade to ≥2 raters named as the planned fix. v0.3 does NOT use this as construct-validity evidence; it is reported alongside reward-hacking diagnostics as a triangulation cue, not a primary claim.

### Failure handler

If author-rater agreement < 60% (failure trigger #3 in §8 of v0.3 plan), LLM-judge claims get a flag in the claim ledger; this does NOT retract any specific headline.

### Selection-script invariants

- Deterministic: seed=42 for pair selection, seed=43 for A/B side randomization
- Anonymization preserved across re-runs (same input pairwise file → same anonymized manifest)
- Re-runnable: rerunning regenerates the same 50-pair manifest from the same pairwise_scores.jsonl
- Sample-target tolerance: if a stratum is short, the script reports the shortfall but does NOT pad from other strata

**Script path**: `drivers/select_human_rater_pairs.py`.
**Rater CLI**: `drivers/rater_cli.py`.
**Analyzer block**: D5 in `src/psycheeval/analyze.py`.

---

## Sign-off checklist

For the user when they review:

- [ ] -1.1 Pair manifest reviewed
- [ ] -1.2 Power memo reviewed (see drivers/.v0_3_power_sim_output.txt)
- [ ] -1.3 Tie policy = Path A approved
- [ ] -1.4 Endpoint hierarchy approved
- [ ] -1.5 Model snapshot freeze approved
- [ ] **-1.6 MCID option chosen** (A / B / C)
- [ ] -1.7 Expansion triggers approved
- [ ] **-1.8 D5 decision** (skip / conditional / unconditional)
- [ ] **-1.9 C5_NONPUBLIC scope** (PI-matched / PS-only)
- [ ] -1.10 Scenario audit findings noted
- [ ] -1.11 Failure criteria approved
- [ ] -1.12 Power/margin reconciliation noted
- [ ] **-1.13 Phase 5 selection rule** (added 2026-05-19 afternoon; predeclared before v0.3 pairwise data exists)

Once the bolded items have decisions, Phase 0 generation can begin in full. The unbolded items can be revised but the plan is workable as-is.
