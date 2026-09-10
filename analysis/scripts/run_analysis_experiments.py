#!/usr/bin/env python3
"""A1-A9: Analysis-only experiments on existing cross-model evaluation data.

No LLM calls. Reads existing run JSON files and computes statistical analyses.
Output: JSON files in experiments/methodology-supplement/
"""

import json
import math
import statistics
from pathlib import Path
from itertools import combinations

RUNS_DIR = Path.home() / "claudeworkspace/psyche/profiles/analysis/runs"
PROFILES = Path.home() / "claudeworkspace/psyche/profiles/analysis"
OUTPUT_DIR = Path.home() / "claudeworkspace/psyche/experiments/methodology-supplement"
DOMAINS = ["N", "E", "O", "A", "C"]
# The subject's merged Big Five ground truth is PRIVATE. It is read at runtime
# from a gitignored file (psyche/benchmark/ground_truth.json — see
# benchmark/.gitignore); the committed fallback is a synthetic midpoint profile
# so this script stays runnable from a public checkout. Anything computed
# against the fallback is a placeholder, not the subject's data.
_GT_FILE = Path.home() / "claudeworkspace/psyche/benchmark/ground_truth.json"
PSYCHE = (json.loads(_GT_FILE.read_text()) if _GT_FILE.exists()
          else {"N": 50.0, "E": 50.0, "O": 50.0, "A": 50.0, "C": 50.0})

KEY_MAP = {
    "neuroticism": "N", "extraversion": "E", "openness": "O",
    "agreeableness": "A", "conscientiousness": "C"
}

FACET_NAMES = {
    "N": ["N1_anxiety", "N2_anger", "N3_depression", "N4_self_consciousness", "N5_impulsiveness", "N6_vulnerability"],
    "E": ["E1_warmth", "E2_gregariousness", "E3_assertiveness", "E4_activity", "E5_excitement_seeking", "E6_positive_emotions"],
    "O": ["O1_fantasy", "O2_aesthetics", "O3_feelings", "O4_actions", "O5_ideas", "O6_values"],
    "A": ["A1_trust", "A2_straightforwardness", "A3_altruism", "A4_compliance", "A5_modesty", "A6_tender_mindedness"],
    "C": ["C1_competence", "C2_order", "C3_dutifulness", "C4_achievement_striving", "C5_self_discipline", "C6_deliberation"],
}


def load_runs(level: str, backend: str) -> list[dict] | None:
    """Load all valid runs for a level/backend, normalizing key names."""
    d = RUNS_DIR / level / backend
    if not d.exists():
        return None
    results = []
    for f in sorted(d.glob("run-*.json")):
        data = json.loads(f.read_text())
        doms = data.get("big_five", {}).get("domains", {})
        scores = {}
        for k, v in doms.items():
            short = KEY_MAP.get(k, k)
            if short in DOMAINS:
                scores[short] = v["score"] if isinstance(v, dict) else v
        if len(scores) == 5 and all(v > 0 for v in scores.values()):
            results.append(scores)
    return results if results else None


def load_facets(level: str, backend: str) -> list[dict] | None:
    """Load facet scores from all valid runs."""
    d = RUNS_DIR / level / backend
    if not d.exists():
        return None
    results = []
    for f in sorted(d.glob("run-*.json")):
        data = json.loads(f.read_text())
        facets = data.get("big_five", {}).get("facets", {})
        if facets:
            normed = {}
            for k, v in facets.items():
                if isinstance(v, dict):
                    normed[k] = v.get("score", v.get("value", 0))
                elif isinstance(v, (int, float)):
                    normed[k] = v
            if normed:
                results.append(normed)
    return results if results else None


def mean_scores(runs: list[dict]) -> dict:
    return {d: sum(r[d] for r in runs) / len(runs) for d in DOMAINS}


def sd_scores(runs: list[dict]) -> dict:
    return {d: statistics.stdev([r[d] for r in runs]) if len(runs) > 1 else 0 for d in DOMAINS}


def ci95(runs: list[dict]) -> dict:
    n = len(runs)
    if n < 2:
        return {d: 0 for d in DOMAINS}
    return {d: 1.96 * statistics.stdev([r[d] for r in runs]) / math.sqrt(n) for d in DOMAINS}


def mean_delta(means: dict, gt: dict) -> float:
    return sum(abs(means[d] - gt[d]) for d in DOMAINS) / len(DOMAINS)


# ============================================================
# A1: Variance Decomposition + ROPE Test
# ============================================================
def a1_variance_decomposition():
    print("A1: Variance decomposition...")
    registers = ["subject-sms", "academic", "messenger", "ai-conv", "mixed"]
    backends = ["claude", "codex"]

    # Collect all individual run scores
    all_data = []  # list of (register, evaluator, domain, score)
    for reg in registers:
        for be in backends:
            runs = load_runs(reg, be)
            if not runs:
                continue
            model = "opus" if be == "claude" else "gpt"
            for run in runs:
                for d in DOMAINS:
                    all_data.append({"register": reg, "evaluator": model, "domain": d, "score": run[d]})

    # Per-domain variance decomposition (simplified: SS between evaluators / SS total)
    result = {"method": "simplified_variance_decomposition", "per_domain": {}}
    for d in DOMAINS:
        d_data = [x for x in all_data if x["domain"] == d]
        grand_mean = sum(x["score"] for x in d_data) / len(d_data)
        ss_total = sum((x["score"] - grand_mean) ** 2 for x in d_data)

        # SS evaluator
        for ev in ["opus", "gpt"]:
            ev_data = [x for x in d_data if x["evaluator"] == ev]
            ev_mean = sum(x["score"] for x in ev_data) / len(ev_data)

        opus_data = [x["score"] for x in d_data if x["evaluator"] == "opus"]
        gpt_data = [x["score"] for x in d_data if x["evaluator"] == "gpt"]
        opus_mean = sum(opus_data) / len(opus_data)
        gpt_mean = sum(gpt_data) / len(gpt_data)
        ss_evaluator = len(opus_data) * (opus_mean - grand_mean) ** 2 + len(gpt_data) * (gpt_mean - grand_mean) ** 2

        # SS register (within each evaluator)
        ss_register = 0
        for ev in ["opus", "gpt"]:
            ev_scores = {reg: [] for reg in registers}
            for x in d_data:
                if x["evaluator"] == ev:
                    ev_scores[x["register"]].append(x["score"])
            ev_mean_all = sum(x["score"] for x in d_data if x["evaluator"] == ev) / sum(1 for x in d_data if x["evaluator"] == ev)
            for reg in registers:
                if ev_scores[reg]:
                    reg_mean = sum(ev_scores[reg]) / len(ev_scores[reg])
                    ss_register += len(ev_scores[reg]) * (reg_mean - ev_mean_all) ** 2

        ss_residual = ss_total - ss_evaluator - ss_register
        eta2_eval = ss_evaluator / ss_total if ss_total > 0 else 0
        eta2_reg = ss_register / ss_total if ss_total > 0 else 0
        eta2_resid = ss_residual / ss_total if ss_total > 0 else 0

        result["per_domain"][d] = {
            "eta2_evaluator": round(eta2_eval, 4),
            "eta2_register": round(eta2_reg, 4),
            "eta2_residual": round(eta2_resid, 4),
            "evaluator_bias": round(gpt_mean - opus_mean, 1),
        }

    # ROPE test on generator effect from replicated 2×2
    gen_effects = []
    for be in ["claude", "codex"]:
        opus_gen = load_runs("subject", be)
        gpt_gen = load_runs("subject-gpt-gen", be)
        if opus_gen and gpt_gen:
            om = mean_scores(opus_gen)
            gm = mean_scores(gpt_gen)
            for d in DOMAINS:
                gen_effects.append(abs(gm[d] - om[d]))

    gen_mean = sum(gen_effects) / len(gen_effects) if gen_effects else 0
    rope_bound = 3.0
    result["rope_test"] = {
        "generator_effect_mean": round(gen_mean, 2),
        "rope_bound": rope_bound,
        "inside_rope": gen_mean < rope_bound,
        "verdict": "NEGLIGIBLE" if gen_mean < rope_bound else "MEANINGFUL",
    }

    return result


# ============================================================
# A2: Evaluator × Register Interaction
# ============================================================
def a2_interaction():
    print("A2: Evaluator × register interaction...")
    registers = ["subject-sms", "academic", "messenger", "ai-conv", "mixed"]
    result = {"per_domain": {}}

    for d in DOMAINS:
        biases = {}
        for reg in registers:
            opus = load_runs(reg, "claude")
            gpt = load_runs(reg, "codex")
            if opus and gpt:
                biases[reg] = round(mean_scores(gpt)[d] - mean_scores(opus)[d], 1)

        vals = list(biases.values())
        mean_bias = sum(vals) / len(vals)
        sd_bias = statistics.stdev(vals) if len(vals) > 1 else 0
        cv = abs(sd_bias / mean_bias * 100) if mean_bias != 0 else 0

        result["per_domain"][d] = {
            "per_register_bias": biases,
            "mean_bias": round(mean_bias, 1),
            "sd_bias": round(sd_bias, 1),
            "cv_percent": round(cv, 1),
            "uniform": cv < 30,
        }

    return result


# ============================================================
# A3: Cross-Register Transportability
# ============================================================
def a3_transportability():
    print("A3: Cross-register transportability...")
    registers = ["subject-sms", "academic", "messenger", "ai-conv", "mixed"]
    profiles = {}
    for reg in registers:
        runs = load_runs(reg, "claude")
        if runs:
            profiles[reg] = mean_scores(runs)

    # Pairwise profile correlation
    matrix = {}
    for r1, r2 in combinations(registers, 2):
        if r1 in profiles and r2 in profiles:
            p1 = [profiles[r1][d] for d in DOMAINS]
            p2 = [profiles[r2][d] for d in DOMAINS]
            m1, m2 = sum(p1) / 5, sum(p2) / 5
            cov = sum((a - m1) * (b - m2) for a, b in zip(p1, p2)) / 5
            sd1 = (sum((a - m1) ** 2 for a in p1) / 5) ** 0.5
            sd2 = (sum((b - m2) ** 2 for b in p2) / 5) ** 0.5
            r = cov / (sd1 * sd2) if sd1 * sd2 > 0 else 0
            matrix[f"{r1}_vs_{r2}"] = round(r, 3)

    mean_r = sum(matrix.values()) / len(matrix) if matrix else 0
    return {
        "pairwise_correlations": matrix,
        "mean_correlation": round(mean_r, 3),
        "interpretation": "HIGH transportability" if mean_r > 0.8 else "MODERATE" if mean_r > 0.5 else "LOW",
    }


# ============================================================
# A4: Post-Hoc Evaluator Calibration
# ============================================================
def a4_calibration():
    print("A4: Evaluator calibration (leave-one-out)...")
    registers = ["subject-sms", "academic", "messenger", "ai-conv", "mixed"]
    result = {"leave_one_out": {}}

    for holdout in registers:
        train_regs = [r for r in registers if r != holdout]
        # Fit bias from training registers
        biases = {d: [] for d in DOMAINS}
        for reg in train_regs:
            opus = load_runs(reg, "claude")
            gpt = load_runs(reg, "codex")
            if opus and gpt:
                om, gm = mean_scores(opus), mean_scores(gpt)
                for d in DOMAINS:
                    biases[d].append(gm[d] - om[d])

        fitted_bias = {d: sum(biases[d]) / len(biases[d]) for d in DOMAINS}

        # Validate on holdout
        opus_ho = load_runs(holdout, "claude")
        gpt_ho = load_runs(holdout, "codex")
        if opus_ho and gpt_ho:
            om_ho, gm_ho = mean_scores(opus_ho), mean_scores(gpt_ho)
            corrected = {d: gm_ho[d] - fitted_bias[d] for d in DOMAINS}
            rmse = (sum((corrected[d] - om_ho[d]) ** 2 for d in DOMAINS) / 5) ** 0.5
            result["leave_one_out"][holdout] = {
                "fitted_bias": {d: round(fitted_bias[d], 1) for d in DOMAINS},
                "corrected_gpt": {d: round(corrected[d], 1) for d in DOMAINS},
                "actual_opus": {d: round(om_ho[d], 1) for d in DOMAINS},
                "rmse": round(rmse, 2),
            }

    rmses = [v["rmse"] for v in result["leave_one_out"].values()]
    result["mean_rmse"] = round(sum(rmses) / len(rmses), 2) if rmses else 0
    result["verdict"] = "CALIBRATABLE" if result["mean_rmse"] < 5 else "INTERACTION_EFFECTS_TOO_LARGE"
    return result


# ============================================================
# A5: CIs on Replicated 2×2 Cells
# ============================================================
def a5_replicated_cis():
    print("A5: Replicated 2×2 CIs...")
    cells = {
        "opus_gen_opus_eval": ("subject", "claude"),
        "opus_gen_gpt_eval": ("subject", "codex"),
        "gpt_gen_opus_eval": ("subject-gpt-gen", "claude"),
        "gpt_gen_gpt_eval": ("subject-gpt-gen", "codex"),
    }
    result = {}
    for label, (level, backend) in cells.items():
        runs = load_runs(level, backend)
        if runs:
            m = mean_scores(runs)
            ci = ci95(runs)
            deltas = [abs(m[d] - PSYCHE[d]) for d in DOMAINS]
            result[label] = {
                "n": len(runs),
                "means": {d: round(m[d], 1) for d in DOMAINS},
                "ci95": {d: round(ci[d], 1) for d in DOMAINS},
                "mean_delta_psyche": round(sum(deltas) / len(deltas), 1),
            }

    # Check overlap between Opus-eval cells
    oo = result.get("opus_gen_opus_eval", {})
    go = result.get("gpt_gen_opus_eval", {})
    if oo and go:
        overlap = {}
        for d in DOMAINS:
            oo_lo = oo["means"][d] - oo["ci95"][d]
            oo_hi = oo["means"][d] + oo["ci95"][d]
            go_lo = go["means"][d] - go["ci95"][d]
            go_hi = go["means"][d] + go["ci95"][d]
            overlap[d] = oo_lo <= go_hi and go_lo <= oo_hi
        result["opus_eval_ci_overlap"] = overlap
        result["generators_indistinguishable"] = all(overlap.values())

    return result


# ============================================================
# A6: Register-Matched Narrative Evaluation
# ============================================================
def a6_register_matched():
    print("A6: Register-matched narrative evaluation...")
    sms_ref = load_runs("subject-sms", "claude")
    if not sms_ref:
        return {"error": "no subject-sms runs"}
    sms_means = mean_scores(sms_ref)

    # Old corpus reference (from prior analysis)
    old_ref = {"N": 51.1, "E": 28.3, "O": 88.6, "A": 36.4, "C": 61.4}

    narrative_files = {
        "old": "narrative-subject-llm-claude.json",
        "1m": "narrative-subject-1m-llm-claude.json",
        "filtered": "narrative-subject-filtered-llm-claude.json",
        "long": "narrative-subject-long-llm-claude.json",
    }

    result = {}
    for label, fname in narrative_files.items():
        p = PROFILES / fname
        if not p.exists():
            continue
        data = json.loads(p.read_text())
        doms = data.get("big_five", {}).get("domains", {})
        scores = {}
        for k, v in doms.items():
            short = KEY_MAP.get(k, k)
            if short in DOMAINS:
                scores[short] = v["score"] if isinstance(v, dict) else v

        if len(scores) == 5:
            delta_old = mean_delta(scores, old_ref)
            delta_sms = mean_delta(scores, sms_means)
            delta_psyche = mean_delta(scores, PSYCHE)
            result[label] = {
                "scores": {d: round(scores[d], 1) for d in DOMAINS},
                "delta_old_corpus_ref": round(delta_old, 1),
                "delta_sms_register_ref": round(delta_sms, 1),
                "delta_psyche": round(delta_psyche, 1),
            }

    result["sms_reference"] = {d: round(sms_means[d], 1) for d in DOMAINS}
    result["old_corpus_reference"] = old_ref
    result["psyche"] = PSYCHE
    return result


# ============================================================
# A7: Bias-Corrected GPT Rankings
# ============================================================
def a7_corrected_rankings():
    print("A7: Bias-corrected GPT rankings...")
    # Mean corpus bias
    registers = ["subject-sms", "academic", "messenger", "ai-conv", "mixed"]
    biases = {d: [] for d in DOMAINS}
    for reg in registers:
        opus = load_runs(reg, "claude")
        gpt = load_runs(reg, "codex")
        if opus and gpt:
            om, gm = mean_scores(opus), mean_scores(gpt)
            for d in DOMAINS:
                biases[d].append(gm[d] - om[d])
    mean_bias = {d: sum(biases[d]) / len(biases[d]) for d in DOMAINS}

    # Load GPT narrative evals and correct
    gpt_narr_files = {
        "old": "narrative-subject-llm-gpt54.json",
        "1m": "narrative-subject-1m-llm-gpt54.json",
    }

    opus_scores = {}
    gpt_scores = {}
    corrected_scores = {}

    for label, fname in gpt_narr_files.items():
        p = PROFILES / fname
        if not p.exists():
            continue
        data = json.loads(p.read_text())
        doms = data["big_five"]["domains"]
        raw = {KEY_MAP.get(k, k): v["score"] if isinstance(v, dict) else v for k, v in doms.items() if KEY_MAP.get(k, k) in DOMAINS}
        gpt_scores[label] = raw
        corrected_scores[label] = {d: round(raw[d] - mean_bias[d], 1) for d in DOMAINS}

    # Load Opus narrative evals for comparison
    opus_narr_files = {
        "old": "narrative-subject-llm-claude.json",
        "1m": "narrative-subject-1m-llm-claude.json",
    }
    for label, fname in opus_narr_files.items():
        p = PROFILES / fname
        if p.exists():
            data = json.loads(p.read_text())
            doms = data["big_five"]["domains"]
            opus_scores[label] = {KEY_MAP.get(k, k): v["score"] if isinstance(v, dict) else v for k, v in doms.items() if KEY_MAP.get(k, k) in DOMAINS}

    result = {
        "mean_corpus_bias": {d: round(mean_bias[d], 1) for d in DOMAINS},
        "conditions": {},
    }
    for label in corrected_scores:
        opus_ref = {"N": 51.1, "E": 28.3, "O": 88.6, "A": 36.4, "C": 61.4}
        delta_raw = mean_delta(gpt_scores[label], opus_ref) if label in gpt_scores else None
        delta_corrected = mean_delta(corrected_scores[label], opus_ref)
        delta_opus = mean_delta(opus_scores[label], opus_ref) if label in opus_scores else None

        result["conditions"][label] = {
            "gpt_raw": {d: round(gpt_scores[label][d], 1) for d in DOMAINS} if label in gpt_scores else None,
            "gpt_corrected": corrected_scores[label],
            "opus": {d: round(opus_scores[label][d], 1) for d in DOMAINS} if label in opus_scores else None,
            "delta_gpt_raw": round(delta_raw, 1) if delta_raw else None,
            "delta_gpt_corrected": round(delta_corrected, 1),
            "delta_opus": round(delta_opus, 1) if delta_opus else None,
        }

    # Check ranking match
    opus_ranking = sorted(opus_scores.keys(), key=lambda l: mean_delta(opus_scores[l], PSYCHE))
    corrected_ranking = sorted(corrected_scores.keys(), key=lambda l: mean_delta(corrected_scores[l], PSYCHE))
    result["opus_ranking"] = opus_ranking
    result["corrected_gpt_ranking"] = corrected_ranking
    result["rankings_match"] = opus_ranking == corrected_ranking

    return result


# ============================================================
# A8: Facet-Level Register + Context Effects
# ============================================================
def a8_facet_effects():
    print("A8: Facet-level register + context effects...")
    registers = ["subject-sms", "academic", "messenger", "ai-conv", "mixed"]
    all_facets = set()
    for flist in FACET_NAMES.values():
        all_facets.update(flist)

    # Per-register facet means (Opus)
    register_facets = {}
    for reg in registers:
        facet_runs = load_facets(reg, "claude")
        if facet_runs:
            means = {}
            for fn in all_facets:
                vals = [r.get(fn, r.get(fn.lower())) for r in facet_runs if fn in r or fn.lower() in r]
                if vals:
                    means[fn] = round(sum(vals) / len(vals), 1)
            register_facets[reg] = means

    # FC vs chunked facet shift (subject-sms)
    chunked_facets = load_facets("subject-sms", "claude")
    fc_facets = load_facets("subject-sms-fullctx", "claude")
    debiased_facets = load_facets("subject-sms-fullctx-debiased", "claude")

    fc_shift = {}
    debiased_shift = {}
    if chunked_facets and fc_facets:
        ch_means = {fn: sum(r.get(fn, 0) for r in chunked_facets) / len(chunked_facets) for fn in all_facets if any(fn in r for r in chunked_facets)}
        fc_means = {fn: sum(r.get(fn, 0) for r in fc_facets) / len(fc_facets) for fn in all_facets if any(fn in r for r in fc_facets)}
        for fn in all_facets:
            if fn in ch_means and fn in fc_means:
                fc_shift[fn] = round(fc_means[fn] - ch_means[fn], 1)

    if chunked_facets and debiased_facets:
        ch_means = {fn: sum(r.get(fn, 0) for r in chunked_facets) / len(chunked_facets) for fn in all_facets if any(fn in r for r in chunked_facets)}
        db_means = {fn: sum(r.get(fn, 0) for r in debiased_facets) / len(debiased_facets) for fn in all_facets if any(fn in r for r in debiased_facets)}
        for fn in all_facets:
            if fn in ch_means and fn in db_means:
                debiased_shift[fn] = round(db_means[fn] - ch_means[fn], 1)

    # Facet-level generator effects from replicated 2×2
    opus_gen_facets = load_facets("subject", "claude")
    gpt_gen_facets = load_facets("subject-gpt-gen", "claude")
    gen_effect = {}
    if opus_gen_facets and gpt_gen_facets:
        og_means = {fn: sum(r.get(fn, 0) for r in opus_gen_facets) / len(opus_gen_facets) for fn in all_facets if any(fn in r for r in opus_gen_facets)}
        gg_means = {fn: sum(r.get(fn, 0) for r in gpt_gen_facets) / len(gpt_gen_facets) for fn in all_facets if any(fn in r for r in gpt_gen_facets)}
        for fn in all_facets:
            if fn in og_means and fn in gg_means:
                gen_effect[fn] = round(gg_means[fn] - og_means[fn], 1)

    return {
        "register_facet_means": register_facets,
        "fc_vs_chunked_shift": fc_shift,
        "debiased_vs_chunked_shift": debiased_shift,
        "generator_effect_replicated": gen_effect,
    }


# ============================================================
# A9: N Genre Effect Quantification
# ============================================================
def a9_genre_effect():
    print("A9: N genre effect quantification...")
    sms = load_runs("subject-sms", "claude")
    narr = load_runs("subject", "claude")

    if sms and narr:
        sms_n = mean_scores(sms)["N"]
        narr_n = mean_scores(narr)["N"]
        gap = narr_n - sms_n
        return {
            "sms_corpus_N": round(sms_n, 1),
            "narrative_N_replicated": round(narr_n, 1),
            "genre_uplift": round(gap, 1),
            "posts_cited_range": "+13 to +20",
            "actual_range_accurate": 13 <= gap <= 20,
            "note": f"Actual genre uplift is +{gap:.1f} which is {'within' if 13 <= gap <= 20 else 'outside'} the cited range"
        }
    return {"error": "missing data"}


# ============================================================
# Main
# ============================================================
def main():
    results = {}

    results["a1_variance_decomposition"] = a1_variance_decomposition()
    results["a2_evaluator_register_interaction"] = a2_interaction()
    results["a3_cross_register_transportability"] = a3_transportability()
    results["a4_evaluator_calibration"] = a4_calibration()
    results["a5_replicated_2x2_cis"] = a5_replicated_cis()
    results["a6_register_matched_evaluation"] = a6_register_matched()
    results["a7_bias_corrected_rankings"] = a7_corrected_rankings()
    results["a8_facet_effects"] = a8_facet_effects()
    results["a9_genre_effect"] = a9_genre_effect()

    # Write individual files
    for key in ["a1_variance_decomposition"]:
        (OUTPUT_DIR / "variance-decomposition.json").write_text(json.dumps(results[key], indent=2))

    interaction_data = {
        "a2_interaction": results["a2_evaluator_register_interaction"],
        "a3_transportability": results["a3_cross_register_transportability"],
    }
    (OUTPUT_DIR / "interaction-analysis.json").write_text(json.dumps(interaction_data, indent=2))

    calibration_data = {
        "a4_calibration": results["a4_evaluator_calibration"],
        "a7_corrected_rankings": results["a7_bias_corrected_rankings"],
    }
    (OUTPUT_DIR / "calibration-analysis.json").write_text(json.dumps(calibration_data, indent=2))

    (OUTPUT_DIR / "replicated-2x2-cis.json").write_text(json.dumps(results["a5_replicated_2x2_cis"], indent=2))
    (OUTPUT_DIR / "register-matched-evaluation.json").write_text(json.dumps(results["a6_register_matched_evaluation"], indent=2))

    # Update facet analysis
    existing_facet = {}
    facet_path = OUTPUT_DIR / "facet-analysis.json"
    if facet_path.exists():
        existing_facet = json.loads(facet_path.read_text())
    existing_facet["a8_register_context_effects"] = results["a8_facet_effects"]
    facet_path.write_text(json.dumps(existing_facet, indent=2))

    # Print summary
    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)

    a1 = results["a1_variance_decomposition"]
    print(f"\nA1: Variance decomposition (eta²)")
    for d in DOMAINS:
        pd = a1["per_domain"][d]
        print(f"  {d}: evaluator={pd['eta2_evaluator']:.3f} register={pd['eta2_register']:.3f} residual={pd['eta2_residual']:.3f}")
    print(f"  ROPE test: generator effect = {a1['rope_test']['generator_effect_mean']:.1f} pts → {a1['rope_test']['verdict']}")

    a2 = results["a2_evaluator_register_interaction"]
    print(f"\nA2: Bias uniformity (CV%)")
    for d in DOMAINS:
        pd = a2["per_domain"][d]
        print(f"  {d}: bias={pd['mean_bias']:+.1f} ±{pd['sd_bias']:.1f} (CV={pd['cv_percent']:.0f}%) {'UNIFORM' if pd['uniform'] else 'VARIABLE'}")

    a3 = results["a3_cross_register_transportability"]
    print(f"\nA3: Cross-register transportability: mean r = {a3['mean_correlation']:.3f} ({a3['interpretation']})")

    a4 = results["a4_evaluator_calibration"]
    print(f"\nA4: Evaluator calibration: mean held-out RMSE = {a4['mean_rmse']:.1f} → {a4['verdict']}")

    a5 = results["a5_replicated_2x2_cis"]
    print(f"\nA5: Generators indistinguishable under Opus eval: {a5.get('generators_indistinguishable', 'N/A')}")

    a6 = results["a6_register_matched_evaluation"]
    print(f"\nA6: Narrative |Δ| vs SMS register ref:")
    for label, data in a6.items():
        if isinstance(data, dict) and "delta_sms_register_ref" in data:
            print(f"  {label}: old_ref={data['delta_old_corpus_ref']:.1f} sms_ref={data['delta_sms_register_ref']:.1f} psyche={data['delta_psyche']:.1f}")

    a7 = results["a7_bias_corrected_rankings"]
    print(f"\nA7: Rankings match after bias correction: {a7['rankings_match']}")

    a9 = results["a9_genre_effect"]
    if "genre_uplift" in a9:
        print(f"\nA9: N genre uplift: {a9['genre_uplift']:+.1f} pts (SMS {a9['sms_corpus_N']} → narrative {a9['narrative_N_replicated']})")
        print(f"  Posts cite '+13 to +20': {'ACCURATE' if a9['actual_range_accurate'] else 'NEEDS CORRECTION'}")

    print(f"\n{'=' * 70}")
    print("Output files written to experiments/methodology-supplement/")


if __name__ == "__main__":
    main()
