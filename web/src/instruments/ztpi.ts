import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Zimbardo Time Perspective Inventory (ZTPI)
 * 56-item measure of individual differences in time perspective.
 * Source: Zimbardo & Boyd (1999) — available at thetimeparadox.com.
 *
 * Five subscales:
 * - Past-Negative (10 items): negative view of the past
 * - Past-Positive (9 items): warm, sentimental view of the past
 * - Present-Hedonistic (15 items): pleasure-seeking, risk-taking orientation
 * - Present-Fatalistic (9 items): helpless, fatalistic attitude toward present/future
 * - Future (13 items): goal-oriented, planning orientation
 *
 * Some items are reverse-scored within their subscale.
 */

interface ZTPIItem {
  text: string;
  scale: "past_negative" | "past_positive" | "present_hedonistic" | "present_fatalistic" | "future";
  reversed: boolean;
}

const ITEMS: ZTPIItem[] = [
  // Past-Negative (10 items)
  { text: "I think about the bad things that have happened to me in the past.", scale: "past_negative", reversed: false },
  { text: "Painful past experiences keep being replayed in my mind.", scale: "past_negative", reversed: false },
  { text: "I think about the good things that I have missed out on in my life.", scale: "past_negative", reversed: false },
  { text: "I've made mistakes in the past that I wish I could undo.", scale: "past_negative", reversed: false },
  { text: "Things rarely work out as I expected.", scale: "past_negative", reversed: false },
  { text: "It's hard for me to forget unpleasant images of my youth.", scale: "past_negative", reversed: false },
  { text: "I often think of what I should have done differently in my life.", scale: "past_negative", reversed: false },
  { text: "I think about the bad things that were done to me in the past.", scale: "past_negative", reversed: false },
  { text: "Even when I am enjoying the present, I am drawn back to comparisons with similar past experiences.", scale: "past_negative", reversed: false },
  { text: "The past has too many unpleasant memories that I prefer not to think about.", scale: "past_negative", reversed: false },

  // Past-Positive (9 items)
  { text: "Familiar childhood sights, sounds, smells often bring back a flood of wonderful memories.", scale: "past_positive", reversed: false },
  { text: "I enjoy stories about how things used to be in the 'good old times'.", scale: "past_positive", reversed: false },
  { text: "Happy memories of good times spring readily to mind.", scale: "past_positive", reversed: false },
  { text: "I get nostalgic about my childhood.", scale: "past_positive", reversed: false },
  { text: "I like family rituals and traditions that are regularly repeated.", scale: "past_positive", reversed: false },
  { text: "I have fond memories of my birthday celebrations.", scale: "past_positive", reversed: false },
  { text: "I take pleasure in thinking about my past.", scale: "past_positive", reversed: false },
  { text: "On balance, there is much more good to recall than bad in my past.", scale: "past_positive", reversed: false },
  { text: "I miss my childhood.", scale: "past_positive", reversed: false },

  // Present-Hedonistic (15 items)
  { text: "I believe that getting together with one's friends to party is one of life's important pleasures.", scale: "present_hedonistic", reversed: false },
  { text: "I do things impulsively.", scale: "present_hedonistic", reversed: false },
  { text: "I take risks to put excitement in my life.", scale: "present_hedonistic", reversed: false },
  { text: "I try to live my life as fully as possible, one day at a time.", scale: "present_hedonistic", reversed: false },
  { text: "It is important to put excitement in my life.", scale: "present_hedonistic", reversed: false },
  { text: "Taking risks keeps my life from becoming boring.", scale: "present_hedonistic", reversed: false },
  { text: "I prefer friends who are spontaneous rather than predictable.", scale: "present_hedonistic", reversed: false },
  { text: "I like my close relationships to be passionate.", scale: "present_hedonistic", reversed: false },
  { text: "Life is too short to worry about the consequences.", scale: "present_hedonistic", reversed: false },
  { text: "Ideally, I would live each day as if it were my last.", scale: "present_hedonistic", reversed: false },
  { text: "I make decisions on the spur of the moment.", scale: "present_hedonistic", reversed: false },
  { text: "I often follow my heart more than my head.", scale: "present_hedonistic", reversed: false },
  { text: "I find myself getting swept up in the excitement of the moment.", scale: "present_hedonistic", reversed: false },
  { text: "It is more important for me to enjoy life's journey than to focus only on the destination.", scale: "present_hedonistic", reversed: false },
  { text: "I believe it's important to enjoy yourself and not worry.", scale: "present_hedonistic", reversed: false },

  // Present-Fatalistic (9 items)
  { text: "Fate determines much in my life.", scale: "present_fatalistic", reversed: false },
  { text: "Since whatever will be will be, it doesn't really matter what I do.", scale: "present_fatalistic", reversed: false },
  { text: "You can't really plan for the future because things change so much.", scale: "present_fatalistic", reversed: false },
  { text: "My life path is controlled by forces I cannot influence.", scale: "present_fatalistic", reversed: false },
  { text: "It doesn't make sense to worry about the future, since there is nothing that I can do about it anyway.", scale: "present_fatalistic", reversed: false },
  { text: "Often luck pays off better than hard work.", scale: "present_fatalistic", reversed: false },
  { text: "I feel that it's not important to take 'tomorrow' too seriously since plans hardly ever work out anyway.", scale: "present_fatalistic", reversed: false },
  { text: "Things don't change much regardless of what I do.", scale: "present_fatalistic", reversed: false },
  { text: "If things don't get done on time, I don't worry about it.", scale: "present_fatalistic", reversed: false },

  // Future (13 items)
  { text: "When I want to achieve something, I set goals and consider specific means for reaching those goals.", scale: "future", reversed: false },
  { text: "Meeting tomorrow's deadlines and doing other necessary work comes before tonight's play.", scale: "future", reversed: false },
  { text: "It upsets me to be late for appointments.", scale: "future", reversed: false },
  { text: "I complete projects on time by making steady progress.", scale: "future", reversed: false },
  { text: "I am able to resist temptations when I know that there is work to be done.", scale: "future", reversed: false },
  { text: "I keep working at difficult, uninteresting tasks if they will help me get ahead.", scale: "future", reversed: false },
  { text: "I believe that a person's day should be planned ahead each morning.", scale: "future", reversed: false },
  { text: "Before making a decision, I weigh the costs against the benefits.", scale: "future", reversed: false },
  { text: "I make lists of things to do.", scale: "future", reversed: false },
  { text: "I believe that it is important to save for a rainy day.", scale: "future", reversed: false },
  { text: "I consider how things might turn out before making decisions.", scale: "future", reversed: false },
  { text: "I believe in planning for the future.", scale: "future", reversed: false },
  { text: "I often think about what my life will be like in the future.", scale: "future", reversed: false },
];

const ztpi: Instrument = {
  id: "ztpi",
  name: "Zimbardo Time Perspective Inventory",
  shortName: "ZTPI",
  description:
    "Measures five dimensions of how people relate to time: Past-Negative (regret/rumination), Past-Positive (nostalgia/warmth), Present-Hedonistic (pleasure-seeking/spontaneity), Present-Fatalistic (helplessness/resignation), and Future (planning/goal-orientation).",
  citation:
    "Zimbardo, P. G., & Boyd, J. N. (1999). Putting time in perspective: A valid, reliable individual-differences metric. Journal of Personality and Social Psychology, 77, 1271-1288.",
  itemCount: 56,
  estimatedMinutes: 10,
  scales: [
    { id: "past_negative", name: "Past-Negative", description: "Negative, aversive view of the past; trauma and regret" },
    { id: "past_positive", name: "Past-Positive", description: "Warm, sentimental attitude toward the past; nostalgia" },
    { id: "present_hedonistic", name: "Present-Hedonistic", description: "Pleasure-oriented, risk-taking, living in the moment" },
    { id: "present_fatalistic", name: "Present-Fatalistic", description: "Helpless, fatalistic attitude; belief that fate controls life" },
    { id: "future", name: "Future", description: "Goal-oriented, planning, delayed gratification" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `ztpi-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 5,
      labels: [
        "Very Uncharacteristic",
        "Uncharacteristic",
        "Neutral",
        "Characteristic",
        "Very Characteristic",
      ],
    },
    scaleId: item.scale,
    reversed: item.reversed,
  })),
};

registerInstrument(ztpi, scoreLikert);

export default ztpi;
