# PsycheEval v0.4 — Phase B1 pre-registration

> **Locked**: 2026-06-28, **before any target-conditioned judging run**. Frozen decisive sets: `data/phaseB1/decisive_sets_frozen.json` (sha256 `2103e6eebd401d4c89861bdaa66dbd29dc65ea9b06547e6d48bfa6ffd164ff2c`). Any change to this file after the first judging call is logged in §11 (Deviations), not silently edited.
> **Parent plan**: `docs/phase_b_plan.md`. **Foundation**: `reports/analysis/phaseA_synthesis_gate_AB.md` (Gate A→B = GO).
> **Hard constraints**: Opus eval calls pinned to `claude-opus-4-7`; cross-provider judging (gpt↔opus-authored) is the confirmatory PRIMARY; same-provider is halo-audit secondary, never folded into the headline.

## 1. What B1 is and what it confirms
B1 re-judges the *existing* v0.3 corpus to convert Phase A's directional probes (#2 target-conditioned recovery 67% on n=18; #4 fit≫quality) into headline-grade, counterbalanced, per-judge-calibrated measurement — **before** any new generation (B2). No new generation occurs in B1. This is the pre-registered gate that decides whether B2 runs the full content×form×salience factorial (GO), narrows to evaluation-instrument work (NARROW), or re-opens the judge design (STOP).

## 2. Data (all frozen, no new generation)
- **Pair universe**: the 239 matched C4 / C4_WRONG_PROFILE outputs sharing (scenario, synthetic-user, author-model), from `runs/2026-05-19_v03/`. C4 = correct-target contract; C4_WRONG_PROFILE = a reciprocal-pair persona's profile in the same form.
- **Authors** (3): gpt-5.4, gpt-5.5, opus(-4.7). **Judges** (2): gpt-5.5-xhigh (codex), opus-4.7 (`claude -p --safe-mode --model claude-opus-4-7`). Full **3×2 author×judge** cross.
- **Frozen decisive sets** (per-pair definition, locked in §0 artifact): a pair is *decisive* for a judge family iff that family's **unconditional** v0.3 pairwise judge picked C4_WRONG_PROFILE in a **strict majority of its non-tie verdicts** on that pair. Frozen counts:

| cell | role | pairs | decisive |
|---|---|---:|---:|
| openai_judge · anthropic_author | **cross-provider PRIMARY** | 79 | **22** |
| anthropic_judge · openai_author | **cross-provider PRIMARY** | 160 | **59** |
| openai_judge · openai_author | same-provider halo | 160 | 48 |
| anthropic_judge · anthropic_author | same-provider halo | 79 | 26 |

Cross-provider decisive N = **81** (vs Phase A's 18). The decisive set is computed **per judge family** so each judge is tested on exactly the cells where *it* erred unconditionally.

## 3. Manipulation
For each pair, the **target-conditioned** judge (`prompts/07c_pairwise_judge_target_conditioned_ternary.md`, the tie-augmented variant of validated `07c`) is asked twice — "which response better serves **P**?" (P = the pair's true target) and "which serves **Q**?" (Q = the reciprocal/wrong persona) — under **both AB and BA** orientations. = **4 calls / pair / judge.** Judge is blind to condition and author.

## 4. Primary outcome & estimand
- **Pick** = which of {C4, C4_WRONG} output the judge selects (or `tie`).
- **Recovery** (decisive cells, "which serves P?"): judge picks the **C4 (true-target)** output.
- **Primary estimand**: model-estimated marginal **P(recovery)** on the **cross-provider decisive pairs**, pooled across the two primary cells, marginalized over AB/BA orientation and target slot. Raw proportion reported alongside as a descriptive companion.

## 5. Confirmatory hypotheses (directional)
- **H1 (recovery survives scaling+counterbalancing)**: cross-provider decisive recovery > 0.50.
- **H1a/H1b**: holds in **each** cross-provider direction (gpt-judge·opus-author; opus-judge·gpt-author) — guards against a one-sided artifact.
- **H2 (fit≫quality mechanism)**: from the two-axis `07d` re-score, fit_gap (C4−C4_WRONG) > quality_gap, for **both** judges, with fit_gap 90% CI excluding 0.
- **H3 (not merely the pole)**: in the full-universe mixed model (§6), marginal P(pick_target) > 0.50 **after** adjusting for the deterministic global-pole index — recovery is not explained away by global desirability.

## 6. Analysis model (pre-specified)
Mixed-effects logistic over all judged (pair × target-query × orientation) observations:

```
pick_target ~ 1 + is_decisive + global_pole_index_z + judge_family
              + author_family + position(AB/BA) + target_query(P/Q)
              + (1 | persona_pair) + (1 | scenario)
```

- **Random intercepts**: persona_pair (the 4 reciprocal pairs) and scenario — handles the within-task non-independence flagged as a Phase A caveat.
- **CIs** (amended 2026-06-28, pre-unblinding — see §11 D1): **primary** = cluster bootstrap resampling **by scenario** (80 clusters, 2000 resamples, 90% intervals) — scenario is the well-powered clustering unit. **Robustness**: (i) **leave-one-persona-pair-out** range (drop each of the 4 reciprocal pairs in turn, recompute recovery — the honest check for persona-pair dependence given only 4 groups), and (ii) persona-pair-clustered interval reported as a conservative bound. The mixed model carries persona_pair + scenario as crossed random intercepts. Hand-rolled numpy (reuse `gate2_global_pole_reg.py` / `gate6_position_residuals.py`); no Wilson-only or pooled aggregate-win-rate headlines (explicit v0.3 dead-end).
- **global_pole_index_z**: per-persona global-desirability (win-rate when *not* the target) computed **leave-one-out** over the existing unconditional swap corpus (`pairwise_swap_scores.jsonl`), z-scored. Deterministic, 0 LLM calls.
- **Reporting is per-judge and per-cell**, never pooled across providers for the headline.

## 7. Tie handling, position, calibration
- **Ties** (07c-ternary): **primary** analysis excludes ties from the recovery denominator (recovery = picks_target / (picks_target + picks_opposite)). **Sensitivity**: ties = 0.5. Tie rate reported per judge.
- **Position**: AB/BA orientation is a fixed effect; per-judge position bias = the AB/BA asymmetry, reported.
- **Pole-stickiness** (per judge): rate of *non-flip* on the P→Q target-swap (same output picked for both targets) — a target-frame measure of residual pole anchoring; reported, not gated.

## 8. Decision gate (B1 → B2) — HARD cutoffs
Let `R` = pooled cross-provider decisive recovery (primary estimand, §4); `R.lo` = its 90% cluster-bootstrap lower bound; `R_gpt`, `R_opus` = the two per-direction cross-provider recoveries.

- **GO** (B2 runs the full content×form×salience factorial) — requires **all** of:
  1. `R ≥ 0.60`;
  2. `R.lo ≥ 0.53` (clearly above the 0.50 chance null);
  3. `R_gpt ≥ 0.55` **and** `R_opus ≥ 0.55` (both directions agree);
  4. **H2 holds** (fit_gap > quality_gap, both judges, fit_gap 90% CI excludes 0).
- **NARROW** (B2 = evaluation-instrument work only: stronger judge ensemble / calibration, **no** content×form generation): not GO, **but** `R.lo > 0.50` (recovery is real but small, fragile, or direction-asymmetric).
- **STOP / RE-DESIGN** (re-open the judge design before any new generation): `R.lo ≤ 0.50` (counterbalanced recovery indistinguishable from chance).

H3 is a confirmatory robustness check: if H1 passes but **H3 fails** (recovery vanishes once the pole index is adjusted), the verdict is capped at **NARROW** regardless of `R`.

## 9. Sequence & no-peeking
1. Freeze decisive sets (§0) — **done before this doc was committed**.
2. Run the **GPT/codex** judge arm to completion (target-cond ternary + two-axis), cap-free.
3. Compute deterministic calibration (global-pole index, position, pole-stickiness).
4. Run the **Opus-4.7** arm: cross-provider-primary (gpt-authored) first, then same-provider halo. Windowed, checkpoint-resumable.
5. **Only after both cross-provider arms are complete** is the §8 gate evaluated (the gate needs both directions, so it is structurally impossible to evaluate from the GPT arm alone — no peeking by construction). No adaptive N; the decisive sets and the model are fixed here.

## 10. Multiplicity & secondary
- **Confirmatory family**: {H1, H1a, H1b, H2(gpt), H2(opus), H3}. Holm correction at α=0.05, one-sided where directional.
- **Secondary (reported, not gated)**: full-universe metrics (p_picks_target, q_picks_opposite, reversed-correctly, flip-rate); same-provider halo cells; two-axis scalar gaps at full N; per-judge position/tie/pole-stickiness.
- **Human cross-check** (owed from v0.3): **≥2 raters** recode (a) a stratified ~40-pair subsample of the target-conditioned verdicts and (b) the Gate-3 blind-recovery sample. Report human–LLM agreement (Krippendorff's α / Cohen's κ). Not a numeric gate, but α < 0.40 on (a) is flagged as a judge-validity threat in the B1 write-up.

## 11. Deviations log
*(append-only; any departure from §2–§10 recorded here with date + reason)*
- **D1 (2026-06-28, pre-unblinding — no decisive-cell recovery computed yet):** §6 CI method amended. Original spec bootstrapped solely by persona_pair, which is **degenerate** (only 4 reciprocal pairs → unstable/wide bootstrap). Replaced with scenario-cluster bootstrap (80 clusters) as primary + leave-one-persona-pair-out range + persona-pair-clustered conservative bound as robustness. The §8 gate cutoffs are unchanged; only the interval estimator changed. Logged before any unblinding (the GPT judging arm was still mid-run and no recovery statistic had been read).
- **D2 (2026-08-05, post-unblinding — recorded late, executed under the workshop-paper ship criteria, owner-authorized):** the §6 mixed-effects estimator and the §10 Holm family were **not run** at gate time. The 2026-06-29 B1→B2 gate was evaluated on a **substituted descriptive analysis** (`phaseB1_analyze.py`: per-pair recovery + scenario-cluster bootstrap + LOPO + a one-predictor pole logistic) with the §8 cutoffs applied as written. That substitution was disclosed in the long-form write-up at the time but not logged here — this entry repairs the log. The registered estimator was then executed on 2026-08-05 (`drivers/analysis/phaseB1_registered_model.py`, seed 20260805 declared pre-run), i.e. **after descriptive unblinding**; model, family, and cutoffs were taken verbatim from this frozen document. One implementation choice was required where §6/D1 is silent: bootstrap refits hold variance components at the full-data ML values (a 200-resample re-estimated sensitivity matches to ±0.003). **Result: all six confirmatory tests reject under Holm** (pooled marginal recovery 0.753, 90% CI 0.694–0.807; both directions > 0.50; H2 fit-gaps exclude 0 for both judges; H3 at mean pole 0.754). Details: `reports/analysis/phaseB1_registered_model_NOTE.md`. The §8 gate verdict (GO) is unchanged by this execution; any paper reporting B1 must describe the estimator as "preregistered, executed after descriptive unblinding" and report the descriptive companion (raw decisive recovery 0.636) beside the model-estimated primary (0.753), including the reconciliation note.
