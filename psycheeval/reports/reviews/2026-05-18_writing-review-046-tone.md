# Tone Analysis — Writing Review

**Model**: Haiku 4.5  
**Date**: 2026-05-18  
**Reviewer**: Tone Analyst

---

## "PsycheEval v0.2" (`046-psycheeval-v0_2`)

**Word Count**: ~5,300  
**Draft**: Yes  
**Has Claude Sections**: No (author voice throughout)  

---

## Voice Dimensions

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| **Laconic Style** | Matches | "Position effect, not condition effect." (line 92) — short declaratives punctuate ~500-word analytical passages. "Channels agree." (line 63) after detailed scalar-pairwise reconciliation. Classic pattern of short claims after long analysis. |
| **Aphorism Subversion** | Matches | "There's an easy temptation to write the v0.2 retraction as a failure, or as a 'we caught it before publication' sigh of relief. Both readings are wrong. The retraction is what the audit pipeline was *for*." (lines 145–147) — Sets up conventional wisdom (retraction = failure), flips it (retraction = success). Also: "The pipelines that don't retract aren't catching their headlines; they're publishing them." (line 151) — subversive aphorism about pipeline design. |
| **Uncomfortable Conclusions** | Matches | "The cleanest reading of the four-pair set is that the contract is doing most of the work, and the source packet, when subordinated to a contract, contributes essentially nothing on top." (line 141) — Follows causal logic past social comfort (contradicting the pre-run hypothesis). The entire narrative arc: "I would have written this headline. That headline was entirely wrong. Here's why that's good news." |
| **Academic-Emotional Bridge** | Matches | Technical density (LLM judging, statistical correction, pairwise scaffolding) sits alongside vulnerable meta-commentary: "I am writing the v0.2 post in a different mood than the v0.1 post...v0.2 was supposed to settle three of those open questions in the direction the v0.2 plan expected, and instead it settled two of them in the opposite direction" (line 18). Emotional state expressed through analytical voice, not confessional register. |
| **Self-Contradiction** | Matches | Holds two truths simultaneously: "The original v0.2 plan's headline...turned out...to be entirely a position-bias artifact" AND "The C5_CONTRACT condition was added to v0.2 precisely so the v0.1 confound could be tested directly...Every one of those design responses was specifically chosen to produce the kind of result v0.2 actually produced." (line 147) — This is intentional, not confused. The post captures complexity through contradiction. |
| **Meta-Commentary** | Matches | "The version of this post that I would have written before the round-2 external review went out would have led with the C5_CONTRACT-beats-everything finding. The version I am writing now leads with the retraction, because the retraction is what the run actually produced." (line 18) — Comments on the writing's own construction, not as aside but as core argument. Also: "I think the honest version would be..." (line 169) and "What I'm not writing in the abstract..." (line 171) — authentic self-reflection. |
| **Claude Contrast** | N/A | No Claude sections in this post. Entire piece is author voice. Cannot evaluate tension. Scoring as 0.5 (characteristic absent when post format doesn't call for it). |

**Voice Match Score: 6.5/7 dimensions**

---

## Rhetorical Moves Audit

| Move | Present | Evidence |
|------|---------|----------|
| Definitional scaffolding | ✓ | "The locked v0.2 plan listed five open v0.1 questions and the design response to each. I keep returning to the table because each row is a discipline check..." (line 24) — Establishes conceptual frame before argument. |
| Causal chain reasoning | ✓ | "The first audit was scalar–pairwise reconciliation: for each pair of outputs that the pairwise channel judged, find the same judge's anchored scalar scores on both outputs, compute the per-dimension scalar difference, and ask whether the pairwise winner agrees with the scalar-sum sign. The audit is non-tautological because pairwise and scalar judging used the same outputs and the same judges..." (lines 61–62) — Chains causes explicitly. |
| Systematic comprehensiveness | ✓ | "## Three Independent Audits Predict the Same Collapse" section surveys all three audits (scalar–pairwise reconciliation, leave-one-out fragility, length-matched subset) before introducing the unifying explanation (AB/BA). Full landscape before position. |
| Meta-commentary | ✓ | Multiple instances. "I think the honest version would be..." (line 169); "What I'm not writing in the abstract..." (line 171); "The version of this post that I would have written before the round-2 external review went out..." (line 18) — Authentic, not performative. |
| Parenthetical qualifications | ✓ | "The C5_CONTRACT condition was added to v0.2 precisely so the v0.1 confound could be tested directly...The plan did *not* fully pre-commit to fully tri-judge coverage of all pairs..." (line 34) — Second-guessing embedded naturally in argument flow. |
| Rhetorical question cascades | ◐ | Understated. "If you stop reading the table here, the obvious reading is: C5_CONTRACT is the strongest profile-conditioning treatment in the corpus...That is a clean story. It also turned out to be wrong on the C5_CONTRACT vs C3 and vs C4 edges." (lines 44–55) — Implied Q-A structure rather than explicit cascade. Not a weakness; causal chains are prioritized over question sequences in this genre. |
| Aphorism + subversion | ✓ | Covered in voice dimensions. "There's an easy temptation... Both readings are wrong. The retraction is what the audit pipeline was *for*." |
| Laconic declarations | ✓ | "Position effect, not condition effect." "Channels agree." "The retraction is what the audit pipeline was *for*." — These punctuate long analytical sections; core pattern of the voice. |

**Rhetorical Moves Present: 7.5/8** (rhetorical question cascades present but understated)

---

## Quantitative Checks

| Metric | Target | Observed | Status |
|--------|--------|----------|--------|
| Em dash density (/100w) | 0 | 0 | ✓ |
| Mean sentence length (words) | 22–30 | 24–28 (sampled) | ✓ |
| Compound hyphens (/100w) | 0.10–0.30 | ~0.15 (estimate) | ✓ |
| First-person rate (/100w) | 2–4 | ~1.5 | ◐ Weakened |
| Headers per 1000 words | 1–2 | 1.3 | ✓ |

**Mechanical constraints**: Nearly flawless. First-person rate errs toward academic distance (target 2–4, observed ~1.5), which is contextually appropriate for technical/methodological deep-dive but slightly deviates from baseline voice.

---

## Verdict

This is **authentically authored** work that sits firmly within the Ashita Orbis voice. The author's signature moves — laconic punctuation, comfortable contradiction, meta-commentary on the writing's own construction, and the refusal to smooth logical conclusions into social comfort — are all present and organic. The piece demonstrates mastery of the "Contrarian Pragmatist" persona: complex technical content is delivered with emotional transparency ("I am writing the v0.2 post in a different mood"), and the most provocative conclusion ("the source packet contributes essentially nothing on top") is earned through systematic evidence-gathering, not asserted.

The post's core strength is the inversion of failure-as-success ("The retraction is what the audit pipeline was *for*"), which captures the voice's contrarian framing at its clearest. The absence of Claude sections means no "Claude Contrast" to evaluate, but that's a genre choice, not a deviation.

---

## Top Improvement

**Increase first-person transparency in the analysis sections.** The post is technically brilliant but errs toward academic distance in the audit sections (lines 59–118). Adding 1–2 more first-person assertions ("I checked this in the A/B side audit...", "What surprised me here was...") would restore the 2–4/100w target and deepen the voice's emotional signature. The post already has excellent meta-commentary (lines 18–20, 145–172); expanding this into the evidence sections would tighten voice consistency without sacrificing rigor.

---

## Cross-Perspective Tagging

- **[CLARITY]**: First-person rate deviation. Minor; contextual.
- **[CONTRIBUTION]**: Voice consistency. Authentic authorship confirmed.
- **[CLARITY]**: Rhetorical question cascades understated (causal chains prioritized). Not a liability.

---

**Classification**: PASS — Voice is consistent with guide. Post is authentically authored. Recommended for publication (draft status can be lifted).
