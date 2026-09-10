import { describe, it, expect } from "vitest";
import { scoreLikert, scoreBinary } from "../src/scoring/engine";
import type { Instrument, InstrumentSession } from "../src/instruments/types";

function makeInstrument(items: { id: string; scaleId: string; reversed?: boolean }[]): Instrument {
  return {
    id: "test",
    name: "Test",
    shortName: "T",
    description: "",
    citation: "",
    itemCount: items.length,
    estimatedMinutes: 1,
    scales: [
      { id: "A", name: "Scale A" },
      { id: "B", name: "Scale B" },
    ],
    items: items.map((i) => ({
      ...i,
      text: "test item",
      response: { type: "likert" as const, min: 1, max: 5, labels: [] },
    })),
  };
}

describe("scoreLikert", () => {
  it("computes mean score for a scale", () => {
    const inst = makeInstrument([
      { id: "a1", scaleId: "A" },
      { id: "a2", scaleId: "A" },
      { id: "b1", scaleId: "B" },
    ]);

    const session: InstrumentSession = {
      instrumentId: "test",
      startedAt: 0,
      responses: [
        { itemId: "a1", value: 4, timestamp: 0 },
        { itemId: "a2", value: 2, timestamp: 0 },
        { itemId: "b1", value: 5, timestamp: 0 },
      ],
    };

    const result = scoreLikert(inst, session);
    const scaleA = result.scores.find((s) => s.scaleId === "A")!;
    const scaleB = result.scores.find((s) => s.scaleId === "B")!;

    expect(scaleA.raw).toBe(3); // (4+2)/2
    expect(scaleA.normalized).toBe(50); // (3-1)/(5-1)*100
    expect(scaleA.itemCount).toBe(2);
    expect(scaleB.raw).toBe(5);
    expect(scaleB.normalized).toBe(100);
  });

  it("reverse scores items", () => {
    const inst = makeInstrument([
      { id: "a1", scaleId: "A" },
      { id: "a2", scaleId: "A", reversed: true },
    ]);

    const session: InstrumentSession = {
      instrumentId: "test",
      startedAt: 0,
      responses: [
        { itemId: "a1", value: 5, timestamp: 0 }, // straight: 5
        { itemId: "a2", value: 5, timestamp: 0 }, // reversed: 1+5-5 = 1
      ],
    };

    const result = scoreLikert(inst, session);
    const scaleA = result.scores.find((s) => s.scaleId === "A")!;

    // Mean of (5 + 1) / 2 = 3
    expect(scaleA.raw).toBe(3);
    expect(scaleA.normalized).toBe(50);
  });

  it("handles missing responses gracefully", () => {
    const inst = makeInstrument([
      { id: "a1", scaleId: "A" },
      { id: "a2", scaleId: "A" },
    ]);

    const session: InstrumentSession = {
      instrumentId: "test",
      startedAt: 0,
      responses: [{ itemId: "a1", value: 4, timestamp: 0 }],
    };

    const result = scoreLikert(inst, session);
    const scaleA = result.scores.find((s) => s.scaleId === "A")!;

    // Only one response, mean is just that value
    expect(scaleA.raw).toBe(4);
    expect(scaleA.itemCount).toBe(1);
  });
  it("last response wins for duplicate itemIds", () => {
    const inst = makeInstrument([
      { id: "a1", scaleId: "A" },
    ]);

    const session: InstrumentSession = {
      instrumentId: "test",
      startedAt: 0,
      responses: [
        { itemId: "a1", value: 2, timestamp: 0 },
        { itemId: "a1", value: 5, timestamp: 1 }, // overwrites
      ],
    };

    const result = scoreLikert(inst, session);
    expect(result.scores[0]!.raw).toBe(5);
  });

  it("items with unknown scaleId are silently excluded", () => {
    const inst = makeInstrument([
      { id: "a1", scaleId: "A" },
      { id: "x1", scaleId: "UNKNOWN" },
    ]);

    const session: InstrumentSession = {
      instrumentId: "test",
      startedAt: 0,
      responses: [
        { itemId: "a1", value: 3, timestamp: 0 },
        { itemId: "x1", value: 5, timestamp: 0 },
      ],
    };

    const result = scoreLikert(inst, session);
    // UNKNOWN scale items are grouped but UNKNOWN is not in instrument.scales,
    // so it never appears in the output
    expect(result.scores).toHaveLength(1);
    expect(result.scores[0]!.scaleId).toBe("A");
  });

  it("non-numeric responses are filtered out", () => {
    const inst = makeInstrument([
      { id: "a1", scaleId: "A" },
      { id: "a2", scaleId: "A" },
    ]);

    const session: InstrumentSession = {
      instrumentId: "test",
      startedAt: 0,
      responses: [
        { itemId: "a1", value: 4, timestamp: 0 },
        { itemId: "a2", value: "text response", timestamp: 0 },
      ],
    };

    const result = scoreLikert(inst, session);
    expect(result.scores[0]!.itemCount).toBe(1); // only numeric response counted
    expect(result.scores[0]!.raw).toBe(4);
  });
});

// --- scoreBinary tests ---

function makeBinaryInstrument(items: { id: string; scaleId: string; reversed?: boolean }[]): Instrument {
  return {
    id: "test-binary",
    name: "Test Binary",
    shortName: "TB",
    description: "",
    citation: "",
    itemCount: items.length,
    estimatedMinutes: 1,
    scales: [
      { id: "A", name: "Scale A" },
      { id: "B", name: "Scale B" },
    ],
    items: items.map((i) => ({
      ...i,
      text: "test item",
      response: { type: "binary" as const, labels: ["True", "False"] },
    })),
  };
}

describe("scoreBinary", () => {
  it("computes mean score for a scale", () => {
    const inst = makeBinaryInstrument([
      { id: "a1", scaleId: "A" },
      { id: "a2", scaleId: "A" },
      { id: "b1", scaleId: "B" },
    ]);

    const session: InstrumentSession = {
      instrumentId: "test-binary",
      startedAt: 0,
      responses: [
        { itemId: "a1", value: 1, timestamp: 0 }, // True
        { itemId: "a2", value: 0, timestamp: 0 }, // False
        { itemId: "b1", value: 1, timestamp: 0 }, // True
      ],
    };

    const result = scoreBinary(inst, session);
    const scaleA = result.scores.find((s) => s.scaleId === "A")!;
    const scaleB = result.scores.find((s) => s.scaleId === "B")!;

    expect(scaleA.raw).toBe(0.5); // (1+0)/2
    expect(scaleA.normalized).toBe(50); // 0.5 * 100
    expect(scaleA.itemCount).toBe(2);
    expect(scaleB.raw).toBe(1);
    expect(scaleB.normalized).toBe(100);
  });

  it("reverse scores binary items", () => {
    const inst = makeBinaryInstrument([
      { id: "a1", scaleId: "A" },
      { id: "a2", scaleId: "A", reversed: true },
    ]);

    const session: InstrumentSession = {
      instrumentId: "test-binary",
      startedAt: 0,
      responses: [
        { itemId: "a1", value: 1, timestamp: 0 }, // straight: 1
        { itemId: "a2", value: 1, timestamp: 0 }, // reversed: 1-1 = 0
      ],
    };

    const result = scoreBinary(inst, session);
    const scaleA = result.scores.find((s) => s.scaleId === "A")!;

    expect(scaleA.raw).toBe(0.5); // (1 + 0) / 2
    expect(scaleA.normalized).toBe(50);
  });

  it("returns empty scores when all responses missing", () => {
    const inst = makeBinaryInstrument([
      { id: "a1", scaleId: "A" },
      { id: "a2", scaleId: "A" },
    ]);

    const session: InstrumentSession = {
      instrumentId: "test-binary",
      startedAt: 0,
      responses: [],
    };

    const result = scoreBinary(inst, session);
    expect(result.scores).toHaveLength(0);
  });

  it("binary reverser (1-v) differs from Likert reverser (max+min-v)", () => {
    // Binary: reversed value of 1 = 1-1 = 0
    // Likert (1-5): reversed value of 5 = 1+5-5 = 1
    // These are fundamentally different operations, verify both produce correct results

    const binaryInst = makeBinaryInstrument([
      { id: "a1", scaleId: "A", reversed: true },
    ]);
    const binarySession: InstrumentSession = {
      instrumentId: "test-binary",
      startedAt: 0,
      responses: [{ itemId: "a1", value: 1, timestamp: 0 }],
    };
    const binaryResult = scoreBinary(binaryInst, binarySession);
    expect(binaryResult.scores[0]!.raw).toBe(0); // 1 - 1 = 0

    const likertInst = makeInstrument([
      { id: "a1", scaleId: "A", reversed: true },
    ]);
    const likertSession: InstrumentSession = {
      instrumentId: "test",
      startedAt: 0,
      responses: [{ itemId: "a1", value: 5, timestamp: 0 }],
    };
    const likertResult = scoreLikert(likertInst, likertSession);
    expect(likertResult.scores[0]!.raw).toBe(1); // 1 + 5 - 5 = 1
  });
});
