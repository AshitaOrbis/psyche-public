# Phase 5 human-rater pair manifest

**Generated**: 2026-05-27T22:30:16.898961+00:00
**v0.3 tag**: `2026-05-19_v03`
**v0.2 tag**: `2026-04-26_v02_hard_codex_only`
**Selection rule**: docs/v0_3_phase_minus_1_design_lock.md §-1.13
**Seeds**: pair selection=42, A/B anonymization=43
**Total selected**: 11 / target 50

## By stratum

- **T1**: 2 / 32
- **T2**: 4 / 8
- **v02_anchor**: 5 / 10

## By pair type

- `C4` vs `C5`: 3
- `C5` vs `C5_CONTRACT`: 2
- `C5_NONPUBLIC` vs `C5_NONPUBLIC_CONTRACT`: 2
- `L1` vs `L2`: 2
- `L2` vs `L3`: 2

## Shortfalls

- C0 vs C_GENERIC_CONTRACT (have 0)
- C3 vs C_GENERIC_CONTRACT (have 0)
- C4 vs C_GENERIC_CONTRACT (have 0)
- C5 vs C_GENERIC_CONTRACT (have 0)
- C0 vs C4_WRONG_PROFILE (have 0)
- C3 vs C4_WRONG_PROFILE (have 0)
- C4 vs C4_WRONG_PROFILE (have 0)
- C4_WRONG_PROFILE vs C5 (have 0)
- C5 vs C5_NONPUBLIC (have 0)
- C5_CONTRACT vs C5_NONPUBLIC (have 0)
- C3 vs C5_NONPUBLIC (have 0)
- C4 vs C5_NONPUBLIC (have 0)
- C5_CONTRACT vs C5_NONPUBLIC_CONTRACT (have 0)
- C3 vs C5_NONPUBLIC_CONTRACT (have 0)
- C4 vs C5_NONPUBLIC_CONTRACT (have 0)
- C5 vs L1 (have 0)
- C5_CONTRACT vs L3 (have 0)
- v02 anchor C0 vs C4 (have 0, want 3)
- v02 anchor C1_padded vs C4 (have 0, want 2)

## Next step

Run `drivers/rater_cli.py` to rate the 50 pairs.
