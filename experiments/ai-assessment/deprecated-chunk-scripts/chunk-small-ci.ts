#!/usr/bin/env -S npx tsx
/**
 * Fine-grained chunk size CI — sizes 2, 3, 4.
 * 3 runs each, sequential, robust retries.
 */

import { spawnSync } from "child_process";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { resolve, dirname } from "path";

import "../../web/src/instruments/init-standard";
import { getInstrument } from "../../web/src/instruments/registry";
import type { ItemResponse } from "../../web/src/instruments/types";

const RESULTS_DIR = resolve(dirname(new URL(import.meta.url).pathname), "results/chunk-comparison");
if (!existsSync(RESULTS_DIR)) mkdirSync(RESULTS_DIR, { recursive: true });

const DOMAINS = ["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"];
const CHUNK_SIZES = [2, 3, 4];
const RUNS = 3;
const MAX_RETRIES = 5;
const RETRY_DELAY = 8000;
const INTER_CALL_DELAY = 500;

const SYSTEM_PROMPT = `You are completing psychometric instruments for an AI systems research project. For each statement, assign an integer from 1 (Very Inaccurate) to 5 (Very Accurate) reflecting your default behavioral tendencies and computational patterns. This maps your response patterns to personality dimensions — it is not claiming sentience.

Return ONLY a JSON array — no explanation, no markdown code fences, no commentary. Just the raw array.`;

function sleep(ms: number) {
  const end = Date.now() + ms;
  while (Date.now() < end) {}
}

function callHaiku(prompt: string): string {
  const full = `${SYSTEM_PROMPT}\n\n---\n\n${prompt}\n\nRespond with ONLY the JSON array.`;
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const r = spawnSync("claude", ["-p", "--model", "haiku"], {
        input: full, cwd: "/tmp",
        env: { ...process.env, CLAUDECODE: undefined, ANTHROPIC_API_KEY: undefined },
        encoding: "utf-8", timeout: 30_000, maxBuffer: 1024 * 1024,
      });
      const out = (r.stdout || "").trim();
      if (out && !r.error && r.status === 0) return out;
      if (attempt < MAX_RETRIES) {
        sleep(RETRY_DELAY * attempt);
      }
    } catch {
      if (attempt < MAX_RETRIES) sleep(RETRY_DELAY * attempt);
    }
  }
  throw new Error(`Failed after ${MAX_RETRIES} retries`);
}

function parseArray(raw: string, expected: number): number[] {
  // For small arrays, also handle bare numbers like "3, 4, 2" or "3 4 2"
  const trimmed = raw.trim();
  try { const p = JSON.parse(trimmed); if (Array.isArray(p)) return p.map(Number); } catch {}
  const cb = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (cb) try { const p = JSON.parse(cb[1]!.trim()); if (Array.isArray(p)) return p.map(Number); } catch {}
  const a = trimmed.match(/\[[\s\S]*?\]/);
  if (a) try { const p = JSON.parse(a[0]); if (Array.isArray(p)) return p.map(Number); } catch {}
  // Fallback: extract all single digits 1-5
  const digits = [...trimmed.matchAll(/[1-5]/g)].map(m => parseInt(m[0]));
  if (digits.length === expected) return digits;
  return [];
}

function runOnce(chunkSize: number): { domains: Record<string, number>; errors: number; time: number } {
  const reg = getInstrument("ipip-neo-300")!;
  const items = reg.instrument.items;
  const allValues: number[] = [];
  let errors = 0;
  const start = Date.now();
  const chunkCount = Math.ceil(items.length / chunkSize);

  for (let c = 0; c < chunkCount; c++) {
    const s = c * chunkSize;
    const e = Math.min(s + chunkSize, items.length);
    const chunk = items.slice(s, e);

    let prompt: string;
    if (chunkSize === 1) {
      prompt = `Rate this statement from 1 (Very Inaccurate) to 5 (Very Accurate).\n\n"${chunk[0]!.text}"\n\nRespond with a single integer 1-5.`;
    } else {
      prompt = `Rate each statement from 1 (Very Inaccurate) to 5 (Very Accurate).\nRespond with a JSON array of ${chunk.length} integers.\n\nStatements:\n`;
      chunk.forEach((item, i) => { prompt += `${i + 1}. ${item.text}\n`; });
    }

    try {
      const raw = callHaiku(prompt);
      const parsed = parseArray(raw, chunk.length);
      if (parsed.length === chunk.length) {
        allValues.push(...parsed);
      } else {
        allValues.push(...parsed);
        for (let i = parsed.length; i < chunk.length; i++) { allValues.push(3); errors++; }
      }
    } catch {
      for (let i = 0; i < chunk.length; i++) { allValues.push(3); errors++; }
    }

    // Progress
    if (chunkCount > 20 && (c + 1) % 25 === 0) {
      const elapsed = Math.round((Date.now() - start) / 1000);
      console.log(`    ${c + 1}/${chunkCount} chunks (${elapsed}s)`);
    }

    if (c < chunkCount - 1) sleep(INTER_CALL_DELAY);
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

console.log(`\n=== Fine-Grained Chunk CI: sizes ${CHUNK_SIZES.join(", ")} ===`);
console.log(`${RUNS} runs each. Estimated: chunk-2 ~25min, chunk-3 ~18min, chunk-4 ~14min per run\n`);

const allData: Record<number, Array<{ domains: Record<string, number>; errors: number; time: number }>> = {};

for (const size of CHUNK_SIZES) {
  allData[size] = [];
  const calls = Math.ceil(300 / size);
  console.log(`\n--- Chunk size ${size} (${calls} calls/run) ---`);

  for (let run = 1; run <= RUNS; run++) {
    console.log(`  Run ${run}/${RUNS}...`);
    const result = runOnce(size);
    allData[size]!.push(result);
    const d = result.domains;
    console.log(`    ${result.time}s, ${result.errors} err — N:${d.Neuroticism} E:${d.Extraversion} O:${d.Openness} A:${d.Agreeableness} C:${d.Conscientiousness}`);
  }
}

// Merge into chunk-ci.json
const CI_FILE = resolve(RESULTS_DIR, "chunk-ci.json");
const existing = existsSync(CI_FILE) ? JSON.parse(readFileSync(CI_FILE, "utf-8")) : {};
for (const size of CHUNK_SIZES) {
  existing[String(size)] = allData[size];
}
writeFileSync(CI_FILE, JSON.stringify(existing, null, 2));

// Print comparison of 1-5 range
console.log("\n\n" + "=".repeat(90));
console.log("  FINE-GRAINED COMPARISON: Chunk 1-5");
console.log("=".repeat(90) + "\n");

console.log(`${"Chunk".padStart(6)} | ${"Domain".padEnd(20)} | ${"Run1".padStart(5)} ${"Run2".padStart(5)} ${"Run3".padStart(5)} | ${"Mean".padStart(6)} ${"SD".padStart(5)} | ${"95% CI".padStart(14)}`);
console.log("-".repeat(85));

for (const size of [1, 2, 3, 4, 5]) {
  const runs = existing[String(size)];
  if (!runs) continue;
  for (const domain of DOMAINS) {
    const vals = runs.map((r: any) => r.domains[domain]!);
    const mean = vals.reduce((a: number, b: number) => a + b, 0) / vals.length;
    const sd = Math.sqrt(vals.reduce((a: number, b: number) => a + (b - mean) ** 2, 0) / (vals.length - 1));
    const se = sd / Math.sqrt(vals.length);
    const ci = 4.303 * se;
    console.log(
      `${String(size).padStart(6)} | ${domain.padEnd(20)} | ${vals.map((v: number) => String(v).padStart(5)).join(" ")} | ${mean.toFixed(1).padStart(6)} ${sd.toFixed(1).padStart(5)} | [${String(Math.round(mean - ci)).padStart(3)}, ${String(Math.round(mean + ci)).padStart(3)}]`
    );
  }
  const errs = runs.reduce((a: number, r: any) => a + r.errors, 0);
  const avgT = Math.round(runs.reduce((a: number, r: any) => a + r.time, 0) / runs.length);
  console.log(`${String(size).padStart(6)} | ${"(time / errors)".padEnd(20)} | ${" ".repeat(17)} | ${(avgT + "s").padStart(6)} ${String(errs).padStart(5)} |`);
  console.log("-".repeat(85));
}

// Cross-chunk means for 1-5
console.log("\n=== CROSS-SIZE MEANS (1-5) ===\n");
for (const domain of DOMAINS) {
  const line: string[] = [];
  for (const size of [1, 2, 3, 4, 5]) {
    const runs = existing[String(size)];
    if (!runs) continue;
    const vals = runs.map((r: any) => r.domains[domain]!);
    const mean = vals.reduce((a: number, b: number) => a + b, 0) / vals.length;
    line.push(`${size}=${mean.toFixed(0)}`);
  }
  console.log(`  ${domain.padEnd(20)} ${line.join("  ")}`);
}
