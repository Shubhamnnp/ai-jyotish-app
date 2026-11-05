# JyotishOS — Codebase & Subsystems Inventory (Phase U0, Task U0-T5)

**Timestamp:** 2026-11-05T09:30:00Z  
**Branch:** `upgrade/phase-0-baseline`  
**Reference Commit:** `a41933e`  
**Total Source Python Files:** 177 | **Total Test Files:** 76 | **Total Lines:** ~75,820 lines

---

## 1. Executive Subsystems Mapping

| Subsystem | Path | Files | Lines | Primary Responsibility | Active Wiring | Test Suite Status |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| **Core Ganita Engine** | `src/jyotish/core/` | 25 | 12,321 | Swiss Ephemeris calculations, Vargas, Shadbala, Ashtakavarga, Houses, Jaimini, Upagrahas, LRU Caching | UI & API | 100% Tested (12 test suites) |
| **Dasha Engines** | `src/jyotish/dasha/` | 10 | 2,026 | Vimshottari (5-level), Yogini, Jaimini Chara, Narayana, Sthira, Drig | UI & API | Tested (`test_dasha_*`) |
| **Rules Engine & Lab** | `src/jyotish/rules/` | 10 | 3,125 | Schema v2, Inverted Index, Quarantine, Evaluator, Conflict Graph, Consensus | UI & API | Tested (`test_rules_*`) |
| **AI & Grounding** | `src/jyotish/ai/`, `narrate/` | 8 | 2,868 | Grounded narration, Evidence validation, Multi-agent orchestrator | UI & API | Tested (`test_narrator_*`, `test_trio_*`) |
| **Services Layer** | `src/jyotish/services/` | 36 | 19,861 | BTR, Milan, Prashna, Report Generator, Shastriya Faladesh, Varshaphal, Timeline | UI & API | Tested (18 test suites) |
| **REST API Gateway** | `src/jyotish/api/` | 16 | 2,147 | FastAPI OpenAPI v1 endpoints, Evidence pack, Auth, Health probes | Port 8000 | Tested (`test_api*`) |
| **UI & Workbench** | `src/jyotish/ui/` | 40 | 29,476 | Streamlit Workbench, 30 Dedicated Modules, SVG North/South/East Renderers | Port 8501 | Smoke Tested (`verify.py`) |
| **Timezone & Geo** | `src/jyotish/timeloc/` | 5 | 417 | Historical IANA timezones, War Time (+6.5h), Pre-1906 LMT, Geocoding | UI & API | Tested (`test_timeloc*`) |
| **Security & Privacy** | `src/jyotish/security/`, `safety/` | 4 | 326 | Fernet AES encryption, Argon2id, DPDP Right-to-Erasure, Ethical Filters | Core & API | Tested (`test_privacy_*`, `test_auth_*`) |
| **Astrological Schools** | `src/jyotish/schools/` | 9 | 1,192 | School isolation: Parashari, Jaimini, KP, Lal Kitab, Western | Engine | Tested (`test_school_*`) |
| **Events & Evidence** | `src/jyotish/events/`, `evidence/`| 10 | 1,764 | Event query matrix, 2-tier factor extraction, Timing synthesis | Services | Tested (`test_evidence_*`) |
| **Database** | `src/jyotish/db/` | 2 | 289 | SQLAlchemy models & SessionManager | Optional | Tested (`test_database_*`) |

---

## 2. Calculation Capabilities Inventory

### 2.1 Astronomical Ephemeris & House Systems (`src/jyotish/core/`)
- **Ephemeris Engine:** `SwissEphemerisProvider` (`pyswisseph`/`swisseph` 20260201) with fallback to `PyEphemProvider` (visibly flagged via `engine_degraded=True`).
- **Ayanamsa Support:** 5 Standard Modes (Lahiri/Chitra Paksha, Raman, Krishnamurti KP, Yukteshwar, True Chitra).
- **House Systems Supported:**
  1. `Whole Sign` ('W' - Default Vedic Rashi bhava)
  2. `Equal` ('E' - Equal 30° from Ascendant)
  3. `Sripati` ('O' - Porphyry-based trisection with Bhava Madhyas and Bhava Sandhis)
  4. `Porphyry` ('O' - Quadrant trisection)
  5. `Placidus` ('P' - Semi-arc quadrant system used in KP)
- **High-Latitude Safeguards:** Automatic fallback to Equal house system when `abs(latitude) > 66.0°` (polar circles).

### 2.2 Complete Vargas (`src/jyotish/core/varga.py`)
- **Implemented Divisions (20 total):**
  - Shodashavarga (16 classical): D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60
  - Additional: D5, D6, D8, D11
- **All 16 Shodashavarga charts verified against golden Swiss Ephemeris oracle.**

### 2.3 Planetary Strengths (`src/jyotish/core/shadbala.py`)
- **6-Fold Shadbala Sub-Components:**
  1. *Sthanabala* (Uccha, Saptavargaja, Ojayugma, Kendradi, Drekkana)
  2. *Digbala* (Directional strength)
  3. *Kaalabala* (Nathonnatha, Paksha, Tribhaga, Varsha/Masa/Dina/Hora, Yuddhabala)
  4. *Cheshtabala* (Retrograde / planetary motion velocity)
  5. *Naisargikabala* (Fixed luminosity strength: Sun > Moon > Venus > Jupiter > Mercury > Mars > Saturn)
  6. *Drigbala* (Aspectual strength)
- **Bhava Bala:** Evaluates Bhava Adhipati Bala, Bhava Digbala, and Bhava Drishti Bala.

### 2.4 Ashtakavarga & Classical Reductions (`src/jyotish/core/ashtakavarga.py`)
- **Bhinnashtakavarga (BAV):** 7 planets + Lagna 8×12 matrices.
- **Sarvashtakavarga (SAV):** Exact 337 total points invariant.
- **Trikona Shodhana:** Trikona rashi reductions (Aries-Leo-Sagittarius, Taurus-Virgo-Capricorn, etc.).
- **Ekadhipatya Shodhana:** Dual-ownership planet sign reductions (Mars, Mercury, Jupiter, Venus, Saturn).

### 2.5 Jaimini & Upagrahas
- **Jaimini Chara Karakas:** 7 Karakas (Atmakaraka AK to Darakaraka DK) + 8 Karaka variant.
- **Arudha Padas:** All 12 Bhava Padas (AL, A2–A11, UL) with Swakshetra and 7th house exceptions.
- **Diurnal Upagrahas:** Mandi and Gulika computed from exact Dinamana/Ratrimana portions, plus Dhuma, Vyatipata, Parivesha, Indrachapa, and Upaketu.

### 2.6 Dasha Systems (`src/jyotish/dasha/`)
- **Vimshottari Dasha:** 120-year cycle with 5-level nested hierarchy (Maha, Antar, Pratyantar, Sookshma, Prana) with exact Moon-longitude balance.
- **Secondary Dashas:** Yogini (36-yr), Jaimini Chara, Narayana, Sthira, and Drig Dasha.

---

## 3. UI Modules Inventory (Streamlit Astrologer Workbench)

All 30 active modules located in `src/jyotish/ui/modules/`:

| Index | Module File | UI Name | Status |
| :---: | :--- | :--- | :---: |
| **0** | `d1_varga_view.py` | 📜 Birth Chart (Kundali & D1-D60) | **Active & Wired** |
| **1** | `event_view.py` | 🎯 Event Analysis (Events) | **Active & Wired** |
| **2** | `remedies_view.py` | 🛡️ Afflictions & Remedies (Remedies) | **Active & Wired** |
| **3** | `varga_grid_view.py` | 📊 Varga Grid (Vargas) | **Active & Wired** |
| **4** | `vastu_view.py` | 🏛️ Vastu Astrology (Vastu) | **Active & Wired** |
| **5** | `prashna_view.py` | ❓ Horary Chart (Prashna) | **Active & Wired** |
| **6** | `shadbala_view.py` | ⚖️ Planetary Strengths (Bala) | **Active & Wired** |
| **7** | `jaimini_view.py` | 🔱 Jaimini Astrology (Jaimini) | **Active & Wired** |
| **8** | `dasha_view.py` | ⏱️ Dasha Systems (Dasha) | **Active & Wired** |
| **9** | `transit_view.py` | 🪐 Transit & Ashtakvarga (Transit) | **Active & Wired** |
| **10** | `kp_view.py` | 📐 KP Astrology (KP System) | **Active & Wired** |
| **11** | `muhurta_view.py` | ⏳ Auspicious Timing (Muhurta) | **Active & Wired** |
| **12** | `sudarshan_chakra_view.py` | ☸️ Sudarshan Chakra (Sudarshan) | **Active & Wired** |
| **13** | `varshaphal_view.py` | 📅 Solar Return (Varshaphal) | **Active & Wired** |
| **14** | `btr_view.py` | ⏳ Birth Time Rectification (BTR) | **Active & Wired** |
| **15** | `matching_view.py` | 💍 Kundali Matching (Matching) | **Active & Wired** |
| **16** | `daivajna_view.py` | 💬 Daivajna AI (AI Astrologer) | **Active & Wired** |
| **17** | `reports_view.py` | 📄 Kundali Reports (Reports) | **Active & Wired** |
| **18** | `rules_library_view.py`| 📚 Rules Library & Lab (Rules) | **Active & Wired** |
| **19** | `validation_view.py` | 🔍 Calculation Validation (Validation)| **Active & Wired** |
| **20** | `yogas_doshas_view.py` | ⚡ Yogas & Doshas (Yog & Dosh) | **Active & Wired** |
| **21** | `numerology_view.py` | 🔢 Numerology (Lo-Shu) | **Active & Wired** |
| **22** | `lal_kitab_view.py` | 📕 Lal Kitab (Lal Kitab) | **Active & Wired** |
| **23** | `ayurvedic_diet_view.py`| 🍽️ Ayurvedic Diet (Diet) | **Active & Wired** |
| **24** | `relationships_view.py`| 🤝 Relationships (Relations) | **Active & Wired** |
| **25** | `health_disease_view.py`| 🏥 Health & Disease (Health) | **Active & Wired** |
| **26** | `body_anatomy_view.py` | 🧬 Body & Physique (Physique) | **Active & Wired** |
| **27** | `pooja_view.py` | 🕉️ Ishta Devata & Pooja (Pooja) | **Active & Wired** |
| **28** | `karma_view.py` | 🧘 Karma & Destiny (Karma) | **Active & Wired** |
| **29** | `panchang_view.py` | 📅 Vedic Panchang (Panchang) | **Active & Wired** |

---

## 4. API Endpoints Inventory (`src/jyotish/api/`)

- **`/health`**: Service availability & version probe.
- **`/health/engine`**: Precision ephemeris state (`swisseph` vs `degraded`).
- **`/api/v1/evidence/pack`**: Full evidence pack extraction for external AI or callers.
- **`/api/v1/evidence/domains`**: List of 8 grounded life domains.
- **`/api/v1/evidence/schema`**: OpenAPI Schema definition for evidence contracts.
- **`/api/v1/rules/audit-stats`**: Live status counts of classical rules (verified vs quarantined).
- **`/api/v1/privacy/delete-user-data`**: DPDP Right-to-Erasure compliant user deletion.
- **`/api/v1/privacy/export-user-data`**: DPDP data portability export.

---

## 5. Dead Code & Unwired Candidate Audit

1. **`src/jyotish/cli.py`**: Empty stub file (0 lines). Candidate for implementation or documentation in Phase U3.
2. **`run_api.bat` / `run_api.ps1`**: Needs verification to ensure correct uvicorn invocation.
3. **`data/rules/legacy_raw_rules.json`**: Historical unverified draft rules, quarantined from production runtime.
4. **Duplicate static assets**: `static/` vs `ui/static/` — will be consolidated without removing referenced paths in Phase U3.
