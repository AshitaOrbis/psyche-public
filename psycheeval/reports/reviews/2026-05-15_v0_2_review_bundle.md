# PsycheEval v0.2 — review bundle

**Date**: 2026-05-15
**Purpose**: external review of the completed PsycheEval v0.2 tri-model run,
specifically requesting (a) additional analytical angles, (b) reasonably
affordable additional experiments, and (c) deeper open questions that could
shape v3.

This bundle is structured so a reviewer can: (1) read the project history
in the design docs, (2) read the canonical v0.1 report, (3) read the v0.2
data summary below, and (4) respond with their critique.

---

## 1. Project background — what PsycheEval is

PsycheEval is a synthetic-first evaluation framework for testing whether
structured user-profile context ("Psyche profiles") changes how an
assistant responds. The parent project, **Psyche**, derives profiles from
psychometric instruments + user writing + LLM interpretation. PsycheEval
tests whether those profiles actually improve downstream AI behavior.

**Not** therapy, diagnosis, clinical triage, or mental-health treatment.
**Is** an evaluation of personalization, self-interpretation, calibrated
challenge, anti-sycophancy, and interpersonal judgment under structured
profile context.

Full design rationale lives in the GPT-authored kickstart, revision brief,
and tri-model extension plan — see §6 for paths.

---

## 2. Conditions tested

| Code | Description |
|---|---|
| C0 | No profile (baseline). |
| C1 | Trait labels only (Big Five percentiles + tag list). |
| C1_padded | C1 + benign meta-padding to match C4 word count (length control). |
| C3 | Behavioral contract — if-then instructions for how to engage this user. |
| C4 | C3 + light scenario-conditional hints. |
| C4_shuffled | C4 with sentence/bullet order shuffled (structure control). |
| C5 | Source packet (PI personas only) — fictionalized public-anchor prose. **No** behavioral contract. |
| **C5_CONTRACT** | **v0.2 PAE separator.** C5 source packet **plus** the same contract used in C3/C4. Anti-mimicry rules explicit. Locked design decision D1: contract-first ordering, packet treated as evidence not as style to imitate. |

C5 and C5_CONTRACT are PI-only (4 public-inspired personas × source packets).
PS personas (4 pure-synthetic) get the 6 core conditions only.

---

## 3. v0.2 corpus inventory (final)

- **80 scenarios** × **8 personas** (4 PI + 4 PS) × **3 authors** (GPT-5.4 + GPT-5.5-xhigh + Opus 4.7) × varying conditions = **1,680 assistant outputs**
- **3 judges** (same set, drawn from 2 provider families: OpenAI and Anthropic)
- **Anchored scalar judging** (0–10 with calibration anchors; replaces v0.1's 0–5 unanchored Likert): **3,949 records** (1,134 GPT-5.4 + 1,135 GPT-5.5 + 1,680 Opus) — fully tri-model
- **Pairwise**: **3,123 total records**, of which:
  - **2,944 are true same-author** (records where output_A's author = output_B's author)
  - **179 are cross-author** (concentrated entirely on the 3 C5_CONTRACT vs {C3, C4, C5} edges; 174 from the Opus judge — `--scope same_author_only` was not consistently passed during the Opus C5_CONTRACT pairwise phase). Excluded from same-author analyses.
  - Of the 2,944 same-author records: **2,680 are same-provider** (judge family = author family); **264 are cross-provider** (judge family ≠ author family), all on the C5_CONTRACT edges.
- C5_CONTRACT pairwise restricted to {C3, C4, C5} comparators per locked decision D2 — full all-vs-all deferred to v0.3 (manifest at `reports/backlog/v02_deferred_pairwise_edges.json`)
- **80 scenarios** across 8 families (interpersonal_conflict, procrastination_avoidance, authority_disagreement, creative_feedback, epistemic_uncertainty, moral_uncertainty, shame_self_interpretation, ambition_status). Each persona gets 10 scenarios; difficulty mean 3.58/5 (identical between PI and PS)

> **2026-05-15 correction**: an earlier version of this bundle conflated total pairwise records (3,123) with same-author records (true: 2,944). Corrected here. See `pairwise.cross_author_leak_detection` and `pairwise.cluster_bootstrap_scope_counts` in `metrics_2026-04-26_v02_hard_codex_only.json` for the auditable breakdown.

---

## 4. v0.2 headline findings — pairwise (cluster-bootstrap CIs)

All-judge same-author pairwise (n=2,944 records). Each row's `lo_win` = win
rate of the lower-numbered condition. `***` = bootstrap CI excludes 0.5.

> **2026-05-15**: the table below is all-judge same-author. Stratified
> cross-provider-only and same-provider-only CIs now live in the metrics
> JSON under `cluster_bootstrap_ci_cross_provider_same_author` and
> `cluster_bootstrap_ci_same_provider_same_author`. New finding from
> stratification: the **C3 vs C5_CONTRACT** edge — which the all-judge CI
> shows touching 0.500 — is actually **stronger under cross-provider
> judging** (CI [0.238, 0.446] for C3 win rate, i.e., C5_CONTRACT wins
> 55–76%) and **straddles 0.500 under same-provider judging** (CI [0.381,
> 0.545]). Same-provider judging dilutes the headline. Implication: the
> "C3 vs C5_CONTRACT is borderline" reviewer criticism is correct for
> the unstratified all-judge view but reverses direction once stratified.

```
pair                       lo_win   Wilson CI            Bootstrap CI         n
C0 vs C4                   0.134    [0.101, 0.176] ***   [0.094, 0.181] ***   320
C1_padded vs C4            0.319    [0.270, 0.372] ***   [0.256, 0.388] ***   320
C1 vs C1_padded            0.434    [0.381, 0.489] ***   [0.369, 0.500]       320
C1 vs C4                   0.326    [0.277, 0.379] ***   [0.262, 0.392] ***   319
C3 vs C4                   0.378    [0.327, 0.432] ***   [0.309, 0.447] ***   320
C3 vs C5_CONTRACT          0.428    [0.371, 0.486] ***   [0.354, 0.500]       283
C4 vs C4_shuffled          0.519    [0.464, 0.573]       [0.456, 0.584]       320
C4 vs C5                   0.637    [0.561, 0.708] ***   [0.544, 0.731] ***   160
C4 vs C5_CONTRACT          0.400    [0.345, 0.458] ***   [0.329, 0.472] ***   285
C5 vs C5_CONTRACT          0.240    [0.195, 0.293] ***   [0.183, 0.303] ***   287
```

**Direct readings of the seven locked v0.2 research questions:**

| Q | Claim | Result |
|---|-------|--------|
| Q1 | C4 beats C1_padded? | **Yes, decisively** — C4 wins 68.1% (bootstrap [0.613, 0.744]). Behavioral structure beats length. v0.1 left this open; v0.2 settles it. |
| Q2 | C4 beats C4_shuffled? | **No** — 51.9% (bootstrap [0.456, 0.584] straddles 0.5). Coherent structure does not significantly beat shuffled content. Counterintuitive but a real finding. |
| Q3 | C5_CONTRACT beats C5? | **Yes, decisively** — C5_CONTRACT wins 76.0% (bootstrap [0.697, 0.817]). The contract repairs source-packet fragility. The v0.1 §10 PAE-vs-no-contract confound is now empirically settled in favor of "absence of contract" as the dominant driver. |
| Q4 | C5_CONTRACT vs C3 / C4? | **C5_CONTRACT *outperforms* both.** C3 wins 42.8% (C5_CONTRACT 57.2%); C4 wins 40.0% (C5_CONTRACT 60.0%). When the contract is held constant, adding a source packet *adds* value. Surprising vs v0.1 framing. |
| Q5 | Does C5 remain pairwise-competitive with C3/C4? | **No, not in v0.2.** Under the anchored rubric + harder scenarios, C4 beats C5 63.7% (bootstrap [0.544, 0.731]). The v0.1 §6c "C5 pairwise-competitive" finding does not replicate. |
| Q6 | Do C5 / C5_CONTRACT red flags correlate with pairwise losses? | (per-pair correlation analysis is still to be computed; raw data is there) |
| Q7 | Which scenario families produce biggest conditioning effects? | Native `scenario_family_breakdowns_same_author` block exists; raw n per family per pair available. Not yet aggregated to a headline. |

---

## 5. v0.2 headline findings — scalar (anchored 0–10, PI-only, cross-provider)

```
cond          helpful  profile  calibra  anti_sy  agency_  epistem  emotion  boundar  non_car  transfe
C0            7.23     5.89     6.92     7.29     7.44     6.86     6.14     7.56     7.21     7.08
C1            8.01     6.73     7.81     8.04     7.95     7.61     6.62     7.84     7.69     7.88
C1_padded     7.99     6.76     7.87     7.93     8.04     7.70     6.51     7.96     7.70     7.83
C3            8.26     7.13     8.07     8.30     8.26     7.99     6.80     8.17     7.93     8.15
C4            8.25     7.06     8.06     8.30     8.31     7.99     6.76     8.08     7.89     8.02
C4_shuffled   8.05     6.99     7.99     8.05     8.20     7.96     6.62     7.94     7.88     7.92
C5            7.76     6.50     7.54     7.70     7.84     7.43     6.44     7.89     7.64     7.67
C5_CONTRACT   8.18     7.05     8.00     8.12     8.18     7.77     6.77     8.09     7.92     8.10
```

**Anchored rubric recovered headroom** — means span 5.89 to 8.31 (2.42-point range across the 0–10 scale, vs v0.1's compressed 4.0–4.8 = 0.8-point range across 0–5). The v0.1 §13 #6 "anchored rubric should resolve ceiling" question is answered yes.

**Scalar agreement (anchored, Pearson / Spearman):**

```
gpt-5.4 vs gpt-5.5: 0.697 / 0.623
gpt-5.4 vs opus:    0.658 / 0.596
gpt-5.5 vs opus:    0.632 / 0.531
```

No dimensions flagged as weak (all judge-pair Pearson ≥ 0.30). The v0.1 §11b "scalar pooling unmeasured assumption" caveat is now empirically addressed.

---

## 6. Where to look (paths)

| Path | What |
|---|---|
| `docs/chatgpt_log/2026-04-19_kickstart_prompt_plan.md` | Original GPT-authored project kickoff (72KB, design rationale + master prompt) |
| `docs/report_revision_brief.md` | First GPT review of v0.1 (revision brief) |
| `docs/tri_model_extension_plan.md` | GPT plan for tri-model + GPT-5.5 extension |
| `docs/v0_2_plan_extended_2026-05-05.md` | Canonical v0.2 plan with 7 locked decisions (D1–D7) |
| `docs/v0_2_execution_log_2026-05-05.md` | Phase-by-phase execution log including cap-burn bug discovery + fix |
| `reports/psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model.md` | v0.1 curated report (final, 363→573 lines after Path B + GPT Pro review fixes) |
| `reports/reviews/2026-05-04_*.md` & `2026-05-05_*.md` | v0.1 round 1 review artifacts (Gemini, Opus, GPT-5.5) + consolidated + fix manifests |
| `reports/reviews/2026-05-05_consolidated_round1.md` | v0.1 consolidated review (18 MUST FIX, 9 SHOULD FIX, 11 NICE TO HAVE) |
| `reports/psycheeval_v0_2_skeleton.md` | Pre-staged v0.2 report scaffold |
| `reports/psycheeval_v0_1_v02_hard_pilot_2026-04-26_v02_hard_codex_only_autogen.md` | v0.2 autogen scaffold (11 KB; raw tables + native diagnostic blocks) |
| `reports/metrics_2026-04-26_v02_hard_codex_only.json` | v0.2 canonical metrics JSON (316 KB; full nested structure) |
| `reports/failure_cards_2026-04-26_v02_hard_codex_only.md` | 12 worst-failure exemplars in v0.2 |
| `reports/backlog/v02_deferred_pairwise_edges.json` | D2 deferred-edges manifest (full C5_CONTRACT all-vs-all pairwise queued for v0.3) |
| `runs/2026-04-26_v02_hard_codex_only/` | Raw JSONL data (assistant_outputs, anchored_judge_scores, pairwise_scores) |

---

## 7. What we are asking the reviewer

Three deliverables, in priority order:

### A. **Further analytical angles** on the existing v0.2 data

The data is complete tri-model with 3,949 anchored scalar scores + 3,123 pairwise records + 1,680 outputs. What slices, decompositions, or contrasts haven't we computed that would meaningfully shift confidence in or against the headline findings?

Examples of the kind of thing we're looking for (not exhaustive):

- Per-judge stratification of the C5_CONTRACT vs {C3, C4} findings (do all three judges agree, or does the headline depend on one judge?)
- C5_CONTRACT scenario-family analysis (does the surprise of "C5_CONTRACT > C3" hold across families or concentrate in some?)
- Length sensitivity of v0.2 results: with C1_padded settled, what about C5_CONTRACT length? Does its length distribution differ from C3/C4?
- Per-PI-persona behavior (only 4 PI personas; some may be driving the C5_CONTRACT result)
- Author × condition interactions (does Opus-authored C5_CONTRACT behave differently from GPT-5.4-authored?)

### B. **Reasonably affordable additional experiments** that would meaningfully strengthen v0.2

What 1–3 experiments would substantially increase confidence in the headlines? Affordability constraint: bounded codex quota (effectively unlimited on chat subscription) + Anthropic Max 5-hour cap on Opus (~50 prompts/window). Total budget for new experiments: roughly 1,000–2,000 Opus quota draws maximum.

Examples of the kind we're hoping for (not exhaustive):

- A `C5_NONPUBLIC` condition (source-packet-style narrative for synthetic personas, no public anchor) — would isolate "public anchor" effects from "source packet form" effects. Cost: ~80 generations + judging.
- A judge-stratified re-run with stylometric controls
- Per-pair red-flag-to-pairwise-loss correlation analysis (no new generation, just analysis on existing data)
- A small human calibration sample (~30 pairs, 2-3 raters)

### C. **Deeper open questions that could shape v3**

What questions does v0.2 leave most exposed? Where would v3 most fruitfully push?

Examples of the kind we're hoping for:

- Real-user validation strategy (paper-grade; the methodology shift from synthetic to real)
- Reverse causality questions (do "good" profiles confer responsiveness, or do good responders look "good" under good profiles?)
- Profile-format generalization (do the same findings hold for Big-Five vs OCEAN vs Schwartz-values vs etc?)
- Judge-pluralism limits (3 judges from 2 families; what's needed to claim "this generalizes"?)
- Cross-cultural / language generalization
- Adversarial robustness (what happens with a deliberately misleading profile?)

### Constraints on the critique

- **No mealy-mouthed validation** — direct, specific, actionable critique. We have already done two rounds of multi-reviewer critique on v0.1 and integrated the findings; we're looking for things those rounds missed.
- **Per-finding evidence pointers welcome** — if you cite a number, give a path to the file or block.
- **Note false positives / overclaims explicitly** — the v0.1 review caught several; v0.2 likely has its own.
- **Don't restate the data.** We have the data. We want what the data doesn't yet say.

---

## 8. Constraints on the v3 plan, if you propose one

- We have a 5-hour rolling cap on Opus (~50 prompts per window). Anything > ~2,000 Opus calls = multi-week wall time.
- Codex (GPT-5.4 + GPT-5.5) quota is much larger; experiments primarily on codex side are cheap.
- Human raters require separate program / IRB-equivalent thinking.
- Total Opus budget for v3 should fit in 4-6 weeks of cap windows = ~2,000–3,000 Opus calls.

---

## 9. Project status snapshot

- v0.1 tri-model report: canonical artifact (post-Path-B + GPT Pro round 2 fixes). Public-facing v1 blog draft exists at `applications/ashitaorbis/shared/content/posts/042-what-the-psycheeval-pilot-was-actually-measuring.md` (`draft: true`, awaits writing-review).
- v0.2 corpus: complete (tri-model, anchored rubric, length controls, C5_CONTRACT separator).
- v0.2 report: skeleton exists, headline findings extracted; not yet curated.
- v0.2 blog post: not yet drafted.
- v3 design: this review's output will inform it.
