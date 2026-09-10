import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreBinary } from "../scoring/engine";

/**
 * Snyder Self-Monitoring Scale (Original 25-item)
 * Binary True/False measure of self-monitoring.
 * Source: Snyder (1974) — public domain.
 * Replaces Self-Monitoring-18 (Snyder & Gangestad 1986 revision) in Heavy tier.
 */

interface SmItem {
  text: string;
  /** True = keyed toward high self-monitoring */
  keyedTrue: boolean;
}

const ITEMS: SmItem[] = [
  { text: "I find it hard to imitate the behavior of other people.", keyedTrue: false },
  { text: "My behavior is usually an expression of my true inner feelings, attitudes, and beliefs.", keyedTrue: false },
  { text: "At parties and social gatherings, I do not attempt to do or say things that others will like.", keyedTrue: false },
  { text: "I can only argue for ideas which I already believe.", keyedTrue: false },
  { text: "I can make impromptu speeches even on topics about which I have almost no information.", keyedTrue: true },
  { text: "I guess I put on a show to impress or entertain people.", keyedTrue: true },
  { text: "When I am uncertain how to act in a social situation, I look to the behavior of others for cues.", keyedTrue: true },
  { text: "I would probably make a good actor.", keyedTrue: true },
  { text: "I rarely need the advice of my friends to choose movies, books, or music.", keyedTrue: false },
  { text: "I sometimes appear to others to be experiencing deeper emotions than I actually am.", keyedTrue: true },
  { text: "I laugh more when I watch a comedy with others than when alone.", keyedTrue: true },
  { text: "In a group of people I am rarely the center of attention.", keyedTrue: false },
  { text: "In different situations and with different people, I often act like very different persons.", keyedTrue: true },
  { text: "I am not particularly good at making other people like me.", keyedTrue: false },
  { text: "Even if I am not enjoying myself, I often pretend to be having a good time.", keyedTrue: true },
  { text: "I'm not always the person I appear to be.", keyedTrue: true },
  { text: "I would not change my opinions (or the way I do things) in order to please someone else or win their favor.", keyedTrue: false },
  { text: "I have considered being an entertainer.", keyedTrue: true },
  { text: "In order to get along and be liked, I tend to be what people expect me to be rather than anything else.", keyedTrue: true },
  { text: "I have never been good at games like charades or improvisational acting.", keyedTrue: false },
  { text: "I have trouble changing my behavior to suit different people and different situations.", keyedTrue: false },
  { text: "At a party I let others keep the jokes and stories going.", keyedTrue: false },
  { text: "I feel a bit awkward in company and do not show up quite as well as I should.", keyedTrue: false },
  { text: "I can look anyone in the eye and tell a lie with a straight face (if for a right end).", keyedTrue: true },
  { text: "I may deceive people by being friendly when I really dislike them.", keyedTrue: true },
];

const snyderSm25: Instrument = {
  id: "snyder-sm-25",
  name: "Self-Monitoring Scale (Original)",
  shortName: "Self-Monitor (Full)",
  description:
    "Original 25-item self-monitoring scale measuring the extent to which people monitor and control their expressive behavior and self-presentation. High = social chameleon; Low = cross-situationally consistent.",
  citation:
    "Snyder, M. (1974). Self-monitoring of expressive behavior. Journal of Personality and Social Psychology, 30(4), 526-537.",
  itemCount: 25,
  estimatedMinutes: 4,
  scales: [
    { id: "self-monitoring", name: "Self-Monitoring", description: "Social adaptiveness vs. behavioral consistency" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `sm25-${idx + 1}`,
    text: item.text,
    response: {
      type: "binary" as const,
      labels: ["True", "False"] as [string, string],
    },
    scaleId: "self-monitoring",
    reversed: !item.keyedTrue,
  })),
};

registerInstrument(snyderSm25, scoreBinary);

export default snyderSm25;
