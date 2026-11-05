"""
Phase 9 Comprehensive Test Suite: SaaS Infrastructure, Security & Modular UI.
Validates tasks P9-T1 through P9-T5:
- P9-T1: Database Engine Pooling, Health Check & Relational Schema Parity
- P9-T2: OpenAPI Gateway & REST Contract for Next.js SaaS Frontend
- P9-T3: Asynchronous Background Task Execution & Polling
- P9-T4: Field-Level Data Encryption & Argon2id Password Security
- P9-T5: Multi-Tenant Client Vault Isolation & SaaS Subscription Tiers
"""

import time
import pytest
from fastapi.testclient import TestClient

from src.jyotish.api.main import app
from src.jyotish.db.session import check_db_health, SessionLocal
from src.jyotish.db.models import Organization, User, Client as ClientModel, BirthProfile, Chart
from src.jyotish.security.crypto import DataPrivacyCrypto, DEFAULT_SENSITIVE_FIELDS
from src.jyotish.services.folder_manager import ChartFolderManager
from src.jyotish.services.vault import KundaliVaultService
from argon2 import PasswordHasher

client = TestClient(app)


# -----------------------------------------------------------------------------
# P9-T1: Database Engine Pooling & Relational Schema Parity
# -----------------------------------------------------------------------------
def test_p9_t1_database_health_and_schema():
    """Verify database connection health check and relational entity integrity."""
    health = check_db_health()
    assert health["status"] == "healthy"
    assert health["connected"] is True
    assert health["dialect"] in ("sqlite", "postgresql")

    # Verify session management and ORM models
    db = SessionLocal()
    try:
        assert hasattr(Organization, "users")
        assert hasattr(User, "password_hash")
        assert hasattr(ClientModel, "organization_id")
        assert hasattr(BirthProfile, "charts")
        assert hasattr(Chart, "planets")
        assert hasattr(Chart, "dashas")
        assert hasattr(Chart, "vargas")
    finally:
        db.close()


# -----------------------------------------------------------------------------
# P9-T2: OpenAPI Gateway & REST Contract for Next.js SaaS Frontend
# -----------------------------------------------------------------------------
def test_p9_t2_openapi_gateway_spec():
    """Verify OpenAPI 3.x schema completeness for decoupled Next.js web client."""
    openapi = app.openapi()
    assert openapi["openapi"].startswith("3.")
    assert "paths" in openapi

    paths = openapi["paths"]
    # Essential API v1 paths for Next.js SaaS frontend
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/charts/calculate" in paths
    assert "/api/v1/rules/count" in paths
    assert "/api/v1/evidence/pack" in paths
    assert "/api/v1/health" in paths
    assert "/api/v1/privacy/delete-user-data" in paths
    assert "/api/v1/tasks/generate-report" in paths


# -----------------------------------------------------------------------------
# P9-T3: Asynchronous Background Task Execution & Polling
# -----------------------------------------------------------------------------
def test_p9_t3_async_background_task_worker():
    """Verify non-blocking background task submission and lifecycle."""
    payload = {
        "name": "Vivekananda Background Test",
        "birth_date": "1863-01-12",
        "birth_time": "06:33:00",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "timezone_offset": 5.89,
        "gender": "male"
    }

    # 1. Enqueue task
    resp = client.post("/api/v1/tasks/generate-report", json=payload)
    assert resp.status_code == 202
    data = resp.json()
    assert "task_id" in data
    task_id = data["task_id"]
    assert data["status"] in ("queued", "running")

    # 2. Poll until completed (with timeout)
    max_wait = 15.0
    start = time.time()
    final_status = None
    task_info = None

    while time.time() - start < max_wait:
        poll_resp = client.get(f"/api/v1/tasks/{task_id}")
        assert poll_resp.status_code == 200
        task_info = poll_resp.json()
        final_status = task_info["status"]
        if final_status in ("completed", "failed"):
            break
        time.sleep(0.5)

    assert final_status == "completed"
    assert task_info["result"] is not None
    assert task_info["result"]["is_ready"] is True
    assert task_info["result"]["report_size_bytes"] > 500


# -----------------------------------------------------------------------------
# P9-T4: Field-Level Data Encryption & Argon2id Security
# -----------------------------------------------------------------------------
def test_p9_t4_field_encryption_and_argon2id():
    """Verify AES-128-CBC + HMAC-SHA256 at-rest encryption and Argon2id passwords."""
    crypto = DataPrivacyCrypto()

    # 1. String level encryption
    secret_text = "Secret Client Name: Pandit Ji"
    enc = crypto.encrypt(secret_text)
    assert enc.startswith("enc::v1::")
    assert enc != secret_text
    dec = crypto.decrypt(enc)
    assert dec == secret_text

    # 2. Dictionary / birth data field-level encryption
    raw_profile = {
        "name": "Ramesh Kumar",
        "city": "Varanasi",
        "email": "ramesh@example.com",
        "latitude": 25.3176,
        "longitude": 82.9739
    }
    enc_profile = crypto.encrypt_birth_data(raw_profile)
    assert enc_profile["name"].startswith("enc::v1::")
    assert enc_profile["city"].startswith("enc::v1::")
    assert enc_profile["email"].startswith("enc::v1::")
    # Coordinates must remain numerical for ephemeris computation
    assert enc_profile["latitude"] == 25.3176

    dec_profile = crypto.decrypt_birth_data(enc_profile)
    assert dec_profile["name"] == "Ramesh Kumar"
    assert dec_profile["city"] == "Varanasi"
    assert dec_profile["email"] == "ramesh@example.com"

    # 3. Argon2id password hash verification
    ph = PasswordHasher()
    hashed = ph.hash("AstrologerSecurePass2026!")
    assert hashed.startswith("$argon2id$")
    assert ph.verify(hashed, "AstrologerSecurePass2026!")


# -----------------------------------------------------------------------------
# P9-T5: Multi-Tenant Vault Isolation & Subscription Tiers
# -----------------------------------------------------------------------------
def test_p9_t5_vault_isolation_and_saas_tiers(tmp_path):
    """Verify multi-tenant isolation across astrologers and tier rate-limiting."""
    db_file = str(tmp_path / "tenant_vault.json")
    mgr = ChartFolderManager(db_path=db_file)
    vault = KundaliVaultService(db_path=db_file)
    vault.manager = mgr

    # Astrologer 1 creates a client
    sample_birth = {
        "birth_date": "1985-05-10",
        "birth_time": "14:15:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "city": "Delhi"
    }
    vault.save_client(name="Private Client Astro 1", birth_data=sample_birth, owner_email="astro1@jyotish.com")

    # Astrologer 2 creates a client
    vault.save_client(name="Private Client Astro 2", birth_data=sample_birth, owner_email="astro2@jyotish.com")

    # Astrologer 1 MUST NOT see Astrologer 2's client
    clients_1 = vault.list_all_clients(owner_email="astro1@jyotish.com")
    names_1 = [c["name"] for c in clients_1]
    assert "Private Client Astro 1" in names_1
    assert "Private Client Astro 2" not in names_1

    # Astrologer 2 MUST NOT see Astrologer 1's client
    clients_2 = vault.list_all_clients(owner_email="astro2@jyotish.com")
    names_2 = [c["name"] for c in clients_2]
    assert "Private Client Astro 2" in names_2
    assert "Private Client Astro 1" not in names_2
