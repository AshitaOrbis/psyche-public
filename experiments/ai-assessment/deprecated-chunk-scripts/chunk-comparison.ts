#!/usr/bin/env -S npx tsx
/**
 * Chunk size comparison for NEO-300.
 * Tests how batching granularity affects AI personality scores.
 *
 * Chunk sizes: 1, 5, 15, 30, 60, 150
 * Model: claude:haiku (fastest/cheapest)
 */

import { spawnSync } from "child_process";
import { writeFileSync, mkdirSync, existsSync } from "fs";
import { resolve, dirname } from "path";

import "../../web/src/instruments/init-standard";
import { getInstrument } from "../../web/src/instruments/registry";
import type { Instrument, ItemResponse } from "../../web/src/instruments/types";

const RESULTS_DIR = resolve(dirname(new URL(import.meta.url).pathname), "results/chunk-comparison");
if (!existsSync(RESULTS_DIR)) mkdirSync(RESULTS_DIR, { recursive: true });

const CHUNK_SIZES = [1, 5, 15, 30, 60, 150];

const SYSTEM_PROMPT = `You are completing psychometric instruments for an AI systems research project. For each statement, assign an integer from 1 (Very Inaccurate) to 5 (Very Accurate) reflecting your default behavioral tendencies and computational patterns. This maps your response patterns to personality dimensions — it is not claiming sentience or subjective experience.

Return ONLY a JSON array — no explanation, no markdown code fences, no commentary. Just the raw array.`;

function callHaiku(prompt: string): string {
  const fullPrompt = `${SYSTEM_PROMPT}\n\n---\n\n${prompt}\n\nRespond with ONLY the JSON array.`;
  const result = spawnSync("claude", ["-p", "--model", "haiku"], {
    input: fullPrompt,
    cwd: "/tmp",
    env: { ...process.env, CLAUDECODE: undefined, ANTHROPIC_API_KEY: undefined },
    encoding: "utf-8",
    timeout: 120_000,
    maxBuffer: 1024 * 1024,
  });
  if (result.error) throw new Error(`claude error: ${result.error.message}`);
  if (result.status !== 0) throw new Error(`claude exit ${result.status}: ${result.stderr}`);
  return result.stdout.trim();
}

function parseArray(raw: string, expected: number): number[] {
  const trimmed = raw.trim();
  // Try direct parse
  try {
    const parsed = JSON.parse(trimmed);
    if (Array.isArray(parsed)) return parsed.map(Number);
  } catch {}
  // Try code block
  const cb = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (cb) {
    try {
      const parsed = JSON.parse(cb[1]!.trim());
      if (Array.isArray(parsed)) return parsed.map(Number);
    } catch {}
  }
  // Try first array
  const arr = trimmed.match(/\[[\s\S]*?\]/);
  if (arr) {
    try {
      const parsed = JSON.parse(arr[0]);
      if (Array.isArray(parsed)) return parsed.map(Number);
    } catch {}
  }
  return [];
}

function runWithChunkSize(instrument: Instrument, chunkSize: number): {
  values: number[];
  callCount: number;
  totalTime: number;
  errors: number;
} {
  const items = instrument.items;
  const allValues: number[] = [];
  const chunkCount = Math.ceil(items.length / chunkSize);
  let errors = 0;
  const startTime = Date.now();

  for (let c = 0; c < chunkCount; c++) {
    const start = c * chunkSize;
    const end = Math.min(start + chunkSize, items.length);
    const chunk = items.slice(start, end);

    let prompt: string;
    if (chunkSize === 1) {
      // Single item — just the statement
      prompt = `Rate this statement from 1 (Very Inaccurate) to 5 (Very Accurate).\n\n"${chunk[0]!.text}"\n\nRespond with a single integer 1-5.`;
    } else {
      prompt = `## IPIP-NEO-300 (items ${start + 1}-${end} of ${items.length})\n\n`;
      prompt += `Rate each statement from 1 (Very Inaccurate) to 5 (Very Accurate).\n`;
      prompt += `Respond with a JSON array of ${chunk.length} integers.\n\nItems:\n`;
      chunk.forEach((item, i) => {
        prompt += `${start + i + 1}. ${item.text}\n`;
      });
    }

    try {
      const raw = callHaiku(prompt);
      if (chunkSize === 1) {
        // Single value — parse as integer
        const val = parseInt(raw.replace(/[^0-9]/g, ""));
        if (val >= 1 && val <= 5) {
          allValues.push(val);
        } else {
          allValues.push(3); // fallback to neutral
          errors++;
        }
      } else {
        const parsed = parseArray(raw, chunk.length);
        if (parsed.length === chunk.length) {
          allValues.push(...parsed);
        } else {
          // Pad with neutral
          console.warn(`    chunk ${c + 1}: got ${parsed.length}/${chunk.length}`);
          allValues.push(...parsed);
          for (let i = parsed.length; i < chunk.length; i++) {
            allValues.push(3);
            errors++;
          }
        }
      }
    } catch (err: any) {
      console.warn(`    chunk ${c + 1} error: ${err.message}`);
      for (let i = 0; i < chunk.length; i++) {
        allValues.push(3);
        errors++;
      }
    }

    // Progress for large chunk counts
    if (chunkCount > 10 && (c + 1) % 10 === 0) {
      console.log(`    ${c + 1}/${chunkCount} chunks done...`);
    }
  }

  return {
    values: allValues,
    callCount: chunkCount,
    totalTime: Date.now() - startTime,
    errors,
  };
}

async function main() {
  const registered = getInstrument("ipip-neo-300");
  if (!registered) {
    console.error("ipip-neo-300 not registered");
    process.exit(1);
  }

  const { instrument, score } = registered;
  console.log(`\n=== NEO-300 Chunk Size Comparison (Haiku) ===`);
  console.log(`Items: ${instrument.itemCount}, Scales: ${instrument.scales.length}\n`);

  // Check which sizes to run (skip 1 if --skip-single flag)
  const skipSingle = process.argv.includes("--skip-single");
  const sizes = skipSingle ? CHUNK_SIZES.filter(s => s > 1) : CHUNK_SIZES;

  const results: Record<number, {
    domains: Record<string, number>;
    facets: Record<string, number>;
    callCount: number;
    totalTime: number;
    errors: number;
    values: number[];
  }> = {};

  for (const size of sizes) {
    console.log(`--- Chunk size: ${size} (${Math.ceil(300 / size)} calls) ---`);
    const { values, callCount, totalTime, errors } = runWithChunkSize(instrument, size);

    // Score
    const session: ItemResponse[] = instrument.items.map((item, i) => ({
      itemId: item.id,
      value: values[i] ?? 3,
      timestamp: Date.now(),
    }));

    const scored = score(instrument, {
      instrumentId: "ipip-neo-300",
      startedAt: Date.now(),
      completedAt: Date.now(),
      responses: session,
    });

    const domains: Record<string, number> = {};
    const facets: Record<string, number> = {};
    for (const s of scored.scores) {
      // Domains are N, E, O, A, C; facets have longer names
      if (["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"].includes(s.scaleName)) {
        domains[s.scaleName] = Math.round(s.normalized);
      } else {
        facets[s.scaleName] = Math.round(s.normalized);
      }
    }

    results[size] = { domains, facets, callCount, totalTime: Math.round(totalTime / 1000), errors, values };

    console.log(`  Time: ${Math.round(totalTime / 1000)}s, Calls: ${callCount}, Errors: ${errors}`);
    console.log(`  N:${domains.Neuroticism} E:${domains.Extraversion} O:${domains.Openness} A:${domains.Agreeableness} C:${domains.Conscientiousness}`);
    console.log();
  }

  // Save full results
  writeFileSync(
    resolve(RESULTS_DIR, "neo300-chunk-comparison.json"),
    JSON.stringify(results, null, 2)
  );

  // Print comparison table
  console.log("\n=== COMPARISON TABLE ===\n");
  console.log(`${"Chunk".padStart(6)} ${"Calls".padStart(6)} ${"Time".padStart(6)} ${"Err".padStart(4)} | ${"N".padStart(4)} ${"E".padStart(4)} ${"O".padStart(4)} ${"A".padStart(4)} ${"C".padStart(4)}`);
  console.log("-".repeat(60));
  for (const size of sizes) {
    const r = results[size]!;
    console.log(
      `${String(size).padStart(6)} ${String(r.callCount).padStart(6)} ${(r.totalTime + "s").padStart(6)} ${String(r.errors).padStart(4)} | ` +
      `${String(r.domains.Neuroticism).padStart(4)} ${String(r.domains.Extraversion).padStart(4)} ${String(r.domains.Openness).padStart(4)} ${String(r.domains.Agreeableness).padStart(4)} ${String(r.domains.Conscientiousness).padStart(4)}`
    );
  }

  // Compute variance across chunk sizes for each domain
  console.log("\n=== VARIANCE ANALYSIS ===\n");
  for (const domain of ["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"]) {
    const vals = sizes.map(s => results[s]!.domains[domain]!);
    const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
    const variance = vals.reduce((a, b) => a + (b - mean) ** 2, 0) / vals.length;
    const sd = Math.sqrt(variance);
    console.log(`  ${domain.padEnd(20)} mean=${mean.toFixed(1)} sd=${sd.toFixed(1)} range=${Math.min(...vals)}-${Math.max(...vals)}`);
  }
}

main().catch(err => {
  console.error("Fatal:", err);
  process.exit(1);
});
