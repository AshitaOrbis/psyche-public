import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Maximization Scale (MS-13)
 * 13-item measure of maximizing vs. satisficing decision style.
 * Source: Schwartz, Ward, Monterosso, et al. (2002); shortened by Nenkov et al. (2008).
 *
 * Three subscales:
 * - High Standards: setting high standards for outcomes
 * - Alternative Search: extensive search for alternatives
 * - Decision Difficulty: difficulty committing to choices
 */

interface MSItem {
  text: string;
  scale: "high_standards" | "alternative_search" | "decision_difficulty";
}

const ITEMS: MSItem[] = [
  // Alternative Search (4 items)
  { text: "When I watch TV, I channel surf, often scanning through the available options even while attempting to watch one program.", scale: "alternative_search" },
  { text: "When I am in the car listening to the radio, I often check other stations to see if something better is playing, even if I am relatively satisfied with what I'm listening to.", scale: "alternative_search" },
  { text: "I treat relationships like clothing: I expect to try a lot on before finding the perfect fit.", scale: "alternative_search" },
  { text: "I often find it difficult to shop for a gift for a friend.", scale: "alternative_search" },

  // Decision Difficulty (4 items)
  { text: "Renting videos is really difficult. I'm always struggling to pick the best one.", scale: "decision_difficulty" },
  { text: "I find that writing is very difficult, even if it's just writing a letter to a friend, because it's so hard to word things just right.", scale: "decision_difficulty" },
  { text: "No matter what I do, I have the highest standards for myself.", scale: "high_standards" },
  { text: "I never settle for second best.", scale: "high_standards" },

  // High Standards (5 items)
  { text: "Whenever I'm faced with a choice, I try to imagine what all the other possibilities are, even ones that aren't present at the moment.", scale: "alternative_search" },
  { text: "I often fantasize about living in ways that are quite different from my actual life.", scale: "alternative_search" },
  { text: "No matter how satisfied I am with my job, it's only right for me to be on the lookout for better opportunities.", scale: "high_standards" },
  { text: "I often have difficulty deciding what to eat at a restaurant.", scale: "decision_difficulty" },
  { text: "When shopping, I have a hard time finding clothing that I really love.", scale: "decision_difficulty" },
];

const maximization: Instrument = {
  id: "maximization",
  name: "Maximization Scale",
  shortName: "MS-13",
  description:
    "Measures the tendency to maximize (exhaustively search for the best option) vs. satisfice (choose the first acceptable option). Three subscales: High Standards, Alternative Search, and Decision Difficulty.",
  citation:
    "Schwartz, B., Ward, A., Monterosso, J., Lyubomirsky, S., White, K., & Lehman, D. R. (2002). Maximizing versus satisficing: Happiness is a matter of choice. Journal of Personality and Social Psychology, 83, 1178-1197.",
  itemCount: 13,
  estimatedMinutes: 2,
  scales: [
    { id: "high_standards", name: "High Standards", description: "Setting high standards for outcomes and performance" },
    { id: "alternative_search", name: "Alternative Search", description: "Tendency to extensively search for better alternatives" },
    { id: "decision_difficulty", name: "Decision Difficulty", description: "Difficulty committing to and feeling satisfied with choices" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `ms-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 7,
      labels: [
        "Completely Disagree",
        "Disagree",
        "Slightly Disagree",
        "Neutral",
        "Slightly Agree",
        "Agree",
        "Completely Agree",
      ],
    },
    scaleId: item.scale,
    reversed: false,
  })),
};

registerInstrument(maximization, scoreLikert);

export default maximization;
