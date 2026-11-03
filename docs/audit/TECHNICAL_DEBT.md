# BHARAT JYOTISH AI — TECHNICAL DEBT AUDIT
## Comprehensive Technical Debt, Performance & Architecture Deficit Report
**Date:** November 2026  
**Auditor:** Principal Software Architect & QA Lead  
**Scope:** Whole Repository Audit

---

## 1. Executive Summary

This report catalogues all technical debt, code smells, performance bottlenecks, deprecation warnings, and architectural anti-patterns identified in the Bharat Jyotish AI codebase during the Phase 1 audit.

Overall Health Score: **82 / 100** (Solid calculation core, passing tests, but presentation and database infrastructure require modernization).

---

## 2. Identified Technical Debt & Remediation Strategy

### 2.1 UI Monolith Architecture (Severity: HIGH)
- **Current State:** `src/jyotish/ui/app.py` previously exceeded 23,200 lines (~1.7 MB). While screens 10–28 have been cleanly extracted into `src/jyotish/ui/modules/`, screens 0 through 9 (including D1/Varga charts, Afflictions, Shadbala, Jaimini, Dasha, and Gochar) remain embedded inside `app.py`.
- **Impact:**
  - High memory footprint on Streamlit session boot.
  - Slower script parsing on hot reload.
  - Merge conflict risks when multiple engineers work on UI screens.
- **Remediation Plan:** Complete extraction of screens 0 to 9 into `src/jyotish/ui/modules/` during Phase 2. Ensure each module imports lazily on route selection.

### 2.2 Database Concurrency & SQLite Lock Contention (Severity: HIGH)
- **Current State:** The production database is a single SQLite file (`data/jyotish_enterprise.db`, 14.58 MB) running with standard file locks.
- **Impact:**
  - Under concurrent multi-tenant API traffic, SQLite exhibits write-lock contention (`database is locked` errors).
  - No connection pooling, horizontal read replication, or point-in-time recovery (PITR).
- **Remediation Plan:** Migrate to PostgreSQL 16+ using SQLAlchemy async engine, Alembic database migration scripts, and Redis connection caching.

### 2.3 Python 3.13 Datetime Deprecation Warnings (Severity: LOW)
- **Current State:** Deprecation warnings identified during test runs in `test_past_event_verification.py` and `test_v1_commercial_services.py`:
  `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in Python 3.14+`.
- **Impact:** Code will fail when upgraded to Python 3.14.
- **Remediation Plan:** Replace all instances of `datetime.utcnow()` with `datetime.now(timezone.utc)`.

### 2.4 Synchronous Processing of Heavy Computations (Severity: MEDIUM)
- **Current State:** 50-page PDF report generation (`report_generator.py`) and fine-grained Birth Time Rectification (`btr.py`) run synchronously on FastAPI worker threads.
- **Impact:** HTTP request timeouts, blocked server workers, degraded user experience.
- **Remediation Plan:** Introduce asynchronous task queue (Celery or ARQ backed by Redis) for PDF generation, bulk CSV batch calculations, and BTR searches.

### 2.5 API Response Typing & Serialization Consistency (Severity: MEDIUM)
- **Current State:** Several endpoints in `src/jyotish/api/main.py` return unvalidated dictionaries or JSON strings rather than strongly-typed Pydantic schemas.
- **Impact:** Frontend cannot auto-generate TypeScript clients; runtime type mismatches.
- **Remediation Plan:** Refactor all endpoints into `src/jyotish/api/v1/` routers using strict Pydantic v2 `BaseModel` request and response schemas.

### 2.6 Frontend Dual-Stack Fragmentation (Severity: MEDIUM)
- **Current State:** The repository contains both a Streamlit UI (`src/jyotish/ui/app.py`) and a preliminary vanilla JavaScript frontend (`src/jyotish/ui/web/`).
- **Impact:** Duplicated effort in maintaining two separate presentation implementations.
- **Remediation Plan:**
  - Maintain the Streamlit app as the internal Astrologer Workbench and rapid prototyping tool.
  - Build the production SaaS client using Next.js 14+ (App Router) + TypeScript + Tailwind CSS communicating exclusively via FastAPI REST endpoints.

---

## 3. Technical Debt Remediation Matrix

| Debt Item | Severity | Effort | Phase Scheduled | Target Deliverable |
| :--- | :--- | :--- | :--- | :--- |
| Modularize Screens 0-9 in `app.py` | High | 1-2 Days | Phase 2 | Zero monolithic blocks in `app.py` |
| Migrate SQLite to PostgreSQL + Alembic | High | 2-3 Days | Phase 2 | Production PostgreSQL schema |
| Replace `datetime.utcnow()` with timezone-aware | Low | 0.5 Day | Phase 2 | Zero deprecation warnings in test suite |
| Add Redis & Celery for Heavy Jobs | Medium | 2 Days | Phase 2 | Async task queue for PDF/BTR |
| Enforce Pydantic schemas across all API endpoints | Medium | 2 Days | Phase 3 | OpenAPI 3.1 100% typed documentation |
| Next.js Frontend Enterprise Build | Medium | Phase 11 | Phase 11 | Complete SaaS web application |
