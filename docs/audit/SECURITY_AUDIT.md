# BHARAT JYOTISH AI — SECURITY & PRIVACY AUDIT
## Security, Data Privacy & Compliance Audit Report (PRD Phase 1)
**Date:** November 2026  
**Auditor:** Principal Security Engineer & Compliance Lead  
**Scope:** Whole Application & Data Stores

---

## 1. Executive Summary

This security audit assesses the Bharat Jyotish AI codebase against industry security standards (OWASP Top 10, GDPR/DPDP personal data protection, and enterprise SaaS multi-tenancy requirements).

Security Health Score: **86 / 100** (Strong multi-tenant isolation and password hashing; requires field-level encryption for birth records and strict JWT expiry).

---

## 2. Security Domain Findings

### 2.1 Authentication & Password Security
- **Status:** **PASS (Grade A-)**
- **Findings:**
  - Passwords are encrypted using salted PBKDF2-HMAC-SHA256 (`src/jyotish/services/auth.py`). Plaintext passwords are never stored.
  - Verification test `test_database_persistence.py::test_user_authentication_security` confirms invalid passwords reject with HTTP 401.
  - JWT tokens are signed using `HS256` with configurable `SECRET_KEY`.
- **Recommendation:** Enforce argon2id password hashing in production for enhanced resistance to GPU brute-forcing. Implement automated token refresh rotation with strict 15-minute access token lifespan.

### 2.2 Multi-Tenant Vault Isolation
- **Status:** **PASS (Grade A)**
- **Findings:**
  - Multi-tenant client isolation is enforced at the database query level via `organization_id` foreign key checks.
  - Verification test `tests/test_vault_isolation.py::test_multi_tenant_chart_isolation` asserts that Organization B cannot view, query, or delete charts belonging to Organization A.
  - 33 immutable audit records exist in the `audit_logs` table tracking sensitive resource mutations with IP address and timestamp.
- **Recommendation:** Implement PostgreSQL Row-Level Security (RLS) policies when migrating from SQLite to provide database-enforced isolation defense-in-depth.

### 2.3 Data Protection & Privacy of Birth Records (PII)
- **Status:** **NEEDS IMPROVEMENT (Grade B-)**
- **Findings:**
  - Birth data (full name, date of birth, exact time, latitude/longitude, city) is currently stored as unencrypted relational columns in `birth_profiles`.
  - Birth data constitutes sensitive biometric and astrological personal identifying information (PII).
- **Recommendation:**
  - Implement field-level AES-256-GCM encryption for `birth_date`, `birth_time`, `latitude`, and `longitude` in the database.
  - Provide automated GDPR/DPDP "Right to Erasure" and complete chart data export endpoints (`/api/v1/user/export-data` and `/api/v1/user/delete-account`).

### 2.4 Secrets & API Key Management
- **Status:** **PASS (Grade A)**
- **Findings:**
  - No active API keys or secrets are hardcoded in git tracked files.
  - `.env.example` provides clean template keys (`OPENAI_API_KEY`, `GEMINI_API_KEY`, `SECRET_KEY`, `DATABASE_URL`).
  - `.gitignore` properly includes `.env`, `*.db`, and sensitive logs.
- **Recommendation:** Add pre-commit hooks (e.g. `detect-secrets`) to prevent inadvertent committing of production credentials.

### 2.5 API Rate Limiting & Denial-of-Service Defense
- **Status:** **PASS (Grade B+)**
- **Findings:**
  - Tier-based rate limiter middleware exists in `src/jyotish/api/v1/middleware.py`.
  - Anonymous users are throttled to 5 calculations per day; Enterprise accounts receive unlimited quota.
  - Verified in `tests/test_saas_tiers.py::test_rate_limiter_anonymous_quota`.
- **Recommendation:** Migrate in-memory rate limiting state to a distributed Redis Sliding-Window token bucket for clustered API deployments.

---

## 3. Security Hardening Checklist for Production

- [ ] Transition from SQLite to PostgreSQL with Row-Level Security (RLS).
- [ ] Add AES-256 field encryption for birth profiles (`full_name`, `birth_date`, `birth_time`, `lat`, `lon`).
- [ ] Implement Redis-backed distributed token bucket rate limiter.
- [ ] Configure HTTPS/TLS 1.3 termination and HSTS security headers.
- [ ] Set up automated database encryption-at-rest and daily encrypted backups.
- [ ] Implement automated user account deletion and data export endpoints (GDPR/DPDP compliance).

