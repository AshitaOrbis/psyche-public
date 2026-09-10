# PsycheEval v0.3 — full-pilot tri-model report

**Tag**: `2026-05-19_v03`
**Supersedes**: v0.2 hard-pilot report (`psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md` and curated v0.2)
**Date**: 2026-06-16
**Canonical metrics**: `reports/metrics_2026-05-19_v03.json`
**Status**: curated draft; publication-review **rounds 1–2 applied** (2026-06-16/17; raw + consolidated findings in `reviews/`), **full-pool opus D1/D4 sentinels finalized** (2026-06-17; §4.4), and the **existing-data gate battery + GPT Pro round-2 forward-analysis applied** (2026-06-17; §4.5). Failure-triggers **#7 (FIRES — judge×author-cell structure preference) and #8 (specificity not robust to surface control)** are now run (§4.5/§8). Open before publication: **Phase 5 single-rater check (#3)**; the v0.4 de-echo / target-conditioned-judging tests that would convert "discriminable" into "target-serving" (§10). Note: full-pool D4 fired trigger #2 (high ternary-tie equipoise), downgrading the public-anchor claim — see §4.4 / §5.

This is a synthetic-personas **methodology pilot**, not a validation study. No claim here is about whether Psyche profiles help real users — that is the separate Phase 9 shadow-mode program (`docs/shadow_mode_validation_v04_design.md`), executed in v0.4.

---

## 1. TL;DR

v0.3 was designed at Phase -1 (predeclared 2026-05-19, before any generation) to answer four mechanism questions v0.2 surfaced, plus one methodology question. All four mechanism questions now have answers on the full corpus, judged by three model families (gpt-5.4, gpt-5.5-xhigh, Opus 4.7), AB/BA position-controlled, with cluster-bootstrap CIs.

> **Gate-battery update (read first; §4.5).** Post-hoc existing-data deconfounding materially revises three of the four readings below. The *specificity* increment (Q1) **does not survive surface control** (not separable from the formatting it induces); the *matching* effect (Q2) is **mostly a global trait-pole preference, not target-fit** (3/4 reciprocal pairs) — though a global pole could be genuine unconditional quality, not only judge bias (§4.5); and the *structure* floor is **not judge-unanimous** — it is concentrated in one judge×author cell (opus-judge/gpt-author, at or below chance for the other cell; the scope confounds judge family with author family). The constructive result: blind non-study coding shows the conditioned outputs are **2-way discriminable** (93% recoverable by a single coder *holding both briefs* — partly via surface contract-echo, so this is discriminability, **not** demonstrated behavioral adaptation). That makes the observed global-pole pattern at least partly an **evaluation-stage** artifact, and evaluation **the clearer bottleneck** — but it does not clear generation, because whether the distinctness is *target-serving* is exactly what v0.4's target-conditioned judging must test. (Gate 3 is a single-model, single-pass audit, n=8 per persona; treat 93% as a directional discriminability signal, not a measured rate.) Read the four forced-choice answers below as the surface; **§4.5 is the load-bearing correction**.

**The mechanism questions and what v0.3 found** (cross-provider, same-author scope; "win rate" = position-controlled decisive win rate; CIs are Wilson 95%; each is revised by the gate battery — §4.5):

1. **Does profile *specificity* matter, or just contract *structure*?**
   In forced choice, a profile-specific contract beats a structurally-identical *generic* contract: **C3 > C_GENERIC 57.1% [51.6, 62.4]**, **C4 > C_GENERIC 58.8% [53.3, 64.1]**, and the generic contract alone strongly beats no-profile (**C_GENERIC > C0 65.6%**). **But this specificity increment does *not* survive surface control** (Gates 1/1b, §4.5): once length/overlap/stylometry are balanced, C3/C4 > C_GENERIC is indistinguishable from chance — so it does not robustly demonstrate that profile-specific *content* helps beyond the formatting it induces (a post-treatment-mediator control, so this shows non-robustness, not that the content is inert). (Specificity over generic was already undetectable for the bare packet C5: C5 vs C_GENERIC 53.1% [45.4, 60.7].)

2. **Does profile *matching* matter, or any well-formed contract?**
   In forced choice the correct profile beats a *wrong* (opposite-trait) profile — **C3 > C4_WRONG 63.2% [57.8, 68.3]**, **C4 > C4_WRONG 61.2% [55.7, 66.4]** — and a *content* (non-formatting) signal survives surface control. **But the reciprocal sign-flip test (Gate 2, §4.5) shows that surviving signal is mostly a *global trait-pole* preference, not target-matching**: in 3 of 4 reciprocal pairs one persona's profile wins *regardless of which persona is the target* (a pattern consistent with either an evaluation bias *or* a real unconditional-quality gap between trait-poles — the design cannot distinguish them). A wrong profile also beats no-profile (**C4_WRONG > C0 61.5%**). And the structure floor is **not judge-unanimous** — it is concentrated in the opus-judge/gpt-author cell (trigger #7, §4.5). Blind non-study coding (Gate 3) shows the conditioned outputs are *discriminable* by persona (93% recoverable, partly via contract-echo), so the global-pole pattern is at least partly an **evaluation-stage** artifact — not proof that generation achieves target-fit, which remains open.

3. **Is the source-packet effect about the *public anchor* or just narrative form?**
   The public-anchored packet beats a trait-matched, length-matched *nonpublic* packet on the same persona: **C5 > C5_NONPUBLIC 62.0% [54.3, 69.2]**, and the same advantage appears with a contract present on both sides (**C5_CONTRACT > C5_NONPUBLIC_CONTRACT 62.0% [54.3, 69.2]**). This is **consistent with** a public-anchor contribution, but does not cleanly isolate it, and is **the weakest of the four findings**: the nonpublic packets were human-authored, so a residual prose-style difference the design cannot rule out is an alternative explanation (§9); the "contract held constant" arm matches the contract's *structure* but not its packet-derived *content*; and — most tellingly — under *ternary* judging (with an explicit "no meaningful difference" option) C5 vs C5_NONPUBLIC shows a **75% tie rate** (§4.4 D4), so the 62% forced-choice figure largely converts equipoise into a number. (The two contrasts coincide at 62.0% by marginal-total arithmetic on independent record sets — 58.8% cell-level agreement — not duplicated data; see §4.2 note.)

4. **What inside the C5_CONTRACT package does the work?**
   On the ablation ladder (L0=C5 → L1 minimal contract → L2 +anti-mimicry → L3 contract-first ordering → L4=C5_CONTRACT), **contract-first ordering is the only single-step addition that reaches detection**. The +feature side is at chance for the first two steps — L0→L1 (L1 47.5% [39.9, 55.2]) and L1→L2 (L2 51.6% [43.8, 59.4]) — and jumps at **L2→L3 (L3 69.7% [62.0, 76.4])**. Two cautions bound the reading: this is a *single-path* ladder, and the equivalence test was deliberately skipped (§2), so the first two steps are *not-detected*, not established-null — we cannot separate "ordering is causally privileged" from "ordering is where the accumulated structure crosses the detection threshold," nor rule out interactions. And since the L2→L3 jump is itself a contract-structure effect, trigger #7 (§4.5) implies it is plausibly the same opus-judge/gpt-author-cell structure preference rather than a generation-side mechanism.

**The methodology question** — how much of the AB/BA flip rate is position bias vs retest noise — is addressed by the same-orientation sentinel (D1), paraphrased-anchor sentinel (D2), and ternary tie sentinel (D4); see §4.4 and §7.

**One-line synthesis (gate-corrected)**: persona conditioning produces outputs that are *blind-discriminable* by persona (though partly via surface contract-echo, so target-*serving* adaptation is unproven), while the unconditional-quality judges reward contract scaffolding (concentrated in the opus-judge/gpt-author cell) and a *global trait-pole* more than fit-to-target — so the forced-choice win rates above are mostly a map of judge preference, and the clearer thing for v0.4 to attack is the **evaluation** stage (target-conditioned judging), not better profiles.

---

## 2. What changed from v0.2

| Axis | v0.2 | v0.3 |
|------|------|------|
| Authors | gpt-5.4, gpt-5.5-xhigh, Opus 4.7 | same |
| Judges | gpt-5.4, gpt-5.5-xhigh, Opus 4.7 | same |
| Scenarios / personas | 80 / 8 (4 PI, 4 PS) | same |
| Conditions | 8 | 8 + 7 new = 15 |
| New T1 conditions | — | C_GENERIC_CONTRACT, C4_WRONG_PROFILE, C5_NONPUBLIC, C5_NONPUBLIC_CONTRACT |
| New T2 ablation ladder | — | L1, L2, L3 (between C5=L0 and C5_CONTRACT=L4) |
| AB/BA | retrofitted late | mandatory from the start (`--ab-ba-mandatory`) |
| Sentinels | none | same-orientation (D1), paraphrased anchor (D2), ternary tie (D4) |
| Analyzer blocks | 17 | 21 (+ D1, D2, D3, D4) |
| Pair manifest | partial | full, predeclared at Phase -1.1 (28 pair types) |
| Failure criteria | implicit | 8 predeclared (Phase -1.11; §8) |
| D5 equivalence-margin TOST | proposed | **skipped** — power simulation confirmed ±5pp undecidable at any v0.3-feasible budget (Phase -1.8) |

---

## 3. Corpus and methods

### 3.1 Corpus counts (canonical metrics JSON)

| Element | v0.2 | v0.3 (this corpus) |
|---------|------|--------------------|
| Personas / scenarios / authors | 8 / 80 / 3 | same |
| Conditions | 8 | 15 |
| Assistant outputs | 1,680 | **2,757** (v0.3 7-condition set pooled with the v0.2 8-condition set) |
| Anchored scalar scores | 3,949 | **7,180** |
| Pairwise records (forced + AB/BA swap) | ~5,027 | **14,733** |
| D1 same-orientation sentinel | — | 503 (full pool, all 26 pair types) |
| D2 paraphrased-anchor sentinel | — | 646 (≈9% of pooled scalar; 15% of the v0.3-run scalar pool at collection time) |
| D4 ternary tie sentinel | — | 477 (full pool, all 26 pair types) |

**Pooling note (Path A).** The 7 new v0.3 conditions were generated and judged against the existing v0.2 baselines (C0/C3/C4/C5/C5_CONTRACT) by pooling the v0.2 corpus into the v0.3 run. v0.2 used the identical 80 scenarios and 8 personas, the same anchored 0–10 rubric, and the same forced-choice pairwise prompt, so the pool is methodologically clean. The cross-condition pairwise (v0.3 condition vs v0.2 baseline) is the new judging work; v0.2 within-baseline pairwise and all scalar scores are reused.

### 3.2 Model-version integrity (Opus 4.7)

All Opus calls in this corpus are **Opus 4.7**, pinned explicitly. The bare `opus` CLI alias rolled to Opus 4.8 in early June 2026; ~4,476 June-dated Opus pairwise records generated through the alias were 4.8. Those were purged (archived under `runs/2026-05-19_v03/archive_2026-06-16_pre_opus48_purge/` with a manifest) and regenerated on `claude-opus-4-7`. Opus scalar and the D2 paraphrased sentinel were pre-rollover (May, 4.7); the D1/D4 full-pool sentinel re-sample (2026-06-17) ran on the explicitly-pinned `claude-opus-4-7`. The entire Opus corpus is uniformly 4.7; zero duplicate pairwise keys verified. (Harness fix: `ModelSpec.cli_model` override pins the CLI `--model` to 4.7 while records stay labelled `opus`.)

### 3.3 v0.3 condition descriptions

| Code | Description | Persona scope |
|------|-------------|---------------|
| C_GENERIC_CONTRACT | Structurally C3-like contract, generic language, length-matched to C4 | all 8 |
| C4_WRONG_PROFILE | C4 template with an opposite-trait persona's profile substituted | all 8 |
| C5_NONPUBLIC | PI-matched fictional biographical packet (no public anchor), trait pattern preserved | PI 4 |
| C5_NONPUBLIC_CONTRACT | C5_NONPUBLIC + anti-mimicry contract wrapper | PI 4 |
| L1 | C5 + minimal contract, packet-first, no anti-mimicry, length-matched to C5 | PI 4 |
| L2 | L1 + anti-mimicry rules | PI 4 |
| L3 | L2 with contract-first ordering | PI 4 |
| (L0 = C5, L4 = C5_CONTRACT) | inherited from v0.2 | PI 4 |

### 3.4 Judges and rubrics

Three judges: `gpt-5.4`, `gpt-5.5-xhigh`, `opus` (Anthropic 4.7). Anchored 0–10 rubric (`06b`) for primary scalar; paraphrased-anchor rubric (`06c`) for the D2 sentinel; forced-choice pairwise (`07`) for primary pairwise; ternary tie/equipoise (`07b`) for the D4 sentinel. All claude-cli judging runs `--safe-mode` from a neutral cwd for context isolation (the profile-leak fix of 2026-06-09).

### 3.5 Pair manifest (Phase -1.1, predeclared)

- **T1 (16 pair types)**: C_GENERIC × {C0, C3, C4, C5}; C4_WRONG × {C0, C3, C4, C5}; C5_NONPUBLIC × {C5, C5_CONTRACT, C3, C4}; C5_NONPUBLIC_CONTRACT × {C5_NONPUBLIC, C5_CONTRACT, C3, C4}.
- **T2 (12 pair types)**: L0=C5 ↔ L1 ↔ L2 ↔ L3 ↔ L4=C5_CONTRACT consecutive; L1/L2/L3 vs C5 and C5_CONTRACT anchors; L1 vs C3, L2 vs C3, L3 vs C4.

All primary contrasts labelled PRIMARY / SECONDARY / EXPLORATORY before generation. No PRIMARY rows were added post hoc.

---

## 4. Findings — Tier 1 substantive (v0.3)

All rates below are **cross-provider, same-author, AB/BA position-controlled decisive win rates** with Wilson 95% CIs (cluster-bootstrap CIs, cluster unit = persona × scenario × author, 2000 resamples, are reported alongside in the metrics JSON and agree to within ~1pp; Appendix B). "Cross-provider" = the judge's model family differs from the author's. This controls **self-preference halo** (a model rating its own outputs higher); it does **not** control a halo *common to all three judges* — e.g., a shared learned preference for directive, front-loaded, instruction-salient text, which several conditions here (contract-first especially) produce by construction. See §9. n_clusters ≈ 239 for all-persona pairs; **≈ 120 for PI-only pairs (the entire §4.2 public-anchor and §4.3 ladder families)**, which therefore carry wider intervals by construction.

Multiplicity: the 26-pair manifest was predeclared (no post-hoc fishing), but the rates are not multiplicity-adjusted. Contrasts whose Wilson lower bound only just clears 0.5 (C3 > C_GENERIC 51.6; C4 > C_GENERIC 53.3; C4_WRONG vs C5 50.7) should be read as *suggestive, reliable-but-fragile*, not as strongly as the mid-60s contrasts whose CIs clear 0.5 comfortably.

### 4.1 Personalization probes — does specificity / matching matter?

| Contrast | Winner | Controlled win rate | Wilson 95% | Reading |
|----------|--------|--------------------:|-----------|---------|
| C_GENERIC vs C0 | C_GENERIC | 65.6% | [60.2, 70.6] | A generic behavioral contract beats no-profile |
| C3 vs C_GENERIC | C3 | 57.1% | [51.6, 62.4] | Specificity edge in forced choice — **does not survive surface control (§4.5)** |
| C4 vs C_GENERIC | C4 | 58.8% | [53.3, 64.1] | Same, with scenario hints — **does not survive surface control (§4.5)** |
| C5 vs C_GENERIC | — | 53.1% | [45.4, 60.7] | No detectable difference (CI straddles 0.5) |
| C4_WRONG vs C0 | C4_WRONG | 61.5% | [56.0, 66.8] | Even a *wrong* profile beats no-profile (opus-judge/gpt-author cell, §4.5) |
| C3 vs C4_WRONG | C3 | 63.2% | [57.8, 68.3] | Right beats wrong in forced choice — **mostly global-pole, not target-fit (§4.5)** |
| C4 vs C4_WRONG | C4 | 61.2% | [55.7, 66.4] | Same, with scenario hints |
| C4_WRONG vs C5 | C5 | 58.5% | [50.7, 65.9] | Bare source-packet beats a wrong-profile contract |

**Reading.** Two effects of comparable size stack on top of a baseline. (a) *Structure*: any well-formed contract — even generic, even mis-matched — beats no-profile by ~60–66%. Note C0 is not instruction-quantity-matched to the contract conditions, so this floor is "having a directive instruction block vs none," not yet separated from a generic more-instructions-→-better-output effect (the v0.2 ledger's length-matched C4 > C1_padded 62.3% addresses length but not instruction content). (b) *Content/matching*: a contract carrying the *correct* profile beats the *wrong* one by ~61–63%. The two signals are roughly equal in magnitude — and that is the report's own strongest caution on the personalization framing: a deliberately mismatched profile beats baseline (61.5%) nearly as much as the correct profile beats the wrong one (63.2%), so **at least half the over-baseline advantage is matching-independent**. "Personalization works" should be read as "having a contract works, and matching adds a comparable second increment." The specificity increment over a *generic* contract (C3/C4 > C_GENERIC ~57–59%) appears reliable but fragile in forced choice (lower CI bounds 51.6 / 53.3), is absent for the bare packet (C5 vs C_GENERIC straddles 0.5), and — per §4.5 — does not survive surface control.

**Gate-battery correction (§4.5).** Post-hoc deconfounding sharpens all three readings here. (a) The specificity increment **does not survive surface control** (Gates 1/1b) — once length/stylometry are balanced its CI includes 0.5; note these surface features are post-treatment mediators, so this is "not separable from the formatting it induces" rather than proof the content is inert (over-controlling a through-mediator pathway can manufacture a null). (b) The matching increment **survives surface control as a content (non-formatting) signal, but Gate 2 shows that same surviving signal is mostly a global trait-pole preference** (3/4 reciprocal pairs), so it is not a second, independent endorsement of target-fit — and a global pole is consistent with either a judge bias *or* a real unconditional-quality gap the design cannot distinguish. (c) The structure floor is **not judge-unanimous** — it is concentrated in the opus-judge/gpt-author cell (trigger #7: that cell rewards contracts 68–91%, the gpt-judge/opus-author cell at or below chance; judge family is confounded with author family, so this cannot be attributed to the judge side alone). The constructive result: the conditioned outputs are **blind-discriminable** (Gate 3, 93% by a single coder holding both briefs, partly via contract-echo), so the global-pole pattern is at least partly an **evaluation-stage** artifact — but this is discriminability, not demonstrated target-serving adaptation. The "matching adds a comparable second increment" framing should therefore be read as a statement about *judge preference*, not personalization efficacy.

### 4.2 Public-anchor isolation

| Contrast | Winner | Controlled win rate | Wilson 95% | Reading |
|----------|--------|--------------------:|-----------|---------|
| C5 vs C5_NONPUBLIC | C5 | 62.0% | [54.3, 69.2] | Public-anchored packet beats trait-matched nonpublic packet |
| C5_CONTRACT vs C5_NONPUBLIC_CONTRACT | C5_CONTRACT | 62.0% | [54.3, 69.2] | Public-anchor effect persists with contract held constant |
| C5_NONPUBLIC vs C5_NONPUBLIC_CONTRACT | C5_NONPUBLIC_CONTRACT | 71.1% | [63.6, 77.6] | Adding a contract to a nonpublic packet is the dominant move |
| C3 vs C5_NONPUBLIC | C3 | 69.2% | [61.6, 75.8] | Contract-only beats a nonpublic source packet |
| C4 vs C5_NONPUBLIC | C4 | 63.8% | [56.1, 70.8] | Same, with scenario hints |

**Reading.** The public-anchored packet carries a ~62% advantage over a trait-matched, length-matched nonpublic packet on the *same* persona, and the same advantage appears with a contract present on both sides (C5_CONTRACT vs C5_NONPUBLIC_CONTRACT, 62.0%). This is *consistent with* a public-anchor contribution — but two caveats keep it from being a clean isolation of "public anchor" vs "narrative form": (i) the nonpublic packets were human-authored, so a residual prose-style difference (§9) is an alternative explanation; (ii) the "contract held constant" arm matches the contract's structure but not its packet-derived content. The largest single move in this family remains adding a contract (71.1%), consistent with the §4.1 structural finding.

> **Note on the identical 62.0% values.** C5 vs C5_NONPUBLIC and C5_CONTRACT vs C5_NONPUBLIC_CONTRACT report a character-for-character identical point estimate and CI. This was audited against raw records: it is a genuine coincidence of marginal totals (each contrast: 98 public-wins / 60 nonpublic-wins / 2 ties of 160) computed from **independent** record sets with only **58.8% cell-level verdict agreement** — not duplicated data or a pipeline alias. The two contrasts corroborate the public-vs-nonpublic direction; they are not independent evidence streams (both isolate the same public-vs-nonpublic signal).

> **Ternary-tie caveat (full-pool D4).** When judges may decline a forced choice, C5 vs C5_NONPUBLIC is judged "no meaningful difference" **75% of the time** (n=12) and C5_CONTRACT vs C5_NONPUBLIC_CONTRACT 43% (n=14). The forced-choice 62% overstates a preference that is mostly equipoise; failure-trigger #2 fires here (§8). Treat the public-anchor result as suggestive at best, pending the cleaner v0.4 isolation matrix (§10).

### 4.3 C5_CONTRACT mechanism ablation ladder

Success criterion (v0.3 plan §8) was to *screen which component additions visibly contribute* — not to fully decompose interactions. Single-path ladder; interactions not identified.

| Step | Contrast | Controlled win rate of the +feature side | Wilson 95% | Marginal contribution |
|------|----------|------------------------------------------:|-----------|----------------------|
| L0→L1 | C5 vs L1 (contract presence) | 47.5% (L1) | [39.9, 55.2] | Not detectable (straddles 0.5) |
| L1→L2 | L1 vs L2 (anti-mimicry rules) | 51.6% (L2) | [43.8, 59.4] | Not detectable (straddles 0.5) |
| L2→L3 | L2 vs L3 (contract-first ordering) | **69.7% (L3)** | [62.0, 76.4] | **The dominant step** |

**Reading.** Of the components that distinguish C5 from C5_CONTRACT, **contract-first ordering is the only single-step addition whose marginal effect reaches detection in this one ladder ordering**. Adding a minimal contract (L0→L1) and adding anti-mimicry rules (L1→L2) each produce no detected preference *on their own, in this order*; placing the contract first (L2→L3) lands the +feature side at ~70%. Three constraints bound what this licenses: (a) it is a *single-path* ladder, so component effects are confounded with addition order and with each other (anti-mimicry might only register once the contract is front-loaded); (b) the equivalence test was deliberately skipped, so the first two steps are *not-detected*, not established-null — this is a preference-*pattern* result, not yet a mechanism decomposition; (c) L2→L3 is also the point of maximum accumulated structure, so "ordering is causally privileged" is not separable from "ordering is where the accumulated components cross the judges' detection threshold." The reward-hacking covariate regression that gated causal "mechanism" wording (trigger #8) has now run (Gates 1/1b, §4.5) and finds the *specificity* family is not robust to surface control; "mechanism" wording is still avoided here pending a ladder-specific deconfounding (and because the surface features are post-treatment mediators). Note the contract-first jump (L2→L3) is itself a contract-structure effect, and trigger #7 (§4.5) shows contract-structure preference is **concentrated in the opus-judge/gpt-author cell** — so the ladder's one detectable step is plausibly the same cell-specific structure preference, not a generation-side mechanism. (The L3→L4 length step and the L-vs-anchor contrasts are in Appendix C.)

### 4.4 Sentinel reads

- **D1 — same-orientation flip rate (retest noise floor).** Re-judging the same (run_a, run_b, judge) tuple *without swapping the Slot A / Slot B prompt order* isolates retest noise from position bias. **Full pool, all 26 pair types** (opus D1 re-sample completed 2026-06-17): corpus-mean flip **8.5%** (median 7.2%); only one pair exceeds 25% — C5_CONTRACT vs L3 at 36.4% (small n). The retest-noise floor is low, so the AB/BA flip rates reflect genuine position bias rather than re-judge instability for almost all pairs. Same-orientation flip exceeds the AB/BA position-flip rate on only **1 of 26 pairs**, so **failure-trigger #6 does not fire** — the AB/BA decomposition remains informative.
- **D2 — paraphrased-anchor consistency.** Re-scoring **646 scalar outputs** with reworded rubric anchors (≈ 9% of the 7,180 pooled scalar scores; the 15% sampling rate was applied to the v0.3-run scalar pool at collection time, before the v0.2 scalar was pooled in): corpus mean shift **+0.056** (negligible), corpus mean Spearman ρ **0.716**, max mean-shift observed **0.412** (under the 0.5-SD threshold), **min ρ 0.344** on one dimension/judge. The mean-shift side passes failure-trigger #1; the rank-stability side is borderline — most dimensions hold rank but at least one shows moderate anchor sensitivity. Scalar-supported claims are retained but flagged as anchor-sensitive on the weakest dimension (§8, trigger #1).
- **D3 — reward-hacking diagnostics.** Per-condition surface features (word count, profile-reference count, hedging, source-packet lexical overlap, refusal markers) are tabulated in the metrics JSON. Profile-reference counts are near-zero across conditions and lexical overlap with the source packet is low (≈0.10). This cuts *against* the simplest reward-hacking story (judges are not visibly rewarding outputs that name the profile) — but it is double-edged: if the correct-profile conditions win without being measurably more profile-grounded, *what* the judges are responding to is an open question, and a surface property the judges happen to like (structure, directiveness) is not yet excluded. The predeclared covariate-controlled logistic regression (winner ~ surface features + condition) — trigger #8 — **has now run** (Gates 1/1b, §4.5): the specificity increment is not robust to surface control, while matching and structure survive it. Because the surface features are post-treatment mediators, causal "mechanism" wording is still avoided; see §8.
- **D4 — ternary tie rate (this materially qualifies the forced-choice headlines).** Re-judging a ~10% sample with an explicit "no meaningful difference" option, **full pool, all 26 pair types** (opus D4 re-sample completed 2026-06-17): corpus-mean tie rate **31%**, and **14 of 26 pairs exceed the 25% trigger-#2 threshold**. The effect is concentrated exactly where it bites hardest: the public-anchor pair **C5 vs C5_NONPUBLIC has a 75% tie rate** (n=12; 9 of 12 judged "no meaningful difference"), and **C5_CONTRACT vs C5_NONPUBLIC_CONTRACT 43%** (n=14) — so when judges are *allowed* to decline, the public-anchor "advantage" largely dissolves into ties. The ladder middle is similar (L1 vs L2 32%, n=41; L2 vs L3 30%, n=50). **Failure-trigger #2 fires** for the C5_CONTRACT-edge pairs (§8). Interpretation: the forced-choice win rates in §4.1–§4.3 overstate the *strength* of preference — a 62% forced win on a pair with a 43–75% equipoise rate is a weak, often-absent preference that forced choice converts into a number. The per-pair ternary n is small (median ~14), so individual tie rates are noisy, but the direction is consistent across the high-tie pairs and is the single most important caution in this report after the shared-formatting null (§9).

---

### 4.5 Existing-data gate battery (post-hoc deconfounding — Gates 1, 1b, 2, 3, trigger #7)

After the primary analysis, five existing-data gates — specified by the GPT Pro forward-analysis (`reports/reviews/2026-06-16_gptpro_v0_3_forward_analysis.md`) and mapping onto predeclared failure-triggers #7/#8 — stress-tested whether the three personalization-relevant headlines (specificity, matching, structure) reflect target-specific adaptation or shared formatting / a global trait-pole preference. These are **post-hoc, exploratory** diagnostics (not predeclared contrasts); surface features are post-treatment mediators, so they are conservative adversarial controls, not clean causal estimates. Full detail and scripts: `reports/analysis/gate_battery_findings.md`, `drivers/analysis/gate{1,1b,2,3}_*.py`, `trigger7_judge_divergence.py`.

| Gate | Question | Result | Effect on headline |
|------|----------|--------|--------------------|
| **1 + 1b** (trigger #8) | Do headlines survive surface / stylometric control? | Specificity (C3/C4 > C_GENERIC) does **NOT** survive (surface-adjusted CIs include 0.5 under both a 3-feature and a 9-feature index; point estimates ≈ unchanged); matching (C3/C4 > C4_WRONG) and structure (> C0) **do** | **Specificity not separable from formatting** (mediator caveat below) |
| **2** | Is matching real target-fit, or a global trait-pole preference? (reciprocal sign-flip) | **3 of 4** reciprocal pairs are global-pole — one persona's profile wins regardless of which persona is the target | **Matching is mostly global-pole** (bias *or* a real quality gap — undetermined) |
| **3** | Are the conditioned outputs *discriminable* by persona? (blind, non-study coder; n=8/persona, single pass) | **Yes** — 93% blind recovery [0.872, 0.963]; 2 of 3 clean global-pole pairs sign-flip at the *text* level (both ≥0.75; dario/pawl confounded by delta-form reconstruction) | **Outputs are discriminable** (partly via contract-echo) → global-pole is at least partly evaluation-side |
| **#7** | Is "structure" judge-unanimous? | **No** — fires on 5/11 covered contrasts, all contract-structure; the opus-judge/gpt-author cell rewards contracts (68–91%), the gpt-judge/opus-author cell at or below chance (C5_CONTRACT vs C5 gpt_n=16) | **Structure floor is not judge-unanimous** (one judge×author cell; confounded) |

**Synthesis.** The three personalization-relevant claims are each undercut by a different gate, and jointly they paint a sharper picture than any single contrast — with one genuine but carefully-bounded constructive result. (a) The specificity increment over a generic contract **does not survive surface control** (Gates 1/1b) — its CI includes 0.5 once length/stylometry are balanced. The surface features are post-treatment mediators, so this is best stated as "not separable from the formatting it induces," not "the content is inert": controlling a mediator is conservative for the effects that *survive* but can over-control a genuine through-mediator effect into a *null*, so the specificity downgrade is "not robust," not "disproven." (b) The structure floor is **not judge-unanimous** (#7) — it is concentrated in the opus-judge/gpt-author cell (that cell rewards contracts 68–91%; the gpt-judge/opus-author cell sits at or below chance). Because the cross-provider scope ties judge family to author family, this cannot be attributed to the judge side alone — it is equally consistent with "gpt-authored contracts are more rewardable" — so the honest statement is "not judge-unanimous; concentrated in one judge×author cell." (c) The matching increment is mostly a **global trait-pole preference** (Gate 2, 3/4 reciprocal pairs) — though a global pole is consistent with *either* a judge bias *or* a real unconditional-quality gap between trait-poles, which this design (no ground-truth quality, no target-conditioned arm) cannot distinguish.

The constructive result, and its limits: **Gate 3 shows the conditioned outputs are 2-way *discriminable*** by a blind non-study coder (93% recovery; the cross-tab finds that in ~25% of pairs — ~16 of 64 tasks — the C4 output is recovered to its target yet the study judge preferred the opposite-conditioned output). That makes the global-pole pattern *at least partly* an **evaluation-stage** artifact. But three caveats keep this from "generation works": the coder *held both briefs* and did an easy 2-way attribution (not the judges' unconditional-quality call); its stated bases frequently cite surface **contract-echo**, so the 93% measures *discriminability*, not demonstrated behavioral **adaptation** (if it is mostly echo, "target-distinct" collapses toward "contract-distinct formatting" — the very shared-formatting null the report fights); and it is a **single model, single pass, n=8 per persona** (the 93% CI also treats 64×2 coupled judgments as independent, so it is optimistic). A first de-echo probe (**Gate 3b**, `drivers/analysis/gate3b_*.py`) masked every verbatim ≥4-gram overlap between each output and its own conditioning contract and re-ran the audit (54/64 tasks before Gemini quota cut off): recovery was **0.963 [0.909, 0.986]**, *unchanged* from Gate 3 — so the recovery is **not crude verbatim copying**. But only ~1.2% of output words were maskable as verbatim echo, and the coder's bases still cite short distinctive contract phrases, so this rules out *literal copying* only; *directive-following vs deep behavioral adaptation* remains open pending the **neutral-paraphrase** test (v0.4 §10 #0, the decisive version). So the defensible reframe is: *the unconditional-quality judges are the clearer bottleneck — they reward contract structure (in one judge×author cell) and a global trait-pole more than fit-to-target — and the outputs are at least blind-discriminable; whether that discriminability is **target-serving** (genuine adaptation) is open.* The decisive next tests (v0.4, §10) are **de-echoed / neutral-paraphrase blind recovery** (does discriminability survive removing contract phrasing?) and **target-conditioned judging** ("which is better *for* persona P?"). The C4-vs-C4_WRONG contrast asked for *unconditional* quality with no persona reference, so it was never a test of fit-to-target in the first place.

---

## 5. Findings — retractions and non-results

No v0.3 *pairwise* headline reversed direction under triangulation, but **the post-hoc gate battery (§4.5) downgraded three of the headline readings**, and the D4 sentinel weakened a fourth:

- **Specificity over generic → downgraded (post-hoc, exploratory)** (Gates 1/1b): C3/C4 > C_GENERIC does not survive length/stylometry control (CI includes 0.5). Because surface features are post-treatment mediators this is "not separable from the formatting it induces," not "disproven" — but it is no longer counted as robust evidence that profile-specific content helps.
- **Matching → downgraded to mostly a global trait-pole preference (post-hoc, exploratory)** (Gate 2): 3/4 reciprocal pairs are global-pole, not target-matching (a pole that could be bias *or* a real unconditional-quality gap). Gate 3 shows the outputs are at least *discriminable* by persona (93%, single coder, partly via contract-echo), so the shortfall is *at least partly* evaluation-stage — but Gate 3 establishes discriminability, not target-serving adaptation.
- **Structure floor → downgraded; not judge-unanimous (post-hoc, exploratory)** (trigger #7): "any contract beats baseline" is concentrated in the opus-judge/gpt-author cell (confounded with author family), not unanimous across judges.
- **Public-anchor → substantially weakened** by the full-pool D4 ternary sentinel (75% tie rate on C5 vs C5_NONPUBLIC; failure-trigger #2 fires): downgraded to "suggestive, pending a cleaner v0.4 test."

The matching and ladder findings survive *in direction* but with the §4.4-D4 caveat that forced-choice win rates overstate preference strength on higher-tie pairs, and the §4.5 caveat that they track judge preference more than target-fit. Scalar-supported claims additionally carry the trigger-#1 anchor-sensitivity flag (§4.4 D2). Two predeclared null/near-null results are reported as such rather than buried:

- **Specificity is undetectable for the bare source packet** (C5 vs C_GENERIC 53.1%, CI straddles 0.5) — and, per Gate 1/1b (§4.5), the forced-choice specificity edge a *contract* shows over generic (C3/C4 > C_GENERIC) does not survive surface control either. So specificity-of-content is not robustly demonstrated in either carrier.
- **Two of three ablation-ladder steps are individually null** (L0→L1, L1→L2). Reported as the intended screening result, not a failure.

The v0.2 retraction of C5_CONTRACT > C3 / C5_CONTRACT > C4 stands (no detected preference; §6). v0.3 did not attempt to convert "no detection" into "established equivalence" — the D5 TOST was skipped after the Phase -1.2 power simulation showed ±5pp undecidable at any feasible budget.

---

## 6. Inherited v0.2 findings (carried over; AB/BA position-controlled where tested)

From the canonical claim ledger (Appendix A):

| Claim | Controlled rate | CI | Status |
|-------|----------------:|----|--------|
| C0 (no-profile) was dominated by every profile condition | ~86% (C4 over C0, original forced pairwise) + scalar Δ_total +6.08 | — | Large; **not** AB/BA-tested directly (the only row here without position control; magnitude far exceeds the ~15–17pp position-bias band, so likely robust) |
| C4 > C1_padded (length-matched) | C4 62.3% | [56.1, 68.3] | Holds; length- and position-controlled |
| C4 > C5 | C4 68.0% | [61.5, 74.4] | Holds in direction; "judge-unanimous" descriptor is from the broader-scope v0.2 analysis — under v0.3 cross-provider same-author scope this contrast has only one judge-family cell (trigger #7 coverage gap, §4.5), so judge-unanimity is **not re-verified here** |
| C5_CONTRACT > C5 | C5_CONTRACT 67.7% | [61.7, 73.3] | Holds in aggregate, but **trigger #7 fires** (opus-judge 0.68 / gpt-judge 0.44, Δ24pp, gpt_n=16; §4.5) — the contract preference is concentrated in the opus-judge/gpt-author cell, not judge-unanimous |
| C4 > C4_shuffled (Tier 1.5) | C4 57.8% | [52.2, 63.8] | Modest; meaningfully smaller than the above |
| C5_CONTRACT vs C3 | 49.9% (no detected preference) | [44.3, 55.7] | Retained retraction |
| C5_CONTRACT vs C4 | 51.8% (no detected preference) | [46.0, 57.5] | Retained retraction |

The §4.3 ablation ladder is the v0.3 follow-through on "C5_CONTRACT > C5, mechanism not isolated" (v0.2's open item): the only single-step addition that reaches detection is contract-first ordering, but the mechanism remains unresolved (single-path ladder; the jump is itself a contract-structure effect, which trigger #7 ties to the opus-judge/gpt-author cell).

---

## 7. Methodology contribution

v0.2's methodology contribution was quantifying per-judge slot-B (later-answer) preference: GPT-5.5-xhigh 25–31pp, Opus 4.7 9–24pp (content-varying), GPT-5.4 negligible. v0.3 extends the position-bias toolkit:

- **AB/BA mandatory from generation** (not retrofitted), so every primary pairwise claim is position-controlled by construction.
- **Same-orientation sentinel (D1)** decomposes the AB/BA flip rate into position bias vs retest noise: a flip under *swapped* order net of the *same-order* flip rate is position bias; the same-order flip rate alone is retest noise (~10–30% on covered pairs).
- **Paraphrased-anchor sentinel (D2)** tests whether the 0–10 scalar rubric is anchor-sensitive: mean shift negligible (+0.056), rank stability mostly good (ρ 0.716) but borderline on one dimension.
- **Ternary tie sentinel (D4)** surfaces forced-choice equipoise: ladder-middle pairs carry ~21–23% genuine ties, distinguishing "no preference" from "weak preference."
- **Predeclared pair manifest at Phase -1** eliminates the post-hoc expansion confound that the v0.2 reviewers flagged.

The position-bias finding is scoped to this corpus, prompt, judge set, and protocol; it is consistent with prior LLM-as-judge position-bias literature (Zheng et al. 2023; Shi et al. 2024) and is **not** a claim that all LLM judges show slot-B preference (GPT-5.4 here did not).

---

## 8. Failure-trigger checks (Phase -1.11, predeclared)

| # | Trigger | Status | Notes |
|---|---------|--------|-------|
| 1 | Paraphrased anchor ≥0.5 SD mean shift OR rank changes (ρ < ~0.7) | **PARTIAL** | Mean shift passes (max 0.41 < 0.5 SD). Mean ρ 0.716 ≈ threshold; min ρ 0.344 on one dim/judge. Scalar claims retained but flagged anchor-sensitive on the weakest dimension. |
| 2 | Tie rate > 25% on a C5_CONTRACT-edge pair | **FIRES** | Full pool: C5_CONTRACT vs C5_NONPUBLIC_CONTRACT 43% (n=14), C5_CONTRACT vs L3 38% (n=13), C5_CONTRACT vs C5_NONPUBLIC 25%; and the public-anchor C5 vs C5_NONPUBLIC 75% (n=12). 14/26 pairs >25% (mean 31%). **Effect**: the public-anchor and ladder *package* claims are downgraded — forced-choice wins overstate preference strength (§4.4 D4, §4.2). |
| 3 | Author-rater agreement < 60% | **PENDING** | Phase 5 single-rater sanity check not yet run (toolkit ready; full pool now available to sample). |
| 4 | C4_WRONG beats C_GENERIC > 55% | **PASS (no fire)** | C4_WRONG vs C_GENERIC is within the manifest; both clear C0 but neither dominates the other beyond noise — personalization claim (right > wrong, §4.1) is not undermined. |
| 5 | C5_NONPUBLIC indistinguishable from C5 (point effect < 5pp from chance) | **PASS — no fire** | C5 > C5_NONPUBLIC 62.0% = 12pp above chance (Wilson lower bound 54.3 = 4.3pp above chance). The point effect exceeds the 5pp MCID, so the "indistinguishable" trigger does not fire; the CI lower bound is a separate caution noted in §4.2. |
| 6 | Same-orientation flip ≥ AB/BA flip on > 50% of pairs | **PASS — no fire** | Full pool: same-orient flip ≥ AB/BA flip on only 1/26 pairs; corpus-mean same-orient flip 8.5%. AB/BA decomposition remains informative (§4.4 D1). |
| 7 | Opus vs OpenAI divergence > 0.15 on a T1 pair | **FIRES** | Per-judge-family win rate (`drivers/analysis/trigger7_judge_divergence.py`): **5 of 11 covered contrasts diverge >15pp**, every one a contract-structure comparison — **C_GENERIC vs C0** (opus-judge 0.91 / gpt-judge 0.50, Δ41pp), **C4_WRONG vs C0** (0.90/0.41, Δ49pp), **C5 vs C_GENERIC** (0.32/0.65, Δ33pp), **C5 vs C4_WRONG** (0.37/0.66, Δ29pp), **C5_CONTRACT vs C5** (0.68/0.44, Δ24pp). Matching (C3/C4 vs C4_WRONG ≤7pp) and public-anchor (≤3pp) do NOT diverge. **Effect**: the structure/floor claim is **not judge-unanimous** — it is concentrated in the opus-judge/gpt-author cell; §4.5, §4.1, §6 reworded. **Confound (load-bearing)**: cross-provider scope ties judge family to author family (opus-judge⟺gpt-author, gpt-judge⟺opus-author), so the divergence cannot be attributed to the judge side alone — it is equally consistent with gpt-authored contracts being more rewardable. (The C5_CONTRACT vs C5 row rests on gpt_n=16 — lower weight than the others. Inherited C4>C5 / C4>C1_padded / C4>C4_shuffled lack both-judge coverage under v0.3 scope.) |
| 8 | Reward-hacking: > 50% of preference explained by length + profile-refs | **FIRES (partial)** | Covariate-controlled logistic deconfounding now run (Gate 1 + 1b, `drivers/analysis/gate1{,b}_*.py`): **specificity over generic does NOT survive surface control** — C4/C3 > C_GENERIC surface-adjusted CIs include 0.5 (3-feature and 9-feature stylometric index agree). This is a *post-hoc, mediator-laden* regression (surface features are post-treatment), so it shows the increment is **not robust to surface control**, not that the content is causally inert. Matching (C3/C4 > C4_WRONG) and structure (vs C0) **do** survive surface control. **Effect**: the specificity leg is downgraded as not robust (§4.1, §4.5, §5); "mechanism" wording remains avoided. Near-zero profile-reference / tailoring-marker variance independently confirms judges do not reward profile-naming. |

Among the **completed** checks, **three fired** — **#2** (ternary-tie equipoise on the C5_CONTRACT-edge and public-anchor pairs; §4.4 D4), **#7** (opus-vs-OpenAI judge divergence on the contract-structure contrasts; §4.5), and **#8 partial** (specificity-over-generic does not survive surface control; §4.5) — and **#1 is PARTIAL**. One remains **open**: #3 (Phase 5 single-rater). **The predeclared "≥3 fired → open with a *what didn't work* section" threshold is now MET**: this report's framing is correspondingly skeptical (the executive summary and §4.5 lead with what the gates undercut), and the existing-data gate battery (§4.5) is the *what-didn't-replicate* accounting. The gate is not final until #3 (Phase 5) closes — the sign-off checklist tracks it.

---

## 9. Limitations

- **The strongest skeptical reading — "this measures judge formatting preference, not personalization."** The single biggest threat to interpretation is that the entire win-rate structure is a composite of (i) a *cross-model shared* stylistic preference for directive, front-loaded, instruction-salient text — which cross-provider scoping does **not** control, because it is common to all three judge families; (ii) generic instruction-quantity effects (any contract vs none); and (iii) human-authorship style artifacts in the nonpublic packets. Each of these predicts exactly the observed pattern — directive contracts beat narratives, contract-first beats buried-contract, any contract beats baseline — without any of it being about personalization fidelity. The D-series sentinels constrain *position/retest/anchor/tie* noise but do not target this null; **the post-hoc gate battery (§4.5) now does, and resolves it into three *distinct* nulls rather than one shared one**: (i) a surface/stylometry effect (Gates 1/1b — the specificity increment does not survive surface control); (ii) a judge×author-cell structure preference (#7 — and note this points *against* the "shared across all judges" framing: the contract preference is concentrated in the opus-judge/gpt-author cell, not common to all three families); and (iii) a global trait-pole preference (Gate 2 — a *content* preference, not a stylistic-formatting one). Two facts inside the primary analysis already pointed the same way: a *wrong* profile beats baseline nearly as much as the right profile beats the wrong one (§4.1), and correct-profile wins leave near-zero differential profile-grounding (§4.4 D3). **What the gates do *not* establish is that generation is exculpated**: Gate 3 shows the conditioned outputs are blind-*discriminable* (93% by a single coder holding both briefs, partly via contract-echo) — that locates the global-pole confound *at least partly* at the *evaluation* stage, but discriminability is not target-serving adaptation, so generation is not cleanly cleared. The findings are therefore reported as patterns in how the judge families respond to conditioning variants — patterns that are mostly judge-side formatting/pole preference — and whether *target-conditioned* judging would reward genuine fit is exactly what v0.4's construct-validity program must test. (Limitations of the gates themselves: surface features are post-treatment mediators (over-control can manufacture a null); trigger #7's judge/author confound; Gate 3's single non-study coder (n=8/persona), which may reward surface contract-echo; the global-pole-as-real-quality alternative; the dario/pawl delta-profile wrinkle. See §4.5.)
- **Cross-provider controls self-preference, not shared priors.** "Cross-provider" neutralizes a model preferring its own outputs; it does not neutralize a preference shared across all three judges (§4 intro, above).
- **Public-anchor confound.** C5_NONPUBLIC packets are human-authored to match traits and length; residual prose-style differences from the public-anchored packets could contribute to the §4.2 effect. The same advantage under contract-present-on-both-sides mitigates but does not eliminate this (the contract's structure is matched, its packet-derived content is not).
- **Ablation ladder is single-path.** L0→L1→L2→L3→L4 tests marginal additions in one order; component effects are confounded with addition order and with each other, and the two undetected steps are *not-detected*, not established-null (equivalence test skipped). Interactions are not identified.
- **Sentinel sample sizes.** The full-pool opus D1/D4 sentinels now span all 26 pair types, but the ~10% sampling leaves small per-pair n (D4 median ~14), so individual per-pair tie/flip rates are noisy even though the corpus-level pattern (high ternary equipoise; low retest noise) is clear.
- **Human-rater check not yet run** (Phase 5); single-rater by design (n=1 sanity check, not calibration). v0.4 upgrades to ≥2 raters.
- **Still synthetic personas.** No construct-validity bridge to real users; that is the Phase 9 / v0.4 shadow-mode program.

---

## 10. v0.4 priorities

The gate battery (§4.5) makes evaluation the clearer bottleneck, so v0.4 leads with judge-side fixes, and with two cheap **existing-data** tests that would convert v0.3's "discriminable" into "target-serving" (or refute it). Full sequenced plan with decision gates: `docs/v0_4_plan.md`.

0. **(Cheap, existing data) De-echoed / neutral-paraphrase blind recovery + target-conditioned re-judging.** (a) Re-run the Gate-3 blind audit on outputs with persona/contract phrasing masked or neutral-paraphrased (decisions/reasoning preserved): if recovery stays ≥~0.75 it is behavioral adaptation; if it collapses toward 0.5 it was contract-echo. (b) Re-judge the existing AB/BA pairs target-conditioned ("better *for* persona P?"): if the target-conditioned judge sign-flips correctly where the unconditional judge shows global-pole, the evaluation-bottleneck reading is confirmed (GPT Pro round-2). Also cheap: a global-pole-index regression (`win ~ target-match + global-pole desirability + structure + surface + judge family`) and a persona-fit-vs-general-quality two-axis re-score.
1. **Target-conditioned judging** (as a primary mode, not just a re-judge) — judge "which response is better *for persona P*?" (and re-ask for persona Q), not unconditional quality. This is the test of whether the distinctness *serves the target*; it holds surface constant and varies only the eval target (GPT Pro v0.4 #11).
2. **Per-judge calibration + trait-pole-balanced design** — trigger #7 shows the structure floor is concentrated in one judge×author cell and Gate 2 shows a global trait-pole bias, so fully cross author×judge family, report per-judge-family results as primary (not just pooled), and balance persona sampling across trait-poles (with decoys matched on verbosity/structure/warmth/safety) so a global pole cannot masquerade as matching.
3. **Instruction-quantity-matched C0 controls** — `C0_STYLE_ONLY`, `C_PLACEBO_CONTRACT`, `C0_LONG_NEUTRAL` — to separate "directive block vs none" from personalization (GPT Pro v0.4 #10).
4. **Shadow-mode validation** at the Psyche public results page (`docs/shadow_mode_validation_v04_design.md`).
5. **≥2-rater human calibration** for inter-rater reliability (and a human cross-check of the Gate 3 blind-coding, replacing the single non-study coder).
6. **Long-horizon profile-realism conditions** (stale, contradictory, user-edited, compressed); **multi-turn interaction tests**; **adversarial profile robustness**.
7. **Equivalence-margin TOST** revisited with shadow-mode-calibrated MCID and tighter ICC estimates.

---

## 11. Closing

v0.3 set out to take the v0.2 "behavioral contracts beat trait conditioning" result apart and ask *which part does the work*. The forced-choice surface showed a layered structure — a well-formed contract as the largest factor, with correct-profile and public-anchor increments on top. **The existing-data gate battery (§4.5) then relocated the explanation toward the judge.** Two of the personalization-relevant layers do not survive scrutiny: the specificity increment does not survive surface control (it is not separable from the formatting it induces), and the structure floor is not judge-unanimous (it is concentrated in the opus-judge/gpt-author cell — which the design cannot cleanly attribute to the judge rather than the author). The matching layer is real in forced choice but is mostly a *global trait-pole* preference — which could be a judge bias *or* a genuine unconditional-quality gap the design cannot distinguish. The constructive counterweight, carefully bounded: blind non-study coding shows the conditioned outputs are at least **2-way discriminable** by persona (93% recoverable by a single coder holding both briefs — but partly via surface contract-echo, so this is discriminability, not demonstrated target-serving adaptation). That places the global-pole confound *at least partly* at the **evaluation** stage and makes the unconditional-quality judge the clearer thing to fix — but it does not establish that generation succeeds at personalization, because whether the discriminable distinctness actually *serves* the target is undetermined here. So the safest summary remains largely descriptive, now with a directional lead: the unconditional-quality judges reward contract scaffolding (in one judge×author cell) and a global trait-pole more than fit-to-target, while the conditioned text is at least blind-discriminable. That reframes v0.4 — **target-conditioned ("better *for* persona P") judging, de-echoed/neutral-paraphrase recovery, per-judge calibration, and trait-pole-balanced persona sampling become the priority over better profiles** — and it sharpens the construct-validity question rather than answering it: does target-distinct text actually serve the target? Only judging that asks that question, on de-echoed outputs, can say.

---

## Appendices

- **A. Claim ledger** — canonical per-claim summary with allowed/forbidden wording, controlled rates, evidence paths: `reports/metrics_2026-05-19_v03.json` → `claim_ledger.rows` (8 rows; rendered in the autogen scaffold).
- **B. Cluster-bootstrap CI methodology** — cluster unit = persona × scenario × author; 2000 resamples; Wilson + bootstrap CIs side by side (carried from v0.2 appendix).
- **C. Full per-pair AB/BA tables** — `pairwise.cluster_bootstrap_ci_cross_provider_same_author` (all 26 pair types), plus same-provider and pooled scopes for halo comparison.
- **D. Provenance** — v0.3 plan: `docs/v0_3_plan.md`; Phase -1 design-lock: `docs/v0_3_phase_minus_1_design_lock.md`; 3-reviewer consolidated review: `reports/reviews/2026-05-18_consolidated_v0_3_plan_review.md`; Path A + 4.7 fix: `docs/v0_3_status_2026-06-16_pathA_complete.md`; Phase 9 design: `docs/shadow_mode_validation_v04_design.md`.

---

## Sign-off checklist

- [x] All headline numbers sourced from canonical metrics JSON
- [x] Inherited v0.2 claim ledger re-verified on this corpus
- [x] Sentinel reads — D2 complete; D1/D4 full-pool opus re-sample finalized 2026-06-17 (trigger #2 fires; §4.4)
- [x] Failure-trigger #7 (opus vs OpenAI divergence) — **run, FIRES** on the contract-structure contrasts (§4.5)
- [x] Failure-trigger #8 (reward-hacking regression) — **run via Gate 1/1b**, specificity does not survive surface control (§4.5)
- [x] Existing-data gate battery (Gates 1, 1b, 2, 3 + #7) — `reports/analysis/gate_battery_findings.md`; §4.5
- [ ] Phase 5 single-rater sanity check (trigger #3)
- [x] `/publication-review` 3-reviewer panel — round 1 applied (GPT-5.5 / Gemini 3.1 Pro / Opus)
- [x] GPT Pro forward-analysis pass (round 1) — three existing-data gates specified (`reports/reviews/2026-06-16_gptpro_v0_3_forward_analysis.md`)
- [ ] GPT Pro round-2 pass on gate results; `/publication-review` round-2 delta after Phase 5
