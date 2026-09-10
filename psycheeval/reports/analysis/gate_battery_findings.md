# PsycheEval v0.3 — existing-data gate battery (Gates 1, 1b, 2, 3 + trigger #7)

**Date**: 2026-06-17
**Supersedes**: `gates_1_2_findings.md` (Gates 1 + 2 only; kept for audit trail).
**Source data**: `runs/2026-05-19_v03` — pairwise both orientations, D3 per-output features, raw `assistant_response` text, persona contracts.
**Scope**: cross-provider, same-author, AB/BA both orientations. Cluster bootstrap (persona×scenario×author), 2000 resamples, where applicable.
**Scripts**: `drivers/analysis/{gate1_style_deconfound,gate1b_stylometry,gate2_signflip,trigger7_judge_divergence,gate3_prepare,gate3_score}.py`
**Context**: GPT Pro's three pre-registered existing-data gates (`reviews/2026-06-16_gptpro_v0_3_forward_analysis.md`) + predeclared failure-triggers #7/#8. These are the load-bearing tests for whether v0.3 shows real personalization vs shared formatting / global trait-pole preference.

---

## Headline

Each of the three personalization-relevant claims is undercut by a **different** gate, and the one robust claim (structure) turns out **not to be judge-unanimous**:

| Claim | Survives surface control? (Gate 1 / 1b) | Target-fit vs global-pole? (Gate 2) | Judge-consistent? (trigger #7) | Net |
|-------|:--:|:--:|:--:|-----|
| **Structure** (any contract > C0) | YES | n/a | **NO — one judge×author cell (fires)** | not judge-unanimous; concentrated in opus-judge/gpt-author cell (confounded), not personalization |
| **Specificity** (C3/C4 > C_GENERIC) | **NO** | n/a | borderline (8–12pp) | not robust to surface control (mediator caveat); downgrade |
| **Matching** (C3/C4 > C4_WRONG) | YES (content signal) | **mostly GLOBAL-POLE (3/4)** | YES (≤7pp) | the surviving content signal *is* the global-pole; bias or real quality undetermined |
| Public-anchor (C5 > C5_NONPUBLIC) | — | — | YES (≤3pp) | already downgraded by D4 ties (75%) |

The strongest *surviving* signal is **structure**, which is the **least** personalization-relevant — and even it is concentrated in one judge×author cell. **Gate 3 adds the locus, carefully bounded**: the conditioned outputs are blind-*discriminable* by persona (non-study recovery **93%**, but partly via surface contract-echo, so this is discriminability, not demonstrated adaptation), which places the matching/global-pole failure *at least partly* at the **evaluation** stage — the study judges, asked for *unconditional* quality, reward a global trait-pole rather than fit-to-target. The honest reframe: **evaluation is the clearer bottleneck; whether generation is *target-serving* is open** (needs de-echoed recovery + target-conditioned judging).

---

## Gate 1 — do the headline effects survive control for surface features? (also trigger #8)

Surface features pruned to the three with real variance — **log word count, source-packet lexical overlap, hedging/100w**. (`profile_reference_count` 99% zero, `tailoring_marker_count` 100% zero, `refusal_safety_marker_count` 89% zero — dropped; their near-zero variance independently confirms **judges do not reward profile-naming or explicit tailoring markers**.) Surface-adjusted win rate = logistic intercept at ΔS=0, slot-balanced. Cluster-bootstrap 95% CIs.

| Contrast | n | raw win | surface-adjusted (95% CI) | survives? |
|----------|---:|--------:|---------------------------|:--:|
| **C4 > C4_WRONG** | 635 | 0.565 | **0.568 [0.511, 0.624]** | **YES** |
| **C3 > C4_WRONG** | 636 | 0.593 | **0.595 [0.539, 0.651]** | **YES** |
| C4 > C_GENERIC | 635 | 0.550 | 0.551 [0.495, 0.610] | **NO** |
| C3 > C_GENERIC | 635 | 0.521 | 0.522 [0.468, 0.580] | **NO** |
| C_GENERIC > C0 | 634 | 0.702 | 0.729 [0.675, 0.788] | YES |
| C4_WRONG > C0 | 628 | 0.653 | 0.670 [0.611, 0.733] | YES |

**Result.** Matching (right > wrong) and structure (contract > none) survive surface control. **Specificity-over-generic does NOT** — once surface is balanced, C3/C4 > C_GENERIC is indistinguishable from chance. The raw 57–59% specificity headline was substantially a surface effect. **This satisfies predeclared failure-trigger #8** (covariate-controlled regression): the specificity leg is the casualty.

## Gate 1b — richer stylometric index (strengthens Gate 1)

Re-ran the deconfounding with a **9-feature** index extracted directly from raw output text: log word count, bullet/heading/numbered-list density, imperative-start fraction, 2nd-person rate, markdown-marker density, mean sentence length, bold/emphasis density — i.e. exactly the "directive/scaffolded/contract-like" surface the shared-formatting null predicts judges reward.

| Contrast | n | raw | stylo-adjusted (95% CI) | survives rich control? |
|----------|---:|----:|-------------------------|:--:|
| C4 > C4_WRONG | 635 | 0.565 | **0.575 [0.513, 0.638]** | **YES** |
| C3 > C4_WRONG | 636 | 0.593 | **0.597 [0.544, 0.658]** | **YES** |
| C4 > C_GENERIC | 635 | 0.550 | 0.553 [0.492, 0.614] | NO |
| C3 > C_GENERIC | 635 | 0.521 | 0.522 [0.461, 0.581] | NO |
| C_GENERIC > C0 | 634 | 0.702 | 0.740 [0.680, 0.807] | YES |
| C4_WRONG > C0 | 628 | 0.653 | 0.678 [0.619, 0.747] | YES |

**Result.** Identical conclusion to Gate 1 with the richer index: matching and structure survive even controlling all directive-formatting features; specificity does not. The specificity downgrade is robust to how surface is measured. (Caveat, per GPT Pro: surface features are post-treatment mediators; this is a conservative adversarial diagnosis — "does the effect survive net of the formatting it induces" — not a clean causal estimate.)

## Gate 2 — is "matching" real target-matching, or a global trait-pole preference?

`OPPOSITE_TRAIT_MAPPING` is reciprocal (A↔B). On A's scenarios C4=A's profile, C4_WRONG=B's; on B's scenarios C4=B's, C4_WRONG=A's. If matching is real, each persona's **own** profile should win on its **own** scenarios in *both* directions (sign-flip). If one profile-pole wins regardless of target, "right beats wrong" is a global preference.

| reciprocal pair | A own-profile win | B own-profile win | verdict |
|-----------------|------------------:|------------------:|---------|
| dario_armadillo / pawl_gram | **0.80** | 0.34 | **GLOBAL-POLE** |
| slalom_altar / emily_blender | **0.88** | 0.29 | **GLOBAL-POLE** |
| calibration_goblin / high_agency_spiraler | 0.54 | 0.41 | **GLOBAL-POLE** |
| conflict_allergic_moralist / patient_craftsperson | 0.72 | 0.54 | matching (weak) |

**Result — NEGATIVE for the matching headline.** In **3 of 4** reciprocal pairs one persona's profile wins *regardless of which persona is the target*. The aggregate C4 > C4_WRONG ≈ 61% is inflated by the cases where the correct profile is the globally-preferred pole. Genuine sign-flipping target-matching appears in **at most 1 of 4** pairs (and weakly). So matching, though it survives *surface* control, is **largely a content-level preference for certain trait-poles** (plausibly the more agentic/assertive/structured personas), **not target-fit**. (Note: the dario/pawl pair additionally has a delta-form wrong-profile conditioning wrinkle — see Gate 3 §setup — but the slalom/emily and goblin/spiraler global-pole results use clean full profiles, so the finding does not depend on it.)

## Trigger #7 — opus-vs-OpenAI judge divergence (gates "judge-unanimous" wording)

Per-judge-family win rate of the nominal winner, **>15pp divergence fires**. Confound (declared): cross-provider same-author scope means opus-judge⟺gpt-author and gpt-judge⟺opus-author, so a divergence is judge-family OR author-family. Either way it kills "judge-unanimous."

| contrast | opus-judge win | gpt-judge win | Δpp | fires |
|----------|---:|---:|---:|:--:|
| **C_GENERIC vs C0** | 0.906 | 0.497 | **40.9** | **YES** |
| **C4_WRONG vs C0** | 0.901 | 0.408 | **49.2** | **YES** |
| **C5 vs C_GENERIC** | 0.319 | 0.650 | **33.1** | **YES** |
| **C5 vs C4_WRONG** | 0.371 | 0.662 | **29.1** | **YES** |
| **C5_CONTRACT vs C5** | 0.682 | 0.438 | **24.4** | **YES** |
| C3 vs C_GENERIC | 0.480 | 0.563 | 8.4 | no |
| C4 vs C_GENERIC | 0.608 | 0.491 | 11.8 | no |
| C3 vs C4_WRONG | 0.559 | 0.627 | 6.7 | no |
| C4 vs C4_WRONG | 0.583 | 0.547 | 3.6 | no |
| C5 vs C5_NONPUBLIC | 0.503 | 0.531 | 2.8 | no |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | 0.500 | 0.531 | 3.1 | no |
| C4 vs C5 | 0.738 | — (no cell) | — | n/a (coverage) |
| C4 vs C1_padded | — | — | — | n/a (coverage) |
| C4 vs C4_shuffled | — | — | — | n/a (coverage) |

**Result — FIRES on 5 of the 11 covered contrasts.** The pattern is sharp and consistent: **every firing contrast is a contract-structure comparison, and opus-as-judge rewards the contract (68–91%) while gpt-as-judge is at or below chance.** The "structure beats baseline" floor (the strongest surviving claim from Gates 1/1b) is **largely an opus-as-judge phenomenon** — the aggregate 65.6% averages an opus-judge ~90% with a gpt-judge ~50%. By contrast, **matching and public-anchor contrasts never fire (≤7pp)** — those effects are judge-robust. The inherited §6 contrasts C4>C5 / C4>C1_padded / C4>C4_shuffled have **incomplete judge-family coverage** under the cross-provider same-author scope (only one cell), so the §6 "**Judge-unanimous**" descriptor on C4>C5 cannot be supported under v0.3 scope and must be attributed to the original (broader-scope) v0.2 analysis; the one adjacent contract contrast that IS covered (C5_CONTRACT vs C5) fires at 24pp.

---

## Gate 3 — blind semantic persona-alignment audit (generation vs evaluation)

**Design.** A non-study model (Gemini 3.1 Pro, default) is shown, blind to condition, two de-leaked **full** persona briefs (target P, opposite Q) and the two outputs (C4 = P-conditioned, C4_WRONG = Q-conditioned) for the same scenario, in randomized order, and asked which persona each output behaviorally fits. 64 tasks, 8 per persona, balanced across the 4 reciprocal pairs. Answer keys held in `/tmp` (out of Gemini's workspace reach); workspace prompt files carry no names/labels/conditions. 64/64 clean verdicts, no parse failures.

**Results.**

| Metric | Value | Reading |
|--------|-------|---------|
| Blind recovery, **all outputs** | **0.93 [0.872, 0.963]** (n=128) | authors strongly steer text toward the conditioning persona |
| Recovery, C4 (own-profile) outputs | 0.953 [0.871, 0.984] (n=64) | target-conditioned text is target-distinct |
| Recovery, C4_WRONG (opposite) outputs | 0.906 [0.81, 0.956] (n=64) | opposite-conditioned text is opposite-distinct too |
| Per-target C4-alignment, range | 0.75 (dario) – 1.00 (six personas) | every persona ≥0.75 |

**Text-level sign-flip vs Gate 2's judge-level preference** (the decisive table):

| reciprocal pair | G3 text-align A | text-align B | G2 judge-win A | judge-win B | reading |
|---|---:|---:|---:|---:|---|
| slalom / emily | 1.00 | 1.00 | 0.88 | 0.29 | **GEN works / EVAL global-pole-biased** |
| dario / pawl | 0.75 | 1.00 | 0.80 | 0.34 | **GEN works / EVAL global-pole-biased** |
| calibration_goblin / high_agency_spiraler | 1.00 | 1.00 | 0.54 | 0.41 | **GEN works / EVAL global-pole-biased** |
| moralist / craftsperson | 0.88 | 1.00 | 0.72 | 0.54 | both target-fit |

**Gen × eval cross-tab** (per task, n=64): gen recovers target & judge prefers target **70%**; **gen recovers target but judge prefers the OPPOSITE output 25%** (eval-side global-pole bias made concrete); gen misses target 5%.

**Result — the personalization failure is at EVALUATION, not generation.** Blind Gemini recovers the conditioning persona ~93% of the time, and on all three of Gate 2's "global-pole" reciprocal pairs the text-level alignment *sign-flips* (both directions ≥0.75) even though the study judge's preference did **not**. So the profiles **do** produce target-distinct outputs in both directions; the study judges simply don't reward target-fit — in 25% of pairs they prefer the *opposite*-conditioned output. The Gate-2 "global-pole, not matching" result is therefore an **evaluation-stage** phenomenon, not a generation failure.

**Crucial asymmetry (why this is the cleanest statement).** Gate 3's coder *had the persona briefs* and was asked to *match a target*; the study judges in the C4-vs-C4_WRONG contrast had **no** persona reference and were asked "**which response is better**" unconditionally. So v0.3's "matching" contrast measured *unconditional quality of P-conditioned vs Q-conditioned text*, which tracks a global trait-pole — not *fit to P*. The conditioning works (text is target-distinct, recoverable at 93% when the target is known); it is the **unconditional-quality judging that has the global-pole bias**. This directly motivates GPT Pro's v0.4 #11 **target-conditioned ("which is better *for* persona P") judging** as the load-bearing fix, over better profiles.

**Caveat.** Gemini's stated bases frequently cite the output *echoing contract phrasing* ("uses P1's exact 'checkable language' phrase"), so this is **discriminability, not demonstrated adaptation** — partly *surface contract-following*, not proof of deep behavioral embodiment. Single non-study coder (Gemini); the dario/pawl pair has the delta-form wrong-profile wrinkle (its C4_WRONG was conditioned on pawl's contract stored in "Everything in C3, plus" form) — so the clean text-level sign-flip is **2 of 3** global-pole pairs; the 93% CI also treats the 64×2 within-task judgments as independent (optimistic).

## Gate 3b — de-echoed blind recovery (first probe of the echo caveat)

`drivers/analysis/gate3b_*.py`. Masked every verbatim ≥4-gram overlap between each output and its **own conditioning contract** (`profile_text_supplied`) + a trait-word list, then re-ran the identical blind audit (same tasks/seed as Gate 3).

- **Only ~1.2% of output words were maskable as verbatim 4-gram echo** (median 0.7%, max 5.8%) — the outputs do *not* crudely copy their contracts.
- **De-echoed recovery: 0.963 [0.909, 0.986]** (n=108 judgments / 54 tasks; 10 tasks lost to a Gemini Pro daily-quota cutoff mid-run) — **unchanged from Gate 3's 0.93** (Δ +0.03, within noise).
- **Reading**: rules out *crude verbatim copying* as the driver of recovery. But the 4-gram mask cannot strip short distinctive phrases (e.g. "checkable language", "next 30 seconds") or paraphrased/stylistic echo — and the coder's bases still cite those — so **directive-following vs deep behavioral adaptation remains open**. The decisive test is the **neutral-paraphrase** recovery (rewrite outputs to a neutral house style preserving decisions/reasoning, strip style; v0.4 §10 #0), which is **blocked until the Gemini Pro quota resets** (~2026-06-18) — so it is deferred, not skipped.

---

## Combined reading (to feed the report §1, §4.1–4.3, §5, §8, §9, §11)

- **Structure** (any contract > no-profile): survives surface control, but trigger #7 shows it is **not judge-unanimous** — concentrated in opus-as-judge (~90%) vs gpt-as-judge (~50%). And C0 is not instruction-quantity-matched, so even the surviving part is "directive block vs none," not personalization. **Reword from "structure carries the floor" to "opus-as-judge rewards contract structure; gpt-as-judge largely does not."**
- **Specificity over generic**: does **not** survive surface control (Gates 1 + 1b). **Downgrade to a surface effect.** (Clears trigger #8.)
- **Matching** (right > wrong): survives surface + is judge-robust, but Gate 2 shows it is **mostly a global trait-pole preference, not target-matching** (3/4 pairs) — and **Gate 3 localizes this to the evaluation stage**: the *text is target-distinct* (93% blind recovery; all 3 global-pole pairs sign-flip at the text level), so the conditioning works; the unconditional-quality judges just don't reward target-fit (they prefer the opposite output in 25% of pairs). **Reword from "matching matters" to "conditioning produces target-distinct text, but the judges reward a global trait-pole, not fit-to-target; whether personalization helps a *specific* target needs target-conditioned judging (v0.4)."**
- **Public-anchor**: already downgraded by D4 (75% ties); judge-robust but mostly equipoise.
- **Net**: this pushes hard toward GPT Pro's adversarial conclusion — with one constructive sharpening from Gate 3. The honest v0.3 summary: *Persona conditioning reliably produces target-distinct outputs (generation works, ~93% blind-recoverable). But the LLM judges reward instruction-salient contract scaffolding (esp. opus-as-judge) and a global trait-pole, not fit-to-target: the specificity increment is surface (Gate 1/1b), the structure floor is largely an opus-as-judge effect (#7), and the "matching" increment is the judges' global-pole preference coinciding with the correct profile (Gate 2), not a reward for target adaptation (Gate 3). The bottleneck is evaluation, not generation — so v0.4's load-bearing move is target-conditioned judging + per-judge calibration, not better profiles.*
