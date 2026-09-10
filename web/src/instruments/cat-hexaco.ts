/**
 * CAT HEXACO — Adaptive HEXACO assessment using IRT.
 *
 * Loads GRM item bank at runtime and runs per-facet adaptive testing.
 * Heavy tier only. Seeds per-facet priors from fixed-form HEXACO-200/60 scores
 * (calibrated theta/se when present; otherwise an approximate percentile-derived
 * prior with conservative SE — see cat-controller.ts fixedFormPrior()).
 */

import { registerInstrument } from "./registry";
import type { Instrument, InstrumentResult, InstrumentSession } from "./types";

const FACET_NAMES: Record<string, string> = {
  HH1: "Sincerity", HH2: "Fairness", HH3: "Greed-Avoidance", HH4: "Modesty",
  EM1: "Fearfulness", EM2: "Anxiety", EM3: "Dependence", EM4: "Sentimentality",
  EX1: "Social Self-Esteem", EX2: "Social Boldness", EX3: "Sociability", EX4: "Liveliness",
  AG1: "Forgiveness", AG2: "Gentleness", AG3: "Flexibility", AG4: "Patience",
  CO1: "Organization", CO2: "Diligence", CO3: "Perfectionism", CO4: "Prudence",
  OP1: "Aesthetic Appreciation", OP2: "Inquisitiveness", OP3: "Creativity", OP4: "Unconventionality",
};

const DOMAIN_NAMES: Record<string, string> = {
  HH: "Honesty-Humility", EM: "Emotionality", EX: "Extraversion",
  AG: "Agreeableness", CO: "Conscientiousness", OP: "Openness",
};

const instrument = {
  id: "cat-hexaco",
  name: "CAT HEXACO (Adaptive)",
  shortName: "CAT-HX",
  description: "Computerized Adaptive Testing for HEXACO personality facets using IRT Graded Response Model.",
  citation: "SAPA Project. HEXACO: Lee & Ashton (2004). GRM: Samejima (1969).",
  itemCount: 0,
  estimatedMinutes: 10,
  adaptive: true as const,
  scales: [
    ...Object.entries(DOMAIN_NAMES).map(([id, name]) => ({ id, name })),
    ...Object.entries(FACET_NAMES).map(([id, name]) => ({
      id,
      name,
      parentId: id.slice(0, 2),
    })),
  ],
  items: [] as Instrument["items"],
} satisfies Instrument & { adaptive: true };

function scoreCATPlaceholder(
  _instrument: Instrument,
  _session: InstrumentSession,
): InstrumentResult {
  return {
    instrumentId: "cat-hexaco",
    completedAt: Date.now(),
    scores: [],
  };
}

registerInstrument(instrument, scoreCATPlaceholder);

export { FACET_NAMES as CAT_HEXACO_FACET_NAMES, DOMAIN_NAMES as CAT_HEXACO_DOMAIN_NAMES };
