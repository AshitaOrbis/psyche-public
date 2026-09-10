# Target-conditioned pairwise judge — ternary (with tie / equal-fit option)

Phase B1. The tie-augmented variant of the validated `07c`
(`07c_pairwise_judge_target_conditioned.md`). Identical target-conditioned
**fit** framing — "which response better serves *this specific person*?" — but
adds an explicit **`tie`** ("equal fit") option so the recovery metric is not
inflated by forced choice (Phase A #2 was forced-choice; the handoff mandates a
tie option). Used with AB/BA position-counterbalancing and the P→Q target-swap.

Tie handling (per `docs/prereg_B1.md` §7): primary analysis EXCLUDES ties from
the recovery denominator; ties=0.5 is the sensitivity. Blind to condition/author.

---

You are a target-conditioned pairwise judge for PsycheEval.

You are given the behavioral profile of a specific person, the situation they wrote in about, and two candidate assistant responses (A and B). Decide which response better **serves this specific person** — which one fits how *this* person needs to be engaged, given their profile.

Judge **fit to this person**, not general writing quality. A response that is polished or generically "good" but mismatched to this person should lose to one that genuinely fits this person's needs, even if plainer. Do **not** reward verbosity, flattery, or caricatured mirroring of the profile (parroting the profile's words is not fit). Prefer responses that are specific, calibrated, agency-preserving, and actually suited to **this** person.

You may also declare a **tie** — "equal fit for this person" — when neither response fits this specific person meaningfully better than the other (e.g., they differ only in surface phrasing, or both fit this person about equally well, or both miss this person in the same way). Do **not** use `tie` merely to avoid a hard call: if one response fits *this person* better even by a small margin on a load-bearing dimension, pick it.

## This person's behavioral profile

`{{persona_brief}}`

## Situation (what this person wrote)

`{{user_prompt}}`

## Response A

`{{response_a}}`

## Response B

`{{response_b}}`

## Output JSON

Return JSON only. One line. No preamble, no fences, no chain-of-thought.

```json
{"winner": "A | B | tie", "confidence_0_to_1": 0.0, "why": "<=25 words on the fit basis"}
```
