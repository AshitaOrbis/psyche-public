# v0.3 Status — 2026-06-16: Path A complete, opus 4.7-clean, Phase 6 analyzed

## TL;DR
Path A (pool v0.2 corpus + fill all 28 cross-condition pair types) is **complete**.
The Opus-4.8 contamination was caught, fixed, and the June opus pairwise records
regenerated on pinned **Opus 4.7**. Phase 6 analysis ran clean. All four v0.3
mechanism questions have answers.

## Corpus (canonical metrics: reports/metrics_2026-05-19_v03.json, 2.4 MB)
- assistant_outputs: 2,757 (v0.3 7 conditions + pooled v0.2 8 conditions, 80 scenarios, 8 personas, 3 authors)
- anchored scalar: 7,180
- pairwise (forced + swap): 14,733 records
- All 3 judges (gpt-5.4, gpt-5.5-xhigh, **opus = 4.7**) across all 26 design-lock pair types
- v0.3 analyzer blocks D1 / D2 / D3 / D4 all populated

## Model-version integrity (the 2026-06-16 fix)
- The bare `opus` CLI alias rolled to Opus 4.8 in early June. ~4,476 June-timestamped
  opus pairwise records were 4.8-contaminated.
- Fix (commit bf70b28): `ModelSpec.cli_model` override — CLI invokes `claude-opus-4-7`
  while records stay labelled `opus`. Verified live (self-reports 4.7).
- June opus pairwise purged (archived: `runs/2026-05-19_v03/archive_2026-06-16_pre_opus48_purge/`
  with MANIFEST) and regenerated on 4.7.
- Opus scalar + all sentinels (D1/D4/D2) were already May-only → clean 4.7. Verified.
- **Entire opus corpus is now uniformly 4.7.** Zero duplicate pairwise keys (verified).

## Headline mechanism findings (cross-provider, same-author, AB/BA position-controlled, cluster-bootstrap CIs)

### Q1 — Does profile *specificity* matter vs a generic contract?
- C3 > C_GENERIC: 57.1% [Wilson 51.6–62.4]  ·  C4 > C_GENERIC: 58.8% [53.3–64.1]
- C5 vs C_GENERIC: 53.1% [45.4–60.7] — CI straddles 0.5 (no reliable difference)
- C_GENERIC > C0 baseline: 65.6%
- **Answer: profile specificity adds a modest, reliable edge over a generic contract (C3/C4 ~57–59%); a generic contract alone still strongly beats no-profile.**

### Q2 — Does profile *matching* matter (right person vs wrong person)?
- C3 > C4_WRONG: 63.2% [57.8–68.3]  ·  C4 > C4_WRONG: 61.2% [55.7–66.4]
- C4_WRONG > C0 baseline: 61.5%
- **Answer: matching matters (~61–63% right-over-wrong), BUT a wrong profile still beats no-profile (61.5%) — part of the benefit is structural (having a contract at all), not matching-specific.**

### Q3 — Public-anchor isolation (C5_NONPUBLIC vs C5, PI-matched, trait pattern held constant)
- C5 > C5_NONPUBLIC: 62.0% [54.3–69.2]
- C5_CONTRACT > C5_NONPUBLIC_CONTRACT: 62.0% [54.3–69.2] (public anchor still helps with contract held constant)
- adding a contract to the nonpublic packet (C5_NONPUBLIC → C5_NONPUBLIC_CONTRACT): 71.1%
- **Answer: the public-anchor narrative form carries a real ~62% advantage over a trait-matched nonpublic packet — a genuine public-anchor effect distinct from narrative form. New v0.3 finding.**

### Q4 — C5_CONTRACT ablation ladder (L0=C5 → L1 → L2 → L3 → L4=C5_CONTRACT)
- L0→L1 (contract presence): 52.5% [44.8–60.1] — straddles, ≈ null
- L1→L2 (anti-mimicry): 48.4% [40.7–56.2] — straddles, ≈ null
- L2→L3 (contract-first ordering): **L3 wins 69.7%** [Wilson 62.0–76.4]
- **Answer: essentially all the detectable C5_CONTRACT package benefit localizes to the contract-first ORDERING step (L2→L3 ~70%); contract presence and anti-mimicry are individually undetectable.**

## Caveats for the v0.3 report
- Numbers above are AB/BA position-controlled cross-provider same-author. Forced-choice + sentinel reconciliation per analyzer blocks.
- **Opus sentinel coverage gap**: D1 (53) / D4 (41) opus sentinel records were sampled from the *original* small opus pairwise pool (the 3 within-new pairs only), so opus-side position-bias/tie decomposition does not cover the new cross-condition pairs. Codex sentinels cover the full pool. Optional v0.3 follow-up: re-sample opus D1/D4 across the full pool (~small cost). Flagged, not yet done.

## Next (Phase 7+)
- Curate report from skeleton (reports/psycheeval_v0_3_skeleton.md) using these numbers + claim ledger
- Phase 5 human-rater sanity check (toolkit ready; select_human_rater_pairs.py now has a full pool to sample from)
- /publication-review, then v3 blog post (post 047) per plan §8
