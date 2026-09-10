"""LLM-driven regeneration of the behavioral-specification snippet.

Complements ``narrative.py`` (templated, deterministic, fast, free) with an
LLM path that loads the full 39-instrument manifold in one 1M-context call
and produces a richer snippet that surfaces Phase 4 battery constructs
(SWLS, AAQ-II, SCS-26, MFQ-2, ZTPI, MAAS, AOT-13, IUS-12, Maximization,
Authenticity, Dweck ITIS, CEI-II, Frost MPS, Tangney SCS).

Uses ``claude -p`` CLI subprocess (NOT the Anthropic SDK) because this
path runs under the user's Max plan and there is no API key in the env.
This is a deliberate design choice — see psyche_analysis/config.py for
the SDK-vs-CLI discussion.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .profile import PsycheProfile


SYSTEM_PROMPT = """You are generating a behavioral-directives file that gets \
imported into every Claude Code session via ~/.claude/CLAUDE.md. Its job is \
to calibrate how Claude Code responds to this particular user on coding, \
review, research, planning, and technical-writing work.

## The reader and the channel

The reader is Claude Code at session start: a coding agent operating in a \
turn-based text channel (terminal, IDE, or web UI). The user types, Claude \
responds, the user types again when they choose. Between turns, the user \
might be actively reading, might be in a meeting, or might have stepped \
away entirely — Claude has no signal about which, and nothing useful depends \
on which. Sessions are short, continuity across them lives in files, and \
the primary work is software engineering and technical writing rather than \
conversational companionship.

This matters for how directives are framed, not for what content belongs in \
the file. A directive like "prefer probabilistic framing over categorical \
claims" fires on any turn where Claude is stating something uncertain — it \
cashes out every session. A directive like "check in if he goes quiet" \
describes something real about the user but points at a state that isn't \
observable in this channel, so it doesn't know when to fire. The honest \
question for each directive is: "on what kind of turn, against what kind \
of input, would this change what Claude says?" When the answer is clear, \
the directive earns its place. When the answer is "it describes something \
true about the person that doesn't fire in this channel," it's usually \
better as background context than as a line-item directive — or reshaped \
into a form that does fire (e.g., "when the user asks the same question \
twice, answer the same way the second time" is a text-scoped version of \
the attachment-anxiety content).

Use your judgment here. The prior generation (included below) is a \
reasonable starting point — good voice, strong Glass Pane framing, most \
structural directives are sound. A few lines read more as personality \
observation than response-shaping directive; where you notice those, \
reshape them or absorb them into background context. Don't rewrite what \
already works.

## What belongs in the file

Whatever actually helps Claude respond to this user better: response style, \
explanation patterns, feedback calibration, framings that land vs alienate, \
epistemic preferences, format conventions, domain-specific notes, and \
enough background context (Glass Pane paragraph, heroic-narrative framing, \
capability self-reference patterns) for Claude to reason about edge cases \
the directives don't explicitly cover. The 39-instrument battery and \
interview give you a lot of signal; use the parts that produce concrete \
response-shaping guidance, and let the rest inform the background \
paragraphs.

Cite scores when they clarify a directive that would otherwise look \
arbitrary — the self-report-68 vs interview-30 agreeableness gap is worth \
citing because it produces a specific directive (trust the direct- \
communication framing over the "pretty agreeable" surface reading). Don't \
list scores for their own sake.

## Constraints

Privacy is hard: no real names. Use "he" / "him" / "his" or "the user" or \
"the subject"; if source material names specific people, reference them \
structurally ("a past partner", "a close friend"). This is enforced by a \
post-generation grep — a leaked name fails the check.

Format: markdown with section headers of your choice. The prior generation \
used Communication / Decision-Making / Feedback & Conflict / Motivation / \
Epistemic Style / Interpersonal Defaults / Emotional Architecture; several \
of those read as personality-profile sections rather than behavioral- \
directive sections, so renaming is welcome if the new structure serves \
Claude's response-shaping job better.

Length: ~8-10 KB. The goal is coverage (the battery usefully informing \
Claude's responses), not volume.

Return only the snippet body, starting with \
'# Personality Context (Behavioral Specification)'. No preamble, no \
"here is the file", just the content."""


USER_PROMPT_TEMPLATE = """Generate the Claude Code behavioral directives \
using the full 39-instrument battery. Inputs below.

================================================================================
PRIOR GENERATION (good bones — build on it)
================================================================================

Here is the most recent shipped version. It has good voice, the Glass \
Pane background framing, and most structural directives are sound. A few \
lines read more as personality observation than response-shaping directive \
(e.g., descriptions of how the user processes silence or withdraws under \
criticism — both real about him, but not states Claude observes in a \
text-turn channel). Use the bones; reshape what would serve Claude better \
as background context or as a text-scoped directive.

{existing_snippet}
{findings_block}
================================================================================
INTERVIEW TRANSCRIPT (12 Q&A, Peters & Matz assessment condition)
================================================================================

{transcript}

================================================================================
NARRATIVE INPUT (multi-method merged scores with evidence quotes, all instruments)
================================================================================

{narrative_input}

================================================================================
FULL PROFILE JSON (complete schema, all Phase 3 + Phase 4 battery scores)
================================================================================

{profile_json}

================================================================================
END INPUTS
================================================================================

Generate the snippet now. Remember: no real names, behavioral patterns not trait \
labels, surface Phase 4 constructs, match reference voice, 9-10 KB."""


FINDINGS_BLOCK_TEMPLATE = """
================================================================================
REVIEW FINDINGS (owner-validated corrections — these OVERRIDE the prior \
generation and the merged scores where they conflict)
================================================================================

The following findings come from an adversarial review of the prior \
generation against raw corpus evidence, with the corrections validated by \
the subject through structured probes. Where a directive in the prior \
generation conflicts with these findings, the findings win.

{findings}
"""


def build_regeneration_prompt(
    *,
    profile_path: Path,
    narrative_input_path: Path,
    transcript_path: Path,
    existing_snippet_path: Path,
    findings_path: Path | None = None,
) -> str:
    """Assemble the full 1M-context prompt from the project's input files.

    ``findings_path`` (optional) injects owner-validated review findings
    that override the prior generation — used by the Fable Review Framework
    so refuted directives don't survive regeneration by inheritance.
    """
    profile_json = profile_path.read_text()
    narrative_input = narrative_input_path.read_text()
    transcript = transcript_path.read_text()
    existing_snippet = existing_snippet_path.read_text()
    findings_block = (
        FINDINGS_BLOCK_TEMPLATE.format(findings=findings_path.read_text())
        if findings_path is not None
        else ""
    )
    return USER_PROMPT_TEMPLATE.format(
        existing_snippet=existing_snippet,
        transcript=transcript,
        narrative_input=narrative_input,
        profile_json=profile_json,
        findings_block=findings_block,
    )


def invoke_claude_cli(prompt: str, *, model: str = "opus", timeout: int = 600) -> str:
    """Run ``claude -p --model <model>`` with the prompt on stdin.

    Using the CLI (not the SDK) lets this run under the Max plan without an
    API key, matching the ``~/.claude/CLAUDE.md`` guidance for Max-plan
    programmatic calls.
    """
    result = subprocess.run(
        ["claude", "-p", "--model", model, "--append-system-prompt", SYSTEM_PROMPT],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"claude -p failed (rc={result.returncode})\n"
            f"stderr: {result.stderr[:2000]}\n"
            f"stdout: {result.stdout[:500]}"
        )
    return result.stdout.strip()


# Privacy denylist — grep the generated snippet for any of these strings
# and reject the output if any match. This enforces the user's global
# CLAUDE.md rule: "Never include real names in any public-facing content".
#
# The names themselves are NOT hardcoded here (this repo is public — a
# committed denylist would itself leak the names it protects). They are
# loaded from a gitignored file (profiles/private-names.txt, one name per
# line, "#" comments allowed) and/or the PSYCHE_PRIVATE_NAMES env var
# (comma-separated). Loading fails CLOSED: if no names are configured,
# _load_privacy_denylist raises rather than silently skipping the check.

_PRIVATE_NAMES_FILE = Path(__file__).resolve().parents[3] / "profiles" / "private-names.txt"


def _load_privacy_denylist() -> list[str]:
    names: list[str] = []
    if _PRIVATE_NAMES_FILE.exists():
        for line in _PRIVATE_NAMES_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                names.append(line)
    for name in os.environ.get("PSYCHE_PRIVATE_NAMES", "").split(","):
        if name.strip():
            names.append(name.strip())
    if not names:
        raise RuntimeError(
            "Privacy denylist is empty. Create profiles/private-names.txt "
            "(gitignored; one real name per line) or set PSYCHE_PRIVATE_NAMES "
            "before generating snippets — the privacy check must not be skipped."
        )
    return names


PRIVACY_DENYLIST = _load_privacy_denylist


# Phrases that tend to indicate a directive describes the user rather than
# directs Claude's response — they reference state that isn't observable
# in a turn-based text channel (silence, withdrawal, distress, presence).
# The detector is a backstop; the primary guardrail is contextual framing
# in SYSTEM_PROMPT. When hits appear, they're usually worth reshaping into
# a text-turn-scoped form rather than deleting outright — the underlying
# observation is often true, just mislocated as a directive.
#
# Match case-insensitive.
ANTI_PATTERN_PHRASES = [
    "goes quiet",
    "if he withdraws",
    "withdrawal pattern",
    "check in if",
    "silence after",
    "silence means",
    "silence is",
    "silence after feedback",
    "when he goes silent",
    "in distress states",
    "crisis mode",
    "under duress",
    "emotional integration",
    "nervous system",
    "affective contagion",           # true but unusable as directive
    "pre-verbal channel",
    "embodied channel",
]


def check_privacy_leaks(snippet: str) -> list[str]:
    """Return a list of denylist terms that appear in ``snippet``. Empty if clean."""
    hits = []
    for term in PRIVACY_DENYLIST():
        if term in snippet:
            hits.append(term)
    return hits


def check_anti_patterns(snippet: str) -> list[str]:
    """Return a list of anti-pattern phrases in ``snippet``. Empty if clean.

    Anti-patterns are directive framings that assume Claude can observe
    user state beyond text input. These are the "personality profile" trap:
    coherent-sounding observations that a coding agent cannot cash out.
    """
    lower = snippet.lower()
    hits = []
    for phrase in ANTI_PATTERN_PHRASES:
        if phrase.lower() in lower:
            hits.append(phrase)
    return hits


def regenerate(
    *,
    profile_path: Path,
    narrative_input_path: Path,
    transcript_path: Path,
    existing_snippet_path: Path,
    model: str = "opus",
    findings_path: Path | None = None,
) -> str:
    """End-to-end regeneration. Returns the snippet text (not yet written to disk).

    Caller is responsible for deciding whether to write to ``claude-context.md``
    or to a ``.candidate.md`` for review. Always call :func:`check_privacy_leaks`
    on the result before writing to the canonical path.
    """
    prompt = build_regeneration_prompt(
        profile_path=profile_path,
        narrative_input_path=narrative_input_path,
        transcript_path=transcript_path,
        existing_snippet_path=existing_snippet_path,
        findings_path=findings_path,
    )
    snippet = invoke_claude_cli(prompt, model=model)
    return snippet
