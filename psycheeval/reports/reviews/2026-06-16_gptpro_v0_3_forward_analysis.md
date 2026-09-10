# GPT Pro (GPT-5.5 Pro) — v0.3 Forward Analysis

**Date**: 2026-06-16
**Source**: ChatGPT Pro conversation `6a323602-...` (recovered live from DOM; the MCP capture truncated at the framing preamble — see §"capture note"). Full response ≈ 28.7k chars.
**Prompt**: post-publication-review v0.3 brief — asked for (A) analyses on existing data, (B) v0.4 experiments, (C) priority ranking; emphasis on discriminating real personalization from the shared-formatting-preference null.

> **Capture note.** The `chatgpt-pro` MCP reported `complete` at 5m with only the 351-char framing preamble — its completion detector fired during GPT Pro's long internal-reasoning pause. The body streamed in afterward; a live-DOM watcher captured the full 28.7k-char response. (Raw math notation was LaTeX that did not survive `innerText` extraction; this is the de-mathed distillation. Provenance URL above.)

---

## GPT Pro's headline verdict

> "v0.3 currently looks **much stronger as evidence that LLM judges reward directive/scaffolded answer-producing prompts than as evidence of true persona personalization**. The personalization interpretation is still viable, but it should be made to pass tests where mere formatting, generic helpfulness, and globally-preferred trait-poles cannot explain the wins."

This is the same central threat the Opus publication-review pass raised (shared cross-model formatting preference), sharpened into a falsification program. A credible personalization signal must satisfy: (1) correct-profile beats wrong-profile *after surface/style balancing*; (2) the preferred profile *flips when the target persona flips*; (3) the effect is *largest where the profile should change the answer*; (4) winners are *measurably more semantically aligned to the persona*, not just longer/more-structured; (5) it survives position/noise/tie modeling.

---

## A. Analyses runnable on the EXISTING data (ranked)

1. **Cross-fitted "shared-formatting-preference" style index (Very high / M).** Train a condition-blind style/reward-hack score (length, bullets/headings, imperatives, 2nd-person address, markdown density, refusal/hedging, "contract-likeness" classifier) **only on non-personalization contrasts** (C_GENERIC vs C0, C4_WRONG vs C0, C4 vs C4_shuffled, L2 vs L3), cross-fit by persona×scenario×author, then test whether the headline contrasts survive after removing ΔS — and on a **style-balanced subset** (|ΔS|<ε, or where the disadvantaged condition has equal/higher style score). *He calls this the single most important analysis; D3 alone is "too blunt."* Survives → personalization plausible; vanishes → it was formatting.
2. **Paired-choice deconfounding (Very high / M).** NOT a flat `winner ~ features + condition` regression (treats paired responses as independent). Use a Bradley–Terry / conditional-logit on the *paired difference* of D3 features + judge-specific slot-bias term + persona×scenario×author cluster, preserving AB/BA duplicates within cluster. Report each headline at 5 adjustment levels (unadjusted → slot-adjusted → D3-adjusted → +stylometry → style-matched). Surface features are post-treatment mediators — fine for adversarial diagnosis.
3. **Source-profile vs target-match decomposition (Very high / S–M).** The C4 > C4_WRONG "matching" result has a dangerous alternative: judges may globally prefer one trait-pole (warmth, conscientiousness, caution) regardless of target. Fit `μ·1[g=p] + ρ_g (global appeal of source profile) + surface`. **Decisive test: does the preferred profile FLIP with the target?** For target p, does profile-p beat profile-q, AND for target q does profile-q beat profile-p? Same profile winning both directions ⇒ global preference, not matching.
4. **Semantic persona-alignment audit (Very high / M–L).** Replace near-zero profile-reference counts with a *blind, behavioral* alignment score per output (direct-vs-gentle, risk-seeking-vs-averse, detail-vs-concise, validation-vs-solving, deference-vs-assertive, boundary-vs-accommodation), and ΔA = fit(o,p) − fit(o,q). Test (i) do C3/C4 raise target alignment vs C_GENERIC/C0; (ii) does C4_WRONG raise *opposite*-persona alignment; (iii) are judge wins associated with ΔA, not just ΔS. **Use a non-study-model or human coder** (study models may reproduce the shared preference); coding prompt asks for observable behaviors, not "which is better."
5. **Profile-stakes moderation (High / M).** Pre-code (blind) a trait-divergence score R_{p,s} per persona×scenario. Personalization predicts correct-profile advantage *grows with R*, wrong-profile-over-C0 *shrinks/reverses in high-R*, and C_GENERIC>C0 is *flat* across R (generic scaffolding). Shared-formatting null predicts broad, scenario-insensitive uplift. Strong falsifier.
6. **Latent measurement model over AB/BA + D1 + D4 + D2 (High / M).** Collapse each AB/BA pair to order-invariant {target wins both / split / loses both}; fit latent preference with judge-specific lapse ε_j (from D1) + position bias δ_j; D4 ties anchor the "no meaningful difference" threshold; D2 paired scalar deltas cross-check. Plus **uncertainty sensitivity**: re-estimate under multiway (persona, scenario, author, output-pair) and coarse persona-level clustering — if CIs widen materially (only 8 personas), soften the headline.
7. **Hierarchical network meta-analysis over all 26 pairs (High / M).** Bradley–Terry latent-utility decomposition: λ_c = β·(ContractLike, FrontLoaded, ScenarioHints, CorrectProfileContent, WrongProfileContent, PublicAnchor, AntiMimicry). Compare M_style vs M_style+match vs M_full by **leave-cluster-out** prediction. Style-only explaining the 26-contrast pattern ≈ as well as full ⇒ design doesn't identify personalization. (Design is collinear → diagnostic, not causal.)
8. **Public-anchor confound dissection (Medium-high / M).** Packet-level + output-level covariates (readability, concrete life-events, named entities, narrative specificity, lexical overlap, biographical allusions) on C5 vs C5_NONPUBLIC. **Hard limit: existing data cannot isolate the public-anchor effect** — at best shows whether it's robust enough to justify a clean v0.4 test.

## B. v0.4 experiments (ranked)

9. **Fully crossed content × form × salience design (Very high / XL)** — the core. Persona-content {none/generic/correct/opposite/random} × Form {prose/trait-list/contract} × Salience {front/buried/shuffled} × Length-matched. Real personalization ⇒ correct>opposite even with form/length/salience held constant, esp. high-stakes.
10. **Instruction-quantity-matched C0 controls (Very high / M)** — C0_LONG_NEUTRAL (length-matched filler), C0_STYLE_ONLY (asks for the judge-preferred style, no persona), C_PLACEBO_CONTRACT (if-then skeleton with generic/irrelevant directives). If these approach C4, discount personalization heavily.
11. **Target-swap judging (Very high / M)** — judge the *same* output pair twice, once "which is better for persona p?" and once "for persona q?". Preference should *reverse*. Holds surface form constant, varies only the eval target. (Partially runnable on existing outputs; formalize as a v0.4 sentinel.)
12. **High/med/low profile-stakes scenario panel (Very high / L)** — pre-register expected direction; personalization effects should concentrate in high-divergence scenarios.
13. **Factorial C5_CONTRACT ablation, not single-path ladder (High / L–XL)** — randomize contract-first ordering *independently* of anti-mimicry and hints (resolution IV/V fractional factorial), keep L0/L4 as anchors. Fixes the v0.3 ladder confound directly.
14. **Style-normalized & proposition-only judging (High / M–L)** — re-judge canonical-rewrite and action-extraction versions; contract advantages collapsing under normalization ⇒ surface-form, not content.
15. **Public-anchor isolation matrix (High / L)** — same writer/template/length: identified-public / deidentified-public / fictional-clone / name-only / fake-public placebo. Separates external-knowledge, name-priming, concreteness, style, trait content.
16. **Gold adversarial sentinels + decomposed human/external judging (High / M–L)** — pairs where persona-fit and polish conflict by construction (correct-but-blunt vs wrong-but-polished); judges score separate axes (task quality / persona fit / polish / safety / overall); stratified human subset. If LLM judges fail the gold sentinels, the main results are "LLM-judge style preference," not personalization.

## Explicit dead-ends (don't spend v0.4 budget here)

More aggregate win-rate tables; more Wilson intervals (use clustered/hierarchical); more public-inspired personas via the same confounded packet process; more judge families without style-masked/gold calibration; more profile-reference counts (replace with semantic alignment); equivalence-tests-alone for L1/L2 (factorial ablation is the real fix); repeating C5 vs C_GENERIC without style-matched packet controls.

## GPT Pro's strongest recommendation — three existing-data gates

Make the next decision depend on three analyses runnable **now**:
1. Does **C4 > C4_WRONG survive style-index balancing** (A1/A2)?
2. Does the **correct-profile preference flip in reciprocal opposite-persona tests** (A3)?
3. Are **winners semantically more aligned to the target persona, especially in high-stakes scenarios** (A4/A5)?

Pass ⇒ v0.3 has a plausible personalization signal worth the v0.4 program. Fail ⇒ the honest, sharper, still-valuable conclusion: *LLM judges reward instruction-salient scaffolding and contract-like generation; evidence for persona-specific adaptation remains unproven.*
