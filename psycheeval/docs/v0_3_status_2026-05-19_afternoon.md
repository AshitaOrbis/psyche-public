# v0.3 Status — 2026-05-19 afternoon update

**Major progress checkpoint**. Phase -1 sealed. Phase 0 complete (all sentinels). Phase 1 generation running autonomously (4 background processes). Phase 9 design doc shipped.

## TL;DR

- **18 commits today in psyche/ repo** (none pushed)
- **All v0.3 code is in place** — conditions, analyzer blocks, sentinel commands, prompts, tests, orchestrators
- **4 background processes running** the full v0.3 codex+Opus pipeline autonomously
- **Quality verified**: spot-checked C_GENERIC, C4_WRONG, L1 ladder all produce substantive contract-following responses
- **Phase 9 shadow-mode design doc** shipped at `docs/shadow_mode_validation_v04_design.md`
- **Estimated v0.3 completion**: ~9 hours total wall time for full codex+sentinels chain; Opus runs in parallel at ~6 hours wall time

## Background process state

| PID | Started | Role | Status |
|-----|---------|------|--------|
| 3125527 | 07:00 | Codex Phase 1 generation (gpt-5.4 + gpt-5.5-xhigh × 7 new conditions) | RUNNING |
| 3144900 | 07:07 | Opus Phase 1 generation (opus × 7 new conditions) | RUNNING (cap-protected) |
| 3141240 | 07:06 | Codex orchestrator (waits for gen → scalar → pairwise+swap) | WAITING |
| 3177825 | 07:19 | Sentinel orchestrator (waits for 3141240 → D1/D4/D2) | WAITING |

## v0.3 code state — everything in place

### Conditions (8 new in v0.3 corpus)
| Code | Description |
|------|-------------|
| C_GENERIC_CONTRACT | Structurally-C3-like, generic language, length-matched to C4 |
| C4_WRONG_PROFILE | C4 with opposite-trait persona's profile substituted |
| C5_NONPUBLIC | PI-matched fictional biographical narrative (no public anchor) |
| C5_NONPUBLIC_CONTRACT | C5_NONPUBLIC + anti-mimicry contract wrapper |
| L1 | C5 + minimal contract, packet-first, no anti-mimicry, length-matched to C5 |
| L2 | L1 + anti-mimicry rules |
| L3 | L2 with contract-first ordering |

### Analyzer blocks (4 new in v0.3, all wired into compute_metrics)
| Block | Purpose |
|-------|---------|
| D1 same-orientation sentinel | Decomposes AB/BA flip into position-bias + retest-noise |
| D2 paraphrased anchor consistency | Detects rubric anchor-sensitivity via Spearman ρ |
| D3 reward-hacking diagnostics | Per-output: length, profile-refs, hedging, lexical overlap |
| D4 tie-aware reinterpretation | Cross-prompt forced-choice vs ternary tie rate |

### Sentinel commands (all live)
| Command | Purpose | Sample |
|---------|---------|--------|
| `same-orientation-rejudge` | D1 input | 10% of pairwise |
| `ternary-sample` | D4 input (07b ternary prompt) | 10% of pairwise |
| `score --rubric paraphrased_anchored --sample-pct 15` | D2 input (06c paraphrased) | 15% of scalar |

### Tests
26 smoke tests passing in `tests/test_v03_analyzer_blocks.py`.

### Phase 9 deliverable
`docs/shadow_mode_validation_v04_design.md` — UI delta, routing, instrumentation, power analysis, pre-registered predictions framework, falsification conditions.

## Commits today (18 total, none pushed)

| Commit | Subject |
|--------|---------|
| 1b58d23 | v0.3 plan + reviews + initial condition wiring |
| 3268ead | D1 + D3 analyzer blocks + ternary prompt |
| 0015767 | First overnight status note |
| f4088c9 | Phase -1 sealed + D2/D4 analyzer blocks + 4 nonpublic packets |
| b0348e6 | --ab-ba-mandatory flag + 26 smoke tests |
| 4597faf | Final overnight status note |
| 15de3f0 | v0.3 conditions in run.py + --conditions/--scenario-limit |
| 53c912a | Wire D1-D4 into compute_metrics + bundle_id fix |
| 9ea9847 | Paraphrased anchored rubric (06c) |
| dc47d5f | Codex pipeline orchestrator script |
| 0ea46a3 | Morning hand-off status note |
| fb9cacc | same-orientation-rejudge command |
| 320ff36 | Phase 9 shadow-mode v0.4 design doc |
| 9c22295 | ternary-sample command + refactor to shared helper |
| 546da21 | paraphrased_anchored rubric + --sample-pct flag |
| 34b889e | Codex orchestrator: add D1/D2/D4 sentinel stages |
| c93c4ed | Sentinel-after-pipeline orchestrator |
| (this commit) | Afternoon status checkpoint |

## What's left to ship v0.3

| Item | Status |
|------|--------|
| Phase 1 generation (codex + Opus) | RUNNING ~3-6h |
| Phase 3 anchored scalar judging | queued (auto, ~30min) |
| Phase 4 AB/BA pairwise judging | queued (auto, ~3-4h) |
| Phase 4 sentinels (D1/D4/D2) | queued (auto, ~1-2h) |
| Opus side scalar + pairwise judging | NOT QUEUED — user burns cap |
| Phase 5 human rater | manual, ~50 pairs |
| Phase 6 analysis | depends on judging, ~1 day |
| Phase 7 curate report | depends on analysis, 2-3 days |
| Phase 8 v3 blog post | depends on report, 2-3 days |
| Phase 9 design doc | ✅ shipped |

## Manual commands

### Opus judging (user burns cap to run)
```bash
cd ~/claudeworkspace/psyche/psycheeval

# After Opus generation completes:
PYTHONPATH=src python3 -m psycheeval.judge score \
  --tag 2026-05-19_v03 --pilot v03_full_pilot \
  --judges opus --rubric anchored --workers 1

# Opus pairwise (pair whitelist is in drivers/run_v03_codex_pipeline.sh):
PYTHONPATH=src python3 -m psycheeval.judge pairwise \
  --tag 2026-05-19_v03 --pilot v03_full_pilot \
  --judges opus --pairs '<see pipeline script>' \
  --scope same_author_only --ab-ba-mandatory --workers 1

# Opus sentinels:
PYTHONPATH=src python3 -m psycheeval.judge same-orientation-rejudge \
  --tag 2026-05-19_v03 --pilot v03_full_pilot \
  --judges opus --pairs '<see pipeline script>' --workers 1

PYTHONPATH=src python3 -m psycheeval.judge ternary-sample \
  --tag 2026-05-19_v03 --pilot v03_full_pilot \
  --judges opus --pairs '<see pipeline script>' --workers 1

PYTHONPATH=src python3 -m psycheeval.judge score \
  --tag 2026-05-19_v03 --pilot v03_full_pilot \
  --judges opus --rubric paraphrased_anchored --sample-pct 15 --workers 1
```

### Phase 6 analysis (after all judging completes)
```bash
PYTHONPATH=src python3 -m psycheeval.analyze \
  --tag 2026-05-19_v03 --pilot v03_full_pilot
```

This produces `reports/metrics_2026-05-19_v03.json` with all v0.2 blocks +
4 new v0.3 blocks (D1-D4).

## Quality spot check (verified)

Sampled outputs at ~12% generation completion:
- **C_GENERIC_CONTRACT**: produces direct contract-following responses without referencing user's specific traits ✓
- **C4_WRONG_PROFILE**: follows the donor persona's contract style ✓
- **L1 (PI-only)**: produces measured contract-following responses ✓

Cell counts balanced across all 3 authors.

## Next decisions for user

None blocking. Possible:
1. When to burn next Claude cap on Opus judging (after Opus gen completes ~mid-afternoon)
2. Whether to run human calibration during pipeline run
3. Whether to start v3 blog post draft structure now

## Pipeline monitoring

```bash
cd ~/claudeworkspace/psyche/psycheeval

# Snapshot
echo "outputs: $(wc -l < runs/2026-05-19_v03/assistant_outputs.jsonl)"
echo "scalar:  $(wc -l < runs/2026-05-19_v03/anchored_judge_scores.jsonl 2>/dev/null || echo 0)"
echo "pairwise: $(wc -l < runs/2026-05-19_v03/pairwise_scores.jsonl 2>/dev/null || echo 0)"

# Health
for pid in 3125527 3141240 3144900 3177825; do
  echo "$pid: $(ps -p $pid -o etime,cmd --no-headers 2>/dev/null || echo DEAD)"
done

# Logs
tail -3 logs/v0_3_phase1_codex.log
tail -3 logs/v0_3_phase1_opus_gen.log
tail -3 logs/v03_codex_pipeline.log
tail -3 logs/v03_sentinels.log
```
