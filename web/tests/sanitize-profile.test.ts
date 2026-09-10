import { describe, it, expect } from "vitest";
import { sanitizeImportedProfile } from "../src/components/sanitizeProfile";

describe("sanitizeImportedProfile (psy-8)", () => {
  it("clamps percentile scores to [0, 100]", () => {
    const out = sanitizeImportedProfile({
      big_five: {
        domains: {
          O: { final_score: 9999, ci_lower: -50, ci_upper: 1e9, divergence: 250 },
        },
      },
    }) as any;
    const d = out.big_five.domains.O;
    expect(d.final_score).toBe(100);
    expect(d.ci_lower).toBe(0);
    expect(d.ci_upper).toBe(100);
    // divergence is exempt (not a percentile score)
    expect(d.divergence).toBe(250);
  });

  it("leaves non-score numerics unclamped (version, crt_score, counts, theta, z)", () => {
    const out = sanitizeImportedProfile({
      version: 4,
      cognitive: { crt_score: 7 },
      metadata: { corpus_word_count: 1_470_000, llm_tokens_used: 999_999 },
      scores: { theta: -1.8, se: 0.42, z: -3.1 },
    }) as any;
    expect(out.version).toBe(4);
    expect(out.cognitive.crt_score).toBe(7);
    expect(out.metadata.corpus_word_count).toBe(1_470_000);
    expect(out.metadata.llm_tokens_used).toBe(999_999);
    expect(out.scores.theta).toBe(-1.8);
    expect(out.scores.se).toBe(0.42);
    expect(out.scores.z).toBe(-3.1);
  });

  it("coerces non-finite scores to 0", () => {
    const out = sanitizeImportedProfile({
      big_five: { domains: { N: { final_score: Number.POSITIVE_INFINITY } } },
    }) as any;
    expect(out.big_five.domains.N.final_score).toBe(0);
  });

  it("caps oversized strings", () => {
    const huge = "x".repeat(500_000);
    const out = sanitizeImportedProfile({ narrative: huge }) as any;
    expect(out.narrative.length).toBe(100_000);
  });

  it("caps oversized arrays", () => {
    const longArr = Array.from({ length: 10_000 }, (_, i) => `item-${i}`);
    const out = sanitizeImportedProfile({
      persona: { characteristic_phrases: longArr },
    }) as any;
    expect(out.persona.characteristic_phrases.length).toBe(2_000);
  });

  it("clamps scores inside arrays of objects (estimates)", () => {
    const out = sanitizeImportedProfile({
      big_five: {
        domains: {
          E: {
            final_score: 60,
            estimates: [
              { method: "self-report", score: 5000, evidence: ["a", "b"] },
              { method: "interview", score: -10, evidence: [] },
            ],
          },
        },
      },
    }) as any;
    const est = out.big_five.domains.E.estimates;
    expect(est[0].score).toBe(100);
    expect(est[1].score).toBe(0);
    // strings inside arrays preserved
    expect(est[0].evidence).toEqual(["a", "b"]);
  });

  it("preserves valid in-range data unchanged", () => {
    const profile = {
      version: 4,
      created_at: "2026-06-22",
      big_five: { domains: { A: { final_score: 73, ci_lower: 68, ci_upper: 78 } } },
      narrative: "A short narrative.",
    };
    const out = sanitizeImportedProfile(profile) as any;
    expect(out).toEqual(profile);
  });

  it("passes through booleans and null", () => {
    const out = sanitizeImportedProfile({ a: true, b: null, c: false }) as any;
    expect(out).toEqual({ a: true, b: null, c: false });
  });

  it("truncates pathologically deep nesting to null", () => {
    // Build 20 levels deep; beyond MAX_DEPTH (12) it becomes null.
    let nested: any = { score: 50 };
    for (let i = 0; i < 20; i++) nested = { child: nested };
    const out = sanitizeImportedProfile(nested) as any;
    // Walk down — at some point we hit null instead of an object.
    let cur = out;
    let hitNull = false;
    for (let i = 0; i < 20 && cur; i++) {
      if (cur.child === null) {
        hitNull = true;
        break;
      }
      cur = cur.child;
    }
    expect(hitNull).toBe(true);
  });
});
