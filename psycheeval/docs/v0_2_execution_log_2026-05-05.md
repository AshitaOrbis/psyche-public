# PsycheEval v0.2 — execution session log

**Started**: 2026-05-05 23:52 PT
**User status**: sleeping; autonomous execution per instruction "begin working through the next phases, we'll likely hit usage limits but also it would be an issue if we didn't and lost the available usage."

This log is updated as the session progresses. The most recent entry below
is the current state.

---

## Phase 0 (no LLM cost) — COMPLETE 2026-05-05

- Cap-burn handler at `src/psycheeval/cap_burn.py`: 19 tests passing
- `judge.py` wired with cap-burn protection on both score + pairwise paths
- Native analyzer ports landed:
  - `_compute_tie_rates` (verifies v0.1 §6e numbers exactly)
  - `_compute_pi_ps_split_pairwise` (verifies v0.1 §6f numbers exactly)
  - `_compute_length_buckets_pairwise` (verifies v0.1 §6g numbers exactly)
  - `_compute_red_flag_stratification` (judge / cross-provider / output-level)
  - `_compute_scenario_family_breakdowns`
  - `_compute_cluster_bootstrap_pairwise` (cluster unit: persona × scenario × author)
  - `_compute_scalar_inter_judge_agreement` (per-dim Pearson + Spearman + severity offsets)
- 87/87 tests passing
- v0.1 metrics regenerated with new analyzer; cluster-bootstrap CIs confirm
  v0.1 §12 #5 threat (C3 vs C4 Wilson [0.400, 0.494] → bootstrap [0.383, 0.515])
- Scalar inter-judge agreement on v0.1: Pearson 0.60–0.74 across pairs
  (resolves v0.1 §11b unmeasured-pooling caveat empirically)

## Phase 1 (codex side) — IN PROGRESS

### Decisions locked (2026-05-05, all defaults)

D1 contract-first prompt order; D2 restricted pairwise scope {C3, C4, C5};
D3 defer C5_NONPUBLIC / C5_SHORT / C5_BEHAVIORALIZED to v0.3;
D4 cluster-bootstrap CIs in v0.2; D5 scalar ICC in v0.2;
D6 stylometric audit optional; D7 ship v2 blog after v0.2 report.

Plan doc: `docs/v0_2_plan_extended_2026-05-05.md`
Deferred-edges manifest: `reports/backlog/v02_deferred_pairwise_edges.json`

### Phase 1.1–1.4 scaffolding — DONE

- `Condition.C5_CONTRACT` added to enum
- `ProfileConditions.C5_contract` field added
- `normalize.py` _C_KEYS + short_to_long updated
- `run.py` cond_map + cond_field_map updated
- `config.PILOT_CONDITIONS["v02_hard_pilot"]["public_extra"]` includes C5_CONTRACT
- Tests still green

### Phase 1.3 prompt template + v02_prepare — DONE

- `build_c5_contract(c3_text, c5_text)` in `v02_prepare.py`
- Synthesis: `[BEHAVIORAL CONTRACT] {C3 text}\n\n{PRIORITY RULES}\n\n[SOURCE PACKET — context only; do not perform or imitate] {C5 text}`
- Anti-mimicry rules per locked D1: prioritize contract; do not perform/mimic/caricature; use packet for inferring support preferences only; preserve uncertainty; contract wins on conflict
- Re-materialized v02_hard_pilot bundles: 4 PI personas have C5_CONTRACT populated; 4 PS personas correctly have C5_CONTRACT=None

### Phase 1.5 codex generation — COMPLETE 2026-05-06

80/80 outputs, 0 failed. Original launch 2026-05-05 23:52, complete ~00:30 next morning.

Original launch details (PID 3532435):
Command: `psycheeval.run --pilot v02_hard_pilot --tag 2026-04-26_v02_hard_codex_only --authors gpt-5.4,gpt-5.5-xhigh --workers 4`

80 new C5_CONTRACT outputs total (4 PI × 10 scenarios × 2 codex authors).
Resume-safe via existing dedup; existing 1040 codex outputs are skipped.

Progress log at `logs/phase1_5_codex_gen.log`.

Qualitative spot-check after 50/80 outputs landed: C5_CONTRACT response on
`scn_v02_ambition_status_user_pfi_slalom_altar_001_6` (gpt-5.5 author) is
228 words vs C5's 318 words on the same scenario. C5_CONTRACT response uses
explicit decision-frame structure ("Strong counterargument:", "If/then" branches)
matching the contract style; C5 response is more aphoristic. The
contract-first ordering and anti-mimicry rules appear observable in actual
outputs — a good sign.

### Phase 1.6 codex scoring — QUEUED

Driver: `drivers/phase1_codex_pipeline.sh` — waits for 1.5 PID then chains.
Will judge the 80 new C5_CONTRACT outputs with anchored rubric (2 codex
judges × 80 = 160 calls, plus any other missing records). Resume-safe.

### Phase 1.7 codex pairwise — RUNNING (relaunched 00:36 with corrected scope)

Pairs filter: `C3:C5_CONTRACT@PI,C4:C5_CONTRACT@PI,C5:C5_CONTRACT@PI`.

**Bug caught + fixed**: the original chain driver did not pass `--scope` and
the judge.py CLI default is `exhaustive` (cross-author + same-author pairs).
The original v0.2 codex pairwise was generated with `same_author_only` scope.
Running Phase 1.7 with the wrong scope would have generated wasteful
cross-author pairs we don't want for v0.2.

After 9 records had been written under the wrong scope, the issue was
caught (pending count=1080 didn't match expected ~480). Process killed,
chain driver fixed to pass `--scope same_author_only`, Phase 1.7 relaunched
manually as PID 3784657. The 9 stray cross-author records left in
`pairwise_scores.jsonl` are harmless — analyzer's existing same-author
filter excludes them automatically.

Both the Phase 3 chain driver and the Opus orchestrator have the same
fix applied so Opus pairwise will use the correct scope when it kicks in.

Expected = 504 pair records (3 pairs × (40 gpt-5.4 + 40 gpt-5.5 + 4 opus
PI same-author cells) × 2 codex judges, with the Opus count growing as
more Opus author outputs land).

**Note on existing v0.2 pairwise scope.** Inventory of the existing
2,080 codex pairwise records (1,040 per judge):

| Pair | n per judge |
|------|---:|
| C0 vs C4 | 160 |
| C1 vs C1_padded | 160 |
| C1 vs C4 | 160 |
| C1_padded vs C4 | 160 |
| C3 vs C4 | 160 |
| C4 vs C4_shuffled | 160 |
| C4 vs C5 (PI only) | 80 |

The existing v0.2 pairwise scope was a C4-centric set (every pair includes C4
except `C1 vs C1_padded`, which is the length-control-only test). This is a
deliberate scope-narrowing choice from the original 2026-04-24 v0.2 plan to
keep cost down. The C5_CONTRACT additions (C3 / C4 / C5 vs C5_CONTRACT)
deliberately complement this — the report's PAE story needs the C5_CONTRACT
vs {C3, C4, C5} comparisons specifically.

This means **C5 vs C3 pairwise is NOT in v0.2** (it was in v0.1). If we want
to re-establish whether C3 still beats C5 under the anchored rubric on harder
scenarios, that's a v0.3 backfill candidate. Documented in the deferred-edges
manifest as out of scope.

## Phase 2 (Opus authoring) — IN PROGRESS

Launched 2026-05-05 23:53. Background PID 3538464.
Command: `psycheeval.run --pilot v02_hard_pilot --tag 2026-04-26_v02_hard_codex_only --authors opus --workers 1`

Workers=1 enforced for Opus per cap-protective default. Cap-burn handler
will kick in when 5h cap hits; checkpoint will be written to
`runs/<tag>/checkpoint_score_<rubric>.json`. Resume-safe via dedup.

Estimated work: ~600 Opus author outputs needed (8 personas × varying
conditions × 10 scenarios). At ~1 output/min sequential, full corpus is
~10 hours. The 5h cap will trigger one window's worth of work, then cap.

Progress log at `logs/phase2_opus_author.log`.

## Phase 3 (Opus judging) — QUEUED behind Phase 2

Driver: `drivers/phase3_opus_judging_pipeline.sh` — waits for Phase 2 PID
then chains anchored scoring + restricted pairwise. workers=1.

## Optional: cross-cap-window auto-resume — `drivers/opus_nightly_orchestrator.sh`

Available but **not auto-launched**. The current Phase 2 + Phase 3 drivers
run a single Opus iteration. If you want to auto-resume across cap windows
(useful for overnight or weekend runs), invoke the orchestrator after the
current chain exits:

```bash
cd ~/claudeworkspace/psyche/psycheeval
nohup bash drivers/opus_nightly_orchestrator.sh > logs/orchestrator.log 2>&1 &
```

Defaults: 3 iterations, 5h sleep between iterations. Each iteration runs
Opus authoring → anchored scoring → restricted pairwise. Resume-safe via
existing dedup; iterations after the first only do remaining work.

The reason this isn't auto-launched: introducing a long-running loop with
sleep timers in an autonomous overnight session is higher-risk than letting
the existing one-shot drivers complete and surfacing the resume option for
human review.

## Phase 4–6 — manual after data lands

Phase 4 (analysis) is `psycheeval.analyze --tag <v0.2-tag>`. Phase 5
(curate report) uses the skeleton at `reports/psycheeval_v0_2_skeleton.md`.
Phase 6 (v2 blog) is the remote-session writer.

## Side: v1 blog draft is COMPLETE (independent of v0.2)

The v1 blog post for the **v0.1 tri-model report** was completed by the
remote writer session spawned earlier. Saved as draft at
`~/claudeworkspace/applications/ashitaorbis/shared/content/posts/042-what-the-psycheeval-pilot-was-actually-measuring.md`
(103 lines, frontmatter `draft: true`, ready for `/writing-review` and
`/publication-review`). Includes the load-bearing findings: length-bucketed
pairwise C5 analysis, corrected halo-direction reversal, PAE confound
disclosure, methodology-pilot framing. Once the review skills are run and
draft flag removed, `scripts/deploy-posts.sh` deploys across all three
Ashita Orbis tiers.

This is for v0.1 (v1 blog post). The v2 blog post (after v0.2 corpus is
analyzed) will spin up a separate writer session and reuse the
`reports/psycheeval_v0_2_skeleton.md` scaffold.

---

## What's running right now

| PID | Process | Started | Phase |
|---|---|---|---|
| 3532435 | psycheeval.run (codex C5_CONTRACT) | 23:52 | 1.5 |
| 3538464 | psycheeval.run (Opus authoring full) | 23:53 | 2 |
| 3554167 | drivers/phase1_codex_pipeline.sh (waiting) | 23:55 | 1.6 → 1.7 |
| 3557949 | drivers/phase3_opus_judging_pipeline.sh (waiting) | 23:56 | 3.1 → 3.2 |

Monitors armed for both: codex completion/error (`tail -F | grep`), Opus
cap events / completion (`tail -F | grep`).

## When the user wakes up

### One-line status

```bash
cd ~/claudeworkspace/psyche/psycheeval && bash drivers/morning_status.sh
```

This prints active processes, corpus counts, cap events, checkpoints, and
recent log tails — one page summary.

### Run analyzer on whatever data is in

```bash
bash drivers/analyze_v02_partial.sh
```

This regenerates `metrics_<tag>.json` and the autogen scaffold with all the
new native v0.2 diagnostic blocks. Safe even mid-run: it operates on
snapshot of the JSONL files at invocation time. Probe records are excluded
fail-closed.

### What state is everything in

**v0.1 work** — DONE before this session. Canonical artifact:
`reports/psycheeval_v0_1_micro_pilot_2026-04-26_micro_tri_model.md`.

**v1 blog post** — DRAFT exists at
`~/claudeworkspace/applications/ashitaorbis/shared/content/posts/042-what-the-psycheeval-pilot-was-actually-measuring.md`,
`draft: true`, ready for `/writing-review` and `/publication-review`.
Independent of v0.2 — can be deployed today after review.

**Phase 0** (cap-burn fix + native analyzer port + tests) — DONE.
94/94 tests passing. v0.1 metrics regenerated with the new analyzer blocks.

**Phase 1.5** (codex C5_CONTRACT generation) — DONE. 80/80 outputs.

**Phase 1.6** (codex anchored scoring on new outputs) — IN PROGRESS at
launch time of this log entry. Auto-chains to 1.7 on completion.

**Phase 1.7** (codex pairwise C5_CONTRACT × {C3, C4, C5}) — QUEUED. Auto.

**Phase 2** (Opus authoring full v0.2 corpus) — IN PROGRESS. Will hit cap
during the night; cap-burn handler protects against rc=1 spins.

**Phase 3** (Opus judging full v0.2 corpus) — QUEUED behind Phase 2.

**Opus nightly orchestrator** — sleeping 6h before iteration 1 (started
00:08, will wake ~06:08 to retry Phase 2 + 3 if cap-aborted). Up to 3
iterations × 5h sleeps. Resume-safe.

### If something is stuck

If `morning_status.sh` shows checkpoints with `cap_aborted: true`, the
suggested_resume_command in each checkpoint is what to run next. The
orchestrator will auto-resume once it wakes up; you can also re-run
manually.

If a process is stuck (running but not progressing), the cap-burn handler
should have already engaged. Check `runs/<tag>/cap_events.jsonl` for the
latest cap event — if it's hours old and the process is still running,
something's wrong. `kill <PID>` and re-launch via the suggested resume.

### Phase 4 (analysis) when the corpus is "done enough"

When you're ready to curate v0.2:

```bash
bash drivers/analyze_v02_partial.sh
```

Then open `reports/psycheeval_v0_2_skeleton.md` and fill in the
[PLACEHOLDER] markers from the metrics JSON. The skeleton structure mirrors
the v0.1 report so the same review workflow (Path B → publication-review)
applies.
