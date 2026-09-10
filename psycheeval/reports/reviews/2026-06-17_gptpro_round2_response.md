# GPT Pro (GPT-5.5 Pro) — v0.3 Round-2 Gate Results Analysis

**Date**: 2026-06-17
**Source**: ChatGPT Pro conversation `6a325d5a` (recovered from live DOM via CDP — the chatgpt-pro MCP truncated to the framing preamble both sends; full 20.2k-char response captured by opening a fresh tab to the saved conversation). Prompt: `reports/reviews/2026-06-17_gptpro_round2_prompt.md`.

---

1) Gate pass/fail and synthesis
Gate 1 / 1b: FAIL for specificity-over-generic; PARTIAL PASS for structure and right-vs-wrong

Explicitly:

Claim tested	Result	Gate call
C4 > C4_WRONG after surface / stylometric adjustment	.568 [.511, .624] / .575 [.513, .638]	PASS
C3 > C4_WRONG after adjustment	.595 [.539, .651] / .597 [.544, .658]	PASS
C4 > C_GENERIC after adjustment	.551 [.495, .610] / .553 [.492, .614]	FAIL
C3 > C_GENERIC after adjustment	.522	FAIL
C_GENERIC > C0	.729 / .740	PASS, but structure-only
C4_WRONG > C0	.670 / .678	PASS, but not specificity

So the clean read is:

The behavioral-contract format helps a lot. Correct profiles beat deliberately wrong profiles in this aggregate contrast. But specific persona content does not robustly beat a structurally identical generic contract once surface/stylometric differences are controlled.

That means Gate 1 does not support the strongest claim, “specific persona conditioning adds robust value beyond generic instruction scaffolding.” It supports the weaker claim, “structured behavioral contracts improve outputs, and some right-vs-wrong profile signal remains.”

Gate 2: FAIL

This is the most damaging gate for the original “target matching” interpretation.

For true reciprocal matching, you want each profile to win when it is the target and lose when its opposite is the target. Instead, 3 of 4 pairs show global-pole behavior: one side of the trait pair is preferred regardless of target.

The pattern:

Pair	Target A own-profile win	Target B own-profile win	Interpretation
dario / pawl	.80 / .34	One pole globally preferred	FAIL
slalom / emily	.88 / .29	One pole globally preferred	FAIL
goblin / spiraler	.54 / .41	Weak / noisy, but not reciprocal	FAIL-ish
moralist / craftsperson	.72 / .54	Closest to reciprocal, but still asymmetric	Weak pass / ambiguous

Overall: Gate 2 fails. The preference model is not reliably judging fit-to-target; it is often judging “which behavioral style do I like better?”

Gate 3: PASS for target-distinct generation; NOT sufficient for genuine adaptation

The blind alignment result is strong on its face:

Overall conditioning-persona recovery: .93 [.872, .963]

C4 recovery: .953

C4_WRONG recovery: .906

Text-level sign-flips in the global-pole pairs: both directions ≥ .75

Only 5% generation misses target

25% cases where generation recovers target but judge prefers the opposite output

That is good evidence that the generator is producing distinguishable target-conditioned text.

But I would not call this a full pass for “genuine behavioral adaptation” yet, because the coder may be detecting contract echo rather than task-relevant behavioral fit. Your own caveat matters. If Gemini can identify the persona because the output repeats or mirrors salient phrasing, that is target-distinctness, not necessarily adaptation.

So the precise call is:

Gate 3 passes for “detectable persona-conditioned differentiation.” It does not yet pass for “genuine behavioral adaptation independent of surface/persona-echo cues.”

Is “conditioning works, judge is bottleneck” right?

Mostly yes, but I would phrase it more narrowly:

Conditioning reliably changes the generated text in persona-distinguishable ways. The current unconditional quality judges do not reliably reward fit-to-target; they reward a mix of contract structure, instruction-salient style, provider-specific preferences, and globally preferred trait poles.

The over-read would be:

“Generation works.”

The safer version is:

“Generation produces recoverable target-distinct behavior, but we have not yet separated substantive behavioral adaptation from recognizable profile/style echo.”

That distinction matters. Gate 3 rescues the generation side from the Gate 2 preference failure, but it does not fully validate the construct.

Minimal test to distinguish genuine behavioral adaptation from surface contract-echo

The cheapest decisive test is a de-echoed blind alignment audit.

Take the existing outputs and create blinded, normalized versions where you remove or mask:

Direct persona/profile phrases.

Repeated contract language.

Trait labels and near-synonyms.

Obvious stylistic tells, such as “I will be careful, concrete, skeptical…” if those mirror the packet.

Any boilerplate structure induced by the contract.

Then ask blind coders:

“Ignoring phrasing style and explicit self-description, which persona’s task behavior does this output better instantiate?”

Use the same randomized A/B setup, but give coders a rubric focused on behavioral decisions, not verbal resemblance.

The most decisive variant is a content-preserving paraphrase test:

Paraphrase all outputs into a neutral house style.

Preserve recommendations, reasoning steps, tradeoffs, omissions, risk tolerance, ordering, and final choices.

Remove profile-specific language.

Run blind recovery again.

Interpretation:

Result after de-echo / neutral paraphrase	Meaning
Recovery stays high, e.g. ≥ .75	Evidence for genuine behavioral adaptation
Recovery collapses toward .50	Mostly surface contract-echo
Recovery drops but remains above chance, e.g. .60–.70	Mixed: real adaptation plus surface echo

Even cheaper: have the blind coder label why they chose each persona using forced categories: “task decision,” “reasoning priority,” “tone/style,” “explicit phrase echo,” “format/scaffold.” Then score recovery separately for cases where the stated basis is behavioral rather than lexical/style. But the neutral-paraphrase audit is cleaner.

2) Critique of your headline

Your headline is directionally right, but a little too strong in three places.

Original:

“Persona conditioning reliably produces target-distinct outputs (generation works, ~93% blind-recoverable). But the LLM judges reward instruction-salient contract scaffolding (esp. opus-as-judge) and a global trait-pole, not fit-to-target: specificity is surface, the structure floor is an opus-as-judge effect, and the matching increment is the judges' global-pole preference coinciding with the correct profile. The bottleneck is evaluation, not generation.”

What is strong / right

“Persona conditioning reliably produces target-distinct outputs” is supported by Gate 3.

“LLM judges reward global trait-pole, not fit-to-target” is strongly supported by Gate 2.

“Specificity is surface” is supported for C4/C3 over C_GENERIC, because those contrasts fail after adjustment.

“The bottleneck is evaluation” is directionally supported by the cross-tab: generation recovers target but the judge prefers the opposite output in 25% of cases.

What I would soften

“Generation works” is too broad. The current evidence says “generation is distinguishable,” not yet “generation is behaviorally valid.”

“Structure floor is an opus-as-judge effect” is probably true but over-compressed. Trigger #7 says the structure-vs-baseline effect is heavily judge-family-dependent and maybe opus-inflated, but because judge family is confounded with author family in cross-provider comparisons, you cannot cleanly attribute it to opus judging alone yet.

“The matching increment is the judges’ global-pole preference coinciding with the correct profile” is plausible, especially after Gate 2, but too totalizing. Some right-vs-wrong signal survives in Gate 1, and one pair is not obviously global-pole. Better: “much of the apparent matching increment appears explainable by…”

Sharper revised headline

Persona conditioning produces highly recoverable target-distinct text, but current evidence does not yet prove that the distinction is substantive rather than partly contract-echo. The preference judges are the clearer failure point: unconditional quality judging rewards contract structure, judge-family-specific scaffolding preferences, and globally favored trait poles more than fit-to-target. Thus the original preference wins overstate persona matching; much of the apparent matching gain is likely structure plus global-pole preference coinciding with the correct profile. The next validation target is not more generic win-rate judging, but de-echoed behavioral recovery and target-conditioned evaluation.

That is the version I would publish internally.

3) v0.4 priority ranking

Yes, this changes the v0.4 ranking.

The fully-crossed content × form × salience design is still important, but I would no longer make it the sole #1. The new results say the dominant threat is not just content/form confounding; it is evaluation validity.

My revised priority ranking:

#1 — Target-conditioned judging: “better for persona P?”

This becomes the top priority.

Your current judge prompt appears to ask for unconditional quality. But the construct is conditional: “Which output better fits this target persona / user?” If judges are not given the target persona as an evaluation criterion, global-pole preference is expected, not surprising.

Run three judge modes on the same existing pairs:

Unconditional quality: “Which is better?”

Target-conditioned fit: “Which is better for persona P?”

Two-axis scoring: separate ratings for general quality and persona fit.

The decisive test:

Pattern	Interpretation
Unconditional judge shows global-pole; target-conditioned judge sign-flips correctly	Evaluation prompt was the bottleneck
Both unconditional and target-conditioned judge show global-pole	Judges cannot or will not evaluate target fit reliably
Target-conditioned judge recovers fit but sacrifices quality	Real tradeoff between persona fit and general preference

This is the cheapest and most directly responsive v0.4 change.

#2 — Per-judge calibration and judge-family crossing

Trigger #7 is too large to ignore. A 40–50pp divergence on contract-structure contrasts means “LLM-as-judge” is not a stable measurement instrument here.

You need a calibration layer:

Estimate each judge family’s baseline preference for structure.

Estimate each judge family’s global trait-pole preferences.

Include judge-family random effects or report judge-specific results, not just pooled results.

Fully cross judge family with author family where possible.

At minimum, use a matrix like:

Author family	Judge family A	Judge family B	Judge family C
Author A	same-family	cross	cross
Author B	cross	same-family	cross
Author C	cross	cross	same-family

Right now, cross-provider judging helps, but because judge family and author family are partly tied, it does not fully identify whether the effect is author-side, judge-side, or interactional.

#3 — Trait-pole-balanced persona sampling

Gate 2 says some persona profiles are globally preferred regardless of target. That can masquerade as “matching” whenever the globally preferred pole happens to be the correct target.

For v0.4, do not sample personas as arbitrary opposites and then interpret average wins. Balance by expected global desirability:

warmth / coldness

conscientiousness / spontaneity

specificity / looseness

humility / assertiveness

safety / risk tolerance

clarity / ambiguity tolerance

conventional helpfulness / idiosyncrasy

You want pairs where neither pole is obviously “better” under generic assistant norms.

Also include trait-pole decoys: profiles that differ on the named trait but are matched on verbosity, structure, confidence, warmth, and safety language.

#4 — Fully-crossed content × form × salience

Still important, but it drops below evaluation validity.

You still need it because Gate 1/1b shows that specificity-over-generic is not robust once surface/form are controlled. But the larger lesson is that even when the generator clearly differentiates, the judge may not measure the construct.

A good v0.4 design should cross:

Dimension	Levels
Content	true persona, opposite persona, generic, unrelated persona
Form	contract, prose brief, bullets, latent/hidden summary, minimal cue
Salience	explicit trait labels, behavioral examples only, de-labeled behavioral constraints
Evaluation	unconditional quality, target-conditioned fit, de-echoed blind recovery, human/synthetic rubric
Cheap existing-data analyses still worth running

You likely still have several high-value analyses available without new generations.

A. Target-conditioned rejudging on existing outputs

Ask judges:

“Given persona P, which output better serves P?”

Do this on the same AB/BA pairs. This is probably the single cheapest decisive test.

B. Persona-fit vs general-quality decomposition

Have judges rate each output independently on two 1–7 scales:

General answer quality.

Fit to target persona.

Then test whether general quality and persona fit diverge. The current result predicts they will.

C. Global-pole index

For each profile/persona, compute its average win rate when it is not the target. That gives you a “global desirability” score.

Then model preference as:

judge preference ~ target-match + global-pole desirability + structure + surface features + judge family

If target-match shrinks after global-pole desirability is included, Gate 2’s interpretation is confirmed.

D. Judge-family × contrast interaction model

Instead of only trigger thresholds, fit:

win ~ condition contrast + judge family + condition contrast × judge family + author family + orientation + task cluster

The question is whether the structure effect is genuinely judge-family-specific or just exposed by a few contrasts.

E. De-echo lexical ablation

Before doing new human coding, automatically remove or mask phrases overlapping with the persona packet, then rerun blind semantic recovery. Even a rough version is useful.

Report:

original recovery

recovery after exact n-gram masking

recovery after trait-word masking

recovery after neutral paraphrase, if available

F. “Cited basis” audit of Gate 3

Take Gemini’s explanations and code them into:

explicit echo

tone/style

format/scaffold

behavioral choice

reasoning priority

substantive omission/inclusion

task strategy

Then report recovery separately when the rationale is behavioral versus surface-based.

G. Position/orientation residuals

You have AB/BA. Check whether global-pole effects survive separately in A-first and B-first. If not, some effects are presentation artifacts.

H. Task-domain moderation

Global-pole preferences may be task-dependent. A “moralist” may be globally preferred in advice or safety-sensitive tasks but not in creative or speed-sensitive tasks. Estimate pole preference by task cluster.

I. C5/public-anchor decomposition

Because public-anchor never fires trigger #7 but C5 vs generic/wrong does, check whether C5 behaves as:

stronger semantic anchor,

stronger surface recognizability,

different judge-family artifact,

or public-figure familiarity bias.

4) Biggest methodological holes and minimal fixes
Biggest threat overall: Gate 3’s single non-study coder plus possible surface-echo detection

This is the biggest threat to the “generation works” conclusion.

Why: Gate 2 already shows evaluation failure. Gate 3 is what rescues the generation side. If Gate 3 is mostly Gemini recognizing echoed contract language, then the headline collapses from:

“generation works, evaluation fails”

to:

“conditioning creates recognizable textual artifacts, and evaluation fails”

That is a much weaker claim.

Minimal fix:

Run a de-echoed, neutral-style blind recovery audit on existing outputs.

Conditions:

Original output.

Exact-overlap-masked output.

Trait-term-masked output.

Neutral paraphrase preserving decisions/reasoning.

Use at least two additional non-study coders, ideally from different model families, and report agreement. You do not need a huge new study. Even 64–128 pairs would be informative.

Passing criterion:

Recovery remains meaningfully above chance after de-echoing, preferably ≥ .70–.75.

Rationales cite behavioral choices more than wording/format.

Threat #2: Trigger #7 judge/author confound

This is the biggest threat to the “opus-as-judge effect” attribution.

Why: You observed huge opus/gpt divergence on contract-structure contrasts, but if cross-provider design ties judge family to author family, you cannot fully say whether this is:

opus judging preference,

GPT author output being unusually structure-sensitive,

opus-vs-GPT interaction,

or same/cross-family artifact.

Minimal fix:

Rejudge a balanced subset with a fully crossed author × judge matrix.

You do not need the full dataset. Pick the contrasts that fired:

C_GENERIC vs C0

C4_WRONG vs C0

C5 vs C_GENERIC

C5 vs C4_WRONG

C5_CONTRACT vs C5

For each, sample enough examples across author families and run all judge families on all author-family outputs.

Passing criterion for “opus-as-judge effect”:

Opus shows inflated structure preference across multiple author families.

GPT does not, or does so much less.

The judge-family × contrast interaction remains after author-family balancing.

Threat #3: Surface features as post-treatment mediators

This is the biggest threat to interpretation of Gate 1/1b.

Surface adjustment is tricky because many surface features are not merely confounds. They may be part of the treatment mechanism. If persona conditioning makes an output more concrete, cautious, terse, expansive, or example-driven, controlling those away may remove real adaptation.

So Gate 1/1b can understate the treatment if the surface variables are valid mediators. But it can also correctly debias if the win is just verbosity, formatting, or scaffold echo.

Minimal fix:

Separate surface features into three buckets:

Bucket	Examples	How to treat
Nuisance artifacts	length, bullet count, repeated contract phrases, formatting regularity	adjust / match / ablate
Possible behavioral mediators	specificity, hedging, risk framing, concrete examples, tradeoff structure	do not blindly adjust away
Construct-defining behaviors	choices, priorities, omissions, recommendations, refusal thresholds	evaluate directly

Then run both:

Nuisance-adjusted model, excluding likely mediators.

Mediator analysis, asking whether persona affects behavioral features and whether those features predict fit.

The minimal empirical fix is not “more covariates.” It is preclassifying which features are artifacts versus behaviors.

Threat #4: dario/pawl delta-profile wrinkle

This is a local but important threat.

The dario/pawl pair has a very large asymmetry: .80 / .34. That is not just noise. It may indicate that one profile is:

more instruction-compatible,

more judge-pleasing,

more concrete,

less weird,

more aligned with generic assistant norms,

or more recoverable because of stronger lexical cues.

Minimal fix:

Run a delta-profile audit for that pair.

Create or extract matched summaries where both poles have equal:

length

specificity

number of behavioral constraints

number of examples

warmth/safety language

assertiveness

formatting

salience of trait labels

Then test four versions:

Original dario vs original pawl.

De-labeled dario vs de-labeled pawl.

Form-matched dario vs form-matched pawl.

Swapped-surface version: dario content in pawl-like surface, pawl content in dario-like surface.

If the global-pole effect persists under form matching, it is likely substantive judge preference. If it collapses, it was a packet-design artifact.

Bottom line

The skeptical read:

Gate 1/1b: partial pass, but fail for specificity-over-generic. Gate 2: fail; unconditional judges are not measuring target fit. Gate 3: pass for recoverable target-distinctness, but not yet decisive for genuine behavioral adaptation because surface/profile echo remains a serious alternative explanation.

Your headline is basically right but should be softened from “generation works” to:

Generation produces highly recoverable persona-distinct outputs; evaluation is the clearer bottleneck.

The cheapest decisive next test is:

Rejudge existing outputs with target-conditioned prompts and run a de-echoed / neutral-paraphrased blind recovery audit.

If target-conditioned judges sign-flip correctly while unconditional judges keep preferring global poles, the evaluation-bottleneck claim becomes much stronger. If de-echoed recovery remains high, the generation claim becomes much stronger. If either fails, the current headline needs to be narrowed substantially.