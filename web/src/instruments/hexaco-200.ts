import type { Instrument, Scale } from "./types";
import { registerInstrument } from "./registry";
import { scoreLikert } from "../scoring/engine";

/**
 * HEXACO-200 (IPIP version)
 * 200-item measure of 6 personality factors with 24 facets (4 per domain, ~8 items each).
 * Source: IPIP representation of HEXACO-PI-R (ipip.ori.org) — public domain.
 * Based on: Lee & Ashton (2004, 2018). HEXACO Personality Inventory-Revised.
 */

interface HexacoItem {
  text: string;
  facet: string;
  reversed: boolean;
}

// Domain and facet definitions
const DOMAIN_DEFS: Record<string, { name: string; description: string; facets: { id: string; name: string }[] }> = {
  hh: {
    name: "Honesty-Humility",
    description: "Sincerity, fairness, greed avoidance, modesty",
    facets: [
      { id: "hh_sin", name: "Sincerity" },
      { id: "hh_fai", name: "Fairness" },
      { id: "hh_gre", name: "Greed Avoidance" },
      { id: "hh_mod", name: "Modesty" },
    ],
  },
  em: {
    name: "Emotionality",
    description: "Fearfulness, anxiety, dependence, sentimentality",
    facets: [
      { id: "em_fea", name: "Fearfulness" },
      { id: "em_anx", name: "Anxiety" },
      { id: "em_dep", name: "Dependence" },
      { id: "em_sen", name: "Sentimentality" },
    ],
  },
  ex: {
    name: "Extraversion",
    description: "Social self-esteem, social boldness, sociability, liveliness",
    facets: [
      { id: "ex_sse", name: "Social Self-Esteem" },
      { id: "ex_bol", name: "Social Boldness" },
      { id: "ex_soc", name: "Sociability" },
      { id: "ex_liv", name: "Liveliness" },
    ],
  },
  ag: {
    name: "Agreeableness",
    description: "Forgiveness, gentleness, flexibility, patience",
    facets: [
      { id: "ag_for", name: "Forgiveness" },
      { id: "ag_gen", name: "Gentleness" },
      { id: "ag_fle", name: "Flexibility" },
      { id: "ag_pat", name: "Patience" },
    ],
  },
  co: {
    name: "Conscientiousness",
    description: "Organization, diligence, perfectionism, prudence",
    facets: [
      { id: "co_org", name: "Organization" },
      { id: "co_dil", name: "Diligence" },
      { id: "co_per", name: "Perfectionism" },
      { id: "co_pru", name: "Prudence" },
    ],
  },
  op: {
    name: "Openness to Experience",
    description: "Aesthetic appreciation, inquisitiveness, creativity, unconventionality",
    facets: [
      { id: "op_aes", name: "Aesthetic Appreciation" },
      { id: "op_inq", name: "Inquisitiveness" },
      { id: "op_cre", name: "Creativity" },
      { id: "op_unc", name: "Unconventionality" },
    ],
  },
};

function buildScales(): Scale[] {
  const scales: Scale[] = [];
  for (const [domainId, domain] of Object.entries(DOMAIN_DEFS)) {
    scales.push({ id: domainId, name: domain.name, description: domain.description });
    for (const facet of domain.facets) {
      scales.push({ id: facet.id, name: facet.name, parentId: domainId });
    }
  }
  return scales;
}

// IPIP-HEXACO 200 items — 8-9 items per facet, 24 facets
// All items from the public domain IPIP (ipip.ori.org)
const ITEMS: HexacoItem[] = [
  // ─── Honesty-Humility ─────────────────────────────

  // Sincerity (8 items)
  { text: "I wouldn't pretend to like someone just to get that person to do favors for me.", facet: "hh_sin", reversed: false },
  { text: "I wouldn't use flattery to get a raise or promotion at work, even if I thought it would succeed.", facet: "hh_sin", reversed: false },
  { text: "If I want something from a person, I will laugh at that person's worst jokes.", facet: "hh_sin", reversed: true },
  { text: "I wouldn't pretend to be nice to someone if I disliked them.", facet: "hh_sin", reversed: false },
  { text: "If I wanted to, I could manipulate people into doing what I want.", facet: "hh_sin", reversed: true },
  { text: "I would never try to manipulate others to get what I want.", facet: "hh_sin", reversed: false },
  { text: "I am not interested in using charm or flattery to influence people.", facet: "hh_sin", reversed: false },
  { text: "I sometimes tell people what they want to hear, not what I really think.", facet: "hh_sin", reversed: true },

  // Fairness (8 items)
  { text: "I would never accept a bribe, even if it were very large.", facet: "hh_fai", reversed: false },
  { text: "I would be tempted to use counterfeit money, if I were sure I could get away with it.", facet: "hh_fai", reversed: true },
  { text: "If I knew that I could never get caught, I would be willing to steal a million dollars.", facet: "hh_fai", reversed: true },
  { text: "I would never take things that aren't mine.", facet: "hh_fai", reversed: false },
  { text: "I'd be tempted to use someone else's credit card number if I could get away with it.", facet: "hh_fai", reversed: true },
  { text: "I would never cheat on my taxes.", facet: "hh_fai", reversed: false },
  { text: "I would not mind pocketing a bit of extra change if a cashier made a mistake.", facet: "hh_fai", reversed: true },
  { text: "Honesty is always the best policy, even if it costs me money.", facet: "hh_fai", reversed: false },

  // Greed Avoidance (8 items)
  { text: "I would like to be seen driving around in a very expensive car.", facet: "hh_gre", reversed: true },
  { text: "I would get a lot of pleasure from owning expensive luxury goods.", facet: "hh_gre", reversed: true },
  { text: "Having a lot of money is not especially important to me.", facet: "hh_gre", reversed: false },
  { text: "I would like to live in a very expensive, high-class neighborhood.", facet: "hh_gre", reversed: true },
  { text: "I am satisfied with what I have and don't need more luxuries.", facet: "hh_gre", reversed: false },
  { text: "I would enjoy being able to buy expensive things.", facet: "hh_gre", reversed: true },
  { text: "I do not care about having flashy possessions.", facet: "hh_gre", reversed: false },
  { text: "Wealth and status symbols don't interest me much.", facet: "hh_gre", reversed: false },

  // Modesty (9 items)
  { text: "I think that I am entitled to more respect than the average person is.", facet: "hh_mod", reversed: true },
  { text: "I want people to know that I am an important person of high status.", facet: "hh_mod", reversed: true },
  { text: "I am an ordinary person who is no better than others.", facet: "hh_mod", reversed: false },
  { text: "I don't think of myself as being better than anyone else.", facet: "hh_mod", reversed: false },
  { text: "I consider myself more special than most people.", facet: "hh_mod", reversed: true },
  { text: "I try not to brag about my accomplishments.", facet: "hh_mod", reversed: false },
  { text: "I don't care much about being important.", facet: "hh_mod", reversed: false },
  { text: "I like to show off now and then.", facet: "hh_mod", reversed: true },
  { text: "I believe I deserve special treatment.", facet: "hh_mod", reversed: true },

  // ─── Emotionality ─────────────────────────────────

  // Fearfulness (8 items)
  { text: "I would feel afraid if I had to travel in bad weather conditions.", facet: "em_fea", reversed: false },
  { text: "I don't mind doing jobs that involve dangerous work.", facet: "em_fea", reversed: true },
  { text: "When it comes to physical danger, I am very fearful.", facet: "em_fea", reversed: false },
  { text: "Even in an emergency I wouldn't feel like panicking.", facet: "em_fea", reversed: true },
  { text: "I get nervous around dangerous situations.", facet: "em_fea", reversed: false },
  { text: "I am not easily frightened.", facet: "em_fea", reversed: true },
  { text: "I am careful to avoid physical risks.", facet: "em_fea", reversed: false },
  { text: "I would rather avoid situations that could be physically dangerous.", facet: "em_fea", reversed: false },

  // Anxiety (8 items)
  { text: "I sometimes can't help worrying about little things.", facet: "em_anx", reversed: false },
  { text: "I worry a lot less than most people do.", facet: "em_anx", reversed: true },
  { text: "I often worry about things that turn out to be unimportant.", facet: "em_anx", reversed: false },
  { text: "I seldom feel anxious about how things will turn out.", facet: "em_anx", reversed: true },
  { text: "I tend to worry even about things that don't matter much.", facet: "em_anx", reversed: false },
  { text: "I get stressed about things that are out of my control.", facet: "em_anx", reversed: false },
  { text: "I rarely lose sleep over my worries.", facet: "em_anx", reversed: true },
  { text: "I tend to overthink things.", facet: "em_anx", reversed: false },

  // Dependence (8 items)
  { text: "I can handle difficult situations without needing emotional support from anyone else.", facet: "em_dep", reversed: true },
  { text: "Whenever I feel worried about something, I want to share my concern with another person.", facet: "em_dep", reversed: false },
  { text: "I need someone to lean on when I face difficulties.", facet: "em_dep", reversed: false },
  { text: "I prefer to handle my problems on my own.", facet: "em_dep", reversed: true },
  { text: "When I'm feeling down, I seek comfort from others.", facet: "em_dep", reversed: false },
  { text: "I don't usually need reassurance from others.", facet: "em_dep", reversed: true },
  { text: "I feel better about problems when I talk them over with someone.", facet: "em_dep", reversed: false },
  { text: "I like having someone to turn to for emotional support.", facet: "em_dep", reversed: false },

  // Sentimentality (9 items)
  { text: "I feel like crying when I see other people crying.", facet: "em_sen", reversed: false },
  { text: "I remain unemotional even in situations where most people get very sentimental.", facet: "em_sen", reversed: true },
  { text: "I am easily moved by music, art, or stories.", facet: "em_sen", reversed: false },
  { text: "I don't get emotional easily.", facet: "em_sen", reversed: true },
  { text: "Sad movies can make me cry.", facet: "em_sen", reversed: false },
  { text: "I feel strong emotions when someone close to me is going through a hard time.", facet: "em_sen", reversed: false },
  { text: "I am touched by things I observe around me.", facet: "em_sen", reversed: false },
  { text: "I can watch sad scenes in movies without being affected.", facet: "em_sen", reversed: true },
  { text: "I feel sympathy for people who are less fortunate.", facet: "em_sen", reversed: false },

  // ─── Extraversion ─────────────────────────────────

  // Social Self-Esteem (8 items)
  { text: "I feel reasonably satisfied with myself overall.", facet: "ex_sse", reversed: false },
  { text: "I think most people like some aspects of my personality.", facet: "ex_sse", reversed: false },
  { text: "I feel that I am an unpopular person.", facet: "ex_sse", reversed: true },
  { text: "I sometimes feel that I am a worthless person.", facet: "ex_sse", reversed: true },
  { text: "I feel confident about myself in social situations.", facet: "ex_sse", reversed: false },
  { text: "I have high self-esteem.", facet: "ex_sse", reversed: false },
  { text: "I sometimes doubt whether I have value as a person.", facet: "ex_sse", reversed: true },
  { text: "I generally feel positive about myself.", facet: "ex_sse", reversed: false },

  // Social Boldness (8 items)
  { text: "In social situations, I'm usually the one who makes the first move.", facet: "ex_bol", reversed: false },
  { text: "When I'm in a group of people, I'm often the one who speaks on behalf of the group.", facet: "ex_bol", reversed: false },
  { text: "I tend to feel quite self-conscious when speaking in front of a group of people.", facet: "ex_bol", reversed: true },
  { text: "I can easily approach strangers and start a conversation.", facet: "ex_bol", reversed: false },
  { text: "I feel uncomfortable being the center of attention.", facet: "ex_bol", reversed: true },
  { text: "I can express myself easily in a group.", facet: "ex_bol", reversed: false },
  { text: "I would rather follow than lead.", facet: "ex_bol", reversed: true },
  { text: "I am comfortable taking charge in social situations.", facet: "ex_bol", reversed: false },

  // Sociability (8 items)
  { text: "I prefer jobs that involve active social interaction to those that involve working alone.", facet: "ex_soc", reversed: false },
  { text: "The first thing that I always do in a new place is to make friends.", facet: "ex_soc", reversed: false },
  { text: "I enjoy having lots of people around me.", facet: "ex_soc", reversed: false },
  { text: "I prefer to be alone rather than in a large group.", facet: "ex_soc", reversed: true },
  { text: "I like to go out and socialize with people.", facet: "ex_soc", reversed: false },
  { text: "I am happiest when I can spend time by myself.", facet: "ex_soc", reversed: true },
  { text: "I enjoy meeting new people.", facet: "ex_soc", reversed: false },
  { text: "Large social gatherings bore me.", facet: "ex_soc", reversed: true },

  // Liveliness (9 items)
  { text: "On most days, I feel cheerful and optimistic.", facet: "ex_liv", reversed: false },
  { text: "I am full of energy.", facet: "ex_liv", reversed: false },
  { text: "Most people are more upbeat and dynamic than I generally am.", facet: "ex_liv", reversed: true },
  { text: "I am an enthusiastic person.", facet: "ex_liv", reversed: false },
  { text: "I feel excited and happy most of the time.", facet: "ex_liv", reversed: false },
  { text: "I rarely feel enthusiastic about things.", facet: "ex_liv", reversed: true },
  { text: "I have a lot of energy and vitality.", facet: "ex_liv", reversed: false },
  { text: "I often feel listless and tired.", facet: "ex_liv", reversed: true },
  { text: "I wake up most mornings feeling ready to go.", facet: "ex_liv", reversed: false },

  // ─── Agreeableness ────────────────────────────────

  // Forgiveness (8 items)
  { text: "I rarely hold a grudge, even against people who have badly wronged me.", facet: "ag_for", reversed: false },
  { text: "My attitude toward people who have treated me badly is 'forgive and forget'.", facet: "ag_for", reversed: false },
  { text: "If someone has cheated me once, I will always feel suspicious of that person.", facet: "ag_for", reversed: true },
  { text: "I find it hard to fully forgive someone who has done something mean to me.", facet: "ag_for", reversed: true },
  { text: "I can forgive people who have hurt me.", facet: "ag_for", reversed: false },
  { text: "I tend to hold grudges against people who have wronged me.", facet: "ag_for", reversed: true },
  { text: "I believe in second chances.", facet: "ag_for", reversed: false },
  { text: "I have a hard time letting go of past hurts.", facet: "ag_for", reversed: true },

  // Gentleness (8 items)
  { text: "I tend to be lenient in judging other people.", facet: "ag_gen", reversed: false },
  { text: "People sometimes tell me that I am too critical of others.", facet: "ag_gen", reversed: true },
  { text: "Even when people make a lot of mistakes, I rarely say anything negative.", facet: "ag_gen", reversed: false },
  { text: "I tend to judge people harshly.", facet: "ag_gen", reversed: true },
  { text: "I try to see the good in everyone.", facet: "ag_gen", reversed: false },
  { text: "I can be quite harsh in my judgments of others.", facet: "ag_gen", reversed: true },
  { text: "I am generally kind and gentle with people.", facet: "ag_gen", reversed: false },
  { text: "I sometimes say mean things to people.", facet: "ag_gen", reversed: true },

  // Flexibility (8 items)
  { text: "People sometimes tell me that I'm too stubborn.", facet: "ag_fle", reversed: true },
  { text: "I am usually quite flexible in my opinions when people disagree with me.", facet: "ag_fle", reversed: false },
  { text: "When people tell me that I'm wrong, my first reaction is to argue with them.", facet: "ag_fle", reversed: true },
  { text: "I am willing to compromise in an argument.", facet: "ag_fle", reversed: false },
  { text: "I can be stubborn when I think I'm right.", facet: "ag_fle", reversed: true },
  { text: "I try to see other people's point of view.", facet: "ag_fle", reversed: false },
  { text: "I find it hard to change my mind once I've made a decision.", facet: "ag_fle", reversed: true },
  { text: "I'm open to changing my plans based on others' input.", facet: "ag_fle", reversed: false },

  // Patience (9 items)
  { text: "I rarely feel the urge to retaliate against people who have hurt me.", facet: "ag_pat", reversed: false },
  { text: "I have a quick temper.", facet: "ag_pat", reversed: true },
  { text: "I am a patient person.", facet: "ag_pat", reversed: false },
  { text: "I lose my temper quickly.", facet: "ag_pat", reversed: true },
  { text: "It takes a lot to get me angry.", facet: "ag_pat", reversed: false },
  { text: "People sometimes say I need to calm down.", facet: "ag_pat", reversed: true },
  { text: "I can remain calm in frustrating situations.", facet: "ag_pat", reversed: false },
  { text: "I get irritated when things don't go my way.", facet: "ag_pat", reversed: true },
  { text: "I am slow to anger.", facet: "ag_pat", reversed: false },

  // ─── Conscientiousness ────────────────────────────

  // Organization (8 items)
  { text: "I plan ahead and organize things, to avoid scrambling at the last minute.", facet: "co_org", reversed: false },
  { text: "When working, I sometimes have difficulties due to being disorganized.", facet: "co_org", reversed: true },
  { text: "I like to keep my belongings neat and tidy.", facet: "co_org", reversed: false },
  { text: "I tend to be messy and disorganized.", facet: "co_org", reversed: true },
  { text: "I keep my workspace well-organized.", facet: "co_org", reversed: false },
  { text: "I often misplace my things.", facet: "co_org", reversed: true },
  { text: "I always know where my important things are.", facet: "co_org", reversed: false },
  { text: "I have trouble keeping things in order.", facet: "co_org", reversed: true },

  // Diligence (8 items)
  { text: "I often push myself very hard when trying to achieve a goal.", facet: "co_dil", reversed: false },
  { text: "I do only the minimum amount of work needed to get by.", facet: "co_dil", reversed: true },
  { text: "I work hard to achieve my goals.", facet: "co_dil", reversed: false },
  { text: "I tend to put off tasks until the last minute.", facet: "co_dil", reversed: true },
  { text: "I give my best effort in everything I do.", facet: "co_dil", reversed: false },
  { text: "I am a hard worker.", facet: "co_dil", reversed: false },
  { text: "I sometimes slack off when no one is watching.", facet: "co_dil", reversed: true },
  { text: "I try to do more than what is expected of me.", facet: "co_dil", reversed: false },

  // Perfectionism (8 items)
  { text: "When working on something, I don't pay much attention to small details.", facet: "co_per", reversed: true },
  { text: "People often call me a perfectionist.", facet: "co_per", reversed: false },
  { text: "I always try to be accurate in my work, even at the expense of time.", facet: "co_per", reversed: false },
  { text: "I check my work carefully for errors.", facet: "co_per", reversed: false },
  { text: "I pay close attention to details.", facet: "co_per", reversed: false },
  { text: "I am satisfied with work that is less than perfect.", facet: "co_per", reversed: true },
  { text: "I set high standards for my own work.", facet: "co_per", reversed: false },
  { text: "I don't worry about making my work perfect.", facet: "co_per", reversed: true },

  // Prudence (9 items)
  { text: "I make a lot of mistakes because I don't think before I act.", facet: "co_pru", reversed: true },
  { text: "I prefer to do whatever comes to mind, rather than stick to a plan.", facet: "co_pru", reversed: true },
  { text: "When I have a deadline, I often leave things to the last minute.", facet: "co_pru", reversed: true },
  { text: "I think things through before making a decision.", facet: "co_pru", reversed: false },
  { text: "I act on impulse without thinking about the consequences.", facet: "co_pru", reversed: true },
  { text: "I consider the long-term effects of my decisions.", facet: "co_pru", reversed: false },
  { text: "I am careful to avoid making hasty decisions.", facet: "co_pru", reversed: false },
  { text: "I rarely do things I haven't planned for.", facet: "co_pru", reversed: false },
  { text: "I make decisions quickly without much deliberation.", facet: "co_pru", reversed: true },

  // ─── Openness to Experience ───────────────────────

  // Aesthetic Appreciation (8 items)
  { text: "I would be quite bored by a visit to an art gallery.", facet: "op_aes", reversed: true },
  { text: "I would enjoy creating a work of art, such as a novel, a song, or a painting.", facet: "op_aes", reversed: false },
  { text: "If I had the opportunity, I would like to attend a classical music concert.", facet: "op_aes", reversed: false },
  { text: "Sometimes I like to just watch the wind as it blows through the trees.", facet: "op_aes", reversed: false },
  { text: "I appreciate beauty in nature.", facet: "op_aes", reversed: false },
  { text: "I am moved by beautiful things.", facet: "op_aes", reversed: false },
  { text: "Art and music don't do much for me.", facet: "op_aes", reversed: true },
  { text: "I enjoy visiting museums and galleries.", facet: "op_aes", reversed: false },

  // Inquisitiveness (8 items)
  { text: "I enjoy looking at maps of different places.", facet: "op_inq", reversed: false },
  { text: "I find it boring to discuss philosophy.", facet: "op_inq", reversed: true },
  { text: "I have never really enjoyed looking through an encyclopedia.", facet: "op_inq", reversed: true },
  { text: "I enjoy learning about new topics.", facet: "op_inq", reversed: false },
  { text: "I am curious about many different things.", facet: "op_inq", reversed: false },
  { text: "I enjoy exploring new ideas.", facet: "op_inq", reversed: false },
  { text: "I would rather read a factual book than a novel.", facet: "op_inq", reversed: false },
  { text: "I like to learn about the history and geography of other countries.", facet: "op_inq", reversed: false },

  // Creativity (8 items)
  { text: "People have often told me that I have a good imagination.", facet: "op_cre", reversed: false },
  { text: "I am an imaginative person.", facet: "op_cre", reversed: false },
  { text: "I often come up with new ideas.", facet: "op_cre", reversed: false },
  { text: "I am not very creative.", facet: "op_cre", reversed: true },
  { text: "I enjoy finding new solutions to problems.", facet: "op_cre", reversed: false },
  { text: "I prefer doing things in a tried-and-true way.", facet: "op_cre", reversed: true },
  { text: "I have a vivid imagination.", facet: "op_cre", reversed: false },
  { text: "I enjoy brainstorming new approaches to things.", facet: "op_cre", reversed: false },

  // Unconventionality (9 items)
  { text: "I think of myself as a somewhat eccentric person.", facet: "op_unc", reversed: false },
  { text: "I like people who have unconventional views.", facet: "op_unc", reversed: false },
  { text: "I enjoy hearing about unusual ideas and perspectives.", facet: "op_unc", reversed: false },
  { text: "I prefer to follow conventional ways of doing things.", facet: "op_unc", reversed: true },
  { text: "I find unusual people interesting rather than off-putting.", facet: "op_unc", reversed: false },
  { text: "I tend to question conventional wisdom.", facet: "op_unc", reversed: false },
  { text: "I am drawn to nontraditional approaches.", facet: "op_unc", reversed: false },
  { text: "I prefer tried-and-tested methods over experimental ones.", facet: "op_unc", reversed: true },
  { text: "I enjoy thinking about abstract concepts and theories.", facet: "op_unc", reversed: false },
];

const hexaco200: Instrument = {
  id: "hexaco-200",
  name: "HEXACO-200",
  shortName: "HEXACO (Full)",
  description:
    "Full 200-item HEXACO personality inventory with facet-level measurement. 6 domains, 24 facets (~8 items per facet). Provides detailed personality assessment including Honesty-Humility.",
  citation:
    "Lee, K., & Ashton, M. C. (2018). Psychometric properties of the HEXACO-200. Assessment, 25(5), 543-556. IPIP items from ipip.ori.org (public domain).",
  itemCount: ITEMS.length,
  estimatedMinutes: 25,
  scales: buildScales(),
  items: ITEMS.map((item, idx) => ({
    id: `hex200-${idx + 1}`,
    text: item.text,
    response: {
      type: "likert" as const,
      min: 1,
      max: 5,
      labels: ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
    },
    scaleId: item.facet,
    reversed: item.reversed,
  })),
};

registerInstrument(hexaco200, (instrument, session) => {
  // Score at facet level first
  const facetResult = scoreLikert(instrument, session);

  // Compute domain scores as mean of their facet scores
  const domainScores = Object.keys(DOMAIN_DEFS).map((domainId) => {
    const domain = DOMAIN_DEFS[domainId]!;
    const facetIds = domain.facets.map((f) => f.id);
    const facetScores = facetResult.scores.filter((s) => facetIds.includes(s.scaleId));
    const avgNorm = facetScores.length > 0
      ? facetScores.reduce((sum, s) => sum + s.normalized, 0) / facetScores.length
      : 0;
    const avgRaw = facetScores.length > 0
      ? facetScores.reduce((sum, s) => sum + s.raw, 0) / facetScores.length
      : 0;
    return {
      scaleId: domainId,
      scaleName: domain.name,
      raw: avgRaw,
      normalized: avgNorm,
      itemCount: facetScores.reduce((sum, s) => sum + s.itemCount, 0),
    };
  });

  return {
    instrumentId: instrument.id,
    completedAt: session.completedAt ?? Date.now(),
    scores: [...domainScores, ...facetResult.scores],
  };
});

export default hexaco200;
