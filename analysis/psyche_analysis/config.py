"""Centralized model and runtime configuration for Psyche analysis.

Design principle: two layers with different lifecycle needs.

- Config/user layer (env vars, CLI defaults): use aliases (``opus``,
  ``sonnet``, ``haiku``). These don't rot when Anthropic ships new
  generations; the alias just points somewhere new.

- Output-provenance layer (analysis result JSONs): record the *resolved*
  full model ID at invocation time (e.g., ``claude-opus-4-7``) so past
  results remain interpretable after the alias moves.

The Anthropic Python SDK does NOT accept bare aliases; it expects full
model IDs. Callers using the SDK must resolve first via
:func:`resolve_model_id`. The ``claude -p`` CLI accepts both.

Known limitation: Psyche's LLM analysis path invokes the Anthropic SDK
directly and therefore requires ``ANTHROPIC_API_KEY`` in the environment.
On a Max plan without an API key, this path will fail at call time.
Migrating corpus analysis to ``claude -p`` subprocess is a separate
architectural decision tracked in the project plan.
"""

from __future__ import annotations

import os

# Default Claude model. Uses the alias, not a pinned full ID.
# Override via PSYCHE_CLAUDE_MODEL env var (alias or full ID both accepted).
#
# Opus is the default because 1M context + stronger reasoning materially
# improves assessment quality on the 1.47M-word corpus. For cheap/fast
# iteration set PSYCHE_CLAUDE_MODEL=sonnet or a pinned Sonnet ID.
DEFAULT_CLAUDE_MODEL: str = os.environ.get("PSYCHE_CLAUDE_MODEL", "opus")


# Alias -> current full model ID. Keep in sync with ``~/.claude/CLAUDE.md``
# contemporary-models table. Future improvement: read from
# ``claude-evolution/state/contemporary-models.json`` once Claude models
# are added there (they are currently excluded).
_ALIAS_TO_FULL_ID: dict[str, str] = {
    "opus":   "claude-opus-4-7",
    "sonnet": "claude-sonnet-4-6",
    "haiku":  "claude-haiku-4-5",
}


def resolve_model_id(model: str) -> str:
    """Resolve a Claude model alias to its full ID.

    If ``model`` is a known alias, looks up the current full ID. If it's
    already a full ID (anything not in the alias table), returns unchanged
    so caller-supplied full IDs always flow through as-is. Unknown strings
    pass through; caller error surfaces at the SDK.

    >>> resolve_model_id("opus")
    'claude-opus-4-7'
    >>> resolve_model_id("claude-opus-4-7")
    'claude-opus-4-7'
    >>> resolve_model_id("claude-opus-4-6")
    'claude-opus-4-6'
    """
    return _ALIAS_TO_FULL_ID.get(model, model)
