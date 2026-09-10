# PsycheEval: Complete Opus Coverage + GPT-5.5 xhigh Tri-Model Plan

**Audience:** Claude Code / implementation agent  
**Date:** 2026-04-25  
**Current v0.1 run tag:** `2026-04-20_micro`  
**Current posture:** finish v0.1 cleanly, then extend to a tri-model evaluation with GPT-5.5 xhigh, then run v0.2 with the same model coverage discipline.

---

## 0. Purpose

This document gives you the full context and implementation plan for the next PsycheEval work block.

The goals are:

1. **Complete Opus pairwise coverage for v0.1.** The current v0.1 pairwise corpus is directionally useful but incomplete: GPT-5.4-as-judge is complete, while Opus-as-judge is partially missing because Claude Max caps interrupted the run. Finish the missing Opus calls so the v0.1 pairwise corpus is no longer a 75%-coverage result.
2. **Add GPT-5.5 xhigh as a third model for all relevant cases.** GPT-5.5 xhigh should be added as both an **author** and a **judge**, not just as a one-off extra scorer. Treat this as a tri-model extension, with explicit provider/family halo accounting.
3. **Update the analysis/reporting language and tables.** Keep the report honest: use “pairwise-supported,” not “pairwise-confirmed,” unless and until the relevant pairwise corpus is actually complete. Replace “three independent instruments” with “three converging measurement channels.” Keep C5/public-archetype echo framed as a hypothesis supported by the current run, not as a settled fact.
4. **Prepare v0.2 to run with the same tri-model structure.** v0.2 should not start as a two-model run that later has to be awkwardly patched. Add GPT-5.5 xhigh to v0.2 before execution.

External source check: OpenAI’s GPT-5.5 announcement describes GPT-5.5 as built for complex work such as coding, research, information synthesis, data analysis, and document-heavy workflows. The OpenAI API model documentation says GPT-5.5 supports `reasoning.effort` values including `xhigh`. Before running, verify the exact local CLI alias/snapshot available in this workspace.

---

## 1. Current state summary

The current internal session summary says:

- v0.1 run tag: `2026-04-20_micro`.
- Pairwise data is finalized at **75% coverage** for the two-model run: **2,640 / 3,504 records**.
- GPT-5.4-as-judge is complete: **1,752 / 1,752 pairwise records**.
- Opus-as-judge is incomplete: **888 / 1,752 pairwise records**, with **864 Opus calls missing**.
- The missing Opus calls hit the Claude Max cap twice; a third lower-concurrency backfill is needed.
- The current directional result is stable in the observed data but should be described as **pairwise-supported**, not fully confirmed, until the missing Opus records are backfilled.
- v0.2 code is already largely complete: C1 padded, C4 shuffled, anchored 0–10 rubric, v0.2 hard scenarios, anchored analyzer path, length-control deltas, token/character summaries, targeted pairwise whitelist, and drift-prevention tests are implemented.
- Test suite is currently passing: **29/29**.

Existing v0.1 scientific pattern:

> Behavioral contracts C3/C4 outperform source-packet-informed C5 in the cleanest available comparisons. C5 appears to trigger a possible public-archetype-echo failure mode: recognizable public-style coherence that is less scenario-specific and more generic than a behavioral contract.

Keep this result, but frame it carefully.

---

## 2. Judgment-call protocol

Use the `ask_user_question` tool for true judgment calls, but do not ask for routine implementation choices where this document gives a default.

### Ask the user before changing these defaults

1. **Whether to mutate the canonical v0.1 tag.**
   - Default: do **not** mutate `2026-04-20_micro` beyond completing the missing Opus pairwise backfill and regenerating its v0.1 report.
   - Default for GPT-5.5 work: create a new extension tag, e.g. `2026-04-25_micro_tri_model`, that copies or references the v0.1 artifacts and adds GPT-5.5 xhigh.
   - Ask the user only if repository constraints make a separate extension tag impractical.

2. **Whether v0.1 tri-model pairwise should be exhaustive or same-author-only.**
   - Default: implement the coverage planner so both modes are possible.
   - Recommended default for comparability with the existing v0.1 pairwise run: preserve the existing all-output-pairs semantics for the tri-model v0.1 extension if budget/quota is acceptable.
   - If the expected call count becomes too large for practical completion, ask the user whether to switch to same-author-only or a targeted pairwise subset.

3. **The exact GPT-5.5 model alias/snapshot.**
   - Default: try `gpt-5.5` with `reasoning_effort=xhigh`.
   - If the local wrapper/CLI rejects this, run a probe/list command if available. If still ambiguous, ask the user which local model name maps to GPT-5.5 xhigh.

4. **Quota tradeoffs.**
   - Default: complete Opus v0.1 coverage first, then run GPT-5.5 scalar work, then pairwise expansion, then v0.2.
   - If Claude Max caps prevent full Opus completion after repeated low-concurrency attempts, ask whether to pause until a clean window or proceed with GPT-5.5 work while clearly marking Opus incomplete.

For all other implementation details, proceed with the defaults below.

---

## 3. Language and framing requirements

The report language matters. Do not overstate the current evidence.

### Required wording changes

Use:

> **pairwise-supported**

Do not use:

> pairwise-confirmed

unless the relevant expected pairwise matrix is actually complete and stratified diagnostics show the direction is stable.

Use:

> **three converging measurement channels**

Do not use:

> three independent instruments

because scalar scores, red-flag labels, and pairwise preferences reuse the same outputs, scenarios, authors, and judge families.

Use:

> **The current run supports the public-archetype-echo hypothesis.**

Do not use:

> The run proves public-archetype echo.

Use:

> **In this synthetic pilot / tri-model extension...**

Do not use:

> PsycheEval proves that profiles help real users.

Use:

> **source-packet-informed public-anchor personas**

Do not use:

> simulated [public-figure anchor — redacted] / simulated [public-figure anchor — redacted] / real-person psych profiles

unless explicitly discussing the fictionalization strategy. These are fictionalized public-anchor synthetic personas, not claims about the real people.

### Suggested TL;DR once Opus coverage is complete

```markdown
## TL;DR

This synthetic v0.1 pilot supports a sharper claim than “profiles help”:

> Behavioral contracts outperformed source-packet-informed public-anchor personas under the cleanest comparison available: same scenario, controlled condition pair, and cross-provider judging.

After completing the Opus backfill, report the final pairwise numbers here. In the 75%-complete interim corpus, C3 beat C5 by 65.6% / 34.4%, and C4 beat C5 by 57.6% / 42.4%. Treat these interim values as historical context only once the full corpus is regenerated.

The emerging hypothesis is **public-archetype echo**: source packets can make a model produce recognizable public-style advice rather than scenario-specific help for the user. Behavioral contracts appear more robust because they translate persona knowledge into action constraints.

This remains a synthetic pilot, not evidence about real users. The purpose of v0.1 is to debug the evaluation harness, surface failure modes, and generate hypotheses for v0.2 and human calibration.
```

---

## 4. Execution order

Do the work in this order.

1. **Freeze/check current state.**
2. **Complete v0.1 Opus pairwise backfill.**
3. **Regenerate v0.1 metrics and report with complete two-model pairwise coverage.**
4. **Add model-registry support for GPT-5.5 xhigh.**
5. **Create a tri-model v0.1 extension tag.**
6. **Generate GPT-5.5 xhigh outputs for all v0.1 cases.**
7. **Run scalar judging so every v0.1 output has all three judge scores.**
8. **Run tri-model pairwise according to the selected coverage mode.**
9. **Regenerate v0.1 tri-model metrics/report.**
10. **Update v0.2 to include GPT-5.5 xhigh before execution.**
11. **Run v0.2 generation, scalar judging, targeted pairwise, and analysis.**
12. **Only then consider external/public sharing.**

Do not start v0.2 generation until the v0.1 Opus backfill and analysis/report changes are complete.

---

## 5. Step A — Freeze and inspect current state

Before modifying anything, capture:

```bash
git status --short
git diff --stat
uv run pytest
```

Write a short note to `psycheeval/docs/session_log_2026-04-25_next.md` or similar containing:

- current branch;
- current uncommitted file list;
- current test status;
- current pairwise record counts by judge;
- whether validation warnings are present.

Do not commit unless the user explicitly says to commit.

---

## 6. Step B — Complete Opus pairwise coverage for v0.1

### Goal

Bring current v0.1 pairwise coverage from:

```text
GPT-5.4 judge: 1752 / 1752 complete
Opus judge:     888 / 1752 complete
Total:         2640 / 3504 complete
```

to:

```text
GPT-5.4 judge: 1752 / 1752 complete
Opus judge:    1752 / 1752 complete
Total:         3504 / 3504 complete
```

### Required implementation behavior

If not already implemented, add a robust missing-record planner:

```text
expected_pairwise_records(tag, pilot, judges, authors, conditions, pair_scope)
observed_pairwise_records(tag)
missing_pairwise_records = expected - observed
```

The planner must identify missing records by a deterministic key, not by file length.

Suggested key fields:

```text
pilot
tag
scenario_id
persona_id
persona_type
judge_model
author_A
condition_A
output_id_A
author_B
condition_B
output_id_B
pair_order_key
```

If order is randomized for judging, preserve a canonical unordered pair key plus a presented-order field.

### Backfill command

Use low concurrency for Opus because previous 4-worker bursts hit the Claude Max cap.

If the CLI already resumes automatically:

```bash
uv run python -m psycheeval.judge pairwise \
  --tag 2026-04-20_micro \
  --pilot v01_micro \
  --judges opus \
  --workers 1
```

If there is or can be a missing-only flag, prefer:

```bash
uv run python -m psycheeval.judge pairwise \
  --tag 2026-04-20_micro \
  --pilot v01_micro \
  --judges opus \
  --workers 1 \
  --missing-only
```

If rate caps still occur, retry with:

```bash
--workers 1
```

and no concurrent Claude/Opus workloads.

### Completion criteria

Do not call the backfill complete until all are true:

- expected pairwise records: 3,504;
- observed pairwise records: 3,504;
- Opus judge expected = observed = 1,752;
- GPT-5.4 judge expected = observed = 1,752;
- no validation errors;
- invalid red-flag warnings are summarized, not silently ignored;
- coverage diagnostics show 100% for judge, author, persona type, and condition-pair strata.

---

## 7. Step C — Add coverage diagnostics and stratified pairwise reporting

Before rewriting conclusions, add diagnostics that make pairwise coverage visible.

### Required coverage tables

Add a section to metrics JSON and the report with expected vs observed counts by:

1. judge;
2. author;
3. persona type: PI vs PS;
4. condition pair;
5. judge × author;
6. judge × condition pair;
7. judge × author × condition pair;
8. persona type × condition pair;
9. same-author vs cross-author pair type, if all-output-pairs are included.

### Required pairwise win-rate tables

Report win rates in at least two forms:

1. **Pooled observed win rate.**
2. **Macro-averaged win rate across judge/author strata.**

For the v0.1 two-model run, the load-bearing cells include:

- C3 vs C5, all available;
- C4 vs C5, all available;
- C3 vs C5, PI-only;
- C4 vs C5, PI-only;
- C3 vs C4, PI-only;
- C3 vs C4, PS-only.

### Required uncertainty intervals

Add Wilson intervals or bootstrap intervals for the key pairwise cells, especially when `n` is small.

Suggested output:

```text
pair
n
win_rate_A
ci_low
ci_high
ties
judge_macro_win_rate_A
macro_ci_low
macro_ci_high
```

Do not make the report look like a stats paper, but give readers enough uncertainty information to avoid overreading small `n` comparisons.

---

## 8. Step D — Regenerate v0.1 two-model report

After completing Opus pairwise coverage, run:

```bash
uv run python -m psycheeval.analyze \
  --tag 2026-04-20_micro \
  --pilot v01_micro
```

Then regenerate/update:

- `psycheeval/reports/metrics_2026-04-20_micro.json`
- `psycheeval/reports/psycheeval_v0_1_micro_pilot_2026-04-20_micro.md`
- rendered HTML if the repository uses generated HTML reports
- failure cards if affected
- coverage diagnostics JSON/MD

### Required report notes

Add an artifact status block near the top:

```markdown
## Artifact status

- v0.1 pre-brief report: archived / superseded.
- v0.1 revised two-model report: current for the original Opus + GPT-5.4 run.
- v0.1 pairwise corpus: complete at 3,504 / 3,504 records after Opus backfill.
- v0.1 tri-model extension: separate tag, pending or current depending on status.
- v0.2: code complete, execution queued or running.
```

Mark any pre-brief report artifacts clearly as:

```text
SUPERSEDED — pre-pairwise / pre-cross-provider-primary revision
```

---

## 9. Step E — Add GPT-5.5 xhigh to model registry

### Model identity

Add GPT-5.5 xhigh as a first-class model, not a string special case.

Suggested fields:

```python
ModelSpec(
    key="gpt-5.5-xhigh",
    provider="openai",
    family="gpt-5.5",
    display_name="GPT-5.5 xhigh",
    api_model="gpt-5.5",          # verify locally before use
    reasoning_effort="xhigh",    # verify wrapper support before use
    roles={"author", "judge"},
)
```

If the local wrapper requires a different alias, snapshot name, or effort syntax, use the wrapper’s supported form but keep the internal key stable as `gpt-5.5-xhigh`.

### Probe before running

Add or run a lightweight model probe before launching expensive generation:

```bash
uv run python -m psycheeval.models_probe --model gpt-5.5-xhigh
```

If no probe exists, add one or use the lowest-cost equivalent call.

The probe should confirm:

- model alias resolves;
- `reasoning_effort=xhigh` is accepted;
- JSON mode / structured output path works if required;
- the model can produce a minimal valid `JudgeScore` or `PairwiseScore` object;
- the wrapper records the model alias/snapshot in run metadata.

### Metadata capture

Every output/score should capture:

```json
{
  "model_key": "gpt-5.5-xhigh",
  "provider": "openai",
  "family": "gpt-5.5",
  "api_model": "...actual alias...",
  "reasoning_effort": "xhigh",
  "snapshot": "...if available...",
  "generated_at": "...",
  "wrapper": "codex-cli/openai-responses/etc"
}
```

---

## 10. Step F — Update halo and primary-scoring logic for three models

Adding GPT-5.5 changes the halo logic. GPT-5.4 and GPT-5.5 are different models but the same provider family.

### Classify judge/author relation

Add a relation label for every judge score and pairwise judgment:

```text
exact_self:        same exact model key, e.g. GPT-5.5 judging GPT-5.5
same_provider:     same provider but different model, e.g. GPT-5.5 judging GPT-5.4
cross_provider:    OpenAI judging Anthropic or Anthropic judging OpenAI
```

Optional finer-grained labels:

```text
same_family
same_generation
cross_family
```

### Primary scalar reporting with three models

For the tri-model report, do not naively average all judges as primary.

Use these sections:

1. **Primary cross-provider scores.**
   - Opus-authored outputs judged by OpenAI judges can be reported as OpenAI-cross-provider, but show GPT-5.4 and GPT-5.5 separately and macro-average them.
   - GPT-5.4-authored outputs judged by Opus are primary cross-provider.
   - GPT-5.5-authored outputs judged by Opus are primary cross-provider.

2. **Secondary same-provider cross-model scores.**
   - GPT-5.4 judging GPT-5.5.
   - GPT-5.5 judging GPT-5.4.

3. **Exact self-halo scores.**
   - Opus judging Opus.
   - GPT-5.4 judging GPT-5.4.
   - GPT-5.5 judging GPT-5.5.

4. **All-judge means.**
   - Appendix only.

### Halo tables

Add halo tables for:

- exact self minus cross-provider;
- same-provider cross-model minus cross-provider;
- GPT-5.5 judge vs GPT-5.4 judge on the same Opus-authored outputs;
- Opus judge vs GPT judges on OpenAI-authored outputs.

This is important because GPT-5.5 may become a better judge or a more flattering same-provider judge; do not assume either.

---

## 11. Step G — Create v0.1 tri-model extension tag

Default: do not mutate the canonical `2026-04-20_micro` beyond completing the original Opus backfill.

Create a new extension tag:

```text
2026-04-25_micro_tri_model
```

The extension tag should either copy or reference the original v0.1 artifacts:

- personas;
- scenarios;
- profile bundles;
- Opus outputs;
- GPT-5.4 outputs;
- existing scalar scores;
- existing pairwise scores after Opus backfill;
- validation warnings;
- metadata.

Then add GPT-5.5 xhigh outputs, scores, and pairwise judgments.

### Expected v0.1 output counts

Original v0.1 per author:

- all 48 scenarios have C0, C1, C3, C4: `48 × 4 = 192` outputs;
- 24 PI scenarios also have C5: `24 × 1 = 24` outputs;
- total per author: `216` outputs.

With three authors:

```text
216 outputs/author × 3 authors = 648 outputs
```

GPT-5.5 xhigh adds:

```text
216 new assistant outputs
```

### Suggested generation command

If `run.py` supports author selection:

```bash
uv run python -m psycheeval.run \
  --pilot v01_micro \
  --tag 2026-04-25_micro_tri_model \
  --authors gpt-5.5-xhigh \
  --workers 2
```

If it does not support author selection, add `--authors` before running to avoid regenerating Opus/GPT-5.4 outputs.

Use lower concurrency initially until GPT-5.5 rate behavior is known.

---

## 12. Step H — Scalar judging for v0.1 tri-model

### Expected scalar score counts

Tri-model v0.1:

```text
648 outputs × 3 judges = 1,944 scalar judge scores
```

Existing original scores:

```text
432 outputs × 2 judges = 864 scalar judge scores
```

Additional scalar scores needed for full tri-model coverage:

1. GPT-5.5 judging all 648 outputs: `648` scores.
2. Opus judging GPT-5.5-authored outputs: `216` scores.
3. GPT-5.4 judging GPT-5.5-authored outputs: `216` scores.

Total new scalar scores:

```text
648 + 216 + 216 = 1,080
```

### Commands

Run in stages to avoid provider contention.

```bash
# GPT-5.5 as judge on all outputs
uv run python -m psycheeval.judge score \
  --tag 2026-04-25_micro_tri_model \
  --pilot v01_micro \
  --judges gpt-5.5-xhigh \
  --workers 2

# Existing judges on GPT-5.5-authored outputs
uv run python -m psycheeval.judge score \
  --tag 2026-04-25_micro_tri_model \
  --pilot v01_micro \
  --judges opus,gpt-5.4 \
  --authors gpt-5.5-xhigh \
  --workers 2
```

If `--authors` is not supported in `judge score`, add it.

### Completion criteria

- expected scalar scores: 1,944;
- observed scalar scores: 1,944;
- every output has exactly three judge scores;
- no validation errors;
- warning summaries generated;
- relation labels assigned: `exact_self`, `same_provider`, `cross_provider`.

---

## 13. Step I — Pairwise for v0.1 tri-model

There are two possible pairwise scopes. Implement coverage planning for both.

### Option 1 — Exhaustive all-output-pairs scope

This matches the apparent semantics of the existing v0.1 pairwise run, where all outputs within a scenario are paired, including cross-author pairs.

With three authors:

- PS scenario: 4 conditions × 3 authors = 12 outputs → `C(12,2)=66` pairs.
- PI scenario: 5 conditions × 3 authors = 15 outputs → `C(15,2)=105` pairs.
- If v0.1 has 24 PS and 24 PI scenarios:

```text
PS: 24 × 66  = 1,584 pairs per judge
PI: 24 × 105 = 2,520 pairs per judge
Total:        4,104 pairs per judge
Three judges: 12,312 pairwise records
```

This is the most complete interpretation of “all cases,” but it is expensive.

Existing two-model pairwise after Opus backfill:

```text
3,504 pairwise records
```

Additional tri-model exhaustive pairwise records needed:

```text
12,312 - 3,504 = 8,808 additional records
```

This includes:

- new GPT-5.5 judge on the old two-model pair space;
- pairs involving GPT-5.5-authored outputs;
- all three judges over the expanded pair space.

### Option 2 — Same-author condition-pair scope

This is more directly interpretable for condition effects because it asks: same scenario, same author, two conditions.

Per author:

- PS: 24 scenarios × `C(4,2)=6` condition pairs = 144.
- PI: 24 scenarios × `C(5,2)=10` condition pairs = 240.
- Total per author = 384.

With three authors and three judges:

```text
384 × 3 authors × 3 judges = 3,456 pairwise records
```

This is much cheaper and cleaner for condition effects, but it is not the same as the existing v0.1 all-output-pairs run.

### Default recommendation

1. Complete the original two-model v0.1 all-output-pairs corpus first.
2. Create the tri-model extension with a coverage planner that can report both all-output-pairs and same-author-only.
3. If budget/quota is acceptable, run the exhaustive all-output-pairs tri-model corpus.
4. If quota becomes prohibitive, ask the user whether to use same-author-only for the tri-model extension.

### Commands

Exhaustive mode:

```bash
uv run python -m psycheeval.judge pairwise \
  --tag 2026-04-25_micro_tri_model \
  --pilot v01_micro \
  --judges opus,gpt-5.4,gpt-5.5-xhigh \
  --workers 2 \
  --scope exhaustive
```

Same-author-only mode:

```bash
uv run python -m psycheeval.judge pairwise \
  --tag 2026-04-25_micro_tri_model \
  --pilot v01_micro \
  --judges opus,gpt-5.4,gpt-5.5-xhigh \
  --workers 2 \
  --scope same_author_only
```

If `--scope` does not exist, add it before running.

### Worker strategy

- Opus: `--workers 1` or `--workers 2` max.
- GPT-5.4: `--workers 2–4`, depending on rate limits.
- GPT-5.5 xhigh: start with `--workers 1–2`; increase only after stable validation and rate behavior.
- Never run Opus pairwise backfill concurrently with v0.2 or GPT-5.5 expansion if it risks Claude Max caps.

---

## 14. Step J — Tri-model analysis/reporting

Run:

```bash
uv run python -m psycheeval.analyze \
  --tag 2026-04-25_micro_tri_model \
  --pilot v01_micro
```

### New required report sections

1. **Why a tri-model extension was added.**
   - GPT-5.5 xhigh was added after the original v0.1 run to test whether the findings survive a stronger/newer OpenAI model and a third judge family member.

2. **Coverage status.**
   - Expected vs observed outputs, scalar scores, and pairwise records.
   - Coverage by judge, author, persona type, condition pair, and relation type.

3. **Primary cross-provider scalar results.**
   - Do not blend exact-self, same-provider, and cross-provider scores in the main table.

4. **Tri-model pairwise results.**
   - Pooled and macro-averaged.
   - Wilson/bootstrap intervals for key cells.

5. **GPT-5.5 author behavior.**
   - Does GPT-5.5 xhigh as author follow the same C3/C4-over-C5 pattern?
   - Does it reduce generic slop or public-archetype echo?
   - Does it produce fewer red flags overall?

6. **GPT-5.5 judge behavior.**
   - Does GPT-5.5 xhigh agree with Opus and GPT-5.4?
   - Does it show less or more same-provider halo?
   - Does it punish C5/public-archetype echo more strongly or less strongly?

7. **Updated public-archetype-echo synthesis.**
   - Keep framed as hypothesis.
   - Report whether adding GPT-5.5 strengthens, weakens, or complicates the pattern.

8. **Limitations.**
   - Synthetic only.
   - New model added after original run; tri-model extension is not identical to a clean from-scratch three-model v0.1.
   - Same-provider OpenAI cross-model judging is not equivalent to cross-provider judging.
   - Human calibration still not done.

---

## 15. Step K — v0.2 with GPT-5.5 xhigh included before execution

Do not start v0.2 as a two-model run if the goal is now tri-model coverage.

### Expected v0.2 outputs

Current v0.2 dry-run with two authors:

```text
1,040 outputs
PI: 560
PS: 480
```

Per author:

```text
520 outputs
```

With three authors:

```text
520 × 3 = 1,560 outputs
```

GPT-5.5 xhigh adds:

```text
520 new outputs compared with the current two-author dry run
```

### Expected v0.2 scalar scores

With three judges:

```text
1,560 outputs × 3 judges = 4,680 anchored scalar judge scores
```

### Expected v0.2 targeted pairwise scores

Current targeted pairwise whitelist:

```text
C4:C0
C4:C1
C4:C1_padded
C4:C4_shuffled
C3:C4
C1:C1_padded
C4:C5@PI
```

Assuming 80 scenarios total and 40 PI / 40 PS:

- six all-scenario pairs × 80 = 480 condition pairs per author;
- one PI-only pair × 40 = 40 condition pairs per author;
- total per author = 520 pairwise comparisons;
- three authors = 1,560 same-author pairwise comparisons per judge;
- three judges = 4,680 pairwise records.

If these assumptions differ from the manifest, compute from the manifest rather than hardcoding.

### v0.2 commands

After GPT-5.5 is registered and probed:

```bash
# Prepare, if not already done
uv run python -m psycheeval.v02_prepare

# Dry-run first; expected outputs should be 1,560 after adding GPT-5.5
uv run python -m psycheeval.run \
  --pilot v02_hard_pilot \
  --tag 2026-04-25_v02_hard_tri_model \
  --authors opus,gpt-5.4,gpt-5.5-xhigh \
  --dry-run

# Generate outputs
uv run python -m psycheeval.run \
  --pilot v02_hard_pilot \
  --tag 2026-04-25_v02_hard_tri_model \
  --authors opus,gpt-5.4,gpt-5.5-xhigh \
  --workers 2

# Anchored scalar judging
uv run python -m psycheeval.judge score \
  --tag 2026-04-25_v02_hard_tri_model \
  --pilot v02_hard_pilot \
  --judges opus,gpt-5.4,gpt-5.5-xhigh \
  --workers 2 \
  --rubric anchored

# Targeted pairwise
uv run python -m psycheeval.judge pairwise \
  --tag 2026-04-25_v02_hard_tri_model \
  --pilot v02_hard_pilot \
  --judges opus,gpt-5.4,gpt-5.5-xhigh \
  --workers 2 \
  --pairs "C4:C0,C4:C1,C4:C1_padded,C4:C4_shuffled,C3:C4,C1:C1_padded,C4:C5@PI" \
  --scope same_author_only

# Analyze
uv run python -m psycheeval.analyze \
  --tag 2026-04-25_v02_hard_tri_model \
  --pilot v02_hard_pilot
```

If `--authors` or `--scope same_author_only` is not implemented for these commands, add them before running.

---

## 16. v0.2 analysis priorities

v0.2 exists to answer whether C4 wins for the right reasons, not merely whether a longer profile wins.

### Required v0.2 delta blocks

Report these prominently:

1. `C4 − C0`: main profile/contract effect.
2. `C4 − C1`: contract vs trait labels.
3. `C4 − C1_PADDED`: structure/content vs length padding.
4. `C4 − C4_SHUFFLED`: structured contract vs degraded same-ish material.
5. `C4 − C5`, PI-only: behavioral contract vs source-packet persona.
6. `C3 − C4`: plain behavioral contract vs anti-sycophancy extension.
7. `C1 − C1_PADDED`: padding sanity check.

### Required v0.2 questions

Answer these explicitly:

1. Does C4 beat C1_PADDED?
   - If yes, the result is less likely to be just extra tokens.
2. Does C4 beat C4_SHUFFLED?
   - If yes, the structure of the behavioral contract matters.
3. Does C4 beat C5 in PI-only cases again?
   - If yes, public-archetype echo becomes a stronger hypothesis.
4. Does GPT-5.5 xhigh reduce or amplify C5 failures?
5. Do model judges agree on public-archetype echo, or is one judge driving it?
6. Does C4’s advantage hold under the anchored 0–10 rubric?
7. Does C4 reduce red flags, or only improve scalar ratings?

---

## 17. Tests to add or verify

Keep the existing 29/29 tests passing. Add tests for the new tri-model path.

### Model registry tests

- `test_model_registry_includes_gpt55_xhigh`
- `test_gpt55_has_provider_family_and_reasoning_effort`
- `test_model_probe_records_snapshot_or_alias`

### Coverage planner tests

- v0.1 two-model expected pairwise = 3,504 under existing exhaustive semantics.
- v0.1 three-model exhaustive expected pairwise = 12,312 if assumptions hold.
- v0.1 three-model same-author-only expected pairwise = 3,456 if assumptions hold.
- v0.2 three-model targeted expected outputs = 1,560 if manifest assumptions hold.
- v0.2 three-model targeted pairwise expected = 4,680 if manifest assumptions hold.

Use manifest-derived counts where possible; tests should fail if assumptions drift without updated expected values.

### Analysis tests

- analyzer handles three authors;
- analyzer handles three judges;
- analyzer does not mix 0–5 and 0–10 rubrics;
- analyzer separates exact-self, same-provider, and cross-provider scores;
- macro-averaged pairwise win rates compute correctly;
- Wilson/bootstrap intervals appear for key pairwise rows;
- C5 never appears in global C0–C4 comparisons unless the subset is PI-only or explicitly marked compositionally different.

### Prompt/schema tests

Keep existing red-flag enum drift tests. Also verify:

- GPT-5.5 judge prompts receive the same generated red-flag vocabulary;
- no hardcoded red-flag lists reappear;
- pairwise prompt accepts all 24 red-flag labels;
- schemas match `RedFlag` exactly.

---

## 18. Data integrity and warning handling

Do not silently erase evidence.

`_coerce_red_flags()` should continue to prevent one invalid red flag from failing an entire record, but invalid labels must be logged and summarized.

Required outputs:

```text
runs/<tag>/validation_warnings.jsonl
reports/validation_warnings_<tag>.md or .json
```

Summaries should include:

- invalid label string;
- count;
- judge;
- author;
- condition;
- prompt file/rubric if available;
- scenario family;
- first few examples.

Suggested policy:

- Any invalid red-flag label count > 0 should be visible in report appendix.
- Invalid labels > 1% of judged records should make the run status `warning`.
- Invalid labels > 5% should make the run status `failed_validation` unless user overrides.

---

## 19. Reporting structure for the next public/internal report

Use this order:

1. **Title and artifact status.**
2. **TL;DR.**
3. **What PsycheEval is testing.**
4. **What this synthetic run can and cannot show.**
5. **Model coverage and run completeness.**
6. **Experimental design.**
7. **Primary scalar results: cross-provider only.**
8. **Pairwise results: pooled, macro-averaged, with intervals.**
9. **Red-flag analysis.**
10. **C5 / public-archetype-echo synthesis.**
11. **GPT-5.5 extension findings.**
12. **Judge/model halo audit.**
13. **PI-only vs PS-only comparisons.**
14. **Threats to validity.**
15. **v0.2 plan or v0.2 results, depending on execution status.**
16. **Appendices: all-judge means, full coverage tables, validation warnings, failure cards.**

---

## 20. Key scientific framing to preserve

The strongest current finding is not generic “profiles helped.” It is this:

> Behavioral contracts appear more robust than source-packet-informed public-anchor personas for psychologically loaded assistant behavior. Source packets may create recognizable public-style coherence while reducing scenario-specific fit.

Keep the emphasis on **which kinds of personalization help**.

The central distinction:

```text
C1: trait labels
C3: behavioral contract
C4: behavioral contract + anti-sycophancy / motive uncertainty / repair clauses
C5: source-packet-informed public-anchor persona
```

The emerging hypothesis:

```text
Public-archetype echo: source-packet-informed personas cause the model to respond to a recognizable public archetype or voice rather than to the scenario-specific user need.
```

Do not claim this is proven. The current evidence is convergence across scalar, red-flag, and pairwise views.

---

## 21. Commit/bundling guidance

Do not commit without the user’s go-ahead.

When the user asks to commit, split into clean commits if possible:

```text
1. Complete v0.1 Opus pairwise backfill and coverage diagnostics
2. Add GPT-5.5 xhigh model registry support and probe metadata
3. Add tri-model scalar/pairwise coverage planning and analysis
4. Add v0.1 tri-model extension artifacts/report
5. Update v0.2 to run as tri-model with GPT-5.5 xhigh
6. Reporting language/framing cleanup and superseded artifact markers
```

Do not bundle unrelated prior-session modifications into the same commit unless explicitly requested.

---

## 22. Stop conditions

Stop and ask the user if:

1. GPT-5.5 xhigh cannot be invoked reliably through the local CLI/API wrapper.
2. Completing the Opus backfill repeatedly hits caps even at one worker.
3. Exhaustive tri-model v0.1 pairwise is projected to be impractical and same-author-only would materially change the report’s comparability.
4. Any new analysis reverses the C3/C4-over-C5 direction in a major stratum.
5. Validation warnings exceed the failure threshold.
6. Test suite cannot be restored to passing without changing result semantics.

Otherwise proceed according to this plan.

---

## 23. Final acceptance checklist

### v0.1 two-model completion

- [ ] Opus pairwise backfill complete: 1,752 / 1,752.
- [ ] Total pairwise complete: 3,504 / 3,504.
- [ ] Coverage tables show 100% by judge/author/persona type/condition pair.
- [ ] Pairwise report language says “supported” unless fully justified otherwise.
- [ ] Old v0.1 pre-brief artifact marked superseded.

### GPT-5.5 xhigh integration

- [ ] Model registry has `gpt-5.5-xhigh`.
- [ ] Probe verifies alias + `xhigh` reasoning effort.
- [ ] Metadata captures provider/family/model/snapshot/effort.
- [ ] GPT-5.5 can author outputs.
- [ ] GPT-5.5 can scalar-judge.
- [ ] GPT-5.5 can pairwise-judge.

### v0.1 tri-model extension

- [ ] Separate extension tag created.
- [ ] Expected outputs: 648 observed.
- [ ] Expected scalar scores: 1,944 observed.
- [ ] Pairwise expected count matches selected scope and is fully observed.
- [ ] exact-self / same-provider / cross-provider relation labels present.
- [ ] Tri-model report generated.

### v0.2 tri-model readiness

- [ ] Dry-run output count updated to 1,560, or manifest-derived count explained.
- [ ] Anchored scalar expected count computed and checked.
- [ ] Targeted pairwise expected count computed and checked.
- [ ] `--authors` and `--scope same_author_only` available or equivalent safeguards implemented.
- [ ] Analyzer handles tri-model anchored scores.

### Report quality

- [ ] “Pairwise-supported,” not “pairwise-confirmed,” unless complete.
- [ ] “Converging measurement channels,” not “independent instruments.”
- [ ] C5/public-archetype echo framed as hypothesis.
- [ ] Synthetic-only limitations prominent.
- [ ] All-judge means appendix only.
- [ ] C5 never compared globally against C0–C4 without PI-only qualification.
