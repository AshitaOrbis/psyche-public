import type {
  Instrument,
  InstrumentSession,
  InstrumentResult,
  ScaleScore,
  Item,
  ItemResponse,
} from "../instruments/types";
import type { CATSession } from "./cat-controller";
import { catSessionToScores } from "./cat-controller";
import { getInstrument } from "../instruments/registry";

/**
 * Build a response map and group scored values by scale.
 * Shared between scoreBinary and scoreLikert.
 */
function groupResponsesByScale(
  instrument: Instrument,
  session: InstrumentSession,
  reverser: (value: number, item: Item) => number,
): Map<string, { item: Item; value: number }[]> {
  const responseMap = new Map<string, ItemResponse>();
  for (const r of session.responses) {
    responseMap.set(r.itemId, r);
  }

  const scaleItems = new Map<string, { item: Item; value: number }[]>();
  for (const item of instrument.items) {
    const resp = responseMap.get(item.id);
    if (!resp || typeof resp.value !== "number") continue;

    const value = item.reversed ? reverser(resp.value, item) : resp.value;
    const existing = scaleItems.get(item.scaleId) ?? [];
    existing.push({ item, value });
    scaleItems.set(item.scaleId, existing);
  }

  return scaleItems;
}

/**
 * Aggregate grouped scale items into ScaleScore[].
 * Shared between scoreBinary and scoreLikert.
 */
function aggregateScales(
  instrument: Instrument,
  scaleItems: Map<string, { item: Item; value: number }[]>,
  normalizer: (raw: number, scaleId: string, firstItem: Item | undefined) => number,
): ScaleScore[] {
  const scores: ScaleScore[] = [];
  for (const scale of instrument.scales) {
    const items = scaleItems.get(scale.id);
    if (!items || items.length === 0) continue;

    const raw = items.reduce((sum, i) => sum + i.value, 0) / items.length;
    const normalized = normalizer(raw, scale.id, items[0]?.item);

    scores.push({
      scaleId: scale.id,
      scaleName: scale.name,
      raw,
      normalized,
      itemCount: items.length,
    });
  }
  return scores;
}

/**
 * Generic binary (True/False) scoring engine.
 * True = 1, False = 0; reverse scoring supported.
 */
export function scoreBinary(
  instrument: Instrument,
  session: InstrumentSession
): InstrumentResult {
  const scaleItems = groupResponsesByScale(
    instrument, session,
    (value) => 1 - value,
  );

  const scores = aggregateScales(
    instrument, scaleItems,
    (raw) => Math.max(0, Math.min(100, raw * 100)), // 0-1 → 0-100, clamped
  );

  return {
    instrumentId: instrument.id,
    completedAt: session.completedAt ?? Date.now(),
    scores,
  };
}

/**
 * Generic Likert scoring engine.
 * Handles reverse scoring, scale aggregation, and normalization.
 */
export function scoreLikert(
  instrument: Instrument,
  session: InstrumentSession
): InstrumentResult {
  const scaleItems = groupResponsesByScale(
    instrument, session,
    (value, item) => {
      if (item.response.type === "likert") {
        const { min, max } = item.response;
        return max + min - value;
      }
      return value;
    },
  );

  const scores = aggregateScales(
    instrument, scaleItems,
    (raw, _scaleId, firstItem) => {
      if (firstItem?.response.type === "likert") {
        const { min, max } = firstItem.response;
        if (max === min) return raw === min ? 0 : 100;
        return Math.max(0, Math.min(100, ((raw - min) / (max - min)) * 100));
      }
      return Math.max(0, Math.min(100, raw));
    },
  );

  return {
    instrumentId: instrument.id,
    completedAt: session.completedAt ?? Date.now(),
    scores,
  };
}

/**
 * Convert a completed CAT session into an InstrumentResult.
 * Theta estimates are converted to 0-100 percentile scores via normal CDF.
 *
 * Scale names and the facet -> parent-domain mapping are resolved from the
 * registered instrument definition (falling back to the optional scaleNames
 * map), so domain scores are aggregated from CAT facets rather than borrowed
 * from a different instrument.
 */
export function scoreAdaptive(
  instrumentId: string,
  catSession: CATSession,
  scaleNames?: Map<string, string>,
  fixedFormScores?: ScaleScore[],
): InstrumentResult {
  // Resolve scale metadata from the instrument registry when available
  const registered = getInstrument(instrumentId);
  const nameMap = new Map<string, string>(scaleNames ?? []);
  const facetParents = new Map<string, string>();
  if (registered) {
    for (const scale of registered.instrument.scales) {
      if (!nameMap.has(scale.id)) nameMap.set(scale.id, scale.name);
      if (scale.parentId) facetParents.set(scale.id, scale.parentId);
    }
  }

  const scores = catSessionToScores(
    catSession,
    fixedFormScores,
    facetParents.size > 0 ? facetParents : undefined,
  );
  for (const score of scores) {
    score.scaleName = nameMap.get(score.scaleId) ?? score.scaleName ?? score.scaleId;
  }
  return {
    instrumentId,
    completedAt: Date.now(),
    scores,
  };
}
