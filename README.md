# Psyche

Open-source framework for constructing reliable personality profiles by triangulating validated psychometric instruments with LLM-based text analysis.

_This repository was re-created from an audited root on 2026-09-05 and carries a single initial commit; the earlier repository is retired and unpublished._

## Live Deployment

A hosted version of Psyche is available at [app.ashitaorbis.com/psyche](https://app.ashitaorbis.com/psyche). It runs the instrument battery in-browser, collects a 10-question written interview (on the website, or through the Ashita Orbis MCP server inside your own Claude conversation), and generates a narrative personality report using **GPT-5.6 Luna**, served through OpenRouter.

The report generation prompt includes a safety clause checked against 3 synthetic stress-test profiles (clinical-edge, aggressive-conflict, religious-intensity) using dual-judge evaluation (Opus 4.6 + GPT-5.4). See [`benchmark/`](benchmark/) for full methodology and results. That exercise tested the prompt's safety clause against synthetic inputs; it is not a validation of the report, of its clinical safety, or of its effect on real readers, and nothing here should be read as one.

**Privacy model — the hosted service and this repository are two different things, and this section used to blur them.** What follows describes the *hosted* service; if you clone this repository and run it yourself, you get the local-only behaviour described under [Privacy](#privacy) below, because you supply your own storage and your own API keys.

The hosted service **does** have a backend: a Cloudflare Worker with a D1 database, in the United States. Scale items are displayed and scored **in your browser**, and your individual item answers are not transmitted — only the scale scores computed from them, your ten written interview answers, a random session ID, and (if you generate one) your report. Those are stored server-side under a published retention ladder: a session that never generates a report is deleted 7 days after it was created; one that does is kept up to 90 days; opting in to research use at the end is the one path that retains your responses — including, in that case, your item answers — for up to 24 months from your last activity or until you withdraw, whichever comes first — longer only if the session is held for a specific named research purpose recorded against it, which withdrawing ends. The opt-in says all of this at the moment it asks. There are no accounts, no cookies, and no device identifiers, and the application stores no IP address. Two boundaries worth naming: (1) Cloudflare, as the host, processes standard request metadata including your IP address in order to serve any request, as it does for any site it serves; (2) generating a report sends your scores and interview text to OpenRouter and onward to the serving provider — on a route that pins zero data retention, so that content is retained at neither hop, leaving only the billing and abuse-prevention metadata each keeps about the request itself under their policies rather than ours.

The authoritative, always-current statement of all of this is the consent and data-map copy on the assessment itself. Where this README and the live disclosure disagree, the live disclosure is right and this file is stale — which it was, materially, until 2026-08-10.

## Quick Start

### Web App (Psychometric Instruments)

```bash
cd web
pnpm install
pnpm dev        # http://localhost:5173
```

Complete the instrument battery (up to 39 instruments across four phases, tiered by depth), then export your results as JSON for profile synthesis.

### Analysis Pipeline (Text Corpus)

```bash
cd analysis
uv sync

# Ingest text corpus (symlink your data into data/raw/ first)
uv run psyche ingest all

# Create diversity-sampled subset
uv run psyche sample

# Run analysis
uv run psyche analyze empath           # Local, no API cost
uv run psyche analyze llm-claude       # Requires ANTHROPIC_API_KEY (pip install psyche-analysis[llm])

# Merge into unified profile
uv run psyche synthesize --self-report path/to/export.json

# View report
uv run psyche report
```

## Architecture

### Web App (`web/`)
- **React 19 + TypeScript + Vite 6** with Zustand state management
- Config-driven instrument definitions with generic scoring engine
- Single-item display with keyboard shortcuts (1-7 for Likert, T/F for binary, arrow keys for navigation)
- localStorage persistence with full JSON export/import

### Analysis Pipeline (`analysis/`)
- **Corpus parsers**: ChatGPT, Claude.ai, SMS, academic writing, Facebook
- **Quality filters**: AI-generated content detection, authorship verification, gibberish filtering
- **LLM inference**: Assessment-optimized prompting (Peters & Matz 2024, r~.44)
- **Empath analysis**: 200+ lexical categories mapped to Big Five
- **Profile synthesis**: Weighted merge with confidence intervals
- **Persona model**: Facet-level behavioral patterns for AI context generation

### Outputs
- **Profile JSON**: Structured data for all traits, methods, and confidence intervals
- **Narrative Report**: Human-readable markdown report (2000-4000 words)
- **CLAUDE.md Snippet**: ~500 word behavioral context for AI assistants (if-then patterns, not trait labels)

## Instrument Battery

39 instruments organized into three tiers of increasing depth. Tiers are additive with replacement — higher tiers substitute longer-form instruments for their shorter counterparts. See [docs/EVOLUTION.md](docs/EVOLUTION.md) for full development history and design rationale.

| Tier | Instruments | Items | Time |
|------|------------|-------|------|
| **Lite** | 15 | ~260 | ~35 min |
| **Standard** | 20 | ~590 | ~80 min |
| **Heavy** | 33 | ~1,130+ | ~160 min |

### Core Battery (all tiers)

| Instrument | Items | Measures |
|-----------|-------|----------|
| Big Five (IPIP-NEO-60/120/300) | 60-300 | Big Five + 30 facets (tier-dependent depth) |
| CRT-7 | 7 | Analytical thinking |
| NCS-18 | 18 | Need for Cognition |
| Rosenberg | 10 | Self-esteem |
| SD3 | 27 | Dark Triad |
| PHQ-8 + GAD-7 | 15 | Depression/anxiety screening (public tiers). The full PHQ-9 — 16 items, including the suicidal-ideation item — is registered for the private `heavy` tier only; see `web/src/instruments/phq8-gad7.ts` for why. |
| ECR-R | 36 | Attachment |
| ERQ-10 | 10 | Emotion regulation |
| IRI-28 | 28 | Empathy (4 dimensions) |
| Self-Monitoring (18/25) | 18-25 | Social flexibility (tier-dependent) |
| Locus of Control (IE-4/IPC-24) | 4-24 | Internal/External attribution (tier-dependent) |
| Grit (S/O) | 8-12 | Perseverance + Interest consistency (tier-dependent) |
| RIASEC-48 | 48 | Vocational interests |
| BPNS (9/21) | 9-21 | Basic psychological needs (tier-dependent) |
| Conversational Interview | 10-15 | Values, self-concept, behavioral examples |

### Standard Tier Additions

| Instrument | Items | Measures |
|-----------|-------|----------|
| HEXACO-60 | 60 | Honesty-Humility + 5 factors |
| SWLS | 5 | Life satisfaction |
| AAQ-II | 7 | Psychological flexibility |
| Dweck ITIS | 8 | Growth mindset |
| CEI-II | 10 | Curiosity |

### Heavy Tier Additions

| Instrument | Items | Measures |
|-----------|-------|----------|
| HEXACO-200 | 200 | Full HEXACO (replaces HEXACO-60) |
| CAT Big Five + HEXACO | ~40-60 adaptive | GRM-based adaptive refinement |
| AOT-13 | 13 | Open-minded thinking |
| IUS-12 | 12 | Intolerance of uncertainty |
| SCS-26 | 26 | Self-compassion |
| MFQ-2 | 36 | Moral foundations (6 foundations) |
| Frost MPS | 35 | Perfectionism (6 dimensions) |
| MAAS | 15 | Mindfulness |
| Authenticity Scale | 12 | Authenticity (3 subscales) |
| Tangney SCS | 36 | Self-control |
| Maximization Scale | 13 | Decision style (maximizer vs satisficer) |
| ZTPI | 56 | Time perspective (5 orientations) |

## Methodology

The framework triangulates four contributing evidence sources. These weights are
`METHOD_WEIGHTS` in `analysis/psyche_analysis/synthesis/merge.py` — the values the merge
actually applies:

| Method | Expected Accuracy | Weight | Notes |
|--------|-------------------|--------|-------|
| Psychometric self-report | Alpha ~.85+ | 0.43 | Up to 39 validated instruments (tier-dependent) |
| LLM inference (Claude) | r~.44 | 0.24 | Assessment-optimized prompting (Peters & Matz 2024) |
| Conversational interview | Qualitative | 0.24 | Semi-structured 10-question protocol |
| HuggingFace models | Fine-tuned | 0.09 | Fine-tuned personality classifiers |
| Empath linguistic analysis | LIWC-validated | **0.00** | **Excluded from the merge** — measures language register, not personality. Retained as a reported method, contributing no weight. |

Empath's exclusion is why the other four are not round numbers: they are the original
0.35 / 0.20 / 0.20 / 0.07 renormalised over the 0.82 that remained once Empath was dropped.

*(Corrected 2026-08-12, bq-280: this table previously listed Empath at 0.10 and omitted
HuggingFace entirely, and its other three weights were the pre-renormalisation values — so
every row disagreed with the code. The weights above are the shipped ones.)*

Confidence intervals reflect cross-method agreement. When methods diverge significantly (SD > 15), the trait is flagged as context-dependent.

### Persona Model

The synthesis generates a 10-dimension persona model mapping psychometric scores to behavioral predictions:

1. **Communication** — directness, depth preference, rationale needs, audience adaptation
2. **Decision-making** — attribution style, risk orientation, deliberation process
3. **Conflict response** — behavior under criticism, regulation strategy, feedback preference
4. **Motivation** — primary needs, persistence patterns, interest consistency
5. **Epistemic style** — analytical tendency, uncertainty tolerance, source preferences
6. **Interpersonal** — trust threshold, empathy mode, ethical stance
7. **Stress response** — crisis mode, recovery strategy, coping mechanisms
8. **Relationships** — attachment style, initiation/maintenance patterns
9. **Flow states** — triggers, phenomenology, barriers
10. **Self-concept** — identity model, competence gap, comparative orientation

The persona model generates behavioral CLAUDE.md snippets — if-then patterns that tell an AI assistant how to behave differently, not trait labels that describe the person.

### ChatLedger Integration (Optional)

If you have a [ChatLedger](https://github.com/AshitaOrbis/chatledger) database with enriched SMS data, pass it to the synthesizer for additional behavioral evidence:

```bash
uv run psyche synthesize --self-report export.json --chatledger-db /path/to/chatledger/
# Or via environment variable:
export PSYCHE_CHATLEDGER_DB=/path/to/chatledger/
uv run psyche synthesize --self-report export.json
```

## Validation

See [docs/VALIDATION-DESIGN.md](docs/VALIDATION-DESIGN.md) for the experimental design to test whether personality-derived context actually shifts AI behavior toward the profiled person's preferences.

## Privacy

- `profiles/`, `data/raw/`, `data/ingested/`, `data/sampled/` are gitignored
- `web/public/seed-data.json` and `web/public/profile.json` are gitignored (see `.example.json` files for schema)
- No corpus data leaves the machine except via explicit LLM API calls
- **Running this repository yourself:** self-report data is stored in localStorage (browser-only) and persists until you clear it or export it — there is no automatic expiry, because there is nothing to expire it
- **The hosted service at app.ashitaorbis.com is different** and has a server-side database with a 7-day / 90-day / research-opt-in retention ladder — see [Live Deployment](#live-deployment) above, and the consent copy on the assessment itself, which is authoritative
- The hosted site is served by Cloudflare Pages; the application stores no IP address, but the host processes standard metadata (including IP addresses) to serve any website
- **Exported JSON can be highly identifying.** Open-ended interview answers are free text written by you, and the export includes response timestamps. Treat exported files as sensitive personal data.

## License

MIT — see [`LICENSE`](LICENSE). The MIT grant covers the original code and
original content of this project.

**Third-party instrument item text is carved out of the MIT grant.** The
verbatim item text of several reproduced psychometric instruments (e.g. SD3,
Frost MPS, MAAS, ZTPI, Grit, SCS-26, and others) is copyrighted by its original
authors and is included here for non-commercial research and educational use
only, under each instrument's own terms — this repository grants no
redistribution or commercial-use rights to that item text. Other instruments
(e.g. the IPIP-based Big Five and HEXACO representations, Rosenberg, PHQ-8/PHQ-9/GAD-7,
SWLS, MFQ-2) use public-domain or openly licensed items that remain covered by
MIT. The full per-instrument audit and terms are in
[`LICENSES/THIRD-PARTY-INSTRUMENTS.md`](LICENSES/THIRD-PARTY-INSTRUMENTS.md).
