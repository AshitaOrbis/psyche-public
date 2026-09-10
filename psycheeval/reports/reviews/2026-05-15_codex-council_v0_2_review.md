## 1. Consensus

**Labeling defect is the headline blocker** `[unanimous]`. The bundle calls the n=320/n=288 pairwise table "cross-provider, same-author" ([bundle:61](file://~/claudeworkspace/psyche/psycheeval/reports/reviews/2026-05-15_v0_2_review_bundle.md)), but the autogen scaffold and raw JSONL audit show those rows are all-judge same-author (or OpenAI-only for non-C5_CONTRACT edges). True cross-provider same-author is only 264 records and only covers the three C5_CONTRACT edges ([autogen:14](file://~/claudeworkspace/psyche/psycheeval/reports/psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md), [metrics:748](file://~/claudeworkspace/psyche/psycheeval/reports/metrics_2026-04-26_v02_hard_codex_only.json)). Fix before any curated report leaves the building. (Empiricist verified via raw join; Risk Analyst, Skeptic, Architect independently surfaced.)

**Two headlines survive intact** `[unanimous]`: C4 > C1_padded (68.1%) and C5_CONTRACT > C5 (76.0%). Bootstrap CIs are comfortably above 0.5; effect holds across judges per Empiricist's raw audit. Behavioral contracts beat padded length is real; the contract repairs C5's fragility is real.

**"C5_CONTRACT outperforms C3" is overphrased** `[unanimous]`. Cluster bootstrap CI for C3 vs C5_CONTRACT reaches exactly 0.500 ([metrics:1876](file://~/claudeworkspace/psyche/psycheeval/reports/metrics_2026-04-26_v02_hard_codex_only.json)); GPT-5.4 actively reverses it (C3 wins ~57%); epistemic-uncertainty and shame scenario families also reverse. Reword as "directionally beats C3, not robust under clustered CI or judge stratification."

**"Source packets add value when subordinated to contracts" is not yet earned** `[unanimous]`. C5_CONTRACT changes 5+ things at once vs C3/C4 (source packet, contract, prompt order, anti-mimicry, profile length). Profile char means: C3 2,518 / C4 3,689 / C5 3,884 / C5_CONTRACT 7,433 ([metrics:3565](file://~/claudeworkspace/psyche/psycheeval/reports/metrics_2026-04-26_v02_hard_codex_only.json)). Until length and order are controlled, the source-packet causal claim is confounded.

**Position bias is unaudited and structurally present** `[skeptic, architect, risk-analyst, empiricist]`. C5_CONTRACT is always slot B in the headline pairs; lower-numbered conditions are nearly always slot A. Zheng et al. 2023 and Shi et al. 2024 document material judge position bias. Cannot estimate from current data; flag as design limitation until AB/BA is run.

**Scenario-family heterogeneity should be promoted from appendix to primary** `[unanimous]`. Reversals exist: epistemic_uncertainty favors C3 over C5_CONTRACT (64.3%); shame is mixed; ambition/authority/moral families drive most of the average effect ([autogen:195](file://~/claudeworkspace/psyche/psycheeval/reports/psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md)).

**Red-flag conclusions remain judge-fragile** `[risk-analyst, architect, empiricist, skeptic]`. Mean κ for red-flag agreement is ~0.231 GPT-5.4 vs GPT-5.5 ([metrics:3651](file://~/claudeworkspace/psyche/psycheeval/reports/metrics_2026-04-26_v02_hard_codex_only.json)). Pairwise-record red flags are post-hoc rationales from the same judge — nearly tautological as predictors. Use independent / left-out-judge red flags before claiming a flag→loss relationship.

**v3's biggest exposure is construct/predictive validity, not leaderboard strength** `[unanimous]`. Cronbach & Meehl construct-validity framing (Skeptic); kickstart already named this limitation (Architect, Empiricist); real users may prefer responses model judges penalize and vice versa (Risk Analyst).

## 2. Disagreements

This is a high-consensus case. The four agents largely converge; the genuine disagreements are about *degree of publishability* and *which experiment is cheapest decisive*.

**Disagreement 1: Is v0.2 publishable now with relabeling + softened claims, or does it need same-data robustness gates first?**

*Architect's strongest argument*: Analysis-first hardening (relabel, stratify, length-model, family forest plot) is achievable on existing data and gets a defensible methodology pilot out the door. The two robust findings carry the report; the weak ones get downgraded. Don't burn quota before squeezing existing data.

*Risk Analyst's strongest argument*: "Proceed with mitigation" but the mitigation list is long — labels fixed, C5_CONTRACT > C3 downgraded, C4 > C5 marked OpenAI-judge-only, length sensitivity and family heterogeneity promoted. If any of these can't survive in a curated report, abort/pause.

*Adjudication*: They're closer than they look. Architect's path is Risk Analyst's mitigation list. The practical sequence is: do the same-data hardening (Section A below), and *that* produces the publishable v0.2 report. Skip new experiments only if the report can preserve scope qualifiers; if relabeling forces "we have no clean cross-provider non-C5_CONTRACT evidence" and that's unacceptable, then a small Opus backfill is needed before publication.

**Disagreement 2: AB/BA rejudging vs C5_NONPUBLIC as the highest-value next Opus spend.**

*Skeptic/Empiricist's argument*: AB/BA is the cheapest decisive check because position bias confounds every C5_CONTRACT pairwise win (always slot B). If AB/BA flips the order, the most exciting v0.2 claim collapses. ~200-800 pairs covers it.

*Architect's argument*: Both matter, but C5_NONPUBLIC is the only experiment that actually isolates the public-anchor mechanism — and the v0.2 plan already named it as the deferred high-value variant. Without it, the source-packet causal claim is structurally unresolvable.

*Adjudication*: AB/BA first, C5_NONPUBLIC second — and they're not competing for the same budget. AB/BA is a few hundred Opus draws; C5_NONPUBLIC requires authoring new conditions plus judging. Run AB/BA inside the existing data first (cheaper, faster, tests a methodological fragility that affects *all* C5_CONTRACT claims). If AB/BA holds, then spend on C5_NONPUBLIC. If AB/BA flips, the planned C5_NONPUBLIC design needs revision before it's worth running.

**Disagreement 3 (latent): How strong is the C4 > C5 finding?**

*Empiricist/Risk Analyst*: Opus has zero observed C4 vs C5 pairwise records ([metrics:3353](file://~/claudeworkspace/psyche/psycheeval/reports/metrics_2026-04-26_v02_hard_codex_only.json)); GPT-5.4 and GPT-5.5 have 80 each. This is an OpenAI-judge result, not tri-judge. Label accordingly.

*Skeptic*: Treats C4 > C5 (63.7%) as relatively secure compared to the C5_CONTRACT claims.

*Adjudication*: Risk Analyst is right on the data — this is OpenAI-judge-only. Skeptic's framing is too generous given the coverage gap. Add to the relabeling work: C4 > C5 needs an explicit "Opus backfill pending" footnote, or the headline needs the judge-subset qualifier.

## 3. Open questions

- **Does C4 > C4_shuffled (51.9%, CI straddles 0.5) mean structure isn't the mechanism, or that the shuffle didn't damage the operative instructions?** Skeptic raised — the null result is hard to interpret without an audit of what the shuffle actually disrupted. Synthesis-emergent follow-up: was the shuffle at the section level or the sentence level? Section-level shuffles may leave block-internal directives intact.

- **Is C5_CONTRACT's pairwise win partly response-verbosity?** Architect noted length buckets flip several pairwise patterns ([autogen:87,101](file://~/claudeworkspace/psyche/psycheeval/reports/psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md)). Cannot resolve without length-matched C5_CONTRACT_SHORT or response-length regression.

- **Do "good profiles" cause better answers, or just make answers easier to judge as good?** Empiricist raised; this is a reverse-causality / construct-validity question that the existing data cannot answer.

- **How much of the C5_CONTRACT effect is driven by one PI persona?** Skeptic found `pfi_slalom_altar_001` reverses C4 vs C5_CONTRACT to 34.3%. Synthesis-emergent: leave-one-persona-out cluster bootstrap should be a required diagnostic, not an appendix.

- **Does pre-registering anchor paraphrases shift the ranking?** Risk Analyst flagged — rubric robustness check is partly about whether the construct survives harmless wording changes or is anchored-language-dependent.

- **What's the threshold for "good enough" judge agreement to support headline claims?** Synthesis-emergent. Scalar Pearson > 0.30 isn't the right bar; ICC, Krippendorff α, severity-offset analysis, and human-human agreement are needed before model-judge agreement levels are interpretable.

## 4. Final recommendation

**Publish v0.2 as a methodology pilot, but only after same-data hardening lands. Spend the first new Opus budget on AB/BA rejudging, not on new conditions.**

### Decision-ready sequence

**Phase 1 — Same-data hardening (must complete before any curated report)**

1. Relabel every pairwise table with explicit filter / n / judge mix / author scope. Produce three side-by-side tables: all-judge same-author, cross-provider same-author, same-provider same-author.
2. Downgrade headline #4 ("C5_CONTRACT outperforms both C3 and C4") to: "C5_CONTRACT directionally outperforms C4 on average; the C3 comparison straddles 0.500 in cluster bootstrap and reverses for GPT-5.4 and in epistemic-uncertainty/shame scenario families."
3. Footnote headline #5 (C4 > C5): "based on GPT-5.4 + GPT-5.5 judges only; Opus pairwise records pending."
4. Promote scenario-family heterogeneity and per-judge stratification from appendix to primary results. Required diagnostic: family × pair forest plot with cluster-bootstrap CIs.
5. Compute leave-one-persona-out cluster bootstrap for all C5_CONTRACT edges. Add to robustness table.
6. Compute matched within-cell scalar deltas (persona × scenario × author × judge); aggregate paired deltas with cluster bootstrap. Replace pooled scalar means in headline blocks.
7. Fit one hierarchical logistic model on pairwise wins: condition pair, judge, author, persona, family, response length, profile length, A/B position. Use as decomposition, not p-value engine.
8. Replace red-flag → pairwise-loss correlation with independent / left-out-judge flag predictors. The same-judge version is tautological.
9. Downweight `profile_fit` dimension in headlines (already in revision brief; enforce it).

**Phase 2 — AB/BA rejudging (cheapest decisive new experiment)**

Run 400-800 swapped-order pairs prioritizing C4 vs C1_padded, C4 vs C5, C5_CONTRACT vs C3/C4/C5, and C4 vs C4_shuffled. Use Opus on GPT-authored outputs and GPT judges on Opus-authored outputs. Fits comfortably in the 1,000-2,000 Opus budget. **This is the load-bearing experiment**: if it flips, the entire C5_CONTRACT story needs revision before v3.

**Phase 3 — Conditional on AB/BA passing**

Run C5_NONPUBLIC (+ optional C5_NONPUBLIC_CONTRACT) on a small PS slice: 2 PS personas × 20 scenarios × 2 authors. Match length/format to C5; author packets from same latent records. This isolates public-anchor recognizability from source-packet form — the only clean way to make a source-packet causal claim survive review.

In parallel: 40-60 pairwise items for human calibration (2-3 blinded raters), balanced across the headline edges. This is judge calibration, not real-user validation — frame it that way.

**Defer to v3**

- C5_CONTRACT_SHORT length-matched variant
- Paraphrased-anchor rubric robustness
- Adversarial profile tests (stale, misleading, flattering, identity-locking, "write in my voice")
- Non-English / non-WEIRD scenario expansion
- Shadow-mode / retrospective trace validation with real users (this is the v3 construct-validity centerpiece, not a sidebar)

### Confidence

- **High confidence**: C4 > C1_padded and C5_CONTRACT > C5 are real. Behavioral contracts are the reliable unit; uncontracted C5 is fragile. Publish these.
- **Medium confidence**: C5_CONTRACT > C4 on average across PI personas. Heterogeneous; report as such.
- **Low confidence**: C5_CONTRACT > C3, "source packets add value when subordinated to contracts," and any causal mechanism claim. These should not survive Phase 1 in their current wording.
- **Low confidence on timeline**: depends on whether AB/BA can run inside the next quota cycle and whether C5_NONPUBLIC authoring is gated on additional persona-source work.

### Conditions that would change the recommendation

- AB/BA shows material order bias on C5_CONTRACT edges → C5_CONTRACT story needs full rework before v3; do not publish even the softened version without an "order-sensitivity caveat."
- Cross-provider backfill reverses any same-provider-heavy pair → expand relabeling into a "what we cannot yet claim" section.
- Human raters disagree systematically with model judges on the headline edges → judge-pluralism becomes the v3 priority, not source-packet decomposition.
- C5_NONPUBLIC behaves like C5 (not like C3/C4) → the source-packet effect is partly public-anchor recognizability, not source form. Reframe.

### Cheapest decisive next action

**Run AB/BA on the C5_CONTRACT pairwise edges first.** It costs ~200-400 Opus calls plus codex coverage, tests the single most consequential design fragility, and gates whether Phase 3 experiments are worth running. Do this before C5_NONPUBLIC, before human calibration, before any new condition.

## 5. Attribution map

| Claim | Contributing agent(s) |
|---|---|
| Cross-provider label mismatch is the critical bug | unanimous (Empiricist verified via raw join) |
| C4 > C1_padded and C5_CONTRACT > C5 are robust | unanimous |
| C5_CONTRACT > C3 straddles 0.500 in CI | risk-analyst, skeptic, empiricist (per metrics:1876) |
| C5_CONTRACT vs C3 reverses for GPT-5.4 | empiricist, architect, skeptic |
| Profile-char length confound (C5_CONTRACT 7,433 vs C4 3,689) | unanimous (per metrics:3565) |
| C4 > C5 is OpenAI-judge-only (Opus n=0) | risk-analyst, empiricist (per metrics:3353) |
| Position bias is structurally present, unaudited | skeptic, architect, risk-analyst, empiricist |
| Red-flag κ ~0.231 → flag conclusions judge-fragile | risk-analyst, architect, empiricist |
| Scenario-family heterogeneity (epistemic_uncertainty reversal) | unanimous |
| One PI persona reverses C4 vs C5_CONTRACT | skeptic (raw join), architect |
| AB/BA is cheapest decisive next experiment | skeptic, empiricist |
| C5_NONPUBLIC is the missing isolation experiment | architect, risk-analyst, skeptic, empiricist |
| Analysis-first hardening before new conditions | architect (primary), risk-analyst |
| Construct/predictive validity is v3's central exposure | unanimous |
| WEIRD generalization risk | skeptic |
| Adversarial profile patterns deferred to v3 | architect (per kickstart:1789,1855) |
| Leave-one-persona-out as required diagnostic | synthesis-emergent (from skeptic + empiricist observations) |
| Hierarchical logistic decomposition over pooled bootstrap | skeptic (primary), architect |
| Downweight `profile_fit` dimension | architect (per revision brief:202) |
| Reverse causality: profiles cause good answers or just judgeable ones | empiricist |
