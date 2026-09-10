"""Merge scores from multiple methods into unified profile."""

from __future__ import annotations

import json
import math
from pathlib import Path

from rich.console import Console

from .profile import (
    PsycheProfile,
    BigFiveProfile,
    ValuesProfile,
    MergedTrait,
    TraitEstimate,
    AnalysisMetadata,
    FacetScore,
    InstrumentManifest,
    InstrumentRecord,
)

console = Console()

# Method reliability weights. Must sum to 1.0.
#
# Derived by normalizing the original design weights (which summed to 0.92
# due to an implicit Empath allocation that was removed without
# redistribution) to preserve their relative proportions after:
#   - dropping llm-gpt: no llm_gpt.py source module exists in this codebase;
#     it was a placeholder that never had estimates flowing into merge.
#   - explicitly excluding empath: Empath measures language register (what a
#     person writes *about*), not personality traits (who they are). Empath
#     data is used only for comparative corpus characterization.
#
# The runtime code at _merge_estimates() renormalizes by total_weight on each
# call, so scores were never numerically broken — they just drifted from the
# documented proportions. This fix aligns documented intent with behavior.
#
# See tests/test_merge.py::TestMethodWeights for the invariant.
METHOD_WEIGHTS = {
    "self-report": 0.43,  # Psychometric instruments (was 0.35; 0.35/0.82)
    "interview":   0.24,  # Semi-structured interview, Peters & Matz (was 0.20; 0.20/0.82)
    "llm-claude":  0.24,  # Assessment-optimized prompting, r~.44 (was 0.20; 0.20/0.82)
    "huggingface": 0.09,  # Fine-tuned models (was 0.07; 0.07/0.82)
    "empath":      0.00,  # Excluded: language register, not personality
}

DOMAIN_NAMES = {
    "N": "Neuroticism",
    "E": "Extraversion",
    "O": "Openness",
    "A": "Agreeableness",
    "C": "Conscientiousness",
}

_FACET_NAMES = {
    "N1": "Anxiety", "N2": "Anger", "N3": "Depression",
    "N4": "Self-Consciousness", "N5": "Immoderation", "N6": "Vulnerability",
    "E1": "Friendliness", "E2": "Gregariousness", "E3": "Assertiveness",
    "E4": "Activity Level", "E5": "Excitement-Seeking", "E6": "Cheerfulness",
    "O1": "Imagination", "O2": "Artistic Interests", "O3": "Emotionality",
    "O4": "Adventurousness", "O5": "Intellect", "O6": "Liberalism",
    "A1": "Trust", "A2": "Morality", "A3": "Altruism",
    "A4": "Cooperation", "A5": "Modesty", "A6": "Sympathy",
    "C1": "Self-Efficacy", "C2": "Orderliness", "C3": "Dutifulness",
    "C4": "Achievement-Striving", "C5": "Self-Discipline", "C6": "Cautiousness",
}

# Instrument reliability constants for weighted averaging
INSTRUMENT_RELIABILITY: dict[str, dict[str, float | int]] = {
    "ipip-neo-60":  {"alpha": 0.75, "items_per_facet": 2},
    "ipip-neo-120": {"alpha": 0.85, "items_per_facet": 4},
    "ipip-neo-300": {"alpha": 0.93, "items_per_facet": 10},
    "hexaco-60":    {"alpha": 0.80},
    "hexaco-200":   {"alpha": 0.90},
    "grit-s":       {"alpha": 0.82},
    "grit-o":       {"alpha": 0.85},
    "bpns-9":       {"alpha": 0.78},
    "bpns-21":      {"alpha": 0.85},
    "loc-ie4":      {"alpha": 0.72},
    "levenson-ipc-24": {"alpha": 0.80},
    "self-monitoring-18": {"alpha": 0.70},
    "snyder-sm-25": {"alpha": 0.73},
    "cat-big5":     {"alpha": 0.95, "scoring_method": "cat"},
    "cat-hexaco":   {"alpha": 0.95, "scoring_method": "cat"},
    # Phase 4: Extended battery
    "swls":          {"alpha": 0.87},
    "aaq-ii":        {"alpha": 0.84},
    "dweck-itis":    {"alpha": 0.90},
    "cei-ii":        {"alpha": 0.86},
    "aot-13":        {"alpha": 0.84},
    "ius-12":        {"alpha": 0.91},
    "scs-26":        {"alpha": 0.92},
    "mfq-2":         {"alpha": 0.82},
    "frost-mps":     {"alpha": 0.90},
    "maas":          {"alpha": 0.87},
    "authenticity":  {"alpha": 0.78},
    "tangney-scs":   {"alpha": 0.89},
    "maximization":  {"alpha": 0.72},
    "ztpi":          {"alpha": 0.80},
}

# HEXACO domain-level scale IDs
_HEXACO_MAP = {
    "hh": "honesty_humility",
    "em": "emotionality",
    "ex": "extraversion",
    "ag": "agreeableness",
    "co": "conscientiousness",
    "op": "openness",
}


def merge_profile(
    analysis_dir: Path,
    self_report_path: Path | None = None,
    tier: str | None = None,
) -> PsycheProfile:
    """Merge all available analysis results into a unified profile.

    Reads from:
    - analysis_dir/llm-claude.json
    - analysis_dir/empath.json
    - self_report_path (exported from web app)

    Args:
        tier: Override tier detection. If None, auto-detects from instruments present.
    """
    profile = PsycheProfile()
    methods_used: list[str] = []

    # Load LLM-Claude results
    llm_path = analysis_dir / "llm-claude.json"
    llm_data = None
    if llm_path.exists():
        llm_data = json.loads(llm_path.read_text())
        methods_used.append("llm-claude")
        profile.metadata.llm_tokens_used += llm_data.get("total_tokens", 0)

    # Load interview results
    interview_path = analysis_dir / "interview.json"
    interview_data = None
    if interview_path.exists():
        interview_data = json.loads(interview_path.read_text())
        methods_used.append("interview")

    # Empath is excluded from profile synthesis — it measures language
    # register (what you write about), not personality traits (who you are).
    # Empath data is used only for comparative corpus characterization.

    # Load self-report results
    self_report = None
    if self_report_path and self_report_path.exists():
        self_report = json.loads(self_report_path.read_text())
        methods_used.append("self-report")

    # Auto-detect tier from instruments present
    detected_tier = tier or _detect_tier(self_report)
    profile.manifest.tier = detected_tier  # type: ignore[assignment]

    # Merge Big Five
    for domain_key in DOMAIN_NAMES:
        estimates: list[TraitEstimate] = []

        # LLM-Claude estimate
        if llm_data and llm_data.get("big_five"):
            domain_data = llm_data["big_five"].get("domains", {}).get(domain_key)
            if domain_data:
                estimates.append(TraitEstimate(
                    score=domain_data["score"],
                    confidence=domain_data.get("confidence", "medium"),
                    method="llm-claude",
                    evidence=domain_data.get("evidence", []),
                ))

        # Interview estimate
        if interview_data and interview_data.get("big_five"):
            domain_data = interview_data["big_five"].get("domains", {}).get(domain_key)
            if domain_data:
                estimates.append(TraitEstimate(
                    score=domain_data["score"],
                    confidence=domain_data.get("confidence", "medium"),
                    method="interview",
                    evidence=domain_data.get("evidence", []),
                ))

        # Self-report estimate — use highest-precision NEO available
        # If multiple present, weight by reliability
        if self_report:
            results = self_report.get("results", {})
            sr_scores: list[tuple[float, float]] = []  # (score, weight)

            for instrument_id, weight in [
                ("ipip-neo-300", 0.93),
                ("ipip-neo-120", 0.85),
                ("ipip-neo-60", 0.75),
            ]:
                inst = results.get(instrument_id)
                if inst:
                    for s in inst.get("scores", []):
                        if s.get("scaleId") == domain_key:
                            sr_scores.append((s["normalized"], weight))
                    _ensure_manifest_record(profile, instrument_id, inst)

            if sr_scores:
                # Weighted average by reliability
                total_w = sum(w for _, w in sr_scores)
                avg_score = sum(s * w for s, w in sr_scores) / total_w
                estimates.append(TraitEstimate(
                    score=avg_score,
                    confidence="high",
                    method="self-report",
                ))

        profile.big_five.domains[domain_key] = _merge_estimates(estimates)

    # Extract facet-level scores from all NEO instruments
    if self_report:
        results = self_report.get("results", {})
        neo60_facets: dict[str, float] = {}
        neo120_facets: dict[str, float] = {}
        neo300_facets: dict[str, float] = {}

        for inst_id, facet_dict in [
            ("ipip-neo-60", neo60_facets),
            ("ipip-neo-120", neo120_facets),
            ("ipip-neo-300", neo300_facets),
        ]:
            inst = results.get(inst_id)
            if inst:
                for s in inst.get("scores", []):
                    sid = s.get("scaleId", "")
                    if sid not in DOMAIN_NAMES:  # skip domain-level scores
                        facet_dict[sid] = s["normalized"]

        # Extract CAT theta estimates (converted to 0-100)
        cat_facets: dict[str, tuple[float, float | None]] = {}  # fid -> (score, se)
        cat_b5 = results.get("cat-big5")
        if cat_b5:
            _ensure_manifest_record(profile, "cat-big5", cat_b5)
            for s in cat_b5.get("scores", []):
                theta = s.get("theta")
                se = s.get("se")
                if theta is not None:
                    cat_facets[s["scaleId"]] = (_theta_to_100(theta), se)

        all_facet_ids = sorted(
            set(neo60_facets) | set(neo120_facets) | set(neo300_facets) | set(cat_facets)
        )
        for fid in all_facet_ids:
            v60 = neo60_facets.get(fid)
            v120 = neo120_facets.get(fid)
            v300 = neo300_facets.get(fid)
            cat_val, cat_se_val = cat_facets.get(fid, (None, None))

            # Weighted average by instrument reliability
            weighted_vals: list[tuple[float, float]] = []
            if cat_val is not None:
                weighted_vals.append((cat_val, 0.95))  # CAT is highest precision
            if v300 is not None:
                weighted_vals.append((v300, 0.93))
            if v120 is not None:
                weighted_vals.append((v120, 0.85))
            if v60 is not None:
                weighted_vals.append((v60, 0.75))

            avg = None
            if weighted_vals:
                total_w = sum(w for _, w in weighted_vals)
                avg = sum(v * w for v, w in weighted_vals) / total_w

            domain = fid[0] if fid and fid[0] in DOMAIN_NAMES else ""
            profile.big_five.facet_scores.append(FacetScore(
                facet_id=fid,
                name=_FACET_NAMES.get(fid, fid),
                domain=domain,
                neo60=v60,
                neo120=v120,
                neo300=v300,
                cat=cat_val,
                cat_se=cat_se_val,
                average=round(avg, 1) if avg is not None else None,
            ))

    # Merge Values (from LLM + interview)
    all_value_keys: set[str] = set()
    value_sources: list[tuple[dict, str]] = []
    if llm_data and llm_data.get("values"):
        vals = llm_data["values"].get("values", {})
        all_value_keys.update(vals.keys())
        value_sources.append((vals, "llm-claude"))
    if interview_data and interview_data.get("values"):
        vals = interview_data["values"].get("values", {})
        all_value_keys.update(vals.keys())
        value_sources.append((vals, "interview"))

    for value_key in all_value_keys:
        value_estimates: list[TraitEstimate] = []
        for vals_dict, method_name in value_sources:
            vd = vals_dict.get(value_key)
            if isinstance(vd, dict):
                value_estimates.append(TraitEstimate(
                    score=vd.get("score", 50),
                    confidence=vd.get("confidence", "medium"),
                    method=method_name,
                    evidence=vd.get("evidence", []),
                ))
        if value_estimates:
            profile.values.values[value_key] = _merge_estimates(value_estimates)

    # Determine top/bottom values from merged scores
    sorted_values = sorted(
        profile.values.values.items(),
        key=lambda x: x[1].final_score,
        reverse=True,
    )
    profile.values.top_3 = [k for k, _ in sorted_values[:3]]
    profile.values.bottom_3 = [k for k, _ in sorted_values[-3:]]

    # Import self-report scores for all instruments
    if self_report:
        results = self_report.get("results", {})

        # CRT
        crt = results.get("crt-7")
        if crt:
            for s in crt.get("scores", []):
                if s.get("scaleId") == "crt-analytic":
                    profile.cognitive.crt_score = s["raw"]
            _ensure_manifest_record(profile, "crt-7", crt)

        # NCS
        ncs = results.get("ncs-18")
        if ncs:
            for s in ncs.get("scores", []):
                if s.get("scaleId") == "ncs":
                    profile.cognitive.need_for_cognition = s["normalized"]
            _ensure_manifest_record(profile, "ncs-18", ncs)

        # Rosenberg
        rses = results.get("rosenberg")
        if rses:
            for s in rses.get("scores", []):
                if s.get("scaleId") == "self-esteem":
                    profile.cognitive.self_esteem = s["normalized"]
            _ensure_manifest_record(profile, "rosenberg", rses)

        # SD3
        sd3 = results.get("sd3")
        if sd3:
            for s in sd3.get("scores", []):
                if s.get("scaleId") == "mach":
                    profile.dark_triad.machiavellianism = s["normalized"]
                elif s.get("scaleId") == "narc":
                    profile.dark_triad.narcissism = s["normalized"]
                elif s.get("scaleId") == "psych":
                    profile.dark_triad.psychopathy = s["normalized"]
            _ensure_manifest_record(profile, "sd3", sd3)

        # PHQ-9 / GAD-7
        phq_gad = results.get("phq9-gad7")
        if phq_gad:
            for s in phq_gad.get("scores", []):
                if s.get("scaleId") == "phq9":
                    profile.clinical.phq9 = s["raw"]
                    profile.clinical.phq9_severity = _phq9_severity(s["raw"])
                elif s.get("scaleId") == "gad7":
                    profile.clinical.gad7 = s["raw"]
                    profile.clinical.gad7_severity = _gad7_severity(s["raw"])
            _ensure_manifest_record(profile, "phq9-gad7", phq_gad)

        # ─── Phase 3: Extended Battery ───────────────────────

        # ECR-R (Attachment)
        ecr = results.get("ecr-r")
        if ecr:
            for s in ecr.get("scores", []):
                if s.get("scaleId") == "anxiety":
                    profile.attachment.anxiety = s["normalized"]
                elif s.get("scaleId") == "avoidance":
                    profile.attachment.avoidance = s["normalized"]
            _ensure_manifest_record(profile, "ecr-r", ecr)

        # ERQ (Emotion Regulation)
        erq = results.get("erq-10")
        if erq:
            for s in erq.get("scores", []):
                if s.get("scaleId") == "reappraisal":
                    profile.emotion_reg.reappraisal = s["normalized"]
                elif s.get("scaleId") == "suppression":
                    profile.emotion_reg.suppression = s["normalized"]
            _ensure_manifest_record(profile, "erq-10", erq)

        # IRI (Empathy)
        iri = results.get("iri-28")
        if iri:
            for s in iri.get("scores", []):
                if s.get("scaleId") == "fantasy":
                    profile.empathy.fantasy = s["normalized"]
                elif s.get("scaleId") == "perspective_taking":
                    profile.empathy.perspective_taking = s["normalized"]
                elif s.get("scaleId") == "empathic_concern":
                    profile.empathy.empathic_concern = s["normalized"]
                elif s.get("scaleId") == "personal_distress":
                    profile.empathy.personal_distress = s["normalized"]
            _ensure_manifest_record(profile, "iri-28", iri)

        # Self-Monitoring: prefer Snyder SM-25, fallback to SM-18
        sm25 = results.get("snyder-sm-25")
        sm18 = results.get("self-monitoring-18")
        if sm25:
            for s in sm25.get("scores", []):
                if s.get("scaleId") == "self-monitoring":
                    profile.social.self_monitoring = s["normalized"]
            _ensure_manifest_record(profile, "snyder-sm-25", sm25)
        elif sm18:
            for s in sm18.get("scores", []):
                if s.get("scaleId") == "self-monitoring":
                    profile.social.self_monitoring = s["normalized"]
            _ensure_manifest_record(profile, "self-monitoring-18", sm18)

        # LOC: prefer Levenson IPC-24, fallback to IE-4
        ipc = results.get("levenson-ipc-24")
        ie4 = results.get("loc-ie4")
        if ipc:
            for s in ipc.get("scores", []):
                if s.get("scaleId") == "internal":
                    profile.social.loc_internal = s["normalized"]
                elif s.get("scaleId") == "powerful_others":
                    profile.social.loc_powerful_others = s["normalized"]
                elif s.get("scaleId") == "chance":
                    profile.social.loc_chance = s["normalized"]
            # Derive loc_external as mean of powerful_others + chance for backwards compat
            if profile.social.loc_powerful_others is not None and profile.social.loc_chance is not None:
                profile.social.loc_external = (profile.social.loc_powerful_others + profile.social.loc_chance) / 2
            _ensure_manifest_record(profile, "levenson-ipc-24", ipc)
        elif ie4:
            for s in ie4.get("scores", []):
                if s.get("scaleId") == "internal":
                    profile.social.loc_internal = s["normalized"]
                elif s.get("scaleId") == "external":
                    profile.social.loc_external = s["normalized"]
            _ensure_manifest_record(profile, "loc-ie4", ie4)

        # Grit: prefer Grit-O, fallback to Grit-S
        grit_o = results.get("grit-o")
        grit_s = results.get("grit-s")
        if grit_o:
            for s in grit_o.get("scores", []):
                if s.get("scaleId") == "perseverance":
                    profile.grit.perseverance = s["normalized"]
                elif s.get("scaleId") == "interest_consistency":
                    profile.grit.interest_consistency = s["normalized"]
                elif s.get("scaleId") == "overall":
                    profile.grit.overall = s["normalized"]
            _ensure_manifest_record(profile, "grit-o", grit_o)
        elif grit_s:
            for s in grit_s.get("scores", []):
                if s.get("scaleId") == "perseverance":
                    profile.grit.perseverance = s["normalized"]
                elif s.get("scaleId") == "interest_consistency":
                    profile.grit.interest_consistency = s["normalized"]
            _ensure_manifest_record(profile, "grit-s", grit_s)

        # RIASEC
        riasec = results.get("riasec-48")
        if riasec:
            scale_map = {
                "realistic": "realistic",
                "investigative": "investigative",
                "artistic": "artistic",
                "social": "social",
                "enterprising": "enterprising",
                "conventional": "conventional",
            }
            for s in riasec.get("scores", []):
                field = scale_map.get(s.get("scaleId", ""))
                if field:
                    setattr(profile.vocational, field, s["normalized"])
            _ensure_manifest_record(profile, "riasec-48", riasec)

        # BPNS: prefer BPNS-21, fallback to BPNS-9
        bpns21 = results.get("bpns-21")
        bpns9 = results.get("bpns-9")
        if bpns21:
            for s in bpns21.get("scores", []):
                sid = s.get("scaleId", "")
                if sid == "autonomy_satisfaction":
                    profile.needs.autonomy = s["normalized"]
                elif sid == "competence_satisfaction":
                    profile.needs.competence = s["normalized"]
                elif sid == "relatedness_satisfaction":
                    profile.needs.relatedness = s["normalized"]
                elif sid == "autonomy_frustration":
                    profile.needs.autonomy_frustration = s["normalized"]
                elif sid == "competence_frustration":
                    profile.needs.competence_frustration = s["normalized"]
                elif sid == "relatedness_frustration":
                    profile.needs.relatedness_frustration = s["normalized"]
            _ensure_manifest_record(profile, "bpns-21", bpns21)
        elif bpns9:
            for s in bpns9.get("scores", []):
                if s.get("scaleId") == "autonomy":
                    profile.needs.autonomy = s["normalized"]
                elif s.get("scaleId") == "competence":
                    profile.needs.competence = s["normalized"]
                elif s.get("scaleId") == "relatedness":
                    profile.needs.relatedness = s["normalized"]
            _ensure_manifest_record(profile, "bpns-9", bpns9)

        # HEXACO: prefer HEXACO-200, fallback to HEXACO-60
        hex200 = results.get("hexaco-200")
        hex60 = results.get("hexaco-60")
        if hex200:
            for s in hex200.get("scores", []):
                sid = s.get("scaleId", "")
                field = _HEXACO_MAP.get(sid)
                if field:
                    setattr(profile.hexaco, field, s["normalized"])
                elif "_" in sid:
                    # Facet-level scores
                    profile.hexaco.facets[sid] = s["normalized"]
            _ensure_manifest_record(profile, "hexaco-200", hex200)
        elif hex60:
            for s in hex60.get("scores", []):
                field = _HEXACO_MAP.get(s.get("scaleId", ""))
                if field:
                    setattr(profile.hexaco, field, s["normalized"])
            _ensure_manifest_record(profile, "hexaco-60", hex60)

        # ─── Phase 4: Extended Battery ─────────────────────

        # SWLS (Life Satisfaction)
        swls = results.get("swls")
        if swls:
            for s in swls.get("scores", []):
                if s.get("scaleId") == "life_satisfaction":
                    profile.wellbeing.life_satisfaction = s["normalized"]
            _ensure_manifest_record(profile, "swls", swls)

        # AAQ-II (Psychological Flexibility)
        aaq = results.get("aaq-ii")
        if aaq:
            for s in aaq.get("scores", []):
                if s.get("scaleId") == "psychological_flexibility":
                    profile.decision_style.psychological_flexibility = s["normalized"]
            _ensure_manifest_record(profile, "aaq-ii", aaq)

        # Dweck ITIS (Growth Mindset)
        dweck = results.get("dweck-itis")
        if dweck:
            for s in dweck.get("scores", []):
                if s.get("scaleId") == "growth_mindset":
                    profile.decision_style.growth_mindset = s["normalized"]
            _ensure_manifest_record(profile, "dweck-itis", dweck)

        # CEI-II (Curiosity)
        cei = results.get("cei-ii")
        if cei:
            for s in cei.get("scores", []):
                if s.get("scaleId") == "stretching":
                    profile.curiosity.stretching = s["normalized"]
                elif s.get("scaleId") == "embracing":
                    profile.curiosity.embracing = s["normalized"]
            _ensure_manifest_record(profile, "cei-ii", cei)

        # AOT-13 (Actively Open-Minded Thinking)
        aot = results.get("aot-13")
        if aot:
            for s in aot.get("scores", []):
                if s.get("scaleId") == "open_minded_thinking":
                    profile.decision_style.open_minded_thinking = s["normalized"]
            _ensure_manifest_record(profile, "aot-13", aot)

        # IUS-12 (Intolerance of Uncertainty)
        ius = results.get("ius-12")
        if ius:
            ius_scores: list[float] = []
            for s in ius.get("scores", []):
                if s.get("scaleId") == "prospective":
                    profile.decision_style.uncertainty_prospective = s["normalized"]
                    ius_scores.append(s["normalized"])
                elif s.get("scaleId") == "inhibitory":
                    profile.decision_style.uncertainty_inhibitory = s["normalized"]
                    ius_scores.append(s["normalized"])
            if ius_scores:
                profile.decision_style.uncertainty_intolerance = sum(ius_scores) / len(ius_scores)
            _ensure_manifest_record(profile, "ius-12", ius)

        # SCS-26 (Self-Compassion)
        scs = results.get("scs-26")
        if scs:
            pos_scales: list[float] = []
            neg_scales: list[float] = []
            for s in scs.get("scores", []):
                sid = s.get("scaleId", "")
                if sid == "self_kindness":
                    profile.self_compassion.self_kindness = s["normalized"]
                    pos_scales.append(s["normalized"])
                elif sid == "self_judgment":
                    profile.self_compassion.self_judgment = s["normalized"]
                    neg_scales.append(s["normalized"])
                elif sid == "common_humanity":
                    profile.self_compassion.common_humanity = s["normalized"]
                    pos_scales.append(s["normalized"])
                elif sid == "isolation":
                    profile.self_compassion.isolation = s["normalized"]
                    neg_scales.append(s["normalized"])
                elif sid == "mindfulness":
                    profile.self_compassion.mindfulness = s["normalized"]
                    pos_scales.append(s["normalized"])
                elif sid == "over_identification":
                    profile.self_compassion.over_identification = s["normalized"]
                    neg_scales.append(s["normalized"])
            # Total: mean of positive subscales + reversed negative subscales
            all_for_total = pos_scales + [100 - n for n in neg_scales]
            if all_for_total:
                profile.self_compassion.total = round(sum(all_for_total) / len(all_for_total), 1)
            _ensure_manifest_record(profile, "scs-26", scs)

        # MFQ-2 (Moral Foundations)
        mfq = results.get("mfq-2")
        if mfq:
            mfq_map = {
                "care": "care", "equality": "equality", "proportionality": "proportionality",
                "loyalty": "loyalty", "authority": "authority", "purity": "purity",
            }
            for s in mfq.get("scores", []):
                field = mfq_map.get(s.get("scaleId", ""))
                if field:
                    setattr(profile.moral_foundations, field, s["normalized"])
            _ensure_manifest_record(profile, "mfq-2", mfq)

        # Frost MPS (Perfectionism)
        fmps = results.get("frost-mps")
        if fmps:
            fmps_map = {
                "concern_over_mistakes": "concern_over_mistakes",
                "personal_standards": "personal_standards",
                "parental_expectations": "parental_expectations",
                "parental_criticism": "parental_criticism",
                "doubts_about_actions": "doubts_about_actions",
                "organization": "organization",
            }
            for s in fmps.get("scores", []):
                field = fmps_map.get(s.get("scaleId", ""))
                if field:
                    setattr(profile.perfectionism, field, s["normalized"])
            _ensure_manifest_record(profile, "frost-mps", fmps)

        # MAAS (Mindfulness)
        maas = results.get("maas")
        if maas:
            for s in maas.get("scores", []):
                if s.get("scaleId") == "mindful_attention":
                    profile.mindfulness.mindful_attention = s["normalized"]
            _ensure_manifest_record(profile, "maas", maas)

        # Authenticity Scale
        auth = results.get("authenticity")
        if auth:
            for s in auth.get("scores", []):
                sid = s.get("scaleId", "")
                if sid == "authentic_living":
                    profile.authenticity.authentic_living = s["normalized"]
                elif sid == "self_alienation":
                    profile.authenticity.self_alienation = s["normalized"]
                elif sid == "external_influence":
                    profile.authenticity.external_influence = s["normalized"]
            _ensure_manifest_record(profile, "authenticity", auth)

        # Tangney Self-Control Scale
        tscs = results.get("tangney-scs")
        if tscs:
            tscs_scores: list[float] = []
            for s in tscs.get("scores", []):
                sid = s.get("scaleId", "")
                if sid == "restraint":
                    profile.self_control.restraint = s["normalized"]
                    tscs_scores.append(s["normalized"])
                elif sid == "impulsivity":
                    profile.self_control.impulsivity = s["normalized"]
                    tscs_scores.append(s["normalized"])
            if tscs_scores:
                profile.self_control.total = round(sum(tscs_scores) / len(tscs_scores), 1)
            _ensure_manifest_record(profile, "tangney-scs", tscs)

        # Maximization Scale (MS-13)
        ms = results.get("maximization")
        if ms:
            ms_scores: list[float] = []
            for s in ms.get("scores", []):
                sid = s.get("scaleId", "")
                if sid == "high_standards":
                    profile.decision_style.high_standards = s["normalized"]
                    ms_scores.append(s["normalized"])
                elif sid == "alternative_search":
                    profile.decision_style.alternative_search = s["normalized"]
                    ms_scores.append(s["normalized"])
                elif sid == "decision_difficulty":
                    profile.decision_style.decision_difficulty = s["normalized"]
                    ms_scores.append(s["normalized"])
            if ms_scores:
                profile.decision_style.maximizing_total = round(sum(ms_scores) / len(ms_scores), 1)
            _ensure_manifest_record(profile, "maximization", ms)

        # ZTPI (Time Perspective)
        ztpi = results.get("ztpi")
        if ztpi:
            ztpi_map = {
                "past_negative": "past_negative", "past_positive": "past_positive",
                "present_hedonistic": "present_hedonistic", "present_fatalistic": "present_fatalistic",
                "future": "future",
            }
            for s in ztpi.get("scores", []):
                field = ztpi_map.get(s.get("scaleId", ""))
                if field:
                    setattr(profile.time_perspective, field, s["normalized"])
            _ensure_manifest_record(profile, "ztpi", ztpi)

        # CAT HEXACO: adaptive refinement scores
        cat_hex = results.get("cat-hexaco")
        if cat_hex:
            _ensure_manifest_record(profile, "cat-hexaco", cat_hex)
            for s in cat_hex.get("scores", []):
                theta = s.get("theta")
                se = s.get("se")
                sid = s.get("scaleId", "")
                if theta is not None:
                    score_100 = _theta_to_100(theta)
                    # Map domain-level scores
                    field = _HEXACO_MAP.get(sid)
                    if field:
                        # CAT domain score — prefer over fixed-form if SE is low
                        if se is not None and se < 0.35:
                            setattr(profile.hexaco, field, score_100)
                    elif "_" in sid:
                        # Facet-level CAT scores
                        profile.hexaco.facets[f"cat_{sid}"] = score_100

    profile.metadata.methods_used = methods_used
    return profile


def _detect_tier(self_report: dict | None) -> str:
    """Auto-detect tier from which instruments are present in self-report data."""
    if not self_report:
        return "standard"
    results = self_report.get("results", {})
    # Check for explicit tier in export
    if "selectedTier" in self_report:
        return self_report["selectedTier"]
    # Heuristic: check for heavy-only instruments
    if any(results.get(i) for i in ("hexaco-200", "grit-o", "bpns-21", "levenson-ipc-24", "snyder-sm-25", "cat-big5", "cat-hexaco",
                                      "aot-13", "ius-12", "scs-26", "mfq-2", "frost-mps", "maas", "authenticity", "tangney-scs", "maximization", "ztpi")):
        return "heavy"
    if any(results.get(i) for i in ("ipip-neo-300", "hexaco-60", "swls", "aaq-ii", "dweck-itis", "cei-ii")):
        return "standard"
    if results.get("ipip-neo-60"):
        return "lite"
    return "standard"


def _ensure_manifest_record(profile: PsycheProfile, instrument_id: str, inst_data: dict) -> None:
    """Record an instrument in the manifest if not already present."""
    existing_ids = {r.instrument_id for r in profile.manifest.instruments}
    if instrument_id in existing_ids:
        return
    rel = INSTRUMENT_RELIABILITY.get(instrument_id, {})
    scores = inst_data.get("scores", [])
    item_count = sum(s.get("itemCount", 0) for s in scores)
    profile.manifest.instruments.append(InstrumentRecord(
        instrument_id=instrument_id,
        item_count=item_count,
        reliability_alpha=rel.get("alpha"),  # type: ignore[arg-type]
        items_per_facet=rel.get("items_per_facet"),  # type: ignore[arg-type]
    ))


def _merge_estimates(estimates: list[TraitEstimate]) -> MergedTrait:
    """Merge multiple method estimates into a single score with CI."""
    if not estimates:
        return MergedTrait(final_score=50.0, confidence="low")

    if len(estimates) == 1:
        e = estimates[0]
        ci_half = 15 if e.confidence == "high" else 25 if e.confidence == "medium" else 35
        return MergedTrait(
            final_score=e.score,
            ci_lower=max(0, e.score - ci_half),
            ci_upper=min(100, e.score + ci_half),
            confidence=e.confidence,
            estimates=estimates,
        )

    # Weighted average
    total_weight = 0.0
    weighted_sum = 0.0
    for e in estimates:
        w = METHOD_WEIGHTS.get(e.method, 0.1)
        # Adjust weight by confidence
        conf_mult = {"high": 1.0, "medium": 0.7, "low": 0.4}.get(e.confidence, 0.5)
        effective_w = w * conf_mult
        weighted_sum += e.score * effective_w
        total_weight += effective_w

    final = weighted_sum / total_weight if total_weight > 0 else 50.0

    # Compute divergence (SD across estimates)
    scores = [e.score for e in estimates]
    mean = sum(scores) / len(scores)
    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    divergence = math.sqrt(variance)

    # CI based on divergence and number of methods
    ci_half = max(5, divergence * 1.5) if len(estimates) >= 2 else 20

    # Overall confidence
    if divergence > 20:
        conf = "low"
    elif divergence > 10 or any(e.confidence == "low" for e in estimates):
        conf = "medium"
    else:
        conf = "high"

    return MergedTrait(
        final_score=round(final, 1),
        ci_lower=max(0, round(final - ci_half, 1)),
        ci_upper=min(100, round(final + ci_half, 1)),
        confidence=conf,
        estimates=estimates,
        divergence=round(divergence, 1),
    )


def _theta_to_100(theta: float) -> float:
    """Convert IRT theta to 0-100 scale via normal CDF.

    theta=0 -> 50, theta=1 -> ~84, theta=-1 -> ~16.
    Uses Hart (1968) approximation, accurate to 7 digits.
    """
    # Abramowitz & Stegun approximation for normal CDF
    if theta < -6:
        return 0.0
    if theta > 6:
        return 100.0

    t = 1.0 / (1.0 + 0.2316419 * abs(theta))
    d = 0.3989422804014327  # 1/sqrt(2*pi)
    p = d * math.exp(-0.5 * theta * theta)
    poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    cdf = 1.0 - p * poly if theta >= 0 else p * poly
    return round(cdf * 100, 1)


def _phq9_severity(score: float) -> str:
    if score < 5: return "none"
    if score < 10: return "mild"
    if score < 15: return "moderate"
    if score < 20: return "moderately severe"
    return "severe"


def _gad7_severity(score: float) -> str:
    if score < 5: return "none"
    if score < 10: return "mild"
    if score < 15: return "moderate"
    return "severe"
