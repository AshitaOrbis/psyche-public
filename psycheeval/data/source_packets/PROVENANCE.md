# Source packets: provenance note

**Written**: 2026-11-22
**Applies to**: the four raw source caches in this directory (`dario_armadillo_raw.jsonl`,
`emily_blender_raw.jsonl`, `pawl_gram_raw.jsonl`, `slalom_altar_raw.jsonl`) and the four
packet files built from them: `source_packets.jsonl` in `data/micro_pilot/`,
`data/micro_pilot_kimi/`, `data/v02_hard_pilot/` and `data/v03_full_pilot/` (the same four
packets in each, 16 in all).

## The files say `high`; by this project's own rule the packets are `low`

Every packet in those files carries `source_grounding: "high"`. That label, and the source
lists behind it, are exactly as the source-hunt run of 2026-04-20 wrote them. By the
project's own definition the grounding of these four packets is **low**:

- **How the source lists were written.** `src/psycheeval/source_hunt.py` was run with
  `--fallback-only`, which skips any retrieved cache and asks GPT-5.4, for each public
  figure, for a list of representative public material, with a URL only where the model
  knows a real one (the "high-level public reputation" fallback). The model wrote all 28
  entries in the four caches. No retrieval run produced them and none is recorded: each row
  holds only `url`, `source_type`, `short_description` and `representative_excerpt`, with no
  fetched URL, retrieval time or content hash.
- **What the project's rule says.** `PLAN.md` §2.4 has a researcher run gather the sources
  first, and says a packet that falls back to high-level public reputation is flagged
  `source_grounding: "low"`, with its results reported separately; it lists "pure background
  knowledge with no retrieval" among the rejected alternatives. The module docstring of
  `source_hunt.py` says the same of the fallback path. The code of that date did not enforce
  it: it kept the label the ingestion step returned, or else counted non-empty URLs, and so
  these packets were labelled high.
- **The URLs are real.** All 28 were checked on 2026-11-22. 25 served their page, and none
  returned not-found. The other 3 (two publications identified by DOI and one U.S. Senate PDF)
  refused the automated request with HTTP 403; both DOIs are registered and resolve to those
  publishers' pages, and the PDF has a web-archive copy captured on 2026-11-14 with status 200.

## Why the files are kept as they are

In v0.1, v0.2 and v0.3, the public-anchor C5 conditions, and the variants built from those
packets, ran on these four packets (v0.3's `C5_NONPUBLIC` controls used separate fictional
packets instead). Rewriting the label would change files those results
cite and overwrite the record of what the April run produced, so the files keep their bytes
and this note carries the correction: read `high` in them as `low`. No finding has been shown
wrong by this. The design table of the v0.1 report
(`reports/psycheeval_v0_1_micro_pilot_2026-04-20_micro.md`, and its two archived copies)
carries the same correction.
