# Psyche Public — Ethics Protocol

**Date**: 2026-03-08 (amended 2026-03-09, 2026-03-09, 2026-06-11)
**Version**: 1.6 — 2026-08-15 amendment, two changes shipping together. (a) **Zero data retention is now pinned** on the report/persona route (`provider.zdr = true`, owner rulings `q-luna-zdr-adopt` = A and `q-psyche-provider-zdr` = A) — it had been ruled twice and implemented nowhere, so participants' written answers had been reaching the serving provider under default retention; every claim surface that said the pin was absent is corrected with it, not before it. (b) The research set is scoped to **adults only** (owner ruling `q-psyche-participants-r2` = A). Eligibility is declared in the level-2 consent and enforced server-side; the assessment itself remains open to everyone and gains no gate. Handling of false declarations and of any record discovered to be a minor's is written out in `docs/PARTICIPANT-ELIGIBILITY.md`, which this document now cites. Prior: 1.5 — 2026-08-12 amendment: corrected the report model and processor throughout (Kimi K2.5 / DeepInfra -> **GPT-5.6 Luna (OpenAI), served through OpenRouter, United States**), which this document had continued to assert after the production switch. Prior: 1.4 (2026-08-11, named-purpose retention holds); 1.3 (2026-06-11, DeepSeek V3.2 -> Kimi K2.5 and the IP-address distinction between application-level logging and hosting-provider request processing). The live consent screen is the authoritative statement of the current model; this document tracks it and is stale whenever they disagree.
**Principal Investigator**: Ashita Orbis (independent researcher, Canada-based)

## Purpose

This document establishes the ethics protocol for the Psyche Public personality assessment tool, deployed at `app.ashitaorbis.com/psyche`. It is intended to serve as contemporaneous documentation for a future IRB exempt determination under 45 CFR 46.104(d)(2).

## Study Description

Psyche Public is a personality assessment that combines 15 validated psychometric instruments (~260 items) with 10 open-ended interview questions. It is accessible through two pathways:

1. **Website-only flow** (`app.ashitaorbis.com/psyche`): User completes consent, instruments, and interview on the website. An AI model (GPT-5.6 Luna, an OpenAI model served through OpenRouter, US; Kimi K2.5 via DeepInfra before the 2026-08 switch; DeepSeek V3.2 before 2026-03-19) generates narrative personality reports.
2. **MCP hybrid flow**: User conducts the interview conversationally with Claude (via MCP connector on claude.ai), then completes quantitative instruments on the website. Claude generates the narrative report using the user's own subscription — no third-party AI processing of interview text.

The research component studies whether AI models can accurately interpret personality from text by comparing model-generated trait predictions against psychometric ground truth (validated instrument scores).

## Anonymization Approach

**No identifiers are collected at any point:**
- No IP addresses logged by the application. (The hosting/edge provider, Cloudflare, transiently processes standard request metadata — including IP addresses — to serve requests, as for any hosted site. The application never stores or links this metadata to session data.)
- No user accounts or authentication
- No cookies or browser fingerprinting
- No device identifiers
- No cross-session identifiers
- Sessions identified only by UUID v4 (122 bits entropy)

**Data stored per session:**
- Psychometric scale scores (aggregated, not individual items, unless research consent given)
- Interview text responses (10 prompts)
- AI-generated report text
- Session metadata (created_at, source, consent level)

**Individual item responses** (per-question answers) are stored only if the participant explicitly opts in to research contribution (Level 2 consent).

## Consent Design

### Level 1 — Pre-assessment (required to use the tool)

Presented before any data collection begins. Covers:
- Not a clinical assessment or diagnosis
- Anonymous: no IP, no account, no device ID, no cookies
- Interview text transferred to and processed by a named third-party model, with **zero data retention pinned** so the text is retained at neither hop (specific model, route and provider disclosed). Session data is stored in the United States; report-generation endpoints are published in more than one region and no region is pinned — see Cross-Border Data Transfer
- Session data stored on US-based servers (Cloudflare) for 7 days, then deleted
- Scores computed in browser
- Written for adults, with no age gate: the site cannot verify age, and asking for a
  self-declaration it could not check bought nothing while costing the one visitor it was
  aimed at a reason to lie on the way in (removed 2026-08-11, owner ruling
  q-psyche-age-gate-review). The screening-questions box states the intended audience and
  points a younger reader to a trusted adult and to the crisis services.

Checkbox: "I understand and want to proceed"

### Level 2 — Post-results research opt-in (optional)

Presented AFTER the participant has seen their results (evidence-based timing: users are engaged post-completion, not fatigued by pre-task wall). Design principles:

1. Lead with the research question, not data request
2. Make anonymity concrete with specific examples
3. Emphasize user control (results already visible)
4. Broad consent language covering future studies
5. Withdrawal mechanism explained
6. No dark patterns: unchecked by default, equal button prominence

7. **Adults only, declared here and nowhere else** (2026-08-15, owner ruling `q-psyche-participants-r2` = A). The consent sentence opens "I am 18 or older, and I agree…". The declaration is merged into the consent text rather than presented as a second checkbox, so that it lands inside the frozen per-session consent record instead of gating a button and being stored nowhere; an eligibility statement is not a consent, so the granularity objection to bundled consent does not apply. It is enforced at the API — a level-2 consent whose stored text lacks the clause is refused before it is written — and the resulting flag, not a substring match against prose, is what defines the research set. **Level 1 is deliberately untouched: the assessment is open to everyone and acquires no age gate.** Scope, the regulatory basis (45 CFR 46.104(b)(3)), the handling of false declarations, the exclusion-and-purge procedure for a record discovered to be a minor's, and the pre-amendment legacy cohort: `docs/PARTICIPANT-ELIGIBILITY.md`.

Language: "I am 18 or older, and I agree for my scale scores, my written interview answers, and my individual per-item answers to be used in academic research on AI and personality assessment, including future studies." (Before 2026-08-15 the sentence opened at "I agree"; earlier still it said "anonymized", which the 2026-08-12 anonymity analysis retired — the records are session-coded and treated as pseudonymous.)

### MCP Consent Pathway

For users who access Psyche through the Claude MCP integration, consent is obtained in two stages across two interfaces:

**Level 1 — Conversational consent (via Claude):**

The MCP tool description (`take_psyche_interview`) instructs Claude to present the full consent terms before starting the interview. Claude must:
1. Disclose that this is not a clinical assessment or diagnosis
2. Explain anonymization (no IP, account, device ID, or cookies collected)
3. State that interview text will be stored on US-based servers (Cloudflare) and deleted 7 days later unless the user asks sooner, and that **no psychometric scales are administered on this route**. (Until 2026-08-11 this step read "psychometric scores will be computed in the user's browser." The scales are website-only for the reasons in "Why the scored instruments are website-only" below — the location of the scoring arithmetic is not one of them. The shipped tool text is in the `take_psyche_interview` description.)
4. Obtain explicit confirmation of understanding (no age confirmation is asked for — see the
   age note below)
5. Remind the user not to include personally identifying information in responses

Claude does not proceed until the user confirms. The record written to the API is deliberately NOT phrased as user consent, because on this route the server cannot observe the user: it is stored as a CALLER ATTESTATION carrying `verification_method=none` and a disclosure version, stating what the calling MCP client asserted it showed and was told. The earlier wording ("User confirmed understanding that … user is 16 or older") was written by the worker regardless of what any human did — a bare HTTP client with no user produced three such records in seconds on 2026-08-10 — and was replaced along with the age assertion.

This conversational consent is substantively equivalent to the web checkbox consent. The same disclosures are presented; the mechanism differs (conversational confirmation vs. checkbox + button). The consent text is frozen and stored in the database identically to web consent.

**Level 2 — Research opt-in (on website):**

After the MCP user completes instruments on the website and reaches the results phase, the same Level 2 research opt-in component is displayed. This is identical to the web-only flow: unchecked checkbox, equal button prominence for "Contribute to Research" and "No Thanks." The MCP flow does not bypass or alter the Level 2 consent experience.

### Report Generation Privacy — MCP vs. Web

| Aspect | Web-only flow | MCP hybrid flow |
|--------|--------------|-----------------|
| Interview text processing | GPT-5.6 Luna, served through OpenRouter (US) | Claude (Anthropic, user's own subscription) |
| Third-party AI access | Yes (OpenRouter, and onward to its serving provider). **Zero data retention is pinned** (`provider.zdr = true`, owner rulings `q-luna-zdr-adopt` = A and `q-psyche-provider-zdr` = A), which restricts routing to endpoints retaining neither prompt nor completion — for this model, Microsoft Azure. Content is not retained at either hop; billing and abuse-prevention metadata is. | No |
| Report storage | Database (Cloudflare D1) | Conversation context only |
| Privacy posture | Disclosed in L1 consent | Equivalent or stronger (no third-party AI) |

In the MCP flow, interview text is processed only by Claude using the user's own subscription. It is not sent to OpenRouter or any third-party model. The consent disclosure for web users explicitly names the report model and OpenRouter because that flow does involve third-party processing; this disclosure does not apply to MCP users. (The disclosure must track the current production model — GPT-5.6 Luna through OpenRouter since the 2026-08 switch.) The MCP consent text omits the OpenRouter reference because it is not applicable.

### Why the Scored Instruments Are Website-Only

The MCP route administers the ten open-ended interview questions and nothing else; the scored instruments are available only on the website. The split was reaffirmed on 2026-08-11, and its stated reason was replaced at the same time.

**The retired reason.** The split used to be justified on the ground that scale scores are computed in the participant's browser, and that administering the instruments over MCP would move that arithmetic to a server. That justification is withdrawn as unsound. Where a computation happens is not by itself a privacy property: it fixes the location of an arithmetic operation and says nothing about what leaves the device, which was always a separate claim requiring separate verification. On the MCP route the participant's answers are typed into a conversation with the model before any Ashita Orbis code runs at all, so the browser boundary is not a property that route can either honour or breach. Reasoning from it would also license the wrong things — a future browser-side scoring arrangement inside a chat client would satisfy the letter of the retired reason while leaving all three of the real objections intact.

**The three reasons that hold**, none of which concerns where scoring happens:

1. **Administration fidelity.** The MCP tool takes the question wording back as a free-text field with nothing validating it against the canonical items. Across ten open-ended questions an unenforced paraphrase costs comparability between participants. Across a several-hundred-item forced-choice battery with fixed anchors and reverse-keyed scoring it changes the instrument — and this site publishes normed 0–100 scale scores computed from those items. A conversational administration of a full battery is also long enough that automatic context summarization could leave the model submitting reconstructed rather than received answers, which neither the participant nor the server would be able to detect. That is a data-integrity failure in a dataset whose entire purpose is to serve as psychometric ground truth.

2. **The consent surface is not proportionate to the stake.** Consent on the MCP route is a caller attestation carrying `verification_method=none` — a record of what a client asserted it showed someone, which the server cannot check. That is proportionate to a ten-question interview held for 7 days. It is not proportionate to a model asserting, on a stranger's behalf, the Level 2 research consent that places item-level psychometric data on a 24-month clock. Level 2 remains what it is on the website: an unchecked, post-results choice the participant makes for themselves, on a rendered page, with equal button prominence.

3. **Screening instruments do not belong in a chat window.** The public battery includes PHQ-8 and GAD-7. Item 9 of the PHQ-9 was removed from the public battery on the reasoning that asking a question one cannot act on is collection rather than screening. Conversational administration makes distressed disclosure more likely, not less, and there is no clinician anywhere in this system.

One further constraint rules out the most obvious implementation on mechanism alone: persisting per-item answers from an MCP session would require recording research consent for that session, which moves it off the 7-day deletion path the MCP tool promises without qualification and onto the 24-month research path that honours named-purpose retention holds. The unqualified "deleted 7 days later" that the tool states would become false the moment such a design shipped.

Full analysis, including the only shape a future version could take and the empirical test that would weaken reason 1: `orchestration/backlog-recovery/day-2026-07-28/reports/psyche-mcp-readjudication-2026-08-11.md` (internal).

## Data Retention

- Active sessions: 7 days, then automatically deleted
- Completed sessions with Level 2 consent: retained for research
- Withdrawn sessions: responses and interviews deleted immediately; session record retained with withdrawal_at timestamp
- Excluded sessions (a record discovered to be a minor's): responses, interviews and evaluations deleted, scores/report/persona/consent nulled, any named-purpose hold released, and a content-free tombstone retained — session id, timestamps, how it came to be known, and the authorising ruling. Procedure and rationale: `docs/PARTICIPANT-ELIGIBILITY.md` §5
- No account, name, email or device identifier is collected, so nothing held links a record to a person by construction; the residual identifiability is the participant's own written answers, which is why these records are treated as pseudonymous rather than anonymous

## Risk Assessment

**Risks to participants:**
- Minimal. Responses are anonymous; disclosure cannot reasonably place subjects at risk
- Standard personality instruments in public domain
- PHQ-8/GAD-7 screening items may surface distressing content — not diagnostic, disclaimer provided

**Suicidal ideation: the question is no longer asked (2026-08-11).**
- The public site administers **PHQ-8** — the PHQ-9 without item 9, "thoughts that you would be
  better off dead or of hurting yourself in some way". PHQ-8 is a published instrument whose
  validation found it performs essentially identically as a severity measure, and it is the
  standard choice for exactly this situation: a study that cannot respond to a disclosure.
- The earlier mitigation was an interstitial after the section, plus an interrupt on a nonzero
  answer to item 9. Both are gone with the item, because the honest reading is that neither was
  a mitigation. This site is run by one person, has no clinician, and has no way to contact a
  respondent — so a disclosure of suicidal ideation could be *received* and never *acted on*,
  while the answer sat in a research table nothing read. Asking a question you cannot act on is
  not screening; it is collection. (Owner ruling `q-psyche-phq9-drop` = A; analysis in
  `reports/psyche-phq9-drop-analysis-2026-08-11.md`.)
- The **full PHQ-9 remains in the private research battery** (`heavy` tier), where a result is
  read by a person who chose to run it on themselves.
- What stays for the public site: the crisis card before the start button, the persistent footer
  link, and the crisis block on the results screen — a battery containing SD3, a self-esteem
  scale and a ten-question self-reflection interview can still land badly on someone, and those
  are offered without claiming to have detected anything about them.
- Crisis resources cover US (988 Suicide & Crisis Lifeline, Crisis Text Line), Canada (988 Suicide
  Crisis Helpline, Crisis Services Canada), UK & ROI (Samaritans) and international (Find A
  Helpline) contacts.

**Identifying information in free text:**
- Interview question design evaluated for this risk (questions about self-description, values, decision-making — not biographical facts)
- Participants are instructed not to include their name, location, employer, or other personally identifying details in interview responses (notice displayed alongside each text entry)
- Content-check procedure required for any interview responses excerpted in publications
- No question asks for name, location, employer, or other identifiable details

## Exempt Determination Pathway

This research is put forward for exempt status under 45 CFR 46.104(d)(2) — survey and interview procedures:
- Survey and interview research, with no intervention
- Records are session-coded and treated as pseudonymous. They are **not** described as anonymous: a random UUID joins the scores, the written answers and the report, and ten open-ended answers are the participant's own words (2026-08-12 anonymity analysis). Which sub-paragraph therefore applies — (d)(2)(i), which turns on what is *recorded*, or (d)(2)(iii), the limited-IRB-review route for recorded identifiable responses — is a question for the reviewing body rather than one to be settled here, and is put to it explicitly.
- Disclosure of responses is not reasonably expected to place subjects at risk of criminal or civil liability, or damage to financial standing, employability or reputation

**Adults only — and this is what makes the pathway available.** 45 CFR 46.104(b)(3) limits which exemptions may be applied to research subject to subpart D (children): the exemptions at (d)(2)(i) and (ii) reach research with children only where it involves educational tests or the observation of public behavior in which the investigator does not participate, and the exemption at (d)(2)(iii) may not be applied to research with children at all. This assessment is neither an educational test nor observation of public behavior, and the investigator records the responses — so neither carve-out reaches it. A (d)(2) determination premised on adult participation therefore cannot be assumed to cover minors, and the research set is scoped accordingly (owner ruling `q-psyche-participants-r2` = A, 2026-08-15). Including minors properly would require a separate child protocol with assent, parental permission and the safeguards the board requires; no such protocol has been written and none is being run. Scope, enforcement, false-declaration handling, the exclusion-and-purge procedure and the pre-amendment legacy cohort: `docs/PARTICIPANT-ELIGIBILITY.md`.

*The Common Rule binds federally-funded or institutionally-engaged research. This project is neither, so 45 CFR 46 is a voluntary standard adopted here rather than a jurisdictional obligation — which does not license stretching a determination premised on adults over children.*

**Pre-publication plan**: Submit to Pearl IRB for formal exempt determination letter (1-3 business days). The determination confirms the research was always exempt — it does not constitute retroactive approval. The submission must state that the research set is adults-only, and must disclose the pre-amendment legacy cohort described in `docs/PARTICIPANT-ELIGIBILITY.md` §6 — a small number of research records collected before the eligibility declaration existed, to which the question was never put.

## Canadian Regulatory Analysis

*Added 2026-03-09. The principal investigator is based in Canada.*

### TCPS 2 (Tri-Council Policy Statement)

TCPS 2 applies only to research "conducted under the auspices of any institution that is eligible to receive and administer research funds from any of the three federal Agencies (CIHR, NSERC, SSHRC)." As an independent researcher with no institutional affiliation and no tri-council funding, this research is categorically outside TCPS 2's mandatory scope (Interagency Advisory Panel, Scope interpretation).

Even if TCPS 2 applied, anonymous online surveys qualify for exemption from REB review under Article 2.4: "REB review is not required for research that relies exclusively on secondary use of anonymous information." The TCPS 2 glossary defines "anonymous information" as "information that never had identifiers associated with it (e.g., anonymous surveys)" — precisely this scenario.

### PIPEDA (Personal Information Protection and Electronic Documents Act)

PIPEDA applies to organizations collecting personal information "in the course of commercial activities" (s. 4(1)(a)). Two threshold questions:

1. **Commercial activity**: This is a non-commercial research tool. No monetization, no data resale, no advertising. The "commercial activity" threshold is likely not met.

2. **Personal information**: PIPEDA defines personal information as "information about an identifiable individual" (s. 2(1)). The OPC's test requires "a serious possibility that an individual could be identified through the use of that information, alone or in combination with other information." Data that never had identifiers associated with it presents a stronger case for falling outside PIPEDA's scope than de-identified data (which was once identifiable). Psychometric scores with no linked identifiers satisfy this standard.

**Free-text risk**: Interview responses could inadvertently contain self-disclosed identifying information (name, location, employer). Mitigation: participants are explicitly instructed not to include identifying details. This instruction is displayed alongside each text entry field.

Provincial equivalents (BC PIPA, Alberta PIPA) mirror PIPEDA's "identifiable individual" standard and the same analysis applies.

### Quebec Law 25 / ARPPIPS

Quebec's Act respecting the protection of personal information in the private sector (ARPPIPS, as amended by Law 25) defines personal information as "any information which relates to a natural person and allows that person to be identified" (s. 2).

**Cross-border transfer (s. 17)**: ARPPIPS s. 17 requires a Transfer Impact Assessment and transparency notice before communicating personal information outside Quebec. These obligations are predicated on transferring "personal information." Data that is genuinely anonymous (never linked to identifiers) falls outside this definition. The consent disclosure explicitly states that interview text is "transferred to and processed on servers located in the United States" and that session data is stored on US-based servers — satisfying the transparency obligation even if the data were deemed personal.

The Quebec Anonymization Regulation (in force May 30, 2024) establishes that information is anonymous when "it is, at all times, reasonably foreseeable in the circumstances that it irreversibly no longer allows the person to be identified," assessed against correlation, individualization, and inference risks all being "very low." Psychometric scores with no linked identifiers satisfy this standard.

### Cross-Border Data Transfer

Session data is stored in the United States; report generation is processed by a provider that publishes endpoints in more than one region:
- Session data: Cloudflare D1 (edge SQLite, US)
- Interview text processing: OpenRouter (US), model GPT-5.6 Luna, onward to its serving provider. Since 2026-08-15 the request pins zero data retention, which narrows the serving provider for this model to Microsoft Azure and means the text is **not retained** at either hop. Azure's zero-retention endpoints for this model are published in both US and European regions, and the request does **not** pin which region serves it — so a given report may be processed outside the United States, transiently and without retention. This is a correction to the previous flat claim that all processing occurred in the US, which was never enforced by anything; whether to pin a region is an open question recorded against the Europe posture (`q-psyche-europe`).

The consent disclosure has been updated (v1.1, 2026-03-09) to explicitly state that data is "transferred to and processed on servers located in the United States" and that session data is "stored on US-based servers (Cloudflare)."

### Age of Consent

No Canadian province has a specific statute setting a research-participation age of consent. TCPS 2 uses a capacity-based model rather than a fixed age; a fixed 16+ threshold would be more conservative than TCPS 2 requires for account-unlinked, low-risk survey research.

**The research set is adults-only as of 2026-08-15; the assessment is not** (owner ruling `q-psyche-participants-r2` = A). The eligibility declaration is asked once, immediately before the optional research opt-in at the end — after results have already been shown — and never at the door. The 18 threshold is a choice made to match the exemption categories the determination pathway relies on (45 CFR 46.104(b)(3), above), not a number read off a Canadian statute; as this section notes, none sets one. Full rule: `docs/PARTICIPANT-ELIGIBILITY.md`.

**There is no age gate as of 2026-08-11** (owner ruling `q-psyche-age-gate-review`), and the 2026-08-15 ruling does not reintroduce one. The previous 16+ checkbox was an unverifiable self-declaration on a site that had just finished promising not to ask personal questions it did not need, and its own copy admitted it was "an honesty gate and not age verification" — a claim that mostly taught a younger visitor to tick the box. What replaced it states the intended audience plainly and, for a younger reader, points at a trusted adult and the crisis services, which is the only part of the old paragraph that was ever advice rather than paperwork. The PHQ-8/GAD-7 mental-health considerations are handled by the section introduction, per-item refusal and section skip — and, since 2026-08-11, by not asking the suicidal-ideation item at all rather than by reacting to the answer.

### Canadian Ethics Review Options

If a Canadian ethics imprimatur is desired (in addition to or instead of Pearl IRB):
- **IRB Services** (Toronto/Montreal, AAHRPP-accredited)
- **Veritas IRB** (Canadian-owned, accredited)

Since TCPS 2 does not apply, there is no mandatory Canadian ethics review requirement. A US IRB exempt determination is sufficient for most publication venues.

## Changes to This Protocol

Any changes to consent language, data collection scope, or anonymization approach will be documented as amendments to this protocol with dates and rationale.

### Amendment Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-03-08 | 1.0 | Initial protocol |
| 2026-08-15 | 1.6 | **Zero data retention pinned** on the report/persona route (`provider.zdr = true`; rulings `q-luna-zdr-adopt` = A, `q-psyche-provider-zdr` = A). Ruled 2026-08-11 and again 2026-08-12, implemented 2026-08-15: both OpenRouter calls had set model and messages and nothing else, so participants' written answers were retained under the provider's defaults. Now built at a single choke point in `api/src/routes/psyche.ts` with a regression test, no non-ZDR fallback, and every disclosure surface updated **after** the config was verified. Pinning narrows the serving provider for this model to Microsoft Azure; the flat "all processing occurs in the United States" claim is corrected, because ZDR endpoints are published in US and European regions and no region is pinned. **Research set scoped to adults only** (`q-psyche-participants-r2` = A). Eligibility declared as the opening clause of the level-2 consent — merged into the consent sentence so it lands inside the frozen per-session record — and enforced at the API, which refuses a level-2 consent whose stored text lacks it. Level 1 untouched: no age gate at the door, and the 2026-08-11 ruling that removed one stands. Exempt-determination section now states the 45 CFR 46.104(b)(3) limitation that makes the scoping necessary, and drops the "anonymous survey research" characterisation in favour of the session-coded/pseudonymous framing set by the 2026-08-12 anonymity analysis. Retention section gains the `excluded` disposition. New companion document `docs/PARTICIPANT-ELIGIBILITY.md` carries the false-declaration rule, the exclusion-and-purge procedure, and the disclosure of the pre-amendment legacy cohort. |
| 2026-08-11 | 1.5 | Corrected the record on why the scored instruments are website-only. The browser-scoring justification is retired — it fixed where an arithmetic operation happens and never guaranteed what leaves the device — and is replaced by administration fidelity, the disproportion between an unverifiable caller attestation and a 24-month research consent, and the refusal to administer depression and anxiety screens conversationally. The MCP Level 1 consent script no longer says scores are computed in the user's browser; it says no psychometric scales are administered on that route, matching the shipped tool text. No change to the rule itself. |
| 2026-08-11 | 1.4 | Retention holds introduced: a session may be kept past the 24-month research clock only under a **named research purpose** recorded in `psyche_retention_holds` with the ruling that authorised it. First and only holds: three research-consented sessions retained for the interview-correlation study (`q-psyche-research-rows` = C). Withdrawal ends a hold. |
| 2026-08-11 | 1.3 | Public battery switched to PHQ-8 (item 9 removed; full PHQ-9 retained privately). Item-9 interrupt and post-section interstitial removed with it. Age gate removed. MCP consent record reclassified as a caller attestation. |
| 2026-03-09 | 1.1 | Added Canadian regulatory analysis (PIPEDA, TCPS 2, Quebec Law 25). Updated consent language to explicitly state US-based data transfer and processing. Added crisis resource interstitial after PHQ-9/GAD-7 (US, Canada, international lines) and persistent footer link. Added instruction against including identifying information in free-text interview responses. |
| 2026-03-09 | 1.2 | Added MCP consent pathway documentation. Updated study description to cover both website-only and MCP hybrid flows. Added section on conversational consent equivalence (Claude presents same disclosures as web checkbox). Documented that Level 2 research opt-in is presented to MCP users on the website identically to web-only users. Added report generation privacy comparison table (MCP avoids third-party AI processing). |
