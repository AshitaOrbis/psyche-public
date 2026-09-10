# Third-Party Psychometric Instruments — Item-Text Notice

This repository (Psyche) is released under the MIT License (see [`/LICENSE`](../LICENSE)).
The MIT grant covers the **original code and original content** authored for this
project — the scoring engine, adaptive-testing controller, the web app, the
analysis pipeline, configuration, documentation, and any original prose.

The MIT grant does **NOT** cover the **verbatim item text** (the actual question
wording / statements presented to respondents) of the third-party psychometric
instruments reproduced in this repository where that item text is the
copyrighted work of its original author or publisher. That item text is
**carved out** of the MIT License and is included here **for non-commercial
research and educational use only, under each instrument's own terms**, with
attribution to the original authors.

This repository does **not** grant — and cannot grant — any right to
redistribute, sublicense, relicense, or make commercial use of the restricted
instrument item text listed below. Those rights remain with the respective
copyright holders. **No representation is made that permission to redistribute
the restricted item text has been obtained.** If you intend to use any restricted
instrument beyond non-commercial research/education, or to redistribute its item
text, you must obtain permission directly from the rights holder or consult the
cited source for its terms. The maintainer may seek formal permission from the
respective rights holders in the future; until such permission is documented
here, treat every restricted item as "research/educational use only;
redistribution rights are not granted by this repository."

Conservative classification policy: an instrument is listed as **FREE** only
where its item text is in the public domain, has an explicit public-domain
dedication, or is released under a license that permits redistribution
(e.g. IPIP items, or a Creative Commons license). Where item text is
author/publisher copyrighted and there is no explicit public-domain dedication
or redistribution-permitting license — even where non-commercial research use is
commonly permitted — it is conservatively listed as **RESTRICTED**.

Where the original article/scale is identified by its DOI or author page, that
citation is the authoritative source for the instrument's actual terms; the
"License status" column below is a good-faith, conservative summary, not legal
advice.

Where the repository reproduces a **public-domain reconstruction** of a
proprietary construct (for example, the IPIP representations of HEXACO and the
Big Five rather than the proprietary HEXACO-PI-R or NEO-PI-R item text), the
public-domain reconstruction is what ships here, and it is classified FREE.

---

## Instruments whose item text IS covered by this repository's MIT License (FREE)

The verbatim item text for these instruments is public domain or released under
a redistribution-permitting license. It is covered by the repository's MIT
License. Attribution to the original authors is still expected as a matter of
scholarly practice.

| Instrument | File(s) | Author(s) | License status of item text |
|------------|---------|-----------|------------------------------|
| IPIP-NEO-60 / 120 / 300 (Big Five) | `web/src/instruments/ipip-neo-60.ts`, `ipip-neo-120.ts`, `ipip-neo-300.ts` | Goldberg (IPIP); 120-item form via Johnson; 60-item via Maples-Keller et al. (2019). 60-item data sourced from the MIT-licensed npm package `b5-johnson-120-ipip-neo-pi-r`. | Public domain (IPIP items, ipip.ori.org) |
| RIASEC markers (48) | `web/src/instruments/riasec-48.ts` | IPIP / Goldberg (Holland RIASEC markers) | Public domain (IPIP items) |
| HEXACO-60 (IPIP representation) | `web/src/instruments/hexaco-60.ts` | IPIP representation of HEXACO (ipip.ori.org); construct: Ashton & Lee (2009) | Public domain (IPIP items; not the proprietary HEXACO-PI-R) |
| HEXACO-200 (IPIP representation) | `web/src/instruments/hexaco-200.ts` | IPIP representation of HEXACO-PI-R (ipip.ori.org); construct: Lee & Ashton (2004, 2018) | Public domain (IPIP items; not the proprietary HEXACO-PI-R) |
| Rosenberg Self-Esteem Scale (RSES) | `web/src/instruments/rosenberg.ts` | Rosenberg, M. (1965) | Public domain (per University of Maryland, holder of Rosenberg's papers) |
| PHQ-9 + GAD-7 | `web/src/instruments/phq9-gad7.ts` | Kroenke, Spitzer & Williams (2001); Spitzer et al. (2006); developed with an educational grant from Pfizer | Free to reproduce/distribute without permission (released by Pfizer without copyright restriction) |
| Satisfaction With Life Scale (SWLS) | `web/src/instruments/swls.ts` | Diener, Emmons, Larsen & Griffin (1985) | Public domain (per the Diener scales page) |
| Moral Foundations Questionnaire 2 (MFQ-2) | `web/src/instruments/mfq-2.ts` | Atari, Haidt, Graham et al. (2023) | Open access / Creative Commons (CC BY) — redistribution permitted with attribution |
| IE-4 Locus of Control | `web/src/instruments/loc-ie4.ts` | Kovaleva, Beierlein, Kemper & Rammstedt (2012); GESIS | Open access (CC BY); English adaptation published open access |

---

## Instruments whose item text is NOT covered by this repository's MIT License (RESTRICTED)

The verbatim item text for these instruments is the copyrighted work of its
original author(s) or publisher(s). It is **carved out of the MIT License** and
is included here for **non-commercial research and educational use only, under
the instrument's own terms**. **This repository grants no redistribution,
sublicensing, relicensing, or commercial-use rights for this item text**, and
asserts no permission beyond what each cited source provides. For any other use,
obtain permission from the rights holder or see the cited source.

| Instrument | File | Author(s) / rights holder | License status of item text |
|------------|------|---------------------------|------------------------------|
| Cognitive Reflection Test (CRT-7) | `web/src/instruments/crt-7.ts` | Toplak, West & Stanovich (2014); Frederick (2005) | Author/publisher copyright; no redistribution grant. Research/educational use; redistribution rights not granted by this repository — see Toplak et al. (2014), *Thinking & Reasoning* 20(2):219–243 |
| Need for Cognition Scale (NCS-18) | `web/src/instruments/ncs-18.ts` | Cacioppo, Petty & Kao (1984) | Author/publisher copyright; no redistribution grant. Research/educational use; redistribution rights not granted by this repository — see the original article |
| Short Dark Triad (SD3) | `web/src/instruments/sd3.ts` | Jones & Paulhus (2014) | Author/publisher copyright; no redistribution grant. Research/educational use; redistribution rights not granted by this repository — see Jones & Paulhus (2014), *Assessment* |
| Experiences in Close Relationships—Revised (ECR-R) | `web/src/instruments/ecr-r.ts` | Fraley, Waller & Brennan (2000) | Author copyright (items posted for use/copying on the author's page, but no public-domain or redistribution grant). Research/educational use; redistribution rights not granted by this repository — see labs.psychology.illinois.edu/~rcfraley/measures/ecrr.htm |
| Emotion Regulation Questionnaire (ERQ-10) | `web/src/instruments/erq-10.ts` | Gross & John (2003) | Author copyright; research use commonly permitted but no redistribution grant. Redistribution rights not granted by this repository — see the Stanford Psychophysiology Lab / original article |
| Interpersonal Reactivity Index (IRI-28) | `web/src/instruments/iri-28.ts` | Davis (1980, 1983) | Author copyright; no public-domain or redistribution grant. Research/educational use; redistribution rights not granted by this repository — see eckerd.edu/psychology/iri |
| Self-Monitoring Scale (18-item revised) | `web/src/instruments/self-monitoring-18.ts` | Snyder & Gangestad (1986) | Author/publisher copyright; no redistribution grant. Research/educational use; redistribution rights not granted by this repository |
| Self-Monitoring Scale (Snyder original, 25-item) | `web/src/instruments/snyder-sm-25.ts` | Snyder (1974) | Author/publisher copyright; no redistribution grant. Research/educational use; redistribution rights not granted by this repository |
| Levenson IPC Locus of Control (24-item) | `web/src/instruments/levenson-ipc-24.ts` | Levenson (1981) | Author copyright; permission-required per several sources. Research/educational use; redistribution rights not granted by this repository |
| Short Grit Scale (Grit-S) | `web/src/instruments/grit-s.ts` | Duckworth & Quinn (2009) | Author copyright (Duckworth Lab): free for non-commercial research/education, reproduction in books/commercial outlets and commercial use prohibited. Redistribution rights not granted by this repository — see angeladuckworth.com |
| Original Grit Scale (Grit-O) | `web/src/instruments/grit-o.ts` | Duckworth, Peterson, Matthews & Kelly (2007) | Author copyright (Duckworth Lab): free for non-commercial research/education only; reproduction/commercial use prohibited. Redistribution rights not granted by this repository — see angeladuckworth.com |
| Basic Psychological Need Satisfaction (BPNS-9) | `web/src/instruments/bpns-9.ts` | Deci & Ryan; Center for Self-Determination Theory | Copyright SDT center; academic use permitted, commercial permission required; no redistribution grant. Redistribution rights not granted by this repository — see selfdeterminationtheory.org |
| Basic Psychological Need Satisfaction & Frustration (BPNSFS-21) | `web/src/instruments/bpns-21.ts` | Chen et al. (2015); Center for Self-Determination Theory | Copyright SDT center; academic use permitted, commercial permission required; no redistribution grant. Redistribution rights not granted by this repository — see selfdeterminationtheory.org |
| Acceptance and Action Questionnaire II (AAQ-II) | `web/src/instruments/aaq-ii.ts` | Bond, Hayes et al. (2011) | Author/publisher copyright; research/client use permitted, commercial use requires permission; no redistribution grant. Redistribution rights not granted by this repository — see contextualscience.org |
| Implicit Theories of Intelligence Scale (Dweck ITIS) | `web/src/instruments/dweck-itis.ts` | Dweck (1999) | © Carol Dweck; no public-domain or redistribution grant. Research/educational use; redistribution rights not granted by this repository |
| Curiosity and Exploration Inventory II (CEI-II) | `web/src/instruments/cei-ii.ts` | Kashdan, Gallagher, Silvia et al. (2009) | Author/publisher copyright; no explicit redistribution grant. Research/educational use; redistribution rights not granted by this repository |
| Actively Open-Minded Thinking Scale (AOT-13) | `web/src/instruments/aot-13.ts` | Haran, Ritov & Mellers (2013); Stanovich & West | Author/publisher copyright; no explicit redistribution grant for the items as reproduced here. Research/educational use; redistribution rights not granted by this repository |
| Intolerance of Uncertainty Scale — Short Form (IUS-12) | `web/src/instruments/ius-12.ts` | Carleton, Norton & Asmundson (2007) | Author/publisher copyright; no redistribution grant identified. Research/educational use; redistribution rights not granted by this repository |
| Self-Compassion Scale (SCS-26) | `web/src/instruments/scs-26.ts` | Neff (2003) | Author copyright; broad permission to use, but no explicit redistribution/sublicensing license. Research/educational use; redistribution rights not granted by this repository — see self-compassion.org |
| Frost Multidimensional Perfectionism Scale (Frost MPS) | `web/src/instruments/frost-mps.ts` | Frost, Marten, Lahart & Rosenblate (1990) | Author/publisher copyright; no public-domain or redistribution grant. Research/educational use; redistribution rights not granted by this repository |
| Mindful Attention Awareness Scale (MAAS) | `web/src/instruments/maas.ts` | Brown & Ryan (2003) | Author/APA copyright; no open redistribution license. Research/educational use; redistribution rights not granted by this repository |
| Authenticity Scale | `web/src/instruments/authenticity.ts` | Wood, Linley, Maltby, Baliousis & Joseph (2008) | Author/APA copyright; no public-domain or redistribution grant. Research/educational use; redistribution rights not granted by this repository |
| Self-Control Scale (Tangney SCS, 36-item) | `web/src/instruments/tangney-scs.ts` | Tangney, Baumeister & Boone (2004) | Author/publisher copyright; no explicit redistribution grant. Research/educational use; redistribution rights not granted by this repository |
| Maximization Scale (MS-13) | `web/src/instruments/maximization.ts` | Schwartz et al. (2002); short form Nenkov et al. (2008) | Author/publisher copyright; research availability is not a redistribution license. Research/educational use; redistribution rights not granted by this repository |
| Zimbardo Time Perspective Inventory (ZTPI) | `web/src/instruments/ztpi.ts` | Zimbardo & Boyd (1999) | © 1999 Zimbardo & Boyd, all rights reserved; online test access is not redistribution permission. Research/educational use; redistribution rights not granted by this repository |

---

## Notes

- **Adaptive item banks** (`web/public/item-banks/big5-grm-params.json`,
  `hexaco-grm-params.json`) contain only IRT calibration parameters and
  **placeholder** item labels (e.g. `[Anxiety item 1]`), not verbatim
  third-party item text, and are covered by the MIT License.
- The conversational interview (`web/src/instruments/open-ended.ts`) is original
  content authored for this project and is covered by the MIT License.
- This file is a good-faith, conservative summary prepared without legal counsel.
  It is not legal advice. The cited sources govern in case of any conflict.
- Corrections and documented permission grants are welcome; please open an issue
  or pull request so this notice can be updated.
