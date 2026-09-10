import type { Instrument, InstrumentSession, InstrumentResult } from "./types";

type ScoringFn = (
  instrument: Instrument,
  session: InstrumentSession
) => InstrumentResult;

interface RegisteredInstrument {
  instrument: Instrument;
  score: ScoringFn;
}

const registry = new Map<string, RegisteredInstrument>();

export function registerInstrument(
  instrument: Instrument,
  score: ScoringFn
): void {
  // Warn if any scale has items with differing response format ranges
  for (const scale of instrument.scales) {
    const scaleItems = instrument.items.filter((i) => i.scaleId === scale.id);
    if (scaleItems.length > 0 && scaleItems[0]?.response.type === "likert") {
      const first = scaleItems[0].response as { min: number; max: number };
      for (const item of scaleItems) {
        if (item.response.type === "likert") {
          const resp = item.response as { min: number; max: number };
          if (resp.min !== first.min || resp.max !== first.max) {
            console.warn(
              `[Psyche] Instrument "${instrument.id}" scale "${scale.id}" ` +
              `has items with differing min/max (${first.min}-${first.max} vs ${resp.min}-${resp.max}). ` +
              `Normalization assumes uniform ranges.`
            );
            break;
          }
        }
      }
    }
  }
  registry.set(instrument.id, { instrument, score });
}

export function getInstrument(id: string): RegisteredInstrument | undefined {
  return registry.get(id);
}

export function getAllInstruments(): RegisteredInstrument[] {
  return Array.from(registry.values());
}

export function getInstrumentIds(): string[] {
  return Array.from(registry.keys());
}

/** Check if an instrument is adaptive (CAT-based) */
export function isAdaptiveInstrument(id: string): boolean {
  const reg = registry.get(id);
  return reg?.instrument.adaptive === true;
}

/**
 * True if any registered instrument declares this scale.
 *
 * A CAT result legitimately carries scores forward from the fixed-form
 * instrument that seeded it, and those keep the SOURCE instrument's scale
 * IDs — cat-hexaco (HH, HH1…) carries hexaco-200 scales (hh, hh_sin…). So
 * import validation cannot demand that every scale on a result belong to the
 * result's own instrument; a carried-over scale must still be one the battery
 * actually defines, rather than an invented ID.
 */
export function isKnownScaleId(scaleId: string): boolean {
  for (const { instrument } of registry.values()) {
    for (const scale of instrument.scales) {
      if (scale.id === scaleId) return true;
    }
  }
  return false;
}
