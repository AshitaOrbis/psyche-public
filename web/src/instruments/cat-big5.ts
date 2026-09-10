/**
 * CAT Big Five — Adaptive personality assessment using IRT.
 *
 * Loads GRM item bank at runtime and runs per-facet adaptive testing.
 * Heavy tier only. Seeds per-facet priors from fixed-form NEO-300/120 scores
 * (calibrated theta/se when present; otherwise an approximate percentile-derived
 * prior with conservative SE — see cat-controller.ts fixedFormPrior()).
 */

import { registerInstrument } from "./registry";
import type { Instrument, InstrumentResult, InstrumentSession } from "./types";

const FACET_NAMES: Record<string, string> = {
  N1: "Anxiety", N2: "Anger", N3: "Depression",
  N4: "Self-Consciousness", N5: "Immoderation", N6: "Vulnerability",
  E1: "Friendliness", E2: "Gregariousness", E3: "Assertiveness",
  E4: "Activity Level", E5: "Excitement-Seeking", E6: "Cheerfulness",
  O1: "Imagination", O2: "Artistic Interests", O3: "Emotionality",
  O4: "Adventurousness", O5: "Intellect", O6: "Liberalism",
  A1: "Trust", A2: "Morality", A3: "Altruism",
  A4: "Cooperation", A5: "Modesty", A6: "Sympathy",
  C1: "Self-Efficacy", C2: "Orderliness", C3: "Dutifulness",
  C4: "Achievement-Striving", C5: "Self-Discipline", C6: "Cautiousness",
};

const DOMAIN_NAMES: Record<string, string> = {
  N: "Neuroticism", E: "Extraversion", O: "Openness",
  A: "Agreeableness", C: "Conscientiousness",
};

// Use intersection type to add adaptive flag beyond the Instrument interface
const instrument = {
  id: "cat-big5",
  name: "CAT Big Five (Adaptive)",
  shortName: "CAT-B5",
  description: "Computerized Adaptive Testing for Big Five personality facets using IRT Graded Response Model. Adapts item selection to maximize measurement precision per facet.",
  citation: "SAPA Project (Condon & Revelle, 2014). GRM: Samejima (1969).",
  itemCount: 0, // Dynamic — depends on stopping criteria
  estimatedMinutes: 15,
  adaptive: true as const,
  // Scales: 5 domains + 30 facets
  scales: [
    ...Object.entries(DOMAIN_NAMES).map(([id, name]) => ({ id, name })),
    ...Object.entries(FACET_NAMES).map(([id, name]) => ({
      id,
      name,
      parentId: id[0],
    })),
  ],
  items: [] as Instrument["items"],
} satisfies Instrument & { adaptive: true };

// CAT instruments don't use the standard scoring function —
// scoring is handled by the CATController + scoreAdaptive().
// This placeholder returns empty results if called directly.
function scoreCATPlaceholder(
  _instrument: Instrument,
  _session: InstrumentSession,
): InstrumentResult {
  return {
    instrumentId: "cat-big5",
    completedAt: Date.now(),
    scores: [],
  };
}

registerInstrument(instrument, scoreCATPlaceholder);

export { FACET_NAMES as CAT_BIG5_FACET_NAMES, DOMAIN_NAMES as CAT_BIG5_DOMAIN_NAMES };
