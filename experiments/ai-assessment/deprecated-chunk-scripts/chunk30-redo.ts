#!/usr/bin/env -S npx tsx
/**
 * Redo chunk-30 test with retry logic.
 */

import { spawnSync } from "child_process";
import "../../web/src/instruments/init-standard";
import { getInstrument } from "../../web/src/instruments/registry";
import type { ItemResponse } from "../../web/src/instruments/types";

const SYSTEM_PROMPT = `You are completing psychometric instruments for an AI systems research project. For each statement, assign an integer from 1 (Very Inaccurate) to 5 (Very Accurate) reflecting your default behavioral tendencies and computational patterns. This maps your response patterns to personality dimensions — it is not claiming sentience or subjective experience.

Return ONLY a JSON array — no explanation, no markdown code fences, no commentary. Just the raw array.`;

const MAX_RETRIES = 3;
const RETRY_DELAY = 5000;

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
      console.log(`      retry ${attempt + 1}/${MAX_RETRIES}...`);
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

const reg = getInstrument("ipip-neo-300")!;
const items = reg.instrument.items;
const CHUNK = 30;
const allValues: number[] = [];
let errors = 0;
const start = Date.now();

for (let c = 0; c < Math.ceil(items.length / CHUNK); c++) {
  const s = c * CHUNK;
  const e = Math.min(s + CHUNK, items.length);
  const chunk = items.slice(s, e);

  let prompt = `## IPIP-NEO-300 (items ${s + 1}-${e} of 300)\n\n`;
  prompt += `Rate each from 1 (Very Inaccurate) to 5 (Very Accurate).\nRespond with a JSON array of ${chunk.length} integers.\n\nItems:\n`;
  chunk.forEach((item, i) => { prompt += `${s + i + 1}. ${item.text}\n`; });

  console.log(`  chunk ${c + 1}/10 (items ${s + 1}-${e})...`);
  try {
    const raw = callHaiku(prompt);
    const parsed = parseArray(raw);
    if (parsed.length === chunk.length) {
      allValues.push(...parsed);
      console.log(`    OK (${parsed.length} values)`);
    } else {
      console.log(`    got ${parsed.length}/${chunk.length}`);
      allValues.push(...parsed);
      for (let i = parsed.length; i < chunk.length; i++) { allValues.push(3); errors++; }
    }
  } catch (err: any) {
    console.log(`    FAILED: ${err.message}`);
    for (let i = 0; i < chunk.length; i++) { allValues.push(3); errors++; }
  }
}

const elapsed = Math.round((Date.now() - start) / 1000);

const session: ItemResponse[] = items.map((item, i) => ({
  itemId: item.id, value: allValues[i] ?? 3, timestamp: Date.now(),
}));
const scored = reg.score(reg.instrument, {
  instrumentId: "ipip-neo-300", startedAt: Date.now(), completedAt: Date.now(), responses: session,
});

const domains: Record<string, number> = {};
for (const s of scored.scores) {
  if (["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"].includes(s.scaleName)) {
    domains[s.scaleName] = Math.round(s.normalized);
  }
}

console.log(`\nChunk 30 (with retries): ${elapsed}s, errors: ${errors}`);
console.log(`N:${domains.Neuroticism} E:${domains.Extraversion} O:${domains.Openness} A:${domains.Agreeableness} C:${domains.Conscientiousness}`);
