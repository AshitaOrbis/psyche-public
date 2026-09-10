import { describe, it, expect } from "vitest";
import {
  categoryProbability,
  categoryProbabilities,
  itemInformation,
  estimateTheta,
  thetaToPercentile,
  selectNextItem,
  type GRMItem,
  type CATResponse,
} from "../src/scoring/grm-engine";

// Standard test item with typical personality-scale parameters
const testItem: GRMItem = {
  id: "test-001",
  text: "I am the life of the party.",
  discrimination: 1.5,
  thresholds: [-1.5, -0.5, 0.5, 1.5],
  numCategories: 5,
  dimensionId: "E1",
};

describe("GRM Engine", () => {
  describe("categoryProbability", () => {
    it("probabilities sum to 1", () => {
      const thetas = [-2, -1, 0, 1, 2];
      for (const theta of thetas) {
        let sum = 0;
        for (let k = 0; k < testItem.numCategories; k++) {
          sum += categoryProbability(testItem, theta, k);
        }
        expect(sum).toBeCloseTo(1.0, 4);
      }
    });

    it("extreme low theta favors lowest category", () => {
      const p0 = categoryProbability(testItem, -4, 0);
      const p4 = categoryProbability(testItem, -4, 4);
      expect(p0).toBeGreaterThan(0.9);
      expect(p4).toBeLessThan(0.01);
    });

    it("extreme high theta favors highest category", () => {
      const p0 = categoryProbability(testItem, 4, 0);
      const p4 = categoryProbability(testItem, 4, 4);
      expect(p0).toBeLessThan(0.01);
      expect(p4).toBeGreaterThan(0.9);
    });

    it("theta at threshold shifts modal category", () => {
      // At theta = b2 (-0.5), categories 0+1 should dominate over 3+4
      const probs = categoryProbabilities(testItem, -0.5);
      const lowerSum = probs[0]! + probs[1]!;
      const upperSum = probs[3]! + probs[4]!;
      expect(lowerSum).toBeGreaterThan(upperSum);
    });
  });

  describe("categoryProbabilities", () => {
    it("returns array of correct length", () => {
      const probs = categoryProbabilities(testItem, 0);
      expect(probs).toHaveLength(5);
    });

    it("normalized probabilities sum to 1", () => {
      const probs = categoryProbabilities(testItem, 0.7);
      const sum = probs.reduce((a, b) => a + b, 0);
      expect(sum).toBeCloseTo(1.0, 6);
    });
  });

  describe("itemInformation", () => {
    it("information is non-negative", () => {
      for (const theta of [-3, -1, 0, 1, 3]) {
        expect(itemInformation(testItem, theta)).toBeGreaterThanOrEqual(0);
      }
    });

    it("higher discrimination gives more information", () => {
      const lowDisc: GRMItem = { ...testItem, discrimination: 0.5 };
      const highDisc: GRMItem = { ...testItem, discrimination: 2.0 };
      expect(itemInformation(highDisc, 0)).toBeGreaterThan(itemInformation(lowDisc, 0));
    });

    it("information peaks near thresholds", () => {
      // Information should be higher near thresholds than at extremes
      const infoCenter = itemInformation(testItem, 0);
      const infoExtreme = itemInformation(testItem, 4);
      expect(infoCenter).toBeGreaterThan(infoExtreme);
    });
  });

  describe("estimateTheta", () => {
    it("returns prior with no responses", () => {
      const result = estimateTheta([], [], 0.5, 1.0);
      expect(result.theta).toBe(0.5);
      expect(result.se).toBe(1.0);
    });

    it("high responses increase theta estimate", () => {
      const items = [testItem];
      const responses: CATResponse[] = [{ itemId: "test-001", category: 4 }];
      const result = estimateTheta(items, responses);
      expect(result.theta).toBeGreaterThan(0);
    });

    it("low responses decrease theta estimate", () => {
      const items = [testItem];
      const responses: CATResponse[] = [{ itemId: "test-001", category: 0 }];
      const result = estimateTheta(items, responses);
      expect(result.theta).toBeLessThan(0);
    });

    it("more items reduce SE", () => {
      const items: GRMItem[] = Array.from({ length: 5 }, (_, i) => ({
        ...testItem,
        id: `item-${i}`,
      }));
      const responses1: CATResponse[] = [{ itemId: "item-0", category: 3 }];
      const responses5: CATResponse[] = items.map((item) => ({
        itemId: item.id,
        category: 3,
      }));

      const result1 = estimateTheta(items.slice(0, 1), responses1);
      const result5 = estimateTheta(items, responses5);
      expect(result5.se).toBeLessThan(result1.se);
    });

    it("converges toward true theta with enough items", () => {
      // Simulate respondent with true theta = 1.0
      const trueTheta = 1.0;
      const items: GRMItem[] = Array.from({ length: 12 }, (_, i) => ({
        ...testItem,
        id: `conv-${i}`,
        // Vary discrimination slightly
        discrimination: 1.2 + Math.random() * 0.6,
      }));

      // Generate "expected" responses for theta=1.0
      // At theta=1.0 with thresholds [-1.5,-0.5,0.5,1.5], category 3 is most likely
      const responses: CATResponse[] = items.map((item) => ({
        itemId: item.id,
        category: 3, // Consistently high response
      }));

      const result = estimateTheta(items, responses);
      // Should be within ~0.5 of true theta with 12 items
      expect(Math.abs(result.theta - trueTheta)).toBeLessThan(0.5);
    });
  });

  describe("thetaToPercentile", () => {
    it("theta=0 maps to 50th percentile", () => {
      expect(thetaToPercentile(0)).toBe(50);
    });

    it("theta=1 maps to ~84th percentile", () => {
      const p = thetaToPercentile(1.0);
      expect(p).toBeGreaterThan(83);
      expect(p).toBeLessThan(85);
    });

    it("theta=-1 maps to ~16th percentile", () => {
      const p = thetaToPercentile(-1.0);
      expect(p).toBeGreaterThan(15);
      expect(p).toBeLessThan(17);
    });

    it("extremes clamp to 0 and 100", () => {
      expect(thetaToPercentile(-7)).toBe(0);
      expect(thetaToPercentile(7)).toBe(100);
    });

    it("is approximately symmetric", () => {
      const pos = thetaToPercentile(1.5);
      const neg = thetaToPercentile(-1.5);
      expect(Math.abs(pos + neg - 100)).toBeLessThan(0.5);
    });
  });

  describe("selectNextItem", () => {
    it("selects most informative item", () => {
      const bank: GRMItem[] = [
        { ...testItem, id: "low", discrimination: 0.5 },
        { ...testItem, id: "high", discrimination: 2.0 },
      ];
      const result = selectNextItem(bank, 0, new Set());
      expect(result?.id).toBe("high");
    });

    it("excludes administered items", () => {
      const bank: GRMItem[] = [
        { ...testItem, id: "a", discrimination: 2.0 },
        { ...testItem, id: "b", discrimination: 1.0 },
      ];
      const result = selectNextItem(bank, 0, new Set(["a"]));
      expect(result?.id).toBe("b");
    });

    it("returns null when all items administered", () => {
      const bank: GRMItem[] = [{ ...testItem, id: "only" }];
      const result = selectNextItem(bank, 0, new Set(["only"]));
      expect(result).toBeNull();
    });
  });
});
