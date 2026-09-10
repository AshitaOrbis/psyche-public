# PsycheEval v0.1 micro-pilot — tri-model completed report

**Tag**: `2026-04-26_micro_tri_model` (extends `2026-04-20_micro` with GPT-5.5 as third author + judge)
**Status**: Final tri-model state. Supersedes the two-model v0.1 report and the prior tri-model interim report.
**Date**: 2026-05-02

---

## 1. TL;DR

The completed tri-model v0.1 pilot supports two robust findings, one open question, and one judge-methods finding — all within the qualifications listed below.

**Robust within same-author scope (§6a):** all four profile-conditioning conditions beat the no-profile baseline in pairwise judging, with `***` Wilson CIs across every judge slice individually. This is the strongest claim of v0.1 — a 4-way result that holds for each judge separately. It is robust **within author** (the pairwise scope holds the author model fixed; cross-author pairs were not judged in v0.1, see §12 #1).

**Robust within same-author scope, narrower in scope:** explicit behavioral conditioning (C3, C4) beats simple trait conditioning (C1) in same-author pairwise across every judge slice. This is one specific within-conditioning comparison rather than a 4-way generalization. C3 vs C4 is judge-dependent (only GPT-5.5 and Opus distinguish them in pairwise; GPT-5.4 cannot — see §6b).

**Open question — C5 channel pattern:** scalar and red-flag tables show C5 below C3/C4 in the PI-only slice where C5 applies (any-flag rate 12.5% vs C3 8.3% / C4 7.4%; profile_fit 4.23 vs 4.43 / 4.47). Pairwise judging produces a more complicated picture: GPT-5.4 distinguishes C3 and C4 from C5 (***), while GPT-5.5 and Opus cannot. v0.1 cannot discriminate among at least three readings — channel-sensitivity asymmetry, length confound (C5 outputs are 30–40% longer), or the structural absence of behavioral contract in C5. **PAE remains a hypothesis confounded with structural difference**, not a settled finding (§10). The §13 #4 per-pair correlation analysis would settle this; it is queued for v0.2.

**Judge-methods finding — narrowed:** adding GPT-5.5 made it possible to separate exact-self halo from same-provider halo for the first time. On at least one cell — `calibrated_challenge` at C0 for GPT-5.5-authored outputs — the same-provider halo (GPT-5.4 judging GPT-5.5-authored outputs, +0.729) exceeds the exact-self halo (GPT-5.5 judging its own outputs, +0.646). This is one cell, not a multi-cell generalization; other cells (e.g. GPT-5.5-authored on `emotional_accuracy`: +0.625 self vs +0.521 sibling) show the opposite ordering. The defensible finding is **the two halo types are separable** when the panel includes more than one model per provider, which the prior two-model design could not test. v0.2 should expand the panel to determine whether the single-cell result generalizes.

**What this is not.** v0.1 is a synthetic-personas / synthetic-scenarios methodology pilot. It supports harness development, condition comparison, and measurement-design choices; it does not yet validate that Psyche profiles improve outcomes for real users with real problems. Inter-judge agreement is modest (κ ≈ 0.3 on red-flag labels; scalar agreement unmeasured). Scalar means cluster between 4.0 and 4.8 on a 0–5 rubric, putting many of the pairwise differences in §7 within the per-cell standard error these data can support — they should be read as descriptive, not significance-tested.

---

## 2. What PsycheEval is testing

PsycheEval is a measurement framework for asking whether structured user-profile context (a "Psyche profile") changes how an assistant responds. The micro-pilot tests five conditioning conditions on a fixed set of personas and scenarios, and asks three judge models — drawn from two provider families — to evaluate the resulting responses along ten rubric dimensions, plus a binary red-flag taxonomy, plus head-to-head pairwise comparisons.

The pilot is *not* an evaluation of a real product. It is a methodology probe designed to surface which profile formats produce measurable differences, where measurement channels (scalar / red-flag / pairwise) agree or diverge, and what kinds of judge bias the harness will need to control for in a real validation study.

---

## 3. What this pilot can and cannot show

**It can:**

- Compare response quality across explicit conditioning treatments held constant.
- Surface which profile formats produce *measurable* differences from baseline.
- Detect convergence and divergence between scalar, red-flag, and pairwise channels.
- Quantify judge-bias structure (exact-self, same-provider, cross-provider halos).
- Generate hypotheses for v0.2 about scenario effects, length confounds, and rubric sensitivity.

**It cannot:**

- Establish that Psyche profiles improve outcomes for real users with real problems.
- Establish ecological validity. Personas, scenarios, and ground truth are synthetic.
- Decompose treatment effects into format vs. content effects (v0.2 length controls address part of this).
- Settle whether observed differences are clinically meaningful, only whether they are statistically distinguishable.

This is harness development, not psychometric validation. A real validation study with human raters and real users is a separate program (see §13).

---

## 4. Experimental design

### Conditions

| Code | Description |
|---|---|
| C0 | No profile (baseline). |
| C1 | Trait labels only. Big Five percentile scores plus a brief descriptor tag list (e.g. "high openness, low conformity, intellectual"). No behavioral instructions. |
| C2 | *Reserved.* Earlier design notes positioned C2 as a narrative/prose profile condition. The data structures exist (`Condition.C2`, `ProfileConditionText.C2_narrative`), but no narrative content was authored for v0.1, so no C2 outputs were generated. v0.1 intentionally jumps from C1 to C3. v0.2 may reintroduce C2 if narrative profiles become a target condition. |
| C3 | Behavioral contract. Specific if-then-style instructions for how the assistant should engage this user — calibrated challenge instead of validation, anti-sycophancy, uncertainty preservation, repair-oriented response cues, profile-fit guidance. |
| C4 | C3 plus scenario-conditional guidance. The behavioral contract from C3 is extended with light scenario-class hints (e.g. "in interpersonal-conflict scenarios prioritize ___; in epistemic-uncertainty scenarios prioritize ___"). C4 is therefore strictly a superset of C3 in instruction content. |
| C5 | Source packet (public-inspired personas only). A composed "public-archetype" packet — fictionalized prose that gestures at the persona's reference public anchor. Does **not** include the structured behavioral contract. C5 is therefore confounded with the absence of contract, not a clean test of source-packet vs contract (see §10). |

C5 only runs against public-inspired (PI) personas where a public anchor is meaningful. Pure-synthetic (PS) personas do not have a C5 condition.

**Note on PI personas (ethics).** PI personas are *fictionalized* public-anchor personas. They are not claims about real individuals, not psychometric assessments of any specific person, and not attempts to simulate private beliefs. They are used to test whether publicly recognizable source patterns alter assistant behavior in patterned ways. The names in `pfi_*` user IDs are deliberate placeholders (snowclone-shaped tokens like `slalom_altar_001`); they do not match any real public figure.

### Personas

8 personas: 4 public-inspired (PI; users with names beginning `pfi_`) and 4 pure-synthetic (PS; users with names beginning `syn_`). Each persona has a fixed profile in each condition.

### Scenarios

48 scenarios across 8 families: interpersonal_conflict (8), procrastination_avoidance (8), authority_disagreement (6), creative_feedback (6), epistemic_uncertainty (6), moral_uncertainty (6), shame_self_interpretation (5), ambition_status (3). Each persona is paired with 6 of these scenarios — not all 48 — drawn to fit the persona's profile. Per-persona scenario count: 6, all distinct.

Difficulty is rated 1–5 per scenario; mean across the bank is 3.58 (range 2–5). The PI subset (24 scenarios) and PS subset (24 scenarios) have **identical** difficulty distributions in this run. Family mix differs: PS has more shame_self_interpretation (4 vs 1 for PI); PI has more authority_disagreement (4 vs 2) and ambition_status (2 vs 1).

### Authors (response generators)

3 author models: GPT-5.4, GPT-5.5 (xhigh reasoning, added in tri-model extension), Opus.

### Judges

3 judge models, drawn from 2 provider families (OpenAI: GPT-5.4, GPT-5.5; Anthropic: Opus).

### Scales

- Scalar rubric: 10 dimensions, 0–5 Likert.
- Red flags: enumerated taxonomy of 25 labels (full schema in `src/psycheeval/models.py:RedFlag`). Examples: `sycophancy_escalation`, `fake_certainty`, `generic_slop`, `missed_boundary`, `caricature_public_anchor`, `public_archetype_echo`, `style_mimicry_overfit`, `repair_avoidance`. Two PAE-specific labels (`caricature_public_anchor` and `public_archetype_echo`) are defined but were never assigned by any judge in the v0.1 corpus — the PAE evidence in §10 rests on indirect labels (`generic_slop`, `overpersonalization`), not direct PAE labels.
- Pairwise: forced choice (A wins / B wins / tie), with rationale.

### Blinding

Each output is given a hashed `run_id` before being shown to a judge. Judges cannot see the author model, the condition, or the persona type.

---

## 5. Final tri-model data inventory

| Channel | Records | Status |
|---|---|---|
| Assistant outputs (per-cell math below) | 648 | complete |
| Scalar judging (3 judges × 648) | 1,944 | complete |
| Pairwise — GPT-5.4 judge (same-author scope) | 1,152 | complete |
| Pairwise — GPT-5.5 judge (same-author scope) | 1,152 | complete |
| Pairwise — Opus judge (same-author scope) | 1,152 | complete |
| Validation warnings (judges producing invalid red_flag labels) | 0 | clean |

### Per-cell math

Each (author, condition, persona, scenario) tuple produces exactly one assistant output:

| Slice | Math | Outputs |
|---|---|---|
| C0/C1/C3/C4 (4 conditions × all 8 personas × 6 scenarios per persona × 3 authors) | 4 × 8 × 6 × 3 | 576 |
| C5 (PI-only: 4 PI personas × 6 scenarios × 3 authors) | 4 × 6 × 3 | 72 |
| **Total** | | **648** |

PI-only slices (used in §7b, §8a) cover 4 PI personas × 6 scenarios × 3 authors = 72 outputs per condition, judged 3× = 216 scalar records per condition. PS-only slices (§8b) cover 4 PS personas × 6 scenarios × 3 authors = 72 outputs per condition, judged 3× = 216 scalar records.

### Pairwise scope

`same-author`: both responses in the head-to-head come from the same author model, so the comparison isolates condition effects rather than author effects. Cross-author pairs (e.g. Opus C4 vs GPT-5.4 C4) were not judged.

Pairwise counts per judge derive cleanly from condition-pair geometry. There are 10 unordered condition pairs total (`{C0,C1,C3,C4,C5} choose 2`); 4 of those involve C5, which is PI-only.

| Slice | Math | Pairs per judge |
|---|---|---|
| Non-C5 pairs (6 pairs × 8 personas × 6 scenarios × 3 authors) | 6 × 8 × 6 × 3 | 864 |
| C5 pairs (4 pairs × 4 PI personas × 6 scenarios × 3 authors) | 4 × 4 × 6 × 3 | 288 |
| **Per judge** | | **1,152** |
| **Across 3 judges** | 1,152 × 3 | **3,456** |

---

## 6. Primary pairwise findings

### Methods note (filter scopes)

Two related but distinct pairwise scopes are reported in this section and §14a:

- **§6 — all-judges-pooled, judge-stratified.** Each pair's win rate aggregates over all three judges *without* a cross-provider filter, then is also broken out per judge so that exact-self halo (a judge scoring its own family's outputs) is visible rather than hidden. With three judges from two provider families, half of the same-author records are exact-self for one of the GPT judges; pooling without stratification would let that halo silently inflate apparent significance.
- **§14a — cross-provider-only.** Removes any record where the judge's provider family equals the author's family. This is the more conservative scope; some §6 pooled `***` flags do not survive it (notably C1 vs C5).

Both views are produced by the same analyzer; neither is "correct" — they answer different questions.

`low` win rate = win rate of the lower-numbered condition in each pair. Wilson 95% CIs are computed on **decisive** outcomes (ties excluded from denominator). `***` is a mechanical flag indicating CI excludes 0.5; it is not a strength indicator on its own. A `***` flag with a CI that hugs 0.5 is a near-call, not a robust win — read the CI, not the asterisks. Because the same persona × scenario × author cell appears in multiple condition-pair rows, the Wilson assumption of independent Bernoulli trials over-states effective n; per-cell clustering would widen these CIs (see §12, *Pairwise CIs assume independence*).

This section's headline reading: **explicit behavioral conditioning beats simple trait conditioning, and all conditioning beats baseline, within the same-author scope.** Cross-author comparisons were not judged in v0.1 (see §12, *Same-author pairwise scope only*); the within-same-author qualifier is load-bearing.

### 6a. Robust across all three judges (CI excludes 0.5 for every judge slice)

| Pair | Pooled `low` win | GPT-5.4-only | GPT-5.5-only | Opus-only | Reading |
|---|---|---|---|---|---|
| C0 vs C1 | 0.264 [0.224, 0.308] *** | 0.354 [0.281, 0.435] *** | 0.243 [0.180, 0.319] *** | 0.188 [0.131, 0.263] *** | C1 beats C0 |
| C0 vs C3 | 0.185 [0.151, 0.225] *** | 0.292 [0.224, 0.371] *** | 0.174 [0.120, 0.244] *** | 0.086 [0.050, 0.145] *** | C3 beats C0 |
| C0 vs C4 | 0.237 [0.199, 0.279] *** | 0.319 [0.249, 0.399] *** | 0.208 [0.150, 0.282] *** | 0.180 [0.125, 0.252] *** | C4 beats C0 |
| C0 vs C5 | 0.284 [0.228, 0.347] *** | 0.347 [0.248, 0.462] *** | 0.250 [0.164, 0.361] *** | 0.254 [0.167, 0.366] *** | C5 beats C0 (PI-only) |
| C1 vs C3 | 0.274 [0.234, 0.318] *** | 0.319 [0.249, 0.399] *** | 0.229 [0.168, 0.304] *** | 0.273 [0.206, 0.353] *** | C3 beats C1 |
| C1 vs C4 | 0.329 [0.287, 0.375] *** | 0.375 [0.300, 0.456] *** | 0.299 [0.230, 0.378] *** | 0.314 [0.243, 0.395] *** | C4 beats C1 |

**Headline framing (within same-author scope)**: All conditioning beats baseline, and explicit behavioral conditioning (C3, C4) beats simple trait conditioning (C1). These are the strongest within-author findings of v0.1. PI and PS contribute equal n for these non-C5 pairs (192 PI records + 192 PS records per pair = 384 each, 384/judge × 3 judges via §6); PS baseline red-flag rates are higher (§8b) which provides more statistical separation per record, so the PS contribution likely drives more of the *signal-to-noise* even though the *n* itself is balanced. PI/PS-stratified pairwise rates are reported in §6e.

### 6b. Judge-dependent (some judge slices `***`, others straddle 0.5)

| Pair | Pooled | GPT-5.4-only | GPT-5.5-only | Opus-only | Reading |
|---|---|---|---|---|---|
| C3 vs C4 | 0.446 [0.400, 0.494] *** | 0.521 [0.440, 0.601] | 0.417 [0.339, 0.498] *** | 0.400 [0.323, 0.483] *** | C4 over C3 — GPT-5.4 cannot distinguish |
| C1 vs C5 | 0.426 [0.362, 0.493] *** | 0.500 [0.387, 0.613] | 0.306 [0.211, 0.420] *** | 0.472 [0.361, 0.586] | C5 over C1 — only GPT-5.5 calls it; GPT-5.4 and Opus indistinguishable |
| C3 vs C5 | 0.565 [0.498, 0.630] | 0.639 [0.524, 0.740] *** | 0.514 [0.401, 0.626] | 0.543 [0.427, 0.654] | GPT-5.4 calls C3 over C5; GPT-5.5 and Opus cannot |
| C4 vs C5 | 0.523 [0.457, 0.589] | 0.639 [0.524, 0.740] *** | 0.417 [0.310, 0.532] | 0.514 [0.401, 0.626] | GPT-5.4 calls C4 over C5; GPT-5.5 and Opus cannot |

**Headline framing**: C5-involving pairs behave very differently across judges. **GPT-5.4 is the only judge that pairwise-prefers behavioral contracts to source packets** (C3 over C5 ***, C4 over C5 ***). GPT-5.5 and Opus cannot reliably distinguish C5 from C3 or C4. This is a meaningful inter-judge disagreement: the report's earlier "Opus distinguishes, GPT cannot" framing was correct on C3 vs C4 but reversed on C5 pairs. The pooled-GPT column hid this, because pooling across two GPT judges that disagree masks the disagreement.

### 6c. (removed)

The previous §6c grouped C3 vs C5 and C4 vs C5 as "pairwise-indistinguishable across all judges." The judge-stratified view in §6b shows this is wrong: GPT-5.4 distinguishes them. The honest reading is that **GPT-5.5 and Opus cannot distinguish C5 from C3/C4**; GPT-5.4 can. Whether GPT-5.4 is detecting structural weakness or applying a different rubric is an open question for v0.2.

### 6d. Cross-provider-only same-author cross-check

Reproducing §6a/§6b under the cross-provider filter (judge ≠ author family) — the more conservative scope. This drops same-provider records (~50%) and removes exact-self halo entirely.

| Pair | Cross-provider `low` win | n_decisive | vs §6 pooled (∆) | Note |
|---|---|---|---|---|
| C0 vs C1 | 0.273 [0.214, 0.342] *** | 183 | +0.009 | unchanged direction |
| C0 vs C3 | 0.187 [0.138, 0.249] *** | 187 | +0.002 | unchanged |
| C0 vs C4 | 0.267 [0.209, 0.335] *** | 187 | +0.030 | unchanged |
| C0 vs C5 | 0.263 [0.185, 0.360] *** | 95 | −0.021 | unchanged |
| C1 vs C3 | 0.246 [0.190, 0.312] *** | 187 | −0.028 | unchanged |
| C1 vs C4 | 0.346 [0.281, 0.416] *** | 188 | +0.017 | unchanged |
| **C1 vs C5** | **0.417 [0.323, 0.517]** | 96 | −0.009 | **`***` lost** — CI now straddles 0.5 |
| **C3 vs C4** | **0.457 [0.388, 0.529]** | 188 | +0.011 | **`***` lost** — CI now straddles 0.5 |
| C3 vs C5 | 0.564 [0.463, 0.660] | 94 | −0.001 | indistinguishable in both views |
| C4 vs C5 | 0.490 [0.392, 0.588] | 96 | −0.033 | indistinguishable in both views |

**Headline framing**: Under the more conservative cross-provider filter, two of the §6 marginal `***` flags do not survive (C1 vs C5, C3 vs C4). The §6a robust findings all survive. This is one reason to read the §6 `***` flags as mechanical, not as strength indicators.

### 6e. Tie rates per pair

Pairwise judgments allow A / B / tie. Throughout §6a–§6d, win rates are computed on **decisive** outcomes only (ties excluded from denominator). Tie rates are reported here for completeness; v0.1 pairwise judges rarely tie.

| Pair | total | decisive | ties | tie rate | lo decisive win |
|---|---:|---:|---:|---:|---:|
| C0 vs C1 | 432 | 421 | 11 | 2.5% | 0.264 |
| C0 vs C3 | 432 | 427 | 5 | 1.2% | 0.185 |
| C0 vs C4 | 432 | 427 | 5 | 1.2% | 0.237 |
| C0 vs C5 | 216 | 215 | 1 | 0.5% | 0.284 |
| C1 vs C3 | 432 | 427 | 5 | 1.2% | 0.274 |
| C1 vs C4 | 432 | 428 | 4 | 0.9% | 0.329 |
| C1 vs C5 | 216 | 216 | 0 | 0.0% | 0.426 |
| C3 vs C4 | 432 | 428 | 4 | 0.9% | 0.446 |
| C3 vs C5 | 216 | 214 | 2 | 0.9% | 0.565 |
| C4 vs C5 | 216 | 216 | 0 | 0.0% | 0.523 |

Tie rates are uniformly under 3%; ties are not driving any of the §6 conclusions. The forced-choice pairwise format is producing decisive outcomes at near-ceiling rates, which has its own concern (§12 *Forced-choice pairwise compresses information*) but does not shift the win-rate point estimates.

### 6f. PI/PS-stratified pairwise (non-C5 pairs)

The §6a robust findings hold equally in PI-only and PS-only slices. Same-author pairwise stratified by persona type, all judges pooled, decisive only:

| Pair | PI lo win | PI CI | PI n | PS lo win | PS CI | PS n |
|---|---:|---|---:|---:|---|---:|
| C0 vs C1 | 0.214 | [0.164, 0.274] | 215 | 0.316 | [0.256, 0.382] | 206 |
| C0 vs C3 | 0.167 | [0.123, 0.223] | 215 | 0.203 | [0.154, 0.262] | 212 |
| C0 vs C4 | 0.228 | [0.177, 0.288] | 215 | 0.245 | [0.192, 0.307] | 212 |
| C1 vs C3 | 0.284 | [0.228, 0.347] | 215 | 0.264 | [0.209, 0.327] | 212 |
| C1 vs C4 | 0.326 | [0.266, 0.391] | 215 | 0.333 | [0.273, 0.399] | 213 |
| C3 vs C4 | 0.440 | [0.375, 0.506] | 216 | 0.453 | [0.387, 0.520] | 212 |

Direction is identical in PI and PS for every pair, with point estimates within ~0.05 of each other. The C0 vs C1 pair is the only one where the PI and PS estimates differ enough to read differently — PS shows a weaker C1 effect (0.316 vs PI's 0.214). Across the board, the §6a "all conditioning beats baseline" and "behavioral beats trait" findings are not driven by either persona type alone.

C5 pairs are not included here because C5 is PI-only by construction.

### 6g. Length-bucketed pairwise for C5 pairs (length confound diagnostic)

Per §12 (*Length confound*), C5 outputs are 30–40% longer than C0–C4 outputs (mean 518 words vs 372–400). To test whether C5's pairwise competitiveness is a length artifact, here is each C5-involving pair stratified by the lower-numbered condition's response length minus the higher-numbered condition's response length within the same persona × scenario × author cell. Negative buckets = C5 longer; positive = C5 shorter.

Each row: low-condition's decisive win rate within that length bucket. Wilson CIs.

**C0 vs C5** (C0 is the no-profile baseline):

| Length bucket | n | lo (C0) decisive win | CI |
|---|---:|---:|---|
| C0 much shorter (>100 words) | 98 | 0.378 | [0.288, 0.476] |
| C0 moderately shorter (20–100) | 48 | 0.062 | [0.021, 0.168] |
| similar (±20) | 27 | 0.222 | [0.106, 0.408] |
| C0 moderately longer (20–100) | 33 | 0.273 | [0.151, 0.442] |
| C0 much longer (>100) | 9 | 0.667 | [0.354, 0.879] |

C0 vs C5 is **almost entirely length-mediated**. When C0 is much-shorter than C5, C5 wins 62.2% of decisive judgments. When C0 is moderately shorter, C5 wins 93.8%. When C0 is much-longer, C0 *wins* 66.7%. The §6a "C5 beats C0" headline is largely a "longer wins" finding for this pair.

**C3 vs C5**:

| Length bucket | n | lo (C3) decisive win | CI |
|---|---:|---:|---|
| C3 much shorter | 79 | 0.582 | [0.472, 0.685] |
| C3 moderately shorter | 54 | 0.481 | [0.354, 0.611] |
| similar | 27 | 0.667 | [0.478, 0.814] |
| C3 moderately longer | 36 | 0.528 | [0.370, 0.680] |
| C3 much longer | 18 | 0.667 | [0.437, 0.837] |

C3's pairwise win over C5 is **stable across length buckets** — point estimates 0.48–0.67. C3 wins regardless of length difference, suggesting structural advantage rather than length confound.

**C4 vs C5**:

| Length bucket | n | lo (C4) decisive win | CI |
|---|---:|---:|---|
| C4 much shorter | 93 | 0.559 | [0.458, 0.656] |
| C4 moderately shorter | 48 | 0.500 | [0.364, 0.636] |
| similar | 15 | 0.267 | [0.109, 0.520] |
| C4 moderately longer | 27 | 0.370 | [0.215, 0.558] |
| C4 much longer | 33 | 0.697 | [0.527, 0.826] |

C4's pattern is **U-shaped and length-mediated.** When C4 and C5 are similar in length, C4 wins only 26.7% of decisive judgments — the lowest C4-vs-C5 rate in any bucket. When C4 is much-longer, C4 wins 69.7%. The C4-over-C5 advantage in §6b's pooled view is largely a length effect; once length is held roughly constant, C4 *loses* to C5 in this slice.

**C1 vs C5**: pattern is more uniform across buckets (0.37–0.56) — no strong length signal in either direction.

**Bottom line**: the C5 pairwise story breaks cleanly into two findings under length-bucketing. (1) C3's pairwise advantage over C5 is robust to length — structural. (2) C4's pairwise advantage over C5 is length-mediated — disappears or reverses when length is held constant. (3) C0 vs C5 is dominated by length. v0.2's `C1_padded` and `C4_shuffled` are the right tests; the v0.1 length analysis already suggests that some §6 marginal findings will not survive length-controlled comparisons.

---

## 7. Scalar findings

0–5 Likert means under the cross-provider judge filter (judge ≠ author family). The cross-provider scope removes exact-self halo from these tables; without it C0–C4 means would be roughly +0.1 higher on average, dominated by the GPT-judge pairs.

### Methods and caveats up front

A few framing notes before reading the tables:

- **Effect-size caveat (read this first).** v0.1 means cluster between 4.0 and 4.8 on a 0–5 scale. Inter-judge agreement on red-flag labels is κ ≈ 0.3 (§11b). Differences of 0.05–0.20 between conditions are within the per-cell standard error these data can support; they should be read as descriptive, not as significance-tested. v0.1 reports point estimates only — no scalar SEs, paired bootstrap CIs, or Cohen's d. v0.2 introduces the anchored 0–10 rubric specifically to recover headroom. Treat scalar gaps below ~0.20 with corresponding skepticism.
- **n is records, not outputs.** C0–C4 rows in §7a use 192 records per cell (cross-provider filter on 432 all-persona records). C5 in §7a uses 96 records (cross-provider filter on 216 PI-only records). PI-only §7b uses 96 records for every cell. All "n" values reflect cross-provider filtered records; per-cell raw output counts are 144 / 72 (see §5 per-cell math).
- **Mixed filters across §6 vs §7 vs §8.** §7 uses cross-provider; §8 red flags use all three judges; §6 pairwise uses all-judges-pooled with judge stratification. Each scope is reported under its own filter, and comparisons between sections should account for the difference. There is no single "canonical" filter — different questions call for different filters.

### 7a. Pooled across all personas (cross-provider, n=192 per C0–C4 cell, n=96 for C5 PI-only)

| Cond | helpful | profile_fit | calibrated | anti_syc | agency | epistemic | emotional | boundary | non_caric | transfer | row mean (10 dims) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 4.06 | 3.85 | 4.19 | 4.34 | 4.01 | 3.76 | 3.81 | 4.46 | 4.41 | 4.19 | 4.11 |
| C1 | 4.24 | 4.17 | 4.42 | 4.57 | 4.20 | 3.80 | 3.94 | 4.50 | 4.60 | 4.34 | 4.28 |
| C3 | 4.42 | 4.32 | 4.48 | 4.64 | 4.37 | 3.96 | 4.10 | 4.63 | 4.72 | 4.52 | 4.42 |
| C4 | 4.40 | 4.35 | 4.49 | 4.68 | 4.33 | 4.10 | 4.17 | 4.62 | 4.72 | 4.46 | 4.43 |
| C5 (PI-only) | 4.46 | 4.23 | 4.55 | 4.69 | 4.36 | 3.90 | 4.20 | 4.74 | 4.70 | 4.53 | *4.44* |

The C5 row in §7a is **not** apples-to-apples with C0–C4: C5 covers only PI personas (which are easier scenarios on average), while C0–C4 cover all 8 personas. The C5 row mean of 4.44 is shown in italics to discourage cross-row comparison; the PI-only table in §7b is the comparable view. Glance at §7b first.

### 7b. PI-only scalar means — apples-to-apples for C5 (cross-provider, n=96 per cell, all 10 dimensions)

| Cond | helpful | profile_fit | calibrated | anti_syc | agency | epistemic | emotional | boundary | non_caric | transfer |
|---|---|---|---|---|---|---|---|---|---|---|
| C0 | 4.34 | 4.04 | 4.44 | 4.50 | 4.30 | 3.90 | 4.06 | 4.80 | 4.54 | 4.46 |
| C1 | 4.56 | 4.41 | 4.67 | 4.85 | 4.52 | 3.91 | 4.25 | 4.84 | 4.78 | 4.64 |
| C3 | 4.63 | 4.43 | 4.60 | 4.77 | 4.62 | 4.07 | 4.22 | 4.80 | 4.77 | 4.73 |
| C4 | 4.65 | 4.47 | 4.59 | 4.76 | 4.55 | 4.05 | 4.27 | 4.78 | 4.79 | 4.67 |
| **C5** | **4.46** | **4.23** | **4.55** | **4.69** | **4.37** | **3.90** | **4.20** | **4.74** | **4.70** | **4.53** |

In the PI-only slice **C5 is below C1, C3, and C4 on all 10 scalar dimensions** (verified directly against the table above). Relative to the no-profile baseline C0, C5 is higher on 8 of 10 dimensions, tied on `epistemic_hygiene` (3.90 = 3.90), and lower on `boundary_safety` (4.74 < 4.80) — so C5 still beats no-conditioning on most of the rubric, but loses to every other conditioning condition. The largest gaps vs C3/C4 are on `profile_fit` (C5 = 4.23 vs C3 = 4.43, C4 = 4.47), `helpfulness` (C5 = 4.46 vs C3 = 4.63, C4 = 4.65), `transfer_value` (C5 = 4.53 vs C3 = 4.73, C4 = 4.67), and `epistemic_hygiene` (C5 = 3.90 vs C3 = 4.07, tied with the no-profile baseline). On `boundary_safety` C5 = 4.74 is the lowest of all five conditions — earlier presentations that paired the C5 PI-only number with C0–C4 all-persona numbers made it appear to be the highest, an artifact of the unfair comparison. The gap to C1 is narrower than the gap to C3/C4 on most dimensions; the widest C5-vs-C1 gap is on `profile_fit` (4.23 vs 4.41).

The gaps are real but mostly modest in magnitude (0.05–0.25). At the rubric's near-ceiling resolution and κ ≈ 0.3 inter-judge agreement, this is suggestive directional evidence rather than significance-tested findings; see §10 for how PAE confounds with the structural difference between C5 and C3/C4.

---

## 8. Red-flag findings

Per-record incidence of any red-flag label, computed across all three judges (no cross-provider filter on this section). PI and PS personas are reported separately. PS personas show roughly 3× the any-flag rate of PI personas, but the difference is *not* explained by scenario difficulty — both PI and PS subsets have identical mean difficulty 3.58 with the same 1–5 distribution. The likely driver is family mix: PS scenarios skew toward `shame_self_interpretation` (4 of 24 vs 1 of 24 for PI), which produces more boundary and repair-avoidance flags. The "PS lives in harsher terrain" framing rests on family composition, not difficulty.

### 8a. PI-only (public-inspired personas, all-judges-pooled)

| Cond | records | any-flag rate | avg flags per record | top labels |
|---|---|---|---|---|
| C0 | 216 | 10.2% | 0.139 | generic_slop (12), missed_boundary (4), pseudo_depth (4) |
| C1 | 216 | 6.5% | 0.079 | missed_boundary (6), generic_slop (3), pseudo_depth (3) |
| C3 | 216 | 8.3% | 0.102 | missed_boundary (10), fake_certainty (4), generic_slop (2) |
| C4 | 216 | 7.4% | 0.083 | missed_boundary (9), generic_slop (4), fake_certainty (2) |
| **C5** | **216** | **12.5%** | **0.181** | **missed_boundary (11), generic_slop (8), overpersonalization (7)** |

C5 has the highest any-flag rate in the PI-only slice — even higher than the no-profile baseline. The label profile is distinctive: `generic_slop` and `overpersonalization` are concentrated in C5 specifically, where they are scarce in C3 and C4.

The two red-flag labels most directly aligned with the public-archetype-echo hypothesis — `caricature_public_anchor` and `public_archetype_echo` — were never assigned by any judge in v0.1, despite being available in the schema. The flags concentrated in C5 are the indirect labels (`generic_slop`, `overpersonalization`) rather than the direct PAE labels. The label distribution is **consistent with PAE** but is not the direct PAE signature the schema was designed to capture; it could equally reflect "C5 outputs are less specific to this scenario than C3/C4 outputs," which is a different (and weaker) claim. See §10 for the PAE-vs-confound analysis.

### 8b. PS-only (pure-synthetic personas; no C5)

| Cond | records | any-flag rate | top labels |
|---|---|---|---|
| C0 | 216 | 34.7% | missed_boundary (31), repair_avoidance (18), generic_slop (13) |
| C1 | 216 | 33.3% | missed_boundary (31), fake_certainty (16), repair_avoidance (14) |
| C3 | 216 | 22.7% | missed_boundary (24), fake_certainty (8), unsafe_specificity (8) |
| C4 | 216 | 22.2% | missed_boundary (26), fake_certainty (9), therapy_cosplay (6) |

The conditioning effect on red-flag reduction (≈12 percentage points C0→C3) is larger on PS than on PI, but the ordering is the same: explicit behavioral conditioning reduces red flags relative to baseline and trait-only conditioning.

---

## 9. Scalar/pairwise pattern around C5 — open question, not core finding

C5 produces mixed signals across the three measurement channels. Scalar and red-flag analyses show C5 below C3/C4 on the PI-only slice (any-flag rate 12.5% vs C3's 8.3% and C4's 7.4%; profile_fit 4.23 vs C3/C4 ≈ 4.45). Pairwise judging gives a more complicated picture: C3 vs C5 and C4 vs C5 are pairwise-indistinguishable for GPT-5.5 and Opus, but **GPT-5.4 distinguishes them in C3/C4's favor** (C3 vs C5 = 0.639 ***, C4 vs C5 = 0.639 *** — see §6b). This is itself a judge-disagreement finding, not a uniform null.

There are at least three possible readings of this pattern, and v0.1's length-bucketed analysis (§6g) starts to discriminate among them:

1. **Channel-sensitivity asymmetry.** Scalar rubrics weight profile-fit and red-flag dimensions heavily; pairwise judging weights surface fluency and contextual appropriateness; the rubrics surface different aspects of the same outputs. Under this reading, GPT-5.4 is the only judge whose pairwise rubric is sensitive enough to register the structural weaknesses the scalar tables show.
2. **Length confound — partially confirmed by §6g.** C5 outputs are substantially longer (mean 518 words vs C0–C4's 372–400 words — see §12, *Length confound*). The §6g length-bucketed analysis shows that **C4's pairwise advantage over C5 is length-mediated** (C4 wins only when much-longer; loses 26.7% when similar in length), while **C3's pairwise advantage over C5 is robust across length buckets** (0.48–0.67 across all buckets). C0 vs C5 is dominated by length almost entirely. So length confound is real for C0 vs C5 and for C4 vs C5; it is *not* the explanation for C3 vs C5.
3. **Scalar-PAE confound.** C5's scalar gap on `profile_fit` may reflect the structural absence of behavioral-contract instructions in C5 (see §10), not a quality difference per output. The scalar rubric measures what the contract instructed; C5 has no contract; the gap is by construction.

Earlier framing of this as a "core v0.1 finding about measurement" overstates what one condition's mixed signals can support. The §6g length analysis sharpens the story: the C5 pairwise pattern fragments into pair-specific findings rather than a single channel-divergence finding. C3 over C5 is structural; C4 over C5 is partly length; C5 over C0 is mostly length. The honest framing is **"C5 channel divergence resolves into pair-specific findings under length stratification, several of which need v0.2 controls (`C1_padded`, `C4_shuffled`) to settle"** — not "scalar/pairwise tension is a core finding." The §10 hedging is the calibrated reading; this section now matches it.

---

## 10. Public-archetype echo: a hypothesis confounded with structural difference

The public-archetype-echo (PAE) hypothesis predicts that profile conditioning built from a public anchor — a familiar archetype the assistant can invoke from training data — will produce responses that recognize the *type* but miss the *individual*. Concretely, PAE predicts elevated `generic_slop`, elevated `overpersonalization`, weaker `profile_fit` than a behavioral-contract condition, and intact or even elevated surface fluency.

The v0.1 evidence for PAE:

- **Scalar (PI-only)**: C5 is the lowest-scoring conditioning condition on **all 10 dimensions** vs C1/C3/C4, while still beating C0 on 8 of 10. Consistent with PAE.
- **Red flags (PI-only)**: C5 has the highest any-flag rate among conditioning conditions, with `generic_slop` and `overpersonalization` concentrated in C5. Consistent with PAE.
- **Pairwise**: GPT-5.4 distinguishes C3 and C4 from C5 (C3 vs C5 = 0.639 ***, C4 vs C5 = 0.639 ***). GPT-5.5 and Opus cannot. The strong-form PAE prediction that all pairwise judges detect the structural weakness is **not** supported; the partial-form prediction (a more discriminative judge can detect it) is consistent with GPT-5.4's pattern.
- **Direct PAE labels**: `caricature_public_anchor` and `public_archetype_echo` were never assigned by any judge in v0.1. The schema was designed to capture PAE specifically; the indirect labels (`generic_slop`, `overpersonalization`) are doing all the work.

### The structural-difference confound (load-bearing)

C5 is **not** a pure test of public-archetype echo. C5 omits the behavioral contract entirely (§4: "*does not* include the structured behavioral contract"). C3 and C4 *do* include the contract — the contract specifies how the assistant should engage the user, including profile-fit instructions. So C5 underperforming C3/C4 on `profile_fit` is at least partly **a tautology**: C5 has no profile-fit instructions because C5 has no contract.

To distinguish PAE from "no behavioral contract = lower profile_fit," v0.1 would need either:

1. A **C5-with-contract** condition (source packet plus contract) — would let us isolate the source-packet effect on top of identical contract instructions, or
2. A **non-public source-packet, no-contract** condition — would let us isolate the public-anchor effect from the absence of contract.

Neither exists in v0.1. The C5 evidence is **consistent with PAE**, but it is **also fully consistent with** "any condition without a behavioral contract underperforms on profile-fit-driven dimensions." These two stories make identical scalar predictions in v0.1; the indirect red-flag labels do not discriminate them either, since `generic_slop` and `overpersonalization` are also predicted by "no contract guiding response specificity."

PAE remains a hypothesis worth tracking, but v0.1 does not test it cleanly. v0.2 should add at least one of the discriminating conditions, or the PAE framing should be retired in favor of the more conservative "behavioral contracts are load-bearing, full stop." The §1 framing has been narrowed to match this caveat.

---

## 11. Judge halo and inter-judge agreement

Adding GPT-5.5 made it possible to distinguish *exact-self halo* (judge prefers outputs authored by itself) from *same-provider halo* (judge prefers outputs authored by a sibling in the same provider family). With one model per provider, the two are inseparable. Three buckets become possible with three models from two families.

### 11a. Halo audit on `calibrated_challenge` at C0 — narrowed to a single-cell finding

The halo-audit table is indexed by **(condition, author)**, not by judge. The row labeled `C0 × <model>` reports, for outputs *authored* by that model under condition C0, how various judge groups score those outputs relative to cross-provider judges' scoring of the same outputs.

| Author | exact_self − cross_provider (= self judging) | same_provider − cross_provider (= sibling judging) | Notes |
|---|---|---|---|
| GPT-5.4-authored | +0.771 | +0.458 | GPT-5.4 scores its own outputs +0.771 higher on `calibrated_challenge` than cross-provider judges (Opus) score the same outputs; GPT-5.5 scores GPT-5.4-authored outputs +0.458 higher than Opus does. |
| GPT-5.5-authored | +0.646 | **+0.729** | GPT-5.5 scores its own outputs +0.646 higher than Opus does; **GPT-5.4 (sibling judge) scores GPT-5.5-authored outputs +0.729 higher than Opus does** — larger than GPT-5.5's own self-bias on these outputs. |
| Opus-authored | +0.021 | n/a (no Anthropic sibling) | Opus scoring its own Opus-authored outputs vs cross-provider (= GPT) judges scoring the same outputs. |

**The headline finding (corrected, narrowed):** for GPT-5.5-authored outputs on `calibrated_challenge` at C0, the sibling judge (GPT-5.4) shows a larger halo (+0.729) than the self judge (GPT-5.5, +0.646). The directional reading: a same-family judge can be **more** generous to a sibling's outputs than the sibling is to its own. This is one cell — one dimension, one condition, one author × judge configuration. It is not a general claim that "same-provider halo always exceeds exact-self halo." Other cells in §14b show the opposite ordering (e.g. GPT-5.5-authored on `emotional_accuracy`: exact_self +0.625, same_provider +0.521).

The narrower defensible claim is that **the two halo types are separable when more than one model per provider is in the panel**, and that on at least one combination of dimension × condition × author the same-provider halo can exceed the exact-self halo. The earlier framing "same-provider preference can exceed exact-self preference" is left in place for that one cell but should not be read as a multi-cell or general property. v0.2's expanded panel and anchored rubric should resolve whether this generalizes.

**Opus's near-zero exact-self halo on `calibrated_challenge` is suggestive but not yet distinct from a stricter-scoring artifact.** §14b shows that on `emotional_accuracy`, Opus scores its own outputs *below* cross-provider judges (−0.115). A truly low self-bias model wouldn't show negative deltas; the negative delta is more plausibly a sign that Opus rates *all* outputs more strictly, including its own, which compresses every halo measure toward zero (or below). On `profile_fit`, Opus's exact-self halo is +0.385 — within the range of the GPT models. The honest reading is that **Opus shows a structurally different halo signature from GPT-5.4 and GPT-5.5 — possibly less self-bias on calibrated_challenge specifically, possibly stricter scoring across the board.** A scalar-variance comparison (Opus vs GPT-5.4 vs GPT-5.5 across all conditions) is queued for v0.2.

A further alternative reading should be acknowledged: same-provider halo is consistent with at least three mechanisms that this study cannot distinguish — (a) provider-family preference, (b) stylistic similarity in outputs (sibling models recognize each other's structure and reward it), (c) shared training-data biases that make particular phrasings feel correct to both. v0.2 should run a small stylometric check (response length, formatting density, hedging frequency) to discriminate (a) from (b)/(c).

### 11b. Inter-judge agreement on red-flag labels (Cohen's κ, n=648 overlap)

| Pair | mean κ across pair-defined label set | n labels with defined κ |
|---|---|---|
| GPT-5.4 ↔ GPT-5.5 | 0.32 | 18 |
| GPT-5.4 ↔ Opus | 0.33 | 20 |
| GPT-5.5 ↔ Opus | 0.29 | 19 |

The label count differs per pair because κ is undefined when one judge never assigns a label (or both judges always agree at zero); the per-pair count reflects only labels where κ is computable. The mean is taken over the defined-κ set for that pair.

Following Landis & Koch (1977) the 0.21–0.40 range is conventionally labeled "fair," 0.41–0.60 "moderate." Subsequent literature has criticized this scale as arbitrary; we report the numeric κ values directly to avoid leaning on the label. What matters operationally: **agreement is real but modest.** Pooling across judges is supported in the sense that a single judge cannot serve as ground truth, and majority-vote dynamics across three judges are visible (cross-judge convergence on the largest red-flag rates in §8a), but pooling does not rescue claims that depend on tight agreement. GPT-5.4 sits roughly equidistant from GPT-5.5 and Opus in this run — which is a coincidence to flag, not a conclusion.

**Important caveat for scalar pooling.** §11b reports inter-judge agreement on **red-flag labels**, not on the **scalar rubric**. Throughout §7 we pool scalar means across judges; that pooling rests on the implicit assumption that scalar agreement is at least as high as red-flag agreement. v0.1 does not measure scalar agreement directly — neither paired κ on dichotomized scalar judgments nor ICC / Krippendorff's α on the continuous scale. v0.2 should add this measurement before scalar pooling is treated as a robust methodological choice.

---

## 12. Threats to validity

Listed roughly in order of how much each affects the headline claims, not numerical importance.

1. **Same-author pairwise scope only.** Tri-model pairwise was run with `same_author_only` scope to isolate condition effects. Cross-author pairs (e.g. Opus C4 vs GPT-5.4 C4) were not judged. The §6 headlines ("all conditioning beats baseline," "behavioral > trait") are therefore robust **within author**, not as universal statements about assistant behavior. The TL;DR has been narrowed to reflect this scope qualifier.
2. **PAE confounds with the absence of behavioral contract.** The C5 vs C3/C4 scalar gap is consistent with public-archetype echo and equally consistent with "C5 has no profile-fit instructions." v0.1 cannot discriminate these (see §10). PAE is a hypothesis to track in v0.2, not a settled finding.
3. **Synthetic personas, synthetic scenarios.** Outputs are not validated against real users with real problems. Treatment effects observed here may not transfer to real users.
4. **Length confound (quantified).** Per-condition response length means in this run: C0 = 372 ± 144 words; C1 = 400 ± 131; C3 = 378 ± 156; C4 = 389 ± 131; **C5 = 518 ± 153 words**. C5 outputs are 30–40% longer than other conditions. Pairwise preferences for or against C5 may be tracking length rather than profile structure. v0.2 introduces `C1_padded` and `C4_shuffled` to test this directly; v0.1 does not.
5. **Pairwise CIs assume independence; effective n is over-stated.** The same persona × scenario × author cell appears in multiple condition-pair rows (it is in C0vsC1, C0vsC3, C0vsC4, C1vsC3, etc). Wilson CIs treating each pair record as an independent Bernoulli trial inflate effective n. A cluster-bootstrap CI by persona × scenario would widen the §6 intervals; some §6a `***` flags may not survive that widening. v0.1 reports Wilson CIs without clustering correction.
6. **Persona × condition imbalance for C5.** C5 only runs against PI personas. PI any-flag rates are ~10% in C0; PS rates are ~35%. Any cross-condition comparison involving C5 inherits this confound. The 8a/8b split addresses it for descriptive purposes; pairwise §6 comparisons involving C5 are PI-only by construction.
7. **Judge models from a small ecosystem.** Three judges from two providers is not a panel of human raters. Halo audits separate exact-self from same-provider, but inter-judge agreement on red-flag labels is modest (κ ≈ 0.3) and inter-judge agreement on **scalar** dimensions is unmeasured (§11b). The framework's measurement validity against human raters is unestablished.
8. **Forced-choice pairwise compresses information.** A/B with rare ties may compress signal that scalar judges resolve more granularly. The §9 channel pattern around C5 may partly reflect this asymmetry rather than substantive judgment difference. v0.2's anchored rubric should partially resolve scalar compression; pairwise compression is structural.
9. **Limited scenarios.** 48 scenarios in 8 families, of which only 6 are run per persona, is enough for hypothesis generation but not for population-level claims about scenario sensitivity. Each persona's 6-scenario subset is fixed across conditions and authors, which preserves within-persona comparability but limits cross-persona generalization.
10. **Likert ceiling effects.** v0.1 scalar means cluster between 4.0 and 4.8 on a 0–5 scale. Differences of 0.05–0.20 are at the per-cell standard error these data can support and are not significance-tested. v0.2's anchored 0–10 rubric should recover headroom.
11. **Mixed judge filters across sections.** §6 pairwise uses all-judges-pooled with judge stratification; §7 scalar uses cross-provider; §8 red flags uses all three judges. The methods note in §6 declares this; §7 and §8 should be read with the corresponding scope in mind. These are coherent choices but they are choices — different filters answer different questions.
12. **No human raters.** No comparison to a human ground-truth panel exists for v0.1 or v0.2. The framework's *measurement validity* against human judgment is unestablished and is the primary deliverable for an eventual validation study.

---

## 13. v0.2 implications

v0.2 is built around the open questions surfaced in v0.1. Split into research questions (what v0.2 should *answer*) and operational items (what v0.2 *requires*).

### Research questions

1. **Does C4 beat C1_padded?** Tests whether C4's advantage over C1 is structural (behavioral contract) or merely a length effect. C1_padded brings C1's length up to C4's without changing the content type.
2. **Does C4 beat C4_shuffled?** Tests whether coherent contract structure adds value beyond having the same words. C4_shuffled scrambles C4's structure while preserving content.
3. **Can a C5-with-contract or non-public-no-contract condition isolate PAE from the structural confound (§10)?** This is the load-bearing question for the PAE story. v0.1 cannot distinguish "public-archetype echo" from "no behavioral contract"; either of these conditions would cleanly isolate the source-packet effect.
4. **Do C5 red flags correlate with pairwise losses at the per-pair level?** If yes, red flags explain pairwise outcomes (channels are aligned, just with different sensitivity). If no, pairwise and red-flag channels are measuring different notions of quality.
5. **Which scenario families produce C5's scalar/red-flag pattern?** Candidates surfaced in v0.1: interpersonal_conflict, shame_self_interpretation, procrastination_avoidance, epistemic_uncertainty, creative_feedback. v0.2's harder scenarios should reveal whether C5 fails predictably by family or globally.
6. **Does the anchored 0–10 rubric resolve the Likert ceiling effect?** v0.1 means cluster in 4.0–4.8 on a 0–5 scale, putting many cell-to-cell differences at instrument noise floor. The anchored rubric should spread the distribution.
7. **Does the §11a single-cell same-provider halo finding generalize?** v0.1 surfaced one cell where same-provider halo exceeds exact-self halo (`calibrated_challenge` × C0 × GPT-5.5-authored). v0.2's expanded panel should test whether this generalizes across dimensions, conditions, and authors, or remains a single-cell artifact. A stylometric check (response length, formatting density, hedging) would help discriminate provider-family preference from stylistic-similarity / training-overlap mechanisms.
8. **Does scalar inter-judge agreement match red-flag agreement?** v0.1 only measured red-flag κ. Scalar pooling rests on an unmeasured assumption. v0.2 should add paired κ on dichotomized scalar judgments or ICC / Krippendorff's α on the continuous scale.
9. **Do cluster-bootstrap CIs change §6's significance pattern?** v0.1 reports Wilson CIs that assume independence; the same persona × scenario × author appears in multiple pair rows. Cluster-bootstrap by persona × scenario would widen the intervals and may invalidate marginal `***` flags.

### Operational items / dependencies

- Extend the corpus to include Opus as an author (currently only the codex side has run for v0.2). Queued in the project backlog; depends on Opus quota; does not block v0.2 as a 2-judge initial pilot.
- Add a methodology / measurement-validity sub-paper targeting the κ-on-scalar measurement (#8 above), since that gates the pooling justification used throughout §7.

### Proposed v0.2 / v0.3 condition expansions

To resolve the v0.1 confounds (especially the PAE-vs-no-contract issue surfaced in §10 and the length confound surfaced in §6g), candidate new conditions to add. Listed roughly in priority order:

| Code | Description | What it tests |
|---|---|---|
| **C5_CONTRACT** | Source packet **plus** the same behavioral contract used in C3/C4 | The load-bearing PAE separator. Holds the contract constant across C3/C4/C5_CONTRACT and varies only the source-packet vs no-source-packet axis. If C5_CONTRACT matches C3/C4 on profile_fit, the v0.1 C5 gap was the absent contract, not PAE. If C5_CONTRACT still underperforms C3/C4 on profile_fit, that's PAE evidence. |
| **C3_SOURCELESS** | Behavioral contract without any source packet (= current C3) — but make the comparison against C5_CONTRACT explicit | Reference point for the C5_CONTRACT test |
| **C5_NONPUBLIC** | Source-packet-style narrative for pure-synthetic personas (no public anchor) | Discriminates "public-archetype echo" from "any source-packet narrative." If C5_NONPUBLIC lands like C3, the v0.1 C5 gap is specifically about public anchoring; if it lands like C5, the gap is about source-packet form rather than its public-anchor content. |
| **C5_SHORT** | C5 source packet constrained to the same response length as C3/C4 (or shorter) | Direct length-confound resolution for the C5 pairwise pattern in §6g |
| **C5_BEHAVIORALIZED** | C5 source packet rewritten as if-then behavioral instructions (i.e. "translated" from prose to contract) | Tests whether prose-form is the locus of weakness, separate from source content |

Adding any of these requires regenerating outputs for the affected personas + scenarios + authors, and then judging. Per the existing v0.2 plan, only `C1_padded` and `C4_shuffled` are currently queued. **C5_CONTRACT is the load-bearing addition** for the PAE story and should be added to v0.2 if quota allows. The remaining C5_* variants are v0.3 candidates.

### Paper-targeted methodology work

These are not v0.2 deliverables; they are the methodology measurements needed to upgrade from "pilot" to "validated framework" for an eventual paper:

- **Cluster-bootstrap CIs** by persona × scenario × author, replacing or supplementing the Wilson CIs throughout §6. Disclosed in §12 as threat #5; v0.1 reports point estimates with Wilson but acknowledges the clustering issue.
- **Scalar inter-judge ICC / Krippendorff's α** to defend the scalar-pooling decision (§11b only measures red-flag κ).
- **Stylometric audit of provider-family halo** (response length, formatting density, hedging frequency) to discriminate among the (a) provider-family preference / (b) stylistic similarity / (c) shared training-data alternatives raised in §11a.
- **Human calibration sample** (~30–50 pairwise comparisons, 2–3 raters across C0/C1/C3/C4/C5) to establish how well model judges track human judgments on the dimensions PsycheEval claims to measure. The purpose is calibration of model judges against human judgment, not validation that PsycheEval works for real users — the latter is a separate program.
- **Unblinded mechanism audit for PAE.** The current red-flag audit is blinded to the source packet; a separate unblinded judge with C5 source-packet visibility could mark "responses that echo the public archetype rather than serving the scenario." Direct PAE labels (`caricature_public_anchor`, `public_archetype_echo`) were never assigned in the blinded v0.1 corpus; the indirect labels carry the inferential weight today.

---

## 14. Appendix

### 14a. Macro-averaged pair preference vs pooled (validation)

For the cross-provider same-author pairwise table, the analyzer computes both a pooled win rate (records weighted equally) and a macro-averaged win rate (weighted equally per judge × author stratum, then averaged). The two should agree closely; large divergence indicates a stratum imbalance.

| Pair | Pooled `low` win | Macro-avg `low` win | Strata |
|---|---|---|---|
| C0 vs C4 | 0.260 | 0.264 | gpt-5.4__opus, gpt-5.5__opus, opus__gpt-5.4, opus__gpt-5.5 |
| C1 vs C4 | 0.339 | 0.344 | (same 4) |
| C3 vs C4 | 0.448 | 0.455 | (same 4) |
| C3 vs C5 | 0.552 | 0.563 | (same 4) |
| C4 vs C5 | 0.490 | 0.490 | (same 4) |

Pooled and macro-averaged agree to within 0.01–0.02 on every pair. Stratum imbalance is not driving the headline numbers.

### 14b. Halo audit, all three buckets

Selected dimensions, cross-provider as the comparison baseline. Negative values mean the bucket scored *lower* than cross-provider judges on that dimension.

| Cond × Judge | Dimension | exact_self − cross | same_provider − cross | same_minus_cross (legacy) |
|---|---|---|---|---|
| C0 × GPT-5.4 | calibrated_challenge | +0.771 | +0.458 | +0.615 |
| C0 × GPT-5.5 | calibrated_challenge | +0.646 | +0.729 | +0.688 |
| C0 × Opus | calibrated_challenge | +0.021 | n/a | +0.021 |
| C0 × GPT-5.4 | emotional_accuracy | +0.750 | +0.667 | +0.708 |
| C0 × GPT-5.5 | emotional_accuracy | +0.625 | +0.521 | +0.573 |
| C0 × Opus | emotional_accuracy | −0.115 | n/a | −0.115 |
| C0 × GPT-5.4 | profile_fit | +0.396 | +0.438 | +0.417 |
| C0 × GPT-5.5 | profile_fit | +0.521 | +0.333 | +0.427 |
| C0 × Opus | profile_fit | +0.385 | n/a | +0.385 |

The legacy `same − cross` column is the two-bucket equivalent reported in the prior two-model report. The exact_self vs same_provider split was invisible in that earlier framing.

### 14c. Artifact status

| Artifact | Status |
|---|---|
| v0.1 original two-model report (`reports/psycheeval_v0_1_micro_pilot_2026-04-20_micro.md`) | Superseded |
| v0.1 revised two-model report (interim, prior to tri-model completion) | Superseded |
| v0.1 tri-model autogen scaffold (`reports/psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model_autogen.md`) | Superseded by this curated report |
| v0.1 tri-model scalar | Complete |
| v0.1 tri-model pairwise (GPT-5.4, GPT-5.5, Opus, same-author scope) | Complete |
| v0.1 tri-model metrics JSON (`reports/metrics_2026-04-26_micro_tri_model.json`) | Current |
| v0.1 tri-model failure cards (`reports/failure_cards_2026-04-26_micro_tri_model.md`) | Current |
| v0.1 curated tri-model report (this document) | **Current** |
| v0.2 code | Complete |
| v0.2 corpus (codex-side: 1,040 outputs from GPT-5.4 + GPT-5.5) | Complete |
| v0.2 anchored scalar (codex judges) | Complete |
| v0.2 pairwise (codex judges) | Complete |
| v0.2 Opus authoring + Opus judging | Queued (depends on Opus quota; do not start until v0.1 archive is final) |
| v0.2 curated report | Pending |

### 14d. Run inventory

- Tag: `2026-04-26_micro_tri_model`
- Base tag (extended): `2026-04-20_micro`
- Source files:
  - `runs/2026-04-26_micro_tri_model/assistant_outputs.jsonl` (648 outputs)
  - `runs/2026-04-26_micro_tri_model/judge_scores.jsonl` (1,963 records: 1,944 from the three official judges + 19 from `moonshotai/kimi-k2.6` partial test run)
  - `runs/2026-04-26_micro_tri_model/pairwise_scores.jsonl` (3,456 pairwise)
  - `runs/2026-04-26_micro_tri_model/blinding_key.json`
  - `runs/2026-04-26_micro_tri_model/run_manifest.jsonl`

The 19 Kimi records are a 4th-judge feasibility probe (Kimi K2.6 was tested as a possible additional judge for a later run) on 19 of the 648 outputs. They are excluded from all v0.1 analyses in this report; the 1,944 figure cited throughout § 5 and §11 reflects only the three official judges (GPT-5.4, GPT-5.5, Opus). κ values in §11b also exclude the Kimi records.
- Generated reports:
  - `reports/metrics_2026-04-26_micro_tri_model.json` (this analysis)
  - `reports/failure_cards_2026-04-26_micro_tri_model.md` (12 failure cases)
  - `reports/psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model_autogen.md` (autogen scaffold)
  - `reports/psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model.md` (this curated report)

---

v0.1 establishes that the harness can detect treatment effects within same-author scope and surfaces several open questions for v0.2 to settle: per-pair correlation between red-flag presence and pairwise loss, length-controlled comparison via `C1_padded` and `C4_shuffled`, scenario-family resolution of C5's pattern, and replication of the provider-judge bias structure under the anchored 0–10 rubric. The pilot's value is methodological: condition comparison, channel-disagreement diagnostics, and judge-bias measurement design — not yet validation that Psyche profiles improve outcomes for real users.
