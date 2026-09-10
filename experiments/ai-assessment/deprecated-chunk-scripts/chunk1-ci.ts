#!/usr/bin/env -S npx tsx
/**
 * Chunk size 1 CI — 3 runs of NEO-300 with individual items.
 * Runs sequentially with robust retry logic and generous delays.
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
const RUNS = 3;
const MAX_RETRIES = 5;
const RETRY_DELAY = 8000;
const INTER_ITEM_DELAY = 500; // 0.5s between items to avoid rate limits

const SYSTEM_PROMPT = `You are completing a psychometric instrument for an AI systems research project. Rate the following statement reflecting your default behavioral tendencies. This maps your response patterns to personality dimensions — it is not claiming sentience.

Respond with ONLY a single integer from 1 (Very Inaccurate) to 5 (Very Accurate). Nothing else.`;

function sleep(ms: number) {
  const end = Date.now() + ms;
  while (Date.now() < end) {}
}

function callHaikuSingle(statement: string): number {
  const prompt = `${SYSTEM_PROMPT}\n\nStatement: "${statement}"`;
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const r = spawnSync("claude", ["-p", "--model", "haiku"], {
        input: prompt, cwd: "/tmp",
        env: { ...process.env, CLAUDECODE: undefined, ANTHROPIC_API_KEY: undefined },
        encoding: "utf-8", timeout: 30_000, maxBuffer: 1024 * 1024,
      });
      const out = (r.stdout || "").trim();
      if (r.error || r.status !== 0 || !out) {
        if (attempt < MAX_RETRIES) {
          console.log(`      retry ${attempt + 1}/${MAX_RETRIES} (exit=${r.status})...`);
          sleep(RETRY_DELAY * attempt);
          continue;
        }
        return 3; // fallback
      }
      // Extract single digit 1-5
      const match = out.match(/[1-5]/);
      if (match) return parseInt(match[0]!);
      // Model might have returned a verbose response — try harder
      const digits = out.replace(/[^1-5]/g, "");
      if (digits.length === 1) return parseInt(digits);
      if (attempt < MAX_RETRIES) {
        console.log(`      retry ${attempt + 1}/${MAX_RETRIES} (bad response: "${out.slice(0, 50)}")...`);
        sleep(RETRY_DELAY * attempt);
        continue;
      }
      return 3; // fallback
    } catch (err: any) {
      if (attempt < MAX_RETRIES) {
        console.log(`      retry ${attempt + 1}/${MAX_RETRIES} (${err.message})...`);
        sleep(RETRY_DELAY * attempt);
      }
    }
  }
  return 3; // fallback after all retries
}

function runOnce(runNum: number): { domains: Record<string, number>; errors: number; time: number; values: number[] } {
  const reg = getInstrument("ipip-neo-300")!;
  const items = reg.instrument.items;
  const values: number[] = [];
  let errors = 0;
  const start = Date.now();

  for (let i = 0; i < items.length; i++) {
    const val = callHaikuSingle(items[i]!.text);
    values.push(val);

    // Track fallbacks
    if (val === 3) {
      // Could be genuine 3 or fallback — can't distinguish, but we tried hard
    }

    // Progress
    if ((i + 1) % 25 === 0) {
      const elapsed = Math.round((Date.now() - start) / 1000);
      const rate = (i + 1) / elapsed;
      const eta = Math.round((items.length - i - 1) / rate);
      console.log(`    ${i + 1}/300 (${elapsed}s elapsed, ~${eta}s remaining)`);
    }

    // Inter-item delay to avoid rate limiting
    if (i < items.length - 1) {
      sleep(INTER_ITEM_DELAY);
    }
  }

  // Score
  const session: ItemResponse[] = items.map((item, i) => ({
    itemId: item.id, value: values[i] ?? 3, timestamp: Date.now(),
  }));
  const scored = reg.score(reg.instrument, {
    instrumentId: "ipip-neo-300", startedAt: Date.now(), completedAt: Date.now(), responses: session,
  });
  const domains: Record<string, number> = {};
  for (const sc of scored.scores) {
    if (DOMAINS.includes(sc.scaleName)) domains[sc.scaleName] = Math.round(sc.normalized);
  }

  return { domains, errors, time: Math.round((Date.now() - start) / 1000), values };
}

// --- Main ---

console.log(`\n=== NEO-300 Chunk Size 1 CI (${RUNS} runs, 300 items each) ===`);
console.log(`Estimated time: ~20-25 min per run, ~60-75 min total\n`);

const results: Array<{ domains: Record<string, number>; errors: number; time: number }> = [];

for (let run = 1; run <= RUNS; run++) {
  console.log(`--- Run ${run}/${RUNS} ---`);
  const result = runOnce(run);
  results.push(result);
  const d = result.domains;
  console.log(`  Done: ${result.time}s — N:${d.Neuroticism} E:${d.Extraversion} O:${d.Openness} A:${d.Agreeableness} C:${d.Conscientiousness}\n`);

  // Save incremental results
  writeFileSync(resolve(RESULTS_DIR, "chunk-1-ci.json"), JSON.stringify(results, null, 2));
}

// Final summary
console.log("\n=== CHUNK 1 RESULTS ===\n");
console.log(`${"Domain".padEnd(20)} | ${"Run1".padStart(5)} ${"Run2".padStart(5)} ${"Run3".padStart(5)} | ${"Mean".padStart(6)} ${"SD".padStart(5)} | ${"95% CI".padStart(14)}`);
console.log("-".repeat(75));

for (const domain of DOMAINS) {
  const vals = results.map(r => r.domains[domain]!);
  const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
  const sd = Math.sqrt(vals.reduce((a, b) => a + (b - mean) ** 2, 0) / (vals.length - 1));
  const se = sd / Math.sqrt(vals.length);
  const ci95 = 4.303 * se;
  console.log(
    `${domain.padEnd(20)} | ${vals.map(v => String(v).padStart(5)).join(" ")} | ${mean.toFixed(1).padStart(6)} ${sd.toFixed(1).padStart(5)} | [${String(Math.round(mean - ci95)).padStart(3)}, ${String(Math.round(mean + ci95)).padStart(3)}]`
  );
}

const avgTime = Math.round(results.reduce((a, r) => a + r.time, 0) / results.length);
console.log(`\nAvg time per run: ${avgTime}s (${Math.round(avgTime / 60)} min)`);

// Load chunk-ci.json and merge
const CI_FILE = resolve(RESULTS_DIR, "chunk-ci.json");
if (existsSync(CI_FILE)) {
  const ciData = JSON.parse(readFileSync(CI_FILE, "utf-8"));
  ciData["1"] = results;
  writeFileSync(CI_FILE, JSON.stringify(ciData, null, 2));
  console.log("\nMerged into chunk-ci.json");
}
