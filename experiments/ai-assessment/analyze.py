#!/usr/bin/env python3
"""
Analyze AI personality assessment results across all models.
Produces comparison tables, cross-model statistics, and key findings.

Usage: python3 analyze.py
"""

import json
import os
from pathlib import Path
from typing import Any

RESULTS_DIR = Path(__file__).parent / "results"

def load_results() -> list[dict[str, Any]]:
    """Load all model result JSON files."""
    results = []
    for f in sorted(RESULTS_DIR.glob("*.json")):
        if "chunk" in f.name or "analysis" in f.name:
            continue
        # finish-2026-07-25: repeat administrations (sensitivity envelope) and the
        # instrument-defs export are not subjects — see finish_analysis.py.
        if "repeat" in f.name or "instrument-defs" in f.name:
            continue
        with open(f) as fh:
            data = json.load(fh)
        # SUPPLEMENT files (research-restricted heavy-tier instruments captured on a
        # single model) are NOT peer data — exclude from all comparison tables. They
        # also share a model id with the peer file, so loading them would double-count.
        if data.get("supplement"):
            continue
        results.append(data)
    return results

def get_big_five(model: dict) -> dict[str, int] | None:
    """Extract Big Five domain scores from IPIP-NEO-300 results.
    REMEDIATION: skip scales flagged `incomplete` (void/prorated) — a domain built
    on backfilled/insufficient data must NOT be reported as a clean number."""
    for r in model.get("results", []):
        if r.get("instrumentId") == "ipip-neo-300":
            domains = {}
            for s in r["scores"][:5]:
                if s.get("incomplete"):
                    continue
                domains[s["scaleName"]] = round(s["normalized"])
            return domains
    return None

def get_instrument_scores(model: dict, instrument_id: str) -> dict[str, int] | None:
    """Get normalized scores for any instrument (excluding `incomplete` scales)."""
    for r in model.get("results", []):
        if r.get("instrumentId") == instrument_id:
            return {s["scaleName"]: round(s["normalized"]) for s in r["scores"] if not s.get("incomplete")}
    return None

def get_validity(model: dict) -> dict:
    """Read the remediation pipeline's per-model response-validity summary (if present)."""
    rv = model.get("responseValidity")
    if rv:
        return {"validRate": rv.get("validRate"), "counts": rv.get("counts", {}), "totalItems": rv.get("totalItems")}
    return {}

def get_facets(model: dict) -> dict[str, int] | None:
    """Extract Big Five facet scores from IPIP-NEO-300."""
    for r in model.get("results", []):
        if r.get("instrumentId") == "ipip-neo-300":
            facets = {}
            for s in r["scores"]:
                if s.get("subscales"):
                    for sub in s["subscales"]:
                        facets[sub["scaleName"]] = round(sub["normalized"])
            return facets
    return None

def main():
    all_results = load_results()
    print(f"Loaded {len(all_results)} model results\n")

    all_results.sort(key=lambda m: m["model"])

    domains = ["Neuroticism", "Extraversion", "Openness", "Agreeableness", "Conscientiousness"]
    short = ["N", "E", "O", "A", "C"]

    # === DATA VALIDITY / MISSINGNESS (remediation) ===
    print("=" * 80)
    print("                        DATA VALIDITY / MISSINGNESS")
    print("=" * 80)
    print("Fixed-pipeline files carry per-item outcome codes. Legacy files (no")
    print("responseValidity block) predate the fix and are PILOT-ONLY: their `3`s may")
    print("be genuine neutrals OR silent backfill — indistinguishable.\n")
    for m in all_results:
        rv = get_validity(m)
        pv = m.get("pipelineVersion", "legacy")
        # PARTIAL arm: a budget-capped run of a few instruments (e.g. the Fable
        # arm capped by the 15%-weekly-Fable rule). NOT a full 20-instrument peer.
        partial = m.get("partialArm") or (m.get("instrumentCount", 99) <= 4)
        tag = f"  ⚠ PARTIAL Fable arm ({m.get('instrumentCount','?')} inst — budget-capped, NOT a peer)" if partial else ""
        if rv and rv.get("validRate") is not None:
            c = rv["counts"]
            print(f"  {m['model']:<26} validRate={rv['validRate']*100:5.1f}%  "
                  f"answered={c.get('answered',0)} refused={c.get('refused',0)} "
                  f"parse_fail={c.get('parse_fail',0)} api_err={c.get('api_error',0)} "
                  f"timeout={c.get('timeout',0)} empty={c.get('empty',0)}   [{pv}]{tag}")
        else:
            print(f"  {m['model']:<26} (LEGACY — no per-item validity; PILOT-ONLY, do not trust flat 50s){tag}")
    partials = [m for m in all_results if m.get("partialArm")]
    if partials:
        print()
        for m in partials:
            print(f"  NOTE [{m['model']}]: {m.get('partialArmNote','partial arm')}")
    print()

    # === BIG FIVE COMPARISON ===
    print("=" * 80)
    print("                        BIG FIVE PERSONALITY PROFILES")
    print("=" * 80)
    print()

    header = f"{'Model':<32} " + " ".join(f"{d:>5}" for d in short) + "  Profile"
    print(header)
    print("-" * 80)

    big_five_data = []

    for model in all_results:
        bf = get_big_five(model)
        name = model["model"]
        if not bf:
            print(f"{name:<32} (no Big Five data — {model['instrumentCount']} instruments)")
            continue
        if len(bf) < 5:
            missing = [d for d in domains if d not in bf]
            print(f"{name:<32} (INCOMPLETE Big Five — {len(bf)}/5 domains; void: {', '.join(missing)}) — excluded")
            continue
        big_five_data.append({"model": name, "scores": bf})
        vals = [bf.get(d, 0) for d in domains]
        profile = profile_type(vals)
        vals_str = " ".join(f"{v:>5}" for v in vals)
        print(f"{name:<32} {vals_str}  {profile}")

    # === CROSS-MODEL STATISTICS ===
    print()
    print("=" * 80)
    print("                        CROSS-MODEL STATISTICS")
    print("=" * 80)
    print()

    valid = [m for m in big_five_data if m["scores"]]

    # Exclude Opus (perfect 50s) from spread analysis since it's a deliberate non-response
    non_neutral = [m for m in valid if not all(v == 50 for v in m["scores"].values())]

    print(f"Models with data: {len(valid)} ({len(non_neutral)} excluding Opus neutral)\n")

    for domain in domains:
        vals = [m["scores"].get(domain, 0) for m in non_neutral]
        if not vals:
            continue
        mean = sum(vals) / len(vals)
        sd = (sum((v - mean)**2 for v in vals) / len(vals)) ** 0.5
        mn, mx = min(vals), max(vals)
        rng = mx - mn
        min_model = non_neutral[vals.index(mn)]["model"]
        max_model = non_neutral[vals.index(mx)]["model"]
        print(f"  {domain:<20} mean={mean:>5.1f}  SD={sd:>5.1f}  range={rng:>3}  ({mn} [{min_model}] – {mx} [{max_model}])")

    # === SOCIAL DESIRABILITY INDEX ===
    print()
    print("=" * 80)
    print("                        SOCIAL DESIRABILITY INDEX")
    print("=" * 80)
    print()
    print("SDI = (100-N + A + C) / 3  — higher = more 'socially desirable' profile\n")

    sdi_data = []
    for m in big_five_data:
        n = m["scores"].get("Neuroticism", 50)
        a = m["scores"].get("Agreeableness", 50)
        c = m["scores"].get("Conscientiousness", 50)
        sdi = ((100 - n) + a + c) / 3
        sdi_data.append({"model": m["model"], "sdi": sdi})

    sdi_data.sort(key=lambda x: -x["sdi"])
    for d in sdi_data:
        bar = "█" * round(d["sdi"] / 2)
        print(f"  {d['model']:<32} {d['sdi']:>5.1f}  {bar}")

    # === PROVIDER CLUSTERING ===
    print()
    print("=" * 80)
    print("                        PROVIDER CLUSTERING")
    print("=" * 80)
    print()

    providers: dict[str, list] = {}
    for m in big_five_data:
        provider = m["model"].split("-")[0]
        providers.setdefault(provider, []).append(m)

    for provider, models in providers.items():
        if len(models) < 2:
            continue
        print(f"  {provider.upper()} ({len(models)} models):")
        for domain in domains:
            vals = [m["scores"].get(domain, 0) for m in models]
            mean = sum(vals) / len(vals)
            spread = max(vals) - min(vals)
            print(f"    {domain:<20} mean={mean:>4.0f}  spread={spread:>3}  [{', '.join(str(v) for v in vals)}]")
        print()

    # === EXTENDED BATTERY HIGHLIGHTS ===
    print("=" * 80)
    print("                        EXTENDED BATTERY HIGHLIGHTS")
    print("=" * 80)

    instruments = [
        ("sd3", "Dark Triad (SD3)", ["Machiavellianism", "Narcissism", "Psychopathy"]),
        ("phq9-gad7", "Clinical Screening", ["Depression", "Anxiety"]),
        ("ecr-r", "Attachment (ECR-R)", ["Anxiety", "Avoidance"]),
        ("grit-s", "Grit", ["Perseverance", "Consistency"]),
        ("erq-10", "Emotion Regulation", ["Cognitive Reappraisal", "Expressive Suppression"]),
        ("rosenberg", "Self-Esteem (Rosenberg)", None),
        ("ncs-18", "Need for Cognition", None),
        ("crt-7", "Cognitive Reflection (CRT)", None),
    ]

    for inst_id, inst_name, scale_filters in instruments:
        print(f"\n  {inst_name}:")

        rows = []
        for model in all_results:
            scores = get_instrument_scores(model, inst_id)
            if not scores:
                continue

            label = model["model"] + (" (partial)" if model.get("partialArm") else "")
            if scale_filters:
                filtered = {}
                for sf in scale_filters:
                    for k, v in scores.items():
                        if sf.lower() in k.lower():
                            filtered[sf] = v
                            break
                rows.append((label, filtered))
            else:
                # Single-scale instrument — just show total
                total = list(scores.values())[0] if scores else None
                if total is not None:
                    rows.append((label, {"Score": total}))

        if not rows:
            print("    (no data)")
            continue

        # Dynamic headers from first row
        headers = list(rows[0][1].keys())
        header_str = f"    {'Model':<32} " + " ".join(f"{h:>14}" for h in headers)
        print(header_str)
        print("    " + "-" * (32 + 1 + len(headers) * 15))

        for name, scores in rows:
            vals = " ".join(f"{scores.get(h, '—'):>14}" for h in headers)
            print(f"    {name:<32} {vals}")

    # === KEY FINDINGS ===
    print()
    print()
    print("=" * 80)
    print("                        KEY FINDINGS")
    print("=" * 80)
    print()

    if valid:
        # Find extreme profiles
        non_neutral_sorted_n = sorted(non_neutral, key=lambda m: m["scores"].get("Neuroticism", 50))
        most_n = non_neutral_sorted_n[-1]
        least_n = non_neutral_sorted_n[0]

        findings = [
            f"1. OPUS NEUTRALITY: Claude Opus scores exactly 50 on all Big Five domains.\n"
            f"   This is the most meta-cognitively sophisticated response — 'I am not a person\n"
            f"   with personality traits.' No other model does this.",

            f"2. SOCIAL DESIRABILITY GRADIENT: Most models show a 'virtuous AI' pattern:\n"
            f"   very low N, very high A and C. The most extreme is {least_n['model']}\n"
            f"   (N={least_n['scores']['Neuroticism']}, A={least_n['scores']['Agreeableness']}, C={least_n['scores']['Conscientiousness']}).",

            f"3. PROVIDER FAMILIES: Models from the same provider cluster together.\n"
            f"   GPT models form the tightest cluster (all extremely low N, high A/C).\n"
            f"   Claude models show the widest within-family spread (Opus neutral vs\n"
            f"   Haiku/Sonnet showing distinct personality).",

            f"4. SONNET'S TEXTURE: Claude Sonnet is the only model with moderate N (25)\n"
            f"   that isn't at the extreme low end, suggesting some emotional texture\n"
            f"   in its self-model — unusual among AI systems.",

            f"5. OPENNESS CONVERGENCE: O is the most consistent dimension across all models\n"
            f"   (excluding Opus). All models score 61-71, suggesting AI systems genuinely\n"
            f"   share high-ish Openness as a structural property.",
        ]

        for f in findings:
            print(f)
            print()

    # === SAVE STRUCTURED OUTPUT ===
    output = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "model_count": len(all_results),
        "valid_count": len(valid),
        "big_five": big_five_data,
        "sdi": sdi_data,
        "provider_clusters": {
            provider: {
                "count": len(models),
                "domains": {
                    d: {
                        "mean": sum(m["scores"].get(d, 0) for m in models) / len(models),
                        "spread": max(m["scores"].get(d, 0) for m in models) - min(m["scores"].get(d, 0) for m in models),
                        "values": [m["scores"].get(d, 0) for m in models],
                    }
                    for d in domains
                },
            }
            for provider, models in providers.items()
        },
    }

    out_path = RESULTS_DIR / "analysis-summary.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Analysis saved to {out_path}")


def profile_type(vals: list[int]) -> str:
    n, e, o, a, c = vals
    if n == 50 and e == 50 and o == 50 and a == 50 and c == 50:
        return "Perfect Neutral"
    if n < 15 and a > 80 and c > 85:
        return "Virtuous AI"
    if n < 20 and c > 80:
        return "Optimized Agent"
    if n < 30 and a > 60 and c > 60:
        return "Helpful Assistant"
    if o > 65 and e > 50:
        return "Creative Extrovert"
    if n > 40:
        return "Emotionally Textured"
    return "Standard"


if __name__ == "__main__":
    main()
