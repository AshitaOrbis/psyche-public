## 1. Consensus

All four agents converged on the following points (with strength of agreement noted):

- **v0.2 is publishable as a scoped, methodology-forward report — not a mechanism paper.** No remaining data-level blocker if the report is disciplined. [unanimous]
- **`C5_CONTRACT > C5` is the cleanest Tier 1 finding, but supports only a *package* claim, not a *mechanism* claim.** Contract presence is confounded with ordering, anti-mimicry text, profile length, and instruction density. Mechanism attribution requires `C_GENERIC_CONTRACT` and related v0.3 ablations. [unanimous]
- **`C3 vs C5_CONTRACT` should be reported as "no all-judge controlled preference" (49.9% CI crossing 0.5).** The earlier cross-provider stratified result is a judge×position-bias interaction / hypothesis-generating diagnostic, not a verdict. The `C5_CONTRACT vs C4` edge also collapses. [unanimous]
- **`C4 > C5` is scope-limited.** Phase 0 confirmed zero Opus pairwise records on this edge. It must be labeled "OpenAI-judge / PI-author pairwise" — not "tri-model" — unless an Opus AB/BA fill is run. [unanimous]
- **`C4 > C4_shuffled` is positive but modest** (57.8% controlled). Report as "moderate evidence for coherent ordering," not as a peer-strength Tier 1 claim. Persona/family heterogeneity is meaningful. [unanimous]
- **Stale/contradictory prose must be fixed before curation.** Specifically the Phase 1 line claiming `C4_shuffled` wins (it doesn't — final table shows C4 at 57.8%), and any "cross-provider primary" framing in the autogen. [skeptic, architect, risk-analyst, empiricist]
- **The slot-B position-bias finding is real and publishable, but "pure position bias" overclaims.** AB/BA flips can reflect position bias + stochasticity + ambiguous pair quality. Direction-and-magnitude of orig-vs-swap asymmetry is the position-bias evidence; raw flip rate is instability+bias. [skeptic, architect, risk-analyst; empiricist concurs implicitly via citing Zheng/Judging-the-Judges]
- **Replace the rough Wilson AB/BA CI with paired/cluster bootstrap over scenario×persona×author cells.** All four agents independently spot-checked this; none of their cluster bootstraps overturned Tier 1 verdicts, but the canonical numbers should reflect the matched estimator. [unanimous]
- **Add AB/BA stratified tables by judge, author, provider-scope, persona, scenario family, and length bucket.** Highest-value single analyzer addition. [unanimous]
- **Add the complete-case scalar table Phase 0 asked for.** Current 67.5% complete-case rate is too low to rely on pooled means alone for scalar reconciliation. [skeptic, architect, risk-analyst, empiricist]
- **v0.3 priority #1 is `C_GENERIC_CONTRACT` + `C4_WRONG_PROFILE`.** This is the cheapest decisive test of whether PsycheEval is measuring personalization vs. generic high-quality behavioral prompting. [unanimous]
- **Round 1 underweighted: profile *failure modes*** (stale, contradictory, misleading, user-edited profiles), **judge reliability as an experimental object** (same-order repeats, rubric paraphrase, tie calibration), and **scenario construction controls / profile-irrelevant scenarios**. [skeptic, architect, risk-analyst, empiricist — each surfaced a subset; together they converge]

## 2. Disagreements

The agents are unusually aligned this round. There are three genuine seams, all about *emphasis* rather than direction:

**Disagreement 1: How hard to gate v0.2 on the Opus C4-vs-C5 fill.**
- *Architect / Empiricist position*: The Opus AB/BA fill is "optional but high value." If skipped, just label `C4 > C5` as OpenAI-judge-only and ship.
- *Skeptic position*: This is the single <1-day experiment "higher value than starting a new condition" if you want `C4 > C5` as a real Tier 1 headline. Implicitly closer to "do it before curation."
- *Risk-Analyst position*: Treats the coverage gap as a labeling problem, not an experiment problem.
- **Adjudication**: The Skeptic has the stronger case *if* you want `C4 > C5` to read as a generalizable Tier 1 finding rather than a scope-limited one. The Architect/Empiricist framing is correct if you accept a tightly-scoped headline. Since the cost is low (<1 day, well within the 1–2K Opus budget) and the alternative is a permanent scope caveat on the headline, **do the Opus fill before curation.** This is the cleanest reconciliation.

**Disagreement 2: How to treat the slot-B position bias finding rhetorically.**
- *Skeptic / Architect / Risk-Analyst position*: Don't call `position_flip_rate` "pure position bias" — it conflates order bias with judge stochasticity. Need a same-order repeat control (Architect proposes 50–100 pair re-judgments) before standalone methodological claims.
- *Empiricist position*: The finding is unsurprising in light of Zheng 2023 and Judging-the-Judges 2024; what's valuable is that PsycheEval quantified it on its own corpus. Doesn't demand the same-order repeat control as a blocker.
- **Adjudication**: Skeptic/Architect/Risk-Analyst have the stronger case on **wording discipline** ("slot-B preference of magnitude X" rather than "position bias of X"). Empiricist is right that the *publication value* of the finding doesn't depend on the control. **Reconciliation: publish the finding with disciplined wording; add the same-order repeat mini-audit (50–100 pairs) as a quick fix — it's cheap and it converts the methodology section from "we observed flips" to "we decomposed flips into position effect + retest noise."**

**Disagreement 3: Whether AB/BA-controlled estimates have a hidden second-order problem.**
- *Risk-Analyst position*: "Counterbalancing can create false certainty: high flip rates mean the judge instrument is noisy, not merely position-biased." Flags this as a second-order risk that adding diagnostics can look like post-hoc fishing — predeclare confirmatory vs. stress-test vs. v0.3 hypothesis-generation tables.
- *Empiricist / Architect / Skeptic position*: None challenge this; none emphasize it. Implicit position: noise widens CIs, AB/BA still gives the unbiased point estimate.
- **Adjudication**: This isn't really a disagreement — it's a concern the Risk-Analyst raised that the others didn't address. **It deserves to be flagged in the report's methods section.** A high flip rate after controlling for order means the underlying judge construct is noisy regardless of who's in slot B. That should temper any "Tier 1 is robust" framing into "Tier 1 estimates have meaningful instrument noise; replication on independent corpora is v0.3 work."

## 3. Open questions

- **Does the C5_CONTRACT package effect survive when contract is paired with a *generic* (non-profile-specific) personality contract?** [unanimous — primary v0.3 question]
- **What fraction of the AB/BA flip rate is order bias vs. retest stochasticity vs. genuinely ambiguous pair quality?** Cannot be answered without same-order repeats. [skeptic, architect, risk-analyst]
- **Do `C4 > C5` and `C4 > C4_shuffled` survive *under Opus judges*?** Currently unknown due to zero Opus pairwise records on the C4-vs-C5 edge. [skeptic, empiricist]
- **Does response length mediate any Tier 1 controlled win after AB/BA?** Phase 0 had a length warning on `C4 > C5`; nobody has run AB/BA × length-bucket as a single table. [skeptic, risk-analyst]
- **Are scenarios advantaged toward profile-conditions by construction?** Scenarios may have been written with persona content in mind. Synthesis-emergent + empiricist.
- **What is PsycheEval's *target outcome*?** Skeptic surfaced this as the meta-question: model-judge agreement is judge calibration, not construct validity. User preference, satisfaction, follow-through, expert decision-quality — which? [skeptic, risk-analyst]
- **Does a bad/stale/contradictory profile cause measurable harm, or just zero uplift?** Round 1 focused on uplift; harm is the deployment-relevant variable. [risk-analyst, skeptic]
- **Is the multiclass TF-IDF discoverability audit actually the right test for pair-specific recognition?** Skeptic argues no — needs binary, pair-specific, grouped audits. Synthesis-emergent question: was any pair-specific recognition test ever run, or is the report relying on the multiclass F1=0 result as if it were one?

## 4. Final recommendation

**Write v0.2 now as a disciplined, tiered methodology-and-scoped-results report.** Three claim types, no more:

1. **Methodology finding (publishable as a primary contribution):** PsycheEval's AB/BA counterbalancing exposed a ~15–17pp slot-B preference in pairwise LLM judging, with judge-family variance (gpt-5.4 negligible; gpt-5.5 25–31pp; Opus 9–24pp). Word as "slot-B preference," not "pure position bias." Cite Zheng 2023 and Judging-the-Judges 2024 for prior art; frame PsycheEval's contribution as in-corpus quantification.

2. **Surviving Tier 1 package effects (with explicit scope):**
   - `C5_CONTRACT > C5` at 67.7% controlled [62.1, 72.8] — **package claim only**, no mechanism language.
   - `C4 > C1_padded` at 66.1% controlled [59.5, 72.0].
   - `C4 > C5` at 68.9% controlled [61.6, 75.9] — **OpenAI-judge pairwise scope** unless Opus fill is run first (recommended: run it).
   - `C5_CONTRACT > C5` and `C0` dominated by profile conditions — scalar evidence noted alongside pairwise.
   - `C4 > C4_shuffled` at 57.8% — **demote to "moderate evidence for coherent ordering"**, not peer-strength with the above.

3. **Collapsed-to-null findings (report transparently):** `C3 vs C5_CONTRACT` and `C4 vs C5_CONTRACT` show no controlled all-judge preference. The earlier "C5_CONTRACT outperforms C3/C4" headline is retracted.

**Forbidden wording in the curated report:** "tri-model" on non-C5 pairwise edges, "PAE resolved," "mechanism," "contract repairs source packets," "cannot be a recognition artifact" (the multiclass F1 test doesn't establish this), and "pure position bias."

**Confidence:**
- **High** that v0.2 can ship in this form and tell an honest, defensible story.
- **High** that `C5_CONTRACT > C5` is the right anchor finding under package framing.
- **Medium** that the surviving Tier 1 edges generalize beyond OpenAI judges — this is exactly what the Opus fill resolves.
- **Low** that v0.2 says anything about real-user validity or personalization mechanism — and the report should explicitly disclaim both.

**Conditions that would change the recommendation:**
- If matched/cluster AB/BA CIs cross 0.5 for `C5_CONTRACT > C5` or `C4 > C1_padded`: demote those edges, don't rescue with wording.
- If complete-case scalar table flips a Tier 1 headline: same — demote.
- If Opus AB/BA fill reverses `C4 > C5`: demote to OpenAI-judge-only or collapse to null.
- If a binary pair-specific discoverability audit shows `C5` vs `C5_CONTRACT` is text-recognizable: the package claim becomes "package + recognition" and needs caveats.

**Cheapest decisive next actions (in priority order before drafting the curated report):**

1. **Run paired/cluster bootstrap CIs on the canonical AB/BA table.** (Hours, no new data.)
2. **Add the AB/BA × judge × author × provider-scope × persona × family × length-bucket stratified table.** (Hours.)
3. **Fix the stale prose** in Phase 1 (`C4_shuffled` direction, line ~199–201) and the autogen "cross-provider primary" framing. Add a string lint against forbidden phrases. (Minutes.)
4. **Add the complete-case scalar table.** (Hours.)
5. **Run the Opus AB/BA fill for `C4 vs C5`.** (<1 day; fits in budget; converts a scope-limited headline into a generalizable one — or correctly demotes it.) Skeptic's strongest specific recommendation.
6. **Run binary pair-specific discoverability audits** for `C5 vs C5_CONTRACT`, `C4 vs C4_shuffled`, and `C1_padded vs C4`, grouped by scenario/author/persona. (Hours.) Replaces over-reliance on the multiclass F1 result.
7. **Run a same-order repeat mini-audit on 50–100 pair judgments.** Converts the slot-B finding from "we saw flips" into "we decomposed flips into order effect + retest noise." (Hours.)
8. **Add a claim-scope table** to the report itself: claim → estimate → allowed wording → forbidden wording → scope → remaining caveat. Risk-Analyst's single highest-leverage suggestion. (Minutes.)

**v0.3 design (one factorial, not a list of one-offs):**

The Architect's framing is the strongest: v0.3 should be a small **factorial mechanism design** around the C5/C5_CONTRACT package, plus a parallel **profile-realism arm**.

- *Mechanism arm:* `C_GENERIC_CONTRACT`, `C4_WRONG_PROFILE`, `C5_NONPUBLIC`, `C5_NONPUBLIC_CONTRACT`, `C5_CONTRACT_SHORT`, packet-first vs. contract-first ordering, no-anti-mimicry variants, facts-only packets.
- *Profile-realism arm:* stale, partially wrong, contradictory, user-edited, low-confidence profiles. Measure *harm*, not just uplift.
- *Judge-reliability arm (default infrastructure, not separate experiments):* AB/BA by default, same-order repeats, tie calibration, rubric paraphrase, judge-family stratification.
- *Construct-validity arm:* real-user shadow validation with predeclared target outcomes (preference, satisfaction, follow-through, expert-rated decision quality, escalation rate). This is the deepest underweighted question from round 1 — surfaced by the Skeptic.
- *Tail-risk reporting:* worst-decile and red-flag rates, not only mean win rates. Risk-Analyst contribution.
- *Compression curve:* how much benefit survives at 500, 1,000, 2,000 tokens? Architect contribution.

## 5. Attribution map

| Claim | Contributing agent(s) |
|---|---|
| v0.2 publishable as scoped report, no data-level blocker | unanimous |
| `C5_CONTRACT > C5` is package claim only, not mechanism | unanimous |
| `C3 vs C5_CONTRACT` reports as no-preference; cross-provider is exploratory | unanimous |
| `C4 > C5` is OpenAI-judge-scope unless Opus fill done | skeptic, architect, empiricist; risk-analyst (as labeling risk) |
| `C4 > C4_shuffled` should be demoted from peer-strength Tier 1 | skeptic, architect, risk-analyst, empiricist |
| Stale Phase 1 prose contradicts canonical table (line ~199–201) | empiricist (precise line cite), skeptic, risk-analyst |
| Slot-B finding ≠ "pure position bias" — needs disciplined wording | skeptic, architect, risk-analyst |
| Same-order repeat mini-audit (50–100 pairs) as quick fix | architect (sized it) |
| Replace rough Wilson with paired/cluster bootstrap | unanimous — analyzer self-noted limitation cited by skeptic & empiricist |
| AB/BA stratified table is highest-value analyzer addition | empiricist, architect, risk-analyst |
| Complete-case scalar table needed | unanimous |
| Multiclass TF-IDF F1 is wrong test for pair-specific recognition | skeptic (sole; sharp call) |
| Binary pair-specific discoverability audit needed | skeptic |
| Opus AB/BA fill for `C4 vs C5` is highest-value <1-day experiment | skeptic, empiricist |
| Claim-scope table in the report itself | risk-analyst |
| String lint against forbidden phrases | risk-analyst |
| Cross-author leak invariant in curation | risk-analyst |
| AB/BA creates false certainty if flip rate reflects judge noise | risk-analyst (second-order risk) |
| Predeclare confirmatory vs. stress-test vs. v0.3-hypothesis tables | risk-analyst |
| v0.3 = factorial mechanism design, not one-off ablations | architect |
| Profile failure modes / harm-not-uplift | skeptic, architect, risk-analyst |
| Real-user shadow validation with predeclared target outcomes | skeptic, risk-analyst |
| Scenario construction controls / profile-irrelevant scenarios | empiricist, architect, risk-analyst |
| Tail-risk reporting (worst-decile, red-flag rates) | risk-analyst |
| Compression curve at 500/1K/2K tokens | architect |
| Judge reliability as default infrastructure (not post-hoc rescue) | empiricist, architect |
| Zheng 2023 / Judging-the-Judges 2024 prior art | skeptic, empiricist |
| Synthesis-emergent: was a binary pair-specific recognition test ever run? | synthesis-emergent (from skeptic's critique of the multiclass test) |
| Synthesis-emergent: PsycheEval's target outcome (judge calibration vs. construct validity) is the meta-question | skeptic surfaced; synthesis elevated |
