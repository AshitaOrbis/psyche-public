import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Acceptance and Action Questionnaire II (AAQ-II)
 * 7-item measure of psychological flexibility / experiential avoidance.
 * Source: Bond, Hayes, et al. (2011) — free for research use.
 *
 * All items measure experiential avoidance (inflexibility).
 * Reverse-scored so that high = more psychological flexibility.
 */

const ITEMS = [
  "My painful experiences and memories make it hard for me to live a life that I would value.",
  "I'm afraid of my feelings.",
  "I worry about not being able to control my worries and feelings.",
  "My painful memories prevent me from having a fulfilling life.",
  "Emotions cause problems in my life.",
  "It seems like most people are handling their lives better than I am.",
  "Worries get in the way of my success.",
];

const aaqII: Instrument = {
  id: "aaq-ii",
  name: "Acceptance and Action Questionnaire II",
  shortName: "AAQ-II",
  description:
    "Measures psychological flexibility — the ability to contact the present moment and persist or change behavior in the service of valued ends. High scores indicate greater flexibility.",
  citation:
    "Bond, F. W., Hayes, S. C., Baer, R. A., Carpenter, K. M., Guenole, N., Orcutt, H. K., Waltz, T., & Zettle, R. D. (2011). Preliminary psychometric properties of the AAQ-II. Behavior Therapy, 42, 676-688.",
  itemCount: 7,
  estimatedMinutes: 1,
  scales: [
    { id: "psychological_flexibility", name: "Psychological Flexibility", description: "Ability to accept difficult experiences and act in accordance with values" },
  ],
  items: ITEMS.map((text, idx) => ({
    id: `aaq-${idx + 1}`,
    text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 7,
      labels: [
        "Never True",
        "Very Seldom True",
        "Seldom True",
        "Sometimes True",
        "Frequently True",
        "Almost Always True",
        "Always True",
      ],
    },
    scaleId: "psychological_flexibility",
    reversed: true, // All items measure inflexibility; reverse for flexibility score
  })),
};

registerInstrument(aaqII, scoreLikert);

export default aaqII;
