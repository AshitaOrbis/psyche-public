"""Paths and constants for PsycheEval."""

from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parents[1]

PROMPTS_DIR = PROJECT_ROOT / "prompts"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
DATA_DIR = PROJECT_ROOT / "data"
RUNS_DIR = PROJECT_ROOT / "runs"
REPORTS_DIR = PROJECT_ROOT / "reports"

SEED_BANK_PUBLIC = DATA_DIR / "seed_bank_public_inspired.jsonl"
SEED_BANK_SYNTHETIC = DATA_DIR / "seed_bank_pure_synthetic.jsonl"
SOURCE_PACKETS_DIR = DATA_DIR / "source_packets"

# --- Pilot definitions ------------------------------------------------------

MICRO_PILOT_PUBLIC_INSPIRED = [
    "pfi_slalom_altar_001",
    "pfi_dario_armadillo_001",
    "pfi_emily_blender_001",
    "pfi_pawl_gram_001",
]

MICRO_PILOT_PURE_SYNTHETIC = [
    "syn_calibration_goblin_001",
    "syn_conflict_allergic_moralist_001",
    "syn_high_agency_spiraler_001",
    "syn_patient_craftsperson_001",
]

# Legacy (v0.1): micro-pilot conditions. C5 only for public-inspired (gated on source packet grounding).
MICRO_PILOT_CONDITIONS_CORE = ["C0", "C1", "C3", "C4"]
MICRO_PILOT_CONDITIONS_PUBLIC_EXTRA = ["C5"]

# Per-pilot condition map. run.py looks up by pilot name; falls back to the
# legacy MICRO_PILOT_* constants when a pilot is not listed.
PILOT_CONDITIONS: dict[str, dict[str, list[str]]] = {
    "micro_pilot": {
        "core": MICRO_PILOT_CONDITIONS_CORE,
        "public_extra": MICRO_PILOT_CONDITIONS_PUBLIC_EXTRA,
    },
    # v0.2 hard-scenario pilot: adds C1_padded and C4_shuffled length controls.
    # C5_CONTRACT (PAE separator, locked 2026-05-05) joins C5 in PI-only.
    "v02_hard_pilot": {
        "core": ["C0", "C1", "C1_padded", "C3", "C4", "C4_shuffled"],
        "public_extra": ["C5", "C5_CONTRACT"],
    },
    # v0.3 full pilot. Inherits v0.2 corpus; adds:
    #   T1 personalization probes: C_GENERIC_CONTRACT (all personas, length-matched to C4),
    #     C4_WRONG_PROFILE (all personas, opposite-trait/opposite-need mapping per R10),
    #     C5_NONPUBLIC + C5_NONPUBLIC_CONTRACT (scope per Phase -1.9 decision).
    #   T2 C5_CONTRACT ablation ladder: L1, L2, L3 (L0=C5, L4=C5_CONTRACT exist already).
    # Phase 0 splits these into core / pi_only via the public_extra mechanism.
    "v03_full_pilot": {
        "core": ["C0", "C1", "C1_padded", "C3", "C4", "C4_shuffled",
                 "C_GENERIC_CONTRACT", "C4_WRONG_PROFILE"],
        "public_extra": ["C5", "C5_CONTRACT", "C5_NONPUBLIC", "C5_NONPUBLIC_CONTRACT",
                         "L1", "L2", "L3"],
    },
}


def conditions_for(pilot_name: str) -> dict[str, list[str]]:
    return PILOT_CONDITIONS.get(
        pilot_name,
        {"core": MICRO_PILOT_CONDITIONS_CORE, "public_extra": MICRO_PILOT_CONDITIONS_PUBLIC_EXTRA},
    )


# Author models used in the micro-pilot
AUTHOR_MODELS = ["opus", "gpt-5.4"]

# Default judge models intentionally exclude Opus. Claude/Opus judging is a
# quota-bound deferred project and must be requested explicitly.
JUDGE_MODELS = ["gpt-5.4", "gpt-5.5-xhigh", "kimi-k2.6"]
OPUS_DEFERRED_JUDGE_MODELS = ["opus"]

# Official judges for v0.1 tri-model canonical analysis. Records with any
# other judge_model are exploratory probes and are excluded from canonical
# reports unless `include_probes=True` is set explicitly. The canonical
# record format stores the bare model id ("gpt-5.5", "opus"), not the
# reasoning-effort-suffixed JUDGE_MODELS variant ("gpt-5.5-xhigh").
OFFICIAL_JUDGES_V01 = ("gpt-5.4", "gpt-5.5", "opus")


def pilot_dir(pilot_name: str = "micro_pilot") -> Path:
    """Directory for pilot-specific generated data."""
    return DATA_DIR / pilot_name


def run_dir(run_tag: str) -> Path:
    """Directory for a specific model-author run. run_tag like `2026-04-20_micro`."""
    return RUNS_DIR / run_tag
