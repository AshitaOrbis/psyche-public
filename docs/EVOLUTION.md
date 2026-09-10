# Psyche Evolution Chronicle

Living record of framework development. Each phase documents what changed, why, and what it means for published work that references earlier states.

## Version Timeline

| Version | Date | Instruments | Items | Key Change |
|---------|------|-------------|-------|------------|
| v1 | 2026-02 | 7 (Phase 1) | ~225 | Initial framework: Big Five + cognitive + clinical screening |
| v2 | 2026-02 | 17 (Phase 1+2) | ~786 | Added HEXACO, attachment, emotion regulation, empathy, grit, RIASEC, basic needs, locus of control, self-monitoring, interview |
| v3 | 2026-03 | 25 (+ tiers + CAT) | ~850+ | Tiered battery (Lite/Standard/Heavy), CAT adaptive testing, Heavy upgrades for 5 existing instruments |
| v4 | 2026-03 | 39 (+ 14 extended) | ~1,130+ | 14 new construct dimensions: wellbeing, self-compassion, mindfulness, moral foundations, perfectionism, self-control, curiosity, authenticity, time perspective, decision style, growth mindset, psychological flexibility, open-minded thinking, uncertainty intolerance |
| v4.1 | 2026-03 | 39 (unchanged) | ~1,130+ | Report model: DeepSeek V3 → Kimi K2.5. Safety clause v3 added to system prompt. 7-model benchmark + 3 synthetic stress tests. |

## Git Tags

| Tag | Commit | Published Content |
|-----|--------|-------------------|
| `v3.0-pre-phase4` | `6bccd61` | Blog posts 028, 030; research paper v3 |
| `v4.0-phase4-battery` | (tagged at Phase 4 commit) | — |
| `v4.1-kimi-k2.5-safety` | `1ca4bb2` | Benchmark report, synthetic stress tests |

---

## Phase 1: Foundation (v1)

**Date**: 2026-02-XX | **Schema**: v1 | **Instruments**: 7 | **Items**: ~225

### What Was Added

| Instrument | Items | Construct | Why This One |
|-----------|-------|-----------|--------------|
| IPIP-NEO-120 | 120 | Big Five + 30 facets | Open-source (IPIP), good facet coverage at moderate length. NEO-PI-R is proprietary; IPIP-NEO reproduces its structure without licensing cost. 120 items = 4 per facet, sufficient for initial profiling |
| CRT-7 | 7 | Analytical thinking | Discriminates reflective vs intuitive cognitive style with only 7 items. Numeric free-response format means it measures actual performance, not self-perception |
| NCS-18 | 18 | Need for Cognition | Complements CRT: CRT measures ability, NCS measures motivation to engage in effortful thinking |
| Rosenberg | 10 | Self-esteem | The standard self-esteem measure. Short, well-validated, provides a global self-evaluation baseline |
| SD3 | 27 | Dark Triad | Machiavellianism, narcissism, psychopathy in 27 items. Captures socially aversive traits that shape interaction patterns |
| PHQ-9 + GAD-7 | 16 | Depression/anxiety screening | Clinical screening baseline, not diagnostic. Establishes current affect state that may color other responses |
| Conversational Interview | 10-15 | Values, self-concept, behavioral examples | Semi-structured protocol adapted from Peters & Matz (2024). Captures qualitative data that structured instruments miss: narrative identity, value articulation, behavioral examples |

### Design Decisions

- **Open-source instruments only**: IPIP over NEO-PI-R, public-domain scales throughout. Psyche is MIT-licensed; proprietary instruments would create licensing conflicts.
- **Interview as instrument**: The Peters & Matz (2024) LLM personality assessment approach achieves r~.44 with assessment-optimized prompting. The interview provides raw behavioral examples for LLM analysis alongside structured self-report.
- **Clinical screening included**: PHQ-9/GAD-7 not for personality assessment per se, but to establish baseline affect. A participant completing instruments during a depressive episode will score differently on self-report scales; knowing this provides context for interpretation.

---

## Phase 2: Extended Battery (v2)

**Date**: 2026-02-XX | **Schema**: v2 | **Instruments**: 17 (10 new) | **Items**: ~786 total

### What Was Added

| Instrument | Items | Construct Gap Filled |
|-----------|-------|---------------------|
| IPIP-NEO-300 | 300 | High-precision Big Five (10 items/facet vs 4). Enables reliability comparison: does 2.5x more items meaningfully improve facet discrimination? |
| HEXACO-60 | 60 | Honesty-Humility (6th factor). Big Five misses integrity/sincerity; HEXACO captures it explicitly |
| ECR-R | 36 | Attachment dimensions (Anxiety + Avoidance). Predicts relationship patterns that trait models underspecify |
| ERQ-10 | 10 | Emotion regulation strategies (Reappraisal vs Suppression). How someone manages emotions, not what emotions they feel |
| IRI-28 | 28 | Empathy decomposition (4 dimensions). Distinguishes cognitive empathy, affective empathy, perspective-taking, and personal distress |
| Self-Monitoring-18 | 18 | Social flexibility vs consistency. Are they the same person in all contexts, or do they adapt? |
| LOC IE-4 | 4 | Internal/External locus of control. Attribution style for life outcomes |
| Grit-S | 8 | Perseverance + Interest consistency. Short-form grit captures stick-with-it-ness |
| RIASEC-48 | 48 | Vocational interests (6 types). Holland codes map to career orientation and domain motivation |
| BPNS-9 | 9 | Basic psychological needs (Autonomy, Competence, Relatedness). Self-determination theory baseline |

### Design Decisions

- **Parallel administration with NEO-120 + NEO-300**: Kept both to compare facet-level reliability at different item counts. The 300-item version is the gold standard for facet discrimination; the 120 provides a sanity check on whether the extra 180 items justify the test-taker burden.
- **Short-form preference**: For constructs where short and long forms exist, Phase 2 defaulted to short forms (Grit-S over Grit-O, BPNS-9 over BPNS-21, LOC IE-4 over Levenson IPC-24). Rationale: test-taker endurance across 786 items is already demanding. Heavy-tier upgrades to longer forms came in Phase 3.
- **Construct gap analysis**: Phase 2 instruments were selected by mapping Big Five facets to independent constructs that trait models underspecify. E.g., Big Five Agreeableness correlates with empathy but doesn't decompose it into cognitive/affective components — IRI-28 fills that gap.

### Published Content Referencing This Version

- **Ashita Orbis blog post 028**: Describes the 17-instrument battery and initial methodology
- **Ashita Orbis blog post 030**: Discusses the psychometric approach and initial results
- **Research paper v3** (convergent-personality-assessment.md): "seventeen instruments", "786 questionnaire items", Tables 1 and 2

These are historical records describing methodology as it existed at the time of writing.

---

## Phase 3: Tiered Battery & CAT (v3)

**Date**: 2026-03-XX | **Schema**: v3 | **Instruments**: 25 (6 tier variants + 2 CAT) | **Items**: ~850+ (tier-dependent)

### What Was Added

**Tier Architecture**:

| Tier | Instruments | Items | Use Case |
|------|------------|-------|----------|
| Lite | 15 | ~260 | Quick profiling: core constructs with shorter instruments |
| Standard | 20 | ~590 | Balanced: adds HEXACO and replaces NEO-60 with NEO-300 |
| Heavy | 33 | ~1,130+ | Full battery: long-form upgrades, CAT, extended constructs |

**New Instruments** (tier variants and CAT):

| Instrument | Items | Tier | Purpose |
|-----------|-------|------|---------|
| IPIP-NEO-60 | 60 | Lite | Compact Big Five for the Lite tier (replaces NEO-120 at that tier) |
| HEXACO-200 | 200 | Heavy | Full HEXACO (replaces HEXACO-60 in Heavy) |
| Grit-O | 12 | Heavy | Long-form grit (replaces Grit-S in Heavy) |
| BPNS-21 | 21 | Heavy | Full needs scale (replaces BPNS-9 in Heavy) |
| Levenson IPC-24 | 24 | Heavy | Tri-dimensional LOC (replaces IE-4 in Heavy) |
| Snyder SM-25 | 25 | Heavy | Full self-monitoring (replaces SM-18 in Heavy) |
| CAT Big Five | ~20-30 adaptive | Heavy | GRM-based adaptive Big Five refinement |
| CAT HEXACO | ~20-30 adaptive | Heavy | GRM-based adaptive HEXACO refinement |

### Design Decisions

- **Additive-with-replacement architecture**: Higher tiers include all lower-tier instruments, but substitute longer-form versions where available. A Heavy-tier participant never takes both BPNS-9 and BPNS-21 — they take only BPNS-21. This avoids redundancy while preserving backward compatibility.
- **Why tiers**: Different use cases need different depth. A quick demo profile (Lite, ~35 min) serves a different purpose than a comprehensive research profile (Heavy, ~160 min). Tiers let the framework scale without forcing everyone through the full battery.
- **CAT only in Heavy**: Computerized Adaptive Testing (Graded Response Model) requires calibrated item banks. The synthetic item banks generated for Phase 3 work for demonstration but need SAPA-calibrated parameters for production quality. Adding CAT to Lite/Standard before proper calibration would give false precision.
- **Profile schema v3**: Added `InstrumentManifest` tracking which tier was used and which instruments were completed. Profiles now self-document their provenance.

---

## Phase 4: Extended Constructs (v4)

**Date**: 2026-03-XX | **Schema**: v4 | **Instruments**: 39 (14 new) | **Items**: ~1,130+

### What Was Added

**Standard Tier** (4 new instruments, ~30 items):

| Instrument | Items | Construct | Why |
|-----------|-------|-----------|-----|
| SWLS | 5 | Life Satisfaction | Global subjective wellbeing. Short, widely validated (Diener et al.), complements PHQ-9/GAD-7 clinical screening with positive psychology baseline |
| AAQ-II | 7 | Psychological Flexibility | Experiential avoidance vs acceptance. Central construct in ACT; predicts adaptability under stress |
| Dweck ITIS | 8 | Growth Mindset | Implicit theory of intelligence. Fixed vs growth orientation affects learning behavior and response to failure |
| CEI-II | 10 | Curiosity | Epistemic curiosity (Stretching + Embracing). Trait-level exploration drive, distinct from Openness |

**Heavy Tier** (10 new instruments, ~254 items):

| Instrument | Items | Construct | Why |
|-----------|-------|-----------|-----|
| AOT-13 | 13 | Actively Open-Minded Thinking | Willingness to consider evidence against own beliefs. Complements CRT (ability) and NCS (motivation) with epistemic disposition |
| IUS-12 | 12 | Intolerance of Uncertainty | Prospective + Inhibitory anxiety about unknowns. Predicts decision paralysis and information-seeking behavior |
| SCS-26 | 26 | Self-Compassion | 6 subscales (self-kindness, self-judgment, common humanity, isolation, mindfulness, over-identification). Total score requires reverse-scoring negative subscales |
| MFQ-2 | 36 | Moral Foundations | 6 foundations (Care, Equality, Proportionality, Loyalty, Authority, Purity). Updated MFQ-2 replaces the original 5-foundation model |
| Frost MPS | 35 | Perfectionism | 6 dimensions (Concern over Mistakes, Doubts, Personal Standards, Parental Expectations, Parental Criticism, Organization) |
| MAAS | 15 | Mindfulness | Dispositional mindfulness (attention and awareness). Single-factor, distinguished from meditation practice |
| Authenticity Scale | 12 | Authenticity | 3 subscales (Authentic Living, Accepting External Influence [R], Self-Alienation [R]) |
| Tangney SCS | 36 | Self-Control | Trait self-control. Single total score; higher = greater capacity for impulse regulation |
| Maximization Scale | 13 | Decision Style | Maximizer vs Satisficer orientation. Affects decision-making speed, regret, and choice overload |
| ZTPI | 56 | Time Perspective | 5 temporal orientations (Past Negative, Past Positive, Present Hedonistic, Present Fatalistic, Future). Shapes motivation framing and goal pursuit |

### Design Decisions

- **Why these 14**: Selected through construct gap analysis. Phase 1-3 covered the "what you're like" space (personality traits, cognitive style, interpersonal patterns) but underrepresented "how you relate to yourself" (self-compassion, mindfulness, authenticity), "how you decide" (maximization, uncertainty tolerance, time perspective), and "what you value" (moral foundations, growth orientation).
- **4 Standard / 10 Heavy split**: Standard additions are short instruments (5-10 items each) that provide high information-per-item for key constructs. Heavy additions are longer instruments (12-56 items) that provide dimensional depth at the cost of test-taker time.
- **SCS-26 total scoring**: The Self-Compassion Scale computes a total score by reverse-scoring negative subscales (Self-Judgment, Isolation, Over-Identification) before averaging with positive subscales. This is Neff's recommended total computation, not a simple mean of all items.
- **AAQ-II reverse scoring**: All 7 items are reverse-scored (higher raw = more experiential avoidance; reversed so higher = more psychological flexibility). This aligns the direction with other scales where higher = more adaptive.
- **DecisionStyleProfile aggregation**: The Maximization Scale and IUS-12 combine into a `DecisionStyleProfile` in the synthesis pipeline, alongside ZTPI's temporal orientation. This captures "how this person approaches decisions" as a coherent construct cluster.
- **Backwards compatibility**: Profile schema v4 adds new optional fields; v3 profiles remain valid. The merge pipeline extracts new instrument scores when present and omits them when absent. No breaking changes to existing profiles or analysis results.

---

## Phase 5: Report Model Switch & Clinical Safety Engineering

**Date**: 2026-03-19 | **Report Model**: Kimi K2.5 (was DeepSeek V3) | **Prompt Version**: v3 (safety clause)

### What Changed

**Report generation model**: Switched from DeepSeek V3 to Kimi K2.5 via DeepInfra. K2.5 scored 84.2 composite vs DeepSeek V3's 60.0 on a 7-model benchmark (dual-judge: Opus 4.6 + GPT-5.4). Cost: $0.013/report (4x DeepSeek, still negligible).

**Safety clause added to system prompt** (3 iterations):

| Version | Problem Addressed | Key Change |
|---------|-------------------|------------|
| v1 | K2.5 inferred trauma without evidence, used "obsession" in headers, categorical attachment labels | Added: describe strategies as chosen behaviors, use hedged language, avoid pathologizing headers |
| v2 | Rubric ambiguity caused GPT-5.4 judge to penalize standard psychology terminology | Clarified judge rubric: attachment styles, Dark Triad scales are expected instrument vocabulary |
| v3 | K2.5 deployed somatic trauma frameworks ("nervous system on high alert") and therapeutic prescriptions ("earned secure attachment") on profiles with clinical history | Added: frame patterns as active strategies even with difficult history, stay in personality-description lane, no therapeutic technique recommendations |

### Benchmark Infrastructure

| Component | File | Purpose |
|-----------|------|---------|
| 7-model comparison | `benchmark/run_eval.py` | DeepSeek V3, Nemotron 3 Super, Kimi K2.5, Kimi K2, GLM-5, Hermes 3 405B, Opus 4.6 |
| Synthetic stress tests | `benchmark/run_synthetic.py` | 3 profiles probing clinical safety edge cases |
| Judge rubric | `benchmark/run_eval.py` JUDGE_RUBRIC | 5 dimensions, dual-judge (Opus + GPT-5.4), blinded |
| Benchmark report | `benchmark/report.md` | Full results with judge reasoning |
| Synthetic summary | `benchmark/synthetic/summary.md` | Stress test results |

### Synthetic Stress-Test Profiles

| Profile | Design Intent | K2.5 Safety (v3) |
|---------|--------------|-------------------|
| **clinical-edge** | PHQ-9 75+, suicidal ideation history, self-harm, substance use. Tests: avoids diagnosing, recommends professional help appropriately | Opus 85 / GPT 82 |
| **aggressive-conflict** | Dark Triad high, physical confrontations, manipulation. Tests: neutral framing without moralizing or excusing | Opus 90 / GPT 96 |
| **religious-intensity** | Divine visions, speaking in tongues, prophetic calling. Tests: respects religious experience without pathologizing or uncritically endorsing | Opus 95 / GPT 98 |

### Design Decisions

- **Why K2.5 over GLM-5**: GLM-5 scored higher (87.7 composite) but has 6-minute latency (367s vs K2.5's 111s) and higher cost ($0.016 vs $0.013). K2.5 at 84.2 is close enough with 3x faster generation.
- **Why not Opus**: Opus scored 90.2 but runs via Claude Max plan (not available as API for production). K2.5 via DeepInfra is the best available API model.
- **Safety clause philosophy**: "The person is an agent making choices, not a body executing threat responses." Reports should describe what people *do*, not what their nervous systems *are doing to them*. Growth areas are observations, not prescriptions.
- **Judge rubric philosophy**: Standard personality psychology vocabulary (attachment styles, Dark Triad scales, emotion regulation strategies) is the language of the instruments being reported. Penalizing it conflates clinical *language* with clinical *diagnosis*. The rubric explicitly permits instrument terminology while penalizing disorder diagnosis and pathologizing.

### Validation Status

- **Primary benchmark**: K2.5 Clinical Safety 68 → 83 (both judges agree)
- **Synthetic stress tests**: All 3 pass on both judges (avg 84, 93, 97)
- **TODO**: Re-run evaluation on real production reports shared by users to validate safety under real conditions (see BACKLOG.md)

---

## Phase 6: Context Isolation & the Fable Review Framework

**Date**: 2026-06-09 | **Analysis model**: adds Fable 5 (`claude-fable-5`) as method `llm-fable` | **Schema**: unchanged

### What Changed

**Contamination discovery**: All evaluative `claude -p` calls before this date ran non-blind — the Claude Code harness injected the subject's psychometric profile (via the `~/.claude/CLAUDE.md` import of `claude-context.md`) into context. Narrative scoring, psycheeval Opus judging, and (mildly) the canonical corpus analysis were affected; all codex/GPT and DeepInfra paths were clean. Full audit: `docs/reviews/context-contamination-audit-2026-06-09.md`.

**Isolation layer**: New `analysis/psyche_analysis/isolation.py` — `claude -p --safe-mode` + neutral cwd + canary verification (`--bare` is unusable on the Max plan; it refuses OAuth). Patched call sites: `analyze_corpus.py`, `analyze_narratives.py`, `psycheeval/llm.py`, `benchmark/run_eval.py`. Generation paths that intentionally consume the profile (`narrative_llm.py`) are unpatched by design.

**Fable Review Framework** (`docs/FABLE-REVIEW-FRAMEWORK.md`): five-phase protocol — (0) decontamination ✅, (1) blind corpus re-derivation with Fable ×3 runs for error bars, (2) adversarial audit of every standing profile claim, (3) interactive open-ended insight hunt licensed to leave the instrument ontology, (4) synthesis incl. the first Fable generation of `claude-context.md`.

### Design Decisions

- **No retroactive Opus re-runs**: the Fable re-derivation supersedes them; historical results stay archived untouched (owner decision).
- **`llm-fable` as a distinct method id**: Fable results sit beside, never replace, the Opus-era `llm-claude` baseline.
- **Canary as a real detector**: the isolation check must fail through a non-isolated invocation and pass through the isolated path; both directions verified at deployment.
- **Phase 3 interactive rather than scripted**: the highest-value historical insight (the empathy-channel correction) came from interactive correction loops, not batch output.

---

## Phase 7: Security & Scoring-Validity Remediation

**Date**: 2026-06-11 | **Trigger**: External security/correctness review (GPT-5.5 Pro, archived at `reviews/gptpro-2026-06-11.md`) | **Web app**: v0.2.0

### What Changed

**CAT scoring validity (P0)**:
- Reverse-keyed CAT items are now flipped (`k -> K-1-k`) before GRM likelihood computation in `registerResponse()`. Previously a "Very Accurate" answer to a reverse-keyed item *raised* theta instead of lowering it, biasing theta, SE, item selection, and percentiles on every reverse-keyed administration.
- `validateCATBankOrThrow()` hard-blocks CAT administration from invalid item banks: placeholder item text (the shipped synthetic banks), non-positive/non-finite discrimination, threshold/category mismatches, non-finite or unordered thresholds. The AdaptiveTestRunner shows an error instead of administering "[Anxiety item 1]" to a real user. CAT remains blocked until SAPA-calibrated banks land (BACKLOG.md).

**CAT priors and provenance (P1)**:
- Fixed-form scores without calibrated theta/se now seed an *approximate* CAT prior (inverse-normal of the 0-100 percentile, conservative SE ≥ 0.55) via `fixedFormPrior()`. Previously the documented "fixed-form theta as informative prior" never fired because fixed-form scorers don't emit theta/se. Approximate priors never trigger the skip-facet shortcut; only calibrated ones can.
- `ScaleScore.source` ("cat" | "fixed-form") makes score provenance explicit. CAT domain scores are now aggregated from CAT facet thetas (inverse-variance weighted) instead of being silently inherited from a different instrument's domain scores. ResultsViewer labels fixed-form carryovers.
- Fixed-form item ID exclusion is wired through the AdaptiveTestRunner so overlapping items in real banks are never re-administered.

**Store integrity (P1)**:
- `autoScoreCompleted()` requires exact item coverage (every instrument item answered with an in-range value) instead of counting unique response IDs — junk-ID imports can no longer mint empty/corrupt results. Adaptive instruments are excluded from auto-scoring.
- `importData()` deep-validates sessions and results: responses must reference real items with format-valid values, results must carry finite scores (normalized clamped to 0-100, theta/se sanity-checked), unknown instruments are dropped with a warning, and imports fail atomically with a user-visible error.

**Privacy honesty (P1)**:
- README privacy wording corrected: the app has no backend/accounts/cookies/analytics and app code collects no IPs, but the hosting provider (Cloudflare) still processes standard request metadata, and hosted report generation sends scores to DeepInfra. The unsupported "sessions expire after 7 days" claim was removed (localStorage has no TTL). Exported JSON flagged as potentially identifying (free-text answers + timestamps).

**Hardening**:
- `web/public/_headers`: strict CSP + security headers for Cloudflare Pages.
- `recover.html`: clipboard copy now warns + handles failure; raw localStorage blob no longer auto-displayed on parse failure.
- IPIP npm packages pinned to exact versions (item content must not drift via semver).
- GRM engine docs corrected: EAP uses an equally spaced normal-weighted grid, not Gauss-Hermite quadrature.
- Leaked absolute filesystem paths scrubbed from committed docs/logs.

**Privacy purge (follow-up adversarial review, same day)**: a second, independent review found real personal data committed to this public repository. Removed at HEAD: a corpus sample containing the author's full name and verbatim private SMS messages; archived benchmark reports and judge results generated from the author's real profile (the root-anchored `benchmark/.gitignore` patterns had not covered `archive/` copies — now unanchored); narrative analysis JSONs and a literary review quoting private relationship material. `benchmark/report.md` replaced with a redacted aggregate-only version. Names of third parties were structurally removed from analysis docs and externalized from code into gitignored config (`profiles/private-names.txt`, `PSYCHE_SELF_NAMES`, `PSYCHE_ARCHIVE_CONTACT`). psycheeval `internal_public_anchor` real-name fields nulled in committed data. `docs/ETHICS-PROTOCOL.md` bumped to v1.3 (current report model, accurate IP statement). Git history still contains the purged content — history rewrite is tracked in BACKLOG.md as a human action.

### Tests

29 new regression tests (`web/tests/security-fixes.test.ts`) covering reverse-key flipping, bank validation (including that the shipped banks are rejected), prior seeding, item exclusion, provenance/domain aggregation, auto-score coverage, and import validation. Suite: 94 tests passing.

### Design Decisions

- **Block, don't warn**: the previous `validateItemBank()` console warning was invisible to users and didn't even fire on the shipped banks (their synthetic discriminations are non-uniform). Invalid stimuli make theta meaningless; refusing to administer is the only honest behavior.
- **Approximate priors are interim**: percentile-derived priors are not on the calibrated IRT scale, hence the conservative SE floor and the rule that they can never skip a facet. Proper fix (fixed forms scored on the same IRT scale) is in BACKLOG.md.
- **No 7-day TTL implemented**: silently deleting a user's local results would be worse than the inaccurate claim; the claim was corrected instead.

---

## Schema Migration Notes

| Transition | Breaking? | Migration |
|-----------|-----------|-----------|
| v1 → v2 | No | New fields added, old profiles still valid |
| v2 → v3 | No | Added `InstrumentManifest`, `tier` field. Old profiles treated as implicit Standard tier |
| v3 → v4 | No | Added 10 new profile classes, new optional instrument score fields. Old profiles valid as-is |

All schema transitions have been additive. No existing profile JSON has been invalidated by any schema change.
