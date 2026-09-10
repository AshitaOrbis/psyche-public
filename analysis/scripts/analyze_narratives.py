#!/usr/bin/env python3
"""Quantitative personality analysis of text corpora and Opus-generated narratives.

Runs Empath lexical analysis and LLM inference (Claude Opus 4.6 via `claude -p`,
or GPT-5.4 via `codex exec`) on text samples, then compares against the Psyche
merged profile to assess personality signal preservation and cross-model agreement.

Narrative levels (Opus-generated first-person narratives):
  v2-full     - Full v2 author_first_person.md (33K words)
  v2-arc1     - v2 chapters 1-13 only (27K words, no ***REMOVED*** overlap)
  v2-arc2     - v2 chapters 14-18 only (8.8K words, overlaps with ***REMOVED***)
  subject       - Full subject author_first_person.md (24K words)
  combined    - Both full author-PoV files (57K words)
  arc1-subject  - v2 ch 1-13 + subject full (51K words, overlap removed)

Corpus levels (direct personality inference from raw text):
  corpus      - Legacy corpus.jsonl (academic + sms, stale sampling)
  subject-sms   - ***REMOVED*** SMS self-authored messages (~7K msgs, ~134K words)
  academic    - Academic writing from ingested/ (114 docs, ~151K words)
  messenger   - Messenger conversations from ingested/ (32K msgs, ~413K words)
  ai-conv     - ChatGPT + Claude AI conversations (~8K msgs, ~508K words)
  mixed       - Stratified ~100K words from all 4 real sources (Psyche-equivalent)

Uses `claude -p` CLI (Claude Max plan) or `codex exec` (GPT-5.4) for LLM
inference rather than the Anthropic SDK, since we don't maintain an API key.

Usage:
  cd psyche/analysis
  uv run python scripts/analyze_narratives.py --all
  uv run python scripts/analyze_narratives.py --level subject-sms --skip-empath --backend claude --run-id 1
  uv run python scripts/analyze_narratives.py --level academic --full-context --backend claude --run-id 2
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Add the analysis package to path
ANALYSIS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ANALYSIS_ROOT))

from psyche_analysis.corpus.types import TextSample
from psyche_analysis.methods.empath_analysis import (
    EMPATH_TO_BIG_FIVE,
    EmpathResult,
    analyze_empath,
)

from rich.console import Console
from rich.table import Table

console = Console()


def _subject_dir() -> str:
    """On-disk narrative subdir for the study subject.

    Read from PSYCHE_SUBJECT_DIR (env var; the subject's real first name is the
    on-disk directory/file token and is intentionally not hardcoded in this public
    repo). Mirrors the _archive_contact() / PSYCHE_ARCHIVE_CONTACT pattern.
    """
    name = os.environ.get("PSYCHE_SUBJECT_DIR", "").strip()
    if not name:
        raise RuntimeError(
            "Set PSYCHE_SUBJECT_DIR to the subject's narrative directory/file token "
            "(the on-disk first-name dir under narratives/output and the "
            "<token>_first_person.md prefix) before running subject-level analysis."
        )
    return name


# --- Paths ---
WORKSPACE = Path(__file__).parent.parent.parent.parent  # claudeworkspace/
NARRATIVES = WORKSPACE / "research" / "voice-clone" / "narratives" / "output"
SUBJECT_DIR = _subject_dir()  # on-disk subject token (env-resolved; not hardcoded)
PROFILES = WORKSPACE / "psyche" / "profiles" / "analysis"

V2_AUTHOR_FULL = NARRATIVES / "v2" / "author_first_person.md"
SUBJECT_AUTHOR_FULL = NARRATIVES / SUBJECT_DIR / "author_first_person.md"
V2_CHAPTERS_DIR = NARRATIVES / "v2" / "chapters" / SUBJECT_DIR
SUBJECT_CHAPTERS_DIR = NARRATIVES / SUBJECT_DIR / "chapters" / SUBJECT_DIR

# 1M context experiment outputs
EXPERIMENTS_1M = WORKSPACE / "research" / "voice-clone" / "narratives" / "experiments" / "1m-context"
SUBJECT_1M_AUTHOR = EXPERIMENTS_1M / SUBJECT_DIR / "author_first_person.md"
V2_1M_AUTHOR = EXPERIMENTS_1M / SUBJECT_DIR / "author_first_person.md"

# 1M ablation experiment outputs
SUBJECT_FILTERED_AUTHOR = EXPERIMENTS_1M / f"{SUBJECT_DIR}-filtered" / "author_first_person.md"
SUBJECT_LONG_AUTHOR = EXPERIMENTS_1M / f"{SUBJECT_DIR}-long" / "author_first_person.md"

# GPT-generated narrative (cross-model generation experiment)
EXPERIMENTS_GPT = WORKSPACE / "research" / "voice-clone" / "narratives" / "experiments" / "gpt-generation"
SUBJECT_GPT_AUTHOR = EXPERIMENTS_GPT / "author_first_person.md"

# R4: Second Opus generation (generation variance experiment)
EXPERIMENTS_R4 = WORKSPACE / "research" / "voice-clone" / "narratives" / "experiments" / "r4-second-generation"
SUBJECT_R4_AUTHOR = EXPERIMENTS_R4 / "author_first_person.md"

ORIGINAL_EMPATH = PROFILES / "empath.json"
ORIGINAL_LLM = PROFILES / "llm-claude.json"

# Citation marker pattern: {FN:hexhash}
CITATION_RE = re.compile(r"\{FN:[a-f0-9]+\}")

NARRATIVE_LEVELS = [
    "v2-full", "v2-arc1", "v2-arc2", "subject", "combined", "arc1-subject",
    "subject-1m", "v2-1m", "subject-filtered", "subject-long",
    "v2-subject", "v2-third-person", "v2-dual-pov",
    "subject-subject", "subject-third-person", "subject-dual-pov",
    "subject-gpt-gen",
    "subject-r4",
]
CORPUS_LEVELS = [
    "corpus",       # Legacy corpus.jsonl (academic + sms)
    "subject-sms",    # ***REMOVED*** SMS self-authored only
    "academic",     # Academic writing from ingested/
    "messenger",    # Messenger conversations from ingested/
    "ai-conv",      # ChatGPT + Claude AI conversations
    "mixed",        # Stratified ~100K from all 4 real sources
]
LEVELS = NARRATIVE_LEVELS + CORPUS_LEVELS

# Sampled corpus for direct personality inference (legacy, stale sampling)
CORPUS_JSONL = WORKSPACE / "psyche" / "data" / "sampled" / "corpus.jsonl"

# Ingested data sources (authoritative, used by new corpus levels)
INGESTED = WORKSPACE / "psyche" / "data" / "ingested"
SMS_FULL = WORKSPACE / "research" / "voice-clone" / "data" / "cleaned" / "sms_full.jsonl"

# Output directory for multi-run results
RUNS_DIR = PROFILES / "runs"

# Import prompts for LLM inference
sys.path.insert(0, str(ANALYSIS_ROOT / "prompts"))
from personality_inference import (  # noqa: E402
    SYSTEM_PROMPT,
    BIG_FIVE_ASSESSMENT_PROMPT,
    VALUES_ASSESSMENT_PROMPT,
)


# --- LLM inference backends (Claude via `claude -p`, GPT via `codex exec`) ---

def _call_claude(prompt: str, system: str, model: str = "opus", timeout: int = 300) -> str:
    """Call Claude via isolated `claude -p --safe-mode` CLI.

    CONTAMINATION NOTE (2026-06-09): runs before this date used a plain
    `claude -p`, which loads ~/.claude/CLAUDE.md — including the subject's
    psychometric profile with ground-truth trait scores. All Claude-backend
    narrative scoring results produced before 2026-06-09 are therefore
    non-blind. See docs/reviews/context-contamination-audit-2026-06-09.md.
    The codex backend was never affected (codex exec loads no CLAUDE.md).
    """
    from psyche_analysis.isolation import call_claude_isolated

    return call_claude_isolated(prompt, system=system, model=model, timeout=timeout)


def _call_codex(prompt: str, system: str, model: str = "gpt-5.4") -> str:
    """Call GPT via codex exec CLI, returning the raw text response.

    Inlines the system prompt since codex exec has no --system-prompt flag.
    Uses --skip-git-repo-check to avoid trusted directory errors,
    read-only sandbox since we only need text generation, and
    --ephemeral to skip session persistence.
    """
    full_prompt = f"{system}\n\n---\n\n{prompt}"
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        output_file = f.name

    try:
        result = subprocess.run(
            [
                "codex", "exec",
                "--skip-git-repo-check",
                "--ephemeral",
                "-s", "read-only",
                "-m", model,
                "-o", output_file,
                "-",
            ],
            input=full_prompt,
            capture_output=True,
            text=True,
            env=env,
            timeout=600,
        )
        if result.returncode != 0:
            # Extract just the error line from codex's verbose stderr
            error_lines = [l for l in result.stderr.splitlines() if l.startswith("ERROR:")]
            error_msg = error_lines[0] if error_lines else result.stderr[-500:]
            raise RuntimeError(f"codex exec failed: {error_msg}")
        return Path(output_file).read_text().strip()
    finally:
        try:
            os.unlink(output_file)
        except OSError:
            pass


def _extract_json(text: str) -> dict:
    """Extract JSON object from Claude's response, handling markdown code blocks and trailing text."""
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find the outermost JSON object by brace matching
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response")

    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        c = text[i]
        if escape:
            escape = False
            continue
        if c == "\\":
            escape = True
            continue
        if c == '"' and not escape:
            in_string = not in_string
            continue
        if in_string:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])

    raise ValueError(f"Could not find complete JSON object in response (length: {len(text)})")


def _prepare_text_chunks(
    samples: list[TextSample],
    max_words_per_chunk: int = 8000,
    max_chunks: int = 5,
) -> list[str]:
    """Prepare text samples into chunks for LLM analysis.

    Replicates the logic from llm_claude.py but without SDK dependency.
    """
    by_source: dict[str, list[TextSample]] = {}
    for s in samples:
        by_source.setdefault(s.source, []).append(s)

    for source_samples in by_source.values():
        source_samples.sort(key=lambda s: s.word_count, reverse=True)

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_words = 0

    source_lists = list(by_source.values())
    indices = [0] * len(source_lists)

    while len(chunks) < max_chunks:
        added = False
        for i, sl in enumerate(source_lists):
            if indices[i] >= len(sl):
                continue
            sample = sl[indices[i]]
            indices[i] += 1

            text = sample.text
            words = text.split()
            if len(words) > 2000:
                text = " ".join(words[:2000]) + " [truncated]"

            sample_words = len(text.split())

            if current_words + sample_words > max_words_per_chunk and current_chunk:
                chunks.append("\n\n---\n\n".join(current_chunk))
                current_chunk = []
                current_words = 0
                if len(chunks) >= max_chunks:
                    break

            header = f"[Source: {sample.source}]"
            current_chunk.append(f"{header}\n{text}")
            current_words += sample_words
            added = True

        if not added:
            break

    if current_chunk:
        chunks.append("\n\n---\n\n".join(current_chunk))

    return chunks[:max_chunks]


def _prepare_full_context_text(samples: list[TextSample]) -> str:
    """Concatenate all samples into a single text block for full-context evaluation.

    Used with 1M context window (Opus only). Preserves temporal ordering and
    source labels. No truncation — the model sees everything.
    """
    parts: list[str] = []
    for s in samples:
        header = f"[Source: {s.source}]"
        parts.append(f"{header}\n{s.text}")
    return "\n\n---\n\n".join(parts)


def analyze_big_five_cli(
    samples: list[TextSample],
    model: str = "opus",
    backend: str = "claude",
    max_chunks: int = 5,
    full_context: bool = False,
    debiased_prompt: bool = False,
    n_debiased: bool = False,
) -> dict:
    """Run Big Five personality inference via CLI (claude or codex).

    If full_context=True, sends all text in a single prompt (requires 1M context).
    Otherwise, chunks the text for sequential analysis.
    """
    assert_self_only(samples, "analyze_big_five_cli")  # bq-276: outbound boundary
    call_fn = _call_codex if backend == "codex" else _call_claude

    system = SYSTEM_PROMPT
    if debiased_prompt:
        system += "\n\nIMPORTANT: When evaluating personality from this text, ensure you weight mundane/neutral passages as heavily as emotionally intense passages. Do not anchor on the most salient or dramatic moments. Sample your evidence broadly across the full text, giving equal consideration to routine exchanges and emotional peaks."
        console.print("  [yellow]Using debiased prompt (diversity instruction appended)[/yellow]")
    if n_debiased:
        system += "\n\nIMPORTANT — Neuroticism calibration for narrative text: First-person literary narratives systematically inflate anxiety-coded (N1) and vulnerability-coded (N6) language through genre conventions (introspective self-narration, dramatic tension). When scoring Neuroticism facets, discount passages where anxiety or vulnerability language serves NARRATIVE FUNCTION (building tension, creating empathy, reflecting on past events) rather than indicating TRAIT-LEVEL emotional reactivity. Focus scoring evidence on: (a) N2 Anger/Hostility — least affected by narrative genre, (b) N5 Impulsiveness — behavioral markers resist genre inflation, (c) frequency of anxiety relative to text length rather than absolute presence. Do NOT suppress genuine high-N signal — the goal is to separate trait from genre, not to force low scores."
        console.print("  [yellow]Using N-targeted debiased prompt (genre-adjusted N scoring)[/yellow]")

    if full_context:
        text = _prepare_full_context_text(samples)
        total_words = len(text.split())
        # Full-context needs longer timeout: ~1.5 min per 25K words for reading + response
        fc_timeout = max(900, (total_words // 25_000 + 1) * 90 + 300)
        console.print(f"  Full-context analysis ({total_words:,} words, timeout={fc_timeout}s) via {backend}...")
        prompt = BIG_FIVE_ASSESSMENT_PROMPT.format(text_samples=text)

        # Retry up to 3 times on JSON parse failure (model sometimes returns prose preamble)
        max_attempts = 4
        for attempt in range(max_attempts):
            response = call_fn(prompt, system, model=model, timeout=fc_timeout)
            try:
                result = _extract_json(response)
                result["word_count_analyzed"] = total_words
                return result
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                if attempt < max_attempts - 1:
                    console.print(f"  [yellow]Parse failed attempt {attempt + 1}/{max_attempts} ({e}), retrying...[/yellow]")
                    debug_path = PROFILES / f"_debug_{backend}_fullctx_attempt{attempt + 1}.txt"
                    debug_path.write_text(response)
                else:
                    raise

    chunks = _prepare_text_chunks(samples, max_chunks=max_chunks)
    all_results: list[dict] = []

    for i, chunk in enumerate(chunks):
        console.print(f"  Analyzing chunk {i + 1}/{len(chunks)} ({len(chunk.split())} words) via {backend}...")
        prompt = BIG_FIVE_ASSESSMENT_PROMPT.format(text_samples=chunk)

        try:
            response = call_fn(prompt, system, model=model)
            result = _extract_json(response)
            all_results.append(result)
        except (json.JSONDecodeError, IndexError, ValueError) as e:
            console.print(f"  [red]Failed to parse chunk {i + 1}: {e}[/red]")
            debug_path = PROFILES / f"_debug_{backend}_chunk_{i + 1}.txt"
            debug_path.write_text(response)
            console.print(f"  [dim]Raw response saved to {debug_path}[/dim]")
        except RuntimeError as e:
            console.print(f"  [red]Backend error on chunk {i + 1}: {e}[/red]")
            console.print(f"  [yellow]Continuing with {len(all_results)} successful chunk(s)...[/yellow]")
            break  # Don't try remaining chunks if backend is rate-limited

    if not all_results:
        raise ValueError("No valid results from any chunk")

    return _merge_big_five_results(all_results, chunks)


def analyze_values_cli(
    samples: list[TextSample],
    model: str = "opus",
    backend: str = "claude",
) -> dict:
    """Run Schwartz Values inference via CLI (claude or codex)."""
    assert_self_only(samples, "analyze_values_cli")  # bq-276: outbound boundary
    call_fn = _call_codex if backend == "codex" else _call_claude
    chunks = _prepare_text_chunks(samples, max_chunks=3)
    chunk = chunks[0] if chunks else ""

    console.print(f"  Analyzing values ({len(chunk.split())} words) via {backend}...")
    prompt = VALUES_ASSESSMENT_PROMPT.format(text_samples=chunk)

    response = call_fn(prompt, SYSTEM_PROMPT, model=model)
    result = _extract_json(response)

    return {
        "values": result.get("values", {}),
        "top_3_values": result.get("top_3_values", []),
        "bottom_3_values": result.get("bottom_3_values", []),
        "overall_confidence": result.get("overall_confidence", "medium"),
    }


def _merge_big_five_results(results: list[dict], chunks: list[str]) -> dict:
    """Merge multiple chunk results by averaging scores."""
    domain_scores: dict[str, list[float]] = {}
    domain_evidence: dict[str, list[str]] = {}
    domain_reasoning: dict[str, list[str]] = {}
    domain_confidence: dict[str, list[str]] = {}
    facet_scores: dict[str, list[float]] = {}
    facet_confidence: dict[str, list[str]] = {}
    all_caveats: list[str] = []

    for r in results:
        for domain_key, domain_data in r.get("domains", {}).items():
            if isinstance(domain_data, dict):
                score = domain_data.get("score", 50)
                domain_scores.setdefault(domain_key, []).append(score)
                domain_evidence.setdefault(domain_key, []).extend(
                    domain_data.get("evidence", [])
                )
                domain_reasoning.setdefault(domain_key, []).append(
                    domain_data.get("reasoning", "")
                )
                domain_confidence.setdefault(domain_key, []).append(
                    domain_data.get("confidence", "medium")
                )

        for facet_key, facet_data in r.get("facets", {}).items():
            if isinstance(facet_data, dict):
                facet_scores.setdefault(facet_key, []).append(
                    facet_data.get("score", 50)
                )
                facet_confidence.setdefault(facet_key, []).append(
                    facet_data.get("confidence", "medium")
                )

        all_caveats.extend(r.get("caveats", []))

    domains = {}
    for key in domain_scores:
        scores = domain_scores[key]
        avg_score = sum(scores) / len(scores)
        conf = _merge_confidence(domain_confidence.get(key, ["medium"]))
        evidence = list(dict.fromkeys(domain_evidence.get(key, [])))[:5]
        reasoning = " | ".join(filter(None, domain_reasoning.get(key, [])))

        domains[key] = {
            "score": round(avg_score, 1),
            "confidence": conf,
            "evidence": evidence,
            "reasoning": reasoning,
        }

    facets = {}
    for key in facet_scores:
        scores = facet_scores[key]
        avg_score = sum(scores) / len(scores)
        conf = _merge_confidence(facet_confidence.get(key, ["medium"]))
        facets[key] = {"score": round(avg_score, 1), "confidence": conf}

    conf_order = {"low": 0, "medium": 1, "high": 2}
    overall = min(
        (d["confidence"] for d in domains.values()),
        key=lambda c: conf_order.get(c, 1),
        default="medium",
    )

    return {
        "domains": domains,
        "facets": facets,
        "overall_confidence": overall,
        "caveats": list(dict.fromkeys(all_caveats)),
        "word_count_analyzed": sum(len(c.split()) for c in chunks),
    }


def _merge_confidence(confidences: list[str]) -> str:
    """Merge confidence ratings from multiple chunks."""
    counts = {"low": 0, "medium": 0, "high": 0}
    for c in confidences:
        counts[c] = counts.get(c, 0) + 1
    return max(counts, key=lambda k: counts[k])


def run_llm_analysis(
    samples: list[TextSample],
    model: str = "opus",
    backend: str = "claude",
    max_chunks: int = 5,
    full_context: bool = False,
    debiased_prompt: bool = False,
    n_debiased: bool = False,
) -> dict:
    """Run complete LLM personality analysis via CLI (claude or codex)."""
    # bq-276: earliest outbound boundary. The per-assessment guards below are kept
    # as well — this one gives a clear failure before any work is done, those catch
    # a caller that reaches an assessment without coming through here.
    assert_self_only(samples, "run_llm_analysis")
    report_nonself_rejects()
    if backend == "codex":
        label = f"GPT ({model}) via codex"
        method = "llm-gpt54"
        model_used = f"{model}-via-codex-exec"
    else:
        label = f"Claude ({model}) via claude -p"
        method = "llm-claude"
        model_used = f"claude-{model}-via-claude-cli"

    ctx = "full-context" if full_context else f"{max_chunks} chunks max"
    console.print(f"[bold]Running LLM analysis: {label} ({len(samples)} samples, {ctx})...[/bold]")

    big_five = analyze_big_five_cli(samples, model, backend=backend, max_chunks=max_chunks, full_context=full_context, debiased_prompt=debiased_prompt, n_debiased=n_debiased)
    values = analyze_values_cli(samples, model, backend=backend)

    return {
        "method": method,
        "model_used": model_used,
        "context_mode": "full-context" if full_context else "chunked",
        "big_five": big_five,
        "values": values,
    }


def strip_citations(text: str) -> str:
    """Remove {FN:hash} citation markers from narrative text."""
    cleaned = CITATION_RE.sub("", text)
    # Warn about remaining curly braces that might be malformed citations
    remaining = re.findall(r"\{[^}]*\}", cleaned)
    if remaining:
        examples = remaining[:3]
        console.print(f"  [yellow]Warning: {len(remaining)} remaining curly-brace patterns "
                      f"(e.g. {examples})[/yellow]")
    return cleaned


def load_file(path: Path, source: str) -> TextSample:
    """Load a narrative file as a single TextSample."""
    text = strip_citations(path.read_text())
    return TextSample(
        id=path.stem,
        source=source,
        author="self",
        text=text,
    )


def load_file_segmented(
    path: Path, source: str, segment_words: int = 2000
) -> list[TextSample]:
    """Load a narrative file and split into segments.

    Full narrative files (20-33K words) would be truncated to 2K by the
    chunking algorithm if loaded as a single TextSample. Splitting into
    segments gives the chunker multiple samples to work with, matching
    the behavior of chapter-based levels.
    """
    text = strip_citations(path.read_text())
    words = text.split()
    if len(words) <= segment_words:
        return [TextSample(id=path.stem, source=source, author="self", text=text)]

    segments: list[TextSample] = []
    for i in range(0, len(words), segment_words):
        segment_text = " ".join(words[i : i + segment_words])
        segments.append(
            TextSample(
                id=f"{path.stem}_seg{i // segment_words + 1:02d}",
                source=source,
                author="self",
                text=segment_text,
            )
        )
    return segments


def load_chapters(directory: Path, source: str, start: int = 1, end: int = 99) -> list[TextSample]:
    """Load chapter files from a directory, filtering by chapter number."""
    samples = []
    for path in sorted(directory.glob("chapter_*.md")):
        num = int(path.stem.split("_")[1])
        if start <= num <= end:
            samples.append(load_file(path, source))
    return samples


# --- privacy boundary: only the subject's own words leave this machine --------
# bq-276 (psyche.nonself_corpus_exfiltration_01). TextSample.author is "self" for
# the subject's own text and A REAL NAME for anyone else. These samples are sent
# to external model backends, so a row that is not explicitly the subject's is
# another private individual's words leaving the machine.
#
# Both loaders below previously did `d.get("author", "self")`, which does not
# merely skip the check — it RELABELS an unlabelled row as the subject. That is
# fail-OPEN on the one property that matters here, so the default is gone and an
# absent/blank author is now a rejection.
#
# Two layers on purpose: reject at load, then hard-stop before any outbound call.
# The corpus manager already filters (corpus/manager.py), but this script reads
# the ingested files by a SEPARATE path that never did — one filtered path and
# one unfiltered path is exactly how this survived.
NONSELF_REJECTS: dict[str, int] = {}


def _is_self_authored(d: dict, source_label: str) -> bool:
    """True only when the row is explicitly authored by the subject. Fail closed."""
    author = (d.get("author") or "").strip()
    if author == "self":
        return True
    key = f"{source_label}:{'<absent>' if not author else '<non-self>'}"
    NONSELF_REJECTS[key] = NONSELF_REJECTS.get(key, 0) + 1
    return False


def report_nonself_rejects() -> None:
    """Print what was withheld, by source. Silence here means nothing was dropped."""
    if not NONSELF_REJECTS:
        return
    total = sum(NONSELF_REJECTS.values())
    console.print(f"  [yellow]Privacy filter: withheld {total} non-self row(s) "
                  f"before any outbound call[/yellow]")
    for key in sorted(NONSELF_REJECTS):
        console.print(f"      {key}: {NONSELF_REJECTS[key]}")


def assert_self_only(samples: list[TextSample], where: str) -> None:
    """Hard-stop if a non-self row reached the outbound boundary.

    Raises rather than filtering: by this point something upstream has already
    failed, and silently dropping the row would hide that. Refusing to send is
    always recoverable; sending is not.
    """
    bad = [s for s in samples if (s.author or "").strip() != "self"]
    if bad:
        by_source: dict[str, int] = {}
        for s in bad:
            by_source[s.source] = by_source.get(s.source, 0) + 1
        # Deliberately reports COUNTS BY SOURCE only — never the author values or
        # the text, since those are the private data this guard exists to protect.
        raise RuntimeError(
            f"REFUSING OUTBOUND CALL from {where}: {len(bad)} non-self sample(s) "
            f"reached the model boundary, by source: {by_source}. "
            "Every sample sent to an external backend must be author == 'self'."
        )


def load_corpus_samples() -> list[TextSample]:
    """Load corpus samples from corpus.jsonl for direct personality inference.

    Returns a stratified sample targeting ~100K words to match the Opus GT
    word count (101,005). Prioritizes diversity across sources.
    """
    import random

    lines = CORPUS_JSONL.read_text().strip().split("\n")
    all_samples = []
    for line in lines:
        d = json.loads(line)
        if not _is_self_authored(d, f"corpus-{d['source']}"):
            continue
        all_samples.append(TextSample(
            id=d["id"],
            source=f"corpus-{d['source']}",
            author="self",
            text=d["text"],
        ))

    # Separate by source for stratified sampling
    by_source: dict[str, list[TextSample]] = {}
    for s in all_samples:
        by_source.setdefault(s.source, []).append(s)

    # Include ALL non-SMS samples (academic + facebook = ~143 samples, ~70K words)
    # Then add SMS samples until we hit ~105K words target
    selected: list[TextSample] = []
    total_words = 0

    for source, samples in sorted(by_source.items()):
        if source != "corpus-sms":
            selected.extend(samples)
            total_words += sum(s.word_count for s in samples)

    # Shuffle SMS and add until target
    sms = by_source.get("corpus-sms", [])
    random.seed(42)  # Deterministic selection
    random.shuffle(sms)
    target_words = 105_000
    for s in sms:
        if total_words >= target_words:
            break
        selected.append(s)
        total_words += s.word_count

    console.print(f"  Corpus: {len(selected)} samples, {total_words:,} words "
                  f"(from {len(all_samples)} total, targeting ~{target_words // 1000}K)")
    return selected


def load_ingested_jsonl(path: Path, source_label: str) -> list[TextSample]:
    """Load samples from an ingested JSONL file (standard Psyche format).

    Format: {id, source, author, text, timestamp, word_count}
    """
    samples = []
    rejected_before = sum(NONSELF_REJECTS.values())
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if not _is_self_authored(d, source_label):
                continue
            samples.append(TextSample(
                id=d["id"],
                source=source_label,
                author="self",
                text=d["text"],
            ))
    total_words = sum(s.word_count for s in samples)
    dropped = sum(NONSELF_REJECTS.values()) - rejected_before
    suffix = f", withheld {dropped} non-self" if dropped else ""
    console.print(f"  Loaded {len(samples)} samples from {path.name}, "
                  f"{total_words:,} words{suffix}")
    return samples


def _archive_contact() -> str:
    """Archive contact token from PSYCHE_ARCHIVE_CONTACT (not hardcoded; public repo)."""
    name = os.environ.get("PSYCHE_ARCHIVE_CONTACT", "").strip()
    if not name:
        raise RuntimeError(
            "Set PSYCHE_ARCHIVE_CONTACT to the archive contact token used in "
            "sms_full.jsonl before running the subject-sms level."
        )
    return name


def load_subject_sms() -> list[TextSample]:
    """Load self-authored SMS messages to the archive contact from sms_full.jsonl.

    Filters by contact == PSYCHE_ARCHIVE_CONTACT (env var; the contact's real
    first name is intentionally not hardcoded in this public repo) and
    direction="sent" (self-authored only).
    Format: {sender, contact, address, timestamp, direction, source, text}
    """
    samples = []
    with open(SMS_FULL) as f:
        for line in f:
            d = json.loads(line)
            if d.get("contact") == _archive_contact() and d.get("direction") == "sent":
                text = d.get("text", "")
                if text.strip():
                    samples.append(TextSample(
                        id=f"subject-sms-{len(samples):05d}",
                        source="subject-sms",
                        author="self",
                        text=text,
                    ))
    total_words = sum(s.word_count for s in samples)
    console.print(f"  Archive SMS: {len(samples)} self-authored messages, {total_words:,} words")
    return samples


def load_ai_conversations() -> list[TextSample]:
    """Load ChatGPT + Claude AI conversation samples from ingested data."""
    chatgpt_path = INGESTED / "chatgpt.jsonl"
    claude_path = INGESTED / "claude_ai.jsonl"

    samples = []
    rejected_before = sum(NONSELF_REJECTS.values())
    for path, label in [(chatgpt_path, "chatgpt"), (claude_path, "claude_ai")]:
        with open(path) as f:
            for line in f:
                d = json.loads(line)
                # bq-276: this is the source the finding names most directly — an
                # AI conversation contains the assistant's turns as well as the
                # subject's, so an unfiltered load sends the model its own prior
                # output back as if it were the subject's writing.
                if not _is_self_authored(d, label):
                    continue
                samples.append(TextSample(
                    id=d["id"],
                    source=label,
                    author="self",
                    text=d["text"],
                ))

    total_words = sum(s.word_count for s in samples)
    dropped = sum(NONSELF_REJECTS.values()) - rejected_before
    suffix = f", withheld {dropped} non-self" if dropped else ""
    console.print(f"  AI Conversations: {len(samples)} samples, {total_words:,} words "
                  f"(chatgpt + claude_ai){suffix}")
    return samples


def load_mixed_stratified(target_words: int = 100_000, seed: int = 42) -> list[TextSample]:
    """Load stratified sample from all 4 real Psyche sources.

    Proportional to Psyche's source word distribution:
      SMS: ~27% (from ingested sms.jsonl)
      Academic: ~10% (from ingested academic.jsonl)
      Messenger: ~28% (from ingested messenger.jsonl)
      AI Conversations: ~35% (from chatgpt + claude_ai)

    Target: ~100K words to match Psyche's LLM analysis volume.
    """
    import random

    # Load all sources
    sources: dict[str, list[TextSample]] = {}

    # SMS from ingested (already self-authored)
    sources["sms"] = load_ingested_jsonl(INGESTED / "sms.jsonl", "sms")

    # Academic from ingested
    sources["academic"] = load_ingested_jsonl(INGESTED / "academic.jsonl", "academic")

    # Messenger from ingested
    sources["messenger"] = load_ingested_jsonl(INGESTED / "messenger.jsonl", "messenger")

    # AI conversations
    sources["ai-conv"] = load_ai_conversations()

    # Calculate proportional word targets
    total_available = sum(sum(s.word_count for s in samples) for samples in sources.values())
    word_targets = {}
    for src, samples in sources.items():
        src_words = sum(s.word_count for s in samples)
        proportion = src_words / total_available
        word_targets[src] = int(target_words * proportion)

    console.print(f"\n  Mixed stratified targets (total: {target_words:,}):")
    for src, target in word_targets.items():
        console.print(f"    {src}: ~{target:,} words ({target * 100 // target_words}%)")

    # Sample from each source
    rng = random.Random(seed)
    selected: list[TextSample] = []
    for src, samples in sources.items():
        target = word_targets[src]
        rng.shuffle(samples)
        words_so_far = 0
        for s in samples:
            if words_so_far >= target:
                break
            # Relabel source for consistency
            selected.append(TextSample(
                id=s.id,
                source=f"mixed-{src}",
                author=s.author,
                text=s.text,
            ))
            words_so_far += s.word_count

    total_selected = sum(s.word_count for s in selected)
    console.print(f"\n  Mixed total: {len(selected)} samples, {total_selected:,} words")
    return selected


def get_samples_for_level(level: str) -> list[TextSample]:
    """Return the appropriate TextSample list for an analysis level."""
    if level == "v2-full":
        return load_file_segmented(V2_AUTHOR_FULL, "narrative-v2")
    elif level == "v2-arc1":
        return load_chapters(V2_CHAPTERS_DIR, "narrative-v2-arc1", start=1, end=13)
    elif level == "v2-arc2":
        return load_chapters(V2_CHAPTERS_DIR, "narrative-v2-arc2", start=14, end=18)
    elif level == "subject":
        return load_file_segmented(SUBJECT_AUTHOR_FULL, "narrative-subject")
    elif level == "combined":
        samples = load_file_segmented(V2_AUTHOR_FULL, "narrative-v2")
        samples.extend(load_file_segmented(SUBJECT_AUTHOR_FULL, "narrative-subject"))
        return samples
    elif level == "arc1-subject":
        samples = load_chapters(V2_CHAPTERS_DIR, "narrative-v2-arc1", start=1, end=13)
        samples.extend(load_file_segmented(SUBJECT_AUTHOR_FULL, "narrative-subject"))
        return samples
    elif level == "subject-1m":
        return load_file_segmented(SUBJECT_1M_AUTHOR, "narrative-subject-1m")
    elif level == "v2-1m":
        return load_file_segmented(V2_1M_AUTHOR, "narrative-v2-1m")
    elif level == "subject-filtered":
        return load_file_segmented(SUBJECT_FILTERED_AUTHOR, "narrative-subject-filtered")
    elif level == "subject-long":
        return load_file_segmented(SUBJECT_LONG_AUTHOR, "narrative-subject-long")
    elif level == "v2-subject":
        return load_file_segmented(NARRATIVES / "v2" / f"{SUBJECT_DIR}_first_person.md", "narrative-v2-subject")
    elif level == "v2-third-person":
        return load_file_segmented(NARRATIVES / "v2" / "third_person_account.md", "narrative-v2-third-person")
    elif level == "v2-dual-pov":
        return load_file_segmented(NARRATIVES / "v2" / "dual_pov_relationship.md", "narrative-v2-dual-pov")
    elif level == "subject-subject":
        return load_file_segmented(NARRATIVES / SUBJECT_DIR / f"{SUBJECT_DIR}_first_person.md", "narrative-subject-subject")
    elif level == "subject-third-person":
        return load_file_segmented(NARRATIVES / SUBJECT_DIR / "third_person_account.md", "narrative-subject-third-person")
    elif level == "subject-dual-pov":
        return load_file_segmented(NARRATIVES / SUBJECT_DIR / "dual_pov_relationship.md", "narrative-subject-dual-pov")
    elif level == "subject-gpt-gen":
        return load_file_segmented(SUBJECT_GPT_AUTHOR, "narrative-subject-gpt-gen")
    elif level == "subject-r4":
        return load_file_segmented(SUBJECT_R4_AUTHOR, "narrative-subject-r4")
    elif level == "corpus":
        return load_corpus_samples()
    elif level == "subject-sms":
        return load_subject_sms()
    elif level == "academic":
        return load_ingested_jsonl(INGESTED / "academic.jsonl", "academic")
    elif level == "messenger":
        return load_ingested_jsonl(INGESTED / "messenger.jsonl", "messenger")
    elif level == "ai-conv":
        return load_ai_conversations()
    elif level == "mixed":
        return load_mixed_stratified()
    else:
        raise ValueError(f"Unknown level: {level}")


def output_suffix(level: str) -> str:
    """Return the filename suffix for a given level."""
    return f"-{level}" if level != "combined" else ""


def load_original_results() -> tuple[dict, dict]:
    """Load original empath and LLM analysis results."""
    empath = json.loads(ORIGINAL_EMPATH.read_text())
    llm = json.loads(ORIGINAL_LLM.read_text())
    return empath, llm


def evaluate_empath_methodology(
    original: dict,
    narrative_results: dict[str, EmpathResult],
) -> dict:
    """Evaluate why Empath produces compressed Big Five scores.

    Returns a structured evaluation with root cause analysis.
    """
    from empath import Empath
    lexicon = Empath()

    # 1. Check which mapped categories actually exist in Empath
    all_empath_cats = set(lexicon.analyze("test", normalize=True).keys())
    missing_cats = {}
    valid_cats = {}
    for domain, mapping in EMPATH_TO_BIG_FIVE.items():
        for cat in mapping:
            if cat not in all_empath_cats:
                missing_cats.setdefault(domain, []).append(cat)
            else:
                valid_cats.setdefault(domain, []).append(cat)

    # 2. Compute raw score ranges before calibration
    original_big_five = original.get("big_five_estimates", {})
    original_cats = original.get("categories", {})

    # Compute the weighted sums (pre-calibration) for original
    raw_scores_original = {}
    for domain, mapping in EMPATH_TO_BIG_FIVE.items():
        weighted_sum = 0.0
        total_weight = 0.0
        for cat, weight in mapping.items():
            if cat in original_cats:
                weighted_sum += original_cats[cat] * weight
                total_weight += abs(weight)
        if total_weight > 0:
            raw_scores_original[domain] = weighted_sum / total_weight

    # 3. Check if categories differentiate between original and narratives
    cat_comparison = {}
    # Use the combined narrative result if available, else first available
    narr_key = next(
        (k for k in ["combined", "v2-full", "subject"] if k in narrative_results),
        None,
    )
    if narr_key:
        narr_cats = narrative_results[narr_key].categories
        # Compare top 20 categories from each
        orig_top = sorted(
            ((k, v) for k, v in original_cats.items() if v > 0),
            key=lambda x: x[1], reverse=True,
        )[:20]
        narr_top = sorted(
            ((k, v) for k, v in narr_cats.items() if v > 0),
            key=lambda x: x[1], reverse=True,
        )[:20]
        cat_comparison = {
            "original_top_20": [(k, round(v, 6)) for k, v in orig_top],
            "narrative_top_20": [(k, round(v, 6)) for k, v in narr_top],
            "overlap_count": len(set(k for k, _ in orig_top) & set(k for k, _ in narr_top)),
        }

    # 4. Compute the actual range of raw scores to determine compression source
    raw_range = max(raw_scores_original.values()) - min(raw_scores_original.values()) if raw_scores_original else 0
    calibrated_range = max(original_big_five.values()) - min(original_big_five.values()) if original_big_five else 0

    # 5. Determine verdict
    if raw_range < 0.001:
        verdict = "fundamental_limitation"
        explanation = (
            "Raw weighted category scores show minimal differentiation across domains "
            f"(range: {raw_range:.6f}). The Empath lexical categories, when mapped to Big Five "
            "domains, produce near-identical aggregate scores regardless of domain. This suggests "
            "lexical frequency counting at corpus level lacks sensitivity for personality "
            "differentiation — it measures genre/topic distribution rather than personality."
        )
    elif calibrated_range < 10 and raw_range > 0.002:
        verdict = "calibration_issue"
        explanation = (
            f"Raw scores differentiate (range: {raw_range:.6f}) but calibration formula "
            f"compresses to {calibrated_range:.1f}-point range. The `50 + raw * 2000` scaling "
            "does not adequately amplify the small raw differences."
        )
    elif raw_range > 0.001:
        verdict = "mapping_issue"
        explanation = (
            f"Some raw differentiation exists (range: {raw_range:.6f}) but the mapping from "
            "~200 Empath categories to 5 domains via weighted averaging dilutes distinct signals. "
            "Opposing category weights cancel out, producing regression to the mean."
        )
    else:
        verdict = "indeterminate"
        explanation = "Unable to isolate a single root cause."

    evaluation = {
        "verdict": verdict,
        "explanation": explanation,
        "missing_empath_categories": missing_cats,
        "valid_category_counts": {d: len(cs) for d, cs in valid_cats.items()},
        "raw_score_range": round(raw_range, 6),
        "calibrated_score_range": round(calibrated_range, 1),
        "raw_scores_pre_calibration": {k: round(v, 6) for k, v in raw_scores_original.items()},
        "original_big_five": original_big_five,
        "category_comparison": cat_comparison,
    }

    return evaluation


def print_comparison_table(
    original_llm: dict,
    original_empath: dict,
    narrative_llm_results: dict[str, dict],
    narrative_empath_results: dict[str, EmpathResult],
):
    """Print a comparison table of all analysis levels vs original."""
    domains = ["N", "E", "O", "A", "C"]

    # LLM comparison
    console.print("\n[bold cyan]═══ LLM Big Five Comparison ═══[/bold cyan]")
    table = Table(title="LLM Inference: Original Corpus vs Narratives")
    table.add_column("Level", style="bold")
    for d in domains:
        table.add_column(d, justify="right")
    table.add_column("Words", justify="right")

    # Original row
    orig_scores = {d: original_llm["big_five"]["domains"][d]["score"] for d in domains}
    table.add_row(
        "Original (corpus)",
        *[str(orig_scores[d]) for d in domains],
        f"{original_llm['big_five'].get('word_count_analyzed', '?'):,}",
        style="green",
    )

    for level in LEVELS:
        if level not in narrative_llm_results:
            continue
        result = narrative_llm_results[level]
        bf = result.get("big_five", {})
        if not bf:
            continue
        scores = {d: bf["domains"].get(d, {}).get("score", "?") for d in domains}
        words = bf.get("word_count_analyzed", "?")
        words_str = f"{words:,}" if isinstance(words, int) else str(words)
        table.add_row(level, *[str(scores[d]) for d in domains], words_str)

    console.print(table)

    # Delta table
    console.print("\n[bold cyan]═══ LLM Delta from Original ═══[/bold cyan]")
    delta_table = Table(title="Score Differences (Narrative - Original)")
    delta_table.add_column("Level", style="bold")
    for d in domains:
        delta_table.add_column(f"Δ{d}", justify="right")
    delta_table.add_column("Mean |Δ|", justify="right")

    for level in LEVELS:
        if level not in narrative_llm_results:
            continue
        result = narrative_llm_results[level]
        bf = result.get("big_five", {})
        if not bf:
            continue
        deltas = {}
        for d in domains:
            narr_score = bf["domains"].get(d, {}).get("score")
            if narr_score is not None:
                deltas[d] = narr_score - orig_scores[d]

        if deltas:
            mean_abs = sum(abs(v) for v in deltas.values()) / len(deltas)
            style = "green" if mean_abs < 10 else ("yellow" if mean_abs < 20 else "red")
            delta_table.add_row(
                level,
                *[f"{deltas.get(d, '?'):+.0f}" if isinstance(deltas.get(d), (int, float)) else "?" for d in domains],
                f"{mean_abs:.1f}",
                style=style,
            )

    console.print(delta_table)

    # Empath comparison
    console.print("\n[bold cyan]═══ Empath Big Five Comparison ═══[/bold cyan]")
    empath_table = Table(title="Empath Estimates: Original Corpus vs Narratives")
    empath_table.add_column("Level", style="bold")
    for d in domains:
        empath_table.add_column(d, justify="right")
    empath_table.add_column("Words", justify="right")

    orig_empath_scores = original_empath.get("big_five_estimates", {})
    empath_table.add_row(
        "Original (corpus)",
        *[str(orig_empath_scores.get(d, "?")) for d in domains],
        f"{original_empath.get('total_words', '?'):,}",
        style="green",
    )

    for level in LEVELS:
        if level not in narrative_empath_results:
            continue
        result = narrative_empath_results[level]
        b5 = getattr(result, "big_five_estimates", None) or {}
        empath_table.add_row(
            level,
            *[str(b5.get(d, "—")) for d in domains],
            f"{result.total_words:,}",
        )

    console.print(empath_table)


def print_empath_evaluation(evaluation: dict):
    """Print the Empath methodology evaluation."""
    console.print("\n[bold cyan]═══ Empath Methodology Evaluation ═══[/bold cyan]")

    # Verdict
    verdict = evaluation["verdict"]
    color = {"fundamental_limitation": "red", "calibration_issue": "yellow",
             "mapping_issue": "yellow", "indeterminate": "dim"}.get(verdict, "white")
    console.print(f"\n[bold {color}]Verdict: {verdict.upper().replace('_', ' ')}[/bold {color}]")
    console.print(f"  {evaluation['explanation']}\n")

    # Missing categories
    if evaluation["missing_empath_categories"]:
        console.print("[bold]Missing Empath categories in Big Five mapping:[/bold]")
        for domain, cats in evaluation["missing_empath_categories"].items():
            console.print(f"  {domain}: {', '.join(cats)}")
        console.print()

    # Valid category counts
    console.print("[bold]Valid category counts per domain:[/bold]")
    for domain, count in evaluation["valid_category_counts"].items():
        console.print(f"  {domain}: {count} categories")

    # Raw vs calibrated ranges
    console.print(f"\n[bold]Score ranges:[/bold]")
    console.print(f"  Raw score range: {evaluation['raw_score_range']:.6f}")
    console.print(f"  Calibrated score range: {evaluation['calibrated_score_range']:.1f} points")

    # Raw pre-calibration scores
    console.print(f"\n[bold]Raw scores (pre-calibration):[/bold]")
    for domain, score in evaluation["raw_scores_pre_calibration"].items():
        console.print(f"  {domain}: {score:.6f}")

    # Category comparison
    comp = evaluation.get("category_comparison", {})
    if comp:
        console.print(f"\n[bold]Top-20 category overlap:[/bold] "
                      f"{comp.get('overlap_count', '?')}/20 shared between corpus and narrative")

        console.print("\n[bold]Original corpus top 10:[/bold]")
        for cat, val in comp.get("original_top_20", [])[:10]:
            console.print(f"  {cat:25s} {val:.6f}")

        console.print("\n[bold]Narrative top 10:[/bold]")
        for cat, val in comp.get("narrative_top_20", [])[:10]:
            console.print(f"  {cat:25s} {val:.6f}")


def _compute_max_chunks(level: str, total_words: int) -> int:
    """Determine max chunks based on level and data size.

    Large corpus sources need more chunks (up to 13) to cover sufficient text.
    Narrative levels use the default 5.
    """
    if level in CORPUS_LEVELS:
        # Scale chunks based on word count: ~8K words/chunk
        return min(max(total_words // 8000, 3), 13)
    return 5


def run_level(
    level: str,
    *,
    skip_llm: bool = False,
    skip_empath: bool = False,
    backend: str = "claude",
    full_context: bool = False,
    run_id: int | None = None,
    shuffle: bool = False,
    slice_mode: str | None = None,
    debiased_prompt: bool = False,
    n_debiased: bool = False,
) -> tuple[EmpathResult | None, dict | None]:
    """Run analysis for a single level. Returns (empath_result, llm_result_dict).

    Args:
        full_context: If True, send all text in a single prompt (requires 1M context).
        run_id: If set, saves to runs/ subdirectory with run number for CI computation.
        shuffle: If True, randomly shuffle sample order before analysis.
        slice_mode: If set, use only a chronological slice ('first-quarter' or 'last-quarter').
        debiased_prompt: If True, append diversity instruction to system prompt.
    """
    ctx_label = " full-context" if full_context else ""
    run_label = f" run={run_id}" if run_id is not None else ""
    mod_labels = []
    if shuffle: mod_labels.append("shuffled")
    if slice_mode: mod_labels.append(slice_mode)
    if debiased_prompt: mod_labels.append("debiased")
    if n_debiased: mod_labels.append("n-debiased")
    mod_label = f" [{','.join(mod_labels)}]" if mod_labels else ""
    console.print(f"\n[bold magenta]{'=' * 60}[/bold magenta]")
    console.print(f"[bold magenta]  Level: {level}  (backend: {backend}{ctx_label}{run_label}{mod_label})[/bold magenta]")
    console.print(f"[bold magenta]{'=' * 60}[/bold magenta]")

    samples = get_samples_for_level(level)

    # Apply slice filter (before shuffle, since slicing is chronological)
    if slice_mode:
        n = len(samples)
        quarter = n // 4
        if slice_mode == "first-quarter":
            samples = samples[:quarter]
            console.print(f"  Sliced to first quarter: {len(samples)} of {n} samples")
        elif slice_mode == "last-quarter":
            samples = samples[-quarter:]
            console.print(f"  Sliced to last quarter: {len(samples)} of {n} samples")
        elif slice_mode == "half":
            samples = samples[:n // 2]
            console.print(f"  Sliced to first half: {len(samples)} of {n} samples")
        elif slice_mode == "three-quarter":
            samples = samples[:3 * n // 4]
            console.print(f"  Sliced to first three-quarter: {len(samples)} of {n} samples")

    # Apply shuffle
    if shuffle:
        import random
        random.seed(42 + (run_id or 0))  # Deterministic but different per run
        random.shuffle(samples)
        console.print(f"  Shuffled sample order (seed={42 + (run_id or 0)})")

    total_words = sum(s.word_count for s in samples)
    console.print(f"  Loaded {len(samples)} sample(s), {total_words:,} words")

    if total_words < 1000:
        console.print(f"  [yellow]Warning: only {total_words:,} words — low confidence expected[/yellow]")

    if full_context:
        est_tokens = total_words * 4
        if est_tokens > 900_000:
            console.print(f"  [red]Warning: ~{est_tokens // 1000}K tokens — may exceed 1M context![/red]")
        elif est_tokens > 700_000:
            console.print(f"  [yellow]~{est_tokens // 1000}K tokens — approaching 1M limit[/yellow]")
        if backend == "codex":
            console.print(f"  [red]Full-context mode is only supported with claude backend (1M context)[/red]")
            console.print(f"  [red]Falling back to chunked mode[/red]")
            full_context = False

    suffix = output_suffix(level)

    # Determine output directory: runs/ for multi-run, profiles/ for single runs
    if run_id is not None:
        ctx_tag = "-fullctx" if full_context else ""
        if shuffle: ctx_tag += "-shuffled"
        if slice_mode: ctx_tag += f"-{slice_mode}"
        if debiased_prompt: ctx_tag += "-debiased"
        if n_debiased: ctx_tag += "-n-debiased"
        run_dir = RUNS_DIR / f"{level}{ctx_tag}" / backend
        run_dir.mkdir(parents=True, exist_ok=True)
        out_base = run_dir / f"run-{run_id:02d}"
    else:
        out_base = None  # Use legacy paths

    empath_result = None
    llm_result_dict = None

    # Empath analysis
    if not skip_empath:
        console.print(f"\n  [bold]Running Empath analysis...[/bold]")
        if out_base:
            empath_out = Path(f"{out_base}-empath.json")
        else:
            empath_out = PROFILES / f"narrative{suffix}-empath.json"
        empath_result = analyze_empath(samples)
        empath_out.parent.mkdir(parents=True, exist_ok=True)
        empath_out.write_text(empath_result.model_dump_json(indent=2))
        console.print(f"  Saved to {empath_out}")

    # LLM analysis
    if not skip_llm:
        if backend == "codex":
            model = "gpt-5.4"
            llm_suffix = "llm-gpt54"
        else:
            model = "opus"
            llm_suffix = "llm-claude"

        max_chunks = _compute_max_chunks(level, total_words)

        if out_base:
            llm_out_path = Path(f"{out_base}-{llm_suffix}.json")
        else:
            llm_out_path = PROFILES / f"narrative{suffix}-{llm_suffix}.json"

        llm_result_dict = run_llm_analysis(
            samples, model=model, backend=backend,
            max_chunks=max_chunks, full_context=full_context,
            debiased_prompt=debiased_prompt, n_debiased=n_debiased,
        )
        # Add metadata for traceability
        llm_result_dict["metadata"] = {
            "level": level,
            "backend": backend,
            "run_id": run_id,
            "full_context": full_context,
            "max_chunks": max_chunks if not full_context else None,
            "total_samples": len(samples),
            "total_words": total_words,
        }
        llm_out_path.parent.mkdir(parents=True, exist_ok=True)
        llm_out_path.write_text(json.dumps(llm_result_dict, indent=2))
        console.print(f"  Saved to {llm_out_path}")

    return empath_result, llm_result_dict


def _validate_paths_for_levels(levels: list[str]) -> bool:
    """Validate that required data files exist for the given levels. Returns True if all present."""
    required_paths: list[tuple[Path, str]] = []
    for lvl in levels:
        if lvl in ("v2-full", "v2-arc1", "v2-arc2", "combined", "arc1-subject"):
            required_paths.append((V2_AUTHOR_FULL, "v2 author_first_person.md"))
            required_paths.append((V2_CHAPTERS_DIR, "v2 chapters/<subject>"))
        if lvl in ("subject", "combined", "arc1-subject"):
            required_paths.append((SUBJECT_AUTHOR_FULL, "subject author_first_person.md"))
            required_paths.append((SUBJECT_CHAPTERS_DIR, "subject chapters/<subject>"))
        if lvl == "subject-1m":
            required_paths.append((SUBJECT_1M_AUTHOR, "1m subject author_first_person.md"))
        if lvl == "v2-1m":
            required_paths.append((V2_1M_AUTHOR, "1m subject author_first_person.md"))
        if lvl == "subject-filtered":
            required_paths.append((SUBJECT_FILTERED_AUTHOR, "1m subject-filtered author_first_person.md"))
        if lvl == "subject-long":
            required_paths.append((SUBJECT_LONG_AUTHOR, "1m subject-long author_first_person.md"))
        if lvl == "subject-gpt-gen":
            required_paths.append((SUBJECT_GPT_AUTHOR, "gpt-generation author_first_person.md"))
        if lvl == "subject-r4":
            required_paths.append((SUBJECT_R4_AUTHOR, "r4-second-generation author_first_person.md"))
        if lvl == "v2-subject":
            required_paths.append((NARRATIVES / "v2" / f"{SUBJECT_DIR}_first_person.md", "v2 subject_first_person.md"))
        if lvl == "v2-third-person":
            required_paths.append((NARRATIVES / "v2" / "third_person_account.md", "v2 third_person_account.md"))
        if lvl == "v2-dual-pov":
            required_paths.append((NARRATIVES / "v2" / "dual_pov_relationship.md", "v2 dual_pov_relationship.md"))
        if lvl == "subject-subject":
            required_paths.append((NARRATIVES / SUBJECT_DIR / f"{SUBJECT_DIR}_first_person.md", "subject subject_first_person.md"))
        if lvl == "subject-third-person":
            required_paths.append((NARRATIVES / SUBJECT_DIR / "third_person_account.md", "subject third_person_account.md"))
        if lvl == "subject-dual-pov":
            required_paths.append((NARRATIVES / SUBJECT_DIR / "dual_pov_relationship.md", "subject dual_pov_relationship.md"))
        if lvl == "corpus":
            required_paths.append((CORPUS_JSONL, "corpus.jsonl"))
        if lvl == "subject-sms":
            required_paths.append((SMS_FULL, "sms_full.jsonl"))
        if lvl in ("academic", "mixed"):
            required_paths.append((INGESTED / "academic.jsonl", "ingested academic.jsonl"))
        if lvl in ("messenger", "mixed"):
            required_paths.append((INGESTED / "messenger.jsonl", "ingested messenger.jsonl"))
        if lvl in ("ai-conv", "mixed"):
            required_paths.append((INGESTED / "chatgpt.jsonl", "ingested chatgpt.jsonl"))
            required_paths.append((INGESTED / "claude_ai.jsonl", "ingested claude_ai.jsonl"))
        if lvl in ("sms", "mixed"):
            required_paths.append((INGESTED / "sms.jsonl", "ingested sms.jsonl"))

    ok = True
    for path, name in dict(required_paths).items():  # deduplicate
        if not path.exists():
            console.print(f"[red]Missing: {path} ({name})[/red]")
            ok = False
    return ok


def main():
    parser = argparse.ArgumentParser(description="Analyze text corpora and narratives for personality signal")
    parser.add_argument("--all", action="store_true", help="Run all analysis levels")
    parser.add_argument("--level", choices=LEVELS, help="Run a single analysis level")
    parser.add_argument("--skip-llm", action="store_true", help="Skip LLM inference (Empath only)")
    parser.add_argument("--skip-empath", action="store_true", help="Skip Empath analysis (LLM only)")
    parser.add_argument("--backend", choices=["claude", "codex"], default="claude",
                        help="LLM backend: claude (Opus via claude -p) or codex (GPT-5.4 via codex exec)")
    parser.add_argument("--full-context", action="store_true",
                        help="Send all text in single prompt (requires 1M context, Opus only)")
    parser.add_argument("--run-id", type=int, default=None,
                        help="Run number for multi-run CI computation (saves to runs/ subdirectory)")
    parser.add_argument("--compare-only", action="store_true",
                        help="Skip analysis, just load existing results and compare")
    parser.add_argument("--shuffle", action="store_true",
                        help="Randomly shuffle sample order before analysis (destroys temporal ordering)")
    parser.add_argument("--slice", choices=["first-quarter", "last-quarter", "half", "three-quarter"],
                        help="Use only a chronological slice of samples")
    parser.add_argument("--debiased-prompt", action="store_true",
                        help="Append diversity instruction to system prompt for full-context evaluation")
    parser.add_argument("--n-debiased", action="store_true",
                        help="Append N-targeted debiasing prompt (discount narrative genre anxiety/vulnerability inflation)")
    args = parser.parse_args()

    if not args.all and not args.level and not args.compare_only:
        parser.print_help()
        sys.exit(1)

    # Validate paths (only check what's needed for selected levels)
    levels_to_check = LEVELS if args.all else ([args.level] if args.level else LEVELS)
    if not _validate_paths_for_levels(levels_to_check):
        sys.exit(1)

    # Load original results
    original_empath, original_llm = load_original_results()

    # Determine which levels to run
    levels_to_run = LEVELS if args.all else ([args.level] if args.level else [])

    empath_results: dict[str, EmpathResult] = {}
    llm_results: dict[str, dict] = {}

    if args.compare_only:
        # Load existing results from disk
        for level in LEVELS:
            suffix = output_suffix(level)
            empath_path = PROFILES / f"narrative{suffix}-empath.json"
            llm_path = PROFILES / f"narrative{suffix}-llm-claude.json"
            if empath_path.exists():
                data = json.loads(empath_path.read_text())
                empath_results[level] = EmpathResult(**data)
            if llm_path.exists():
                llm_results[level] = json.loads(llm_path.read_text())
    else:
        # Run analysis
        for level in levels_to_run:
            empath_r, llm_r = run_level(
                level,
                skip_llm=args.skip_llm,
                skip_empath=args.skip_empath,
                backend=args.backend,
                full_context=args.full_context,
                run_id=args.run_id,
                shuffle=args.shuffle,
                slice_mode=args.slice,
                debiased_prompt=args.debiased_prompt,
                n_debiased=args.n_debiased,
            )
            if empath_r:
                empath_results[level] = empath_r
            if llm_r:
                llm_results[level] = llm_r

    # Print comparison tables
    if llm_results or empath_results:
        print_comparison_table(original_llm, original_empath, llm_results, empath_results)

    # Empath methodology evaluation
    if empath_results:
        evaluation = evaluate_empath_methodology(original_empath, empath_results)
        print_empath_evaluation(evaluation)

        # Save evaluation
        eval_path = PROFILES / "empath-evaluation.json"
        eval_path.write_text(json.dumps(evaluation, indent=2))
        console.print(f"\n  Saved Empath evaluation to {eval_path}")

    console.print("\n[bold green]Done.[/bold green]")


if __name__ == "__main__":
    main()
