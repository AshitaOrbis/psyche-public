/**
 * Graded Response Model (GRM) engine for Computerized Adaptive Testing.
 *
 * Implements Samejima's (1969) GRM for polytomous items (e.g., 5-point Likert).
 * Uses Expected A Posteriori (EAP) estimation over a fixed, equally spaced
 * quadrature grid with normal prior weights (not Gauss-Hermite quadrature).
 *
 * Mathematical basis:
 *   P*(k|θ) = 1 / (1 + exp(-a * (θ - b_k)))
 *   P(X=k|θ) = P*(k|θ) - P*(k+1|θ)  where P*(0)=1, P*(K)=0
 *   I(θ) = a² * Σ_k [P'(X=k|θ)² / P(X=k|θ)]
 */

/** IRT parameters for a single GRM item. */
export interface GRMItem {
  /** Unique item identifier */
  id: string;
  /** Item text for display */
  text: string;
  /** Discrimination parameter (a > 0) */
  discrimination: number;
  /** Threshold parameters [b₁, b₂, ..., b_{K-1}], strictly ordered */
  thresholds: number[];
  /** Number of response categories (e.g., 5 for 1-5 Likert) */
  numCategories: number;
  /** Dimension/facet this item measures */
  dimensionId: string;
  /**
   * Whether to reverse-score this item.
   * Note: In GRM, reverse scoring is metadata for response mapping (flipping
   * the response before computing probabilities). The IRT model handles
   * directionality via the discrimination sign and threshold ordering, so
   * `reverse` is NOT used in the GRM probability computation itself.
   */
  reverse?: boolean;
}

/** Response to a CAT item. */
export interface CATResponse {
  itemId: string;
  /** 0-indexed category (0 = lowest, numCategories-1 = highest) */
  category: number;
}

/** Quadrature point for EAP estimation. */
interface QuadPoint {
  theta: number;
  weight: number;
}

// ── Constants ──────────────────────────────────────────────────

const CLAMP_MIN = 1e-10;
const CLAMP_MAX = 1 - 1e-10;
const QUAD_RANGE = 4.0; // ±4 SD
const QUAD_POINTS = 41;  // Odd for symmetry

// ── Core GRM Functions ─────────────────────────────────────────

/**
 * Cumulative probability P*(k|θ) = 1 / (1 + exp(-a*(θ - b_k))).
 * P*(0) = 1, P*(K) = 0 by convention.
 */
function cumulativeProb(item: GRMItem, theta: number, k: number): number {
  if (k <= 0) return 1.0;
  if (k >= item.numCategories) return 0.0;
  const threshold = item.thresholds[k - 1];
  if (threshold === undefined) return 0.0;
  const z = item.discrimination * (theta - threshold);
  // Numerically stable logistic
  if (z > 30) return 1.0;
  if (z < -30) return 0.0;
  return 1.0 / (1.0 + Math.exp(-z));
}

/**
 * Category probability P(X=k|θ) = P*(k) - P*(k+1).
 * Returns a clamped value in [CLAMP_MIN, CLAMP_MAX].
 */
export function categoryProbability(item: GRMItem, theta: number, category: number): number {
  const pStar = cumulativeProb(item, theta, category);
  const pStarNext = cumulativeProb(item, theta, category + 1);
  return Math.max(CLAMP_MIN, Math.min(CLAMP_MAX, pStar - pStarNext));
}

/**
 * All category probabilities for an item. Normalized to sum to 1.
 */
export function categoryProbabilities(item: GRMItem, theta: number): number[] {
  const probs: number[] = [];
  let sum = 0;
  for (let k = 0; k < item.numCategories; k++) {
    const p = categoryProbability(item, theta, k);
    probs.push(p);
    sum += p;
  }
  // Normalize
  if (sum > 0) {
    for (let i = 0; i < probs.length; i++) {
      probs[i] = probs[i]! / sum;
    }
  }
  return probs;
}

/**
 * Fisher information I(θ) for a single item.
 * Uses numerical approximation via category probabilities.
 *
 * I(θ) = a² * Σ_k [(P*_k(1-P*_k) - P*_{k+1}(1-P*_{k+1}))² / P(X=k)]
 */
export function itemInformation(item: GRMItem, theta: number): number {
  const a = item.discrimination;
  let info = 0;
  for (let k = 0; k < item.numCategories; k++) {
    const pk = categoryProbability(item, theta, k);
    const pStarK = cumulativeProb(item, theta, k);
    const pStarK1 = cumulativeProb(item, theta, k + 1);
    // Derivative terms
    const dPstarK = pStarK * (1 - pStarK);
    const dPstarK1 = pStarK1 * (1 - pStarK1);
    const numerator = (dPstarK - dPstarK1) ** 2;
    info += numerator / pk;
  }
  return a * a * info;
}

/**
 * Total test information at θ for a set of items.
 */
export function testInformation(items: GRMItem[], theta: number): number {
  return items.reduce((sum, item) => sum + itemInformation(item, theta), 0);
}

// ── Theta Estimation ───────────────────────────────────────────

/**
 * Build quadrature grid for EAP estimation.
 * Uses equidistant points with normal prior weights.
 */
function buildQuadGrid(
  priorMean: number,
  priorSD: number,
  nPoints: number = QUAD_POINTS,
  range: number = QUAD_RANGE,
): QuadPoint[] {
  const points: QuadPoint[] = [];
  const lo = priorMean - range * priorSD;
  const hi = priorMean + range * priorSD;
  const step = (hi - lo) / (nPoints - 1);

  let totalWeight = 0;
  for (let i = 0; i < nPoints; i++) {
    const theta = lo + i * step;
    const z = (theta - priorMean) / priorSD;
    const weight = Math.exp(-0.5 * z * z);
    points.push({ theta, weight });
    totalWeight += weight;
  }
  // Normalize weights
  for (const p of points) {
    p.weight /= totalWeight;
  }
  return points;
}

/**
 * Expected A Posteriori (EAP) theta estimation.
 *
 * Computes posterior mean of θ given observed responses and a normal prior.
 * Numerical integration uses the fixed equally spaced grid from buildQuadGrid
 * (normal-prior-weighted), not Gauss-Hermite nodes.
 *
 * Returns { theta, se } where se is the posterior standard deviation.
 */
export function estimateTheta(
  items: GRMItem[],
  responses: CATResponse[],
  priorMean: number = 0,
  priorSD: number = 1,
): { theta: number; se: number } {
  if (responses.length === 0) {
    return { theta: priorMean, se: priorSD };
  }

  const responseMap = new Map<string, number>();
  for (const r of responses) {
    responseMap.set(r.itemId, r.category);
  }

  const grid = buildQuadGrid(priorMean, priorSD);

  // Compute log-likelihood at each quadrature point
  const logLikelihoods: number[] = [];
  let maxLL = -Infinity;

  for (const point of grid) {
    let logL = 0;
    for (const item of items) {
      const cat = responseMap.get(item.id);
      if (cat === undefined) continue;
      const p = categoryProbability(item, point.theta, cat);
      logL += Math.log(p);
    }
    logLikelihoods.push(logL);
    if (logL > maxLL) maxLL = logL;
  }

  // Compute posterior (prior * likelihood) with log-sum-exp for stability
  let posteriorSum = 0;
  let thetaSum = 0;
  let thetaSqSum = 0;

  for (let i = 0; i < grid.length; i++) {
    const point = grid[i]!;
    const logL = logLikelihoods[i]!;
    // posterior ∝ prior_weight * exp(logL - maxLL)
    const posterior = point.weight * Math.exp(logL - maxLL);
    posteriorSum += posterior;
    thetaSum += point.theta * posterior;
    thetaSqSum += point.theta * point.theta * posterior;
  }

  if (posteriorSum === 0) {
    return { theta: priorMean, se: priorSD };
  }

  const thetaHat = thetaSum / posteriorSum;
  const variance = thetaSqSum / posteriorSum - thetaHat * thetaHat;
  const se = Math.sqrt(Math.max(0, variance));

  return { theta: thetaHat, se: se || priorSD };
}

// ── Utility ────────────────────────────────────────────────────

/**
 * Convert IRT theta to 0-100 percentile scale via normal CDF.
 * theta=0 → 50, theta=1 → ~84, theta=-1 → ~16.
 *
 * Uses Abramowitz & Stegun approximation (7-digit accuracy).
 */
export function thetaToPercentile(theta: number): number {
  if (theta < -6) return 0;
  if (theta > 6) return 100;

  const t = 1.0 / (1.0 + 0.2316419 * Math.abs(theta));
  const d = 0.3989422804014327; // 1/sqrt(2π)
  const p = d * Math.exp(-0.5 * theta * theta);
  const poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
  const cdf = theta >= 0 ? 1.0 - p * poly : p * poly;
  return Math.round(cdf * 10000) / 100; // Two decimal places
}

/**
 * Inverse of the standard normal CDF (quantile function).
 * Acklam's rational approximation (relative error < 1.15e-9).
 * Input p is clamped to (1e-10, 1 - 1e-10).
 */
export function inverseNormalCDF(p: number): number {
  const pc = Math.min(1 - 1e-10, Math.max(1e-10, p));

  const a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
    1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00];
  const b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
    6.680131188771972e+01, -1.328068155288572e+01];
  const c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
    -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00];
  const d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
    3.754408661907416e+00];

  const pLow = 0.02425;
  const pHigh = 1 - pLow;

  let q: number;
  let r: number;
  if (pc < pLow) {
    q = Math.sqrt(-2 * Math.log(pc));
    return (((((c[0]! * q + c[1]!) * q + c[2]!) * q + c[3]!) * q + c[4]!) * q + c[5]!) /
      ((((d[0]! * q + d[1]!) * q + d[2]!) * q + d[3]!) * q + 1);
  } else if (pc <= pHigh) {
    q = pc - 0.5;
    r = q * q;
    return (((((a[0]! * r + a[1]!) * r + a[2]!) * r + a[3]!) * r + a[4]!) * r + a[5]!) * q /
      (((((b[0]! * r + b[1]!) * r + b[2]!) * r + b[3]!) * r + b[4]!) * r + 1);
  } else {
    q = Math.sqrt(-2 * Math.log(1 - pc));
    return -(((((c[0]! * q + c[1]!) * q + c[2]!) * q + c[3]!) * q + c[4]!) * q + c[5]!) /
      ((((d[0]! * q + d[1]!) * q + d[2]!) * q + d[3]!) * q + 1);
  }
}

/**
 * Select the most informative item for a given theta from an item bank,
 * excluding already-administered items.
 */
export function selectNextItem(
  bank: GRMItem[],
  theta: number,
  administered: Set<string>,
): GRMItem | null {
  let bestItem: GRMItem | null = null;
  let bestInfo = -Infinity;

  for (const item of bank) {
    if (administered.has(item.id)) continue;
    const info = itemInformation(item, theta);
    if (info > bestInfo) {
      bestInfo = info;
      bestItem = item;
    }
  }
  return bestItem;
}
