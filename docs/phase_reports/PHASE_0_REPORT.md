# Phase 0 Completion Report: Security & Repo Hygiene

**Date:** 2026-11-04  
**Status:** COMPLETE (All 7 tasks implemented, verified, and committed)  
**Reference PRD:** `docs/IMPLEMENTATION_PRD.md` (Phase 0)  
**Agent Protocol:** `AGENTS.md` (Section 0.1)  

---

## 1. Executive Summary

Phase 0 successfully addressed all critical repository hygiene, secrets management, authentication security, database persistence, and dependency segregation tasks. The repository is completely untracked of local database and sensitive user data, master license keys are removed from source code, license redemption uses SHA-256 digests, API CORS is strictly origin-gated, authentication endpoints enforce brute-force rate limiting and lockout, password hashing conforms to OWASP standards (600,000 PBKDF2 iterations with Argon2id support), and dependencies are split into production and development manifests with `swisseph` support available.

All 157 automated tests pass with zero regressions.

---

## 2. Completed Tasks & Commit History

| Task ID | Commit | Description | Scope / Verification |
|---------|--------|-------------|----------------------|
| **P0-T1** | `893aef1` | `P0-T1: ignore and untrack data, db, and secret files` | Untracked `data/jyotish_enterprise.db`, `data/users.json`, `data/purchase_codes.json`, `saved_charts_db.json`. Provided `data/*.example.json` templates. Verified `git ls-files data` displays only example templates. |
| **P0-T2** | `06826e6` | `P0-T2: remove hard-coded master licence code and store licence codes hashed` | Removed hard-coded `BH-PRO-2026-MASTER` and `BH-PRO-VIP-VAIDIK` from `src/jyotish/services/auth.py` and UI placeholders. Implemented SHA-256 hashed code verification in `AuthService`. Added `scripts/admin_cli.py` for admin license provisioning. Tests: `tests/test_auth_security.py` (2 passed). |
| **P0-T3** | `d508221` | `P0-T3: provide security rotation and git history purge guide` | Created comprehensive runbook `docs/SECURITY_ROTATION.md` for secret rotation, BFG/git-filter-repo git history purging (owner-executed), and legacy license invalidation. |
| **P0-T4** | `d5f5e21` | `P0-T4: configure strict CORS origins from ALLOWED_ORIGINS env` | Configured FastAPI CORS middleware in `src/jyotish/api/main.py` to read `ALLOWED_ORIGINS` dynamically, defaulting to strict deny. Tests: `tests/test_api_cors_security.py` (2 passed). |
| **P0-T5** | `2a5be47` | `P0-T5: add rate limiting and login attempt lockout` | Added sliding-window rate limiting to `/api/v1/auth/login` (5 req/min) and 5-minute user account lockout after 5 consecutive failed login attempts. Tests: `tests/test_rate_limiting.py` (2 passed). |
| **P0-T6** | `fd9725d` | `P0-T6: enforce >= 600k PBKDF2 iterations and Argon2id support` | Upgraded PBKDF2 iterations to 600,000 in `src/jyotish/services/auth.py` and enabled Argon2id verification. Verified SQLite/PostgreSQL SQLAlchemy models. Tests: `tests/test_database_persistence.py` (3 passed). |
| **P0-T7** | `a3c65fd` | `P0-T7: separate production and dev dependencies and add pyswisseph` | Separated `requirements.txt` (prod) and `requirements-dev.txt` (dev). Removed duplicate `google-generativeai` in favor of official `google-genai`. Added `pysweph`/`pyswisseph`, `tzdata`, `timezonefinder`. Verified `swisseph`, `zoneinfo`, and `timezonefinder` imports. |

---

## 3. Test Suite Verification

Full test suite execution results (`pytest -q`):
```text
================== 157 passed, 1 warning in 78.72s ==================
```

### Specific Phase 0 Test Coverage:
1. `tests/test_auth_security.py` — Confirms no master license bypass exists in source and code hashing behaves cryptographically.
2. `tests/test_api_cors_security.py` — Confirms unauthorized origins receive no `Access-Control-Allow-Origin` headers.
3. `tests/test_rate_limiting.py` — Confirms HTTP 429 Too Many Requests upon rapid calls and lockout on 5 consecutive bad passwords.
4. `tests/test_database_persistence.py` — Confirms multi-user database persistence across reboots.

---

## 4. Phase Gate Checklist (PRD Section 4: Phase 0 Gate)

- [x] **CI Green**: All existing golden benchmarks (SAV=337, planet longitude tolerance < 0.0001 deg) and new security tests pass.
- [x] **No secrets in tree**: No `.db`, live `users.json`, or production license codes tracked in Git index.
- [x] **Master license removed**: No backdoor license codes in source code.
- [x] **Dependencies cleanly segregated**: Production dependencies exclude testing tools; Python Swiss Ephemeris bindings (`swisseph`) installed and functional.

---

## 5. Known Gaps & Handoff to Phase 1

- Ephemeris calculations currently use PyEphem as default fallback; Phase 1 will make Swiss Ephemeris (`pyswisseph`/`pysweph`) mandatory and replace silent fallbacks with explicit degradation signaling (`engine_degraded=true`).
- Historical Indian Daylight Saving Time (1941–1945 war time) and IANA timezone resolution (`src/jyotish/timeloc/`) will be implemented in Phase 1.
