# Archive: pre-opus-4.8-purge (2026-06-16)

## Reason
The bare `opus` CLI alias rolled to Opus 4.8 in 2026-06. Opus pairwise
records with judged_at >= 2026-06-01 were generated on 4.8, contaminating
the 4.7 dataset. User decision (2026-06-16): regenerate June opus pairwise
on pinned 4.7 (claude-opus-4-7).

## What this archive contains
Full pairwise_scores.jsonl + pairwise_swap_scores.jsonl BEFORE the June-opus
purge. Codex records and May opus records are unchanged in the live files;
only opus records with judged_at >= 2026-06-01 were removed from the live
files and will be regenerated on 4.7.

## Cut rule
Removed from live: judge_model=="opus" AND judged_at >= "2026-06-01".
Kept in live: all codex records; opus records with judged_at < "2026-06-01".

## Provenance note
Records do not store the CLI-resolved version (judge_model="opus" for both
4.7 and 4.8). The June-boundary cut rests on the project CLAUDE.md anchor
"as of 2026-06 [opus] resolves to Opus 4.8". May opus records are assumed
4.7 per user decision; exact rollover date not empirically recoverable.
