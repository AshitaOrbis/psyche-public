/**
 * Imported results must be earned, not asserted.
 *
 * sanitizeImportedResults() used to check only that the instrument ID was
 * registered, that scaleId was a non-empty string, and that raw/normalized
 * were finite. Nothing tied a score to a scale that instrument actually has,
 * to a response set, or to anything at all — so a hand-written backup could
 * mint a full IPIP-NEO-300 profile without a single answered item. Those
 * values then survive export and reach the analysis merger, which promotes
 * matching NEO domain scores to "high-confidence self-report"
 * (analysis/psyche_analysis/synthesis/merge.py).
 *
 * The rules under test:
 *   - fixed-form results are RECOMPUTED from the imported responses; the
 *     serialized score values are never trusted
 *   - a fixed-form result with no complete response set is dropped
 *   - result-only (adaptive) data must name registered scales, name each one
 *     once, carry provenance, and have a session behind it
 */
import { describe, it, expect, beforeEach } from "vitest";
import { usePsycheStore } from "../src/state/store";
import { getInstrument } from "../src/instruments/registry";
import type { ItemResponse } from "../src/instruments/types";

import "../src/instruments/init";

function importJSON(payload: unknown): void {
  usePsycheStore.getState().importData(JSON.stringify(payload));
}

/** Every item of a fixed-form instrument answered with a legal value. */
function fullResponses(instrumentId: string, pick: "min" | "max" = "min"): ItemResponse[] {
  const { instrument } = getInstrument(instrumentId)!;
  return instrument.items.map((item) => {
    let value: number | string = 0;
    if (item.response.type === "likert") {
      value = pick === "min" ? item.response.min : item.response.max;
    } else if (item.response.type === "binary") {
      value = pick === "min" ? 0 : 1;
    } else if (item.response.type === "numeric") {
      value = 1;
    } else if (item.response.type === "multiple-choice") {
      value = 0;
    } else {
      value = "an answer";
    }
    return { itemId: item.id, value, timestamp: 1_700_000_000_000 };
  });
}

describe("imported results must be bound to responses", () => {
  beforeEach(() => {
    localStorage.clear();
    usePsycheStore.setState({
      sessions: {},
      results: {},
      activeInstrumentId: null,
      currentItemIndex: 0,
      selectedTier: "standard",
    });
  });

  it("a fabricated NEO result with no responses is rejected outright", () => {
    importJSON({
      sessions: {},
      results: {
        "ipip-neo-300": {
          instrumentId: "ipip-neo-300",
          completedAt: Date.now(),
          scores: [{ scaleId: "N", scaleName: "Neuroticism", raw: 4.9, normalized: 99, itemCount: 60 }],
        },
      },
    });
    expect(usePsycheStore.getState().results["ipip-neo-300"]).toBeUndefined();
  });

  it("a fixed-form result is recomputed from responses, not read off the payload", () => {
    const responses = fullResponses("rosenberg", "min");
    importJSON({
      sessions: { rosenberg: { instrumentId: "rosenberg", startedAt: 1, completedAt: 2, responses } },
      results: {
        rosenberg: {
          instrumentId: "rosenberg",
          completedAt: 2,
          // A lie: every item was answered at the floor of the scale.
          scores: [{ scaleId: "self-esteem", scaleName: "Self-Esteem", raw: 4, normalized: 100, itemCount: 10 }],
        },
      },
    });
    const result = usePsycheStore.getState().results["rosenberg"];
    expect(result).toBeDefined();
    const honest = getInstrument("rosenberg")!.score(
      getInstrument("rosenberg")!.instrument,
      usePsycheStore.getState().sessions["rosenberg"]!,
    );
    expect(result!.scores).toEqual(honest.scores);
    expect(result!.scores[0]!.normalized).not.toBe(100);
  });

  it("a fixed-form result keeps its original completion timestamp", () => {
    importJSON({
      sessions: {
        rosenberg: { instrumentId: "rosenberg", startedAt: 1, completedAt: 2, responses: fullResponses("rosenberg") },
      },
      results: {
        rosenberg: { instrumentId: "rosenberg", completedAt: 1_700_000_123_456, scores: [] },
      },
    });
    expect(usePsycheStore.getState().results["rosenberg"]!.completedAt).toBe(1_700_000_123_456);
  });

  it("a fixed-form result with an incomplete response set is dropped", () => {
    const responses = fullResponses("rosenberg").slice(0, 3);
    importJSON({
      sessions: { rosenberg: { instrumentId: "rosenberg", startedAt: 1, responses } },
      results: {
        rosenberg: {
          instrumentId: "rosenberg",
          completedAt: Date.now(),
          scores: [{ scaleId: "self-esteem", scaleName: "SE", raw: 3, normalized: 75, itemCount: 10 }],
        },
      },
    });
    expect(usePsycheStore.getState().results["rosenberg"]).toBeUndefined();
  });

  it("an honest export round-trips unchanged", () => {
    importJSON({
      sessions: {
        rosenberg: { instrumentId: "rosenberg", startedAt: 1, completedAt: 2, responses: fullResponses("rosenberg", "max") },
      },
      results: {},
    });
    const first = usePsycheStore.getState().results["rosenberg"];
    expect(first).toBeDefined();

    const exported = usePsycheStore.getState().exportData();
    usePsycheStore.setState({ sessions: {}, results: {} });
    usePsycheStore.getState().importData(exported);

    expect(usePsycheStore.getState().results["rosenberg"]!.scores).toEqual(first!.scores);
  });
});

describe("result-only (adaptive) imports are checked against the registry", () => {
  const session = { "cat-big5": { instrumentId: "cat-big5", startedAt: 1, completedAt: 2, responses: [] } };

  function catScore(scaleId: string, extra: Record<string, unknown> = {}) {
    return {
      scaleId,
      scaleName: scaleId,
      raw: 0.4,
      normalized: 65,
      itemCount: 6,
      theta: 0.4,
      se: 0.25,
      source: "cat",
      ...extra,
    };
  }

  beforeEach(() => {
    localStorage.clear();
    usePsycheStore.setState({
      sessions: {},
      results: {},
      activeInstrumentId: null,
      currentItemIndex: 0,
      selectedTier: "heavy",
    });
  });

  it("accepts a well-formed CAT result", () => {
    importJSON({
      sessions: session,
      results: {
        "cat-big5": { instrumentId: "cat-big5", completedAt: 3, scores: [catScore("N1"), catScore("N")] },
      },
    });
    const result = usePsycheStore.getState().results["cat-big5"];
    expect(result).toBeDefined();
    expect(result!.scores).toHaveLength(2);
  });

  it("rejects a result naming a scale the instrument does not have", () => {
    importJSON({
      sessions: session,
      results: {
        "cat-big5": {
          instrumentId: "cat-big5",
          completedAt: 3,
          scores: [catScore("N1"), catScore("self-esteem")], // borrowed from Rosenberg
        },
      },
    });
    expect(usePsycheStore.getState().results["cat-big5"]).toBeUndefined();
  });

  it("rejects a result naming the same domain twice", () => {
    importJSON({
      sessions: session,
      results: {
        "cat-big5": {
          instrumentId: "cat-big5",
          completedAt: 3,
          scores: [catScore("N", { normalized: 10 }), catScore("N", { normalized: 90 })],
        },
      },
    });
    expect(usePsycheStore.getState().results["cat-big5"]).toBeUndefined();
  });

  it("rejects a result-only payload with no session behind it", () => {
    importJSON({
      sessions: {},
      results: {
        "cat-big5": { instrumentId: "cat-big5", completedAt: 3, scores: [catScore("N1")] },
      },
    });
    expect(usePsycheStore.getState().results["cat-big5"]).toBeUndefined();
  });

  it("rejects scores with no provenance", () => {
    const noSource = catScore("N1");
    delete (noSource as Record<string, unknown>).source;
    importJSON({
      sessions: session,
      results: { "cat-big5": { instrumentId: "cat-big5", completedAt: 3, scores: [noSource] } },
    });
    expect(usePsycheStore.getState().results["cat-big5"]).toBeUndefined();
  });

  it("rejects a cat-sourced score without a usable theta/se pair", () => {
    importJSON({
      sessions: session,
      results: {
        "cat-big5": {
          instrumentId: "cat-big5",
          completedAt: 3,
          scores: [catScore("N1", { se: 0 })],
        },
      },
    });
    expect(usePsycheStore.getState().results["cat-big5"]).toBeUndefined();
  });

  it("accepts a fixed-form carryover scale from the seeding instrument", () => {
    // cat-hexaco scales are HH/HH1…; the hexaco-200 scores it carries forward
    // keep that instrument's namespace (hh/hh_sin…). Both are real scales.
    importJSON({
      sessions: { "cat-hexaco": { instrumentId: "cat-hexaco", startedAt: 1, completedAt: 2, responses: [] } },
      results: {
        "cat-hexaco": {
          instrumentId: "cat-hexaco",
          completedAt: 3,
          scores: [
            catScore("HH1"),
            { scaleId: "hh_sin", scaleName: "Sincerity", raw: 3.9, normalized: 72, itemCount: 9, source: "fixed-form" },
          ],
        },
      },
    });
    expect(usePsycheStore.getState().results["cat-hexaco"]!.scores).toHaveLength(2);
  });

  it("rejects a carryover scale no instrument in the battery defines", () => {
    importJSON({
      sessions: { "cat-hexaco": { instrumentId: "cat-hexaco", startedAt: 1, completedAt: 2, responses: [] } },
      results: {
        "cat-hexaco": {
          instrumentId: "cat-hexaco",
          completedAt: 3,
          scores: [
            catScore("HH1"),
            { scaleId: "invented_scale", scaleName: "Invented", raw: 5, normalized: 99, itemCount: 9, source: "fixed-form" },
          ],
        },
      },
    });
    expect(usePsycheStore.getState().results["cat-hexaco"]).toBeUndefined();
  });

  it("still clamps normalized into 0-100 on an accepted result", () => {
    importJSON({
      sessions: session,
      results: {
        "cat-big5": { instrumentId: "cat-big5", completedAt: 3, scores: [catScore("N1", { normalized: 250 })] },
      },
    });
    expect(usePsycheStore.getState().results["cat-big5"]!.scores[0]!.normalized).toBe(100);
  });
});
