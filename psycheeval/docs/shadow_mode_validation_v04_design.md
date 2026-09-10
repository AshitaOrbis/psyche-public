# Shadow-Mode Validation Design (v0.4)

**Phase 9.1 deliverable per v0.3 plan §5**. Concrete design for executing real-user construct-validity validation of PsycheEval's profile-conditioning effects at the Psyche public results page (`app.ashitaorbis.com/psyche`).

**Date**: 2026-05-19 (initial draft)
**Status**: Draft. Pre-registered predictions (§7) await v0.3 LLM-judge analysis results.
**Decision basis**: Phase -1 (D4 = Psyche public results page, approved 2026-05-19).

## 1. Why this exists

v0.3 measures whether **LLM judges** prefer profile-conditioned responses over generic responses. The deepest unresolved question from v0.2's external reviewers is whether **real users** would prefer the same responses. v0.3 cannot answer that question — synthetic personas + LLM judges form a closed loop. Shadow-mode validation is the construct-validity bridge.

**Goal of v0.4 shadow-mode**: collect real-user engagement signal on profile-conditioned vs generic responses, on real Psyche assessment-takers, and compare the result against v0.3's pre-registered predictions.

**Pre-registration matters because**: if v0.4 engagement gaps match v0.3 LLM-judge predictions, we have construct-validity evidence. If they don't, we have a published negative result with quantified divergence. Both outcomes are scientifically informative; only the pre-registration distinguishes confirmation from data-mining.

## 2. Context: the Psyche public results page

`app.ashitaorbis.com/psyche` currently does the following:
1. Visitor takes a personality assessment (39-instrument battery).
2. Backend (`applications/ashitaorbis/api/src/routes/psyche.ts`) calls Kimi K2.5 via DeepInfra to generate a multi-section narrative report.
3. Report is displayed; visitor can re-read, save, share.
4. No follow-up conversation interface currently exists.

**Shadow-mode adds a "follow-up question" interface** to the results page. The user types a follow-up; the backend generates a response in one of two arms (profile-conditioned vs generic); routing logic chooses the arm; engagement events are logged.

## 3. UI delta

### 3.1 Existing results-page layout (no changes)
- Profile summary panel
- Trait-by-trait narrative sections
- Reading guide / how-to-interpret notes

### 3.2 New "Ask a follow-up question" panel (below existing report)

```
+-------------------------------------------------+
| Want to dig deeper?                             |
|                                                 |
| Ask a follow-up question about your profile,    |
| specific scenarios, or how this might apply     |
| to a situation you are navigating.              |
|                                                 |
|  +------------------------------------------+   |
|  | [text input, 3-line textarea]            |   |
|  +------------------------------------------+   |
|                                                 |
|  [ Submit ]                                     |
|                                                 |
| --- --- --- --- --- --- --- --- --- --- --- -- |
| Disclosure: follow-up responses are part of    |
| an ongoing methodology study; aggregate         |
| engagement data is anonymized.                  |
+-------------------------------------------------+
```

### 3.3 Response display

Once the user submits, a response area expands below the textarea:

```
+-------------------------------------------------+
|  Response                                       |
|                                                 |
|  [rendered markdown response, ~500-1000 chars]  |
|                                                 |
|  Was this useful?                               |
|  [ thumbs-up ] [ thumbs-down ]                  |
|                                                 |
|  [ Ask another question ]                       |
+-------------------------------------------------+
```

### 3.4 Visual + UX notes

- Disclosure copy is small-font, not modal-blocking. The user has already accepted the assessment terms; this is a continuation, not a new consent flow.
- Thumbs are optional. Skip is a valid path.
- "Ask another question" reveals a new textarea below (multi-turn in-page).

## 4. Routing logic

```
# pseudocode for psyche.ts /api/psyche/follow-up handler
def handle_follow_up(session_id, question, user_profile):
    # Deterministic per-session arm assignment (stable user experience
    # within a session; randomized across sessions).
    arm = "RESULTS_CONTRACT" if hash(session_id) % 2 == 0 else "RESULTS_GENERIC"

    if arm == "RESULTS_CONTRACT":
        contract_text = build_c4_style_contract(user_profile)
        prompt = compose_with_contract(contract_text, question)
    else:
        prompt = compose_generic(question)  # no profile injection

    response = call_kimi(prompt)

    log_event("follow_up_routed", session_id=session_id, arm=arm,
              question_chars=len(question), response_chars=len(response))

    return {"response": response, "arm": arm}  # arm NOT shown to user
```

**Key design points**:
- **Per-session deterministic assignment**: 3 follow-ups in one session = same arm. Avoids within-session oscillation.
- **50/50 split**: equal sample sizes per arm.
- **No user-visible signal of arm**: prevents response-style as a confound.
- **Arm logged server-side only**: blinding preserved.

## 5. Engagement instrumentation

### 5.1 Event schema

| Event | Triggered when | Captured fields |
|-------|----------------|-----------------|
| `report_viewed` | results page loads | session_id, visitor_id, timestamp, profile_hash |
| `follow_up_rendered` | follow-up panel becomes visible | session_id, scroll_depth_pct |
| `follow_up_submitted` | user clicks Submit | session_id, question_chars, time_to_submit_seconds |
| `follow_up_routed` | backend selects arm | session_id, arm, model_id, latency_ms |
| `follow_up_response_shown` | response renders | session_id, response_chars, time_to_render_ms |
| `follow_up_response_thumbs` | user clicks thumbs | session_id, thumbs_direction |
| `follow_up_next_clicked` | user clicks "Ask another question" | session_id, time_since_response_seconds |
| `follow_up_copied` | user copies response text | session_id, response_chars |
| `follow_up_shared` | user shares response | session_id, share_target |
| `session_ended` | tab closed or session timeout | session_id, total_time_on_page_seconds |

### 5.2 Primary engagement metric

**Composite: `engagement_score`** per session = weighted combination of:
- Submitted at least one follow-up: 1.0 weight
- Submitted >=2 follow-ups (multi-turn engagement): +1.0 weight
- Explicit thumbs-up on at least one response: +0.5 weight
- Copied or shared at least one response: +0.5 weight
- Time-on-page > 5 minutes: +0.5 weight

Range: 0.0 (saw report only) to 3.5 (highly engaged user).

**Per-arm metric**: mean(engagement_score) across all sessions in that arm.

### 5.3 Secondary metrics

- Follow-up submission rate per session (proportion submitting >=1)
- Thumbs-up / thumbs-down ratio per arm
- Mean time-to-second-submission (engagement depth proxy)
- Copy / share rate per arm

## 6. Power analysis

**Assumptions** (to refine with pilot data):
- Baseline engagement_score under generic arm: mean 1.2, sigma ~ 1.0
- Detect +/-0.2 effect (about a 15% effect on the composite metric)

**Sample size**:
- For Cohen's d = 0.2, alpha=0.05, beta=0.20: n = 393 per arm (786 total)
- For Cohen's d = 0.3, same params: n = 175 per arm (350 total)

**v0.4 target**: 400 sessions per arm (800 total). At current Psyche assessment-taker traffic of ~5-10/day, that's 4-8 months of data collection. Plan accordingly.

**Stopping rules**:
- Pre-specified n=800 cumulative; analyze at that point.
- Safety stop: if either arm shows >2 sigma deviation from steady-state baseline (e.g., response generation broken in one arm), pause routing and investigate.

## 7. Pre-registered predictions (PLACEHOLDERS — fill after v0.3 analysis)

These predictions lock before v0.4 routing begins. They are the construct-validity test: if v0.3 LLM-judge findings predict the engagement gap correctly, the LLM-judge metric has external validity. If not, the gap |predicted - observed| is the construct-validity divergence.

### 7.1 Primary prediction
> Profile-conditioned arm (`RESULTS_CONTRACT`) will produce an engagement_score mean **{X}** higher than generic arm (`RESULTS_GENERIC`).
>
> **X = TBD; derived from v0.3 C_GENERIC_CONTRACT vs C4 controlled lo_win rate.**
>
> Specifically: if v0.3 finds C4 (profile-specific) beats C_GENERIC (no profile) at p% controlled lo_win, this implies a (p - 50)/100 * engagement_scale_factor effect. We commit to scale factor **0.04** (a 60% LLM-judge win rate translates to a 0.4 engagement_score difference) — chosen conservatively based on prior LLM-judge / real-user comparison literature.

### 7.2 Secondary predictions
- Thumbs-up rate will be higher in profile-conditioned arm by **{Y}** percentage points
- Multi-turn rate (>=2 follow-ups) will be higher in profile-conditioned arm by **{Z}** percentage points
- Time-on-response will be higher in profile-conditioned arm (specific magnitude TBD)

### 7.3 Direction-only predictions
- Profile-conditioned arm shows stronger directional engagement (mean > 0 effect)
- The effect is present across persona-type subgroups (PI personas vs PS personas)

### 7.4 Falsification conditions
The construct-validity claim is **falsified** if any of:
- Observed engagement gap is in the opposite direction
- Observed gap > 2x predicted magnitude (LLM judges drastically under-predicted)
- Observed gap < 0.5x predicted magnitude (LLM judges drastically over-predicted)

A gap within 0.5x-2x predicted is consistent with construct validity at the chosen scale factor.

## 8. Consent and privacy

### 8.1 Disclosure
Inline at the follow-up panel:
> Follow-up responses are part of an ongoing methodology study; aggregate engagement data is anonymized.

### 8.2 Privacy-preserving choices
- No raw question text stored long-term beyond what's needed for response generation
- No PII collected beyond what the original Psyche assessment already collected
- Aggregate engagement metrics published; per-session data is internal
- Session-level data retention: 90 days, then aggregated

### 8.3 Existing terms
The current Psyche assessment terms cover analytics on results-page activity. This methodology study is within scope; no new consent flow required, but the inline disclosure makes the research framing explicit.

## 9. Implementation diff against `psyche.ts`

**Files to modify** (rough sketch):
- `applications/ashitaorbis/api/src/routes/psyche.ts` — add `/api/psyche/follow-up` handler (~80 lines)
- `applications/ashitaorbis/tier-3-nextjs/app/psyche/results/page.tsx` — add follow-up UI panel (~60 lines)
- `applications/ashitaorbis/api/src/lib/contract-builder.ts` — NEW; `build_c4_style_contract(user_profile)` (~40 lines)
- `applications/ashitaorbis/api/src/lib/event-logger.ts` — extend with new event types (~30 lines)
- `applications/ashitaorbis/shared/instrumentation/schema.ts` — new event schemas (~50 lines)

**Total**: ~260 lines of new application code + ~50 lines of schema/config. ~2-3 days of focused implementation work for someone familiar with the codebase.

## 10. v0.4 execution plan

| Step | Owner | When |
|------|-------|------|
| Implement UI + backend changes | Author | v0.4 Phase A (3 days) |
| Internal smoke test (author-only routing) | Author | v0.4 Phase B (1 day) |
| Public launch with feature flag enabled for 100% of new sessions | Author | v0.4 Phase C |
| Collect ~800 sessions of routed data | Time | v0.4 Phase D (~4-8 months) |
| Pre-registered analysis | Author | v0.4 Phase E (1 week) |
| Curated v0.4 report + blog post | Author + reviewers | v0.4 Phase F (2-3 weeks) |

## 11. What this design does NOT do

- **Does not bridge to non-Psyche users**: only people who completed the assessment are routed. Generalizing to non-assessment users is a v0.5+ question.
- **Does not test prompt variations**: the profile-conditioned arm uses one fixed contract style (C4-equivalent). Variations require additional arms and bigger sample sizes.
- **Does not measure long-term retention**: the engagement metric is within-session. Multi-session retention is a v0.5+ question.
- **Does not test agent-mediated workflows**: only direct chat. Workflows where Psyche profile feeds into another product surface are out of scope here.

## 12. Open design questions

These should resolve before v0.4 implementation begins:

1. **Tie-breaking when v0.3 predictions are null**: if v0.3 finds C_GENERIC ~= C4 (no detected preference), what does the pre-registered prediction say? Probably: "engagement gap < 0.1 with 90% confidence" — a tighter null prediction than equivalence.
2. **Multi-turn assignment**: a user who returns in a new session: same arm or re-randomized? Recommendation: re-randomize, since the analysis unit is the session.
3. **Adversarial follow-ups**: if a user submits hostile or harmful content, what happens? Both arms refuse identically; routing must not affect safety behavior.
4. **Model upgrade during v0.4**: if Kimi K2.6 or similar lands mid-collection, do we keep the original model fixed or upgrade? Recommendation: fix the model at v0.4 launch and document model_id in every routed_response event. Re-run v0.4 if model changes during collection.

## 13. Connection to v0.3 findings

This design assumes v0.3 produces findings of the form:
- C_GENERIC vs C4: controlled lo_win rate X% -> predicts engagement gap
- C5_NONPUBLIC_CONTRACT vs C5_CONTRACT: controlled lo_win rate Y% -> predicts secondary engagement gap
- T2 ladder: marginal contribution of each component -> predicts incremental engagement gains

If v0.3 finds null effects across the board (no detected preferences), the v0.4 shadow-mode test becomes a falsification test for v0.3 methodology itself: if v0.4 finds clear engagement gaps where v0.3 found none, the LLM-judge metric is missing something real users notice.

If v0.3 finds strong directional effects, v0.4 tests whether those effects translate to engagement.

Either outcome is publishable.

## 14. Sign-off

When v0.3 analysis is complete:
- [ ] Fill in §7 pre-registered predictions with specific magnitudes
- [ ] Lock the design (no changes after this point)
- [ ] Begin v0.4 implementation
