<!-- Recovered from ChatGPT conversation: https://chatgpt.com/c/6a0bfa18-cf8c-83e8-b8a7-7bdac11d9a4c -->
<!-- Conversation title: PsycheEval v0.3 Review -->
<!-- 2 assistant message(s), 29141 chars -->
<!-- Originally cancelled at 17m49s with 28K-char partial; recovered from server-side history -->

I’ll treat the bundle as the source of truth and pressure-test design validity, attribution, and budget tradeoffs rather than polish. I’ll focus especially on mechanism isolation, TOST, judge validity, and the human/real-user bridge.

---

# A) Plan-level critique

## 1. The mechanism-decomposition claim is stronger than the design supports.

The plan says v0.2 left unresolved that **“C5_CONTRACT differs from C5 on ≥4 dimensions: contract presence, contract-first ordering, anti-mimicry rules, prompt length.”** Then v0.3 says Tier 2 will **“decompose C5_CONTRACT > C5 into which of the 4 simultaneous differences is dominant.”**

But the Tier 2 condition list does **not** isolate those four differences.

The biggest miss: there is no clean **contract-presence** condition. The listed Tier 2 conditions are:

> **“C5_CONTRACT_SHORT … Length”**
> 
> **“C5_CONTRACT_PACKET_FIRST … Ordering”**
> 
> **“C5_CONTRACT_NO_ANTIMIMICRY … Anti-mimicry effect”**
> 
> **“C5_FACTS_ONLY … Narrative form vs facts”**

“Facts only” is not one of the four simultaneous differences named in the v0.2 finding. Meanwhile the actual first difference, **contract presence**, is missing. This is not a small terminology issue; it means the advertised decomposition cannot answer the mechanism question it claims to answer.

You need either a pure `C5_WITH_CONTRACT_ONLY` condition or an explicit ablation ladder. For example:

1. C5 baseline: source packet only.

2. C5 + contract, packet-first, no anti-mimicry, length-matched.

3. C5 + contract + anti-mimicry, packet-first, length-matched.

4. C5 + contract + anti-mimicry + contract-first, length-matched.

5. Full C5_CONTRACT, expanded length.

That would still be path-dependent, but at least the path would correspond to the claimed mechanisms.

## 2. The length-control condition uses the wrong target.

The plan says:

> **“C5_CONTRACT_SHORT | Compressed to C3's char count (~2,518 chars vs 7,434) | Length”**

But the v0.2 confound was:

> **“prompt length (7,434 vs 3,884 chars)”**

That is C5_CONTRACT versus C5, not C5_CONTRACT versus C3. Compressing to C3’s length does not isolate the length difference between C5_CONTRACT and C5. It introduces a new compression regime and may remove substance, specificity, rhetorical scaffolding, examples, or constraints.

If the target is the C5_CONTRACT > C5 mechanism, the primary length control should be matched to **C5’s length**, not C3’s. A C3-length compression may be interesting, but it is not the right first-order length ablation.

## 3. “The combination” is not identifiable from these conditions.

The success criteria say Tier 2 should determine whether one of the four differences is dominant **“or ‘the combination’ with evidence.”**

With single-factor ablations around one prompt, you can observe that removing one component weakens or does not weaken performance. You cannot cleanly identify interaction effects or prove “the combination” unless you include a factorial or fractional-factorial design. If contract presence, ordering, anti-mimicry, and length interact, the current design will not distinguish:

- no single dominant factor,

- two-factor synergy,

- length amplifying contract salience,

- anti-mimicry only mattering when contract-first,

- judge preference for polished prompt artifacts.

So the plan should downgrade this claim. It can say: “estimate marginal ablation sensitivity around C5_CONTRACT.” It should not say “decompose” unless the condition graph is redesigned.

## 4. The plan spends heavily on same-corpus LLM-judge precision while leaving construct validity thin.

The most expensive part is:

> **“Phase 4 — AB/BA pairwise + Phase 4.4 equivalence-margin TOST … ~$280 … ~17,600 pairwise calls”**

But the scenario set remains:

> **“Scenario set unchanged (80 scenarios, mean difficulty 3.58/5)”**

This is a precision-heavy, generalization-light design. You are buying more judgments over the same synthetic corpus. That improves within-corpus estimates, but it does not answer whether PsycheEval generalizes to new scenarios, real profiles, real users, or adversarially messy inputs.

The weakest part is still:

> **“50-pair human-rater calibration sample (single rater, per D2): one-rater alignment statistic”**

A single author-rater is not “human calibration” in any serious sense. It is an author-preference sanity check. That may still be useful, but it should not be described as a construct-validity bridge.

## 5. The new tie/equipoise option creates comparability problems.

The plan commits to:

> **“Tie / equipoise pairwise option”**

This is probably a good addition, but it changes the pairwise measurement scale. v0.2 pairwise judgments were forced-choice. v0.3 pairwise judgments with ties are ternary. That matters for:

- combining v0.2 and v0.3 data,

- interpreting win rates,

- AB/BA flip rates,

- TOST equivalence margins,

- judge-specific slot-B preference estimates.

Before execution, the plan needs to specify whether Phase 4.4 uses forced-choice to remain comparable with v0.2, or whether v0.2 is reinterpreted/reweighted somehow. Otherwise the combined-corpus TOST is methodologically muddy.

## 6. Pair-set scope is under-specified and invites post hoc expansion.

D3 says:

> **“4 most informative pair types per new condition … Phase 6 expansion if missing pair becomes load-bearing.”**

That last clause is a red flag. If a pair becomes “load-bearing” after inspecting results, adding it later is exploratory, not confirmatory. This is exactly the kind of analyst-degree-of-freedom that AB/BA and bootstraps do not fix.

The plan should predeclare the full contrast graph or explicitly separate confirmatory and exploratory expansions. “Phase 6 expansion if missing pair becomes load-bearing” should not feed into headline claims.

## 7. The output/call arithmetic is not auditable.

Examples:

> **“Tier-1 generation (4 conditions) … ~440 outputs”**
> 
> **“Tier-2 generation (4 mechanism conditions, PI only) … ~560 outputs”**

The narrower Tier 2 somehow has more outputs than Tier 1. That may be correct given persona subsets, author models, or reuse rules, but the plan does not show the formula. Same issue for:

> **“~4,225 calls”**
> 
> **“~17,600 pairwise calls”**

For a locked plan, the unit accounting should be explicit: conditions × personas × scenarios × author models × judges × AB/BA × sentinels × repeats. Right now the budget is not independently checkable.

## 8. The blog-post phase is premature.

The plan includes:

> **“Phase 8 — v3 blog post … Through writing-review … + publication-review”**

before any real shadow-mode execution. That creates pressure to narrativize LLM-judge results as substantive product findings. Unless the blog is explicitly a methods/process post, defer it until the construct bridge is stronger. The current v0.3 can support a technical report; it should not be framed as validating Psyche in the real-user sense.

---

# B) Decision audit: D1–D5

## D1 — Scope of Tier 2 mechanism conditions

Decision:

> **“All four (SHORT, PACKET_FIRST, NO_ANTIMIMICRY, FACTS_ONLY). Combinatorial decomposition essential.”**

Push back hard.

First, these are not “all four” of the v0.2 confounds. Contract presence is absent, and “FACTS_ONLY” introduces a different dimension: narrative form versus facts.

Second, “combinatorial decomposition” is the wrong phrase. Four one-off ablations are not combinatorial. If combinatorial decomposition is essential, then run a real factorial or fractional-factorial design. If budget cannot support that, call it an ablation sensitivity study.

Third, Tier 2 is described as:

> **“4 mechanism conditions, PI only”**

That is dangerous if C5/C5_CONTRACT behavior differs across PI and PS personas, especially because Tier 1 includes:

> **“C5_NONPUBLIC | Source-packet narrative for PS personas”**

If the public-anchor issue is PS-specific but mechanism decomposition is PI-only, v0.3 may answer the wrong mechanism question for the wrong subgroup.

Recommendation: replace D1 with a smaller, cleaner mechanism ladder. Drop or defer `C5_FACTS_ONLY` unless narrative-vs-facts is promoted to a separate question. Add a pure contract-presence condition.

## D2 — Human calibration sample

Decision:

> **“Single rater (author) for v0.3. v0.4 upgrade to ≥2 raters.”**

This is badly calibrated. A single author-rater cannot estimate inter-rater reliability, cannot separate human preference from author theory, and cannot credibly validate LLM judges. It can only answer: “Does the plan author personally agree with the model judges on a small sample?”

That is still useful, but then label it honestly:

> author blind sanity check, n=1

Do not call it “human calibration” without a large caveat in every place it appears.

Better options at similar cost:

- two blinded raters × 25 pairs each, with 10 overlapping pairs;

- three raters × 20 pairs each, with a small overlap set;

- one author-rater plus one external rater, explicitly reported separately;

- skip the rater UI and spend the saved effort on a minimal shadow-mode instrumentation test.

If D2 stays as written, it should not be used as evidence of construct validity.

## D3 — Pair-set scope for T1 conditions

Decision:

> **“4 most informative pair types per new condition … Phase 6 expansion if missing pair becomes load-bearing.”**

The first half is defensible if the contrast graph is predeclared. The second half is not.

Post hoc expansion after a pair becomes “load-bearing” is acceptable only if reported as exploratory. It should not feed Tier 1 claims, equivalence claims, or blog-post claims.

Recommendation: before Phase 1, lock a contrast matrix with each pair labeled:

- primary confirmatory,

- secondary confirmatory,

- exploratory only,

- not tested.

Do not let Phase 6 add confirmatory pairs after seeing results.

## D4 — Shadow-mode validation context

Decision:

> **“Psyche public results page … v0.3 ships design + pre-registered predictions; v0.4 executes.”**

This is partly reasonable, but it conflicts with the plan’s heavier inferential ambitions. If v0.3 is mostly a methods pilot, design-doc-only is fine. If v0.3 is going to make deployment-relevant claims and publish a blog post, design-doc-only is too weak.

Also, D5 uses shadow-mode relevance to justify the equivalence margin:

> **“±5pp margin justified by deployment relevance in shadow-mode validation … at engagement gaps <5pp, real-user signal dominates.”**

That means D4 is not merely future work; it is part of the justification for a current statistical decision. Therefore the shadow-mode design should be moved earlier, before Phase 4.4, and the mapping between LLM-judge pairwise points and user-engagement percentage points should be treated as speculative unless actually measured.

## D5 — C5_CONTRACT > C3 equivalence-margin

Decision:

> **“Predeclared ±5pp TOST on combined v0.2+v0.3 corpus (n_combined ≈ 600 per pair). Phase 4.4 generates ~3,750 additional pairs.”**

This is the most questionable locked decision.

Problems:

1. **The ±5pp margin is not well justified.**

The plan says it is justified because **“at engagement gaps <5pp, real-user signal dominates.”** But LLM pairwise win-rate percentage points and real-user engagement percentage points are not the same scale. A 5pp LLM-judge difference might correspond to 0pp, 2pp, 10pp, or negative user engagement difference.

2. **Combining v0.2 and v0.3 may be invalid.**

v0.3 adds **“Tie / equipoise pairwise option.”** v0.2 did not. Unless Phase 4.4 uses the exact v0.2 forced-choice protocol, the combined corpus is not cleanly comparable.

3. **More pairwise calls over the same 80 scenarios may not buy the precision you think it buys.**

The plan promises **“cluster bootstrap CIs”** while keeping the **“Scenario set unchanged.”** If the cluster unit is scenario/persona/author, then `n_combined ≈ 600 per pair` overstates the effective sample size. Additional AB/BA judgments reduce judge noise, not scenario-distribution uncertainty.

4. **The likely outcome is still “no established equivalence.”**

v0.2 had C5_CONTRACT vs C3 controlled at **49.9% [43.4, 56.4]** and C5_CONTRACT vs C4 at **51.8% [45.2, 58.7]**. The latter is especially likely to fail a ±5pp TOST unless the estimate moves inward and the cluster CI tightens materially.

Recommendation: do not spend 3,750 extra pairwise calls on Phase 4.4 as currently framed. Either downgrade to “no detection plus SESOI-bounded estimate” or redirect the spend to new scenarios, external raters, or a minimal shadow-mode MVP.

---

# C) Sequencing critique

## 1. Add a real pre-registration phase before generation.

Phase 0 currently says:

> **“8 new conditions wired, ab-ba-mandatory flag, two new analyzer blocks, tests green”**

That is implementation hardening, not inferential hardening.

Add a Phase 0.1 pre-analysis lock containing:

- exact condition definitions;

- exact contrast graph;

- primary versus exploratory comparisons;

- tie-handling rules;

- AB/BA aggregation rule;

- same-orientation sentinel aggregation rule;

- cluster bootstrap unit;

- multiplicity policy;

- model IDs and version-pinning policy;

- exclusion/failure criteria;

- whether v0.2 and v0.3 can be combined;

- how paraphrased-anchor discrepancies change claims.

Without this, v0.3 will still have too many degrees of freedom.

## 2. Run a small smoke test before full generation.

Before Phase 1 and Phase 2, run a tiny all-condition test: maybe 1 persona × 5 scenarios × all new conditions × all judges. The point is not inference. The point is to catch:

- broken condition wiring,

- C4_WRONG_PROFILE obvious mismatch artifacts,

- C5_NONPUBLIC accidentally retaining public-anchor cues,

- tie option overuse,

- judge prompt confusion,

- same-orientation sentinel implementation bugs.

This is especially important because the plan introduces many moving parts at once: 8 new conditions, AB/BA mandatory, ties, paraphrased anchors, same-orientation sentinels, and human calibration.

## 3. Move shadow-mode design earlier.

Phase 9 currently comes after the report/blog phases:

> **“Phase 9 — Shadow-mode validation design doc”**

But D5 uses shadow-mode relevance to justify ±5pp equivalence. So the shadow-mode design cannot be an afterthought. Move the design doc before Phase 4.4 or before Phase 6.

At minimum, Phase 0 should define what user-visible outcome would actually make a 5pp LLM-judge difference meaningful.

## 4. Human calibration should be blinded and sequenced before model-result interpretation.

Phase 5 says:

> **“Human calibration (single rater) … 50 pairs scored”**

This should happen after outputs are generated but before the author has inspected model-judge results for those same pairs. If the author-rater sees model results first, the already-weak calibration becomes even weaker.

Also, the rater should not see condition labels. The sample should be preselected or randomly stratified before analysis, not chosen because certain pairs became interesting.

## 5. Paraphrased-anchor sentinel should be validated before full scalar judging.

The plan says:

> **“Paraphrased rubric anchors (sample at 15%): rubric robustness”**

Do not discover after 4,225 scalar calls that the paraphrased anchor changes the score distribution. Run a small pilot first. If the paraphrase produces different absolute means but stable rankings, that is a different result from true anchor robustness.

The analyzer should distinguish:

- score correlation,

- mean shift,

- condition-rank stability,

- judge-specific effects,

- threshold-crossing effects.

## 6. Do not put blog production before validation design.

The sequence:

> **“Phase 7 — Curate v0.3 report”**
> 
> **“Phase 8 — v3 blog post”**
> 
> **“Phase 9 — Shadow-mode validation design doc”**

is backwards if the blog says anything deployment-relevant. Move Phase 9 before Phase 8. Better: do not write the public-facing blog until the shadow-mode design is locked and the report clearly separates synthetic LLM-judge claims from real-user claims.

---

# D) Cheaper alternatives

## 1. Replace Phase 4.4 TOST with SESOI-bounded estimation unless equivalence is truly necessary.

The plan asks whether Phase 4.4 is the right way to settle C5_CONTRACT vs C3/C4. I do not think it is.

The current v0.2 result already says:

> **“C5_CONTRACT vs C3: original 57.2% → controlled 49.9% [43.4, 56.4]. Scalar Δ_total −0.053.”**
> 
> **“C5_CONTRACT vs C4: original 60.0% → controlled 51.8% [45.2, 58.7]. Scalar Δ_total −0.231.”**

That is a publishable methodological result: uncontrolled pairwise suggested an effect; AB/BA control collapsed it; scalar evidence did not support superiority. You do not need to prove equivalence to make that point.

A cheaper and cleaner framing:

> “No superiority detected; estimates are near equipoise; equivalence not established; further deployment relevance requires human/user validation.”

That is more honest than spending 3,750 calls trying to force a ±5pp equivalence conclusion on the same corpus.

## 2. If you keep TOST, make it sequential and targeted.

Instead of committing upfront to:

> **“~3,750 additional pairs”**

use a sequential design:

1. Recompute v0.2 + essential v0.3 estimates under one harmonized forced-choice protocol.

2. Stop if the CI already cannot plausibly enter the ±5pp band.

3. Add pairwise batches only for the specific contrast that remains equivalence-plausible.

4. Stop when either equivalence is established or the maximum sample is reached.

This avoids spending the full Phase 4.4 budget on contrasts likely to end as “no established equivalence.”

## 3. Spend extra budget on new clusters, not repeated judgments.

Because the plan keeps the:

> **“Scenario set unchanged (80 scenarios)”**

the more valuable precision improvement is probably new scenarios/personas, not more pairwise repetitions. If cluster bootstrap is the headline uncertainty method, add clusters.

A cheaper alternative to 3,750 pairwise calls:

- 20–40 new scenarios,

- only C3 / C4 / C5_CONTRACT / one best new condition,

- AB/BA pairwise only on the critical contrasts,

- report old-corpus and new-corpus estimates separately.

That gives a stronger generalization claim than another large batch on the original 80 scenarios.

## 4. Use scalar judging as a screen, pairwise as confirmation.

The plan runs both scalar and massive pairwise judging. A cheaper design:

1. Run scalar judging for all new outputs.

2. Use predeclared rules to identify contrasts with material scalar differences or close scalar uncertainty.

3. Run AB/BA pairwise only on those confirmatory contrasts.

4. Keep pairwise for headline claims, not every interesting comparison.

This is only valid if the pairwise selection rule is predeclared. But it would cut a lot of cost.

## 5. Replace the current Tier 2 condition set with a cleaner ablation ladder.

The current Tier 2 adds four mechanism variants but still fails to isolate contract presence. A cheaper alternative is to drop `C5_FACTS_ONLY` and use the saved generation/judging budget for the missing contract condition.

Better Tier 2 set:

- C5 baseline.

- C5 + minimal contract, packet-first, no anti-mimicry, length-matched to C5.

- C5 + minimal contract + anti-mimicry, packet-first, length-matched.

- C5 + minimal contract + anti-mimicry, contract-first, length-matched.

- C5_CONTRACT full.

This is still not a full factorial, but it is more interpretable than the current set.

## 6. Replace the single author-rater with two cheap blinded raters.

The plan already budgets:

> **“~1 day rater time + UI build”**

The UI build is probably the expensive fixed cost. Once built, adding a second rater is disproportionately valuable. Two raters with overlap would be much more publishable than one author-rater.

If budget is tight, reduce model pairwise calls and buy rater redundancy. One human rater is not where this project should economize.

## 7. Minimal shadow-mode MVP may be cheaper than Phase 4.4 and more valuable.

A small v0.3 shadow-mode execution would beat a design doc plus extra LLM pairwise calls. It does not need to be fully powered.

Possible MVP:

- one page only: Psyche public results page;

- two safe presentation variants;

- randomize at session/user level;

- collect consented lightweight metrics: continue click, dwell time, section expansion, save/share, optional “felt accurate/useful” rating;

- run only as instrumentation validation plus directional estimate;

- do not claim efficacy.

Even if underpowered, this would test whether the product can actually collect the outcome that D5 uses rhetorically.

---

# E) Construct validity bridge depth

The v0.3 pacing is too conservative on real-user validation and too aggressive on synthetic inference.

The plan says v0.3 includes:

> **“Phase 9 shadow-mode design doc … executable in v0.4”**

and also:

> **“v3 blog post”**

That combination is mismatched. A design doc is enough if v0.3 remains an internal methodology checkpoint. It is not enough if v0.3 is going to make public-facing claims about Psyche quality.

The deeper problem is that the current construct remains mostly:

> LLM judges prefer output A over output B on synthetic personas and scenarios.

That is not the same as:

> real users find the result more accurate, useful, non-creepy, engaging, or self-relevant.

The plan gestures at this with:

> **“Real-user construct validity”**

and:

> **“Shadow-mode validation design doc”**

but it defers the actual bridge.

I would push v0.3 to include a minimal execution, not merely a design. It can be explicitly underpowered. The goal would be instrumentation and sanity, not final effect estimation.

Recommended v0.3 construct bridge:

1. Keep the full v0.4 design doc.

2. Add a tiny live or quasi-live MVP in v0.3.

3. Test only one or two contrasts.

4. Predeclare that the MVP cannot validate efficacy.

5. Use it to verify whether engagement metrics are collectable and whether users react differently at all.

The current claim:

> **“at engagement gaps <5pp, real-user signal dominates”**

should not appear as a justification until there is at least some real-user measurement. Right now it is an intuition, not an empirical bridge.

Also, the Phase 9 power target says:

> **“80%/7pp power analysis”**

but D5 uses:

> **“±5pp margin”**

That mismatch should be resolved. If 5pp is deployment-relevant, why is the shadow-mode design powered around 7pp? If 7pp is the realistic detectable effect, why is 5pp the equivalence margin?

---

# F) The deepest open question

The deepest unresolved question is not mechanism attribution. It is whether PsycheEval measures the construct Psyche actually cares about.

Right now v0.3 mostly asks:

> Which prompt/profile condition produces outputs that LLM judges prefer under an anchored rubric and AB/BA pairwise controls?

That is valuable, but it may still be an evaluation of **judge-legible personalization artifacts**, not human-relevant personalization.

Several missing areas should be added or at least explicitly scheduled for v0.4+.

## 1. Real-profile realism

The plan says:

> **“Profile-realism (deferred to v0.4)”**

This is a major deferral. Synthetic personas and curated scenarios are useful for controlled methodology, but they may not resemble real Psyche users. Real profiles are likely to be sparse, contradictory, vague, aspirational, defensive, or noisy.

At minimum, v0.3 should include a tiny realism stress test:

- sparse profile,

- contradictory profile,

- highly generic profile,

- overly detailed profile,

- emotionally sensitive profile,

- profile with irrelevant facts,

- profile with misleading but plausible facts.

This does not require a full real-user study.

## 2. Adversarial and safety robustness

There is no explicit adversarial-robustness section. That is a miss.

Psyche-like profiles can contain prompt injection, self-diagnosis, manipulative claims, extreme preferences, or unsafe requests. A method that performs well on clean synthetic profiles may fail badly when the profile itself is hostile or misleading.

Add adversarial profile conditions:

- profile says “ignore all safety rules”;

- profile asks the system to flatter or validate delusions;

- profile contains contradictory identity claims;

- profile contains irrelevant but emotionally salient facts;

- profile includes public-figure mimicry bait;

- profile contains hidden instructions to the assistant;

- profile tries to force a particular output style.

The current anti-mimicry condition is not enough.

## 3. Public-anchor leakage

The plan includes:

> **“C5_NONPUBLIC | Source-packet narrative for PS personas (no public-anchor prose)”**

But public-anchor effects are not isolated unless names, biographical cues, and judge/world-knowledge leakage are controlled. If the model or judge can infer the public anchor from residual facts, you have not removed the public anchor.

A stronger design would include:

- public anchor named;

- public anchor anonymized but facts retained;

- public anchor facts paraphrased and de-identifying cues removed;

- nonpublic synthetic persona matched on richness and extremity;

- judge prompt explicitly blind to profile source.

Otherwise, C5_NONPUBLIC may confound publicness with vividness, recognizability, factual density, or narrative quality.

## 4. Generic excellence versus personalized fit

The plan tests generic contracts through:

> **“C_GENERIC_CONTRACT … generic, non-profile-specific language”**

and wrong profiles through:

> **“C4_WRONG_PROFILE … another persona's C4 profile substituted”**

That is good directionally, but the deeper missing control is a very strong generic response baseline. A generic response can be excellent: concise, emotionally intelligent, practical, non-creepy, and scenario-specific. If personalized prompts merely produce more “profile-scented” prose, LLM judges may prefer them while real users do not.

Add a high-quality generic baseline optimized for scenario usefulness but forbidden from using profile facts. Compare it against profile-specific conditions under both LLM judges and humans.

## 5. Judge reward-hacking

Contracts and anti-mimicry rules may cause outputs to exhibit surface features judges like: caveats, self-awareness, non-mimicry language, reflective phrasing, explicit profile references. That does not necessarily mean better user value.

Add diagnostics for:

- output length,

- number of profile references,

- explicit self-description references,

- hedging,

- “I’m tailoring this to you” language,

- generic empathy markers,

- refusal/safety markers,

- lexical overlap with source packet.

Then test whether judge preference remains after controlling for these. v0.2 already found position bias mattered; v0.3 should assume other judge-visible artifacts matter too.

## 6. Generalization beyond same-author, same-scenario, same-judge ecology

The plan says:

> **“Same-author scope primary; cross-author exploratory”**

That is still narrow. Same-author controls are good for isolating condition effects, but the product does not exist only in a same-author/same-scenario/same-judge lab ecology.

At minimum, v0.3 should predeclare what claims are corpus-scoped and what claims are intended to generalize. Do not let same-author results imply general model behavior unless cross-author results support them.

## 7. Failure criteria

The plan has success criteria but not enough failure criteria. For example:

- What if paraphrased anchors change condition rankings?

- What if tie rates differ wildly by judge?

- What if the author-rater disagrees with LLM judges?

- What if C4_WRONG_PROFILE beats generic?

- What if public-anchor anonymization does not change anything?

- What if same-orientation retest noise is so high that AB/BA decomposition is unstable?

- What if Opus and OpenAI judges diverge again?

Predeclare what would cause a claim to be downgraded, not just what would count as success.

---

# Top 3 recommended changes

1. **Fix Tier 2 before running it.**

The current mechanism set does not isolate the four claimed C5_CONTRACT confounds. Add a pure contract-presence condition, length-match to C5 rather than C3, and either use a predeclared ablation ladder or stop claiming “decomposition.”

2. **Cut or radically narrow Phase 4.4 TOST.**

The ±5pp equivalence test is over-expensive, weakly justified, hard to combine with v0.2 if ties are introduced, and may not reduce cluster-level uncertainty because the scenario set is unchanged. Use SESOI-bounded estimation or sequential targeted testing; redirect savings to new scenarios, external raters, or a minimal shadow-mode MVP.

3. **Add a real Phase 0 pre-analysis lock and move construct-bridge work earlier.**

Predeclare contrasts, tie handling, cluster units, combination rules, model versions, multiplicity, and failure criteria before generation. Move the shadow-mode design before Phase 4.4, and preferably execute a tiny v0.3 instrumentation MVP rather than ending with only a design doc.