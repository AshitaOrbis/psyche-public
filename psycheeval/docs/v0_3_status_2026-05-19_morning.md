# v0.3 Status — 2026-05-19 morning hand-off

**Session checkpoint**: codex generation running autonomously; Opus side queued for the user to launch when burning a Claude cap.

## Pipeline state

| Stage | Status | PID | ETA |
|-------|--------|-----|-----|
| Codex Phase 1 generation (720 outputs) | **RUNNING** | 3125527 | ~3h remaining |
| Pipeline orchestrator (chains into scalar + pairwise) | **WAITING** for gen | 3141240 | will start when gen finishes |
| Codex scalar judging | queued (auto) | — | ~30min |
| Codex AB/BA pairwise | queued (auto) | — | ~3-4h |
| Opus generation | **NOT STARTED** — user decides when to launch | — | ~3-6h (Claude cap) |
| Opus judging | not started | — | ~3-4h (Claude cap) |
| Sentinels (D1, D2, D4) | not implemented as commands yet | — | — |
| Phase 6 analysis | depends on judging | — | ~1 day |
| Phase 7 report | depends on analysis | — | 2-3 days |

## Background process commands

The codex pipeline runs autonomously. To monitor:

```bash
# Progress checks
cd ~/claudeworkspace/psyche/psycheeval
wc -l runs/2026-05-19_v03/assistant_outputs.jsonl
tail -20 logs/v0_3_phase1_codex.log
tail -20 logs/v03_codex_pipeline.log

# Are processes alive?
ps -p 3125527 -o pid,etime --no-headers   # generation
ps -p 3141240 -o pid,etime --no-headers   # orchestrator
```

## To burn a Claude cap on Opus work

When ready, launch Opus generation:

```bash
cd ~/claudeworkspace/psyche/psycheeval
nohup env PYTHONPATH=src python3 -u -m psycheeval.run \
  --pilot v03_full_pilot \
  --tag 2026-05-19_v03 \
  --authors opus \
  --conditions C_GENERIC_CONTRACT,C4_WRONG_PROFILE,C5_NONPUBLIC,C5_NONPUBLIC_CONTRACT,L1,L2,L3 \
  --workers 1 \
  > logs/v0_3_phase1_opus_gen.log 2>&1 &
```

Then Opus scalar judging (after generation completes):

```bash
python3 -m psycheeval.judge score \
  --tag 2026-05-19_v03 \
  --pilot v03_full_pilot \
  --judges opus \
  --rubric anchored \
  --workers 1
```

Then Opus pairwise:

```bash
# 28 pair-type whitelist defined in drivers/run_v03_codex_pipeline.sh
# Run with same pair list as codex pairwise; --ab-ba-mandatory ensures swap
python3 -m psycheeval.judge pairwise \
  --tag 2026-05-19_v03 \
  --pilot v03_full_pilot \
  --judges opus \
  --pairs '<see pipeline script>' \
  --scope same_author_only \
  --ab-ba-mandatory \
  --workers 1
```

## Phase 0 complete

All Phase 0 items are in. Commits today:
- `15de3f0` — v0.3 conditions in run.py + --conditions / --scenario-limit filters
- `53c912a` — wire D1-D4 into compute_metrics + bundle_id fix
- `9ea9847` — paraphrased anchored rubric (06c_judge_anchored_paraphrased.md) for D2
- `dc47d5f` — codex pipeline orchestrator script

Earlier today (yesterday's overnight):
- `1b58d23` — v0.3 plan revision + reviews + initial condition wiring
- `3268ead` — D1 + D3 analyzer blocks + ternary prompt
- `0015767` — first overnight status note
- `f4088c9` — Phase -1 sealed + D2 + D4 analyzer blocks + 4 PI-matched nonpublic packets
- `b0348e6` — --ab-ba-mandatory flag + 26 smoke tests
- `4597faf` — final overnight status note

11 commits total in `psyche/` repo. None pushed.

## Open Phase 0 items (deferred)

The sentinel COMMANDS (not analyzer blocks) aren't implemented yet:
1. **Same-orientation rejudge command** — needed for D1 sentinel. Would mirror `pairwise_swap_rejudge` but not swap. ~1h.
2. **Ternary pairwise command** — needed for D4 sentinel. Uses `07b_pairwise_judge_ternary.md`. ~1h.
3. **Paraphrased anchored judging command** — needed for D2 sentinel. Uses `06c_judge_anchored_paraphrased.md`. ~30min.

Total ~2.5h of additional code work. These can be done while the codex pipeline runs. The analyzer blocks themselves (D1/D2/D4) handle empty input gracefully, so they won't crash if the sentinel records don't exist yet.

## v0.3 estimated total wall time remaining

Optimistic path (cap-window-aware):
- **Today (3-4 caps)**:
  - Cap 1 (current): codex pipeline launched, runs autonomously; ~6-8h
  - Cap 2: Opus generation (~3-6h)
  - Cap 3: Opus judging (~3-4h) + sentinel commands code work
  - Cap 4: Phase 6 analysis + Phase 7 report draft start
- **Tomorrow**:
  - Sentinel data collection (paraphrased / same-orientation / ternary samples)
  - Phase 7 review pass (publication-review)
  - Phase 8 blog post draft
  - Phase 9 shadow-mode design doc

v0.3 ships sometime tomorrow or day after, depending on cap timing.

## Decision points coming up

None blocking right now. Possible future ones:
1. Opus quota constraints — if `claude -p` hits its 5-hour cap mid-Opus-generation, the cap-burn handler will checkpoint and exit cleanly. User decides when to resume.
2. If sentinel data is insufficient (e.g., <50 paraphrased records produced) the D2 block will return `status: "no_paraphrased_records"` — gracefully degrades, doesn't crash analysis.
3. Phase 9 shadow-mode design doc requires the user's input on Psyche results-page UI/instrumentation details if the design is going to be specific enough to execute in v0.4.
