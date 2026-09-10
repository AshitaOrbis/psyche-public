import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Satisfaction With Life Scale (SWLS)
 * 5-item measure of global life satisfaction.
 * Source: Diener, Emmons, Larsen, & Griffin (1985) — public domain.
 */

const ITEMS = [
  "In most ways my life is close to my ideal.",
  "The conditions of my life are excellent.",
  "I am satisfied with my life.",
  "So far I have gotten the important things I want in life.",
  "If I could live my life over, I would change almost nothing.",
];

const swls: Instrument = {
  id: "swls",
  name: "Satisfaction With Life Scale",
  shortName: "SWLS",
  description:
    "Measures global cognitive judgments of one's life satisfaction as a whole, distinct from affect or domain-specific satisfaction.",
  citation:
    "Diener, E., Emmons, R. A., Larsen, R. J., & Griffin, S. (1985). The Satisfaction With Life Scale. Journal of Personality Assessment, 49, 71-75.",
  itemCount: 5,
  estimatedMinutes: 1,
  scales: [
    { id: "life_satisfaction", name: "Life Satisfaction", description: "Global cognitive judgment of life satisfaction" },
  ],
  items: ITEMS.map((text, idx) => ({
    id: `swls-${idx + 1}`,
    text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 7,
      labels: [
        "Strongly Disagree",
        "Disagree",
        "Slightly Disagree",
        "Neither Agree nor Disagree",
        "Slightly Agree",
        "Agree",
        "Strongly Agree",
      ],
    },
    scaleId: "life_satisfaction",
    reversed: false,
  })),
};

registerInstrument(swls, scoreLikert);

export default swls;
