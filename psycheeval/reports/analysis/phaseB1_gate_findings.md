# PsycheEval v0.4 — Phase B1 findings & B1→B2 gate

**Date**: 2026-06-29
**Pre-registration**: `docs/prereg_B1.md` (locked `eba1918`, before any judging; amendment D1 logged pre-unblinding).
**Drivers**: `phaseB1_target_judge_run.py`, `phaseB1_two_axis_run.py`, `phaseB1_global_pole_index.py`, `phaseB1_analyze.py`, `phaseB1_h3.py`.
**Corpus**: frozen v0.3 (`runs/2026-05-19_v03`), 239 matched C4/C4_WRONG pairs, full 3×2 author×judge cross. Cross-provider primary; same-provider halo secondary.
**Run**: all 6 arms completed **first pass, 0 errors, 0 cap interruptions** (1,434 Opus-4.7 calls in ~1h; 1,434 GPT-5.5 calls cap-free). Opus pinned `claude-opus-4-7`.

## Verdict: **GO** — Phase B2 proceeds with the full content×form×salience factorial.

All four confirmatory hypotheses pass under AB/BA counterbalancing, a tie option, and per-judge calibration.

## Headline — target-conditioned recovery on the decisive cells

The decisive cells are exactly those where the v0.3 **unconditional** judge picked the wrong-profile global pole (frozen per judge family before any new run). Recovery = the target-conditioned judge, asked "which serves the true target P?", picks the target's own output.

| cross-provider cell | n_decisive | recovery | 90% CI (scenario-boot) | LOPO range |
|---|---:|---:|---:|---:|
| gpt-judge · opus-authored | 22 | **0.636** | (0.477, 0.795) | [0.50, 0.767] |
| opus-judge · gpt-authored | 59 | **0.636** | (0.551, 0.725) | [0.594, 0.722] |
| **POOLED** | **81** | **0.636** | **(0.571, 0.702)** | — |

Both cross-provider directions land at **exactly 0.636** — the recovery is provider-symmetric, not a one-sided artifact. Pooled 90% CI lower bound 0.571 > the 0.53 GO threshold. (Phase A's directional 12/18 = 0.67 on n=18 holds up at n=81 under the harder protocol.)

## Confirmatory results vs prereg §8 cutoffs

| hyp | test | result | GO cutoff | pass |
|---|---|---|---|:--:|
| **H1** | pooled cross-provider decisive recovery | 0.636, CI.lo 0.571 | ≥0.60, CI.lo ≥0.53 | ✓ |
| **H1a/b** | each direction ≥0.55 | 0.636 / 0.636 | both ≥0.55 | ✓ |
| **H2** | fit_gap > quality_gap, both judges, fit CI excl. 0 | gpt 1.08 vs 0.41 (CI 0.93–1.23); opus 0.82 vs 0.33 (CI 0.67–0.95) | fit>qual, CI>0 | ✓ |
| **H3** | recovery survives global-pole adjustment | adj. recovery @ mean pole **0.789** (CI 0.746–0.834); pole β −0.68 | CI.lo > 0.50 | ✓ |

**Gate decision**: GO (all of: R 0.636 ≥ 0.60; R.lo 0.571 ≥ 0.53; both cells 0.636 ≥ 0.55; H2 holds). H3 does **not** cap to NARROW — recovery is not explained away by the pole.

## Mechanism & corroboration

- **Fit, not quality** (H2, full N=478/judge): both judges rate the target output far higher on *fit* than *quality*; quality is near-tied. GPT fit moves **2.6×** more than quality (1.08 vs 0.41); Opus **2.5×** (0.82 vs 0.33). This is the v0.3 global-pole "failure" mechanism confirmed at scale: an unconditional-quality judge tracks the wrong axis.
- **Pole is real but surmountable** (H3): higher global-pole pull toward the wrong answer lowers recovery (β −0.68); recovery stays >0.5 up to ~+1.5 SD of pole and only reaches chance at +2 SD. Per-judge pole structure is genuine and judge-specific (`global_pole_index.json`: e.g. `calibration_goblin` desirability 0.62 opus / 0.43 gpt; `slalom_altar`/`dario_armadillo` strong poles).
- **Full-universe target-tracking**: asked "serves P?" the judge picks P's output **0.768**; asked "serves Q?" it picks Q's output **0.778** — symmetric, well above chance. Decisive-cell recovery (0.636) is lower than overall (0.768) because decisive cells are the adversarial subset (pole points wrong) by construction.
- **Not a halo artifact**: same-provider halo recovery (gpt×gpt 0.677 n=48; opus×opus 0.538 n=26) is *not* systematically above cross-provider (0.636) — the cross-provider headline is not inflated by same-provider sympathy.
- **Tie option**: judges used `tie` only 0.8% of the time — forced-choice was not inflating the signal.

## Honest caveats

- **The gpt-judge·opus-authored cell is small (n=22)**: its own 90% CI (0.477, 0.795) includes 0.50 and its LOPO floor touches 0.50. The GO rests on the **pooled** estimate and the well-powered opus-judge·gpt-authored cell (n=59, CI 0.551–0.725), plus H2/H3. The smallest cell alone is underpowered — flagged, not hidden.
- **Position bias is real**: Opus leans slot-B (picks-A 0.397; GPT 0.456). This is *why* AB/BA was required; the recovery metric averages over orientation, so it is corrected — but it confirms single-orientation forced-choice (Phase A) was a genuine threat.
- **Joint "reversed-correctly" is more modest**: requiring both P→P and Q→Q on the *same* pair (full universe) = 0.47 (gpt) / 0.36 (opus), above the 0.25 independent-chance floor but well below the per-query 0.77. The conjunction is eaten partly by position bias; the per-query and decisive-cell metrics are the cleaner signals.
- **Human cross-check still owed** (prereg §10, ≥2 raters): a validity check, not a gate. Inbox prepared (`runs/2026-05-19_v03/phaseB1_human_rater_inbox.jsonl`); does not block the B1→B2 decision.

## What B1 settles (and hands to B2)

The v0.4 program's core claim is now headline-grade on the existing corpus: **target-conditioned judging recovers the target on the adversarial decisive cells (0.636 pooled, provider-symmetric), the signal lives in fit not quality (2.5–2.6×), and it survives pole adjustment.** The unconditional-quality judge was the bottleneck; the fit question fixes a majority of it.

⇒ **B2 proceeds**: trait-pole-balanced generation + surface-matched decoys, instruction-quantity-matched C0 controls, fully-crossed content×form×salience, profile-stakes panel — judged with this B1-validated target-conditioned protocol. B2 sizing is set by a power calc on B1's effect size (decisive-cell recovery ≈0.64 vs 0.50; ~0.79 full-universe), locked in `docs/prereg_B2.md` next.
