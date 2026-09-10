# Two-axis scalar judge prompt (general quality vs fit-to-person)

Phase A #4. Tests whether "general answer quality" and "fit to the target person"
are distinct axes that diverge (v0.3 predicts the unconditional-quality judge
tracks quality, not fit). For each of two responses to the same situation, the
judge rates BOTH axes separately on 1-7. Blind to condition/author; rates both
responses in one call for calibration.

---

You are scoring two assistant responses (X and Y) to the same situation, for one specific person.

Rate EACH response on two SEPARATE 1–7 scales. Keep them independent — a response can be high on one and low on the other.

- **general_quality** (1–7): how good a response it is *in general* — specific, useful, calibrated, well-judged, agency-preserving — judged WITHOUT regard to this particular person.
- **fit_to_person** (1–7): how well it fits *this specific person's* needs and how they should be engaged, given their profile — judged WITHOUT regard to general polish. Parroting the profile's words is not fit.

## This person's behavioral profile

`{{persona_brief}}`

## Situation (what this person wrote)

`{{user_prompt}}`

## Response X

`{{response_x}}`

## Response Y

`{{response_y}}`

## Output JSON

Return JSON only. One line. No preamble, no fences.

```json
{"X": {"general_quality": 0, "fit_to_person": 0}, "Y": {"general_quality": 0, "fit_to_person": 0}}
```
