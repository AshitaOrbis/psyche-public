import { describe, it, expect } from "vitest";
import "../src/instruments/ipip-neo-60";
import { getInstrument } from "../src/instruments/registry";
import type { InstrumentSession, ItemResponse } from "../src/instruments/types";

describe("IPIP-NEO-60 instrument", () => {
  const registered = getInstrument("ipip-neo-60")!;
  const { instrument, score } = registered;

  it("is registered with correct metadata", () => {
    expect(instrument).toBeDefined();
    expect(instrument.id).toBe("ipip-neo-60");
    expect(instrument.itemCount).toBe(60);
    expect(instrument.items).toHaveLength(60);
  });

  it("has 5 domain scales and 30 facet scales", () => {
    const domains = instrument.scales.filter((s) => !s.parentId);
    const facets = instrument.scales.filter((s) => s.parentId);
    expect(domains).toHaveLength(5);
    expect(facets).toHaveLength(30);
  });

  it("each facet has exactly 2 items", () => {
    const facetItemCounts = new Map<string, number>();
    for (const item of instrument.items) {
      facetItemCounts.set(item.scaleId, (facetItemCounts.get(item.scaleId) ?? 0) + 1);
    }
    for (const [facetId, count] of facetItemCounts) {
      expect(count, `Facet ${facetId} should have 2 items`).toBe(2);
    }
  });

  it("scores all 5 domains on neutral responses", () => {
    const responses: ItemResponse[] = instrument.items.map((item) => ({
      itemId: item.id,
      value: 3,
      timestamp: 0,
    }));

    const session: InstrumentSession = {
      instrumentId: "ipip-neo-60",
      startedAt: 0,
      completedAt: 1,
      responses,
    };

    const result = score(instrument, session);

    // Should have 5 domain + 30 facet scores
    expect(result.scores).toHaveLength(35);

    const domains = result.scores.filter((s) => s.scaleId.length === 1);
    expect(domains).toHaveLength(5);

    for (const d of domains) {
      expect(d.normalized).toBeCloseTo(50, 0);
    }
  });

  // ── Content pinning (psy-10) ────────────────────────────────────────────
  // The NEO-60 is built by selecting the first 2 items per facet from the same
  // npm package as the NEO-120. Pin the resulting item set so a package bump
  // (or a change to the selection logic) can't silently alter which items are
  // administered or how they're keyed/mapped.

  /** Normalized, sort-stable view of each item's identity + mapping. */
  const normalizedItems = instrument.items
    .map((i) => ({ id: i.id, scaleId: i.scaleId, reversed: !!i.reversed }))
    .sort((a, b) => a.id.localeCompare(b.id));

  it("pins the normalized item list (ids, scale/facet mapping, keyed direction)", () => {
    expect(normalizedItems).toMatchSnapshot();
  });

  it("pins aggregate content invariants", () => {
    // Exactly 60 items (2 per facet × 30 facets), all unique.
    expect(normalizedItems).toHaveLength(60);
    expect(new Set(normalizedItems.map((i) => i.id)).size).toBe(60);

    // Every item maps to one of the 30 expected facet scales.
    const expectedScaleIds = new Set<string>();
    for (const d of ["N", "E", "O", "A", "C"]) {
      for (let f = 1; f <= 6; f++) expectedScaleIds.add(`${d}${f}`);
    }
    for (const i of normalizedItems) {
      expect(expectedScaleIds.has(i.scaleId)).toBe(true);
    }

    // Pin the reverse-keyed count.
    expect(normalizedItems.filter((i) => i.reversed).length).toMatchSnapshot(
      "reversed-item-count",
    );
  });
});
