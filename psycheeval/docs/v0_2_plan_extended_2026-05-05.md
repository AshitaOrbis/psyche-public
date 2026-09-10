# PsycheEval v0.2 — Extended Plan (post-v0.1 review, post-GPT-Pro)

**Date**: 2026-05-05
**Supersedes**: `docs/v0.2_plan.md` (2026-04-24, codex-only era — archived as historical reference)
**Status**: planning. Some phases below are ready to execute; others gate on Opus quota or design decisions.

This plan reconciles three inputs:

1. **The original v0.2 design** (`docs/v0.2_plan.md`): length controls (C1_padded, C4_shuffled), anchored 0–10 rubric, harder hand-crafted scenarios (80 scenarios across 8 personas), extended red-flag taxonomy. **Codex-side execution is complete** — 1,040 outputs across GPT-5.4 + GPT-5.5 authors, anchored scalar judging done, pairwise done.
2. **The v0.1 → tri-model lessons** (Path B + Round 2 fix manifests): probe isolation, native diagnostics for length-bucketing / PI-PS / tie rates, framing rules, banned-phrase guardrails, halo-direction correction.
3. **The GPT Pro consolidated review of v0.1** (`~/.claude/uploads/.../4c490e7d-psycheeval_v01_cleanup_prompt_for_claude_code.md`): proposed new condition expansions (C5_CONTRACT priority, plus C3_SOURCELESS / C5_NONPUBLIC / C5_SHORT / C5_BEHAVIORALIZED), red-flag stratification, scenario-family breakdowns, cluster-bootstrap CIs, scalar ICC, stylometric provider-family halo audit, human calibration sample design.

---

## 1. Status snapshot — what's actually done vs pending

### Done (no v0.2 work needed)
- v0.2 code complete: `v02_prepare`, `--rubric anchored`, length-control conditions, parallel execution, anchored Pydantic models
- v0.2 codex-side corpus: **1,040 outputs** from GPT-5.4 (520) + GPT-5.5 (520) across 7 conditions × 80 scenarios × 8 personas (with C5 PI-only)
- v0.2 codex-side anchored scalar judging: complete
- v0.2 codex-side pairwise: complete
- 80 hand-crafted hard scenarios + extended red-flag taxonomy in place

### Pending (immediate v0.2 work)
- Opus author outputs across v0.2 (gated on Opus quota; ~640 calls expected, similar to v0.1 Opus authoring)
- Opus judging on full v0.2 corpus (anchored scalar + pairwise; ~3,500–4,000 calls; gated on Opus quota)
- **C5_CONTRACT condition** — user-approved at 2026-05-05; needs prompt template + content authoring + generation + judging
- Native analyzer port of Round 2 diagnostics (length-bucket / PI-PS / tie-rate / scenario-family / red-flag-stratified / cluster-bootstrap option)
- v0.2 curated report
- v2 blog post

### Pending (paper-grade, may slip past v0.2)
- Cluster-bootstrap CIs for pairwise (replaces or supplements Wilson)
- Scalar inter-judge ICC / Krippendorff's α
- Stylometric audit of provider-family halo
- Human calibration sample (~30–50 pairs, 2–3 raters)
- Unblinded mechanism audit for PAE (separate judge with C5 source visibility)

### Hardening (P1 backlog, blocks long Opus runs)
- **Cap-burn fix in `judge.py`** — `claude -p` rc=1 cap-window failures don't sleep/back-off; observed 3× during v0.1 J3. This must land before any extended Opus campaign or we burn quota windows on rc=1 spins.

---

## 2. New v0.2 design decisions vs the original plan

### Authors panel: tri-model, not two-model

The original v0.2 plan was written before GPT-5.5 landed and before the tri-model extension to v0.1. v0.2 should match v0.1's tri-model panel: **GPT-5.4 + GPT-5.5 + Opus** as both authors and judges. Codex side is done; Opus side is the remaining work.

### Conditions: original 7 plus new GPT-Pro additions

**Committed to v0.2** (original design):

| Code | Status | Notes |
|---|---|---|
| C0 | done (codex), pending (Opus author) | Baseline |
| C1 | done (codex), pending (Opus author) | Trait labels |
| C1_padded | done (codex), pending (Opus author) | Length control for C1 |
| C3 | done (codex), pending (Opus author) | Behavioral contract |
| C4 | done (codex), pending (Opus author) | Contract + scenario hints |
| C4_shuffled | done (codex), pending (Opus author) | Structure control for C4 |
| C5 | done (codex, PI-only), pending (Opus author) | Source packet (no contract) |

**Newly committed for v0.2** (user-approved 2026-05-05):

| Code | Description | Justification |
|---|---|---|
| **C5_CONTRACT** | Source packet + same behavioral contract as C3 | Load-bearing PAE separator. Discriminates "PAE" from "no behavioral contract" — currently confounded in v0.1 §10. If C5_CONTRACT ≈ C3 on profile_fit, the v0.1 C5 gap was the absent contract. If C5_CONTRACT < C3 on profile_fit, that's PAE evidence with the contract held constant. |

**Deferred to v0.3 unless time/quota allows**:

| Code | Description | Why deferred |
|---|---|---|
| C5_NONPUBLIC | Source-packet-style narrative for synthetic personas (no public anchor) | Requires authoring 4 new source-packet-style prose blocks per PS persona — content authoring task with no programmatic shortcut. v0.3 is the right place. |
| C5_SHORT | C5 source packet truncated to match C3/C4 length | Programmatic, cheap to add — but only useful if v0.2's length-bucket analysis (already in §6g for v0.1) doesn't already settle the question. v0.3 if the length-bucket evidence in v0.2 leaves residual ambiguity. |
| C5_BEHAVIORALIZED | Translate C5 source packet into if-then behavioral instructions | Requires per-persona translation — meaningful authoring effort. v0.3. |
| C3_SOURCELESS | Behavioral contract without source packet | This is **already what C3 is.** The GPT Pro framing was making the C3-vs-C5_CONTRACT comparison explicit by relabeling C3 in that context. No new condition needed; just framing in the v0.2 report. |

### Diagnostics: bake the v0.1 Round-2 additions into the analyzer

In v0.1 the length-bucket / PI-PS / tie-rate diagnostics were computed in an ad-hoc script and saved to `/tmp/pairwise_diagnostics.json`. For v0.2, port these into `analyze.py` so they regenerate with each metrics run:

- Tie rates per pair (already columns in §6e)
- PI/PS-stratified pairwise (§6f)
- Length-bucketed pairwise for C5-involving pairs (§6g) — **most consequential v0.1 finding**
- Red-flag stratification by judge / cross-provider / output-level (deferred from v0.1)
- Scenario-family breakdowns (deferred from v0.1; n=10 scenarios per family in v0.2 vs 6 in v0.1, more tractable)

### Methodology hardening: which paper-grade items make v0.2

| Item | Decision |
|---|---|
| Cluster-bootstrap CIs by persona × scenario × author | **In v0.2.** ~50 lines of Python; non-blocking; resolves a known threat (§12 #5 in v0.1 report). |
| Scalar inter-judge ICC / Krippendorff's α | **In v0.2.** Necessary to defend scalar pooling; v0.1 §11b explicitly flagged its absence. |
| Stylometric audit of provider-family halo | **Optional in v0.2.** Cheap (response length, formatting density, hedging frequency on existing outputs). Worth including if writeup time allows. |
| Human calibration sample | **Defer to paper.** Out of v0.2 scope; design as separate program. |
| Unblinded mechanism audit for PAE | **Defer to v0.3 or paper.** Requires re-prompting a judge with source-packet visibility — additional run. |

---

## 3. Phased execution plan

### Phase 0 — Pre-flight hardening (no LLM calls, ~2 hours)

Blocking work that must land before any extended LLM run.

| # | Task | File / location | Estimate |
|---|------|-----------------|----------|
| 0.1 | Fix `judge.py` cap-burn: detect rc=1, exponential backoff (60→300→900→1800s), max 5 retries, log to validation_warnings.jsonl | `src/psycheeval/judge.py` | ~1h |
| 0.2 | Test for cap-burn handling (mocked `claude -p` returning rc=1 → assert sleep is called) | `tests/test_judge_cap_burn.py` | ~30m |
| 0.3 | Native port of Round-2 diagnostics into analyzer: `_compute_tie_rates`, `_compute_pi_ps_split_pairwise`, `_compute_length_buckets` | `src/psycheeval/analyze.py` | ~1.5h |
| 0.4 | Native port: red-flag stratification (by judge, cross-provider, output-level any/2+/majority) | `src/psycheeval/analyze.py` | ~1h |
| 0.5 | Native port: scenario-family breakdowns of condition effects | `src/psycheeval/analyze.py` | ~45m |
| 0.6 | Tests for new analyzer blocks (extend `test_analyzer_smoke.py`) | tests | ~1h |

**Exit criteria**: judge.py rc=1 paths back off, analyzer produces native diagnostics, all tests green.

### Phase 1 — C5_CONTRACT design + scaffolding (~3 hours)

| # | Task | Notes |
|---|------|-------|
| 1.1 | Add `C5_CONTRACT = "C5_CONTRACT"` to `Condition` enum | `src/psycheeval/models.py` |
| 1.2 | Add `C5_contract: ProfileConditionText \| None` to `ProfileConditions`; update normalize/run wiring | parallels C5/C2 wiring |
| 1.3 | Compose C5_CONTRACT prompt: prepend the existing C3 behavioral-contract template to the existing C5 source-packet body, with explicit framing that the contract takes precedence | Decision: contract first then packet, or packet first then contract? Default: contract first (matches C3 structure). |
| 1.4 | Update `PILOT_CONDITIONS["v02_hard_pilot"]["public_extra"]` to include `C5_CONTRACT` | `src/psycheeval/config.py` |
| 1.5 | Generate C5_CONTRACT outputs for the 4 PI personas across 80 scenarios × 3 authors (GPT-5.4, GPT-5.5, Opus) = 960 outputs total. Codex side first (~640), Opus side gated on quota. | `psycheeval.run --conditions C5_CONTRACT` |
| 1.6 | Anchored scalar judging on C5_CONTRACT outputs (3 judges × 960 outputs = ~2,880 calls). Codex-side first. | gated on cap-burn fix in Phase 0.1 |
| 1.7 | Pairwise on C5_CONTRACT: include in the existing same-author pair set. New pairs added: C5_CONTRACT vs C0, C1, C1_padded, C3, C4, C4_shuffled, C5 = 7 pairs × 4 PI personas × 80 scenarios × 3 authors = ~6,720 pairs per judge. 3 judges = ~20,160 pairwise calls. **Substantial.** | gated on cap-burn fix |

**Phase 1 cost estimate**: at current pricing, ~$60–100 for codex-side generation + judging, plus Opus quota draw for the Opus side.

**Phase 1 risk**: pairwise scope balloons because C5_CONTRACT pairs with everything. Could limit to "interesting" pairs (C5_CONTRACT vs {C3, C4, C5}) to cut by 60%. **Decision needed before Phase 1.7.**

### Phase 2 — Opus authoring on full v0.2 corpus (Opus quota dependent, ~1 week wall time)

| # | Task | Notes |
|---|------|-------|
| 2.1 | Generate Opus author outputs across 7 original conditions: 8 personas × 80 scenarios × 1 author = 640 outputs (PI gets +80 for C5 = 720) | `psycheeval.run --pilot v02_hard_pilot --authors opus` |
| 2.2 | Opus author outputs on C5_CONTRACT (already covered in Phase 1.5 if Opus quota allows there) | combined with Phase 1.5 in practice |
| 2.3 | Validate corpus completeness (per-cell coverage diagnostic) | `psycheeval.coverage --tag <v0.2>` |

**Phase 2 risk**: Opus weekly quota. Run can be split across windows; resume-safe writes already protect against partial runs (post-cap-burn fix).

### Phase 3 — Tri-model judging on full v0.2 corpus (~3,000–4,000 Opus calls)

| # | Task | Notes |
|---|------|-------|
| 3.1 | Anchored scalar judging by Opus on full v0.2 corpus (= 1,040 codex outputs + 720 Opus outputs + 320 C5_CONTRACT outputs ≈ 2,080 outputs). Opus is the missing 3rd judge. | requires cap-burn fix |
| 3.2 | Pairwise judging by Opus on same-author pairs across the full corpus | requires cap-burn fix; ~1,500–2,500 pairwise calls |
| 3.3 | Mid-run targeted-block decision gate (analogous to v0.1 J3): if Opus's marginal-pair preferences confirm the codex-side direction on the most informative pairs, accept; else investigate before continuing. | per the v0.1 decision-gate pattern |

### Phase 4 — Analysis on completed v0.2 corpus

| # | Task |
|---|------|
| 4.1 | Run `psycheeval.analyze --tag <v0.2-tri-model> --pilot v02_hard_pilot` to produce `metrics_<tag>.json` with all native diagnostics (length-buckets / PI-PS / tie-rates / scenario-family / red-flag-stratified / cluster-bootstrap) |
| 4.2 | Generate failure cards (`failure_cards_<tag>.md`) |
| 4.3 | Generate autogen scaffold (`psycheeval_v0_2_autogen.md`) |
| 4.4 | Compute scalar inter-judge ICC / α as a sanity check on scalar pooling |
| 4.5 | Optional: stylometric provider-family halo audit (length, formatting density, hedging) on existing outputs |

### Phase 5 — Curate v0.2 report

Mirror the v0.1 process:

| # | Task | Reference |
|---|------|-----------|
| 5.1 | Path B-style first-pass curation against the autogen scaffold. Apply v0.1 framing rules (banned phrases / required language / scope qualifiers). | follows `2026-05-05_fix-manifest_round1.md` patterns |
| 5.2 | First multi-reviewer round (`/publication-review` against the curated v0.2 report) | uses GPT-5.5 + Gemini 3.1 Pro + Opus 4.6 panel |
| 5.3 | Apply consolidated fixes; persist all 5 review artifacts to `reports/reviews/` per the new convention | persistence is now mandatory |
| 5.4 | (Optional) Round 2 delta-mode review | only if Round 1 surfaces structural issues |
| 5.5 | Generate HTML; push to the reading device for read-through | `send-to-the reading device` skill |

### Phase 6 — v2 blog post

Mirror the v1 post process:

| # | Task |
|---|------|
| 6.1 | Spin up writer session via `remote-session` skill, briefed with the v0.2 curated report as ground truth |
| 6.2 | Writer produces draft + outline → user review on the reading device |
| 6.3 | `/writing-review` + `/publication-review` against draft |
| 6.4 | Deploy via Ashita Orbis 3-tier pipeline |

### Phase 7 — Paper-grade methodology (parallel, optional for v0.2)

These can run in parallel with Phases 5–6 or slip past them:

| # | Task | Notes |
|---|------|-------|
| 7.1 | Cluster-bootstrap CIs by persona × scenario × author for all major pairs | landed in Phase 0.3 if scope allowed |
| 7.2 | Stylometric audit of provider-family halo | deferred from v0.1 |
| 7.3 | Begin design of human calibration sample (30–50 pairs, 2–3 raters) | proposal doc, not execution |
| 7.4 | Unblinded mechanism audit prompt for PAE (separate judge with C5 source visibility) | v0.3 candidate |

---

## 4. Decisions — locked 2026-05-05

All seven decisions were locked at planning time per user direction "nail down the seven decisions now rather than progressively." Defaults adopted in every case. Any genuinely new judgment calls that arise during execution surface as needed.

| # | Decision | Locked value | Notes |
|---|----------|--------------|-------|
| **D1** | C5_CONTRACT prompt order | **Contract-first.** | The behavioral contract takes precedence; the source packet is treated as evidence/context, not as a style to imitate. Prompt must explicitly include: (i) prioritize contract over source packet; (ii) do not perform, mimic, or caricature the public-anchor voice; (iii) use source packet only to infer support preferences, friction style, and likely failure modes; (iv) preserve uncertainty and avoid psychologizing the user beyond the evidence. |
| **D2** | C5_CONTRACT pairwise scope | **Restricted to {C3, C4, C5} comparators.** | Saves ~60% of the all-vs-all pairwise call count. Initial v0.2 covers the load-bearing comparisons: C5_CONTRACT vs C3, C5_CONTRACT vs C4, C5_CONTRACT vs C5. Other C5_CONTRACT pairs (C5_CONTRACT vs C0, C1, C1_padded, C4_shuffled) are **deferred and backfillable**, recorded in `reports/backlog/v02_deferred_pairwise_edges.json`. The omission affects breadth, not the core C5 mechanism test. |
| **D3** | Additional C5 variants (C5_NONPUBLIC, C5_SHORT, C5_BEHAVIORALIZED) | **Defer all three to v0.3.** | v0.2 already has substantial moving parts (anchored rubric, length controls, harder scenarios, Opus author/judge completion, C5_CONTRACT). Adding more conditions multiplies execution risk without clearer payoff. |
| **D4** | Cluster-bootstrap CIs | **Include in v0.2, native analyzer.** | Cluster unit: `persona_id × scenario_id × author_model`. Report **both** Wilson CI (continuity) and cluster-bootstrap CI (conservative check) side-by-side. Implemented in `analyze.py`, not as ad-hoc scripts. |
| **D5** | Scalar inter-judge agreement (ICC / α) | **Include in v0.2.** | Necessary to defend scalar pooling. Minimum content: per-dimension judge mean / severity offset, per-dimension inter-judge agreement, scalar judge-pair correlations, and explicit notation of dimensions where agreement is weak. |
| **D6** | Stylometric audit of provider-family halo | **Optional in v0.2, non-blocking.** | Run only if cheap on existing outputs and does not delay Phase 0, C5_CONTRACT, or Opus completion. Treat as methods appendix, not headline result. Narrow useful question: does provider-family halo correlate with stylistic similarity or author recognizability? |
| **D7** | v2 blog post timing | **Ship after curated v0.2 report; paper builds on top.** | Do not hold all v0.2 output for a paper. Blog/report = public-facing, cautious; paper-grade methods follow. |

### Deferred-edges manifest (D2)

Pairs deferred from v0.2 are recorded machine-readably at `reports/backlog/v02_deferred_pairwise_edges.json` so they can be backfilled later without reconstructing the design.

### Reporting language (carried forward from v0.1 framing discipline)

Do **not** say:
- "C5 failed."
- "Public-archetype echo was proven."
- "Source packets are bad."
- "All instruments agree."
- "C5_CONTRACT fixes C5" — unless the data actually supports that.

Do use:
- "Source-packet/public-anchor condition"
- "Public-archetype echo hypothesis"
- "Scalar/red-flag fragility"
- "Pairwise competitiveness"
- "Channel disagreement"
- "Behavioral contract structure"
- "Length/control interpretation"

### Questions the v0.2 report must answer

1. Does C4 beat C1_PADDED? (behavioral structure vs profile length)
2. Does C4 beat C4_SHUFFLED? (coherent contract structure vs degraded same content)
3. Does C5_CONTRACT beat C5? (contract repair of source-packet condition)
4. Does C5_CONTRACT beat C3/C4? (whether source packets add value once behavioralized)
5. Does C5 remain pairwise-competitive while accumulating more red flags? (scalar/pairwise tension)
6. Do C5 / C5_CONTRACT red flags correlate with pairwise losses? (whether red flags explain pairwise behavior)
7. Which scenario families produce the biggest conditioning effects? (interpersonal_conflict / shame_self_interpretation / procrastination / epistemic_uncertainty / creative_feedback / authority_disagreement / ambition_status / moral_uncertainty)

---

## 5. Sequencing & dependencies

```
Phase 0 (hardening) ─────────────────┐
                                      │
                                      v
Phase 1 (C5_CONTRACT design + codex generation/judging) ─┐
                                      │                   │
                                      v                   │
Phase 2 (Opus author outputs) ←── Opus quota window      │
                                      │                   │
                                      v                   │
Phase 3 (Opus judging) ←── Opus quota window             │
                                      │                   │
                                      v                   │
                                Phase 4 (analysis) ←─────┘
                                      │
                                      v
                                Phase 5 (curate report)
                                      │
                                      v
                                Phase 6 (v2 blog post)

Phase 7 (paper-grade) — parallel from Phase 4 onward
```

**Critical path**: Phase 0 (hardening) must complete before any extended LLM run. After that, Phases 1 codex-side and Phase 2 Opus authoring can run in parallel. Phase 3 (Opus judging) blocks until both Phase 1 codex outputs and Phase 2 Opus authoring complete.

**Time estimate** (no Opus quota delays): Phase 0 ~2h, Phase 1 codex-side ~6–8h LLM time + ~3h scaffolding, Phase 4 ~2h analysis, Phase 5 ~6–8h curation + review, Phase 6 ~writer-session timeline.

**Time estimate with Opus**: Phase 2 + Phase 3 add wall-time depending on Opus quota; could be 1–3 weeks calendar.

---

## 6. Cost estimate (LLM-side, rough)

Rough budget at current API pricing. Codex side runs against ChatGPT subscription quota; only Opus draws against the Anthropic Max plan's 5h cap.

| Phase | LLM calls | Approximate cost |
|---|---|---|
| 0 | 0 (no LLM) | $0 |
| 1 codex-side (C5_CONTRACT generation + judging on PI codex authors) | ~640 outputs + ~3,800 judging calls + ~13,000 pairwise calls | $40–80 (codex subscription, no marginal cost beyond quota) |
| 1 Opus side (C5_CONTRACT) | ~320 outputs + ~960 judging | Opus quota: ~1,300 cap-window draws |
| 2 Opus authoring | ~720 outputs | Opus quota: ~720 cap-window draws |
| 3 Opus judging full corpus | ~3,000–4,000 calls | Opus quota: substantial — multiple weeks of cap windows |
| 4 analysis | 0 (compute) | $0 |
| 5 publication review | ~9 review calls (3 reviewers × ~3 rounds) | $5–10 codex + Opus + Gemini |

**Total Opus quota draw expected**: ~5,000–6,000 calls. Even at the recent v0.1 J3 backfill rate (3 cap-window cycles for ~1,200 calls), this is **at least 4–5 weeks of cap windows** assuming no further bug-induced burn.

This is the strongest argument for prioritizing Phase 0.1 (cap-burn fix) — every cap window we waste extends the calendar by another week.

---

## 7. Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Opus weekly quota window doesn't move | High calendar | Cap-burn fix (P0); resume-safe writes already in place; can split work across many short windows |
| C5_CONTRACT prompt design is ambiguous (contract vs packet ordering matters) | Medium | Pilot a small subset (~20 outputs) and spot-check before full Phase 1.5 |
| Pairwise scope explosion when C5_CONTRACT lands | Medium | D2 decision: restrict pairs to {C3, C4, C5} comparators |
| Native analyzer port for diagnostics introduces regressions | Low | Smoke test fixture (already exists) catches most; expand fixture coverage |
| Cluster-bootstrap implementation diverges from Wilson on existing data | Low (informative — wider CIs are expected) | Report both; document the methodology |
| The PAE story stays ambiguous even after C5_CONTRACT | Medium | Then v0.3 needs C5_NONPUBLIC + unblinded mechanism audit. Plan acknowledges this |
| v2 blog post pre-empts the paper's findings | Low | Blog and paper target different audiences and depths |

---

## 8. Done = ?

v0.2 is complete when:

1. The full v0.2 corpus exists across 3 authors × 8 personas × 80 scenarios × 7+1 conditions (with C5/C5_CONTRACT PI-only) = ~2,400+ outputs.
2. Tri-model judging (anchored scalar + same-author pairwise) is complete across the corpus.
3. The analyzer's metrics JSON includes native length-bucket / PI-PS / tie-rate / scenario-family / red-flag-stratified diagnostics, plus cluster-bootstrap CIs and scalar ICC/α.
4. A curated v0.2 report exists at `reports/psycheeval_v0_2_*.md`, has been through at least one publication-review round, and is on the reading device.
5. The v2 blog post is drafted, reviewed, and either published or queued for publication on the Ashita Orbis pipeline.

v0.3 starts when v0.2 has surfaced enough new questions to warrant another round of conditions and infrastructure changes — currently expected to focus on PAE mechanism resolution (C5_NONPUBLIC, unblinded mechanism audit) and any v0.2 findings that need stronger discrimination.
