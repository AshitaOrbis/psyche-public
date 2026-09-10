import { describe, it, expect } from "vitest";
import "../src/instruments/init";
import { getInstrumentsForTier } from "../src/instruments/tiers";
import { getInstrument } from "../src/instruments/registry";

describe("Tier configuration", () => {
  it("lite tier has 15 instruments", () => {
    const ids = getInstrumentsForTier("lite");
    expect(ids).toHaveLength(15);
    expect(ids).toContain("ipip-neo-60");
    expect(ids).toContain("crt-7");
    expect(ids).toContain("open-ended");
    // Should NOT contain standard/heavy instruments
    expect(ids).not.toContain("ipip-neo-300");
    expect(ids).not.toContain("ipip-neo-120");
    expect(ids).not.toContain("hexaco-60");
    expect(ids).not.toContain("hexaco-200");
  });

  it("standard tier has 20 instruments", () => {
    const ids = getInstrumentsForTier("standard");
    expect(ids).toHaveLength(20);
    // NEO-60 replaced by NEO-300
    expect(ids).not.toContain("ipip-neo-60");
    expect(ids).toContain("ipip-neo-300");
    // HEXACO-60 added
    expect(ids).toContain("hexaco-60");
    // Phase 6 Standard additions
    expect(ids).toContain("swls");
    expect(ids).toContain("aaq-ii");
    expect(ids).toContain("dweck-itis");
    expect(ids).toContain("cei-ii");
    // Lite instruments still present
    expect(ids).toContain("crt-7");
    expect(ids).toContain("grit-s");
    expect(ids).toContain("open-ended");
  });

  it("heavy tier has correct instruments with replacements", () => {
    const ids = getInstrumentsForTier("heavy");
    // NEO-120 added alongside NEO-300 (not replacing)
    expect(ids).toContain("ipip-neo-120");
    expect(ids).toContain("ipip-neo-300");
    // HEXACO-60 replaced by HEXACO-200
    expect(ids).not.toContain("hexaco-60");
    expect(ids).toContain("hexaco-200");
    // Extended instruments replaced by longer forms
    expect(ids).not.toContain("grit-s");
    expect(ids).toContain("grit-o");
    expect(ids).not.toContain("bpns-9");
    expect(ids).toContain("bpns-21");
    expect(ids).not.toContain("loc-ie4");
    expect(ids).toContain("levenson-ipc-24");
    expect(ids).not.toContain("self-monitoring-18");
    expect(ids).toContain("snyder-sm-25");
    // CAT instruments (Heavy only)
    expect(ids).toContain("cat-big5");
    expect(ids).toContain("cat-hexaco");
    // Phase 6 Heavy additions
    expect(ids).toContain("aot-13");
    expect(ids).toContain("ius-12");
    expect(ids).toContain("scs-26");
    expect(ids).toContain("mfq-2");
    expect(ids).toContain("frost-mps");
    expect(ids).toContain("maas");
    expect(ids).toContain("authenticity");
    expect(ids).toContain("tangney-scs");
    expect(ids).toContain("maximization");
    expect(ids).toContain("ztpi");
    // Standard instruments carry through
    expect(ids).toContain("swls");
    expect(ids).toContain("aaq-ii");
    expect(ids).toContain("dweck-itis");
    expect(ids).toContain("cei-ii");
    // Lite instruments that aren't replaced persist
    expect(ids).toContain("crt-7");
    expect(ids).toContain("open-ended");
  });

  it("all tier instruments are registered", () => {
    for (const tier of ["lite", "standard", "heavy"] as const) {
      const ids = getInstrumentsForTier(tier);
      for (const id of ids) {
        const registered = getInstrument(id);
        expect(registered, `Instrument ${id} should be registered (tier: ${tier})`).toBeDefined();
      }
    }
  });

  it("tiers are additive (standard includes lite instruments)", () => {
    const lite = getInstrumentsForTier("lite");
    const standard = getInstrumentsForTier("standard");
    // All lite instruments that aren't replaced should be in standard
    for (const id of lite) {
      if (id !== "ipip-neo-60") {
        // NEO-60 is replaced by NEO-300
        expect(standard, `${id} from lite should be in standard`).toContain(id);
      }
    }
  });
});
