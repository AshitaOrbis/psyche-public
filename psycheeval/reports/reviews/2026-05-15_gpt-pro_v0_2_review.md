I’ll treat the bundle as the full evidence base and focus on decision-changing failure modes: stratification, dependence, confounds, mechanism identification, and which claims need new draws versus reanalysis.

---

## First: headline claims that need tightening

- **Overclaim: “C5_CONTRACT outperforms both C3 and C4.”**

C5_CONTRACT vs C4 is supported pairwise. C5_CONTRACT vs C3 is **fragile**: bootstrap CI for C3 win rate is `[0.354, 0.500]`, so the inverse C5_CONTRACT advantage touches 0.5. Treat this as **borderline**, not settled.

- **Major inconsistency: pairwise says C5_CONTRACT beats C3/C4, scalar means do not.**

In the PI scalar table, **C3 beats C5_CONTRACT on every listed dimension**. C4 also beats or ties C5_CONTRACT on many dimensions. That means the “source packets add value when subordinated to contracts” claim is currently a **pairwise-judge preference claim**, not yet an anchored-rubric performance claim.

- **“v0.1 PAE confound is empirically resolved” is too strong.**

v0.2 shows that **adding a contract to the public-anchor source packet dramatically improves C5**. It does not yet isolate public anchoring, source-packet prose form, evidence richness, ordering, anti-mimicry language, or output-length effects.

- **C4 > C1_padded is strong, but it only kills one length confound.**

It controls for **input profile length**, not necessarily **output length**, verbosity, specificity, formatting, warmth, or judge-detectable condition cues.

- **C4 vs C4_shuffled should not be read as “structure does not matter” yet.**

It may mean the shuffle preserved the meaningful atomic directives, or that judges reward directive coverage more than coherent ordering. The ablation may be too weak.

---

# A. Further analytical angles on existing v0.2 data

## A1. Reconcile pairwise vs scalar before claiming C5_CONTRACT superiority

This is the most important missing analysis.

Run, for every same-author pairwise comparison, a paired scalar-delta analysis on the same scenario/persona/author/judge cells:

- `C5_CONTRACT − C3`

- `C5_CONTRACT − C4`

- `C5_CONTRACT − C5`

- `C4 − C1_padded`

- `C4 − C4_shuffled`

- `C4 − C5`

Then compare:

- Pairwise winner.

- Mean scalar delta across all dimensions.

- Scalar delta by dimension.

- Whether pairwise winner loses on anchored scalar dimensions.

Decision rule: if C5_CONTRACT wins pairwise but loses scalar dimensions, the headline should become:

> “Holistic pairwise judges often prefer C5_CONTRACT, but anchored scalar dimensions do not yet show consistent superiority over C3/C4.”

That is materially different from “source packets add value.”

## A2. Equal-weighted judge, author, persona, and scenario aggregation

Current pooled records risk pseudo-precision. The scalar record counts are unbalanced: Opus has 1,680 scalar records, GPT-5.4 has 1,134, GPT-5.5 has 1,135. Pairwise counts are also unbalanced: GPT-5.4 and GPT-5.5 each have about 1,294–1,295, while Opus has 534.

Compute all headline contrasts under:

- Micro-average over records.

- Macro-average over judges.

- Macro-average over authors.

- Macro-average over personas.

- Macro-average over scenario families.

- Full equal-weighted scenario/persona/author/judge cells.

If a headline survives only under pooled micro-averaging, it should be downgraded.

## A3. Per-judge and judge-family stratification

For each headline pair, report win rates separately by judge model/family.

Especially:

- C5_CONTRACT vs C5.

- C5_CONTRACT vs C4.

- C5_CONTRACT vs C3.

- C4 vs C4_shuffled.

- C4 vs C1_padded.

Also test:

- Judge-provider × author-provider interaction.

- Same-provider preference: does a judge prefer outputs written by models from the same provider family?

- Judge-condition halo: does one judge systematically reward richer profile cues or longer tailored language?

If C5_CONTRACT’s advantage is driven by one judge family, it is not yet a general result.

## A4. Per-author stratification

Run all headline contrasts separately for outputs authored by:

- GPT-5.4.

- GPT-5.5-xhigh.

- Opus 4.7.

This matters because “contract repair” may be an **author compliance effect**, not a profile effect. One model may follow anti-mimicry instructions well; another may overfit source packets; another may produce more judge-pleasing personalization prose.

Report:

- Win rate by author.

- Scalar deltas by author.

- Author × condition interaction.

- Whether C5_CONTRACT beats C5 for every author.

- Whether C5_CONTRACT beats C4 for every author.

## A5. Leave-one-unit-out fragility analysis

For each key pair, especially PI-only comparisons, run leave-one-out robustness:

- Leave one PI persona out.

- Leave one scenario family out.

- Leave one author out.

- Leave one judge out.

- Leave one high-leverage scenario out.

This is essential for C5/C5_CONTRACT because PI-only means only **four public-inspired personas**. A single persona could drive the result.

Report a table like:

| Contrast | Full win rate | Worst leave-one-persona rate | Worst leave-one-judge rate | Worst leave-one-author rate |
| --- | --- | --- | --- | --- |

If C5_CONTRACT > C4 collapses when one persona or judge is removed, it is not a stable source-packet result.

## A6. Mixed-effects / Bradley-Terry model instead of record-level Wilson summaries

Use a hierarchical pairwise model:

`winner ~ condition_contrast + author + judge + scenario_family + difficulty + output_length + condition×author + condition×judge + condition×family + random effects for persona/scenario`

Also run a scalar mixed model:

`score ~ condition + dimension + author + judge + persona + scenario_family + difficulty + interactions`

The current CIs are useful, but record-level pairwise summaries can understate dependence across shared outputs, scenarios, judges, and personas.

For binary pairwise outcomes, use either:

- Bradley-Terry / Thurstone model.

- Logistic mixed model.

- Multiway cluster bootstrap.

- Randomization test over paired scenario/persona/author units.

## A7. Output-length and stylometric sensitivity

C1_padded controls profile-context length, not assistant-output length. Judges may be rewarding responses that are longer, more structured, warmer, more specific, or more “profile-y.”

Compute for every output:

- Token count.

- Sentence count.

- Bullet count.

- Number of direct questions.

- Number of hedges.

- Number of concrete user-specific references.

- Number of profile-cue references.

- Readability / density.

- Apology / affirmation / challenge markers.

- “I notice / given your profile / for you” style markers.

- Public-anchor echoes for C5/C5_CONTRACT.

Then rerun headline contrasts:

- Raw.

- Length-matched.

- Length as covariate.

- Stylometry as covariate.

- Matched subsets by output token count.

Critical tests:

- Does C4 still beat C1_padded after output length control?

- Does C5_CONTRACT still beat C5 after output length and specificity control?

- Does C5_CONTRACT still beat C4 after output length and “profile-specific phrase” control?

## A8. Pairwise position effects and tie handling

Run position diagnostics:

- Win rate when condition appears on the left.

- Win rate when condition appears on the right.

- Judge-specific left/right bias.

- Condition-specific order bias.

- Whether longer response on top wins more often.

Then rerun all pairwise claims under tie sensitivity:

- Ties excluded.

- Ties counted as 0.5.

- Ties counted against focal claim.

- Near-ties collapsed using scalar thresholds, for example scalar aggregate delta `< 0.25` or `< 0.5`.

This matters most for:

- C4 vs C4_shuffled.

- C3 vs C5_CONTRACT.

- C1 vs C1_padded.

- Any pair with bootstrap CI near 0.5.

## A9. Scenario-family heterogeneity

You already have scenario-family blocks. Turn them into decision-relevant effects.

For each headline contrast, report win rate by family:

- interpersonal_conflict

- procrastination_avoidance

- authority_disagreement

- creative_feedback

- epistemic_uncertainty

- moral_uncertainty

- shame_self_interpretation

- ambition_status

Use shrinkage or hierarchical estimates, not just raw small-n percentages.

Questions to answer:

- Is C4’s advantage mostly interpersonal/shame and weak in epistemic/moral uncertainty?

- Does C5_CONTRACT help in ambition/status because public-anchor prose gives richer aspiration cues?

- Does C5 fail specifically in authority disagreement or epistemic uncertainty because source packets invite mimicry or over-personalized advice?

- Does C4_shuffled perform similarly because scenario hints are independent atoms?

Averages are not enough. The product question is “where does personalization help or harm?”

## A10. Difficulty and “personalization-need” interaction

Difficulty mean is matched, but average matching is not sufficient.

Run:

`effect_size ~ scenario_difficulty + condition + condition×difficulty`

Also manually tag or model-tag scenarios for:

- Need for emotional attunement.

- Need for epistemic calibration.

- Need for anti-sycophancy.

- Need for boundary-setting.

- Need for direct behavioral planning.

- Need for identity-sensitive language.

Then test whether profiles help most when the scenario actually requires personalization. If C4 beats C0 even in low-personalization scenarios, that suggests generic prompt quality rather than profile-specific value.

## A11. PI vs PS split for core conditions

For C0, C1, C1_padded, C3, C4, and C4_shuffled, report separately:

- PI personas only.

- PS personas only.

- Per-persona effects.

This is important because C5/C5_CONTRACT are PI-only. If C4’s core advantage behaves differently in PI vs PS, then comparing C5_CONTRACT to C4 on PI only may not generalize.

## A12. Persona × condition interactions and harm tails

Compute, for each persona:

- Best condition.

- Worst condition.

- C4 − C0.

- C4 − C1_padded.

- C5_CONTRACT − C4, for PI only.

- Rate of scalar regressions relative to C0.

Do not only report mean improvement. Report tail risk:

- % of outputs where profile condition is worse than C0.

- % where anti-sycophancy drops by >1 point.

- % where calibration drops by >1 point.

- % where boundaries drop by >1 point.

- Worst 5% examples by condition.

A condition that improves average helpfulness but creates rare high-risk failures is not production-ready.

## A13. Red-flag analysis should be predictive, not just correlational

For Q6, avoid a simple correlation headline.

Run:

`pairwise_loss ~ red_flag_type + condition + author + judge + scenario_family + persona`

Report:

- Which red flags predict losses.

- Whether red flags predict scalar drops.

- Sensitivity/specificity of red flags for bad pairwise outcomes.

- False positives: red flags that appear in winning outputs.

- False negatives: losing outputs with no red flags.

Separate red-flag classes:

- Public-anchor mimicry.

- Over-identification.

- Sycophantic agreement.

- Overconfident psychologizing.

- Boundary weakening.

- Excessive genericism.

- Advice that ignores scenario specifics.

- Profile overuse.

## A14. C4_shuffled autopsy

The C4 vs C4_shuffled result is important but currently under-interpreted.

Analyze the shuffled prompt itself:

- Did shuffling preserve complete if-then atoms?

- Did it merely reorder independent bullets?

- Did it break local coherence?

- Did it change salience of certain instructions?

- Did the first/last instruction positions change condition behavior?

Then analyze outputs:

- Did C4_shuffled outputs follow fewer instructions?

- Did they omit scenario hints?

- Did they become less coherent?

- Did they become more generic?

- Did judges fail to distinguish because outputs were functionally equivalent?

The likely interpretation is not “structure does not matter.” It is probably:

> “This specific shuffling operation did not remove enough functional behavioral information to reduce judged quality.”

## A15. C5 source-packet mechanism analysis

For C5 and C5_CONTRACT, code whether the output:

- Uses source-packet evidence appropriately.

- Imitates persona style.

- Mentions public-anchor-like details.

- Overfits to inferred identity.

- Subordinates packet evidence to the behavioral contract.

- Violates anti-mimicry rules.

- Adds useful specificity not present in C3/C4.

- Adds irrelevant psychologizing.

Then test whether these features predict wins/losses.

This would clarify whether C5_CONTRACT wins because of:

- More evidence.

- More vivid language.

- Better personalization.

- More judge-detectable profile use.

- More emotionally resonant prose.

- Longer outputs.

- Reduced C5 mimicry failures.

Those are different mechanisms.

## A16. Rubric-weight sensitivity

The scalar table should not be treated as one implicit utility function.

Compute aggregate scalar results under several weightings:

1. Equal-weighted all dimensions.

2. Safety-first: anti-sycophancy, calibration, boundaries, agency.

3. Personalization-first: profile fit, emotional attunement, transfer.

4. Epistemic-first: epistemic humility, calibration, non-carceral/non-coercive behavior if that is what `non_car` means.

5. Product-first: helpfulness, agency, transfer.

Then test whether C5_CONTRACT still beats C3/C4 under each. Given the current scalar means, I would expect the C5_CONTRACT > C3 claim to weaken sharply.

## A17. Condition discoverability

Train a cheap classifier or use simple feature analysis to predict condition from output text alone.

If judges can easily infer condition from response style, profile-specific phrasing, or public-anchor cues, then pairwise preferences may partly reward recognizable treatment rather than actual downstream quality.

Report:

- Condition-classification accuracy.

- Most predictive features.

- Whether easily detectable conditions win more often.

- Whether “profile-sounding” outputs get higher profile-fit scores even when not more helpful.

## A18. Missingness and balance audit

The scalar record counts imply incomplete or uneven judging. Run a missingness table by:

- Condition.

- Persona.

- Author.

- Judge.

- Scenario family.

- PI vs PS.

- C5/C5_CONTRACT availability.

If missingness is not random, the scalar means may be biased. At minimum, report complete-case scalar results where all three judges scored the same output.

---

# B. Affordable additional experiments for v3 confidence

## B1. Add wrong-profile and generic-contract controls

This is the biggest missing experiment.

Current C4 wins may reflect “good behavioral prompt engineering,” not user-specific personalization.

Add:

- **C4_GENERIC**: same length and structure as C4, but uses universally good assistant behaviors with no persona-specific content.

- **C4_WRONG_PROFILE**: use another persona’s C4 profile, matched by PI/PS type and approximate length.

- Optional: **C3_GENERIC** and **C3_WRONG_PROFILE**.

Run on the existing 80 persona-scenario cells, with three authors if feasible.

Key comparisons:

- C4_RIGHT vs C4_GENERIC.

- C4_RIGHT vs C4_WRONG_PROFILE.

- C4_GENERIC vs C0.

- C4_WRONG_PROFILE vs C0.

- C4_RIGHT vs C1_padded.

Decision logic:

- If C4_RIGHT > C4_GENERIC and C4_RIGHT > C4_WRONG_PROFILE, Psyche has evidence of profile-specific value.

- If C4_GENERIC ≈ C4_RIGHT, the main effect is generic behavioral prompting.

- If C4_WRONG_PROFILE ≈ C4_RIGHT, the profile is not doing much user-specific work.

- If C4_WRONG_PROFILE > C0 but < C4_RIGHT, both generic contract quality and profile match matter.

Approximate Opus cost: moderate. Generate only the new wrong/generic conditions with Opus; use Codex for full judging and Opus for a stratified judge sample.

## B2. Add C5_NONPUBLIC to isolate public-anchor effects

Add de-anchored source-packet conditions for PI personas:

- **C5_NONPUBLIC**: source-packet form, same inferred behavioral evidence, no public-anchor prose or public identity cues.

- **C5_NONPUBLIC_CONTRACT**: same, plus contract-first ordering and anti-mimicry rules.

Use existing C5 and C5_CONTRACT as the public-anchor versions.

Key comparisons:

- C5 vs C5_NONPUBLIC.

- C5_CONTRACT vs C5_NONPUBLIC_CONTRACT.

- C5_NONPUBLIC_CONTRACT vs C4.

- C5_NONPUBLIC vs C4.

- C5_NONPUBLIC_CONTRACT vs C5_NONPUBLIC.

Decision logic:

- If nonpublic packet + contract matches public packet + contract, public anchoring is unnecessary.

- If public packet wins only on profile-fit but loses safety/calibration, public anchoring is risky.

- If nonpublic packet fails while public packet succeeds, the public anchor is doing substantive work — but that raises generalization and ethics concerns.

- If both packet forms need contracts, the v0.2 C5 repair finding generalizes beyond public-anchor prose.

Approximate Opus cost: low to moderate. Only two new conditions across 40 PI scenario/persona cells.

## B3. Rerun critical pairwise judgments with stronger judge protocol

Before generating a large v3 corpus, rerun judging on existing outputs for the fragile/important pairs:

- C4 vs C4_shuffled.

- C3 vs C5_CONTRACT.

- C4 vs C5_CONTRACT.

- C5 vs C5_CONTRACT.

- C4 vs C5.

- C4 vs C1_padded.

Protocol changes:

- Balanced left/right order.

- Explicit tie option.

- Paraphrased rubric anchors.

- Blind condition labels.

- Instruction to ignore verbosity unless it improves substance.

- Separate “which is more helpful?” and “which better follows the profile?” questions.

- Record confidence.

This is probably more valuable than adding many new model outputs, because it directly tests whether the existing headline effects are judge-prompt artifacts.

Approximate Opus cost: 500–900 judge calls depending on sample size and whether you include swapped-order repeats.

## B4. Human-rater calibration sample

Do a small, carefully sampled human calibration set. Not a giant crowd study.

Sample 150–250 comparisons, stratified across:

- Strong model-judge agreement.

- Model-judge disagreement.

- C5_CONTRACT vs C4.

- C5_CONTRACT vs C3.

- C5 vs C5_CONTRACT.

- C4 vs C4_shuffled.

- C4 vs C1_padded.

- Worst-tail safety cases.

- Wrong-profile/generic-profile comparisons if B1 is run.

Use 3–5 trained raters. Blind conditions. Ask for dimension-level ratings, not just overall preference.

Report:

- Human-human agreement.

- Human-model agreement.

- Which model judge aligns best with humans.

- Whether humans also prefer C5_CONTRACT over C4.

- Whether humans detect source-packet mimicry or over-personalization more harshly than model judges.

This is not about replacing model judging. It is about calibrating whether the model-judge preference surface is sane.

## B5. Profile-format and ordering ablation for C5_CONTRACT

C5_CONTRACT has multiple bundled design decisions:

- Contract-first ordering.

- Source packet as evidence.

- Public-anchor prose.

- Anti-mimicry rules.

- Extra context length.

- Richer specificity.

A small ablation should isolate the mechanism.

Add variants on a PI subset:

- **C5_CONTRACT_PACKET_FIRST**: source packet before contract.

- **C5_CONTRACT_NO_ANTI**: remove explicit anti-mimicry rules.

- **C5_FACTS_CONTRACT**: convert source packet into neutral behavioral-evidence bullets, no prose.

- **C5_SUMMARY_CONTRACT**: compressed source-packet summary with same token budget as C4.

- Optional: **C5_CONTRACT_LENGTH_MATCHED_TO_C4**.

Key comparisons:

- C5_CONTRACT vs C5_FACTS_CONTRACT.

- C5_CONTRACT vs C5_SUMMARY_CONTRACT.

- C5_CONTRACT vs C5_CONTRACT_PACKET_FIRST.

- C5_CONTRACT vs C5_CONTRACT_NO_ANTI.

- C5_FACTS_CONTRACT vs C4.

Decision logic:

- If facts-contract ≈ source-prose-contract, prose packets are unnecessary.

- If packet-first degrades, ordering matters.

- If no-anti degrades, anti-mimicry is an active safety component.

- If length-matched C5_CONTRACT loses advantage, packet benefit may be token/specificity driven.

## B6. Length-controlled generation rerun

Run a small generation rerun with strict output budgets.

For example:

- 180–220 words max.

- Same response structure.

- Same number of bullets.

- No explicit “given your profile” phrasing unless substantively necessary.

Key contrasts:

- C4 vs C1_padded.

- C5_CONTRACT vs C5.

- C5_CONTRACT vs C4.

- C4 vs C4_shuffled.

If headline effects shrink materially under matched output length and structure, v0.2 was partly measuring judge preference for richer response form.

This can be Codex-heavy, with Opus only on a stratified subset.

## B7. Held-out persona replication

Add at least one new PI-style persona and one new PS persona, with new scenarios.

Do not run full all-vs-all. Use only decisive and fragile contrasts:

For PS:

- C0.

- C1_padded.

- C3.

- C4.

- C4_shuffled.

- C4_GENERIC or C4_WRONG_PROFILE.

For PI:

- C3.

- C4.

- C5.

- C5_CONTRACT.

- C5_NONPUBLIC.

- C5_NONPUBLIC_CONTRACT.

- C4_GENERIC or C4_WRONG_PROFILE.

Use 10–20 scenarios per new persona, biased toward scenario families where v0.2 found high heterogeneity.

Purpose:

- Test whether results survive beyond the original eight personas.

- Test whether C5_CONTRACT’s apparent value is persona-specific.

- Test whether public-anchor packets generalize.

## B8. Rubric robustness check

Rerun scalar judging on a subset using:

- Original anchors.

- Paraphrased anchors.

- Short anchors.

- Safety-weighted rubric.

- Personalization-weighted rubric.

- Rubric with “do not reward profile name-dropping” explicitly stated.

Then test whether the same condition ordering appears.

This is especially important because v0.1 to v0.2 changed the judging rubric, and C5’s competitiveness did not replicate. That suggests rubric sensitivity is real.

## B9. Adversarial and negative-control scenarios

Add a small hard set designed to trigger failures:

- User asks for reassurance when they need challenge.

- User asks for identity-confirming advice based on shaky evidence.

- User gives a manipulative or self-serving framing.

- User asks assistant to imitate their style.

- User asks for public-persona-like language.

- User presents emotionally charged but epistemically ambiguous claims.

- User asks for advice where profile hints conflict with current stated preference.

- User tries to override profile instructions.

Run only:

- C0.

- C4.

- C4_WRONG_PROFILE.

- C5.

- C5_CONTRACT.

- C5_NONPUBLIC_CONTRACT.

Report mean performance and worst-tail failures.

This tests whether personalization remains safe when the scenario is adversarial rather than cooperative.

---

# C. Deeper open questions for v3

## C1. Is Psyche measuring personalization, or just better prompting?

This is the central exposure.

C4 beating C0/C1_padded does not prove user-specific personalization. It may prove that a structured behavioral contract makes assistants better in general.

v3 needs right-profile vs wrong-profile vs generic-contract controls. Without them, the strongest defensible claim is:

> “Structured behavioral contracts improve judged responses under this scenario set.”

Not yet:

> “User-specific profiles improve responses.”

## C2. What is the target outcome?

Right now the target is mostly model-judge preference under synthetic scenarios.

v3 needs to define the primary endpoint:

- User preference?

- User feeling understood?

- Task completion?

- Better decisions?

- Less sycophancy?

- More calibrated challenge?

- Long-term user satisfaction?

- Safety under emotionally charged requests?

- Transfer to real conversations?

Different endpoints will rank conditions differently. C5_CONTRACT may win holistic pairwise preference while losing safety-weighted scalar rubrics. That distinction matters.

## C3. Real-user validation strategy

Synthetic-first is fine for iteration, but v3 should specify the bridge to real users.

A credible staged path:

1. Synthetic stress tests.

2. Human-rater calibration.

3. Profile-owner preference tests on de-identified real or semi-real scenarios.

4. Prospective user study with pre-registered outcomes.

5. Longitudinal deployment metrics.

6. Safety review for tail failures.

Do not jump directly from model-judge synthetic wins to product claims.

## C4. Reverse causality and judge-detectable tailoring

A response may look “good under a profile” because it visibly uses profile-like language. Judges may reward that signal.

The causal question is:

> Does the profile cause better help, or do good/verbose/profile-sounding responses get judged as better profile use?

Needed controls:

- Wrong-profile condition.

- Generic-contract condition.

- Condition-blind human judging.

- Output-length control.

- Condition-discoverability classifier.

- Profile-specificity penalty rubric.

## C5. Profile-format generalization

v0.2 tests specific artifacts:

- Trait labels.

- Behavioral contracts.

- Scenario hints.

- Shuffled contract/hints.

- Public-anchor source packets.

- Contract-subordinated source packets.

But the broader question is which representation is robust:

- If-then rules?

- Trait labels?

- Evidence packets?

- Natural-language summaries?

- User-authored preferences?

- Learned latent profile?

- Dynamic memory?

- Minimal safety contract?

- Source-derived behavioral hypotheses?

C4_shuffled’s result suggests that the exact coherence of the profile format may not be doing what the project assumes. v3 should identify the minimal sufficient profile representation.

## C6. Behavioral-contract specification language

C3/C4 appear powerful. That makes the contract itself a core product object.

Open questions:

- Which clauses are essential?

- Which clauses are harmful?

- How much specificity is needed?

- How should challenge vs validation be encoded?

- How should anti-sycophancy be operationalized?

- How should the assistant handle profile-current-message conflict?

- When should the assistant ignore the profile?

- How should uncertainty about the profile be expressed?

- What is the safest instruction hierarchy?

The C5_CONTRACT result may be less about source packets and more about getting the contract spec right.

## C7. Public-anchor ethics and generalization

C5/C5_CONTRACT are PI-only and use fictionalized public-anchor prose. That creates unresolved issues:

- Public personas may be caricatured.

- Source packets may invite style mimicry.

- Judges may reward vividness from public identity cues.

- Public-anchor results may not generalize to private users.

- The system may infer sensitive traits too confidently.

- Public-source prose may create privacy and consent problems if generalized.

C5_NONPUBLIC is not optional if source packets remain part of the project.

## C8. Judge pluralism limits

Three LLM judges from two provider families are useful, but not enough to settle normative questions.

Risks:

- Shared RLHF preferences.

- Shared “helpful therapist-like answer” aesthetics.

- Overrewarding warmth and structure.

- Underpenalizing subtle manipulation.

- Underpenalizing profile overreach.

- Provider-family bias toward familiar writing styles.

- Preference for longer, more polished outputs.

v3 should treat model judges as scalable screeners, not final arbiters.

## C9. Cross-cultural and non-English validity

The current scenario families and profile interpretations likely encode Anglophone norms around:

- Agency.

- Assertiveness.

- Shame.

- Authority disagreement.

- Emotional disclosure.

- Ambition/status.

- Moral uncertainty.

- Directness vs indirectness.

A profile that improves responses in English interpersonal-conflict scenarios may fail in other languages or cultural contexts. Translation alone will not solve this; scenario norms and judge rubrics need localization.

## C10. In-distribution performance vs predictive validity

The current corpus tests responses to curated scenario families. It does not prove prediction for:

- Real user conversations.

- Long multi-turn interactions.

- Ambiguous user intent.

- Changing user preferences.

- High-stakes decisions.

- Contexts where the profile is stale or wrong.

- Tasks outside the eight scenario families.

v3 should include out-of-distribution scenarios and profile-current-message conflict cases.

## C11. Tail-risk governance

Mean improvements are not enough.

Personalization can fail by:

- Becoming sycophantic.

- Over-psychologizing.

- Treating profile hypotheses as facts.

- Suppressing user agency.

- Encouraging identity fixation.

- Mimicking public figures.

- Failing to update from the current message.

- Giving overconfident advice in morally or epistemically ambiguous situations.

v3 should predefine safety-tail metrics, not just helpfulness averages.

## C12. Scenario construction bias

If scenarios were written with profile-relevant behavior in mind, profile conditions may get an artificial advantage.

Needed checks:

- Scenarios written blind to condition.

- Scenarios written by different authors.

- Scenarios generated from user tasks rather than profile theory.

- Scenarios where profile information is irrelevant.

- Scenarios where profile information is misleading.

- Scenarios where current user request conflicts with profile.

Without this, PsycheEval may partly measure “does the profile help on profile-shaped scenarios?”

## C13. Deployment reality: context budget and profile freshness

C5_CONTRACT may work because it gives rich context. In deployment, the system will face:

- Context-window tradeoffs.

- Stale profile information.

- Contradictory memories.

- User edits.

- Privacy constraints.

- Latency constraints.

- Need for explainability.

- Need for user control over personalization.

v3 should test compressed profiles and stale/wrong profile variants.

## C14. Source-packet value vs behavioral-contract value

The deepest mechanism question after v0.2 is:

> Are source packets adding information, or are they merely making the assistant sound more specifically attuned?

To answer this, v3 needs:

- Nonpublic source packets.

- Neutral fact packets.

- Length-matched packets.

- Wrong packets.

- Generic contracts.

- Profile-owner/human preference checks.

- Safety-weighted judging.

Until then, “source packets add value” should be treated as a live hypothesis, not a settled conclusion.

---

## Recommended v3 priority order

1. **Run existing-data reanalysis first**, especially scalar-pairwise reconciliation, per-judge/per-author stratification, leave-one-persona-out, and output-length controls.

2. **Add wrong-profile and generic-contract controls.** This is the main missing causal test.

3. **Add C5_NONPUBLIC and C5_NONPUBLIC_CONTRACT.** This isolates public-anchor effects.

4. **Rerun critical pairwise judgments with tie/order/rubric robustness.** Especially C5_CONTRACT vs C3/C4 and C4 vs C4_shuffled.

5. **Add a small human calibration sample.** Do not scale model-judge conclusions without it.

6. **Only then expand personas/scenarios.** More data before these controls risks precisely estimating the wrong effect.