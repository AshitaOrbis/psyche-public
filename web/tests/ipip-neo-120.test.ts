import { describe, it, expect } from "vitest";
import "../src/instruments/ipip-neo-120";
import { getInstrument } from "../src/instruments/registry";
import type { InstrumentSession, ItemResponse } from "../src/instruments/types";

describe("IPIP-NEO-120 instrument", () => {
  const registered = getInstrument("ipip-neo-120")!;
  const { instrument, score } = registered;

  it("is registered with correct metadata", () => {
    expect(instrument).toBeDefined();
    expect(instrument.id).toBe("ipip-neo-120");
    expect(instrument.itemCount).toBe(120);
    expect(instrument.items).toHaveLength(120);
  });

  it("has 5 domain scales and 30 facet scales", () => {
    const domains = instrument.scales.filter((s) => !s.parentId);
    const facets = instrument.scales.filter((s) => s.parentId);
    expect(domains).toHaveLength(5);
    expect(facets).toHaveLength(30);
  });

  it("each facet has exactly 4 items", () => {
    const facetItemCounts = new Map<string, number>();
    for (const item of instrument.items) {
      facetItemCounts.set(item.scaleId, (facetItemCounts.get(item.scaleId) ?? 0) + 1);
    }
    for (const [facetId, count] of facetItemCounts) {
      expect(count, `Facet ${facetId} should have 4 items`).toBe(4);
    }
  });

  it("scores all 5 domains on neutral responses", () => {
    const responses: ItemResponse[] = instrument.items.map((item) => ({
      itemId: item.id,
      value: 3, // neutral
      timestamp: 0,
    }));

    const session: InstrumentSession = {
      instrumentId: "ipip-neo-120",
      startedAt: 0,
      completedAt: 1,
      responses,
    };

    const result = score(instrument, session);

    // Should have 5 domain + 30 facet scores
    expect(result.scores).toHaveLength(35);

    // All domain scores should be ~50 (neutral)
    const domains = result.scores.filter((s) => s.scaleId.length === 1);
    expect(domains).toHaveLength(5);

    for (const d of domains) {
      expect(d.normalized).toBeCloseTo(50, 0);
    }
  });

  it("scores high on all-5 responses", () => {
    const responses: ItemResponse[] = instrument.items.map((item) => ({
      itemId: item.id,
      value: 5, // max agreement
      timestamp: 0,
    }));

    const session: InstrumentSession = {
      instrumentId: "ipip-neo-120",
      startedAt: 0,
      completedAt: 1,
      responses,
    };

    const result = score(instrument, session);
    const domains = result.scores.filter((s) => s.scaleId.length === 1);

    // Reversed items will get low scores, so domains won't be 100
    // But unreversed facets should be 100
    for (const d of domains) {
      // Should be somewhere between 0-100, not all 100 due to reverse coding
      expect(d.normalized).toBeGreaterThan(0);
      expect(d.normalized).toBeLessThanOrEqual(100);
    }
  });

  // ── Content pinning (psy-10) ────────────────────────────────────────────
  // These assertions PIN the item content sourced from the npm package
  // `b5-johnson-120-ipip-neo-pi-r`. A silent package bump that changes item
  // IDs, keyed direction, or scale/facet mapping must break these tests rather
  // than silently re-scaling everyone's Big Five results.

  /** Normalized, sort-stable view of each item's identity + mapping. */
  const normalizedItems = instrument.items
    .map((i) => ({ id: i.id, scaleId: i.scaleId, reversed: !!i.reversed }))
    .sort((a, b) => a.id.localeCompare(b.id));

  it("pins the normalized item list (ids, scale/facet mapping, keyed direction)", () => {
    expect(normalizedItems).toMatchSnapshot();
  });

  it("pins aggregate content invariants", () => {
    // Exactly 120 items, all with unique IDs.
    expect(normalizedItems).toHaveLength(120);
    expect(new Set(normalizedItems.map((i) => i.id)).size).toBe(120);

    // Every item maps to one of the 30 expected facet scales (domain letter + 1-6).
    const expectedScaleIds = new Set<string>();
    for (const d of ["N", "E", "O", "A", "C"]) {
      for (let f = 1; f <= 6; f++) expectedScaleIds.add(`${d}${f}`);
    }
    for (const i of normalizedItems) {
      expect(expectedScaleIds.has(i.scaleId)).toBe(true);
    }

    // Keyed-direction balance: a content change that flipped a block of items
    // would shift this count. Pin the exact number of reverse-keyed items.
    const reversedCount = normalizedItems.filter((i) => i.reversed).length;
    expect(reversedCount).toBe(
      instrument.items.filter((i) => i.reversed).length,
    );
    expect(reversedCount).toMatchSnapshot("reversed-item-count");
  });

  it("pins a known anchor item's identity and mapping", () => {
    // "Worry about things" is the first N-Anxiety (N1) item, plus-keyed.
    const worry = instrument.items.find((i) => i.id === "43c98ce8-a07a-4dc2-80f6-c1b2a2485f06");
    expect(worry).toBeDefined();
    expect(worry!.scaleId).toBe("N1");
    expect(worry!.reversed).toBe(false);
    expect(worry!.text).toBe("Worry about things");
  });
});
