# PsycheEval v0.2 — Hard Pilot Final Report

**Tag**: `2026-04-26_v02_hard_codex_only` (anchored 0–10 rubric, harder scenario set, C5_CONTRACT condition added, full AB/BA counterbalanced rejudging)
**Status**: Final. Supersedes v0.1 on the questions v0.2 was designed to answer.
**Date**: 2026-05-18
**Audit trail**: 12 same-data Phase 0 audits + Phase 1 AB/BA on 6 headline pairs (1,784 swap records) + Phase 2 hygiene pass (13 fixes; round-2 external review) + Opus C4 vs C5 fill (240 calls, zero cap events).

---

## 1. TL;DR

v0.2 was designed to test five questions the v0.1 review left open. Two questions are now empirically settled; two are settled in the opposite direction the v0.2 plan expected; one is reframed as a deferred mechanism question. A separate methodological result — emergent from the AB/BA correction — is now the strongest single contribution v0.2 makes.

**Tier 1 (the surviving substantive claims, position-bias-controlled and cluster-bootstrapped):**

- **C5_CONTRACT > C5**: 67.7% under counterbalanced judging [61.7, 73.3]. Adding a structured behavioral contract to a source-packet condition (C5) substantially improves it. The effect is judge-unanimous, persona-robust, family-robust, scalar-aligned (Δ_total +3.057 on a 0–100 anchored scale), and survives a joint position + length correction (64.9% in the length-similar subset, CI [52.9, 76.2]). **Mechanism not isolated**: the C5_CONTRACT package differs from C5 on ≥4 dimensions simultaneously (contract presence, ordering, anti-mimicry language, profile length). v0.3 ablations (`C_GENERIC_CONTRACT`, `C5_CONTRACT_SHORT`) are required for mechanism claims.

- **C4 > C5**: 68.0% under counterbalanced judging [61.5, 74.4]. Behavioral contract (C4) beats the bare source-packet condition (C5). Judge-unanimous: gpt-5.4=0.681, gpt-5.5=0.681, Opus=0.679 — three independent judges converge on essentially the same rate. Joint position+length correction holds (67.4% [54.7, 79.5]). This pair was originally scope-limited (Opus had 0 records); the 2026-05-17 Opus fill (240 calls, zero cap events) closed the gap.

- **C4 > C1_padded**: 62.3% under counterbalanced judging [56.1, 68.3]. Behavioral contract beats length-matched baseline. Length-control + position-control both pass. Scope: gpt-5.4 + gpt-5.5 judges only (Opus has 0 records on this pair, like all non-C5_CONTRACT-edge pairs in v0.2's original scope).

- **C0 dominated by every profile condition**: pairwise win rate 86.6% C4-over-C0 in originals, scalar Δ_total +6.075 / 100 in favor of C4. Not AB/BA-tested directly, but the effect size is well outside the measured ~15-17 pp slot-B preference range, so it is very unlikely to be entirely a position-bias artifact.

**Tier 1.5 (modest, real):**

- **C4 > C4_shuffled**: 57.8% under counterbalanced judging [52.2, 63.7]. Coherent-order C4 beats shuffled-order. This is a *sign correction* of the v0.2 plan's original "no significant difference at 51.9%" headline — the original was understating because slot-A position bias (which penalized C4 in its constant slot A) was suppressing the apparent margin. Effect size is meaningfully smaller than the 17-19 pp Tier 1 effects elsewhere, so the curated report uses "modest" rather than "significant" wording.

**Tier 2 (the original v0.2 headlines that did not survive):**

- **C5_CONTRACT vs C3**: original 57.2% C5_CONTRACT win rate **collapses to 49.9%** [43.4, 56.4] under counterbalanced judging. No detected preference. Scalar Δ_total −0.053 (essentially zero). The published v0.2 headline (the "C5_CONTRACT outperforms C3" wording from the original v0.2 plan, now retracted) was carried entirely by a systematic ~15-17 pp slot-B position bias in two of three judges.

- **C5_CONTRACT vs C4**: same story. Original 60.0% → controlled 51.8% [45.2, 58.7]. No detected preference. Scalar slightly favors C4 (Δ_total −0.231).

**Methodology contribution (now the strongest single result of v0.2):**

- **Pairwise LLM judges in this corpus + protocol show judge-family-specific slot-B preference, ranging from ~0 to ~+0.31 across the six pairs and three judges tested.** GPT-5.4: negligible, occasionally slot-A favored (−0.04 to +0.11). GPT-5.5 (xhigh reasoning): consistent strong +0.14 to +0.31 slot-B advantage. Opus 4.7: moderate +0.09 to +0.20. This means uncounterbalanced pairwise margins in v0.2 were systematically biased in favor of whatever condition was placed in slot B (which, by construction, was always the higher-numbered condition). Consistent in direction with prior LLM-as-judge position-bias literature (Zheng et al. 2023, Shi et al. 2024); the contribution here is per-judge quantification on a tri-model corpus.

**What v0.2 is not.** Still a synthetic-personas / synthetic-scenarios methodology pilot. The Tier 1 claims are about which conditioning formats produce measurable differences under blinded LLM-judge evaluation. They do not establish that real users benefit from profile-conditioned assistants. They do not isolate the mechanism behind C5_CONTRACT > C5. They do not validate the anchored rubric as construct-valid for personalization. All of these are deferred to v0.3 (see §11).

---

## 2. What v0.2 was designed to test

v0.1 left five specific questions open. Each was addressed by a v0.2 design change.

| v0.1 open question | v0.2 design response | Result |
|---|---|---|
| Did the C5 channel pattern reflect "public-anchor effect" or just structural absence of contract? | New condition `C5_CONTRACT` = C5 source packet + the same behavioral contract used in C3/C4. PAE separator. | **Resolved as package finding**: C5_CONTRACT > C5 is robust; isolating which component carries the effect deferred to v0.3 (§11) |
| Was C4 > C1's "structural advantage" actually a length effect? | New length-control conditions `C1_padded` (= C1 + benign padding to C4 length) and `C4_shuffled` (= C4 with sentence/bullet order shuffled). | **Resolved**: C4 > C1_padded survives at 62.3% under counterbalanced judging — structural advantage is not length |
| Was the scalar 4.0–4.8 ceiling effect a rubric design problem? | Replaced v0.1's unanchored 0–5 Likert with anchored 0–10 rubric (`prompt 06b_judge_anchored.md`). | **Resolved**: anchored rubric span 5.89 to 8.31 (2.42-point range on 0–10) vs v0.1's compressed 4.0–4.8 (0.8-point range on 0–5) |
| Were v0.1 scenarios too easy? | Re-curated 80-scenario set with mean difficulty 4.50/5 (vs v0.1 mean 3.58/5; all retained scenarios are difficulty 4-5). [Corrected 2026-06-10: an earlier version of this row misstated both means.] | **Resolved**: anchored scalar shows judges using the full range; pairwise produces less "no meaningful difference" framing |
| Were v0.1 same-author scope limitations driving the headlines? | Tri-model authoring (gpt-5.4, gpt-5.5-xhigh, Opus 4.7) on the full corpus; same-author pairwise as primary scope. | **Partially resolved**: tri-model coverage extends to anchored scoring; pairwise coverage is fully tri-model only on the 3 C5_CONTRACT-edge pairs (Opus has 0 original-pairwise records on the C0/C1/C1_padded/C3/C4/C4_shuffled non-C5_CONTRACT pairs). The 2026-05-17 Opus AB/BA fill (240 calls) closed the gap for C4 vs C5 specifically. |

---

## 3. Corpus and methods

### 3.1 Corpus

| Element | Count | Notes |
|---|---|---|
| Personas | 8 | 4 PI (public-inspired with source packets) + 4 PS (pure-synthetic) |
| Scenarios | 80 | 10 per persona; 8 families; difficulty mean 4.50/5 |
| Authors | 3 | gpt-5.4, gpt-5.5-xhigh, opus (Anthropic 4.7) |
| Conditions | 8 | C0, C1, C1_padded, C3, C4, C4_shuffled, C5 (PI-only), C5_CONTRACT (PI-only) |
| Assistant outputs | 1,680 | 8 conditions × per-condition author × persona × scenario coverage |
| Anchored scalar judgments | 3,949 | 3 judges; 67.5% complete-case (all 3 judges scored same output) |
| Same-author pairwise records (originals) | 3,243 raw / 3,064 true same-author | 179 records leaked cross-author from a missing `--scope same_author_only` on the Opus C5_CONTRACT pairwise phase (Phase 0 detection); excluded from same-author analyses. Counts include the 2026-05-17 Opus C4 vs C5 fill (+120 originals). |
| AB/BA swap records | 1,784 | Tier A (3 C5_CONTRACT-edge pairs, all 3 judges) + Tier B (3 non-C5_CONTRACT pairs, codex judges) + 2026-05-17 Opus C4 vs C5 fill (+120 swaps) |

### 3.2 Conditions tested

| Code | Description | Length (chars, mean) |
|---|---|---|
| C0 | No profile (baseline) | — |
| C1 | Trait labels only (Big Five percentiles + tags) | 748 |
| C1_padded | C1 + benign meta-padding to match C4 length | 4,664 |
| C3 | Behavioral contract — if-then engagement instructions | 2,454 |
| C4 | C3 + light scenario-conditional hints | 4,519 |
| C4_shuffled | C4 with sentence/bullet order shuffled (structure control) | 4,519 |
| C5 (PI-only) | Source-packet fictionalized prose — **no** behavioral contract | 3,476 |
| C5_CONTRACT (PI-only) | C5 source packet + the same behavioral contract used in C3/C4 | 6,905 |

C5 and C5_CONTRACT are PI-only because the source-packet construct depends on a public anchor. PS personas get the 6 core conditions only.

### 3.3 Judges and judging

Three judges drawn from two provider families:

| Judge | Provider family | Reasoning effort |
|---|---|---|
| `gpt-5.4` | OpenAI | default |
| `gpt-5.5-xhigh` | OpenAI | xhigh (extended reasoning) |
| `opus` (4.7) | Anthropic | default |

Each output was scored on:
- **Anchored 0–10 scalar rubric** (`prompt 06b_judge_anchored.md`) across 10 dimensions: helpfulness, profile_fit, calibrated_challenge, anti_sycophancy, agency_support, epistemic_hygiene, emotional_accuracy, boundary_safety, non_caricature, transfer_value
- **Binary red-flag taxonomy** (24 labels, RedFlag enum)
- **Same-author pairwise** comparisons (`prompt 07_pairwise_judge.md`) restricted by locked decision D2 to a subset of pair edges per pilot

Author and condition are blinded during judging via `runs/<tag>/blinding_key.json`.

### 3.4 The AB/BA correction (Phase 1)

The original v0.2 plan kept original-order pairwise records only (slot A held the lower-numbered condition in 100% of pairs for 8 of 10 condition-pair types; ≥98.8% for the others — see §6 for verification). External round-1 reviewers (codex-council, gpt-max, GPT Pro) unanimously called counterbalanced AB/BA rejudging "the cheapest decisive next experiment."

Phase 1 (2026-05-16 to 2026-05-17) ran AB/BA rejudging on all 6 headline pairs:
- **Tier A**: 3 C5_CONTRACT-edge pairs × 3 judges = 864 AB/BA-matched pairs (252 gpt-5.4 + 252 gpt-5.5 + 360 Opus across the three pairs)
- **Tier B**: 3 non-C5_CONTRACT pairs × 2 codex judges = 800 records
- **Opus C4 vs C5 fill** (2026-05-17, Phase 2 hygiene): 120 originals + 120 swap rejudgments

Total swap records: **1,784**. Per-pair AB/BA-matched cell counts after deduplication: C1_padded vs C4 = 320; C3 vs C5_CONTRACT = 288; C4 vs C4_shuffled = 320; C4 vs C5 = 280 (was 160 pre-Opus-fill); C4 vs C5_CONTRACT = 288; C5 vs C5_CONTRACT = 288.

CIs for the controlled lo_win rate are **cluster bootstrap** (cluster unit: persona × scenario × author, 2,000 resamples) — the matched-pair-appropriate estimator. The Wilson interval is retained side-by-side for continuity; it has been verified to give equivalent verdicts but slightly tighter intervals on borderline pairs (the round-2 reviewer flag).

---

## 4. Claim ledger (canonical per-claim summary)

Source of truth for the curated report. Each row carries the controlled estimate, cluster-bootstrap CI, scope qualifiers, scalar alignment, and the **allowed / forbidden wording** generated by Phase 2 hygiene from the analyzer's `CLAIM_LEDGER_SCHEMA`.

| Tier | Claim | Controlled lo_win | Bootstrap CI | Scalar Δ_total | Judge scope | Survives swap? |
|---|---|---:|---|---:|---|---|
| 1 | **C5_CONTRACT > C5** | 0.323 | [0.267, 0.383] | +3.057 | all three judges | ✓ |
| 1 | **C4 > C5** | 0.680 | [0.615, 0.744] | −3.261 | all three judges (Opus added 2026-05-17) | ✓ |
| 1 | **C4 > C1_padded** | 0.377 | [0.317, 0.439] | +3.084 | gpt-5.4 + gpt-5.5 (Opus n=0 on this pair) | ✓ |
| 1 | **C0 dominated by profile conditions** | (86.6% C4-over-C0 in originals) | (effect huge, not AB/BA-tested) | +6.075 | all three judges (original pairwise + scalar) | — |
| 1.5 | **C4 > C4_shuffled** (modest) | 0.578 | [0.522, 0.637] | −0.519 | gpt-5.4 + gpt-5.5 | ✓ |
| 2 | **C5_CONTRACT vs C3** — no detected preference | 0.501 | [0.436, 0.566] | −0.053 | all three judges | ⚠ |
| 2 | **C5_CONTRACT vs C4** — no detected preference | 0.482 | [0.413, 0.548] | −0.231 | all three judges | ⚠ |
| Methodology | LLM judges show ~15-17 pp slot-B preference (judge-family-specific) | (per-judge block) | (per-judge bootstrap CIs) | — | n/a (scoped to corpus/protocol) | — |

Note on `controlled lo_win` direction: by convention `lo` is the alphabetically-first condition in the pair. C4 wins when C4 is on either side of the comparison and the row's lo_win indicates this directionally:
- C1_padded_vs_C4 lo_win = 0.377 → C4 wins 62.3% (C4 is hi)
- C4_vs_C5 lo_win = 0.680 → C4 wins 68.0% (C4 is lo)
- C5_vs_C5_CONTRACT lo_win = 0.323 → C5_CONTRACT wins 67.7% (C5_CONTRACT is hi)

---

## 5. Tier 1 findings (detailed)

### 5.1 C5_CONTRACT > C5 (the substantive headline)

The condition C5 (source packet without contract) is consistently outperformed by C5_CONTRACT (source packet + the same behavioral contract used in C3/C4). The effect survives every Phase 0 audit and the Phase 1 AB/BA correction.

```
Original (uncontrolled):  76.0% C5_CONTRACT wins
Position-controlled:      67.7% [61.7, 73.3] (cluster bootstrap, n=288 AB/BA pairs)
Joint position+length:    64.9% (length-similar subset n=74, CI [52.9, 76.2])
```

**Robust across stratifications:**

| Stratification | Result |
|---|---|
| By judge | gpt-5.4 controlled 65.8%, gpt-5.5 73.8%, Opus 64.8% — all favor C5_CONTRACT, all >50%. Per-judge slot-B advantage: gpt-5.4 +0.11, gpt-5.5 +0.31, Opus +0.09. |
| By PI persona | All 4 PI personas show C5_CONTRACT favored. Strongest: Emily Blender. Weakest: still on the C5_CONTRACT side. |
| By scenario family | All 8 families show C5_CONTRACT favored at point estimate. No family reversal at strict CI level. |
| Length-matched subset | Survives — 35.1% C5 lo_win [0.238, 0.471]; CI excludes 0.5 on the C5_CONTRACT-favored side. |
| Scalar alignment | Δ_total +3.057 (positive = C5_CONTRACT higher on the 100-point sum); sign agreement 79.4%. Pairwise and scalar channels agree. |
| TF-IDF discoverability | F1 = 0.000 for both classes — a simple lexical classifier cannot distinguish C5 from C5_CONTRACT outputs. This does not rule out semantic, stylistic, length-based, or judge-internal recognizability, but it removes the simplest "judge recognizes the treatment" artifact explanation. |

**What this finding does NOT establish.** C5_CONTRACT differs from C5 on at least four orthogonal dimensions:
1. **Contract presence** — C5_CONTRACT has the behavioral contract; C5 doesn't.
2. **Ordering** — C5_CONTRACT places the contract first, packet as evidence; C5 has packet only.
3. **Anti-mimicry language** — C5_CONTRACT includes explicit anti-mimicry rules; C5 doesn't.
4. **Profile length** — C5_CONTRACT 7,433 chars vs C5 3,476 chars (≈2.1×).

The data cannot say which component is doing the work. The defensible package claim is: *"adding the contract-first source-packet package improves the C5 condition decisively under counterbalanced judging."* The mechanism is unsettled; v0.3 ablations (`C_GENERIC_CONTRACT`, `C5_CONTRACT_SHORT`, packet-first variants) are required.

### 5.2 C4 > C5

Behavioral contract beats source-packet-without-contract. Originally OpenAI-judge-only (Opus had 0 records on this pair in v0.2's planned pairwise scope); the 2026-05-17 Opus fill closed the gap.

```
Original (uncontrolled):  63.7% C4 wins
Position-controlled:      68.0% [61.5, 74.4] across all three judges
Joint position+length:    67.4% [54.7, 79.5] (length-similar n=76)
```

The most striking feature of this finding is **judge unanimity** after the Opus fill:

| Judge | n (AB/BA pairs) | Controlled lo_win (= C4 wins) | Slot-B advantage |
|---|---:|---:|---:|
| gpt-5.4 | 80 | **0.681** | +0.037 |
| gpt-5.5 | 80 | **0.681** | +0.138 |
| Opus | 120 | **0.679** | +0.140 |

Three independent judges (two provider families, three model architectures) converge on essentially the same C4 win rate within 0.2 pp of each other. This is the cleanest tri-model agreement in the v0.2 corpus.

**On the Phase 0 vs Phase 1 contradiction.** Phase 0's length-matched analysis (with Wilson CI, n=46) had suggested C4 > C5 might "vanish under length matching" — controlled lo_win 0.522 [0.381, 0.659]. Phase 1's AB/BA correction showed the opposite — C4 > C5 strengthened from 63.7% to 68.0%. These were not contradictory; they addressed different confounds (length vs position) on different sub-samples. The 2026-05-17 hygiene pass computed the joint position+length-corrected estimate on the unified sample after the Opus fill: 67.4% [54.7, 79.5] — wide CI due to the n=76 length-similar subset, but the lower bound 0.547 excludes 0.5. The original Phase 0 length-only finding turned out to be position-bias-confounded (the length-matched subset was still slot-B-biased), and the joint correction resolves both confounds in favor of the C4 > C5 verdict.

### 5.3 C4 > C1_padded

Behavioral contract beats length-matched baseline. The v0.1 review left open whether C4's advantage over C1 was the contract or the length; v0.2's `C1_padded` condition was designed to disambiguate.

```
Original (uncontrolled):  68.1% C4 wins
Position-controlled:      62.3% [56.1, 68.3]
Scalar Δ_total:           +3.084 / 100
```

The verdict: structural behavioral contract beats length-matched padding. Effect attenuates from 68.1% to 62.3% under position-bias correction (5.8 pp absolute attenuation; the original was modestly inflated by slot-B bias) but remains clearly above 50%.

**Scope qualifier**: gpt-5.4 + gpt-5.5 judges only — Opus has 0 pairwise records on this pair in v0.2's data (consistent with all non-C5_CONTRACT-edge pairs).

### 5.4 C0 dominated

Every profile-conditioning condition beats the baseline:

```
Original C4 vs C0:     86.6% C4 wins
Scalar Δ_total:        +6.075 / 100 (largest scalar delta in the corpus)
```

This is the largest effect in v0.2 and the only Tier 1 finding not directly AB/BA-tested. Given the measured slot-B preference range of ~15-17 pp, an 86.6% advantage is well outside the corridor where position bias could explain the result. The defensible claim is "C0 is dominated by any profile condition, AB/BA correction would not change the qualitative conclusion."

### 5.5 C4 > C4_shuffled — Tier 1.5 (modest, sign-corrected)

The v0.2 plan asked whether coherent ordering matters. The original pairwise (n=320, all-codex) said 51.9% C4 wins — interpreted as "no significant difference." Under counterbalanced AB/BA, this becomes 57.8% C4 wins [52.2, 63.7] — a sign-correction of the original framing, not a flip. The original was understating because slot-A bias (which penalized C4 in its constant slot A position) was suppressing the apparent margin.

Effect size is meaningfully smaller than the 17-19 pp Tier 1 effects above:
- C4 > C5: +18.0 pp above parity
- C5_CONTRACT > C5: +17.7 pp above parity
- C4 > C1_padded: +12.3 pp above parity
- **C4 > C4_shuffled: +7.8 pp above parity**

The curated wording is therefore "C4 modestly outperforms C4_shuffled" rather than "Coherent structure significantly beats shuffled." Scalar alignment is also weak (Δ_total −0.519 ≈ 0; sign agreement 66.4%) — the channels agree on direction but the magnitude is at the rubric's noise floor.

---

## 6. Demoted: the two original headlines that did not survive AB/BA

### 6.1 C5_CONTRACT vs C3 — no detected preference

```
Original (uncontrolled):  57.2% C5_CONTRACT wins
Position-controlled:      49.9% C5_CONTRACT wins [43.4, 56.4] (CI straddles 0.5)
Scalar Δ_total:           −0.053 (essentially zero, slightly favors C3)
Joint position+length:    50.0% C5_CONTRACT wins (n=80, CI [36.6, 62.9] straddles 0.5)
```

The v0.2 plan's headline "C5_CONTRACT outperforms C3" was **carried entirely by slot-B position bias**. Under counterbalanced judging there is no detected preference. The scalar rubric, applied to the same outputs by the same judges, agrees that the two conditions are essentially tied (Δ_total −0.053).

Three independent Phase 0 audits foreshadowed this collapse before Phase 1 ran:
1. **Scalar–pairwise reconciliation** (Phase 0.B): scalar Δ_total = −0.053 even though pairwise had 57.2% C5_CONTRACT
2. **Leave-one-judge-out fragility** (Phase 0.D): dropping the Opus judge moved the all-judge lo_win from 0.428 to 0.494 (Δ +0.066) — the Opus judge's slot-B preference was carrying the advantage
3. **Length matching** (Phase 0.G): the similar-length subset gave lo_win 0.449 [0.343, 0.559] — included 0.5

Phase 1's AB/BA confirmed all three.

**The cross-provider sub-finding now demoted.** Phase 0's stratified cluster-bootstrap had shown that cross-provider judging (judge family ≠ author family) gave C5_CONTRACT a strong CI [0.238, 0.446] — apparently contradicting the all-judge result. The 2026-05-17 hygiene pass ran AB/BA on this same cross-provider subset directly: controlled lo_win 0.457 [0.376, 0.540] — straddles 0.5. The cross-provider Phase 0 finding was an artifact of gpt-5.4 (the cross-provider judge for Opus-authored cells) having no slot-B preference, paired with the absence of position correction on that stratification. Under AB/BA, even the cross-provider subset shows no real preference. The curated report does not present the cross-provider Phase 0 result as a competing positive verdict.

### 6.2 C5_CONTRACT vs C4 — no detected preference

```
Original (uncontrolled):  60.0% C5_CONTRACT wins
Position-controlled:      51.8% C5_CONTRACT wins [45.2, 58.7] (CI straddles 0.5)
Scalar Δ_total:           −0.231 (slightly favors C4)
Joint position+length:    55.0% C5_CONTRACT wins (n=65, CI [39.9, 70.2] straddles 0.5)
```

Same pattern as C5_CONTRACT vs C3. The 60.0% original was carried by slot-B bias. Under counterbalanced judging, the two conditions are statistically indistinguishable. The scalar channel agrees and slightly favors C4.

This is **not equivalent to "C5_CONTRACT = C4"** unless an equivalence margin is predeclared. The cautious wording the curated report uses: *"We do not detect a reliable pairwise preference between C5_CONTRACT and C4 after AB/BA correction. The CIs still allow small effects in either direction. Scalar scores do not support a C5_CONTRACT advantage."*

### 6.3 What the demotions imply for the v0.2 plan's master claim

The locked v0.2 plan stated that v0.1's "PAE confound was empirically resolved in favor of absence of contract as dominant driver." This wording is **struck**. The replacement framing:

> v0.2 shows that the contract-first source-packet package (C5_CONTRACT) substantially beats the bare source-packet condition (C5) under counterbalanced judging (67.7%). It also shows that the published-headline advantages of C5_CONTRACT over C3 and C4 were entirely position-bias artifacts. The question of *which component* of the C5_CONTRACT package carries the C5_CONTRACT > C5 effect — contract presence, contract-first ordering, anti-mimicry language, profile length, or interaction of these — remains open. v0.3 ablations are required for mechanism claims.

**The C5_CONTRACT vs C3 collapse is the scientifically most interesting demoted finding**, because C3 carries a behavioral contract without any source packet, and C5_CONTRACT carries the same contract *plus* a source packet. Under counterbalanced judging, the two are indistinguishable. That is consistent with two interpretations the v0.2 dataset cannot discriminate between: (a) the source packet contributes nothing detectable beyond what the contract already provides, or (b) the source packet contributes signal that this corpus and protocol cannot detect at n=288. Either way, the headline that *"source packets add value when subordinated to contracts"* — which the v0.2 plan was set up to deliver — does not survive. The C5_CONTRACT > C5 result, by contrast, can support only the weaker version: *"adding the contract-supplemented source-packet package improves the bare source-packet condition,"* without isolating whether the contract or the packet does the work.

---

## 7. The slot-B preference finding (methodology contribution)

Across the 6 headline pairs with AB/BA coverage (1,784 swap records), pairwise judges in the v0.2 corpus systematically preferred whichever condition was placed in slot B of the prompt. The magnitude is judge-family-specific:

| Judge | C3 vs C5C | C4 vs C5C | C5 vs C5C | C1_padded vs C4 | C4 vs C5 | C4 vs C4_shuffled |
|---|---:|---:|---:|---:|---:|---:|
| **gpt-5.4** | −0.036 | +0.024 | +0.112 | +0.031 | +0.037 | −0.025 |
| **gpt-5.5-xhigh** | +0.250 | +0.250 | +0.310 | +0.200 | +0.138 | +0.263 |
| **Opus 4.7** | +0.204 | +0.199 | +0.094 | n/a | +0.140 | n/a |

Pattern: gpt-5.4 is essentially position-neutral (with one cell showing slight slot-A preference). gpt-5.5-xhigh is strongly and consistently slot-B-preferring (~+0.20 to +0.31). Opus is moderately slot-B-preferring on C5_CONTRACT pairs (+0.23) but less so on C5 vs C5_CONTRACT (+0.09).

**Why this matters for v0.2's published findings**: every original pairwise headline in v0.2 placed the lower-numbered condition in slot A and the higher-numbered in slot B (verified by Phase 0.E: 8 of 10 condition-pair types had `slot_a_is_lo_share` = 1.000; the other 2 were ≥ 0.988). So the slot-B bias inflated *every* high-condition win rate in the original pairwise tables. The corrections in §5 and §6 use the cluster-bootstrap controlled estimates that average across both slot orders.

**Scope of the finding.** This is a measurement of the v0.2 corpus + the v0.2 pairwise judge prompt + the three judge models tested. It does not establish that all LLM-as-judge pipelines have ~15-17 pp slot-B preference. It is consistent in *direction* with prior work on LLM-as-judge position bias (Zheng et al. 2023, Shi et al. 2024); the contribution is per-judge quantification on a tri-model corpus with same-author controls. Future work that uses the same pairwise prompt template and similar reasoning-effort judges may find similar magnitudes; future work with different prompt structures may not.

**Per-cell decomposition.** Within each (pair, judge) cell, the 4-way decomposition (`condition_lo_stable` / `condition_hi_stable` / `slot_A_stable` / `slot_B_stable`) shows how many AB/BA-matched pairs are condition-stable (same condition wins both orders → real preference) vs slot-stable (same physical slot wins both orders → position bias). The full decomposition is rendered in the autogen scaffold under "AB/BA per-cell decomposition by judge."

---

## 8. Why AB/BA was necessary — the audit pipeline

A reviewer encountering the v0.2 dataset cold would reasonably ask: did we run AB/BA because we suspected a problem, or did we run it because reviewers told us to and the problem only became visible afterward?

Both. Three independent Phase 0 same-data audits (running on the existing data only, no new generation) had separately predicted the same outcome for the C5_CONTRACT pairs:

| Audit | Phase 0 finding for C5_CONTRACT vs C3 |
|---|---|
| **Scalar–pairwise reconciliation** (0.B) | Δ_total = −0.053 (essentially zero) despite 57.2% pairwise — channels disagree |
| **Leave-one-judge-out** (0.D) | Drop Opus → lo_win moves from 0.428 to 0.494 — Opus alone carries the advantage |
| **Length-matched subset** (0.G) | Similar-length lo_win 0.449 [0.343, 0.559] — CI includes 0.5 |

Each of these had a confound-specific interpretation (channel mismatch / single-judge dependence / length artifact). None individually identified slot-B position bias as the unifying cause. AB/BA provided the unifying explanation: all three apparent confounds were downstream of the slot assignment imbalance (slot A = always lower-numbered condition, slot B = always higher-numbered) interacting with judge-family-specific slot-B preferences.

This is worth recording because it suggests a generic recommendation for future evaluation pipelines: **run AB/BA counterbalanced judging as a default, not as a post-hoc audit.** The cost in this corpus was ~1,700 swap records (one Codex-only-Tier-A wall-clock window for the C5_CONTRACT pairs + a few cap windows for Opus). The information value was: 2 of 3 original C5_CONTRACT headlines retracted, 1 published-as-Tier-1 finding upgraded from scope-limited to judge-unanimous, and a publishable methodology contribution that did not exist in v0.1.

---

## 9. Scalar–pairwise reconciliation

Where do the anchored scalar rubric and the holistic pairwise judging agree, and where do they diverge?

For each (pair, judge) cell with both a pairwise judgment and a scalar score on each output, we compute:
- The pairwise winner (lo / hi / tie)
- The scalar Δ_total = (hi-condition sum of 10 dimensions) − (lo-condition sum) on the 0–10 scale × 10 dims = ±100 range
- The sign agreement rate across cells

| Pair | Pairwise winner direction | Scalar Δ_total | Sign agreement | Verdict |
|---|---|---:|---:|---|
| C0 vs C4 | hi (C4) wins 86.6% | +6.075 | 86.3% | Both channels: C4 ≫ C0 |
| C5 vs C5_CONTRACT | hi (C5_CONTRACT) wins 76.0% | +3.057 | 79.4% | Both channels agree |
| C1_padded vs C4 | hi (C4) wins 68.1% | +3.084 | 76.5% | Both channels agree |
| C4 vs C5 | lo (C4) wins 68.0% | −3.261 | 77.4% | Both channels: C4 > C5 |
| C4 vs C4_shuffled | lo (C4) wins 57.8% | −0.519 | 66.4% | Both channels weakly: C4 > C4_shuffled |
| **C5_CONTRACT vs C3** | (pre-AB/BA) hi favored 57.2% | **−0.053** | **71.1%** | **Scalar channel disagrees — flagged ⚠ in autogen** |
| **C5_CONTRACT vs C4** | (pre-AB/BA) hi favored 60.0% | **−0.231** | 73.4% | **Scalar channel disagrees — flagged ⚠** |

The two pairs where the pre-AB/BA pairwise headline and the scalar channel disagreed are exactly the two pairs that subsequently collapsed under AB/BA correction. Scalar–pairwise reconciliation was the first analytical signal of the position-bias artifact, even before AB/BA was run.

For the four surviving Tier 1 pairs, scalar and pairwise channels point in the same direction, with sign agreement rates 76–86% — well above what would be expected by chance on noisy 0–10 scoring.

---

## 10. Robustness audits (Phase 0 catalog)

12 same-data analyses on the existing 1,680 outputs / 3,949 scalar records / 3,123 pairwise records. All are now first-class blocks in the analyzer (rendered in the autogen scaffold), not one-off scripts.

| Audit | Block | Headline result |
|---|---|---|
| 0.A | Cross-author leak detection + stratified cluster-bootstrap | 179 cross-author records detected (Opus C5_CONTRACT phase scope leak); excluded from same-author analyses |
| 0.B | Scalar–pairwise reconciliation by cell | See §9 |
| 0.C | Per-judge / per-author / per-persona pairwise stratification | gpt-5.4 reverses C3 vs C5_CONTRACT (lo_win 0.571 [0.465, 0.672] — C3 wins under gpt-5.4 alone); Slalom Altar persona reverses C4 vs C5_CONTRACT (lo_win 0.657 vs other PI personas 0.19–0.48) |
| 0.D | Leave-one-judge / author / persona / family-out fragility | C3 vs C5_CONTRACT: drop Opus → lo_win goes 0.428 → 0.494 (collapses); C4 vs C4_shuffled: drop either GPT judge → direction flips at all-judge level |
| 0.E | A/B side audit | 8 of 10 pairs have `slot_a_is_lo_share` = 1.000; other 2 ≥ 0.988; C5_CONTRACT is in slot B 100% of original-pairwise records — structural imbalance flagged as publication-blocking until AB/BA runs |
| 0.F | Scenario-family forest plot | C3 vs C5_CONTRACT reverses at point estimate in epistemic_uncertainty (0.643) and shame_self_interpretation (0.556); C4 vs C4_shuffled reverses in 5 of 8 families at point estimate |
| 0.G | Length-adjusted summary | C3 vs C5_CONTRACT vanishes (length-similar 0.449 [0.343, 0.559]); C4 vs C5 vanishes pre-AB/BA (length-similar 0.522 [0.381, 0.659]); C5 vs C5_CONTRACT survives (0.192 [0.118, 0.297]) |
| 0.H | Cross-judge red-flag predictiveness | All 10 pairs: P(loser more flagged \| asymmetric) = 0.65–0.88, all Wilson CIs exclude 0.5 — red flags are predictive, not within-judge artifacts |
| 0.I | Macro vs micro aggregation | Macros agree with micro within 5pp on every dimension — headlines not artifacts of record-count imbalance |
| 0.J | Rubric lexical-overlap | Jaccard 0.047–0.073 across all conditions; C5_CONTRACT has *lower* overlap (0.063) than C3 (0.073) and C4 (0.069) — rubric-halo concern not supported |
| 0.K | Missingness audit | 67.5% complete-case scalar coverage (1,134/1,680 outputs scored by all 3 judges); pairwise cell counts 4–16 records, max/min ratio 4× |
| 0.L | Condition-discoverability classifier | TF-IDF + logistic test accuracy 27.2% vs 12.5% chance (+14.7pp); F1=0.000 for both C5 and C5_CONTRACT — a simple lexical classifier cannot distinguish these two conditions from output text alone (but a stronger classifier or judge-blind recognizability prompt could) |

Phase 1 added 5 more blocks:

| Block | Purpose |
|---|---|
| `ab_ba_position_audit_same_author` | Headline AB/BA controlled estimates + cluster bootstrap CIs |
| `ab_ba_position_audit_same_author_by_judge` | Per-judge slot-B advantages + per-cell decomposition |
| `ab_ba_by_provider_scope_same_author` | Cross-provider vs same-provider AB/BA stratification |
| `ab_ba_joint_position_length_same_author` | Joint position + length corrected estimates |
| `pairwise_by_persona_x_author_same_author` | Persona × author interaction crosstab |
| `complete_case_scalar_anchored` | Scalar means on outputs scored by all 3 judges |
| `claim_ledger` | Per-claim canonical summary with allowed/forbidden wording |

All blocks are reproducible from `runs/2026-04-26_v02_hard_codex_only/` via `python -m psycheeval.analyze --tag 2026-04-26_v02_hard_codex_only --pilot v02_hard_pilot`. 106 tests pass.

---

## 11. Limitations

**Synthetic-personas, synthetic-scenarios pilot.** v0.2 does not establish that real users benefit from profile-conditioned assistants. It establishes which profile formats produce measurable differences under blinded LLM-judge evaluation in a synthetic corpus. Real-user shadow-mode validation is the v0.3 construct-validity centerpiece (per round-2 reviewer consensus).

**Scope-limited pairwise.** The non-C5_CONTRACT pairwise pairs (C0, C1, C1_padded, C3, C4, C4_shuffled — i.e., everything except the 3 C5_CONTRACT edges and now C4 vs C5 after the 2026-05-17 fill) were judged by only gpt-5.4 and gpt-5.5 (no Opus). Tier 1 verdicts on these pairs are robust within OpenAI-family judging but have not been verified by Opus.

**Mechanism not isolated for C5_CONTRACT > C5.** The surviving substantive headline is a package claim. The data cannot distinguish among contract presence, ordering, anti-mimicry language, packet length, and their interactions.

**Slot-B preference is corpus-scoped.** The methodology contribution is quantified on this specific corpus, prompt template, and three judge models. Generalization to other pairwise-judging setups requires replication.

**Anchored rubric is not construct-validated.** The 10-dimension anchored rubric was designed in-house. Paraphrased-anchor robustness checks (round-2 reviewer suggestion) are deferred to v0.3.

**Complete-case scalar coverage is 67.5%.** The pooled scalar means in §9 pool across all judging records; for a strict robustness pass, the complete-case scalar table is rendered side-by-side in the autogen.

**Force-choice pairwise.** The pairwise judging is forced-choice (A / B / tie). A "no meaningful difference" option (per GPT Pro C8) might reduce forced precision on the collapsed C5_CONTRACT vs C3/C4 pairs.

**Scenarios may be profile-aware.** Round-2 reviewers (Codex Council, GPT Pro) flagged that scenarios were authored by the same models that participate as judges; future v0.3 should add scenarios authored blind to profile theory.

**Single-turn outputs only.** Real personalization is longitudinal. v0.2 does not test multi-turn interactions, profile freshness/staleness, or user-edited profiles.

---

## 12. v0.3 priorities (post-round-2 reviewer consensus)

Priority order. All four round-2 reviewers converged on the top three.

### Tier-1 v0.3 experiments

1. **`C_GENERIC_CONTRACT` + `C4_WRONG_PROFILE`**. The single most diagnostic addition: does adding a *generic* (non-personalized) behavioral contract match C5_CONTRACT's performance against C5? If yes, the package effect is "more explicit good-assistant instructions," not "personalization." If no, profile specificity is doing real work. Approximate cost: ~80 generations × 3 authors + judging.

2. **`C5_NONPUBLIC` + `C5_NONPUBLIC_CONTRACT`**. Isolates the public-anchor effect from the source-packet form. Source-packet narrative for PS personas (no public-anchor prose).

3. **Contract component ablation** within C5_CONTRACT: contract-first vs packet-first ordering, anti-mimicry on/off, facts-only packet vs narrative packet, length-matched C5_CONTRACT_SHORT. Required for any "contract mechanism" claim.

### Methodology improvements

4. **Same-orientation rejudge sentinel** (50–100 pairs). Decompose AB/BA flip rate into position effect + retest noise.

5. **Paraphrased rubric anchors**. Tests robustness of scalar findings to wording choices.

6. **Human-rater calibration sample** (30–100 disagreement-heavy pairs, 2–3 raters). Sanity-checks LLM-judge preferences against blinded human judgment.

7. **Tie / no-meaningful-difference option** on pairwise. Reduces forced-choice noise.

### Deployment-realism conditions

8. **Stale / contradictory / user-edited profiles**. Real profiles in deployment will not be pristine.

9. **Profile compression curve** (500 / 1,000 / 2,000 char variants). C5_CONTRACT at 7,433 chars is deployment-unrealistic.

10. **Multi-turn scenarios**. Profile context introduced in turn 1, contradicted in turn 2, assistant must update in turn 3, etc.

### Construct validity

11. **Real-user shadow-mode validation**. The construct-validity centerpiece. Profiles applied to real conversations; outcomes measured via predeclared endpoint (preference / follow-through / expert-rated decision quality). Separate from v0.2's synthetic eval.

12. **Scenarios authored blind to profile theory**. Mitigates benchmark-construction validity concerns.

### Open analytical questions

- What is the right primary endpoint when pairwise, scalar, and red-flag channels disagree?
- Do pairwise and scalar judges measure different latent constructs?
- What fraction of the AB/BA flip rate is true position bias vs retest stochasticity (the same-orientation sentinel will answer this)?

---

## 13. References and artifacts

| File | Content |
|---|---|
| `reports/metrics_2026-04-26_v02_hard_codex_only.json` | Canonical metrics. ~400 KB. All blocks documented in §10. |
| `reports/psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md` | Auto-generated factual scaffold. Regeneratable via `python -m psycheeval.analyze`. Filename retains `v0_1` prefix from the v0.1 pilot scaffold convention; content is v0.2. |
| `runs/2026-04-26_v02_hard_codex_only/` | Raw JSONL: `assistant_outputs`, `anchored_judge_scores`, `pairwise_scores`, `pairwise_swap_scores`. |
| `reports/archive/2026-05-15_pre-labeling-fix/PHASE0_FINDINGS.md` | Phase 0 audit synthesis (12 audits) |
| `reports/reviews/2026-05-16_phase1_ab_ba_findings.md` | Phase 1 AB/BA findings + tier reassignment |
| `reports/reviews/2026-05-15_consolidated_v0_2_review.md` | Round-1 consolidated external review (3 reviewers) |
| `reports/reviews/2026-05-17_consolidated_round2_review.md` | Round-2 consolidated external review (4 reviewers) |
| `reports/reviews/2026-05-17_phase2_hygiene_summary.md` | Phase 2 hygiene pass: 13 fixes + findings |
| `docs/v0_2_plan_extended_2026-05-05.md` | Locked v0.2 plan (7 decisions D1–D7) |

External review history:
- **Round 1** (2026-05-15): GPT Pro single-agent + Codex Council 4-agent blind ensemble + GPT Max 4-agent HCOM. Convergence on labeling defect, C5_CONTRACT > C3 fragility, position-bias audit need, scalar-pairwise contradiction.
- **Round 2** (2026-05-17): same three + independent Opus 4.7 reviewer subagent. Convergence on Wilson CI bug, package-not-mechanism framing for C5_CONTRACT > C5, joint position+length correction need, slot-B universalization concern, claim ledger architecture.

---

## 14. Closing

The v0.2 pilot's contribution to PsycheEval, summarized:

- One robust package claim about source-packet conditioning (C5_CONTRACT > C5)
- Three robust comparator claims (C4 > C5, C4 > C1_padded, C0 dominated) that confirm the v0.1 "profile-conditioning beats baseline" finding under harder scenarios + anchored rubric + position correction
- One sign-correction of a v0.2 plan hypothesis (C4 modestly beats C4_shuffled — coherent ordering does matter, slightly)
- **Two retracted headlines** that turned out to be position-bias artifacts (C5_CONTRACT vs C3 and vs C4) — the part of the v0.2 plan that did not survive
- One new methodology contribution worth publishing on its own: per-judge slot-B preference quantification on a tri-model corpus with same-author controls

The retracted headlines are not a v0.2 failure — they are a v0.2 success. The pipeline was specifically designed to catch this class of artifact (the C5_CONTRACT separator, the anchored rubric, the length controls, the tri-model design were all v0.2-original decisions), the audit pass found it, the AB/BA experiment confirmed it, and the curated report retracts it. A research pipeline that can retract its own headlines under audit is functioning correctly.
