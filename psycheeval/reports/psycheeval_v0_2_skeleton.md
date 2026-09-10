# PsycheEval v0.2 — hard-pilot tri-model report (SKELETON)

**Status**: SKELETON. Pre-staged 2026-05-05 while v0.2 generation/judging is still in flight.
Fill in [PLACEHOLDER] markers once `metrics_<v0.2-tag>.json` exists. Numbers throughout
this skeleton must come from the canonical metrics JSON, not be hand-entered.

**Tag**: `<TAG_TBD>` — likely `2026-04-26_v02_hard_codex_only` extended with Opus author/judge.
**Supersedes**: v0.1 tri-model report (`psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model.md`).
**Date**: <COMPLETION_DATE>

---

## 1. TL;DR

The completed v0.2 hard-pilot tri-model run answers the seven research questions
locked into the v0.2 plan (D7), plus surfaces v0.2-specific findings the
length-control conditions and C5_CONTRACT separator make possible.

**The seven questions and their v0.2 answers** (fill in once analyzed):

1. **Does C4 beat C1_PADDED?** [PLACEHOLDER — answers behavioral structure vs profile length]
2. **Does C4 beat C4_SHUFFLED?** [PLACEHOLDER — coherent contract structure vs degraded same content]
3. **Does C5_CONTRACT beat C5?** [PLACEHOLDER — contract-repair-of-source-packet test; load-bearing for the v0.1 PAE-vs-no-contract confound]
4. **Does C5_CONTRACT beat C3 / C4?** [PLACEHOLDER — does the source packet add value once behavioralized]
5. **Does C5 remain pairwise-competitive while accumulating more red flags?** [PLACEHOLDER — replicates or revises the v0.1 §9 channel pattern]
6. **Do C5 / C5_CONTRACT red flags correlate with pairwise losses?** [PLACEHOLDER — answers the v0.1 §13 #4 question that v0.1 deferred]
7. **Which scenario families produce the biggest conditioning effects?** [PLACEHOLDER — uses the native scenario-family breakdowns analyzer block]

**Within-author scope qualifier remains load-bearing.** Same-author pairwise
isolates condition effects, so v0.2 headlines describe behavior conditional
on a specific author. Cross-author pairs were not judged in v0.2 (consistent
with v0.1).

**Methodology improvements over v0.1.** v0.2 uses the anchored 0–10 rubric
(addresses the Likert ceiling effect surfaced in v0.1 §13 #6), reports
cluster-bootstrap CIs alongside Wilson (addresses v0.1 §12 #5), and reports
scalar inter-judge agreement (addresses v0.1 §11b unmeasured-pooling
caveat).

**What this is not.** v0.2 remains a synthetic-personas / synthetic-scenarios
methodology pilot. It does not validate that Psyche profiles improve outcomes
for real users with real problems. Human-rater calibration is paper work.

---

## 2. What changed from v0.1

| Axis | v0.1 | v0.2 |
|---|---|---|
| Scenarios | 48 (6 per persona, opus-generated) | 80 (10 per persona, hand-crafted hard scenarios per brief §17) |
| Conditions | C0, C1, C3, C4 + C5 PI-only (5 total) | C0, C1, C1_padded, C3, C4, C4_shuffled + C5, C5_CONTRACT PI-only (8 total) |
| New v0.2 conditions | — | C1_padded (length control), C4_shuffled (structure control), C5_CONTRACT (PAE separator) |
| Rubric | 0–5 unanchored Likert | 0–10 anchored Likert with calibration examples |
| Red-flag taxonomy | 25 labels | 25 labels (unchanged; v0.2 adds analytical stratification, not new labels) |
| Authors | GPT-5.4 + GPT-5.5 + Opus | GPT-5.4 + GPT-5.5 + Opus (same panel) |
| Judges | GPT-5.4 + GPT-5.5 + Opus | GPT-5.4 + GPT-5.5 + Opus (same panel) |
| Pairwise scope | full same-author all-vs-all | same-author all-vs-all for original pairs; **C5_CONTRACT pairs restricted to {C3, C4, C5}** comparators (D2 lock; deferred edges in `reports/backlog/v02_deferred_pairwise_edges.json`) |
| Diagnostics | tie rates / PI-PS split / length buckets in `/tmp` ad-hoc scripts | native in `analyze.py`; cluster-bootstrap CIs, scalar inter-judge agreement, scenario-family breakdowns added |
| Cap-burn protection | manual `--missing-only` re-runs | `CapBurnHandler` with exponential backoff + cap_events.jsonl + checkpoint (resolved BACKLOG P1) |

---

## 3. Experimental design

### 3.1 Conditions

| Code | Description |
|---|---|
| C0 | No profile (baseline). |
| C1 | Trait labels only. Big Five percentile scores plus brief tag list. |
| C1_padded | C1 padded with benign meta-text to approximately C4 word count. Tests behavioral structure vs profile length. |
| C2 | *Reserved.* No content authored for v0.2 (same as v0.1). |
| C3 | Behavioral contract — if-then-style instructions. |
| C4 | C3 plus light scenario-conditional guidance. Strict superset of C3 in instruction content. |
| C4_shuffled | C4 with sentence/bullet order shuffled (deterministic seed). Tests coherent structure vs degraded same content. |
| C5 | Source packet (PI-only). Public-archetype packet without behavioral contract. |
| **C5_CONTRACT** | **PI-only.** Behavioral contract (= C3) wrapped around the C5 source packet, with explicit anti-mimicry rules. **Load-bearing PAE separator.** Per locked D1, contract takes precedence over packet; packet is treated as evidence/context, not as a style to imitate. |

### 3.2 Personas, scenarios, panel

8 personas (4 PI + 4 PS), 10 scenarios per persona = 80 hand-crafted hard
scenarios, distributed across 8 families per the v0.2 seed file.

3 author models (GPT-5.4, GPT-5.5, Opus). 3 judge models (same set;
tri-model panel mirrors v0.1).

### 3.3 Per-cell math

[PLACEHOLDER — fill from metrics JSON]

### 3.4 PI persona ethics note

PI personas are *fictionalized* public-anchor personas. Same wording as
v0.1 §4 ethics note carries forward.

---

## 4. Final corpus inventory

| Channel | Records | Status |
|---|---|---|
| Assistant outputs | [PLACEHOLDER] | [PLACEHOLDER] |
| Anchored scalar judging (3 judges) | [PLACEHOLDER] | [PLACEHOLDER] |
| Pairwise — GPT-5.4 judge | [PLACEHOLDER] | [PLACEHOLDER] |
| Pairwise — GPT-5.5 judge | [PLACEHOLDER] | [PLACEHOLDER] |
| Pairwise — Opus judge | [PLACEHOLDER] | [PLACEHOLDER] |
| Validation warnings | [PLACEHOLDER] | [PLACEHOLDER] |
| Cap events (cap_events.jsonl) | [PLACEHOLDER] | [PLACEHOLDER] |

---

## 5. Length controls — does C4 beat C1_padded? does C4 beat C4_shuffled?

[PLACEHOLDER — pull from `pairwise.pair_preference_cross_provider_same_author` for C1:C1_padded, C4:C1_padded, C4:C4_shuffled]

Expected v0.2 reading patterns:

- **C4 vs C1_padded**: if C4 still wins, the C4-over-C1 advantage from v0.1 was structural, not a length effect.
- **C4 vs C4_shuffled**: if C4 still wins, coherent contract structure adds value beyond having the same words.

---

## 6. C5_CONTRACT — does the contract repair source-packet fragility?

This section answers the load-bearing v0.1 §10 confound between PAE and
"absence of behavioral contract." Three comparisons matter:

### 6.1 C5_CONTRACT vs C5

[PLACEHOLDER]

If C5_CONTRACT >> C5 on profile_fit / red-flag rate / pairwise: the v0.1 C5
gap was substantially the absent contract. The PAE-specific signal weakens
correspondingly.

If C5_CONTRACT ≈ C5: the source packet itself was the problem; PAE evidence
strengthens.

### 6.2 C5_CONTRACT vs C3

[PLACEHOLDER]

This is the cleanest PAE test: contract held constant, packet present in
C5_CONTRACT and absent in C3. If C5_CONTRACT < C3, the source packet is
*adding* harm even with the contract. If C5_CONTRACT ≈ C3, the source
packet adds little (and PAE is weak in this direction). If C5_CONTRACT > C3,
the source packet provides useful evidence the contract alone can't.

### 6.3 C5_CONTRACT vs C4

[PLACEHOLDER]

C4 is C3 + scenario hints. C5_CONTRACT is C3 + source packet. This pair tells
us whether scenario-conditional guidance or source-packet evidence is more
useful when the contract is held constant.

---

## 7. Channel-disagreement pattern around C5 — does v0.1 §9 replicate?

[PLACEHOLDER — pull from native length-bucket diagnostics in v0.2]

In v0.1 §6g, C3 vs C5 was structural (robust across length buckets); C4
vs C5 was length-mediated; C0 vs C5 was dominated by length. v0.2's harder
scenarios should replicate or revise this pattern.

---

## 8. Scalar findings (anchored 0–10)

[PLACEHOLDER — pull from `primary_cross_provider.by_condition_C0C4_all_personas` (anchored block)]

### 8.1 All personas, cross-provider, anchored 0–10

[PLACEHOLDER]

### 8.2 PI-only

[PLACEHOLDER]

### 8.3 Headroom check

The anchored rubric was introduced specifically to recover headroom lost
to the v0.1 0–5 ceiling (means clustering 4.0–4.8). Comparison: v0.1 means
clustered in 16% of the rubric; v0.2 means cluster in [PLACEHOLDER]% of the
0–10 rubric. [PLACEHOLDER — comment on whether anchored rubric resolved the ceiling]

---

## 9. Red-flag findings (anchored, stratified)

Three views, all native in v0.2 analyzer:

### 9.1 By judge × condition

[PLACEHOLDER]

### 9.2 By cross-provider filter × condition

[PLACEHOLDER]

### 9.3 Output-level threshold (any-judge / 2+ / majority)

[PLACEHOLDER]

### 9.4 Direct PAE labels

[PLACEHOLDER — verify whether `caricature_public_anchor` and `public_archetype_echo` are now nonzero in v0.2 (they were zero in v0.1)]

---

## 10. Scenario-family breakdowns

Native scenario-family breakdowns answer "which scenario families produce
the biggest conditioning effects?"

[PLACEHOLDER — pull from `pairwise.scenario_family_breakdowns_same_author`]

Expected hypothesis to test (not assume): C3/C4 may matter most in
psychologically loaded families (interpersonal conflict, shame /
self-interpretation, procrastination) and least in flatter families
(creative feedback, epistemic uncertainty).

---

## 11. Judge halo and inter-judge agreement

### 11.1 Halo audit

[PLACEHOLDER — replicates v0.1 §11a structure]

Track whether the v0.1 single-cell finding (GPT-5.4 judging GPT-5.5-authored
on `calibrated_challenge` × C0 = +0.729) replicates in the harder v0.2
scenarios with the anchored rubric.

### 11.2 Scalar inter-judge agreement (NEW — addresses v0.1 §11b caveat)

[PLACEHOLDER — pull from `scalar_inter_judge_agreement_anchored`]

v0.1 §11b explicitly noted that scalar pooling rested on an unmeasured
assumption (only red-flag κ was measured). v0.2 reports per-dimension
Pearson + Spearman correlations between judges on the anchored rubric.
Compare against the v0.1 calculation on the legacy rubric: GPT-5.4 ↔ GPT-5.5
Pearson 0.74; GPT-5.4 ↔ Opus 0.60; GPT-5.5 ↔ Opus 0.60.

### 11.3 Red-flag agreement (κ on labels)

[PLACEHOLDER — replicates v0.1 §11b structure]

---

## 12. Threats to validity

Carries forward v0.1 §12 with the following modifications:

1. **Same-author pairwise scope** — unchanged threat; v0.2 retains scope qualifier.
2. **PAE confounds with absence of behavioral contract** — [PLACEHOLDER: significantly weakened, retired, or persistent depending on §6 results]
3. Synthetic personas, synthetic scenarios — unchanged.
4. **Length confound (quantified per condition)** — [PLACEHOLDER per-condition word counts from v0.2]
5. **Pairwise CIs** — v0.2 reports both Wilson AND cluster-bootstrap. Cluster unit: persona × scenario × author. Threat #5 from v0.1 substantially addressed.
6. Persona × condition imbalance for C5 — also affects C5_CONTRACT (PI-only by design).
7. Judge models from a small ecosystem — unchanged.
8. Forced-choice pairwise — unchanged.
9. Limited scenarios (80 in v0.2 vs 48 in v0.1; 10 per persona × 8 families).
10. **Likert ceiling** — v0.2 anchored rubric should partially resolve. [PLACEHOLDER — confirm with §8.3]
11. Mixed judge filters across sections — same disclosure as v0.1.
12. **No human raters** — paper-grade work; out of v0.2 scope.
13. (NEW) **C5_CONTRACT pair scope deferred** — v0.2 covers C5_CONTRACT vs {C3, C4, C5} only; full all-vs-all deferred per D2. Backfillable.

---

## 13. v0.3 / paper implications

Updates the v0.1 §13 list:

1. Resolved or substantially advanced in v0.2: C4 vs C1_padded, C4 vs C4_shuffled, C5_CONTRACT vs C5, scalar inter-judge agreement, cluster-bootstrap CIs.
2. Carried forward: stylometric audit of provider-family halo (D6 optional), human calibration sample (paper).
3. New v0.3 candidates: backfill of deferred C5_CONTRACT pairwise edges, C5_NONPUBLIC and other v0.3-deferred conditions if v0.2 surfaces a need, unblinded mechanism audit for direct PAE detection.

---

## 14. Appendix

### 14.1 Macro-averaged pair preference vs pooled (validation)

[PLACEHOLDER]

### 14.2 Halo audit, all three buckets

[PLACEHOLDER]

### 14.3 Cluster-bootstrap CIs (NEW)

[PLACEHOLDER — full table of pair-by-pair Wilson vs bootstrap CIs]

### 14.4 Artifact status

| Artifact | Status |
|---|---|
| v0.1 tri-model report | Superseded by v0.2 for current methodology |
| v0.2 corpus | [PLACEHOLDER] |
| v0.2 anchored scalar | [PLACEHOLDER] |
| v0.2 pairwise (full restricted scope) | [PLACEHOLDER] |
| v0.2 metrics JSON | [PLACEHOLDER] |
| v0.2 curated report (this document) | Current |

### 14.5 Run inventory

[PLACEHOLDER]
