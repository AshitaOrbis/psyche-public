## 1. Consensus

- **v0.2 is writable without new generation.** All four agents converge: Phase 0 + Phase 1 did the substantive repair work; the remaining work is analyzer/report hygiene, not more data collection. `[unanimous]`
- **AB/BA must be the primary pairwise evidence channel.** Original all-judge headline tables should not lead the report. `[unanimous]`
- **C5_CONTRACT > C5 is a package claim, not a mechanism claim.** Allowed wording: "contract-first source-packet package beats uncontracted source packet." Forbidden until v0.3: "contract mechanism," "public-anchor value," "profile-specificity proven." `[unanimous]`
- **C5_CONTRACT vs C3 and vs C4 collapse to "no significant condition preference."** The original headlines must be removed; controlled estimates are 49.9% [44.3, 55.7] and 51.8% [46.0, 57.5]. `[unanimous]`
- **The cross-provider Phase 0 C3 vs C5_CONTRACT result must be reframed as a judge/position interaction diagnostic, not a rival positive verdict.** It belongs in the "why AB/BA was necessary" section, not in headlines or abstract. `[unanimous]`
- **Slot-B bias is a major standalone methodology finding worth publishing.** All four endorse it as a result, not an embarrassment. `[unanimous]`
- **Stale-text cleanup is mandatory before prose finalization.** Specifically: any sentence implying C4_shuffled wins controlled judging, "PAE empirically resolved," "C5_CONTRACT outperforms C3/C4," and unqualified "tri-model cross-provider." `[architect, risk-analyst, empiricist]` (skeptic implicit)
- **Per-claim scope labels are required everywhere** (persona subset, judge mix, author scope, same/cross-provider, n). `[unanimous]`
- **A claim ledger table is the right report architecture** — claim, controlled estimate, scope, scalar alignment, allowed wording. `[architect formalized; skeptic, risk-analyst, empiricist endorsed]`
- **Tier 1 robust findings:** C0 dominated, C4 > C1_padded, C4 > C5, C5_CONTRACT > C5, C4 > C4_shuffled (with the empiricist's caveat that this last is modest and the skeptic's preference to call it "Tier 1.5"). `[unanimous on the list; calibrated disagreement on C4 > C4_shuffled — see §2]`
- **v0.3 priority queue** (largely matches round-1 reviewer convergence): C_GENERIC_CONTRACT and C4_WRONG_PROFILE first (decides personalization vs generic-good-prompting), then C5_NONPUBLIC/C5_NONPUBLIC_CONTRACT, then component/length ablations of the contract itself, then paraphrased rubric, then small human calibration set. `[unanimous]`

## 2. Disagreements

### Disagreement A: Is unclustered Wilson AB/BA a publication blocker?

- **Skeptic's case:** The analyzer itself labels the Wilson interval as "rough." Repeated judges within persona-scenario-author cells make these records non-independent. Publishing rough intervals as final, publication-grade uncertainty — especially for the modest C4 > C4_shuffled finding — is a publication-facing risk that should be fixed *before* the curated report, not after.
- **Empiricist's case:** Ran the matched-pair bootstrap directly on current AB/BA rows. All six headline verdicts preserved: C1_padded vs C4 0.623 [0.577, 0.669], C3 vs C5_CONTRACT 0.499 [0.452, 0.546], C4 vs C4_shuffled 0.578 [0.531, 0.623], C4 vs C5 0.681 [0.613, 0.747], C4 vs C5_CONTRACT 0.518 [0.471, 0.566], C5 vs C5_CONTRACT 0.677 [0.631, 0.722]. The matched estimator should be canonicalized but does not overturn tier assignment.
- **Adjudication:** Empiricist wins on facts; skeptic wins on hygiene. The bootstrap already shows the verdicts survive, so this is not a *substantive* blocker — but it is a *publication* blocker in the narrow sense that the curated report should display the matched/clustered CIs rather than the Wilson ones it currently reports. Architect and risk-analyst both endorse this as a required quick fix. **Action:** canonicalize the matched-pair bootstrap CIs in the analyzer; report those; this takes hours, not days.

### Disagreement B: How should C4 > C4_shuffled be reported?

- **Skeptic's case:** 57.8% [52.3, 63.1] is positive but modest, with a Phase 0 length warning still in play. Calling it Tier 1 alongside the ~67–69% effects equates very different effect sizes. Prefers "Tier 1.5" or "survives with small margin."
- **Architect / Empiricist's case:** It survives AB/BA, it's a sign-corrected Phase 0 result, the matched bootstrap holds at 0.578 [0.531, 0.623], and it is the load-bearing evidence that *order* (not just contract content) matters within C4-family. Demoting it weakens the ordering-effect story unnecessarily.
- **Adjudication:** Skeptic has the cleaner reader-facing point. A claim ledger with effect-size column resolves this without semantic argument: list it as Tier 1, tag effect size as "modest" or print the CI alongside the C4 > C5 CI so the reader sees the gap directly. No need to invent a Tier 1.5 bucket; just don't let "Tier 1" launder a 7.8pp effect into peer status with a 17–19pp effect.

### Disagreement C: Scope of the slot-B bias claim

- **Skeptic's case:** Publishable as "this corpus, prompt, judge set, pairwise protocol directly measured large judge-family-specific position bias and uncounterbalanced margins were misleading." Do not imply a universal 15–17pp law.
- **Empiricist / Architect / Risk-Analyst's case:** Effectively the same wording. Empiricist explicitly notes the result agrees with the general LLM-as-judge position-bias literature but should not be universalized.
- **Adjudication:** Not a real disagreement — convergent. Flagging it because the skeptic's wording is the cleanest and should be adopted verbatim in the methodology section.

### Disagreement D: How to handle the C3 vs C5_CONTRACT cross-provider Phase 0 result

- **Architect / Risk-Analyst's case:** Treat as Phase 0 diagnostic only. The all-judge AB/BA at 49.9% is the verdict; cross-provider stratified is interaction noise.
- **Empiricist sharpening:** Ran cross-provider AB/BA directly — high-condition win is only 0.543 [0.466, 0.622]. So even within the cross-provider stratum, AB/BA collapses the earlier signal. This makes the "diagnostic, not verdict" framing not just a reporting choice but an empirical finding.
- **Adjudication:** No genuine disagreement; empiricist's direct check strengthens the others' position. The report should cite the cross-provider AB/BA collapse as the reason cross-provider Phase 0 is superseded — closes a loop that would otherwise look like a reviewer judgment call.

## 3. Open questions

- **Does Opus AB/BA on C4 vs C5 change the scope label?** Currently PI-only, OpenAI-judge-scoped. Architect flagged as a <1-day check that could broaden the claim. Empiricist's bootstrap covers OpenAI scope only.
- **Does red-flag-conditioned pairwise analysis collapse the surviving wins?** If so, the report should say "reduces judged failure modes" rather than broader "quality improvement." (architect)
- **Do scenario families contain enough genuinely personalization-requiring tasks, or were they written in ways that reward profile-legibility per se?** This is a benchmark-construction validity question that v0.3 should not ignore. (risk-analyst, skeptic — synthesis-emergent in the form that the v0.2 corpus may have been authored partly profile-aware)
- **Component attribution within the contract itself** (generic challenge language vs anti-mimicry vs scenario hints vs ordering vs packet length) — even C_GENERIC_CONTRACT only answers generic-vs-specific, not which clause does the work. (skeptic — fresh angle round 1 missed)
- **Stale/incorrect profile tests:** real deployments will carry outdated or partially wrong user models. (empiricist — fresh angle)
- **Profile compression and freshness:** real deployments will not carry 7k-character packets forever. (skeptic — fresh angle)
- **Position-bias-resistant judge protocol as a future default,** rather than treating AB/BA as a one-off correction. (architect — fresh angle)

## 4. Final recommendation

**Write the v0.2 curated report now, after a small, defined analyzer/report hygiene pass. Do not run new generation.**

Confidence: **high** on the direction (proceed, not pause for v0.3); **high** on the Tier 1 controlled verdicts surviving (empiricist's matched bootstrap already confirms); **medium-high** on the appropriate prose tier for C4 > C4_shuffled until the matched estimator is canonicalized in the analyzer; **low** on any mechanism attribution for C5_CONTRACT, which all four agents agree must wait for v0.3.

### Conditions that would change the recommendation

Any of these flips the call from "publish with hygiene pass" to "block and investigate":
- Clustered/matched AB/BA materially widens C5_CONTRACT > C5 or C4 > C1_padded to cross 0.5 (unlikely given empiricist's bootstrap).
- Complete-case scalar analysis reverses C5_CONTRACT > C5.
- Persona/family forest table shows any Tier 1 claim is driven by a single stratum.
- Red-flag-conditioned audit shows the surviving wins are essentially failure-flag avoidance.
- Stale-text scan surfaces a contradiction the curated report inherits.

### Required quick fixes (before prose finalization)

These are not optional; they are the hygiene pass that makes the report defensible. Order is roughly cost-benefit:

1. **Canonicalize matched-pair / clustered AB/BA bootstrap CIs** in the analyzer. Replace Wilson intervals in the displayed table. (Resolves Disagreement A directly.)
2. **Build the claim ledger table:** claim | controlled estimate | matched CI | AB/BA status | judge scope | persona scope | author scope | scalar alignment | length-audit result | allowed wording | tier. This is the central artifact; everything else hangs off it.
3. **Judge-stratified AB/BA table** (pair × judge family), showing slot-B advantage and per-stratum controlled preference. Detects single-stratum artifacts before reviewers do.
4. **Per-cell consistency / slot-flip / either-tie rates** by judge family and pair.
5. **Stale-text lint pass:** strike "C5_CONTRACT outperforms C3/C4," "PAE empirically resolved," unqualified "cross-provider," any sentence implying C4_shuffled wins controlled judging.
6. **Supersession table:** Phase 0 claims that Phase 1 supersedes, with one-line resolution each. Prevents readers from reconciling contradictory files themselves.
7. **Complete-case scalar reconciliation** beside every headline (only 67.5% of outputs have all three scalar judges; mark pooled vs complete-case).
8. **Cross-provider C3 vs C5_CONTRACT AB/BA strata** (empiricist already ran this — 0.543 [0.466, 0.622]). Publish it as the empirical reason the Phase 0 cross-provider result is demoted.

### Optional <1-day audits (do if time permits, in priority order)

1. **C0 vs C4 AB/BA or position-bias sensitivity bound** — C0 dominated is the only Tier 1-style result without direct position control. (empiricist)
2. **Opus AB/BA on existing C4 vs C5 outputs** — broadens the scope label if it confirms; if it reverses, the report must scope down. (architect)
3. **Red-flag-conditioned pairwise audit** — sharpens C5_CONTRACT > C5 wording from "quality improvement" toward "reduces judged failure modes" if appropriate. (architect)

### Headline structure for the v0.2 report

Order the report this way:
1. **Tier 1 controlled findings** (with effect-size differentiation): C0 dominated; C4 > C1_padded; C4 > C5 (PI-only, OpenAI-judge-scoped); C5_CONTRACT > C5 (package claim only); C4 > C4_shuffled (modest, post-sign-correction).
2. **Explicit demotions:** C5_CONTRACT vs C3 and vs C4 collapsed to "no significant condition preference under counterbalancing."
3. **Methodology contribution:** measured judge-family-specific slot-B bias, scoped to this corpus/protocol.
4. **Why AB/BA was necessary** (Phase 0 diagnostic context, including cross-provider C3 vs C5_CONTRACT supersession).
5. **Scope, limitations, v0.3 roadmap.**

### v0.3 investment priorities

Within the ~1,000–2,000 Opus draws + larger codex budget:

1. **C_GENERIC_CONTRACT + C4_WRONG_PROFILE** — decides whether PsycheEval measures personalization or generic high-quality behavioral prompting. Highest single-experiment information value. (round-1 convergent + all four agents)
2. **C5_NONPUBLIC and C5_NONPUBLIC_CONTRACT** — isolates public-anchor contribution.
3. **C5_CONTRACT_SHORT + contract component ablations** (ordering, anti-mimicry, scenario hints, packet summarization) — only this distinguishes "contract mechanism" from "longer well-structured packet works." (skeptic — round-1 underweighted)
4. **Stale/incorrect/contradictory profile conditions** — deployment realism. (empiricist — round-1 missed)
5. **Profile compression and freshness tests.** (skeptic — round-1 missed)
6. **Scenario-authoring controls:** future scenarios authored blind to profile theory, to prevent benchmark contamination. (skeptic/risk-analyst — round-1 underweighted)
7. **Behavioral feature labeling** (challenge, calibration, repair, boundary-setting, escalation avoidance, profile name-dropping) tied to both scalar and pairwise wins — moves from judge preference to construct mediation. (skeptic — fresh angle)
8. **Small human calibration set** focused on disagreement-heavy and safety-relevant pairs. (round-1 convergent)
9. **Paraphrased rubric judging.** (round-1 convergent)

### Cheapest decisive next action

**Canonicalize the matched-pair bootstrap CIs in the analyzer and run the stale-text lint** — both can be done in hours, both are prerequisites for prose finalization, and together they resolve the only remaining disagreement (A) and the highest-probability publication failure mode (stale Phase 0 language).

## 5. Attribution map

| Claim | Contributing agent(s) |
|---|---|
| v0.2 is writable without new generation | unanimous |
| AB/BA must be primary pairwise evidence | unanimous |
| C5_CONTRACT > C5 is package, not mechanism | unanimous |
| C5_CONTRACT vs C3/C4 collapse to no preference | unanimous |
| Cross-provider Phase 0 reframed as diagnostic | unanimous |
| Slot-B bias as standalone methodology finding | unanimous |
| Claim ledger as report architecture | architect (formalized); skeptic, risk-analyst, empiricist endorsed |
| Matched-pair bootstrap preserves all six verdicts | empiricist (directly ran) |
| Cross-provider AB/BA C3 vs C5_CONTRACT = 0.543 [0.466, 0.622] | empiricist (directly ran) |
| Wilson CI is a publication-hygiene blocker, not substantive | skeptic raised; architect and risk-analyst endorsed; empiricist resolved empirically |
| C4 > C4_shuffled should be tagged "modest" not equated with 17pp effects | skeptic |
| Slot-B claim should be scoped to corpus/protocol, not universalized | skeptic |
| Stale-text lint mandatory before prose | architect, risk-analyst, empiricist |
| Supersession table needed | risk-analyst, empiricist |
| Opus AB/BA on C4 vs C5 as broadening check | architect |
| Red-flag-conditioned pairwise audit | architect |
| C0 vs C4 sensitivity bound | empiricist |
| Judge-stratified AB/BA table | risk-analyst, skeptic, architect |
| Complete-case scalar robustness | skeptic, risk-analyst, empiricist |
| Persona/family forest tables for Tier 1 | risk-analyst |
| Contract component ablation (round 1 missed) | skeptic |
| Stale/incorrect profile tests (round 1 missed) | empiricist |
| Profile compression/freshness (round 1 missed) | skeptic |
| Scenario-authoring blind controls (round 1 underweighted) | skeptic, risk-analyst |
| Behavioral feature mediation analysis | skeptic |
| Position-bias-resistant judge protocol as default | architect |
| C_GENERIC_CONTRACT + C4_WRONG_PROFILE as top v0.3 priority | round-1 convergent + all four agents |
| Mechanism overclaim is highest residual publication risk | risk-analyst (formalized), architect, skeptic |
