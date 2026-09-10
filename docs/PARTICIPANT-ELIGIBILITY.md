# Participant Eligibility — the adults-only research scope

**Date**: 2026-08-15
**Status**: binding. Implemented, not aspirational — the enforcement points are named below.
**Authority**: owner ruling `q-psyche-participants-r2` = A (2026-08-16T00:33Z).
**Companion to**: `docs/ETHICS-PROTOCOL.md` (v1.6), which this document is cited from.

---

## 1. The rule, in one paragraph

**The research set is adults-only. The assessment is not.** Anyone may take the Psyche
Public assessment and receive their results; no age question stands between a visitor
and the test. The eligibility question is asked at one place only — immediately before
the optional research opt-in, at the end, after results have already been shown. A
record enters the research set only if that declaration was made. A record we come to
know is a minor's is removed from the research set and purged, and this document says
exactly what that means.

This scopes **which protocol is being run**. It does not verify anyone's age, and
nothing in this document should be read as claiming otherwise.

## 2. Why the line is drawn here and not at the door

Two earlier decisions constrain this one, and both still stand.

**There is no age gate at the site door** (ruling `q-psyche-age-gate-review` = A,
2026-08-11). A 16+ checkbox once sat at the entrance. It was removed because it was an
unverifiable self-declaration on a site that had just finished promising not to ask for
personal information it did not need — its own copy conceded it was "an honesty gate and
not age verification" — and because the one visitor it was aimed at was the one it
taught to lie on the way in. Nothing here reintroduces it. What replaced it survives
unchanged: a plain statement of who the assessment is written for, and, for a younger
reader, a pointer to a trusted adult and to the crisis services.

**A checkbox does not make an ethics determination cover a population.** This was the
correction that produced the present rule. The first draft of the question framed it as
"add one checkbox"; the review was right that this was too small. A self-declaration
does not by itself make a protocol adult-only. The decision that matters is what happens
to a minor's record — and the application has to implement the answer, which §4 and §5
are.

**The regulatory reason the line exists at all.** The exempt-determination pathway this
project documents (`docs/ETHICS-PROTOCOL.md`, §Exempt Determination Pathway) rests on
45 CFR 46.104(d)(2) — survey and interview research. 45 CFR 46.104(b)(3) limits which
exemptions may be applied to research subject to subpart D, the children provisions:

- the exemptions at (d)(2)(i) and (d)(2)(ii) reach research with children **only** where
  it involves educational tests, or the observation of public behavior where the
  investigator does not participate in the activities being observed; and
- the exemption at (d)(2)(iii) — the limited-IRB-review route, which is the fallback an
  adult protocol would use when identifiable responses are recorded — **may not be
  applied to research with children at all.**

Psyche Public is neither an educational test nor observation of public behavior; the
investigator collects and records the responses. So neither carve-out reaches it, and a
(d)(2) determination premised on adult participation cannot be assumed to cover minors.
Including minors properly is a different protocol — assent, parental permission, waiver
and safeguards — and it is a protocol this project has not written and is not running.

Two honest qualifications. The Common Rule binds federally-funded or
institutionally-engaged research; this project is neither, so 45 CFR 46 is a **voluntary
standard adopted here**, not a jurisdictional obligation — which changes nothing about
the fact that a determination premised on adults cannot silently be stretched over
children. And no Canadian province sets a statutory age for research participation;
TCPS 2 uses a capacity-based model rather than a fixed age. The 18 threshold is
therefore a **choice**, made to match the exemption categories the determination
pathway relies on, not a number read off a statute.

## 3. What is asked, where it lives, and what enforces it

**Asked**: as the opening clause of the level-2 (research) consent, merged into the
consent sentence rather than added as a separate checkbox —

> *I am 18 or older, and I agree for my assessment data to be used in academic research…*

**Why merged.** The consent text is frozen and stored verbatim against the session, so
merging puts the declaration **inside the durable consent record**. A separate transient
checkbox would gate a button and then be stored nowhere. The granularity objection to
bundled consent applies to bundling two *consents*; an eligibility statement is not a
consent, and separating it here would have produced a weaker record, not a
better-informed participant.

**Enforced**, in three places, so that no single one of them is load-bearing alone:

| Where | What it does |
|---|---|
| `api/src/routes/psyche.ts` → `recordConsent` | Refuses (HTTP 400) any level-2 consent whose stored text lacks the declaration, **before** the write. The client sends the consent text, so this — not the checkbox — is the control. Level 1 is untouched: the assessment is not gated. |
| `psyche_sessions.adult_attested` | The machine-readable projection of what the stored text says, written in the same statement. The predicate for "is this row in the research set" must not be a substring match against prose that is expected to be reworded. |
| `psyche_research_set` (SQL view) | The research set, defined once, with withdrawal and exclusion built into the definition rather than reapplied at each call site. |

Reword the declaration in the web copy without moving the server constant and research
opt-in begins failing closed — visibly, which is the correct direction for a consent
gate to break.

## 4. A false declaration

The declaration is unverifiable and is treated as unverifiable. The site cannot check an
age and does not attempt to; there is no identity document, no inference from writing
style, no third-party age-estimation service, and none of these will be added — each
would collect far more than the question is worth, on a site whose entire posture is not
asking for what it does not need.

So the handling rule is not detection. It is this:

1. **A false declaration does not make the record admissible.** Eligibility is a fact
   about the participant, not about the box they ticked. If it becomes known that a
   research record is a minor's, the declaration it carries is irrelevant to what
   happens next — §5 applies in full, exactly as it would if no declaration existed.
2. **A false declaration is not treated as misconduct by the participant.** No
   consequence attaches to the person. The record is removed and that is the end of it.
   A minor who ticked a box to see their personality results has done nothing this
   project intends to punish, and building an adverse process around it would create
   exactly the reason not to come forward that §5 depends on not existing.
3. **The project does not go looking.** There is no scanning of interview text for age
   cues, no profiling of participants against the declaration. Such a search would mean
   reading everyone's answers for a signal about them that they did not offer, which is
   a worse privacy act than the one it aims to remedy. Knowledge arrives the way it
   actually arrives: someone tells us, or a participant says so in their own words.

## 5. A record discovered to be a minor's

Exclusion and purge are **one operation**. There is no state in which a record has been
identified and is still sitting in the database awaiting a decision.

**Command** (the whole procedure — there is no manual variant):

```bash
polaris/tools/vault exec --as aox-production-repair \
  --env CLOUDFLARE_API_TOKEN=cloudflare -- \
  applications/ashitaorbis/scripts/psyche-exclude-minor.sh <session-id> "<basis>" "<ruling-ref>"
```

**What it does, in order:** records the exclusion tombstone *first* (so a crash mid-way
leaves "verify the purge landed", never "data is gone and nothing says why"); deletes the
item responses, the interview text and the model evaluations; nulls the scores, report,
persona, behavioral context and the entire consent record; sets the session status to
`excluded`, which the API treats as dead rather than merely empty; releases any
named-purpose retention hold, because a hold is our reason to keep something and cannot
outlive a record we may not hold at all; then re-reads the database and fails loudly if
anything survived.

**What remains afterwards**, and it is deliberately almost nothing: the random session
id, the timestamps, a short note of **how it came to be known**, and the ruling
authorising the action. No age. No answer, score, report or interview text. Not the
disclosure that prompted the exclusion — the basis field records *that a participant
wrote in*, never *what they wrote*.

**Why keep even that.** A deletion that leaves no trace cannot be audited, and "how many
records have you excluded" is a question an ethics determination asks in that form. The
tombstone answers it with a count instead of a recollection, and it stops the same id
being re-admitted by any later import.

**Withdrawal is unaffected and always faster.** A participant who withdraws deletes their
own record immediately, hold or no hold, without anybody being told why. Nothing in this
document is a precondition for that.

## 6. The legacy cohort — records collected before this rule

A small number of research-consented sessions predate the eligibility declaration. They
carry `adult_attested = NULL`, which means **the question was never put to them** — not
that they answered it badly, and not that anything is known about their age.

**They remain in the research set**, for two reasons. They are not known-minor records,
and §5 is about knowledge, not suspicion. And three of them are held under a named
research purpose by a standing owner ruling (`q-psyche-research-rows` = C, 2026-08-11,
the interview-correlation study); a rule enacted today has no authority to quietly
overturn that.

**They are counted separately and disclosed, not absorbed.**
`applications/ashitaorbis/scripts/check-psyche-retention.sh` reports
`legacy_rows_never_asked` as its own figure, so "how many of your research records carry
an eligibility declaration" always has a truthful answer. Any determination request must
state that this cohort exists and was collected under the pre-amendment protocol. If a
reviewing body wants them out, removing them is §5 applied per session — the machinery
already exists and takes one command each.

## 7. Where this sits among the other 2026-08 decisions

This is the last of the psyche compliance items and is intended to be read with them,
as one adult-protocol package rather than a pile of separate fixes:

| Decision | What it settled |
|---|---|
| `q-psyche-age-gate-review` = A (08-11) | No age gate at the door. Unchanged by this document. |
| `q-psyche-phq9-drop` = A (08-11) | Public battery is PHQ-8; the suicidal-ideation item is not asked, because asking what one cannot act on is collection, not screening. |
| `q-psyche-research-rows` = C (08-11) | Named-purpose retention holds; the three held sessions of §6. |
| `q-psyche-mcp-scored` = A (08-11) | The scored instruments stay off the MCP route — in part because a caller attestation with `verification_method=none` is not a surface that can carry a research consent. The same reasoning applies to an eligibility declaration, and is why §3 is enforced at the level-2 boundary rather than by trusting any client. |
| `q-psyche-retention-copy` = B (08-12) | Retention ladder 7d / 90d / 24mo, plus annual review of every open hold. |
| `q-psyche-pushlock-readme` = A, `q-psyche-public-push-bq275` = A (08-11/12) | The public privacy documents corrected against the live service. |
| **`q-psyche-participants-r2` = A (08-15)** | **This document.** |

Retention, withdrawal, processor disclosure and eligibility now describe the same
system. Where any of them disagrees with the live consent screen, the consent screen is
authoritative and the document is stale.

## 8. What this document does not claim

- It does not claim the assessment is adults-only. It is not, by design.
- It does not claim anyone's age has been verified. Nothing here verifies an age.
- It does not claim an exempt determination has been obtained. The determination is
  still to be sought; this document exists so that what is being determined is stated
  accurately when it is.
- It does not claim the research records are anonymous. They are **session-coded and
  treated as pseudonymous** — a random UUID joins the scores, the written answers and
  the report, and ten open-ended answers are the participant's own words. That framing
  is set by the 2026-08-12 anonymity analysis and is not weakened here.

## 9. Amendment log

| Date | Change |
|---|---|
| 2026-08-15 | Created. Enacts `q-psyche-participants-r2` = A: eligibility declaration merged into the level-2 consent and enforced server-side; `psyche_minor_exclusions` + `psyche_research_set` added; exclusion-and-purge procedure written and implemented; legacy cohort disclosed. |
