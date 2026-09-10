# PsycheEval v0.4 — Phase B2 pre-registration

> **Status**: design + analysis + **sizing LOCKED (2026-06-29: Recommended tier, §6)**. Remaining before generation: the persona-axis list + scenario-stakes set (new creative artifacts, §3/§10) get one review pass; then the persona balance-screen runs, then mass generation. This doc is the pre-registration of record.
> **Gate cleared**: `reports/analysis/phaseB1_gate_findings.md` — B1 verdict **GO** (decisive-cell recovery 0.636 pooled cross-provider; fit≫quality 2.5–2.6×; survives pole adjustment 0.789).
> **Constraints**: Opus pinned `claude-opus-4-7`; cross-provider judging PRIMARY; staged cap-free-first.

## 1. The question B2 answers
B1 proved the *judge* can be made fit-sensitive on the existing corpus. B2 asks the generation-side question the whole program exists for: **is persona-conditioned personalization load-bearing — does giving the author the *correct* profile beat the *inverted* profile when form, salience, and length are held, and does the effect behave like real personalization (concentrate in high-divergence situations, survive de-labeling, and exceed instruction-matched scaffolding)?** Unlike B1 (frozen corpus), B2 generates new outputs under a controlled factorial with **trait-pole-balanced personas** so a global pole cannot masquerade as fit.

## 2. Design factors (all length-matched)
| factor | levels | role |
|---|---|---|
| **Content** | none · generic · **correct** · **opposite** · random | `correct` vs `opposite` = primary estimand; none/generic/random = content controls |
| **Form** | prose · trait-list · contract · hidden-summary · minimal-cue | moderator (does fit survive form?) |
| **Salience** | explicit-labels · behavioral-examples · **de-labeled** | moderator; de-labeled kills label-echo |
| **Scenario stakes** | high · med · low trait-divergence | H5 falsifier (effect must concentrate in high) |
| **Author** | gpt-5.5 (primary) · opus-4.7 (replication subsample) | generation robustness |
| **Instruction-matched controls** | C0_STYLE_ONLY · C_PLACEBO_CONTRACT · C0_LONG_NEUTRAL | H6 discount test |

**Length-matching**: every condition padded/trimmed to a common token band (pre-registered target ± tolerance); length logged per output and entered as a covariate.

## 3. Personas — trait-pole-balanced + surface-matched (kills Gate-2 confound at the source)
- Sample reciprocal **persona pairs along behavioral-fit axes where neither pole is generically "better"** (warmth↔coldness, conscientiousness↔spontaneity, assertiveness↔humility, risk↔safety, challenge↔reassurance, brevity↔thoroughness).
- **Pre-generation balance screen** (deterministic, the B1 method): draft each pair, generate a small pilot, run `phaseB1_global_pole_index` logic; **keep only pairs with |Δ global-desirability| < 0.15** (both judge families). Imbalanced pairs are rejected and resampled *before* mass generation. (B1's v0.3 pairs ranged 0.18–0.75 — explicitly NOT balanced; B2 fixes this.)
- The `opposite` profile is the reciprocal pole = inherently surface/verbosity/structure-matched to `correct` (same writer, same template, same length band) — this is the decoy.

## 4. Hypotheses (confirmatory, directional)
- **H4 (personalization is load-bearing)**: P(target-conditioned judge picks `correct` > `opposite`) > 0.50, pooled, form/salience/length held.
- **H4-moderated**: H4 holds *within each* form level and *within each* salience level (report per level + homogeneity test).
- **H5 (stakes concentration)**: the H4 effect is monotone increasing in scenario trait-divergence (high > med > low; pre-registered linear-trend test). Flat ⇒ generic scaffolding.
- **H6 (beats scaffolding)**: `correct` exceeds each instruction-matched control (C0_STYLE_ONLY, C_PLACEBO_CONTRACT, C0_LONG_NEUTRAL) by a margin; if any control approaches `correct` (Δ within 0.05), discount personalization.
- **H7 (survives de-labeling)**: H4 holds in the **de-labeled** salience condition — fit isn't label/keyword echo.

## 5. Judging & analysis
- **Protocol = B1-validated**: `07c_ternary` target-conditioned fit prompt, **AB/BA** counterbalancing, per-judge calibration, **cross-provider primary** (gpt-judge↔opus-authored; opus-judge↔gpt-authored) + same-provider halo. The `correct`-vs-`opposite` pair is judged "which serves the target?" (single-target P-query; 2 calls/pair for AB/BA). Two-axis `07d` as standing secondary.
- **Model**: mixed logistic `pick_correct ~ 1 + content_contrast + form + salience + stakes + content×form + content×salience + content×stakes + length_z + judge_family + author_family + position + (1|persona_pair) + (1|scenario)`. Primary CI = scenario-cluster bootstrap (per B1 D1) + LOPO robustness. Holm across the confirmatory family.
- **Conclusion rule**: "personalization is load-bearing" requires **H4 ∧ H7 ∧ H5 ∧ H6**. Partial passes yield a graded conclusion (e.g., H4∧H7 but flat stakes ⇒ "real but not stakes-sensitive").

## 6. Power calc & sizing — THE OPEN DECISION
**Planning effect** (from B1): the genuine personalization signal with the pole neutralized sits between B1's adversarial decisive recovery (0.636) and its full-universe target-tracking (0.768). Plan conservatively at **p₁ = 0.62 vs p₀ = 0.50**.

One-sided binomial, α=0.05, ×1.4 cluster design-effect:

| target | n / form×salience cell | power/cell | total `correct`-vs-`opposite` pairs |
|---|---:|---:|---:|
| main effect + marginal moderators only | ~60 | ~0.60 (per cell) | **~900** |
| **+ 2-way interactions (recommended)** | ~110 | ~0.80 | **~1,650** |
| + well-powered interactions | ~150 | ~0.90 | ~2,250 |

The **main effect** (H4 pooled) and the **marginal** form/salience/stakes moderators are well-powered at every tier (≥0.9 pooled even at the lean tier); the tiers differ in power for the **per-cell 2-way interaction lattice**. Stakes (H5) is powered at the margin: ~550 pairs/stratum at the recommended tier.

**Recommended design (the ~1,650-pair tier):**
- **16 personas (8 pole-balanced reciprocal pairs)**, balance-screened (§3).
- **30 scenarios** (10 high / 10 med / 10 low divergence).
- Balanced-incomplete allocation: each of the 480 (persona × scenario) units generated under ~3–4 (form×salience) cells × {correct, opposite}, Latin-square rotated so each of the 15 cells accrues ~110 pairs and each stakes stratum ~550.
- **Generation** ≈ 3,300 primary (correct+opposite) + ~900 controls ≈ **~4,200 generations** — cap-free GPT-5.5 author; **Opus-4.7 author replication on ~15%** (~630, cap-bound).
- **Judging** ≈ 1,650 pairs × 2 (AB/BA) × cross-provider split ≈ **~3,300 target-cond calls/judge-coverage**; Opus judging arm ≈ **~1,650–3,300 cap-bound** (~2–3× B1's 1,434, which ran in ~1h with no cap — so plausibly a few hours windowed) + two-axis secondary.

## 7. Cap/quota budget & staging (same discipline as B1)
1. Persona balance-screen pilot (small) → reject imbalanced pairs **before** mass generation.
2. Generation: GPT-5.5 author (cap-free) full; Opus-author replication subsample (cap-bound, windowed).
3. Judging: GPT/codex arm full (cap-free) + deterministic calibration; then Opus arm cross-primary → halo, checkpoint-resumable chains (reuse `run_until_complete.sh`).
4. Analyzer with no-peek guard → gate H4–H7 → findings.

## 8. Explicit dead-ends (carried) & owed
- No aggregate win-rate / Wilson-only headlines; no more confounded public-packet personas; no profile-reference counts (semantic alignment only); factorial ablation, not equivalence-tests-alone.
- Carry the B1-owed ≥2-rater human cross-check forward; add a B2 human spot-check on the de-labeled condition.

## 9. Sizing — LOCKED (2026-06-29)
**Recommended tier**: ~1,650 `correct`-vs-`opposite` pairs, **16 pole-balanced personas (8 reciprocal pairs)**, **30 stakes-stratified scenarios (10/10/10)**, ~110 pairs/form×salience cell (per-cell 2-way power ~0.80; main effect + marginal moderators ≥0.9). ~4,200 generations (cap-free GPT-5.5 author + ~15% Opus-4.7 replication); Opus judging ~2–3× B1.

## 10. Remaining pre-generation step (one review pass, then execute)
Before mass generation, two new creative artifacts get a review pass, then the deterministic balance screen runs:
1. **Persona-axis list** — the 8 reciprocal pairs and which behavioral-fit axis each contrasts (warmth, conscientiousness, assertiveness, risk, challenge, brevity, + 2 more), with the `do-not-infer` / caricature guards.
2. **Scenario-stakes set** — 30 scenarios tagged high/med/low trait-divergence, with the divergence rationale per scenario.
3. **Balance screen** (deterministic): pilot-generate, run the B1 pole-index, **reject any pair with |Δ global-desirability| ≥ 0.15** and resample, before committing to the full ~4,200-generation run.
