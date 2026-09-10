/**
 * CAT Controller — orchestrates per-facet adaptive testing.
 *
 * Manages multiple independent mini-CATs (one per dimension/facet).
 * Uses fixed-form theta as informative prior when available.
 * Excludes fixed-form items from the CAT item pool.
 */

import type { GRMItem, CATResponse } from "./grm-engine";
import { estimateTheta, thetaToPercentile, selectNextItem, inverseNormalCDF } from "./grm-engine";
import type { ScaleScore } from "../instruments/types";

/** Stopping criteria for adaptive testing. */
export interface StoppingCriteria {
  /** Target standard error (stop when SE ≤ this) */
  seThreshold: number;
  /** Minimum items per dimension before stopping is allowed */
  minItems: number;
  /** Maximum items per dimension (hard stop) */
  maxItems: number;
}

/** State for a single dimension's CAT session. */
export interface DimensionSession {
  dimensionId: string;
  /** Current theta estimate */
  theta: number;
  /** Current standard error */
  se: number;
  /** Items administered for this dimension */
  administered: CATResponse[];
  /** Set of administered item IDs */
  administeredIds: Set<string>;
  /** Whether this dimension is complete */
  complete: boolean;
  /** Prior theta (from fixed-form if available) */
  priorMean: number;
  /** Prior SD (from fixed-form SE if available) */
  priorSD: number;
}

/** Full CAT session state. */
export interface CATSession {
  instrumentId: string;
  /** Per-dimension sessions */
  dimensions: Map<string, DimensionSession>;
  /** Order in which dimensions are tested */
  dimensionOrder: string[];
  /** Index of current dimension being tested */
  currentDimensionIndex: number;
  /** Total items administered across all dimensions */
  totalItemsAdministered: number;
  /** Whether the entire CAT is complete */
  complete: boolean;
  /** Items grouped by dimension — O(1) lookup (readonly cache, set once in initCATSession) */
  readonly dimensionItems: ReadonlyMap<string, GRMItem[]>;
  /** Item ID → GRMItem — O(1) lookup (readonly cache) */
  readonly itemIndex: ReadonlyMap<string, GRMItem>;
}

/** Default stopping criteria for personality assessment. */
export const DEFAULT_STOPPING: StoppingCriteria = {
  seThreshold: 0.30,
  minItems: 3,
  maxItems: 10,
};

/**
 * Smoke test for item bank validity. Checks if all discrimination values
 * are identical (typical of synthetic/placeholder banks).
 *
 * Does NOT check: threshold diversity, reasonable discrimination range (0.3-2.5),
 * cross-validation fit, or item content quality. These require real calibration data.
 * See BACKLOG.md for validated item bank requirements.
 */
export function validateItemBank(itemBank: GRMItem[]): boolean {
  if (itemBank.length === 0) return false;
  // Synthetic banks typically have uniform discrimination (a) values
  const aValues = new Set(itemBank.map(item => item.discrimination));
  if (aValues.size === 1) {
    console.warn(
      '[Psyche CAT] Item bank appears to use synthetic/placeholder parameters ' +
      '(all discrimination values are identical). CAT results will not be psychometrically valid. ' +
      'See BACKLOG.md for validated item bank requirements.'
    );
    return false;
  }
  return true;
}

/** Matches placeholder item text such as "[Anxiety item 1]". */
const PLACEHOLDER_TEXT_RE = /^\[[^\]]+\]$/;

/**
 * Hard validator for CAT item banks. Throws on the first defect found.
 *
 * Rejects banks that contain placeholder item text (e.g. "[Anxiety item 1]"),
 * non-finite or non-positive discriminations, threshold/category mismatches,
 * non-finite thresholds, or unordered thresholds. Callers (the adaptive test
 * runner) must refuse to administer a CAT from a bank that fails this check —
 * no amount of GRM math makes theta estimates from invalid items meaningful.
 */
export function validateCATBankOrThrow(bank: GRMItem[]): void {
  if (bank.length === 0) {
    throw new Error("CAT item bank is empty");
  }
  for (const item of bank) {
    if (typeof item.text !== "string" || item.text.trim().length === 0) {
      throw new Error(`Missing item text: ${item.id}`);
    }
    if (PLACEHOLDER_TEXT_RE.test(item.text.trim())) {
      throw new Error(
        `Placeholder CAT item text: ${item.id} ("${item.text}"). ` +
        `This item bank is not calibrated for real use — see BACKLOG.md.`
      );
    }
    if (!Number.isFinite(item.discrimination) || item.discrimination <= 0) {
      throw new Error(`Invalid discrimination for ${item.id}: ${item.discrimination}`);
    }
    if (!Number.isInteger(item.numCategories) || item.numCategories < 2) {
      throw new Error(`Invalid numCategories for ${item.id}: ${item.numCategories}`);
    }
    if (!Array.isArray(item.thresholds) || item.thresholds.length !== item.numCategories - 1) {
      throw new Error(`Threshold/category mismatch for ${item.id}`);
    }
    if (!item.thresholds.every((t) => Number.isFinite(t))) {
      throw new Error(`Non-finite threshold for ${item.id}`);
    }
    for (let i = 1; i < item.thresholds.length; i++) {
      if (item.thresholds[i]! <= item.thresholds[i - 1]!) {
        throw new Error(`Unordered thresholds for ${item.id}`);
      }
    }
  }
}

/**
 * Conservative SE used when seeding a CAT prior from a fixed-form score that
 * lacks a calibrated theta/se. Wide enough that the "skip CAT for this facet"
 * shortcut never fires from an uncalibrated score (always > seThreshold),
 * narrow enough that the prior still informs early item selection.
 */
function conservativePriorSE(itemCount: number): number {
  const n = Math.max(1, itemCount);
  return Math.max(0.55, 1.2 / Math.sqrt(n));
}

/**
 * Derive a CAT prior from a fixed-form ScaleScore.
 *
 * Prefers a calibrated theta/se when the score carries one. Otherwise maps the
 * 0-100 normalized score through the inverse normal CDF as an approximate
 * theta and pairs it with a conservative SE. Returns null when no usable
 * information exists. The approximate path is interim: fixed-form percentile
 * is not on the same calibrated IRT scale as the CAT bank, hence the wide SE.
 */
export function fixedFormPrior(
  score: ScaleScore,
): { theta: number; se: number; calibrated: boolean } | null {
  if (
    score.theta !== undefined && score.se !== undefined &&
    Number.isFinite(score.theta) && Number.isFinite(score.se) && score.se > 0
  ) {
    return { theta: score.theta, se: score.se, calibrated: true };
  }
  if (typeof score.normalized !== "number" || !Number.isFinite(score.normalized)) {
    return null;
  }
  const p = Math.min(0.999, Math.max(0.001, score.normalized / 100));
  return {
    theta: inverseNormalCDF(p),
    se: conservativePriorSE(score.itemCount),
    calibrated: false,
  };
}

/**
 * Initialize a CAT session for a set of dimensions.
 *
 * @param instrumentId - Identifier for this CAT instrument
 * @param itemBank - Full item bank with GRM parameters
 * @param fixedFormScores - Optional scores from fixed-form instruments (theta estimates used as priors)
 * @param fixedFormItemIds - Item IDs from fixed-form instruments to exclude from CAT pool
 * @param stopping - Stopping criteria
 */
export function initCATSession(
  instrumentId: string,
  itemBank: GRMItem[],
  fixedFormScores?: ScaleScore[],
  fixedFormItemIds?: Set<string>,
  stopping: StoppingCriteria = DEFAULT_STOPPING,
): CATSession {
  // Group items by dimension and build ID index (cached on session for O(1) lookup)
  const dimensionItems = new Map<string, GRMItem[]>();
  const itemIndex = new Map<string, GRMItem>();
  for (const item of itemBank) {
    // Skip items already administered in fixed form
    if (fixedFormItemIds?.has(item.id)) continue;
    const items = dimensionItems.get(item.dimensionId) ?? [];
    items.push(item);
    dimensionItems.set(item.dimensionId, items);
    itemIndex.set(item.id, item);
  }

  // Build dimension sessions
  const dimensions = new Map<string, DimensionSession>();
  const dimensionOrder: string[] = [];

  // Build fixed-form prior lookup. Calibrated theta/se is used directly;
  // otherwise an approximate prior is derived from the normalized percentile
  // (see fixedFormPrior) so a long fixed form actually informs the CAT.
  const fixedTheta = new Map<string, { theta: number; se: number; calibrated: boolean }>();
  if (fixedFormScores) {
    for (const score of fixedFormScores) {
      const prior = fixedFormPrior(score);
      if (prior) {
        fixedTheta.set(score.scaleId, prior);
      }
    }
  }

  for (const [dimId] of dimensionItems) {
    // Skip dimension only when a CALIBRATED fixed-form estimate already meets
    // the SE threshold. Approximate (percentile-derived) priors never skip.
    const prior = fixedTheta.get(dimId);
    if (prior && prior.calibrated && prior.se <= stopping.seThreshold) {
      continue; // Fixed form good enough, skip CAT for this facet
    }

    const priorMean = prior?.theta ?? 0;
    const priorSD = prior?.se ?? 1;

    dimensions.set(dimId, {
      dimensionId: dimId,
      theta: priorMean,
      se: priorSD,
      administered: [],
      administeredIds: new Set(),
      complete: false,
      priorMean,
      priorSD,
    });
    dimensionOrder.push(dimId);
  }

  // Sort for deterministic dimension ordering regardless of item bank JSON order
  dimensionOrder.sort();

  return {
    instrumentId,
    dimensions,
    dimensionOrder,
    currentDimensionIndex: 0,
    totalItemsAdministered: 0,
    complete: dimensionOrder.length === 0,
    dimensionItems,
    itemIndex,
  };
}

/**
 * Get the next item to administer.
 * Returns null if all dimensions are complete.
 * Returns a new session state to reflect any dimension advancement.
 */
export function getNextItem(
  session: CATSession,
): { item: GRMItem; dimensionId: string; session: CATSession } | null {
  if (session.complete) return null;

  let currentIndex = session.currentDimensionIndex;
  let updatedDims = session.dimensions;

  // Find next incomplete dimension
  while (currentIndex < session.dimensionOrder.length) {
    const dimId = session.dimensionOrder[currentIndex]!;
    const dimSession = updatedDims.get(dimId);
    if (!dimSession) {
      currentIndex++;
      continue;
    }

    if (dimSession.complete) {
      currentIndex++;
      continue;
    }

    // O(1) dimension lookup + filter only administered items
    const dimItems = session.dimensionItems.get(dimId) ?? [];
    const dimBank = dimItems.filter(
      (item) => !dimSession.administeredIds.has(item.id),
    );

    if (dimBank.length === 0) {
      updatedDims = new Map(updatedDims);
      updatedDims.set(dimId, { ...dimSession, complete: true });
      currentIndex++;
      continue;
    }

    // dimBank is already filtered to exclude administered items, so pass empty set
    const nextItem = selectNextItem(dimBank, dimSession.theta, new Set());
    if (!nextItem) {
      updatedDims = new Map(updatedDims);
      updatedDims.set(dimId, { ...dimSession, complete: true });
      currentIndex++;
      continue;
    }

    const newSession: CATSession = {
      ...session,
      dimensions: updatedDims,
      currentDimensionIndex: currentIndex,
    };
    return { item: nextItem, dimensionId: dimId, session: newSession };
  }

  // All dimensions complete
  return null;
}

/**
 * Register a response and update theta estimate.
 * Returns a new session state. If itemId was already administered, returns unchanged session.
 */
export function registerResponse(
  session: CATSession,
  itemId: string,
  category: number,
  stopping: StoppingCriteria = DEFAULT_STOPPING,
): CATSession {
  // O(1) item lookup via session cache
  const item = session.itemIndex.get(itemId);
  if (!item) return session;

  const dimSession = session.dimensions.get(item.dimensionId);
  if (!dimSession) return session;

  // Double-submit guard: if already administered, return unchanged
  if (dimSession.administeredIds.has(itemId)) return session;

  // Clamp raw category to the item's valid range
  const clamped = Math.max(0, Math.min(item.numCategories - 1, Math.round(category)));

  // Reverse-keyed items: flip the response category BEFORE likelihood
  // computation. GRM probabilities assume higher category = higher theta;
  // `reverse: true` items are worded in the opposite direction, so the
  // endorsed category must be mirrored (k -> K-1-k). The stored CATResponse
  // therefore always holds the SCORED (already-flipped) category.
  const scoredCategory = item.reverse
    ? item.numCategories - 1 - clamped
    : clamped;

  // Build new dimension session with the response added
  const response: CATResponse = { itemId, category: scoredCategory };
  const newAdministered = [...dimSession.administered, response];
  const newAdministeredIds = new Set([...dimSession.administeredIds, itemId]);

  // Get all items for this dimension that have been administered
  const dimItems = session.dimensionItems.get(item.dimensionId) ?? [];
  const administeredItems = dimItems.filter(
    (i) => newAdministeredIds.has(i.id),
  );

  // Re-estimate theta
  const estimate = estimateTheta(
    administeredItems,
    newAdministered,
    dimSession.priorMean,
    dimSession.priorSD,
  );

  // Check stopping criteria
  const nItems = newAdministered.length;
  let isComplete = false;
  if (nItems >= stopping.maxItems) {
    isComplete = true;
  } else if (nItems >= stopping.minItems && estimate.se <= stopping.seThreshold) {
    isComplete = true;
  }

  const newDimSession: DimensionSession = {
    ...dimSession,
    administered: newAdministered,
    administeredIds: newAdministeredIds,
    theta: estimate.theta,
    se: estimate.se,
    complete: isComplete,
  };

  const newDims = new Map(session.dimensions);
  newDims.set(item.dimensionId, newDimSession);

  let newIndex = session.currentDimensionIndex;
  let sessionComplete = session.complete;
  if (isComplete) {
    newIndex++;
    if ([...newDims.values()].every((d) => d.complete)) {
      sessionComplete = true;
    }
  }

  return {
    ...session,
    dimensions: newDims,
    currentDimensionIndex: newIndex,
    totalItemsAdministered: session.totalItemsAdministered + 1,
    complete: sessionComplete,
  };
}

/**
 * Get progress summary for all dimensions.
 */
export function getCATProgress(session: CATSession): {
  dimensionId: string;
  theta: number;
  se: number;
  itemsAdministered: number;
  complete: boolean;
  percentile: number;
}[] {
  return session.dimensionOrder.map((dimId) => {
    const dim = session.dimensions.get(dimId)!;
    return {
      dimensionId: dimId,
      theta: dim.theta,
      se: dim.se,
      itemsAdministered: dim.administered.length,
      complete: dim.complete,
      percentile: thetaToPercentile(dim.theta),
    };
  });
}

/**
 * Convert completed CAT session to ScaleScore array for storage.
 *
 * Each score is tagged with its provenance: CAT-estimated facet scores and
 * CAT-derived domain aggregates are `source: "cat"`; any score carried over
 * from a fixed-form instrument is `source: "fixed-form"` so the UI can label
 * it honestly rather than presenting it as an adaptive result.
 *
 * When `facetParents` is provided (facet scaleId -> parent domain scaleId),
 * domain scores are computed from the CAT facet thetas via inverse-variance
 * weighting — NOT inherited from a different instrument's domain scores.
 *
 * When fixedFormScores are provided, fixed-form scores are appended ONLY for
 * scales the CAT did not measure and did not aggregate (e.g. facets skipped
 * because a calibrated fixed-form SE already met the stopping threshold).
 */
export function catSessionToScores(
  session: CATSession,
  fixedFormScores?: ScaleScore[],
  facetParents?: Map<string, string>,
): ScaleScore[] {
  const scores: ScaleScore[] = [];
  for (const [dimId, dim] of session.dimensions) {
    scores.push({
      scaleId: dimId,
      scaleName: dimId, // Will be mapped to proper names by the instrument definition
      raw: dim.theta,
      normalized: thetaToPercentile(dim.theta),
      itemCount: dim.administered.length,
      theta: dim.theta,
      se: dim.se,
      itemsAdministered: dim.administered.length,
      source: "cat",
    });
  }

  // Aggregate CAT facet thetas into domain scores (inverse-variance weighted)
  const aggregatedDomainIds = new Set<string>();
  if (facetParents) {
    const domainAccum = new Map<string, { wTheta: number; w: number; items: number }>();
    for (const [dimId, dim] of session.dimensions) {
      const parent = facetParents.get(dimId);
      if (!parent || dim.administered.length === 0 || !(dim.se > 0)) continue;
      const w = 1 / (dim.se * dim.se);
      const acc = domainAccum.get(parent) ?? { wTheta: 0, w: 0, items: 0 };
      acc.wTheta += dim.theta * w;
      acc.w += w;
      acc.items += dim.administered.length;
      domainAccum.set(parent, acc);
    }
    for (const [domainId, acc] of domainAccum) {
      if (acc.w <= 0) continue;
      const theta = acc.wTheta / acc.w;
      const se = Math.sqrt(1 / acc.w);
      scores.push({
        scaleId: domainId,
        scaleName: domainId,
        raw: theta,
        normalized: thetaToPercentile(theta),
        itemCount: acc.items,
        theta,
        se,
        itemsAdministered: acc.items,
        source: "cat",
      });
      aggregatedDomainIds.add(domainId);
    }
  }

  // Append fixed-form scores only for scales not covered by CAT, labeled as such
  if (fixedFormScores) {
    const coveredIds = new Set([...session.dimensions.keys(), ...aggregatedDomainIds]);
    for (const score of fixedFormScores) {
      if (!coveredIds.has(score.scaleId)) {
        scores.push({ ...score, source: "fixed-form" });
      }
    }
  }

  return scores;
}
