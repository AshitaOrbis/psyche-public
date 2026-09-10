import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { StateStorage } from "zustand/middleware";
import type {
  Instrument,
  InstrumentSession,
  InstrumentResult,
  ItemResponse,
  ScaleScore,
  Item,
  Tier,
} from "../instruments/types";
import { getInstrument, isKnownScaleId } from "../instruments/registry";

interface PsycheState {
  /** Active sessions keyed by instrument ID */
  sessions: Record<string, InstrumentSession>;
  /** Computed results keyed by instrument ID */
  results: Record<string, InstrumentResult>;
  /** Current instrument being taken */
  activeInstrumentId: string | null;
  /** Current item index within the active instrument */
  currentItemIndex: number;
  /** Selected tier for the instrument battery */
  selectedTier: Tier;

  // Actions
  setTier: (tier: Tier) => void;
  startInstrument: (instrumentId: string) => void;
  recordResponse: (response: ItemResponse) => void;
  advanceItem: () => void;
  goBackItem: () => void;
  completeInstrument: (result: InstrumentResult) => void;
  setActiveInstrument: (id: string | null) => void;
  resetInstrument: (instrumentId: string) => void;
  exportData: () => string;
  importData: (json: string) => void;

  // ── Persistence health (psy-9) ──────────────────────────────
  /**
   * Set when a write to localStorage fails (typically QuotaExceededError).
   * Surfaced to the user — the page should prompt them to export their data.
   * Null when persistence is healthy. Cleared on the next successful write.
   */
  storageError: string | null;
  /** Approximate bytes the persisted store occupies in localStorage. */
  storageBytes: number;
  /** Dismiss the current storage error banner. */
  clearStorageError: () => void;
}

/** Storage key for the persisted store. Exported so UI can reference it. */
export const STORE_KEY = "psyche-store";

/** Maximum accepted length for free-text responses (chars). Enforced both on
 *  write (recordResponse) and on import (isValidResponseValue). */
export const MAX_TEXT_RESPONSE_LENGTH = 20000;

/** True if an error looks like a storage-quota failure across browsers. */
function isQuotaError(e: unknown): boolean {
  if (!(e instanceof DOMException)) return false;
  // Chrome/Safari throw name "QuotaExceededError"; Firefox legacy code 1014.
  return (
    e.name === "QuotaExceededError" ||
    e.name === "NS_ERROR_DOM_QUOTA_REACHED" ||
    e.code === 22 ||
    e.code === 1014
  );
}

/**
 * localStorage adapter that surfaces quota failures instead of swallowing
 * them, and records approximate byte usage on each write. SSR/no-storage
 * environments degrade to a no-op (getItem → null) so the app still loads.
 */
function createQuotaAwareStorage(): StateStorage {
  const ls = (): Storage | null => {
    try {
      return typeof window !== "undefined" ? window.localStorage : null;
    } catch {
      return null; // localStorage can throw in private-mode / blocked contexts
    }
  };

  // Re-entry guard: the health-field setState calls below would re-trigger a
  // persist write (→ setItem → setState → …). The guard reports health on the
  // outermost write only, breaking the recursion.
  let reporting = false;
  const report = (patch: Partial<PsycheState>) => {
    if (reporting) return;
    reporting = true;
    try {
      usePsycheStore.setState(patch as never);
    } finally {
      reporting = false;
    }
  };

  return {
    getItem: (name) => {
      const store = ls();
      return store ? store.getItem(name) : null;
    },
    setItem: (name, value) => {
      const store = ls();
      if (!store) return;
      try {
        store.setItem(name, value);
        // Success: clear any prior error and record approximate usage.
        report({ storageError: null, storageBytes: value.length });
      } catch (e) {
        const msg = isQuotaError(e)
          ? "Browser storage is full — export your data to avoid losing progress."
          : "Could not save to browser storage. Export your data as a backup.";
        // Non-silent: write the error into state so the UI can show it.
        // We do NOT re-throw — re-throwing here propagates out of zustand's
        // persist write as an uncaught error; surfacing via state is the
        // user-visible signal we want.
        report({ storageError: msg });
      }
    },
    removeItem: (name) => {
      const store = ls();
      if (store) store.removeItem(name);
    },
  };
}

export const usePsycheStore = create<PsycheState>()(
  persist(
    (set, get) => ({
      sessions: {},
      results: {},
      activeInstrumentId: null,
      currentItemIndex: 0,
      selectedTier: "standard",
      storageError: null,
      storageBytes: 0,

      clearStorageError: () => set(() => ({ storageError: null })),

      setTier: (tier) => set(() => ({ selectedTier: tier })),

      startInstrument: (instrumentId) =>
        set((state) => ({
          activeInstrumentId: instrumentId,
          currentItemIndex: 0,
          sessions: {
            ...state.sessions,
            [instrumentId]: state.sessions[instrumentId] ?? {
              instrumentId,
              startedAt: Date.now(),
              responses: [],
            },
          },
        })),

      recordResponse: (response) =>
        set((state) => {
          const id = state.activeInstrumentId;
          if (!id) return state;
          const session = state.sessions[id];
          if (!session) return state;

          // Cap open-ended (text) responses on write so a single very long
          // answer can't blow the localStorage quota (psy-9).
          const capped: ItemResponse =
            typeof response.value === "string" &&
            response.value.length > MAX_TEXT_RESPONSE_LENGTH
              ? { ...response, value: response.value.slice(0, MAX_TEXT_RESPONSE_LENGTH) }
              : response;

          // Replace existing response for this item or append
          const existing = session.responses.findIndex(
            (r) => r.itemId === capped.itemId
          );
          const responses = [...session.responses];
          if (existing >= 0) {
            responses[existing] = capped;
          } else {
            responses.push(capped);
          }

          return {
            sessions: {
              ...state.sessions,
              [id]: { ...session, responses },
            },
          };
        }),

      advanceItem: () =>
        set((state) => ({
          currentItemIndex: state.currentItemIndex + 1,
        })),

      goBackItem: () =>
        set((state) => ({
          currentItemIndex: Math.max(0, state.currentItemIndex - 1),
        })),

      completeInstrument: (result) =>
        set((state) => {
          const id = state.activeInstrumentId;
          if (!id) return state;
          const session = state.sessions[id];
          if (!session) return state;

          return {
            activeInstrumentId: null,
            currentItemIndex: 0,
            sessions: {
              ...state.sessions,
              [id]: { ...session, completedAt: Date.now() },
            },
            results: {
              ...state.results,
              [id]: result,
            },
          };
        }),

      setActiveInstrument: (id) =>
        set(() => ({
          activeInstrumentId: id,
          currentItemIndex: 0,
        })),

      resetInstrument: (instrumentId) =>
        set((state) => {
          const { [instrumentId]: _s, ...sessions } = state.sessions;
          const { [instrumentId]: _r, ...results } = state.results;
          return { sessions, results };
        }),

      exportData: () => {
        const { sessions, results, selectedTier } = get();
        return JSON.stringify({ sessions, results, selectedTier, exportedAt: Date.now() }, null, 2);
      },

      importData: (json) => {
        let data: Record<string, unknown>;
        try {
          data = JSON.parse(json);
        } catch {
          throw new Error("Invalid JSON");
        }
        if (
          !data ||
          typeof data !== "object" ||
          Array.isArray(data) ||
          !data.sessions ||
          typeof data.sessions !== "object" ||
          Array.isArray(data.sessions) ||
          !data.results ||
          typeof data.results !== "object" ||
          Array.isArray(data.results)
        ) {
          throw new Error("Invalid data: sessions and results must be objects");
        }
        if (
          data.selectedTier !== undefined &&
          data.selectedTier !== "lite" &&
          data.selectedTier !== "standard" &&
          data.selectedTier !== "heavy"
        ) {
          throw new Error("Invalid data: selectedTier must be lite, standard, or heavy");
        }

        // Validate imported payload BEFORE merging — import fails atomically
        // with a thrown Error; nothing is written to the store on failure.
        const importedSessions = sanitizeImportedSessions(
          data.sessions as Record<string, unknown>,
        );

        // Merge with existing data (don't overwrite completed results)
        const currentState = get();
        const mergedSessions = structuredClone({
          ...importedSessions,
          ...currentState.sessions,
        });

        // Results are validated against the sessions they will actually sit
        // beside — the merged ones, since an existing session wins over an
        // imported one. A fixed-form result is recomputed from those
        // responses rather than read off the payload.
        const importedResults = sanitizeImportedResults(
          data.results as Record<string, unknown>,
          mergedSessions,
        );
        const mergedResults = structuredClone({
          ...importedResults,
          ...currentState.results,
        });

        const tier = data.selectedTier as Tier | undefined;
        set({ sessions: mergedSessions, results: mergedResults, ...(tier && { selectedTier: tier }) });
        // Auto-score any sessions that have all responses but no result
        autoScoreCompleted();
      },
    }),
    {
      name: STORE_KEY,
      // Quota-aware storage: surfaces QuotaExceededError to the user and
      // tracks approximate byte usage instead of failing silently (psy-9).
      storage: createJSONStorage(createQuotaAwareStorage),
      // Persist only the durable assessment data — never the transient
      // persistence-health fields (they're recomputed at runtime).
      partialize: (state) => ({
        sessions: state.sessions,
        results: state.results,
        selectedTier: state.selectedTier,
        // Persist in-progress position so a mid-assessment reload resumes in
        // place rather than dropping back to the instrument list (psy P1).
        // The transient health/quota fields (storageError, storageBytes) stay
        // OUT — they are recomputed at runtime.
        activeInstrumentId: state.activeInstrumentId,
        currentItemIndex: state.currentItemIndex,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) autoScoreCompleted();
      },
    }
  )
);

// ── Import validation ──────────────────────────────────────────

function isFiniteTimestamp(t: unknown): t is number {
  return typeof t === "number" && Number.isFinite(t) && t > 0;
}

/** Validate a response value against the item's declared response format. */
function isValidResponseValue(value: unknown, item: Item): boolean {
  const resp = item.response;
  switch (resp.type) {
    case "likert":
      return (
        typeof value === "number" &&
        Number.isFinite(value) &&
        value >= resp.min &&
        value <= resp.max
      );
    case "binary":
      return value === 0 || value === 1;
    case "numeric":
      return typeof value === "number" && Number.isFinite(value);
    case "text":
      return typeof value === "string" && value.length <= MAX_TEXT_RESPONSE_LENGTH;
    case "multiple-choice":
      return (
        (typeof value === "number" &&
          Number.isInteger(value) &&
          value >= 0 &&
          value < resp.options.length) ||
        (typeof value === "string" && resp.options.includes(value))
      );
    default:
      return false;
  }
}

/**
 * Validate and repair imported sessions. Sessions for unregistered
 * instruments or with a malformed shape are dropped (with a console warning);
 * responses are filtered to those matching a real item with an in-range value.
 * Throws only on payloads that are not even object-shaped (caller pre-checks).
 */
function sanitizeImportedSessions(
  raw: Record<string, unknown>,
): Record<string, InstrumentSession> {
  const out: Record<string, InstrumentSession> = {};
  for (const [id, value] of Object.entries(raw)) {
    const registered = getInstrument(id);
    if (!registered) {
      console.warn(`[Psyche import] Skipping session for unknown instrument "${id}"`);
      continue;
    }
    if (!value || typeof value !== "object" || Array.isArray(value)) {
      console.warn(`[Psyche import] Skipping malformed session "${id}" (not an object)`);
      continue;
    }
    const session = value as Record<string, unknown>;
    if (!Array.isArray(session.responses)) {
      console.warn(`[Psyche import] Skipping session "${id}" (responses is not an array)`);
      continue;
    }

    const itemsById = new Map(registered.instrument.items.map((i) => [i.id, i]));
    const responses: ItemResponse[] = [];
    const seen = new Set<string>();
    for (const r of session.responses) {
      if (!r || typeof r !== "object") continue;
      const resp = r as Record<string, unknown>;
      if (typeof resp.itemId !== "string" || seen.has(resp.itemId)) continue;
      const item = itemsById.get(resp.itemId);
      if (!item) continue; // itemId must exist in the registered instrument
      if (!isValidResponseValue(resp.value, item)) continue;
      seen.add(resp.itemId);
      responses.push({
        itemId: resp.itemId,
        value: resp.value as number | string,
        timestamp: isFiniteTimestamp(resp.timestamp) ? resp.timestamp : Date.now(),
      });
    }

    out[id] = {
      instrumentId: id,
      startedAt: isFiniteTimestamp(session.startedAt) ? session.startedAt : Date.now(),
      ...(isFiniteTimestamp(session.completedAt) && { completedAt: session.completedAt }),
      responses,
    };
  }
  return out;
}

/** True when every item of the instrument has a response with a legal value. */
function hasCompleteResponses(instrument: Instrument, session: InstrumentSession): boolean {
  const answered = new Map(session.responses.map((r) => [r.itemId, r]));
  return instrument.items.every((item) => {
    const r = answered.get(item.id);
    return r !== undefined && isValidResponseValue(r.value, item);
  });
}

/**
 * Validate one score of a result-only (adaptive) payload.
 *
 * Returns null to reject — and rejection is fatal for the whole result, not
 * just the score: a payload carrying a scale this battery does not define, or
 * naming a scale twice, is not a payload with one bad row in it. It is a
 * payload that does not describe this instrument.
 */
function sanitizeResultOnlyScore(
  s: unknown,
  ownScales: Set<string>,
  seen: Set<string>,
): ScaleScore | null {
  if (!s || typeof s !== "object" || Array.isArray(s)) return null;
  const score = s as Record<string, unknown>;

  if (typeof score.scaleId !== "string" || score.scaleId.length === 0) return null;
  if (seen.has(score.scaleId)) return null; // one score per scale
  // Provenance is required: a result we cannot recompute has to say where it
  // came from, and the two provenances have different scale-membership rules.
  if (score.source !== "cat" && score.source !== "fixed-form") return null;
  if (score.source === "cat") {
    // CAT-estimated scales must be this instrument's own.
    if (!ownScales.has(score.scaleId)) return null;
  } else if (!ownScales.has(score.scaleId) && !isKnownScaleId(score.scaleId)) {
    // Carried over from the seeding fixed-form instrument — a different scale
    // namespace, but still one the battery defines.
    return null;
  }

  if (typeof score.raw !== "number" || !Number.isFinite(score.raw)) return null;
  if (typeof score.normalized !== "number" || !Number.isFinite(score.normalized)) return null;
  if (
    typeof score.itemCount !== "number" ||
    !Number.isInteger(score.itemCount) ||
    score.itemCount < 0
  ) {
    return null;
  }

  const hasTheta =
    typeof score.theta === "number" && Number.isFinite(score.theta) &&
    typeof score.se === "number" && Number.isFinite(score.se) && score.se > 0;
  // A CAT score without a usable theta/se pair did not come out of the CAT.
  if (score.source === "cat" && !hasTheta) return null;

  const administered =
    typeof score.itemsAdministered === "number" &&
    Number.isInteger(score.itemsAdministered) &&
    score.itemsAdministered >= 0
      ? score.itemsAdministered
      : undefined;

  return {
    scaleId: score.scaleId,
    scaleName:
      typeof score.scaleName === "string" && score.scaleName.length > 0
        ? score.scaleName
        : score.scaleId,
    raw: score.raw,
    normalized: Math.max(0, Math.min(100, score.normalized)),
    itemCount: score.itemCount,
    ...(hasTheta && { theta: score.theta as number, se: score.se as number }),
    ...(administered !== undefined && { itemsAdministered: administered }),
    source: score.source,
  };
}

/**
 * Validate imported results against what the instrument and the imported
 * responses can actually support.
 *
 * The old version checked only that the instrument was registered and that
 * raw/normalized were finite numbers. Nothing tied a score to a scale the
 * instrument has, to a response set, or to anything at all — so a corrupt or
 * crafted backup could mint a plausible IPIP-NEO-300 profile for an
 * instrument nobody answered, and `autoScoreCompleted` would then skip that
 * instrument precisely *because* a result already existed. Those values
 * survive export into the analysis merger, which promotes matching NEO domain
 * scores to high-confidence self-report.
 *
 * So: for a fixed-form instrument we hold the items, and the honest score is
 * the one we compute from the responses — the serialized values are ignored
 * entirely, and a result without a complete response set is dropped. For
 * adaptive instruments there is nothing to recompute from (CAT responses live
 * in the runner, not the session), so the payload must instead prove it
 * describes this instrument: registered scales, each named once, provenance
 * present, and a session behind it.
 */
function sanitizeImportedResults(
  raw: Record<string, unknown>,
  sessions: Record<string, InstrumentSession>,
): Record<string, InstrumentResult> {
  const out: Record<string, InstrumentResult> = {};
  for (const [id, value] of Object.entries(raw)) {
    const registered = getInstrument(id);
    if (!registered) {
      console.warn(`[Psyche import] Skipping result for unknown instrument "${id}"`);
      continue;
    }
    if (!value || typeof value !== "object" || Array.isArray(value)) {
      console.warn(`[Psyche import] Skipping malformed result "${id}" (not an object)`);
      continue;
    }
    const result = value as Record<string, unknown>;
    if (!Array.isArray(result.scores)) {
      console.warn(`[Psyche import] Skipping result "${id}" (scores is not an array)`);
      continue;
    }
    const completedAt = isFiniteTimestamp(result.completedAt) ? result.completedAt : Date.now();
    const session = sessions[id];
    const { instrument, score } = registered;

    // ── Fixed-form: recompute, never trust ──────────────────────────
    if (!instrument.adaptive && instrument.items.length > 0) {
      if (!session || !hasCompleteResponses(instrument, session)) {
        console.warn(
          `[Psyche import] Dropping result "${id}" — no complete response set to recompute it from`,
        );
        continue;
      }
      let recomputed: InstrumentResult;
      try {
        recomputed = score(instrument, session);
      } catch {
        console.warn(`[Psyche import] Dropping result "${id}" (scoring threw)`);
        continue;
      }
      if (instrument.scales.length > 0 && recomputed.scores.length === 0) {
        console.warn(`[Psyche import] Dropping result "${id}" (recomputed to nothing)`);
        continue;
      }
      // Recomputed values, imported timestamp.
      out[id] = { instrumentId: id, completedAt, scores: recomputed.scores };
      continue;
    }

    // ── Result-only (adaptive): prove it belongs to this instrument ──
    if (!session) {
      console.warn(`[Psyche import] Dropping result "${id}" — no session backs it`);
      continue;
    }
    const ownScales = new Set(instrument.scales.map((s) => s.id));
    const seen = new Set<string>();
    const scores: ScaleScore[] = [];
    let rejected = false;
    for (const s of result.scores) {
      const clean = sanitizeResultOnlyScore(s, ownScales, seen);
      if (!clean) {
        rejected = true;
        break;
      }
      seen.add(clean.scaleId);
      scores.push(clean);
    }
    if (rejected || scores.length === 0) {
      console.warn(
        `[Psyche import] Dropping result "${id}" — scores do not describe this instrument`,
      );
      continue;
    }

    out[id] = { instrumentId: id, completedAt, scores };
  }
  return out;
}

/** Score any sessions that have all responses but no result yet. */
function autoScoreCompleted(): void {
  const { sessions, results } = usePsycheStore.getState();
  const newResults: Record<string, InstrumentResult> = {};

  for (const [id, session] of Object.entries(sessions)) {
    if (results[id]) continue; // already scored
    const registered = getInstrument(id);
    if (!registered) continue; // instrument not in registry
    const { instrument, score } = registered;

    // Adaptive instruments are scored by the CAT flow; auto-scoring them
    // would mint empty results from their placeholder scorer.
    if (instrument.adaptive || instrument.items.length === 0) continue;

    // Require EXACT coverage: every instrument item must have a response
    // whose itemId matches a real item and whose value is in range.
    // (Counting unique IDs alone lets junk IDs mint empty/corrupt results.)
    const answered = new Map(session.responses.map((r) => [r.itemId, r]));
    const complete = instrument.items.every((item) => {
      const r = answered.get(item.id);
      return r !== undefined && isValidResponseValue(r.value, item);
    });
    if (!complete) continue;

    try {
      const result = score(instrument, session);
      // Reject degenerate results — an instrument with scales should score
      if (instrument.scales.length > 0 && result.scores.length === 0) continue;
      newResults[id] = result;
    } catch {
      // scoring failed — skip
    }
  }

  if (Object.keys(newResults).length > 0) {
    usePsycheStore.setState({
      results: { ...results, ...newResults },
      sessions: Object.fromEntries(
        Object.entries(sessions).map(([id, s]) =>
          newResults[id] ? [id, { ...s, completedAt: s.completedAt ?? Date.now() }] : [id, s]
        )
      ),
    });
  }
}
