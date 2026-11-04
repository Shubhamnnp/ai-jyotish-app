# Phase 1 Completion Report: Ephemeris & Time Correctness

**Date:** 2026-11-04  
**Status:** 100% COMPLETE (Tasks P1-T1 through P1-T10)  
**Reference PRD:** `docs/IMPLEMENTATION_PRD.md` (Phase 1)  
**Agent Protocol:** `AGENTS.md` (Section 0.1)  
**Test Suite Result:** 203 / 203 PASSED (0 failures, 1 warning)

---

## 1. Executive Summary

Phase 1 establishes Swiss Ephemeris (`swisseph`) as the sole authoritative high-precision astronomical engine for JyotishOS, eliminating all silent fallbacks, implementing official Swiss sidereal ayanamsa modes, solving the historical B3 epoch drift, introducing true lunar node dynamics, sidereal house systems (Whole Sign, Equal, Sripati Bhava Chalit, Porphyry, Placidus) with polar safeguards, deterministic offline geocoding and IANA timezone resolution, historical Indian time rules, school-configurable combustion orbs, and transparent astronomical provenance metadata.

---

## 2. Complete Phase 1 Task Ledger

| Task ID | Commit | Description | Verification & Impact |
|:---|:---|:---|:---|
| **P1-T1** | `8fb9ec1` | Primary Swiss Ephemeris with J2000 self-test | Configured `SWE_EPHE_PATH` discovery, startup test (< 0.001° Sun error), and `/health/engine` endpoint. |
| **P1-T2** | `b331c97` | Elimination of silent ephemeris fallbacks | Replaced silent exception suppression with `EphemerisUnavailable`. PyEphem strictly gated behind `ALLOW_DEGRADED_ENGINE=true`. Engine labeled `Swiss (Moshier)` unless `.se1` files present. Streamlit UI warning banner active. |
| **P1-T3** | `1fcadc7` | Canonical Sidereal Ayanamsa Mapping | Mapped 24 classical ayanamsa modes to Swiss `SIDM_*` constants. Unknown names raise `ValueError`. Added `GET /api/v1/astronomy/ayanamsas`. |
| **P1-T4** | `4516ed2` | PRD Finding B3 Epoch Drift Investigation | Benchmarked 1950–2050 CE. Proved PyEphem equinox precession double-counting drifts up to 0.709° (42.5 arcmin). Formally declared PyEphem standalone path unsupported. |
| **P1-T5** | `054337d` | Lunar Node Speeds & Direct Motion | Integrated Swiss Ephemeris `FLG_SPEED` for True and Mean lunar nodes. True Node station/direct motion supported. Enforced `Ketu = (Rahu + 180°) % 360°`. |
| **P1-T6** | `4f2ace4` | Swiss `houses_ex` & Sidereal Systems | Implemented Whole Sign (`b'W'`), Equal (`b'E'`), Sripati (`b'O'`), Porphyry (`b'O'`), and Placidus (`b'P'`). Polar safeguard (> 66° N/S) auto-falls back to Equal with warning. Sripati calculates 12 Madhyas and 12 Sandhis as midpoints. |
| **P1-T7** | `0b3f47a` | Time & Location Service (`src/jyotish/timeloc/`) | Replaced naive timezone subtraction with standard library `zoneinfo` + `tzdata`. Enforced historical Indian time rules (1942–45 War Time +6:30, 1962/1965/1971 DST, pre-1906 LMT). Ambiguous DST times require `fold=0` or `fold=1`; non-existent spring-forward gaps raise `NonExistentTimeError`. |
| **P1-T8** | `454581e` | Offline Geocoding & Timezone Resolution | Built `src/jyotish/timeloc/geo.py` using `timezonefinder` and offline directory of major Indian/world cities. Added `GET /api/v1/astronomy/timeloc/resolve`. |
| **P1-T9** | `e41df25` | Planetary Speed & Configurable Combustion | Extracted daily planetary speed directly via `FLG_SPEED`. Built `src/jyotish/core/combustion.py` with classical BPHS / Surya Siddhanta default orbs (Moon 12°, Mars 17°, Mercury 14°/12°, Jupiter 11°, Venus 10°/8°, Saturn 15°) and Varahamihira / custom school presets. |
| **P1-T10** | `1049212` | Rich Chart Calculation Metadata Block | Attached `{engine, engine_type, engine_version, ayanamsa: {name, value_degrees}, house_system, timezone_iana, utc_datetime, jd_ut, delta_t_seconds, engine_degraded, ephemeris_mode}` to `CalculationMetadata`. Rendered interactive provenance block in Streamlit UI. |

---

## 3. PRD Finding B3 Benchmark Summary

| Date (UTC) | Sun Discrepancy | Moon Discrepancy | Jupiter Discrepancy | Status |
| :--- | :--- | :--- | :--- | :--- |
| **1950-01-15** | 0.703643° (2533″) | 0.697757° (2512″) | 0.703490° (2533″) | Unsupported in PyEphem |
| **1975-04-14** | 0.350942° (1263″) | 0.345253° (1243″) | 0.350798° (1263″) | Unsupported in PyEphem |
| **2000-01-01** | 0.005794° (21″)   | 0.000020° (0.1″)  | 0.001393° (5.0″)  | Coincides near J2000 epoch |
| **2025-01-01** | 0.343440° (1236″) | 0.348585° (1255″) | 0.354451° (1276″) | Unsupported in PyEphem |
| **2050-11-11** | 0.704443° (2536″) | 0.705532° (2540″) | 0.709229° (2553″) | Unsupported in PyEphem |

**Root Cause:** Linear precession double-counting at $\approx 50.3\text{ arcsec/year}$.  
**Resolution:** PyEphem is formally declared unsupported for standard operations. Swiss Ephemeris is enforced.

---

## 4. Verification & Test Suite Summary

- **Total Tests:** 203
- **Passed:** 203 (100%)
- **Failed:** 0
- **Regression Invariants:** Verified against `tests/golden/benchmarks_snapshot.json` (10 historical Kundalis, 337 SAV invariant preserved).
- **New Test Modules Added in Phase 1:**
  1. `tests/test_ephemeris_engine.py` (9 tests)
  2. `tests/test_ayanamsa_mapping.py` (5 tests)
  3. `tests/test_b3_epoch_discrepancy.py` (3 tests)
  4. `tests/test_lunar_nodes.py` (3 tests)
  5. `tests/test_house_systems.py` (6 tests)
  6. `tests/test_timeloc.py` (8 tests)
  7. `tests/test_timeloc_geo.py` (5 tests)
  8. `tests/test_combustion_and_motion.py` (4 tests)
  9. `tests/test_chart_metadata.py` (3 tests)

---

## 5. Known Gaps & Handoff to Phase 2

1. **Ephemeris Data Files (.se1):** Currently running in built-in Moshier analytical mode (`Swiss (Moshier)`). The system operates seamlessly, and downloading optional JPL `.se1` files into `./ephe` or `C:\sweph\ephe` unlocks sub-arcsecond precision.
2. **Phase 2 Handoff:** Phase 1 (Ephemeris & Time Correctness) is 100% complete. Phase 2 (Golden Invariant Harness & Accuracy Benchmark) is ready to begin upon owner review and approval.
