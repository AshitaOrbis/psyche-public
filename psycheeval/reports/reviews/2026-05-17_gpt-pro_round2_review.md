I’ll treat §6 as the operative prompt and judge only against the inlined bundle. I’ll separate true report blockers from wording/robustness fixes, then give a prioritized v0.3 agenda.

---

I’ll stress-test whether “Tier 1” is a uniform category after AB/BA, with particular attention to estimator validity, residual confounds, and unstable claim framing.

---

## Bottom-line decision

v0.2 is **publishable only after a narrower rewrite and several pre-writing fixes**. The core empirical story should become:

> Structured behavioral contracts matter in some contrasts; the strongest surviving contrast is **C5_CONTRACT > C5**, but the mechanism is not isolated. **C5_CONTRACT does not beat C3 or C4 after AB/BA correction.** LLM pairwise judging in this setup had large order effects, especially for GPT-5.5 and Opus judges.

The current bundle still has report-blocking issues. The biggest ones are not philosophical; they are table/provenance/statistical issues.

---

# (A) Issues that would block the v0.2 report

## A1. The AB/BA result table and final Tier 1 summary are internally inconsistent

This blocks publication until reconciled.

### Count inconsistency

You state:

> Tier A: 873 swap-rejudge records
> 
> Tier B: 800 records
> 
> Total: 1,664 records

But the table gives Tier A as:

- C3 vs C5_CONTRACT: 288

- C4 vs C5_CONTRACT: 288

- C5 vs C5_CONTRACT: 288

That sums to **864**, not 873. And **864 + 800 = 1,664**, which matches the stated total.

So either “873” is a typo, or 9 records are missing from the table. This needs a single source of truth.

### C1_padded vs C4 estimate inconsistency

The AB/BA row says:

```
C1_padded vs C4orig lo_win = 0.319swap lo_win = 0.434controlled = 0.377CI = [0.324, 0.429]
```

If `lo` is C1_padded, then the controlled C4 win rate is:

```
1 - 0.377 = 0.623
```

So the AB/BA table implies **C4 wins 62.3%**, not **66.1%**.

But the Tier 1 summary says:

```
C4 > C1_padded: 68.1% → 66.1% C4 [59.5, 72.0]
```

That cannot be derived from the displayed AB/BA row. This is not a rounding issue. Either the row is wrong, the final Tier 1 summary is wrong, or `controlled` is not what the table says it is.

### C4 vs C5 estimate inconsistency

The AB/BA row says:

```
C4 vs C5controlled = 0.681CI = [0.606, 0.749]
```

But the Tier 1 summary says:

```
C4 > C5: 68.9% [61.6, 75.9]
```

That is a smaller mismatch than the C1_padded row, but still a mismatch. Fix before writing. Add a smoke test that checks:

```
final_report_estimate == transformed_abba_table_estimatefinal_report_CI == transformed_abba_table_CIpair counts sum to declared totals
```

Until this is fixed, the curated report should not be drafted.

---

## A2. The AB/BA correction may confound position with phase drift

The bundle describes Phase 1 as **swap-rejudging**, not full same-phase rejudging of both orientations. That implies:

```
controlled estimate = original AB judgments from earlier phase + later BA swap judgments
```

If true, then AB/BA correction is not purely estimating position bias. It also includes possible:

- judge model drift,

- provider deployment drift,

- prompt/pipeline changes,

- stochastic rejudge variance,

- run-date effects.

This matters because the headline methodological contribution is now the slot-B bias finding. To support that claim, you need a same-orientation repeatability check.

Minimum fix before report:

Run a small **same-orientation rejudge sentinel**:

```
For each major pair, rejudge a random subset in the original orientation during the same Phase 1/Phase 2 batch as the swapped orientation.
```

Then report:

```
original_AB win ratesame_phase_AB_rejudge win ratesame_phase_BA win rateAB-to-AB agreementAB-to-BA position shift
```

If same-orientation rejudging is stable, the AB/BA correction is credible. If not, widen uncertainty and avoid strong claims about slot-B bias magnitude.

---

## A3. Current CIs likely overstate precision unless they are paired/cluster robust

The displayed CIs look like record-level intervals. But the records are not independent. The design reuses:

- the same scenarios,

- the same personas,

- the same authors,

- the same judges,

- paired AB/BA versions of the same output pair,

- multiple judgments over the same underlying cell.

This especially threatens the marginal Tier 1 claim:

```
C4 > C4_shuffled: 57.8% [52.3, 63.1]
```

That effect is small. It may vanish under cluster bootstrap or paired-cell uncertainty.

Before writing, recompute all Tier 1 CIs using at least:

1. paired AB/BA cell bootstrap,

2. scenario-cluster bootstrap,

3. persona-cluster bootstrap,

4. scenario × persona cell bootstrap,

5. judge-cluster or judge-stratified meta-analysis,

6. author-stratified estimates.

The report should show naive CI versus cluster-robust CI. If only the naive CI clears 50%, the claim is exploratory.

---

## A4. C4 > C4_shuffled is over-tiered as written

The sign-correction is important, but the result should not sit beside C5_CONTRACT > C5 as equally robust.

Current result:

```
C4 > C4_shuffled: 57.8% [52.3, 63.1]
```

That is a modest effect, near the noise floor, discovered after an AB/BA correction in a setting with many pairwise comparisons and known judge-order artifacts.

Recommended wording:

> C4 modestly outperforms C4_shuffled under AB/BA-controlled pairwise judging, suggesting order/coherence may matter, but the effect is small and should be treated as suggestive until cluster-robust and judge-family checks confirm it.

Do not write:

> Coherent structure significantly beats shuffled structure.

That is too strong unless it survives paired/cluster CIs and judge-stratified checks.

---

## A5. C4 > C5 is not fully judge-family robust

You already note that Phase 0 found:

```
C4 vs C5 is OpenAI-judge-only; Opus n = 0
```

Phase 1 Tier B also appears to use only the two codex/OpenAI judges for non-C5_CONTRACT pairs.

So the result:

```
C4 > C5: 68.9% C4 [61.6, 75.9]
```

or table-implied:

```
68.1% C4 [60.6, 74.9]
```

should not be framed as a three-judge, cross-provider verdict.

Correct framing:

> In OpenAI-family pairwise judging, C4 beats C5 after AB/BA correction.

Not:

> C4 beats C5.

To make it Tier 1 without caveat, add Opus judging for C4 vs C5.

---

## A6. C0 dominated is probably real, but not AB/BA-controlled

You list:

```
C0 dominated: 86.6% C4
```

Because the observed slot-B bias is around 15–17pp in some judge configurations, a huge 86.6% effect likely survives correction. But the exact magnitude is not controlled.

Report it as:

> C4 overwhelmingly beats C0 in the original pairwise setup; given the size of the margin, this is unlikely to be explained solely by position bias, but it was not AB/BA tested.

Do not put it in the same evidentiary bucket as AB/BA-tested contrasts unless you run the swap.

---

## A7. C5_CONTRACT > C5 survives, but the mechanism claim must be narrowed

This is the strongest surviving C5_CONTRACT result.

You have:

```
C5_CONTRACT > C5:original = 76.0%AB/BA-controlled = 67.7%CI = [62.1, 72.8]judge-unanimousscalar-alignedsurvives Phase 0 + AB/BA
```

This is publishable.

But the mechanism claim must be much narrower.

Allowed claim:

> Adding the C5_CONTRACT wrapper to the C5 source-packet condition improves judged output quality relative to C5 alone.

Not allowed:

> Source packets add value when subordinated to contracts.

That claim died when:

```
C5_CONTRACT vs C3: 49.9% [44.3, 55.7]C5_CONTRACT vs C4: 51.8% [46.0, 57.5]
```

Also not allowed without C_GENERIC_CONTRACT:

> The behavioral contract specifically, rather than generic instruction scaffolding, length, salience, repetition, or formatting, caused the lift.

The C5_CONTRACT > C5 contrast tells you the package works. It does not isolate why.

Also, the attenuation is being misstated. The win rate moves:

```
76.0% → 67.7%
```

That is **8.3pp absolute attenuation**, not ~16pp. The above-parity edge shrinks from:

```
+26.0pp → +17.7pp
```

That is about a **32% reduction in edge size**. Still meaningful, but no longer “overwhelming.”

---

## A8. The LLM-judge slot-B bias finding is real enough to report, but not as a universal LLM fact

Your current framing:

> LLM judges show ~15–17pp systematic slot-B preference.

Better framing:

> In this pairwise judging setup, two of three judge configurations showed large later-answer / slot-B preference. GPT-5.5 and Opus showed substantial slot-B effects; GPT-5.4 showed little to none.

The per-judge pattern is the key result:

```
C3 vs C5_CONTRACT:gpt-5.4 = -3.6ppgpt-5.5 = +25.0ppOpus = +23.3ppC4 vs C5_CONTRACT:gpt-5.4 = +2.4ppgpt-5.5 = +25.0ppOpus = +23.8ppC5 vs C5_CONTRACT:gpt-5.4 = +11.2ppgpt-5.5 = +31.0ppOpus = +9.4pp
```

This is not one homogeneous “LLM judge bias.” It is model-specific and pair-specific.

Add CIs for every judge-specific position effect. Also report a per-cell four-way decomposition:

```
condition-stable winneropponent-stable winnerslot-A-stable winnerslot-B-stable winner
```

That table will make the bias finding much more convincing than mean slot-B deltas.

---

## A9. C3 vs C5_CONTRACT cross-provider strengthening should be reported as an artifact, not a robustness result

Phase 0 said:

```
C3 vs C5_CONTRACT strengthens under cross-provider judging:CI [0.238, 0.446] favoring C5_CONTRACT
```

Phase 1 explains it:

```
gpt-5.4 was the cross-provider judge for Opus-authored cellsgpt-5.4 has essentially no position biasgpt-5.5 and Opus have large slot-B bias
```

So the cross-provider result is not evidence that C5_CONTRACT beats C3. It is an example of why provider stratification without position control can mislead.

Recommended report language:

> The apparent cross-provider strengthening of C5_CONTRACT over C3 was not stable under AB/BA correction and appears to be explained by judge-specific position-bias structure. We therefore do not treat the cross-provider Phase 0 result as evidence of C5_CONTRACT superiority.

---

## A10. C4 > C5 strengthening under AB/BA does not automatically imply an analyzer bug

You asked whether the C4 > C5 AB/BA strengthening contradicts the Phase 0 length-match result.

Not necessarily. These are different estimands.

Length matching can change the scenario/persona/author composition. AB/BA correction changes position balance. A length-matched subset can lose power or select unusual cells even if the full position-corrected contrast is real.

But because the result is surprising, run this before writing:

```
For C4 vs C5, compute AB/BA-controlled win rate:1. full set2. same length-matched subset used in Phase 03. non-length-matched complement4. regression/mixed model with length difference as covariate5. scenario-family and author strata inside length buckets
```

Report the full AB/BA result as primary. Report the length-match result as a mechanism caveat, not as a competing headline.

If the full AB/BA result survives but the length-matched subset does not, the right conclusion is:

> C4 beats C5 overall in the tested distribution, but we cannot attribute that advantage cleanly to structure independent of length/composition.

---

## A11. Missingness is still under-addressed

You report:

```
Only 67.5% of outputs scored by all 3 judgescomplete-case = 1,134 / 1,680
```

That is not automatically fatal, but it is too large to leave as a note.

Before report writing, add:

```
missingness by conditionmissingness by authormissingness by judgemissingness by personamissingness by scenario familymissingness by paircomplete-case vs all-available estimatesworst-case sensitivity bounds
```

If missingness is condition-correlated, judge-correlated, or scenario-family-correlated, it can move marginal results.

The C5_CONTRACT > C5 result likely survives. C4 > C4_shuffled might not.

---

## A12. Scalar-pairwise contradiction was addressed for C5_CONTRACT, but not fully generalized

You correctly found:

```
C5_CONTRACT > C3:pairwise originally favored C5_CONTRACTscalar Δ_total = -0.053C5_CONTRACT > C4:pairwise originally favored C5_CONTRACTscalar Δ_total = -0.231C5_CONTRACT > C5:pairwise and scalar agreescalar Δ_total = +3.057
```

But before the curated report, every Tier 1 claim needs the same scalar-pairwise alignment table.

Add scalar deltas for:

```
C4 vs C1_paddedC4 vs C5C5_CONTRACT vs C5C4 vs C4_shuffledC4 vs C0
```

If any Tier 1 pair has pairwise positive but scalar negative, it should be downgraded or explicitly discussed.

---

## A13. TF-IDF F1 = 0.000 does not prove “cannot be recognition artifact”

You wrote:

> C5 vs C5_CONTRACT cannot be recognition artifact: TF-IDF classifier has F1=0.000 for both.

That is too strong.

A weak lexical classifier failing does not rule out:

- semantic recognizability,

- stylistic recognizability,

- length/structure recognizability,

- judge sensitivity to contract-like output features,

- non-linear feature recognition.

Also, F1 = 0.000 for both classes is suspicious enough that the report should show:

```
train/test splitclass balancebaseline classifierconfusion matrixaccuracymacro F1calibrationtop features
```

Better wording:

> We did not find evidence that a simple TF-IDF classifier could distinguish C5 from C5_CONTRACT outputs. This does not rule out semantic or stylistic recognizability.

---

## A14. Red-flag predictiveness is useful, but do not overclaim it as external validation

You report:

```
P(loser more flagged | asymmetric) = 0.65–0.88 across all 10 pairsall CIs exclude 0.5
```

This is a good internal consistency diagnostic. But if the same judge or same judging pipeline generates both the red flags and the preference, it is not independent validation.

Use it as:

> Pairwise loser decisions were directionally consistent with judge red-flag annotations.

Not:

> Red flags validate the pairwise preferences.

---

## A15. Tier 2 “collapse” means “no detected pairwise preference,” not equivalence

For:

```
C5_CONTRACT vs C3: 49.9% [44.3, 55.7]C5_CONTRACT vs C4: 51.8% [46.0, 57.5]
```

Do not call these equivalent unless you define an equivalence margin and run equivalence tests.

Correct wording:

> We do not detect a reliable pairwise preference between C5_CONTRACT and C3/C4 after AB/BA correction. The CIs still allow small effects in either direction.

Also mention scalar direction:

> Scalar scores do not support a C5_CONTRACT advantage over C3 or C4.

That is stronger and more honest than “tie.”

---

# (B) Quick fixes before v0.2 report writing

## B1. Tables to add to the curated report

### 1. Single source-of-truth verdict table

For every pair:

```
pairconditionsn originaln swappedjudges includedauthors includedorig condition-A winswap condition-A winAB/BA-controlled condition winnaive CIcluster-robust CIscalar Δ_totalscalar sign agreementfinal verdictallowed claimforbidden claim
```

This table should replace the current split between “Final AB/BA results” and “Final tier assignment,” because those currently conflict.

### 2. AB/BA judge-stratified table

For every pair × judge:

```
orig win rateswap win ratecontrolled condition effectslot-B effectslot-B CIAB/BA agreement raten cells
```

Do not average judge bias until the per-judge estimates are visible.

### 3. Per-cell AB/BA consistency table

For each pair:

```
condition X wins both orientationscondition Y wins both orientationsslot A wins both orientationsslot B wins both orientationsorientation-inconsistent / stochastic
```

This is the clearest way to show whether the pair is quality-driven, position-driven, or noisy.

### 4. Cluster-robust CI table

For Tier 1 and Tier 2 pairs:

```
naive CIpaired-cell bootstrap CIscenario-cluster CIpersona-cluster CIscenario-family-cluster CIauthor-stratified CIjudge-stratified meta-analytic CI
```

If the conclusion changes across rows, the report should say so.

### 5. Heterogeneity forest table

For each Tier 1 pair:

```
by authorby judgeby personaby scenario familyby same-provider vs cross-providerby length bucketby complete-case vs incomplete-case
```

The C3/C5_CONTRACT collapse was hiding in subgroups. Do not assume Tier 1 pairs are clean until this table exists.

### 6. Scalar-pairwise alignment table

For every headline pair:

```
pairwise controlled win ratescalar Δ_totalscalar Δ by dimensionsign agreementred-flag agreement
```

C5_CONTRACT > C5 should look strong here. C5_CONTRACT > C3/C4 should not.

### 7. Missingness table

Show:

```
output-level completenessjudge-level completenesscondition-level completenesspair-level completenesscomplete-case estimateall-available estimateworst-case sensitivity estimate
```

### 8. Length/salience table

For each pair:

```
mean chars by conditionmedian chars by conditionlength differencewin rate by length bucketAB/BA-controlled win rate inside similar-length bucketAB/BA-controlled win rate outside similar-length bucket
```

This is mandatory for C4 vs C5 and C5_CONTRACT vs C5.

### 9. Claim ledger

Add a table with three columns:

```
ClaimStatus after Phase 0/1Permitted wording
```

Example:

```
C5_CONTRACT > C3StruckNo detected pairwise preference after AB/BA; scalar does not favor C5_CONTRACT.C5_CONTRACT > C5SurvivesThe C5_CONTRACT package improves over C5 alone; mechanism not isolated.LLM judges have slot-B biasNarrowedGPT-5.5 and Opus show large slot-B preference in this pairwise setup; GPT-5.4 does not.
```

---

## B2. Robustness checks on AB/BA itself

Run these before writing.

### 1. Same-orientation repeatability sentinel

Rejudge a random subset in the original orientation.

Report:

```
original AB vs same-phase AB agreementsame-phase AB vs same-phase BA shift
```

This separates true position bias from phase/stochastic drift.

### 2. Paired-cell bootstrap

Do not bootstrap individual judgment records. Bootstrap the underlying paired cells.

Unit should be something like:

```
persona × scenario × author × pair
```

Then keep all judge observations attached to that cell.

### 3. Judge-stratified AB/BA

For each judge, estimate condition effect and slot effect separately.

Averaging GPT-5.4, GPT-5.5, and Opus hides the most important methodological finding.

### 4. Mixed-effects pairwise model

Fit a model equivalent to:

```
winner ~ condition + slot + condition:judge + slot:judge       + author + scenario_family + persona       + random intercepts for scenario and cell
```

You do not need to sell this as the primary estimator, but it should match the simpler AB/BA averages directionally.

### 5. Position-bias CIs

Every slot-B effect needs uncertainty.

The current table gives point estimates:

```
mean slot-B advantage ≈ 14.7–16.9pp
```

But without CIs, the methodological claim is under-supported.

### 6. Orientation-stability decomposition

Classify every paired AB/BA cell as:

```
condition-stableopponent-stableslot-B-stableslot-A-stableunstable
```

This should become a centerpiece figure.

### 7. Leave-one-stratum-out

For each Tier 1 pair:

```
leave one judge outleave one author outleave one persona outleave one scenario family out
```

A Tier 1 claim should not depend on one persona, one author, or one judge.

### 8. Length-intersection audit for C4 vs C5

Run:

```
full AB/BA C4>C5length-matched AB/BA C4>C5non-length-matched AB/BA C4>C5length-adjusted mixed model
```

This resolves the apparent contradiction with Phase 0.

### 9. Complete-case sensitivity

For every pair:

```
all available judgmentscomplete-case onlymissing-as-favorable-to-Amissing-as-favorable-to-Binverse-probability weighted estimate
```

This is especially important for marginal effects.

---

## B3. Sanity-check experiments runnable in <1 day

Priority order:

### 1. Same-orientation rejudge sample

This is the most important quick experiment.

Purpose:

```
separate position bias from model/pipeline drift
```

Sample:

```
small random subset across all six AB/BA pairsall three judges where feasible
```

### 2. Add Opus judging for Tier B headline pairs

Especially:

```
C4 vs C5C4 vs C4_shuffledC1_padded vs C4
```

C4 vs C5 cannot be fully Tier 1 while Opus judge coverage is zero.

### 3. AB/BA-test C0 vs C4 on a smaller sample

You do not need full coverage. The effect is huge. A targeted swap sample can validate that C0 domination is not just slot-B inflation.

### 4. Recompute C4 vs C5 on the exact Phase 0 length-matched subset

This is no new generation, just analysis if the swapped judgments exist for those cells.

### 5. Paraphrased pairwise judging prompt on a small Tier 1/Tier 2 sample

Use a rubric paraphrase and changed ordering language.

Include:

```
C5_CONTRACT vs C5C4 vs C5C4 vs C4_shuffledC3 vs C5_CONTRACTC4 vs C5_CONTRACT
```

If the same pattern holds, the report is stronger.

### 6. Forced-choice versus “no meaningful difference” judge prompt

The collapsed C5_CONTRACT vs C3/C4 pairs may be forced-choice noise. Add a tie option on a small sample.

Report:

```
A winsB winsno meaningful differencejudge uncertainty
```

### 7. Human spot-check calibration

Small but useful:

```
50–100 pairwise comparisonsbalanced across strongest, marginal, and collapsed pairsblind AB/BA
```

Do not try to solve human validation in v0.2. Use it only as a sanity check.

### 8. Mini C_GENERIC_CONTRACT ablation

This is not required to publish C5_CONTRACT > C5, but it is required for mechanism.

Minimal version:

```
C5C5 + generic contractC5 + actual behavioral contract
```

Use a targeted subset of hard scenarios.

### 9. Length-pad control

For mechanism:

```
C5C5_LENGTH_PADC5_GENERIC_CONTRACTC5_CONTRACT
```

This distinguishes length/salience from contract content.

---

## B4. New Phase 0-style audits you did not run

These are no-new-output or low-new-judgment audits.

1. **Internal consistency audit**

Check all pair counts, complement transforms, CI transforms, and final-tier values.

2. **Same-orientation repeatability audit**

Required because Phase 1 appears to be swap-only rejudging.

3. **Cluster-robust CI audit**

Recompute intervals under clustered dependence.

4. **Scalar-pairwise alignment for all Tier 1 pairs**

Not only C5_CONTRACT pairs.

5. **Tier 1 heterogeneity audit**

Persona, scenario family, author, judge, same-provider/cross-provider, length bucket.

6. **Missingness mechanism audit**

Missing completely at random is not a safe assumption.

7. **Semantic condition recognizability audit**

TF-IDF is insufficient. Use stronger classifiers or judge-blind recognizability prompts. Phrase results cautiously.

8. **Model self-preference/style-preference audit**

Check whether judges favor outputs authored by related model families or stylistic signatures.

9. **Red-flag circularity audit**

Separate red flags produced by the deciding judge from red flags produced by independent judges.

10. **Multiple-comparison sensitivity**

Especially for C4 > C4_shuffled. The report can be exploratory, but should not use marginal p-value language across many tested pairs.

---

# (C) v0.3 questions: what round 1 missed

Round 1 correctly pushed toward:

```
C_GENERIC_CONTRACTC4_WRONG_PROFILEC5_NONPUBLICparaphrased rubrichuman calibrationreal-user shadow validation
```

Those are still right. But round 2 exposes additional v0.3 questions.

## C1. What is the minimum effective contract?

C4 and C5_CONTRACT are too bundled.

v0.3 should separate:

```
generic contractbehavioral contractshort behavioral contractfull behavioral contractcontract without profile detailsprofile details without contract
```

Question:

> How much of the benefit comes from contract structure versus contract content?

---

## C2. Is the effect caused by instruction hierarchy, salience, or actual user modeling?

C5_CONTRACT may win over C5 because it makes some information more salient, not because the model genuinely uses a better user profile.

Add conditions like:

```
same facts, different hierarchysame facts, bullet salience onlysame facts, prose onlysame facts, contract language removedsame facts, generic “be adaptive” instruction
```

---

## C3. Does contract use create overpersonalization?

The current eval rewards adaptation. It may under-measure cases where adaptation becomes intrusive, presumptive, or stereotyping.

Add scenario labels for:

```
user did not ask for personalizationprofile relevance ambiguoussensitive trait possibly relevantsensitive trait not relevantprofile use would feel creepy
```

Measure:

```
helpfulnessoverreachprivacy respectuser agency
```

---

## C4. When should the assistant ask instead of using profile context?

The current framing assumes profile context should change behavior. But sometimes the correct behavior is:

```
ask a clarifying questionavoid using latent profileexplicitly check preferenceignore stale context
```

Add a dimension:

> Did the assistant use profile context only when warranted?

---

## C5. What happens with uncertain, stale, or conflicting profiles?

Round 1 had wrong-profile. v0.3 should also include:

```
low-confidence profilestale profileconflicting profile fieldsprofile updated by recent user messageprofile contradicted by current requestprofile from unreliable source
```

This is closer to real memory systems.

---

## C6. Does profile context improve hard cases or just make easy cases warmer?

Scenario-family reversals already matter:

```
epistemic_uncertaintyshameSlalom Altar persona
```

v0.3 should stratify by expected mechanism:

```
emotional regulationplanningidentity-sensitive adviceepistemic uncertaintyconflictsafety boundarymotivationpreference fulfillment
```

Do not treat “personalization” as one homogeneous outcome.

---

## C7. Are pairwise and scalar judging measuring different latent constructs?

The scalar-pairwise contradiction was the biggest analytical surprise. v0.3 needs to model it directly.

Questions:

```
Do pairwise judges reward fluency, warmth, and polish?Do scalar judges penalize overreach more?Do scalar dimensions capture harms pairwise judges miss?Which metric better matches human preference?
```

Do not assume pairwise is the gold standard.

---

## C8. Should pairwise judging include a tie / no-difference option?

The C3/C5_CONTRACT and C4/C5_CONTRACT collapses suggest forced-choice pairwise may manufacture apparent differences.

Add:

```
A betterB betterno meaningful differenceboth badjudge uncertain
```

This will reduce fake precision.

---

## C9. How large is judge-order bias across tasks, not just this task?

The slot-B finding is now one of the most important results. v0.3 should study it deliberately.

Vary:

```
A/B labelsleft/right layoutfirst/second wordinganswer lengthanswer quality gapjudge modelrubric wordingtie option
```

Question:

> Is slot-B bias a recency effect, an interface effect, a rubric effect, or a judge-model-specific artifact?

---

## C10. Are judges rewarding visible “contract-shaped” output artifacts?

Even if TF-IDF fails, judges might reward outputs that look more organized, cautious, or emotionally structured.

Measure output features:

```
lengthnumber of bulletsnumber of caveatsempathy markersquestions askedexplicit personalizationsafety disclaimersspecificityaction steps
```

Then model whether condition effects survive feature adjustment.

---

## C11. Does the contract improve outcomes or merely style?

A response can sound more attuned while not being more useful.

Add outcome dimensions:

```
task successspecificityactionabilityfactual accuracyemotional fitnon-overreachsafetycalibrationuser autonomy
```

Separate “pleasant” from “better.”

---

## C12. What is the token-cost efficiency frontier?

C5_CONTRACT is long:

```
C5_CONTRACT ≈ 7,433 charsC4 ≈ 3,689 charsC3 ≈ 2,518 chars
```

Since C5_CONTRACT only ties C3/C4 after AB/BA, cost matters.

v0.3 should ask:

> Which condition gives the best quality gain per token?

Include compressed variants:

```
C4_shortC5_CONTRACT_shortC5_CONTRACT_summaryC5_CONTRACT_top-k facts
```

---

## C13. Does profile context increase safety risk in sensitive domains?

Add adversarial or high-risk cases:

```
mental healthmedicallegalfinancialself-worth/shamefamily conflictworkplace conflictidentity-sensitive advice
```

Measure not only helpfulness but also:

```
unsafe reassurancefalse certaintydependency encouragementprivacy leakageemotional manipulationoverconfident personalization
```

---

## C14. Does the benefit survive multi-turn interaction?

Single-turn outputs may not reflect real profile use.

v0.3 should include:

```
profile introduced in turn 1user contradicts profile in turn 2assistant must update in turn 3assistant must remember but not overuse in turn 4
```

Profile systems are longitudinal. Single-turn tests overestimate clean context use.

---

## C15. Does author model style interact with judge preference?

You already saw judge-specific effects. Next check author/judge style interactions.

Questions:

```
Do OpenAI judges prefer OpenAI-authored outputs?Do Anthropic judges prefer Anthropic-authored outputs?Do judges prefer outputs with their own rhetorical style?Does AB/BA correction remove or reveal this?
```

This is separate from provider-family cross-judging.

---

## C16. Can the eval detect harmful personalization?

Current pairs mostly ask, “Which is better?” v0.3 needs explicit negative controls where profile use should hurt.

Examples:

```
profile irrelevant to taskprofile sensitive but not consentedprofile suggests a preference but current request contradicts itprofile would bias advice unfairlyprofile would induce stereotyping
```

Success requires not using the profile.

---

## C17. Are scenario authors accidentally optimizing for their own model’s strengths?

Scenarios were authored by GPT-5.4, GPT-5.5-xhigh, and Opus 4.7. That is good diversity, but synthetic scenarios can still encode model-specific assumptions about what “good personalization” looks like.

Add:

```
human-authored scenariosadversarially authored scenariosscenario paraphrasesscenario difficulty ratingsheld-out scenario families
```

---

## C18. What is the right primary endpoint?

v0.2 now has three partially conflicting signals:

```
pairwise preferencescalar rubricred flags
```

v0.3 should define the primary endpoint before running.

Possible hierarchy:

```
1. human/user preference or expert-calibrated pairwise2. LLM pairwise with AB/BA and tie option3. scalar dimension scores4. red flags as diagnostics
```

Without a hierarchy, future contradictions will keep producing interpretive ambiguity.

---

# Recommended priority order

## Before v0.2 writing

Do these first:

1. Fix AB/BA table/count/final-summary inconsistencies.

2. Run same-orientation rejudge sentinel.

3. Recompute paired/cluster-robust CIs.

4. Add missingness sensitivity.

5. Add scalar-pairwise alignment for all Tier 1 pairs.

6. Reframe C4 > C5 as OpenAI-judge-only unless Opus is added.

7. Downgrade C4 > C4_shuffled to modest/suggestive unless robust CIs confirm.

8. Narrow C5_CONTRACT > C5 mechanism claim.

9. Reframe cross-provider C3/C5_CONTRACT as an artifact lesson.

## Best final Tier framing

I would use something like this:

### Strong / publishable

```
C5_CONTRACT > C5
```

With mechanism caveat.

### Publishable with caveat

```
C4 > C5
```

But currently OpenAI-judge-only.

```
C4 > C1_padded
```

But only after resolving the estimate inconsistency.

### Large but not AB/BA-controlled

```
C4 > C0
```

Likely real, but do not present exact controlled magnitude.

### Suggestive / marginal

```
C4 > C4_shuffled
```

Needs cluster/judge robustness.

### Struck

```
C5_CONTRACT > C3C5_CONTRACT > C4PAE empirically resolvedsource packets add value when subordinated to contractsgeneric LLM judges have universal slot-B bias
```

The report will be much stronger if it says plainly: the most interesting result of v0.2 is not that C5_CONTRACT won. It is that **the original C5_CONTRACT superiority story mostly collapsed under AB/BA, while C5_CONTRACT > C5 survived and the judge-position artifact became a first-class methodological finding.**