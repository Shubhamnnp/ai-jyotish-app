# BHARAT JYOTISH AI — RECOMMENDED TARGET ARCHITECTURE
## Architectural Blueprint & System Design Specification (PRD Phase 1 Deliverable)
**Date:** November 2026  
**Author:** Principal Software Architect & Multi-Agent System Architect  
**Target Specification:** PRD Version 2.0 Complete Architecture

---

## 1. Architectural Principles

1. **Deterministic Calculation Core:** Astronomical positions, divisional charts, planetary strengths, dashas, and transits are computed exclusively by verified mathematical engines. AI never invents calculations.
2. **Traceable Classical Knowledge:** Every astrological rule links directly to authoritative Sanskrit editions (BPHS, Saravali, Phaladeepika, Brihat Jataka, Jaimini Sutras). Unverified rules are never presented as classical facts.
3. **Evidence-Based Explanations:** The system outputs supporting evidence, conflicting indicators, exceptions, and cancellations before drawing conclusions.
4. **Logical Decoupling:** Astrological traditions (Parashari, Jaimini, KP, Tajika, Prashna, Lal Kitab) remain logically separate and maintain dedicated calculation namespaces.
5. **Modular Monolith to Cloud-Native SaaS:** A clean, decoupled monolithic core initially, transitioning to containerized micro-services as scaling demands dictate.

---

## 2. Five-Layer Target Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       LAYER 1: PRESENTATION LAYER                           │
│  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐  │
│  │     Next.js 14+ React Client     │   │      Streamlit Workbench UI     │  │
│  │   (Tailwind, Radix UI, i18n:    │   │   (Astrologer Internal Lab,     │  │
│  │   Hindi, English, Hinglish)     │   │   Rapid Calculation Prototyping)│  │
│  └─────────────────────────────────┘   └─────────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST & WebSockets
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                            LAYER 2: API GATEWAY                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     Python FastAPI RESTful Service                    │  │
│  │  • JWT / OAuth2 Auth  • RBAC Permissions  • Redis Rate Limiter        │  │
│  │  • OpenAPI 3.1 Docs   • Pydantic v2 Models • Tenant Vault Isolation   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    LAYER 3: JYOTISH COMPUTATIONAL CORE                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────────────┐  │
│  │ Astronomical     │  │ Divisional (D1)  │  │ Dasha Framework           │  │
│  │ Ephemeris Engine │  │ Shodashvarga D60 │  │ (Vimshottari, Yogini,     │  │
│  │ (Swiss Ephem)    │  │ (Vimsopaka Bala) │  │  Chara, KCD, Shoola, etc) │  │
│  └──────────────────┘  └──────────────────┘  └───────────────────────────┘  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────────────┐  │
│  │ Planetary        │  │ Astrological     │  │ Shastriya Rules &         │  │
│  │ Strengths        │  │ Traditions       │  │ Inverted Index            │  │
│  │ (Shadbala / SAV) │  │ (KP/Jaimini/Taj) │  │ (12,506 Classical Rules)  │  │
│  └──────────────────┘  └──────────────────┘  └───────────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                      LAYER 4: AI MULTI-AGENT SYSTEM                         │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       Master Jyotish Orchestrator                     │  │
│  └───────────────────────────────────┬───────────────────────────────────┘  │
│          ┌───────────────────────────┴───────────────────────────┐          │
│          ▼                                                       ▼          │
│  ┌───────────────────────────────┐               ┌───────────────────────┐  │
│  │     14 Specialist Agents      │               │   Independent Audit   │  │
│  │  (Parashari, Jaimini, KP,     │               │   & Verification Agent│  │
│  │   Dasha, Transit, Yoga, BTR)  │               │   (Anti-Hallucination)│  │
│  └───────────────────────────────┘               └───────────────────────┘  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    LAYER 5: INFRASTRUCTURE & PERSISTENCE                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────────────┐  │
│  │ PostgreSQL 16+   │  │ pgvector         │  │ Redis 7+ Cache &          │  │
│  │ (Multi-Tenant    │  │ (Shastra Semantic│  │ Celery Async Task Worker  │  │
│  │  RLS Schemas)    │  │  Embeddings)     │  │ (PDFs, BTR Searches)      │  │
│  └──────────────────┘  └──────────────────┘  └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Subsystem Specifications

### 3.1 Astronomical Engine (`jyotish_core/astronomy/`)
- Pure Python and C-binding Swiss Ephemeris (`swisseph`) layer.
- Exact planetary longitudes, geocentric coordinates, topocentric Moon adjustments, diurnal speeds, combustion thresholds, and ayanamsa presets (Lahiri Chitrapaksha default, KP, Raman, Yukteshwar).

### 3.2 Master Event Prediction Engine (`prediction_engine/`)
Implements 18 specialized event analytical pipelines:
1. Marriage & Relationship (`event_registry/marriage.py`)
2. Career, Enterprise & Job Transitions (`event_registry/career.py`)
3. Financial Prosperity & Wealth Accumulation (`event_registry/finance.py`)
4. Real Estate, Land & Vehicle Acquisition (`event_registry/property.py`)
5. Higher Education & Competitive Examinations (`event_registry/education.py`)
6. Foreign Travel & Overseas Settlement (`event_registry/foreign_travel.py`)
7. Childbirth & Progeny (`event_registry/children.py`)
8. Litigation, Disputes & Legal Vindication (`event_registry/litigation.py`)
9. Health, Disease Vulnerability & Ayurdaya (`event_registry/health.py`)
10. Spiritual Awakening, Deeksha & Karmic Ledger (`event_registry/spirituality.py`)

Every event pipeline evaluates:
`Janma D1 -> Relevant Varga -> Dasha Activation -> Double Transit (Jupiter/Saturn) -> Kakshya Bindus -> Shastriya Evidence Chain`.

### 3.3 Multi-Agent AI Architecture (`ai/orchestrator/`)
- **Master Jyotish Orchestrator:** Parses user intent in Hindi, English, or Hinglish; extracts target event date; delegates computation to structured Jyotish engines.
- **Specialist Agents:** 14 domain-specific agents consuming strictly structured calculation artifacts (never raw LLM prompts).
- **Independent Audit Agent:** Inspects agent narrative outputs before delivery to user. Verifies that all cited slokas exist in the verified knowledge base and that no astronomical facts are hallucinated.

---

## 4. Technology Stack Justification

| Component | Selected Technology | Alternative Considered | Justification |
| :--- | :--- | :--- | :--- |
| **Primary Backend** | Python 3.13 + FastAPI | Go, Node.js | Native integration with `pyswisseph`, NumPy, and scientific Jyotish libraries. |
| **Relational Database** | PostgreSQL 16+ | MongoDB, MySQL | ACID transactions, Row-Level Security (RLS) for multi-tenancy, JSONB querying for AST conditions. |
| **Vector Database** | `pgvector` (embedded) | Pinecone, Qdrant | Zero operational complexity, co-locates rule text embeddings directly with relational rule rows. |
| **Cache & Task Queue** | Redis 7 + Celery / ARQ | RabbitMQ | Low-latency in-memory cache for ephemeris computations + async queue for PDF generation. |
| **Frontend SaaS** | Next.js 14+ (App Router) | Vue, Angular | Server-Side Rendering (SSR) for SEO, optimal Devanagari typography rendering, dynamic SVG chart rendering. |

