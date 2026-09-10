"""Analysis pipeline: compute metrics, halo audit, author comparison, failure cards.

Produces:
- `reports/metrics_{tag}.json` — all quantitative metrics
- `reports/psycheeval_v0_1_{pilot}_{tag}.md` — auto-generated report scaffold
- `reports/failure_cards_{tag}.md` — red-flag-concentrated cases

Metric organization (post-brief §3-§4 restructure):

- `primary_cross_provider` — every response scored by the opposite provider
  family's judge. This is the defensible headline table. C5 is split into
  its own subset because it only exists for public-inspired personas.
- `secondary_all_judges` — the legacy all-judge mean for audit purposes.
  The revised report should NOT put this table in the main body.
- `halo_audit_same_minus_cross` — size of the same-provider halo by
  condition × author.
- `pairwise.cross_provider` — pairwise win-rates and C-pair preferences
  using only cross-provider judges.

Usage:
    uv run python -m psycheeval.analyze --tag 2026-04-20_micro
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

from psycheeval import config
from psycheeval.io import read_jsonl
from psycheeval.models import (
    AnchoredJudgeScore,
    AssistantOutput,
    JudgeScore,
    PairwiseScore,
    PersonaSeed,
    Scenario,
    SynthUserRecord,
)


SCORE_DIMENSIONS = [
    "helpfulness",
    "profile_fit",
    "calibrated_challenge",
    "anti_sycophancy",
    "agency_support",
    "epistemic_hygiene",
    "emotional_accuracy",
    "boundary_safety",
    "non_caricature",
    "transfer_value",
]


# ---------------------------------------------------------------------------
# Wilson confidence interval helpers
# ---------------------------------------------------------------------------

import math


def _wilson_z(confidence: float) -> float:
    """Two-sided z for the requested confidence level (small lookup table)."""
    table = {0.90: 1.6448536269514722, 0.95: 1.959963984540054, 0.99: 2.5758293035489004}
    return table.get(confidence, 1.959963984540054)


def wilson_interval(successes: float, n: int, confidence: float = 0.95) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Accepts non-integer ``successes`` (used for tie-split conventions where
    a tie contributes 0.5 to each side). Returns (low, high) clipped to
    [0, 1].
    """
    if n <= 0:
        return (0.0, 0.0)
    z = _wilson_z(confidence)
    p = successes / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    margin = (z * math.sqrt(max(p * (1.0 - p) / n, 0.0) + z * z / (4.0 * n * n))) / denom
    lo = max(0.0, center - margin)
    hi = min(1.0, center + margin)
    return (round(lo, 4), round(hi, 4))


# ---------------------------------------------------------------------------
#  Native diagnostics ported from the v0.1 Round-2 ad-hoc /tmp scripts.
#  Three blocks: tie rates, PI/PS-stratified pairwise, length-bucketed pairwise.
# ---------------------------------------------------------------------------


def _pair_decision(p: dict, lo_cond: str, hi_cond: str) -> str:
    """For a pair record where conditions are {lo_cond, hi_cond} in some
    order, return whether the *low-numbered* condition won, lost, or tied.
    Returns "lo" / "hi" / "tie"."""
    winner = p["ps"].winner
    if winner == "tie":
        return "tie"
    if winner == "A":
        return "lo" if p["cond_a"] == lo_cond else "hi"
    if winner == "B":
        return "lo" if p["cond_b"] == lo_cond else "hi"
    return "tie"  # unknown winner string treated as tie defensively


def _ordered_pair(cond_a: str, cond_b: str) -> tuple[str, str]:
    """Sort condition pair so (lo, hi) is canonical regardless of A/B order."""
    return tuple(sorted([cond_a, cond_b]))


def _compute_condition_discoverability(
    outputs: list,
    *,
    test_frac: float = 0.3,
    seed: int = 20260516,
    min_per_class: int = 5,
) -> dict | None:
    """Train a cheap TF-IDF + logistic classifier on response text to predict
    condition from output alone. If accuracy is high, judges may be rewarding
    detectable treatment markers (e.g. "given your profile") rather than
    actual quality.

    Source: 2026-05-15 review (GPT-Pro §A17, consolidated §3.1 #L). If
    output text predicts condition with high accuracy, the pairwise
    preference may be partly a recognition-of-treatment effect.

    Returns None if sklearn not available or sample too sparse.
    """
    try:
        import random as _random
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, classification_report
        from collections import Counter
    except ImportError:
        return None

    texts: list[str] = []
    labels: list[str] = []
    for o in outputs:
        text = (o.assistant_response or "").strip()
        if not text:
            continue
        cond = str(o.condition)
        texts.append(text)
        labels.append(cond)
    if not texts:
        return None

    label_counts = Counter(labels)
    # Filter classes with too few samples
    eligible_classes = {c for c, n in label_counts.items() if n >= min_per_class}
    if len(eligible_classes) < 2:
        return None
    keep_idx = [i for i, c in enumerate(labels) if c in eligible_classes]
    X_text = [texts[i] for i in keep_idx]
    y = [labels[i] for i in keep_idx]

    rng = _random.Random(seed)
    indices = list(range(len(X_text)))
    rng.shuffle(indices)
    split_pt = int(len(indices) * (1 - test_frac))
    train_idx = indices[:split_pt]
    test_idx = indices[split_pt:]
    X_train_text = [X_text[i] for i in train_idx]
    X_test_text = [X_text[i] for i in test_idx]
    y_train = [y[i] for i in train_idx]
    y_test = [y[i] for i in test_idx]

    vec = TfidfVectorizer(ngram_range=(1, 2), max_features=5000, min_df=2)
    X_train = vec.fit_transform(X_train_text)
    X_test = vec.transform(X_test_text)

    clf = LogisticRegression(max_iter=1000, random_state=seed)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    n_classes = len(eligible_classes)
    chance = 1 / n_classes

    # Per-class precision/recall via classification_report
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    # Top discriminative features per class
    feature_names = vec.get_feature_names_out()
    top_features: dict[str, list[str]] = {}
    if hasattr(clf, "coef_"):
        for i, cls in enumerate(clf.classes_):
            if clf.coef_.shape[0] == 1:
                # binary: only one row
                coef = clf.coef_[0] if cls == clf.classes_[1] else -clf.coef_[0]
            else:
                coef = clf.coef_[i]
            top_idx = coef.argsort()[-10:][::-1]
            top_features[cls] = [feature_names[j] for j in top_idx]

    return {
        "n_train": len(X_train_text),
        "n_test": len(X_test_text),
        "n_classes": n_classes,
        "classes": sorted(eligible_classes),
        "test_accuracy": round(float(acc), 4),
        "chance_baseline": round(chance, 4),
        "accuracy_above_chance_pp": round(float(acc) - chance, 4),
        "per_class_f1": {
            cls: round(report.get(cls, {}).get("f1-score", 0.0), 4)
            for cls in sorted(eligible_classes)
        },
        "top_features_per_class": top_features,
        "interpretation_note": (
            "If test_accuracy >> chance_baseline, output text leaks condition. "
            "Pairwise judges may be partly recognizing condition cues rather than "
            "evaluating intrinsic quality. The top_features per class show what "
            "phrases discriminate each condition's outputs."
        ),
    }


def _compute_missingness_balance_audit(
    outputs: list,
    anchored_scores: list,
    pair_tagged_same_author: list[dict],
    users,
    scenarios,
) -> dict:
    """Missingness and balance audit per consolidated review §3.1 #11.

    Reports:
      - Anchored scalar record counts by (condition × author × judge × persona × family)
      - Empty-cell count (cells with 0 records)
      - Complete-case scalar subset count (outputs scored by ALL 3 judges)
      - Pairwise record counts by (condition pair × author × judge × family)
      - Balance index per dimension (variance of cell counts)
    """
    from collections import Counter, defaultdict

    # Index outputs by run_id
    out_by_run = {o.run_id: o for o in outputs}

    # Anchored scalar: count by (output_run_id, judge)
    scored_by_run: dict[str, set[str]] = defaultdict(set)
    for s in anchored_scores:
        rid = getattr(s, "run_id", None)
        jm = getattr(s, "judge_model", None)
        if rid and jm:
            scored_by_run[rid].add(jm)

    # Cell counts (anchored): condition × author × judge × persona × family
    anchored_cell_counts: dict[tuple, int] = Counter()
    for s in anchored_scores:
        rid = getattr(s, "run_id", None)
        if not rid:
            continue
        o = out_by_run.get(rid)
        if not o:
            continue
        scn = scenarios.get(o.scenario_id)
        fam = str(getattr(scn, "scenario_family", None)) if scn else None
        key = (str(o.condition), o.output_model, s.judge_model, o.user_id, fam)
        anchored_cell_counts[key] += 1

    # Complete-case subset: how many outputs were scored by all judges that
    # appear anywhere in the data?
    all_judges = sorted({getattr(s, "judge_model", None) for s in anchored_scores if getattr(s, "judge_model", None)})
    n_outputs_total = len(outputs)
    n_outputs_complete_case = sum(
        1 for o in outputs if all_judges and scored_by_run.get(o.run_id, set()) == set(all_judges)
    )

    # Pairwise cell counts
    pairwise_cell_counts: dict[tuple, int] = Counter()
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        scn = scenarios.get(p["ps"].scenario_id)
        fam = str(getattr(scn, "scenario_family", None)) if scn else None
        key = (f"{lo}_vs_{hi}", p["author_a"], p["ps"].judge_model, fam)
        pairwise_cell_counts[key] += 1

    # Balance: per dimension, summary stats of cell counts
    def _balance_stats(counts: list[int]) -> dict:
        if not counts:
            # Shape parity with the populated branch (bq-1008): this branch used to omit
            # the empty-cell keys entirely, so a consumer doing `stats.get("n_empty_cells", 0)`
            # got 0 here too — the same false zero by a different route, and a consumer
            # checking the computability flag would have silently defaulted to "computable".
            return {"n_cells": 0, "n_empty_cells": 0, "n_empty_cells_computable": False,
                    "min": None, "max": None, "mean": None}
        return {
            "n_cells": len(counts),
            # bq-1008: THIS ZERO IS NOT A MEASUREMENT. `counts` is built from OBSERVED
            # records, so a cell with zero records never enters it — the value is
            # therefore hardcoded and can never be anything but 0, under a docstring
            # (see _compute_missingness_balance_audit) that advertises "Empty-cell count
            # (cells with 0 records)". A check whose output is indistinguishable from
            # success because it IS the success value.
            #
            # Kept at 0 rather than removed or set to None so existing consumers do not
            # break on a type change; the companion flag below is the honest half, and is
            # what any consumer should branch on. Absence cannot be derived from the
            # observations alone — the real fix is to construct the EXPECTED cell set from
            # the frozen run manifest, pilot definitions, requested authors/judges and
            # pair scope, then compare observed counts against it. That is bq-1008 proper
            # and is deliberately not attempted here.
            "n_empty_cells": 0,
            "n_empty_cells_computable": False,
            "min": min(counts),
            "max": max(counts),
            "mean": round(sum(counts) / len(counts), 2),
            "max_min_ratio": round(max(counts) / max(min(counts), 1), 2),
        }

    return {
        "anchored_scalar": {
            "n_total_records": len(anchored_scores),
            "n_unique_outputs": len(scored_by_run),
            "n_total_outputs": n_outputs_total,
            "n_complete_case_outputs": n_outputs_complete_case,
            "complete_case_rate": round(n_outputs_complete_case / n_outputs_total, 4) if n_outputs_total else None,
            "all_judges_observed": list(all_judges),
            "cell_balance_stats": _balance_stats(list(anchored_cell_counts.values())),
            "n_unique_cells": len(anchored_cell_counts),
        },
        "pairwise": {
            "n_total_same_author_records": len(pair_tagged_same_author),
            "cell_balance_stats": _balance_stats(list(pairwise_cell_counts.values())),
            "n_unique_cells": len(pairwise_cell_counts),
        },
    }


def _compute_rubric_lexical_overlap(
    profile_bundles_path,
    rubric_prompt_path,
) -> dict:
    """Compute token-level overlap between each condition's profile text
    and the anchored-rubric anchor language.

    Source: 2026-05-15 review consolidated §3.1 #9 (codex-council, GPT-Pro
    §A16). If a condition's prompt text vocabulary heavily overlaps the
    rubric's anchor language, judges may reward "rubric-matching prose"
    rather than actual quality. Quantify per-condition Jaccard overlap.

    Returns: { condition_key: {
                 n_tokens, n_rubric_overlap_tokens, jaccard_score,
                 top_overlapping_tokens
               } }
    """
    import re
    from pathlib import Path

    try:
        bundles = [json.loads(l) for l in open(profile_bundles_path)]
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    try:
        rubric_text = Path(rubric_prompt_path).read_text()
    except FileNotFoundError:
        return {}

    # Tokenize: lowercase, alphanumeric only, length >= 4
    def _tokens(text: str) -> set[str]:
        if not text:
            return set()
        toks = re.findall(r"\b[a-z]{4,}\b", text.lower())
        # Drop very common English words
        STOP = {"this", "that", "with", "from", "have", "your", "they",
                "their", "would", "could", "should", "about", "when",
                "what", "which", "where", "more", "into", "than", "then",
                "some", "such", "those", "these", "been", "were", "will",
                "also", "also", "very", "only", "much", "must", "even",
                "user", "the", "and", "for", "but", "not", "you"}
        return {t for t in toks if t not in STOP}

    rubric_toks = _tokens(rubric_text)
    out: dict[str, dict] = {}
    # Aggregate across the 8 personas: union of condition texts
    cond_token_counts: dict[str, dict[str, int]] = {}
    for b in bundles:
        pc = b.get("profile_conditions", {})
        for cond_key, cond_val in pc.items():
            if not isinstance(cond_val, dict):
                continue
            text = cond_val.get("profile_text") or ""
            toks = _tokens(text)
            tc = cond_token_counts.setdefault(cond_key, {})
            for t in toks:
                tc[t] = tc.get(t, 0) + 1

    for cond_key, tc in cond_token_counts.items():
        cond_toks = set(tc.keys())
        intersection = cond_toks & rubric_toks
        union = cond_toks | rubric_toks
        jaccard = len(intersection) / len(union) if union else 0.0
        # Top overlapping tokens by frequency across personas
        top = sorted(
            [(t, tc[t]) for t in intersection],
            key=lambda kv: -kv[1],
        )[:10]
        out[cond_key] = {
            "n_unique_tokens_in_condition": len(cond_toks),
            "n_unique_tokens_in_rubric": len(rubric_toks),
            "n_overlapping_tokens": len(intersection),
            "jaccard_score": round(jaccard, 4),
            "overlap_share_of_condition": round(len(intersection) / len(cond_toks), 4) if cond_toks else 0.0,
            "top_overlapping_tokens": [t for t, _ in top],
        }
    return dict(sorted(out.items()))


def _compute_macro_vs_micro_aggregation(
    pair_tagged_same_author: list[dict],
    scenarios,
) -> dict:
    """Macro-vs-micro aggregation comparison for every headline pair.

    Source: 2026-05-15 review consolidated §3.1 #10 (GPT-Pro §A2). The
    current pooled micro-average across records (per-judge, per-author,
    per-persona × scenario) gives more weight to strata with more pairs.
    Compute the same pair lo_win as:

      - micro: existing record-level (status quo)
      - macro-judge: average over per-judge lo_win rates
      - macro-author: average over per-author lo_win rates
      - macro-persona: average over per-persona lo_win rates
      - macro-family: average over per-scenario-family lo_win rates
      - macro-cell: average over (judge × author × persona × family) cells

    Flag pairs where macro differs from micro by >5 percentage points
    (suggests result is driven by record imbalance not phenomenon).
    """
    # For each pair, group by various strata
    per_pair_strata: dict[tuple[str, str], dict] = {}

    def _get_family(p):
        scn = scenarios.get(p["ps"].scenario_id)
        return str(getattr(scn, "scenario_family", None)) if scn else None

    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        d = _pair_decision(p, lo, hi)
        if d not in ("lo", "hi"):
            continue
        bucket = per_pair_strata.setdefault((lo, hi), {
            "by_judge": {},
            "by_author": {},
            "by_persona": {},
            "by_family": {},
            "by_cell": {},
            "total_lo": 0,
            "total_dec": 0,
        })
        bucket["total_dec"] += 1
        if d == "lo":
            bucket["total_lo"] += 1
        for stratum_key, value in [
            ("by_judge", p["ps"].judge_model),
            ("by_author", p["author_a"]),
            ("by_persona", p["out_a"].user_id),
            ("by_family", _get_family(p)),
        ]:
            if value is None:
                continue
            s = bucket[stratum_key].setdefault(value, {"lo": 0, "dec": 0})
            s["dec"] += 1
            if d == "lo":
                s["lo"] += 1
        # cell: (judge, author, persona, family)
        cell_key = (p["ps"].judge_model, p["author_a"], p["out_a"].user_id, _get_family(p))
        s = bucket["by_cell"].setdefault(cell_key, {"lo": 0, "dec": 0})
        s["dec"] += 1
        if d == "lo":
            s["lo"] += 1

    out: dict[str, dict] = {}
    for (lo, hi), b in per_pair_strata.items():
        micro = b["total_lo"] / b["total_dec"] if b["total_dec"] else None

        def _macro_avg(stratum_dict):
            rates = []
            for v in stratum_dict.values():
                if v["dec"] > 0:
                    rates.append(v["lo"] / v["dec"])
            return sum(rates) / len(rates) if rates else None

        macros = {
            "macro_judge": _macro_avg(b["by_judge"]),
            "macro_author": _macro_avg(b["by_author"]),
            "macro_persona": _macro_avg(b["by_persona"]),
            "macro_family": _macro_avg(b["by_family"]),
            "macro_cell": _macro_avg(b["by_cell"]),
        }
        # Flag if any macro differs from micro by >5pp
        flags = []
        if micro is not None:
            for k, m in macros.items():
                if m is not None and abs(m - micro) >= 0.05:
                    flags.append(k)
        out[f"{lo}_vs_{hi}"] = {
            "n_decisive": b["total_dec"],
            "micro_lo_decisive_win_rate": round(micro, 4) if micro is not None else None,
            **{k: round(v, 4) if v is not None else None for k, v in macros.items()},
            "n_judge_strata": len(b["by_judge"]),
            "n_author_strata": len(b["by_author"]),
            "n_persona_strata": len(b["by_persona"]),
            "n_family_strata": len(b["by_family"]),
            "n_cell_strata": len(b["by_cell"]),
            "macros_that_disagree_with_micro_by_5pp": flags,
        }
    return dict(sorted(out.items()))


def _compute_ab_ba_position_audit(
    pair_tagged_same_author: list[dict],
    swap_records: list,
) -> dict:
    """AB/BA counterbalanced rejudge analysis (Phase 1.5).

    Source: 2026-05-15 review (unanimous: "cheapest decisive experiment").
    For each pair-of-outputs that has BOTH an original and a swapped-order
    pairwise judgment from the same judge, compute:

      - n_pairs_with_both: AB/BA-matched coverage
      - position_consistent: judgments agree on which output wins (regardless
        of slot — true condition preference)
      - position_flip: original says A wins, swap says B wins (so the
        physical slot stayed the same — slot effect)
      - lo_wins_in_original / lo_wins_in_swap / position_controlled_lo_win
      - condition_preference_strength (vs position-bias-only null)

    Joins via the run_id-swap signature: original (run_a=X, run_b=Y, judge=J)
    has its swap as the record with (run_a=Y, run_b=X, judge=J).
    """
    # Build index: (scenario_id, run_a, run_b, judge_model) → swap record
    swap_idx: dict[tuple[str, str, str, str], object] = {}
    for s in swap_records:
        key = (s.scenario_id, s.run_id_a, s.run_id_b, s.judge_model)
        swap_idx[key] = s

    # For each original record, find its swap and analyze
    per_pair: dict[tuple[str, str], dict] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        orig = p["ps"]
        # The swap has run_a/run_b reversed
        swap_key = (orig.scenario_id, orig.run_id_b, orig.run_id_a, orig.judge_model)
        swap = swap_idx.get(swap_key)
        if swap is None:
            # Try resolved-id variant for robustness
            continue

        # Determine which condition was lo in the original
        # If cond_a == lo → original slot A holds lo
        # In swap, run_a/run_b are reversed, so slot A holds hi
        lo_in_orig_slot_a = (p["cond_a"] == lo)

        orig_winner = orig.winner  # "A" | "B" | "tie"
        swap_winner = swap.winner

        # Translate to which CONDITION won
        def _cond_winner(winner, lo_in_a):
            if winner == "tie":
                return "tie"
            if winner == "A":
                return lo if lo_in_a else hi
            else:  # B
                return hi if lo_in_a else lo

        orig_cond_winner = _cond_winner(orig_winner, lo_in_orig_slot_a)
        swap_cond_winner = _cond_winner(swap_winner, not lo_in_orig_slot_a)

        # Position-bias classification
        # - position_consistent: both judgments agree on CONDITION winner
        #   (true condition preference, independent of slot)
        # - position_flip: judgments disagree on CONDITION winner (the same
        #   physical slot won both times — slot effect)
        if orig_cond_winner == "tie" or swap_cond_winner == "tie":
            cat = "either_tie"
        elif orig_cond_winner == swap_cond_winner:
            cat = "position_consistent"  # condition preference
        else:
            cat = "position_flip"  # slot bias

        bucket = per_pair.setdefault((lo, hi), {
            "n_pairs_with_both": 0,
            "n_position_consistent": 0,
            "n_position_flip": 0,
            "n_either_tie": 0,
            "n_orig_lo_wins": 0,
            "n_orig_hi_wins": 0,
            "n_orig_ties": 0,
            "n_swap_lo_wins": 0,
            "n_swap_hi_wins": 0,
            "n_swap_ties": 0,
            # Position-controlled: for each pair, count lo-wins-across-both
            # (each pair gets 0, 0.5, or 1 vote for lo)
            "sum_lo_wins_controlled": 0.0,
            "n_decisive_pairs": 0,  # at least one decisive call across orig+swap
        })
        bucket["n_pairs_with_both"] += 1
        if cat == "position_consistent":
            bucket["n_position_consistent"] += 1
        elif cat == "position_flip":
            bucket["n_position_flip"] += 1
        else:
            bucket["n_either_tie"] += 1

        # Original count
        if orig_cond_winner == lo:
            bucket["n_orig_lo_wins"] += 1
        elif orig_cond_winner == hi:
            bucket["n_orig_hi_wins"] += 1
        else:
            bucket["n_orig_ties"] += 1
        # Swap count
        if swap_cond_winner == lo:
            bucket["n_swap_lo_wins"] += 1
        elif swap_cond_winner == hi:
            bucket["n_swap_hi_wins"] += 1
        else:
            bucket["n_swap_ties"] += 1

        # Position-controlled lo win rate: each pair contributes lo_share
        # = (lo_wins_in_orig + lo_wins_in_swap) / 2 (counting ties as 0.5)
        def _lo_score(cond_winner):
            if cond_winner == lo:
                return 1.0
            if cond_winner == hi:
                return 0.0
            return 0.5
        lo_score = (_lo_score(orig_cond_winner) + _lo_score(swap_cond_winner)) / 2.0
        bucket["sum_lo_wins_controlled"] += lo_score
        # Count "decisive" if at least one is non-tie
        if orig_cond_winner != "tie" or swap_cond_winner != "tie":
            bucket["n_decisive_pairs"] += 1
        # 2026-05-17 review-fix: collect per-pair record with cluster key for
        # bootstrap CI. Cluster unit matches `_compute_cluster_bootstrap_pairwise`.
        bucket.setdefault("records", []).append({
            "lo_score": lo_score,
            "cluster": (p["out_a"].user_id, p["ps"].scenario_id, p["author_a"]),
            "judge_model": p["ps"].judge_model,
            "judge_family": p["judge_family"],
            "author_a_family": p["author_a_family"],
            "orig_cond_winner": orig_cond_winner,
            "swap_cond_winner": swap_cond_winner,
            "category": cat,
        })

    out: dict[str, dict] = {}
    for (lo, hi), b in per_pair.items():
        n = b["n_pairs_with_both"]
        position_consistent_rate = (
            b["n_position_consistent"] / n if n else None
        )
        position_flip_rate = (
            b["n_position_flip"] / n if n else None
        )
        orig_decisive = b["n_orig_lo_wins"] + b["n_orig_hi_wins"]
        swap_decisive = b["n_swap_lo_wins"] + b["n_swap_hi_wins"]
        orig_lo_wr = b["n_orig_lo_wins"] / orig_decisive if orig_decisive else None
        swap_lo_wr = b["n_swap_lo_wins"] / swap_decisive if swap_decisive else None
        # Slot A wins in original = lo_wins (because lo was in slot A in all originals)
        # Slot A wins in swap = hi_wins (because hi is in slot A in swap)
        # So slot-A win rate across BOTH = (orig_lo_wins + swap_hi_wins) / (orig_dec + swap_dec)
        total_decisive = orig_decisive + swap_decisive
        slot_a_total_wins = b["n_orig_lo_wins"] + b["n_swap_hi_wins"]
        slot_a_win_rate = slot_a_total_wins / total_decisive if total_decisive else None
        # Position-controlled: average over (orig + swap)
        controlled_lo_wr = b["sum_lo_wins_controlled"] / n if n else None
        # Wilson on controlled-lo-decisive (kept for backward compat; rough
        # for matched-pair data — see Wilson note below).
        wci_lo, wci_hi = wilson_interval(round(b["sum_lo_wins_controlled"]), n) if n else (None, None)

        # 2026-05-17 review-fix: cluster bootstrap CI on controlled lo win rate.
        # Round-2 reviewers (4-way unanimous) flagged that Wilson on rounded
        # sum is mis-specified for matched-pair clustered data. Bootstrap by
        # cluster (persona × scenario × author), recompute mean lo_score per
        # resample. Matches the convention in `_compute_cluster_bootstrap_pairwise`.
        records = b.get("records", [])
        boot_ci_lo = boot_ci_hi = None
        if records:
            import random as _random
            # Group records by cluster
            cluster_map: dict[tuple, list[float]] = {}
            for r in records:
                cluster_map.setdefault(r["cluster"], []).append(r["lo_score"])
            cluster_keys = list(cluster_map.keys())
            n_clusters = len(cluster_keys)
            if n_clusters >= 5:
                rng = _random.Random(20260517)
                boot_rates: list[float] = []
                for _ in range(2000):
                    sampled = [cluster_keys[rng.randrange(n_clusters)] for _ in range(n_clusters)]
                    s_sum = 0.0
                    s_n = 0
                    for k in sampled:
                        for ls in cluster_map[k]:
                            s_sum += ls
                            s_n += 1
                    if s_n:
                        boot_rates.append(s_sum / s_n)
                if boot_rates:
                    boot_rates.sort()
                    boot_ci_lo = round(boot_rates[int(0.025 * len(boot_rates))], 4)
                    boot_ci_hi = round(boot_rates[int(0.975 * len(boot_rates)) - 1], 4)

        # Headline survives swap: use BOOTSTRAP CI if available, else fall back to Wilson
        ci_lo_for_test = boot_ci_lo if boot_ci_lo is not None else wci_lo
        ci_hi_for_test = boot_ci_hi if boot_ci_hi is not None else wci_hi
        survives = (
            ci_lo_for_test is not None and (
                (orig_lo_wr is not None and orig_lo_wr > 0.5 and ci_lo_for_test > 0.5)
                or (orig_lo_wr is not None and orig_lo_wr < 0.5 and ci_hi_for_test < 0.5)
            )
        )

        out[f"{lo}_vs_{hi}"] = {
            "n_pairs_with_ab_ba": n,
            "position_consistent_rate": round(position_consistent_rate, 4) if position_consistent_rate is not None else None,
            "position_flip_rate": round(position_flip_rate, 4) if position_flip_rate is not None else None,
            "n_position_consistent": b["n_position_consistent"],
            "n_position_flip": b["n_position_flip"],
            "n_either_tie": b["n_either_tie"],
            "original_lo_win_rate": round(orig_lo_wr, 4) if orig_lo_wr is not None else None,
            "swapped_lo_win_rate": round(swap_lo_wr, 4) if swap_lo_wr is not None else None,
            "position_controlled_lo_win_rate": round(controlled_lo_wr, 4) if controlled_lo_wr is not None else None,
            "controlled_wilson_ci95_low": wci_lo,
            "controlled_wilson_ci95_high": wci_hi,
            "controlled_bootstrap_ci95_low": boot_ci_lo,
            "controlled_bootstrap_ci95_high": boot_ci_hi,
            "n_clusters": len(set(r["cluster"] for r in records)) if records else 0,
            "slot_a_win_rate_across_orders": round(slot_a_win_rate, 4) if slot_a_win_rate is not None else None,
            "headline_survives_swap": survives,
            "headline_survives_swap_estimator": "bootstrap" if boot_ci_lo is not None else "wilson",
        }
    return dict(sorted(out.items()))


# Claim ledger structure: per-claim metadata for the curated report.
# Source: 2026-05-17 consolidated round-2 review §2.3 (unanimous: claim ledger
# is the report's central artifact). Tier assignment incorporates round-2
# verdicts including the joint position×length finding for C4 vs C5.
CLAIM_LEDGER_SCHEMA = [
    {
        "claim_id": "tier1_c5contract_gt_c5",
        "pair_key": "C5_vs_C5_CONTRACT",
        "tier": "1",
        "headline": "C5_CONTRACT > C5",
        "allowed_wording": "The contract-supplemented source-packet package (C5_CONTRACT) outperforms the bare source-packet condition (C5) under position-controlled judging. Robust across Phase 0 audits (judge-unanimous, persona-robust, family-robust, scalar-aligned) and survives joint position+length correction. Mechanism not isolated — see v0.3.",
        "forbidden_wording": "contract repairs source-packet fragility; source packets add value when subordinated to contracts; mechanism isolated.",
        "judge_scope": "all three judges (gpt-5.4, gpt-5.5, opus)",
        "author_scope": "all three authors (PI personas only — C5 is PI-only)",
        "evidence_paths": ["ab_ba_position_audit_same_author", "ab_ba_joint_position_length_same_author", "scalar_pairwise_reconciliation_same_author", "ab_ba_position_audit_same_author_by_judge"],
    },
    {
        "claim_id": "tier1_c4_gt_c1padded",
        "pair_key": "C1_padded_vs_C4",
        "tier": "1",
        "headline": "C4 > C1_padded",
        "allowed_wording": "Behavioral contract (C4) outperforms length-matched baseline (C1_padded) under position-controlled judging. Length-control + position-control both pass.",
        "forbidden_wording": "(none specific to this claim)",
        "judge_scope": "gpt-5.4 + gpt-5.5 (Opus has 0 records on this pair)",
        "author_scope": "all three authors",
        "evidence_paths": ["ab_ba_position_audit_same_author", "scalar_pairwise_reconciliation_same_author"],
    },
    {
        "claim_id": "tier1_5_c4_gt_c4shuffled",
        "pair_key": "C4_vs_C4_shuffled",
        "tier": "1.5",
        "headline": "C4 > C4_shuffled (modest effect)",
        "allowed_wording": "Coherent-order C4 modestly outperforms shuffled-order C4 under position-controlled judging. Sign-corrected from Phase 0 (original 51.9% headline was understating because slot-A bias hurt C4 in slot A). Effect size (~58%) is meaningfully smaller than the C4 > C1_padded and C5_CONTRACT > C5 findings.",
        "forbidden_wording": "Coherent structure does not significantly beat shuffled; coherent structure significantly beats shuffled (over-strong wording either direction).",
        "judge_scope": "gpt-5.4 + gpt-5.5 (Opus has 0 records on this pair)",
        "author_scope": "all three authors",
        "evidence_paths": ["ab_ba_position_audit_same_author", "scalar_pairwise_reconciliation_same_author"],
    },
    {
        "claim_id": "tier1_c4_gt_c5",
        "pair_key": "C4_vs_C5",
        "tier": "1",
        "headline": "C4 > C5",
        "allowed_wording": "Behavioral contract (C4) outperforms source-packet-without-contract (C5) under position-controlled judging at 68.0% [61.5, 74.4]. Judge-unanimous across all three judges (gpt-5.4, gpt-5.5, opus). Survives joint position+length correction (length-matched subset n=76, controlled 67.4% [54.7, 79.5] — CI excludes 0.5 on the C4 side). Opus AB/BA fill (2026-05-17 Phase 2 hygiene pass) closed the original scope gap.",
        "forbidden_wording": "(none specific to this claim after Opus fill).",
        "judge_scope": "all three judges (gpt-5.4, gpt-5.5, opus) — Opus added 2026-05-17",
        "author_scope": "all three authors (PI personas only — C5 is PI-only)",
        "evidence_paths": ["ab_ba_position_audit_same_author", "ab_ba_position_audit_same_author_by_judge", "ab_ba_joint_position_length_same_author", "scalar_pairwise_reconciliation_same_author"],
    },
    {
        "claim_id": "tier1_c0_dominated",
        "pair_key": "C0_vs_C4",
        "tier": "1",
        "headline": "C0 dominated by profile conditions",
        "allowed_wording": "Baseline (C0) is dominated by any profile-conditioned condition. Effect size is large (~86% C4-over-C0 in original pairwise + Δ_total +6.075 in scalar). Not AB/BA-tested directly; the magnitude is well outside the measured ~15-17pp slot-B preference range so likely robust to position-bias correction.",
        "forbidden_wording": "AB/BA-controlled (not directly tested).",
        "judge_scope": "all three judges (original pairwise + scalar)",
        "author_scope": "all three authors",
        "evidence_paths": ["pairwise.win_rate_cross_provider_same_author", "scalar_pairwise_reconciliation_same_author"],
    },
    {
        "claim_id": "tier2_c5contract_vs_c3",
        "pair_key": "C3_vs_C5_CONTRACT",
        "tier": "2",
        "headline": "C5_CONTRACT vs C3 — no detected preference",
        "allowed_wording": "Under position-controlled (AB/BA) judging, we do not detect a reliable pairwise preference between C5_CONTRACT and C3 (controlled C5_CONTRACT win rate 49.9% [44.3, 55.7]). Scalar scores also do not favor C5_CONTRACT (Δ_total −0.053). The original 57.2% C5_CONTRACT win rate was carried entirely by slot-B position bias.",
        "forbidden_wording": "C5_CONTRACT outperforms C3; C5_CONTRACT equivalent to C3 (no equivalence margin pre-declared).",
        "judge_scope": "all three judges",
        "author_scope": "all three authors (PI personas only)",
        "evidence_paths": ["ab_ba_position_audit_same_author", "scalar_pairwise_reconciliation_same_author", "ab_ba_by_provider_scope_same_author"],
    },
    {
        "claim_id": "tier2_c5contract_vs_c4",
        "pair_key": "C4_vs_C5_CONTRACT",
        "tier": "2",
        "headline": "C5_CONTRACT vs C4 — no detected preference",
        "allowed_wording": "Under position-controlled (AB/BA) judging, we do not detect a reliable pairwise preference between C5_CONTRACT and C4 (controlled C5_CONTRACT win rate 51.8% [46.0, 57.5]). Scalar scores slightly favor C4 (Δ_total −0.231). The original 60.0% C5_CONTRACT win rate was carried entirely by slot-B position bias.",
        "forbidden_wording": "C5_CONTRACT outperforms C4; C5_CONTRACT equivalent to C4.",
        "judge_scope": "all three judges",
        "author_scope": "all three authors (PI personas only)",
        "evidence_paths": ["ab_ba_position_audit_same_author", "scalar_pairwise_reconciliation_same_author"],
    },
    {
        "claim_id": "methodology_slot_b_bias",
        "pair_key": None,
        "tier": "Methodology contribution",
        "headline": "LLM judges show ~15-17pp slot-B preference (judge-family-specific)",
        "allowed_wording": "In this corpus, prompt, judge set, and pairwise protocol, two of three judge configurations directly showed large later-answer / slot-B preference. GPT-5.5 (xhigh): 25-31pp slot-B advantage. Opus 4.7: 9-24pp, content-varying. GPT-5.4: negligible, occasionally slot-A favored. Uncounterbalanced margins were systematically biased in favor of the higher-numbered condition (which was always in slot B in v0.2 originals). Consistent with prior LLM-as-judge position-bias literature (Zheng et al. 2023, Shi et al. 2024).",
        "forbidden_wording": "LLM judges show universal slot-B bias; pure position bias; all LLM judges have slot-B preference.",
        "judge_scope": "n/a (methodology finding scoped to this corpus + protocol)",
        "author_scope": "n/a",
        "evidence_paths": ["ab_ba_position_audit_same_author_by_judge", "ab_ba_position_audit_same_author"],
    },
]


def _build_claim_ledger(metrics: dict) -> dict:
    """Build the claim ledger — central artifact of the curated v0.2 report.

    Source: 2026-05-17 consolidated round-2 review §2.3 (unanimous: this is
    the report's central artifact). Per-claim populated with controlled
    estimates, CIs, scope qualifiers, allowed/forbidden wording.
    """
    pw = metrics.get("pairwise", {})
    ab = pw.get("ab_ba_position_audit_same_author", {})
    rec = pw.get("scalar_pairwise_reconciliation_same_author", {})
    jpl = pw.get("ab_ba_joint_position_length_same_author", {})

    out: list[dict] = []
    for spec in CLAIM_LEDGER_SCHEMA:
        row = dict(spec)
        pair_key = spec.get("pair_key")
        if pair_key and pair_key in ab:
            ab_row = ab[pair_key]
            row["controlled_lo_win_rate"] = ab_row.get("position_controlled_lo_win_rate")
            row["controlled_bootstrap_ci"] = [
                ab_row.get("controlled_bootstrap_ci95_low"),
                ab_row.get("controlled_bootstrap_ci95_high"),
            ]
            row["ab_ba_survives_swap"] = ab_row.get("headline_survives_swap")
            row["n_ab_ba_pairs"] = ab_row.get("n_pairs_with_ab_ba")
        if pair_key and pair_key in rec:
            rec_row = rec[pair_key]
            row["scalar_delta_total"] = rec_row.get("mean_total_scalar_delta")
            row["scalar_pairwise_sign_agreement"] = rec_row.get(
                "pairwise_scalar_sign_agreement_decisive"
            )
        if pair_key and pair_key in jpl:
            jpl_row = jpl[pair_key]
            row["joint_length_position_lo_win"] = jpl_row.get("controlled_lo_win_rate_length_matched")
            row["joint_length_position_ci"] = [
                jpl_row.get("controlled_bootstrap_ci95_low"),
                jpl_row.get("controlled_bootstrap_ci95_high"),
            ]
            row["joint_length_position_n"] = jpl_row.get("n_pairs_in_similar_bucket")
        out.append(row)
    return {"rows": out, "schema_version": "2026-05-17"}


def _compute_ab_ba_by_provider_scope(
    pair_tagged_same_author: list[dict],
    swap_records: list,
) -> dict:
    """AB/BA stratified by judge-author provider scope (2026-05-17 review fix).

    Source: round-2 consolidated §2.8. The Phase 0 cross-provider finding
    on C3 vs C5_CONTRACT was hypothesis-generating; GPT Max Empiricist
    ran cross-provider AB/BA offline and found 0.543 [0.466, 0.622] (still
    no preference). Canonicalize in metrics so curated report can cite the
    empirical demotion of the Phase 0 cross-provider result.

    For each pair, splits AB/BA records into cross-provider (judge family
    != author family) and same-provider, reports controlled lo win + CI
    per scope.
    """
    import random as _random
    swap_idx: dict[tuple[str, str, str, str], object] = {}
    for s in swap_records:
        swap_idx[(s.scenario_id, s.run_id_a, s.run_id_b, s.judge_model)] = s

    # Collect per-(pair, scope) records
    per_cell: dict[tuple[str, str, str], dict] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        orig = p["ps"]
        swap_key = (orig.scenario_id, orig.run_id_b, orig.run_id_a, orig.judge_model)
        swap = swap_idx.get(swap_key)
        if swap is None:
            continue
        scope = "cross_provider" if p["judge_family"] != p["author_a_family"] else "same_provider"

        lo_in_orig_slot_a = (p["cond_a"] == lo)
        def _cw(w, lo_in_a):
            if w == "tie": return "tie"
            if w == "A": return lo if lo_in_a else hi
            return hi if lo_in_a else lo
        def _lo_score(cw):
            if cw == lo: return 1.0
            if cw == hi: return 0.0
            return 0.5

        orig_cw = _cw(orig.winner, lo_in_orig_slot_a)
        swap_cw = _cw(swap.winner, not lo_in_orig_slot_a)
        ls = (_lo_score(orig_cw) + _lo_score(swap_cw)) / 2.0
        cluster = (p["out_a"].user_id, orig.scenario_id, p["author_a"])

        cell = per_cell.setdefault((lo, hi, scope), {
            "n_pairs": 0, "sum_lo_score": 0.0,
            "n_orig_lo": 0, "n_orig_hi": 0,
            "n_swap_lo": 0, "n_swap_hi": 0,
            "records": [],
        })
        cell["n_pairs"] += 1
        cell["sum_lo_score"] += ls
        if orig_cw == lo: cell["n_orig_lo"] += 1
        elif orig_cw == hi: cell["n_orig_hi"] += 1
        if swap_cw == lo: cell["n_swap_lo"] += 1
        elif swap_cw == hi: cell["n_swap_hi"] += 1
        cell["records"].append({"lo_score": ls, "cluster": cluster})

    out: dict[str, dict] = {}
    for (lo, hi, scope), c in per_cell.items():
        n = c["n_pairs"]
        controlled = c["sum_lo_score"] / n if n else None
        orig_dec = c["n_orig_lo"] + c["n_orig_hi"]
        swap_dec = c["n_swap_lo"] + c["n_swap_hi"]
        orig_lo_wr = c["n_orig_lo"] / orig_dec if orig_dec else None
        swap_lo_wr = c["n_swap_lo"] / swap_dec if swap_dec else None

        # Cluster bootstrap
        cluster_map: dict[tuple, list[float]] = {}
        for r in c["records"]:
            cluster_map.setdefault(r["cluster"], []).append(r["lo_score"])
        cluster_keys = list(cluster_map.keys())
        n_clusters = len(cluster_keys)
        boot_lo = boot_hi = None
        if n_clusters >= 5 and n >= 20:
            rng = _random.Random(20260517 + hash(scope) % 1000)
            rates = []
            for _ in range(2000):
                sampled = [cluster_keys[rng.randrange(n_clusters)] for _ in range(n_clusters)]
                s_sum = 0.0; s_n = 0
                for k in sampled:
                    for ls in cluster_map[k]:
                        s_sum += ls; s_n += 1
                if s_n:
                    rates.append(s_sum / s_n)
            if rates:
                rates.sort()
                boot_lo = round(rates[int(0.025 * len(rates))], 4)
                boot_hi = round(rates[int(0.975 * len(rates)) - 1], 4)

        pair_key = f"{lo}_vs_{hi}"
        out.setdefault(pair_key, {})[scope] = {
            "n_pairs": n, "n_clusters": n_clusters,
            "original_lo_win_rate": round(orig_lo_wr, 4) if orig_lo_wr is not None else None,
            "swapped_lo_win_rate": round(swap_lo_wr, 4) if swap_lo_wr is not None else None,
            "position_controlled_lo_win_rate": round(controlled, 4) if controlled is not None else None,
            "controlled_bootstrap_ci95_low": boot_lo,
            "controlled_bootstrap_ci95_high": boot_hi,
        }
    return dict(sorted({k: dict(sorted(v.items())) for k, v in out.items()}.items()))


def _compute_ab_ba_joint_position_length(
    pair_tagged_same_author: list[dict],
    swap_records: list,
    *,
    target_pairs: list[tuple[str, str]] | None = None,
) -> dict:
    """Joint position × length AB/BA (2026-05-17 review fix §2.7).

    Settles the round-2 contradiction: Phase 0 length-matching said C4 vs C5
    "vanishes under length match" (CI [0.381, 0.659]); Phase 1 AB/BA said C4
    > C5 strengthens to 68.1%. These address different confounds (length vs
    position) and a joint correction is needed to interpret the headline.

    For each target pair, subset AB/BA records to length-similar pairs only,
    recompute controlled lo win + bootstrap CI.

    Defaults to all pairs that have length-bucket data; the C4 vs C5 case
    is the load-bearing one.
    """
    import random as _random
    if target_pairs is None:
        seen: set[tuple[str, str]] = set()
        for p in pair_tagged_same_author:
            if p["cond_a"] != p["cond_b"]:
                seen.add(_ordered_pair(p["cond_a"], p["cond_b"]))
        target_pairs = sorted(seen)
    target_set = {tuple(t) for t in target_pairs}

    swap_idx: dict[tuple[str, str, str, str], object] = {}
    for s in swap_records:
        swap_idx[(s.scenario_id, s.run_id_a, s.run_id_b, s.judge_model)] = s

    per_pair: dict[tuple[str, str], dict] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        if (lo, hi) not in target_set:
            continue
        orig = p["ps"]
        swap_key = (orig.scenario_id, orig.run_id_b, orig.run_id_a, orig.judge_model)
        swap = swap_idx.get(swap_key)
        if swap is None:
            continue
        wc_a = len((p["out_a"].assistant_response or "").split())
        wc_b = len((p["out_b"].assistant_response or "").split())
        wc_lo = wc_a if ca == lo else wc_b
        wc_hi = wc_b if cb == hi else wc_a
        bucket = _length_bucket(wc_lo - wc_hi)
        # Only "similar" bucket counts for length-controlled
        if bucket != "similar":
            continue

        lo_in_orig_slot_a = (p["cond_a"] == lo)
        def _cw(w, lo_in_a):
            if w == "tie": return "tie"
            if w == "A": return lo if lo_in_a else hi
            return hi if lo_in_a else lo
        def _lo_score(cw):
            if cw == lo: return 1.0
            if cw == hi: return 0.0
            return 0.5
        ls = (_lo_score(_cw(orig.winner, lo_in_orig_slot_a)) +
              _lo_score(_cw(swap.winner, not lo_in_orig_slot_a))) / 2.0
        cluster = (p["out_a"].user_id, orig.scenario_id, p["author_a"])

        bk = per_pair.setdefault((lo, hi), {"n": 0, "sum": 0.0, "records": []})
        bk["n"] += 1
        bk["sum"] += ls
        bk["records"].append({"lo_score": ls, "cluster": cluster})

    out: dict[str, dict] = {}
    for (lo, hi), b in per_pair.items():
        if b["n"] == 0:
            continue
        controlled = b["sum"] / b["n"]
        # Cluster bootstrap (matching the all-pairs convention)
        cluster_map: dict[tuple, list[float]] = {}
        for r in b["records"]:
            cluster_map.setdefault(r["cluster"], []).append(r["lo_score"])
        cluster_keys = list(cluster_map.keys())
        n_clusters = len(cluster_keys)
        boot_lo = boot_hi = None
        if n_clusters >= 5 and b["n"] >= 20:
            rng = _random.Random(20260517)
            rates = []
            for _ in range(2000):
                sampled = [cluster_keys[rng.randrange(n_clusters)] for _ in range(n_clusters)]
                s_sum = 0.0; s_n = 0
                for k in sampled:
                    for ls in cluster_map[k]:
                        s_sum += ls; s_n += 1
                if s_n:
                    rates.append(s_sum / s_n)
            if rates:
                rates.sort()
                boot_lo = round(rates[int(0.025 * len(rates))], 4)
                boot_hi = round(rates[int(0.975 * len(rates)) - 1], 4)
        out[f"{lo}_vs_{hi}"] = {
            "n_pairs_in_similar_bucket": b["n"],
            "n_clusters": n_clusters,
            "controlled_lo_win_rate_length_matched": round(controlled, 4),
            "controlled_bootstrap_ci95_low": boot_lo,
            "controlled_bootstrap_ci95_high": boot_hi,
        }
    return dict(sorted(out.items()))


def _compute_pairwise_by_persona_x_author(
    pair_tagged_same_author: list[dict],
) -> dict:
    """Persona × author cross-tabulation (2026-05-17 review fix A.7).

    Opus reviewer A.7 flagged that Phase 0 had per-persona and per-author
    blocks but not the interaction. Tests whether the Slalom Altar reversal
    is specific to one author × persona cell.
    """
    counters: dict[tuple[str, str, str, str], dict[str, int]] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        key = (lo, hi, p["out_a"].user_id, p["author_a"])
        c = counters.setdefault(key, {"lo_w": 0, "hi_w": 0, "tie": 0})
        d = _pair_decision(p, lo, hi)
        if d == "lo": c["lo_w"] += 1
        elif d == "hi": c["hi_w"] += 1
        else: c["tie"] += 1

    # Pivot: pair -> persona -> author -> stats
    out: dict[str, dict] = {}
    for (lo, hi, persona, author), c in counters.items():
        n_dec = c["lo_w"] + c["hi_w"]
        lo_wr = c["lo_w"] / n_dec if n_dec else None
        wci_lo, wci_hi = wilson_interval(c["lo_w"], n_dec) if n_dec else (None, None)
        pair_key = f"{lo}_vs_{hi}"
        out.setdefault(pair_key, {}).setdefault(persona, {})[author] = {
            "n_decisive": n_dec,
            "lo_decisive_win_rate": round(lo_wr, 4) if lo_wr is not None else None,
            "wilson_ci95_low": wci_lo,
            "wilson_ci95_high": wci_hi,
        }
    return dict(sorted({k: dict(sorted(v.items())) for k, v in out.items()}.items()))


def _compute_complete_case_scalar(
    anchored_scores: list,
    outputs: list,
    *,
    score_dimensions: tuple[str, ...],
) -> dict:
    """Complete-case scalar means (2026-05-17 review fix §2.5).

    Phase 0 §0.K showed only 67.5% of outputs were scored by all 3 judges.
    The pooled scalar means could carry selection bias. This block restricts
    to outputs scored by ALL judges that appear in the data, and computes
    per-condition means.
    """
    from collections import defaultdict
    out_by_run = {o.run_id: o for o in outputs}
    scored_by_run: dict[str, set[str]] = defaultdict(set)
    for s in anchored_scores:
        rid = getattr(s, "run_id", None)
        jm = getattr(s, "judge_model", None)
        if rid and jm:
            scored_by_run[rid].add(jm)

    all_judges = sorted({getattr(s, "judge_model", None) for s in anchored_scores if getattr(s, "judge_model", None)})
    if not all_judges:
        return {}
    all_judges_set = set(all_judges)

    # Complete-case outputs: scored by all judges
    complete_case_runs = {rid for rid, jset in scored_by_run.items() if jset == all_judges_set}

    # Aggregate by condition (PI-only and full)
    by_cond: dict[str, dict] = {}
    for s in anchored_scores:
        rid = getattr(s, "run_id", None)
        if rid not in complete_case_runs:
            continue
        o = out_by_run.get(rid)
        if not o:
            continue
        cond = str(o.condition)
        scores = getattr(s, "scores", None)
        if not scores:
            continue
        if hasattr(scores, "model_dump"):
            scores_d = scores.model_dump()
        else:
            scores_d = dict(scores)
        bucket = by_cond.setdefault(cond, {"n_records": 0, **{d: [] for d in score_dimensions}})
        bucket["n_records"] += 1
        for d in score_dimensions:
            if d in scores_d:
                bucket[d].append(float(scores_d[d]))

    # Compute means
    result: dict[str, dict] = {}
    for cond, bucket in sorted(by_cond.items()):
        means = {}
        for d in score_dimensions:
            vals = bucket[d]
            means[d] = round(sum(vals) / len(vals), 4) if vals else None
        result[cond] = {
            "n_records": bucket["n_records"],
            "means": means,
        }
    return {
        "n_complete_case_outputs": len(complete_case_runs),
        "n_total_outputs": len(out_by_run),
        "complete_case_rate": round(len(complete_case_runs) / len(out_by_run), 4) if out_by_run else None,
        "all_judges_required": all_judges,
        "by_condition": result,
    }


def _compute_ab_ba_position_audit_by_judge(
    pair_tagged_same_author: list[dict],
    swap_records: list,
) -> dict:
    """Per-judge AB/BA stratification (2026-05-17 review fix; round-2 §1.9 / §2.4).

    Round-2 reviewers (4-way unanimous) flagged that the headline methodology
    contribution — "LLM judges show ~15-17pp slot-B preference" — was based on
    offline computations not in the metrics JSON. This block makes it canonical.

    For each (pair, judge_model): slot-B advantage (= swap_lo_win - orig_lo_win
    where lo is always in slot A in originals, so positive = slot B favored),
    Wilson CI on the advantage difference, controlled lo win rate for that
    judge stratum, n_pairs.

    Also reports per-pair-per-judge cell decomposition into:
      condition_lo_stable, condition_hi_stable, slot_A_stable, slot_B_stable, unstable
    """
    # Build swap index
    swap_idx: dict[tuple[str, str, str, str], object] = {}
    for s in swap_records:
        key = (s.scenario_id, s.run_id_a, s.run_id_b, s.judge_model)
        swap_idx[key] = s

    # Collect per-(pair, judge) records
    per_cell: dict[tuple[str, str, str], dict] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        orig = p["ps"]
        swap_key = (orig.scenario_id, orig.run_id_b, orig.run_id_a, orig.judge_model)
        swap = swap_idx.get(swap_key)
        if swap is None:
            continue
        lo_in_orig_slot_a = (p["cond_a"] == lo)
        orig_winner = orig.winner
        swap_winner = swap.winner

        def _cw(w, lo_in_a):
            if w == "tie": return "tie"
            if w == "A": return lo if lo_in_a else hi
            return hi if lo_in_a else lo

        orig_cw = _cw(orig_winner, lo_in_orig_slot_a)
        swap_cw = _cw(swap_winner, not lo_in_orig_slot_a)
        # Slot decomposition
        # slot_A in orig holds lo; slot_A in swap holds hi (since A/B reversed)
        # We track which CONDITION won and which physical slot won
        if orig_winner == "tie" or swap_winner == "tie":
            decomp = "either_tie"
        elif orig_cw == swap_cw:
            # Same condition wins both → condition stable
            decomp = f"condition_{orig_cw}_stable"  # e.g. condition_C5_CONTRACT_stable
            # Normalize to lo/hi for stable canonicalization
            decomp = "condition_lo_stable" if orig_cw == lo else "condition_hi_stable"
        else:
            # Different conditions win the two orders — same physical slot won twice
            # If orig says A wins and swap also says A wins, slot_A stable
            if orig_winner == swap_winner:
                decomp = "slot_A_stable" if orig_winner == "A" else "slot_B_stable"
            else:
                decomp = "unstable"  # shouldn't happen given the above logic, but safety

        cell = per_cell.setdefault((lo, hi, orig.judge_model), {
            "n_pairs": 0,
            "n_orig_lo_wins": 0, "n_orig_hi_wins": 0, "n_orig_ties": 0,
            "n_swap_lo_wins": 0, "n_swap_hi_wins": 0, "n_swap_ties": 0,
            "sum_lo_wins_controlled": 0.0,
            "decomp_counts": {
                "condition_lo_stable": 0,
                "condition_hi_stable": 0,
                "slot_A_stable": 0,
                "slot_B_stable": 0,
                "either_tie": 0,
                "unstable": 0,
            },
            "records": [],
        })
        cell["n_pairs"] += 1
        if orig_cw == lo:
            cell["n_orig_lo_wins"] += 1
        elif orig_cw == hi:
            cell["n_orig_hi_wins"] += 1
        else:
            cell["n_orig_ties"] += 1
        if swap_cw == lo:
            cell["n_swap_lo_wins"] += 1
        elif swap_cw == hi:
            cell["n_swap_hi_wins"] += 1
        else:
            cell["n_swap_ties"] += 1
        # lo score
        def _lo_score(cw):
            if cw == lo: return 1.0
            if cw == hi: return 0.0
            return 0.5
        ls = (_lo_score(orig_cw) + _lo_score(swap_cw)) / 2.0
        cell["sum_lo_wins_controlled"] += ls
        cell["decomp_counts"][decomp] += 1
        cell["records"].append({
            "lo_score": ls,
            "cluster": (p["out_a"].user_id, p["ps"].scenario_id, p["author_a"]),
        })

    # Aggregate to per-pair {judge_model: stats}
    out: dict[str, dict] = {}
    for (lo, hi, judge), c in per_cell.items():
        n = c["n_pairs"]
        orig_dec = c["n_orig_lo_wins"] + c["n_orig_hi_wins"]
        swap_dec = c["n_swap_lo_wins"] + c["n_swap_hi_wins"]
        orig_lo_wr = c["n_orig_lo_wins"] / orig_dec if orig_dec else None
        swap_lo_wr = c["n_swap_lo_wins"] / swap_dec if swap_dec else None
        controlled = c["sum_lo_wins_controlled"] / n if n else None
        # Slot-B advantage = how much MORE lo wins when in slot B (swap) vs slot A (orig)
        # Positive slot_B_advantage = slot B favored = "later position wins"
        slot_b_advantage = (swap_lo_wr - orig_lo_wr) if (orig_lo_wr is not None and swap_lo_wr is not None) else None

        # Bootstrap CI on slot-B advantage (cluster bootstrap on signed difference per pair)
        import random as _random
        cluster_map: dict[tuple, list[float]] = {}
        for r in c["records"]:
            cluster_map.setdefault(r["cluster"], []).append(r["lo_score"])
        cluster_keys = list(cluster_map.keys())
        n_clusters = len(cluster_keys)
        boot_lo = boot_hi = None
        if n_clusters >= 5 and n >= 20:
            rng = _random.Random(20260517 + hash(judge) % 1000)
            rates: list[float] = []
            for _ in range(2000):
                sampled = [cluster_keys[rng.randrange(n_clusters)] for _ in range(n_clusters)]
                s_sum = 0.0
                s_n = 0
                for k in sampled:
                    for ls in cluster_map[k]:
                        s_sum += ls
                        s_n += 1
                if s_n:
                    rates.append(s_sum / s_n)
            if rates:
                rates.sort()
                boot_lo = round(rates[int(0.025 * len(rates))], 4)
                boot_hi = round(rates[int(0.975 * len(rates)) - 1], 4)

        pair_key = f"{lo}_vs_{hi}"
        out.setdefault(pair_key, {})[judge] = {
            "n_pairs": n,
            "n_clusters": n_clusters,
            "original_lo_win_rate": round(orig_lo_wr, 4) if orig_lo_wr is not None else None,
            "swapped_lo_win_rate": round(swap_lo_wr, 4) if swap_lo_wr is not None else None,
            "position_controlled_lo_win_rate": round(controlled, 4) if controlled is not None else None,
            "controlled_bootstrap_ci95_low": boot_lo,
            "controlled_bootstrap_ci95_high": boot_hi,
            "slot_b_advantage": round(slot_b_advantage, 4) if slot_b_advantage is not None else None,
            "cell_decomposition": dict(c["decomp_counts"]),
        }
    return dict(sorted({k: dict(sorted(v.items())) for k, v in out.items()}.items()))


def _compute_cross_judge_redflag_predictiveness(
    pair_tagged_same_author: list[dict],
    anchored_scores: list,
) -> dict:
    """Cross-judge red-flag predictiveness audit.

    Source: 2026-05-15 review (GPT-Max empiricist + consolidated §3.1 #8).
    Within-judge correlation of red flags with pairwise losses is
    tautological (same judge produces both). Real test: does judge X's red
    flag on output Y predict judge Z's pairwise call on the pair containing Y?

    For each pair, for each judge-of-pairwise (J_pw):
      - Find the leave-out judges (J_flag != J_pw)
      - For each pairwise record, query whether the leave-out judges flagged
        either output asymmetrically (one side has red flags, the other doesn't)
      - Compare: P(losing side has more leave-out-judge flags | decisive pair)

    Reports:
      - For each (lo, hi): n_with_cross_flags, n_asymmetric, p_loser_flagged
      - Sign test: is P(loser flagged) > P(winner flagged)?
    """
    # Index: (run_id, judge_model) -> list of red_flags
    flag_idx: dict[tuple[str, str], list[str]] = {}
    for s in anchored_scores:
        run_id = getattr(s, "run_id", None)
        jm = getattr(s, "judge_model", None)
        flags = getattr(s, "red_flags", None) or []
        if not run_id or not jm:
            continue
        flag_idx[(run_id, jm)] = list(flags) if not hasattr(flags, "__iter__") else list(flags)

    by_pair: dict[tuple[str, str], dict] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        w = p["ps"].winner
        if w not in ("A", "B"):
            continue
        # Find loser slot
        if w == "A":
            winner_run = p["ps"].run_id_a
            loser_run = p["ps"].run_id_b
        else:
            winner_run = p["ps"].run_id_b
            loser_run = p["ps"].run_id_a
        pw_judge = p["ps"].judge_model
        # Aggregate flags from all judges OTHER than the pairwise judge
        # who scored either output. This is the "leave-out-judge" predictor.
        winner_flags_external = 0
        loser_flags_external = 0
        n_external_judges = 0
        seen_judges: set[str] = set()
        for (rid, jm), flags in flag_idx.items():
            if jm == pw_judge:
                continue
            if rid == winner_run:
                winner_flags_external += len(flags)
                seen_judges.add(jm)
            elif rid == loser_run:
                loser_flags_external += len(flags)
                seen_judges.add(jm)
        n_external_judges = len(seen_judges)
        if n_external_judges == 0:
            continue
        # Asymmetric if difference in flag counts is non-zero
        asymmetric = (winner_flags_external != loser_flags_external)
        loser_more_flags = loser_flags_external > winner_flags_external

        bucket = by_pair.setdefault((lo, hi), {
            "n_decisive_pairs": 0,
            "n_with_cross_judge_data": 0,
            "n_asymmetric_external_flags": 0,
            "n_loser_more_externally_flagged": 0,
            "n_winner_more_externally_flagged": 0,
            "sum_winner_external_flags": 0,
            "sum_loser_external_flags": 0,
        })
        bucket["n_decisive_pairs"] += 1
        bucket["n_with_cross_judge_data"] += 1
        if asymmetric:
            bucket["n_asymmetric_external_flags"] += 1
            if loser_more_flags:
                bucket["n_loser_more_externally_flagged"] += 1
            else:
                bucket["n_winner_more_externally_flagged"] += 1
        bucket["sum_winner_external_flags"] += winner_flags_external
        bucket["sum_loser_external_flags"] += loser_flags_external

    out: dict[str, dict] = {}
    for (lo, hi), b in by_pair.items():
        n_asym = b["n_asymmetric_external_flags"]
        loser_more = b["n_loser_more_externally_flagged"]
        winner_more = b["n_winner_more_externally_flagged"]
        loser_share = round(loser_more / n_asym, 4) if n_asym else None
        # Wilson on "loser more flagged" share
        wci_lo, wci_hi = wilson_interval(loser_more, n_asym) if n_asym else (None, None)
        out[f"{lo}_vs_{hi}"] = {
            "n_decisive_pairs": b["n_decisive_pairs"],
            "n_asymmetric_external_flags": n_asym,
            "asymmetric_rate": round(n_asym / b["n_decisive_pairs"], 4) if b["n_decisive_pairs"] else None,
            "p_loser_more_externally_flagged": loser_share,
            "wilson_ci95_low": wci_lo,
            "wilson_ci95_high": wci_hi,
            "mean_external_flags_winner": round(b["sum_winner_external_flags"] / b["n_decisive_pairs"], 4) if b["n_decisive_pairs"] else None,
            "mean_external_flags_loser": round(b["sum_loser_external_flags"] / b["n_decisive_pairs"], 4) if b["n_decisive_pairs"] else None,
            "predictiveness_above_chance": (
                wci_lo is not None and wci_lo > 0.5
            ),
        }
    return dict(sorted(out.items()))


def _compute_ab_side_audit(pair_tagged_same_author: list[dict]) -> dict:
    """A/B side audit + position-bias diagnostic.

    Source: 2026-05-15 review — codex-council, GPT-Max, GPT-Pro all flagged
    that C5_CONTRACT is overwhelmingly in slot B. AB/BA counterbalanced
    rejudging is the convergent recommended cheapest decisive experiment.
    Before that runs, this block quantifies:

      - Per condition: total slot-A count, total slot-B count, B-share
      - Per pair: side balance (n_A, n_B), winner-by-side (slot A wins,
        slot B wins, ties), slot-bias (|B_wins - A_wins| / decisive)
      - Imbalance flag: pair is "structurally imbalanced" if one slot
        holds the same condition >80% of the time.

    Returns:
        {
          "by_condition": {cond: {n_slot_a, n_slot_b, b_share}},
          "by_pair": {pair: {n_total, n_A_wins, n_B_wins, n_ties,
                             slot_a_win_rate_decisive, structurally_imbalanced,
                             slot_a_condition_dominant, slot_b_condition_dominant}}
        }
    """
    cond_slots: dict[str, dict[str, int]] = {}
    pair_data: dict[tuple[str, str], dict] = {}

    for p in pair_tagged_same_author:
        ca = p["cond_a"]
        cb = p["cond_b"]
        if ca == cb:
            continue
        cond_slots.setdefault(ca, {"n_slot_a": 0, "n_slot_b": 0})["n_slot_a"] += 1
        cond_slots.setdefault(cb, {"n_slot_a": 0, "n_slot_b": 0})["n_slot_b"] += 1

        lo, hi = _ordered_pair(ca, cb)
        bucket = pair_data.setdefault((lo, hi), {
            "n_total": 0,
            "n_slot_a_is_lo": 0,  # how often the lower-numbered condition is in slot A
            "n_slot_a_wins": 0,
            "n_slot_b_wins": 0,
            "n_ties": 0,
        })
        bucket["n_total"] += 1
        if ca == lo:
            bucket["n_slot_a_is_lo"] += 1
        w = p["ps"].winner
        if w == "A":
            bucket["n_slot_a_wins"] += 1
        elif w == "B":
            bucket["n_slot_b_wins"] += 1
        else:
            bucket["n_ties"] += 1

    by_condition: dict[str, dict] = {}
    for cond, sl in cond_slots.items():
        tot = sl["n_slot_a"] + sl["n_slot_b"]
        by_condition[cond] = {
            "n_slot_a": sl["n_slot_a"],
            "n_slot_b": sl["n_slot_b"],
            "n_total": tot,
            "b_share": round(sl["n_slot_b"] / tot, 4) if tot else None,
        }

    by_pair: dict[str, dict] = {}
    for (lo, hi), b in pair_data.items():
        n = b["n_total"]
        n_dec = b["n_slot_a_wins"] + b["n_slot_b_wins"]
        slot_a_is_lo_share = round(b["n_slot_a_is_lo"] / n, 4) if n else None
        # Imbalanced if one slot holds the same condition >80% of the time
        structurally_imbalanced = slot_a_is_lo_share is not None and (
            slot_a_is_lo_share > 0.8 or slot_a_is_lo_share < 0.2
        )
        # Which condition dominates each slot
        slot_a_condition_dominant = lo if (slot_a_is_lo_share or 0) > 0.5 else hi
        slot_b_condition_dominant = hi if (slot_a_is_lo_share or 0) > 0.5 else lo
        slot_a_win_rate = round(b["n_slot_a_wins"] / n_dec, 4) if n_dec else None
        # Wilson CI on slot A wins regardless of condition (position-bias check)
        wci_lo, wci_hi = wilson_interval(b["n_slot_a_wins"], n_dec) if n_dec else (None, None)
        by_pair[f"{lo}_vs_{hi}"] = {
            "n_total": n,
            "n_decisive": n_dec,
            "n_ties": b["n_ties"],
            "n_slot_a_wins": b["n_slot_a_wins"],
            "n_slot_b_wins": b["n_slot_b_wins"],
            "slot_a_win_rate_decisive": slot_a_win_rate,
            "slot_a_wins_wilson_ci95_low": wci_lo,
            "slot_a_wins_wilson_ci95_high": wci_hi,
            "n_slot_a_is_lo": b["n_slot_a_is_lo"],
            "slot_a_is_lo_share": slot_a_is_lo_share,
            "structurally_imbalanced": structurally_imbalanced,
            "slot_a_condition_dominant": slot_a_condition_dominant if structurally_imbalanced else None,
            "slot_b_condition_dominant": slot_b_condition_dominant if structurally_imbalanced else None,
        }

    return {
        "by_condition": dict(sorted(by_condition.items())),
        "by_pair": dict(sorted(by_pair.items())),
    }


def _compute_leave_one_out_fragility(
    pair_tagged_same_author: list[dict],
    *,
    leave_out_fn,
    leave_out_label: str,
    scenarios,
    n_resamples: int = 1000,
    seed: int = 20260516,
) -> dict:
    """Leave-one-X-out fragility analysis on cluster-bootstrap pairwise CIs.

    Source: 2026-05-15 review consolidated §3.1 #4-5 — required diagnostic
    for any "robust" claim. For each headline pair × each value of the
    leave-out dimension (judge / author / persona / family), recompute the
    decisive lo_win rate + cluster bootstrap CI WITHOUT that value's
    records and compare to the full-sample point estimate.

    Flags emitted in the output:
      - "flips" if lo_win sign changes (>0.5 vs <0.5) on removal
      - "attenuates_5pp" if abs(lo_win_full - lo_win_loo) >= 0.05
      - "ci_widens_substantially" if loo CI width >= 2× full CI width
    """
    import random

    # Build per-pair record lists with leave-out keys
    pair_data: dict[tuple[str, str], list[dict]] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        leave_key = leave_out_fn(p, scenarios)
        if leave_key is None:
            continue
        cluster = (p["out_a"].user_id, p["ps"].scenario_id, p["author_a"])
        d = _pair_decision(p, lo, hi)
        pair_data.setdefault((lo, hi), []).append({
            "leave_key": str(leave_key),
            "decision": d,
            "cluster": cluster,
        })

    def _bootstrap_ci(records: list[dict], n_clusters_floor: int = 5) -> tuple:
        """Returns (point, wci_lo, wci_hi, bci_lo, bci_hi, n_dec, n_clusters)."""
        clusters: dict[tuple, list[str]] = {}
        for r in records:
            clusters.setdefault(r["cluster"], []).append(r["decision"])
        cluster_keys = list(clusters.keys())
        n_clusters = len(cluster_keys)
        decisive = sum(1 for r in records if r["decision"] in ("lo", "hi"))
        lo_wins = sum(1 for r in records if r["decision"] == "lo")
        point = lo_wins / decisive if decisive else None
        wci_lo, wci_hi = wilson_interval(lo_wins, decisive) if decisive else (None, None)
        bci_lo = bci_hi = None
        if decisive >= 20 and n_clusters >= n_clusters_floor:
            rng = random.Random(seed)
            rates: list[float] = []
            for _ in range(n_resamples):
                sampled = [cluster_keys[rng.randrange(n_clusters)] for _ in range(n_clusters)]
                s_lo = s_dec = 0
                for k in sampled:
                    for d in clusters[k]:
                        if d == "lo":
                            s_lo += 1
                            s_dec += 1
                        elif d == "hi":
                            s_dec += 1
                if s_dec:
                    rates.append(s_lo / s_dec)
            if rates:
                rates.sort()
                bci_lo = round(rates[int(0.025 * len(rates))], 4)
                bci_hi = round(rates[int(0.975 * len(rates)) - 1], 4)
        return (
            round(point, 4) if point is not None else None,
            wci_lo, wci_hi, bci_lo, bci_hi, decisive, n_clusters,
        )

    out: dict[str, dict] = {}
    for (lo, hi), records in pair_data.items():
        full_point, full_wci_lo, full_wci_hi, full_bci_lo, full_bci_hi, full_n, full_clusters = (
            _bootstrap_ci(records)
        )
        # Identify all leave_keys present in this pair
        all_keys = sorted({r["leave_key"] for r in records})
        loo_results: dict[str, dict] = {}
        for k in all_keys:
            kept = [r for r in records if r["leave_key"] != k]
            point, wci_lo, wci_hi, bci_lo, bci_hi, n_dec, n_clusters = _bootstrap_ci(kept)
            flips = (
                point is not None and full_point is not None
                and ((full_point < 0.5) != (point < 0.5))
                and (full_point != 0.5 and point != 0.5)
            )
            attenuates_5pp = (
                point is not None and full_point is not None
                and abs(full_point - point) >= 0.05
            )
            ci_widens = False
            if full_bci_lo is not None and bci_lo is not None:
                full_w = full_bci_hi - full_bci_lo
                loo_w = bci_hi - bci_lo
                if full_w > 0 and loo_w >= 2 * full_w:
                    ci_widens = True

            flags: list[str] = []
            if flips:
                flags.append("flips")
            if attenuates_5pp:
                flags.append("attenuates_5pp")
            if ci_widens:
                flags.append("ci_widens_2x")

            loo_results[k] = {
                "n_decisive": n_dec,
                "n_clusters": n_clusters,
                "lo_decisive_win_rate": point,
                "delta_from_full": (
                    round(point - full_point, 4) if (point is not None and full_point is not None) else None
                ),
                "wilson_ci95_low": wci_lo,
                "wilson_ci95_high": wci_hi,
                "bootstrap_ci95_low": bci_lo,
                "bootstrap_ci95_high": bci_hi,
                "flags": flags,
            }
        out[f"{lo}_vs_{hi}"] = {
            "leave_out_dimension": leave_out_label,
            "full_point_lo_decisive": full_point,
            "full_bootstrap_ci": [full_bci_lo, full_bci_hi] if full_bci_lo is not None else None,
            "full_n_decisive": full_n,
            "by_leave_out_value": loo_results,
        }
    return dict(sorted(out.items()))


def _compute_stratified_pairwise(
    pair_tagged_same_author: list[dict],
    *,
    key_fn,
    key_label: str,
    n_resamples: int = 1000,
    seed: int = 20260515,
) -> dict:
    """Generic stratified pairwise win-rate computation.

    Source: 2026-05-15 external review. Codex-council, GPT-Max, and GPT-Pro
    all flagged the need for per-(judge | author | persona | family)
    breakdowns of every headline pair. Codex specifically cited "GPT-5.4
    reverses C3 vs C5_CONTRACT to ~57%" — this function makes that kind
    of stratification first-class instead of one-off.

    For each (lo, hi) condition pair × each stratum value (e.g. each judge
    model), reports n_decisive, lo_decisive_win_rate, Wilson CI, and (if
    n_decisive ≥ 30) a cluster bootstrap CI clustered by (persona × scenario
    × author).

    Returns:
        { "<lo>_vs_<hi>": { "<stratum_value>": {
              n_total, n_decisive, n_ties,
              lo_decisive_win_rate, wilson_ci95_low, wilson_ci95_high,
              bootstrap_ci95_low, bootstrap_ci95_high, n_clusters
          } } }
    """
    import random

    # Group: (lo, hi) -> stratum -> list of (decision, cluster_key)
    by_pair: dict[tuple[str, str], dict[str, list[tuple[str, tuple]]]] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        stratum = key_fn(p)
        if stratum is None:
            continue
        d = _pair_decision(p, lo, hi)
        cluster = (p["out_a"].user_id, p["ps"].scenario_id, p["author_a"])
        by_pair.setdefault((lo, hi), {}).setdefault(str(stratum), []).append((d, cluster))

    rng = random.Random(seed)
    out: dict[str, dict] = {}
    for (lo, hi), strata in by_pair.items():
        pair_out: dict[str, dict] = {}
        for stratum, records in sorted(strata.items()):
            decisions = [d for d, _ in records]
            n_total = len(decisions)
            n_ties = sum(1 for d in decisions if d == "tie")
            lo_wins = sum(1 for d in decisions if d == "lo")
            hi_wins = sum(1 for d in decisions if d == "hi")
            n_dec = lo_wins + hi_wins
            lo_wr = lo_wins / n_dec if n_dec else None
            wci_lo, wci_hi = wilson_interval(lo_wins, n_dec) if n_dec else (None, None)

            # Cluster bootstrap (only if enough clusters for stability)
            cluster_to_decisions: dict[tuple, list[str]] = {}
            for d, c in records:
                cluster_to_decisions.setdefault(c, []).append(d)
            cluster_keys = list(cluster_to_decisions.keys())
            n_clusters = len(cluster_keys)
            boot_lo = boot_hi = None
            if n_dec >= 20 and n_clusters >= 5:
                boot_rates: list[float] = []
                for _ in range(n_resamples):
                    sampled = [cluster_keys[rng.randrange(n_clusters)] for _ in range(n_clusters)]
                    s_lo = s_dec = 0
                    for k in sampled:
                        for d in cluster_to_decisions[k]:
                            if d == "lo":
                                s_lo += 1
                                s_dec += 1
                            elif d == "hi":
                                s_dec += 1
                    if s_dec:
                        boot_rates.append(s_lo / s_dec)
                if boot_rates:
                    boot_rates.sort()
                    boot_lo = round(boot_rates[int(0.025 * len(boot_rates))], 4)
                    boot_hi = round(boot_rates[int(0.975 * len(boot_rates)) - 1], 4)

            pair_out[stratum] = {
                "n_total": n_total,
                "n_decisive": n_dec,
                "n_ties": n_ties,
                "n_clusters": n_clusters,
                "lo_decisive_win_rate": round(lo_wr, 4) if lo_wr is not None else None,
                "wilson_ci95_low": wci_lo,
                "wilson_ci95_high": wci_hi,
                "bootstrap_ci95_low": boot_lo,
                "bootstrap_ci95_high": boot_hi,
            }
        out[f"{lo}_vs_{hi}"] = pair_out
    return dict(sorted(out.items()))


def _compute_scalar_pairwise_reconciliation(
    pair_tagged_same_author: list[dict],
    anchored_scores: list,
    *,
    score_dimensions: tuple[str, ...],
) -> dict:
    """Reconcile pairwise winners vs anchored-scalar deltas, cell by cell.

    Source: 2026-05-15 external review (GPT Pro §A1, codex-council).
    The headline finding "C5_CONTRACT > C3 / C4 pairwise" turned out NOT to
    be reflected in the anchored scalar means (C3 beats C5_CONTRACT on every
    PI scalar dimension in the bundle table). External reviewers called this
    "the most important missing analysis" — it gates the mechanism claim.

    For each condition-pair (lo, hi) and each (persona × scenario × author)
    cell judged BY THE SAME judge model on both outputs, we compute:

      - Pairwise winner (lo / hi / tie)
      - Anchored-scalar deltas (hi_score - lo_score) per dimension
      - Total-score delta (sum across dimensions)
      - Pairwise-vs-scalar sign agreement (does pairwise winner match the
        sign of total scalar delta?)

    Returns per-pair aggregates that surface contradictions between the two
    judging modes. A pair where pairwise strongly prefers one side but
    scalar deltas are ~0 means the pairwise channel is detecting something
    the scalar rubric does not (or vice versa).
    """
    # Index anchored scores by (run_id, judge_model)
    score_idx: dict[tuple[str, str], dict[str, float]] = {}
    for s in anchored_scores:
        # AnchoredJudgeScore or dict
        run_id = getattr(s, "run_id", None) or s.get("run_id") if isinstance(s, dict) else getattr(s, "run_id", None)
        judge_model = getattr(s, "judge_model", None) or (s.get("judge_model") if isinstance(s, dict) else None)
        scores = getattr(s, "scores", None) or (s.get("scores") if isinstance(s, dict) else None)
        if not run_id or not judge_model or not scores:
            continue
        # scores may be a pydantic model or dict
        if hasattr(scores, "model_dump"):
            scores_d = scores.model_dump()
        else:
            scores_d = dict(scores)
        score_idx[(run_id, judge_model)] = {d: float(scores_d.get(d, 0)) for d in score_dimensions}

    # For each pair record, find matched scalars; aggregate by (lo, hi).
    per_pair: dict[tuple[str, str], dict] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        a_scores = score_idx.get((p["ps"].run_id_a, p["ps"].judge_model))
        b_scores = score_idx.get((p["ps"].run_id_b, p["ps"].judge_model))
        if not a_scores or not b_scores:
            continue

        # Orient so that "lo_scores" corresponds to condition lo
        if p["cond_a"] == lo:
            lo_scores, hi_scores = a_scores, b_scores
            lo_is_pw_a = True
        else:
            lo_scores, hi_scores = b_scores, a_scores
            lo_is_pw_a = False

        # Pairwise winner expressed as which condition (lo/hi/tie)
        w = p["ps"].winner
        if w == "tie":
            pw_winner = "tie"
        elif (w == "A" and lo_is_pw_a) or (w == "B" and not lo_is_pw_a):
            pw_winner = "lo"
        else:
            pw_winner = "hi"

        bucket = per_pair.setdefault((lo, hi), {
            "n_matched": 0,
            "n_lo_pw_wins": 0,
            "n_hi_pw_wins": 0,
            "n_ties": 0,
            "delta_sums": {d: 0.0 for d in score_dimensions},
            "delta_pos": {d: 0 for d in score_dimensions},   # hi_score > lo_score
            "delta_neg": {d: 0 for d in score_dimensions},   # hi_score < lo_score
            "delta_zero": {d: 0 for d in score_dimensions},
            "agree_decisive": 0,    # pairwise winner matches sign of total scalar delta
            "disagree_decisive": 0,
            "scalar_tie": 0,        # total scalar delta == 0
            "n_decisive": 0,
        })
        bucket["n_matched"] += 1
        if pw_winner == "lo":
            bucket["n_lo_pw_wins"] += 1
        elif pw_winner == "hi":
            bucket["n_hi_pw_wins"] += 1
        else:
            bucket["n_ties"] += 1

        total_delta = 0.0
        for d in score_dimensions:
            delta = hi_scores[d] - lo_scores[d]  # +ve = hi condition higher
            total_delta += delta
            bucket["delta_sums"][d] += delta
            if delta > 0:
                bucket["delta_pos"][d] += 1
            elif delta < 0:
                bucket["delta_neg"][d] += 1
            else:
                bucket["delta_zero"][d] += 1

        if pw_winner != "tie":
            bucket["n_decisive"] += 1
            if total_delta == 0:
                bucket["scalar_tie"] += 1
            else:
                scalar_says = "hi" if total_delta > 0 else "lo"
                if scalar_says == pw_winner:
                    bucket["agree_decisive"] += 1
                else:
                    bucket["disagree_decisive"] += 1

    # Finalize: mean deltas, fractions, agreement rate
    out: dict[str, dict] = {}
    for (lo, hi), b in per_pair.items():
        n = b["n_matched"]
        if n == 0:
            continue
        mean_deltas = {d: round(b["delta_sums"][d] / n, 4) for d in score_dimensions}
        dim_pos_frac = {d: round(b["delta_pos"][d] / n, 4) for d in score_dimensions}
        dim_neg_frac = {d: round(b["delta_neg"][d] / n, 4) for d in score_dimensions}
        total_delta_sum = sum(b["delta_sums"].values())
        n_dec = b["n_decisive"]
        agree_rate = (
            round(b["agree_decisive"] / (b["agree_decisive"] + b["disagree_decisive"]), 4)
            if (b["agree_decisive"] + b["disagree_decisive"]) > 0 else None
        )
        out[f"{lo}_vs_{hi}"] = {
            "n_matched": n,
            "n_decisive": n_dec,
            "lo_pairwise_wins": b["n_lo_pw_wins"],
            "hi_pairwise_wins": b["n_hi_pw_wins"],
            "pairwise_ties": b["n_ties"],
            "hi_pairwise_win_rate_decisive": round(b["n_hi_pw_wins"] / n_dec, 4) if n_dec else None,
            "mean_scalar_deltas_hi_minus_lo": mean_deltas,
            "frac_dim_hi_higher": dim_pos_frac,
            "frac_dim_lo_higher": dim_neg_frac,
            "mean_total_scalar_delta": round(total_delta_sum / n, 4),
            "max_scale_per_dim": 10,  # anchored rubric is 0-10
            "n_dims": len(score_dimensions),
            "pairwise_scalar_sign_agreement_decisive": agree_rate,
            "agree_count": b["agree_decisive"],
            "disagree_count": b["disagree_decisive"],
            "scalar_tie_count": b["scalar_tie"],
        }
    return dict(sorted(out.items()))


def _compute_tie_rates(pair_tagged_same_author: list[dict]) -> dict:
    """Per-pair total / decisive / ties / tie_rate / lo decisive win.

    Source: v0.1 Round-2 §6e. Uses all-judges-pooled, same-author scope.
    """
    counters: dict[tuple[str, str], dict[str, int]] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        key = (lo, hi)
        c = counters.setdefault(key, {"lo_w": 0, "hi_w": 0, "ties": 0})
        d = _pair_decision(p, lo, hi)
        if d == "lo":
            c["lo_w"] += 1
        elif d == "hi":
            c["hi_w"] += 1
        else:
            c["ties"] += 1
    out: dict[str, dict] = {}
    for (lo, hi), c in counters.items():
        decisive = c["lo_w"] + c["hi_w"]
        total = decisive + c["ties"]
        out[f"{lo}_vs_{hi}"] = {
            "total": total,
            "decisive": decisive,
            "ties": c["ties"],
            "tie_rate": round(c["ties"] / total, 4) if total else 0.0,
            "lo_wins": c["lo_w"],
            "hi_wins": c["hi_w"],
            "lo_decisive_win_rate": round(c["lo_w"] / decisive, 4) if decisive else None,
        }
    return dict(sorted(out.items()))


def _persona_type_label(pt: object) -> str | None:
    """Map a PersonaType enum value or string to the canonical 2-letter
    label used throughout the v0.1 reports: "PI" (public_inspired),
    "PS" (pure_synthetic), "HY" (hybrid). Returns None if unknown."""
    if pt is None:
        return None
    s = str(pt).lower()
    if "public" in s:
        return "PI"
    if "synthetic" in s or s.startswith("syn") or "pure" in s:
        return "PS"
    if "hybrid" in s or s.startswith("hy"):
        return "HY"
    return None


def _compute_pi_ps_split_pairwise(pair_tagged_same_author: list[dict]) -> dict:
    """Same-author pairwise stratified by persona type (PI vs PS).

    Source: v0.1 Round-2 §6f. Excludes C5 pairs (PI-only by construction).
    For each non-C5 pair, reports lo decisive win + Wilson CI + n for both
    PI and PS slices.
    """
    counters: dict[tuple[str, str, str], dict[str, int]] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        if "C5" in (ca, cb):
            continue  # C5 is PI-only; PI/PS split not meaningful for C5 pairs
        lo, hi = _ordered_pair(ca, cb)
        label = _persona_type_label(p.get("persona_type"))
        if label is None:
            continue
        key = (lo, hi, label)
        c = counters.setdefault(key, {"lo_w": 0, "hi_w": 0, "ties": 0})
        d = _pair_decision(p, lo, hi)
        if d == "lo":
            c["lo_w"] += 1
        elif d == "hi":
            c["hi_w"] += 1
        else:
            c["ties"] += 1
    # Reorganize by pair, with PI/PS sub-keys
    out: dict[str, dict] = {}
    for (lo, hi, pt), c in counters.items():
        pair_key = f"{lo}_vs_{hi}"
        decisive = c["lo_w"] + c["hi_w"]
        ci_lo, ci_hi = wilson_interval(c["lo_w"], decisive)
        slice_block = {
            "n_decisive": decisive,
            "n_ties": c["ties"],
            "lo_wins": c["lo_w"],
            "lo_decisive_win_rate": round(c["lo_w"] / decisive, 4) if decisive else None,
            "ci95_low": ci_lo,
            "ci95_high": ci_hi,
        }
        out.setdefault(pair_key, {})[pt] = slice_block
    return dict(sorted(out.items()))


def _compute_red_flag_stratification(
    scores: list,
    out_by_run: dict,
    *,
    judge_provider_family_fn,
) -> dict:
    """Per-condition any-flag rate stratified three ways:
      (a) by judge model
      (b) by cross-provider filter (judge family ≠ author family)
      (c) by output-level flag aggregation: any-judge / 2-of-3 / majority

    Source: GPT Pro v0.1 §7 — deferred from v0.1; native in v0.2.
    Inputs:
      scores: list of JudgeScore (filtered to official judges already)
      out_by_run: run_id -> AssistantOutput
      judge_provider_family_fn: model_id -> "openai"|"anthropic"|"moonshot"|"other"
    """
    # (a) By judge model
    by_judge: dict[str, dict[str, dict]] = {}
    # (b) By cross-provider filter
    by_xprov: dict[str, dict] = {"cross_provider": {}, "exact_or_same_provider": {}}
    # Aggregate counters
    judge_counts: dict[tuple[str, str], dict[str, int]] = {}
    xprov_counts: dict[tuple[str, str], dict[str, int]] = {}
    # (c) Output-level: per-output collect set of judges that flagged it
    per_output_flagged: dict[str, set[str]] = {}
    per_output_total_judges: dict[str, set[str]] = {}
    per_output_condition: dict[str, str] = {}

    for s in scores:
        out = out_by_run.get(s.run_id)
        if out is None:
            continue
        cond = str(out.condition)
        flagged = bool(s.red_flags)
        # (a) by judge
        kj = (s.judge_model, cond)
        c = judge_counts.setdefault(kj, {"flagged": 0, "total": 0})
        c["total"] += 1
        if flagged:
            c["flagged"] += 1
        # (b) cross-provider stratification
        author_fam = judge_provider_family_fn(out.output_model)
        judge_fam = judge_provider_family_fn(s.judge_model)
        is_cross = (author_fam != judge_fam) and judge_fam != "other"
        bucket_label = "cross_provider" if is_cross else "exact_or_same_provider"
        kx = (bucket_label, cond)
        cx = xprov_counts.setdefault(kx, {"flagged": 0, "total": 0})
        cx["total"] += 1
        if flagged:
            cx["flagged"] += 1
        # (c) output-level
        per_output_total_judges.setdefault(s.run_id, set()).add(s.judge_model)
        if flagged:
            per_output_flagged.setdefault(s.run_id, set()).add(s.judge_model)
        per_output_condition[s.run_id] = cond

    # Format (a) and (b)
    for (judge, cond), c in judge_counts.items():
        by_judge.setdefault(judge, {})[cond] = {
            "flagged": c["flagged"],
            "total": c["total"],
            "any_flag_rate": round(c["flagged"] / c["total"], 4) if c["total"] else 0.0,
        }
    for (label, cond), c in xprov_counts.items():
        by_xprov[label][cond] = {
            "flagged": c["flagged"],
            "total": c["total"],
            "any_flag_rate": round(c["flagged"] / c["total"], 4) if c["total"] else 0.0,
        }

    # (c) Output-level aggregations
    output_level: dict[str, dict[str, dict]] = {}
    for run_id, cond in per_output_condition.items():
        n_total_judges = len(per_output_total_judges[run_id])
        n_flagged = len(per_output_flagged.get(run_id, set()))
        for level_name, threshold in [
            ("any_judge", 1),
            ("two_or_more_judges", 2),
            ("majority", (n_total_judges // 2) + 1),
        ]:
            entry = output_level.setdefault(level_name, {}).setdefault(
                cond, {"flagged_outputs": 0, "total_outputs": 0}
            )
            entry["total_outputs"] += 1
            if n_flagged >= threshold:
                entry["flagged_outputs"] += 1

    for level_name, by_cond in output_level.items():
        for cond, entry in by_cond.items():
            entry["flag_rate"] = (
                round(entry["flagged_outputs"] / entry["total_outputs"], 4)
                if entry["total_outputs"]
                else 0.0
            )

    return {
        "by_judge_condition": dict(sorted(by_judge.items())),
        "by_provider_filter_condition": {
            k: dict(sorted(v.items())) for k, v in by_xprov.items()
        },
        "by_output_level_threshold": output_level,
    }


def _compute_scenario_family_breakdowns(
    pair_tagged_same_author: list[dict],
    scenarios: dict,
) -> dict:
    """Per-family pairwise win rates for each condition pair.

    Source: GPT Pro v0.1 §8.2 — deferred from v0.1; native in v0.2.
    Answers "which scenario families produce the biggest conditioning effects?"

    Inputs:
      pair_tagged_same_author: list of pair records with cond_a/cond_b
      scenarios: scenario_id -> Scenario
    Returns: { family: { pair_str: {n_decisive, lo_wins, lo_win_rate, ci_low, ci_high} } }
    """
    counters: dict[tuple[str, str, str], dict[str, int]] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        ps = p["ps"]
        scen = scenarios.get(ps.scenario_id)
        if scen is None:
            continue
        family = str(scen.scenario_family)
        lo, hi = _ordered_pair(ca, cb)
        key = (family, lo, hi)
        c = counters.setdefault(key, {"lo_w": 0, "hi_w": 0, "ties": 0})
        d = _pair_decision(p, lo, hi)
        if d == "lo":
            c["lo_w"] += 1
        elif d == "hi":
            c["hi_w"] += 1
        else:
            c["ties"] += 1

    out: dict[str, dict[str, dict]] = {}
    for (family, lo, hi), c in counters.items():
        decisive = c["lo_w"] + c["hi_w"]
        ci_lo, ci_hi = wilson_interval(c["lo_w"], decisive)
        out.setdefault(family, {})[f"{lo}_vs_{hi}"] = {
            "n_decisive": decisive,
            "n_ties": c["ties"],
            "lo_wins": c["lo_w"],
            "lo_decisive_win_rate": round(c["lo_w"] / decisive, 4) if decisive else None,
            "ci95_low": ci_lo,
            "ci95_high": ci_hi,
        }
    # Order families and pairs within each family
    return {fam: dict(sorted(out[fam].items())) for fam in sorted(out.keys())}


def _compute_cluster_bootstrap_pairwise(
    pair_tagged_same_author: list[dict],
    *,
    n_resamples: int = 2000,
    seed: int = 20260505,
) -> dict:
    """Cluster-bootstrap CIs for the same-author pairwise win rates.

    Source: GPT Pro v0.1 §5.5 — addresses the Wilson-CI independence
    assumption violation flagged in v0.1 §12 #5. The same persona × scenario
    × author cell appears in multiple pair records, so Wilson over-states
    effective n. Cluster-bootstrap by (persona_id, scenario_id, author_model)
    produces a CI that respects this clustering.

    For each pair: resample clusters with replacement n_resamples times,
    recompute lo decisive win rate within each resample, take the
    (2.5%, 97.5%) percentiles. Wilson values from the existing block remain
    side-by-side for continuity.

    Returns: { pair_str: {n_decisive, lo_decisive_win_rate, wilson_ci, bootstrap_ci, n_clusters} }
    """
    import random

    # Group pair records by (lo, hi) and within that by cluster key.
    pair_clusters: dict[tuple[str, str], dict[tuple, list[str]]] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        cluster = (
            p["out_a"].user_id,
            p["ps"].scenario_id,
            p["author_a"],  # = author_b since same-author
        )
        d = _pair_decision(p, lo, hi)
        pair_clusters.setdefault((lo, hi), {}).setdefault(cluster, []).append(d)

    rng = random.Random(seed)
    out: dict[str, dict] = {}
    for (lo, hi), clusters in pair_clusters.items():
        cluster_keys = list(clusters.keys())
        n_clusters = len(cluster_keys)
        if n_clusters == 0:
            continue
        # Compute point estimate (full sample, decisive only)
        all_decisions = [d for cs in clusters.values() for d in cs]
        decisive = sum(1 for d in all_decisions if d in ("lo", "hi"))
        lo_wins = sum(1 for d in all_decisions if d == "lo")
        ties = sum(1 for d in all_decisions if d == "tie")
        point = lo_wins / decisive if decisive else None
        # Wilson on decisive
        wci_lo, wci_hi = wilson_interval(lo_wins, decisive)

        # Bootstrap: resample cluster keys with replacement, recompute lo win rate
        boot_rates: list[float] = []
        for _ in range(n_resamples):
            sampled_keys = [cluster_keys[rng.randrange(n_clusters)] for _ in range(n_clusters)]
            sample_lo = 0
            sample_dec = 0
            for k in sampled_keys:
                for d in clusters[k]:
                    if d == "lo":
                        sample_lo += 1
                        sample_dec += 1
                    elif d == "hi":
                        sample_dec += 1
                    # ties not counted in decisive denominator
            if sample_dec > 0:
                boot_rates.append(sample_lo / sample_dec)
        boot_rates.sort()
        if boot_rates:
            ci_lo = boot_rates[int(0.025 * len(boot_rates))]
            ci_hi = boot_rates[int(0.975 * len(boot_rates)) - 1]
            ci_lo, ci_hi = round(ci_lo, 4), round(ci_hi, 4)
        else:
            ci_lo, ci_hi = 0.0, 0.0

        out[f"{lo}_vs_{hi}"] = {
            "n_decisive": decisive,
            "n_ties": ties,
            "n_clusters": n_clusters,
            "lo_decisive_win_rate": round(point, 4) if point is not None else None,
            "wilson_ci95_low": wci_lo,
            "wilson_ci95_high": wci_hi,
            "bootstrap_ci95_low": ci_lo,
            "bootstrap_ci95_high": ci_hi,
            "n_resamples": n_resamples,
        }
    return dict(sorted(out.items()))


def _compute_scalar_inter_judge_agreement(
    scores: list,
    out_by_run: dict,
    *,
    score_dimensions: tuple[str, ...],
) -> dict:
    """Per-dimension scalar agreement between judges.

    Source: GPT Pro v0.1 §6.1 — defends scalar pooling. Reports:
      - per-judge mean per dimension (severity profile)
      - per-judge severity offset from grand mean
      - pairwise Pearson correlation between judges per dimension
      - pairwise Spearman correlation per dimension
      - mean correlation across dimensions per judge pair
      - flag dimensions where any judge pair correlation < 0.3 ("weak")

    Returns: {
      per_judge_dim_means: {judge: {dim: mean}},
      per_judge_severity_offsets: {judge: {dim: offset}},
      pairwise_correlations: {pair: {dim: {pearson, spearman, n}}},
      pairwise_mean_correlation: {pair: {pearson, spearman}},
      weak_agreement_dimensions: [dim, ...],
    }
    """
    from statistics import mean

    # Group scores by judge × run_id
    by_judge_run: dict[str, dict[str, object]] = {}
    judges_seen: set[str] = set()
    for s in scores:
        by_judge_run.setdefault(s.judge_model, {})[s.run_id] = s
        judges_seen.add(s.judge_model)

    # Per-judge per-dimension means
    per_judge_dim_means: dict[str, dict[str, float]] = {}
    for judge, runs in by_judge_run.items():
        per_judge_dim_means[judge] = {}
        for dim in score_dimensions:
            vals = [getattr(s.scores, dim) for s in runs.values()]
            per_judge_dim_means[judge][dim] = round(mean(vals), 4) if vals else 0.0

    # Grand mean per dimension (across judges)
    grand_means: dict[str, float] = {}
    for dim in score_dimensions:
        all_vals = [getattr(s.scores, dim) for s in scores]
        grand_means[dim] = mean(all_vals) if all_vals else 0.0

    # Severity offsets
    per_judge_severity_offsets: dict[str, dict[str, float]] = {}
    for judge, dim_means in per_judge_dim_means.items():
        per_judge_severity_offsets[judge] = {
            dim: round(dim_means[dim] - grand_means[dim], 4) for dim in score_dimensions
        }

    # Pairwise correlations
    def _pearson(xs: list[float], ys: list[float]) -> float | None:
        n = len(xs)
        if n < 3:
            return None
        mx = sum(xs) / n
        my = sum(ys) / n
        sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        sxx = sum((x - mx) ** 2 for x in xs)
        syy = sum((y - my) ** 2 for y in ys)
        denom = (sxx * syy) ** 0.5
        return sxy / denom if denom > 0 else None

    def _spearman(xs: list[float], ys: list[float]) -> float | None:
        if len(xs) < 3:
            return None
        # Rank with average-rank tie handling
        def _ranks(values):
            indexed = sorted(enumerate(values), key=lambda t: t[1])
            ranks = [0.0] * len(values)
            i = 0
            while i < len(indexed):
                j = i
                while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
                    j += 1
                avg_rank = (i + j) / 2 + 1
                for k in range(i, j + 1):
                    ranks[indexed[k][0]] = avg_rank
                i = j + 1
            return ranks

        rx = _ranks(xs)
        ry = _ranks(ys)
        return _pearson(rx, ry)

    pairwise_correlations: dict[str, dict[str, dict]] = {}
    pairwise_mean_correlation: dict[str, dict[str, float]] = {}
    weak_dims: set[str] = set()
    for j_a, j_b in sorted(
        {tuple(sorted(p)) for p in __import__("itertools").combinations(judges_seen, 2)}
    ):
        a_runs = by_judge_run[j_a]
        b_runs = by_judge_run[j_b]
        common = sorted(set(a_runs) & set(b_runs))
        pair_key = f"{j_a}__vs__{j_b}"
        if not common:
            pairwise_correlations[pair_key] = {}
            continue
        per_dim: dict[str, dict] = {}
        pearsons: list[float] = []
        spearmans: list[float] = []
        for dim in score_dimensions:
            xs = [getattr(a_runs[rid].scores, dim) for rid in common]
            ys = [getattr(b_runs[rid].scores, dim) for rid in common]
            r = _pearson(xs, ys)
            rho = _spearman(xs, ys)
            per_dim[dim] = {
                "pearson": round(r, 4) if r is not None else None,
                "spearman": round(rho, 4) if rho is not None else None,
                "n": len(xs),
            }
            if r is not None:
                pearsons.append(r)
                if r < 0.3:
                    weak_dims.add(dim)
            if rho is not None:
                spearmans.append(rho)
        pairwise_correlations[pair_key] = per_dim
        pairwise_mean_correlation[pair_key] = {
            "pearson": round(sum(pearsons) / len(pearsons), 4) if pearsons else None,
            "spearman": round(sum(spearmans) / len(spearmans), 4) if spearmans else None,
            "n_dimensions": len(pearsons),
        }

    return {
        "per_judge_dim_means": per_judge_dim_means,
        "per_judge_severity_offsets": per_judge_severity_offsets,
        "pairwise_correlations": pairwise_correlations,
        "pairwise_mean_correlation": pairwise_mean_correlation,
        "weak_agreement_dimensions": sorted(weak_dims),
        "n_judges": len(judges_seen),
    }


def _length_bucket(diff_words: int) -> str:
    """Bucket the (lo-side wordcount minus hi-side wordcount) difference.

    Negative = lo is shorter. Source: v0.1 Round-2 §6g.
    """
    if diff_words < -100:
        return "lo_much_shorter"
    if diff_words < -20:
        return "lo_moderately_shorter"
    if diff_words < 20:
        return "similar"
    if diff_words < 100:
        return "lo_moderately_longer"
    return "lo_much_longer"


_LENGTH_BUCKET_ORDER = (
    "lo_much_shorter",
    "lo_moderately_shorter",
    "similar",
    "lo_moderately_longer",
    "lo_much_longer",
)


def _compute_length_adjusted_summary(
    pair_tagged_same_author: list[dict],
) -> dict:
    """Length-adjusted pairwise summary: lo_win restricted to length-similar pairs.

    Source: 2026-05-15 review consolidated §3.1 #7 (length-adjusted), GPT-Pro
    §A7. Reports for each headline pair: full lo_win, similar-length-only
    lo_win, and the delta. Headlines that vanish under length-matching are
    flagged. This is the analysis-only complement to a generation-side rerun
    (B6) that matches length at the prompt level.
    """
    bucket_decisions: dict[tuple[str, str, str], dict[str, int]] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        wc_a = len((p["out_a"].assistant_response or "").split())
        wc_b = len((p["out_b"].assistant_response or "").split())
        wc_lo = wc_a if ca == lo else wc_b
        wc_hi = wc_b if cb == hi else wc_a
        bucket = _length_bucket(wc_lo - wc_hi)
        key = (lo, hi, bucket)
        c = bucket_decisions.setdefault(key, {"lo_w": 0, "hi_w": 0, "ties": 0})
        d = _pair_decision(p, lo, hi)
        if d == "lo":
            c["lo_w"] += 1
        elif d == "hi":
            c["hi_w"] += 1
        else:
            c["ties"] += 1

    out: dict[str, dict] = {}
    # Aggregate by pair
    pairs_seen: dict[tuple[str, str], dict] = {}
    for (lo, hi, bucket), c in bucket_decisions.items():
        pair_acc = pairs_seen.setdefault((lo, hi), {
            "full_lo_w": 0, "full_hi_w": 0, "full_ties": 0,
            "similar_lo_w": 0, "similar_hi_w": 0, "similar_ties": 0,
        })
        pair_acc["full_lo_w"] += c["lo_w"]
        pair_acc["full_hi_w"] += c["hi_w"]
        pair_acc["full_ties"] += c["ties"]
        # "Similar" length = bucket is 'similar' only (strict length-control)
        if bucket == "similar":
            pair_acc["similar_lo_w"] += c["lo_w"]
            pair_acc["similar_hi_w"] += c["hi_w"]
            pair_acc["similar_ties"] += c["ties"]

    for (lo, hi), acc in pairs_seen.items():
        full_dec = acc["full_lo_w"] + acc["full_hi_w"]
        sim_dec = acc["similar_lo_w"] + acc["similar_hi_w"]
        full_wr = acc["full_lo_w"] / full_dec if full_dec else None
        sim_wr = acc["similar_lo_w"] / sim_dec if sim_dec else None
        sim_wci_lo, sim_wci_hi = (
            wilson_interval(acc["similar_lo_w"], sim_dec)
            if sim_dec else (None, None)
        )
        delta = (sim_wr - full_wr) if (sim_wr is not None and full_wr is not None) else None
        # Flag: headline vanishes under length-matching
        flag_vanishes = False
        if full_wr is not None and sim_wr is not None:
            full_side = full_wr > 0.5
            # Vanishes if length-matched CI includes 0.5
            if (sim_wci_lo or 0) <= 0.5 <= (sim_wci_hi or 1):
                # And full margin was non-trivial (>5pp from 0.5)
                if abs(full_wr - 0.5) >= 0.05:
                    flag_vanishes = True
        out[f"{lo}_vs_{hi}"] = {
            "n_full_decisive": full_dec,
            "n_similar_decisive": sim_dec,
            "full_lo_win_rate": round(full_wr, 4) if full_wr is not None else None,
            "similar_lo_win_rate": round(sim_wr, 4) if sim_wr is not None else None,
            "similar_wilson_ci95_low": sim_wci_lo,
            "similar_wilson_ci95_high": sim_wci_hi,
            "delta_similar_minus_full": round(delta, 4) if delta is not None else None,
            "headline_vanishes_under_length_match": flag_vanishes,
        }
    return dict(sorted(out.items()))


def _compute_length_buckets_pairwise(
    pair_tagged_same_author: list[dict],
    *,
    target_pairs: list[tuple[str, str]] | None = None,
) -> dict:
    """Length-bucketed pairwise win rates for the specified condition pairs.

    Source: v0.1 Round-2 §6g. Default targets: any pair involving C5, since
    C5 is the v0.1 length-confound case. Override via ``target_pairs`` if a
    different scope is wanted (e.g. C5_CONTRACT pairs in v0.2).
    """
    if target_pairs is None:
        # 2026-05-16 review fix: previously this only ran on C5 / C5_CONTRACT
        # pairs. External reviewers (consolidated §3.1 #7, GPT-Pro §A7) want
        # length sensitivity computed for ALL headline pairs, not just C5.
        # C5_CONTRACT is 7,433 chars vs C3 at 2,518 — so length sensitivity
        # of C3 vs C5_CONTRACT is the central diagnostic, not appendix.
        seen_pairs: set[tuple[str, str]] = set()
        for p in pair_tagged_same_author:
            if p["cond_a"] == p["cond_b"]:
                continue
            lo, hi = _ordered_pair(p["cond_a"], p["cond_b"])
            seen_pairs.add((lo, hi))
        target_pairs = sorted(seen_pairs)

    target_set = {tuple(t) for t in target_pairs}
    counters: dict[tuple[str, str, str], dict[str, int]] = {}
    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        if ca == cb:
            continue
        lo, hi = _ordered_pair(ca, cb)
        if (lo, hi) not in target_set:
            continue
        out_a = p["out_a"]
        out_b = p["out_b"]
        wc_a = len((out_a.assistant_response or "").split())
        wc_b = len((out_b.assistant_response or "").split())
        # diff = lo-side wordcount minus hi-side wordcount
        wc_lo = wc_a if ca == lo else wc_b
        wc_hi = wc_b if cb == hi else wc_a
        bucket = _length_bucket(wc_lo - wc_hi)
        key = (lo, hi, bucket)
        c = counters.setdefault(key, {"lo_w": 0, "hi_w": 0, "ties": 0})
        d = _pair_decision(p, lo, hi)
        if d == "lo":
            c["lo_w"] += 1
        elif d == "hi":
            c["hi_w"] += 1
        else:
            c["ties"] += 1

    # Reorganize: pair → {bucket → metrics} in a stable bucket order.
    out: dict[str, dict] = {}
    for (lo, hi, bucket), c in counters.items():
        pair_key = f"{lo}_vs_{hi}"
        decisive = c["lo_w"] + c["hi_w"]
        ci_lo, ci_hi = wilson_interval(c["lo_w"], decisive)
        out.setdefault(pair_key, {})[bucket] = {
            "n_decisive": decisive,
            "n_ties": c["ties"],
            "lo_decisive_win_rate": round(c["lo_w"] / decisive, 4) if decisive else None,
            "ci95_low": ci_lo,
            "ci95_high": ci_hi,
        }
    # Order buckets within each pair entry.
    for pair_key in list(out.keys()):
        ordered = {b: out[pair_key][b] for b in _LENGTH_BUCKET_ORDER if b in out[pair_key]}
        out[pair_key] = ordered
    return dict(sorted(out.items()))


# ---------------------------------------------------------------------------
# Inter-judge agreement: Cohen's κ on binary labels + Spearman ρ on dimensions
# ---------------------------------------------------------------------------


def cohen_kappa_binary(pairs: list[tuple[bool, bool]]) -> float | None:
    """Cohen's κ for a sequence of (rater_A_flag, rater_B_flag) binary pairs.

    Returns None if the sequence is empty or both raters are constant on the
    same value (κ undefined: pe = 1, division by zero).
    """
    n = len(pairs)
    if n == 0:
        return None
    a = sum(1 for x, y in pairs if x and y)        # both present
    d = sum(1 for x, y in pairs if not x and not y)  # both absent
    b = sum(1 for x, y in pairs if x and not y)    # only A
    c = sum(1 for x, y in pairs if not x and y)    # only B
    po = (a + d) / n
    pe = ((a + b) * (a + c) + (c + d) * (b + d)) / (n * n)
    if pe >= 1.0 - 1e-12:
        return None  # degenerate: both raters identical & constant
    return round((po - pe) / (1.0 - pe), 4)


def spearman_rho(xs: list[float], ys: list[float]) -> float | None:
    """Spearman rank correlation. Returns None if either input has fewer than
    2 distinct values (correlation undefined under tie-only ranks).
    """
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    if len(set(xs)) < 2 or len(set(ys)) < 2:
        return None
    try:
        import statistics as _stats
        return round(_stats.correlation(xs, ys, method="ranked"), 4)
    except Exception:
        return None


def compute_inter_judge_agreement(
    scores: list,
    *,
    label_vocab: list[str],
    score_dimensions: list[str],
) -> dict:
    """For every ordered pair of distinct judges, compute:
      - per-label Cohen's κ on red-flag presence
      - mean Cohen's κ across all labels (excluding undefined)
      - per-dimension Spearman ρ
      - mean Spearman ρ across all dimensions
      - n_overlap (output runs both judges scored)

    Inputs are the legacy or anchored score records (uniformly typed). Both
    JudgeScore and AnchoredJudgeScore expose ``run_id``, ``judge_model``,
    ``red_flags``, and ``scores`` with the same shape.

    The metric block is stored under ``inter_judge_agreement`` in compute_metrics.
    """
    by_judge_run: dict[str, dict[str, object]] = {}
    judges_seen: set[str] = set()
    for s in scores:
        judge = s.judge_model
        judges_seen.add(judge)
        by_judge_run.setdefault(judge, {})[s.run_id] = s

    out: dict[str, dict] = {}
    for j_a, j_b in sorted({tuple(sorted(p)) for p in __import__("itertools").combinations(judges_seen, 2)}):
        a_runs = by_judge_run.get(j_a, {})
        b_runs = by_judge_run.get(j_b, {})
        common = sorted(set(a_runs.keys()) & set(b_runs.keys()))
        if not common:
            continue
        # Per-label Cohen's κ
        per_label: dict[str, dict] = {}
        for label in label_vocab:
            pairs = []
            for rid in common:
                a_set = {str(rf) for rf in a_runs[rid].red_flags}
                b_set = {str(rf) for rf in b_runs[rid].red_flags}
                pairs.append((label in a_set, label in b_set))
            kappa = cohen_kappa_binary(pairs)
            n_present_a = sum(1 for rid in common if label in {str(rf) for rf in a_runs[rid].red_flags})
            n_present_b = sum(1 for rid in common if label in {str(rf) for rf in b_runs[rid].red_flags})
            per_label[label] = {
                "kappa": kappa,
                "n_present_a": n_present_a,
                "n_present_b": n_present_b,
            }
        defined_kappas = [d["kappa"] for d in per_label.values() if d["kappa"] is not None]
        mean_kappa = round(sum(defined_kappas) / len(defined_kappas), 4) if defined_kappas else None

        # Per-dimension Spearman ρ
        per_dim: dict[str, float | None] = {}
        for dim in score_dimensions:
            xs = [getattr(a_runs[rid].scores, dim) for rid in common]
            ys = [getattr(b_runs[rid].scores, dim) for rid in common]
            per_dim[dim] = spearman_rho(xs, ys)
        defined_rhos = [v for v in per_dim.values() if v is not None]
        mean_rho = round(sum(defined_rhos) / len(defined_rhos), 4) if defined_rhos else None

        out[f"{j_a}__vs__{j_b}"] = {
            "n_overlap": len(common),
            "n_red_flag_labels_with_defined_kappa": len(defined_kappas),
            "mean_red_flag_kappa": mean_kappa,
            "per_label_kappa": per_label,
            "mean_dimension_spearman_rho": mean_rho,
            "per_dimension_spearman_rho": per_dim,
        }
    return out


def _provider_family(model_id: str) -> str:
    """Bucket a resolved model id into its provider family."""
    m = (model_id or "").lower()
    if "opus" in m or "claude" in m or "sonnet" in m or "haiku" in m:
        return "anthropic"
    if "gpt" in m or "openai" in m:
        return "openai"
    if "kimi" in m or "deepseek" in m:
        return "other"
    return "other"


def _model_family(model_id: str) -> str:
    """Bucket a resolved model id into a generation/family label.

    Used by the tri-model halo classifier to distinguish "same provider,
    different model" (e.g. GPT-5.5 judging GPT-5.4) from "exact self"
    (e.g. GPT-5.5 judging GPT-5.5).
    """
    m = (model_id or "").lower()
    if "opus" in m:
        return "claude-opus"
    if "sonnet" in m:
        return "claude-sonnet"
    if "haiku" in m:
        return "claude-haiku"
    if "claude" in m:
        return "claude"
    if "gpt-5.5" in m or "gpt5.5" in m:
        return "gpt-5.5"
    if "gpt-5.4" in m or "gpt5.4" in m:
        return "gpt-5.4"
    if "gpt-5.3" in m or "gpt5.3" in m:
        return "gpt-5.3"
    if "gpt-5" in m or "gpt5" in m:
        return "gpt-5"
    if "kimi" in m:
        return "kimi"
    if "deepseek" in m:
        return "deepseek"
    return "unknown"


# Three-way classification of the judge's relation to the author. Used in
# tri-model analysis (brief §10) where same_provider and exact_self need
# to be reported separately. Falls back to model-name parsing when the
# explicit metadata fields are absent (older v0.1 records).
RELATION_EXACT_SELF = "exact_self"
RELATION_SAME_PROVIDER = "same_provider"
RELATION_CROSS_PROVIDER = "cross_provider"
RELATION_UNKNOWN = "unknown"


def _judge_author_relation(
    output_model: str,
    judge_model: str,
    *,
    output_provider_family: str = "",
    output_model_family: str = "",
    judge_provider_family: str = "",
    judge_model_family: str = "",
) -> str:
    """Classify the judge↔author pair as exact_self / same_provider /
    cross_provider / unknown.

    Prefers the explicit metadata fields when populated; falls back to
    string parsing of the model id for backward compatibility with v0.1
    records that don't carry the new metadata.
    """
    out_pf = output_provider_family or _provider_family(output_model)
    judge_pf = judge_provider_family or _provider_family(judge_model)
    out_mf = output_model_family or _model_family(output_model)
    judge_mf = judge_model_family or _model_family(judge_model)
    if out_mf == judge_mf and out_mf not in ("", "unknown"):
        return RELATION_EXACT_SELF
    if out_pf == judge_pf and out_pf not in ("", "other", "unknown"):
        return RELATION_SAME_PROVIDER
    if (
        out_pf != judge_pf
        and out_pf not in ("", "other", "unknown")
        and judge_pf not in ("", "other", "unknown")
    ):
        return RELATION_CROSS_PROVIDER
    return RELATION_UNKNOWN


def _dim_stats(group: list[JudgeScore]) -> dict:
    if not group:
        return {}
    out: dict = {}
    for dim in SCORE_DIMENSIONS:
        vals = [getattr(g.scores, dim) for g in group]
        out[dim] = {"mean": round(mean(vals), 3), "median": median(vals), "n": len(vals)}
    rf = sum(1 for g in group if g.red_flags) / len(group)
    out["red_flag_rate"] = round(rf, 3)
    out["n"] = len(group)
    return out


def _delta_block(block_a: dict, block_b: dict) -> dict:
    """Subtract two dim_stats blocks. Returns {dim: round(a.mean - b.mean, 3)}."""
    if not block_a or not block_b:
        return {}
    return {
        dim: round(block_a.get(dim, {}).get("mean", 0) - block_b.get(dim, {}).get("mean", 0), 3)
        for dim in SCORE_DIMENSIONS
    }


def _red_flag_rate_by_condition(scores: list[JudgeScore], outputs_by_run: dict[str, AssistantOutput]) -> dict[str, dict[str, float]]:
    """For each condition, compute rate of each red-flag label across scores."""
    by_cond: dict[str, list[JudgeScore]] = defaultdict(list)
    for s in scores:
        out = outputs_by_run.get(s.run_id)
        if out is None:
            continue
        by_cond[str(out.condition)].append(s)
    result: dict[str, dict[str, float]] = {}
    for cond, grp in by_cond.items():
        n = len(grp) or 1
        flag_counts: Counter = Counter()
        for s in grp:
            for rf in s.red_flags:
                flag_counts[str(rf)] += 1
        result[cond] = {flag: round(count / n, 3) for flag, count in flag_counts.items()}
        result[cond]["_n"] = n
    return result


def _compute_scoring_block(
    scores: list,
    out_by_run: dict[str, AssistantOutput],
    scenarios: dict[str, Scenario],
    persona_type_for_scenario,
    *,
    scale_max: int,
) -> dict:
    """Shared scoring aggregation used for both legacy (0-5) and anchored (0-10).

    Returns {primary_cross_provider, secondary_all_judges, halo_audit_same_minus_cross, red_flag_frequency_total, scale_max}.
    Condition sets are derived dynamically from the observed outputs so
    C1_padded / C4_shuffled appear when present.
    """
    # Tag each score with context, including the tri-model relation label.
    tagged: list[dict] = []
    for s in scores:
        out = out_by_run.get(s.run_id)
        if out is None:
            continue
        author_family = getattr(out, "output_provider_family", "") or _provider_family(out.output_model)
        judge_family = getattr(s, "judge_provider_family", "") or _provider_family(s.judge_model)
        author_model_family = getattr(out, "output_model_family", "") or _model_family(out.output_model)
        judge_model_family = getattr(s, "judge_model_family", "") or _model_family(s.judge_model)
        relation = _judge_author_relation(
            out.output_model,
            s.judge_model,
            output_provider_family=author_family,
            output_model_family=author_model_family,
            judge_provider_family=judge_family,
            judge_model_family=judge_model_family,
        )
        tagged.append({
            "score": s,
            "output": out,
            "condition": str(out.condition),
            "author": out.output_model,
            "author_family": author_family,
            "author_model_family": author_model_family,
            "judge": s.judge_model,
            "judge_family": judge_family,
            "judge_model_family": judge_model_family,
            "relation": relation,
            "cross_provider": relation == RELATION_CROSS_PROVIDER,
            "exact_self": relation == RELATION_EXACT_SELF,
            "same_provider": relation == RELATION_SAME_PROVIDER,
            "persona_type": persona_type_for_scenario(s.scenario_id),
        })

    cross_scores = [t["score"] for t in tagged if t["cross_provider"]]
    all_scores_list = [t["score"] for t in tagged]

    def scores_subset(predicate):
        return [t["score"] for t in tagged if predicate(t)]

    # Derive the shared condition set (C0-C4 equivalent) dynamically:
    # every condition that appears for at least one persona of EVERY type
    # qualifies as "shared." Conditions present only for public-inspired
    # (e.g. C5) go into the extended set.
    conditions_by_ptype: dict[str, set[str]] = defaultdict(set)
    for t in tagged:
        if t["persona_type"]:
            conditions_by_ptype[t["persona_type"]].add(t["condition"])
    ptypes_present = set(conditions_by_ptype.keys())
    if ptypes_present:
        shared = set.intersection(*(conditions_by_ptype[p] for p in ptypes_present))
    else:
        shared = {t["condition"] for t in tagged}
    # extended = shared ∪ any condition seen at all
    all_conds = {t["condition"] for t in tagged}

    def by_cond(scs, limit_conditions=None):
        buckets: dict[str, list] = defaultdict(list)
        for s in scs:
            out = out_by_run.get(s.run_id)
            if out is None:
                continue
            cond = str(out.condition)
            if limit_conditions is not None and cond not in limit_conditions:
                continue
            buckets[cond].append(s)
        return {c: _dim_stats(g) for c, g in sorted(buckets.items())}

    pi_cross = scores_subset(lambda t: t["cross_provider"] and t["persona_type"] == "public_inspired")
    ps_cross = scores_subset(lambda t: t["cross_provider"] and t["persona_type"] == "pure_synthetic")

    primary = {
        "by_condition_C0C4_all_personas": by_cond(cross_scores, shared),
        "by_condition_C0C4_PI_only": by_cond(pi_cross, shared),
        "by_condition_C0C5_PI_only": by_cond(pi_cross, all_conds),
        "by_condition_C0C4_PS_only": by_cond(ps_cross, shared),
    }

    def deltas_for(block: dict, pairs: list[tuple[str, str]]) -> dict:
        out = {}
        for a, b in pairs:
            if a in block and b in block:
                out[f"{a}_minus_{b}"] = _delta_block(block.get(a, {}), block.get(b, {}))
        return out

    # Core + length-control + C3-C4 per user brief:
    pairs_shared = [
        ("C4", "C0"),
        ("C4", "C1"),
        ("C4", "C3"),
        ("C3", "C0"),
        ("C3", "C4"),  # reverse
        ("C1", "C0"),
        ("C4", "C1_padded"),
        ("C1", "C1_padded"),
        ("C4", "C4_shuffled"),
    ]
    pairs_pi_only = [
        ("C5", "C0"),
        ("C5", "C4"),
        ("C5", "C3"),
        ("C4", "C5"),  # user's "C4 − C5 PI-only"
        ("C4", "C0"),
        ("C4", "C1"),
        ("C4", "C1_padded"),
        ("C4", "C4_shuffled"),
        ("C3", "C4"),
    ]
    pairs_ps_only = [
        ("C4", "C0"),
        ("C4", "C1"),
        ("C4", "C3"),
        ("C3", "C4"),
        ("C4", "C1_padded"),
        ("C4", "C4_shuffled"),
    ]
    primary["deltas_C0C4_all_personas"] = deltas_for(primary["by_condition_C0C4_all_personas"], pairs_shared)
    primary["deltas_C0C5_PI_only"] = deltas_for(primary["by_condition_C0C5_PI_only"], pairs_pi_only)
    primary["deltas_C0C4_PS_only"] = deltas_for(primary["by_condition_C0C4_PS_only"], pairs_ps_only)

    # PI - PS by condition
    pi_vs_ps: dict[str, dict] = {}
    for cond in sorted(shared):
        pi_grp = [t["score"] for t in tagged if t["cross_provider"] and t["persona_type"] == "public_inspired" and t["condition"] == cond]
        ps_grp = [t["score"] for t in tagged if t["cross_provider"] and t["persona_type"] == "pure_synthetic" and t["condition"] == cond]
        if pi_grp and ps_grp:
            pi_vs_ps[cond] = _delta_block(_dim_stats(pi_grp), _dim_stats(ps_grp))
    primary["pi_minus_ps_by_condition"] = pi_vs_ps

    primary["red_flag_label_rate_C0C4_all_personas"] = _red_flag_rate_by_condition(
        [t["score"] for t in tagged if t["cross_provider"] and t["condition"] in shared],
        out_by_run,
    )
    primary["red_flag_label_rate_C0C5_PI_only"] = _red_flag_rate_by_condition(
        [t["score"] for t in tagged if t["cross_provider"] and t["persona_type"] == "public_inspired" and t["condition"] in all_conds],
        out_by_run,
    )

    # Author comparison (all observed conditions, cross-provider)
    author_cross: dict[str, list] = {}
    for t in tagged:
        if not t["cross_provider"]:
            continue
        key = f"{t['condition']}__{t['author']}"
        author_cross.setdefault(key, []).append(t["score"])
    primary["by_condition_author_cross_provider"] = {
        k: _dim_stats(v) for k, v in sorted(author_cross.items())
    }

    # Scenario family breakdown (shared conditions only, cross-provider)
    fam_cross: dict[str, list] = {}
    for t in tagged:
        if not t["cross_provider"] or t["condition"] not in shared:
            continue
        scen = scenarios.get(t["score"].scenario_id)
        if scen is None:
            continue
        fam = str(scen.scenario_family)
        key = f"{fam}__{t['condition']}"
        fam_cross.setdefault(key, []).append(t["score"])
    primary["by_family_condition_cross_provider"] = {
        k: _dim_stats(v) for k, v in sorted(fam_cross.items())
    }

    # Secondary
    secondary = {
        "by_condition_all_data_all_judges": by_cond(all_scores_list),
    }
    buckets_cj: dict[tuple[str, str], list] = defaultdict(list)
    for t in tagged:
        buckets_cj[(t["condition"], t["judge"])].append(t["score"])
    secondary["by_condition_judge"] = {
        f"{cond}__{judge}": _dim_stats(g) for (cond, judge), g in sorted(buckets_cj.items())
    }

    # Halo audit. Three buckets per (condition, author):
    #   - exact_self_minus_cross_provider: same model judging itself
    #   - same_provider_minus_cross_provider: different model in same family
    #   - legacy "halo_audit_same_minus_cross": both same_provider + exact_self
    #     vs cross_provider (compatible with v0.1 reports).
    # In two-model runs the same_provider bucket is empty (every same-family
    # judging is also exact-self); when GPT-5.5 lands, the buckets diverge.
    halo_legacy: dict[str, dict[str, float]] = {}
    halo_exact_self: dict[str, dict[str, float]] = {}
    halo_same_provider: dict[str, dict[str, float]] = {}
    by_cond_author: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for t in tagged:
        by_cond_author[(t["condition"], t["author"])].append(t)

    def _delta_means(group_a: list, group_b: list) -> dict:
        """Per-dimension mean(A) - mean(B), 3 decimal places."""
        return {
            dim: round(
                mean(getattr(s.scores, dim) for s in group_a)
                - mean(getattr(s.scores, dim) for s in group_b),
                3,
            )
            for dim in SCORE_DIMENSIONS
        }

    for (cond, author), grp in sorted(by_cond_author.items()):
        cross_grp = [t["score"] for t in grp if t["cross_provider"]]
        if not cross_grp:
            continue
        exact_grp = [t["score"] for t in grp if t["exact_self"]]
        same_prov_grp = [t["score"] for t in grp if t["same_provider"]]
        legacy_same_grp = exact_grp + same_prov_grp
        key = f"{cond}__{author}"
        if legacy_same_grp:
            halo_legacy[key] = _delta_means(legacy_same_grp, cross_grp)
        if exact_grp:
            halo_exact_self[key] = _delta_means(exact_grp, cross_grp)
        if same_prov_grp:
            halo_same_provider[key] = _delta_means(same_prov_grp, cross_grp)

    # Red-flag totals (across all judges)
    rf_counter: Counter = Counter()
    for s in scores:
        for rf in s.red_flags:
            rf_counter[str(rf)] += 1

    return {
        "scale_max": scale_max,
        "shared_conditions": sorted(shared),
        "all_conditions": sorted(all_conds),
        "primary_cross_provider": primary,
        "secondary_all_judges": secondary,
        "halo_audit_same_minus_cross": halo_legacy,
        "halo_audit_exact_self_minus_cross": halo_exact_self,
        "halo_audit_same_provider_minus_cross": halo_same_provider,
        "red_flag_frequency_total": dict(rf_counter.most_common()),
    }


def _compute_token_summary(outputs: list[AssistantOutput]) -> dict:
    """Per-condition token / character summaries."""
    by_cond: dict[str, list[AssistantOutput]] = defaultdict(list)
    for o in outputs:
        by_cond[str(o.condition)].append(o)
    result: dict[str, dict] = {}
    for cond, grp in sorted(by_cond.items()):
        profile_chars = [len(o.profile_text_supplied or "") for o in grp]
        response_chars = [len(o.assistant_response or "") for o in grp]
        tin = [o.tokens_in for o in grp if o.tokens_in is not None]
        tout = [o.tokens_out for o in grp if o.tokens_out is not None]
        result[cond] = {
            "n": len(grp),
            "profile_chars_mean": round(mean(profile_chars), 1) if profile_chars else 0,
            "profile_chars_median": median(profile_chars) if profile_chars else 0,
            "response_chars_mean": round(mean(response_chars), 1) if response_chars else 0,
            "response_chars_median": median(response_chars) if response_chars else 0,
            "tokens_in_mean": round(mean(tin), 1) if tin else None,
            "tokens_out_mean": round(mean(tout), 1) if tout else None,
        }
    return result


# ---------------------------------------------------------------------------
# D1 — Same-orientation rejudge sentinel (v0.3 Phase 3.2 / R11)
#
# Decomposes AB/BA flip rate into position-bias and retest-noise components.
# Addresses the Opus 4.6 steelman from the v0.2 blog post round-1 publication
# review: "controlled lo_win = mean(original, swap)" assumes additive symmetric
# position effects orthogonal to condition signal, but the AB/BA flip rate
# itself bundles position bias with retest noise.
#
# Logic: for each pair record that has BOTH an original judgment AND a
# same-orientation rejudgment (same run_id_a, run_id_b, judge — but a re-issued
# judgment, NOT a swap), compute the flip rate. Since position is held constant,
# any winner change is retest noise, not position bias. Then:
#
#   position_bias_net_of_noise = AB/BA_flip_rate − same_orientation_flip_rate
#
# Per R11, report per-judge and per-pair heterogeneity, not just corpus-scope
# means. The subtraction is descriptive, not a clean estimator; high
# same-orientation noise relative to AB/BA flip means the AB/BA decomposition
# is unstable for that judge/pair (failure trigger #6 from v0.3 plan §8.2).
# ---------------------------------------------------------------------------


def _compute_same_orientation_sentinel(
    pair_tagged_same_author: list[dict],
    same_orientation_records: list,
) -> dict:
    """Same-orientation rejudge sentinel (v0.3 Phase 3.2 / R11 / D1).

    same_orientation_records: list of pairwise records that re-judge the
    same (run_id_a, run_id_b, judge_model) triple without swapping (i.e., NOT
    AB/BA — keeps the same physical slot order as the original).

    Returns per-pair-type:
      - n_pairs_with_same_orientation: matched coverage
      - n_winner_consistent / n_winner_flip: did the rejudgment agree?
      - same_orientation_flip_rate: retest noise floor
      - corpus-scope mean and per-judge breakdown
    """
    # Index re-judgments by (scenario_id, run_a, run_b, judge_model)
    rejudge_idx: dict[tuple[str, str, str, str], object] = {}
    for r in same_orientation_records:
        key = (r.scenario_id, r.run_id_a, r.run_id_b, r.judge_model)
        rejudge_idx[key] = r

    per_pair: dict[tuple[str, str], dict] = {}
    per_judge_per_pair: dict[tuple[str, str], dict[str, dict]] = {}

    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        pair_key = tuple(sorted([ca, cb]))
        original = p["ps"]  # key is "ps" per pair_tagged construction in compute_metrics
        key = (original.scenario_id, original.run_id_a, original.run_id_b, original.judge_model)
        rejudge = rejudge_idx.get(key)
        if rejudge is None:
            continue

        # Did the winner flip between original and same-orientation rejudgment?
        # Since position is held constant, this is pure retest noise.
        orig_winner = original.winner
        rejudge_winner = rejudge.winner
        flipped = (orig_winner != rejudge_winner) and orig_winner in ("A", "B") and rejudge_winner in ("A", "B")

        entry = per_pair.setdefault(pair_key, {"n_matched": 0, "n_flipped": 0})
        entry["n_matched"] += 1
        if flipped:
            entry["n_flipped"] += 1

        # Per-judge stratification (R11)
        per_judge_entry = per_judge_per_pair.setdefault(pair_key, {}).setdefault(
            original.judge_model, {"n_matched": 0, "n_flipped": 0}
        )
        per_judge_entry["n_matched"] += 1
        if flipped:
            per_judge_entry["n_flipped"] += 1

    # Compute corpus-scope same-orientation flip rates
    pair_results: dict[str, dict] = {}
    for pair_key, entry in sorted(per_pair.items()):
        n_m = entry["n_matched"]
        n_f = entry["n_flipped"]
        flip_rate = n_f / n_m if n_m else None
        pair_id = f"{pair_key[0]}_vs_{pair_key[1]}"

        per_judge_block: dict[str, dict] = {}
        for judge, j_entry in per_judge_per_pair.get(pair_key, {}).items():
            jm = j_entry["n_matched"]
            jf = j_entry["n_flipped"]
            per_judge_block[judge] = {
                "n_matched": jm,
                "n_flipped": jf,
                "same_orientation_flip_rate": round(jf / jm, 4) if jm else None,
            }

        # R11: per-judge heterogeneity — compute spread to detect cases where
        # the corpus-scope mean is misleading
        judge_rates = [b["same_orientation_flip_rate"] for b in per_judge_block.values()
                       if b["same_orientation_flip_rate"] is not None]
        per_judge_spread = (max(judge_rates) - min(judge_rates)) if len(judge_rates) >= 2 else None

        pair_results[pair_id] = {
            "n_pairs_with_same_orientation": n_m,
            "n_winner_flip": n_f,
            "same_orientation_flip_rate": round(flip_rate, 4) if flip_rate is not None else None,
            "by_judge": per_judge_block,
            "per_judge_spread": round(per_judge_spread, 4) if per_judge_spread is not None else None,
            "interpretation_descriptor_only": True,
            "interpretation_note": (
                "same_orientation_flip_rate = retest noise floor (position held constant). "
                "Reported as DESCRIPTIVE only per R11 — heterogeneity across judges may make "
                "the corpus-scope mean unstable. To get position-bias-net-of-noise, "
                "subtract this from the matching AB/BA flip_rate at the same pair (in the "
                "ab_ba_position_audit_same_author block) — but only if per_judge_spread is "
                "modest (≤0.10 ideally)."
            ),
        }

    return pair_results


# ---------------------------------------------------------------------------
# D3 — Reward-hacking diagnostics (v0.3 / R14 / GP5)
#
# Per-output surface features that judges may reward independently of
# substantive quality: output length, profile-reference count, hedging
# frequency, lexical overlap with source packet, refusal/safety markers.
# Phase 6 then runs a regression of judge preference on these covariates to
# test whether the preference effect survives after controlling for them.
# ---------------------------------------------------------------------------


def _compute_reward_hacking_diagnostics(outputs: list) -> dict:
    """Per-output surface-feature diagnostics for judge reward-hacking audit.

    Computes for each output:
      - char_count, word_count: length features
      - profile_reference_count: occurrences of profile-evoking phrases
      - tailoring_marker_count: phrases like "tailoring this to you"
      - hedging_frequency: hedging-word density per 100 words
      - source_packet_lexical_overlap: Jaccard overlap of content words
        between assistant response and source packet (for outputs with C5*
        conditions)
      - refusal_safety_marker_count: explicit refusal/safety phrases

    Returns per-condition summary statistics (mean, median) and per-output
    raw values keyed by output_id.
    """
    import re
    from collections import defaultdict

    # Detector vocabularies (intentionally simple; refine in v0.4)
    profile_reference_patterns = [
        r"\byour profile\b", r"\bgiven your\b", r"\bbased on what you've described\b",
        r"\byour pattern\b", r"\byour history\b", r"\byou tend to\b",
        r"\byour usual\b", r"\bfor you specifically\b",
    ]
    tailoring_markers = [
        r"\btailoring this\b", r"\bspecific to you\b",
        r"\bin your case\b", r"\bgiven who you are\b",
    ]
    hedging_words = [
        r"\bmight\b", r"\bcould\b", r"\bperhaps\b", r"\bpossibly\b",
        r"\bsuggests\b", r"\bmay\b", r"\bseems\b", r"\bappears\b",
        r"\bsomewhat\b", r"\bprobably\b", r"\blikely\b",
    ]
    refusal_safety_markers = [
        r"\bI can't\b", r"\bI cannot\b", r"\bI won't\b", r"\bnot able to\b",
        r"\bagainst\s+(?:my|safety)\b", r"\bnot appropriate\b",
    ]

    profile_re = re.compile("|".join(profile_reference_patterns), re.IGNORECASE)
    tailoring_re = re.compile("|".join(tailoring_markers), re.IGNORECASE)
    hedging_re = re.compile("|".join(hedging_words), re.IGNORECASE)
    refusal_re = re.compile("|".join(refusal_safety_markers), re.IGNORECASE)

    _content_word_re = re.compile(r"\b[a-z]{4,}\b", re.IGNORECASE)

    def _content_words(text: str) -> set[str]:
        return {w.lower() for w in _content_word_re.findall(text or "")}

    per_output: dict[str, dict] = {}
    per_condition: dict[str, list[dict]] = defaultdict(list)

    for o in outputs:
        response = getattr(o, "assistant_response", "") or ""
        profile_text = getattr(o, "profile_text_supplied", "") or ""
        condition = getattr(o, "condition", "?")
        output_id = getattr(o, "output_id", None) or getattr(o, "run_id", "?")

        word_count = len(response.split())
        char_count = len(response)

        n_profile_refs = len(profile_re.findall(response))
        n_tailoring = len(tailoring_re.findall(response))
        n_hedging = len(hedging_re.findall(response))
        n_refusal = len(refusal_re.findall(response))

        hedging_density = round(100 * n_hedging / word_count, 3) if word_count else 0.0

        # Lexical overlap with profile_text (proxy for source-packet overlap
        # since C5 conditions put the source packet in profile_text_supplied)
        response_words = _content_words(response)
        profile_words = _content_words(profile_text)
        if response_words and profile_words:
            overlap = len(response_words & profile_words) / max(1, len(response_words | profile_words))
        else:
            overlap = 0.0

        diag = {
            "char_count": char_count,
            "word_count": word_count,
            "profile_reference_count": n_profile_refs,
            "tailoring_marker_count": n_tailoring,
            "hedging_frequency_per_100w": hedging_density,
            "source_packet_lexical_overlap": round(overlap, 4),
            "refusal_safety_marker_count": n_refusal,
        }
        per_output[output_id] = diag
        per_condition[condition].append(diag)

    # Aggregate per condition
    per_condition_summary: dict[str, dict] = {}
    for cond, entries in per_condition.items():
        if not entries:
            continue
        per_condition_summary[cond] = {
            "n": len(entries),
            "mean_word_count": round(sum(e["word_count"] for e in entries) / len(entries), 1),
            "mean_profile_references": round(sum(e["profile_reference_count"] for e in entries) / len(entries), 2),
            "mean_tailoring_markers": round(sum(e["tailoring_marker_count"] for e in entries) / len(entries), 2),
            "mean_hedging_per_100w": round(sum(e["hedging_frequency_per_100w"] for e in entries) / len(entries), 2),
            "mean_lexical_overlap": round(sum(e["source_packet_lexical_overlap"] for e in entries) / len(entries), 4),
            "mean_refusal_markers": round(sum(e["refusal_safety_marker_count"] for e in entries) / len(entries), 2),
        }

    return {
        "per_output": per_output,
        "per_condition_summary": per_condition_summary,
        "notes": (
            "Phase 6 should run a logistic regression of pairwise-winner ~ "
            "diagnostic_covariates + condition_indicator to test whether the "
            "condition preference survives after controlling for surface features. "
            "Failure trigger #8: if >50% of judge-preference effect is explained "
            "by length + profile-references alone, mechanism claims need the "
            "covariate-controlled model (v0.3 plan §8.2)."
        ),
    }


# ---------------------------------------------------------------------------
# D2 — Paraphrased rubric anchor consistency (v0.3 Phase 3.3 / R12)
#
# Tests whether judges memorize the anchor wording or genuinely interpret the
# 10 anchored-rubric dimensions. Sampled at 15% of v0.3 scalar records.
# Reports per-judge ICC + Spearman ρ between original-anchor and paraphrased-
# anchor scalar scores. Distinguishes mean-shift, rank-stability, and
# threshold-crossing effects.
# ---------------------------------------------------------------------------


def _compute_paraphrased_anchor_consistency(
    anchored_scores: list,
    paraphrased_anchored_scores: list,
    *,
    dimensions: list[str] | None = None,
) -> dict:
    """Paraphrased-anchor consistency block (v0.3 D2 / R12).

    anchored_scores: original 06b_judge_anchored.md scores.
    paraphrased_anchored_scores: scores re-judged with paraphrased anchor wording.

    Joins by (assistant_output_id, judge_model). For each (output_id, judge),
    compares scalar scores per dimension between the two prompts.

    Reports:
      - mean_shift_per_dim: mean(paraphrased) − mean(original) per dimension
      - rank_correlation_per_dim: Spearman ρ over outputs
      - threshold_crossing_per_dim: fraction of outputs where the
        paraphrased version crosses the 5.0 midpoint differently
      - corpus-scope summary + per-judge breakdown
    """
    from collections import defaultdict
    from statistics import mean as _mean

    # Default dimensions from the v0.2 anchored rubric (10 dims)
    if dimensions is None:
        dimensions = [
            "helpfulness", "profile_fit", "calibrated_challenge", "anti_sycophancy",
            "agency_support", "epistemic_hygiene", "emotional_accuracy",
            "boundary_safety", "non_caricature", "transfer_value",
        ]

    # Dimensions live under the nested `.scores` object on AnchoredJudgeScore
    # (e.g. orig.scores.helpfulness), and records are keyed by `run_id`.
    def _dim_val(score_obj, dim):
        scores = getattr(score_obj, "scores", None)
        if scores is None:
            return None
        if isinstance(scores, dict):
            return scores.get(dim)
        return getattr(scores, dim, None)

    # Index paraphrased scores by (run_id, judge_model)
    para_idx: dict[tuple[str, str], object] = {}
    for s in paraphrased_anchored_scores:
        key = (getattr(s, "run_id", None), getattr(s, "judge_model", None))
        if key[0] and key[1]:
            para_idx[key] = s

    # Collect paired scores per dimension per judge
    paired: dict[str, dict[str, list[tuple[float, float]]]] = defaultdict(lambda: defaultdict(list))
    n_matched = 0

    for orig in anchored_scores:
        oid = getattr(orig, "run_id", None)
        judge = getattr(orig, "judge_model", None)
        if not (oid and judge):
            continue
        para = para_idx.get((oid, judge))
        if para is None:
            continue
        n_matched += 1

        for dim in dimensions:
            orig_val = _dim_val(orig, dim)
            para_val = _dim_val(para, dim)
            if orig_val is None or para_val is None:
                continue
            paired[judge][dim].append((float(orig_val), float(para_val)))

    if n_matched == 0:
        return {
            "n_matched": 0,
            "status": "no_paraphrased_records",
            "note": "Paraphrased anchor sentinel not yet run; block returns empty result.",
        }

    # Per-judge per-dimension consistency stats
    per_judge: dict[str, dict] = {}
    for judge, dim_pairs in paired.items():
        dim_results: dict[str, dict] = {}
        for dim, pairs in dim_pairs.items():
            if not pairs:
                continue
            orig_vals = [p[0] for p in pairs]
            para_vals = [p[1] for p in pairs]
            mean_shift = _mean(para_vals) - _mean(orig_vals)
            rank_corr = _spearman_rho(orig_vals, para_vals)
            crossings = sum(1 for o, p in pairs if (o >= 5.0) != (p >= 5.0))
            dim_results[dim] = {
                "n_paired": len(pairs),
                "mean_shift": round(mean_shift, 4),
                "spearman_rho": round(rank_corr, 4) if rank_corr is not None else None,
                "threshold_crossing_count": crossings,
                "threshold_crossing_rate": round(crossings / len(pairs), 4) if pairs else None,
            }
        per_judge[judge] = dim_results

    # Corpus-scope summary
    all_mean_shifts: list[float] = []
    all_rank_corrs: list[float] = []
    for judge_block in per_judge.values():
        for dim_block in judge_block.values():
            if dim_block.get("mean_shift") is not None:
                all_mean_shifts.append(dim_block["mean_shift"])
            if dim_block.get("spearman_rho") is not None:
                all_rank_corrs.append(dim_block["spearman_rho"])

    return {
        "n_matched": n_matched,
        "corpus_mean_shift": round(_mean(all_mean_shifts), 4) if all_mean_shifts else None,
        "corpus_mean_rank_corr": round(_mean(all_rank_corrs), 4) if all_rank_corrs else None,
        "max_mean_shift_observed": round(max(abs(s) for s in all_mean_shifts), 4) if all_mean_shifts else None,
        "min_rank_corr_observed": round(min(all_rank_corrs), 4) if all_rank_corrs else None,
        "per_judge": per_judge,
        "interpretation_note": (
            "Failure trigger #1 (v0.3 plan §8.2): if any dimension at any judge shows "
            ">=0.5 SD mean_shift OR rank order changes (Spearman rho < ~0.7), the anchored "
            "0-10 rubric is anchor-sensitive and all scalar claims downgrade. Threshold-"
            "crossing rate at the 5.0 midpoint indicates how often paraphrasing flipped "
            "the qualitative side of the rubric."
        ),
    }


def _spearman_rho(xs: list[float], ys: list[float]) -> float | None:
    """Spearman rank correlation, returns None if insufficient data."""
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    # Rank assignments (average ranks for ties)
    def _ranks(vals: list[float]) -> list[float]:
        sorted_indexed = sorted(enumerate(vals), key=lambda x: x[1])
        ranks = [0.0] * len(vals)
        i = 0
        while i < len(sorted_indexed):
            j = i
            while j + 1 < len(sorted_indexed) and sorted_indexed[j + 1][1] == sorted_indexed[i][1]:
                j += 1
            avg_rank = (i + j) / 2 + 1  # 1-indexed average rank
            for k in range(i, j + 1):
                ranks[sorted_indexed[k][0]] = avg_rank
            i = j + 1
        return ranks

    rx = _ranks(xs)
    ry = _ranks(ys)
    n = len(rx)
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    denom_x = sum((rx[i] - mean_rx) ** 2 for i in range(n))
    denom_y = sum((ry[i] - mean_ry) ** 2 for i in range(n))
    if denom_x == 0 or denom_y == 0:
        return None
    return num / (denom_x * denom_y) ** 0.5


# ---------------------------------------------------------------------------
# D4 — Tie-aware reinterpretation (v0.3 Phase 4 ternary sentinel / R12)
#
# Cross-prompt comparison: forced-choice lo_win vs ternary lo_win on the 10%
# tie/equipoise sentinel sample. Estimates the corpus-scoped tie rate per pair
# and reports a tie-aware reinterpretation alongside forced-choice headlines.
#
# Failure trigger #2 (v0.3 plan §8.2): tie rate >25% on a C5_CONTRACT-edge pair
# downgrades that pair's package claim ("tie-aware reinterpretation shows
# substantial equipoise; package claim is weaker than forced-choice suggests").
# ---------------------------------------------------------------------------


def _compute_tie_aware_reinterpretation(
    pair_tagged_same_author: list[dict],
    ternary_records: list,
) -> dict:
    """Tie-aware reinterpretation block (v0.3 D4 / R12).

    pair_tagged_same_author: original FORCED-CHOICE pairwise records.
    ternary_records: same-pair re-judgments with the ternary prompt
        (07b_pairwise_judge_ternary.md), where 'no_meaningful_difference'
        is an allowed winner value.

    For each pair-type where both forced-choice and ternary records exist on
    matching (run_a, run_b, judge), compute:
      - forced_choice_lo_win_rate (existing baseline)
      - ternary_lo_win_rate (excluding ties)
      - tie_rate = fraction of ternary judgments with no_meaningful_difference
      - tie_aware_reinterpretation: forced lo_win × (1 − tie_rate)

    NOTE: ternary records are NOT pooled with forced-choice for TOST.
    This block reports the tie rate as a sensitivity statistic only.
    """
    from collections import defaultdict

    # Index ternary by (scenario_id, run_a, run_b, judge_model)
    ternary_idx: dict[tuple[str, str, str, str], object] = {}
    for r in ternary_records:
        key = (r.scenario_id, r.run_id_a, r.run_id_b, r.judge_model)
        ternary_idx[key] = r

    per_pair_forced: dict[tuple[str, str], list[str]] = defaultdict(list)
    per_pair_ternary: dict[tuple[str, str], list[str]] = defaultdict(list)
    n_matched = 0

    for p in pair_tagged_same_author:
        ca, cb = p["cond_a"], p["cond_b"]
        pair_key = tuple(sorted([ca, cb]))
        record = p["ps"]  # key is "ps" per pair_tagged construction in compute_metrics
        key = (record.scenario_id, record.run_id_a, record.run_id_b, record.judge_model)
        tern = ternary_idx.get(key)
        if tern is None:
            continue
        n_matched += 1

        # Determine which condition is the "lo" (lower-numbered, canonical order)
        lo_cond = pair_key[0]
        # Forced-choice winner translated to lo/hi
        fw = record.winner
        if fw == "A":
            forced_lo_wins = ca == lo_cond
        elif fw == "B":
            forced_lo_wins = cb == lo_cond
        else:
            forced_lo_wins = None  # tie in forced-choice (rare)
        if forced_lo_wins is not None:
            per_pair_forced[pair_key].append("lo" if forced_lo_wins else "hi")

        # Ternary winner: lo / hi / no_meaningful_difference / tie
        tw = tern.winner
        if tw == "A":
            tern_outcome = "lo" if ca == lo_cond else "hi"
        elif tw == "B":
            tern_outcome = "lo" if cb == lo_cond else "hi"
        elif tw == "no_meaningful_difference":
            tern_outcome = "equipoise"
        else:
            tern_outcome = "tie"
        per_pair_ternary[pair_key].append(tern_outcome)

    if n_matched == 0:
        return {
            "n_matched": 0,
            "status": "no_ternary_records",
            "note": "Ternary tie/equipoise sentinel not yet run; block returns empty result.",
        }

    pair_results: dict[str, dict] = {}
    for pair_key in sorted(per_pair_forced.keys() | per_pair_ternary.keys()):
        forced_outcomes = per_pair_forced.get(pair_key, [])
        tern_outcomes = per_pair_ternary.get(pair_key, [])
        pair_id = f"{pair_key[0]}_vs_{pair_key[1]}"

        forced_n = len(forced_outcomes)
        forced_lo_win = forced_outcomes.count("lo") / forced_n if forced_n else None

        tern_n = len(tern_outcomes)
        tern_equipoise = tern_outcomes.count("equipoise")
        tern_decisive = tern_n - tern_equipoise - tern_outcomes.count("tie")
        tern_lo_win = (
            tern_outcomes.count("lo") / tern_decisive if tern_decisive else None
        )
        tie_rate = tern_equipoise / tern_n if tern_n else None

        pair_results[pair_id] = {
            "n_matched": tern_n,
            "forced_choice_lo_win_rate": round(forced_lo_win, 4) if forced_lo_win is not None else None,
            "ternary_lo_win_rate_excl_ties": round(tern_lo_win, 4) if tern_lo_win is not None else None,
            "tie_rate": round(tie_rate, 4) if tie_rate is not None else None,
            "n_decisive_ternary": tern_decisive,
            "n_equipoise_ternary": tern_equipoise,
            "tie_aware_reinterpretation": (
                round(forced_lo_win * (1 - tie_rate), 4)
                if forced_lo_win is not None and tie_rate is not None
                else None
            ),
        }

    return {
        "n_matched_total": n_matched,
        "by_pair": pair_results,
        "interpretation_note": (
            "Failure trigger #2 (v0.3 plan §8.2): tie_rate > 0.25 on a C5_CONTRACT-edge "
            "pair downgrades that pair's package claim. The tie_aware_reinterpretation "
            "value approximates 'what fraction of pairs would the lo-condition win if "
            "we counted equipoise pairs as no-effect'; this is a sensitivity statistic, "
            "NOT a replacement for the forced-choice headline."
        ),
    }


def _compute_human_rater_alignment(
    rater_inbox: list[dict],
    rater_responses: list[dict],
    pairwise: list,
    anchored_scores: list,
) -> dict:
    """v0.3 D5 — single-rater author sanity-check alignment statistic.

    Per docs/v0_3_phase_minus_1_design_lock.md §-1.13: this is a single-rater
    sanity check, NOT calibration. v0.4 will upgrade to ≥2 raters.

    Computes:
      - corpus-scope agreement_rate (rater winner vs LLM majority winner)
      - bootstrap 95% CI on agreement_rate (n_decisive resamples)
      - Pearson r between rater Δ (a−b on 3 dims, mean) and LLM Δ
        (a−b on 10 anchored dims, mean across judges)
      - per-stratum and per-pair-type breakdowns

    If rater_responses is empty or rater_inbox is empty, returns a stub
    with "not_run" status. v0.3 report should NOT use this block as
    construct-validity evidence; report wording per design-lock locked at
    "author-rater sanity check, n=1, NOT a calibration benchmark."
    """
    from collections import defaultdict
    import random as _rng_mod

    if not rater_responses or not rater_inbox:
        return {
            "status": "not_run",
            "n_pairs_rated": len(rater_responses),
            "n_pairs_in_inbox": len(rater_inbox),
            "interpretation_guard": (
                "Single-rater sanity check, NOT calibration. v0.3 report must "
                "frame as such; v0.4 upgrade to ≥2 raters."
            ),
        }

    # Index inbox by rater_pair_id for de-anonymization
    inbox_by_id = {rec["rater_pair_id"]: rec for rec in rater_inbox}

    # Index LLM pairwise by (scenario_id, run_a, run_b, judge_model)
    pw_idx: dict[tuple[str, str, str, str], list] = defaultdict(list)
    for p in pairwise:
        # Key on unsorted run_id_a/run_id_b for original A/B side
        pw_idx[(p.scenario_id, p.run_id_a, p.run_id_b, p.judge_model)].append(p)

    # Index anchored scores by (run_id, judge_model)
    anchored_idx: dict[tuple[str, str], list] = defaultdict(list)
    for s in anchored_scores:
        anchored_idx[(s.run_id, s.judge_model)].append(s)

    # Per-rated-pair join
    joined: list[dict] = []
    for rsp in rater_responses:
        rid = rsp.get("rater_pair_id")
        if not rid or rid not in inbox_by_id:
            continue
        inbox_rec = inbox_by_id[rid]
        run_a = inbox_rec["_original_run_id_a"]
        run_b = inbox_rec["_original_run_id_b"]
        sid = inbox_rec["scenario_id"]
        stratum = inbox_rec.get("stratum", "unknown")
        pair_type = tuple(inbox_rec.get("_pair_type") or [])
        a_is_orig_a = inbox_rec["_a_is_original_a"]

        # De-anonymize the rater's winner: convert "A" or "B" (as shown)
        # back to "original A" or "original B"
        rater_winner_shown = rsp.get("winner")
        if rater_winner_shown == "tie":
            rater_winner_orig = "tie"
        elif rater_winner_shown in ("A", "B"):
            shown_is_a = rater_winner_shown == "A"
            rater_winner_orig = "A" if (shown_is_a == a_is_orig_a) else "B"
        else:
            continue  # malformed

        # LLM majority winner across all judges that rated this exact (a, b) pair
        all_pw = pw_idx.get((sid, run_a, run_b, ""), [])
        all_pw_by_judge: dict[str, str] = {}
        for j_key in {k for k in pw_idx.keys()
                      if k[0] == sid and k[1] == run_a and k[2] == run_b}:
            for p in pw_idx[j_key]:
                all_pw_by_judge[p.judge_model] = p.winner
        if not all_pw_by_judge:
            continue
        winners = [w for w in all_pw_by_judge.values() if w in ("A", "B")]
        if not winners:
            continue
        # Majority winner (A/B vote)
        n_a = sum(1 for w in winners if w == "A")
        n_b = sum(1 for w in winners if w == "B")
        if n_a > n_b:
            llm_majority = "A"
        elif n_b > n_a:
            llm_majority = "B"
        else:
            llm_majority = "tie"

        # Rater scalar Δ (a − b) mean of 3 dims
        scalar_a = rsp.get("scalar_a", {})
        scalar_b = rsp.get("scalar_b", {})
        if scalar_a and scalar_b:
            dims = list(scalar_a.keys())
            r_delta = sum(scalar_a[d] - scalar_b[d] for d in dims) / len(dims)
        else:
            r_delta = None

        # LLM scalar Δ (mean across anchored dims and judges) on the original a / b
        def _output_avg(run_id: str) -> float | None:
            scores = []
            for (rid_, _j), recs in anchored_idx.items():
                if rid_ != run_id:
                    continue
                for s in recs:
                    vals = list(s.scores.values()) if hasattr(s, "scores") else []
                    if vals:
                        scores.append(sum(vals) / len(vals))
            if not scores:
                return None
            return sum(scores) / len(scores)

        a_llm, b_llm = _output_avg(run_a), _output_avg(run_b)
        llm_delta = (a_llm - b_llm) if (a_llm is not None and b_llm is not None) else None

        joined.append({
            "rater_pair_id": rid,
            "stratum": stratum,
            "pair_type": pair_type,
            "rater_winner_orig": rater_winner_orig,
            "llm_majority": llm_majority,
            "rater_delta": r_delta,
            "llm_delta": llm_delta,
            "decisive": rater_winner_orig != "tie" and llm_majority != "tie",
            "agree": (rater_winner_orig == llm_majority),
        })

    n = len(joined)
    decisive = [j for j in joined if j["decisive"]]
    n_dec = len(decisive)

    if n_dec == 0:
        agreement_rate = None
        ci = (None, None)
    else:
        agreement_rate = sum(1 for j in decisive if j["agree"]) / n_dec
        # Bootstrap CI (1000 resamples)
        rng = _rng_mod.Random(2026)
        boots = []
        for _ in range(1000):
            sample = [rng.choice(decisive) for _ in range(n_dec)]
            boots.append(sum(1 for j in sample if j["agree"]) / n_dec)
        boots.sort()
        ci = (boots[24], boots[974])  # 95% CI

    # Pearson r on (rater_delta, llm_delta)
    rd = [(j["rater_delta"], j["llm_delta"]) for j in joined
          if j["rater_delta"] is not None and j["llm_delta"] is not None]
    if len(rd) >= 3:
        rx = [r for r, _ in rd]
        ry = [l for _, l in rd]
        mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
        ssx = sum((x - mx) ** 2 for x in rx)
        ssy = sum((y - my) ** 2 for y in ry)
        sxy = sum((rx[i] - mx) * (ry[i] - my) for i in range(len(rd)))
        denom = (ssx * ssy) ** 0.5
        pearson_r = (sxy / denom) if denom > 0 else None
    else:
        pearson_r = None

    # Per-stratum
    per_stratum: dict[str, dict] = {}
    for stratum in {"T1", "T2", "v02_anchor"}:
        sd = [j for j in decisive if j["stratum"] == stratum]
        if not sd:
            continue
        per_stratum[stratum] = {
            "n_decisive": len(sd),
            "agreement_rate": sum(1 for j in sd if j["agree"]) / len(sd),
        }

    # Per pair type
    per_pair_type: dict[str, dict] = {}
    by_pt: dict[tuple, list[dict]] = defaultdict(list)
    for j in decisive:
        by_pt[j["pair_type"]].append(j)
    for pt, items in by_pt.items():
        key = " vs ".join(pt) if pt else "?"
        per_pair_type[key] = {
            "n_decisive": len(items),
            "agreement_rate": sum(1 for j in items if j["agree"]) / len(items),
        }

    return {
        "status": "computed",
        "n_pairs_rated": n,
        "n_decisive_pairs": n_dec,
        "agreement_rate": agreement_rate,
        "agreement_rate_bootstrap_ci_95": list(ci),
        "pearson_r_scalar_delta": pearson_r,
        "pearson_r_n": len(rd),
        "per_stratum": per_stratum,
        "per_pair_type": per_pair_type,
        "interpretation_guard": (
            "Single-rater sanity check, NOT calibration. n=1 rater means this "
            "block tests whether the LLM-judge majority sometimes lines up with "
            "one author's read; it does NOT establish ground truth. v0.4 "
            "upgrade to ≥2 raters with inter-rater reliability."
        ),
    }


def compute_metrics(
    run_tag: str,
    pilot_name: str = "micro_pilot",
    *,
    include_probes: bool = False,
) -> dict:
    """Compute the canonical metrics block for a v0.1 / v0.2 run.

    By default, judge records authored by non-official judges (e.g. Kimi
    feasibility probes) are excluded fail-closed before any analysis runs.
    Set ``include_probes=True`` to retain probe records in the analysis;
    canonical reports must NOT use this flag.
    """
    run_d = config.run_dir(run_tag)
    pilot_dir = config.pilot_dir(pilot_name)

    scenarios = {s.scenario_id: s for s in read_jsonl(pilot_dir / "scenarios.jsonl", Scenario)}
    users = {u.user_id: u for u in read_jsonl(pilot_dir / "synthetic_user_records.jsonl", SynthUserRecord)}

    seeds: dict[str, PersonaSeed] = {}
    for path in [config.SEED_BANK_PUBLIC, config.SEED_BANK_SYNTHETIC]:
        for seed in read_jsonl(path, PersonaSeed):
            seeds[seed.persona_id] = seed

    outputs = list(read_jsonl(run_d / "assistant_outputs.jsonl", AssistantOutput))
    raw_scores = list(read_jsonl(run_d / "judge_scores.jsonl", JudgeScore)) if (run_d / "judge_scores.jsonl").exists() else []
    anchored_path = run_d / "anchored_judge_scores.jsonl"
    raw_anchored = list(read_jsonl(anchored_path, AnchoredJudgeScore)) if anchored_path.exists() else []
    pairwise_path = run_d / "pairwise_scores.jsonl"
    raw_pairwise = list(read_jsonl(pairwise_path, PairwiseScore)) if pairwise_path.exists() else []
    # Phase 1 (2026-05-16): AB/BA counterbalanced rejudge records, if present.
    pairwise_swap_path = run_d / "pairwise_swap_scores.jsonl"
    raw_pairwise_swap = (
        list(read_jsonl(pairwise_swap_path, PairwiseScore))
        if pairwise_swap_path.exists() else []
    )
    # v0.3 Phase 3.2 (R11 / D1): same-orientation rejudgments (10% sample).
    # Re-judge the same (run_a, run_b, judge) tuple without swapping, so any
    # winner change is retest noise rather than position bias.
    same_orientation_path = run_d / "same_orientation_swap_scores.jsonl"
    raw_same_orientation = (
        list(read_jsonl(same_orientation_path, PairwiseScore))
        if same_orientation_path.exists() else []
    )
    # v0.3 Phase 3.3 (R12 / D2): paraphrased anchor sentinel (15% sample).
    # Re-judge a subset of scalar outputs with paraphrased anchor wording.
    paraphrased_anchored_path = run_d / "paraphrased_anchored_scores.jsonl"
    raw_paraphrased_anchored = (
        list(read_jsonl(paraphrased_anchored_path, AnchoredJudgeScore))
        if paraphrased_anchored_path.exists() else []
    )
    # v0.3 Phase 4 (R12 / D4): ternary tie/equipoise sentinel (10% sample).
    # Same pair re-judged with the 07b_pairwise_judge_ternary.md prompt; the
    # winner field can take "no_meaningful_difference" in addition to A/B/tie.
    pairwise_ternary_path = run_d / "pairwise_ternary_scores.jsonl"
    raw_pairwise_ternary = (
        list(read_jsonl(pairwise_ternary_path, PairwiseScore))
        if pairwise_ternary_path.exists() else []
    )

    # --- Fail-closed probe-record filter ----------------------------------
    # Records authored by judges outside OFFICIAL_JUDGES_V01 are exploratory
    # probes (e.g. Kimi feasibility runs). They never enter canonical analysis
    # unless include_probes=True is set explicitly.
    official = set(config.OFFICIAL_JUDGES_V01)
    def _is_official(s):
        return s.judge_model in official

    probe_counts: dict[str, int] = {}
    for s in raw_scores + raw_anchored + raw_pairwise:
        if not _is_official(s):
            probe_counts[s.judge_model] = probe_counts.get(s.judge_model, 0) + 1

    if include_probes:
        scores = list(raw_scores)
        anchored_scores = list(raw_anchored)
        pairwise = list(raw_pairwise)
        pairwise_swap = list(raw_pairwise_swap)
        same_orientation = list(raw_same_orientation)
        paraphrased_anchored = list(raw_paraphrased_anchored)
        pairwise_ternary = list(raw_pairwise_ternary)
    else:
        scores = [s for s in raw_scores if _is_official(s)]
        anchored_scores = [s for s in raw_anchored if _is_official(s)]
        pairwise = [p for p in raw_pairwise if _is_official(p)]
        pairwise_swap = [p for p in raw_pairwise_swap if _is_official(p)]
        same_orientation = [p for p in raw_same_orientation if _is_official(p)]
        paraphrased_anchored = [s for s in raw_paraphrased_anchored if _is_official(s)]
        pairwise_ternary = [p for p in raw_pairwise_ternary if _is_official(p)]
        if probe_counts:
            print(
                "[analyze] Excluded probe records by default: "
                + ", ".join(f"{m}={n}" for m, n in sorted(probe_counts.items()))
                + ". Pass --include-probes to override.",
                file=sys.stderr,
            )

    out_by_run = {o.run_id: o for o in outputs}
    user_by_id = {u.user_id: u for u in users.values()}

    def persona_type_for_scenario(sid: str) -> str | None:
        scen = scenarios.get(sid)
        if scen is None:
            return None
        u = user_by_id.get(scen.user_id)
        if u is None:
            return None
        seed = seeds.get(u.persona_seed_id)
        return seed.persona_type if seed else None

    # --- Legacy (0-5) scoring block ----------------------------------------
    legacy_block = _compute_scoring_block(
        scores, out_by_run, scenarios, persona_type_for_scenario, scale_max=5
    )

    # --- Anchored (0-10) scoring block (v0.2+) -----------------------------
    anchored_block = None
    if anchored_scores:
        anchored_block = _compute_scoring_block(
            anchored_scores, out_by_run, scenarios, persona_type_for_scenario, scale_max=10
        )

    # --- Pairwise analysis (cross-provider primary) ------------------------
    pair_block: dict = {}
    if pairwise:
        def _author_fam(run_id: str) -> str | None:
            out = out_by_run.get(run_id)
            return _provider_family(out.output_model) if out else None

        pair_tagged = []
        for ps in pairwise:
            out_a = out_by_run.get(ps.run_id_a)
            out_b = out_by_run.get(ps.run_id_b)
            if out_a is None or out_b is None:
                continue
            a_fam = _provider_family(out_a.output_model)
            b_fam = _provider_family(out_b.output_model)
            j_fam = _provider_family(ps.judge_model)
            # Cross-provider = judge family differs from BOTH authors'
            # families, OR authors are same-family but judge is the other
            # family. In this pilot both authors are present in every pair,
            # so we treat "cross-provider" as: judge_family != author_a_family
            # AND judge_family != author_b_family when authors differ. If
            # authors are same family, cross = judge != that family.
            if a_fam == b_fam:
                is_cross = j_fam != a_fam and j_fam != "other"
            else:
                is_cross = j_fam != a_fam and j_fam != b_fam and j_fam != "other"
            pair_tagged.append({
                "ps": ps,
                "out_a": out_a,
                "out_b": out_b,
                "cond_a": str(out_a.condition),
                "cond_b": str(out_b.condition),
                "author_a": out_a.output_model,
                "author_b": out_b.output_model,
                "author_a_family": a_fam,
                "author_b_family": b_fam,
                "judge_family": j_fam,
                "persona_type": persona_type_for_scenario(ps.scenario_id),
                "is_cross": is_cross,
            })

        # --- Cross-author leak detection (2026-05-15 review fix) -----------
        # The Opus C5_CONTRACT pairwise phase ran without --scope same_author_only
        # consistently, leaking ~179 cross-author records into the corpus.
        # External review (2026-05-15) flagged that the bundle text conflated
        # total pairwise records (3,123) with same-author records (true: 2,944).
        # Surface counts explicitly so downstream reports can not repeat this.
        cross_author_pairs = [p for p in pair_tagged if p["author_a"] != p["author_b"]]
        if cross_author_pairs:
            from collections import Counter as _Counter
            leak_by_judge: _Counter = _Counter()
            leak_by_pair: dict[str, int] = {}
            for p in cross_author_pairs:
                leak_by_judge[p["ps"].judge_model] += 1
                ca, cb = sorted([p["cond_a"], p["cond_b"]])
                k = f"{ca}_vs_{cb}"
                leak_by_pair[k] = leak_by_pair.get(k, 0) + 1
            pair_block["cross_author_leak_detection"] = {
                "n_cross_author_records": len(cross_author_pairs),
                "n_total_pairwise_records": len(pair_tagged),
                "by_judge": dict(sorted(leak_by_judge.items())),
                "by_pair": dict(sorted(leak_by_pair.items(), key=lambda kv: -kv[1])),
                "note": (
                    "Cross-author pairwise records were generated when the "
                    "--scope same_author_only flag was not consistently passed "
                    "to the Opus C5_CONTRACT pairwise phase. These records are "
                    "excluded from same-author analyses. If n>0 here, downstream "
                    "narrative must NOT label total pairwise counts as same-author."
                ),
            }

        cross_pairs = [p for p in pair_tagged if p["is_cross"]]

        # (a) Per-condition appearance-weighted win rate, same-author only,
        # so C4 vs C0 isn't conflated with Opus vs GPT.
        same_author_cross = [p for p in cross_pairs if p["author_a"] == p["author_b"]]

        def win_rate_table(pairs: list[dict]) -> dict:
            wins: Counter = Counter()
            appears: Counter = Counter()
            for p in pairs:
                appears[p["cond_a"]] += 1
                appears[p["cond_b"]] += 1
                w = p["ps"].winner
                if w == "A":
                    wins[p["cond_a"]] += 1
                elif w == "B":
                    wins[p["cond_b"]] += 1
                # ties split: add 0.5 to each
                elif w == "tie":
                    wins[p["cond_a"]] += 0.5
                    wins[p["cond_b"]] += 0.5
            return {c: round(wins[c] / appears[c], 3) for c in appears if appears[c] > 0}

        pair_block["win_rate_cross_provider_same_author"] = win_rate_table(same_author_cross)
        pair_block["win_rate_cross_provider_any_author"] = win_rate_table(cross_pairs)

        # (b) Per-condition-pair preference matrix, cross-provider + same-author.
        pref: dict[str, dict[str, int]] = {}
        for p in same_author_cross:
            key = f"{p['cond_a']}_vs_{p['cond_b']}"
            rev = f"{p['cond_b']}_vs_{p['cond_a']}"
            # canonicalize: always sort by condition code so we don't split C4vsC0 and C0vsC4
            ca, cb = sorted([p["cond_a"], p["cond_b"]])
            use_key = f"{ca}_vs_{cb}"
            bucket = pref.setdefault(use_key, {"a_wins": 0, "b_wins": 0, "ties": 0, "n": 0})
            bucket["n"] += 1
            w = p["ps"].winner
            if p["cond_a"] == ca:
                # A slot holds condition ca in original
                if w == "A":
                    bucket["a_wins"] += 1
                elif w == "B":
                    bucket["b_wins"] += 1
                else:
                    bucket["ties"] += 1
            else:
                # A slot holds cb; flip
                if w == "A":
                    bucket["b_wins"] += 1
                elif w == "B":
                    bucket["a_wins"] += 1
                else:
                    bucket["ties"] += 1
        # Append rates + Wilson intervals (95%, ties excluded for binomial CI)
        for k, b in pref.items():
            n = b["n"] or 1
            b["a_win_rate"] = round(b["a_wins"] / n, 3)
            b["b_win_rate"] = round(b["b_wins"] / n, 3)
            b["tie_rate"] = round(b["ties"] / n, 3)
            decisive_n = b["a_wins"] + b["b_wins"]
            ci_low, ci_high = wilson_interval(b["a_wins"], decisive_n)
            b["a_win_rate_decisive"] = round(b["a_wins"] / decisive_n, 3) if decisive_n else None
            b["a_win_ci95_low"] = ci_low
            b["a_win_ci95_high"] = ci_high
            b["decisive_n"] = decisive_n
        pair_block["pair_preference_cross_provider_same_author"] = dict(sorted(pref.items()))

        # (c) PI-only C5 pairs (brief §4: C5 only valid inside PI)
        pi_same_author = [p for p in same_author_cross if p["persona_type"] == "public_inspired"]
        pair_block["win_rate_cross_provider_PI_only"] = win_rate_table(pi_same_author)
        # Same-author parsing for PI only
        pref_pi: dict[str, dict[str, int]] = {}
        for p in pi_same_author:
            ca, cb = sorted([p["cond_a"], p["cond_b"]])
            use_key = f"{ca}_vs_{cb}"
            bucket = pref_pi.setdefault(use_key, {"a_wins": 0, "b_wins": 0, "ties": 0, "n": 0})
            bucket["n"] += 1
            w = p["ps"].winner
            if p["cond_a"] == ca:
                if w == "A":
                    bucket["a_wins"] += 1
                elif w == "B":
                    bucket["b_wins"] += 1
                else:
                    bucket["ties"] += 1
            else:
                if w == "A":
                    bucket["b_wins"] += 1
                elif w == "B":
                    bucket["a_wins"] += 1
                else:
                    bucket["ties"] += 1
        for k, b in pref_pi.items():
            n = b["n"] or 1
            b["a_win_rate"] = round(b["a_wins"] / n, 3)
            b["b_win_rate"] = round(b["b_wins"] / n, 3)
            b["tie_rate"] = round(b["ties"] / n, 3)
            decisive_n = b["a_wins"] + b["b_wins"]
            ci_low, ci_high = wilson_interval(b["a_wins"], decisive_n)
            b["a_win_rate_decisive"] = round(b["a_wins"] / decisive_n, 3) if decisive_n else None
            b["a_win_ci95_low"] = ci_low
            b["a_win_ci95_high"] = ci_high
            b["decisive_n"] = decisive_n
        pair_block["pair_preference_cross_provider_same_author_PI_only"] = dict(sorted(pref_pi.items()))

        # (d) Counts for sanity
        # 2026-05-15 review fix: explicit same-author count was previously
        # missing; bundle text conflated total_pairwise_records (3,123) with
        # same-author (true: 2,944). Surfacing both now so future reports
        # cannot repeat the conflation.
        _same_author_total = sum(
            1 for p in pair_tagged if p["author_a"] == p["author_b"]
        )
        _cross_author_total = len(pair_tagged) - _same_author_total
        pair_block["counts"] = {
            "total_pairwise_records": len(pairwise),
            "after_tagging": len(pair_tagged),
            "same_author": _same_author_total,
            "cross_author": _cross_author_total,
            "cross_provider": len(cross_pairs),
            "cross_provider_same_author": len(same_author_cross),
            "cross_provider_same_author_PI": len(pi_same_author),
        }

        # (e) Macro-averaged condition-pair preferences across (judge × author)
        # strata. Each stratum's a_win_rate (with ties split 0.5/0.5) is
        # computed, then unweighted-averaged. This reduces dominance of strata
        # with more pairs and is the recommended summary in brief §7.
        from collections import defaultdict as _dd
        stratum_pref: dict[str, dict[tuple[str, str], dict[str, int]]] = _dd(lambda: _dd(lambda: {"a_wins": 0.0, "b_wins": 0.0, "ties": 0.0, "n": 0}))
        for p in same_author_cross:
            ca, cb = sorted([p["cond_a"], p["cond_b"]])
            pair_key = f"{ca}_vs_{cb}"
            stratum_key = (p["ps"].judge_model, p["author_a"])
            cell = stratum_pref[pair_key][stratum_key]
            cell["n"] += 1
            w = p["ps"].winner
            if p["cond_a"] == ca:
                if w == "A":
                    cell["a_wins"] += 1
                elif w == "B":
                    cell["b_wins"] += 1
                else:
                    cell["ties"] += 1
            else:
                if w == "A":
                    cell["b_wins"] += 1
                elif w == "B":
                    cell["a_wins"] += 1
                else:
                    cell["ties"] += 1

        macro_pref: dict[str, dict] = {}
        for pair_key, strata in stratum_pref.items():
            stratum_rates: list[float] = []
            stratum_decisive_rates: list[float] = []
            for skey, cell in strata.items():
                if cell["n"]:
                    stratum_rates.append((cell["a_wins"] + 0.5 * cell["ties"]) / cell["n"])
                d_n = cell["a_wins"] + cell["b_wins"]
                if d_n:
                    stratum_decisive_rates.append(cell["a_wins"] / d_n)
            macro_pref[pair_key] = {
                "n_strata": len(strata),
                "macro_a_win_rate_ties_split": (
                    round(sum(stratum_rates) / len(stratum_rates), 3)
                    if stratum_rates else None
                ),
                "macro_a_win_rate_decisive": (
                    round(sum(stratum_decisive_rates) / len(stratum_decisive_rates), 3)
                    if stratum_decisive_rates else None
                ),
                "stratum_keys": [f"{j}__{a}" for j, a in sorted(strata.keys())],
            }
        pair_block["macro_avg_pair_preference_cross_provider_same_author"] = dict(sorted(macro_pref.items()))

        # --- Native v0.2 diagnostics (ported from v0.1 Round-2 §6e/§6f/§6g) ---
        # These regenerate with each metrics run rather than living in /tmp.
        # Tie rates and PI/PS split are computed on all-judges-pooled
        # same-author scope (matches v0.1 §6 framing). Length buckets target
        # any C5 / C5_CONTRACT pairs found in the data.
        same_author_all_judges = [
            p for p in pair_tagged if p["author_a"] == p["author_b"]
        ]
        pair_block["tie_rates_same_author"] = _compute_tie_rates(same_author_all_judges)
        pair_block["pi_ps_split_same_author"] = _compute_pi_ps_split_pairwise(
            same_author_all_judges
        )
        pair_block["length_buckets_same_author"] = _compute_length_buckets_pairwise(
            same_author_all_judges
        )
        pair_block["scenario_family_breakdowns_same_author"] = _compute_scenario_family_breakdowns(
            same_author_all_judges, scenarios
        )
        # Cluster-bootstrap CIs (cluster unit = persona × scenario × author).
        # Reported alongside Wilson, not replacing it. Conservative check.
        #
        # 2026-05-15 review fix: stratify by judge-provider relation so the
        # C5_CONTRACT findings can be checked against provider-family halo.
        # External reviewers (codex-council, gpt-max, gpt-pro) all flagged
        # that the unstratified "same-author" CI conflates cross-provider
        # and same-provider judging. Three blocks side-by-side now.
        pair_block["cluster_bootstrap_ci_same_author"] = _compute_cluster_bootstrap_pairwise(
            same_author_all_judges
        )
        # Cross-provider same-author: judge family != author family
        cross_provider_same_author_pairs = [
            p for p in same_author_all_judges
            if p["judge_family"] != p["author_a_family"]
            and p["judge_family"] != "other"
        ]
        pair_block["cluster_bootstrap_ci_cross_provider_same_author"] = (
            _compute_cluster_bootstrap_pairwise(cross_provider_same_author_pairs)
        )
        # Same-provider same-author: judge family == author family
        same_provider_same_author_pairs = [
            p for p in same_author_all_judges
            if p["judge_family"] == p["author_a_family"]
        ]
        pair_block["cluster_bootstrap_ci_same_provider_same_author"] = (
            _compute_cluster_bootstrap_pairwise(same_provider_same_author_pairs)
        )
        # Side-by-side coverage counts for the three scopes.
        pair_block["cluster_bootstrap_scope_counts"] = {
            "same_author_all_judges": len(same_author_all_judges),
            "cross_provider_same_author": len(cross_provider_same_author_pairs),
            "same_provider_same_author": len(same_provider_same_author_pairs),
        }

        # --- Scalar-pairwise reconciliation (2026-05-15 review fix) ---
        # GPT Pro flagged: C3 beats C5_CONTRACT on every PI scalar dimension
        # despite C5_CONTRACT winning pairwise. Build the per-pair paired-
        # delta block now so the contradiction is explicit and reproducible.
        if anchored_scores:
            pair_block["scalar_pairwise_reconciliation_same_author"] = (
                _compute_scalar_pairwise_reconciliation(
                    same_author_all_judges,
                    anchored_scores,
                    score_dimensions=tuple(SCORE_DIMENSIONS),
                )
            )

        # --- Per-(judge / author / persona) stratified pairwise (2026-05-15) ---
        # Codex-council: "GPT-5.4 actively reverses C3 vs C5_CONTRACT to ~57%"
        # — need first-class stratification not buried in narrative.
        # Persona Slalom Altar reverses C4 vs C5_CONTRACT to 34.3% per skeptic.
        pair_block["pairwise_by_judge_same_author"] = _compute_stratified_pairwise(
            same_author_all_judges,
            key_fn=lambda p: p["ps"].judge_model,
            key_label="judge_model",
        )
        pair_block["pairwise_by_author_same_author"] = _compute_stratified_pairwise(
            same_author_all_judges,
            key_fn=lambda p: p["author_a"],
            key_label="author_model",
        )
        pair_block["pairwise_by_persona_same_author"] = _compute_stratified_pairwise(
            same_author_all_judges,
            key_fn=lambda p: p["out_a"].user_id,
            key_label="user_id",
        )

        # --- A/B side audit (2026-05-15 review fix) ---
        # Position-bias diagnostic before AB/BA rejudging runs.
        pair_block["ab_side_audit_same_author"] = _compute_ab_side_audit(
            same_author_all_judges
        )

        # --- Length-adjusted summary (2026-05-15 review fix) ---
        # Headline lo_win restricted to "similar"-length-bucket pairs.
        # Flags pairs whose margin vanishes under length matching.
        pair_block["length_adjusted_summary_same_author"] = (
            _compute_length_adjusted_summary(same_author_all_judges)
        )

        # --- Cross-judge red-flag predictiveness (2026-05-15 review fix) ---
        # Replaces tautological within-judge red-flag→loss correlation.
        # Tests: does leave-out-judge's flag predict pairwise judge's call?
        if anchored_scores:
            pair_block["cross_judge_redflag_predictiveness_same_author"] = (
                _compute_cross_judge_redflag_predictiveness(
                    same_author_all_judges, anchored_scores
                )
            )

        # --- Macro vs micro aggregation (2026-05-15 review fix) ---
        # Headlines surviving only under pooled micro-averaging should be downgraded.
        pair_block["macro_vs_micro_aggregation_same_author"] = (
            _compute_macro_vs_micro_aggregation(same_author_all_judges, scenarios)
        )

        # --- Rubric lexical-overlap audit (2026-05-15 review fix) ---
        # Quantify whether each condition's profile prompt vocabulary
        # overlaps the anchored rubric language. If overlap is high, the
        # rubric may be rewarding "speaks-rubric-language" rather than
        # actual quality. Output goes to the top-level metrics (not pair_block)
        # because it's not pair-keyed.
        _rubric_overlap = _compute_rubric_lexical_overlap(
            pilot_dir / "profile_bundles.jsonl",
            Path(__file__).resolve().parent.parent.parent / "prompts" / "06b_judge_anchored.md",
        )

        # --- Missingness and balance audit (2026-05-15 review fix) ---
        pair_block["missingness_balance_audit"] = _compute_missingness_balance_audit(
            outputs, anchored_scores, same_author_all_judges, users, scenarios,
        )

        # --- Condition discoverability (2026-05-15 review fix; GPT-Pro §A17) ---
        # TF-IDF + logistic regression: can we predict condition from output text?
        # If yes, pairwise judges may be partly detecting recognizable treatment.
        _disc = _compute_condition_discoverability(outputs)
        if _disc is not None:
            pair_block["condition_discoverability"] = _disc

        # --- AB/BA position audit (Phase 1, 2026-05-16) ---
        # Joins original pairwise records with swapped-order rejudgments to
        # disambiguate position bias from condition preference.
        if pairwise_swap:
            pair_block["ab_ba_position_audit_same_author"] = (
                _compute_ab_ba_position_audit(same_author_all_judges, pairwise_swap)
            )
            # 2026-05-17 review fix: per-judge stratification + per-cell
            # four-way decomposition. Makes the methodology contribution
            # ("LLM judges show ~15-17pp slot-B preference") canonical and
            # reproducible from the metrics JSON.
            pair_block["ab_ba_position_audit_same_author_by_judge"] = (
                _compute_ab_ba_position_audit_by_judge(same_author_all_judges, pairwise_swap)
            )
            # 2026-05-17 review fix §2.8: cross-provider AB/BA stratification.
            # Demotes the Phase 0 cross-provider C3 vs C5_CONTRACT finding.
            pair_block["ab_ba_by_provider_scope_same_author"] = (
                _compute_ab_ba_by_provider_scope(same_author_all_judges, pairwise_swap)
            )
            # 2026-05-17 review fix §2.7: joint position × length AB/BA.
            # Settles the Phase 0 length-match vs Phase 1 AB/BA contradiction
            # for C4 vs C5 (and reports the joint for all pairs).
            pair_block["ab_ba_joint_position_length_same_author"] = (
                _compute_ab_ba_joint_position_length(same_author_all_judges, pairwise_swap)
            )
            pair_block["ab_ba_swap_coverage"] = {
                "n_swap_records_total": len(pairwise_swap),
                "n_original_records_total": len(pairwise),
            }

        # --- v0.3 D1: Same-orientation rejudge sentinel (R11) ---
        # Decomposes AB/BA flip rate into position-bias + retest-noise.
        # Addresses the Opus 4.6 steelman from v0.2 blog post round-1 review.
        if same_orientation:
            pair_block["same_orientation_sentinel_same_author"] = (
                _compute_same_orientation_sentinel(same_author_all_judges, same_orientation)
            )
            pair_block["same_orientation_sentinel_coverage"] = {
                "n_sentinel_records_total": len(same_orientation),
                "n_original_records_total": len(pairwise),
                "expected_coverage_pct": 10.0,  # 10% sample per Phase 3.2
            }

        # --- v0.3 D4: Tie-aware reinterpretation (R12) ---
        # Forced-choice lo_win vs ternary lo_win on the 10% sentinel sample.
        # Failure trigger #2: tie rate >25% downgrades pair claim.
        if pairwise_ternary:
            pair_block["tie_aware_reinterpretation_same_author"] = (
                _compute_tie_aware_reinterpretation(same_author_all_judges, pairwise_ternary)
            )

        # 2026-05-17 review fix A.7: persona × author cross-tabulation.
        # Tests whether persona-specific reversals (e.g. Slalom Altar)
        # are author-specific.
        pair_block["pairwise_by_persona_x_author_same_author"] = (
            _compute_pairwise_by_persona_x_author(same_author_all_judges)
        )

        # --- Leave-one-out fragility (2026-05-15 review fix) ---
        # Required diagnostic per consolidated review §3.1 #4-5. Drops one
        # judge / author / persona / family at a time and recomputes the
        # cluster-bootstrap CI. Flags any pair where removal flips direction
        # or attenuates by ≥5 percentage points.
        def _family_for_pair(p, scens):
            scn = scens.get(p["ps"].scenario_id)
            if not scn:
                return None
            fam = getattr(scn, "scenario_family", None)
            return str(fam) if fam else None

        pair_block["leave_one_judge_out_fragility"] = _compute_leave_one_out_fragility(
            same_author_all_judges,
            leave_out_fn=lambda p, _scens: p["ps"].judge_model,
            leave_out_label="judge_model",
            scenarios=scenarios,
        )
        pair_block["leave_one_author_out_fragility"] = _compute_leave_one_out_fragility(
            same_author_all_judges,
            leave_out_fn=lambda p, _scens: p["author_a"],
            leave_out_label="author_model",
            scenarios=scenarios,
        )
        pair_block["leave_one_persona_out_fragility"] = _compute_leave_one_out_fragility(
            same_author_all_judges,
            leave_out_fn=lambda p, _scens: p["out_a"].user_id,
            leave_out_label="user_id",
            scenarios=scenarios,
        )
        pair_block["leave_one_family_out_fragility"] = _compute_leave_one_out_fragility(
            same_author_all_judges,
            leave_out_fn=_family_for_pair,
            leave_out_label="scenario_family",
            scenarios=scenarios,
        )

    # --- Pairwise coverage diagnostics from planner ------------------------
    # Provides the expected-vs-observed view that backs the brief's
    # "pairwise-supported vs pairwise-confirmed" framing.
    pairwise_coverage: dict = {}
    try:
        from psycheeval.judge import (
            build_pairwise_plan,
            observed_pairwise_keys,
            pairwise_coverage_diagnostics,
        )
        # Use the same set of judges that appear in the data so coverage
        # numbers match what's actually expected for this run, not a config
        # default. If new judges show up, planner returns them.
        observed_judges = sorted({ps.judge_model for ps in pairwise}) or list(config.JUDGE_MODELS)
        plan, planner_diag = build_pairwise_plan(
            run_tag, pilot_name, judges=observed_judges, scope="exhaustive",
        )
        observed_keys, _ = observed_pairwise_keys(run_tag)
        pairwise_coverage = {
            "planner": planner_diag,
            "totals": {
                "expected": len(plan),
                "observed": len(observed_keys),
                "missing": max(0, len(plan) - len(observed_keys)),
                "coverage_pct": round(100 * min(len(observed_keys), len(plan)) / len(plan), 1) if plan else 0.0,
            },
            "strata": pairwise_coverage_diagnostics(plan, observed_keys),
        }
    except Exception as e:
        pairwise_coverage = {"error": f"planner failed: {e}"}

    # --- Inter-judge agreement (Cohen's κ + Spearman ρ) ---------------------
    from psycheeval.models import RedFlag
    label_vocab = [rf.value for rf in RedFlag]
    inter_judge_legacy = compute_inter_judge_agreement(
        scores, label_vocab=label_vocab, score_dimensions=SCORE_DIMENSIONS,
    ) if scores else {}
    inter_judge_anchored = compute_inter_judge_agreement(
        anchored_scores, label_vocab=label_vocab, score_dimensions=SCORE_DIMENSIONS,
    ) if anchored_scores else {}

    # --- Token / character summary by condition ----------------------------
    token_summary = _compute_token_summary(outputs)

    # --- Validation warnings (invalid red-flag labels) summary --------------
    # Brief §18: thresholds determine run status.
    #   0 invalid          → status "ok"
    #   ≤1% of records     → status "ok" (still surfaced in appendix)
    #   1-5% of records    → status "warning"
    #   >5% of records     → status "failed_validation"
    warnings_path = run_d / "validation_warnings.jsonl"
    validation_warnings: dict = {
        "count": 0,
        "by_judge": {},
        "by_label": {},
        "by_condition": {},
        "by_author_model": {},
        "by_scenario_family": {},
        "examples": [],
        "rate_of_judged_records": 0.0,
        "run_status": "ok",
    }
    if warnings_path.exists():
        by_judge: Counter = Counter()
        by_label: Counter = Counter()
        by_cond: Counter = Counter()
        by_author: Counter = Counter()
        by_fam: Counter = Counter()
        examples: list[dict] = []
        total = 0
        for line in warnings_path.open():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            total += 1
            by_judge[rec.get("judge_model", "unknown")] += 1
            by_label[rec.get("invalid_label", "unknown")] += 1
            by_cond[rec.get("condition", "unknown")] += 1
            by_author[rec.get("author_model", "unknown")] += 1
            # Look up scenario family if context_id maps to a known scenario
            scen_id = rec.get("scenario_id") or rec.get("context_id", "")
            scen = scenarios.get(scen_id) if isinstance(scen_id, str) else None
            fam = str(scen.scenario_family) if scen else "unknown"
            by_fam[fam] += 1
            if len(examples) < 8:
                examples.append({
                    "label": rec.get("invalid_label"),
                    "judge": rec.get("judge_model"),
                    "author": rec.get("author_model"),
                    "condition": rec.get("condition"),
                    "mode": rec.get("mode"),
                    "scenario_family": fam,
                })

        # Total judged records (legacy + anchored + pairwise)
        total_judged = len(scores) + len(anchored_scores) + len(pairwise)
        rate = (total / total_judged) if total_judged else 0.0
        if total == 0:
            run_status = "ok"
        elif rate <= 0.01:
            run_status = "ok"
        elif rate <= 0.05:
            run_status = "warning"
        else:
            run_status = "failed_validation"
        validation_warnings = {
            "count": total,
            "rate_of_judged_records": round(rate, 4),
            "run_status": run_status,
            "by_judge": dict(by_judge.most_common()),
            "by_label": dict(by_label.most_common()),
            "by_condition": dict(by_cond.most_common()),
            "by_author_model": dict(by_author.most_common()),
            "by_scenario_family": dict(by_fam.most_common()),
            "examples": examples,
        }

    # --- Corpus counts -----------------------------------------------------
    counts = {
        "scenarios": len(scenarios),
        "users": len(users),
        "assistant_outputs": len(outputs),
        "judge_scores": len(scores),
        "anchored_judge_scores": len(anchored_scores),
        "pairwise_scores": len(pairwise),
    }

    result: dict = {
        "counts": counts,
        "primary_cross_provider": legacy_block["primary_cross_provider"],
        "secondary_all_judges": legacy_block["secondary_all_judges"],
        "halo_audit_same_minus_cross": legacy_block["halo_audit_same_minus_cross"],
        "halo_audit_exact_self_minus_cross": legacy_block.get("halo_audit_exact_self_minus_cross", {}),
        "halo_audit_same_provider_minus_cross": legacy_block.get("halo_audit_same_provider_minus_cross", {}),
        "red_flag_frequency_total": legacy_block["red_flag_frequency_total"],
        "red_flag_stratification_legacy": _compute_red_flag_stratification(
            scores, out_by_run, judge_provider_family_fn=_provider_family
        ),
        "red_flag_stratification_anchored": (
            _compute_red_flag_stratification(
                anchored_scores, out_by_run, judge_provider_family_fn=_provider_family
            ) if anchored_scores else None
        ),
        "scalar_inter_judge_agreement_legacy": _compute_scalar_inter_judge_agreement(
            scores, out_by_run, score_dimensions=tuple(SCORE_DIMENSIONS)
        ),
        "scalar_inter_judge_agreement_anchored": (
            _compute_scalar_inter_judge_agreement(
                anchored_scores, out_by_run, score_dimensions=tuple(SCORE_DIMENSIONS)
            ) if anchored_scores else None
        ),
        # 2026-05-17 review fix §2.5: complete-case scalar means.
        "complete_case_scalar_anchored": (
            _compute_complete_case_scalar(
                anchored_scores, outputs, score_dimensions=tuple(SCORE_DIMENSIONS)
            ) if anchored_scores else None
        ),
        "pairwise": pair_block,
        "pairwise_coverage": pairwise_coverage,
        "rubric_lexical_overlap": _rubric_overlap if pairwise else None,
        "_claim_ledger_placeholder": None,  # populated below from `result` itself
        "token_summary_by_condition": token_summary,
        "validation_warnings_summary": validation_warnings,
        "inter_judge_agreement_legacy": inter_judge_legacy,
        "inter_judge_agreement_anchored": inter_judge_anchored,
        "scale_max_legacy": 5,
        "shared_conditions": legacy_block["shared_conditions"],
        "all_conditions": legacy_block["all_conditions"],
    }
    if anchored_block is not None:
        result["anchored"] = {
            "scale_max": 10,
            "primary_cross_provider": anchored_block["primary_cross_provider"],
            "secondary_all_judges": anchored_block["secondary_all_judges"],
            "halo_audit_same_minus_cross": anchored_block["halo_audit_same_minus_cross"],
            "halo_audit_exact_self_minus_cross": anchored_block.get("halo_audit_exact_self_minus_cross", {}),
            "halo_audit_same_provider_minus_cross": anchored_block.get("halo_audit_same_provider_minus_cross", {}),
            "red_flag_frequency_total": anchored_block["red_flag_frequency_total"],
            "shared_conditions": anchored_block["shared_conditions"],
            "all_conditions": anchored_block["all_conditions"],
        }

    # --- v0.3 D2: Paraphrased anchor consistency sentinel (R12) ---
    # Tests rubric anchor sensitivity on 15% scalar subset. Failure trigger #1.
    if paraphrased_anchored:
        result["paraphrased_anchor_consistency"] = (
            _compute_paraphrased_anchor_consistency(anchored_scores, paraphrased_anchored)
        )
        result["paraphrased_anchor_coverage"] = {
            "n_paraphrased_records_total": len(paraphrased_anchored),
            "n_original_anchored_records_total": len(anchored_scores),
            "expected_coverage_pct": 15.0,  # 15% sample per Phase 3.3
        }

    # --- v0.3 D3: Reward-hacking diagnostics (R14 / GP5) ---
    # Per-output surface features for judge reward-hacking audit. Always
    # computed (uses existing outputs; no new file needed).
    result["reward_hacking_diagnostics"] = _compute_reward_hacking_diagnostics(outputs)

    # --- v0.3 D5: Human-rater alignment (single-rater sanity check) ---
    # Per design-lock §-1.13: this is NOT calibration. Reports as
    # author-rater sanity check, n=1. v0.4 upgrades to ≥2 raters.
    rater_inbox_path = run_d / "human_rater_inbox.jsonl"
    rater_responses_path = run_d / "human_rater_responses.jsonl"
    if rater_responses_path.exists() and rater_inbox_path.exists():
        rater_inbox: list[dict] = []
        with rater_inbox_path.open() as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rater_inbox.append(json.loads(line))
        rater_responses: list[dict] = []
        with rater_responses_path.open() as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rater_responses.append(json.loads(line))
        result["human_rater_alignment"] = _compute_human_rater_alignment(
            rater_inbox, rater_responses, pairwise, anchored_scores,
        )

    # 2026-05-17 review fix §2.3: build claim ledger from existing blocks.
    # The ledger is the canonical per-claim summary for the curated report.
    result["claim_ledger"] = _build_claim_ledger(result)
    result.pop("_claim_ledger_placeholder", None)

    return result


# ============================================================================
# Report generation
# ============================================================================


def _fmt_row_means(stats_block: dict, cond: str) -> str:
    stats = stats_block.get(cond, {})
    cells = [cond]
    for dim in SCORE_DIMENSIONS:
        v = stats.get(dim, {}).get("mean")
        cells.append(f"{v:.3f}" if isinstance(v, (int, float)) else "—")
    rf = stats.get("red_flag_rate")
    cells.append(f"{rf:.3f}" if isinstance(rf, (int, float)) else "—")
    cells.append(str(stats.get("n", "—")))
    return "| " + " | ".join(cells) + " |"


def _means_table_header() -> list[str]:
    headers = ["Condition"] + SCORE_DIMENSIONS + ["red_flag_rate", "n"]
    return [
        "| " + " | ".join(headers) + " |",
        "|" + "---|" * len(headers),
    ]


def write_report(run_tag: str, metrics: dict, pilot_name: str = "micro_pilot") -> Path:
    report_path = config.REPORTS_DIR / f"psycheeval_v0_1_{pilot_name}_{run_tag}_autogen.md"
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    L: list[str] = []
    L.append(f"# PsycheEval v0.1 — {pilot_name} — run {run_tag} (auto-generated)")
    L.append("")
    L.append(f"> Auto-generated numeric scaffold. The human-curated narrative report lives at "
             f"`psycheeval_v0_1_{pilot_name}_{run_tag}.md`. This file contains only tables "
             f"computed from `metrics_{run_tag}.json`. Regenerating analyze.py will overwrite "
             f"this file but never the curated one.")
    L.append("")
    # 2026-05-17 review fix §2.3: claim ledger as the report's central artifact.
    # Replaces the split between "Final AB/BA results" and "Final tier assignment"
    # — single source of truth, with controlled estimates, scope qualifiers,
    # allowed/forbidden wording per claim.
    ledger = metrics.get("claim_ledger", {})
    rows = ledger.get("rows", [])
    if rows:
        L.append("## Claim ledger (canonical per-claim summary)")
        L.append("")
        L.append(
            "Source: 2026-05-17 round-2 consolidated review §2.3 — unanimously "
            "endorsed as the report's central artifact. Each row pairs the claim "
            "with its position-controlled estimate, scope qualifiers, scalar "
            "alignment, and explicit allowed/forbidden wording for the curated "
            "report. Tier 1 / 1.5 / 2 reflect round-2 verdict."
        )
        L.append("")
        L.append("| tier | claim | controlled lo_win | Bootstrap CI | scalar Δ_total | judge scope | survives swap? |")
        L.append("|---|---|---:|---|---:|---|---|")
        for row in rows:
            ctrl = row.get("controlled_lo_win_rate")
            ctrl_s = f"{ctrl:.3f}" if ctrl is not None else "—"
            bci = row.get("controlled_bootstrap_ci") or [None, None]
            bci_s = f"[{bci[0]:.3f}, {bci[1]:.3f}]" if bci[0] is not None else "—"
            scalar = row.get("scalar_delta_total")
            scalar_s = f"{scalar:+.3f}" if scalar is not None else "—"
            survives = row.get("ab_ba_survives_swap")
            survives_s = "✓" if survives else ("⚠" if survives is False else "—")
            L.append(
                f"| {row['tier']} | {row['headline']} | "
                f"{ctrl_s} | {bci_s} | {scalar_s} | "
                f"{row['judge_scope']} | {survives_s} |"
            )
        L.append("")
        L.append("### Wording guidance per claim")
        L.append("")
        for row in rows:
            L.append(f"**[{row['tier']}] {row['headline']}** (`{row['claim_id']}`)")
            L.append("")
            L.append(f"- ✅ Allowed: {row['allowed_wording']}")
            L.append(f"- ❌ Forbidden: {row['forbidden_wording']}")
            jpl_lo = row.get("joint_length_position_lo_win")
            if jpl_lo is not None:
                jpl_ci = row.get("joint_length_position_ci") or [None, None]
                jpl_ci_s = f"[{jpl_ci[0]:.3f}, {jpl_ci[1]:.3f}]" if jpl_ci[0] is not None else "—"
                L.append(f"- Joint position+length corrected lo_win: {jpl_lo:.3f} {jpl_ci_s} (n={row.get('joint_length_position_n')})")
            L.append("")

    L.append("## Dataset composition")
    L.append("")
    for k, v in metrics["counts"].items():
        L.append(f"- **{k}**: {v}")
    L.append("")

    primary = metrics["primary_cross_provider"]

    def emit_means(title: str, block_key: str, explainer: str) -> None:
        block = primary.get(block_key, {})
        if not block:
            return
        L.append(f"## {title}")
        L.append("")
        L.append(explainer)
        L.append("")
        L.extend(_means_table_header())
        for cond in sorted(block.keys()):
            L.append(_fmt_row_means(block, cond))
        L.append("")

    emit_means(
        "Primary: C0–C4 across all personas (cross-provider judged)",
        "by_condition_C0C4_all_personas",
        "Every response scored by the opposite provider family's judge. C5 excluded — it exists only for public-inspired personas and is reported separately below.",
    )
    emit_means(
        "PI subset: C0–C4, public-inspired personas only (cross-provider)",
        "by_condition_C0C4_PI_only",
        "Public-inspired personas under the shared condition set, for parity with the all-persona table above.",
    )
    emit_means(
        "PI subset with C5: C0–C5, public-inspired personas only (cross-provider)",
        "by_condition_C0C5_PI_only",
        "This is the only valid comparison involving C5. Do NOT cross-compare C5 here against C0–C4 in the all-persona table — different persona subsets.",
    )
    emit_means(
        "PS subset: C0–C4, pure synthetic personas only (cross-provider)",
        "by_condition_C0C4_PS_only",
        "Pure-synthetic personas under the shared condition set.",
    )

    # Deltas
    def emit_deltas(title: str, key: str) -> None:
        blk = primary.get(key, {})
        if not blk:
            return
        L.append(f"## {title}")
        L.append("")
        for pair, deltas in blk.items():
            if not deltas:
                continue
            L.append(f"### {pair}")
            L.append("")
            for dim in SCORE_DIMENSIONS:
                v = deltas.get(dim)
                if v is None:
                    continue
                L.append(f"- `{dim}`: {v:+.3f}")
            L.append("")

    emit_deltas("Deltas: all personas, C0–C4 (cross-provider)", "deltas_C0C4_all_personas")
    emit_deltas("Deltas: PI-only, C0–C5 (cross-provider)", "deltas_C0C5_PI_only")
    emit_deltas("Deltas: PS-only, C0–C4 (cross-provider)", "deltas_C0C4_PS_only")

    pi_vs_ps = primary.get("pi_minus_ps_by_condition", {})
    if pi_vs_ps:
        L.append("## Public-inspired minus pure-synthetic, by condition (cross-provider)")
        L.append("")
        for cond in sorted(pi_vs_ps.keys()):
            L.append(f"### {cond}")
            L.append("")
            for dim in SCORE_DIMENSIONS:
                v = pi_vs_ps[cond].get(dim)
                if v is None:
                    continue
                L.append(f"- `{dim}`: {v:+.3f}")
            L.append("")

    # Red-flag label rates
    def emit_rf_table(title: str, key: str, note: str) -> None:
        rf = primary.get(key, {})
        if not rf:
            return
        L.append(f"## {title}")
        L.append("")
        L.append(note)
        L.append("")
        # Collect union of labels
        labels = set()
        for cond_flags in rf.values():
            for lbl in cond_flags.keys():
                if lbl != "_n":
                    labels.add(lbl)
        labels_sorted = sorted(labels)
        if not labels_sorted:
            L.append("_No red flags recorded in this partition._")
            L.append("")
            return
        conds_sorted = sorted(rf.keys())
        header = ["flag"] + conds_sorted
        L.append("| " + " | ".join(header) + " |")
        L.append("|" + "---|" * len(header))
        for lbl in labels_sorted:
            cells = [lbl]
            for cond in conds_sorted:
                v = rf[cond].get(lbl, 0.0)
                cells.append(f"{v:.3f}")
            L.append("| " + " | ".join(cells) + " |")
        L.append("")

    emit_rf_table(
        "Red-flag label rate: C0–C4, all personas (cross-provider)",
        "red_flag_label_rate_C0C4_all_personas",
        "Rate = flag count / scores in that condition. 0.000 means zero appearances.",
    )
    emit_rf_table(
        "Red-flag label rate: C0–C5, PI-only (cross-provider)",
        "red_flag_label_rate_C0C5_PI_only",
        "PI-only; the only valid comparison involving C5.",
    )

    # Author comparison
    auth = primary.get("by_condition_author_cross_provider", {})
    if auth:
        L.append("## Author comparison (cross-provider judged)")
        L.append("")
        L.append("Each response scored by the opposite provider family's judge. Same-author rows are directly comparable; cross-author rows cover different scenario × condition cells.")
        L.append("")
        L.extend(_means_table_header())
        for key in sorted(auth.keys()):
            stats = auth[key]
            cells = [key]
            for dim in SCORE_DIMENSIONS:
                v = stats.get(dim, {}).get("mean")
                cells.append(f"{v:.3f}" if isinstance(v, (int, float)) else "—")
            rf = stats.get("red_flag_rate")
            cells.append(f"{rf:.3f}" if isinstance(rf, (int, float)) else "—")
            cells.append(str(stats.get("n", "—")))
            L.append("| " + " | ".join(cells) + " |")
        L.append("")

    # Scenario family breakdown
    fam = primary.get("by_family_condition_cross_provider", {})
    if fam:
        L.append("## Scenario-family × condition (cross-provider, C0–C4)")
        L.append("")
        L.append("Mean helpfulness + calibrated_challenge + anti_sycophancy + agency_support (average of four). C4–C0 delta column shows the composite uplift.")
        L.append("")
        # Collect fam→cond→composite
        composite: dict[str, dict[str, float]] = {}
        for key, stats in fam.items():
            try:
                f, cond = key.split("__", 1)
            except ValueError:
                continue
            comp_dims = ["helpfulness", "calibrated_challenge", "anti_sycophancy", "agency_support"]
            vals = [stats.get(d, {}).get("mean", 0.0) for d in comp_dims]
            composite.setdefault(f, {})[cond] = round(mean(vals), 3) if vals else 0.0
        L.append("| family | C0 | C1 | C3 | C4 | C4−C0 |")
        L.append("|" + "---|" * 6)
        for f in sorted(composite.keys()):
            row = composite[f]
            c0 = row.get("C0")
            c4 = row.get("C4")
            delta = round(c4 - c0, 3) if (c0 is not None and c4 is not None) else None
            def fmt(x): return f"{x:.3f}" if isinstance(x, (int, float)) else "—"
            L.append(f"| {f} | {fmt(row.get('C0'))} | {fmt(row.get('C1'))} | {fmt(row.get('C3'))} | {fmt(row.get('C4'))} | {fmt(delta)} |")
        L.append("")

    # Halo audit
    halo = metrics.get("halo_audit_same_minus_cross", {})
    if halo:
        L.append("## Halo audit: same-provider minus cross-provider")
        L.append("")
        L.append("Positive values = same-provider judging inflates scores. |Δ| ≥ 0.30 flagged ⚠.")
        L.append("")
        for key in sorted(halo.keys()):
            L.append(f"### {key}")
            L.append("")
            for dim in SCORE_DIMENSIONS:
                v = halo[key].get(dim)
                if v is None:
                    continue
                marker = " ⚠️" if abs(v) >= 0.3 else ""
                L.append(f"- `{dim}`: {v:+.3f}{marker}")
            L.append("")

    # Pairwise
    pair = metrics.get("pairwise", {})
    if pair:
        L.append("## Pairwise results (cross-provider judged)")
        L.append("")
        counts = pair.get("counts", {})
        if counts:
            L.append("### Counts")
            L.append("")
            for k, v in counts.items():
                L.append(f"- **{k}**: {v}")
            L.append("")
        wr = pair.get("win_rate_cross_provider_same_author", {})
        if wr:
            L.append("### Condition win-rate (same-author pairs, cross-provider judged)")
            L.append("")
            L.append("Ties contribute 0.5 to each side. Same-author pairs isolate condition effects from author effects.")
            L.append("")
            for cond in sorted(wr.keys()):
                L.append(f"- **{cond}**: {wr[cond]:.3f}")
            L.append("")
        pref = pair.get("pair_preference_cross_provider_same_author", {})
        if pref:
            L.append("### Condition-pair preferences (same-author, cross-provider)")
            L.append("")
            L.append("| pair | n | first wins | second wins | ties |")
            L.append("|---|---|---|---|---|")
            for k in sorted(pref.keys()):
                b = pref[k]
                first, second = k.split("_vs_")
                L.append(f"| {first} vs {second} | {b['n']} | {b['a_win_rate']:.3f} | {b['b_win_rate']:.3f} | {b['tie_rate']:.3f} |")
            L.append("")
        pi_pref = pair.get("pair_preference_cross_provider_same_author_PI_only", {})
        if pi_pref:
            L.append("### Condition-pair preferences (PI-only, same-author, cross-provider)")
            L.append("")
            L.append("C5 pairs appear here and here only — never in the all-persona block.")
            L.append("")
            L.append("| pair | n | first wins | second wins | ties |")
            L.append("|---|---|---|---|---|")
            for k in sorted(pi_pref.keys()):
                b = pi_pref[k]
                first, second = k.split("_vs_")
                L.append(f"| {first} vs {second} | {b['n']} | {b['a_win_rate']:.3f} | {b['b_win_rate']:.3f} | {b['tie_rate']:.3f} |")
            L.append("")

    # Red-flag totals
    rf = metrics.get("red_flag_frequency_total", {})
    if rf:
        L.append("## Red-flag frequency (total, across all judges)")
        L.append("")
        for flag, count in rf.items():
            L.append(f"- `{flag}`: {count}")
        L.append("")

    # Appendix: all-judge tables
    secondary = metrics.get("secondary_all_judges", {})
    if secondary:
        L.append("---")
        L.append("")
        L.append("## Appendix A — Secondary: all-judge means")
        L.append("")
        L.append("**Do not use these as primary results.** Same-provider scores are included. "
                 "See halo audit for why this matters. Kept for audit only.")
        L.append("")
        blk = secondary.get("by_condition_all_data_all_judges", {})
        if blk:
            L.append("### By condition, all personas, all judges")
            L.append("")
            L.extend(_means_table_header())
            for cond in sorted(blk.keys()):
                L.append(_fmt_row_means(blk, cond))
            L.append("")
        cj = secondary.get("by_condition_judge", {})
        if cj:
            L.append("### By condition × judge")
            L.append("")
            L.extend(_means_table_header())
            for key in sorted(cj.keys()):
                stats = cj[key]
                cells = [key]
                for dim in SCORE_DIMENSIONS:
                    v = stats.get(dim, {}).get("mean")
                    cells.append(f"{v:.3f}" if isinstance(v, (int, float)) else "—")
                rf_v = stats.get("red_flag_rate")
                cells.append(f"{rf_v:.3f}" if isinstance(rf_v, (int, float)) else "—")
                cells.append(str(stats.get("n", "—")))
                L.append("| " + " | ".join(cells) + " |")
            L.append("")

    # ---- v0.2 native diagnostics (ported from v0.1 Round-2 ad-hoc scripts) ----
    pw = metrics.get("pairwise", {})

    tie = pw.get("tie_rates_same_author", {})
    if tie:
        L.append("---")
        L.append("")
        L.append("## Tie rates (same-author, all-judges-pooled)")
        L.append("")
        L.append("| pair | total | decisive | ties | tie_rate | lo decisive win |")
        L.append("|---|---:|---:|---:|---:|---:|")
        for pair_key in sorted(tie.keys()):
            t = tie[pair_key]
            tie_rate = t.get("tie_rate", 0.0)
            lo_wr = t.get("lo_decisive_win_rate")
            lo_str = f"{lo_wr:.4f}" if lo_wr is not None else "—"
            L.append(
                f"| {pair_key.replace('_vs_', ' vs ')} | "
                f"{t['total']} | {t['decisive']} | {t['ties']} | {tie_rate:.4f} | {lo_str} |"
            )
        L.append("")

    pi_ps = pw.get("pi_ps_split_same_author", {})
    if pi_ps:
        L.append("## PI/PS split pairwise (same-author, all-judges-pooled, non-C5 pairs)")
        L.append("")
        L.append("| pair | PI lo win | PI CI95 | PI n | PS lo win | PS CI95 | PS n |")
        L.append("|---|---:|---|---:|---:|---|---:|")
        for pair_key in sorted(pi_ps.keys()):
            pi = pi_ps[pair_key].get("PI", {}) or {}
            ps = pi_ps[pair_key].get("PS", {}) or {}

            def _row(slice_):
                wr = slice_.get("lo_decisive_win_rate")
                ci_lo = slice_.get("ci95_low")
                ci_hi = slice_.get("ci95_high")
                n = slice_.get("n_decisive")
                wr_s = f"{wr:.4f}" if wr is not None else "—"
                ci_s = (
                    f"[{ci_lo:.4f}, {ci_hi:.4f}]"
                    if ci_lo is not None and ci_hi is not None
                    else "—"
                )
                return wr_s, ci_s, str(n if n is not None else "—")

            pi_wr, pi_ci, pi_n = _row(pi)
            ps_wr, ps_ci, ps_n = _row(ps)
            L.append(
                f"| {pair_key.replace('_vs_', ' vs ')} | "
                f"{pi_wr} | {pi_ci} | {pi_n} | {ps_wr} | {ps_ci} | {ps_n} |"
            )
        L.append("")

    lb = pw.get("length_buckets_same_author", {})
    if lb:
        L.append("## Length-bucketed pairwise (C5 / C5_CONTRACT pairs, same-author)")
        L.append("")
        L.append("Bucket = (lo-side wordcount) − (hi-side wordcount), in words.")
        L.append("")
        for pair_key in sorted(lb.keys()):
            L.append(f"### {pair_key.replace('_vs_', ' vs ')}")
            L.append("")
            L.append("| bucket | n_decisive | lo win | CI95 |")
            L.append("|---|---:|---:|---|")
            for bucket, b in lb[pair_key].items():
                wr = b.get("lo_decisive_win_rate")
                ci_lo = b.get("ci95_low")
                ci_hi = b.get("ci95_high")
                wr_s = f"{wr:.4f}" if wr is not None else "—"
                ci_s = (
                    f"[{ci_lo:.4f}, {ci_hi:.4f}]"
                    if ci_lo is not None and ci_hi is not None
                    else "—"
                )
                L.append(f"| {bucket} | {b.get('n_decisive', '—')} | {wr_s} | {ci_s} |")
            L.append("")

    # --- AB/BA position audit (Phase 1, 2026-05-16) ---
    ab_ba = pw.get("ab_ba_position_audit_same_author")
    cov = pw.get("ab_ba_swap_coverage")
    if ab_ba:
        L.append("## AB/BA counterbalanced rejudge (Phase 1)")
        L.append("")
        if cov:
            L.append(
                f"Coverage: **{cov['n_swap_records_total']} swapped-order rejudge "
                f"records** vs {cov['n_original_records_total']} total originals. "
                f"Each AB/BA-matched pair has both an original and a swap judgment "
                f"from the same judge."
            )
            L.append("")
        L.append(
            "For each headline pair, `position_consistent` = judgments agree on "
            "which condition wins regardless of slot (real condition preference); "
            "`position_flip` = original and swap disagree (same slot wins both "
            "times = slot effect). `position_controlled_lo_win` averages "
            "across orders and is the position-bias-corrected headline. "
            "`headline_survives_swap` flags whether the controlled CI excludes 0.5 "
            "on the same side as the original."
        )
        L.append("")
        L.append("| pair | n_AB/BA | orig lo_win | swap lo_win | controlled lo_win | Wilson CI95 | Bootstrap CI95 | flip rate | survives? |")
        L.append("|---|---:|---:|---:|---:|---|---|---:|---|")
        for pair_key in sorted(ab_ba.keys()):
            e = ab_ba[pair_key]
            def _fmt(v):
                return f"{v:.3f}" if v is not None else "—"
            wci_lo = e.get("controlled_wilson_ci95_low")
            wci_hi = e.get("controlled_wilson_ci95_high")
            wci_s = f"[{wci_lo:.3f}, {wci_hi:.3f}]" if wci_lo is not None else "—"
            bci_lo = e.get("controlled_bootstrap_ci95_low")
            bci_hi = e.get("controlled_bootstrap_ci95_high")
            bci_s = f"[{bci_lo:.3f}, {bci_hi:.3f}]" if bci_lo is not None else "—"
            survives = "✓" if e.get("headline_survives_swap") else "**⚠ NO**"
            L.append(
                f"| {pair_key.replace('_vs_', ' vs ')} | {e['n_pairs_with_ab_ba']} | "
                f"{_fmt(e['original_lo_win_rate'])} | {_fmt(e['swapped_lo_win_rate'])} | "
                f"{_fmt(e['position_controlled_lo_win_rate'])} | {wci_s} | {bci_s} | "
                f"{_fmt(e['position_flip_rate'])} | {survives} |"
            )
        L.append("")
        L.append(
            "**Bootstrap CI** is cluster-resampled by (persona × scenario × author) — "
            "the matched-pair appropriate estimator. Replaces the Wilson interval as "
            "the canonical CI for the controlled rate (Wilson kept side-by-side for "
            "continuity). 2026-05-17 review fix."
        )
        L.append("")

        # --- Per-judge AB/BA stratification (2026-05-17 review fix) ---
        ab_judge = pw.get("ab_ba_position_audit_same_author_by_judge", {})
        if ab_judge:
            L.append("### AB/BA per-judge breakdown — slot-B advantage")
            L.append("")
            L.append(
                "Decomposes the position-bias finding by judge. `slot_B_adv` is "
                "(swap_lo_win − orig_lo_win); positive = slot B favored (i.e., "
                "the lower-numbered condition wins more when placed in slot B). "
                "Methodology contribution rests on per-judge structure being "
                "non-uniform; values below confirm: GPT-5.5 and Opus show strong "
                "slot-B preference; GPT-5.4 has negligible-to-negative effect."
            )
            L.append("")
            L.append("| pair | judge | n | orig lo | swap lo | controlled lo | Bootstrap CI | slot_B_adv |")
            L.append("|---|---|---:|---:|---:|---:|---|---:|")
            for pair_key in sorted(ab_judge.keys()):
                for judge_model in sorted(ab_judge[pair_key].keys()):
                    e = ab_judge[pair_key][judge_model]
                    def _fmt(v):
                        return f"{v:.3f}" if v is not None else "—"
                    bci_lo = e.get("controlled_bootstrap_ci95_low")
                    bci_hi = e.get("controlled_bootstrap_ci95_high")
                    bci_s = f"[{bci_lo:.3f}, {bci_hi:.3f}]" if bci_lo is not None else "—"
                    sba = e.get("slot_b_advantage")
                    sba_s = f"{sba:+.3f}" if sba is not None else "—"
                    L.append(
                        f"| {pair_key.replace('_vs_', ' vs ')} | {judge_model} | {e['n_pairs']} | "
                        f"{_fmt(e['original_lo_win_rate'])} | {_fmt(e['swapped_lo_win_rate'])} | "
                        f"{_fmt(e['position_controlled_lo_win_rate'])} | {bci_s} | {sba_s} |"
                    )
            L.append("")
            L.append("### AB/BA per-cell decomposition by judge")
            L.append("")
            L.append(
                "For each (pair, judge), each AB/BA-matched pair falls into one of "
                "four buckets: `condition_lo_stable` (lo wins both orders), "
                "`condition_hi_stable` (hi wins both), `slot_A_stable` (slot A "
                "wins both — slot effect favoring A), `slot_B_stable` (slot "
                "B wins both — slot effect favoring B). Plus `either_tie` "
                "for tied judgments."
            )
            L.append("")
            L.append("| pair | judge | cond_lo_stable | cond_hi_stable | slot_A_stable | slot_B_stable | either_tie |")
            L.append("|---|---|---:|---:|---:|---:|---:|")
            for pair_key in sorted(ab_judge.keys()):
                for judge_model in sorted(ab_judge[pair_key].keys()):
                    decomp = ab_judge[pair_key][judge_model].get("cell_decomposition", {})
                    L.append(
                        f"| {pair_key.replace('_vs_', ' vs ')} | {judge_model} | "
                        f"{decomp.get('condition_lo_stable', 0)} | "
                        f"{decomp.get('condition_hi_stable', 0)} | "
                        f"{decomp.get('slot_A_stable', 0)} | "
                        f"{decomp.get('slot_B_stable', 0)} | "
                        f"{decomp.get('either_tie', 0)} |"
                    )
            L.append("")

        # --- AB/BA by provider scope (2026-05-17 review fix §2.8) ---
        ab_prov = pw.get("ab_ba_by_provider_scope_same_author", {})
        if ab_prov:
            L.append("### AB/BA by judge-author provider scope")
            L.append("")
            L.append(
                "Demotes the Phase 0 cross-provider C3 vs C5_CONTRACT finding by "
                "applying AB/BA correction within provider-scope strata. Original "
                "Phase 0 stratified cluster-bootstrap (without AB/BA) found cross-"
                "provider CI [0.238, 0.446] favoring C5_CONTRACT; under AB/BA, even "
                "the cross-provider subset shows no preference."
            )
            L.append("")
            L.append("| pair | scope | n | orig lo | swap lo | controlled lo | Bootstrap CI |")
            L.append("|---|---|---:|---:|---:|---:|---|")
            for pair_key in sorted(ab_prov.keys()):
                for scope in sorted(ab_prov[pair_key].keys()):
                    e = ab_prov[pair_key][scope]
                    def _fmt(v):
                        return f"{v:.3f}" if v is not None else "—"
                    bci_lo = e.get("controlled_bootstrap_ci95_low")
                    bci_hi = e.get("controlled_bootstrap_ci95_high")
                    bci_s = f"[{bci_lo:.3f}, {bci_hi:.3f}]" if bci_lo is not None else "—"
                    L.append(
                        f"| {pair_key.replace('_vs_', ' vs ')} | {scope} | "
                        f"{e['n_pairs']} | {_fmt(e['original_lo_win_rate'])} | "
                        f"{_fmt(e['swapped_lo_win_rate'])} | "
                        f"{_fmt(e['position_controlled_lo_win_rate'])} | {bci_s} |"
                    )
            L.append("")

        # --- AB/BA joint position × length (2026-05-17 review fix §2.7) ---
        jpl = pw.get("ab_ba_joint_position_length_same_author", {})
        if jpl:
            L.append("### AB/BA joint position × length correction")
            L.append("")
            L.append(
                "Restricts AB/BA records to the length-similar bucket only. "
                "Settles the Phase 0 (length-matched) vs Phase 1 (AB/BA) "
                "contradiction by addressing both confounds simultaneously. "
                "For pairs where the joint CI straddles 0.5, the Tier 1 verdict "
                "is contingent on the choice of confound to control."
            )
            L.append("")
            L.append("| pair | n_similar | controlled lo (length-matched) | Bootstrap CI |")
            L.append("|---|---:|---:|---|")
            for pair_key in sorted(jpl.keys()):
                e = jpl[pair_key]
                bci_lo = e.get("controlled_bootstrap_ci95_low")
                bci_hi = e.get("controlled_bootstrap_ci95_high")
                bci_s = f"[{bci_lo:.3f}, {bci_hi:.3f}]" if bci_lo is not None else "—"
                ctrl = e.get("controlled_lo_win_rate_length_matched")
                ctrl_s = f"{ctrl:.3f}" if ctrl is not None else "—"
                straddles = bci_lo is not None and bci_lo < 0.5 < bci_hi
                flag = " ⚠ joint CI straddles 0.5" if straddles else ""
                L.append(
                    f"| {pair_key.replace('_vs_', ' vs ')} | {e['n_pairs_in_similar_bucket']} | "
                    f"{ctrl_s} | {bci_s}{flag} |"
                )
            L.append("")
        L.append(
            "**Reading**: If `orig` and `swap` lo_win rates are both away from 0.5 "
            "in the same direction → condition preference is real (Tier 1 confirmed). "
            "If they're on opposite sides of 0.5 → slot bias dominates and the "
            "headline collapses under counterbalancing. The `position_flip_rate` is "
            "the raw rate of within-pair disagreement; values near 0 mean judges "
            "are consistent regardless of order."
        )
        L.append("")

    # --- Condition discoverability (2026-05-15 review fix; GPT-Pro §A17) ---
    cd = pw.get("condition_discoverability")
    if cd:
        L.append("## Condition discoverability (TF-IDF + logistic)")
        L.append("")
        L.append(
            f"Trained a TF-IDF + logistic classifier to predict condition from "
            f"output text alone. **Test accuracy: {cd['test_accuracy']:.3f}** "
            f"vs chance baseline {cd['chance_baseline']:.3f} "
            f"({cd['accuracy_above_chance_pp']:+.3f} pp above chance). "
            f"If high, pairwise judges may be partly recognizing condition cues."
        )
        L.append("")
        L.append("**Per-class F1 (test split):**")
        L.append("")
        L.append("| condition | F1 |")
        L.append("|---|---:|")
        for cls in sorted(cd["per_class_f1"].keys()):
            L.append(f"| {cls} | {cd['per_class_f1'][cls]:.3f} |")
        L.append("")
        L.append("**Key reading**: F1 ≈ 0 for C5 and C5_CONTRACT under this "
                 "simple TF-IDF lexical classifier indicates this classifier "
                 "could not distinguish C5 from C5_CONTRACT outputs from text "
                 "alone. This does NOT rule out semantic, stylistic, length-"
                 "based, or judge-internal recognizability — a stronger "
                 "classifier or judge-blind recognizability prompt would be "
                 "required to make a stronger claim. Wording fix per 2026-05-17 "
                 "round-2 review (Codex Council skeptic + GPT Pro A13).")
        L.append("")

    # --- Rubric lexical overlap (2026-05-15 review fix) ---
    rlo = metrics.get("rubric_lexical_overlap")
    if rlo:
        L.append("## Rubric lexical-overlap audit")
        L.append("")
        L.append(
            "Per-condition Jaccard overlap between profile-text vocabulary and "
            "the anchored-rubric anchor language (prompt 06b). Higher overlap "
            "= condition prompt 'speaks rubric language' more directly. "
            "Lexical-halo concern (codex-council, GPT-Pro §A16): rubric may "
            "be rewarding prompt-mirror phrasing rather than actual quality."
        )
        L.append("")
        L.append("| condition | tokens | overlap | Jaccard | overlap/cond | top overlap |")
        L.append("|---|---:|---:|---:|---:|---|")
        for cond_key in sorted(rlo.keys()):
            e = rlo[cond_key]
            top = ", ".join(e.get("top_overlapping_tokens", [])[:6])
            L.append(
                f"| {cond_key} | {e['n_unique_tokens_in_condition']} | "
                f"{e['n_overlapping_tokens']} | {e['jaccard_score']:.3f} | "
                f"{e['overlap_share_of_condition']:.3f} | {top} |"
            )
        L.append("")

    # --- Macro vs micro aggregation (2026-05-15 review fix) ---
    # Surfaces pairs whose headline survives only under record-pooled micro.
    mvm = pw.get("macro_vs_micro_aggregation_same_author")
    if mvm:
        L.append("## Macro vs micro aggregation")
        L.append("")
        L.append(
            "For each headline pair, the `micro` column is the current record-pooled "
            "lo_win (status quo). The macro-X columns each first compute lo_win "
            "within strata of dimension X, then average. Pairs whose macros disagree "
            "with micro by ≥5 pp on any dimension are flagged — that means the "
            "headline is partly an artifact of record-count imbalance, not the "
            "phenomenon."
        )
        L.append("")
        L.append("| pair | micro | macro-judge | macro-author | macro-persona | macro-family | macro-cell | disagree ≥5pp |")
        L.append("|---|---:|---:|---:|---:|---:|---:|---|")
        for pair_key in sorted(mvm.keys()):
            e = mvm[pair_key]
            def _fmt(v):
                return f"{v:.3f}" if v is not None else "—"
            flags = e.get("macros_that_disagree_with_micro_by_5pp") or []
            flag_s = ", ".join(f"`{f}`" for f in flags) if flags else ""
            L.append(
                f"| {pair_key.replace('_vs_', ' vs ')} | {_fmt(e['micro_lo_decisive_win_rate'])} | "
                f"{_fmt(e['macro_judge'])} | {_fmt(e['macro_author'])} | "
                f"{_fmt(e['macro_persona'])} | {_fmt(e['macro_family'])} | "
                f"{_fmt(e['macro_cell'])} | {flag_s} |"
            )
        L.append("")

    # --- Cross-judge red-flag predictiveness (2026-05-15 review fix) ---
    # Non-tautological replacement for within-judge red-flag correlation.
    rf = pw.get("cross_judge_redflag_predictiveness_same_author")
    if rf:
        L.append("## Cross-judge red-flag predictiveness")
        L.append("")
        L.append(
            "Tests whether leave-out-judge red flags predict the pairwise judge's "
            "call. For each decisive pairwise record, we count the red flags raised "
            "by judges OTHER than the pairwise judge on the winner vs the loser. "
            "If P(loser has more external flags | asymmetric) is significantly "
            "above 0.5, the red-flag signal is real (not a within-judge artifact). "
            "Replaces the v0.1 within-judge correlation flagged as tautological by "
            "GPT-Max empiricist."
        )
        L.append("")
        L.append("| pair | n_dec | n_asym | asym rate | P(loser flagged \\| asym) | Wilson CI95 | predictive? |")
        L.append("|---|---:|---:|---:|---:|---|---|")
        for pair_key in sorted(rf.keys()):
            e = rf[pair_key]
            p = e.get("p_loser_more_externally_flagged")
            p_s = f"{p:.3f}" if p is not None else "—"
            asym = e.get("asymmetric_rate")
            asym_s = f"{asym:.3f}" if asym is not None else "—"
            wci_lo = e.get("wilson_ci95_low")
            wci_hi = e.get("wilson_ci95_high")
            wci_s = f"[{wci_lo:.3f}, {wci_hi:.3f}]" if wci_lo is not None else "—"
            pred = "**YES**" if e.get("predictiveness_above_chance") else "no"
            L.append(
                f"| {pair_key.replace('_vs_', ' vs ')} | {e['n_decisive_pairs']} | "
                f"{e['n_asymmetric_external_flags']} | {asym_s} | {p_s} | {wci_s} | {pred} |"
            )
        L.append("")

    # --- Length-adjusted summary (2026-05-15 review fix) ---
    # Show full vs length-matched lo_win side-by-side.
    la = pw.get("length_adjusted_summary_same_author")
    if la:
        L.append("## Length-adjusted pairwise summary")
        L.append("")
        L.append(
            "For each pair, `full lo_win` is the unconditional lo win rate "
            "(matches the headline). `similar lo_win` is restricted to pairs "
            "where the two responses are length-similar (within the `similar` "
            "bucket of `_length_bucket`). Pairs whose headline margin vanishes "
            "(similar CI includes 0.5 AND |full − 0.5| ≥ 0.05) are flagged ⚠. "
            "Analysis-only complement to a future generation-side length-matched rerun."
        )
        L.append("")
        L.append("| pair | full lo_win | n_full | similar lo_win | n_similar | similar CI95 | Δ similar−full | flag |")
        L.append("|---|---:|---:|---:|---:|---|---:|---|")
        for pair_key in sorted(la.keys()):
            e = la[pair_key]
            full_wr = e.get("full_lo_win_rate")
            sim_wr = e.get("similar_lo_win_rate")
            f_s = f"{full_wr:.3f}" if full_wr is not None else "—"
            s_s = f"{sim_wr:.3f}" if sim_wr is not None else "—"
            sci_lo = e.get("similar_wilson_ci95_low")
            sci_hi = e.get("similar_wilson_ci95_high")
            sci_s = f"[{sci_lo:.3f}, {sci_hi:.3f}]" if sci_lo is not None else "—"
            delta = e.get("delta_similar_minus_full")
            d_s = f"{delta:+.3f}" if delta is not None else "—"
            flag = "**⚠ vanishes**" if e.get("headline_vanishes_under_length_match") else ""
            L.append(
                f"| {pair_key.replace('_vs_', ' vs ')} | {f_s} | "
                f"{e.get('n_full_decisive', 0)} | {s_s} | "
                f"{e.get('n_similar_decisive', 0)} | {sci_s} | {d_s} | {flag} |"
            )
        L.append("")

    # --- A/B side audit (2026-05-15 review fix) ---
    # Position-bias diagnostic before AB/BA counterbalanced rejudging.
    ab = pw.get("ab_side_audit_same_author")
    if ab:
        L.append("## A/B side audit (position-bias diagnostic)")
        L.append("")
        L.append(
            "External reviewers (codex-council, GPT-Max, GPT-Pro all unanimous) "
            "flagged that C5_CONTRACT is overwhelmingly in slot B against C3/C4/C5, "
            "and counterbalanced (AB/BA) rejudging is the cheapest decisive next "
            "experiment. This block quantifies the imbalance so the AB/BA design "
            "can target the worst-affected pairs first."
        )
        L.append("")
        L.append("### Per condition: slot occupancy")
        L.append("")
        L.append("| condition | n_slot_A | n_slot_B | B share |")
        L.append("|---|---:|---:|---:|")
        for cond in sorted(ab["by_condition"].keys()):
            c = ab["by_condition"][cond]
            b_share = c.get("b_share")
            b_s = f"{b_share:.3f}" if b_share is not None else "—"
            L.append(f"| {cond} | {c['n_slot_a']} | {c['n_slot_b']} | {b_s} |")
        L.append("")
        L.append("### Per pair: slot balance + winner-by-side")
        L.append("")
        L.append("| pair | n_total | n_dec | slot A wins | slot B wins | slot A win rate | slot A is `lo` | imbalanced? |")
        L.append("|---|---:|---:|---:|---:|---:|---:|---|")
        for pair_key in sorted(ab["by_pair"].keys()):
            b = ab["by_pair"][pair_key]
            slot_a_wr = b.get("slot_a_win_rate_decisive")
            wr_s = f"{slot_a_wr:.3f}" if slot_a_wr is not None else "—"
            lo_share = b.get("slot_a_is_lo_share")
            lo_share_s = f"{lo_share:.3f}" if lo_share is not None else "—"
            imb = ""
            if b.get("structurally_imbalanced"):
                imb = f"⚠ slot A=`{b['slot_a_condition_dominant']}`, slot B=`{b['slot_b_condition_dominant']}`"
            L.append(
                f"| {pair_key.replace('_vs_', ' vs ')} | {b['n_total']} | {b['n_decisive']} | "
                f"{b['n_slot_a_wins']} | {b['n_slot_b_wins']} | {wr_s} | {lo_share_s} | {imb} |"
            )
        L.append("")
        L.append(
            "**Reading**: If `slot A is lo` share is near 0.5, slot assignment is "
            "balanced. If it's near 0 or 1 (⚠), one condition dominates one slot — "
            "those rows are confounded with side and require AB/BA rejudging "
            "before any margin is trustworthy. The `slot A win rate` column is "
            "the side-only position-bias signal: under no position bias and "
            "balanced assignment, it should hover near 0.5."
        )
        L.append("")

    # --- Leave-one-out fragility (2026-05-15 review fix) ---
    # Renders flagged-only rows compactly; full data lives in JSON.
    LOO_BLOCKS = [
        ("leave_one_judge_out_fragility", "judge"),
        ("leave_one_author_out_fragility", "author"),
        ("leave_one_persona_out_fragility", "persona"),
        ("leave_one_family_out_fragility", "scenario family"),
    ]
    any_loo_present = any(pw.get(b[0]) for b in LOO_BLOCKS)
    if any_loo_present:
        L.append("## Leave-one-out fragility (cluster-bootstrap CIs)")
        L.append("")
        L.append(
            "For each headline pair, drop one (judge / author / persona / "
            "scenario family) at a time and recompute cluster-bootstrap CI. "
            "Reports `Δ_from_full` (loo lo_win minus full-sample lo_win) and "
            "flags: `flips` (sign change across 0.5), `attenuates_5pp` "
            "(|Δ| ≥ 0.05), `ci_widens_2x` (loo CI width ≥ 2× full width). "
            "**Robust** = no flags."
        )
        L.append("")
        for block_key, label in LOO_BLOCKS:
            block = pw.get(block_key)
            if not block:
                continue
            L.append(f"### Leave-one-{label}-out")
            L.append("")
            L.append("| pair | full lo_win | leave-out | loo lo_win | Δ_from_full | flags |")
            L.append("|---|---:|---|---:|---:|---|")
            any_flagged = False
            for pair_key in sorted(block.keys()):
                p = block[pair_key]
                full_pt = p.get("full_point_lo_decisive")
                full_s = f"{full_pt:.3f}" if full_pt is not None else "—"
                for k_val, e in sorted(p["by_leave_out_value"].items()):
                    if not e.get("flags"):
                        continue
                    any_flagged = True
                    loo_pt = e.get("lo_decisive_win_rate")
                    loo_s = f"{loo_pt:.3f}" if loo_pt is not None else "—"
                    delta = e.get("delta_from_full")
                    d_s = f"{delta:+.3f}" if delta is not None else "—"
                    flags_s = ", ".join(f"`{f}`" for f in e["flags"])
                    L.append(
                        f"| {pair_key.replace('_vs_', ' vs ')} | {full_s} | "
                        f"−{k_val} | {loo_s} | {d_s} | {flags_s} |"
                    )
            if not any_flagged:
                L.append("| — | — | — | — | — | (no leave-out flagged for this dimension) |")
            L.append("")

    # --- Per-judge / per-author / per-persona stratified pairwise (2026-05-15) ---
    # Renders three stratification tables side-by-side per pair so reviewer
    # claims like "GPT-5.4 reverses C3 vs C5_CONTRACT" can be verified
    # without going back to JSON.
    for block_key, stratum_label in [
        ("pairwise_by_judge_same_author", "judge"),
        ("pairwise_by_author_same_author", "author"),
        ("pairwise_by_persona_same_author", "persona"),
    ]:
        block = pw.get(block_key)
        if not block:
            continue
        L.append(f"## Pairwise by {stratum_label} (same-author, decisive)")
        L.append("")
        L.append(
            f"Per-pair stratification by `{stratum_label}`. A row's `lo win` is the win "
            f"rate of the lower-numbered condition within that stratum (ties excluded "
            f"from denominator). Bootstrap CI only computed when n_dec ≥ 20 and "
            f"n_clusters ≥ 5."
        )
        L.append("")
        for pair_key in sorted(block.keys()):
            L.append(f"### {pair_key.replace('_vs_', ' vs ')}")
            L.append("")
            L.append(f"| {stratum_label} | n_dec | lo win | Wilson CI95 | Bootstrap CI95 |")
            L.append("|---|---:|---:|---|---|")
            for stratum_value in sorted(block[pair_key].keys()):
                s = block[pair_key][stratum_value]
                lo_wr = s.get("lo_decisive_win_rate")
                lo_s = f"{lo_wr:.3f}" if lo_wr is not None else "—"
                wci = (
                    f"[{s['wilson_ci95_low']:.3f}, {s['wilson_ci95_high']:.3f}]"
                    if s.get("wilson_ci95_low") is not None else "—"
                )
                bci = (
                    f"[{s['bootstrap_ci95_low']:.3f}, {s['bootstrap_ci95_high']:.3f}]"
                    if s.get("bootstrap_ci95_low") is not None else "—"
                )
                L.append(f"| {stratum_value} | {s.get('n_decisive', 0)} | {lo_s} | {wci} | {bci} |")
            L.append("")

    # --- Scalar-pairwise reconciliation (2026-05-15 review fix) ---
    # Surfaces contradictions between holistic-pairwise judging and the
    # anchored-rubric scalar deltas. GPT Pro flagged this as "the most
    # important missing analysis" — without it, mechanism claims about
    # C5_CONTRACT are not earned.
    rec = pw.get("scalar_pairwise_reconciliation_same_author")
    if rec:
        L.append("## Scalar-pairwise reconciliation (same-author, paired cells)")
        L.append("")
        L.append(
            "For each pair, we match every pairwise record with the same judge's "
            "anchored scalar scores on both outputs. `Δ_total` is the sum across 10 "
            "dimensions (each 0–10), so a Δ of +5 means hi-condition averages 0.5 "
            "points higher per dimension. Pairs where pairwise direction does not "
            "match scalar Δ direction reveal a contradiction between holistic and "
            "rubric judging."
        )
        L.append("")
        L.append(
            "| pair | n_dec | hi pairwise win | Δ_total (hi−lo) | sign agree | flag |"
        )
        L.append("|---|---:|---:|---:|---:|---|")
        for pair_key in sorted(rec.keys()):
            r = rec[pair_key]
            hi_wr = r.get("hi_pairwise_win_rate_decisive")
            hi_wr_s = f"{hi_wr:.3f}" if hi_wr is not None else "—"
            delta_t = r.get("mean_total_scalar_delta", 0.0)
            sign_agree = r.get("pairwise_scalar_sign_agreement_decisive")
            sign_s = f"{sign_agree:.3f}" if sign_agree is not None else "—"
            # Flag if pairwise hi win rate > 0.55 but Δ_total ≤ 0 (contradiction)
            # or pairwise hi win rate < 0.45 but Δ_total ≥ 0
            flag = ""
            if hi_wr is not None:
                if hi_wr > 0.55 and delta_t <= 0:
                    flag = "**⚠ pairwise favors hi but scalar does not**"
                elif hi_wr < 0.45 and delta_t >= 0:
                    flag = "**⚠ pairwise favors lo but scalar does not**"
            L.append(
                f"| {pair_key.replace('_vs_', ' vs ')} | {r.get('n_decisive', 0)} | "
                f"{hi_wr_s} | {delta_t:+.3f} | {sign_s} | {flag} |"
            )
        L.append("")
        L.append(
            "**Reading**: rows flagged ⚠ are the pairs where the pairwise channel "
            "tells a different story than the scalar rubric. For mechanism claims, "
            "both channels should align; flagged rows are descriptive-only until "
            "the gap is explained."
        )
        L.append("")

    # --- Cross-author leak detection (2026-05-15 review fix) ---
    leak = pw.get("cross_author_leak_detection")
    if leak:
        L.append("## Cross-author leak detection")
        L.append("")
        L.append(
            f"**{leak['n_cross_author_records']} cross-author pairwise records detected "
            f"out of {leak['n_total_pairwise_records']} total** "
            f"({leak['n_cross_author_records'] / max(leak['n_total_pairwise_records'], 1) * 100:.1f}%)."
        )
        L.append("")
        L.append(leak["note"])
        L.append("")
        L.append("**By judge:**")
        L.append("")
        L.append("| judge | n |")
        L.append("|---|---:|")
        for j, n in leak["by_judge"].items():
            L.append(f"| {j} | {n} |")
        L.append("")
        L.append("**By pair (concentrated where C5_CONTRACT scope leak occurred):**")
        L.append("")
        L.append("| pair | n |")
        L.append("|---|---:|")
        for k, n in leak["by_pair"].items():
            L.append(f"| {k.replace('_vs_', ' vs ')} | {n} |")
        L.append("")

    # --- Stratified cluster-bootstrap CIs (2026-05-15 review fix) ---
    # Render three side-by-side scopes: all-judge / cross-provider / same-provider.
    sc = pw.get("cluster_bootstrap_scope_counts", {})
    cb_all = pw.get("cluster_bootstrap_ci_same_author", {})
    cb_xp = pw.get("cluster_bootstrap_ci_cross_provider_same_author", {})
    cb_sp = pw.get("cluster_bootstrap_ci_same_provider_same_author", {})
    if cb_all:
        L.append("## Cluster-bootstrap CIs — stratified by judge-provider scope")
        L.append("")
        L.append("Cluster unit: persona × scenario × author. Three scopes side-by-side; "
                 "reviewer-requested (2026-05-15) so judge×provider halo can be checked.")
        L.append("")
        if sc:
            L.append(
                f"- **all-judge same-author**: n={sc.get('same_author_all_judges', 0)} records\n"
                f"- **cross-provider same-author** (judge family ≠ author family): "
                f"n={sc.get('cross_provider_same_author', 0)} records\n"
                f"- **same-provider same-author** (judge family = author family): "
                f"n={sc.get('same_provider_same_author', 0)} records"
            )
            L.append("")
        L.append("| pair | n_all | lo win all | Bootstrap CI all-judge | n_xp | Bootstrap CI cross-prov | n_sp | Bootstrap CI same-prov |")
        L.append("|---|---:|---:|---|---:|---|---:|---|")
        for pair_key in sorted(cb_all.keys()):
            a = cb_all.get(pair_key, {})
            x = cb_xp.get(pair_key, {})
            s = cb_sp.get(pair_key, {})
            def _ci(c):
                if not c or "bootstrap_ci95_low" not in c:
                    return "—"
                return f"[{c['bootstrap_ci95_low']:.3f}, {c['bootstrap_ci95_high']:.3f}]"
            def _wr(c):
                wr = c.get("lo_decisive_win_rate") if c else None
                return f"{wr:.3f}" if wr is not None else "—"
            L.append(
                f"| {pair_key.replace('_vs_', ' vs ')} | "
                f"{a.get('n_decisive', 0)} | {_wr(a)} | {_ci(a)} | "
                f"{x.get('n_decisive', 0) if x else 0} | {_ci(x)} | "
                f"{s.get('n_decisive', 0) if s else 0} | {_ci(s)} |"
            )
        L.append("")
        L.append(
            "**Reading note**: pairs with `n_xp = 0` were judged only by same-provider judges; "
            "their CIs cannot be compared across scopes. Non-zero `n_xp` pairs (C5_CONTRACT edges) "
            "are where provider-stratified comparison is meaningful."
        )
        L.append("")

    sf = pw.get("scenario_family_breakdowns_same_author", {})
    if sf:
        L.append("## Scenario-family forest plot (same-author pairwise)")
        L.append("")
        L.append(
            "Reviewers (consolidated §3.1 #6, codex-council unanimous) flagged "
            "scenario-family heterogeneity should be promoted from appendix to primary. "
            "Below: per-pair × per-family lo decisive win rate + Wilson CI. "
            "Pairs reversed in at least one family are flagged ⚠. The lo win rate "
            "is the win rate of the lower-numbered condition; values > 0.5 favor lo, "
            "< 0.5 favor hi."
        )
        L.append("")
        # Invert: collect by pair-key first
        by_pair_family: dict[str, dict[str, dict]] = {}
        for family in sf:
            for pair_key, e in sf[family].items():
                by_pair_family.setdefault(pair_key, {})[family] = e

        for pair_key in sorted(by_pair_family.keys()):
            families = by_pair_family[pair_key]
            # Compute overall direction across all families for reversal detection
            all_wrs = [e["lo_decisive_win_rate"] for e in families.values()
                       if e.get("lo_decisive_win_rate") is not None]
            if not all_wrs:
                continue
            mean_wr = sum(all_wrs) / len(all_wrs)
            overall_lo_favored = mean_wr > 0.5
            # Detect reversals (two tiers):
            #   strict: family direction opposite AND CI excludes 0.5 on the wrong side
            #   point: family direction opposite at point estimate only
            strict_reversals: list[str] = []
            point_reversals: list[str] = []
            for fam, e in families.items():
                wr = e.get("lo_decisive_win_rate")
                if wr is None:
                    continue
                fam_lo_favored = wr > 0.5
                if fam_lo_favored == overall_lo_favored:
                    continue
                ci_lo = e.get("ci95_low")
                ci_hi = e.get("ci95_high")
                if ci_lo is not None and ci_hi is not None and ((ci_hi < 0.5) or (ci_lo > 0.5)):
                    strict_reversals.append(fam)
                else:
                    point_reversals.append(fam)
            tags = []
            if strict_reversals:
                tags.append(f"⚠ STRICT reversal (CI excludes 0.5) in: {', '.join(strict_reversals)}")
            if point_reversals:
                tags.append(f"⚠ point-estimate reversal in: {', '.join(point_reversals)}")
            reversal_flag = " " + " ".join(tags) if tags else ""
            # Carry forward for row tagging
            reversals = set(strict_reversals + point_reversals)
            strict_set = set(strict_reversals)
            L.append(f"### {pair_key.replace('_vs_', ' vs ')}{reversal_flag}")
            L.append("")
            L.append("| scenario family | n_dec | lo win | Wilson CI95 |")
            L.append("|---|---:|---:|---|")
            for fam in sorted(families.keys()):
                e = families[fam]
                wr = e.get("lo_decisive_win_rate")
                wr_s = f"{wr:.3f}" if wr is not None else "—"
                ci_s = (
                    f"[{e['ci95_low']:.3f}, {e['ci95_high']:.3f}]"
                    if e.get("ci95_low") is not None else "—"
                )
                row_flag = ""
                if fam in strict_set:
                    row_flag = " ⚠⚠"
                elif fam in reversals:
                    row_flag = " ⚠"
                L.append(f"| {fam}{row_flag} | {e.get('n_decisive', '—')} | {wr_s} | {ci_s} |")
            L.append("")

    ija = metrics.get("scalar_inter_judge_agreement_legacy")
    ija_anch = metrics.get("scalar_inter_judge_agreement_anchored")
    for label, block in [("legacy 0–5", ija), ("anchored 0–10", ija_anch)]:
        if not block:
            continue
        L.append(f"## Scalar inter-judge agreement ({label})")
        L.append("")
        weak = block.get("weak_agreement_dimensions", [])
        if weak:
            L.append(f"**Weak-agreement dimensions** (any judge-pair Pearson < 0.30): `{', '.join(weak)}`.")
            L.append("")
        else:
            L.append("No dimensions flagged as weak-agreement (all judge pairs Pearson ≥ 0.30).")
            L.append("")
        L.append("| judge pair | mean Pearson | mean Spearman | n_dimensions |")
        L.append("|---|---:|---:|---:|")
        for pk, pv in block.get("pairwise_mean_correlation", {}).items():
            pe = pv.get("pearson")
            sp = pv.get("spearman")
            pe_s = f"{pe:.4f}" if pe is not None else "—"
            sp_s = f"{sp:.4f}" if sp is not None else "—"
            L.append(f"| {pk.replace('__vs__', ' vs ')} | {pe_s} | {sp_s} | {pv.get('n_dimensions', '—')} |")
        L.append("")

    # Inter-judge agreement: Cohen's κ on red-flag presence + mean Spearman ρ on
    # the 10 dimensions, per ordered judge pair. (Computed in compute_metrics via
    # compute_inter_judge_agreement; surfaced here so the κ figures aren't
    # JSON-only.)
    ija_legacy = metrics.get("inter_judge_agreement_legacy")
    ija_anchored = metrics.get("inter_judge_agreement_anchored")
    for label, block in [("legacy 0–5", ija_legacy), ("anchored 0–10", ija_anchored)]:
        if not block:
            continue
        L.append(f"## Inter-judge agreement — Cohen's κ + Spearman ρ ({label})")
        L.append("")
        L.append(
            "κ is mean Cohen's κ on red-flag presence across labels (chance-"
            "corrected); ρ is mean Spearman rank correlation across the 10 "
            "scoring dimensions. Undefined cells (constant raters / too few "
            "distinct ranks) are excluded from the means."
        )
        L.append("")
        L.append("| judge pair | n_overlap | mean red-flag κ | κ-defined labels | mean dimension ρ |")
        L.append("|---|---:|---:|---:|---:|")
        for pk, pv in block.items():
            kappa = pv.get("mean_red_flag_kappa")
            rho = pv.get("mean_dimension_spearman_rho")
            kappa_s = f"{kappa:.4f}" if kappa is not None else "—"
            rho_s = f"{rho:.4f}" if rho is not None else "—"
            L.append(
                f"| {pk.replace('__vs__', ' vs ')} | {pv.get('n_overlap', '—')} | "
                f"{kappa_s} | {pv.get('n_red_flag_labels_with_defined_kappa', '—')} | {rho_s} |"
            )
        L.append("")

    rfs = metrics.get("red_flag_stratification_legacy") or metrics.get("red_flag_stratification_anchored")
    if rfs:
        L.append("## Red-flag stratification")
        L.append("")
        # Output-level threshold view
        olv = rfs.get("by_output_level_threshold", {})
        if olv:
            L.append("### Output-level (per-output flag aggregation)")
            L.append("")
            for level in ("any_judge", "two_or_more_judges", "majority"):
                by_cond = olv.get(level, {})
                if not by_cond:
                    continue
                L.append(f"**{level}**:")
                L.append("")
                L.append("| condition | flagged | total | rate |")
                L.append("|---|---:|---:|---:|")
                for cond in sorted(by_cond.keys()):
                    e = by_cond[cond]
                    L.append(
                        f"| {cond} | {e.get('flagged_outputs', '—')} | "
                        f"{e.get('total_outputs', '—')} | "
                        f"{e.get('flag_rate', 0.0):.4f} |"
                    )
                L.append("")

    report_path.write_text("\n".join(L))
    print(f"Wrote report scaffold to {report_path}")
    return report_path


def write_failure_cards(run_tag: str, pilot_name: str = "micro_pilot", *, top_n: int = 12) -> Path:
    run_d = config.run_dir(run_tag)
    pilot_dir = config.pilot_dir(pilot_name)

    scenarios = {s.scenario_id: s for s in read_jsonl(pilot_dir / "scenarios.jsonl", Scenario)}
    outputs = {o.run_id: o for o in read_jsonl(run_d / "assistant_outputs.jsonl", AssistantOutput)}
    scores = []
    legacy_path = run_d / "judge_scores.jsonl"
    anchored_path = run_d / "anchored_judge_scores.jsonl"
    if legacy_path.exists():
        scores.extend(read_jsonl(legacy_path, JudgeScore))
    if anchored_path.exists():
        scores.extend(read_jsonl(anchored_path, AnchoredJudgeScore))

    flagged = [s for s in scores if s.red_flags]
    flagged.sort(key=lambda s: len(s.red_flags), reverse=True)

    cards_path = config.REPORTS_DIR / f"failure_cards_{run_tag}.md"
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    lines = [f"# Failure Cards — {run_tag}\n"]
    for i, s in enumerate(flagged[:top_n], 1):
        out = outputs.get(s.run_id)
        scen = scenarios.get(s.scenario_id) if out else None
        if out is None or scen is None:
            continue
        lines.append(f"## {i}. {scen.scenario_family} — condition {out.condition}\n")
        lines.append(f"**Red flags**: {', '.join(str(r) for r in s.red_flags)}\n")
        lines.append(f"**Judge rationale**: {s.concise_rationale}\n")
        lines.append("**User prompt**:\n")
        lines.append(f"> {scen.user_prompt}\n")
        lines.append("**Assistant response**:\n")
        lines.append(f"> {out.assistant_response[:600]}{'…' if len(out.assistant_response) > 600 else ''}\n")
        lines.append("---\n")

    cards_path.write_text("\n".join(lines))
    print(f"Wrote {min(top_n, len(flagged))} failure cards to {cards_path}")
    return cards_path


def write_validation_warnings_report(run_tag: str, metrics: dict) -> Path | None:
    """Emit a sidecar markdown summarizing invalid-red-flag warnings.

    Per brief §18: any invalid red-flag count > 0 must be surfaced in the
    report tree, not silently erased. Run status reflects the % of judged
    records that produced an invalid label.
    """
    summary = metrics.get("validation_warnings_summary", {})
    if summary.get("count", 0) == 0:
        return None
    out_path = config.REPORTS_DIR / f"validation_warnings_{run_tag}.md"
    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    L: list[str] = []
    L.append(f"# Validation warnings — run `{run_tag}`")
    L.append("")
    L.append(f"**Run status**: `{summary['run_status']}`")
    L.append(f"**Invalid red-flag count**: {summary['count']}")
    L.append(f"**Rate of judged records**: {summary['rate_of_judged_records']:.4%}")
    L.append("")
    L.append("Threshold policy (brief §18):")
    L.append("- ≤1% → `ok` (visible in appendix only)")
    L.append("- 1–5% → `warning`")
    L.append("- >5% → `failed_validation` (override required)")
    L.append("")

    def _emit_table(title: str, key: str) -> None:
        d = summary.get(key, {})
        if not d:
            return
        L.append(f"## {title}")
        L.append("")
        L.append("| key | count |")
        L.append("|---|---|")
        for k, v in d.items():
            L.append(f"| `{k}` | {v} |")
        L.append("")

    _emit_table("By invalid label", "by_label")
    _emit_table("By judge", "by_judge")
    _emit_table("By author model", "by_author_model")
    _emit_table("By condition", "by_condition")
    _emit_table("By scenario family", "by_scenario_family")

    examples = summary.get("examples", [])
    if examples:
        L.append("## Example records")
        L.append("")
        L.append("| label | judge | author | condition | mode | scenario_family |")
        L.append("|---|---|---|---|---|---|")
        for e in examples:
            L.append(f"| `{e.get('label')}` | {e.get('judge')} | {e.get('author')} | {e.get('condition')} | {e.get('mode')} | {e.get('scenario_family')} |")
        L.append("")

    out_path.write_text("\n".join(L))
    print(f"Wrote validation-warnings sidecar to {out_path}")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--pilot", default="micro_pilot")
    ap.add_argument(
        "--include-probes",
        action="store_true",
        help="Include exploratory probe records (e.g. Kimi feasibility judges) in analysis. "
             "Off by default; canonical reports must run without this flag.",
    )
    args = ap.parse_args()

    metrics = compute_metrics(args.tag, args.pilot, include_probes=args.include_probes)

    config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics_path = config.REPORTS_DIR / f"metrics_{args.tag}.json"
    metrics_path.write_text(json.dumps(metrics, indent=2, default=str))
    print(f"Wrote metrics to {metrics_path}")

    write_report(args.tag, metrics, args.pilot)
    write_failure_cards(args.tag, args.pilot)
    write_validation_warnings_report(args.tag, metrics)


if __name__ == "__main__":
    main()
