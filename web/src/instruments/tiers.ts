/**
 * Tier configuration for the instrument battery.
 *
 * Tiers are additive: Standard includes Lite instruments (with replacements),
 * Heavy includes Standard instruments (with replacements).
 *
 * The `replaces` map handles instruments superseded by a strictly better version.
 * Heavy adds NEO-120 alongside NEO-300 (not replacing it) for cross-instrument comparison.
 */

import type { Tier } from "./types";

interface TierDef {
  /** Instruments added at this tier level */
  instruments: string[];
  /** Instruments replaced by better versions: old -> new */
  replaces: Record<string, string>;
}

const TIER_DEFS: Record<Tier, TierDef> = {
  lite: {
    instruments: [
      "ipip-neo-60",
      "crt-7",
      "ncs-18",
      "rosenberg",
      "sd3",
      "phq8-gad7",
      "ecr-r",
      "erq-10",
      "iri-28",
      "self-monitoring-18",
      "loc-ie4",
      "grit-s",
      "riasec-48",
      "bpns-9",
      "open-ended",
    ],
    replaces: {},
  },
  standard: {
    instruments: [
      "ipip-neo-300",
      "hexaco-60",
      "swls",
      "aaq-ii",
      "dweck-itis",
      "cei-ii",
    ],
    replaces: {
      "ipip-neo-60": "ipip-neo-300",
    },
  },
  heavy: {
    // CAT instruments (cat-big5, cat-hexaco) are included here but require
    // validated IRT item banks before use. The adaptive runner HARD-BLOCKS
    // administration when the bank fails validation (placeholder item text,
    // invalid GRM parameters) — the shipped synthetic banks will not run.
    // See cat-controller.ts validateCATBankOrThrow() and BACKLOG.md #CAT.
    instruments: [
      "phq9-gad7",
      "ipip-neo-120",
      "hexaco-200",
      "grit-o",
      "bpns-21",
      "levenson-ipc-24",
      "snyder-sm-25",
      "cat-big5",
      "cat-hexaco",
      "aot-13",
      "ius-12",
      "scs-26",
      "mfq-2",
      "frost-mps",
      "maas",
      "authenticity",
      "tangney-scs",
      "maximization",
      "ztpi",
    ],
    replaces: {
      "hexaco-60": "hexaco-200",
      "grit-s": "grit-o",
      "bpns-9": "bpns-21",
      "loc-ie4": "levenson-ipc-24",
      "self-monitoring-18": "snyder-sm-25",
      // The public site administers PHQ-8; the private research battery keeps the
      // full PHQ-9 (owner ruling q-psyche-phq9-drop = A, 2026-08-11). This swap is
      // the ONLY place that split lives — see the mirror note in phq8-gad7.ts. Do
      // not "fix" it by editing the instrument in one tree; the sync would revert it.
      "phq8-gad7": "phq9-gad7",
    },
  },
};

/** Ordered list of tiers from lowest to highest */
const TIER_ORDER: Tier[] = ["lite", "standard", "heavy"];

/**
 * Get the list of instrument IDs for a given tier.
 *
 * Accumulates instruments from lite through the target tier,
 * applying replacement rules at each level.
 */
export function getInstrumentsForTier(tier: Tier): string[] {
  const instruments = new Set<string>();
  const targetIdx = TIER_ORDER.indexOf(tier);

  for (let i = 0; i <= targetIdx; i++) {
    const def = TIER_DEFS[TIER_ORDER[i]!]!;

    // Apply replacements: remove old instruments
    for (const oldId of Object.keys(def.replaces)) {
      instruments.delete(oldId);
    }

    // Add new instruments
    for (const id of def.instruments) {
      instruments.add(id);
    }
  }

  return Array.from(instruments);
}

/** Estimated item counts and times per tier */
export const TIER_META: Record<Tier, { label: string; estimatedItems: string; estimatedTime: string }> = {
  lite: { label: "Lite", estimatedItems: "~260 items", estimatedTime: "~35 min" },
  standard: { label: "Standard", estimatedItems: "~590 items", estimatedTime: "~80 min" },
  heavy: { label: "Heavy", estimatedItems: "~1,130+ items", estimatedTime: "~160 min" },
};

/** Instrument category groupings for display */
export const INSTRUMENT_CATEGORIES: { name: string; instrumentIds: string[] }[] = [
  { name: "Personality", instrumentIds: ["ipip-neo-60", "ipip-neo-120", "ipip-neo-300", "hexaco-60", "hexaco-200", "cat-big5", "cat-hexaco"] },
  { name: "Cognitive", instrumentIds: ["crt-7", "ncs-18", "aot-13", "dweck-itis"] },
  { name: "Wellbeing", instrumentIds: ["phq8-gad7", "phq9-gad7", "rosenberg", "swls", "scs-26", "maas"] },
  { name: "Interpersonal", instrumentIds: ["ecr-r", "iri-28", "self-monitoring-18", "snyder-sm-25", "authenticity"] },
  { name: "Self-Regulation", instrumentIds: ["erq-10", "tangney-scs", "aaq-ii", "frost-mps"] },
  { name: "Motivation", instrumentIds: ["grit-s", "grit-o", "bpns-9", "bpns-21", "loc-ie4", "levenson-ipc-24", "riasec-48", "cei-ii"] },
  { name: "Values & Morals", instrumentIds: ["sd3", "mfq-2"] },
  { name: "Decision Style", instrumentIds: ["maximization", "ius-12", "ztpi"] },
  { name: "Qualitative", instrumentIds: ["open-ended"] },
];
