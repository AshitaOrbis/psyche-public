# PsycheEval v0.4 — plan (evaluation-validity program)

**Status**: draft, 2026-06-17. Grounded in the v0.3 existing-data gate battery (`reports/analysis/gate_battery_findings.md`, report §4.5) and the GPT Pro round-2 forward-analysis (`reports/reviews/2026-06-17_gptpro_round2_response.md`).

## What v0.3 settled (and what it didn't)

The v0.3 forced-choice headlines, once stress-tested by the gate battery, relocate the story from generation to **evaluation**:

- **Specificity** (profile-specific contract > generic contract) does **not** survive surface control — not separable from the formatting it induces (Gates 1/1b).
- **Structure** (any contract > no-profile) is **not judge-unanimous** — concentrated in the opus-judge/gpt-author cell, confounded with author family (trigger #7).
- **Matching** (right profile > wrong profile) is mostly a **global trait-pole** preference, not target-fit (Gate 2, 3/4 reciprocal pairs) — and a global pole could be a judge bias *or* a real unconditional-quality gap; the design can't tell.
- **Generation** is not exculpated, but the conditioned outputs are at least **2-way blind-discriminable** (Gate 3, 93%; Gate 3b de-echo 0.96, ruling out crude verbatim copying). This is **discriminability, not demonstrated target-serving adaptation** — the coder held both briefs and may be rewarding directive-following / contract-echo.

**The one decisive open question**: is the discriminable persona-distinctness *target-serving* (genuine behavioral adaptation), or is it surface/directive-following that the unconditional-quality judges then fail to reward for the right reasons? v0.4 is the evaluation-validity program that answers it.

## Phase A — COMPLETE (2026-06-28) → Gate A→B verdict: **GO**

All 7 Phase A tests ran. Full write-up: `reports/analysis/phaseA_synthesis_gate_AB.md` (+ per-test `phaseA{1..7}_*_findings.md`). Headline:
- **Generation is genuinely target-serving** (not echo): #1 neutral-paraphrase recovery **0.906** (vs 0.93 raw) — survives stripping tone/format/phrasing; #7 67% behavioral-cited; #3 residual target-match survives.
- **Evaluation was the real, fixable bottleneck**: #2 target-conditioned judging recovers the target on **67%** of decisive global-pole cells (cross-provider); #4 the signal lives in **fit not quality** (fit_gap +1.03 vs quality_gap +0.34); #6 global-pole is position-robust; #5 judge-divergence is structure-specific (LR p≈4e-57).
- **Decision**: both A→B "go" halves met → **Phase B leads with target-conditioned judging at scale**, not better profiles. (Drivers: `drivers/analysis/phaseA{1,4,5}_*.py`, `gate{2_global_pole_reg,3_cited_basis,6_position_residuals}.py`; prompts `07c`/`07d`.)

---

## Phase A — cheap existing-data confirmations (run first; mostly no new generation)

These run on the v0.3 corpus and sharpen/confirm the gate reading before any expensive new generation. Ordered by decisiveness.

1. **Neutral-paraphrase blind recovery** *(Gemini-quota-gated; the decisive echo test)*. Rewrite each C4/C4_WRONG output into a neutral house style preserving decisions/reasoning/omissions/ordering/risk-posture, stripping tone/formatting/profile phrasing (paraphraser: a non-judge model, e.g. Sonnet; judge: Gemini, non-study). Re-run the Gate-3 audit.
   - recovery ≥ ~.75 → genuine behavioral adaptation; recovery → .50 → mostly surface/echo; .60–.70 → mixed.
   - The lexical Gate 3b (4-gram mask) already ruled out crude copying (0.96 unchanged); this is the stronger version. *Pipeline is built (`drivers/analysis/gate3b_*.py`) and adapts directly; blocked only by the Gemini Pro daily quota (resets ~2026-06-18).*
2. **Target-conditioned re-judging** of the existing AB/BA pairs: "which response is better **for persona P**?" (and re-ask for Q). If the target-conditioned judge sign-flips correctly where the unconditional judge shows global-pole → the evaluation prompt was the bottleneck (confirms the headline). Judges: gpt-5.5 + opus-4.7 (study judges, but now *target-conditioned*). The single most directly responsive test.
3. **Global-pole-index regression** (deterministic, no LLM): for each persona compute a global-desirability score (win rate when it is *not* the target), then model `win ~ target-match + global-pole-desirability + structure + surface + judge-family`. If the target-match term shrinks toward 0 once global-pole desirability is included, Gate 2's interpretation is confirmed by an independent method. *(Watch circularity — compute desirability leave-one-out.)*
4. **Persona-fit vs general-quality two-axis re-score**: judges rate each output on (a) general answer quality and (b) fit to target persona, separately (1–7). Test whether the two diverge (v0.3 predicts they do). Distinguishes "judge is biased" from "quality and target-fit genuinely trade off."
5. **Judge-family × contrast interaction model** (deterministic): `win ~ contrast + judge-family + contrast×judge-family + author-family + orientation + cluster`. Formalizes trigger #7 and tests whether the structure effect is genuinely judge-family-specific vs exposed by a few contrasts.
6. **Position/orientation residuals** (deterministic): does the Gate-2 global-pole survive separately in A-first and B-first? Rules out a presentation artifact.
7. **Cited-basis audit of Gate 3**: code Gemini's stated bases into {explicit echo, tone/style, format, behavioral choice, reasoning priority, omission, task strategy}; report recovery separately for behavioral vs surface bases.

## Phase B — new generation/judging (the v0.4 experiment proper)

Priority shifted by the gates: evaluation validity now outranks the content×form×salience design.

1. **Target-conditioned judging as the primary mode** (was GPT Pro #11; now #1). The construct is conditional; unconditional judging cannot measure it.
2. **Per-judge calibration + fully-crossed author×judge matrix**. Estimate each judge family's baseline structure preference and global trait-pole preferences; report judge-specific (not just pooled) results; cross author family with judge family so judge-side vs author-side is identified (resolves the trigger-#7 confound — GPT Pro threat #2).
3. **Trait-pole-balanced persona sampling + decoys**. Sample persona pairs where neither pole is obviously "better" under generic assistant norms (warmth/coldness, conscientiousness/spontaneity, assertiveness/humility, risk/safety, …); add decoys matched on verbosity/structure/confidence/warmth/safety so a global pole can't masquerade as matching (addresses Gate 2's confound at the source).
4. **Instruction-quantity-matched C0 controls**: `C0_STYLE_ONLY` (asks for the judge-preferred style, no persona), `C_PLACEBO_CONTRACT` (if-then skeleton, generic directives), `C0_LONG_NEUTRAL` (length-matched filler). If these approach C4, discount personalization heavily.
5. **Fully-crossed content × form × salience** (was the v0.3-forward #1; now below evaluation validity): Content {none/generic/correct/opposite/random} × Form {prose/trait-list/contract/hidden-summary/minimal-cue} × Salience {explicit-labels/behavioral-examples/de-labeled} × Length-matched. Real personalization ⇒ correct > opposite even with form/length/salience held, especially high-stakes.
6. **Profile-stakes scenario panel** (pre-registered high/med/low trait-divergence): personalization effects should concentrate in high-divergence scenarios; flat uplift ⇒ generic scaffolding.

## Decision gates

- **Gate A → B**: if Phase A's neutral-paraphrase recovery collapses toward .50 *and* target-conditioned judging does **not** sign-flip, the honest conclusion is "LLM judges reward instruction-salient scaffolding; persona-specific adaptation unproven" — and Phase B narrows to the evaluation-instrument work (1–4) rather than the full content×form design.
- **If neutral-paraphrase recovery stays high *and* target-conditioned judging sign-flips**: generation is validated and the bottleneck is confirmed to be the unconditional judge — Phase B leads with target-conditioned judging at scale.

## Explicit dead-ends (per GPT Pro)
More aggregate win-rate tables; more Wilson intervals (use clustered/hierarchical); more public-inspired personas via the same confounded packet process; more judge families without style-masked/gold calibration; profile-reference counts (replace with semantic alignment); equivalence-tests-alone for null steps (factorial ablation is the real fix).

## Carry-overs from v0.3 sign-off
- Phase 5 single-rater human check (trigger #3) — still open; v0.4 upgrades to ≥2 raters + a human cross-check of the Gate-3 blind coding.
- Ladder-specific deconfounding (the §4.3 single-path ladder) — fold into the factorial content×form design (resolution IV/V fractional factorial, randomize contract-first ordering independently of anti-mimicry and hints).
- Public-anchor isolation matrix (identified-public / deidentified / fictional-clone / name-only / placebo, same writer/template/length) — the clean v0.4 test the D4-downgraded v0.3 result needs.
