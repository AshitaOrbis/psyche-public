import type { Instrument } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * Authenticity Scale
 * 12-item measure of dispositional authenticity.
 * Source: Wood, Linley, Maltby, Baliousis, & Joseph (2008).
 *
 * Three subscales (4 items each):
 * - Authentic Living: behaving in accordance with one's true self
 * - Self-Alienation: feeling disconnected from one's true self
 * - Accepting External Influence: conforming to others' expectations
 *
 * All items forward-scored within their subscale.
 * Self-Alienation and External Influence are "negative" subscales
 * (high = less authentic), handled in the analysis pipeline.
 */

interface AuthItem {
  text: string;
  scale: "authentic_living" | "self_alienation" | "external_influence";
}

const ITEMS: AuthItem[] = [
  // Authentic Living (4 items)
  { text: "I think it is better to be yourself, than to be popular.", scale: "authentic_living" },
  { text: "I don't know how I really feel inside.", scale: "self_alienation" },
  { text: "I am strongly influenced by the opinions of others.", scale: "external_influence" },
  { text: "I usually do what other people tell me to do.", scale: "external_influence" },
  { text: "I always feel I need to do what others expect me to do.", scale: "external_influence" },
  { text: "Other people influence me greatly.", scale: "external_influence" },
  { text: "I feel as if I don't know myself very well.", scale: "self_alienation" },
  { text: "I always stand by what I believe in.", scale: "authentic_living" },
  { text: "I am true to myself in most situations.", scale: "authentic_living" },
  { text: "I feel out of touch with the 'real me'.", scale: "self_alienation" },
  { text: "I live in accordance with my values and beliefs.", scale: "authentic_living" },
  { text: "I feel alienated from myself.", scale: "self_alienation" },
];

const authenticity: Instrument = {
  id: "authenticity",
  name: "Authenticity Scale",
  shortName: "Authenticity",
  description:
    "Measures three dimensions of authenticity: Authentic Living (behaving true to self), Self-Alienation (disconnection from true self), and Accepting External Influence (conforming to others' expectations).",
  citation:
    "Wood, A. M., Linley, P. A., Maltby, J., Baliousis, M., & Joseph, S. (2008). The authentic personality: A theoretical and empirical conceptualization and the development of the Authenticity Scale. Journal of Counseling Psychology, 55, 385-399.",
  itemCount: 12,
  estimatedMinutes: 2,
  scales: [
    { id: "authentic_living", name: "Authentic Living", description: "Behaving in accordance with one's true self" },
    { id: "self_alienation", name: "Self-Alienation", description: "Subjective feeling of not knowing or being disconnected from oneself" },
    { id: "external_influence", name: "Accepting External Influence", description: "Tendency to conform to others' expectations rather than one's own" },
  ],
  items: ITEMS.map((item, idx) => ({
    id: `auth-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 7,
      labels: [
        "Does Not Describe Me at All",
        "Does Not Describe Me",
        "Slightly Does Not Describe Me",
        "Neutral",
        "Slightly Describes Me",
        "Describes Me",
        "Describes Me Very Well",
      ],
    },
    scaleId: item.scale,
    reversed: false,
  })),
};

registerInstrument(authenticity, scoreLikert);

export default authenticity;
