# Security and Privacy Reports

This project handles psychometric assessment methodology. The public repository must never
contain another person's personal assessment data, real interview content, or identifying
information about a private individual.

**What this tree does contain, stated plainly (corrected 2026-09-05).** Until this date this
file asserted that "all subject-keyed content in this tree is synthetic (archetype-keyed) by
design." **That was false**, and it had been since the research artifacts were first published.
This repository is a single-subject methodology project, and the subject is its author. It
publishes his own aggregate psychometric outputs — corpus-inferred and register-partitioned
Big Five vectors, and the per-condition experimental estimates computed against them — by his
own decision. Those are real, not synthetic, and they are published deliberately.

Three things are deliberately NOT here, and their absence is enforced by the publish gate
rather than by this promise: any other private individual's derived personal data; the merged
39-instrument reference profile and any quantity that reconstructs it; and the narrative
private-profile review conclusions, which are interpretation about a person rather than a
methodology result. Where a table or a backlog line reads "withheld", that is why.

**Exception, stated precisely (bq-1246 correction, 2026-09-04):** `psycheeval`'s
public-inspired personas are not archetype-only. A minority of subject-keyed content —
the `public_inspired` persona family and its `data/source_packets/*.jsonl` — is built
from cited, published material by named public figures (their own essays, talks, and
testimony), and is deliberately, trivially linkable to those figures through that same
citation trail. This is not a synthetic archetype and the alias is not de-identification;
it is public-figure commentary attributed to its source, the same public-figure
carve-out this project uses elsewhere. See
[`psycheeval/README.md`](psycheeval/README.md#licensing) for the full disclosure and
`data/seed_bank_pure_synthetic.jsonl` for the genuinely archetype-only persona family.
Every subject-keyed record in **`psycheeval/` and `benchmark/`** — the pure-synthetic
personas and all their scenario, scoring, and report artifacts — is synthetic and carries no
private individual's data. That claim is scoped to those trees on purpose: the research
artifacts under `experiments/` and `analysis/` are **not** synthetic, and are covered by the
section above rather than by this one. Stating it unscoped is the error corrected on
2026-09-05.

**If you find personal data in this repository, or a vulnerability in the web app**, please
report it:

- Open a [GitHub issue](../../issues) — for privacy findings, do **not** paste the data
  itself; describe the file path and the category of data so it can be verified and removed.
- Or email the privacy-responsible person at `ashitaorbis@gmail.com`. Do not paste the
  assessment data into the message; identify the request by session ID and use the
  session secret for authenticated readback. The full complaint, access, and correction
  procedure is in [the ethics protocol](docs/ETHICS-PROTOCOL.md#privacy-contact-complaints-access-and-accuracy).

Reports about personal data are treated as the highest-severity class and acted on before
anything else.

## Privacy model — the hosted app, and this repository, are two different things

**The single authoritative statement is the consent and data-map copy on the assessment
itself.** Where this file and the live disclosure disagree, the live disclosure is right and
this file is stale. This section is deliberately short and defers rather than restating the
contract, because restating it in three places is exactly what produced the contradiction
corrected on 2026-08-12 (below).

**The hosted battery** ([app.ashitaorbis.com/psyche](https://app.ashitaorbis.com/psyche))
**does have a backend**: a Cloudflare Worker with a D1 database, in the United States. Scale
items are displayed and scored in your browser and your individual item answers are not
transmitted — only the computed scale scores, your ten written interview answers, a random
session ID, and your report if you generate one. Those are stored server-side under a
published retention ladder (7 days / 90 days / research opt-in). There are no accounts, no
cookies, and no device identifiers, and the application stores no IP address — though
Cloudflare, as the host, processes standard request metadata including your IP in order to
serve any request. Generating a report sends your scores and interview text to OpenRouter and
onward to the serving provider, on a route that pins zero data retention: the request
restricts routing to endpoints which retain neither the prompt nor the completion, so
that content is not kept at either hop. What those two still hold is billing and
abuse-prevention metadata about the request itself, under their policies rather than ours.

**Running this repository yourself** is the local-only case: self-report data stays in browser
localStorage, because you supply your own storage and your own API keys.

For the full statement, including the retention ladder and the named processor, see
[Live Deployment](README.md#live-deployment) in `README.md` — and the consent copy on the
assessment, which outranks both.

> **Correction, 2026-08-12.** Until this date, this section stated that the hosted battery had
> "no backend of its own" and that "results stay in browser localStorage". That was false for
> the hosted service and had been since it gained a backend; `README.md` was corrected on
> 2026-08-10/11 and this file was not brought along. A reader deciding whether to disclose
> psychometric data could reasonably have relied on the wrong document. Found by an external
> adversarial review of the published repository.
