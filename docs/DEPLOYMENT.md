# JyotishOS — Production Deployment & Operations Guide
Reference: `docs/IMPLEMENTATION_PRD.md` (Phase 6, Task P6-T8)

This document provides complete instructions for deploying the modernized **JyotishOS** backend and frontend in containerized and cloud environments.

---

## 1. System Architecture

The modernized JyotishOS SaaS stack consists of:
1. **API Gateway (`api`)**: FastAPI REST service exposing `/api/v1` routes (chart calculations, grounded evidence packs, health probes, data privacy).
2. **Astrologer UI (`ui`)**: Streamlit application providing interactive chart analysis, Rules Lab review, and PDF report generation.
3. **Primary Database (`postgres`)**: PostgreSQL 16 storing user authentication, encrypted natal chart records, and consultation notes.
4. **Cache & Rate Limiting (`redis`)**: Redis 7 managing subscription tier rate limits and distributed cache.
5. **Swiss Ephemeris Volume (`./ephe`)**: High-precision JPL/Swiss Ephemeris `.se1` data files mounted read-only at `/app/ephe`.

---

## 2. Environment Variables

Configure the following environment variables in `.env` or your cloud secrets manager:

| Variable | Description | Default / Example |
|---|---|---|
| `EPHE_PATH` | Path to Swiss Ephemeris files (`.se1`) | `/app/ephe` |
| `DATABASE_URL` | PostgreSQL connection URI | `postgresql://user:pass@host:5432/db` |
| `REDIS_URL` | Redis connection URI | `redis://redis:6379/0` |
| `JWT_SECRET` | Secret key for JWT signing | *Cryptographically random 64-char string* |
| `JYOTISH_ENCRYPTION_KEY` | At-rest AES encryption key for birth data | *Cryptographically random string* |
| `GEMINI_API_KEY` | Google Gemini API key for grounded narration | `AIzaSy...` (optional for offline modes) |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins for Web UI | `https://astro-jyotish.streamlit.app` |

---

## 3. Swiss Ephemeris Setup

Swiss Ephemeris files provide sub-arcsecond astronomical accuracy across 6,000 years (-3000 to +3000).

1. Download core ephemeris files (`sepl_18.se1`, `semo_18.se1`, `seas_18.se1`) from [AstroDienst Ephemeris Download](https://www.astro.com/ftp/swisseph/ephe/).
2. Place them into `./ephe/`:
   ```bash
   mkdir -p ephe
   # Copy or symlink downloaded .se1 files into ephe/
   ```
3. If no external `.se1` files are present, JyotishOS automatically utilizes its internal **Swiss Ephemeris Moshier analytical model**, maintaining standard precision with zero degradation errors.

---

## 4. Quickstart with Docker Compose

Deploy the complete stack with a single command:

```bash
# 1. Clone repository
git clone https://github.com/your-org/jyotish-os.git
cd jyotish-os

# 2. Configure environment
cp .env.example .env

# 3. Build and launch services in background
docker compose up -d --build

# 4. Verify running services
docker compose ps
```

Access points:
- **FastAPI Documentation**: `http://localhost:8000/docs`
- **Health Check Endpoint**: `http://localhost:8000/health`
- **Streamlit Web UI**: `http://localhost:8501`

---

## 5. Health Probes & Monitoring

Production container orchestrators (Kubernetes / ECS / Cloud Run) should configure:
- **Liveness Probe**: `GET /health` (returns HTTP 200, status `healthy` or `degraded`, memory RSS, and uptime).
- **Engine Verification**: `GET /health/engine` (verifies Swiss Ephemeris version, detected `.se1` files, and runs self-test calculation).

---

## 6. GDPR / DPDP Compliance & Privacy Operations

- **Right to Erasure (Delete My Data)**:
  `POST /api/v1/privacy/delete-user-data` with `{"owner_email": "user@example.com", "confirm": true}` permanently erases user charts and returns an immutable audit certificate.
- **Data Portability**:
  `GET /api/v1/privacy/export-user-data?owner_email=user@example.com` returns complete personal chart records in structured JSON.
- **At-Rest Encryption**:
  All stored personal identifying fields (names, locations, contact notes) are automatically encrypted using authenticated Fernet symmetric encryption.

---

## 7. OpenAPI Integration & Background Task Processing

- **OpenAPI Schema Contract**:
  The static OpenAPI 3.x schema is version-controlled at `docs/openapi.json` for frontend SDK generation (Next.js, Flutter, React Native).
- **Asynchronous Processing**:
  Heavy calculations and 50+ page multi-page PDF generation run asynchronously via `/api/v1/tasks/generate-report` returning HTTP 202 with polling status via `/api/v1/tasks/{task_id}`.


