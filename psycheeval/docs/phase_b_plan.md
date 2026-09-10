# PsycheEval v0.4 — Phase B implementation plan (DRAFT, pending execution approval)

> **Status**: proposed, not executed. Scope forks **decided (2026-06-28)** — see §9. Awaiting explicit go-ahead to execute B1 (and to draft `docs/prereg_B1.md`).
>
> **Decisions locked (2026-06-28):**
> 1. **Sequencing — B1-first as a hard gate on B2.** Rescale the existing corpus before any new generation.
> 2. **B1 Opus budget — fund the FULL 3×2 author×judge cross**, including the same-provider halo (not just cross-provider-primary). Opus B1 ≈ 1,434 cap-bound calls.
> 3. **B2 breadth — deferred.** No B2 sizing now; pre-register B2 (`docs/prereg_B2.md`) after B1 results, using B1's observed effect size for the power calc.
> **Inputs**: `reports/analysis/phaseA_synthesis_gate_AB.md` (Gate A→B = GO), `docs/v0_4_plan.md` (Phase B), `docs/phase_b_handoff.md`.
> **Constraints (hard)**: all Opus eval calls pinned to `claude-opus-4-7` (`llm.py` `cli_model`); cross-provider judging (gpt↔opus-authored) is PRIMARY, same-provider is halo-audit secondary; Max-plan cap is the binding bottleneck — stage cap-free GPT/codex + deterministic numpy before any Opus.

---

## 0. The one-paragraph version

Phase A proved generation is genuinely target-serving (#1 neutral-paraphrase recovery 0.906) and that the v0.3 "matching fails" result is a **fixable evaluation-instrument artifact** (#2 target-conditioned judging recovers the target on 67% of decisive cells; #4 the signal lives in *fit* not *quality*). But #2/#4 were deliberately quick: single A/B orientation, forced-choice, no per-judge calibration, n=18 decisive cells, one coder. **Phase B's job is to convert those validated probes into headline-grade measurement, then — only if they survive scaling — commit to new trait-pole-balanced generation.** I recommend a **two-stage split**: **B1** hardens the measurement on the *existing* v0.3 corpus (cap-cheap, mostly GPT + deterministic), and **B2** runs the new generation + full content×form×salience factorial, **gated on B1** confirming target-conditioned judging holds at scale. Pre-register both before running.

---

## 1. Scope recommendation: B1 (existing-corpus rescale) FIRST, then B2 (new generation), gated

The handoff's open scope question is "(a) re-judge existing corpus at scale first, vs (b) jump to new generation." **Recommendation: (a)-first, as a hard gate on (b).** Five reasons:

1. **Phase B priorities #1 and #2 are *both* achievable on the existing corpus with no new generation.** The corpus already contains the full grid we need: **239 matched C4/C4_WRONG pairs** (gpt-5.5: 80, gpt-5.4: 80, opus: 79) across a **3-author × 2-judge** matrix. That 3×2 cross is exactly what resolves the trigger-#7 / #5 judge-family-vs-author-family confound (priority #2) — and it's sitting in `runs/2026-05-19_v03/` already.
2. **It de-risks the expensive part.** B2 (trait-pole-balanced generation + decoys) is designed to kill β_pole *at the source*. But if the 67% target-recovery degrades toward 0.50 once we add AB/BA + a tie option + per-judge calibration at full N=239, that *changes the B2 design* (we'd need a stronger judge ensemble or different decoy construction). Better to learn that for the price of GPT calls than after a multi-thousand-generation run.
3. **Cap economics strongly favor it.** The bulk of B1 is cap-free: GPT-5.5 via codex (separate quota) judges the cross-provider-primary opus-authored cells, and the global-pole calibration is deterministic numpy over the existing 13k-record swap corpus. Opus is needed only for its cross-provider-primary slice (judging gpt-authored), bounded and fully checkpoint-resumable.
4. **Most B1 infrastructure exists.** `phaseA2_target_judge_run.py` is the parametrized, resumable, cross-provider template; `07c` (target-conditioned) and `07d` (two-axis) are validated; AB/BA swap machinery and a ternary-tie prompt (`07b`) already exist (`pairwise_swap_scores.jsonl` 13k rows, `pairwise_ternary_scores.jsonl`). Marginal engineering is small.
5. **It pays down owed caveats directly** — larger decisive N, AB/BA, tie option, per-judge calibration, ≥2-coder human cross-check — turning Phase A's directional 67% into a defensible headline before any new claim rests on new data.

**What B1 *cannot* do (and therefore B2 must):** the instruction-quantity-matched controls (`C0_STYLE_ONLY`, `C_PLACEBO_CONTRACT`, `C0_LONG_NEUTRAL`), trait-pole-balanced personas with surface-matched decoys, and the fully-crossed content × form × salience factorial all require new generation. These are B2.

---

## 2. Phase B1 — measurement hardening on the existing corpus (cap-light)

**Goal**: produce the headline-grade, pre-registered version of Phase A #2/#4 — target-conditioned judging at full scale with position counterbalancing, a tie option, per-judge calibration, and a fully-crossed author×judge matrix.

### B1.1 Target-conditioned judging at scale (priority #1)
- **Universe**: all **239** matched C4/C4_WRONG pairs (not the 64-task decisive bundle).
- **Prompt**: `07c` extended to a **ternary** variant (`07c_ternary` — add an explicit `"tie"` winner option; reuse `07b`'s tie wording). The handoff mandates a tie option; forced-choice inflates apparent decisiveness.
- **Position counterbalancing**: judge each pair in **both AB and BA** orientations (C4-as-A and C4-as-B). Per-judge position bias = the AB/BA asymmetry; it becomes a fixed effect in the model, not noise.
- **Target-swap**: keep the P-then-Q swap (ask "which serves P?" then "which serves Q?"). Recovery = picks the target's own output when asked for that target; the *flip* between P and Q is the within-pair fit-sensitivity signal.
- **Calls per pair per judge** = 2 orientations × 2 target-queries = **4**.

### B1.2 Per-judge calibration + fully-crossed author×judge (priority #2)
**Funded scope (decided): the FULL 3×2 author×judge cross — both cross-provider-primary AND same-provider halo.** All 239 pairs judged by both judges; halo reported separately (secondary), never folded into the cross-provider headline.

Report **per-judge**, never pooled. Three calibration components, each cheap:
1. **Global-pole desirability index** (deterministic, 0 LLM calls): per persona, win-rate when it is *not* the target, computed **leave-one-out** from the existing unconditional swap corpus (`pairwise_swap_scores.jsonl`). This is the independent (non-LLM) estimate of how much each persona's pole is globally preferred — the thing target-conditioning must overcome.
2. **Position bias** per judge: extracted *for free* from the B1.1 AB/BA runs.
3. **Pole-stickiness** per judge: the rate at which the judge *fails to flip* on target-swap (picks the same output for both P and Q) — a direct, target-conditioned-frame measure of residual pole anchoring.
- **Author×judge cross**: the existing 3 authors (gpt-5.4, gpt-5.5, opus) × 2 judges (gpt-5.5-xhigh, opus-4.7) is a complete 3×2. Estimating the judge-family main effect *and* the author-family main effect in the same model **identifies** which side the structure/pole effect lives on — closing the #7/#5 confound that Phase A could only flag.

### B1.3 Two-axis fit-vs-quality as a standing secondary (carry `07d`)
- Re-score the 239 pairs on the two scalar axes (general_quality, fit_to_person), 1 call/pair/judge, optionally ×2 for X/Y order. Confirms the #4 mechanism (fit_gap ≫ quality_gap) at full N and gives a continuous companion to the binary recovery metric.

### B1.4 Cheap control reads on existing conditions (optional B1 add-on)
- The corpus also has `C0` (no profile), `C_GENERIC_CONTRACT`, `C1`/`C1_padded`, `C3`, `C5*`, and the `L1–L3` ladder. Re-judging **C4 vs C0** and **C4 vs C_GENERIC_CONTRACT** target-conditioned gives an *early* (if not instruction-quantity-matched) control reading for free. The rigorous instruction-matched controls are B2; this is a cheap preview.

### B1.5 Human cross-check (owed from v0.3; priority: Phase 5)
- **≥2 human raters** re-code a stratified subsample of the target-conditioned judgments (agreement vs the LLM judges) **and** re-code the Gate-3 blind-recovery sample (the single-coder caveat). Human-side cost only; no cap. This is owed and small — fold it into B1 rather than deferring again.

### B1 decision gate (B1 → B2)
Pre-registered (see §6). In plain terms:
- **GO to B2 (full factorial)** if, at N=239 with AB/BA + tie + calibration, **cross-provider target-recovery on decisive cells stays clearly > 0.50** (both judge directions) **and** fit_gap > quality_gap survives. → generation+evaluation story holds; proceed to build the clean factorial.
- **NARROW** if recovery lands ~0.50–0.58 or is judge-direction-asymmetric → the honest conclusion tilts toward "judges reward instruction-salient scaffolding"; B2 shrinks to the evaluation-instrument work (better judge ensemble / calibration) rather than the full content×form design.
- **STOP/RE-DESIGN** if recovery collapses to ≤0.50 under counterbalancing → target-conditioning was a single-orientation artifact; re-open the judge design before any new generation.

---

## 3. Phase B2 — new generation + the content × form × salience factorial (gated on B1 = GO; SIZING DEFERRED)

> **Decided: all B2 sizing is deferred until B1 results.** The design *shape* below is fixed for planning, but cell counts, persona/scenario N, and the fractional fraction are **not committed** — they're set by a power calc on B1's observed effect size and locked in `docs/prereg_B2.md` *after* B1. Treat §3–§4 as the design framework, not a budget commitment.

Built only if B1 clears its gate. Pre-registered separately *after* B1 results are in (so the factorial sizing uses B1's observed effect size for power).

### B2.1 Trait-pole-balanced persona sampling + decoys (priority #3)
- **Problem it fixes**: in v0.3, a persona's "pole" (its globally-preferred behavioral posture) is confounded with being the right target. Sample **new persona pairs along behavioral-fit axes where neither pole is generically "better"** under assistant norms: warmth↔coldness, conscientiousness↔spontaneity, assertiveness↔humility, risk-seeking↔safety, challenge-seeking↔reassurance-seeking, brevity↔thoroughness. (The v0.3 `latent_ground_truth` already encodes behavioral-fit axes — `helpful_response_shape`, `sycophancy_triggers`, `overpersonalization_triggers`, `preferred_challenge_style` — so the axis vocabulary exists.)
- **Decoys**: for each target, add a decoy profile **matched on verbosity / structure / confidence / warmth / safety** so a global pole cannot masquerade as matching. Sampling target = pairs where the two poles have **near-equal global desirability** (verify with the B1.2 deterministic index on a pilot before mass generation).

### B2.2 Instruction-quantity-matched C0 controls (priority #4)
Generate, length- and instruction-count-matched to C4:
- `C0_STYLE_ONLY` — asks for the judge-preferred style (structure/warmth) with **no persona content**.
- `C_PLACEBO_CONTRACT` — an if-then contract *skeleton* with **generic** directives (same form as C4, empty of person-specific content).
- `C0_LONG_NEUTRAL` — length-matched neutral filler.
- **Decision rule**: if any of these approach C4 under target-conditioned judging, **discount personalization heavily** — the uplift is scaffolding/length, not person-fit.

### B2.3 Fully-crossed content × form × salience (priority #5)
- **Content** {none, generic, **correct**, **opposite**, random} (5)
- **Form** {prose, trait-list, contract, hidden-summary, minimal-cue} (5)
- **Salience** {explicit-labels, behavioral-examples, de-labeled} (3)
- **All length-matched.** Real personalization ⇒ **correct > opposite** even with form, length, and salience held — strongest in high-stakes scenarios.
- **Sizing (this is the cost driver — needs fractional design, see §5):** the load-bearing contrast is **correct vs opposite**. Recommend a **nested/D-optimal design**: fully cross {correct, opposite} × Form(5) × Salience(3) = **30 primary cells**, and sample {none, generic, random} at a reduced form set (prose + contract only). Estimate main effects + 2-way interactions without paying for all 75 cells. Final fraction set by B1's effect size in the power calc.

### B2.4 Profile-stakes scenario panel (priority #6)
- Pre-register scenarios stratified **high / med / low trait-divergence** (how much the two poles *should* pull apart given the persona). Personalization effects should **concentrate in high-divergence** scenarios; **flat uplift across strata ⇒ generic scaffolding, not personalization.** This stratification is itself a falsification test.

### B2.5 Judging B2
- Use the **B1-validated** target-conditioned protocol (07c-ternary, AB/BA, per-judge calibration, cross-provider primary). Generation is cap-free (GPT-5.5 author via codex) with an **Opus-author replication on a subsample** only (cap-bound). Judging Opus-arm is the main cap cost — same staging as B1.

---

## 4. The design matrix (B2) at a glance

| Factor | Levels | Role |
|---|---|---|
| **Content** | none · generic · **correct** · **opposite** · random | correct vs opposite = the personalization estimand; none/generic/random = controls |
| **Form** | prose · trait-list · contract · hidden-summary · minimal-cue | moderator: does fit survive form? |
| **Salience** | explicit-labels · behavioral-examples · de-labeled | moderator: does fit survive de-labeling (kills label-echo)? |
| **Length** | matched across all cells | confound control (not a factor) |
| **Scenario stakes** | high / med / low trait-divergence | falsification: effects must concentrate in high |
| **Author** | gpt-5.5 (full) · opus-4.7 (subsample replication) | generation-side robustness |
| **Instruction-matched controls** | C0_STYLE_ONLY · C_PLACEBO_CONTRACT · C0_LONG_NEUTRAL | discount test for scaffolding/length |

**Primary estimand**: P(target-conditioned judge picks `correct` over `opposite`), length/form/salience held, cross-provider, per-judge-calibrated — as a function of scenario stakes.

---

## 5. Cap / quota budget

### B1 (existing corpus) — call budget

| Workload | Judge | Calls | Cap exposure |
|---|---|---:|---|
| Target-cond 07c-ternary, full cross (239 pairs × 4) | **GPT-5.5** | 956 | **cap-free** (codex, separate quota) |
| Target-cond 07c-ternary, full cross (239 pairs × 4) | **Opus-4.7** | 956 | cap-bound |
| Two-axis 07d (239 × 2, X/Y order) | GPT-5.5 | 478 | cap-free |
| Two-axis 07d (239 × 2) | Opus-4.7 | 478 | cap-bound |
| Global-pole calibration index | — | 0 | deterministic numpy |
| Position/pole-stickiness calibration | — | 0 | derived from above runs |

**Funded Opus B1 (decided — full 3×2 cross):** 956 target-cond (239 × 4) + 478 two-axis (239 × 2) ≈ **1,434 cap-bound Opus calls** (matches the GPT arm, symmetric).

**Staged execution (cap-free first, always):**
1. **All GPT/codex** (≈1,434 calls) — full GPT-judge result + cross-provider-primary read on opus-authored cells. Separate quota, runs to completion without touching the Max cap.
2. **Deterministic calibration** (numpy over existing 13k swap rows) — 0 cap.
3. **Opus cross-provider-primary first**: judging the 160 gpt-authored pairs (160 × 4 = **640** target-cond) + two-axis (320) — the headline cross-provider Opus arm. Windowed + checkpointed (`phaseA2_target_judge_run.py` resumes per-call).
4. **Opus same-provider halo** (79 opus-authored pairs: 316 target-cond + 158 two-axis) — **funded**, runs after the cross-primary arm, reported as secondary halo-audit.

**Opus reality check**: `cap_events.jsonl` shows v0.3 Opus judging spread cap-burns across ~8+ days (5–37 events/day) — the cap, not wall-clock, gates throughput. Budget the full Opus B1 arm (≈1,434 calls) as **~4–8 cap windows ≈ 2–5 background days**, fully resumable; the cross-provider-primary headline (≈960 of those) completes first.

### B2 (new generation) — order-of-magnitude only (exact sizing pre-registered post-B1)
- **Generation** is largely **cap-free** (GPT-5.5 author via codex); Opus-author replication restricted to a ~15–20% subsample.
- Generation count scales as `personas × scenarios × conditions × authors`. Even a lean instance (≈12 personas × ≈24 stakes-stratified scenarios × ≈38 conditions × 1 primary author) is **~11k generations** — which is precisely why the fractional/nested design in §3.3 and a power-calc-driven cell count are **mandatory**, not optional. The full 5×5×3 = 75-cell cross × all personas/scenarios/authors is explicitly **out of budget**; we buy main effects + 2-way interactions, not the saturated design.
- **Judging B2** reuses the B1 protocol; Opus-arm judging is the cap cost and is staged identically.

---

## 6. Pre-registration (write before running each stage)

Two pre-reg docs: `docs/prereg_B1.md` (before B1) and `docs/prereg_B2.md` (before B2, using B1's effect size). Each fixes:

**Hypotheses**
- **H1** (B1): cross-provider target-conditioned target-recovery on decisive cells > 0.50, both judge directions, under AB/BA + tie + calibration.
- **H2** (B1): fit_gap > quality_gap at N=239 (both judges).
- **H3** (B1): target-recovery survives adjustment for the deterministic global-pole index (the effect is not *only* pole).
- **H4** (B2): P(correct > opposite) > 0.50 with form/salience/length held.
- **H5** (B2): the H4 effect is monotone increasing in scenario trait-divergence (high > med > low).
- **H6** (B2): instruction-matched controls (C0_STYLE_ONLY/C_PLACEBO_CONTRACT/C0_LONG_NEUTRAL) do **not** approach C4.

**Analysis model** (pre-specified): clustered/hierarchical logistic — `pick_target ~ is_correct + judge_family + author_family + position + content×form + content×salience + (1 | persona_pair) + (1 | scenario)`. Ties handled by a pre-registered rule (drop vs half-credit — specify both as primary/sensitivity). Cluster bootstrap CIs (reuse the hand-rolled numpy templates: `gate2_global_pole_reg.py`, `gate6_position_residuals.py`, `phaseA5_judge_contrast_interaction.py`). **No Wilson-only / aggregate win-rate headlines** (explicit v0.3 dead-end).

**Decision thresholds**: the B1→B2 gate (§2) and B2's discount rule (§3.2), with numeric cutoffs fixed in the pre-reg.

**Stopping / no-peeking**: GPT arm runs to completion before Opus arm is inspected for the gate; calibration computed before the recovery headline is read; no adaptive N on the decisive cells.

**Multiplicity**: per-judge and per-stratum reporting is planned (not pooled), so control family-wise error across the judge × stratum grid (pre-register Holm or hierarchical shrinkage).

---

## 7. Explicit dead-ends to avoid (carried from GPT-Pro/v0.3 sign-off)
More aggregate win-rate tables; more Wilson intervals (use clustered/hierarchical); more public-inspired personas via the same confounded packet process; more judge families without style-masked/gold calibration; profile-reference counts (use semantic alignment); equivalence-tests-alone for null steps (factorial ablation is the real fix).

## 8. Reusable assets (all committed)
- Runner template (resumable, cross-provider, codex+claude): `drivers/analysis/phaseA2_target_judge_run.py`
- Prompts: `07c` (target-cond — extend to ternary), `07d` (two-axis), `07b` (ternary tie wording)
- Deterministic stats: `gate2_global_pole_reg.py`, `gate6_position_residuals.py`, `phaseA5_judge_contrast_interaction.py`
- Corpus: `runs/2026-05-19_v03/`, metrics `reports/metrics_2026-05-19_v03.json`; existing swap infra `pairwise_swap_scores.jsonl` (13k), `pairwise_ternary_scores.jsonl`
- Model wrapper (Opus pinned to 4.7): `src/psycheeval/llm.py`

---

## 9. Decisions (resolved 2026-06-28)
1. **Scope/sequencing** → **B1-first as a hard gate on B2.** ✓
2. **B1 Opus cap appetite** → **fund the full 3×2 cross incl. same-provider halo** (≈1,434 Opus calls, ~2–5 windowed days; cross-provider-primary ≈960 completes first). ✓
3. **B2 generation breadth** → **deferred**; pre-register B2 sizing after B1 from the observed effect size. ✓

## 10. Immediate next steps (on execution go-ahead)
1. Draft `docs/prereg_B1.md` (hypotheses H1–H3, the clustered-logistic model, tie-handling rule, B1→B2 gate cutoffs, no-peeking order) — **before** any judging.
2. Add the `07c_ternary` tie variant of the target-conditioned prompt.
3. Generalize `phaseA2_target_judge_run.py` from the 64-cell decisive bundle to the full 239-pair universe, full 3×2 author×judge, AB/BA orientations.
4. Run the GPT/codex arm to completion (cap-free) + deterministic calibration; then stage the Opus arm (cross-primary → halo), checkpoint-resumable.
5. Compute the per-judge-calibrated recovery headline + two-axis secondary; run the ≥2-rater human cross-check; evaluate the B1→B2 gate.
