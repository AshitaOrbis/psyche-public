import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Curiosity and Exploration Inventory II (CEI-II)
 * 10-item measure of trait curiosity with two dimensions.
 * Source: Kashdan, Gallagher, Silvia, et al. (2009).
 */

interface CEIItem {
  text: string;
  scale: "stretching" | "embracing";
}

const ITEMS: CEIItem[] = [
  // Stretching: motivation to seek out knowledge and new experiences (5 items)
  { text: "I actively seek as much information as I can in new situations.", scale: "stretching" },
  { text: "I am the type of person who really enjoys the uncertainty of everyday life.", scale: "stretching" },
  { text: "I am at my best when doing something that is complex or challenging.", scale: "stretching" },
  { text: "Everywhere I go, I am out looking for new things or experiences.", scale: "stretching" },
  { text: "I view challenging situations as an opportunity to grow and learn.", scale: "stretching" },

  // Embracing: willingness to embrace the novel, uncertain, and unpredictable (5 items)
  { text: "I like to do things that are a little frightening.", scale: "embracing" },
  { text: "I am always looking for experiences that challenge how I think about myself and the world.", scale: "embracing" },
  { text: "I prefer jobs that are excitingly unpredictable.", scale: "embracing" },
  { text: "I frequently seek out opportunities to challenge myself and grow as a person.", scale: "embracing" },
  { text: "I am the kind of person who embraces unfamiliar people, events, and places.", scale: "embracing" },
];

const ceiII: Instrument = {
  id: "cei-ii",
  name: "Curiosity and Exploration Inventory II",
  shortName: "CEI-II",
  description:
    "Measures trait curiosity across two dimensions: Stretching (seeking knowledge and new experiences) and Embracing (willingness to engage with novelty and uncertainty).",
  citation:
    "Kashdan, T. B., Gallagher, M. W., Silvia, P. J., Winterstein, B. P., Breen, W. E., Terhar, D., & Steger, M. F. (2009). The Curiosity and Exploration Inventory-II. Journal of Research in Personality, 43, 987-998.",
  itemCount: 10,
  estimatedMinutes: 2,
  scales: [
    { id: "stretching", name: "Stretching", description: "Motivation to seek out knowledge and new experiences" },
    { id: "embracing", name: "Embracing", description: "Willingness to embrace the novel, uncertain, and unpredictable" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `cei-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 5,
      labels: [
        "Very Slightly or Not at All",
        "A Little",
        "Moderately",
        "Quite a Bit",
        "Extremely",
      ],
    },
    scaleId: item.scale,
    reversed: false,
  })),
};

registerInstrument(ceiII, scoreLikert);

export default ceiII;
