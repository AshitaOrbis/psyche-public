import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Self-Compassion Scale (SCS-26)
 * 26-item measure of self-compassion with six subscales.
 * Source: Neff (2003) — available at self-compassion.org.
 *
 * Six subscales:
 * - Self-Kindness (5 items): being warm toward oneself
 * - Self-Judgment (5 items): being critical of oneself
 * - Common Humanity (4 items): seeing experiences as part of human experience
 * - Isolation (4 items): feeling isolated by suffering
 * - Mindfulness (4 items): balanced awareness of painful feelings
 * - Over-Identification (4 items): over-identifying with painful feelings
 *
 * Subscales are scored independently. Self-Judgment, Isolation, and
 * Over-Identification are "negative" subscales (high = less self-compassionate).
 * Total self-compassion is computed in the analysis pipeline by reversing
 * negative subscales and averaging all six.
 */

interface SCSItem {
  text: string;
  scale: "self_kindness" | "self_judgment" | "common_humanity" | "isolation" | "mindfulness" | "over_identification";
}

const ITEMS: SCSItem[] = [
  // Self-Kindness (5 items)
  { text: "I try to be understanding and patient towards those aspects of my personality I don't like.", scale: "self_kindness" },
  { text: "When I'm going through a very hard time, I give myself the caring and tenderness I need.", scale: "self_kindness" },
  { text: "I'm kind to myself when I'm experiencing suffering.", scale: "self_kindness" },
  { text: "I'm tolerant of my own flaws and inadequacies.", scale: "self_kindness" },
  { text: "I try to be loving towards myself when I'm feeling emotional pain.", scale: "self_kindness" },

  // Self-Judgment (5 items)
  { text: "When I see aspects of myself that I don't like, I get down on myself.", scale: "self_judgment" },
  { text: "When times are really difficult, I tend to be tough on myself.", scale: "self_judgment" },
  { text: "I can be a bit cold-hearted towards myself when I'm experiencing suffering.", scale: "self_judgment" },
  { text: "I'm disapproving and judgmental about my own flaws and inadequacies.", scale: "self_judgment" },
  { text: "I'm intolerant and impatient towards those aspects of my personality I don't like.", scale: "self_judgment" },

  // Common Humanity (4 items)
  { text: "When I feel inadequate in some way, I try to remind myself that feelings of inadequacy are shared by most people.", scale: "common_humanity" },
  { text: "I try to see my failings as part of the human condition.", scale: "common_humanity" },
  { text: "When I'm down and out, I remind myself that there are lots of other people in the world feeling like I am.", scale: "common_humanity" },
  { text: "When things are going badly for me, I see the difficulties as part of life that everyone goes through.", scale: "common_humanity" },

  // Isolation (4 items)
  { text: "When I fail at something that's important to me, I tend to feel alone in my failure.", scale: "isolation" },
  { text: "When I think about my inadequacies, it tends to make me feel more separate and cut off from the rest of the world.", scale: "isolation" },
  { text: "When I'm feeling down, I tend to feel like most other people are probably happier than I am.", scale: "isolation" },
  { text: "When I'm really struggling, I tend to feel like other people must be having an easier time of it.", scale: "isolation" },

  // Mindfulness (4 items)
  { text: "When something painful happens I try to take a balanced view of the situation.", scale: "mindfulness" },
  { text: "When I fail at something important to me I try to keep things in perspective.", scale: "mindfulness" },
  { text: "When something upsets me I try to keep my emotions in balance.", scale: "mindfulness" },
  { text: "When I'm feeling down I try to approach my feelings with curiosity and openness.", scale: "mindfulness" },

  // Over-Identification (4 items)
  { text: "When something upsets me I get carried away with my feelings.", scale: "over_identification" },
  { text: "When I'm feeling down I tend to obsess and fixate on everything that's wrong.", scale: "over_identification" },
  { text: "When something painful happens I tend to blow the incident out of proportion.", scale: "over_identification" },
  { text: "When I fail at something important to me I become consumed by feelings of inadequacy.", scale: "over_identification" },
];

const scs26: Instrument = {
  id: "scs-26",
  name: "Self-Compassion Scale",
  shortName: "SCS",
  description:
    "Measures six dimensions of self-compassion: Self-Kindness vs. Self-Judgment, Common Humanity vs. Isolation, and Mindfulness vs. Over-Identification. Positive and negative poles are scored separately.",
  citation:
    "Neff, K. D. (2003). The development and validation of a scale to measure self-compassion. Self and Identity, 2, 223-250.",
  itemCount: 26,
  estimatedMinutes: 5,
  scales: [
    { id: "self_kindness", name: "Self-Kindness", description: "Being warm and understanding toward oneself in pain" },
    { id: "self_judgment", name: "Self-Judgment", description: "Being harsh and critical toward oneself in pain" },
    { id: "common_humanity", name: "Common Humanity", description: "Seeing one's experiences as part of the larger human experience" },
    { id: "isolation", name: "Isolation", description: "Feeling cut off and isolated by one's suffering" },
    { id: "mindfulness", name: "Mindfulness", description: "Holding painful thoughts and feelings in balanced awareness" },
    { id: "over_identification", name: "Over-Identification", description: "Over-identifying with and ruminating on painful feelings" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `scs-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 5,
      labels: [
        "Almost Never",
        "Rarely",
        "Sometimes",
        "Often",
        "Almost Always",
      ],
    },
    scaleId: item.scale,
    reversed: false,
  })),
};

registerInstrument(scs26, scoreLikert);

export default scs26;
