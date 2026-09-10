# Fable Follow-up Adversarial Review — 2026-06-11 (redacted public copy)

> **Redaction note**: This is the blind follow-up review (Claude Fable 5) run
> after the GPT-5.5 Pro review fixes landed. The reviewer's verbatim output
> quoted the personal content it found; committing those quotes here would
> re-publish the data the subsequent privacy purge removed, so quotes, real
> names, score values, and history-recovery specifics are redacted in this
> copy. Structure and all findings are otherwise preserved. All P0/P1 findings
> below were remediated at HEAD the same day (see docs/EVOLUTION.md Phase 6);
> history rewrite remains a tracked human action (BACKLOG.md).

---

**Scope**: full working tree + git history. Verified empirically: no hardcoded
secrets anywhere (logs, runs, lockfiles scanned with credential-pattern
regexes), web test suite green (94/94 including the 2026-06-11 security-fix
regressions). The code-level security posture is good. **The privacy posture
is not.** The documentation makes strong privacy claims that the committed
data contradicts. Repo confirmed PUBLIC on GitHub.

## P0 Findings

### P0-1: Real private SMS conversations + the author's full legal name committed at HEAD
`experiments/methodology-supplement/corpus-sample-for-gpt.txt` (41KB,
committed) contained the author's full real name (10 occurrences) and verbatim
private SMS messages with timestamps, including intensely intimate
relationship content ([quotes redacted]). At least one sample appears to be
written by the interlocutor, not the author. Violates the repo's own README
privacy section and the owner's global no-real-names rule.
**Status: file removed at HEAD (2026-06-11).**

### P0-2: The author's real psychometric/mental-health reports committed at HEAD, bypassing the gitignore that classifies them as private
`benchmark/.gitignore` excluded `/reports/` and `judge_results.json` as
"Generated from private profile data" — but the patterns were root-anchored,
so archive copies were committed: `benchmark/archive/2026-04-18-pre-judge-update/reports/*.md`
(8 complete clinical-grade profiles of the author — [details redacted]),
`judge_results.json`, and the top-level `benchmark/report.md` quoted the
author's private interview answers verbatim plus the real ground-truth Big
Five scores. The "archive instead of delete" convention defeated the privacy
gitignore.
**Status: archive reports + judge results removed at HEAD; report.md replaced
with a redacted aggregate-only version; gitignore patterns unanchored.**

### P0-3: "Removed" personal files are fully recoverable from public git history
A prior commit deleted the personal behavioral spec (`profiles/claude-context.md`)
from HEAD — with a commit message documenting exactly why it is sensitive —
but history was never rewritten; the full file (and previously deleted
identified profile JSONs under `web/public/profiles/`) remain recoverable
from public history. [Recovery specifics redacted.]
**Status: open — requires `git filter-repo` + force-push + GitHub cache purge.
Tracked as a human action in BACKLOG.md.**

## P1 Findings

### P1-1: Named third parties with derived personality data committed at HEAD
`analysis/BACKLOG.md` published inferred Big Five scores for two named private
individuals; the privacy denylist in `narrative_llm.py` itself hardcoded the
names plus relational metadata; committed analysis JSONs embedded verbatim
excerpts of an intimate relationship narrative; `analyze_narratives.py`
documented the SMS corpus by contact name. These people presumably never
consented to having personality assessments published about them.
**Status: names structurally removed from docs; narrative JSONs removed at
HEAD; code names externalized to gitignored config/env (`profiles/private-names.txt`,
`PSYCHE_SELF_NAMES`, `PSYCHE_ARCHIVE_CONTACT`); residual first-name run labels
tracked in BACKLOG.md.**

### P1-2: De-anonymization of "blinded" public-figure personas
`psycheeval/.gitignore` claims real anchor names are "kept internal only,
never published," but committed seed-bank and source-packet files carried
`internal_public_anchor` real names inline (four named public figures),
violating the data's own `anchor_family_only` policy field, while
`LICENSE-DATA` (CC-BY-4.0) asserts the aliases are not the real figures.
**Status: anchor fields nulled in committed data; explicit names redacted from
prompts/docs. Inherent residual: alias names and source-packet
descriptions/URLs still evoke the real figures by construction — disposition
of the public-inspired datasets is an owner decision (BACKLOG.md).**

### P1-3: Ethics protocol stale against the deployed system
`docs/ETHICS-PROTOCOL.md` (v1.2) stated the report model is "DeepSeek V3.2"
and "No IP addresses logged"; production switched to Kimi K2.5 on 2026-03-19
and Cloudflare processes IPs. If the live consent screen tracks this document,
consent is factually inaccurate.
**Status: protocol amended to v1.3 (current model, accurate IP statement,
explicit note that the live consent screen must name the current model).**

## P2 / Notes

- **Instrument licensing**: the repo MIT-licenses full item text for ~39
  instruments; several (e.g., MAAS, Frost MPS, ZTPI, SD3, HEXACO-200) carry
  research-only or permission-required redistribution terms. **Status: open,
  tracked in BACKLOG.md.**
- **Shell convention**: several `psycheeval/drivers/*.sh` scripts lack
  `set -euo pipefail` (local-only impact). **Status: noted, not changed —
  historical driver scripts; behavior change risk outweighs benefit.**
- **Cross-repo prompt-sync claim** (benchmark `SYSTEM_PROMPT` vs `psyche.ts`):
  unverifiable from this clone; unchecked invariant.

## What held up under adversarial scrutiny

- No credentials anywhere (including a log file whose name suggested a leaked
  key — error spam only).
- Web app: no `dangerouslySetInnerHTML`/`innerHTML`/`eval`; only same-origin
  fetches; the store import path is genuinely hardened (atomic validation,
  per-item range checks, unknown-instrument drops, prototype-pollution-safe);
  `recover.html` avoids dumping raw blobs and warns before clipboard writes.
  The 2026-06-11 fix claims (reverse-keyed CAT scoring, bank validation,
  exact-coverage auto-scoring) are backed by 29 passing regression tests;
  full suite 94/94 green.
- README's privacy section is unusually honest about the Cloudflare-IP and
  DeepInfra-egress boundaries.

## Bottom line (as found)

The *code* is in good shape; the **repository contents were the
vulnerability**. The highest-priority action was a coordinated purge of the
personal-data files plus a git history rewrite. The purge landed at HEAD on
2026-06-11; the history rewrite is pending owner action.
