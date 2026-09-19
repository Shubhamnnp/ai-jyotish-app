# JyotishOS: Shastriya AI Jyotish SaaS Platform

**JyotishOS** is an enterprise-grade, multi-system Vedic Astrology platform uniting deterministic mathematical calculations (Swiss Ephemeris / PyEphem, D1–D60 Shodashavarga, Ashtakavarga Shodhana, 6-fold Shadbala, Vimshottari/Yogini/Chara Dashas, Gochar transits, Varshaphal, BTR, Kundali Milan), a 32-rule classical evaluation engine (Brihat Parashara Hora Shastra, Jaimini, Tajika, Prashna), an integrated Geocoding API & Vedic Rishi API validator, and a grounded Gemini AI narrative & interactive consultation layer.

---

## 🌟 Key Features

1. **Deterministic Calculation Core (No AI Hallucination)**:
   - **Swiss Ephemeris & PyEphem Engine**: Dual-engine architecture with high-precision JPL DE431 astronomical positions, speeds, combustion, and retrograde tracking.
   - **Ayanamsa Support**: Lahiri (Chitra Paksha), Raman, KP, and True Chitra.
   - **House Cusps**: Whole Sign and Equal House systems.
   - **Complete Shodashavarga (D1 to D60)**: D1 (Rashi), D2 (Hora), D3 (Drekkana), D4 (Chaturthamsha), D7 (Saptamsha), D9 (Navamsha), D10 (Dashamsha), D12 (Dwadashamsha), D16 (Shodashamsha), D20 (Vimshamsha), D24 (Chaturvimshamsha), D27 (Saptavimshamsha), D30 (Trimshamsha), D60 (Shashtiamsha), and **Vimsopaka Bala** (20-point divisional strength).
   - **Panchang**: Tithi, Vara, Nakshatra, Yoga, and Karana.
   - **Jaimini 7 & 8 Karakas**: Atmakaraka (AK), Amatyakaraka (AmK), Bhratrukaraka (BK), Matrukaraka (MK), Putrakaraka (PK), Gnatikaraka (GK), Darakaraka (DK), Karakamsha, and Arudha Padas (AL, UL, A1–A12).
   - **Special Lagnas & Upagrahas**: Hora Lagna (HL), Ghati Lagna (GL), Sri Lagna (SL), Indu Lagna, Gulika, Mandi, Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu.
2. **Ashtakavarga & Classical Shodhana**:
   - Bhinna Ashtakavarga (BAV) for all 7 classical grahas.
   - Sarva Ashtakavarga (SAV) summing to exactly **337 bindus** (classical conservation invariant).
   - **Trikona Shodhana** (triplicity reduction) and **Ekadhipatya Shodhana** (dual rulership reduction).
   - **Shodhita Pinda**: Rashi Pinda, Graha Pinda, and Yoga Pinda calculations.
3. **Shadbala, Bhavabala & Planetary Avasthas**:
   - 6-fold strength: Sthana Bala, Dik Bala, Kaala Bala, Cheshta Bala, Naisargika Bala, Drik Bala.
   - Total in Virupas & Rupas against BPHS minimum thresholds (Strength Ratio).
   - Bhava Bala (12 houses) and Ishta/Kashta Phala.
   - Planetary Avasthas: Baladi (Bala, Kumara, Yuva, Vriddha, Mrita), Jagratadi (Awake, Dreaming, Sleeping), and Deeptadi (Deepta, Mudita, Deena, etc.).
4. **Multi-System Dasha Engines**:
   - **120-Year Vimshottari Dasha**: Mahadasha, Antardasha, Pratyantardasha, and Sookshmadasha point-in-time resolver.
   - **36-Year Yogini Dasha**: Mangala, Pingala, Dhanya, Bhramari, Bhadrika, Ulka, Siddha, Sankata cycle.
   - **Jaimini Chara Dasha**: Direct and indirect sign-based dasha durations and sequence.
5. **Ghatna Query (Event Window Analysis - Core MVP)**:
   - Analyzes any single target date (e.g. `12-04-2027`) or 30-day window.
   - Evaluates natal baseline, active dasha, gochar transits (Sade Sati, Dhaiya, Jupiter-Saturn double transit on 10th, Guru-Chandal), Ashtakavarga bindus, and fires applicable shastriya rules with a multi-system consensus score (0.0 to 1.0).
6. **Varshaphal (Tajika Annual Solar Return)**:
   - Precision solar return moment calculation, Varsha Kundali, Muntha, Varshesha (5 candidates), Tajika Sahams (Punya, Vidya, Yashas, Karma), Ithasala/Ishrafa yogas, and Mudda Dasha.
7. **Birth Time Rectification (BTR)**:
   - Multi-event fitting engine scanning candidate windows ($\pm 15$ to $\pm 120$ min) against past verified life events (career, marriage, children, travel, health) to output ranked candidate birth times.
8. **Kundali Milan (Synastry / Matchmaking)**:
   - 36-Guna Ashtakoota (Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi) with classical cancellations and mutual Manglik Dosha analysis.
9. **Geocoding API & Location Resolver**:
   - Built-in gazetteer of 80+ major Indian sacred/metro cities and global hubs, plus online OpenStreetMap Nominatim fallback with automated timezone offset detection.
10. **Vedic Rishi API Integration & Validation**:
    - Connected API client for Vedic Rishi with automated cross-validation comparing planetary longitudes, Panchang, and matching scores.
11. **Gemini AI Sahayak & Classical Knowledge Base**:
    - Grounded RAG powered by Google Gemini (`google-genai` SDK) using authenticated classical scriptures (BPHS, Saravali, Phaladeepika, Jaimini, Tajika, Prashna Marga).
    - Strict ethical guardrails (rejects death prediction, medical diagnosis, and gambling speculation).
12. **Multi-Style Chart Renderer & Standalone HTML Report**:
    - Renders North Indian Diamond, South Indian Box, and East Indian Surya charts in pure vector SVG.
    - Standalone printable HTML report exportable to PDF with 1-click.

---

## 📁 Project Architecture

```
AI Jotish SaaS Project/
├── jyotish-rules-library-v1.json    # 32 Classical Starter Rules (JSON)
├── jyotish-saas-prd.md              # Full Product Requirements Document
├── src/
│   └── jyotish/
│       ├── core/
│       │   ├── constants.py         # Rashis, Nakshatras, Dignities, Aspects, AV Rules
│       │   ├── models.py            # Pydantic schema for Charts, Shodhana, Shadbala, Jaimini
│       │   ├── ephemeris.py         # Swiss Ephemeris & PyEphem Dual-Engine Provider
│       │   ├── calculator.py        # Kundali chart, house cusps, Panchang, Atmakaraka
│       │   ├── varga.py             # D1 to D60 Divisional charts & Vimsopaka Bala
│       │   ├── ashtakavarga.py      # BAV, SAV (337 bindus), Trikona/Ekadhipatya Shodhana
│       │   ├── shadbala.py          # 6-fold Shadbala, Virupas, Bhavabala & Avasthas
│       │   ├── jaimini.py           # 7/8 Chara Karakas, Karakamsha, Arudhas, Special Lagnas
│       │   ├── upagraha.py          # Gulika, Mandi, Dhuma, Vyatipata, Parivesha, etc.
│       │   └── gochar.py            # Transits, Sade Sati, Dhaiya, Double Transit
│       ├── dasha/
│       │   ├── vimshottari.py       # 120-year cycle & point-in-time dasha resolver
│       │   ├── yogini.py            # 36-year Yogini Dasha engine
│       │   └── chara.py             # Jaimini Chara Dasha engine
│       ├── rules/
│       │   ├── engine.py            # Evaluates all 32 classical rules with D9/D10 checks
│       │   └── consensus.py         # Multi-system consensus aggregator & scoring
│       ├── services/
│       │   ├── event_query.py       # Ghatna Query pipeline orchestrator
│       │   ├── prashna.py           # Horary query chart and analysis service
│       │   ├── varshaphal.py        # Tajika Solar Return Annual Chart & Muntha
│       │   ├── btr.py               # Birth Time Rectification engine
│       │   ├── milan.py             # 36-Guna Ashtakoota & Manglik matching
│       │   ├── geocoding.py         # Geocoding API & Location Resolver
│       │   ├── vedic_rishi.py       # Vedic Rishi client & cross-validation
│       │   └── report_generator.py  # Standalone printable HTML/PDF report generator
│       ├── ai/
│       │   ├── knowledge_base.py    # Classical Shastra Knowledge Base (BPHS, Saravali, etc.)
│       │   └── narrative.py         # Gemini AI narrative, chat consultation & guardrails
│       ├── api/
│       │   └── main.py              # FastAPI REST gateway with 15+ endpoints
│       └── ui/
│           ├── chart_renderer.py    # North, South, and East Indian SVG Chart Renderers
│           └── app.py               # Full interactive Streamlit SaaS Dashboard (14 Tabs)
└── tests/
    ├── test_jyotish_engine.py       # Astronomical & astrological test suite (All Passed)
    └── test_api.py                  # FastAPI REST integration tests (All Passed)
```

---

## 🚀 How to Run

### 1. Run the Interactive Streamlit SaaS Dashboard
```bash
python -m streamlit run src/jyotish/ui/app.py
```
Open your browser at `http://localhost:8501` to access all 14 tabs:
- **Affliction & Free Will**: 12 Houses and 9 Planets Free Will percentage, soumya/krura count and symbols toggle, 26 Life Areas 3-pillar breakdown, and Rashi Tatva classification.
- **Dasvarga Table**: Complete color-coded dignity grid across D1-D60 (Own, Moolatrikona, Exaltation, Debilitation, Friend, Neutral, Enemy).
- **Vastu-Jyotish Mandala**: 8 cardinal directions and Brahmasthan alignment, chart-specific diagnostic scoring, sacred plant remedies (Shami, Panasa, Tulsi), and bilingual English/Hindi advice.
- **Prashna (Horary)**: 23 classical categories, Tajika Ithasala yoga detection, 12 houses role mapping with emojis (Doctor 🩺, Treatment 💉, Partner 💍, Client 🫵, Job 💼, Money 💰).
- **Grahalakshanam Cloud Sync**: 1-click authentication and folder/chart synchronization directly with `shubham8jyotish@gmail.com` account.
- **Ghatna Query**: Event window prediction with rule evidence.
- **Janm Kundali**: North, South, and East Indian chart styles with D1-D60 vargas.
- **Shadbala**: 6-fold planetary strength virupas and avasthas.
- **Jaimini**: Chara Karakas, Arudhas (AL, UL), and Special Lagnas.
- **Dashas**: Vimshottari, Yogini, and Chara Dasha drill-down.
- **Transits & Shodhana**: SAV, BAV, and Shodhita Pindas.
- **Varshaphal**: Annual solar return, Muntha, and Sahams.
- **BTR**: Birth Time Rectification with life-events fitting.
- **Kundali Milan**: 36-Guna matching and Manglik check.
- **AI Sahayak**: Interactive chat consultation grounded in Shastras.
- **Comprehensive Report**: 1-click Printable HTML/PDF report download.
- **32 Rules Library**: Classical rules catalog.
- **Vedic Rishi**: Automated API cross-validation.

### 2. Run the FastAPI REST Server
```bash
python -m uvicorn src.jyotish.api.main:app --reload --port 8000
```
Interactive Swagger docs available at: `http://localhost:8000/docs`.

### 3. Run Automated Tests
```bash
python tests/test_jyotish_engine.py
python tests/test_api.py
python tests/test_grahalakshanam_suite.py
```
All three test suites verify:
- Ephemeris calculations, Swiss Ephemeris provider, and Lahiri ayanamsa.
- Grahalakshanam live authentication and full cloud sync.
- AfflictionEngine: Dasvarga table, Free Will scores, and 26 Life Area breakdowns.
- VastuJyotishEngine: 8 cardinal zones and remedial mandala diagnostics.
- PrashnaService: 23 Question categories, house role emojis, and Tajika Ithasala.
- Complete 32 classical starter rules loaded and evaluated.
- Ashtakavarga conservation invariant ($SAV = 337$) and Shodhana reductions.
- Shadbala 6-fold virupas and planetary avasthas.
- Jaimini Karakas, Arudhas, and Upagrahas.
- Secondary Dashas (Yogini and Chara Dasha).
- Varshaphal Tajika solar return, Muntha, and Sahams.
- Birth Time Rectification candidate ranking.
- Kundali Milan 36-Guna Ashtakoota and Manglik matching.
- Geocoding API location resolution and Vedic Rishi cross-validation.
- End-to-end FastAPI endpoints integration.

