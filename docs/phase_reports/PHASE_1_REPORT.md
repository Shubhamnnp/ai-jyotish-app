# Phase 1 Progress & Investigation Report: Ephemeris & Time Correctness

**Date:** 2026-11-04  
**Status:** IN PROGRESS (Tasks P1-T1 through P1-T4 complete)  
**Reference PRD:** `docs/IMPLEMENTATION_PRD.md` (Phase 1)  
**Agent Protocol:** `AGENTS.md` (Section 0.1)  

---

## 1. Overview of Phase 1 Progress

Phase 1 establishes Swiss Ephemeris (`swisseph`) as the mandatory primary engine for JyotishOS, eliminating silent fallbacks, implementing official Swiss sidereal ayanamsa modes, and investigating the historical epoch error (PRD Finding B3).

---

## 2. Completed Tasks

| Task ID | Commit | Description | Scope / Verification |
|---------|--------|-------------|----------------------|
| **P1-T1** | `8fb9ec1` | `P1-T1: make pyswisseph primary ephemeris with startup self-test and health endpoint` | Configured `SWE_EPHE_PATH` discovery, startup self-test (< 0.001° error on Sun at J2000.0), `/health/engine` endpoint, and `docs/EPHEMERIS_SETUP.md`. |
| **P1-T2** | `b331c97` | `P1-T2: remove silent ephemeris fallbacks and require explicit degradation signaling` | Replaced silent `except BaseException` swallows with `EphemerisUnavailable`. PyEphem fallback is restricted strictly to `ALLOW_DEGRADED_ENGINE=true`. Engine is labeled `Swiss (Moshier)` unless `.se1` files are loaded. Streamlit UI banner added. |
| **P1-T3** | `1fcadc7` | `P1-T3: map all supported ayanamsas to Swiss sidereal modes and expose via API` | Mapped 24 classical ayanamsa modes directly to Swiss `SIDM_*` constants. Unknown names raise `ValueError`. Added `GET /api/v1/astronomy/ayanamsas`. |
| **P1-T4** | `pending` | `P1-T4: investigate B3 epoch drift and declare PyEphem unsupported` | Executed 21-point temporal benchmark (1950–2050 CE). Demonstrated epoch drift up to 0.709° (42.5 arcmin). Officially declared PyEphem standalone path unsupported for professional Jyotish. |

---

## 3. PRD Finding B3 Investigation: PyEphem vs Swiss Ephemeris Error Table

As mandated by Task **P1-T4**, sidereal coordinates (Lahiri) were computed via both PyEphem and Swiss Ephemeris for Sun, Moon, and Jupiter at 5-year intervals across 1950–2050 CE at 12:00:00 UTC.

### Benchmark Results Table

| Date (UTC) | Sun Discrepancy | Moon Discrepancy | Jupiter Discrepancy | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **1950-01-15** | 0.703643° (2533″) | 0.697757° (2512″) | 0.703490° (2533″) | **EXCESSIVE (> 0.02°)** |
| **1955-07-20** | 0.626492° (2255″) | 0.620368° (2233″) | 0.626478° (2255″) | **EXCESSIVE (> 0.02°)** |
| **1960-03-10** | 0.561809° (2023″) | 0.555523° (2000″) | 0.557335° (2006″) | **EXCESSIVE (> 0.02°)** |
| **1965-11-05** | 0.482830° (1738″) | 0.477704° (1720″) | 0.473078° (1703″) | **EXCESSIVE (> 0.02°)** |
| **1970-08-25** | 0.415636° (1496″) | 0.409863° (1475″) | 0.413007° (1487″) | **EXCESSIVE (> 0.02°)** |
| **1975-04-14** | 0.350942° (1263″) | 0.345253° (1243″) | 0.350798° (1263″) | **EXCESSIVE (> 0.02°)** |
| **1980-12-30** | 0.271244° (976″)  | 0.265526° (956″)  | 0.265566° (956″)  | **EXCESSIVE (> 0.02°)** |
| **1985-09-18** | 0.205245° (739″)  | 0.199507° (718″)  | 0.195806° (705″)  | **EXCESSIVE (> 0.02°)** |
| **1990-05-02** | 0.140694° (506″)  | 0.135069° (486″)  | 0.138276° (498″)  | **EXCESSIVE (> 0.02°)** |
| **1995-02-28** | 0.073341° (264″)  | 0.067686° (244″)  | 0.068210° (246″)  | **EXCESSIVE (> 0.02°)** |
| **2000-01-01** | 0.005794° (21″)   | 0.000020° (0.1″)  | 0.001393° (5.0″)  | **Tolerable** |
| **2005-06-21** | 0.070822° (255″)  | 0.076356° (275″)  | 0.077255° (278″)  | **EXCESSIVE (> 0.02°)** |
| **2010-10-10** | 0.144808° (521″)  | 0.150757° (543″)  | 0.155754° (541″)  | **EXCESSIVE (> 0.02°)** |
| **2015-04-01** | 0.207344° (746″)  | 0.213139° (767″)  | 0.216033° (778″)  | **EXCESSIVE (> 0.02°)** |
| **2020-08-15** | 0.282455° (1017″) | 0.288170° (1037″) | 0.292633° (1053″) | **EXCESSIVE (> 0.02°)** |
| **2025-01-01** | 0.343440° (1236″) | 0.348585° (1255″) | 0.354451° (1276″) | **EXCESSIVE (> 0.02°)** |
| **2030-07-04** | 0.420501° (1514″) | 0.424763° (1529″) | 0.429432° (1546″) | **EXCESSIVE (> 0.02°)** |
| **2035-12-25** | 0.496738° (1788″) | 0.500779° (1803″) | 0.506220° (1822″) | **EXCESSIVE (> 0.02°)** |
| **2040-05-15** | 0.558176° (2009″) | 0.561207° (2020″) | 0.566730° (2040″) | **EXCESSIVE (> 0.02°)** |
| **2045-09-30** | 0.633154° (2279″) | 0.634641° (2285″) | 0.643953° (2318″) | **EXCESSIVE (> 0.02°)** |
| **2050-11-11** | 0.704443° (2536″) | 0.705532° (2540″) | 0.709229° (2553″) | **EXCESSIVE (> 0.02°)** |

---

## 4. Root Cause Analysis & Architectural Decision

### Root Cause
PyEphem's `body.compute(date)` calculates positions referenced to the apparent equinox of date. When converting to ecliptic coordinates and applying a J2000-based Ayanamsa formula without the full precession-nutation rotation matrix, precession is counted twice or drifts linearly at approximately $50.3\text{ arcsec/year}$. Over a 50-year interval, this accumulates to:
$$50 \times 50.3\text{ arcsec} \approx 2515\text{ arcsec} \approx 0.70^\circ$$

### Architectural Conclusion
Because the maximum error ($0.709^\circ$) dramatically exceeds professional Vedic tolerance ($\le 0.02^\circ$ for planets, $\le 0.05^\circ$ for Moon):
1. **PyEphem is formally declared UNSUPPORTED** for standard JyotishOS calculations.
2. It remains strictly as an emergency degraded fallback requiring explicit opt-in (`ALLOW_DEGRADED_ENGINE=true`).
3. Swiss Ephemeris (`swisseph`) is the sole authoritative astronomical provider for chart casting.
