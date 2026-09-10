# Backlog

Deferred improvements and future work for Psyche.

## Completed (Phase 2)
- [x] HEXACO-60
- [x] ECR-R (Attachment)
- [x] ERQ-10 (Emotion Regulation)
- [x] IRI-28 (Empathy decomposition)
- [x] Self-Monitoring-18 (social flexibility)
- [x] LOC IE-4 (locus of control)
- [x] Grit-S (perseverance + interest consistency)
- [x] BPNS-9 (Basic Psychological Needs)
- [x] RIASEC-48 (Vocational Interests)
- [x] IPIP-NEO-300 (high-precision Big Five)
- [x] Binary response format (True/False items)
- [x] 7-point Likert keyboard support (1-7)
- [x] Behavioral CLAUDE.md snippet (replaces trait-label format)
- [x] Persona model (structured behavioral predictions)
- [x] Extended battery merge pipeline
- [x] Dashboard: Extended Battery tab
- [x] Dashboard: Persona tab

## Completed (Tiered Battery + CAT)
- [x] Tiered instrument battery (Lite/Standard/Heavy)
- [x] IPIP-NEO-60 (Lite tier Big Five)
- [x] HEXACO-200 (Heavy tier HEXACO)
- [x] Grit-O, BPNS-21, Levenson IPC-24, Snyder SM-25 (Heavy tier extended)
- [x] Profile schema v3 with InstrumentManifest
- [x] Tier-aware merge pipeline with fallback chains
- [x] GRM engine (Graded Response Model for polytomous IRT)
- [x] CAT controller (per-facet adaptive testing with SE-based stopping)
- [x] AdaptiveTestRunner component (dynamic item selection UI)
- [x] Synthetic item banks (Big Five 450 items, HEXACO 360 items)
- [x] CAT scoring integration (scoreAdaptive → InstrumentResult)
- [x] CAT score extraction in analysis pipeline (theta→percentile, weighted merge)
- [x] R script for SAPA parameter extraction (one-time, not yet run)

## Completed (Phase 4: Extended Assessment Battery)
- [x] SWLS (Satisfaction With Life Scale, 5 items) — Standard tier
- [x] AAQ-II (Psychological Flexibility, 7 items) — Standard tier
- [x] Dweck ITIS (Growth Mindset, 8 items) — Standard tier
- [x] CEI-II (Curiosity, 10 items) — Standard tier
- [x] AOT-13 (Actively Open-Minded Thinking, 13 items) — Heavy tier
- [x] IUS-12 (Intolerance of Uncertainty, 12 items) — Heavy tier
- [x] SCS-26 (Self-Compassion, 26 items) — Heavy tier
- [x] MFQ-2 (Moral Foundations, 36 items) — Heavy tier
- [x] Frost MPS (Perfectionism, 35 items) — Heavy tier
- [x] MAAS (Mindfulness, 15 items) — Heavy tier
- [x] Authenticity Scale (12 items) — Heavy tier
- [x] Tangney SCS (Self-Control, 36 items) — Heavy tier
- [x] Maximization Scale MS-13 (13 items) — Heavy tier
- [x] ZTPI (Time Perspective, 56 items) — Heavy tier
- [x] Profile schema v4 with 10 new profile classes
- [x] Merge pipeline extraction for all 14 instruments
- [x] Tier configuration updated (Standard: 20, Heavy: 33 instruments)
- [x] Instrument categories reorganized (9 categories for 39 instruments)

## Deferred (from original Phase 2 list)
- [ ] PVQ-40 (Schwartz Values) — covered by LLM+interview currently
- [ ] REI-40 (Rational-Experiential Inventory) — partially covered by CRT+NCS
- [ ] WLEIS (Emotional Intelligence) — partially covered by IRI + ERQ

## CAT Future Work
- [ ] Run SAPA parameter extraction (R script) for production-quality IRT parameters
- [ ] Replace synthetic item banks with SAPA-calibrated parameters — **CAT is hard-blocked until then**: `validateCATBankOrThrow()` rejects the shipped placeholder banks (placeholder item text), and the AdaptiveTestRunner refuses to administer from an invalid bank (2026-06-11 security review, P0-2)
- [ ] Score fixed forms on the same calibrated IRT scale as the CAT banks and store theta/se in ScaleScore — replaces the interim percentile-derived approximate prior in `fixedFormPrior()` (2026-06-11 review, P1-3)
- [ ] CAT session persistence (save/resume adaptive tests)
- [ ] Real-time theta convergence visualization during CAT
- [ ] Cross-validation of GRM parameters on held-out sample

## Privacy Purge Follow-ups (2026-06-11 adversarial review) — HUMAN ACTION REQUIRED
- [x] **Git history rewrite** (2026-06-22): ran `git filter-repo --replace-text` (visible-token rules → codename `subject`, + surname variants) across all 141 commits on an isolated mirror, with integrity gates (HEAD tree byte-identical, all 80 master commits preserved via `--prune-empty=never`), then force-pushed `master` + the `v4.1-kimi-k2.5-safety` tag. Verified by fresh clone from GitHub: **0 occurrences of the name or surname across all history**. Local working repo realigned (`reset --soft`) with no divergence. GitHub Privacy/Support request SENT by owner 2026-06-22: reported that a PUBLIC FORK `github.com/lcyGo/psyche` retains the pre-rewrite history with the private data, and requested (a) removal/disassociation of that fork and (b) cache-purge of stale pre-rewrite commits on `AshitaOrbis/psyche` and `AshitaOrbis/historical-nanochat`; followed up after the automated reply to route to Trust & Safety. AWAITING GitHub action (esp. the third-party fork, which the owner cannot remove). Pre-rewrite backup mirror retained locally.
- [ ] **Recreate local private config** after the name externalization: `profiles/private-names.txt` (privacy denylist for snippet generation), `PSYCHE_SELF_NAMES`, and `PSYCHE_ARCHIVE_CONTACT` env vars are now required by `analysis/` scripts in place of hardcoded names.
- [x] **Rename partner/contact-derived experiment labels** (2026-06-22): all subject-name-derived labels replaced with the neutral codename `subject` across `analysis/scripts/analyze_narratives.py` (+ sibling `run_analysis_experiments.py`, `run_opus_batch.sh`, `compute_cis.py`) and the 10 committed `experiments/methodology-supplement/` artifacts (5 JSON, 3 .sh, 1 .py, 1 .md). On-disk gitignored data directories were NOT renamed — instead path resolution now goes through the required `PSYCHE_SUBJECT_DIR` env var (mirrors the `PSYCHE_ARCHIVE_CONTACT` pattern), so the codename decouples from the local dir name. Accepted tradeoff: committed artifact label keys now desync from the local gitignored data-dir names. `git grep` for the name across HEAD is empty. (Git history also scrubbed 2026-06-22 — see the Git history rewrite item above, now complete.)
- [x] **psycheeval public-inspired personas** (2026-06-22, owner decision): KEEP as-is. These personas are derived from public figures' published material, not private individuals, so the residual alias/source-URL linkage is acceptable exposure and not a privacy concern under the global rule (which targets private individuals in public-facing content). `internal_public_anchor` real names remain nulled.
- [x] **Instrument licensing audit** (psy-7, 2026-06-22): carved third-party instrument item text out of the MIT grant per owner decision (no relicense, no instrument swaps). Audited all 39 instrument files in `web/src/instruments/`: classified 25 as RESTRICTED (author/publisher copyright, research/educational use only, no redistribution grant — CRT-7, NCS-18, SD3, ECR-R, ERQ-10, IRI-28, Self-Monitoring-18, Snyder SM-25, Levenson IPC-24, Grit-S, Grit-O, BPNS-9, BPNSFS-21, AAQ-II, Dweck ITIS, CEI-II, AOT-13, IUS-12, SCS-26, Frost MPS, MAAS, Authenticity, Tangney SCS, Maximization, ZTPI) and the rest FREE (IPIP Big Five/RIASEC + IPIP-HEXACO representations, Rosenberg, PHQ-9/GAD-7, SWLS, MFQ-2 [CC BY], IE-4 [CC BY]). NB: HEXACO-200/60 use the public-domain IPIP representation, not the proprietary Lee-Ashton forms, so they are FREE despite the earlier flag. CAT item banks hold only IRT params + placeholder labels (no real item text). Added exclusion clause to `LICENSE`, created `LICENSES/THIRD-PARTY-INSTRUMENTS.md` (per-instrument table with authors/sources/status), referenced from `LICENSE` and `README.md`. Conservative framing: "research/educational use; redistribution rights not granted by this repository." Owner may seek formal permission later. Status assessed in good faith, not legal advice.

## Security/Privacy Hardening (deferred from 2026-06-11 review)
- [x] **P2-1** (psy-8): Bounds validation for imported profile JSON in ProfileDashboard — `sanitizeImportedProfile` (`web/src/components/sanitizeProfile.ts`) clamps percentile scores/CI to [0,100], caps string/array lengths, exempts non-score numerics (version, crt_score, counts, theta, z, divergence). Wired into all profile load/import paths. Tests: `web/tests/sanitize-profile.test.ts`.
- [x] **P2-3** (psy-9): localStorage quota handling — quota-aware `createJSONStorage` adapter in `web/src/state/store.ts` surfaces QuotaExceededError via `storageError` state (non-silent banner + "Export now" in `App.tsx`); open-ended response length capped on write in `recordResponse`; approximate `storageBytes` usage indicator exposed. Tests: `web/tests/storage-quota.test.ts`.
- [x] (psy-10): Content-pinning tests for the pinned IPIP npm packages (item IDs, keyed direction, scale/facet mapping via `toMatchSnapshot` + explicit invariants) so a future version bump can't silently change item content. `web/tests/ipip-neo-120.test.ts`, `web/tests/ipip-neo-60.test.ts` (+ snapshots).

## Report Quality Monitoring
- [ ] **Real-condition safety validation**: Re-run dual-judge evaluation (Opus + GPT-5.4) on actual production reports generated by real users via Psyche Public (with consent level 2 / research consent). Synthetic stress tests validated safety on extreme edge cases, but real profiles may surface failure modes that synthetic profiles don't — e.g., ambiguous clinical language in moderate-severity profiles, cultural contexts the synthetic personas don't cover, or interaction effects between unusual score combinations and interview content. Run this once 5-10 real reports with research consent have accumulated. Compare safety scores to the synthetic baselines (clinical-edge: 84, aggressive-conflict: 93, religious-intensity: 97). If any real report scores below 75, investigate and tighten the safety clause further.
- [ ] Periodic model re-evaluation: When DeepInfra adds new models or updates K2.5, re-run the 7-model benchmark to check for regressions. The benchmark is cached — only the new/changed model needs regeneration.
- [ ] Optional Opus follow-up for DeepSeek V4 Pro discounted runs: treat Opus judging as deferred backlog work only, not an automatic step. Raw DeepSeek V4 Pro results should be generated with synthetic or AI-as-user inputs first; run Opus review only when Claude quota is healthy and the specific comparison warrants it.

## Fable Review Framework (2026-06-09 — see docs/FABLE-REVIEW-FRAMEWORK.md)
- [x] Phase 0: contamination audit + isolation layer (`psyche_analysis/isolation.py`, 4 call sites patched, canary verified both directions)
- [x] Phase 1: blind Fable corpus re-derivation × 3 runs ✅ 2026-06-10 — results: `profiles/fable-review/2026-06-10/phase1-blind-rederivation.md` (headline: Tradition 72.7 vs Opus 40; N +7.6; run sd ≤1.81)
- [x] Phase 2: claim audit ✅ 2026-06-10 — 61 claims: 22 confirm / 31 refine / 3 refute / 5 insufficient. Results: `profiles/fable-review/2026-06-10/phase2-claim-audit.md` (headline withheld — private-profile review conclusions)
- [x] Phase 3: insight hunt ✅ 2026-06-10 — 5 owner-validated insights (`profiles/fable-review/2026-06-10/insights.md`) (the five insights themselves are withheld — private-profile review conclusions)
- [x] Phase 4: synthesis ✅ 2026-06-10 — review report (`profiles/fable-review/2026-06-10/report.md`) + Fable claude-context.md generation promoted live (INDEX row added; findings-injected regen via `synthesis-for-regen.md`)
- [ ] Research paper: add methods correction note re context contamination (blindness claim doesn't hold for Claude-CLI runs pre-2026-06-09); annotate 1M-experiment and psycheeval v0.2/v0.3 Opus-judge results as non-blind
- [ ] Optional: quantify contamination effect size post hoc using the clean GPT-5.4 judge arm vs contaminated Opus arm on identical inputs

## Future Enhancements
- [ ] Multi-user support (compare profiles)
- [ ] Longitudinal tracking (profile over time)
- [ ] Normative comparison with population data
- [ ] Test-retest reliability computation
- [ ] Embedding-based corpus deduplication
- [ ] Profile versioning dashboard
- [ ] Big Five comparison chart (NEO-120 vs NEO-300 side by side)
- [ ] ChatLedger deep integration (extract communication style metrics)
- [ ] LLM-generated persona model refinement (use Claude to enhance rules-based persona)
- [ ] MCP endpoint + MCP-Apps custom UI for Psyche results (owner note 2026-07-22 note-6006e7, via @benhylak MCP-custom-UI post): consider exposing profile/report data through an MCP server so models consume it structured, and serving the result UI (radar charts, report views) as an MCP App rendered in-client. Design consideration only — spec'd in research/understanding-ai-compendium/COMMISSION.md (MCP endpoint design increment); understanding-AI project is the lead implementation.
