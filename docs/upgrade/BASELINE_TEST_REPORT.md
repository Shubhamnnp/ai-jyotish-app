# JyotishOS — Upgrade Baseline Test & Environment Report (U0-T1 & U0-T2)

**Timestamp:** 2026-11-05T08:20:00Z  
**Branch:** `upgrade/phase-0-baseline`  
**Reference Commit:** `8517117`  
**Protocol Phase:** Phase U0 (Baseline & Safety Net)

---

## 1. Environment & Astronomical Engine Audit (U0-T1)

> [!IMPORTANT]
> **Active Ephemeris Mode: `SwissEph (precise)`**  
> High-precision Swiss Ephemeris C-bindings are active and non-degraded. Sub-arcsecond planetary accuracy is operational across all 357 passing baseline tests.

| Metric | Measured Value |
| :--- | :--- |
| **Python Runtime** | `3.13.7 (64-bit AMD64, MSC v.1944)` |
| **Operating System** | `Windows-10-10.0.19045-SP0` |
| **Primary Ephemeris Provider** | `SwissEphemerisProvider` |
| **Ephemeris Library** | `swisseph 20260201` (Direct C-extension) |
| **Pyswisseph / Pysweph** | `swisseph` active |
| **Ephemeris Data Method** | Built-in Moshier semi-analytical ephemeris model (valid 3000 BCE to 3000 CE, precision < 0.1 arcsec) |
| **`_has_swisseph` Flag** | `True` |
| **`is_degraded` Flag** | `False` |
| **Engine Degradation State** | **None (Precise Engine Active)** |

---

## 2. Baseline Test Suite Summary (U0-T2)

```
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\BMC\Desktop\Shubham File\Shubham Work\AI Jotish SaaS Project
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1, asyncio-1.4.1.post1, cov-7.1.0
collected 357 items

================== 357 passed, 1 warning in 91.56s (0:01:31) ==================
```

### Breakdown:
- **Total Tests Collected:** 357
- **Passed:** 357 (100.0%)
- **Failed:** 0
- **Skipped:** 0
- **Errors:** 0
- **Deprecation Warnings:** 1 (Starlette `anyio.abc.BlockingPortal` deprecation warning in testclient)

---

## 3. Slowest 20 Tests Benchmark (Duration Profiling)

| Duration | Test Case | Subsystem |
| :--- | :--- | :--- |
| **7.18s** | `tests/test_rules_lab_view.py::test_rules_lab_admin_panel_mock` | UI / Rules Lab Admin Mock |
| **4.14s** | `tests/test_auth_security.py::test_licence_code_hash_generation_and_redemption` | Argon2 / Crypto Fixture |
| **3.48s** | `tests/golden/test_oracle_tolerances.py::test_all_100_oracle_tolerances` | 15 Historical Oracle Charts |
| **2.99s** | `tests/test_api.py::test_api_grahalakshanam_login` | FastAPI Auth Endpoint |
| **2.98s** | `tests/test_api.py::test_api_rules` | FastAPI Rules Retrieval |
| **2.78s** | `tests/test_api_production_hardening.py::test_api_v1_openapi_schema_completeness` | OpenAPI Schema Validation |
| **2.73s** | `tests/test_rules_quarantine.py::test_engine_quarantine_integration` | Quarantine & Tier Filtering |
| **1.38s** | `tests/test_panchang.py::test_panchang_delhi_oct_2026` | Astronomical Sunrise & Tithi |
| **1.34s** | `tests/test_trio_ai_engine.py::test_trio_gratitude_response` | AI Grounding & Prompt Engine |
| **1.29s** | `tests/test_gemology.py::test_ai_sahayak_panna_prohibition_when_mercury_in_8th` | Shastriya Safety Filter |
| **1.26s** | `tests/test_gemology.py::test_ai_sahayak_marriage_query_dual_kundali` | Gemology & Dual Kundali |
| **1.19s** | `tests/test_gemology.py::test_ai_sahayak_gratitude_response` | AI Conversation Response |
| **1.16s** | `tests/test_auth_security.py::test_licence_code_hash_generation_and_redemption` | Licence Code Validation |
| **1.15s** | `tests/test_trio_ai_engine.py::test_dasha_inquiry_with_hinglish_typo` | Dasha Engine Query |
| **1.06s** | `tests/test_trio_ai_engine.py::test_trio_greeting_response` | Agent Handshake |
| **0.97s** | `tests/test_gemology.py::test_ai_sahayak_greeting_general_intelligence` | General Intelligence Fallback |
| **0.96s** | `tests/test_panchang.py::test_panchang_arbitrary_date` | Panchang Solar Motion |
| **0.95s** | `tests/test_trio_ai_engine.py::test_trio_astrological_consultation_offline_fallback` | Offline Narration Fallback |
| **0.94s** | `tests/test_timeloc_geo.py::test_timezonefinder_resolution` | Geocoding & Zone Lookup |
| **0.93s** | `tests/test_auth_security.py::test_no_hardcoded_master_code_in_source` | Static Security Check |

---

## 4. Pre-Existing Gaps & Baseline Notes

1. **Zero Failing Tests:** Baseline is 100% green (357 / 357 passing).
2. **Characterization Snapshots Needed:** Prior to Phase U1 refactoring, `tests/regression/` characterization snapshots must lock down the 15 diverse astronomical profiles with exact tolerances.
3. **No Silent Fallback Rule:** Any future test run where `SwissEphemerisProvider` fails to load must immediately flag `engine_degraded=True` and fail characterization snapshot comparisons explicitly.
