# Publication Review — Round 1 Consolidated

**Date**: 2026-05-05
**Document**: `reports/psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model.md`
**Round**: 1 (full document)
**Reviewers**: GPT-5.5 (xhigh) + Gemini 3.1 Pro + Opus 4.6 (hostile-but-fair)
**Source files**:
- `2026-05-04_gemini31_round1.md`
- `2026-05-04_opus46_round1.md`
- `2026-05-05_gpt55_round1.md`

---

## Executive summary

**18 MUST FIX, 9 SHOULD FIX, 11 NICE TO HAVE** after consolidation. Three findings were
flagged independently by multiple reviewers and constitute the highest-priority work:

1. **Scenario family count is wrong** — all three reviewers. GPT-5.5 went further than the
   text-only readers and read the live scenario file: actual count is **8 families**
   including omitted `ambition_status`, not 6 (per §4) and not 7 (per §12).
2. **§6 vs §14a pairwise divergence** — Gemini + GPT-5.5. The two tables use different
   judge-filter scopes; cross-provider-only changes marginal calls (C1 vs C5 CI flips
   from `***` to straddling 0.5).
3. **§7 / §5 / §8 sample-count phrasing is arithmetically wrong** — GPT-5.5, Gemini, Opus all
   flagged variants. "216 outputs × 3 judges" is records, not outputs. Per-cell math should
   be shown explicitly.

Two findings are reviewer-unique but **structurally most damaging** to the report's headlines:

- **PAE evidence doesn't isolate the obvious confound** (Opus MUST FIX #5). C5 has *no*
  behavioral-contract instructions; underperforming on `profile_fit` is a tautology, not
  evidence for archetype echo. To distinguish PAE from "no behavioral contract = lower
  profile_fit" you'd need either C5-with-contract or non-public-source-packet conditions.
  Neither exists. This challenges the central PAE story.
- **§11a halo prose is reversed** (GPT-5.5 MUST FIX #5). The +0.729 same-provider halo is
  *GPT-5.4 judging GPT-5.5-authored outputs*, not "GPT-5.5 judging GPT-5.4 outputs" as the
  text states. The numbers are correct; the prose interpretation is exactly backwards.

The findings cluster around three structural critiques: (a) the headlines about provider-
family halo (claim e) and PAE (claim f) are doing more work than the evidence supports;
(b) the report mixes judge-filter scopes across tables without declaring the asymmetry;
(c) sample-size and per-cell math is sloppy or absent throughout.

---

## MUST FIX (18 items)

### Multi-reviewer (highest signal)

| # | Issue | Tag | GPT-5.5 | Gemini | Opus | Claim |
|---|-------|-----|---------|--------|------|-------|
| 1 | **Scenario family count** — §4 says "6 families", lists 7. §12 says "7 families." Live scenario file has **8 families** including omitted `ambition_status`. Fix all three places. | [VALIDITY] | M1 | M4 | M6 | peripheral, but signals data-hygiene problems |
| 2 | **§6 vs §14a pairwise divergence** — Different judge-filter scopes used without disclosure. §6 = all 3 judges; §14a = cross-provider. C0 vs C4 differs (0.237 vs 0.260); C1 vs C5 marginal call flips between scopes. Reconcile or document. | [VALIDITY] / [TRANSPARENCY] | M3 | M3 | — | (b), (c) |
| 3 | **§7 / §5 / §8 sample-count phrasing wrong** — "(216 outputs × 3 judges)" misuses "outputs"; 216 is records, 72 is C5 outputs. §5's pairwise formula is mathematically incoherent. Show per-cell math: `authors × personas × scenarios = output count`. | [VALIDITY] / [CLARITY] | M2 | S1, S2 | S10 | (c), all pairwise claims |
| 4 | **Scalar effect-size / uncertainty reporting absent** — No SEs, CIs, or Cohen's d on scalar means. Likert ceiling 4.2–4.7 + judge κ ≈ 0.3 puts 0.05–0.20 differences at instrument noise floor. Multi-reviewer flag promotes this from SHOULD. | [SUFFICIENCY] | S3 | — | S8, S9 | (c), (f) |

### Reviewer-unique but structural

| # | Issue | Tag | Source | Claim |
|---|-------|-----|--------|-------|
| 5 | **PAE evidence doesn't control for "C5 has no behavioral contract" confound** — C5 omits the contract entirely. C5 underperforming on `profile_fit` reflects "no profile-fit instructions" not "public-archetype echo." To isolate PAE you'd need C5-with-contract or non-public-source-packet conditions; neither exists. Acknowledge confound in §10 and §12. | [SUFFICIENCY] | Opus M5 | (f) — central PAE story |
| 6 | **Halo prose reversed in §11a** — Text says "GPT-5.5 judging GPT-5.4 outputs produced a larger same-provider halo." Buckets in §14b are condition × author; the +0.729 cell is **GPT-5.4 judging GPT-5.5-authored outputs**. Numbers correct, interpretation backwards. | [VALIDITY] | GPT-5.5 M5 | (e) |
| 7 | **Same-author-only pairwise scope undercuts headlines** — Threats #6 admits cross-author pairs not judged. But §1, §6a, and the closing tagline frame "all conditioning beats baseline" universally. The result is within-author. Add "within same-author comparisons" qualifier to TL;DR + §6a; elevate threat #6 in §12. | [VALIDITY] | Opus M1 | (a), (b) |
| 8 | **"Scalar/pairwise tension is itself a core finding" overclaims** — One condition (C5) showing channel divergence is being upgraded to a "core finding about measurement" without (i) per-pair red-flag-vs-pairwise correlation, (ii) cross-condition pattern, or (iii) principled mechanism. Either downgrade to "open question for v0.2" (matches §10 hedging) or run §13#4 analysis now. | [VALIDITY] | Opus M2 | (d) |
| 9 | **Provider-family halo headline rests on n=1 cell** — §11a's load-bearing finding (+0.729) is one judge × one dimension (`calibrated_challenge`) × one condition (C0). On `emotional_accuracy` and `profile_fit` GPT-5.5's same-provider halo is *lower* than self-halo. The §11a analytical conclusion ("same-provider preference can exceed exact-self preference") is much stronger than the data supports. Scope to single cell or expand audit. | [VALIDITY] | Opus M3 | (e) |
| 10 | **Opus near-zero exact-self halo confounded with strictness** — §14b shows Opus rating its own outputs *below* cross-provider on `emotional_accuracy` (−0.115). Implausible as genuine self-bias absence; more plausibly Opus rates everything strictly. Reframe as "Opus's pattern is structurally different — possibly less self-bias, possibly stricter scoring." | [VALIDITY] | Opus M4 | (e) |
| 11 | **Pairwise CI non-independence / clustering** — Wilson CIs assume independence across pair records, but the same persona × scenario × author appears in C0vsC1, C0vsC3, etc. Treating each as independent Bernoulli inflates effective n. Macro-averaging in §14a addresses strata, not within-output clustering. Cluster-bootstrap CIs by persona × scenario; some `***` flags may not survive. | [TRANSPARENCY] | Opus M7 | (a), (b), (c) |
| 12 | **Omitted dimensions in Table 7b** — 7b drops `anti_syc`, `agency`, `boundary`. Critically, in 7a, C5 scores **highest** on `boundary` (4.74). Asserting below 7b that "C5 is below C3 and C4 on essentially every dimension" while hiding contradictory columns. Restore columns or explain exclusion + show C5 performance. | [TRANSPARENCY] | Gemini M2 | (c), (f) |
| 13 | **§5 1,152 arithmetic obscured** — Surrounding formula doesn't add up. Correct derivation: `3 authors × ((24 PI × 10 C-pairs) + (24 PS × 6 C-pairs)) = 1,152`. State plainly. | [CLARITY] | GPT-5.5 M4 | all pairwise |
| 14 | **Red-flag taxonomy size discrepancy** — §4 says 18 labels; schema has **24**. §11b says "mean κ across 18 labels" but per-pair counts are 18, 20, 19. Fix taxonomy count and explain undefined-κ handling. | [TRANSPARENCY] | GPT-5.5 M6 | (d), (f) |
| 15 | **"PS personas live in tougher scenario terrain" unsupported** — §8 prose claim. Live metadata: PI mean difficulty 3.58, PS mean difficulty 3.58 (equal). Either show the actual evidence (family mix? content severity?) or rephrase as "PS had higher flag rates" without causal claim. | [SUFFICIENCY] | GPT-5.5 M7 | (f), all C5 comparisons using PI/PS |

(Items 1–4 are multi-reviewer; items 5–15 are reviewer-unique. Numbering is consolidation
order, not priority within tier — items 5, 6, 7 are arguably the most damaging.)

Plus three more items folded in below as MUST FIX based on multi-flag promotion:

| # | Issue | Tag | Source | Reason for promotion |
|---|-------|-----|--------|---------------------|
| 16 | **PAE hedging asymmetric §1 vs §10** — §1 promotes scalar result before introducing contradicting pairwise; §10 is well-calibrated. Reorder §1 to lead with "C5 produces mixed signals." | [CLARITY] | GPT-5.5 S2 + Opus S5 | Multi-flag promote (SHOULD → MUST) |
| 17 | **κ-related framing problems** — (a) §11b says κ values are "fair" without citing benchmark scale, (b) inter-judge κ on red-flag labels is being used to justify scalar pooling (different measurement). Either compute scalar κ/ICC or weaken pooling justification. | [TRANSPARENCY] | GPT-5.5 S6 + Opus S4 | Multi-flag promote |
| 18 | **Headline conflates two findings of unequal robustness** — "all four beat baseline" (4-way) and "behavioral > trait" (one specific comparison) presented as parallel. Make the asymmetry explicit in TL;DR. | [CLARITY] | GPT-5.5 S1 + Opus S1 | Multi-flag promote |

---

## SHOULD FIX (9 items)

| # | Issue | Tag | Source | Claim |
|---|-------|-----|--------|-------|
| 1 | **"Judge-dependent" inconsistent definition** — §6b labels C1 vs C5 "judge-dependent"; §6c labels C3/C4 vs C5 "indistinguishable." Threshold not stated. Add explicit rule (e.g., "judge-dependent = at least one slice excludes 0.5 and another doesn't") or fold categories. | [CLARITY] | Opus S2 | (c) |
| 2 | **Length confound admitted but not quantified** — §12 #4 admits but defers. The 648 existing outputs allow trivial per-condition word-count statistics; check whether C5 vs C3 length differences explain pairwise null. | [VALIDITY] | Opus S3 | (a), (b), (c) |
| 3 | **§7a "overall" column misleading for C5** — Bolded `C5 = 4.44` (highest) reads as "C5 is best on scalar" before reader hits the §7a caveat. Bold the PI-only column instead, or move §7b ahead, or remove C5 from the bolded column. | [TRANSPARENCY] | Opus S6 | (c) |
| 4 | **Stylistic-similarity / training-data alternatives for sibling halo** — Provider-family halo could be (a) family preference, (b) stylistic similarity in outputs, or (c) shared training-data biases. Report assumes (a) without addressing (b)/(c). At minimum mention alternatives in §11a or §12; a short stylometric check would help. | [VALIDITY] | Opus S7 | (e) |
| 5 | **Likert ceiling caveat buried in v0.2 section** — §13 #6 admits 4.2–4.7 ceiling but §7 treats 0.05–0.20 differences as substantive. Surface caveat in §7 or §9, not just deferred to v0.2. | [CLARITY] | Opus S8 | (c), all of §6 marginals |
| 6 | **Mixed judge filters need methods paragraph** — Scalar uses cross-provider; red flags use all 3; §6 pairwise uses all; §14a uses cross-provider. Declare the asymmetry up front before any tables. | [TRANSPARENCY] | GPT-5.5 S4 | (a)–(f) |
| 7 | **Unexplained "19 misc" scalar records** — §14d says `judge_scores.jsonl` has "1,944 scalar + 19 misc." Identify what they are and whether all tables exclude them. | [TRANSPARENCY] | GPT-5.5 S5 | scalar support |
| 8 | **PAE wording sometimes stronger than evidence** — §8 says C5 outputs "more often resemble caricatures" but direct PAE labels (`caricature_public_anchor`, `public_archetype_echo`) are zero in judged data. "Consistent with PAE" is supported; "red-flag signature of public-archetype echo" is too strong. | [VALIDITY] | GPT-5.5 S2 (already partially folded into MUST #16; this is the residual evidence-mapping piece) | (f) |
| 9 | **`***` and "marginal" same row contradictory** — §6b "C3 vs C4 — pooled `***` 0.446" labeled "marginal." Define `***` as mechanical CI flag (CI excludes 0.5), not strength indicator. | [CLARITY] | GPT-5.5 N1 + Opus N2 | promoted from NICE on multi-flag |

---

## NICE TO HAVE (11 items)

| # | Issue | Tag | Source |
|---|-------|-----|--------|
| 1 | **§1 sentence repeated in §9** — "This scalar/pairwise tension is itself a core v0.1 finding" appears twice. Cut one. | [CLARITY] | Opus N1 |
| 2 | **§3 "It cannot" item 3 link to v0.2** — Explicit pointer to `C1_padded` and `C4_shuffled` for narrative continuity. | [TRANSPARENCY] | Opus N3 |
| 3 | **§11a Opus row asymmetry** — `n/a` in same_provider but `+0.021` in exact_self. With no Anthropic sibling, exact_self is structurally a 1-way comparison for Opus and 2-way for the GPTs. Surface this. | [CLARITY] | Opus N4 |
| 4 | **§13 split implications vs operational items** — "questions v0.2 must answer" vs "operational dependencies." | [CLARITY] | Opus N5 |
| 5 | **Closing tagline overclaim** — "*Three converging or diverging measurement channels…*" hides the same overclaim as MUST #8. Replace with a more boring closing sentence (or remove entirely once #8 is fixed). | [TRANSPARENCY] | Opus N6 |
| 6 | **Halo terminology drift** — Standardize on "same-provider halo"; drop "provider-family halo" / "provider-sibling halo" mixed usage. | [CLARITY] | Gemini N1 |
| 7 | **Colloquial framing tags** — "The honest framing for v0.1 is…" / "The honest claim:" feel informal for a methodology report. Refine to e.g. "Synthesized finding:" or simply state the claim. | [CLARITY] | Gemini N2 |
| 8 | **Define `low` and tie handling per pairwise table** — Captions should clarify decisive-win-rate vs pooled vs macro. | [CLARITY] | GPT-5.5 N1 (note: this part also feeds SHOULD #9 above) |
| 9 | **"Statistically distinguishable" → "distinguishable under this judge/CI analysis"** — §3 sounds broader than the Wilson-CI, no-human-rater setup supports. | [CLARITY] | GPT-5.5 N2 |
| 10 | **Scenario distribution table** — A small PI/PS × family × difficulty table would make the C5-scope caveat and PI/PS confound auditable at a glance. | [SUFFICIENCY] | GPT-5.5 N3 |

---

## Summary by ReviewBench category

| Category | MUST | SHOULD | NICE | Total | Comment |
|----------|------|--------|------|-------|---------|
| [VALIDITY] | 11 | 2 | — | 13 | Heaviest tier; concentrated on halo, PAE, scope qualifiers |
| [TRANSPARENCY] | 5 | 3 | 2 | 10 | Mixed-judge-filter and per-cell-math problems |
| [CLARITY] | 2 | 3 | 7 | 12 | Mostly polish, but multi-reviewer promotions live here |
| [SUFFICIENCY] | 2 | — | 1 | 3 | Effect sizes + PAE confound + scenario table |
| [CONTRIBUTION] | — | — | — | 0 | None — no reviewer challenged the basic value of the work |

---

## Cross-reviewer concentrations (signal indicators)

The strongest signals — independently surfaced by multiple reviewers — are exactly the
findings most likely to require structural rework rather than text edits:

1. **Family count, sample-count phrasing, judge-filter divergence** (all three reviewers).
   Easily fixable but reflect data-hygiene gaps that compound trust if left.
2. **PAE story is overclaimed in two distinct ways** (Opus structural + GPT-5.5 evidence-mapping).
   Both push toward §10's hedging being correct and §1/§8's framing being wrong.
3. **Halo claims are weaker than the headline suggests** (Opus n=1 + GPT-5.5 reversed prose).
   Different angles, same conclusion: the §11a story needs significant tightening.

## Reviewer-specific signal

- **GPT-5.5** found 7 issues only it could find — all data-grounded (live JSON / schema / scenario file). These are the items that text-only reviewers structurally cannot surface.
- **Opus** found 4 issues only it found — all structural / hostile-but-fair (PAE confound, scope qualifier, n=1 halo, "core finding" overclaim).
- **Gemini** found 1 issue only it caught (Table 7b column omission). Gemini's value here is sentence-level + table-level scrutiny.

This is exactly the panel composition the skill aimed for — coverage of three different
failure modes with low cross-reviewer overlap (good for breadth) but high agreement on
the few items all three flagged (good for priority).
