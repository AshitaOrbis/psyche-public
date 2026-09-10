import type { Instrument, InstrumentSession, InstrumentResult } from "./types";
import { registerInstrument } from "./registry";

/**
 * PHQ-8 (Patient Health Questionnaire, 8-item) + GAD-7 (Generalized Anxiety Disorder)
 * Kroenke et al. (2009) / Spitzer et al. (2006)
 * Screening tools for depression and anxiety.
 *
 * WHY THIS EXISTS ALONGSIDE `phq9-gad7.ts`. The public site administers PHQ-8;
 * the private research battery keeps the full PHQ-9. PHQ-8 is the PHQ-9 minus
 * item 9 — "thoughts that you would be better off dead or of hurting yourself"
 * — and it is a published instrument in its own right, not an improvisation:
 * Kroenke's own validation found the eight-item version performs essentially
 * identically as a depression severity measure, which is precisely why it is
 * the standard choice for population studies that cannot respond to a
 * disclosure of suicidal ideation.
 *
 * That last clause is the whole argument. A site run by one person, with no
 * clinician and no way to contact anyone, was asking strangers whether they
 * wanted to be dead — and then storing the answer in a table nothing read.
 * Asking a question you cannot act on is not screening; it is collection.
 * (Owner ruling `q-psyche-phq9-drop` = A, 2026-08-11; analysis in
 * `reports/psyche-phq9-drop-analysis-2026-08-11.md`.)
 *
 * The items are written out here rather than imported-and-filtered from
 * phq9-gad7.ts ON PURPOSE: an import would ship item 9's text inside the public
 * JavaScript bundle, where anyone can read it, while the site says the question
 * is not asked. Removed means absent from the artifact, not hidden in it.
 *
 * MIRROR NOTE: `applications/ashitaorbis/tier-3-nextjs/src/lib/psyche-src/` is a
 * generated copy of this directory (`scripts/sync-psyche.mjs`, runs on build),
 * and tier-2 symlinks this package directly — so both public tiers get whatever
 * is here. The public/private split lives in `tiers.ts`, NOT in divergent copies
 * of this file: lite ships `phq8-gad7`, heavy replaces it with `phq9-gad7`.
 * Keep it that way; a divergent copy would be silently reverted by the next sync.
 */

const PHQ8_ITEMS = [
  "Little interest or pleasure in doing things",
  "Feeling down, depressed, or hopeless",
  "Trouble falling or staying asleep, or sleeping too much",
  "Feeling tired or having little energy",
  "Poor appetite or overeating",
  "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
  "Trouble concentrating on things, such as reading the newspaper or watching television",
  "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
];

const GAD7_ITEMS = [
  "Feeling nervous, anxious, or on edge",
  "Not being able to stop or control worrying",
  "Worrying too much about different things",
  "Trouble relaxing",
  "Being so restless that it's hard to sit still",
  "Becoming easily annoyed or irritable",
  "Feeling afraid as if something awful might happen",
];

const phq8Gad7: Instrument = {
  id: "phq8-gad7",
  name: "PHQ-8 + GAD-7",
  shortName: "PHQ/GAD",
  description:
    "Brief screening tools for depression (PHQ-8) and generalized anxiety (GAD-7). Over the last 2 weeks, how often have you been bothered by the following?",
  citation:
    "Kroenke, K., et al. (2009). The PHQ-8 as a measure of current depression in the general population. J Affect Disord, 114(1-3), 163-173.",
  itemCount: 15,
  estimatedMinutes: 3,
  scales: [
    { id: "phq8", name: "Depression (PHQ-8)" },
    { id: "gad7", name: "Anxiety (GAD-7)" },
  ],
  items: [
    ...PHQ8_ITEMS.map((text, idx) => ({
      id: `phq8-${idx + 1}`,
      text,
      response: {
        type: "likert" as const,
        min: 0,
        max: 3,
        labels: ["Not at all", "Several days", "More than half the days", "Nearly every day"],
      },
      scaleId: "phq8",
    })),
    ...GAD7_ITEMS.map((text, idx) => ({
      id: `gad7-${idx + 1}`,
      text,
      response: {
        type: "likert" as const,
        min: 0,
        max: 3,
        labels: ["Not at all", "Several days", "More than half the days", "Nearly every day"],
      },
      scaleId: "gad7",
    })),
  ],
};

/** Minimum items required for prorated scoring (standard clinical practice) */
const MIN_PHQ8 = 6;
const MIN_GAD7 = 5;

/** PHQ-8 and GAD-7 use sum scoring (not mean), with proration for missing items */
function scorePhqGad(instrument: Instrument, session: InstrumentSession): InstrumentResult {
  const responseMap = new Map(session.responses.map((r) => [r.itemId, r]));

  let phq8Sum = 0;
  let phq8Count = 0;
  for (let idx = 0; idx < PHQ8_ITEMS.length; idx++) {
    const r = responseMap.get(`phq8-${idx + 1}`);
    if (r && typeof r.value === "number") {
      phq8Sum += r.value;
      phq8Count++;
    }
  }

  let gad7Sum = 0;
  let gad7Count = 0;
  for (let idx = 0; idx < GAD7_ITEMS.length; idx++) {
    const r = responseMap.get(`gad7-${idx + 1}`);
    if (r && typeof r.value === "number") {
      gad7Sum += r.value;
      gad7Count++;
    }
  }

  // Prorate if enough items answered, otherwise mark incomplete
  const phq8Prorated = phq8Count >= MIN_PHQ8
    ? (phq8Sum / phq8Count) * PHQ8_ITEMS.length
    : phq8Sum;
  const phq8Complete = phq8Count >= MIN_PHQ8;

  const gad7Prorated = gad7Count >= MIN_GAD7
    ? (gad7Sum / gad7Count) * GAD7_ITEMS.length
    : gad7Sum;
  const gad7Complete = gad7Count >= MIN_GAD7;

  return {
    instrumentId: instrument.id,
    completedAt: session.completedAt ?? Date.now(),
    scores: [
      {
        scaleId: "phq8",
        scaleName: "Depression (PHQ-8)",
        // PHQ-8 max is 24, not the PHQ-9's 27 — normalising against 27 would
        // quietly deflate every depression score on the public site.
        raw: phq8Complete ? Math.round(phq8Prorated * 100) / 100 : phq8Sum,
        normalized: phq8Complete ? (phq8Prorated / 24) * 100 : 0,
        itemCount: phq8Count,
        ...(phq8Complete ? {} : { incomplete: true }),
      },
      {
        scaleId: "gad7",
        scaleName: "Anxiety (GAD-7)",
        raw: gad7Complete ? Math.round(gad7Prorated * 100) / 100 : gad7Sum,
        normalized: gad7Complete ? (gad7Prorated / 21) * 100 : 0,
        itemCount: gad7Count,
        ...(gad7Complete ? {} : { incomplete: true }),
      },
    ],
  };
}

registerInstrument(phq8Gad7, scorePhqGad);

export default phq8Gad7;
