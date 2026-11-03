# BHARAT JYOTISH AI — IMPLEMENTATION ROADMAP
## Phased Modernization & Engineering Roadmap (PRD Version 2.0)
**Date:** November 2026  
**Auditor:** Principal Software Architect  
**Strategy:** Existing Software Audit → Architecture Upgrade → Modular Implementation → Validation → Production SaaS

---

## 1. Overview of Implementation Protocol

As mandated in **PART 26 (Antigravity Execution Protocol)** of the PRD:
1. Work progresses strictly phase by phase.
2. Existing working features are preserved throughout.
3. Every phase requires passing unit tests, documented APIs, and explicit approval before advancing to the next phase.
4. Calculations are verified against independent ephemeris baselines.
5. No fake or placeholder functionality is marked complete.

---

## 2. Phase-by-Phase Roadmap

### PHASE 0 & 1 — Discovery, Baseline Audit & Architectural Planning
- **Status:** **COMPLETE (Current Phase — Awaiting User Review & Approval)**
- **Deliverables:**
  - `docs/audit/EXISTING_SYSTEM_AUDIT.md` (Full repository audit)
  - `docs/audit/MODULE_INVENTORY.md` (58 modules inventoried & classified)
  - `docs/audit/RULE_AUDIT_REPORT.md` (12,506 grantha rules audited, 27 duplicates flagged)
  - `docs/audit/TECHNICAL_DEBT.md` (UI monolith, SQLite concurrency, deprecation fixes)
  - `docs/audit/SECURITY_AUDIT.md` (Vault multi-tenancy verified, PII encryption roadmap)
  - `docs/audit/RECOMMENDED_ARCHITECTURE.md` (5-layer system design specification)
  - `docs/audit/IMPLEMENTATION_ROADMAP.md` (Master phase-by-phase execution plan)
- **Exit Criteria:** Zero code regressions, 104/104 passing tests, user approval.

---

### PHASE 2 — Architecture Foundation & Monolith Decoupling
- **Objective:** Modernize foundation without breaking existing Streamlit app or API.
- **Key Tasks:**
  1. Complete extraction of UI screens 0 to 9 from `src/jyotish/ui/app.py` into `src/jyotish/ui/modules/`:
     - Screen 0: `d1_varga_view.py`
     - Screen 1: `event_view.py`
     - Screen 2: `remedies_view.py`
     - Screen 3: `varga_grid_view.py`
     - Screen 4: `vastu_view.py`
     - Screen 5: `prashna_view.py`
     - Screen 6: `shadbala_view.py`
     - Screen 7: `jaimini_view.py`
     - Screen 8: `dasha_view.py`
     - Screen 9: `transit_view.py`
  2. Setup PostgreSQL database schema with Alembic migration scripts; migrate from SQLite.
  3. Fix `datetime.utcnow()` deprecation warnings with `datetime.now(timezone.utc)`.
  4. Setup Redis caching layer and connection pooling.
- **Verification:** All 104 automated tests pass; `app.py` reduced from 23,200 lines to < 1,500 lines.

---

### PHASE 3 — Astronomical Calculation Engine Hardening
- **Objective:** Independent, deterministic, zero-dependency astronomical layer.
- **Key Tasks:**
  1. Topocentric Moon calculation toggle for fine-precision nakshatra boundaries.
  2. Polar latitude quadrant house calculation safeguard (>66°N/S).
  3. Automated cross-validation suite against JPL Horizons and Swiss Ephemeris test vectors.
  4. Complete calculation metadata persistence (ephemeris version, ayanamsa, coordinates, timestamp).
- **Verification:** Longitudinal discrepancy `< 0.0001°` across 100 historical benchmark charts.

---

### PHASE 4 — Janma Kundali & Varga Engine Hardening
- **Objective:** Standardized divisional charts D1 through D60 with unified SVG rendering.
- **Key Tasks:**
  1. Standardize Varga data model and mathematical division across all 20 divisional charts.
  2. Unify North Indian, South Indian, and East Indian SVG chart visualizers.
  3. Implement Pushkara Navamsha, Pushkara Bhaga, and Vaisheshikamsa dignity scoring.
- **Verification:** Unit tests verifying exact varga planetary sign assignments against BPHS slokas.

---

### PHASE 5 — Strengths, Multi-System Dashas & Transits
- **Objective:** Complete timing and strength engine integration.
- **Key Tasks:**
  1. Complete breakdown of Shadbala 6 sub-strengths with graphical breakdown.
  2. Unify 9 dasha calculation engines (Vimshottari 5-tier, Yogini, Chara, KCD, Shoola, Ashtottari, Narayana).
  3. Real-time Gochar engine with double-transit (Saturn + Jupiter) and Kakshya bindu evaluation.
- **Verification:** Regression benchmark test suite verifying dasha boundary timestamps down to the second.

---

### PHASE 6 — Classical Jyotish System Engines
- **Objective:** Build dedicated, logically independent system engines.
- **Key Tasks:**
  1. *Parashari Engine:* Graha & Bhava Karakas, Drishti, Bhavesh, Yogas.
  2. *Jaimini Engine:* 7/8 Chara Karakas, Arudhas, Argala, Karakamsa, Swamsha.
  3. *KP Engine:* Placidus cusps, Sublords, 4-Step Significators, Horary 1-249.
  4. *Tajika Engine:* Varshaphal, Muntha, Varshesha, 16 Tajika Yogas.
  5. *Prashna Engine:* Independent question-chart pipeline with classical judgment.
- **Verification:** Distinct namespaces for each tradition; zero cross-contamination of calculation logic.

---

### PHASE 7 — Curated Classical Knowledge Base Migration
- **Objective:** Version-controlled classical rule repository in PostgreSQL with pgvector.
- **Key Tasks:**
  1. Deduplicate the 27 nakshatra transits in `samhita_rules.json`.
  2. Migrate all 12,479 unique rules into the PostgreSQL `shastriya_rules` table.
  3. Generate vector embeddings for Sanskrit shlokas and Hindi explanations for semantic retrieval.
  4. Build Shastra Rule Admin interface for expert rule approval and lifecycle tracking.
- **Verification:** Sub-millisecond indexed rule retrieval; 100% of rules traceable to verified classical editions.

---

### PHASE 8 — Yoga, Dosha & Remedy Engines
- **Objective:** Evidence-backed yoga detection, dosha cancellation, and classical remedy synthesis.
- **Key Tasks:**
  1. Curated library of 300+ Raj Yogas, Dhana Yogas, Vipreet Yogas, and Neechabhanga Yogas.
  2. Automated 16 Manglik Pariharas (cancellations) and Kaal Sarp / Pitru Dosha exception logic.
  3. Classical remedy database (Mantras, Danas, Vrats, Pujas, Gemstone suitability safeguards).
- **Verification:** No severe dosha assigned without evaluating full classical cancellation conditions.

---

### PHASE 9 — Master Event Prediction & BTR Engine
- **Objective:** Central analytical engine for 18 specific life event categories.
- **Key Tasks:**
  1. Implement dedicated analysis pipelines for Marriage, Career, Finance, Property, Children, Litigation, Health.
  2. Birth Time Rectification (BTR) engine correlating life events with divisional transitions.
  3. Event probability window calculation exposing supporting and conflicting evidence.
- **Verification:** Rigorous evaluation against historical life-event test datasets.

---

### PHASE 10 — Multi-Agent AI & Independent Audit Agent
- **Objective:** Controlled AI interpretation layer with zero mathematical hallucination.
- **Key Tasks:**
  1. Master Jyotish Orchestrator delegating to 14 Specialist Agents.
  2. Independent Audit Agent verifying that all cited planetary positions and slokas match deterministic outputs.
  3. Model-agnostic LLM interface supporting Gemini, OpenAI, Claude, and local offline models.
- **Verification:** Audit agent intercepts and rejects any hallucinated astrological claims.

---

### PHASE 11 — Next.js Enterprise Frontend & PDF Reports
- **Objective:** Production-grade multilingual SaaS interface and high-fidelity PDF generation.
- **Key Tasks:**
  1. Modern Next.js 14+ client with Tailwind CSS, Radix UI, and authentic Vedic design language (Navy, Gold, Ivory).
  2. Seamless i18n support for Hindi, English, and Hinglish.
  3. 50-page comprehensive Kundali magazine PDF generator with proper Devanagari typography.
- **Verification:** Responsive UI across mobile and desktop; verified PDF rendering.

---

### PHASE 12 — Accuracy Validation Lab, Security & Production SaaS
- **Objective:** Production launch on cloud infrastructure.
- **Key Tasks:**
  1. Deploy Accuracy Validation Lab with continuous mathematical regression benchmarking.
  2. Implement AES-256 PII encryption for birth data and PostgreSQL Row-Level Security.
  3. Production deployment with Docker, Nginx, Redis, PostgreSQL, and automated backup routines.
- **Verification:** End-to-end security audit, load testing under 1,000 concurrent requests.

