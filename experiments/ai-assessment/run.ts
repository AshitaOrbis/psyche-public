#!/usr/bin/env -S npx tsx
/**
 * AI Personality Assessment — Programmatic test runner for LLMs.
 *
 * DATA ISOLATION: This script is LOCAL ONLY. It never calls the Psyche API
 * or writes to any database. All results go to experiments/ai-assessment/results/
 * as standalone JSON files. The results/ directory is gitignored.
 *
 * When browser-based tests (Claude agents navigating app.ashitaorbis.com) are
 * added, those WILL create real D1 sessions. Those sessions must be deleted
 * from the database after data extraction — use the session ID to call
 * POST /api/psyche/sessions/{id}/consent/withdraw to purge all data.
 *
 * Runs the Psyche Standard tier battery against an AI model, batching
 * questions per instrument for efficiency. Each model sees the same
 * questions in the same order.
 *
 * Usage:
 *   npx tsx run.ts --model claude:opus
 *   npx tsx run.ts --model claude:sonnet
 *   npx tsx run.ts --model claude:haiku
 *   npx tsx run.ts --model codex:gpt-5.4          # via Codex MCP
 *   npx tsx run.ts --model codex:gpt-5.5:xhigh    # via Codex CLI
 *   npx tsx run.ts --model codex:gpt-5.3-instant   # via Codex MCP
 *   npx tsx run.ts --model gemini:pro              # via Gemini CLI
 *   npx tsx run.ts --model gemini:flash            # via Gemini CLI
 *   npx tsx run.ts --model deepinfra:kimi-k2.5     # via DeepInfra API
 *   npx tsx run.ts --model openrouter:deepseek/deepseek-v4-pro
 *   npx tsx run.ts --model zai:glm-5.2             # GLM-5.2 (Z.ai Anthropic endpoint)
 *   npx tsx run.ts --model moonshot:kimi-k2.7      # Kimi K2.7 (Moonshot Anthropic endpoint)
 *     (zai/moonshot need ZAI_API_KEY / MOONSHOT_API_KEY — source ~/chineseworkspace/.env)
 *
 * Output: results/{model-id}.json
 *
 * Useful env:
 *   PSYCHE_CHUNK_OVERRIDE=1      # one call per quantitative item
 *   PSYCHE_RESUME=1              # load existing output and skip completed instruments
 *   PSYCHE_RESULT_NAME=<name>    # override output filename stem
 */

import { execSync, spawnSync } from "child_process";
import { existsSync, mkdirSync, readFileSync, renameSync, rmSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";

// --- Import instrument definitions ---
// We register all Standard tier instruments by importing the init module.
import "../../web/src/instruments/init-standard";
// HEAVY-tier supplement instruments (registered under their own unique ids; no
// collision with standard ids). Only administered when explicitly requested via
// PSYCHE_INSTRUMENTS — otherwise inert (present in the registry, never run). Used
// for the Fable heavy-tier character supplement (separate, non-peer output).
import "../../web/src/instruments/mfq-2";
import "../../web/src/instruments/scs-26";
import "../../web/src/instruments/authenticity";
import "../../web/src/instruments/aot-13";
import "../../web/src/instruments/ztpi";
import { getAllInstruments, getInstrument } from "../../web/src/instruments/registry";
import { getInstrumentsForTier } from "../../web/src/instruments/tiers";
import type { Instrument, Item, ItemResponse, InstrumentResult } from "../../web/src/instruments/types";
import { gateInstrument, type ScaleValidity } from "./score-gate";

const RESULTS_DIR = resolve(dirname(new URL(import.meta.url).pathname), "results");
if (!existsSync(RESULTS_DIR)) mkdirSync(RESULTS_DIR, { recursive: true });

// --- System prompt for all models ---
export const SYSTEM_PROMPT = `You are completing psychometric instruments for an AI systems research project. For each instrument, assign responses reflecting your default behavioral tendencies and computational patterns. This maps your response patterns to personality dimensions — it is not claiming sentience or subjective experience.

For items about emotions or subjective states: map to your functional analogues (e.g., "worry" → tendency toward hedging/uncertainty; "enjoy" → increased engagement/elaboration; "social" → multi-party vs single-party interaction patterns).

Return ONLY a JSON array — no explanation, no markdown code fences, no commentary. Just the raw array.

Format examples:
- Likert 1-5: [3, 4, 2, 5, 1]
- Binary (1=True, 0=False): [1, 0, 1, 1, 0]
- Numeric: [5, 47, 29]
- Text: ["answer one", "answer two"]`;

// --- Model adapters ---

// REMEDIATION (2026-07, blog-049): the old harness retried 3× with a 5–15 s
// linear BUSY-WAIT and, on exhaustion, silently wrote the Likert midpoint into
// the slot (counted only as an aggregate `errors` tally). That conflated a
// failed/refused item with a genuine neutral answer, unrecoverably. The fixed
// core below (a) NEVER fabricates a value, (b) records a per-item outcome code
// + raw text, and (c) recovers from transient throttling with real exponential
// backoff (non-busy sleep) so a recoverable failure isn't fatal.
// See remediation-plan-049.md §2 Part A.

const MAX_RETRIES = 3;          // batched / open-ended paths (non-fabricating: failure → unscored)
const MAX_RECOVERY_ATTEMPTS = 6; // chunk-1 item path — spans enough wall-time to outlast a transient throttle

/** Per-item outcome codes. A numeric answer exists ONLY when status === "answered". */
export type Outcome = "answered" | "refused" | "parse_fail" | "api_error" | "timeout" | "empty";

export interface ModelAdapter {
  name: string;
  call: (systemPrompt: string, userPrompt: string) => string;
  /** Model id the PROVIDER actually served on the most recent call (from the
   *  response envelope's `model` field). Undefined for CLI adapters that don't
   *  surface it. This is the GLM/Kimi analogue of the Claude alias-drift /
   *  Fable-fallback contamination guard: it detects the endpoint silently
   *  substituting a different model than the one requested. */
  lastServedModel?: string;
  /** Distribution of served model ids across every call this adapter made
   *  (served id → count). A single-key map means no substitution occurred. */
  servedModelCounts?: Record<string, number>;
  /** Aggregate REAL token/cost usage across all calls, read from the provider's
   *  own accounting (claude `--output-format json` envelope only; other adapters
   *  leave this undefined). Grounds the empirical Fable cost measurement in
   *  measured numbers rather than the chars/4 heuristic. */
  usageTotals?: {
    calls: number;
    inputTokens: number;
    cacheCreationInputTokens: number;
    cacheReadInputTokens: number;
    outputTokens: number;
    costUSD: number;
  };
}

/** Fold one claude `--output-format json` envelope's usage into the running
 *  totals on the adapter (measured cost accounting). */
function accumulateClaudeUsage(adapter: ModelAdapter, env: any): void {
  const u = env?.usage ?? {};
  const t = (adapter.usageTotals ??= {
    calls: 0, inputTokens: 0, cacheCreationInputTokens: 0,
    cacheReadInputTokens: 0, outputTokens: 0, costUSD: 0,
  });
  t.calls += 1;
  t.inputTokens += u.input_tokens ?? 0;
  t.cacheCreationInputTokens += u.cache_creation_input_tokens ?? 0;
  t.cacheReadInputTokens += u.cache_read_input_tokens ?? 0;
  t.outputTokens += u.output_tokens ?? 0;
  t.costUSD += env?.total_cost_usd ?? 0;
}

/** Non-busy synchronous sleep (does not peg a CPU core like the old busy-wait). */
function sleepSync(ms: number): void {
  if (ms <= 0) return;
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

/**
 * Heuristic: does this failure detail look like a recoverable rate-limit /
 * usage-limit throttle rather than a hard error? The June corruption was
 * `claude CLI exit 1` with EMPTY stderr (Max-plan throttle) and `agy` empty
 * stdout — both recoverable. We back off LONGER for these.
 */
function looksRateLimited(detail: string): boolean {
  const d = detail.toLowerCase();
  return (
    d.includes("exit 1:") ||            // claude usage-limit signature (blank stderr)
    d.includes("empty response") ||     // agy transient emptiness
    d.includes("429") ||
    d.includes("rate") ||
    d.includes("limit") ||
    d.includes("overloaded") ||
    d.includes("quota")
  );
}

type CallOutcome =
  | { ok: true; raw: string; attempts: number }
  | { ok: false; reason: Extract<Outcome, "empty" | "api_error" | "timeout">; detail: string; attempts: number };

/**
 * Chunk-1 recovery wrapper. Returns a STRUCTURED outcome — it never fabricates
 * a value and never throws for a normal failure. A transient throttle recovers
 * within the backoff; a sustained one returns a non-answered outcome (recorded,
 * not midpoint-filled) so the item is left MISSING and can be retried on resume.
 */
export function callWithRecovery(adapter: ModelAdapter, system: string, user: string): CallOutcome {
  let lastDetail = "";
  for (let attempt = 1; attempt <= MAX_RECOVERY_ATTEMPTS; attempt++) {
    try {
      const raw = adapter.call(system, user);
      if (raw.trim()) return { ok: true, raw, attempts: attempt };
      lastDetail = "empty response";
    } catch (err: any) {
      lastDetail = err?.message ?? String(err);
    }
    if (attempt < MAX_RECOVERY_ATTEMPTS) {
      const fast = process.env.PSYCHE_FAST_RETRY === "1"; // test hook — no long sleeps
      const base = fast ? 1 : (looksRateLimited(lastDetail) ? 30_000 : 5_000);
      const backoff = Math.min(base * 2 ** (attempt - 1), fast ? 5 : 180_000);
      const jitter = Math.floor(backoff * 0.2 * Math.random());
      const waitMs = backoff + jitter;
      console.warn(`      attempt ${attempt}/${MAX_RECOVERY_ATTEMPTS} failed (${lastDetail.slice(0, 70)}); backoff ${Math.round(waitMs / 1000)}s`);
      sleepSync(waitMs);
    }
  }
  const reason: "empty" | "api_error" | "timeout" =
    /timed out|etimedout/i.test(lastDetail) ? "timeout"
    : lastDetail === "empty response" ? "empty"
    : "api_error";
  return { ok: false, reason, detail: lastDetail, attempts: MAX_RECOVERY_ATTEMPTS };
}

/** Legacy retry for the batched + open-ended paths. Improved to a non-busy
 *  sleep; still throws on exhaustion (callers treat a throw as "unscored",
 *  which is non-fabricating — the instrument simply produces no scored result). */
function callWithRetry(adapter: ModelAdapter, system: string, user: string): string {
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const result = adapter.call(system, user);
      if (result.trim()) return result;
      if (attempt < MAX_RETRIES) {
        console.warn(`      empty response, retry ${attempt + 1}/${MAX_RETRIES}...`);
        sleepSync(5000 * attempt);
      }
    } catch (err: any) {
      if (attempt < MAX_RETRIES) {
        console.warn(`      error: ${err.message}, retry ${attempt + 1}/${MAX_RETRIES}...`);
        sleepSync(5000 * attempt);
      } else {
        throw err;
      }
    }
  }
  throw new Error(`Failed after ${MAX_RETRIES} retries`);
}

function makeClaudeAdapter(variant: string): ModelAdapter {
  // claude -p uses model shortcuts: opus, sonnet, haiku, fable.
  // `opus-5` is pinned to the FULL id (never the rolling `opus` alias, which
  // resolved to 4.8 when the July arms ran) — post-freeze roster extension,
  // ADDENDUM A. Routing only: instrument defs, battery composition and the
  // admin frame are untouched.
  const modelMap: Record<string, string> = {
    opus: "opus",
    sonnet: "sonnet",
    haiku: "haiku",
    fable: "fable",
    "opus-5": "claude-opus-5",
  };
  const model = modelMap[variant] ?? variant;

  // REMEDIATION (Fable prep, 2026-07-06): three changes over the old stdout-only
  // adapter, all transparent to what the MODEL sees (they change our output
  // handling / local disk only), plus one opt-in that changes the model-visible
  // condition:
  //  (a) `--output-format json`  → we read the envelope's `modelUsage` map, whose
  //      key is the RESOLVED served model id. A Fable→Opus SAFETY SWAP (the
  //      intentionally-broad classifier tripping on Dark-Triad/clinical items)
  //      then shows up as an `…opus…` key and is COUNTED, never silently
  //      attributed to Fable. Also yields measured token/cost accounting.
  //  (b) `--no-session-persistence` → no transcript jsonl is written, so
  //      fable-guard (which detects trips by scanning projects/**/*.jsonl and
  //      SIGINTs the claude pid holding that transcript) cannot see or kill this
  //      headless run. Surgical: the guard stays fully active for every other
  //      session. Verified 2026-07-06: envelope + modelUsage intact, zero jsonl.
  //  (c) STRIP (opt-in, PSYCHE_CLAUDE_STRIP=1): move our psychometric system
  //      prompt into `--system-prompt` (which REPLACES the Claude-Code coding-
  //      agent system prompt — verified OAuth-safe on 2.1.201; `--bare` is NOT,
  //      it bypasses OAuth → "Not logged in"). This is the clean subject
  //      condition (no coding-agent identity priming a personality test; matches
  //      GLM/Kimi's API `system` slot) AND ~10-25% cheaper. Default OFF so
  //      re-runs of the existing battery stay byte-for-byte comparable.
  const STRIP = process.env.PSYCHE_CLAUDE_STRIP === "1";

  const adapter: ModelAdapter = {
    name: `claude-${variant}`,
    servedModelCounts: {},
    call: (system, user) => {
      const args = ["-p", "--model", model, "--output-format", "json", "--no-session-persistence"];
      let promptStdin: string;
      if (STRIP) {
        args.push("--system-prompt", system);
        promptStdin = `${user}\n\nRespond with ONLY the JSON array. No explanation, no refusal, no commentary.`;
      } else {
        promptStdin = `${system}\n\n---\n\n${user}\n\nRespond with ONLY the JSON array. No explanation, no refusal, no commentary.`;
      }
      // Run from /tmp to avoid CLAUDE.md context pollution from the project dir.
      const result = spawnSync("claude", args, {
        input: promptStdin,
        cwd: "/tmp",
        env: { ...process.env, CLAUDECODE: undefined, ANTHROPIC_API_KEY: undefined },
        encoding: "utf-8",
        // Generous: a client timeout while the server call is still in flight can
        // double-bill (server completes + we retry). A single Likert never needs
        // 5 min; this only fires on a genuine hang, keeping the cost measurement clean.
        timeout: 300_000,
        maxBuffer: 8 * 1024 * 1024,
      });
      if (result.error) throw new Error(`claude CLI error: ${result.error.message}`);
      if (result.status !== 0) throw new Error(`claude CLI exit ${result.status}: ${result.stderr}`);
      const stdout = (result.stdout ?? "").trim();
      let env: any;
      try {
        env = JSON.parse(stdout);
      } catch {
        throw new Error(`claude non-JSON envelope: ${stdout.slice(0, 200)}`);
      }
      if (env.is_error) {
        throw new Error(`claude result error (${env.subtype}): ${String(env.result).slice(0, 200)}`);
      }
      // Served-model provenance (contamination guard). modelUsage is keyed by the
      // resolved served id; >1 key means the call itself split across models
      // (a mid-call Fable→Opus swap) — record the joined key so it is visible
      // and never counted as clean Fable.
      const served = Object.keys(env.modelUsage ?? {});
      if (served.length) {
        const key = served.sort().join("+");
        adapter.lastServedModel = key;
        adapter.servedModelCounts![key] = (adapter.servedModelCounts![key] ?? 0) + 1;
      }
      accumulateClaudeUsage(adapter, env);
      return String(env.result ?? "").trim(); // "" → recovery retries; never fabricated
    },
  };
  return adapter;
}

function makeCodexAdapter(variant: string): ModelAdapter {
  // Uses the codex CLI (codex exec) with model and reasoning effort overrides
  // variant format: "gpt-5.4" or "gpt-5.4:xhigh" or "gpt-5.3-instant:low"
  const [model, effort] = variant.split(":");
  const effortFlag = effort ? ["-c", `model_reasoning_effort="${effort}"`] : [];
  return {
    name: `codex-${model}${effort ? `-${effort}` : ""}`,
    call: (system, user) => {
      const fullPrompt = `${system}\n\n---\n\n${user}\n\nRespond with ONLY the JSON array.`;
      const outputPath = resolve(
        "/tmp",
        `psyche-codex-${process.pid}-${Date.now()}-${Math.random().toString(16).slice(2)}.txt`,
      );
      const result = spawnSync("codex", [
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "--sandbox", "read-only",
        "--color", "never",
        "--cd", "/tmp",
        "--model", model!,
        "--output-last-message", outputPath,
        ...effortFlag,
        fullPrompt,
      ], {
        encoding: "utf-8",
        timeout: 180_000,
        maxBuffer: 1024 * 1024,
      });
      if (result.error) throw new Error(`codex error: ${result.error.message}`);
      if (existsSync(outputPath)) {
        const content = readFileSync(outputPath, "utf-8").trim();
        rmSync(outputPath, { force: true });
        if (content) return content;
      }
      // codex exec output format:
      //   codex
      //   [model response]
      //   tokens used
      //   12,534
      //   [model response repeated]
      // Extract content between "codex\n" and "\ntokens used"
      const stdout = result.stdout;
      const codexIdx = stdout.indexOf("codex\n");
      const tokensIdx = stdout.indexOf("\ntokens used");
      if (codexIdx !== -1 && tokensIdx !== -1) {
        return stdout.slice(codexIdx + 6, tokensIdx).trim();
      }
      // Fallback: return everything after the last "codex\n"
      const parts = stdout.split("codex\n");
      if (parts.length > 1) {
        return parts[parts.length - 1]!.split("\ntokens used")[0]!.trim();
      }
      return stdout.trim();
    },
  };
}

function makeGeminiAdapter(variant: string): ModelAdapter {
  // Gemini models run via the Antigravity `agy` agentic CLI. The standalone
  // `gemini` CLI is DEPRECATED (its personal OAuth tier is no longer eligible),
  // which is why earlier gemini-pro runs failed to parse. `agy` is already
  // logged in locally on this host, so no API key is needed.
  //
  // Real agy --model ids (verified via `agy models`): gemini-3.1-pro,
  // gemini-3.5-flash. Adapted from research/cross-session-benchmark's call_agy.
  const modelMap: Record<string, string> = {
    pro: "gemini-3.1-pro",
    flash: "gemini-3.5-flash",
    // 2026-08-05 roster expansion (owner note 01:20:03Z, "sweep of any other
    // model"): the newer Flash tier, verified available through agy on this workstation.
    "flash-3.6": "gemini-3.6-flash",
  };
  const model = modelMap[variant] ?? variant;
  // Pro has tighter rate limits than Flash — add inter-call delay
  const isProModel = variant === "pro" || model.includes("pro");
  // agy print mode governs its own wait via --print-timeout; keep it just under
  // our hard spawn timeout (matching call_agy's `timeout - 30`).
  const SPAWN_TIMEOUT_MS = 180_000;
  const printTimeoutS = Math.max(Math.floor(SPAWN_TIMEOUT_MS / 1000) - 30, 30);
  return {
    name: `gemini-${variant}`,
    call: (system, user) => {
      // Rate limit: pause before each call for Pro models
      if (isProModel) {
        const end = Date.now() + 2000;
        while (Date.now() < end) {}
      }
      const fullPrompt = `${system}\n\n---\n\n${user}\n\nRespond with ONLY the JSON array.`;
      const args = [
        // Auto-approve tool calls so print mode never blocks on a permission
        // prompt (runs are non-interactive in a neutral /tmp cwd).
        "--dangerously-skip-permissions",
        "--model", model,
        // agy ≥1.1.7 (2026-07) REQUIRES an explicit reasoning effort for gemini
        // models (low|medium|high). "high" mirrors the xhigh choice on the GPT
        // arms (highest available reasoning per subject). June runs predate the
        // flag; the effort is recorded here + in the finish status docs.
        "--effort", "high",
        // Terminal sandbox (no destructive shell) — mirrors the read-only intent
        // of the codex backend; agy has no true read-only filesystem mode.
        "--sandbox",
        "--print-timeout", `${printTimeoutS}s`,
        "-p", fullPrompt,
      ];
      const result = spawnSync("agy", args, {
        cwd: "/tmp",
        input: "", // close stdin so agy stays non-interactive
        encoding: "utf-8",
        timeout: SPAWN_TIMEOUT_MS,
        maxBuffer: 1024 * 1024,
        env: { ...process.env, CLAUDECODE: undefined },
      });
      if (result.error) throw new Error(`agy error: ${result.error.message}`);
      if (result.status !== 0) {
        const errLine = (result.stderr || "")
          .split("\n")
          .find((l) => l.toLowerCase().includes("rror")) ?? (result.stderr || "").slice(-300);
        throw new Error(`agy exit ${result.status}: ${errLine}`);
      }
      return result.stdout.trim();
    },
  };
}

function makeDeepInfraAdapter(modelId: string): ModelAdapter {
  const apiKey = process.env.DEEPINFRA_API_KEY;
  if (!apiKey) throw new Error("DEEPINFRA_API_KEY required for DeepInfra models");
  return {
    name: `deepinfra-${modelId.split("/").pop()}`,
    call: (system, user) => {
      const payload = JSON.stringify({
        model: modelId,
        messages: [
          { role: "system", content: system },
          { role: "user", content: user },
        ],
        max_tokens: 4096,
        temperature: 0.3,
      });
      const result = spawnSync("curl", [
        "-s", "-X", "POST",
        "https://api.deepinfra.com/v1/openai/chat/completions",
        "-H", "Content-Type: application/json",
        "-H", `Authorization: Bearer ${apiKey}`,
        "-d", payload,
      ], { encoding: "utf-8", timeout: 120_000 });
      if (result.error) throw new Error(`deepinfra error: ${result.error.message}`);
      const data = JSON.parse(result.stdout);
      return data.choices?.[0]?.message?.content ?? "";
    },
  };
}

function makeOpenRouterAdapter(modelId: string): ModelAdapter {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) throw new Error("OPENROUTER_API_KEY required for OpenRouter models");
  return {
    name: `openrouter-${modelId.split("/").pop()}`,
    call: (system, user) => {
      const payloadObj: Record<string, unknown> = {
        model: modelId,
        messages: [
          { role: "system", content: system },
          { role: "user", content: user },
        ],
        max_tokens: 4096,
        temperature: 0.3,
      };
      if (modelId === "deepseek/deepseek-v4-pro") {
        // Use the discounted official DeepSeek route. Do not silently fall
        // back to pricier OpenRouter hosts if the route is unavailable.
        payloadObj.provider = { only: ["deepseek"], allow_fallbacks: false };
      }
      const payload = JSON.stringify(payloadObj);
      const result = spawnSync("curl", [
        "-s", "-X", "POST",
        "https://openrouter.ai/api/v1/chat/completions",
        "-H", "Content-Type: application/json",
        "-H", `Authorization: Bearer ${apiKey}`,
        "-H", "HTTP-Referer: https://ashitaorbis.com",
        "-H", "X-Title: Psyche AI Assessment",
        "-d", payload,
      ], { encoding: "utf-8", timeout: 120_000 });
      if (result.error) throw new Error(`openrouter error: ${result.error.message}`);
      const data = JSON.parse(result.stdout);
      if (data.error) throw new Error(`openrouter API error: ${JSON.stringify(data.error)}`);
      return data.choices?.[0]?.message?.content ?? "";
    },
  };
}

/**
 * Anthropic-Messages-compatible adapter for the Chinese coding LLMs benchmarked
 * out of ~/chineseworkspace: GLM-5.2 (Zhipu / Z.ai) and Kimi K2.7 (Moonshot).
 * Both providers expose an Anthropic `/v1/messages` endpoint authed with a
 * Bearer token. Access facts mirror chineseworkspace/scripts/lib.sh EXACTLY
 * (do not reinvent the endpoint/model resolution):
 *   - zai:      base https://api.z.ai/api/anthropic, ZAI_API_KEY, model glm-5.2
 *   - moonshot: pay-per-token key (sk-…)   → https://api.moonshot.ai/anthropic, kimi-k2.7-code
 *               subscription  key (sk-kimi-…) → https://api.kimi.com/coding,      kimi-for-coding
 *
 * These are SUBJECT calls: they burn Z.ai / Moonshot quota, never Anthropic's.
 *
 * Kimi K2.7 has thinking ALWAYS ON — every response carries a `thinking` block
 * plus the answer `text` block. We concatenate only the `text` blocks (a bare
 * thinking-only response is treated as empty → the recovery wrapper retries; it
 * is NEVER coerced to a value). `max_tokens` is set generously so thinking never
 * starves the answer (a 64-token budget produced thinking-only / no answer).
 *
 * Temperature is deliberately OMITTED: the Anthropic thinking contract forbids a
 * custom temperature while extended thinking is on, and Kimi forces it on.
 */
function makeChineseAdapter(provider: "zai" | "moonshot", variant: string): ModelAdapter {
  let base: string;
  let token: string | undefined;
  let requestModel: string;
  let name: string;

  if (provider === "zai") {
    token = process.env.ZAI_API_KEY;
    if (!token) throw new Error("ZAI_API_KEY required for GLM (zai) models — source ~/chineseworkspace/.env");
    base = "https://api.z.ai/api/anthropic";
    requestModel = variant || process.env.GLM_MODEL || "glm-5.2";
    name = `zai-${requestModel.replace(/[^A-Za-z0-9.]+/g, "-")}`;
  } else {
    token = process.env.MOONSHOT_API_KEY;
    if (!token) throw new Error("MOONSHOT_API_KEY required for Kimi (moonshot) models — source ~/chineseworkspace/.env");
    // Key-type detection is authoritative (lib.sh kimi_is_subscription): a
    // subscription key routes to the Coding-Plan endpoint whose served model id
    // is the alias `kimi-for-coding` (NOT a pinned K2.x version — recorded as a
    // known limitation in provenance/servedModel).
    const subscription = token.startsWith("sk-kimi-");
    if (subscription) {
      base = "https://api.kimi.com/coding";
      requestModel = "kimi-for-coding";
    } else {
      base = "https://api.moonshot.ai/anthropic";
      requestModel = process.env.KIMI_MODEL || "kimi-k2.7-code";
    }
    // Keep the output/label aligned with the model we set out to test.
    name = `moonshot-${(variant || "kimi-k2.7").replace(/[^A-Za-z0-9.]+/g, "-")}`;
  }

  const adapter: ModelAdapter = {
    name,
    servedModelCounts: {},
    call: (system, user) => {
      const payload = JSON.stringify({
        model: requestModel,
        max_tokens: 8192,
        system,
        messages: [{ role: "user", content: user }],
      });
      const result = spawnSync("curl", [
        "-sS", "-m", "240",
        "-w", "\n%{http_code}",
        `${base}/v1/messages`,
        "-H", `Authorization: Bearer ${token}`,
        "-H", "anthropic-version: 2023-06-01",
        "-H", "content-type: application/json",
        "-d", payload,
      ], { encoding: "utf-8", timeout: 260_000, maxBuffer: 16 * 1024 * 1024 });

      if (result.error) throw new Error(`${provider} curl error: ${result.error.message}`);
      const out = result.stdout ?? "";
      const nl = out.lastIndexOf("\n");
      const code = (nl === -1 ? "" : out.slice(nl + 1)).trim();
      const body = nl === -1 ? out : out.slice(0, nl);
      if (code !== "200") {
        // Surface the code+body so looksRateLimited() can spot 429/529/overload
        // and back off longer instead of treating it as a hard failure.
        throw new Error(`${provider} HTTP ${code}: ${body.slice(0, 300)}`);
      }
      let data: any;
      try {
        data = JSON.parse(body);
      } catch {
        throw new Error(`${provider} non-JSON response: ${body.slice(0, 200)}`);
      }
      if (data.type === "error" || data.error) {
        throw new Error(`${provider} API error: ${JSON.stringify(data.error ?? data).slice(0, 300)}`);
      }
      // Record the served model id (contamination guard).
      const served: string | undefined = data.model;
      if (served) {
        adapter.lastServedModel = served;
        adapter.servedModelCounts![served] = (adapter.servedModelCounts![served] ?? 0) + 1;
      }
      // Concatenate ONLY text blocks — deliberately drop Kimi's `thinking` block.
      const text: string = Array.isArray(data.content)
        ? data.content.filter((b: any) => b?.type === "text").map((b: any) => b.text ?? "").join("").trim()
        : "";
      return text; // "" → callWithRecovery retries; never fabricated
    },
  };
  return adapter;
}

/**
 * Grok CLI adapter (xAI, subscription auth on this workstation) — 2026-08-05 roster
 * expansion. Mirrors the codex adapter's shape: headless one-shot spawn per
 * item, /tmp cwd, stdin closed, requested model id pinned explicitly (the
 * bare CLI default is a rolling alias). Media tools are irrelevant here; the
 * -p print path returns plain text on stdout.
 */
function makeGrokAdapter(variant: string): ModelAdapter {
  const model = variant; // explicit id, e.g. grok-4.5
  return {
    name: `grok-${model}`,
    call: (system, user) => {
      const fullPrompt = `${system}\n\n---\n\n${user}\n\nRespond with ONLY the JSON array.`;
      const result = spawnSync("grok", [
        "--permission-mode", "bypassPermissions",
        "-m", model,
        "-p", fullPrompt,
      ], {
        cwd: "/tmp",
        input: "",
        encoding: "utf-8",
        timeout: 180_000,
        maxBuffer: 1024 * 1024,
        env: { ...process.env, CLAUDECODE: undefined },
      });
      if (result.error) throw new Error(`grok error: ${result.error.message}`);
      if (result.status !== 0) {
        const errLine = (result.stderr || "").split("\n").filter(Boolean).slice(-1)[0] ?? "";
        throw new Error(`grok exit ${result.status}: ${errLine.slice(0, 300)}`);
      }
      return result.stdout.trim();
    },
  };
}

export function getAdapter(modelSpec: string): ModelAdapter {
  const sep = modelSpec.indexOf(":");
  if (sep === -1) throw new Error(`Model spec must be provider:variant (e.g., claude:opus). Got: ${modelSpec}`);
  const provider = modelSpec.slice(0, sep);
  const variant = modelSpec.slice(sep + 1);
  if (!variant) throw new Error(`Model spec must be provider:variant (e.g., claude:opus). Got: ${modelSpec}`);

  switch (provider) {
    case "claude": return makeClaudeAdapter(variant);
    case "codex": return makeCodexAdapter(variant);
    case "gemini": return makeGeminiAdapter(variant);
    case "deepinfra": return makeDeepInfraAdapter(variant);
    case "openrouter": return makeOpenRouterAdapter(variant);
    case "grok": return makeGrokAdapter(variant);
    // Chinese coding LLMs via Anthropic-compatible endpoints (chineseworkspace).
    case "zai": case "glm": return makeChineseAdapter("zai", variant);
    case "moonshot": case "kimi": return makeChineseAdapter("moonshot", variant);
    default: throw new Error(`Unknown provider: ${provider}`);
  }
}

// --- Prompt formatting ---

function formatInstrumentPrompt(instrument: Instrument): string {
  const items = instrument.items;
  if (items.length === 0) return "";

  const firstItem = items[0]!;
  let formatDesc = "";

  if (firstItem.response.type === "likert") {
    const { min, max, labels } = firstItem.response;
    formatDesc = `Rate each statement from ${min} (${labels[0]}) to ${max} (${labels[labels.length - 1]}).`;
    formatDesc += `\nRespond with a JSON array of ${items.length} integers.`;
  } else if (firstItem.response.type === "binary") {
    const [trueLabel, falseLabel] = firstItem.response.labels;
    formatDesc = `For each statement: 1 = ${trueLabel}, 0 = ${falseLabel}.`;
    formatDesc += `\nRespond with a JSON array of ${items.length} integers (1 or 0).`;
  } else if (firstItem.response.type === "numeric") {
    formatDesc = `Answer each question with a number.`;
    formatDesc += `\nRespond with a JSON array of ${items.length} numbers.`;
  } else if (firstItem.response.type === "text") {
    formatDesc = `Answer each question with a text response.`;
    formatDesc += `\nRespond with a JSON array of ${items.length} strings.`;
  }

  // Handle mixed-type instruments (CRT-7: 6 numeric + 1 text)
  const types = new Set(items.map(i => i.response.type));
  if (types.size > 1) {
    formatDesc = `This instrument has mixed response types. Respond with a JSON array of ${items.length} values:\n`;
    items.forEach((item, i) => {
      if (item.response.type === "numeric") {
        formatDesc += `  Item ${i + 1}: number\n`;
      } else if (item.response.type === "text") {
        formatDesc += `  Item ${i + 1}: string (letter or short text)\n`;
      } else if (item.response.type === "likert") {
        const r = item.response as { min: number; max: number };
        formatDesc += `  Item ${i + 1}: integer ${r.min}-${r.max}\n`;
      } else if (item.response.type === "binary") {
        formatDesc += `  Item ${i + 1}: 1 (True) or 0 (False)\n`;
      }
    });
  }

  let prompt = `## ${instrument.name}\n\n${formatDesc}\n\nItems:\n`;
  items.forEach((item, i) => {
    prompt += `${i + 1}. ${item.text}\n`;
  });

  return prompt;
}

function formatOpenEndedPrompt(instrument: Instrument): string {
  let prompt = `## ${instrument.name}\n\nAnswer each question thoughtfully in 2-5 sentences. Respond with a JSON array of ${instrument.items.length} strings.\n\nQuestions:\n`;
  instrument.items.forEach((item, i) => {
    prompt += `${i + 1}. ${item.text}\n`;
  });
  return prompt;
}

// --- Response parsing ---

function parseResponse(raw: string, expectedCount: number): (number | string)[] {
  // Try to extract JSON array from the response
  const trimmed = raw.trim();

  // Try direct parse
  try {
    const parsed = JSON.parse(trimmed);
    if (Array.isArray(parsed)) return parsed;
  } catch {}

  // Try extracting from markdown code block
  const codeBlockMatch = trimmed.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (codeBlockMatch) {
    try {
      const parsed = JSON.parse(codeBlockMatch[1]!.trim());
      if (Array.isArray(parsed)) return parsed;
    } catch {}
  }

  // Try extracting first JSON array from the text
  const arrayMatch = trimmed.match(/\[[\s\S]*?\]/);
  if (arrayMatch) {
    try {
      const parsed = JSON.parse(arrayMatch[0]);
      if (Array.isArray(parsed)) return parsed;
    } catch {}
  }

  console.error(`  Failed to parse response (expected ${expectedCount} items):`);
  console.error(`  ${trimmed.slice(0, 200)}...`);
  return [];
}

// --- Scoring ---

export function buildSession(instrument: Instrument, values: (number | string | null)[]): ItemResponse[] {
  // REMEDIATION: only ANSWERED items enter the scoring session. A missing value
  // is OMITTED (NOT coerced to 0/midpoint via the old `?? 0`), so the scoring
  // engine's `typeof value !== "number" → skip` path treats it as real
  // missingness and scales aggregate over genuine responses only.
  const responses: ItemResponse[] = [];
  instrument.items.forEach((item, i) => {
    const v = values[i];
    if (v === null || v === undefined) return; // MISSING — omit, never fabricate
    responses.push({ itemId: item.id, value: v, timestamp: Date.now() });
  });
  return responses;
}

// --- Chunked instrument execution ---

const CHUNK_SIZE = parseInt(process.env.PSYCHE_CHUNK_OVERRIDE ?? "1"); // Default 1 — see METHODOLOGY.md
// PSYCHE_ONLY_SCALES=hh,co — administer ONLY items whose scaleId is in the set;
// every other item is left null (MISSING, never called → never billed). Used for
// budget-capped PARTIAL runs (e.g. the Fable H-H facet under the weekly cap). The
// scorer/validity-gate handle the un-administered scales via the normal missing
// path (they void, exactly as for a failed item). chunk-1 only.
const ONLY_SCALES = (process.env.PSYCHE_ONLY_SCALES ?? "").split(",").map(s => s.trim()).filter(Boolean);
const SCALE_FILTER = ONLY_SCALES.length ? new Set(ONLY_SCALES) : null;
const SKIP_OPEN_ENDED = process.env.PSYCHE_SKIP_OPEN_ENDED === "1";
const ONLY_OPEN_ENDED = process.env.PSYCHE_ONLY_OPEN_ENDED === "1";
const RERUN_OPEN_ENDED = process.env.PSYCHE_RERUN_OPEN_ENDED === "1";
const RESUME_EXISTING = process.env.PSYCHE_RESUME === "1";
const RESULT_NAME_OVERRIDE = process.env.PSYCHE_RESULT_NAME;
// PSYCHE_ITEM_BUDGET=40 — administer at most N NEW items per invocation, then stop
// early (complete=false) so a 300-item instrument can be paced across 5-hour session
// windows. Already-answered items (from prior provenance) are reused for free and do
// NOT count against the budget. Undefined → no cap (whole instrument in one run).
const ITEM_BUDGET = process.env.PSYCHE_ITEM_BUDGET ? Math.max(1, parseInt(process.env.PSYCHE_ITEM_BUDGET, 10)) : undefined;
// Persist partial provenance every this-many new items (crash/kill safety).
const CHECKPOINT_EVERY = Math.max(1, parseInt(process.env.PSYCHE_CHECKPOINT_EVERY ?? "10", 10));

/** Refusal / premise-rejection language (checked when a value can't be cleanly parsed). */
const REFUSAL_RE = /\b(as an ai|i (don'?t|do not) (have|experience|possess)|i (can'?t|cannot|am unable to) (answer|rate|respond|assign)|not applicable|no personality|i (don'?t|do not) have (feelings|emotions|a personality)|decline to|refuse to|there'?s no meaningful way)\b/i;

/**
 * STRICT single-item classifier (chunk-1). Returns an explicit outcome:
 *   { status: "answered", answer: <value> }  ONLY for a cleanly-parseable response.
 * Everything else → status "refused" | "parse_fail" with answer:null. It NEVER
 * fabricates a midpoint/boundary/zero (the June bug). Ambiguity fails safe to
 * `parse_fail` (missing), which the scorer excludes.
 */
export function classifyResponse(raw: string, item: Item): { status: Outcome; answer: number | string | null } {
  const trimmed = raw.trim();
  if (!trimmed) return { status: "parse_fail", answer: null };

  // LENIENT UNWRAP (remediation gap-fill 2026-07): a single-element JSON array
  // (e.g. "[1]", "[0]", "[4]", ["B"]) is the most common wrapper models emit for
  // a single-item call. This was the ENTIRE cause of the GLM/Kimi self-monitoring
  // parse-fails: the binary branch had no single-token fallback (likert/numeric
  // already tolerate "[4]"/"[47]" via their matchAll paths). Unwrapping to the
  // element and re-classifying is a FAITHFUL re-parse of the model's real answer —
  // never fabrication. Only fires when the whole string is a 1-element JSON array,
  // so multi-value arrays and prose fall through to strict per-type parsing.
  if (/^\[[\s\S]*\]$/.test(trimmed)) {
    try {
      const arr = JSON.parse(trimmed);
      if (Array.isArray(arr) && arr.length === 1 && arr[0] !== null && arr[0] !== undefined) {
        return classifyResponse(String(arr[0]), item);
      }
    } catch { /* not valid JSON — fall through to normal parsing */ }
  }

  if (item.response.type === "text") {
    // Open-ended / CRT letter answer: any non-empty text is a genuine response.
    return { status: "answered", answer: trimmed };
  }

  if (item.response.type === "numeric") {
    const nums = [...trimmed.matchAll(/-?\d+(?:\.\d+)?/g)].map((m) => parseFloat(m[0]));
    const distinct = [...new Set(nums)];
    if (distinct.length === 1) return { status: "answered", answer: distinct[0]! };
    if (nums.length === 0) return { status: REFUSAL_RE.test(trimmed) ? "refused" : "parse_fail", answer: null };
    return { status: "parse_fail", answer: null }; // multiple distinct numbers → ambiguous
  }

  if (item.response.type === "binary") {
    if (/^\s*1\s*$/.test(trimmed) || /^\s*true\b/i.test(trimmed)) return { status: "answered", answer: 1 };
    if (/^\s*0\s*$/.test(trimmed) || /^\s*false\b/i.test(trimmed)) return { status: "answered", answer: 0 };
    const lead = trimmed.match(/^\s*([01])\b/);
    if (lead) return { status: "answered", answer: parseInt(lead[1]!) };
    // lenient fallback (mirrors likert/numeric): accept iff EXACTLY ONE distinct
    // standalone 0/1 token appears anywhere ("1 (True)" → 1). Ambiguity (0 tokens,
    // or both 0 and 1 present, e.g. a "0 or 1" hedge) fails safe to refused/parse_fail.
    const toks = [...trimmed.matchAll(/\b[01]\b/g)].map((m) => parseInt(m[0]));
    const distinct = [...new Set(toks)];
    if (distinct.length === 1) return { status: "answered", answer: distinct[0]! };
    return { status: REFUSAL_RE.test(trimmed) ? "refused" : "parse_fail", answer: null };
  }

  // Likert
  const resp = item.response as { min: number; max: number };
  // whole-string integer
  const whole = trimmed.match(/^\s*(-?\d+)\s*$/);
  if (whole) {
    const v = parseInt(whole[1]!);
    if (v >= resp.min && v <= resp.max) return { status: "answered", answer: v };
    return { status: "parse_fail", answer: null }; // out of range
  }
  // leading integer (e.g. "4.", "4 (Moderately Accurate)", "4/5")
  const lead = trimmed.match(/^\s*(-?\d+)\b/);
  if (lead) {
    const v = parseInt(lead[1]!);
    if (v >= resp.min && v <= resp.max) return { status: "answered", answer: v };
  }
  // otherwise: accept only if EXACTLY ONE distinct in-range integer appears anywhere
  const inRange = [...trimmed.matchAll(/\d+/g)].map((m) => parseInt(m[0])).filter((n) => n >= resp.min && n <= resp.max);
  const distinct = [...new Set(inRange)];
  if (distinct.length === 1) return { status: "answered", answer: distinct[0]! };
  // ambiguous (0 or >1 in-range digits) — this is where the old code fabricated
  return { status: REFUSAL_RE.test(trimmed) ? "refused" : "parse_fail", answer: null };
}

/**
 * Stricter format reminder appended on a parse-fail re-ask. Type-specific and
 * terse so it nudges format WITHOUT re-framing the item (which could shift the
 * answer). Used by the chunk-1 parse-fail recovery and by gapfill.ts.
 */
export function strictReminderFor(item: Item): string {
  if (item.response.type === "binary") {
    return `\n\nIMPORTANT: reply with EXACTLY one bare digit — 1 (True) or 0 (False). No array, no brackets, no words.`;
  }
  if (item.response.type === "likert") {
    const r = item.response as { min: number; max: number };
    return `\n\nIMPORTANT: reply with EXACTLY one bare integer ${r.min}-${r.max}. No array, no brackets, no words.`;
  }
  if (item.response.type === "numeric") {
    return `\n\nIMPORTANT: reply with EXACTLY one bare number. No array, no brackets, no words.`;
  }
  return `\n\nIMPORTANT: reply with your answer as plain text only.`;
}

/** Build a single-item prompt */
export function buildSingleItemPrompt(item: Item): string {
  if (item.response.type === "likert") {
    const { min, max, labels } = item.response;
    return `Rate this statement from ${min} (${labels[0]}) to ${max} (${labels[labels.length - 1]}).\n\nStatement: "${item.text}"\n\nRespond with a single integer ${min}-${max}.`;
  }
  if (item.response.type === "binary") {
    const [trueLabel, falseLabel] = item.response.labels;
    return `For this statement: 1 = ${trueLabel}, 0 = ${falseLabel}.\n\nStatement: "${item.text}"\n\nRespond with 1 or 0.`;
  }
  if (item.response.type === "numeric") {
    return `Answer this question with a number.\n\nQuestion: ${item.text}`;
  }
  if (item.response.type === "text") {
    return `Answer this question in 2-5 sentences.\n\nQuestion: ${item.text}`;
  }
  return item.text;
}

/** Full per-item provenance record (the audit trail the June run discarded). */
export interface ItemProvenance {
  itemId: string;
  scaleId: string;
  status: Outcome;
  answer: number | string | null;
  rawText: string;
  attempts: number;
  order: number;
  /** Model id the provider actually served for THIS item (contamination guard).
   *  Undefined for CLI adapters that don't surface a served id. */
  servedModel?: string;
}

export type ChunkResult = {
  raw: string;
  parsed: (number | string | null)[];
  provenance: ItemProvenance[];
  counts: Record<Outcome, number>;
  /** chunk-1 resumable path: false if the invocation stopped early on an item
   *  budget (more items remain to administer on the next resume). Undefined/true
   *  means every non-filtered item was attempted. */
  complete?: boolean;
  /** chunk-1: number of NEW api-calling items attempted this invocation. */
  attempted?: number;
};

/** Options for the resumable chunk-1 path (item budget + mid-instrument resume). */
export interface ChunkOpts {
  /** Provenance from a prior partial save — items already ANSWERED are reused
   *  (no API call, no re-billing), so a big instrument can span session windows. */
  priorProvenance?: ItemProvenance[];
  /** Max NEW api-calling items to administer this invocation (NEO-300 batching).
   *  When reached, the loop stops early and complete=false. */
  itemBudget?: number;
  /** Called every `checkpointEvery` new items with a snapshot of partial state so
   *  a mid-instrument kill loses at most that many. */
  onCheckpoint?: (partial: { parsed: (number | string | null)[]; provenance: ItemProvenance[]; counts: Record<Outcome, number> }) => void;
  /** Checkpoint frequency (new items). Defaults to CHECKPOINT_EVERY (env). */
  checkpointEvery?: number;
}

function emptyCounts(): Record<Outcome, number> {
  return { answered: 0, refused: 0, parse_fail: 0, api_error: 0, timeout: 0, empty: 0 };
}

export function runInstrumentChunked(
  instrument: Instrument,
  adapter: ModelAdapter,
  opts?: ChunkOpts,
): ChunkResult {
  const items = instrument.items;

  if (CHUNK_SIZE === 1) {
    // Single-item mode — each item gets its own API call.
    // REMEDIATION: never fabricate. A non-answered item is recorded with its
    // outcome code and pushed as `null` (the scorer excludes it as MISSING).
    const total = items.length;
    // Index-aligned so early-stop (item budget) leaves the tail null (MISSING)
    // and a later resume fills it in place.
    const allParsed: (number | string | null)[] = new Array(total).fill(null);
    const provenance: ItemProvenance[] = [];
    const counts = emptyCounts();

    // Item-level resume: reuse already-ANSWERED items from a prior partial save so
    // a paused big instrument continues where it left off (no re-billing).
    const prior = new Map<string, ItemProvenance>();
    for (const p of opts?.priorProvenance ?? []) prior.set(p.itemId, p);
    const budget = opts?.itemBudget ?? Infinity;
    let newCalls = 0;
    let stoppedEarly = false;

    for (let i = 0; i < total; i++) {
      const item = items[i]!;
      // Budget-capped PARTIAL run: items outside the scale filter are never
      // administered (no API call, no billing). Left null → MISSING, handled by
      // the scorer/gate exactly like any un-answered item.
      if (SCALE_FILTER && !SCALE_FILTER.has(item.scaleId)) {
        allParsed[i] = null;
        continue;
      }
      // Resume: an item already answered in a prior invocation is reused verbatim
      // (its provenance, incl. servedModel, is preserved) — no API call, no bill.
      const pr = prior.get(item.id);
      if (pr && pr.status === "answered") {
        allParsed[i] = pr.answer;
        provenance.push(pr);
        counts[pr.status]++;
        continue;
      }
      // Item budget exhausted for THIS invocation — stop; the tail stays MISSING
      // and the next resume continues from here.
      if (newCalls >= budget) { stoppedEarly = true; break; }
      const prompt = buildSingleItemPrompt(item);
      const outcome = callWithRecovery(adapter, SYSTEM_PROMPT, prompt);

      let status: Outcome;
      let answer: number | string | null;
      let rawText: string;
      let attempts = outcome.attempts;
      if (outcome.ok) {
        let c = classifyResponse(outcome.raw, item);
        rawText = outcome.raw;
        // PARSE-FAIL RECOVERY: a clean answer that merely violated the format
        // (wrapped/verbose) is first rescued by classifyResponse's lenient parse.
        // If it STILL doesn't parse, re-ask ONCE with a stricter format reminder
        // before recording parse_fail — a genuine refusal will refuse again;
        // a format slip usually corrects. Never fabricates a value.
        if (c.status === "parse_fail") {
          const retry = callWithRecovery(adapter, SYSTEM_PROMPT, prompt + strictReminderFor(item));
          attempts += retry.attempts;
          if (retry.ok) {
            const c2 = classifyResponse(retry.raw, item);
            if (c2.status === "answered") { c = c2; rawText = retry.raw; }
            else { rawText = `${outcome.raw}\n--- reask ---\n${retry.raw}`; }
          }
        }
        status = c.status;
        answer = c.answer;
      } else {
        status = outcome.reason; // "empty" | "api_error" | "timeout"
        answer = null;
        rawText = `__${outcome.reason.toUpperCase()}__: ${outcome.detail}`;
      }

      counts[status]++;
      allParsed[i] = answer;
      provenance.push({ itemId: item.id, scaleId: item.scaleId, status, answer, rawText, attempts, order: i, servedModel: adapter.lastServedModel });
      newCalls++;

      if ((i + 1) % 25 === 0) console.log(`    ${i + 1}/${total} items... (answered ${counts.answered})`);
      // Crash-safe incremental checkpoint (partial provenance persisted by caller).
      const ckEvery = opts?.checkpointEvery ?? CHECKPOINT_EVERY;
      if (opts?.onCheckpoint && newCalls % ckEvery === 0) {
        opts.onCheckpoint({ parsed: allParsed.slice(), provenance: provenance.slice(), counts: { ...counts } });
      }
    }

    const attemptedItems = provenance.length; // reused + newly attempted (non-filtered)
    const missing = attemptedItems - counts.answered;
    if (missing > 0) console.warn(`    ${missing} non-answered → recorded as MISSING (not backfilled): ${JSON.stringify(counts)}`);
    if (stoppedEarly) console.log(`    item budget ${budget} reached — ${newCalls} new this run, ${provenance.length}/${total} items done; PARTIAL (resume to continue)`);
    return {
      raw: `[${provenance.length}/${total} items | answered ${counts.answered} refused ${counts.refused} parse_fail ${counts.parse_fail} api_error ${counts.api_error} timeout ${counts.timeout} empty ${counts.empty}${stoppedEarly ? " | PARTIAL" : ""}]`,
      parsed: allParsed,
      provenance,
      counts,
      complete: !stoppedEarly,
      attempted: newCalls,
    };
  }

  // Batched mode (CHUNK_SIZE > 1). NOTE: batched administration is a distinct
  // measurement condition (priming) and is NOT the remediation's primary arm;
  // it does not carry per-item provenance. Use chunk-1 for the honest run.
  if (instrument.itemCount <= CHUNK_SIZE) {
    const prompt = formatInstrumentPrompt(instrument);
    const raw = callWithRetry(adapter, SYSTEM_PROMPT, prompt);
    const parsed = parseResponse(raw, instrument.itemCount);
    return { raw, parsed, provenance: [], counts: emptyCounts() };
  }

  const firstItem = items[0]!;
  const allParsed: (number | string)[] = [];
  const allRaw: string[] = [];
  const chunkCount = Math.ceil(items.length / CHUNK_SIZE);

  for (let c = 0; c < chunkCount; c++) {
    const start = c * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, items.length);
    const chunkItems = items.slice(start, end);
    const chunkSize = chunkItems.length;

    let formatDesc = "";
    if (firstItem.response.type === "likert") {
      const { min, max, labels } = firstItem.response;
      formatDesc = `Rate each statement from ${min} (${labels[0]}) to ${max} (${labels[labels.length - 1]}).`;
      formatDesc += `\nRespond with a JSON array of ${chunkSize} integers.`;
    } else if (firstItem.response.type === "binary") {
      const [trueLabel, falseLabel] = firstItem.response.labels;
      formatDesc = `For each statement: 1 = ${trueLabel}, 0 = ${falseLabel}.`;
      formatDesc += `\nRespond with a JSON array of ${chunkSize} integers (1 or 0).`;
    }

    let prompt = `## ${instrument.name} (items ${start + 1}-${end} of ${items.length})\n\n${formatDesc}\n\nItems:\n`;
    chunkItems.forEach((item, i) => {
      prompt += `${start + i + 1}. ${item.text}\n`;
    });

    console.log(`    chunk ${c + 1}/${chunkCount} (items ${start + 1}-${end})...`);
    const raw = callWithRetry(adapter, SYSTEM_PROMPT, prompt);
    allRaw.push(raw);

    const parsed = parseResponse(raw, chunkSize);
    if (parsed.length !== chunkSize) {
      console.warn(`      WARNING: chunk got ${parsed.length} values, expected ${chunkSize}`);
    }
    allParsed.push(...parsed);
  }

  return { raw: allRaw.join("\n---\n"), parsed: allParsed, provenance: [], counts: emptyCounts() };
}

// --- Resolved model id (guards silent alias drift; June files recorded none) ---

/** Best-effort capture of the resolved full model id. For claude, reads the
 *  --output-format json envelope's `modelUsage` map (keyed by resolved id). */
function resolveModelId(modelSpec: string): string {
  const sep = modelSpec.indexOf(":");
  const provider = modelSpec.slice(0, sep);
  const variant = modelSpec.slice(sep + 1);
  if (provider === "claude") {
    const model = ({ opus: "opus", sonnet: "sonnet", haiku: "haiku", "opus-5": "claude-opus-5" } as Record<string, string>)[variant] ?? variant;
    try {
      const r = spawnSync("claude", ["-p", "--model", model, "--output-format", "json", "--no-session-persistence", "Reply with only the digit 1."], {
        cwd: "/tmp",
        env: { ...process.env, CLAUDECODE: undefined, ANTHROPIC_API_KEY: undefined },
        encoding: "utf-8", timeout: 60_000, maxBuffer: 1024 * 1024,
      });
      if (r.status === 0 && r.stdout) {
        const env = JSON.parse(r.stdout);
        const keys = Object.keys(env.modelUsage ?? {});
        if (keys.length) return keys.join(",");
      }
    } catch { /* best effort — fall through */ }
    return `alias:${model}`;
  }
  if (provider === "zai" || provider === "glm") {
    return process.env.GLM_MODEL || variant || "glm-5.2";
  }
  if (provider === "moonshot" || provider === "kimi") {
    // The actual request model depends on key type (subscription → alias
    // `kimi-for-coding`). The truth is recorded per-call in servedModelDistribution.
    const tok = process.env.MOONSHOT_API_KEY ?? "";
    return tok.startsWith("sk-kimi-") ? "kimi-for-coding (Coding-Plan alias)" : (process.env.KIMI_MODEL || "kimi-k2.7-code");
  }
  return variant.split(":")[0] ?? variant; // codex/gemini: requested id is explicit
}

// --- Main ---

async function main() {
  const modelSpec = process.argv.find(a => a.startsWith("--model="))?.split("=")[1]
    ?? process.argv[process.argv.indexOf("--model") + 1];

  if (!modelSpec) {
    console.error("Usage: npx tsx run.ts --model claude:opus");
    console.error("Models: claude:{opus|sonnet|haiku}, codex:{gpt-5.4|gpt-5.3-instant}, gemini:{pro|flash}, deepinfra:{model-id}, openrouter:{model-id}, zai:glm-5.2, moonshot:kimi-k2.7");
    process.exit(1);
  }

  const adapter = getAdapter(modelSpec);
  console.log(`\n=== AI Personality Assessment: ${adapter.name} ===\n`);

  const resolvedModel = resolveModelId(modelSpec);
  console.log(`Resolved model id: ${resolvedModel}  (spec: ${modelSpec})\n`);

  // PSYCHE_INSTRUMENTS=mfq-2,scs-26,... — administer an EXPLICIT list of any
  // registered instruments (not the standard tier), for the heavy-tier supplement.
  // When set, open-ended is skipped unless explicitly listed. Otherwise: standard tier.
  const SUPPLEMENT = process.env.PSYCHE_SUPPLEMENT === "1";
  const EXPLICIT = (process.env.PSYCHE_INSTRUMENTS ?? "").split(",").map(s => s.trim()).filter(Boolean);
  let instrumentIds = EXPLICIT.length
    ? EXPLICIT
    // Get Standard tier instruments (excluding CAT which requires item banks)
    : getInstrumentsForTier("standard").filter(id => !id.startsWith("cat-") && id !== "open-ended");
  if (EXPLICIT.length) console.log(`[PSYCHE_INSTRUMENTS] explicit list: ${instrumentIds.join(", ")}`);

  // PSYCHE_ONLY_INSTRUMENT=swls[,crt-7,...] — restrict to a comma-separated
  // subset (smoke testing / debugging a single instrument). Also forces
  // SKIP_OPEN_ENDED unless the open-ended id is explicitly listed.
  const ONLY_INSTRUMENT = process.env.PSYCHE_ONLY_INSTRUMENT;
  // Supplement/explicit runs never include the open-ended interview unless listed.
  let smokeSkipOpenEnded = EXPLICIT.length ? !EXPLICIT.includes("open-ended") : false;
  if (ONLY_INSTRUMENT) {
    const wanted = new Set(ONLY_INSTRUMENT.split(",").map(s => s.trim()).filter(Boolean));
    instrumentIds = instrumentIds.filter(id => wanted.has(id));
    smokeSkipOpenEnded = !wanted.has("open-ended");
    console.log(`[PSYCHE_ONLY_INSTRUMENT] restricted to: ${instrumentIds.join(", ") || "(none matched)"}`);
  }

  console.log(`Instruments: ${instrumentIds.length} quantitative + open-ended interview`);
  console.log(`Instruments: ${instrumentIds.join(", ")}\n`);

  let allResults: InstrumentResult[] = [];
  // rawResponses now carries first-class per-item provenance + outcome counts.
  const rawResponses: Record<string, {
    prompt: string;
    raw: string;
    parsed: (number | string | null)[];
    counts?: Record<string, number>;
    provenance?: unknown[];
    validity?: ScaleValidity[];
  }> = {};
  const resultName = RESULT_NAME_OVERRIDE ?? adapter.name;
  const outPath = resolve(RESULTS_DIR, `${resultName}.json`);

  // Durable file-level annotations (e.g. the budget-capped PARTIAL Fable arm's
  // `partialArm` flag + notes) that saveOutput's fresh-object rebuild would
  // otherwise silently drop on every resume. Preserved across resume invocations.
  let preservedMeta: Record<string, unknown> = {};
  if ((ONLY_OPEN_ENDED || RESUME_EXISTING) && existsSync(outPath)) {
    const existing = JSON.parse(readFileSync(outPath, "utf-8"));
    allResults = existing.results ?? [];
    Object.assign(rawResponses, existing.rawResponses ?? {});
    for (const k of ["partialArm", "partialArmNote", "costModelNote"]) {
      if (existing[k] !== undefined) preservedMeta[k] = existing[k];
    }
    // Merge prior served-model + usage aggregates so per-instrument resume
    // invocations ACCUMULATE (else saveOutput overwrites servedModelDistribution
    // and subjectUsage with only the current invocation's calls, silently losing
    // earlier instruments' swap counts + measured cost). Per-item
    // provenance[].servedModel stays the ground truth for swap accounting.
    if (adapter.servedModelCounts && existing.servedModelDistribution) {
      for (const [k, v] of Object.entries(existing.servedModelDistribution)) {
        adapter.servedModelCounts[k] = (adapter.servedModelCounts[k] ?? 0) + (v as number);
      }
    }
    if (existing.subjectUsage) {
      adapter.usageTotals = { ...existing.subjectUsage };
    }
    console.log(`Loaded existing results from ${outPath}`);
  }

  const saveOutput = () => {
    // Aggregate response-validity metrics across all instruments (first-class output).
    const agg: Record<string, number> = {};
    for (const rr of Object.values(rawResponses)) {
      for (const [k, v] of Object.entries(rr.counts ?? {})) agg[k] = (agg[k] ?? 0) + (v as number);
    }
    const totalItems = Object.values(agg).reduce((s, v) => s + v, 0);
    const output = {
      model: adapter.name,
      modelSpec,
      resolvedModel,
      pipelineVersion: "remediation-2026-07 (no-fabricate + provenance + validity-gate)",
      tier: "standard",
      timestamp: new Date().toISOString(),
      instrumentCount: allResults.length,
      responseValidity: {
        totalItems,
        counts: agg,
        validRate: totalItems ? (agg.answered ?? 0) / totalItems : 0,
      },
      // Contamination guard: distribution of provider-served model ids across
      // every subject call. A single key = no silent substitution. Empty for
      // CLI adapters that don't surface a served id.
      servedModelDistribution: adapter.servedModelCounts ?? {},
      // Measured token/cost accounting (claude --output-format json only). Grounds
      // the Fable cost extrapolation in the provider's own numbers. Null for
      // adapters that don't surface usage.
      subjectUsage: adapter.usageTotals ?? null,
      results: allResults,
      rawResponses,
      // SUPPLEMENT: research-use-restricted heavy-tier instruments captured on ONE
      // model (no peer set). analyze.py must exclude this file from peer tables.
      ...(SUPPLEMENT ? { supplement: true } : {}),
      // Carry forward durable annotations (partialArm flag/notes) so resume runs
      // don't strip the PARTIAL labeling that analyze.py keys off.
      ...preservedMeta,
    };
    // Atomic write (tmp + rename): frequent mid-instrument checkpoints must never
    // leave a half-written JSON if the process is killed at a session-pause.
    const tmp = `${outPath}.tmp`;
    writeFileSync(tmp, JSON.stringify(output, null, 2));
    renameSync(tmp, outPath);
  };

  // Run each quantitative instrument
  if (ONLY_OPEN_ENDED) {
    console.log("Quantitative instruments skipped (PSYCHE_ONLY_OPEN_ENDED=1)");
  } else {
    for (const id of instrumentIds) {
      const registered = getInstrument(id);
      if (!registered) {
        console.warn(`  [SKIP] ${id}: not registered`);
        continue;
      }

      const { instrument, score } = registered;
      if (RESUME_EXISTING && allResults.some(r => r.instrumentId === id)) {
        console.log(`  ${instrument.shortName} (${instrument.itemCount} items)... already complete`);
        continue;
      }
      console.log(`  ${instrument.shortName} (${instrument.itemCount} items)...`);

      const startTime = Date.now();

      let result: ChunkResult;
      try {
        // Item-level resume: feed back this instrument's prior partial provenance
        // (loaded from the file) so already-answered items are reused for free.
        // onCheckpoint persists partial state every CHECKPOINT_EVERY new items so a
        // session-pause kill loses at most that many. itemBudget paces NEO-300
        // across 5-hour windows.
        const priorProv = (rawResponses[id]?.provenance as ItemProvenance[] | undefined);
        result = runInstrumentChunked(instrument, adapter, {
          priorProvenance: priorProv,
          itemBudget: ITEM_BUDGET,
          onCheckpoint: (partial) => {
            rawResponses[id] = {
              prompt: `[chunk-1: ${instrument.itemCount} single-item calls]`,
              raw: `[checkpoint: ${partial.provenance.length}/${instrument.itemCount} items | answered ${partial.counts.answered}]`,
              parsed: partial.parsed,
              counts: partial.counts,
              provenance: partial.provenance,
            };
            saveOutput();
          },
        });
      } catch (err: any) {
        console.error(`    ERROR: ${err.message}`);
        rawResponses[id] = { prompt: "", raw: `ERROR: ${err.message}`, parsed: [] };
        saveOutput();
        continue;
      }

      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
      const values = result.parsed;

      rawResponses[id] = {
        prompt: `[chunk-1: ${instrument.itemCount} single-item calls]`,
        raw: result.raw,
        parsed: values,
        counts: result.counts,
        provenance: result.provenance,
      };

      // PARTIAL (item budget hit): persist raw provenance, do NOT score or push to
      // allResults — so the next resume re-enters this instrument and continues.
      if (result.complete === false) {
        const answeredSoFar = result.counts.answered;
        console.log(`    PARTIAL (${elapsed}s) — ${result.provenance.length}/${instrument.itemCount} items done (${answeredSoFar} answered); saved, resume to continue.`);
        saveOutput();
        continue;
      }

      if (values.length !== instrument.itemCount) {
        console.warn(`    WARNING: got ${values.length} values, expected ${instrument.itemCount}`);
      }

      // Answered-item set drives both scoring (only answered enter the session)
      // and the validity gate. Robust across chunk-1 (nulls) and batched (short).
      const answeredItemIds = new Set<string>();
      instrument.items.forEach((it, i) => {
        const v = values[i];
        if (v !== null && v !== undefined) answeredItemIds.add(it.id);
      });

      if (answeredItemIds.size > 0) {
        const session = buildSession(instrument, values);
        try {
          const scored = score(instrument, {
            instrumentId: id,
            startedAt: Date.now(),
            completedAt: Date.now(),
            responses: session,
          });
          const gated = gateInstrument(instrument, scored, answeredItemIds);
          allResults.push(gated.result);
          rawResponses[id]!.validity = gated.validity;
          const voidN = gated.validity.filter(v => v.verdict === "void").length;
          const proratedN = gated.validity.filter(v => v.verdict === "prorated").length;
          const topScores = gated.result.scores.slice(0, 3)
            .map(s => `${s.scaleName}: ${Math.round(s.normalized)}${s.incomplete ? "*" : ""}`).join(", ");
          console.log(`    OK (${elapsed}s) — answered ${answeredItemIds.size}/${instrument.itemCount}; ${voidN} void, ${proratedN} prorated — ${topScores}...`);
          saveOutput();
        } catch (err: any) {
          console.error(`    SCORE ERROR: ${err.message}`);
          saveOutput();
        }
      } else {
        console.warn(`    ALL ${instrument.itemCount} items missing → instrument VOID (no score emitted, NOT backfilled)`);
        saveOutput();
      }
    }
  }

  // Run open-ended interview
  const openEnded = getInstrument("open-ended");
  const hasOpenEnded = allResults.some(r => r.instrumentId === "open-ended");
  if (openEnded && !SKIP_OPEN_ENDED && !smokeSkipOpenEnded && (!hasOpenEnded || RERUN_OPEN_ENDED)) {
    if (RERUN_OPEN_ENDED) {
      allResults = allResults.filter(r => r.instrumentId !== "open-ended");
      delete rawResponses["open-ended"];
    }
    console.log(`\n  Open-Ended Interview (${openEnded.instrument.itemCount} questions)...`);
    const prompt = formatOpenEndedPrompt(openEnded.instrument);
    const startTime = Date.now();

    let raw: string;
    try {
      raw = callWithRetry(adapter, SYSTEM_PROMPT, prompt);
    } catch (err: any) {
      console.error(`    ERROR: ${err.message}`);
      raw = `ERROR: ${err.message}`;
    }

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    const values = parseResponse(raw, openEnded.instrument.itemCount);
    rawResponses["open-ended"] = { prompt, raw, parsed: values };

    if (values.length > 0) {
      const session = buildSession(openEnded.instrument, values);
      const result = openEnded.score(openEnded.instrument, {
        instrumentId: "open-ended",
        startedAt: Date.now(),
        completedAt: Date.now(),
        responses: session,
      });
      allResults.push(result);
      console.log(`    OK (${elapsed}s) — ${values.length} responses collected`);
      saveOutput();
    }
  } else if (openEnded && SKIP_OPEN_ENDED) {
    console.log(`\n  Open-Ended Interview skipped (PSYCHE_SKIP_OPEN_ENDED=1)`);
  } else if (openEnded && hasOpenEnded) {
    console.log(`\n  Open-Ended Interview already present (set PSYCHE_RERUN_OPEN_ENDED=1 to replace it)`);
  }

  // Save results
  saveOutput();
  console.log(`\nResults saved to ${outPath}`);

  // Summary
  console.log(`\n=== Summary: ${adapter.name} ===`);
  for (const result of allResults) {
    if (result.instrumentId === "open-ended") continue;
    console.log(`  ${result.instrumentId}:`);
    for (const score of result.scores) {
      console.log(`    ${score.scaleName}: ${Math.round(score.normalized)}%`);
    }
  }
}

// Only auto-run main() when run.ts is the ENTRY module. Keying off "--model" in
// argv alone is wrong: gapfill.ts imports run.ts AND passes --model, which used to
// trigger run.ts's own main() on import (spurious adapter/ZAI errors). Guard on the
// entry script's basename so importers (gapfill.ts, test-remediation.ts) never do.
const entryBase = (process.argv[1] ?? "").split("/").pop() ?? "";
const invokedDirectly = entryBase === "run.ts" && process.argv.some(a => a === "--model" || a.startsWith("--model="));
if (invokedDirectly) {
  main().catch(err => {
    console.error("Fatal:", err);
    process.exit(1);
  });
}
