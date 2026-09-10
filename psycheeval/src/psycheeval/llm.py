"""LLM client wrapper for PsycheEval.

Two model families, each callable via subprocess CLI (workspace convention):
- Opus 4.7 via `claude -p --model opus` (Claude Max plan, no API key)
- GPT-5.4 via `codex exec --skip-git-repo-check -s read-only`

Both return a `LLMResponse`. The `extract_json` helper parses JSON-only
responses with tolerant fallbacks (strip ``` fences, find outermost braces).
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Literal

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

# --- Model registry ---------------------------------------------------------

ModelId = Literal["opus", "gpt-5.4", "gpt-5.5-xhigh", "kimi-k2.6", "deepseek-v4-pro"]


@dataclass
class ModelSpec:
    key: str
    provider: Literal["claude-cli", "codex-cli", "openrouter-api"]
    resolved_id: str
    # Provider-family taxonomy (used by halo classification).
    # provider_family: "anthropic" | "openai" | "moonshot" | …
    # model_family:    e.g. "gpt-5.4", "gpt-5.5", "claude-opus-4"
    provider_family: str = ""
    model_family: str = ""
    reasoning_effort: str | None = None  # e.g. "xhigh" for codex-cli; None = wrapper default
    display_name: str | None = None
    cost_in_per_mtok: float | None = None
    cost_out_per_mtok: float | None = None
    # CLI --model argument override. When set, the claude-cli / codex-cli call
    # uses this instead of resolved_id, while records keep judge_model =
    # resolved_id. Decouples "what version we invoke" from "how the record is
    # labelled". Used to pin opus to claude-opus-4-7 at the CLI while keeping
    # the record label "opus" stable for dedup + analyzer grouping (2026-06-16).
    cli_model: str | None = None


MODELS: dict[str, ModelSpec] = {
    "opus": ModelSpec(
        key="opus",
        provider="claude-cli",
        resolved_id="opus",  # record label (judge_model="opus") — kept stable
        # PINNED 2026-06-16: the bare `opus` alias rolled to Opus 4.8 in 2026-06.
        # The v0.2 corpus and original v0.3 corpus were generated on 4.7; mixing
        # 4.8 records silently contaminates the dataset. cli_model forces the
        # actual `claude -p --model` arg to the explicit 4.7 id while records
        # stay labelled "opus" (so dedup + analyzer treat all opus as one judge).
        # Verified claude-opus-4-7 still available on 2026-06-16.
        cli_model="claude-opus-4-7",
        provider_family="anthropic",
        model_family="claude-opus",
        display_name="Opus 4.7",
    ),
    "gpt-5.4": ModelSpec(
        key="gpt-5.4",
        provider="codex-cli",
        resolved_id="gpt-5.4",
        provider_family="openai",
        model_family="gpt-5.4",
        reasoning_effort="xhigh",  # matches existing ~/.codex/config.toml default
        display_name="GPT-5.4 xhigh",
    ),
    "gpt-5.5-xhigh": ModelSpec(
        key="gpt-5.5-xhigh",
        provider="codex-cli",
        resolved_id="gpt-5.5",
        provider_family="openai",
        model_family="gpt-5.5",
        reasoning_effort="xhigh",
        display_name="GPT-5.5 xhigh",
    ),
    "kimi-k2.6": ModelSpec(
        key="kimi-k2.6",
        provider="openrouter-api",
        resolved_id="moonshotai/kimi-k2.6",
        provider_family="moonshot",
        model_family="kimi-k2",
        cost_in_per_mtok=0.00000075,
        cost_out_per_mtok=0.0000035,
    ),
    "deepseek-v4-pro": ModelSpec(
        key="deepseek-v4-pro",
        provider="openrouter-api",
        resolved_id="deepseek/deepseek-v4-pro",
        provider_family="deepseek",
        model_family="deepseek-v4-pro",
        cost_in_per_mtok=0.000000435,
        cost_out_per_mtok=0.00000087,
    ),
}


@dataclass
class LLMResponse:
    model_key: str
    model_resolved: str
    content: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    elapsed_s: float = 0.0
    raw: dict = field(default_factory=dict)
    # v0.2-tri-model metadata (populated by wrapper for halo classification)
    provider_family: str = ""
    model_family: str = ""
    reasoning_effort: str | None = None


# --- Claude CLI -------------------------------------------------------------


class ClaudeCLIError(RuntimeError):
    pass


class ClaudeCapError(ClaudeCLIError):
    """Raised specifically when ``claude -p`` indicates the rolling 5-hour
    usage cap (or a rate-limit equivalent) has been hit. Distinct from generic
    ClaudeCLIError so callers (notably judge.py's CapBurnHandler) can back off
    on cap and fall through on other errors. Carries the original stderr for
    diagnostics."""

    def __init__(self, message: str, stderr: str = "", returncode: int = 1) -> None:
        super().__init__(message)
        self.stderr = stderr
        self.returncode = returncode


# Markers that indicate the failure was a cap-burn / rate-limit, not some other
# CLI error. Lowercased; substring match. Updated whenever a new cap-style
# stderr surfaces (the Anthropic CLI wording has shifted historically).
_CLAUDE_CAP_MARKERS = (
    "usage limit",
    "you've hit your usage limit",
    "you have hit your usage limit",
    # Observed 2026-05-20 during v0.3 Opus run — Anthropic shortened the
    # message; no "usage" word. Both apostrophe forms observed in stdout.
    "you've hit your limit",
    "you have hit your limit",
    "hit your limit · resets",
    "limit · resets",
    "5-hour limit",
    "5 hour limit",
    "rolling 5-hour",
    "rate limit",
    "rate_limit",
    "rate-limited",
    "usage_limit_reached",
    "claude_usage_limit",
    "anthropic api error: 429",
    "anthropic api error 429",
    "too many requests",
    "quota exhausted",
    "your account has reached",
)


# Burst-rate detector. Module-level because cap state is process-global:
# any worker that sees a rapid burst of rc!=0 calls is evidence that the
# whole process is in cap, regardless of which judge model the failures
# came from. The 2026-05-13 incident burned ~800 records through this hole
# — individual calls returned rc=1 with content that didn't match any
# content-based heuristic, so the only signature left was *timing*.
_BURST_LOCK = threading.Lock()
_BURST_FAIL_TS: list[float] = []  # timestamps of recent rc!=0 from claude -p

# Treat rc!=0 as cap if 3+ failures have occurred within 30s. Below this
# threshold we accept the risk of letting the call through; above it the
# burst pattern itself is strong evidence of cap state.
_BURST_THRESHOLD = 3
_BURST_WINDOW_SEC = 30.0


def _record_claude_failure() -> bool:
    """Append a failure timestamp; return True if this completes a burst."""
    now = time.time()
    with _BURST_LOCK:
        _BURST_FAIL_TS.append(now)
        # Trim entries older than the window
        cutoff = now - _BURST_WINDOW_SEC
        while _BURST_FAIL_TS and _BURST_FAIL_TS[0] < cutoff:
            _BURST_FAIL_TS.pop(0)
        return len(_BURST_FAIL_TS) >= _BURST_THRESHOLD


def _reset_claude_burst_state() -> None:
    """Test helper: clear burst-state. Production code never needs this —
    a successful call doesn't clear the burst window because the window
    is purely time-based (entries age out naturally)."""
    with _BURST_LOCK:
        _BURST_FAIL_TS.clear()


def _is_claude_cap_burn(stderr: str, returncode: int, stdout: str = "") -> bool:
    """Heuristic: did this ``claude -p`` invocation fail because of the 5h
    usage cap (or a rate-limit-like condition)?

    Three heuristics, OR-ed:

    1. Substring match against known cap markers in stderr.
    2. Substring match against known cap markers in stdout (some recent
       claude CLI versions print cap notices to stdout, not stderr).
    3. **Empty-stderr rc=1**: empirical observation from v0.2 Phase 3 Opus
       judging — ``claude -p`` in cap state returns rc=1 with empty stderr
       (and empty stdout). Without this fallback, the worker pool burns
       through hundreds of rc=1 calls in seconds. The cost of a false
       positive (treating a real non-cap empty-stderr rc=1 as cap) is just
       a backoff sleep, which is recoverable; the cost of a false negative
       was observed to be ~1700 wasted Opus quota calls in v0.2 Phase 3.

    Used by callers to decide whether to back off vs fail through.
    Conservative: false negatives are catastrophic (cap burn); false
    positives are merely slow (recoverable backoff)."""
    if returncode == 0:
        return False
    se = (stderr or "").lower()
    so = (stdout or "").lower()
    if any(m in se for m in _CLAUDE_CAP_MARKERS):
        return True
    if any(m in so for m in _CLAUDE_CAP_MARKERS):
        return True
    # Heuristic 3: rc != 0 with empty/whitespace-only stderr AND stdout is the
    # cap-burn signature observed empirically in v0.2 Phase 3. We accept the
    # false-positive cost (slower backoff on actual non-cap errors with empty
    # output) because the false-negative cost (wasting hundreds of Opus
    # cap-window calls) is much worse.
    if not se.strip() and not so.strip():
        return True
    return False


def _call_claude_cli(prompt: str, model_key: str, timeout: int = 300) -> LLMResponse:
    spec = MODELS[model_key]
    assert spec.provider == "claude-cli"

    env = os.environ.copy()
    env.pop("CLAUDECODE", None)  # nested session avoidance

    start = time.time()
    # --safe-mode + neutral cwd: judging must be context-isolated. A plain
    # `claude -p` loads ~/.claude/CLAUDE.md, which imports the subject's
    # psychometric profile (with ground-truth trait scores). All claude-cli
    # judgments produced before 2026-06-09 ran without this isolation and
    # are therefore non-blind. See
    # ../docs/reviews/context-contamination-audit-2026-06-09.md (psyche repo).
    # claude-cron --gate: account routing (A/B) + usage-guard freeze gating
    # before the same claude binary. --safe-mode blindness is unaffected — the
    # wrapper only switches credentials/config-dir, never context loading.
    result = subprocess.run(
        [os.path.expanduser("~/scripts/claude-cron"), "--gate",
         "-p", "--safe-mode", "--model", spec.cli_model or spec.resolved_id],
        input=prompt,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
        cwd=tempfile.gettempdir(),
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        stderr = result.stderr or ""
        stdout = result.stdout or ""
        # Burst-rate signal: record this failure and check whether we've
        # crossed the threshold. Process-global state so all workers see
        # the same burst window.
        burst_detected = _record_claude_failure()
        # Forensic logging: capture every rc!=0 invocation to a debug file
        # so we can diagnose why cap-burn detection sometimes misses bursts.
        # The 2026-05-13 run hit ~800 rc=1 failures with cap_events=0 — the
        # detection didn't fire and we don't know if it's because stdout
        # had non-marker content, or empty, or some other shape. This log
        # capture is cheap (one line per failure) and lets us iterate on
        # the heuristic with actual data.
        try:
            from datetime import datetime
            import json as _json
            log_path = os.path.join(os.path.expanduser("~"), "claudeworkspace", "psyche", "psycheeval", "logs", "claude_cli_failures.jsonl")
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a") as fh:
                fh.write(_json.dumps({
                    "ts": datetime.utcnow().isoformat(),
                    "model_key": model_key,
                    "rc": result.returncode,
                    "stdout_len": len(stdout),
                    "stderr_len": len(stderr),
                    "stdout_preview": stdout[:1000],
                    "stderr_preview": stderr[:1000],
                    "elapsed_s": elapsed,
                }) + "\n")
        except Exception:
            pass  # never let logging crash the call
        if _is_claude_cap_burn(stderr, result.returncode, stdout=stdout) or burst_detected:
            cause = (
                "burst-rate threshold crossed"
                if burst_detected and not _is_claude_cap_burn(stderr, result.returncode, stdout=stdout)
                else "content-marker match"
            )
            raise ClaudeCapError(
                f"claude -p hit usage cap ({cause}; rc={result.returncode}; stderr_len={len(stderr)}; stdout_len={len(stdout)}): {stderr[:500] or stdout[:500] or '(empty)'}",
                stderr=stderr or stdout or f"[burst-rate detection: {len(_BURST_FAIL_TS)} failures in last {_BURST_WINDOW_SEC}s]",
                returncode=result.returncode,
            )
        raise ClaudeCLIError(f"claude -p failed (rc={result.returncode}; stderr_len={len(stderr)}; stdout_len={len(stdout)}): {stderr[:500] or stdout[:500] or '(empty)'}")

    return LLMResponse(
        model_key=model_key,
        model_resolved=spec.resolved_id,
        content=result.stdout.strip(),
        elapsed_s=elapsed,
        provider_family=spec.provider_family,
        model_family=spec.model_family,
        reasoning_effort=spec.reasoning_effort,
    )


# --- Codex CLI --------------------------------------------------------------


class CodexCLIError(RuntimeError):
    pass


def _call_codex_cli(prompt: str, model_key: str, timeout: int = 600) -> LLMResponse:
    spec = MODELS[model_key]
    assert spec.provider == "codex-cli"

    cmd = [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "-s",
        "read-only",
        "--color",
        "never",
        "-m",
        spec.resolved_id,
    ]
    # Per-call reasoning effort override. Without this, codex falls back to the
    # value in ~/.codex/config.toml (currently "xhigh"). Setting it explicitly
    # makes the run reproducible across machines and lets different models
    # carry different efforts in the same pilot.
    if spec.reasoning_effort:
        cmd.extend(["-c", f'model_reasoning_effort="{spec.reasoning_effort}"'])

    start = time.time()
    result = subprocess.run(
        cmd,
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    elapsed = time.time() - start

    if result.returncode != 0:
        raise CodexCLIError(
            f"codex exec failed (rc={result.returncode}): {result.stderr[-500:]}"
        )

    # stdout contains only the final model response (clean).
    # stderr contains the preview/header/token counts.
    content = result.stdout.strip()

    # Pull token usage out of stderr if present (best-effort)
    tokens = None
    for line in result.stderr.splitlines():
        if line.strip().isdigit() and "tokens" in result.stderr[max(0, result.stderr.index(line) - 40) : result.stderr.index(line)]:
            try:
                tokens = int(line.strip().replace(",", ""))
            except ValueError:
                pass

    return LLMResponse(
        model_key=model_key,
        model_resolved=spec.resolved_id,
        content=content,
        completion_tokens=tokens,
        elapsed_s=elapsed,
        provider_family=spec.provider_family,
        model_family=spec.model_family,
        reasoning_effort=spec.reasoning_effort,
    )


# --- OpenRouter API ---------------------------------------------------------

class OpenRouterAPIError(RuntimeError):
    pass


def _call_openrouter_api(prompt: str, model_key: str, timeout: int = 300) -> LLMResponse:
    spec = MODELS[model_key]
    assert spec.provider == "openrouter-api"

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise OpenRouterAPIError("OPENROUTER_API_KEY env var required for OpenRouter models")

    payload_obj = {
        "model": spec.resolved_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 16000,
        "temperature": 0.7,
    }
    if model_key == "deepseek-v4-pro":
        # Pin the discounted official DeepSeek route. If it is unavailable,
        # fail visibly instead of silently falling back to a pricier host.
        payload_obj["provider"] = {"only": ["deepseek"], "allow_fallbacks": False}

    payload = json.dumps(payload_obj).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://ashitaorbis.com",
            "X-Title": "PsycheEval",
        },
        method="POST",
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()[:500]
        raise OpenRouterAPIError(f"OpenRouter HTTP {e.code}: {error_body}") from e
    except Exception as e:
        raise OpenRouterAPIError(f"OpenRouter request failed: {e}") from e
    elapsed = time.time() - start

    if data.get("error"):
        raise OpenRouterAPIError(f"OpenRouter API error: {data['error']}")

    choice = data.get("choices", [{}])[0]
    message = choice.get("message", {})
    content = message.get("content") or ""
    usage = data.get("usage", {})

    return LLMResponse(
        model_key=model_key,
        model_resolved=spec.resolved_id,
        content=content.strip(),
        prompt_tokens=usage.get("prompt_tokens"),
        completion_tokens=usage.get("completion_tokens"),
        elapsed_s=elapsed,
        raw=data,
        provider_family=spec.provider_family,
        model_family=spec.model_family,
        reasoning_effort=spec.reasoning_effort,
    )


# --- Unified interface ------------------------------------------------------


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=30),
    retry=retry_if_exception_type((ClaudeCLIError, CodexCLIError, OpenRouterAPIError, TimeoutError)),
    reraise=True,
)
def complete(
    *,
    system: str,
    user: str,
    model_key: str,
    temperature: float = 0.7,  # ignored by CLI paths; kept for signature stability
    timeout: int = 600,
) -> LLMResponse:
    """Single unified entrypoint. Returns the raw response content.

    Both CLI paths concatenate system + user into one prompt string. Neither
    CLI exposes a native temperature knob, so we rely on model defaults.
    """
    spec = MODELS[model_key]
    combined = f"<system>\n{system}\n</system>\n\n{user}"
    if spec.provider == "claude-cli":
        return _call_claude_cli(combined, model_key, timeout=timeout)
    if spec.provider == "codex-cli":
        return _call_codex_cli(combined, model_key, timeout=timeout)
    if spec.provider == "openrouter-api":
        return _call_openrouter_api(combined, model_key, timeout=timeout)
    raise RuntimeError(f"Unknown provider {spec.provider}")


# --- JSON extraction --------------------------------------------------------


class JSONExtractionError(ValueError):
    pass


_FENCE_RE = re.compile(r"```(?:jsonl?|js)?\s*(.*?)```", re.DOTALL)


def extract_json(content: str) -> dict | list:
    """Parse JSON from LLM output with tolerant fallbacks.

    Strategies (in order):
    1. Raw json.loads
    2. Strip ``` fences and retry
    3. Find the outermost { } or [ ] and parse that
    """
    stripped = content.strip()

    # 1. Direct parse
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # 2. Fence stripping
    match = _FENCE_RE.search(stripped)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 3. Bracket scanning — find outermost balanced { } or [ ]
    for opener, closer in [("{", "}"), ("[", "]")]:
        start = stripped.find(opener)
        end = stripped.rfind(closer)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(stripped[start : end + 1])
            except json.JSONDecodeError:
                continue

    raise JSONExtractionError(f"Could not parse JSON from content (len={len(content)})")


def extract_jsonl(content: str) -> list[dict]:
    """Parse JSONL, one object per non-empty line."""
    # Strip fences if wrapped
    stripped = content.strip()
    match = _FENCE_RE.search(stripped)
    if match:
        stripped = match.group(1).strip()

    out: list[dict] = []
    for line_no, line in enumerate(stripped.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise JSONExtractionError(f"Line {line_no}: {e}") from e
    return out
