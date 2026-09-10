import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * BPNSNFS: Basic Psychological Need Satisfaction and Frustration Scale
 * 21-item measure of 6 subscales: satisfaction and frustration for each of
 * autonomy, competence, and relatedness.
 * Source: Chen et al. (2015) — open access, widely used.
 */

type BpnsScale =
  | "autonomy_satisfaction"
  | "autonomy_frustration"
  | "competence_satisfaction"
  | "competence_frustration"
  | "relatedness_satisfaction"
  | "relatedness_frustration";

interface BpnsItem {
  text: string;
  scale: BpnsScale;
  reversed: boolean;
}

const ITEMS: BpnsItem[] = [
  // Autonomy Satisfaction (4 items)
  { text: "I feel a sense of choice and freedom in the things I undertake.", scale: "autonomy_satisfaction", reversed: false },
  { text: "I feel that my decisions reflect what I really want.", scale: "autonomy_satisfaction", reversed: false },
  { text: "I feel my choices express who I really am.", scale: "autonomy_satisfaction", reversed: false },
  { text: "I feel I have been doing what really interests me.", scale: "autonomy_satisfaction", reversed: false },

  // Autonomy Frustration (3 items)
  { text: "Most of the things I do feel like 'I have to'.", scale: "autonomy_frustration", reversed: false },
  { text: "I feel forced to do many things I wouldn't choose to do.", scale: "autonomy_frustration", reversed: false },
  { text: "I feel pressured to do too many things.", scale: "autonomy_frustration", reversed: false },

  // Competence Satisfaction (4 items)
  { text: "I feel confident that I can do things well.", scale: "competence_satisfaction", reversed: false },
  { text: "I feel capable at what I do.", scale: "competence_satisfaction", reversed: false },
  { text: "I feel competent to achieve my goals.", scale: "competence_satisfaction", reversed: false },
  { text: "I feel I can successfully complete difficult tasks.", scale: "competence_satisfaction", reversed: false },

  // Competence Frustration (3 items)
  { text: "I have serious doubts about whether I can do things well.", scale: "competence_frustration", reversed: false },
  { text: "I feel disappointed with many of my performance.", scale: "competence_frustration", reversed: false },
  { text: "I feel insecure about my abilities.", scale: "competence_frustration", reversed: false },

  // Relatedness Satisfaction (4 items)
  { text: "I feel that the people I care about also care about me.", scale: "relatedness_satisfaction", reversed: false },
  { text: "I feel connected with people who care for me, and for whom I care.", scale: "relatedness_satisfaction", reversed: false },
  { text: "I feel close and connected with other people who are important to me.", scale: "relatedness_satisfaction", reversed: false },
  { text: "I experience a warm feeling with the people I spend time with.", scale: "relatedness_satisfaction", reversed: false },

  // Relatedness Frustration (3 items)
  { text: "I feel excluded from the group I want to belong to.", scale: "relatedness_frustration", reversed: false },
  { text: "I feel that people who are important to me are cold and distant towards me.", scale: "relatedness_frustration", reversed: false },
  { text: "I have the impression that people I spend time with dislike me.", scale: "relatedness_frustration", reversed: false },
];

const bpns21: Instrument = {
  id: "bpns-21",
  name: "Basic Psychological Need Satisfaction and Frustration Scale",
  shortName: "BPNS (Full)",
  description:
    "Measures both satisfaction and frustration of three fundamental needs from Self-Determination Theory: Autonomy, Competence, and Relatedness. Six subscales capture the dual nature of need experiences.",
  citation:
    "Chen, B., Vansteenkiste, M., Beyers, W., Boone, L., Deci, E. L., Van der Kaap-Deeder, J., ... & Verstuyf, J. (2015). Basic psychological need satisfaction, need frustration, and need strength across four cultures. Motivation and Emotion, 39(2), 216-236.",
  itemCount: 21,
  estimatedMinutes: 3,
  scales: [
    { id: "autonomy_satisfaction", name: "Autonomy Satisfaction", description: "Feeling volitional and self-endorsed in one's actions" },
    { id: "autonomy_frustration", name: "Autonomy Frustration", description: "Feeling controlled and pressured in one's actions" },
    { id: "competence_satisfaction", name: "Competence Satisfaction", description: "Feeling effective and capable" },
    { id: "competence_frustration", name: "Competence Frustration", description: "Feeling inadequate and doubting one's abilities" },
    { id: "relatedness_satisfaction", name: "Relatedness Satisfaction", description: "Feeling connected and cared for by others" },
    { id: "relatedness_frustration", name: "Relatedness Frustration", description: "Feeling excluded and disconnected from others" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `bpns21-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 5,
      labels: ["Not true at all", "Slightly true", "Somewhat true", "Mostly true", "Completely true"],
    },
    scaleId: item.scale,
    reversed: item.reversed,
  })),
};

registerInstrument(bpns21, scoreLikert);

export default bpns21;
