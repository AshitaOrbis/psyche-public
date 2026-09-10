import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Mindful Attention Awareness Scale (MAAS)
 * 15-item measure of dispositional mindfulness (attention and awareness).
 * Source: Brown & Ryan (2003) — public domain via GGSC Berkeley.
 *
 * All items describe experiences of mindlessness/inattention.
 * Scale: 1 = Almost Always, 6 = Almost Never.
 * Higher raw scores = less frequent mindlessness = MORE mindful.
 * All items forward-scored (no reversal needed).
 */

const ITEMS = [
  "I could be experiencing some emotion and not be conscious of it until some time later.",
  "I break or spill things because of carelessness, not paying attention, or thinking of something else.",
  "I find it difficult to stay focused on what's happening in the present.",
  "I tend to walk quickly to get where I'm going without paying attention to what I experience along the way.",
  "I tend not to notice feelings of physical tension or discomfort until they really grab my attention.",
  "I forget a person's name almost as soon as I've been told it for the first time.",
  "It seems I am 'running on automatic' without much awareness of what I'm doing.",
  "I rush through activities without being really attentive to them.",
  "I get so focused on the goal I want to achieve that I lose touch with what I'm doing right now to get there.",
  "I do jobs or tasks automatically, without being aware of what I'm doing.",
  "I find myself listening to someone with one ear, doing something else at the same time.",
  "I drive places on 'automatic pilot' and then wonder why I went there.",
  "I find myself preoccupied with the future or the past.",
  "I find myself doing things without paying attention.",
  "I snack without being aware that I'm eating.",
];

const maas: Instrument = {
  id: "maas",
  name: "Mindful Attention Awareness Scale",
  shortName: "MAAS",
  description:
    "Measures dispositional mindfulness — the tendency to attend to and be aware of present-moment experience in daily life. Items describe mindless experiences; less frequent occurrence indicates greater mindfulness.",
  citation:
    "Brown, K. W., & Ryan, R. M. (2003). The benefits of being present: Mindfulness and its role in psychological well-being. Journal of Personality and Social Psychology, 84, 822-848.",
  itemCount: 15,
  estimatedMinutes: 3,
  scales: [
    { id: "mindful_attention", name: "Mindful Attention", description: "Frequency of open, receptive awareness of and attention to present experience" },
  ],
  items: ITEMS.map((text, idx) => ({
    id: `maas-${idx + 1}`,
    text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 6,
      labels: [
        "Almost Always",
        "Very Frequently",
        "Somewhat Frequently",
        "Somewhat Infrequently",
        "Very Infrequently",
        "Almost Never",
      ],
    },
    scaleId: "mindful_attention",
    reversed: false, // High raw (Almost Never experiencing mindlessness) = high mindfulness
  })),
};

registerInstrument(maas, scoreLikert);

export default maas;
