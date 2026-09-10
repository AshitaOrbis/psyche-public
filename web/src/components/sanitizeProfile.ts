/**
 * Defensive sanitizer for imported / fetched profile JSON (psy-8, security
 * review P2-1). The ProfileDashboard renders profile fields directly as React
 * text and — critically — as CSS dimensions (`width: ${ci_upper - ci_lower}%`,
 * `left: ${final_score}%`). Unbounded values there produce broken/overflowing
 * layout; oversized strings/arrays bloat memory and the DOM.
 *
 * This mirrors the store's import sanitizers (`sanitizeImportedResults` /
 * `sanitizeImportedSessions` in state/store.ts): clamp percentile scores to
 * [0, 100], cap string/array lengths, and drop nothing that's structurally
 * fine. It does NOT validate the full schema (the dashboard already gates on
 * `big_five && version`); it neutralizes hostile values in an otherwise
 * shaped object.
 *
 * The score clamp is applied to every number EXCEPT keys that are legitimately
 * outside [0, 100] (raw counts, the schema version, the 0–7 CRT score, IRT
 * theta/se, lexical z-scores, divergence). Everything else is treated as a
 * 0–100 percentile-style score and clamped.
 */

/** Max length for any free-text string in the profile. */
const MAX_STRING_LENGTH = 100_000;
/** Max length for any array in the profile. */
const MAX_ARRAY_LENGTH = 2_000;
/** Max object/array nesting depth to walk (defends against pathological JSON). */
const MAX_DEPTH = 12;

/**
 * Numeric keys that are NOT 0–100 percentile scores and must not be clamped.
 * Anything else numeric is clamped to [0, 100].
 */
const NON_SCORE_NUMERIC_KEYS = new Set<string>([
  "version",
  "crt_score", // 0–7
  "corpus_word_count",
  "llm_tokens_used",
  "corpus_words",
  "words_to_llm",
  "empath_words",
  "divergence",
  "theta",
  "se",
  "z", // empath lexical z-score (can be negative / >100)
]);

function clampScore(n: number): number {
  if (!Number.isFinite(n)) return 0;
  return Math.max(0, Math.min(100, n));
}

/**
 * Recursively sanitize a parsed JSON value in place-safe fashion (returns a
 * new sanitized value; does not mutate the input). `key` is the property name
 * this value was reached under, used to decide whether a number is a score.
 */
function sanitizeValue(value: unknown, key: string | null, depth: number): unknown {
  if (depth > MAX_DEPTH) return null;

  if (typeof value === "string") {
    return value.length > MAX_STRING_LENGTH ? value.slice(0, MAX_STRING_LENGTH) : value;
  }

  if (typeof value === "number") {
    if (!Number.isFinite(value)) return 0;
    if (key !== null && NON_SCORE_NUMERIC_KEYS.has(key)) return value;
    return clampScore(value);
  }

  if (Array.isArray(value)) {
    const capped = value.length > MAX_ARRAY_LENGTH ? value.slice(0, MAX_ARRAY_LENGTH) : value;
    // Array elements inherit the array's key context (e.g. an `estimates`
    // array of objects), so pass `null` so element scalars use generic rules.
    return capped.map((v) => sanitizeValue(v, null, depth + 1));
  }

  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = sanitizeValue(v, k, depth + 1);
    }
    return out;
  }

  // boolean | null | undefined — passthrough.
  return value;
}

/**
 * Sanitize a parsed profile object. Returns a sanitized clone. Accepts the
 * loose `unknown` the caller gets from `JSON.parse`; the caller still gates on
 * `big_five && version` before rendering.
 */
export function sanitizeImportedProfile<T>(raw: T): T {
  return sanitizeValue(raw, null, 0) as T;
}
