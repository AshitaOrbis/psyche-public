#!/usr/bin/env python3
"""Phase 2 of the Fable Review Framework: adversarial claim audit.

Reads profiles/fable-review/2026-06-10/claims.json, builds per-cluster
evidence bundles from the ingested corpus + interview transcript, and has
an ISOLATED Fable adjudicate each claim against the evidence:
confirm | refute | refine | insufficient-evidence.

The adjudicator sees the claims under audit and their evidence bundle —
deliberately — but NOT the rest of the profile, the report, or any prior
scores beyond those a claim explicitly depends on. Isolation via
psyche_analysis.isolation (claude -p --safe-mode).

Usage:
    cd analysis
    uv run python scripts/fable_claim_audit.py            # all clusters
    uv run python scripts/fable_claim_audit.py --cluster agreeableness
    uv run python scripts/fable_claim_audit.py --dry-run  # bundles only

Resumable: clusters with an existing verdicts/<cluster>.json are skipped.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ANALYSIS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ANALYSIS_ROOT))
PSYCHE_ROOT = ANALYSIS_ROOT.parent
REVIEW_DIR = PSYCHE_ROOT / "profiles" / "fable-review" / "2026-06-10"
VERDICTS_DIR = REVIEW_DIR / "verdicts"
INGESTED = PSYCHE_ROOT / "data" / "ingested" / "all.jsonl"
TRANSCRIPT = PSYCHE_ROOT / "profiles" / "interview" / "transcript.md"

from psyche_analysis.isolation import (  # noqa: E402
    call_claude_isolated,
    isolation_provenance,
    verify_isolation,
)

# Keyword maps drive evidence recall per cluster. Patterns are intentionally
# broad; the adjudicator is told the bundle is keyword-sampled and partial.
CLUSTER_PATTERNS: dict[str, str] = {
    "openness-intellect": r"philosoph|metaphysic|first principle|framework|theor(y|ies|etical)|existential|aristot|aquinas|epistem|meaning of life|why the world|big questions|from scratch|novel",
    "conscientiousness-duty": r"\bduty\b|obligat|commit|routine|organiz|disciplin|\bquit\b|bored|new (hobby|interest|project)|stick with|follow.?through|gave up|abandon(ed)? (the|my)|dunning",
    "extraversion-social": r"friend|lonel|alone|social|party|hang out|nobody|isolat|initiat|invite|glass pane|word doc",
    "agreeableness": r"completely lost|disagree|honestly|frankly|wrong about|blunt|idiot|stupid|don'?t care|annoy|argu(e|ing|ment)|confused by people|nobody does anything",
    "neuroticism-coping": r"anxi|depress|alcohol|drink|\bpain\b|dark|black|walls|cope|coping|suffer|panic|despair|wounded|suppress|reapprais|crisis",
    "empathy": r"empath|perspective|feel (her|his|their)|moods?|vibes?|tension between|understand (people|her|him)|resonance|contagion",
    "attachment": r"\blove\b|relationship|girlfriend|breakup|broke up|abandon|reject|close to|attach|clingy|losing (her|him|them)",
    "self-faith-tradition": r"\bgod\b|catholic|faith|church|\bsoul\b|aquinas|thomis|prayer|\bmass\b|jesus|\brome\b|civiliz|tradition|amnesia|memor(y|ies) (loss|lost)|still me",
    "values-motivation": r"status|career|network|money|power|success|comfort|security|belong|ambition|promotion|prestige|hustle",
    "cognition-epistemics": r"probably|not sure|i'?d guess|confiden(ce|t)|uncertain|reasoning|rigorous|evidence|\blogic\b|rational|\biq\b|smart|intelligen",
    "ai-relationship": r"\bclaude\b|\bgpt\b|chatgpt|\bai\b|\bllm\b|\bagent\b|introspection|psycholog(ist|y)|therapy",
    "misc-regulation": r"control|influence|consistent|same person|authentic|adapt|audience|persona\b|register|in control",
}

EXCERPT_WORDS = 110          # words kept around each match
MAX_EXCERPTS = 34            # per cluster, spread evenly over time
BASELINE_EXCERPTS = 6        # unfiltered samples for base-rate calibration
BUNDLE_WORD_CAP = 4500

ADJUDICATOR_SYSTEM = """You are a personality-assessment auditor. You will receive: (a) a set of claims from a personality profile of one person, and (b) an evidence bundle of text written by that person (keyword-sampled corpus excerpts spanning 2008-2026, a few unfiltered baseline excerpts, and a structured-interview transcript).

Your job is adversarial adjudication: for each claim, decide whether the evidence CONFIRMS it, REFUTES it, supports a REFINED version of it, or is INSUFFICIENT to judge.

Rules:
1. Judge ONLY from the provided evidence. Quote specific passages as support.
2. The evidence bundle is keyword-sampled and partial — calibrate confidence accordingly, and prefer 'insufficient-evidence' over guessing.
3. Distinguish what the person TALKS ABOUT from what they ARE. Discussing anxiety is not being anxious.
4. Numeric scores stated inside a claim are measurement facts from validated instruments; you are auditing the INTERPRETATION layered on them, not re-deriving the numbers.
5. For 'refine' verdicts, supply the corrected formulation — keep what the evidence supports, fix what it doesn't.
6. Be willing to refute. Plausible-sounding interpretive frames that the evidence doesn't actually support should be called out. You are not here to be agreeable.
7. Note evidence that suggests something the claim MISSES (put it in 'notes')."""

ADJUDICATION_PROMPT = """CLAIMS UNDER AUDIT (cluster: {cluster}):

{claims_block}

EVIDENCE BUNDLE:

=== Interview transcript (complete) ===
{transcript}

=== Corpus excerpts (keyword-sampled for this cluster, chronological) ===
{excerpts}

=== Baseline excerpts (unfiltered, for base-rate calibration) ===
{baseline}

Respond with ONLY a JSON object, no prose before or after:
{{
  "cluster": "{cluster}",
  "verdicts": [
    {{
      "claim_id": "<id>",
      "verdict": "confirm|refute|refine|insufficient-evidence",
      "confidence": "high|medium|low",
      "evidence_quotes": ["<short quote>", "..."],
      "reasoning": "<2-4 sentences>",
      "refined_formulation": "<only for refine verdicts>",
      "notes": "<anything the claim misses; optional>"
    }}
  ]
}}"""


def load_corpus() -> list[dict]:
    rows = []
    with open(INGESTED) as f:
        for line in f:
            r = json.loads(line)
            if r.get("author") == "self" and r.get("text"):
                rows.append(r)
    rows.sort(key=lambda r: r.get("timestamp") or "")
    return rows


def excerpt_around(text: str, match_start: int, words: int = EXCERPT_WORDS) -> str:
    pre = text[:match_start].split()
    post = text[match_start:].split()
    half = words // 2
    return " ".join(pre[-half:] + post[:half + (half - min(half, len(pre)))])


def spread_indices(n: int, k: int) -> list[int]:
    if n <= k:
        return list(range(n))
    return [round(i * (n - 1) / (k - 1)) for i in range(k)]


def build_bundle(cluster: str, corpus: list[dict]) -> tuple[str, str, dict]:
    pat = re.compile(CLUSTER_PATTERNS[cluster], re.IGNORECASE)
    matches = []
    for r in corpus:
        m = pat.search(r["text"])
        if m:
            # Skip citation/reference-list blocks: matched academic boilerplate
            # is cited literature, not the subject's own prose.
            window = r["text"][max(0, m.start() - 300):m.start() + 300]
            if "doi:" in window or window.count("(20") + window.count("(19") >= 3:
                continue
            matches.append((r, m.start()))

    picked = [matches[i] for i in spread_indices(len(matches), MAX_EXCERPTS)]
    lines, words = [], 0
    for r, pos in picked:
        ts = (r.get("timestamp") or "")[:7] or "undated"
        ex = excerpt_around(r["text"], pos)
        words += len(ex.split())
        if words > BUNDLE_WORD_CAP:
            break
        lines.append(f"[{r['source']}, {ts}] {ex}")

    base_rows = [corpus[i] for i in spread_indices(len(corpus), BASELINE_EXCERPTS)]
    baseline = [
        f"[{r['source']}, {(r.get('timestamp') or '')[:7]}] "
        + " ".join(r["text"].split()[:EXCERPT_WORDS])
        for r in base_rows
    ]
    stats = {"corpus_rows": len(corpus), "matches": len(matches), "excerpts_used": len(lines)}
    return "\n\n".join(lines), "\n\n".join(baseline), stats


def claims_block(claims: list[dict]) -> str:
    out = []
    for c in claims:
        dep = ""
        if c["depends_on_scores"]:
            facts = ", ".join(f"{k}={v}" for k, v in c["depends_on_scores"].items())
            dep = f"\n  [measured scores this claim builds on: {facts}]"
        out.append(f"- {c['id']} ({c['claim_type']}, from {c['source_artifact']}): {c['claim_text']}{dep}")
    return "\n".join(out)


def extract_json(text: str) -> dict:
    if "```" in text:
        text = re.sub(r"^.*?```(?:json)?\s*", "", text, flags=re.S)
        text = text.split("```")[0]
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cluster", default=None)
    ap.add_argument("--model", default="fable")
    ap.add_argument("--dry-run", action="store_true", help="write bundles, skip LLM calls")
    args = ap.parse_args()

    claims_doc = json.loads((REVIEW_DIR / "claims.json").read_text())
    transcript = TRANSCRIPT.read_text()
    corpus = load_corpus()
    VERDICTS_DIR.mkdir(parents=True, exist_ok=True)

    by_cluster: dict[str, list[dict]] = {}
    for c in claims_doc["claims"]:
        by_cluster.setdefault(c["cluster"], []).append(c)

    clusters = [args.cluster] if args.cluster else list(by_cluster)

    if not args.dry_run:
        print("[audit] Verifying context isolation (canary)...")
        verify_isolation()
        print("[audit] Isolation canary: CLEAN")

    for cluster in clusters:
        out_path = VERDICTS_DIR / f"{cluster}.json"
        if out_path.exists():
            print(f"[audit] {cluster}: verdicts exist, skipping")
            continue

        excerpts, baseline, stats = build_bundle(cluster, corpus)
        prompt = ADJUDICATION_PROMPT.format(
            cluster=cluster,
            claims_block=claims_block(by_cluster[cluster]),
            transcript=transcript,
            excerpts=excerpts,
            baseline=baseline,
        )
        (VERDICTS_DIR / f"{cluster}.bundle.txt").write_text(prompt)
        print(f"[audit] {cluster}: {len(by_cluster[cluster])} claims, "
              f"{stats['matches']} corpus matches, {stats['excerpts_used']} excerpts, "
              f"prompt {len(prompt.split()):,} words")
        if args.dry_run:
            continue

        for attempt in (1, 2):
            try:
                raw = call_claude_isolated(
                    prompt, system=ADJUDICATOR_SYSTEM, model=args.model, timeout=600
                )
                break
            except RuntimeError as e:
                if attempt == 2:
                    raise
                print(f"[audit] {cluster}: call failed ({str(e)[:80]}), retrying in 60s")
                time.sleep(60)

        (VERDICTS_DIR / f"{cluster}.raw.txt").write_text(raw)
        result = extract_json(raw)
        result["provenance"] = {
            "model": args.model,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "bundle_stats": stats,
            **isolation_provenance(),
        }
        out_path.write_text(json.dumps(result, indent=2))
        got = {v["claim_id"] for v in result["verdicts"]}
        want = {c["id"] for c in by_cluster[cluster]}
        flag = "" if got == want else f"  MISSING: {want - got}"
        print(f"[audit] {cluster}: saved {len(result['verdicts'])} verdicts{flag}")

    print("[audit] Done.")


if __name__ == "__main__":
    main()
