import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Actively Open-Minded Thinking Scale (AOT-13)
 * 13-item measure of disposition toward open-minded thinking.
 * Source: Stanovich & West (2007/2016), Haran, Ritov, & Mellers (2013).
 *
 * Some items are reverse-scored (closed-minded statements).
 */

interface AOTItem {
  text: string;
  reversed: boolean;
}

const ITEMS: AOTItem[] = [
  { text: "Allowing oneself to be convinced by an opposing argument is a sign of good character.", reversed: false },
  { text: "People should take into consideration evidence that goes against their beliefs.", reversed: false },
  { text: "People should revise their beliefs in response to new information or evidence.", reversed: false },
  { text: "Changing your mind is a sign of weakness.", reversed: true },
  { text: "Intuition is the best guide in making decisions.", reversed: true },
  { text: "It is important to persevere in your beliefs even when evidence is brought to bear against them.", reversed: true },
  { text: "One should disregard evidence that conflicts with one's established beliefs.", reversed: true },
  { text: "People should search actively for reasons why they might be wrong.", reversed: false },
  { text: "I believe that loyalty to one's ideals and principles is more important than open-mindedness.", reversed: true },
  { text: "Coming to decisions quickly is a sign of wisdom.", reversed: true },
  { text: "There is nothing wrong with being undecided about many issues.", reversed: false },
  { text: "I think there are many wrong ways, but only one right way, to almost anything.", reversed: true },
  { text: "I believe that the different ideas of right and wrong that people in other societies have may be valid for them.", reversed: false },
];

const aot13: Instrument = {
  id: "aot-13",
  name: "Actively Open-Minded Thinking Scale",
  shortName: "AOT",
  description:
    "Measures the disposition to weigh new evidence against one's beliefs, think about alternatives, and revise opinions. Distinct from openness to experience — captures epistemic flexibility rather than aesthetic curiosity.",
  citation:
    "Haran, U., Ritov, I., & Mellers, B. A. (2013). The role of actively open-minded thinking in information acquisition, accuracy, and calibration. Judgment and Decision Making, 8(3), 188-201.",
  itemCount: 13,
  estimatedMinutes: 2,
  scales: [
    { id: "open_minded_thinking", name: "Actively Open-Minded Thinking", description: "Disposition to consider alternatives and revise beliefs based on evidence" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `aot-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 6,
      labels: [
        "Completely Disagree",
        "Strongly Disagree",
        "Slightly Disagree",
        "Slightly Agree",
        "Strongly Agree",
        "Completely Agree",
      ],
    },
    scaleId: "open_minded_thinking",
    reversed: item.reversed,
  })),
};

registerInstrument(aot13, scoreLikert);

export default aot13;
