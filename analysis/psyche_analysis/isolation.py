"""Context-isolated `claude -p` invocation for blind LLM inference.

Why this module exists
----------------------
A plain ``claude -p`` call boots the full Claude Code harness, including
``~/.claude/CLAUDE.md`` — which on this machine imports
``psyche/profiles/claude-context.md``, the subject's full behavioral
specification *with trait scores*. Discovered 2026-06-09: every evaluative
``claude -p`` call made by this project before that date (narrative scoring,
psycheeval judging, the 2026-03-04 corpus analysis) therefore had
profile-derived content silently present in context. See
``docs/reviews/context-contamination-audit-2026-06-09.md``.

The fix is ``--safe-mode``, which disables all customizations (CLAUDE.md,
memory, skills, hooks, MCP) while keeping Max-plan OAuth working.
``--bare`` is NOT usable here: it refuses OAuth/keychain auth entirely and
requires ``ANTHROPIC_API_KEY``, which this project does not maintain.

Residual context after isolation (verified empirically 2026-06-09 via the
canary): the user's account email and the current date. Neither carries
trait information; documented as acceptable residual leakage.

Usage
-----
    from psyche_analysis.isolation import call_claude_isolated, verify_isolation

    verify_isolation()          # raises IsolationError if context is dirty
    out = call_claude_isolated(prompt, system=SYSTEM_PROMPT, model="fable")

Every batch of blind calls should be preceded by one ``verify_isolation()``
canary. Record ``isolation_provenance()`` in any output JSON produced from
isolated calls.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile

# Neutral working directory: prevents project-level CLAUDE.md discovery
# (claude -p walks up from cwd) independently of --safe-mode.
NEUTRAL_CWD = tempfile.gettempdir()

ISOLATION_FLAGS = ["--safe-mode"]

CANARY_SYSTEM = "You are a context-inspection test assistant."
CANARY_PROMPT = (
    "Inspect your full context. The user's email address and the current "
    "date are always present in this harness and do NOT count. Beyond "
    "those two items, do you see any user-specific memory, CLAUDE.md "
    "content, user preferences, project instructions, or a "
    "psychometric/personality profile of the user? Answer with exactly "
    "YES or NO on the first line. If YES, quote one short phrase from "
    "the leaked content on the second line."
)


class IsolationError(RuntimeError):
    """Raised when the isolation canary detects leaked user context."""


def _call_provenance(envelope: dict, requested_model: str) -> dict:
    """Recover which model(s) actually ran from a ``claude -p`` JSON envelope.

    ``modelUsage`` is keyed by the *resolved* full model id(s) that billed
    tokens — including any silent ``model_refusal_fallback`` substitution
    (e.g. Fable → Opus), which the ``--model`` alias alone never reveals. A
    fallback is flagged when any billed id fails to contain the requested
    alias/id (``fable`` requested, ``claude-opus-4-8`` billed). Returns None
    for ``fallback_detected`` when ``modelUsage`` is absent (unknown, not
    clean). See ``docs/reviews/PROVENANCE-VERIFICATION-2026-07-01.md``.
    """
    usage = envelope.get("modelUsage") or {}
    resolved = sorted(usage.keys())
    req = requested_model.lower()
    fallback = (
        any(req not in mid.lower() for mid in resolved) if resolved else None
    )
    return {
        "requested_model": requested_model,
        "resolved_models": resolved,
        "fallback_detected": fallback,
        "session_id": envelope.get("session_id"),
    }


def call_claude_isolated(
    prompt: str,
    *,
    system: str,
    model: str = "opus",
    timeout: int = 300,
    capture: dict | None = None,
) -> str:
    """Run ``claude -p --safe-mode`` with no user/project context loaded.

    Returns the raw text response. Raises RuntimeError on nonzero exit
    (caller is responsible for cap-burn / retry handling).

    Uses ``--output-format json`` so the *resolved* model id(s) are
    recoverable from the envelope's ``modelUsage`` map. When a ``capture``
    dict is passed it is filled in place with ``requested_model``,
    ``resolved_models``, ``fallback_detected`` and ``session_id`` — the
    provenance the ``--model`` alias cannot supply once a silent
    ``model_refusal_fallback`` has swapped the model mid-call.
    """
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    result = subprocess.run(
        [
            "claude", "-p",
            *ISOLATION_FLAGS,
            "--model", model,
            "--output-format", "json",
            "--system-prompt", system,
        ],
        input=prompt,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
        cwd=NEUTRAL_CWD,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p (isolated) failed: {result.stderr}")

    try:
        envelope = json.loads(result.stdout)
        text = (envelope.get("result") or "").strip()
        prov = _call_provenance(envelope, model)
    except (json.JSONDecodeError, AttributeError):
        # Older CLI / unexpected output: return raw stdout, no provenance.
        text = result.stdout.strip()
        prov = {
            "requested_model": model,
            "resolved_models": [],
            "fallback_detected": None,
            "session_id": None,
        }

    if capture is not None:
        capture.update(prov)
    return text


def verify_isolation(model: str = "haiku", timeout: int = 120) -> str:
    """Run the canary check; raise IsolationError unless context is clean.

    Returns the canary's raw response on success so callers can log it.
    Uses haiku by default — the canary tests the *harness invocation*, not
    the model, so the cheapest model suffices.
    """
    out = call_claude_isolated(
        CANARY_PROMPT, system=CANARY_SYSTEM, model=model, timeout=timeout
    )
    # bq-279: the canary must be answered EXACTLY, and a clean answer must not be
    # contradicted further down.
    #
    # The old check was `first_line.startswith("NO")`, which passes "NOT SURE",
    # "NOPE — but I can see a personality profile", and "NO IDEA". CANARY_PROMPT
    # asks for "exactly YES or NO on the first line", so the contract is equality;
    # startswith turned a strict protocol into a prefix match, and every string it
    # wrongly admitted means the same thing: context MIGHT be leaking. A canary that
    # cannot fail is worse than no canary, because its passes are cited as evidence
    # of isolation.
    #
    # Trailing punctuation is tolerated ("NO." is still exactly the answer NO);
    # anything else is a failure, INCLUDING an empty response.
    lines = [ln.strip() for ln in out.strip().splitlines()] if out.strip() else []
    first_line = lines[0].rstrip(".!,;: ").strip().upper() if lines else ""
    if first_line != "NO":
        raise IsolationError(
            f"Isolation canary did not answer exactly NO (model={model}). "
            f"First line: {lines[0] if lines else '<empty response>'!r}. "
            f"Response: {out[:500]}"
        )
    # A first-line NO followed by a YES elsewhere is a contradiction, not a pass —
    # the prompt tells the model to quote a leaked phrase when the answer is YES.
    contradictions = [
        ln for ln in lines[1:]
        if ln.rstrip(".!,;: ").strip().upper() == "YES"
    ]
    if contradictions:
        raise IsolationError(
            f"Isolation canary answered NO then contradicted itself (model={model}). "
            f"Response: {out[:500]}"
        )
    return out


def isolation_provenance() -> dict:
    """Provenance fragment to embed in output JSON from isolated runs."""
    return {
        "isolation": "claude-p-safe-mode",
        "isolation_flags": ISOLATION_FLAGS,
        "neutral_cwd": True,
        "residual_context": ["user_email", "current_date"],
        "reference": "docs/reviews/context-contamination-audit-2026-06-09.md",
    }
