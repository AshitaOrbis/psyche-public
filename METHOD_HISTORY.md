# Method History

This repository is published as a **single-snapshot public tree**: one root commit, no
development ancestry. The project's working history contains private material (the author's own
assessment data was the original test corpus) and is retained privately; what is public is the
method. This file preserves the method's evolution so that the snapshot does not orphan it.
In-tree deep dives are linked at each stage.

## 1. Instrument battery (early phase)

The project began as a web battery of validated public-domain psychometric instruments —
ultimately up to 39 instruments across four tiers (Lite → Standard → Standard+ → Deep), spanning
Big Five (IPIP-NEO facets), HEXACO, values (PVQ), interests (RIASEC), cognition (CRT, NFC),
affect and clinical screeners. Scoring, norms, and percentile mapping live in the web app
(`web/`); licensing and provenance for every instrument in `LICENSES/THIRD-PARTY-INSTRUMENTS.md`.

## 2. Corpus triangulation (`analysis/`)

The second axis: profile synthesis by triangulating instrument self-report with LLM-based
analysis of a longitudinal writing corpus. The `analysis/` package implements corpus ingestion,
diversity sampling, lexical baselines (Empath), and LLM analysis passes, with the synthesis
design documented in `docs/VALIDATION-DESIGN.md` and `docs/EVOLUTION.md`.

## 3. Adversarial review discipline (`docs/`, `reviews/`)

Profiles are treated as claims, not oracles: an adversarial review framework
(`docs/FABLE-REVIEW-FRAMEWORK.md`) subjects generated profiles to blind re-derivation and
claim-level audit by independent models, with probe-validated corrections winning over
generation-time output. Review artifacts from this process are in `reviews/` and
`docs/reviews/`. The ethics posture for assessment content is in `docs/ETHICS-PROTOCOL.md`.

## 4. Model benchmark (`benchmark/`)

A dual-judge benchmark comparing LLMs on personality-report quality (prediction accuracy
against instrument ground truth, evidence use, insight, safety). Public results are aggregate
and non-personal; safety validation uses three fully synthetic stress-test profiles
(clinical-edge, aggressive-conflict, religious-intensity) in `benchmark/synthetic/`.

## 5. psycheeval (current phase)

The largest component: a standing evaluation harness for LLM personality-assessment quality —
preregistered designs, blinded multi-judge scoring, context-contamination controls
(`docs/reviews/context-contamination-audit-2026-06-09.md`), and phased studies with
archetype-keyed synthetic subjects. See `psycheeval/PLAN.md` and `psycheeval/docs/`.

## 6. Hosted deployment (`web/`)

The Lite battery runs in-browser at [app.ashitaorbis.com/psyche](https://app.ashitaorbis.com/psyche)
with a no-backend privacy model (localStorage only; report generation is the single flow where
data leaves the browser). See `README.md` for the full privacy statement.

## Why a snapshot

Earlier public history of this project was retired after a privacy review: the development
history interleaved real assessment data with the method. Rather than publish a scrubbed
ancestry whose cleanliness could never be fully proven, the project publishes a verified clean
tree and keeps its history private. The method above is the part that was always meant to be
public.
