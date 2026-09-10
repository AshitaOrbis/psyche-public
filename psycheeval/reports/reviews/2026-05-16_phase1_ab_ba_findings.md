# PsycheEval v0.2 — Phase 1 AB/BA Counterbalanced Rejudging Findings

**Date**: 2026-05-16
**Status**: Tier A + Tier B effectively complete (1,448 records / 1,670 target; 5 codex stragglers still finishing but verdicts settled)
**Tests**: 106 pass; new AB/BA analyzer + driver fully integrated

---

## Headline

The single experiment all three external reviewers called "the cheapest decisive
next experiment" has run. Verdict:

> **C5_CONTRACT > C5 is the only C5_CONTRACT pairwise headline that survives
> position-controlled rejudging.** The C5_CONTRACT > C3 and C5_CONTRACT > C4
> margins were carried entirely by a systematic ~15–17 percentage-point
> slot B bias in two of the three judges.

This converges with three independent Phase 0 paths (scalar reconciliation,
Opus LOO, length matching) that all flagged the same conclusion. Phase 1
turns the convergent suspicion into a direct positive finding.

---

## What was run

For every existing pairwise record on the 3 C5_CONTRACT-vs-{C3, C4, C5}
edges (PI personas, same-author scope), the analyzer issued a second call to
the **same judge** with `run_id_a` and `run_id_b` swapped. The analyzer then
joins originals with swaps via the run_id-swap signature and reports:

- `orig lo_win` — win rate of lower-numbered condition in the original (lo always in slot A)
- `swap lo_win` — win rate of lower-numbered condition after slot reversal (lo now in slot B)
- `controlled lo_win` — average across orders; the position-bias-corrected headline
- `position_consistent_rate` — judgments agree on condition winner regardless of slot (true preference)
- `position_flip_rate` — judgments disagree (the slot, not the condition, won both times)

### Tier A budget actually consumed

| Pair | n AB/BA matched |
|---|---:|
| C3 vs C5_CONTRACT | 288 |
| C4 vs C5_CONTRACT | 288 |
| C5 vs C5_CONTRACT | 288 |
| **Tier A total** | **864** |

(Per-judge records exceed 864 because the swap-rejudge driver wrote raw records before AB/BA matching; the canonical AB/BA-matched count per pair is 288.)

Codex Tier A completed in a single ~75-minute wallclock window across 6
parallel processes. Opus C5 vs C5_CONTRACT completed in a single cap window
(no cap events). Opus C3 and C4 pairs hit cap mid-run, exited cleanly via
the cap-burn handler, and resumed cleanly when the user authorized the
restart after the reset.

---

## Headline AB/BA results (n=1,664 swap records, FULL coverage)

All 6 headline pairs now have full AB/BA coverage:

```
pair                  n_AB/BA  orig lo_win  swap lo_win  controlled  controlled CI95     survives?
C1_padded vs C4         320       0.319       0.434      0.377     [0.324, 0.429]    ✓ YES
C3 vs C5_CONTRACT       288       0.428       0.573      0.501     [0.443, 0.557]    ⚠ NO
C4 vs C4_shuffled       320       0.519       0.637      0.578     [0.523, 0.631]    ✓ YES (stronger)
C4 vs C5                160       0.637       0.725      0.681     [0.606, 0.749]    ✓ YES (stronger)
C4 vs C5_CONTRACT       288       0.400       0.562      0.482     [0.425, 0.540]    ⚠ NO
C5 vs C5_CONTRACT       288       0.240       0.403      0.323     [0.272, 0.379]    ✓ YES
```

### Translated for the curated report

#### Tier 1 — survives AB/BA (publish with the controlled estimate, not the original)

- **C4 > C1_padded** — original 68.1% C4 win rate, **controlled estimate: 62.3% C4 wins** [57.1, 67.6]. Attenuation from position bias (~5.8 pp), but condition preference is solid. Length-control headline survives **+ position-bias control**.

- **C4 > C5** — original 63.7% C4 win rate, **controlled estimate: 68.0% C4 wins** [61.5, 74.4] across all three judges (gpt-5.4=0.681, gpt-5.5=0.681, opus=0.679 — effectively unanimous). After 2026-05-17 Phase 2 Opus C4 vs C5 fill (120 originals + 120 AB/BA swaps, all completed cleanly with zero cap events), the pair now has full 3-judge coverage. **Joint position+length correction survives**: length-matched controlled lo_win 67.4% [54.7, 79.5] excludes 0.5 on the C4-favored side. **Promoted to clean Tier 1** (scope qualifier dropped).

- **C5_CONTRACT > C5** — original 76.0% C5_CONTRACT win rate, **controlled estimate: 67.7% C5_CONTRACT wins** [62.1, 72.8]. Substantial real condition preference. The contract-supplemented source-packet package outperforms the bare source-packet condition under counterbalanced judging. Tier 1 confirmed.
  - **Mechanism not isolated**: C5_CONTRACT differs from C5 on at least four dimensions simultaneously (contract presence, ordering, anti-mimicry language, ~3,549 chars of additional profile text). The package wins; which component carries the effect is deferred to v0.3 (`C_GENERIC_CONTRACT`, `C5_CONTRACT_SHORT`).
  - Attenuation: original 76% → controlled 67.7% is an 8.3 pp absolute attenuation (the above-parity edge shrinks from +26 pp to +17.7 pp — a 32% reduction in edge size).

#### Tier 2 — collapses under AB/BA (downgrade)

- **C5_CONTRACT vs C3** — the original 57.2% C5_CONTRACT win rate was **entirely position-bias.** Controlled: C5_CONTRACT wins 49.9% [44.3, 55.7]. **No significant condition preference.** Three independent Phase 0 paths (scalar reconciliation, Opus LOO, length matching) all flagged this; Phase 1 confirms.

- **C5_CONTRACT vs C4** — the original 60.0% C5_CONTRACT win rate was **entirely position-bias.** Controlled: C5_CONTRACT wins 51.8% [46.0, 57.5]. **No significant condition preference.**

#### Surprise — original headline was *understating* the effect

- **C4 vs C4_shuffled** — the original 51.9% C4 win rate (called "no significant difference" in the bundle) actually **strengthens to 57.8% C4 wins** under controlled judging [52.3, 63.1]. Coherent-order DOES beat shuffled-order. The original was understating the effect because slot-A bias (which penalized C4 in slot A) was suppressing the apparent margin. Once counterbalanced, the C4 advantage becomes clear and the CI excludes 0.5 on the C4-favored side.
  - **This is a sign-correction of the Phase 0 finding**, not a flip. Phase 0 (§6f / Q2) said "coherent structure does not significantly beat shuffled" based on the original 51.9% figure. Phase 1 shows the answer is actually **yes, coherent structure beats shuffled**, at ~58%, after position correction. The Phase 0 framing should be revised in the curated report.
  - Effect size is moderate (controlled CI [0.523, 0.631]) — clearly clear of 0.5 but not as decisive as e.g. C5_CONTRACT > C5 (CI [0.272, 0.379]). Tier 1.5: report as positive but with measured confidence.

---

## Slot B advantage quantification

```
pair                  gpt-5.4    gpt-5.5     Opus      mean (all judges)
C3 vs C5_CONTRACT     -0.036     +0.250     +0.233    +0.147
C4 vs C5_CONTRACT     +0.024     +0.250     +0.238    +0.169
C5 vs C5_CONTRACT     +0.112     +0.310     +0.094    +0.163
```

The pattern is striking and judge-specific:

- **gpt-5.4 has essentially no slot-B preference on the C3 and C4 pairs.** It actually slightly favors slot A on C3 vs C5_CONTRACT (−0.036).
- **gpt-5.5 has a robust 25–31 pp slot-B preference across all 3 pairs.** This is the largest position bias observed.
- **Opus has a 23–24 pp slot-B preference on C3 and C4 pairs**, but only 9 pp on C5 vs C5_CONTRACT.

**Implication for Phase 0's "C3 vs C5_CONTRACT under cross-provider judging" finding (Phase 0.A)**: that result was driven by gpt-5.4 — the only cross-provider judge for the Opus-authored cells — which has no slot-B bias. The other judges' slot-B bias was the dilution in the all-judge cluster bootstrap. The Phase 0 stratified CI was correctly reading judge×position-bias interaction, not a real cross-provider effect.

---

## Verified reviewer predictions

| Phase | Reviewer | Prediction | AB/BA verdict |
|---|---|---|---|
| 0.B | GPT-Pro | "C5_CONTRACT > C3/C4 is pairwise-only; scalar Δ ≈ 0" | ✓ Confirmed: position bias was the entire pairwise advantage |
| 0.D | Codex-council | "Drop Opus and C5_CONTRACT > C3 disappears" | ✓ Confirmed: Opus's slot-B bias was carrying the result |
| 0.G | All three | "Length matching makes C3 vs C5_CONTRACT vanish" | ✓ Confirmed; AB/BA is more decisive than length |
| 0.E + Phase 1 | All three | "AB/BA is the cheapest decisive experiment" | ✓ Confirmed: 864 Tier A AB/BA-matched pairs (252 + 252 + 360 raw judge records, dedup to 288/pair) settled the question |

Three Phase 0 independent paths (scalar reconciliation, Opus leave-one-out, length matching) all converged on the same prediction. Phase 1 confirmed it directly.

---

## Final Tier 1 vs Tier 2 assignment for v0.2 curated report

### Tier 1 (publish — survives Phase 0 + Phase 1)

| Pair | Original headline | Phase 1 controlled estimate | Notes |
|---|---|---|---|
| **C0 dominated by all profile conditions** | 86.6% C4 wins | (not AB/BA tested — effect is huge, +6 pp scalar Δ) | Tier 1 from Phase 0 alone |
| **C4 > C1_padded** | 68.1% C4 wins | **62.3% C4 wins** [57.1, 67.6] | Length-control + position-control |
| **C4 > C5** | 63.7% C4 wins | **68.0% C4 wins** [61.5, 74.4] | Position-controlled, joint length+position robust, judge-unanimous after 2026-05-17 Opus fill |
| **C5_CONTRACT > C5** | 76.0% C5_CONTRACT wins | **67.7% C5_CONTRACT wins** [62.1, 72.8] | Survives all 12 Phase 0 audits + AB/BA |

### Tier 2 → "no significant condition preference"

| Pair | Original headline | Phase 1 controlled estimate | Verdict |
|---|---|---|---|
| **C5_CONTRACT vs C3** | C5_CONTRACT wins 57.2% | C5_CONTRACT wins 49.9% [44.3, 55.7] | **No real preference** |
| **C5_CONTRACT vs C4** | C5_CONTRACT wins 60.0% | C5_CONTRACT wins 51.8% [46.0, 57.5] | **No real preference** |

### Tier 1.5 — original headline was understated

| Pair | Original headline | Phase 1 controlled estimate | Verdict |
|---|---|---|---|
| **C4 vs C4_shuffled** | "no significant difference" 51.9% C4 wins | **C4 wins 57.8%** [52.3, 63.1] | After position-bias correction, coherent ordering wins. Original headline was understating because slot-A bias hurt C4 (always in slot A). Sign-correction of Phase 0 §6f. |

### Strike entirely

- "v0.1 PAE confound is empirically resolved in favor of absence of contract as dominant driver" — replace with: "v0.2 shows the C5_CONTRACT package does substantially beat the C5 package (67.7% wins under counterbalancing), but the question of *which* component of C5_CONTRACT carries this — contract presence, contract-first ordering, anti-mimicry language, source-packet form, or response-length — remains open and is the central Phase 2 question."
- "C5_CONTRACT outperforms both C3 and C4" — replace with the per-pair downgrades above.
- "Coherent structure does not significantly beat shuffled" — replace with: "Under counterbalanced judging, coherent-order C4 wins 57.8% [52.3, 63.1]. The original 51.9% headline was understating the effect because slot-A bias was hurting C4 (always in slot A in the original judging). Coherent ordering does meaningfully beat shuffled."

### Tier 3 (v3 scope) — needs new experiments

- Mechanism attribution for the surviving C5_CONTRACT > C5 effect (Phase 2: `C_GENERIC_CONTRACT`, `C5_NONPUBLIC`, `C5_CONTRACT_SHORT`)
- Anything claiming profile-specificity (Phase 2: `C4_WRONG_PROFILE`)
- Investigate why coherent-order C4 doesn't beat shuffled C4 (small effect, but suggests something about prompt structure dynamics worth understanding)

---

## New methodology finding worth publishing standalone

**LLM judges show systematic slot-B preference in pairwise judging, with magnitude varying by judge family**:

- gpt-5.4 (OpenAI, smaller): negligible position bias
- gpt-5.5 (OpenAI, xhigh): ~25–31 pp slot-B preference
- Opus 4.7 (Anthropic): ~9–24 pp slot-B preference, varies by content

This converges with prior LLM-as-judge research (Zheng et al. 2023, Shi et al. 2024) on the existence of position bias, but provides direct quantification on a tri-model corpus with same-author controls. The slot-B direction (rather than slot-A) is consistent with prior work that finds the "later" item in the prompt context tends to win.

For the v0.2 report, this lifts the methodological-contribution claim. Even the failures of the original v0.2 headlines are evidence of a real, quantifiable artifact that any LLM-as-judge eval needs to control for.

---

## What's next

Three possible Phase 2 directions, in order of value:

### Option A: write the v0.2 curated report now (recommended)

The data is conclusive enough that the curated report can be written from
Phase 0 + Phase 1 evidence. The story is:

1. Methodology pilot (the C5_CONTRACT separator, anchored rubric, length controls, tri-model design)
2. One surviving substantive finding: C5_CONTRACT > C5 (the contract-supplemented source-packet package outperforms the bare source-packet condition; mechanism not isolated — see v0.3)
3. One disconfirmed claim (C5_CONTRACT > C3/C4 = "no real preference under counterbalancing")
4. **New methodological finding**: LLM judge slot-B position bias quantified at 15–17 pp, judge-specific

This is a stronger paper than the original v0.2 plan because the failure mode is itself an informative finding.

### Option B (DONE): Tier B AB/BA on non-C5_CONTRACT pairs

Completed in this run alongside Tier A. Results showed:

- **C1_padded vs C4**: prediction was "still favors C4 but more modestly" — **right direction, magnitude was bigger.** Attenuated from 68.1% → 62.3% (5.8 pp adjustment). The slot-B bias on this pair was moderate.
- **C4 vs C5**: prediction was "still favors C4 (~56%)" — **wrong**. Actually 68.1% C4 wins, *stronger* than original 63.7% because slot-B bias was running *against* C4 (which was always slot A in the originals). Counter to expectation. Note: this is OpenAI-judge-only (Phase 0 confirmed Opus n=0); Opus AB/BA fill pending. Also: AB/BA controls position, not length; the Phase 0 length-matching finding on this pair targets a different confound, and joint position × length analysis is pending.
- **C4 vs C4_shuffled**: prediction was "would flip to C4_shuffled" — **right!** Actually 57.1% C4_shuffled wins under controlled judging.

The position-bias direction (slot-B-favored, ~16 pp) was correctly diagnosed in Tier A, but the per-pair impact varies based on (a) the original C4-slot assignment and (b) which judges (gpt-5.5 with strong bias vs gpt-5.4 with none) dominated each pair. The simple "+0.16 correction" estimator was too crude for the non-C5_CONTRACT pairs.

### Option C: pivot to Phase 2 generation experiments

The convergent reviewer recommendation: `C_GENERIC_CONTRACT` + `C4_WRONG_PROFILE` (tests whether Psyche is *personalization* or just *prompting*) and `C5_NONPUBLIC` (isolates public-anchor effect). Costs: ~300 Opus + ~600 codex generations + judging.

**Recommendation after Tier B complete**: Two parallel tracks possible:

1. **Track A — write v0.2 curated report now** on the full Phase 0 + Phase 1 corrected dataset. The story is clean: 3 Tier 1 findings + 2 Tier 2 downgrades + 1 surprise direction-flip + the methodology contribution. This can ship in 1-2 days.

2. **Track B — start Phase 2 generation** for the deepest finding (C5_CONTRACT > C5 mechanism). The `C_GENERIC_CONTRACT` ablation is the most diagnostic: if generic contract matches C5_CONTRACT, the "profile specificity" claim collapses entirely. Costs roughly ~1 week of Opus quota + codex.

Tracks aren't mutually exclusive — write the v0.2 report on existing data while Phase 2 generation runs in background.

---

## Files produced this phase

| File | Purpose |
|---|---|
| `runs/2026-04-26_v02_hard_codex_only/pairwise_swap_scores.jsonl` | 790 (→ 867) AB/BA swap records |
| `logs/phase1_swap/*.log` | Per-process run logs (6 codex + 3 Opus) |
| `src/psycheeval/judge.py:pairwise_swap_rejudge` | New driver + CLI mode `pairwise-swap` |
| `src/psycheeval/analyze.py:_compute_ab_ba_position_audit` | Analyzer joins originals with swaps; per-pair position-bias quantification + survives_swap flag |
| `reports/metrics_2026-04-26_v02_hard_codex_only.json:pairwise.ab_ba_position_audit_same_author` | Per-pair AB/BA block (canonical numbers) |
| `reports/psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md` | Autogen now includes "## AB/BA counterbalanced rejudge (Phase 1)" section |
| This file (`reports/reviews/2026-05-16_phase1_ab_ba_findings.md`) | Phase 1 findings, tier reassignment, next-steps options |
