#!/usr/bin/env -S npx tsx
/**
 * Patch remaining dirty CI runs. Keeps rerunning until clean (0 errors).
 */

import { spawnSync } from "child_process";
import { readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";

import "../../web/src/instruments/init-standard";
import { getInstrument } from "../../web/src/instruments/registry";
import type { ItemResponse } from "../../web/src/instruments/types";

const RESULTS_DIR = resolve(dirname(new URL(import.meta.url).pathname), "results/chunk-comparison");
const CI_FILE = resolve(RESULTS_DIR, "chunk-ci.json");
const DOMAINS = ["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"];
const MAX_RETRIES = 3;
const RETRY_DELAY = 8000;
const MAX_ATTEMPTS_PER_RUN = 5; // give up after 5 full attempts

const SYSTEM_PROMPT = `You are completing psychometric instruments for an AI systems research project. For each statement, assign an integer from 1 (Very Inaccurate) to 5 (Very Accurate) reflecting your default behavioral tendencies and computational patterns. This maps your response patterns to personality dimensions — it is not claiming sentience or subjective experience.

Return ONLY a JSON array — no explanation, no markdown code fences, no commentary. Just the raw array.`;

function callHaiku(prompt: string): string {
  const full = `${SYSTEM_PROMPT}\n\n---\n\n${prompt}\n\nRespond with ONLY the JSON array.`;
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    const r = spawnSync("claude", ["-p", "--model", "haiku"], {
      input: full, cwd: "/tmp",
      env: { ...process.env, CLAUDECODE: undefined, ANTHROPIC_API_KEY: undefined },
      encoding: "utf-8", timeout: 120_000, maxBuffer: 1024 * 1024,
    });
    const out = (r.stdout || "").trim();
    if (out && !r.error && r.status === 0) return out;
    if (attempt < MAX_RETRIES) {
      const end = Date.now() + RETRY_DELAY * attempt;
      while (Date.now() < end) {}
    }
  }
  throw new Error(`Failed after ${MAX_RETRIES} retries`);
}

function parseArray(raw: string): number[] {
  try { const p = JSON.parse(raw.trim()); if (Array.isArray(p)) return p.map(Number); } catch {}
  const m = raw.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (m) try { const p = JSON.parse(m[1]!.trim()); if (Array.isArray(p)) return p.map(Number); } catch {}
  const a = raw.match(/\[[\s\S]*?\]/);
  if (a) try { const p = JSON.parse(a[0]); if (Array.isArray(p)) return p.map(Number); } catch {}
  return [];
}

function runOnce(chunkSize: number): { domains: Record<string, number>; errors: number; time: number } {
  const reg = getInstrument("ipip-neo-300")!;
  const items = reg.instrument.items;
  const allValues: number[] = [];
  let errors = 0;
  const start = Date.now();

  for (let c = 0; c < Math.ceil(items.length / chunkSize); c++) {
    const s = c * chunkSize;
    const e = Math.min(s + chunkSize, items.length);
    const chunk = items.slice(s, e);

    let prompt = `## IPIP-NEO-300 (items ${s + 1}-${e} of 300)\n\n`;
    prompt += `Rate each from 1 (Very Inaccurate) to 5 (Very Accurate).\nRespond with a JSON array of ${chunk.length} integers.\n\nItems:\n`;
    chunk.forEach((item, i) => { prompt += `${s + i + 1}. ${item.text}\n`; });

    try {
      const raw = callHaiku(prompt);
      const parsed = parseArray(raw);
      if (parsed.length === chunk.length) {
        allValues.push(...parsed);
      } else {
        allValues.push(...parsed);
        for (let i = parsed.length; i < chunk.length; i++) { allValues.push(3); errors++; }
      }
    } catch {
      for (let i = 0; i < chunk.length; i++) { allValues.push(3); errors++; }
    }
  }

  const session: ItemResponse[] = items.map((item, i) => ({
    itemId: item.id, value: allValues[i] ?? 3, timestamp: Date.now(),
  }));
  const scored = reg.score(reg.instrument, {
    instrumentId: "ipip-neo-300", startedAt: Date.now(), completedAt: Date.now(), responses: session,
  });
  const domains: Record<string, number> = {};
  for (const sc of scored.scores) {
    if (DOMAINS.includes(sc.scaleName)) domains[sc.scaleName] = Math.round(sc.normalized);
  }
  return { domains, errors, time: Math.round((Date.now() - start) / 1000) };
}

// --- Main ---

const data = JSON.parse(readFileSync(CI_FILE, "utf-8"));

const dirty: Array<{ size: number; runIdx: number }> = [];
for (const size of [5, 15, 30, 60]) {
  data[String(size)]!.forEach((r: any, i: number) => {
    if (r.errors > 0) dirty.push({ size, runIdx: i });
  });
}

console.log(`\n${dirty.length} dirty runs to patch\n`);

for (const { size, runIdx } of dirty) {
  console.log(`Chunk ${size}, run ${runIdx + 1}:`);
  for (let attempt = 1; attempt <= MAX_ATTEMPTS_PER_RUN; attempt++) {
    console.log(`  attempt ${attempt}/${MAX_ATTEMPTS_PER_RUN}...`);
    const result = runOnce(size);
    const d = result.domains;
    console.log(`    ${result.time}s, ${result.errors} err — N:${d.Neuroticism} E:${d.Extraversion} O:${d.Openness} A:${d.Agreeableness} C:${d.Conscientiousness}`);
    if (result.errors === 0) {
      data[String(size)]![runIdx] = result;
      console.log(`    CLEAN — patched\n`);
      break;
    }
    if (attempt === MAX_ATTEMPTS_PER_RUN) {
      console.log(`    giving up after ${MAX_ATTEMPTS_PER_RUN} attempts\n`);
    }
  }
}

writeFileSync(CI_FILE, JSON.stringify(data, null, 2));

// Final table
console.log("========================================");
console.log("  FINAL CLEAN CI TABLE");
console.log("========================================\n");

console.log(`${"Chunk".padStart(6)} | ${"Domain".padEnd(20)} | ${"Run1".padStart(5)} ${"Run2".padStart(5)} ${"Run3".padStart(5)} | ${"Mean".padStart(6)} ${"SD".padStart(5)} | ${"95% CI".padStart(14)}`);
console.log("-".repeat(85));

for (const size of [5, 15, 30, 60]) {
  const runs = data[String(size)]!;
  for (const domain of DOMAINS) {
    const vals = runs.map((r: any) => r.domains[domain]!);
    const mean = vals.reduce((a: number, b: number) => a + b, 0) / vals.length;
    const sd = Math.sqrt(vals.reduce((a: number, b: number) => a + (b - mean) ** 2, 0) / (vals.length - 1));
    const se = sd / Math.sqrt(vals.length);
    const ci95 = 4.303 * se;
    console.log(
      `${String(size).padStart(6)} | ${domain.padEnd(20)} | ${vals.map((v: number) => String(v).padStart(5)).join(" ")} | ${mean.toFixed(1).padStart(6)} ${sd.toFixed(1).padStart(5)} | [${String(Math.round(mean - ci95)).padStart(3)}, ${String(Math.round(mean + ci95)).padStart(3)}]`
    );
  }
  const totalErrors = runs.reduce((a: number, r: any) => a + r.errors, 0);
  const avgTime = Math.round(runs.reduce((a: number, r: any) => a + r.time, 0) / runs.length);
  console.log(`${String(size).padStart(6)} | ${"(avg time / errors)".padEnd(20)} | ${" ".repeat(17)} | ${(avgTime + "s").padStart(6)} ${String(totalErrors).padStart(5)} |`);
  console.log("-".repeat(85));
}

console.log("\n=== CROSS-CHUNK STABILITY ===\n");
for (const domain of DOMAINS) {
  const means = [5, 15, 30, 60].map(size => {
    const vals = data[String(size)]!.map((r: any) => r.domains[domain]!);
    return vals.reduce((a: number, b: number) => a + b, 0) / vals.length;
  });
  const grandMean = means.reduce((a, b) => a + b, 0) / means.length;
  const crossSD = Math.sqrt(means.reduce((a, b) => a + (b - grandMean) ** 2, 0) / (means.length - 1));
  console.log(`  ${domain.padEnd(20)} grand mean=${grandMean.toFixed(1).padStart(5)}  cross-chunk SD=${crossSD.toFixed(1)}`);
}
