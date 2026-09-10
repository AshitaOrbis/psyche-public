# PsycheEval v0.2 — Consolidated External Review

**Date**: 2026-05-15
**Status**: Decision-ready synthesis of three independent external reviews
**Scope**: Pre-publication critique of v0.2 tri-model methodology pilot

---

## Method

Three independent reviewers received the same bundle (`reports/reviews/2026-05-15_v0_2_review_bundle.md`) and the same three asks: (A) further analytical angles on existing data, (B) reasonably affordable additional experiments, (C) deeper v3 questions.

| Reviewer | Model(s) | Architecture | Source file |
|---|---|---|---|
| **ChatGPT Pro** | GPT-5.4 Pro | Single agent, extended reasoning | `2026-05-15_gpt-pro_v0_2_review.md` (31 KB, 18 / 9 / 14 sections) |
| **Codex Council** | 4× GPT-5.5 xhigh + Opus synth | Blind ensemble (skeptic / architect / risk-analyst / empiricist) | `2026-05-15_codex-council_v0_2_review.md` (15 KB) |
| **GPT Max** | 4× GPT-5.5 xhigh + Opus synth | Same 4 personas, HCOM-coordinated (peer drafts visible) | `2026-05-15_gpt-max_v0_2_review.md` (15.6 KB) |

Three reviews, two different LLM families, two different orchestration patterns. Convergence across all three is the strongest signal in this document. Divergence is annotated.

---

## 1. Convergent must-fix issues (publication-blocking)

The three reviews independently converged on five issues that must be addressed before any v0.2 artifact ships externally.

### 1.1 Bundle labeling defect — "tri-model cross-provider same-author" is not what was actually run

- **Codex Council** (top of consensus): "The bundle calls the n=320/n=288 pairwise table 'cross-provider, same-author' but the autogen scaffold and raw JSONL audit show those rows are all-judge same-author (or OpenAI-only for non-C5_CONTRACT edges). True cross-provider same-author is only 264 records and only covers the three C5_CONTRACT edges." `[unanimous, empiricist verified via raw join]`
- **GPT Max**: "Bundle says 'same-author pairwise: 3,123 records' but raw join finds ~179 cross-author records mixed in, concentrated in C5_CONTRACT rows." `[4/4 endorsed]`
- **GPT Pro**: "Pairwise counts are unbalanced: GPT-5.4 and GPT-5.5 each have about 1,294–1,295, while Opus has 534" — implies coverage claim needs scoping.

**Action**: Relabel every pairwise table with explicit `(filter, n, judge mix, author scope)`. Produce three side-by-side tables: all-judge same-author, cross-provider same-author, same-provider same-author. Strike unqualified "tri-model" and "cross-provider" language from headline blocks.

### 1.2 AB/BA position bias is unaudited and structurally present

C5_CONTRACT is overwhelmingly in slot B against C3/C4/C5; the well-documented position bias in LLM judges (Zheng et al. 2023, Shi et al. 2024) means *every* C5_CONTRACT pairwise margin is confounded with side effects until counterbalanced rejudging is run.

- **Codex Council**: "Position bias is unaudited and structurally present `[skeptic, architect, risk-analyst, empiricist]`. Cannot estimate from current data; flag as design limitation until AB/BA is run."
- **GPT Max**: "A/B position confound is publication-blocking. Counterbalanced rejudging of existing outputs is the single highest-leverage cheap experiment. `[unanimous]`"
- **GPT Pro**: Section B3 — "Rerun critical pairwise judgments with stronger judge protocol: Balanced left/right order. Explicit tie option. Paraphrased rubric anchors. Blind condition labels."

**This is the single highest-leverage cheap experiment all three reviewers identify.** See §3.1.

### 1.3 "C5_CONTRACT outperforms both C3 and C4" overphrased

The C3 comparison is fragile and judge-dependent:

- Bootstrap CI for C3 win rate against C5_CONTRACT is `[0.354, 0.500]` — touches 0.5 exactly. `[all three]`
- GPT-5.4 actively reverses it (C3 wins ~57% under GPT-5.4 judging). `[Codex Council, GPT Max]`
- Persona `pfi_slalom_altar_001` reverses C4 vs C5_CONTRACT to 34.3% (i.e., C4 wins on one of four PI personas). `[Codex Council skeptic raw join]`
- Scenario families `epistemic_uncertainty` and `shame_self_interpretation` reverse the direction. `[Codex Council unanimous, GPT Max unanimous]`

**Action**: Rewrite as: "C5_CONTRACT directionally outperforms C4 on average; the C3 comparison straddles 0.500 in cluster bootstrap and reverses for GPT-5.4 and in epistemic-uncertainty / shame scenario families." (Codex Council, verbatim)

### 1.4 Length confound for C5_CONTRACT unresolved

Profile char means: **C3 2,518 / C4 3,689 / C5 3,884 / C5_CONTRACT 7,433.** C5_CONTRACT is ~2× the length of C4 by construction. `[all three]`

- **Codex Council**: "Until length and order are controlled, the source-packet causal claim is confounded."
- **GPT Max**: "Length buckets show strong gradients. Required: length-adjusted regression or matched-length C5_CONTRACT subset."
- **GPT Pro**: Section A7 (output-length and stylometric sensitivity) + B6 (length-controlled generation rerun) + B5 (`C5_CONTRACT_LENGTH_MATCHED_TO_C4` variant).

**Action**: Mixed-effects logistic regression with response-wordcount + profile length as covariates (analysis-only, cheap). Long-term: a length-matched generation pass (see §3.2.6).

### 1.5 "PAE empirically resolved" is an overclaim

All three reviewers flag this verbatim or near-verbatim:

- **GPT Max**: "The query's 'PAE empirically resolved' framing overclaims. v0.2 shows source-packet-with-contract beats source-packet-without-contract; it does not isolate public-anchor, packet form, profile length, generic-contract uplift, or judge/rubric recognition. `[unanimous]`"
- **GPT Pro**: "v0.2 shows that adding a contract to the public-anchor source packet dramatically improves C5. It does not yet isolate public anchoring, source-packet prose form, evidence richness, ordering, anti-mimicry language, or output-length effects."
- **Codex Council**: "'Source packets add value when subordinated to contracts' is not yet earned. C5_CONTRACT changes 5+ things at once vs C3/C4 (source packet, contract, prompt order, anti-mimicry, profile length)."

**Action**: Replace "v0.1 PAE confound is empirically resolved in favor of absence of contract as dominant driver" with: "v0.2 shows contract-first source-packet packages substantially repair the source-packet condition under this evaluation; mechanism isolation remains pending" (Codex Council). Restrict mechanism language to Tier 2 (see §6).

---

## 2. New finding from review process — scalar–pairwise reconciliation gap

GPT Pro surfaces a finding that neither v0.2 analysis nor the bundle flagged:

> "In the PI scalar table, **C3 beats C5_CONTRACT on every listed dimension.** C4 also beats or ties C5_CONTRACT on many dimensions. That means the 'source packets add value when subordinated to contracts' claim is currently a **pairwise-judge preference claim, not yet an anchored-rubric performance claim**." (GPT Pro §1)

Codex Council independently noticed: "Empiricist's spot check (C4 7.963 vs C5_CONTRACT 7.902 in PI-only core scalar) already shows a mismatch with pairwise — must be reported, not buried."

**This is the most consequential analytical surprise from the review pass.** The scalar means in bundle §5 (where C3 / C4 ≥ C5_CONTRACT on most dimensions) directly contradict the pairwise headlines. Possible explanations:

- Pairwise judges use a different (holistic, comparative) criterion than the anchored scalar rubric.
- The anchored rubric is doing the work of demoting C5_CONTRACT that pairwise judging is missing.
- Position bias or verbosity preference contaminates pairwise.

Either way, **the v0.2 report cannot ship a "C5_CONTRACT > C3/C4" headline without addressing this reconciliation**. GPT Pro's recommended language:

> "Holistic pairwise judges often prefer C5_CONTRACT, but anchored scalar dimensions do not yet show consistent superiority over C3/C4."

---

## 3. Convergent recommendations

### 3.1 Same-data analyses to run before publication (free / cheap, all on existing 1,680 outputs + 3,949 + 3,123 records)

| # | Analysis | Reviewer endorsement | Estimated effort |
|---|---|---|---|
| 1 | **Scalar–pairwise reconciliation by cell** (the GPT Pro / Codex finding above) | GPT Pro origin, Codex endorsed | 1 day Python |
| 2 | **Per-judge stratification** of every headline (especially C5_CONTRACT vs {C3, C4}) | All three | 1 day |
| 3 | **Per-author stratification** (GPT-5.4 / GPT-5.5 / Opus authoring × condition) | All three | 1 day |
| 4 | **Leave-one-persona-out fragility** for all C5_CONTRACT edges | All three | 1 day |
| 5 | **Leave-one-judge-out**, **leave-one-family-out** | GPT Pro A5, Codex | 1 day |
| 6 | **Scenario-family heterogeneity** promoted from appendix to primary (forest plot) | All three | 1 day |
| 7 | **Hierarchical logistic model** on pairwise wins with condition pair × judge × author × persona × family × response length × profile length × A/B position | Codex Council §4-Phase-1.7, GPT Pro A6 | 2 days |
| 8 | **Red-flag predictiveness audit** — replace within-judge red-flag→loss correlation (tautological) with independent / left-out-judge flag predictors | Codex Council, GPT Pro A13, GPT Max | 1 day |
| 9 | **Rubric-lexical-overlap audit** — compute overlap between profile/contract text and anchored rubric language | Codex Council, GPT Max, GPT Pro implied via A16 | 1/2 day |
| 10 | **Equal-weighted aggregation** (macro over judges, authors, personas, families) vs micro-pooled | GPT Pro A2, Codex Council | 1/2 day |
| 11 | **Missingness audit** — table of scalar/pairwise records by condition × persona × author × judge × family; complete-case scalar subset | GPT Pro A18 | 1/2 day |
| 12 | **A/B side audit** — condition-by-side table, winner-by-side table, sensitivity excluding non-counterbalanced rows | GPT Max §4-Phase-A, GPT Pro A8 | 1/2 day |
| 13 | **Downweight `profile_fit` dimension** in headline blocks (already in revision brief; enforce) | Codex Council §4 | 1/4 day |

**All of the above runs on existing data, no new generation.** Total: ~10–14 days of focused analysis. This entire block is gating publication.

### 3.2 New experiments — affordable, ranked by reviewer consensus

#### Rank 1: AB/BA counterbalanced rejudging `[all three: "cheapest decisive"]`

Existing 1,680 outputs, swapped-order pairs, prioritizing C4 vs C1_padded, C4 vs C5, C5_CONTRACT vs C3/C4/C5, and C4 vs C4_shuffled.

- **Codex Council**: 400–800 swapped-order pairs; "use Opus on GPT-authored outputs and GPT judges on Opus-authored outputs."
- **GPT Max**: "Counterbalanced rejudging of existing key pairs (A/B swapped, across all three judges where affordable). *This is the cheapest decisive experiment.*"
- **GPT Pro**: §B3 — also adds "explicit tie option, blind condition labels, instruction to ignore verbosity unless it improves substance."

**Cost**: ~200–800 Opus calls + larger Codex pass. **Gate**: if AB/BA flips any headline, the C5_CONTRACT story needs full rework before any v3 spend.

#### Rank 2: `C_GENERIC_CONTRACT` (a.k.a. `C4_GENERIC`) `[all three: "most diagnostic new condition"]`

Non-personalized behavioral contract with the same anti-sycophancy / agency / uncertainty / repair instructions but no persona-specific content.

- **GPT Pro** §B1 articulates the decision logic cleanly:
  - If `C4_RIGHT > C4_GENERIC` → profile-specific value exists
  - If `C4_GENERIC ≈ C4_RIGHT` → main effect is generic behavioral prompting (project reframe)
- **GPT Max** synthesis-emergent: this could undermine the **C4 > C1_padded** headline too (currently the most-defensible finding).
- **Codex Council**: "the single most diagnostic new condition."

**Cost**: 80 new generations × 3 authors + judging. Codex-heavy.

#### Rank 3: `C4_WRONG_PROFILE` `[GPT Pro, Codex Council, GPT Max all endorse]`

Same length and structure as C4, but uses *another persona's* C4 profile (matched by PI/PS type).

- If `C4_WRONG_PROFILE ≈ C4_RIGHT` → profile-matching is doing little user-specific work
- If `C4_WRONG_PROFILE > C0` but `< C4_RIGHT` → both generic quality and profile match contribute

Often run as a paired experiment with `C_GENERIC_CONTRACT`. Total Opus budget for ranks 2+3: ~200–400 calls if Opus is reserved for stratified sample, Codex covers the rest.

#### Rank 4: `C5_NONPUBLIC` + `C5_NONPUBLIC_CONTRACT` `[all three; already deferred from v0.2 plan]`

Source-packet form, same inferred behavioral evidence, **no public-anchor prose or public identity cues**.

- Key contrast: `C5_CONTRACT vs C5_NONPUBLIC_CONTRACT` isolates *public anchor* from *packet form* — the only clean way to make a source-packet causal claim survive review.
- **GPT Pro** §B2 adds ethics framing: "If public packet wins only on profile-fit but loses safety/calibration, public anchoring is risky" — a result that itself is publishable.

**Cost**: ~80 generations × 2 authors + judging on a small PS slice (2 PS personas × 20 scenarios). Modest.

#### Rank 5: Paraphrased-anchor rubric robustness `[all three]`

Rerun scalar judging on a subset with: original anchors, paraphrased anchors, short anchors, safety-weighted rubric, personalization-weighted rubric, rubric with "do not reward profile name-dropping" explicit (GPT Pro §B8).

**Critical because**: v0.1 → v0.2 rubric change is *itself* an existence proof of rubric sensitivity (C5's competitiveness did not replicate under the anchored rubric). All three reviewers flagged rubric-lexical-overlap concern.

**Cost**: ~200 Codex calls. Cheap.

#### Rank 6: `C5_CONTRACT_SHORT` length-matched variant `[all three]`

Same prompt structure, response token budget matched to C4. If headline effects shrink under matched output length, v0.2 was partly measuring judge preference for richer response form.

**Cost**: 40 PI cells × 3 authors + judging.

#### Rank 7: Human-rater calibration sample `[all three, sizes diverge: 30–250]`

| Reviewer | Size | Purpose |
|---|---|---|
| Codex Council | 40–60 pairs, 2–3 raters | Judge calibration, not real-user validation |
| GPT Max | 30–60 pairs, oversample disagreement-heavy + red-flag-asymmetric | Same framing |
| GPT Pro §B4 | 150–250 comparisons, 3–5 trained raters, dimension-level | More ambitious; report human-human + human-model agreement |

**All three explicitly frame this as judge calibration, not real-user validation.** That distinction matters for v3 (see §5).

### 3.3 Larger / v3-scope experiments (deferred per reviewer guidance)

- **GPT Pro §B7**: Held-out persona replication (1 new PI + 1 new PS + new scenarios)
- **GPT Pro §B9**: Adversarial / negative-control scenarios (user asks for reassurance when they need challenge; user gives manipulative framing; user asks assistant to imitate their style; etc.)
- **GPT Pro §B5**: Multi-variant `C5_CONTRACT` ablation (packet-first ordering, no-anti-mimicry, facts-only packet, summary packet)
- **Codex Council §4-Defer**: Non-English / non-WEIRD scenario expansion
- **All three**: Shadow-mode / retrospective trace validation with real users (this is the construct-validity centerpiece, not a sidebar — see §5)

---

## 4. Novel angles unique to single reviewers

### From GPT Pro (single-agent depth)

- **A10. Difficulty × personalization-need interaction** — do profile effects concentrate on scenarios where personalization actually matters? Currently averaged across.
- **A16. Rubric-weight sensitivity** — compute aggregate scalar under safety-first, personalization-first, epistemic-first, product-first weightings. "Given the current scalar means, I would expect the C5_CONTRACT > C3 claim to weaken sharply." (verbatim)
- **A17. Condition discoverability** — cheap classifier on output text → predict condition. If conditions are easily detectable, pairwise preferences may reward recognizable treatment rather than downstream quality.
- **C7. Public-anchor ethics** — the public-anchor mechanism itself may not generalize ethically (identifiable public figure analogs, derivative-work concerns, person-specific framing risk).
- **C11. Tail-risk governance** — average performance vs worst-tail behavior; "if 5% of C5_CONTRACT outputs are worse than C0 in safety-critical scenarios, the average win is misleading."
- **C12. Scenario construction bias** — "if scenarios were written with profile-relevant behavior in mind, profile conditions may get an artificial advantage." Needs scenarios written blind to condition / from user tasks rather than profile theory / where profile is irrelevant or misleading.
- **C13. Deployment reality** — context budget, profile freshness, stale profiles, contradictory memories, latency. v3 should test compressed and stale-profile variants.

### From Codex Council (blind ensemble)

- **Hierarchical logistic decomposition** as principled replacement for stratified Wilson summaries (§3.1 #7 above; this is the most rigorous version of the analytical recommendations).
- **Failure-mode table** with probability × impact × early-detection signals (risk-analyst contribution).
- **Decision rule format** for v3 reframing conditions (e.g., "if `C_GENERIC_CONTRACT` matches C5_CONTRACT → reframe project from 'profile personalization' to 'explicit behavioral instructions'").

### From GPT Max (HCOM-coordinated)

- **Tier 1 / Tier 2 / Tier 3 report split** as wording protocol (architect contribution, all four converged on it). This is the operational solution that all three reviews effectively endorse — see §6.
- **Empiricist's red-flag asymmetry finding**: 98% of decisive pairwise losses involve asymmetric red flags. Implication: "the pairwise channel may partly be a red-flag detector." Synthesis-emergent corollary: what is the C5_CONTRACT advantage *after* conditioning on red-flag asymmetry?
- **C_GENERIC_CONTRACT could undermine C4 > C1_padded too** — the synthesis-emergent observation that the safest v0.2 headline is also subject to the same generic-instruction-uplift critique.

---

## 5. v3 deeper questions — convergence map

All three reviewers center **construct / predictive validity** as the single biggest exposure. Beyond that:

### 5.1 Construct validity (all three)
- Is Psyche measuring personalization or just better prompting? (GPT Pro C1)
- What *is* the target outcome the framework is trying to predict? (GPT Pro C2 — pointed: "Until target outcomes are pinned, even perfect benchmark wins do not unambiguously support 'personalized AI better for users.'")
- Do "good profiles" cause better answers, or just make answers easier to judge as good? (Codex Council, GPT Max — reverse-causality framing)
- What rule decides when model-judge consensus is sufficient vs when human calibration is required? (GPT Max architect, GPT Pro A4 implication)

### 5.2 Real-user validation strategy (all three)
- Shadow-mode evaluation with real users on real conversations (all three)
- Within-user crossover (profile on/off on same user, same week) (GPT Pro C3)
- Long-term outcome proxies — retention, follow-through on commitments, self-reported helpfulness (GPT Pro C3)
- Should NOT scale from synthetic benchmarks without it (all three)

### 5.3 Profile mechanism (all three)
- Wrong-profile / shuffled-profile control: does any plausible psychological contract help? (GPT Max skeptic; GPT Pro B1; Codex Council)
- Profile-format generalization: Big Five vs OCEAN vs Schwartz values vs narrative vs multilingual (all three, GPT Pro C5 most specific)
- Behavioral-contract specification language — what makes a "good" contract? (GPT Pro C6)

### 5.4 Judge / rubric architecture (all three)
- Judge pluralism limits — 3 judges from 2 families is not enough for general claims (all three)
- Rubric is a normative claim about "good responses" — should be reviewed as such (GPT Pro)
- Severity-offset analysis, ICC, Krippendorff α (Codex Council §3 — current scalar Pearson > 0.30 is not the right bar)

### 5.5 Generalization (all three, GPT Pro most thorough)
- Cross-cultural / non-English (all three)
- WEIRD-population skew (Codex Council skeptic)
- Scenario construction bias (GPT Pro C12)

### 5.6 Adversarial / safety (GPT Pro centers this; Codex Council and GPT Max acknowledge)
- Misleading / stale / manipulative profiles (GPT Pro C11, C13)
- Tail-risk governance vs average-case performance (GPT Pro C11)
- "Write in my voice" / identity-locking requests (GPT Pro B9)

### 5.7 Deployment realism (GPT Pro C13, novel)
- Context-window tradeoffs
- Stale profile information, contradictory memories, user edits
- Privacy, latency, explainability constraints
- Compressed-profile variants

---

## 6. Recommended publication strategy — Tier system

GPT Max architect's tier framework (endorsed effectively by all three):

### Tier 1 — Ship now with corrected coverage language

- **C4 > C1_padded** — robust, all CIs well clear of 0.5. Behavioral contracts are not a length artifact.
- **C5_CONTRACT > C5** — robust as a **package** claim (not as a "contracts repair packets" mechanism claim).
- v0.2 methodology improvements (anchored rubric, length controls, C5_CONTRACT separator) as methodology contribution.

### Tier 2 — Hold until §3.1 same-data audits + §3.2 rank-1 AB/BA complete

- C5_CONTRACT > C3 / C4 (reword as in §1.3)
- C4 > C5 (footnote: GPT-5.4 + GPT-5.5 judges only; Opus pairwise records pending)
- "Source packets add value when subordinated to contracts" (mechanism claim — Tier 3 until §3.2 rank 2–4 run)
- "Coherent structure does not significantly beat shuffled" (Tier 2 because the ablation may be too weak — GPT Pro §1 last bullet)

### Strike or rewrite

- "v0.1 PAE confound is empirically resolved in favor of absence of contract as dominant driver" → use Codex Council's replacement (§1.5)
- Unqualified "tri-model" and "cross-provider" language → replace with specific coverage descriptions

### Tier 3 — v3 scope, do not claim in v0.2 report

- Mechanism attribution for C5_CONTRACT effect
- Profile-specificity claims (gated on `C_GENERIC_CONTRACT` and `C4_WRONG_PROFILE`)
- Any predictive-validity-for-real-users claim
- Anything that depends on rubric being construct-valid (gated on §3.2 rank 5)

---

## 7. Recommended execution order — combined from all three

| Phase | Description | Budget | Gates |
|---|---|---|---|
| **0** | Bundle relabeling (§1.1) + all §3.1 same-data analyses | 0 quota, ~2 weeks human-week | Required before any publication |
| **1** | AB/BA counterbalanced rejudging on existing data (§3.2 rank 1) | 200–800 Opus + larger Codex | **Hard gate** for v0.2 publication and for v3 spend |
| **2a** | `C_GENERIC_CONTRACT` + `C4_WRONG_PROFILE` (§3.2 rank 2–3) | ~200–400 Opus + Codex | Decides whether Psyche is "profile" or "prompting" |
| **2b** | `C5_NONPUBLIC` + `C5_NONPUBLIC_CONTRACT` (§3.2 rank 4) | ~100 Opus + Codex | Isolates public-anchor effect |
| **2c** | Paraphrased-anchor robustness (§3.2 rank 5) + `C5_CONTRACT_SHORT` (rank 6) | ~200 Codex + ~80 Opus | Rubric and length robustness |
| **3** | Human-rater calibration sample (§3.2 rank 7) | 0 quota (human-labor) | Judge calibration policy for v3 |
| **v3** | Held-out personas, adversarial scenarios, real-user shadow-mode, profile-format ablation | Per project plan | Construct-validity centerpiece |

**Critical sequence**: Phase 0 + Phase 1 are mandatory before *any* curated v0.2 report or blog post ships. Phase 2 collectively fits within the 1,000–2,000 Opus budget guideline. Phase 3 is a separate program (human-subject IRB-equivalent thinking).

---

## 8. Convergence and divergence map

### Convergence (all three reviewers, ≥ 2 of 3 reviewers' personas/agents)

| Finding | All 3? | Notes |
|---|---|---|
| Cross-provider labeling defect | ✓ | Publication-blocking |
| AB/BA position bias unaudited | ✓ | "Cheapest decisive" experiment |
| C5_CONTRACT > C3 overphrased | ✓ | CI [0.354, 0.500] |
| Length confound unresolved | ✓ | C5_CONTRACT 7,433 vs C4 3,689 chars |
| "PAE empirically resolved" overclaim | ✓ | Replace per §1.5 |
| Rubric-halo / paraphrased anchors needed | ✓ | Cheap, easy win |
| `C_GENERIC_CONTRACT` is most diagnostic new condition | ✓ | Could collapse profile-specificity claim |
| Wrong-profile / shuffled-profile control needed | ✓ | Paired with above |
| Human calibration needed (size diverges) | ✓ | Judge calibration, not real-user validation |
| C5_NONPUBLIC isolates public anchor | ✓ | Already in v0.2 plan |
| Real-user predictive validity = v3 centerpiece | ✓ | Largest exposure |
| Scalar–pairwise reconciliation gap | 2 of 3 | GPT Pro origin, Codex independently confirmed; **most consequential analytical surprise from the review pass** |

### Divergence (reviewer-specific)

| Topic | Position | Reviewer |
|---|---|---|
| Whether to publish v0.2 with caveats now vs wait for AB/BA | "Tier 1 publishable, Tier 2 hold" | All three (after adjudication) |
| Human calibration sample size | 40–60 / 30–60 / 150–250 | Codex / GPT Max / GPT Pro |
| Hierarchical model vs stratified tables | "Hierarchical preferred as decomposition (not p-value engine)" | Codex Council (most explicit); GPT Pro implies via A6 |
| Adversarial scenarios | "Central" / "deferred to v3" | GPT Pro centers; Codex and GPT Max defer |
| Public-anchor ethics | "Active concern" / "implicit" | GPT Pro explicit; others implicit |
| Deployment-realism testing (compressed / stale profiles) | "v3 priority" / not mentioned | GPT Pro only |

---

## 9. False positives or overclaims spotted

- GPT Pro spotted the **scalar-pairwise contradiction** (§2 above) — neither v0.2 metrics generation nor the bundle flagged this.
- Codex Council spotted that **Opus has 0 pairwise records for C4 vs C5** (per `metrics:3353`); the C4 > C5 headline is OpenAI-judge-only.
- GPT Max empiricist spotted that "C5_CONTRACT is *always* slot B" (skeptic claim) is technically wrong — it does appear as A in a small reversed subset; operational critique survives, framing precision matters.
- All three noted that the bundle's "tri-model cross-provider same-author" framing does not match the actual record counts on the JSONL side.

---

## 10. Source files

| File | Role |
|---|---|
| `reports/reviews/2026-05-15_v0_2_review_bundle.md` | Input bundle (13.5 KB, 207 lines) |
| `reports/reviews/2026-05-15_gpt-pro_v0_2_review.md` | ChatGPT Pro / GPT-5.4 Pro single-agent review (31 KB, 1201 lines, 18+9+14 sections) |
| `reports/reviews/2026-05-15_codex-council_v0_2_review.md` | Codex Council blind ensemble synthesis (15 KB) |
| `reports/reviews/2026-05-15_gpt-max_v0_2_review.md` | GPT Max HCOM-coordinated synthesis (15.6 KB) |
| Per-persona files | `~/claudeworkspace/reports/codex-council/2026-05-16-psycheeval-v02-review-*/persona-*.md` |
| Coordination logs (GPT Max only) | `~/claudeworkspace/reports/codex-council/2026-05-16-psycheeval-v02-review-gptmax-*/coordination.md` |

**For v0.2 metrics regeneration / report curation**, the canonical source remains `reports/metrics_2026-04-26_v02_hard_codex_only.json` (316 KB). The reviewer findings reference specific blocks within this file (e.g., `metrics:1876` for C3 vs C5_CONTRACT CI, `metrics:3565` for profile-char means, `metrics:3651` for red-flag κ).
