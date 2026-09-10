import type { Instrument, InstrumentSession, InstrumentResult } from "./types";
import { registerInstrument } from "./registry";

/**
 * PHQ-9 (Patient Health Questionnaire) + GAD-7 (Generalized Anxiety Disorder)
 * Kroenke et al. (2001) / Spitzer et al. (2006)
 * Clinical screening tools for depression and anxiety.
 */

const PHQ9_ITEMS = [
  "Little interest or pleasure in doing things",
  "Feeling down, depressed, or hopeless",
  "Trouble falling or staying asleep, or sleeping too much",
  "Feeling tired or having little energy",
  "Poor appetite or overeating",
  "Feeling bad about yourself — or that you are a failure or have let yourself or your family down",
  "Trouble concentrating on things, such as reading the newspaper or watching television",
  "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
  "Thoughts that you would be better off dead or of hurting yourself in some way",
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

const phq9Gad7: Instrument = {
  id: "phq9-gad7",
  name: "PHQ-9 + GAD-7",
  shortName: "PHQ/GAD",
  description:
    "Brief screening tools for depression (PHQ-9) and generalized anxiety (GAD-7). Over the last 2 weeks, how often have you been bothered by the following?",
  citation:
    "Kroenke, K., Spitzer, R. L., & Williams, J. B. (2001). The PHQ-9. J Gen Intern Med, 16(9), 606-613.",
  itemCount: 16,
  estimatedMinutes: 3,
  scales: [
    { id: "phq9", name: "Depression (PHQ-9)" },
    { id: "gad7", name: "Anxiety (GAD-7)" },
  ],
  items: [
    ...PHQ9_ITEMS.map((text, idx) => ({
      id: `phq9-${idx + 1}`,
      text,
      response: {
        type: "likert" as const,
        min: 0,
        max: 3,
        labels: ["Not at all", "Several days", "More than half the days", "Nearly every day"],
      },
      scaleId: "phq9",
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
const MIN_PHQ9 = 7;
const MIN_GAD7 = 5;

/** PHQ-9 and GAD-7 use sum scoring (not mean), with proration for missing items */
function scorePhqGad(instrument: Instrument, session: InstrumentSession): InstrumentResult {
  const responseMap = new Map(session.responses.map((r) => [r.itemId, r]));

  let phq9Sum = 0;
  let phq9Count = 0;
  for (let idx = 0; idx < PHQ9_ITEMS.length; idx++) {
    const r = responseMap.get(`phq9-${idx + 1}`);
    if (r && typeof r.value === "number") {
      phq9Sum += r.value;
      phq9Count++;
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
  const phq9Prorated = phq9Count >= MIN_PHQ9
    ? (phq9Sum / phq9Count) * PHQ9_ITEMS.length
    : phq9Sum;
  const phq9Complete = phq9Count >= MIN_PHQ9;

  const gad7Prorated = gad7Count >= MIN_GAD7
    ? (gad7Sum / gad7Count) * GAD7_ITEMS.length
    : gad7Sum;
  const gad7Complete = gad7Count >= MIN_GAD7;

  return {
    instrumentId: instrument.id,
    completedAt: session.completedAt ?? Date.now(),
    scores: [
      {
        scaleId: "phq9",
        scaleName: "Depression (PHQ-9)",
        raw: phq9Complete ? Math.round(phq9Prorated * 100) / 100 : phq9Sum,
        normalized: phq9Complete ? (phq9Prorated / 27) * 100 : 0,
        itemCount: phq9Count,
        ...(phq9Complete ? {} : { incomplete: true }),
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

registerInstrument(phq9Gad7, scorePhqGad);

export default phq9Gad7;
