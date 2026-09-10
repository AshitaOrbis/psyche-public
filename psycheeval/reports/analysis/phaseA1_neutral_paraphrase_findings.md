# Phase A #1 — neutral-paraphrase blind recovery (the decisive echo-vs-adaptation test)

**Date**: 2026-06-28
**Driver**: `drivers/analysis/phaseA1_neutral_paraphrase.py` · **Output**: `reports/analysis/gate1np_results.json` (+ `gate1np_paraphrases.jsonl`, `gate1np_verdicts.jsonl`)
**Cost**: 128 Sonnet-4.6 paraphrase calls (claude CLI) + 64 gemini-3.1-pro recovery calls (agy). 0 paraphrase failures, 0 quota cutoffs, 64/64 tasks clean.

## Purpose
Gate 3 = blind persona recovery **0.93**; Gate 3b (4-gram de-echo) held **0.963**, ruling out *crude verbatim* copying. But #7 found ~33% of the coder's bases still cite short distinctive phrases / tone / format. This is the strong version: rewrite every output into a **neutral house style** (Sonnet 4.6, non-study/non-judge) that **preserves decisions / reasoning / ordering / risk-posture / omissions** but **strips tone, all formatting, and profile-specific phrasing**, then re-run the identical blind Gemini recovery on the paraphrased pairs (briefs unchanged, same /tmp key, agy run from an empty cwd for blindness).

Decision rule: recovery ≥ ~.75 ⇒ genuine behavioral adaptation; → ~.50 ⇒ mostly surface/echo; .58–.75 ⇒ mixed.

## Result
**Neutral-paraphrase recovery = 0.906 [0.843, 0.946]** (n = 128 judgments / 64 tasks).

| stage | recovery | what was stripped |
|---|---:|---|
| Gate 3 (raw) | 0.93 | nothing |
| Gate 3b (4-gram de-echo) | 0.963 | verbatim ≥4-gram overlaps with own contract |
| **#1 (neutral paraphrase)** | **0.906** | **tone + all formatting + profile-specific phrasing (full rewrite)** |

Δ from raw = **−0.024** (well within noise; CIs overlap heavily). Recovery does **not** collapse toward 0.50.

## Reading — generation is genuinely target-serving (echo ruled out)
After aggressive neutralization of style, format, and distinctive phrasing, blind recovery stays at **0.91**. The conditioning persona is therefore recoverable from the **substance** of the responses — which decisions are made, how the reasoning is ordered, what is included/omitted, the risk posture — not from surface phrasing or contract-echo. This **rules out the surface/echo explanation** for the v0.3 93% recovery.

It also resolves #7's open caveat: the 33% of bases that cited echo cues were **correlated with, not the driver of,** recovery — strip the phrasings and the behavioral signal still carries it. Convergent with #3 (a residual genuine target-match effect existed even under unconditional judging) and #7 (recovery mostly behavioral-cited).

## Caveats
- A paraphraser cannot **guarantee** zero residual style transfer (e.g. "load-bearing" survived in spot-checks as substance). So 0.906 is "recovery survives aggressive style/format/phrasing neutralization," strong evidence for substance-level adaptation — not a hermetic isolation. Convergence with Gate 3b (de-echo) and #7 (behavioral coding) is what makes the conclusion robust.
- Single non-study coder (Gemini 3.1 Pro); the 128 within-task judgments treated as independent (optimistic CI), as in Gate 3.
- Sonnet paraphrase preserves substance by instruction; not independently audited for fidelity beyond spot-checks (a v0.4/Phase-B upgrade: human/2nd-model fidelity check on a paraphrase sample).
