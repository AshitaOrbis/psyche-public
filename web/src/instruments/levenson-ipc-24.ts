import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Levenson IPC Locus of Control Scale
 * 24-item measure of three locus of control dimensions:
 * Internal (I), Powerful Others (P), Chance (C).
 * Source: Levenson (1981) — widely used, public domain for research.
 */

type IpcScale = "internal" | "powerful_others" | "chance";

interface IpcItem {
  text: string;
  scale: IpcScale;
  reversed: boolean;
}

const ITEMS: IpcItem[] = [
  // Internal (8 items)
  { text: "Whether or not I get to be a leader depends mostly on my ability.", scale: "internal", reversed: false },
  { text: "When I make plans, I am almost certain to make them work.", scale: "internal", reversed: false },
  { text: "I can pretty much determine what will happen in my life.", scale: "internal", reversed: false },
  { text: "I am usually able to protect my personal interests.", scale: "internal", reversed: false },
  { text: "When I get what I want, it's usually because I worked hard for it.", scale: "internal", reversed: false },
  { text: "My life is determined by my own actions.", scale: "internal", reversed: false },
  { text: "How many friends I have depends on how nice a person I am.", scale: "internal", reversed: false },
  { text: "I feel like what happens in my life is mostly determined by me.", scale: "internal", reversed: false },

  // Powerful Others (8 items)
  { text: "I feel like what happens in my life is mostly determined by powerful people.", scale: "powerful_others", reversed: false },
  { text: "Getting what I want requires pleasing those people above me.", scale: "powerful_others", reversed: false },
  { text: "Although I might have good ability, I will not be given leadership responsibility without appealing to those in positions of power.", scale: "powerful_others", reversed: false },
  { text: "My life is chiefly controlled by powerful others.", scale: "powerful_others", reversed: false },
  { text: "People like myself have very little chance of protecting our personal interests when they conflict with those of strong pressure groups.", scale: "powerful_others", reversed: false },
  { text: "In order to have my plans work, I make sure that they fit in with the desires of people who have power over me.", scale: "powerful_others", reversed: false },
  { text: "I have often found that what is going to happen will happen.", scale: "powerful_others", reversed: false },
  { text: "It's not always wise for me to plan ahead because many things turn out to be a matter of good or bad fortune.", scale: "powerful_others", reversed: false },

  // Chance (8 items)
  { text: "To a great extent my life is controlled by accidental happenings.", scale: "chance", reversed: false },
  { text: "Often there is no chance of protecting my personal interests from bad luck happenings.", scale: "chance", reversed: false },
  { text: "When I get what I want, it's usually because I'm lucky.", scale: "chance", reversed: false },
  { text: "It's chiefly a matter of fate whether or not I have a few friends or many friends.", scale: "chance", reversed: false },
  { text: "I have often found that what is going to happen will happen regardless of what I do.", scale: "chance", reversed: false },
  { text: "It's not always wise for me to plan ahead because many things turn out to be a matter of luck.", scale: "chance", reversed: false },
  { text: "Whether or not I get into a car accident depends mostly on how good a driver the other person is.", scale: "chance", reversed: false },
  { text: "Whether or not I get to be a leader depends on whether I'm lucky enough to be in the right place at the right time.", scale: "chance", reversed: false },
];

const levensonIpc24: Instrument = {
  id: "levenson-ipc-24",
  name: "Levenson IPC Locus of Control Scale",
  shortName: "LOC (Levenson)",
  description:
    "Three-dimensional locus of control: Internal (outcomes from own actions), Powerful Others (outcomes from authority figures), and Chance (outcomes from luck/fate). Replaces the 2-dimensional IE-4 in the Heavy tier.",
  citation:
    "Levenson, H. (1981). Differentiating among internality, powerful others, and chance. In H. M. Lefcourt (Ed.), Research with the locus of control construct (Vol. 1, pp. 15-63). Academic Press.",
  itemCount: 24,
  estimatedMinutes: 4,
  scales: [
    { id: "internal", name: "Internal", description: "Belief that outcomes are determined by own actions and effort" },
    { id: "powerful_others", name: "Powerful Others", description: "Belief that outcomes are determined by authority figures and powerful people" },
    { id: "chance", name: "Chance", description: "Belief that outcomes are determined by luck, fate, or random events" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `ipc-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 6,
      labels: [
        "Strongly Disagree",
        "Disagree",
        "Slightly Disagree",
        "Slightly Agree",
        "Agree",
        "Strongly Agree",
      ],
    },
    scaleId: item.scale,
    reversed: item.reversed,
  })),
};

registerInstrument(levensonIpc24, scoreLikert);

export default levensonIpc24;
