/** Tier levels for the instrument battery */
export type Tier = 'lite' | 'standard' | 'heavy';

/** Response format for an item */
export type ResponseFormat =
  | { type: "likert"; min: number; max: number; labels: string[] }
  | { type: "binary"; labels: [string, string] }
  | { type: "numeric" }
  | { type: "text"; minWords?: number }
  | { type: "multiple-choice"; options: string[] };

/** A single test item */
export interface Item {
  id: string;
  text: string;
  response: ResponseFormat;
  /** Scale/domain this item belongs to */
  scaleId: string;
  /** If true, score is reversed before aggregation */
  reversed?: boolean;
}

/** A measurement scale (e.g. a Big Five domain or facet) */
export interface Scale {
  id: string;
  name: string;
  description?: string;
  /** Parent scale ID for facets */
  parentId?: string;
}

/** Score interpretation tier */
export interface ScoreTier {
  min: number;
  max: number;
  label: string;
  description: string;
}

/** A complete instrument definition */
export interface Instrument {
  id: string;
  name: string;
  shortName: string;
  description: string;
  citation: string;
  itemCount: number;
  estimatedMinutes: number;
  scales: Scale[];
  items: Item[];
  /** Interpretation tiers per scale */
  interpretations?: Record<string, ScoreTier[]>;
  /** True for CAT-based adaptive instruments */
  adaptive?: boolean;
}

/** A single response to an item */
export interface ItemResponse {
  itemId: string;
  value: number | string;
  timestamp: number;
}

/** Completed session for an instrument */
export interface InstrumentSession {
  instrumentId: string;
  startedAt: number;
  completedAt?: number;
  responses: ItemResponse[];
}

/** Computed score for a scale */
export interface ScaleScore {
  scaleId: string;
  scaleName: string;
  raw: number;
  /** Normalized to 0-100 */
  normalized: number;
  /** Number of items that contributed */
  itemCount: number;
  /** Cronbach's alpha if computable */
  alpha?: number;
  /** IRT theta estimate (CAT only) */
  theta?: number;
  /** Standard error of theta (CAT only) */
  se?: number;
  /** Number of items administered (CAT only) */
  itemsAdministered?: number;
  /** True when score is based on fewer items than the minimum for reliable interpretation */
  incomplete?: boolean;
  /**
   * Score provenance. "cat" = estimated by adaptive testing,
   * "fixed-form" = carried over from a fixed-form instrument.
   * Absent for ordinary fixed-form instrument results.
   */
  source?: "cat" | "fixed-form";
}

/** Full results for an instrument */
export interface InstrumentResult {
  instrumentId: string;
  completedAt: number;
  scores: ScaleScore[];
}
