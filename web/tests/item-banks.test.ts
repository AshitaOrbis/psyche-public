import { describe, it, expect } from "vitest";
import type { GRMItem } from "../src/scoring/grm-engine";
import big5Bank from "../public/item-banks/big5-grm-params.json";
import hexacoBank from "../public/item-banks/hexaco-grm-params.json";

function assertGRMItem(item: unknown, index: number): void {
  const obj = item as Record<string, unknown>;
  expect(obj.id, `item[${index}].id`).toBeTypeOf("string");
  expect(obj.text, `item[${index}].text`).toBeTypeOf("string");
  expect(obj.discrimination, `item[${index}].discrimination`).toBeTypeOf("number");
  expect(obj.thresholds, `item[${index}].thresholds`).toBeInstanceOf(Array);
  expect(obj.numCategories, `item[${index}].numCategories`).toBeTypeOf("number");
  expect(obj.dimensionId, `item[${index}].dimensionId`).toBeTypeOf("string");

  const grm = obj as unknown as GRMItem;
  expect(grm.discrimination).toBeGreaterThan(0);
  expect(grm.thresholds.length).toBe(grm.numCategories - 1);
  // Thresholds should be ordered
  for (let i = 1; i < grm.thresholds.length; i++) {
    expect(grm.thresholds[i]).toBeGreaterThanOrEqual(grm.thresholds[i - 1]!);
  }
}

describe("Item Bank JSON Schema", () => {
  it("big5-grm-params.json matches GRMItem interface", () => {
    expect(big5Bank.length).toBeGreaterThan(0);
    for (let i = 0; i < big5Bank.length; i++) {
      assertGRMItem(big5Bank[i], i);
    }
  });

  it("hexaco-grm-params.json matches GRMItem interface", () => {
    expect(hexacoBank.length).toBeGreaterThan(0);
    for (let i = 0; i < hexacoBank.length; i++) {
      assertGRMItem(hexacoBank[i], i);
    }
  });

  it("big5 bank has no legacy itemId/itemText fields", () => {
    for (const item of big5Bank) {
      const obj = item as Record<string, unknown>;
      expect(obj).not.toHaveProperty("itemId");
      expect(obj).not.toHaveProperty("itemText");
    }
  });

  it("hexaco bank has no legacy itemId/itemText fields", () => {
    for (const item of hexacoBank) {
      const obj = item as Record<string, unknown>;
      expect(obj).not.toHaveProperty("itemId");
      expect(obj).not.toHaveProperty("itemText");
    }
  });
});
