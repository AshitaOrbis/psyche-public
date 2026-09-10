# PsycheEval v0.2 — Synthesis

## 1. Consensus

The four agents converged tightly. Below are the points where 3+ endorsed and dissent was weak or absent.

- **C4 > C1_padded is established within scope.** Behavioral contract advantage is not a length artifact. Bootstrap CI [0.613, 0.744] does not straddle 0.5. `[unanimous]`
- **C5_CONTRACT > C5 is the cleanest, most defensible mechanism claim.** All four treat it as the strongest established finding. Empiricist anchors with `pairwise.cluster_bootstrap_ci_same_author` giving C5 lo-win 0.2404 [0.1828, 0.3031]. `[unanimous]`
- **C5_CONTRACT > C3/C4 is NOT settled.** Heterogeneous by judge (GPT-5.4 prefers C3), persona (Slalom Altar reverses), scenario family (epistemic_uncertainty, shame_self_interpretation are weak/reversed), and length bucket. Should be demoted to "promising, conditional." `[unanimous]`
- **A/B position confound is publication-blocking.** C5_CONTRACT is overwhelmingly in side B against C3/C4/C5; side B wins frequently. Counterbalanced rejudging of existing outputs is the single highest-leverage cheap experiment. `[unanimous]`
- **Coverage semantics need correction before publication.** Bundle says "same-author pairwise: 3,123 records" but raw join finds ~179 cross-author records mixed in, concentrated in C5_CONTRACT rows. "Tri-model" and "cross-provider" headline language must be scoped — full crossed judging is not what was run. `[skeptic, architect, risk-analyst, empiricist]`
- **Length confound for C5_CONTRACT remains unresolved.** Profile text ~7,433 chars vs C4 at 3,689; length buckets show strong gradients. Required: length-adjusted regression or matched-length C5_CONTRACT subset. `[unanimous]`
- **The query's "PAE empirically resolved" framing overclaims.** v0.2 shows source-packet-with-contract beats source-packet-without-contract; it does not isolate public-anchor, packet form, profile length, generic-contract uplift, or judge/rubric recognition. `[unanimous]`
- **A generic non-personalized behavioral contract (`C_GENERIC_CONTRACT`) is the single most diagnostic new condition** — directly tests whether profile specificity matters or whether the gain is "more explicit good-assistant instructions." `[skeptic, architect, risk-analyst, empiricist]`
- **Rubric-halo risk is real.** C3/C4/C5_CONTRACT all encode the virtues the anchored rubric scores (calibrated_challenge, anti_sycophancy, agency, etc.). Paraphrased-anchor robustness check is cheap and necessary. `[unanimous]`
- **Real-user predictive validity is the largest v3 exposure.** Synthetic judges on in-distribution scenarios cannot establish that real users benefit. `[unanimous]`
- **Pending native analyses (scenario-family aggregation, red-flag×pairwise correlation) must be finished before mechanism language is published.** Empiricist's raw check already shows red-flag asymmetry predicts ~98% of decisive losses — the pairwise channel may partly be a red-flag detector. `[empiricist, architect, risk-analyst]`

## 2. Disagreements

The agents disagreed less than expected — most divergence is in emphasis, not direction. Three genuine substantive splits:

### Disagreement 1: How firmly to treat C5_CONTRACT > C5 as a "mechanism" finding

- **Skeptic's strongest argument:** C5_CONTRACT is not "C5 + contract" causally. It is a longer, anti-mimicry, contract-first prompt package that also better matches the judge rubric. Calling C5_CONTRACT > C5 a mechanism win for "contracts repair source packets" overclaims because contract language, anti-mimicry salience, profile length, instruction order, and rubric-lexical-overlap all moved together. Without `C5_CONTRACT_SHORT`, `C_GENERIC_CONTRACT`, and paraphrased anchors, "the C5_CONTRACT package works" is what's licensed.
- **Empiricist's strongest argument:** The effect size is large (lo-win 0.2404, CI well clear of 0.5), survives in the cross-provider same-author subset (69.3%), and pure-artifact explanations would have to be doing remarkable work. The effect is real enough to treat as established within scope.
- **Adjudication:** Both are right at different levels of claim. The Empiricist's framing is correct for the **descriptive** statement ("the C5_CONTRACT package beats the C5 package"); the Skeptic's framing is correct for the **causal** statement ("contracts are the active ingredient"). The Architect's tier system handles this cleanly: Tier 1 wording is "adding the contract package to a source packet substantially improves the C5 package under this evaluation"; mechanism attribution sits in Tier 2 pending `C5_CONTRACT_SHORT` and `C_GENERIC_CONTRACT`. **Use Tier 1 phrasing in the v0.2 report.**

### Disagreement 2: Whether C5_CONTRACT is "always" side B

- **Skeptic's framing:** Position confound is severe; C5_CONTRACT is overwhelmingly side B in key comparisons.
- **Empiricist's correction:** In raw pairwise, C5_CONTRACT does appear as A in a small reversed subset; "always" is technically wrong but the practical critique survives.
- **Adjudication:** Empiricist is factually more precise; the operational conclusion is identical. Report should say "highly imbalanced toward side B" not "always side B." Counterbalanced rejudging is still required.

### Disagreement 3: How aggressively to constrain the v0.2 publication

- **Skeptic + Risk-Analyst:** Several findings should be downgraded ("strong candidate repair" not "PAE resolved"); coverage language must be corrected; counterbalanced rejudging is publication-blocking.
- **Architect + Empiricist:** A tiered split (publishable now / publishable after decomposition / v3 questions) lets v0.2 ship most findings with caveats while staging the audits.
- **Adjudication:** This isn't really a disagreement — Architect/Empiricist's tier approach implements Skeptic/Risk-Analyst's caveats. The cleanest resolution: **publish Tier 1 now with corrected coverage language, hold Tier 2 claims until decomposition + swapped-position rejudge complete.** Do not let the report ship with "PAE resolved" framing or unqualified "tri-model cross-provider" language.

## 3. Open questions

Surfaced by the agents or emerging from the synthesis itself:

- **Does C5_CONTRACT's edge survive swapped-position rejudging?** [risk-analyst, skeptic, empiricist] — *the* load-bearing empirical question; until answered, every condition-on-higher-side pairwise margin is suspect.
- **Does length adjustment absorb the C5_CONTRACT advantage?** [architect, empiricist, risk-analyst]
- **Does a generic non-personalized contract (`C_GENERIC_CONTRACT`) match C5_CONTRACT?** [skeptic, architect, risk-analyst] — if yes, profile specificity claims collapse.
- **Does paraphrasing the anchored rubric move winners?** [skeptic, risk-analyst, architect] — direct test of rubric-lexical-overlap halo.
- **Is the pairwise channel mostly a red-flag detector?** [empiricist] — raw check shows 98% loss rate for asymmetric flag cases; if so, pairwise carries less independent signal than the report implies. *Synthesis-emergent corollary:* what is the C5_CONTRACT advantage *after* conditioning on red-flag asymmetry?
- **Do human raters agree with model judges on the disputed C3/C4/C5_CONTRACT edges?** [unanimous] — 30-60 pair sample, oversample disagreement-heavy cases.
- **Does the C4 > C1_padded result survive a `C_GENERIC_CONTRACT` ablation?** [synthesis-emergent] — could the "behavioral contract beats length" claim itself be generic-instruction-uplift?
- **Real-user validity:** do profiles improve outcomes for real users with their own profiles, or only satisfy synthetic judges? [unanimous]
- **Wrong-profile / shuffled-profile control:** does any plausible psychological contract help, or does the matching matter? [skeptic]
- **What rule decides when model-judge consensus is sufficient vs. when human calibration is required?** [architect]
- **Why is C4 vs C4_shuffled near-null?** [synthesis-emergent] — if coherent ordering doesn't matter, what *is* the active ingredient in C4's advantage over C1_padded?

## 4. Final recommendation

**Decision-ready guidance, in execution order:**

### Before any new generation — analysis and audit (Phase A, ~1 week of compute, mostly free)

1. **Produce a coverage and estimand manifest** from `runs/2026-04-26_v02_hard_codex_only/` — counts by judge × author × condition × pair × A/B side × same-author/cross-author/cross-provider. Correct bundle language wherever "same-author" or "tri-model" overstates the analytic denominator.
2. **A/B position audit:** condition-by-side table, winner-by-side table, sensitivity excluding non-counterbalanced rows.
3. **Per-judge, per-author, per-PI-persona leave-one-out** for every C5_CONTRACT headline. Flag any claim that flips on removal of one judge/author/persona/family.
4. **Length-adjusted models:** mixed/logistic regression with response wordcount delta + profile length as covariates; matched-length subset analysis.
5. **Scalar-pairwise reconciliation by cell.** Empiricist's spot check (C4 7.963 vs C5_CONTRACT 7.902 in PI-only core scalar) already shows a mismatch with pairwise — must be reported, not buried.
6. **Finish red-flag × pairwise correlation and scenario-family heterogeneity** — the two pending analyses promised in `docs/v0_2_plan_extended_2026-05-05.md` lines 236-242.
7. **Rubric-lexical-overlap audit:** compute overlap between profile/contract text and anchored rubric language.

### Quota spend — discriminating experiments, not volume (Phase B, ~1,000-2,000 Opus + larger Codex)

Priority order:

1. **Counterbalanced rejudging of existing key pairs** (C3/C4/C5 vs C5_CONTRACT, A/B swapped, across all three judges where affordable). Uses existing outputs; directly attacks the largest pairwise threat. *This is the cheapest decisive experiment.*
2. **`C_GENERIC_CONTRACT`** — non-personalized behavioral contract with the same anti-sycophancy / agency / uncertainty / repair instructions. Cleanest test of personalization specificity.
3. **`C5_NONPUBLIC`** — source-packet-style narrative for PS personas. Isolates public-anchor effect from source-packet form.
4. **`C5_CONTRACT_SHORT`** (or matched-length subset) — isolates prompt-length from contract content.
5. **Paraphrased-anchor robustness pass** on existing outputs.
6. **30-60 pair human calibration sample**, oversampling disagreement-heavy cases, C5_CONTRACT wins, and red-flag-asymmetric cases. Diagnostic, not validation.

Skip: broad all-vs-all C5_CONTRACT pairwise expansion. More volume on biased estimates produces more precise wrong answers.

### v0.2 report wording (Phase C, immediate)

- **Tier 1 (ship now with caveats):** C4 > C1_padded; C5_CONTRACT > C5; structure of v0.2 methodology improvements.
- **Tier 2 (hold until audits complete):** C5_CONTRACT > C3/C4; C4 > C5; "source packets add value"; "coherent structure does not significantly beat shuffled."
- **Strike or weaken:** "v0.1's PAE confound is empirically resolved in favor of absence of contract as dominant driver" → "v0.2 shows contract-first source-packet packages substantially repair the source-packet condition under this evaluation; mechanism isolation remains pending." Strike unqualified "tri-model" and "cross-provider" language; replace with specific coverage descriptions.

### v3 design priorities

In rank order: real-user predictive validity bridge; small factorial mechanism design (contract × public-anchor × packet form × length); judge pluralism rule + human calibration policy; profile-format generalization (Big Five, narrative, multilingual, cross-cultural); adversarial/misleading profile robustness; wrong-profile control.

### Confidence and conditions

**High confidence** on the audit-first sequencing and on the necessity of counterbalanced rejudging before mechanism claims publish. **Medium-high confidence** that current C5_CONTRACT > C3/C4 language overclaims and will partially attenuate under decomposition. **Medium confidence** that C5_CONTRACT > C5 will survive all audits (Skeptic's package-confound critique remains, but effect size is large enough that pure-artifact explanations are uphill). **Low confidence** in real-world predictive validity inference.

**Conditions that would change the recommendation:**
- If swapped-position rejudging reduces C5_CONTRACT wins by >5-8 points → downgrade pairwise headlines sharply, reframe as judge-position artifact.
- If `C_GENERIC_CONTRACT` matches C5_CONTRACT → reframe project from "profile personalization" to "explicit behavioral instructions"; profile-specificity claims need different evidence base.
- If length adjustment absorbs C5_CONTRACT effect → mechanism claim collapses to "verbose prompts win"; pivot to length-matched evaluation as v3 baseline.
- If one persona/judge/family carries the C5_CONTRACT > C3/C4 result on leave-one-out → reframe as "localized signal" not "general mechanism."
- If human raters disagree with model judges on disputed pairs → benchmark validity itself is in question; v3 must lead with human calibration.

### Cheapest decisive next action

**Counterbalanced rejudging of existing C3/C4/C5 vs C5_CONTRACT pairs with A/B swapped, stratified across all PI personas and all three judges.** No new generation; uses existing 1,680 outputs. Directly attacks the largest publication risk. Result is binary: either the headlines survive (raises confidence sharply) or they attenuate (requires Tier 2 wording everywhere). Estimated cost: well under 1,000 Opus draws if Opus is reserved for the most decision-relevant cells; Codex absorbs the rest.

## 5. Attribution map

| Claim | Contributing agent(s) |
|---|---|
| C4 > C1_padded is established within scope | empiricist (CI), unanimous |
| C5_CONTRACT > C5 is the cleanest headline | unanimous; empiricist anchors with metrics JSON |
| C5_CONTRACT > C3/C4 is heterogeneous & should be demoted | empiricist (per-judge GPT-5.4→C3), risk-analyst (LOO sensitivity), architect (Tier 2), skeptic |
| A/B position confound is publication-blocking | skeptic (originating), risk-analyst (severity escalation), empiricist (precise framing), architect |
| Coverage semantics need correction (3,123 "same-author" includes 179 cross-author) | risk-analyst (raw join), skeptic, empiricist |
| Length confound unresolved for C5_CONTRACT | empiricist (length buckets), architect (profile char counts), risk-analyst |
| Rubric-halo / lexical-overlap risk | skeptic (originating), risk-analyst, architect |
| `C_GENERIC_CONTRACT` is the most diagnostic new condition | skeptic (originating), unanimous endorsement |
| Counterbalanced rejudging = cheapest decisive experiment | unanimous; risk-analyst makes it operational gate |
| Pairwise channel may be partly a red-flag detector | empiricist (raw 98% asymmetric-flag loss rate) |
| Scalar-pairwise mismatch (C4 7.963 vs C5_CONTRACT 7.902 on PI core scalar) | empiricist |
| Tier 1 / Tier 2 / Tier 3 report split | architect (framework) |
| Failure-mode table with probability × impact × early-detection signals | risk-analyst |
| "PAE empirically resolved" overclaims | unanimous |
| Real-user predictive validity = largest v3 exposure | unanimous |
| Wrong-profile / shuffled-profile control | skeptic |
| Judge-pluralism rule for v3 | architect |
| C5_CONTRACT does appear as A in small reversed subset | empiricist (correcting skeptic's "always B") |
| Why is C4 vs C4_shuffled near-null? | synthesis-emergent |
| C_GENERIC_CONTRACT could undermine C4 > C1_padded too | synthesis-emergent |
| Conditional-on-red-flag-asymmetry C5_CONTRACT advantage | synthesis-emergent (from empiricist's flag finding) |
