# Synthesized Findings -- Iteration 1

**Date:** 2026-03-20
**Models:** GPT-5.4 (Codex), Gemini 3.1 Pro, Opus 4.6
**Method:** Deduplicated by issue, cross-validated across reports, severity weighted by model agreement

---

## Actionable Findings

| # | Severity | Title | File(s) | Models | Category |
|---|----------|-------|---------|--------|----------|
| 1 | CRITICAL | Public clinical data in static assets | web/public/seed-data.json, profiles/ | GPT | security/privacy |
| 2 | CRITICAL | Stored XSS via importData + recover.html | web/public/recover.html, store.ts | GPT+Gemini | security |
| 3 | CRITICAL | Code duplication across 3 deployment targets | web/ vs tier-3-nextjs/ vs tier-2-astro/ | Gemini+Opus | architecture |
| 4 | CRITICAL | Next.js ScaleScore type missing CAT fields | tier-3-nextjs/src/lib/psyche/types.ts | Opus | cross-file-consistency |
| 5 | HIGH | Open-ended word count bug (empty string = 1) | web/src/instruments/open-ended.ts:48 | Opus | scoring-correctness |
| 6 | HIGH | CAT item-bank schema mismatch (id vs itemId) | grm-engine.ts, item-banks/*.json | GPT | scoring-correctness |
| 7 | HIGH | CAT banks are synthetic placeholders | item-banks/, generate_synthetic_banks.py | GPT | scoring-correctness |
| 8 | HIGH | Standalone app lacks crisis safety interstitial | web/src/components/TestRunner.tsx | GPT | crisis-safety |
| 9 | HIGH | Missing a11y in InstrumentRunner (ARIA, focus) | tier-3-nextjs/components/psyche/InstrumentRunner.tsx | Gemini | accessibility |
| 10 | HIGH | Next.js API client has no error checking (res.ok) | tier-3-nextjs/src/lib/psyche/api.ts | Gemini | api-contract |
| 11 | HIGH | Unsafe JSON.parse in importData (no validation) | web/src/state/store.ts:1204 | Gemini+GPT | security |
| 12 | HIGH | In-memory rate limiting (ephemeral on Workers) | api/src/routes/psyche.ts | Gemini+Opus+GPT | architecture |
| 13 | HIGH | Wildcard CORS on API | api/src/routes/psyche.ts | GPT | security |
| 14 | MEDIUM | PHQ-9/GAD-7 treats missing responses as 0 | web/src/instruments/phq9-gad7.ts:76 | Opus | scoring-correctness |
| 15 | MEDIUM | scoreLikert normalization assumes uniform format | web/src/scoring/engine.ts:465 | Opus+Gemini | scoring-correctness |
| 16 | MEDIUM | Client-computed scores trusted by server | api/src/routes/psyche.ts, api.ts | Gemini | architecture |
| 17 | MEDIUM | DRY violation between scoreBinary and scoreLikert | web/src/scoring/engine.ts:378-486 | Gemini | code-quality |
| 18 | MEDIUM | Prompt injection via unvalidated interview text | api/src/routes/psyche.ts | GPT | security |
| 19 | MEDIUM | InstrumentRunner completion race (no visual delay) | InstrumentRunner.tsx | Opus | state-management |
| 20 | MEDIUM | Map<> for completedInstruments adds fragile serialization | assess/page.tsx | Opus | state-management |
| 21 | MEDIUM | CAT controller mutates session state directly | web/src/scoring/cat-controller.ts | Gemini | react-patterns |
| 22 | MEDIUM | Unmemoized getAllInstruments/getInstrumentsForTier per render | assess/page.tsx | Gemini | performance |
| 23 | MEDIUM | Dual state (React + localStorage) can diverge silently | assess/page.tsx | Gemini | architecture |
| 24 | MEDIUM | Session-UUID-only auth for sensitive data | api/src/routes/psyche.ts | Gemini+GPT | security |
| 25 | MEDIUM | Score normalization has no bounds validation | web/src/scoring/engine.ts | GPT | scoring-correctness |
| 26 | LOW | autoScoreCompleted uses array length not unique count | web/src/state/store.ts | Opus | state-management |
| 27 | LOW | Interview prompts duplicated (open-ended.ts vs InterviewFlow) | open-ended.ts, InterviewFlow.tsx | Gemini | duplication |
| 28 | LOW | word-count phantom scale not in instrument scales[] | web/src/instruments/open-ended.ts | Opus | scoring-correctness |
| 29 | LOW | isAdaptiveInstrument uses unsafe type check | web/src/instruments/registry.ts:135 | Gemini | code-quality |
| 30 | LOW | Seed data fetch on every hydration | web/src/state/store.ts | Gemini | performance |
| 31 | LOW | thetaToPercentile rounds to 1 decimal prematurely | web/src/scoring/grm-engine.ts:755 | Opus | grm-irt |
| 32 | LOW | CAT selectNextItem ignores content balancing | web/src/scoring/grm-engine.ts | Opus | grm-irt |

## Architectural (Deferred -- Too Large for This Iteration)

| # | Title | Reason for Deferral | Models |
|---|-------|---------------------|--------|
| A1 | Extract shared psyche-web package | Major refactor: 21+ instrument files, types, registry, engine across 3 targets. Already in BACKLOG. Fixes #3, #4, partially #17. | Gemini+Opus |
| A2 | Server-side score re-computation | Requires storing raw responses at consent level 1 OR changing the privacy contract. Architectural decision needed. | Gemini |
| A3 | Replace Map<> with Record<> in SessionState | Touches all handlers in assess page, interacts with localStorage serialization. Low risk but wide blast radius. | Opus |
| A4 | Refactor InstrumentRunner into sub-components | Improves testability but large refactor for a working component. | Gemini |
| A5 | CAT controller immutable state refactor | Major API change affecting all CAT consumers. CAT is experimental anyway. | Gemini |
| A6 | Durable rate limiting (KV/D1) | Infrastructure change, not a code fix. | All 3 |

## False Positives

| # | Model | Claim | Why False |
|---|-------|-------|-----------|
| F1 | Gemini | itemInformation omits a^2 term | Code returns `a * a * info` on the return line. Gemini misread. |
| F2 | Gemini | importData merge order is a bug | Intentional: inline comment says "don't overwrite completed results." |
| F3 | Gemini | scoreBinary 1-value assumes 0/1 | Binary responses ARE always 0/1 in this system (InstrumentRunner maps buttons). |
| F4 | GPT | Indefinite session retention | Needs verification -- the cleanup endpoint logic was only partially visible in the digest. May be correct for research-opted sessions. Downgraded from CRITICAL to needs-investigation. |

## Cross-Validation Notes

- **3 models agree:** Rate limiting is ephemeral (all flagged independently)
- **2 models agree:** Code duplication is the root cause of many other findings (Gemini+Opus)
- **2 models agree:** importData needs validation (Gemini+GPT)
- **GPT unique finds:** Public seed-data.json exposure, CAT schema mismatch, recover.html XSS, session retention -- these are high-value finds the other models missed because they didn't examine the public/ directory or shipped assets
- **Opus unique finds:** Open-ended word count bug, PHQ-9 missing-response handling, auto-score count check -- deep scoring logic analysis
- **Gemini unique finds:** Accessibility violations, CAT mutation pattern, DRY in scoring -- architecture and patterns focus

## Priority Ranking for Remediation

**Immediate (this session):**
1. #1 -- Remove public clinical data files (security, 5 min)
2. #2 -- Fix recover.html XSS or remove file (security, 10 min)
3. #5 -- Fix open-ended word count empty string bug (scoring, 2 min)
4. #28 -- Add word-count to open-ended scales[] (scoring, 1 min)
5. #22 -- Wrap getAllInstruments/getInstrumentsForTier in useMemo (perf, 2 min)

**This week:**
6. #10 -- Add res.ok checking to Next.js API client (api, 15 min)
7. #11 -- Add schema validation to importData (security, 20 min)
8. #13 -- Restrict CORS origins (security, 5 min)
9. #14 -- PHQ-9 missing response handling (scoring, 10 min)
10. #4 -- Sync Next.js ScaleScore type with standalone (consistency, 5 min)

**Backlog:**
- Everything else, plus the architectural items
