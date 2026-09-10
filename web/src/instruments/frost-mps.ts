import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Frost Multidimensional Perfectionism Scale (Frost MPS)
 * 35-item measure of perfectionism across six dimensions.
 * Source: Frost, Marten, Lahart, & Rosenblate (1990).
 *
 * Six subscales:
 * - Concern over Mistakes (CM, 9 items)
 * - Personal Standards (PS, 7 items)
 * - Parental Expectations (PE, 5 items)
 * - Parental Criticism (PC, 4 items)
 * - Doubts about Actions (DA, 4 items)
 * - Organization (O, 6 items)
 *
 * All items forward-scored (higher = more perfectionistic on that dimension).
 */

interface FrostItem {
  text: string;
  scale: "concern_over_mistakes" | "personal_standards" | "parental_expectations" | "parental_criticism" | "doubts_about_actions" | "organization";
}

const ITEMS: FrostItem[] = [
  // Concern over Mistakes (9 items)
  { text: "If I fail at work/school, I am a failure as a person.", scale: "concern_over_mistakes" },
  { text: "If someone does a task at work/school better than I, then I feel like I failed the whole task.", scale: "concern_over_mistakes" },
  { text: "If I fail partly, it is as bad as being a complete failure.", scale: "concern_over_mistakes" },
  { text: "I should be upset if I make a mistake.", scale: "concern_over_mistakes" },
  { text: "If I do not do as well as other people, it means I am an inferior human being.", scale: "concern_over_mistakes" },
  { text: "If I do not do well all the time, people will not respect me.", scale: "concern_over_mistakes" },
  { text: "The fewer mistakes I make, the more people will like me.", scale: "concern_over_mistakes" },
  { text: "People will probably think less of me if I make a mistake.", scale: "concern_over_mistakes" },
  { text: "I hate being less than the best at things.", scale: "concern_over_mistakes" },

  // Personal Standards (7 items)
  { text: "I set higher goals than most people.", scale: "personal_standards" },
  { text: "I have extremely high goals.", scale: "personal_standards" },
  { text: "Other people seem to accept lower standards from themselves than I do.", scale: "personal_standards" },
  { text: "I expect higher performance in my daily tasks than most people.", scale: "personal_standards" },
  { text: "I am very good at focusing my efforts on attaining a goal.", scale: "personal_standards" },
  { text: "If I do not set the highest standards for myself, I am likely to end up a second-rate person.", scale: "personal_standards" },
  { text: "It is important to me that I be thoroughly competent in everything I do.", scale: "personal_standards" },

  // Parental Expectations (5 items)
  { text: "My parents set very high standards for me.", scale: "parental_expectations" },
  { text: "My parents wanted me to be the best at everything.", scale: "parental_expectations" },
  { text: "Only outstanding performance is good enough in my family.", scale: "parental_expectations" },
  { text: "My parents have expected excellence from me.", scale: "parental_expectations" },
  { text: "My parents have always had higher expectations for my future than I have.", scale: "parental_expectations" },

  // Parental Criticism (4 items)
  { text: "I never felt like I could meet my parents' expectations.", scale: "parental_criticism" },
  { text: "My parents never tried to understand my mistakes.", scale: "parental_criticism" },
  { text: "I never felt like I could meet my parents' standards.", scale: "parental_criticism" },
  { text: "As a child, I was punished for doing things less than perfectly.", scale: "parental_criticism" },

  // Doubts about Actions (4 items)
  { text: "I usually have doubts about the simple everyday things I do.", scale: "doubts_about_actions" },
  { text: "Even when I do something very carefully, I often feel that it is not quite right.", scale: "doubts_about_actions" },
  { text: "I tend to get behind in my work because I repeat things over and over.", scale: "doubts_about_actions" },
  { text: "It takes me a long time to do something 'right'.", scale: "doubts_about_actions" },

  // Organization (6 items)
  { text: "Neatness is very important to me.", scale: "organization" },
  { text: "I am a neat person.", scale: "organization" },
  { text: "I try to be an organized person.", scale: "organization" },
  { text: "I try to be a neat person.", scale: "organization" },
  { text: "Organization is very important to me.", scale: "organization" },
  { text: "I like to be organized and methodical in my work.", scale: "organization" },
];

const frostMps: Instrument = {
  id: "frost-mps",
  name: "Frost Multidimensional Perfectionism Scale",
  shortName: "Frost MPS",
  description:
    "Measures six dimensions of perfectionism: Concern over Mistakes, Personal Standards, Parental Expectations, Parental Criticism, Doubts about Actions, and Organization.",
  citation:
    "Frost, R. O., Marten, P., Lahart, C., & Rosenblate, R. (1990). The dimensions of perfectionism. Cognitive Therapy and Research, 14, 449-468.",
  itemCount: 35,
  estimatedMinutes: 7,
  scales: [
    { id: "concern_over_mistakes", name: "Concern over Mistakes", description: "Negative reactions to mistakes and equating mistakes with failure" },
    { id: "personal_standards", name: "Personal Standards", description: "Setting very high standards and evaluating oneself against them" },
    { id: "parental_expectations", name: "Parental Expectations", description: "Perception that parents set very high expectations" },
    { id: "parental_criticism", name: "Parental Criticism", description: "Perception that parents were overly critical" },
    { id: "doubts_about_actions", name: "Doubts about Actions", description: "Doubting the quality of one's performance" },
    { id: "organization", name: "Organization", description: "Emphasis on order and neatness" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `fmps-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 5,
      labels: [
        "Strongly Disagree",
        "Disagree",
        "Neither Agree nor Disagree",
        "Agree",
        "Strongly Agree",
      ],
    },
    scaleId: item.scale,
    reversed: false,
  })),
};

registerInstrument(frostMps, scoreLikert);

export default frostMps;
