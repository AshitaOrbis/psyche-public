import { describe, it, expect } from "vitest";
import type { GRMItem } from "../src/scoring/grm-engine";
import {
  initCATSession,
  getNextItem,
  registerResponse,
  getCATProgress,
  catSessionToScores,
  DEFAULT_STOPPING,
} from "../src/scoring/cat-controller";

// Build a small item bank for testing: 2 dimensions, 5 items each
function makeBank(): GRMItem[] {
  const items: GRMItem[] = [];
  for (const dim of ["D1", "D2"]) {
    for (let i = 0; i < 5; i++) {
      items.push({
        id: `${dim}-${i}`,
        text: `Item ${dim}-${i}`,
        discrimination: 1.2 + i * 0.1,
        thresholds: [-1.5, -0.5, 0.5, 1.5],
        numCategories: 5,
        dimensionId: dim,
      });
    }
  }
  return items;
}

describe("CAT Controller", () => {
  describe("initCATSession", () => {
    it("creates sessions for all dimensions", () => {
      const bank = makeBank();
      const session = initCATSession("test-cat", bank);
      expect(session.dimensions.size).toBe(2);
      expect(session.dimensionOrder).toContain("D1");
      expect(session.dimensionOrder).toContain("D2");
      expect(session.complete).toBe(false);
    });

    it("builds dimensionItems and itemIndex caches", () => {
      const bank = makeBank();
      const session = initCATSession("test-cat", bank);
      // dimensionItems should have entries for both dimensions
      expect(session.dimensionItems.size).toBe(2);
      expect(session.dimensionItems.get("D1")).toHaveLength(5);
      expect(session.dimensionItems.get("D2")).toHaveLength(5);
      // itemIndex should have all 10 items
      expect(session.itemIndex.size).toBe(10);
      expect(session.itemIndex.get("D1-0")).toBeDefined();
      expect(session.itemIndex.get("D2-4")).toBeDefined();
    });

    it("skips dimension if fixed-form SE meets threshold", () => {
      const bank = makeBank();
      const fixedScores = [
        { scaleId: "D1", scaleName: "D1", raw: 0, normalized: 50, itemCount: 10, theta: 0.5, se: 0.2 },
      ];
      const session = initCATSession("test-cat", bank, fixedScores);
      // D1 should be skipped (SE 0.2 < threshold 0.30)
      expect(session.dimensionOrder).not.toContain("D1");
      expect(session.dimensionOrder).toContain("D2");
    });

    it("uses fixed-form theta as prior", () => {
      const bank = makeBank();
      const fixedScores = [
        { scaleId: "D1", scaleName: "D1", raw: 0, normalized: 70, itemCount: 10, theta: 0.8, se: 0.4 },
      ];
      const session = initCATSession("test-cat", bank, fixedScores);
      const d1 = session.dimensions.get("D1")!;
      expect(d1.priorMean).toBe(0.8);
      expect(d1.priorSD).toBe(0.4);
    });
  });

  describe("getNextItem", () => {
    it("returns an item from the first dimension", () => {
      const bank = makeBank();
      const session = initCATSession("test-cat", bank);
      const next = getNextItem(session);
      expect(next).not.toBeNull();
      expect(next!.dimensionId).toBe(session.dimensionOrder[0]);
    });

    it("returns null when session is complete", () => {
      const bank = makeBank();
      const session = initCATSession("test-cat", bank);
      const completeSession = { ...session, complete: true };
      expect(getNextItem(completeSession)).toBeNull();
    });

    it("returns updated session state", () => {
      const bank = makeBank();
      const session = initCATSession("test-cat", bank);
      const next = getNextItem(session);
      expect(next).not.toBeNull();
      expect(next!.session).toBeDefined();
      // Original session should not be mutated
      expect(session.currentDimensionIndex).toBe(0);
    });

    it("handles dimension exhaustion (all items administered)", () => {
      const bank = makeBank(); // 2 dims, 5 items each
      const stopping = { seThreshold: 0.01, minItems: 1, maxItems: 5 }; // Force all items
      let session = initCATSession("test-cat", bank, undefined, undefined, stopping);

      // Administer all items in both dimensions
      let count = 0;
      while (count < 10) {
        const next = getNextItem(session);
        if (!next) break;
        session = next.session;
        session = registerResponse(session, next.item.id, 3, stopping);
        count++;
      }

      // All items exhausted — getNextItem should return null
      const final = getNextItem(session);
      expect(final).toBeNull();
      expect(session.complete).toBe(true);
    });
  });

  describe("registerResponse", () => {
    it("updates theta and SE, returns new session", () => {
      const bank = makeBank();
      let session = initCATSession("test-cat", bank);
      const dimId = session.dimensionOrder[0]!;
      const initialSE = session.dimensions.get(dimId)!.se;

      const next = getNextItem(session)!;
      session = next.session;
      session = registerResponse(session, next.item.id, 3);

      const dim = session.dimensions.get(dimId)!;
      expect(dim.administered).toHaveLength(1);
      expect(dim.se).toBeLessThanOrEqual(initialSE);
      expect(session.totalItemsAdministered).toBe(1);
    });

    it("marks dimension complete at maxItems", () => {
      const bank = makeBank();
      const stopping = { ...DEFAULT_STOPPING, maxItems: 3, minItems: 1 };
      let session = initCATSession("test-cat", bank, undefined, undefined, stopping);
      const dimId = session.dimensionOrder[0]!;

      // Administer 3 items
      for (let i = 0; i < 3; i++) {
        const next = getNextItem(session);
        if (!next) break;
        session = next.session;
        session = registerResponse(session, next.item.id, 3, stopping);
      }

      const dim = session.dimensions.get(dimId)!;
      expect(dim.complete).toBe(true);
    });

    it("ignores duplicate item submissions", () => {
      const bank = makeBank();
      let session = initCATSession("test-cat", bank);

      const next = getNextItem(session)!;
      session = next.session;
      session = registerResponse(session, next.item.id, 3);
      expect(session.totalItemsAdministered).toBe(1);

      // Submit same item again — should be ignored
      const session2 = registerResponse(session, next.item.id, 4);
      expect(session2.totalItemsAdministered).toBe(1);
      expect(session2).toBe(session); // Same reference — no mutation
    });
  });

  describe("getCATProgress", () => {
    it("returns progress for all dimensions", () => {
      const bank = makeBank();
      const session = initCATSession("test-cat", bank);
      const progress = getCATProgress(session);
      expect(progress).toHaveLength(2);
      expect(progress[0]!.dimensionId).toBeDefined();
      expect(progress[0]!.se).toBeGreaterThan(0);
    });
  });

  describe("catSessionToScores", () => {
    it("converts session to ScaleScore array", () => {
      const bank = makeBank();
      let session = initCATSession("test-cat", bank);

      // Administer a few items
      for (let i = 0; i < 3; i++) {
        const next = getNextItem(session);
        if (!next) break;
        session = next.session;
        session = registerResponse(session, next.item.id, 3);
      }

      const scores = catSessionToScores(session);
      expect(scores).toHaveLength(2);
      for (const score of scores) {
        expect(score.theta).toBeDefined();
        expect(score.se).toBeDefined();
        expect(score.normalized).toBeGreaterThanOrEqual(0);
        expect(score.normalized).toBeLessThanOrEqual(100);
      }
    });

    it("includes fixed-form scores for skipped dimensions", () => {
      const bank = makeBank(); // 2 dims: D1, D2
      const fixedFormScores = [
        { scaleId: "D1", scaleName: "Dimension 1", raw: 0.5, normalized: 69.15,
          itemCount: 10, theta: 0.5, se: 0.2 },
      ];
      // D1 meets SE threshold (0.2 < 0.30), so CAT skips it
      const session = initCATSession("test-cat", bank, fixedFormScores);
      expect(session.dimensions.has("D1")).toBe(false);
      expect(session.dimensions.has("D2")).toBe(true);

      // Administer some D2 items
      let s = session;
      for (let i = 0; i < 3; i++) {
        const next = getNextItem(s);
        if (!next) break;
        s = next.session;
        s = registerResponse(s, next.item.id, 3);
      }

      // catSessionToScores should include both D2 (CAT) and D1 (fixed-form)
      const scores = catSessionToScores(s, fixedFormScores);
      const dimIds = scores.map(sc => sc.scaleId);
      expect(dimIds).toContain("D1");
      expect(dimIds).toContain("D2");

      // D1 score should be the fixed-form score passed through
      const d1Score = scores.find(sc => sc.scaleId === "D1")!;
      expect(d1Score.theta).toBe(0.5);
      expect(d1Score.se).toBe(0.2);
      expect(d1Score.scaleName).toBe("Dimension 1");
    });
  });

  describe("full session lifecycle", () => {
    it("completes when all dimensions reach stopping criteria", () => {
      const bank = makeBank();
      const stopping = { seThreshold: 0.30, minItems: 2, maxItems: 4 };
      let session = initCATSession("test-cat", bank, undefined, undefined, stopping);

      let iterations = 0;
      while (!session.complete && iterations < 20) {
        const next = getNextItem(session);
        if (!next) break;
        session = next.session;
        session = registerResponse(session, next.item.id, 2, stopping);
        iterations++;
      }

      expect(session.complete).toBe(true);
      expect(iterations).toBeLessThanOrEqual(8); // 4 max per dim * 2 dims
      expect(iterations).toBeGreaterThanOrEqual(4); // 2 min per dim * 2 dims
    });
  });
});
