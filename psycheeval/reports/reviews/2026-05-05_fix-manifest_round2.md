# Fix Manifest — Round 2 (v1-thorough implementation against GPT Pro feedback)

**Date**: 2026-05-05
**Document**: `reports/psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model.md`
**Round**: 2 (delta — applied against the GPT Pro consolidated feedback at `~/.claude/uploads/.../4c490e7d-psycheeval_v01_cleanup_prompt_for_claude_code.md`)
**Implementation path**: v1-thorough — Bucket A (small report fixes) + selected Bucket B (probe isolation, tie rates, PI/PS split, length-bucketed pairwise) + §13 v0.2 condition expansion. Bucket C deferred to paper.

---

## Bucket A — verified and applied

| # | GPT Pro item | Section affected | Action |
|---|--------------|------------------|--------|
| A1 | §1 (1.) "What happened to C2?" | §4 condition table | Added explicit C2 row: reserved for narrative-profile conditioning; `Condition.C2` and `ProfileConditionText.C2_narrative` exist in code; all 8 v0.1 profile bundles have empty `C2_narrative`; no C2 outputs were generated. Verified empirically against `data/micro_pilot/profile_bundles.jsonl` and all run directories. |
| A2 | §3.1 blank parenthetical in TL;DR | §1 | Verified — no blank parenthetical present in the post-Path-B TL;DR. The §1 already reads `GPT-5.4 distinguishes C3 and C4 from C5 (***)` with the asterisks. |
| A3 | §3.2 brittle `§12 #N` references | §6 methods note | Replaced two incorrect numerical refs with phrase refs: `§12 #7` → `§12, *Pairwise CIs assume independence*`; `§12 #6` → `§12, *Same-author pairwise scope only*`. Other `§12 #N` refs were correct. `§13 #4` ref verified correct after the §13 rewrite. |
| A4 | §3.3 "PS-side drives most of the n" | §6a headline framing | Corrected: PI and PS contribute equal n for non-C5 pairs. Reframed as "PS baseline red-flag rates are higher (§8b) which provides more statistical separation per record, so the PS contribution likely drives more of the *signal-to-noise* even though the *n* itself is balanced." Pointed at the new §6f for PI/PS-stratified pairwise. |
| A5 | §3.4 PI-only "see §6d" reference | §6a headline framing | §6d in the post-Path-B report is the cross-provider cross-check, not the PI-only split. Replaced the broken reference with a pointer to the new §6f (PI/PS-stratified pairwise table added in this round). |
| A6 | §3.5 "C5 lowest on 8 of 10" | §7b prose, §10 PAE evidence | Verified against PI-only table. Actual count: **C5 is below C1/C3/C4 on all 10 dimensions** (not 8 of 10). Updated §7b prose and §10 evidence list. Added the C0 comparison breakdown: C5 above C0 on 8 of 10, tied on epistemic, below on boundary. |
| A7 | §3.6 Clarify C4 contents | §4 condition table | Replaced the brief "C3 plus light scenario-conditional guidance" with a concrete description: "C3 plus scenario-conditional guidance — light scenario-class hints (in interpersonal-conflict scenarios prioritize ___ etc). C4 is therefore strictly a superset of C3 in instruction content." Also expanded C3 to mention calibrated challenge, anti-sycophancy, uncertainty preservation, repair cues. |
| A8 | §3.7 PI persona ethics note | §4 condition table | Added an explicit ethics note: PI personas are fictionalized public-anchor personas; not claims about real individuals; not psychometric assessments; the snowclone-shaped names in `pfi_*` IDs do not match any real public figure. |

---

## Bucket B — implemented (subset)

### B1 — Probe isolation (GPT Pro §4)

**Code changes:**

- `src/psycheeval/config.py`: added `OFFICIAL_JUDGES_V01 = ("gpt-5.4", "gpt-5.5", "opus")` constant.
- `src/psycheeval/analyze.py`: `compute_metrics(...)` now takes an `include_probes: bool = False` keyword arg. Default behavior filters scalar / anchored / pairwise records to only those with `judge_model in OFFICIAL_JUDGES_V01`. Non-official records are counted into a `probe_counts` dict and a single warning line is printed to stderr listing the excluded judges and counts. `--include-probes` CLI flag added to `main()` for explicit opt-in.
- `tests/test_analyzer_smoke.py`: new test `test_probe_records_excluded_by_default` injects a Kimi probe record into the synthetic-fixture run, asserts the default `compute_metrics` call excludes it (judge_scores count unchanged), confirms the stderr warning is emitted, and confirms `include_probes=True` retains the record. **Test passes.**

**Why this matters:** the v0.1 raw `judge_scores.jsonl` contains 19 records from a `moonshotai/kimi-k2.6` feasibility probe. They were already excluded from the v0.1 reports by the prior code, but the exclusion was implicit (achieved through provider-family routing) rather than explicit. The new filter is fail-closed and visible: any future probe would now require an explicit `--include-probes` flag to enter canonical analysis.

### B2 — Tie rates per pair (GPT Pro §5.1)

Added §6e to the report. All 10 condition pairs reported with total / decisive / ties / tie_rate / lo decisive win. Tie rates are 0.0–2.5%; ties are not driving any §6 conclusions. Forced-choice pattern reaches near-ceiling decisive rates.

### B3 — PI/PS-stratified pairwise (GPT Pro §5.4)

Added §6f. Same-author pairwise stratified by persona type, all judges pooled, decisive only. All 6 non-C5 pairs reported with PI lo win + PI Wilson CI + PI n + PS counterparts. Direction is identical in PI and PS for every pair, with point estimates within ~0.05 — the §6a robust findings are not driven by either persona type alone.

### B4 — Length-bucketed pairwise for C5 pairs (GPT Pro §8.1)

Added §6g — the most consequential new analysis. For each C5-involving pair, decisive win rates stratified by length-difference bucket (`lo much shorter` / `moderately shorter` / `similar` / `moderately longer` / `much longer`).

**Findings:**

- **C0 vs C5** is dominated by length: when C0 is much-shorter, C5 wins 62%; when C0 is moderately shorter, C5 wins 94%; when C0 is much-longer, C0 wins 67%. The §6a "C5 beats C0" result is largely "longer wins" for this pair.
- **C3 vs C5** is robust to length: 0.48–0.67 win rate for C3 across all length buckets. C3 wins regardless of length difference — structural advantage.
- **C4 vs C5** is U-shaped and length-mediated: when similar in length, C4 wins only 27%; when much-longer, C4 wins 70%. The C4-over-C5 advantage in §6b's pooled view is largely a length effect.
- **C1 vs C5** is uniform across buckets (0.37–0.56): no strong length signal in either direction.

§9 was rewritten to incorporate these findings: the C5 channel-divergence story now fragments into pair-specific findings rather than a single channel-asymmetry claim. C3 over C5 is structural; C4 over C5 is partly length; C5 over C0 is mostly length.

### Helper script

The Python computation that produced §6e/§6f/§6g lives inline in this round's session output. For reproducibility, the diagnostics JSON was saved to `/tmp/pairwise_diagnostics.json`. A future round should fold this computation into `analyze.py` so it auto-regenerates with each metrics run.

---

## §13 condition expansion — applied

GPT Pro's §16 stop-condition triggers required user approval before adding new v0.2 conditions. The user approved (decision 1: "yes" to C5_CONTRACT and friends). Applied:

- New §13 subsection "Proposed v0.2 / v0.3 condition expansions" listing **C5_CONTRACT** (priority — load-bearing PAE separator), **C3_SOURCELESS**, **C5_NONPUBLIC**, **C5_SHORT**, **C5_BEHAVIORALIZED**.
- New §13 subsection "Paper-targeted methodology work" listing cluster-bootstrap CIs, scalar ICC / Krippendorff's α, stylometric provider-family-halo audit, human calibration sample, and unblinded mechanism audit. These are explicitly framed as paper-grade (not v0.2-deliverable) work.

---

## Bucket C — deferred (paper-targeted)

These items from the GPT Pro feedback are out of scope for v1 blog and are explicitly disclosed as paper-targeted in §13's new "Paper-targeted methodology work" subsection:

| GPT Pro § | Item | Status |
|---|------|--------|
| 5.5 | Cluster-bootstrap CIs | Disclosed in §12 as threat; queued for paper |
| 6.1 | Scalar inter-judge ICC / α | Disclosed in §11b and §13; queued for paper |
| 6.2 | Scalar macro-averaging | Disclosed in §13 paper-work; deferred |
| 7 | Red-flag stratification by judge / cross-provider / output-level | Deferred to v0.2 / v2 blog |
| 8.2 | Scenario-family breakdowns of condition effects | Deferred to v0.2 (n=6/family/persona is too thin in v0.1) |
| 10 | PAE-label redesign + unblinded mechanism audit | Disclosed in §13 paper-work |
| 11 | Human calibration design | Disclosed in §13 paper-work |
| 12 | Full test suite (banned-phrase / coverage diagnostics / cluster-bootstrap stability) | Probe-isolation test added in this round; broader test work deferred |

---

## Carry-forward to round 3 (if any)

After this round, the report's main remaining open items are paper-targeted (Bucket C). For a v1 blog release, no additional rounds are required. The natural next checkpoints are:

1. **User read-through on the reading device** — surface anything that reads wrong on a phone screen.
2. **v0.2 execution** — at which point the C5_CONTRACT decision becomes operational (does it get added to the queued v0.2 plan?).
3. **Paper draft** — when the blog is published and v0.2 results are in, the methodology hardening (cluster-bootstrap, scalar ICC, etc.) becomes the paper's contribution.

Round 2 is complete. No round 3 dispatch needed unless the user surfaces issues during read-through.
