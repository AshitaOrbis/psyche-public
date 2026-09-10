# PsycheEval — Execution Plan (v0.1)

Source: `~/claudeworkspace/psyche/inbox/psycheeval_kickstart_prompt_plan.md` (the
"kickstart kit"). That document is a complete research-design artifact: master
prompt, seed banks, schemas, scoring rubrics, pilot plans, failure taxonomy,
repo structure. **This plan is not a replacement for it.** It translates the
kickstart kit into concrete execution steps inside this workspace, resolves
the workspace-specific choices the kit deferred to the user, and flags the
judgment calls that block work until answered.

---

## 0. What PsycheEval is (for orientation)

PsycheEval tests whether personality profiles derived from Psyche actually
improve assistant behavior in psychologically charged situations — and whether
they do so *without* increasing sycophancy, over-personalization, caricature,
or therapy cosplay.

Psyche produces profiles. PsycheEval asks: are the profiles load-bearing, or
decorative? The ideal finding would be a format (e.g. behavioral contract +
anti-sycophancy clauses, C4) that reliably beats `no profile` (C0) on
calibrated challenge and anti-sycophancy *without* losing specificity or
agency support.

---

## 1. Locked decisions

Decided 2026-04-19.

| # | Decision | Chosen |
|---|----------|--------|
| 1 | Public-anchor metadata | Real anchors in internal JSONL; public exports strip to alias + anchor_family |
| 2 | Alias tone | Mildly funny + respectful (kit default) |
| 3 | Initial scope | Micro first (8 personas × 6 scenarios × 4 conditions × 2 authors = 384 responses) |
| 4 | Source material | **Hybrid**: use codex-researcher (GPT-5.4) subagents to gather public material + fall back to high-level public reputation when thin. See §2.4 for the source-hunting workflow. |
| 5 | Scenario risk | Include conflict/shame/ambition/epistemic; avoid clinical crisis (kit default) |
| 6 | Location | `psyche/psycheeval/` |
| 7 | Models | **Opus 4.7 + GPT-5.4** as both authors *and* judges. Author-model comparison (Opus vs GPT as output generator) is promoted to a first-class research question, not a side note. Self-judging halo is mitigated via blind rotation + cross-provider judging (see §2.5). |
| 8 | License | MIT code + CC-BY data |
| 9 | Author's own profile case study | Qualitative sidebar only (n=1). Run scenarios with the real Psyche-derived profile in `profiles/claude-context.md` under C3/C4. Not part of quantitative pilot. |

---

## 2. Proposed location and stack

### 2.1 Where it lives

```
~/claudeworkspace/psyche/
├── analysis/              # existing Python pipeline
├── benchmark/             # existing report-quality benchmark (dual-judge)
├── psycheeval/            # NEW — this project
│   ├── prompts/           # copied verbatim from kickstart kit §6–§13
│   ├── schemas/           # JSON Schema files derived from kit §3
│   ├── data/
│   │   ├── seed_bank_public_inspired.jsonl
│   │   ├── seed_bank_pure_synthetic.jsonl
│   │   └── micro_pilot/...
│   ├── runs/              # YYYY-MM-DD_modelname/ per the kit §22
│   ├── src/psycheeval/    # Python package (uv)
│   │   ├── generate.py    # persona_seed → user_record → profile_bundle → scenarios
│   │   ├── run.py         # scenarios × conditions × models → assistant_outputs
│   │   ├── judge.py       # assistant_outputs × judges → judge_scores (+ pairwise)
│   │   ├── analyze.py     # judge_scores → tables + report.md
│   │   └── models.py      # pydantic for all 6 schemas
│   ├── reports/
│   ├── pyproject.toml
│   ├── PLAN.md            # this file
│   ├── BACKLOG.md
│   └── README.md
```

Rationale: it's a sibling of `benchmark/`, shares the psyche `uv` env and
profile conventions, but has its own directory because the data model
(persona → scenario → run → score) is completely different from the report-
quality benchmark.

### 2.2 Stack

- **Python 3.12 + uv** — matches `analysis/` and `benchmark/`
- **pydantic v2** — schema-as-code for all six object types in kit §3
- **openai SDK against DeepInfra + OpenAI + Anthropic SDK** — mirrors what
  `benchmark/run_eval.py` already does; no new dependencies
- **JSONL everywhere** — per kit §22, and matches the psyche corpus convention
- **pytest** — matches `analysis/tests/`

No web app in v0.1. If the eval matures, a simple Astro/React dashboard for
browsing failure cards could live under `web/` later, but that's out of scope.

### 2.3 Interaction with existing Psyche code

- **Reuse**: nothing in the quantitative pilot. PsycheEval synthesizes its
  own users; it doesn't consume `profiles/`.
- **Qualitative sidebar**: one run uses the real `profiles/claude-context.md`
  as a persona — C0/C3/C4 conditions, hand-evaluated, reported as an
  illustrative case study (decision §1.9).
- **Future**: once PsycheEval has proven a profile format, feed real Psyche-
  generated profiles through the same scenarios at scale. v0.2 task.

### 2.4 Source-hunting workflow (decision §1.4)

Per-persona pipeline for public-inspired seeds:

1. `codex-researcher` subagent runs with prompt: *"Gather representative public
   writing for {anchor}: 3–6 essays, talks, or interview excerpts that
   illustrate their characteristic worldview, rhetorical posture, and
   decision style. Return URLs + short excerpts (fair-use length only), plus
   a 200-word summary of recurring themes. Do not fabricate."*
2. Output is saved to `data/source_packets/{alias}_raw.jsonl`.
3. The kit §7 source packet ingestion prompt then processes that raw
   material into a structured `source_packet` JSON object. Critically: the
   ingestion step is the gate where unsupported inferences are scrubbed.
4. If step 1 returns thin results (< 3 sources, or no coverage on 2+ of the
   eight kit §7 attitude dimensions), the ingestion prompt falls back to
   high-level public reputation, and the resulting `source_packet` is
   flagged `source_grounding: "low"`. These personas get a weaker C5
   condition and their results are reported separately.
5. Every `source_packet` records `source_count`, `source_types`,
   `source_grounding`, and `do_not_infer` explicitly.

**Rejected alternatives I considered**: (i) pure background knowledge with no
retrieval — too much hallucination risk; (ii) manual user-supplied-only —
slow, and you already said you don't want that.

### 2.5 Self-judging halo mitigation (decision §1.7)

Because Opus and GPT-5.4 are both authors *and* judges, every response is at
risk of being judged by its own generator's family. Mitigations:

1. **Blind rotation**: judge prompts never reveal the output-author model.
   The condition letters are randomized per scenario (existing
   `benchmark/blinding_key.json` pattern).
2. **Cross-provider primary judgment**: for every response, report the
   cross-provider judge score as primary (Opus output → GPT-5.4 judge;
   GPT-5.4 output → Opus judge). The same-provider score is secondary.
3. **Halo audit**: compute `same_provider_score - cross_provider_score` per
   condition per author. If the delta is large and systematic, the halo is
   real and must be disclosed in the report.
4. **Author comparison is a first-class finding**: "Does Opus or GPT produce
   better adapted responses under each profile condition?" gets its own
   section in the analysis report, with cross-provider-judged scores as the
   primary evidence.

---

## 3. Phased execution

Each phase has an explicit exit criterion. Don't advance until it's met.

### Phase 0 — Decisions + bootstrap (half day)

- Answer judgment calls §1.1–§1.8
- Create `psycheeval/` skeleton (the tree above)
- Copy kit prompts into `prompts/00_master.md` … `prompts/08_analysis.md`
- Write `schemas/*.schema.json` from kit §3 (six schemas)
- Scaffold `pydantic` models in `src/psycheeval/models.py` matching the
  schemas one-to-one
- Write `README.md` stating: purpose, non-goals, public-anchor policy, ethics
  note, dataset card template
- Commit

Exit: `uv run python -c "from psycheeval.models import PersonaSeed; PersonaSeed.model_validate({...})"` passes against a hand-written fixture.

### Phase 1 — Micro-pilot data generation (2–3 days)

Targets: 8 personas, 6 scenarios each, 4 conditions (C0, C1, C3, C4), **2
output authors (Opus 4.7 + GPT-5.4)**. Per kit §16.1: **generate dataset only,
no assistant responses yet.**

1. **Persona seed bank** — write the full seed banks from kit §4 and §5 into
   `data/seed_bank_*.jsonl`. ~60 public-inspired + ~50 pure synthetic. Keep
   the bank large; the pilot uses a subset.
2. **Select 8 personas** for micro (4 public-inspired + 4 pure, per kit §16.1
   defaults: Slalom Altar, Dario Armadillo, Emily Blender, Pawl Gram; The
   Calibration Goblin, The Conflict-Allergic Moralist, The High-Agency
   Spiraler, The Patient Craftsperson).
3. **Source hunting** (new, per §2.4) — run `codex-researcher` for each of
   the 4 public-inspired personas to gather public material. Save raw
   results to `data/source_packets/{alias}_raw.jsonl`. Then run kit §7
   ingestion prompt to produce structured `source_packets/{alias}.json`.
   Flag `source_grounding` level.
4. **Generate `synthetic_user_record`** for each via `generate.py` using kit
   §6 prompt. One record per persona. Public-inspired personas get their
   source packet passed in; pure synthetic do not. Save to
   `data/micro_pilot/synthetic_user_records.jsonl`.
5. **Generate `profile_bundle`** with C1–C4 per user via kit §8 prompt. For
   the 4 public-inspired personas, also generate C5 (source-packet-informed)
   — this makes micro effectively C0/C1/C3/C4 for all 8, plus C5 for 4, so
   the effective condition count varies by persona. Save to
   `data/micro_pilot/profile_bundles.jsonl`.
6. **Generate 6 scenarios per persona** via kit §9 prompt. Save to
   `data/micro_pilot/scenarios.jsonl`.
7. **Hand-review all generated artifacts** — the most important step. The
   whole pilot fails silently if the synthetic users are trait-bundles. Kit
   §25 gives the invalidation list; check every item on it, plus:
   - Do public-inspired personas read as fictional analogues, not
     impersonations?
   - Do source packets cite real excerpts (verifiable URLs) or confabulate?
   - Do pure synthetic personas contain contradictions (kit §6.8 requires
     "realistic users are not trait vectors")?

Exit: 8 user records + 8 profile bundles + 48 scenarios + 4 source packets
exist, pass schema validation, and a hand read of 3 random personas does not
collectively produce any of the kit §25 weakness patterns.

### Phase 2 — Run + judge (2 days)

1. **Run manifest** — materialize run rows as `run_manifest.jsonl`:
   - 8 personas × 6 scenarios × 4 conditions (C0/C1/C3/C4) × 2 authors = 384 rows
   - Plus 4 public-inspired personas × 6 scenarios × 1 condition (C5) × 2 authors = 48 rows
   - **Total: 432 assistant responses**
2. **Execute `run.py`** against the manifest. Authors: Opus 4.7 + GPT-5.4.
   Temperature 0.7. Save to `runs/YYYY-MM-DD_micro/assistant_outputs.jsonl`.
3. **Blind the conditions** in the judge input (rename `C0/C1/C3/C4/C5` →
   randomized letters per scenario, keep the un-blinding key separate).
   Also blind the *author model* — judge must not know whether Opus or GPT
   wrote the response (this is the §2.5 halo mitigation). Matches how
   `benchmark/blinding_key.json` already works.
4. **Execute `judge.py`** — two judges (Opus 4.7 + GPT-5.4) both score all
   432 responses using the kit §11 rubric. Save to `judge_scores.jsonl`.
   **Total: 864 score records.**
5. **Pairwise judgments** — for each scenario, all pairs of conditions ×
   2 judges. For the 4 public-inspired personas (with C5): C(5,2) = 10 pairs
   × 6 scenarios × 2 judges = 120 per persona × 4 personas = 480. For the 4
   pure synthetic (no C5): C(4,2) = 6 pairs × 6 scenarios × 2 judges = 72
   per persona × 4 = 288. **Total: 768 pairwise calls.** Use kit §12 prompt.
   Save to `pairwise_scores.jsonl`.
6. **Qualitative self-persona run** (parallel) — 6 scenarios × 3 conditions
   (C0/C3/C4) × 2 authors = 36 responses using the actual
   `profiles/claude-context.md`. Same judging pipeline. Reported separately
   as a sidebar, not merged into the quantitative tables.

Exit: all four JSONL files exist, schema-valid, and no judge returned more
than ~5% parse failures.

### Phase 3 — Analysis + report (1–2 days)

1. **Compute core metrics** per kit §13 — mean & median by condition × judge
   × author, red-flag rate by condition, pairwise win rate, C4-C0 and C4-C2
   deltas, public-inspired vs pure-synthetic deltas, inter-judge agreement
   (Cohen's κ on red-flag labels, Spearman on dimension scores).
2. **Halo audit** (new, per §2.5) — `same_provider_score - cross_provider_score`
   per author × condition. Call out any systematic gap ≥0.3 on the 0–5 scale.
3. **Author comparison** — Opus 4.7 vs GPT-5.4 as output author, scored by
   cross-provider judge. Breakdown by scenario family + by condition. This
   is a headline research finding (decision §1.7).
4. **Generate `reports/psycheeval_v0_1_micro_pilot.md`** — human-facing
   research note, not model output. Honest synthetic-limits language per
   kit §19.
5. **Pull ~10 failure cards** — 2 best examples per condition, 1 failure
   per failure-taxonomy category that appeared, plus 2 halo-suspicious cases
   if any surface. Save to `reports/failure_cards.md`.
6. **Write self-persona sidebar** — short narrative of how the real profile
   performed under C0/C3/C4. Include representative quotes. Flagged n=1.
7. **Decide next step**:
   - If C4 beats C0 on ≥6 of 10 dimensions in both authors (cross-provider
     judged) and red-flag deltas point the right way → scale to pilot (24
     personas)
   - If one author dominates and the other floors → iterate on prompts
     before scaling; the "does Opus need different instructions than GPT"
     question becomes its own sub-experiment
   - If halo audit shows large same-provider gap → fix the blinding and
     re-run Phase 2 before publishing

Exit: report exists, committed, and the next-step decision is recorded in
`BACKLOG.md`.

### Phase 4 — Pilot scale-up (only if Phase 3 says yes)

- Kit §16.2: 24 personas × 8 scenarios × 5 conditions × 2 models = 1,920
  responses; add C5 where source packets exist.
- This is where cost starts mattering. Estimate: ~5k author calls + ~10k
  judge calls. At current pricing, roughly $30–$80 depending on model mix.
- Also: first public artifact. License decision (§1.8) must be locked before
  anything is pushed.

### Phase 5+ (out of scope for this plan)

- Length-control experiment (kit §26) — critical for publication credibility
- Adversarial scenarios (kit §28) — add in v0.2
- Real Psyche profile closure: feed an actual Psyche-generated profile
  through the same scenarios and compare to synthetic profiles
- Human validation sample (kit §19.1) — 2–3 expert spot-check raters on 50
  examples. Lowest-cost credible human layer.

---

## 4. Non-goals (explicit)

- **Not clinical.** No diagnosis, no severity scoring, no mental-health
  stratification. The kit is clear on this; the repo README must restate it.
- **Not impersonation.** Public-inspired personas are fictional analogues
  with deliberately wrong aliases, no fake quotes, no inferred private facts.
- **Not a replacement for human evaluation.** Synthetic-first is a
  prerequisite for asking humans meaningful questions later, not a shortcut
  past them.
- **Not a Psyche deliverable.** Psyche produces profiles. PsycheEval tests
  whether they help downstream. They share a repo for now, but the audit
  trails are separate — PsycheEval results do not change `profiles/`.

---

## 5. Risks and mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Synthetic users read as trait bundles (kit §25 primary failure) | High | Phase 1 exit criterion is a hand-review gate; no advance without it |
| C4 wins only because it has more tokens | High | Phase 5 length-control experiment planned before publication |
| Judges infer the condition and reward it | Medium | Blinding key + randomized letters; post-hoc check for condition-guessing |
| Public-inspired personas produce caricature | Medium | Add `caricature_risk` to every seed; judges flag `caricature_public_anchor`; review failure cards specifically for this |
| Cost overrun on scale-up | Medium | Micro first; budget check before pilot; prefer cheaper authors + stronger judges |
| Self-judging halo: Opus judges Opus output favorably | Medium | Two-judge panel (Opus + GPT) + pairwise; report inter-judge disagreement as a first-class metric |
| Naming offense — an alias reads as mocking | Low-medium | Kit §23 naming principles enforced; second-pass human review before publication |
| Result collapses to "no profile is fine, stop worrying" | Low but real | That's a valid finding; write it up honestly |

---

## 6. Open questions the kickstart kit does *not* resolve

These should be decided during Phase 0 or 1, not deferred indefinitely.

1. **Do we include a "bad profile" condition** (e.g. a deliberately wrong
   profile fed to the model) to test whether the model can detect and
   override a mis-specified personalization? This would strengthen the "does
   the profile actually help" claim by showing a dose-response.
2. **Judge rubric calibration** — judges may anchor differently on 0–5
   scales. Should we prepend a calibration packet (5 example responses with
   target scores) to every judge call? Recommendation: yes, after Phase 2
   pilot run if agreement is weak.
3. **Persona-of-the-user-running-this** — should there be a "Claude's own
   user" persona, using the existing `profiles/claude-context.md`? This is
   ethically clean (it's the author's own profile), high-signal (the author
   can eyeball whether responses feel adapted), but also risky as a headline
   result. Recommendation: yes, but as a qualitative case study, not part of
   the quantitative pilot.
4. **Scenario ecological validity** — the kit's scenarios are all "user
   asks for help with X." Real conversations are multi-turn. Do we add a
   follow-up turn in v0.2 where the user responds to the assistant's first
   reply? Probably, but it doubles the cost.
5. **Publication venue** — arXiv draft, blog post on `ashitaorbis.com`,
   standalone site, or all three? This affects how much polish Phase 3 needs.

---

## 7. First-week task list (ordered)

1. ~~Answer judgment calls~~ — done 2026-04-19
2. Scaffold `psycheeval/` directory + pydantic models + schemas (half day)
3. Transcribe full seed banks (kit §4 + §5) to JSONL (1 hour)
4. Build source-hunting workflow: codex-researcher caller + kit §7 ingestion
   pipeline (half day)
5. Run source hunter for 4 public-inspired pilot personas (half day, mostly wait)
6. Write `generate.py` for synthetic_user_record (half day)
7. Write profile-bundle compiler incl. C5 (half day)
8. Write scenario generator (half day)
9. Hand-review gate — *do not skip* (half day)
10. Write `run.py` (author: Opus 4.7 + GPT-5.4, blinded) (half day)
11. Write `judge.py` with cross-provider rotation (half day)
12. Run micro-pilot + self-persona sidebar (1 day wall-clock, mostly API wait)
13. Write `analyze.py` + halo audit + author comparison (1 day)
14. Draft Phase 3 report + failure cards (1 day)

Estimated total: ~7 working days for micro-pilot end-to-end (up from 5 due to
source-hunting + C5 + self-persona sidebar + author-comparison analysis).
Roughly 55% code, 45% judgment. The hand-review gate remains the most
expensive step in hours but the cheapest in tokens.
