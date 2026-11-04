# Swiss Ephemeris Data Files Setup & Configuration Guide

**Reference PRD:** `docs/IMPLEMENTATION_PRD.md` (P1-T1)  
**Engine:** Swiss Ephemeris (`pyswisseph` / `pysweph` / `swisseph`)  

---

## 1. Overview

JyotishOS uses the **Swiss Ephemeris** as its core astronomical engine.
The engine supports two operational modes:

1. **Moshier Semi-Analytical Mode (Default Built-In)**:
   - Built into the Swiss Ephemeris C library.
   - Requires **no external data files**.
   - Computes planetary positions with sub-arcsecond accuracy for general charts.
   - Identified in engine health as `Swiss Ephemeris (Moshier)`.

2. **JPL DE431 High-Precision Ephemeris Mode (`.se1` files)**:
   - Uses compressed Swiss Ephemeris data files (`.se1`) based on JPL DE431.
   - Provides full sub-arcsecond numerical integration over 1800–2400 CE.
   - Identified in engine health as `Swiss Ephemeris (DE431)`.

---

## 2. Downloading Ephemeris Files (1800–2400 CE)

For professional astrological deployments requiring full JPL DE431 files, download the standard `.se1` files from the official AstroDienst repository:

- **Official AstroDienst FTP / HTTP:**
  - `https://www.astro.com/ftp/swisseph/ephe/`
- **Core Files Required for 1800–2400 CE:**
  - `sepl_18.se1` through `sepl_24.se1` (Planetary Ephemerides)
  - `semo_18.se1` through `semo_24.se1` (Lunar Ephemerides)
  - `seas_18.se1` through `seas_24.se1` (Main Asteroids / Chiron / Pholus)

### Automated Download Script
You can place files directly into the `ephe/` folder at project root:

```bash
# Create directory
mkdir -p ephe

# Example download for 1900-2099 CE (covers 99% of contemporary charts)
curl -o ephe/sepl_19.se1 https://www.astro.com/ftp/swisseph/ephe/sepl_19.se1
curl -o ephe/sepl_20.se1 https://www.astro.com/ftp/swisseph/ephe/sepl_20.se1
curl -o ephe/semo_19.se1 https://www.astro.com/ftp/swisseph/ephe/semo_19.se1
curl -o ephe/semo_20.se1 https://www.astro.com/ftp/swisseph/ephe/semo_20.se1
```

---

## 3. Configuring the Ephemeris Path

Set the environment variable `SWE_EPHE_PATH` to point to your directory:

```bash
# Linux / macOS / Docker
export SWE_EPHE_PATH=/app/ephe

# Windows PowerShell
$env:SWE_EPHE_PATH = "C:\path\to\ephe"
```

If `SWE_EPHE_PATH` is not explicitly set, the engine searches the following default paths in order:
1. `./ephe`
2. `./ephemeris_data`
3. `/usr/share/ephe`
4. `/usr/local/share/ephe`

If no `.se1` files are present in the search path, the engine transparently uses the built-in Swiss Moshier analytical ephemeris without failure, tagging its metadata accordingly.

---

## 4. Verifying Engine Health

Verify the active ephemeris engine and self-test results at any time via the API:

```http
GET /health/engine
```

**Example Response (Moshier Mode):**
```json
{
  "engine": "swisseph",
  "version": "20260201",
  "ephe_path": "default (built-in Moshier)",
  "ephe_files_count": 0,
  "ephemeris_mode": "Swiss Ephemeris (Moshier)",
  "self_test": "passed",
  "self_test_details": {
    "test": "Sun sidereal longitude at J2000.0 (JD 2451545.0)",
    "status": "passed",
    "calculated_longitude": 256.515697,
    "difference_degrees": 0.000000189,
    "daily_speed": 1.019392
  }
}
```

