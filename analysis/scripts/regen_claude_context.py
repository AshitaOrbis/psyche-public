#!/usr/bin/env -S uv run --with anthropic python
"""Regenerate profiles/claude-context.md via Opus 4.7 (1M context).

Writes to profiles/claude-context.candidate.md, privacy-checks, and reports
cleanliness. The user decides whether to promote the candidate to the
canonical path and stamp into profiles/archive/claude-context/.

Invocation:
    cd psyche/analysis
    uv run --with anthropic python scripts/regen_claude_context.py

See profiles/archive/claude-context/INDEX.md for archival convention.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make the psyche_analysis package importable when running this script directly.
_THIS = Path(__file__).resolve()
sys.path.insert(0, str(_THIS.parents[1]))  # psyche/analysis

from psyche_analysis.synthesis.narrative_llm import (  # noqa: E402
    ANTI_PATTERN_PHRASES,
    PRIVACY_DENYLIST,
    check_anti_patterns,
    check_privacy_leaks,
    regenerate,
)

PSYCHE_ROOT = _THIS.parents[2]  # .../psyche/
PROFILES = PSYCHE_ROOT / "profiles"

profile_path = PROFILES / "profile.json"
narrative_input_path = PROFILES / "narrative-input.md"
transcript_path = PROFILES / "interview" / "transcript.md"
# Style reference: prefer the currently-deployed claude-context.md since
# it's by definition the most recent shipped version. Fall back to the
# newest archived LLM snapshot by mtime if the deployed file is missing.
archive_dir = PROFILES / "archive" / "claude-context"
deployed = PROFILES / "claude-context.md"
if deployed.exists():
    existing_snippet_path = deployed
else:
    llm_snapshots = sorted(
        archive_dir.glob("*-llm-*.md"),
        key=lambda p: p.stat().st_mtime,
    )
    if not llm_snapshots:
        print(f"[regen] ERROR: No LLM reference snapshot in {archive_dir}", file=sys.stderr)
        sys.exit(2)
    existing_snippet_path = llm_snapshots[-1]
candidate_path = PROFILES / "claude-context.candidate.md"

print(f"[regen] Style reference: {existing_snippet_path.name}")
print(f"[regen] Input sizes:")
for p in [profile_path, narrative_input_path, transcript_path, existing_snippet_path]:
    print(f"  {p.name}: {p.stat().st_size:,} bytes")

# Model is argv-selectable so generations can come from different Claude
# generations (e.g. `... regen_claude_context.py fable`). Default stays opus.
# This path intentionally loads NO isolation: the regen is non-blind by
# design (the profile is its explicit input).
model = sys.argv[1] if len(sys.argv) > 1 else "opus"

# Owner-validated review findings (Fable Review Framework Phase 3/4):
# injected so refuted directives don't survive regeneration by inheritance.
findings_path = (
    PSYCHE_ROOT / "profiles" / "fable-review" / "2026-06-10" / "synthesis-for-regen.md"
)
if findings_path.exists():
    print(f"[regen] Findings injected: {findings_path.name} ({findings_path.stat().st_size:,} bytes)")
else:
    findings_path = None
    print("[regen] No review findings file — plain regeneration")

print(f"[regen] Invoking claude -p --model {model} (60-180s)...")
snippet = regenerate(
    profile_path=profile_path,
    narrative_input_path=narrative_input_path,
    transcript_path=transcript_path,
    existing_snippet_path=existing_snippet_path,
    model=model,
    findings_path=findings_path,
)
print(f"[regen] Got {len(snippet):,} bytes")

candidate_path.write_text(snippet)
print(f"[regen] Candidate: {candidate_path}")

leaks = check_privacy_leaks(snippet)
if leaks:
    print(f"[regen] PRIVACY LEAKS: {leaks}")
    print(f"[regen] Review candidate manually before promotion.")
    sys.exit(1)
print(f"[regen] Privacy check: CLEAN (denylist: {PRIVACY_DENYLIST})")

anti = check_anti_patterns(snippet)
if anti:
    print(f"[regen] CHANNEL ANTI-PATTERNS: {anti}")
    print(f"[regen] The LLM reintroduced directives that assume Claude can")
    print(f"[regen] observe user state beyond text input (silence, withdrawal,")
    print(f"[regen] distress, etc.). Review candidate manually before promotion.")
    sys.exit(1)
print(f"[regen] Anti-pattern check: CLEAN")
print()
print("To promote this candidate:")
print(f"  cp {candidate_path} {PROFILES}/claude-context.md")
today = __import__("datetime").date.today().isoformat()
print(f"  cp {candidate_path} {archive_dir}/{today}-llm-{model}.md")
print(f"  # Then update {archive_dir}/INDEX.md and delete the candidate.")
