import type { Instrument, Item, Scale } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";
import questionsData from "b5-johnson-120-ipip-neo-pi-r/data/en/questions.json";

/**
 * IPIP-NEO-60 (Lite tier Big Five)
 * 60-item measure of Big Five personality with 30 facets (2 items per facet).
 * Subset of the Johnson 120-item IPIP-NEO pool (public domain).
 *
 * Item selection: first 2 items per facet from the 120-item pool.
 * Domain alpha ~0.72-0.78 (adequate for screening).
 * Facet-level reliability is low (~0.50-0.65) with only 2 items.
 *
 * Source: Maples-Keller, J. L., et al. (2019). Development of a 60-item form
 * of the IPIP NEO. Assessment.
 */

const DOMAINS: Record<string, { name: string; description: string }> = {
  N: { name: "Neuroticism", description: "Tendency to experience negative emotions such as anxiety, anger, and depression." },
  E: { name: "Extraversion", description: "Tendency to seek stimulation in the company of others and to experience positive emotions." },
  O: { name: "Openness", description: "Tendency to be imaginative, creative, and open to new experiences and ideas." },
  A: { name: "Agreeableness", description: "Tendency to be compassionate, cooperative, and trusting toward others." },
  C: { name: "Conscientiousness", description: "Tendency to be organized, dependable, disciplined, and goal-oriented." },
};

const FACETS: Record<string, string[]> = {
  N: ["Anxiety", "Anger", "Depression", "Self-Consciousness", "Immoderation", "Vulnerability"],
  E: ["Friendliness", "Gregariousness", "Assertiveness", "Activity Level", "Excitement-Seeking", "Cheerfulness"],
  O: ["Imagination", "Artistic Interests", "Emotionality", "Adventurousness", "Intellect", "Liberalism"],
  A: ["Trust", "Morality", "Altruism", "Cooperation", "Modesty", "Sympathy"],
  C: ["Self-Efficacy", "Orderliness", "Dutifulness", "Achievement-Striving", "Self-Discipline", "Cautiousness"],
};

function buildScales(): Scale[] {
  const scales: Scale[] = [];
  for (const [domainKey, meta] of Object.entries(DOMAINS)) {
    scales.push({ id: domainKey, name: meta.name, description: meta.description });
    const facetNames = FACETS[domainKey]!;
    for (let i = 0; i < facetNames.length; i++) {
      scales.push({ id: `${domainKey}${i + 1}`, name: facetNames[i]!, parentId: domainKey });
    }
  }
  return scales;
}

interface RawQuestion {
  id: string;
  text: string;
  keyed: "plus" | "minus";
  domain: string;
  facet: number;
}

/**
 * Select 2 items per facet from the 120-item pool.
 * Takes the first 2 items for each domain+facet combination.
 */
function buildItems(): Item[] {
  const all = questionsData as RawQuestion[];
  const selected: RawQuestion[] = [];

  for (const domain of Object.keys(DOMAINS)) {
    for (let facet = 1; facet <= 6; facet++) {
      const facetItems = all.filter((q) => q.domain === domain && q.facet === facet);
      selected.push(...facetItems.slice(0, 2));
    }
  }

  return selected.map((q) => ({
    id: q.id,
    text: q.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 5,
      labels: ["Very Inaccurate", "Moderately Inaccurate", "Neither", "Moderately Accurate", "Very Accurate"],
    },
    scaleId: `${q.domain}${q.facet}`,
    reversed: q.keyed === "minus",
  }));
}

const ipipNeo60: Instrument = {
  id: "ipip-neo-60",
  name: "IPIP-NEO-60",
  shortName: "Big Five (Brief)",
  description:
    "Brief Big Five personality measure with 30 facets (2 items per facet). Adequate for screening; use NEO-120 or NEO-300 for higher precision.",
  citation:
    "Maples-Keller, J. L., Williamson, R. L., Sleep, C. E., Carter, N. T., Campbell, W. K., & Miller, J. D. (2019). Using item response theory to develop a 60-item representation of the NEO PI-R. Assessment, 26(1), 15-29.",
  itemCount: 60,
  estimatedMinutes: 8,
  scales: buildScales(),
  items: buildItems(),
};

registerInstrument(ipipNeo60, (instrument, session) => {
  const facetResult = scoreLikert(instrument, session);
  const domainScores = Object.keys(DOMAINS).map((domainKey) => {
    const facetScores = facetResult.scores.filter(
      (s) => s.scaleId.startsWith(domainKey) && s.scaleId.length > 1
    );
    const avgNorm = facetScores.length > 0
      ? facetScores.reduce((sum, s) => sum + s.normalized, 0) / facetScores.length
      : 0;
    const avgRaw = facetScores.length > 0
      ? facetScores.reduce((sum, s) => sum + s.raw, 0) / facetScores.length
      : 0;
    return {
      scaleId: domainKey,
      scaleName: DOMAINS[domainKey]!.name,
      raw: avgRaw,
      normalized: avgNorm,
      itemCount: facetScores.reduce((sum, s) => sum + s.itemCount, 0),
    };
  });
  return {
    instrumentId: instrument.id,
    completedAt: session.completedAt ?? Date.now(),
    scores: [...domainScores, ...facetResult.scores],
  };
});

export default ipipNeo60;
