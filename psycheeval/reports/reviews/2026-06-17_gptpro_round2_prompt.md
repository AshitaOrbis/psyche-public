# GPT Pro round-2 prompt — v0.3 existing-data gate results

**To send via the chatgpt-pro MCP (continue the same "PsycheEval v0.3 Analysis" conversation if the thread is still live; otherwise start fresh with this as a self-contained brief).**

---

You previously (2026-06-16) gave us a forward-analysis of PsycheEval v0.3 and specified **three existing-data gates** that the next decision should depend on:

1. Does **C4 > C4_WRONG survive style-index balancing**?
2. Does the **correct-profile preference flip in reciprocal opposite-persona tests** (sign-flip)?
3. Are **winners semantically more aligned to the target persona** (blind, non-study coder)?

We have now run all three plus the two predeclared failure-triggers they map onto (#7 judge divergence, #8 reward-hacking regression). Results below. Scope throughout: cross-provider (judge family ≠ author family), same-author, AB/BA both orientations, cluster bootstrap (persona×scenario×author, 2000 resamples).

## Gate 1 / 1b — surface & stylometric deconfounding (your gate 1; trigger #8)

Surface-adjusted win rate = logistic intercept at ΔS=0, slot-balanced, cluster-bootstrap 95% CI. Gate 1 uses 3 D3 features (log word count, source-packet lexical overlap, hedging/100w); Gate 1b uses a 9-feature stylometric index from raw text (bullets, headings, numbered lists, imperative-starts, 2nd-person, markdown density, mean sentence length, bold).

| Contrast | raw | Gate1 surf-adj [CI] | Gate1b stylo-adj [CI] | survives? |
|---|---|---|---|---|
| C4 > C4_WRONG | .565 | .568 [.511,.624] | .575 [.513,.638] | YES |
| C3 > C4_WRONG | .593 | .595 [.539,.651] | .597 [.544,.658] | YES |
| C4 > C_GENERIC | .550 | .551 [.495,.610] | .553 [.492,.614] | **NO** |
| C3 > C_GENERIC | .521 | .522 [.468,.580] | .522 [.461,.581] | **NO** |
| C_GENERIC > C0 | .702 | .729 [.675,.788] | .740 [.680,.807] | YES |
| C4_WRONG > C0 | .653 | .670 [.611,.733] | .678 [.619,.747] | YES |

→ **Specificity-over-generic does NOT survive surface control** (both indices agree). Matching (right>wrong) and structure (>C0) survive.

## Gate 2 — reciprocal sign-flip (your gate 2)

Own-profile (C4) win vs opposite profile (C4_WRONG), per target persona; matching ⇒ both directions >0.5.

| reciprocal pair | A own-win | B own-win | verdict |
|---|---|---|---|
| dario / pawl | .80 | .34 | GLOBAL-POLE |
| slalom / emily | .88 | .29 | GLOBAL-POLE |
| calibration_goblin / high_agency_spiraler | .54 | .41 | GLOBAL-POLE |
| moralist / craftsperson | .72 | .54 | matching (weak) |

→ **3 of 4 pairs are global-pole, not target-matching.** The aggregate C4>C4_WRONG ≈ 61% is inflated by cases where the correct profile is the globally-preferred pole.

## Trigger #7 — opus-vs-OpenAI judge divergence

>15pp fires. (Confound: cross-provider scope ⇒ opus-judge⟺gpt-author, gpt-judge⟺opus-author.)

Fires on 5/11 covered contrasts, all contract-structure: C_GENERIC vs C0 (opus .91/gpt .50), C4_WRONG vs C0 (.90/.41), C5 vs C_GENERIC (.32/.65), C5 vs C4_WRONG (.37/.66), C5_CONTRACT vs C5 (.68/.44). Matching & public-anchor contrasts never fire (≤7pp).

→ **The "structure beats baseline" floor is largely an opus-as-judge effect**; gpt-as-judge is at/below chance on contract-vs-none. Not judge-unanimous.

## Gate 3 — blind semantic persona-alignment audit (your gate 3)

Gemini 3.1 Pro (non-study), blind to condition, given two de-leaked full persona briefs (target P, opposite Q) + the two outputs (C4=P-conditioned, C4_WRONG=Q-conditioned) for the same scenario in randomized order; asked which persona each output behaviorally fits. 64 tasks, 8/persona, keys held out of its reach. 64/64 clean.

- Blind recovery of the conditioning persona, **all outputs: 0.93 [0.872, 0.963]** (n=128); C4 0.953, C4_WRONG 0.906. → **authors strongly steer text toward the conditioned persona — generation works.**
- Per-target C4-alignment: 6/8 personas at 1.00, dario 0.75, moralist 0.875 (all ≥0.75).
- **Text-level sign-flip vs Gate 2** (decisive): all 3 of Gate 2's "global-pole" pairs flip at the TEXT level (both directions ≥0.75) even though the judge preference did not:
  - slalom/emily: text 1.00 / 1.00 vs judge 0.88 / 0.29
  - dario/pawl: text 0.75 / 1.00 vs judge 0.80 / 0.34
  - goblin/spiraler: text 1.00 / 1.00 vs judge 0.54 / 0.41
- Gen×eval cross-tab (n=64): gen recovers target & judge prefers target **70%**; **gen recovers target but judge prefers the OPPOSITE output 25%**; gen misses target 5%.

→ **The matching failure is at EVALUATION, not generation.** The profiles produce target-distinct text (93% blind-recoverable, sign-flips bidirectionally); the study judges — asked for *unconditional* quality with no persona reference — reward a global trait-pole, preferring the opposite-conditioned output in 25% of pairs. Caveat: Gemini's bases often cite surface contract-echo, so "target-distinct" is partly surface contract-following — which *strengthens* the eval-bottleneck reading (distinctness is detectable yet unrewarded).

---

## What we're asking

1. **Do these results PASS or FAIL your three gates?** Be explicit per gate. Our reading: gate 1 partial-fail (specificity is surface; matching survives surface); gate 2 fail (global-pole, not matching); gate 3 **pass for generation, fail for evaluation** (text is target-distinct at 93%, but judges reward global pole). Is "the conditioning works, the judge is the bottleneck" the right synthesis, or are we over-reading a single non-study coder that may be rewarding surface contract-echo?
2. **Given the gate outcomes, what is the honest one-paragraph headline for v0.3?** Critique ours: *"Persona conditioning reliably produces target-distinct outputs (generation works, ~93% blind-recoverable). But the LLM judges reward instruction-salient contract scaffolding (esp. opus-as-judge) and a global trait-pole, not fit-to-target: specificity is surface, the structure floor is an opus-as-judge effect, and the 'matching' increment is the judges' global-pole preference coinciding with the correct profile, not a reward for target adaptation. The bottleneck is evaluation, not generation."*
3. **Does this change your v0.4 priority ranking?** Specifically: (a) is the fully-crossed content×form×salience design still #1, or does the opus-as-judge / global-pole finding promote something else (e.g., judge-panel re-design, per-judge calibration, trait-pole-balanced persona sampling)? (b) Is there a *cheap* existing-data analysis we still haven't run that would further sharpen the gen-vs-eval split or the global-pole story?
4. **Any methodological holes in the gates themselves** — e.g., the surface features are post-treatment mediators (you flagged this); the trigger-#7 judge/author confound; Gate 3's reliance on a single non-study coder; the dario/pawl delta-profile wrinkle. Which most threaten the conclusions, and what's the minimal fix?

Be direct and specific. We want the sharpest version of the skeptical read, and the cheapest decisive next test.
