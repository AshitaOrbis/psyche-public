import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Tangney Self-Control Scale (Full, 36 items)
 * Measures dispositional self-control capacity.
 * Source: Tangney, Baumeister, & Boone (2004).
 *
 * Two-factor structure:
 * - Restraint (impulse control, resisting temptation)
 * - Impulsivity (acting without thinking, poor regulation)
 *
 * Items are a mix of positive (restraint) and negative (impulsivity) wording.
 * Impulsivity items are reverse-scored so that high total = more self-control.
 */

interface TangneyItem {
  text: string;
  scale: "restraint" | "impulsivity";
  reversed: boolean;
}

const ITEMS: TangneyItem[] = [
  // Restraint items (forward-scored)
  { text: "I am good at resisting temptation.", scale: "restraint", reversed: false },
  { text: "I have a hard time breaking bad habits.", scale: "impulsivity", reversed: true },
  { text: "I am lazy.", scale: "impulsivity", reversed: true },
  { text: "I say inappropriate things.", scale: "impulsivity", reversed: true },
  { text: "I do certain things that are bad for me, if they are fun.", scale: "impulsivity", reversed: true },
  { text: "I refuse things that are bad for me.", scale: "restraint", reversed: false },
  { text: "I wish I had more self-discipline.", scale: "impulsivity", reversed: true },
  { text: "People would say that I have iron self-discipline.", scale: "restraint", reversed: false },
  { text: "Pleasure and fun sometimes keep me from getting work done.", scale: "impulsivity", reversed: true },
  { text: "I have trouble concentrating.", scale: "impulsivity", reversed: true },
  { text: "I am able to work effectively toward long-term goals.", scale: "restraint", reversed: false },
  { text: "Sometimes I can't stop myself from doing something, even if I know it is wrong.", scale: "impulsivity", reversed: true },
  { text: "I often act without thinking through all the alternatives.", scale: "impulsivity", reversed: true },
  { text: "I get distracted easily.", scale: "impulsivity", reversed: true },
  { text: "I am good about keeping promises.", scale: "restraint", reversed: false },
  { text: "I eat healthy foods.", scale: "restraint", reversed: false },
  { text: "I exercise regularly.", scale: "restraint", reversed: false },
  { text: "I am reliable.", scale: "restraint", reversed: false },
  { text: "I spend too much money.", scale: "impulsivity", reversed: true },
  { text: "I keep everything neat.", scale: "restraint", reversed: false },
  { text: "I drink alcohol excessively or use drugs.", scale: "impulsivity", reversed: true },
  { text: "I lose my temper too easily.", scale: "impulsivity", reversed: true },
  { text: "Getting up in the morning is hard for me.", scale: "impulsivity", reversed: true },
  { text: "I change my mind fairly often.", scale: "impulsivity", reversed: true },
  { text: "I blurt out whatever is on my mind.", scale: "impulsivity", reversed: true },
  { text: "People can count on me to keep on schedule.", scale: "restraint", reversed: false },
  { text: "I am always on time.", scale: "restraint", reversed: false },
  { text: "I have worked or studied all night at the last minute.", scale: "impulsivity", reversed: true },
  { text: "I am not easily discouraged.", scale: "restraint", reversed: false },
  { text: "I'd be better off if I stopped to think before acting.", scale: "impulsivity", reversed: true },
  { text: "I engage in healthy practices.", scale: "restraint", reversed: false },
  { text: "I do things that feel good in the moment but regret later on.", scale: "impulsivity", reversed: true },
  { text: "I can usually find a way to make myself do the things I need to do.", scale: "restraint", reversed: false },
  { text: "I have trouble saying no.", scale: "impulsivity", reversed: true },
  { text: "I tend to give up easily.", scale: "impulsivity", reversed: true },
  { text: "I am patient.", scale: "restraint", reversed: false },
];

const tangneyScs: Instrument = {
  id: "tangney-scs",
  name: "Self-Control Scale",
  shortName: "Self-Control",
  description:
    "Measures dispositional self-control — the ability to override impulses and regulate behavior. Two factors: Restraint (active impulse control) and Impulsivity (difficulty regulating behavior). High scores indicate greater self-control.",
  citation:
    "Tangney, J. P., Baumeister, R. F., & Boone, A. L. (2004). High self-control predicts good adjustment, less pathology, better grades, and interpersonal success. Journal of Personality, 72, 271-324.",
  itemCount: 36,
  estimatedMinutes: 7,
  scales: [
    { id: "restraint", name: "Restraint", description: "Active impulse control and ability to resist temptation" },
    { id: "impulsivity", name: "Impulsivity", description: "Tendency to act without thinking and difficulty self-regulating" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `tscs-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 5,
      labels: [
        "Not at All Like Me",
        "A Little Like Me",
        "Somewhat Like Me",
        "Mostly Like Me",
        "Very Much Like Me",
      ],
    },
    scaleId: item.scale,
    reversed: item.reversed,
  })),
};

registerInstrument(tangneyScs, scoreLikert);

export default tangneyScs;
