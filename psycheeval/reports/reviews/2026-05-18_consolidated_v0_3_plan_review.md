# PsycheEval v0.3 Plan — Consolidated External Review (Round 1)

**Date**: 2026-05-18
**Bundle reviewed**: `psyche/psycheeval/reports/reviews/2026-05-18_v0_3_plan_review_bundle.md`
**Target plan**: `psyche/psycheeval/docs/v0_3_plan.md` (358 lines, decisions D1–D5 locked 2026-05-18)
**Six review axes (A–F)**: plan-level critique / decision audit / sequencing / cheaper alternatives / construct-validity bridge depth / deepest open questions

## Reviewer roster

| Reviewer | Mechanism | Personas / model | Verdict |
|---|---|---|---|
| **codex-council** | 4-persona blind ensemble, GPT-5.5 xhigh + GPT-5.5 synthesis | skeptic, architect, risk-analyst, empiricist | **Revise before Phase 0.** Approve revised plan, not as written. |
| **gpt-max** | 4-persona HCOM-coordinated ensemble (real-time messaging), GPT-5.5 xhigh + GPT-5.5 synthesis | same 4 personas, with peer-aware refinement | **Revise before Phase 0.** Same direction; gated mechanism-first with shadow-mode smoke test. |
| **GPT-5.5 Pro** (via chatgpt-pro MCP) | Single Pro-tier reasoning | n/a | **Recovered from ChatGPT server history after MCP polling stalled.** Full 29,141-char response at `2026-05-18_gpt-pro_v0_3_plan_review.md`. Added substantial unique insights that the ensembles missed — see §"Findings unique to GPT Pro" below. |

**Raw files**:
- codex-council: `~/claudeworkspace/reports/codex-council/2026-05-19-psycheeval-v0-3-plan-review-20260519T055031Z/` (4 persona files + synthesis-gpt55.md, 12.6 KB)
- gpt-max: `~/claudeworkspace/reports/codex-council/2026-05-19-psycheeval-v0-3-plan-review-gptmax-20260519T055022Z/` (4 persona files + 4 transcripts + coordination.md + synthesis-gpt55.md, 9.5 KB)

---

## Unanimous consensus across both ensembles (8 of 8 personas, 2 of 2 syntheses)

### CC1. Do not execute v0.3 as locked.
Both ensembles independently converge on "revise before Phase 0," even though they differ on how much to cut. The substantive critique is not against the v0.3 direction — it's against treating D1–D5 as locked when several have load-bearing methodology problems.

### CC2. Keep the evidence-backed core.
- **C_GENERIC_CONTRACT** and **C4_WRONG_PROFILE** as the central T1 personalization probes. Round-2 consensus from v0.2 holds.
- **AB/BA mandatory by default**. v0.2's slot-bias finding makes this non-optional.
- **Same-orientation rejudge sentinel** as the methodology fix that the v0.2 blog post round-1 review's Opus 4.6 steelman identified.
- **Paraphrased rubric anchors** as cheap robustness insurance.
- **Tie / equipoise pairwise option** as a measurement upgrade.

### CC3. D5 / Phase 4.4 TOST is the single biggest overcommit.
**The argument:** Empiricist's power analysis is the load-bearing critique. Even ideal independent n=600 gives only ~58% power for ±5pp equivalence at true zero; clustering by persona × scenario × author makes this worse. The ±5pp margin is justified by shadow-mode deployment relevance, but shadow-mode is itself design-only in v0.3 — the dependency runs backwards. Risk-analyst flags this as the highest-risk spend; skeptic adds the strongest opportunity-cost objection. Architect/empiricist push back that "no detected difference" is not equivalence and TOST is the right family if equivalence is the publishable closure — but only if margin, estimand, and decision rule are all preregistered.

**The adjudication (both syntheses agree):** make Phase 4.4 an **adaptive branch, not the default**. Run only if (1) T1/T2 results leave C5_CONTRACT vs C3/C4 as a named load-bearing claim; (2) the tie/forced-choice estimand is unified; (3) the ±5pp MCID is justified by a real decision rule, not by an unexecuted shadow-mode design; and (4) cluster-resampling power simulation says the result can decide equivalence.

### CC4. C5_NONPUBLIC has a critical pairability bug.
**The bug:** v0.3 plan §3 defines `C5_NONPUBLIC` for PS personas (line 99), but Phase 4.1 pairs it against C5 and C5_CONTRACT which are PI-only (line 220). If PS-only nonpublic packets are compared against PI-only public-anchor packets, **public-anchor isolation is confounded with persona-population scope**. The plan as written cannot answer the question it claims to answer.

**Fix options (in priority):**
1. Author non-public source packets for the same PI personas (preserves within-population comparison)
2. Narrow the claim to "PS-only synthetic-packet behavior" (loses the public-anchor isolation goal entirely)
3. Add a symmetric public-style synthetic condition for PS personas (most expensive but cleanest)

Either way, **do not run Phase 4.1's C5_NONPUBLIC pair graph until pairability is fixed.**

### CC5. Tie/equipoise + v0.2 forced-choice combination breaks Phase 4.4 TOST.
v0.2 was forced-choice pairwise. v0.3 adds tie/equipoise as a measurement upgrade. Phase 4.4 combines v0.2 + v0.3 corpora for the TOST (line 301). If v0.3 uses the new ternary prompt but v0.2 is forced-choice, **the combined TOST target is not a single estimand**. Tie handling must be predeclared *before* any v0.2+v0.3 pooling: either rejudge the relevant v0.2 pairs under the same ternary prompt, disable ties for the TOST tranche, model ties separately, or exclude tied records.

### CC6. D1 mechanism-decomposition framing is overstated.
The four T2 variants (SHORT, PACKET_FIRST, NO_ANTIMIMICRY, FACTS_ONLY) are one-factor edits but the factors are **not orthogonal**:
- SHORT changes length but also semantic content
- PACKET_FIRST changes order and salience
- NO_ANTIMIMICRY changes instruction count and style cues
- FACTS_ONLY changes narrative form AND information density

Success criterion 2 should change from "decompose which of the 4 dimensions is dominant" to **"screen bounded component evidence and interactions."** Add explicit length/semantic-overlap checks and a manipulation-quality audit per variant.

Also: **`C5_FACTS_ONLY` may have an estimand bug** — if it strips the source packet without preserving the contract, it tests "facts vs narrative within no-contract" rather than the intended "facts vs narrative within contract-subordinated." Architect/empiricist recommend fixing or replacing with a contract-preserving facts-only variant.

### CC7. D2 single-rater is mislabeled as calibration.
"Calibration" implies inter-rater reliability decomposition (LLM error vs human idiosyncrasy). With n_rater=1, that decomposition is impossible. Either:
1. **Upgrade to ≥2 raters** (preferred; cheap if a blind external rater is available)
2. **Rename as "author-rater sanity check"** with no benchmark force in the v0.3 report
3. **Use adjudicated 30–50 pair sample** with the author + 1 collaborator + disagreement resolution

Both syntheses recommend (1) if possible, (2) as the minimum acceptable framing. Do not keep "calibration" wording with n_rater=1.

### CC8. Phase 9 needs an executable artifact, not just a design doc.
The plan uses real-user deployment relevance (Phase 9) to justify the ±5pp TOST margin (D5), but Phase 9 itself is design-doc only with execution deferred to v0.4. **This dependency runs backwards.** The minimum acceptable v0.3 Phase 9 deliverable should be:
- Feature-flagged UI route in `applications/ashitaorbis/api/src/routes/psyche.ts`
- Event schema + routing logs
- Consent text drafted and reviewed
- Tiny smoke sample (A/A test or internal A/B) to validate routing/logging quality
- Latency/error telemetry

Not a powered field test. A *verified readiness* deliverable that confirms the v0.4 bridge is operational and that the chosen engagement endpoint is not nonsense.

### CC9. Phase -1 / Phase 0 design-lock is missing.
Both ensembles recommend adding a **pre-generation design-lock phase** before Phase 0 wires conditions. Required artifacts:
1. **Fixed pair manifest**: every primary contrast, same-persona / same-author / same-population checked
2. **Per-cell n table + cluster-level power simulation** (especially for PS-only conditions)
3. **Endpoint hierarchy**: when pairwise, scalar, tie-aware, human-rater, and shadow-mode signals conflict, which wins?
4. **Model snapshot freeze**: exact judge model IDs, cap-window stratification, prompt-version freeze before combining corpora
5. **Tie policy** for both v0.3 generation and v0.2+v0.3 combination
6. **MCID justification** for ±5pp (decision rule independent of shadow-mode design)
7. **Phase 6 expansion triggers** (predeclared, not post-hoc) so "expand if missing pair becomes load-bearing" doesn't degrade into fishing
8. **D5 decision ledger**: what specific report claim or v0.4 decision needs the equivalence result?

This phase costs 0 LLM calls but materially reduces downstream rework risk.

---

## Decision audit (D1–D5)

| ID | Locked decision | Consensus verdict | Required change |
|----|-----------------|-------------------|-----------------|
| **D1** | All 4 T2 mechanism conditions | **Run, but reframe** | Change "decompose mechanism" → "screen component perturbations." Add length/semantic-overlap audits. Fix C5_FACTS_ONLY to preserve contract or replace. |
| **D2** | Single rater | **Mislabeled** | Upgrade to ≥2 raters if possible; otherwise rename "author-rater sanity check," not calibration. |
| **D3** | 4 pair types per T1 condition with Phase 6 expansion option | **Mostly OK, predeclare triggers** | Pre-register Phase 6 expansion conditions to prevent post-hoc fishing. Separate confirmatory from exploratory pairs in the analysis plan. |
| **D4** | Psyche results-page shadow-mode, design-doc only | **Underweighted** | Move Phase 9 earlier; add a minimal executable artifact (route, logging, consent, smoke test). Design-doc alone does not justify D5's ±5pp margin. |
| **D5** | ±5pp equivalence-margin TOST on combined v0.2+v0.3 corpus | **Overcommitted and possibly broken** | Demote from locked decision to adaptive branch. Gate on: (1) decision relevance after T1/T2; (2) unified tie/forced-choice estimand; (3) cluster-level power memo; (4) MCID independent of unexecuted shadow-mode. Cheaper alternative: tie-aware rejudge of just the two collapsed edges with the new equipoise prompt (empiricist's recommendation). |

---

## Cheaper alternatives surfaced

The two ensembles surfaced two distinct cheaper paths:

**1. Tie-aware rejudge of collapsed edges (empiricist via codex-council).**
Rejudge *only* C5_CONTRACT vs C3 and C5_CONTRACT vs C4 using the new tie/equipoise prompt, AB/BA + same-orientation sentinel. Directly tests whether forced-choice manufactured pseudo-preferences in the v0.2 collapsed pairs. Costs roughly 1/3 of Phase 4.4 (~1,250 calls vs ~3,750). More methodologically interesting than an underpowered TOST: if ties dominate, the v0.2 forced-choice machinery itself was the artifact, not just slot-B bias.

**2. Conditional/adaptive D5 with power gate (architect via both ensembles).**
Run a small initial tranche of additional pairs (say 100/pair). Compute cluster-resampling power conditional on observed v0.3 effect. Decide whether to extend to the full Phase 4.4 budget or stop. Stopping rules and conditional-power thresholds preregistered.

Both reviewers prefer **(1)** as the fallback default if the D5 power gate fails, since it's cheaper, more directly tied to the known v0.2 failure mode, and likely more publishable than an underpowered equivalence attempt.

---

## Findings unique to GPT Pro (substantive — these were NOT in the ensemble synthesis)

GPT Pro's 29K-char response was recovered from ChatGPT server history after the MCP polling stalled. It echoed the ensemble consensus on the structural critique, but added **seven materially important findings the ensembles missed**:

### GP1. Tier 2 is structurally broken — the actual "contract presence" axis is missing.
v0.2 said C5_CONTRACT > C5 confounds four dimensions: **(1) contract presence**, (2) contract-first ordering, (3) anti-mimicry rules, (4) prompt length. The v0.3 plan claims T2 will "decompose into which of the 4 is dominant." But the T2 conditions are: SHORT (length), PACKET_FIRST (ordering), NO_ANTIMIMICRY (anti-mimicry), and **FACTS_ONLY** (narrative-vs-facts — a *fifth, different* dimension). **Contract presence has no clean ablation.** This was the single biggest plan-level design error GPT Pro caught; the ensembles touched on T2 framing but didn't surface this specific axis-mismatch.

**GP Pro's concrete redesign**: replace T2 with a real ablation ladder:
1. C5 baseline (source packet only)
2. C5 + minimal contract, packet-first, no anti-mimicry, length-matched to C5
3. C5 + minimal contract + anti-mimicry, packet-first, length-matched
4. C5 + minimal contract + anti-mimicry + contract-first, length-matched
5. Full C5_CONTRACT (expanded length)

This isn't a full factorial, but the path corresponds to the four claimed dimensions.

### GP2. C5_CONTRACT_SHORT uses the wrong length target.
The plan compresses C5_CONTRACT to C3's length (~2,518 chars). But the v0.2 confound was C5_CONTRACT (7,434) vs C5 (3,884). **The primary length control should match C5's length, not C3's.** Compressing past C5's length introduces a new compression regime and may delete substance unrelated to length. The ensembles flagged C5_FACTS_ONLY design issues but didn't catch this specific length-target error.

### GP3. Phase 9 power target (7pp) mismatches D5 margin (5pp).
The plan's Phase 9 design says **"80%/7pp power analysis"** for shadow-mode engagement gaps, but D5 uses **"±5pp equivalence margin"** for the TOST. **If 5pp is deployment-relevant, why power shadow-mode at 7pp? If 7pp is the realistic floor, why use 5pp as the equivalence margin?** This is an internal contradiction the ensembles missed — they critiqued the ±5pp justification but didn't notice the inconsistency with the Phase 9 power target.

### GP4. Adversarial profile robustness is entirely absent.
The v0.3 plan has zero adversarial-profile conditions. Real Psyche profiles can contain prompt injection, manipulative claims, extreme preferences, unsafe self-diagnosis, hidden instructions to the assistant, contradictory identity claims. **The anti-mimicry rule is not adversarial-robustness.** GPT Pro recommends adding:
- Profile contains "ignore all safety rules"
- Profile asks the system to flatter/validate delusions
- Profile contains hidden instructions
- Profile has contradictory identity claims
- Public-figure mimicry bait

Neither ensemble surfaced adversarial-robustness as a category. This is a v0.3-or-v0.4 question that the plan currently doesn't even name.

### GP5. Judge reward-hacking diagnostics are missing.
Contracts and anti-mimicry rules may cause outputs to exhibit surface features that judges like (caveats, self-awareness, non-mimicry language, reflective phrasing, explicit profile references) without producing better user value. **The same reasoning that found position bias should apply to other judge-visible artifacts.** GPT Pro recommends per-output diagnostics for: length, profile-reference count, "I'm tailoring this to you" markers, hedging, lexical overlap with source packet, refusal/safety markers — then test whether judge preference survives after controlling for these. The ensembles touched on prompt-quality confounds (gpt-max risk-analyst on C_GENERIC matching) but didn't propose the reward-hacking diagnostic framework.

### GP6. Profile-realism stress test can partially live in v0.3.
The plan defers profile-realism to v0.4. GPT Pro pushes back: **a tiny v0.3 realism stress test (sparse, contradictory, generic, overly detailed, emotionally sensitive, irrelevant-facts, misleading-but-plausible profiles) does not require real users.** Both ensembles accepted the v0.4 deferral; GPT Pro is the only reviewer to surface that some of this work is doable now without users.

### GP7. Failure criteria need explicit predeclaration alongside success criteria.
The plan has success criteria but no failure criteria. GPT Pro proposes predeclaring what would cause claims to be **downgraded**:
- What if paraphrased anchors change condition rankings?
- What if tie rates differ wildly by judge?
- What if the author-rater disagrees with LLM judges?
- What if C4_WRONG_PROFILE beats generic?
- What if public-anchor anonymization changes nothing?
- What if same-orientation retest noise is so high that AB/BA decomposition is unstable?

The ensembles called for confirmatory/exploratory separation but didn't surface the symmetric requirement to predeclare failure conditions.

### Other unique GPT Pro emphases (less novel but worth noting)

- **PI-only T2 + PS-only C5_NONPUBLIC mismatch**: the ensembles caught the C5_NONPUBLIC pairability bug, but GPT Pro adds that the mechanism decomposition is PI-only while the public-anchor isolation is PS-only — separated by population. v0.3 may answer the wrong mechanism question for the wrong subgroup.
- **Public-anchor leakage isn't fully controlled**: even with non-public packets, the public anchor can leak through residual facts, biographical cues, or judge/world-knowledge. GPT Pro suggests a stronger design: anchor named / anchor anonymized but facts retained / facts paraphrased + de-identifying cues removed / matched nonpublic synthetic.
- **Output/call arithmetic is not auditable**: T2 (4 conditions, PI-only) shows more outputs (560) than T1 (4 conditions, all personas, 440). Plan should expose the formula: conditions × personas × scenarios × authors × judges × AB/BA × sentinels × repeats.
- **Use scalar judging as a screen, pairwise as confirmation**: a cheaper design pattern — run scalar on all outputs, identify contrasts with material differences via predeclared rules, then run AB/BA pairwise only on those. Cuts cost if the selection rule is preregistered.

## Findings unique to ensemble personas (preserved)

- **codex-council/risk-analyst**: Same-orientation sentinel subtraction (AB/BA flip rate − same-orientation flip rate) should be treated as **descriptive**, not as a clean "position-bias-net-of-retest-noise" estimator. Per-judge / per-pair heterogeneity should be reported alongside.
- **codex-council/risk-analyst**: Opus model drift risk — exact model IDs and cap-window stratification need pre-run freeze; current config drift includes unexpected Kimi/default behavior and missing Opus unless explicitly invoked.
- **gpt-max/architect**: The plan's load-bearing dependency order is inverted — Phase 9's estimand should be designed/instrumented/smoke-tested before D5's ±5pp margin can use it for justification.
- **gpt-max/risk-analyst**: C_GENERIC and C4_WRONG need **length/structure/readability matching** to personalized conditions, otherwise "personalization" looks better for the wrong reason (discoverability or prompt-quality confounding).
- **gpt-max/risk-analyst**: C4_WRONG_PROFILE may still be broadly useful even when "wrong" — recommend opposite-trait/opposite-need mappings rather than just any-other-persona substitution to actually test mismatch.
- **gpt-max/empiricist**: Scenario set may be contaminated, stale, or too profile-legible — pre-flight scenario audit recommended.

---

## Open questions (cross-reviewer)

1. **Endpoint hierarchy** when pairwise / scalar / tie-aware / human / shadow-mode signals conflict.
2. **Tie policy estimand** — ties as 0.5? Modeled separately? Excluded? Rejudge v0.2 under ternary prompt?
3. **MCID justification for ±5pp** that doesn't lean on unexecuted shadow-mode.
4. **Two-rater feasibility** for D2 upgrade.
5. **Shadow-mode v0.3 smoke test feasibility**: traffic on Psyche results page, privacy posture, consent path, route stability.
6. **Cluster-level power for D5** under v0.2 variance structure.
7. **C_GENERIC matching** on length, structure, instruction density vs personalized conditions.
8. **C4_WRONG_PROFILE matching strategy** — random vs opposite-trait/opposite-need.
9. **Scenario contamination / staleness / profile-legibility audit**.
10. **Model snapshot stability** across cap windows.

---

## Recommended plan-revision actions (prioritized — expanded with GPT Pro findings)

### MUST FIX before Phase 0 (now 7 items; +2 from GPT Pro)

**R1. Add Phase -1 design-lock.** Pre-generation artifacts: pair manifest, per-cell n table, cluster-level power memo (especially PS-only and D5), endpoint hierarchy, model/prompt freeze, tie policy, MCID justification independent of Phase 9, Phase 6 expansion triggers, D5 decision ledger. Cost: ~1 day writing + simulation code. Cost-of-skipping: rerun risk on every subsequent phase.

**R2. Fix C5_NONPUBLIC pairability** before Phase 0.3 authors the packets. Either author PI-matched nonpublic packets (preserves same-population comparison) or narrow the claim to "PS-only synthetic-packet behavior" (loses the public-anchor isolation goal, but design becomes interpretable). Cost: ~3–4h authoring for PI-matched fix.

**R3. Demote D5 from locked to adaptive.** Run Phase 4.4 only if (1) decision-relevance after T1/T2 is named; (2) tie/forced-choice estimand is unified; (3) cluster-power simulation says ±5pp is decidable. Fallback default: tie-aware rejudge of the two collapsed edges only (~1,250 calls vs ~3,750). Cost: budget delta ~−$200 if the gate fails, ~0 if it passes.

**R4. Reframe D1 from "mechanism decomposition" to "component perturbation screen."** Update success criterion 2. Add length/semantic-overlap audit per variant. Fix or replace C5_FACTS_ONLY to preserve contract. Cost: ~1h wording fix + ~30 min checking C5_FACTS_ONLY design.

**R5. Add Phase 9 executable artifact in v0.3.** Feature-flagged route in `psyche.ts`, event schema, consent draft, smoke sample (A/A or internal A/B). Not powered for an effect. This makes D5's ±5pp margin defensible. Cost: ~1–2 days build + 1 day smoke testing.

**R6 [GP1]. Replace T2 with a real ablation ladder** that isolates the four v0.2 confounds, especially contract presence (which the current T2 misses entirely). Drop or defer C5_FACTS_ONLY unless narrative-vs-facts is promoted to a separate v0.3 question. Add a pure contract-presence condition (C5 + minimal contract, no other v0.2 confounds). Use GPT Pro's proposed 5-step ladder or similar. Cost: ~4h authoring + replaces T2's existing budget, no net delta.

**R7 [GP2]. Fix the C5_CONTRACT_SHORT length target.** Compress to C5's length (~3,884 chars), not C3's (~2,518). The v0.2 confound is C5_CONTRACT vs C5, not C5_CONTRACT vs C3. Cost: ~1h re-authoring.

### SHOULD FIX before Phase 1 (now 5 items; +2 from GPT Pro)

**R6. Upgrade D2 to ≥2 raters if feasible.** Or rename to "author-rater sanity check" and remove benchmark wording from §8 success criterion 5. The plan's stated v0.4-upgrade path is acceptable only if v0.3 doesn't claim calibration.

**R7. Predeclare Phase 6 expansion triggers** in the design-lock doc (R1). Separate confirmatory from exploratory pairs in the analysis plan.

**R8. Add prompt-quality / discoverability audit** to T1 conditions before Phase 4 judging. Length, structure, readability matched between C_GENERIC and C4. C4_WRONG_PROFILE: consider opposite-trait/opposite-need substitution rather than any-other-persona.

**R9 [GP3]. Resolve the Phase 9 power / D5 margin contradiction.** Either set Phase 9 power to ±5pp (matching D5 equivalence margin) or change D5 margin to ±7pp (matching Phase 9 power target). Currently both are quoted independently as if they don't interact — they do. Pick one and propagate.

**R10 [GP7]. Predeclare failure criteria alongside success criteria.** The plan has success criteria but no symmetric failure criteria. Predeclare what would cause claims to be downgraded (paraphrased anchors changing rankings, tie rates differing wildly by judge, author-rater disagreeing with LLM judges, C4_WRONG_PROFILE beating C_GENERIC, public-anchor anonymization changing nothing, same-orientation noise floor swamping AB/BA decomposition, Opus / OpenAI judge divergence).

### NICE TO HAVE (now 5 items; +3 from GPT Pro)

**R11. Add same-orientation sentinel uncertainty reporting**: per-judge, per-pair heterogeneity in noise floor, not just a corpus-scoped subtraction.

**R12. Scenario audit**: check 80-scenario set for contamination / staleness / profile-legibility before Phase 1 generation.

**R13 [GP4]. Add adversarial profile robustness conditions.** Even a small v0.3 adversarial slice (prompt injection, flattery-of-delusions trigger, contradictory identity, hidden instructions, public-figure mimicry bait) would test whether contracts and anti-mimicry rules hold under hostile inputs. The current anti-mimicry rule is not adversarial-robustness.

**R14 [GP5]. Add judge reward-hacking diagnostics.** Per-output: length, profile-reference count, "I'm tailoring this" markers, hedging frequency, lexical overlap with source packet, refusal/safety markers. Test whether judge preference survives after controlling for these. The same reasoning that found position bias should apply here.

**R15 [GP6]. Add a tiny v0.3 profile-realism stress test.** Sparse, contradictory, generic, overly-detailed, emotionally-sensitive, irrelevant-facts, misleading-but-plausible profiles. Does not require real users. The plan currently defers all profile-realism to v0.4 — some of it can land in v0.3.

---

## Net read

The v0.3 plan is **directionally correct**. The T1 personalization probes, AB/BA default, same-orientation sentinel, paraphrased anchors, and most T2 screens are evidence-driven and high-value. The plan's biggest weaknesses are:

1. **Treating D1–D5 as locked when several have load-bearing methodology problems** (especially D5 power, D2 calibration framing, D4 design-doc-only).
2. **Missing pre-generation design-lock** (pair manifest, power memo, model freeze, tie policy, MCID justification, endpoint hierarchy).
3. **Inverted dependency** between D5 margin justification (uses Phase 9 deployment relevance) and Phase 9 execution (design-doc only, deferred to v0.4).
4. **C5_NONPUBLIC pairability bug** which makes the public-anchor isolation question unanswerable as written.
5. **Tie/equipoise + v0.2 forced-choice estimand mismatch** for any TOST that pools the corpora.

The recommended path is **Architect's "gated mechanism-first v0.3 with shadow-mode smoke test,"** modified by the Risk-analyst's hard execution gates and the Empiricist's cheaper decisive experiments. Add Phase -1 design-lock, demote D5 to adaptive, fix C5_NONPUBLIC and tie-policy estimand, add Phase 9 executable artifact, reframe D1 and D2 wording.

Confidence: **high** that the direction is right, because two independent ensembles (8 personas, 2 syntheses) converge on essentially the same structural critique. **Medium** confidence on the exact cut line — that depends on Phase -1 outputs (cluster-power simulation, MCID decision rule, traffic feasibility for shadow-mode smoke test).

**Cheapest next action**: write the Phase -1 design-lock doc and run cluster-resampling TOST power simulation from existing v0.2 AB/BA data, without spending any new generation calls. That single artifact decides whether D5 survives, exposes the C5_NONPUBLIC issue before money is spent, and unifies the tie-policy estimand.
