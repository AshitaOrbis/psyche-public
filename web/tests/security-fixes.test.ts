/**
 * Regression tests for the 2026-06-11 security/correctness review fixes.
 *
 * Covers: reverse-keyed CAT scoring (P0-1), hard item-bank validation (P0-2),
 * fixed-form prior seeding (P1-3), fixed-form item exclusion (P1-4),
 * auto-scoring exact coverage (P1-5), import validation (P1-6), and
 * CAT score provenance / domain aggregation (P1-7).
 */
import { describe, it, expect, beforeEach } from "vitest";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { GRMItem } from "../src/scoring/grm-engine";
import { estimateTheta, inverseNormalCDF, thetaToPercentile } from "../src/scoring/grm-engine";
import {
  initCATSession,
  getNextItem,
  registerResponse,
  catSessionToScores,
  validateCATBankOrThrow,
  fixedFormPrior,
} from "../src/scoring/cat-controller";
import { scoreAdaptive } from "../src/scoring/engine";
import { usePsycheStore } from "../src/state/store";
import { getInstrument } from "../src/instruments/registry";

// Register the full instrument battery (side-effect import)
import "../src/instruments/init";

function makeItem(overrides: Partial<GRMItem> = {}): GRMItem {
  return {
    id: "T-1",
    text: "I often feel anxious.",
    discrimination: 1.5,
    thresholds: [-1.5, -0.5, 0.5, 1.5],
    numCategories: 5,
    dimensionId: "D1",
    reverse: false,
    ...overrides,
  };
}

function makeBank(dims: string[] = ["D1", "D2"], reverseEvery?: number): GRMItem[] {
  const items: GRMItem[] = [];
  for (const dim of dims) {
    for (let i = 0; i < 5; i++) {
      items.push(
        makeItem({
          id: `${dim}-${i}`,
          text: `Real item text ${dim}-${i}.`,
          discrimination: 1.2 + i * 0.1,
          dimensionId: dim,
          reverse: reverseEvery !== undefined && i % reverseEvery === 0,
        }),
      );
    }
  }
  return items;
}

// ── P0-1: reverse-keyed items must be flipped before GRM scoring ──

describe("P0-1: reverse-keyed CAT scoring", () => {
  it("estimateTheta direction sanity (non-reverse): high category -> higher theta", () => {
    const item = makeItem();
    const hi = estimateTheta([item], [{ itemId: item.id, category: 4 }]);
    const lo = estimateTheta([item], [{ itemId: item.id, category: 0 }]);
    expect(hi.theta).toBeGreaterThan(lo.theta);
  });

  it("registerResponse flips the category for reverse items", () => {
    const reverseItem = makeItem({ id: "R-1", reverse: true });
    const normalItem = makeItem({ id: "N-1", reverse: false });
    const bank = [reverseItem, normalItem];

    // "Very Accurate" (category 4) on a reverse-keyed item must LOWER theta
    let s = initCATSession("t", [reverseItem]);
    s = registerResponse(s, "R-1", 4);
    const reverseTheta = s.dimensions.get("D1")!.theta;

    let s2 = initCATSession("t", [normalItem]);
    s2 = registerResponse(s2, "N-1", 4);
    const normalTheta = s2.dimensions.get("D1")!.theta;

    expect(reverseTheta).toBeLessThan(0);
    expect(normalTheta).toBeGreaterThan(0);
    // Symmetric items: flipped response should mirror the estimate
    expect(reverseTheta).toBeCloseTo(-normalTheta, 6);

    // Stored response holds the SCORED (flipped) category
    let s3 = initCATSession("t", bank);
    s3 = registerResponse(s3, "R-1", 4);
    const stored = s3.dimensions.get("D1")!.administered.find((r) => r.itemId === "R-1")!;
    expect(stored.category).toBe(0);
  });

  it("clamps out-of-range categories", () => {
    const item = makeItem();
    let s = initCATSession("t", [item]);
    s = registerResponse(s, item.id, 99);
    const stored = s.dimensions.get("D1")!.administered[0]!;
    expect(stored.category).toBe(4);
  });
});

// ── P0-2: hard item bank validation ──

describe("P0-2: validateCATBankOrThrow", () => {
  it("accepts a well-formed bank", () => {
    expect(() => validateCATBankOrThrow(makeBank())).not.toThrow();
  });

  it("rejects placeholder item text", () => {
    const bank = [makeItem({ text: "[Anxiety item 1]" })];
    expect(() => validateCATBankOrThrow(bank)).toThrow(/Placeholder/);
  });

  it("rejects empty banks", () => {
    expect(() => validateCATBankOrThrow([])).toThrow(/empty/);
  });

  it("rejects non-positive or non-finite discrimination", () => {
    expect(() => validateCATBankOrThrow([makeItem({ discrimination: 0 })])).toThrow(/discrimination/i);
    expect(() => validateCATBankOrThrow([makeItem({ discrimination: NaN })])).toThrow(/discrimination/i);
  });

  it("rejects threshold/category mismatch", () => {
    expect(() => validateCATBankOrThrow([makeItem({ thresholds: [-1, 0] })])).toThrow(/mismatch/i);
  });

  it("rejects non-finite and unordered thresholds", () => {
    expect(() => validateCATBankOrThrow([makeItem({ thresholds: [-1, 0, NaN, 1] })])).toThrow(/Non-finite/);
    expect(() => validateCATBankOrThrow([makeItem({ thresholds: [1, 0, -1, -2] })])).toThrow(/Unordered/);
  });

  it("REJECTS the shipped synthetic item banks (placeholder text)", () => {
    for (const file of ["big5-grm-params.json", "hexaco-grm-params.json"]) {
      const bank = JSON.parse(
        readFileSync(join(__dirname, "..", "public", "item-banks", file), "utf-8"),
      ) as GRMItem[];
      expect(() => validateCATBankOrThrow(bank)).toThrow(/Placeholder/);
    }
  });
});

// ── P1-3: fixed-form priors are seeded even without calibrated theta/se ──

describe("P1-3: fixed-form prior seeding", () => {
  it("inverseNormalCDF matches known quantiles", () => {
    expect(inverseNormalCDF(0.5)).toBeCloseTo(0, 8);
    expect(inverseNormalCDF(0.975)).toBeCloseTo(1.959964, 4);
    expect(inverseNormalCDF(0.025)).toBeCloseTo(-1.959964, 4);
    // Round-trips with thetaToPercentile
    expect(thetaToPercentile(inverseNormalCDF(0.7))).toBeCloseTo(70, 1);
  });

  it("uses calibrated theta/se directly when present", () => {
    const prior = fixedFormPrior({
      scaleId: "D1", scaleName: "D1", raw: 0, normalized: 69,
      itemCount: 10, theta: 0.5, se: 0.25,
    });
    expect(prior).toEqual({ theta: 0.5, se: 0.25, calibrated: true });
  });

  it("derives an approximate prior from normalized percentile otherwise", () => {
    const prior = fixedFormPrior({
      scaleId: "D1", scaleName: "D1", raw: 4.0, normalized: 84, itemCount: 10,
    })!;
    expect(prior.calibrated).toBe(false);
    expect(prior.theta).toBeCloseTo(inverseNormalCDF(0.84), 8);
    expect(prior.theta).toBeGreaterThan(0.9);
    // Conservative SE: never tight enough to trip the skip shortcut (0.30)
    expect(prior.se).toBeGreaterThanOrEqual(0.55);
  });

  it("initCATSession seeds priors from theta-less fixed-form scores", () => {
    const bank = makeBank(["D1", "D2"]);
    const fixedScores = [
      { scaleId: "D1", scaleName: "D1", raw: 4.2, normalized: 90, itemCount: 10 },
    ];
    const session = initCATSession("t", bank, fixedScores);
    const d1 = session.dimensions.get("D1")!;
    expect(d1.priorMean).toBeGreaterThan(1.0); // ~Φ⁻¹(0.90) = 1.28
    expect(d1.priorSD).toBeGreaterThanOrEqual(0.55);
    // D2 had no fixed-form score: default prior
    const d2 = session.dimensions.get("D2")!;
    expect(d2.priorMean).toBe(0);
    expect(d2.priorSD).toBe(1);
    // Approximate priors never cause a dimension to be skipped
    expect(session.dimensionOrder).toContain("D1");
  });

  it("approximate priors do not skip dimensions even at extreme percentiles", () => {
    const bank = makeBank(["D1"]);
    const fixedScores = [
      { scaleId: "D1", scaleName: "D1", raw: 5, normalized: 99.9, itemCount: 300 },
    ];
    const session = initCATSession("t", bank, fixedScores);
    expect(session.dimensionOrder).toContain("D1");
  });
});

// ── P1-4: fixed-form item exclusion ──

describe("P1-4: fixed-form item exclusion", () => {
  it("excluded item IDs never enter the CAT pool", () => {
    const bank = makeBank(["D1"]);
    const excluded = new Set(["D1-0", "D1-1"]);
    const session = initCATSession("t", bank, undefined, excluded);
    expect(session.itemIndex.has("D1-0")).toBe(false);
    expect(session.itemIndex.has("D1-1")).toBe(false);
    expect(session.dimensionItems.get("D1")).toHaveLength(3);

    // Exhaust the dimension: no excluded item is ever returned
    let s = session;
    const administered: string[] = [];
    for (;;) {
      const next = getNextItem(s);
      if (!next) break;
      s = registerResponse(next.session, next.item.id, 2);
      administered.push(next.item.id);
      if (administered.length > 10) break;
    }
    for (const id of administered) {
      expect(excluded.has(id)).toBe(false);
    }
  });
});

// ── P1-7: provenance + domain aggregation ──

describe("P1-7: CAT score provenance and domain aggregation", () => {
  function runMiniCAT(dims: string[]): ReturnType<typeof initCATSession> {
    const bank = makeBank(dims);
    let s = initCATSession("t", bank);
    for (let i = 0; i < dims.length * 3; i++) {
      const next = getNextItem(s);
      if (!next) break;
      s = registerResponse(next.session, next.item.id, 3);
    }
    return s;
  }

  it("tags CAT scores with source 'cat' and carryovers with 'fixed-form'", () => {
    const s = runMiniCAT(["D1"]);
    const fixedFormScores = [
      { scaleId: "OTHER", scaleName: "Other Scale", raw: 3, normalized: 60, itemCount: 12 },
    ];
    const scores = catSessionToScores(s, fixedFormScores);
    expect(scores.find((sc) => sc.scaleId === "D1")!.source).toBe("cat");
    expect(scores.find((sc) => sc.scaleId === "OTHER")!.source).toBe("fixed-form");
  });

  it("computes domain scores from CAT facets via inverse-variance weighting", () => {
    const s = runMiniCAT(["N1", "N2"]);
    const facetParents = new Map([["N1", "N"], ["N2", "N"]]);
    const scores = catSessionToScores(s, undefined, facetParents);

    const domain = scores.find((sc) => sc.scaleId === "N")!;
    expect(domain).toBeDefined();
    expect(domain.source).toBe("cat");

    const n1 = scores.find((sc) => sc.scaleId === "N1")!;
    const n2 = scores.find((sc) => sc.scaleId === "N2")!;
    const w1 = 1 / (n1.se! * n1.se!);
    const w2 = 1 / (n2.se! * n2.se!);
    const expected = (n1.theta! * w1 + n2.theta! * w2) / (w1 + w2);
    expect(domain.theta).toBeCloseTo(expected, 8);
    expect(domain.se).toBeCloseTo(Math.sqrt(1 / (w1 + w2)), 8);
  });

  it("does NOT inherit fixed-form domain scores when CAT aggregates the domain", () => {
    const s = runMiniCAT(["N1", "N2"]);
    const facetParents = new Map([["N1", "N"], ["N2", "N"]]);
    const fixedFormScores = [
      { scaleId: "N", scaleName: "Neuroticism", raw: 2, normalized: 25, itemCount: 60 },
    ];
    const scores = catSessionToScores(s, fixedFormScores, facetParents);
    const nScores = scores.filter((sc) => sc.scaleId === "N");
    expect(nScores).toHaveLength(1);
    expect(nScores[0]!.source).toBe("cat");
    // Aggregate must come from CAT facets (theta ~> 0 for category-3 answers),
    // not the contradictory fixed-form 25th percentile
    expect(nScores[0]!.normalized).not.toBeCloseTo(25, 0);
  });

  it("scoreAdaptive resolves scale names and parents from the registry", () => {
    const bank = makeBank(["N1", "N2"]);
    let s = initCATSession("cat-big5", bank);
    for (let i = 0; i < 6; i++) {
      const next = getNextItem(s);
      if (!next) break;
      s = registerResponse(next.session, next.item.id, 3);
    }
    const result = scoreAdaptive("cat-big5", s);
    const n1 = result.scores.find((sc) => sc.scaleId === "N1")!;
    expect(n1.scaleName).toBe("Anxiety");
    const domain = result.scores.find((sc) => sc.scaleId === "N");
    expect(domain).toBeDefined();
    expect(domain!.scaleName).toBe("Neuroticism");
    expect(domain!.source).toBe("cat");
  });
});

// ── P1-5 / P1-6: store auto-scoring and import validation ──

describe("P1-5/P1-6: store import validation and auto-scoring", () => {
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

  function importJSON(payload: unknown): void {
    usePsycheStore.getState().importData(JSON.stringify(payload));
  }

  it("rejects payloads without object sessions/results", () => {
    expect(() => importJSON({ sessions: null, results: {} })).toThrow();
    expect(() => importJSON({ sessions: {}, results: [] })).toThrow();
    expect(() => importJSON("just a string")).toThrow();
  });

  it("does not throw on sessions with responses: null (drops them)", () => {
    importJSON({
      sessions: { "rosenberg": { instrumentId: "rosenberg", startedAt: 1, responses: null } },
      results: {},
    });
    expect(usePsycheStore.getState().sessions["rosenberg"]).toBeUndefined();
  });

  it("drops sessions and results for unknown instruments", () => {
    importJSON({
      sessions: { "not-an-instrument": { instrumentId: "not-an-instrument", startedAt: 1, responses: [] } },
      results: { "not-an-instrument": { instrumentId: "not-an-instrument", completedAt: 1, scores: [] } },
    });
    const state = usePsycheStore.getState();
    expect(state.sessions["not-an-instrument"]).toBeUndefined();
    expect(state.results["not-an-instrument"]).toBeUndefined();
  });

  it("junk response IDs do NOT mint a completed result (exact coverage required)", () => {
    const reg = getInstrument("rosenberg")!;
    const junkResponses = Array.from({ length: reg.instrument.items.length }, (_, i) => ({
      itemId: `junk-${i}`,
      value: 3,
      timestamp: Date.now(),
    }));
    importJSON({
      sessions: { rosenberg: { instrumentId: "rosenberg", startedAt: 1, responses: junkResponses } },
      results: {},
    });
    expect(usePsycheStore.getState().results["rosenberg"]).toBeUndefined();
  });

  it("valid full sessions are auto-scored on import", () => {
    const reg = getInstrument("rosenberg")!;
    const responses = reg.instrument.items.map((item) => ({
      itemId: item.id,
      value: item.response.type === "likert" ? item.response.min : 0,
      timestamp: Date.now(),
    }));
    importJSON({
      sessions: { rosenberg: { instrumentId: "rosenberg", startedAt: 1, responses } },
      results: {},
    });
    const result = usePsycheStore.getState().results["rosenberg"];
    expect(result).toBeDefined();
    expect(result!.scores.length).toBeGreaterThan(0);
  });

  it("out-of-range likert values are rejected during import", () => {
    const reg = getInstrument("rosenberg")!;
    const responses = reg.instrument.items.map((item) => ({
      itemId: item.id,
      value: 9999,
      timestamp: Date.now(),
    }));
    importJSON({
      sessions: { rosenberg: { instrumentId: "rosenberg", startedAt: 1, responses } },
      results: {},
    });
    const state = usePsycheStore.getState();
    // Responses dropped; no result minted
    expect(state.sessions["rosenberg"]!.responses).toHaveLength(0);
    expect(state.results["rosenberg"]).toBeUndefined();
  });

  // The two cases below used to assert that a fixed-form result survived
  // import with its normalized value clamped and its bad theta/se stripped —
  // for an instrument with no responses behind it at all. The 2026-08-16
  // review named that as the defect: a serialized result object was trusted
  // far more than the downstream profile code assumes. Fixed-form results are
  // now recomputed from responses, so a result with none is dropped. Clamping
  // and theta/se validation moved to the result-only (adaptive) path and are
  // covered in tests/import-result-integrity.test.ts.

  it("does not mint a fixed-form result from serialized scores alone", () => {
    importJSON({
      sessions: {},
      results: {
        rosenberg: {
          instrumentId: "rosenberg",
          completedAt: Date.now(),
          scores: [
            { scaleId: "self-esteem", scaleName: "Self-Esteem", raw: 2.5, normalized: 250, itemCount: 10 },
            { scaleId: "bad", scaleName: "Bad", raw: NaN, normalized: 50, itemCount: 10 },
            { scaleId: "", scaleName: "Empty", raw: 1, normalized: 50, itemCount: 10 },
          ],
        },
      },
    });
    expect(usePsycheStore.getState().results["rosenberg"]).toBeUndefined();
  });

  it("does not keep a theta/se-bearing result for an unanswered fixed-form instrument", () => {
    importJSON({
      sessions: {},
      results: {
        rosenberg: {
          instrumentId: "rosenberg",
          completedAt: Date.now(),
          scores: [
            { scaleId: "self-esteem", scaleName: "SE", raw: 2, normalized: 50, itemCount: 10, theta: 0.5, se: -1 },
          ],
        },
      },
    });
    expect(usePsycheStore.getState().results["rosenberg"]).toBeUndefined();
  });

  it("does not auto-score adaptive instruments (no empty CAT results minted)", () => {
    importJSON({
      sessions: { "cat-big5": { instrumentId: "cat-big5", startedAt: 1, responses: [] } },
      results: {},
    });
    expect(usePsycheStore.getState().results["cat-big5"]).toBeUndefined();
  });
});
