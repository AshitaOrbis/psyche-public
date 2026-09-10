import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Implicit Theories of Intelligence Scale (ITIS)
 * 8-item measure of growth vs. fixed mindset about intelligence.
 * Source: Dweck (1999) — Self-theories: Their role in motivation, personality, and development.
 *
 * Items 1-4: Entity theory (fixed mindset) — forward-scored (higher raw = disagree with fixed = growth)
 * Items 5-8: Incremental theory (growth mindset) — reverse-scored (higher raw = disagree with growth = fixed)
 *
 * Scale labeled so that Strongly Agree=1, Strongly Disagree=6.
 * For entity items: disagreeing (6) = growth mindset → forward-scored
 * For incremental items: agreeing (1) = growth mindset → reverse-scored
 */

interface DweckItem {
  text: string;
  reversed: boolean;
}

const ITEMS: DweckItem[] = [
  // Entity theory items (fixed mindset statements) — forward-scored
  { text: "You have a certain amount of intelligence, and you really can't do much to change it.", reversed: false },
  { text: "Your intelligence is something about you that you can't change very much.", reversed: false },
  { text: "To be honest, you can't really change how intelligent you are.", reversed: false },
  { text: "You can learn new things, but you can't really change your basic intelligence.", reversed: false },

  // Incremental theory items (growth mindset statements) — reverse-scored
  { text: "No matter how much intelligence you have, you can always change it quite a bit.", reversed: true },
  { text: "You can always substantially change how intelligent you are.", reversed: true },
  { text: "No matter who you are, you can significantly change your intelligence level.", reversed: true },
  { text: "You can change even your basic intelligence level considerably.", reversed: true },
];

const dweckItis: Instrument = {
  id: "dweck-itis",
  name: "Implicit Theories of Intelligence Scale",
  shortName: "Growth Mindset",
  description:
    "Measures beliefs about the malleability of intelligence — whether intelligence is seen as fixed (entity theory) or developable (incremental/growth theory). High scores indicate stronger growth mindset.",
  citation:
    "Dweck, C. S. (1999). Self-theories: Their role in motivation, personality, and development. Psychology Press.",
  itemCount: 8,
  estimatedMinutes: 1,
  scales: [
    { id: "growth_mindset", name: "Growth Mindset", description: "Belief that intelligence can be developed through effort and learning" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `dweck-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 6,
      labels: [
        "Strongly Agree",
        "Agree",
        "Mostly Agree",
        "Mostly Disagree",
        "Disagree",
        "Strongly Disagree",
      ],
    },
    scaleId: "growth_mindset",
    reversed: item.reversed,
  })),
};

registerInstrument(dweckItis, scoreLikert);

export default dweckItis;
