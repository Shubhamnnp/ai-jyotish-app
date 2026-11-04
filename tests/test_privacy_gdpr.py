"""
Unit tests for Data Privacy, At-Rest Encryption, and GDPR/DPDP Endpoints (Phase 6, Task P6-T7).
Reference: docs/IMPLEMENTATION_PRD.md (Section 6.7, P6-T7).
"""

import pytest
from fastapi.testclient import TestClient
from src.jyotish.api.main import app
from src.jyotish.security.crypto import DataPrivacyCrypto, default_crypto, ENCRYPTION_PREFIX
from src.jyotish.services.folder_manager import default_folder_manager


@pytest.fixture
def client():
    return TestClient(app)


def test_crypto_roundtrip_and_idempotency():
    crypto = DataPrivacyCrypto(secret_key="unit-test-secure-privacy-key")
    plaintext = "Yudhisthira Maharaj"

    # 1. Encrypt
    enc = crypto.encrypt(plaintext)
    assert enc.startswith(ENCRYPTION_PREFIX)
    assert enc != plaintext

    # 2. Decrypt
    dec = crypto.decrypt(enc)
    assert dec == plaintext

    # 3. Idempotent encryption: re-encrypting should not double-wrap
    assert crypto.encrypt(enc) == enc

    # 4. Decrypting plaintext passes through safely
    assert crypto.decrypt(plaintext) == plaintext


def test_crypto_birth_data_dict_encryption():
    bd = {
        "name": "Karna",
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "city": "Anga Desh",
        "phone": "+919876500000",
        "latitude": 25.3176,
        "longitude": 82.9739
    }

    enc_bd = default_crypto.encrypt_birth_data(bd)
    assert enc_bd["name"].startswith(ENCRYPTION_PREFIX)
    assert enc_bd["city"].startswith(ENCRYPTION_PREFIX)
    assert enc_bd["phone"].startswith(ENCRYPTION_PREFIX)
    # Non-sensitive / numeric remain unmodified
    assert enc_bd["birth_date"] == "1990-05-15"
    assert enc_bd["latitude"] == 25.3176

    # Decrypt back
    dec_bd = default_crypto.decrypt_birth_data(enc_bd)
    assert dec_bd["name"] == "Karna"
    assert dec_bd["city"] == "Anga Desh"
    assert dec_bd["phone"] == "+919876500000"


def test_privacy_encrypt_decrypt_endpoints(client):
    payload = {
        "data": {
            "name": "Bhimsen",
            "city": "Hastinapur",
            "ayanamsa": "Lahiri"
        }
    }

    # 1. POST /api/v1/privacy/encrypt
    res_enc = client.post("/api/v1/privacy/encrypt", json=payload)
    assert res_enc.status_code == 200
    enc_data = res_enc.json()["data"]
    assert enc_data["name"].startswith(ENCRYPTION_PREFIX)

    # 2. POST /api/v1/privacy/decrypt
    res_dec = client.post("/api/v1/privacy/decrypt", json={"data": enc_data})
    assert res_dec.status_code == 200
    dec_data = res_dec.json()["data"]
    assert dec_data["name"] == "Bhimsen"
    assert dec_data["city"] == "Hastinapur"


def test_delete_user_data_right_to_be_forgotten(client):
    test_user = "pandava_test@jyotish.local"

    # Setup a folder & chart for test user
    default_folder_manager.create_folder("Secret Vault", parent_id=0, owner_email=test_user)
    default_folder_manager.save_chart(
        folder_id=1,
        chart_name="Arjuna Test Chart",
        birth_data={"name": "Arjuna"},
        owner_email=test_user
    )

    # 1. Unconfirmed request rejected
    res_err = client.post("/api/v1/privacy/delete-user-data", json={"owner_email": test_user, "confirm": False})
    assert res_err.status_code == 400

    # 2. Public demo data deletion rejected
    res_sys = client.post("/api/v1/privacy/delete-user-data", json={"owner_email": "public", "confirm": True})
    assert res_sys.status_code == 400

    # 3. Valid confirmed deletion
    res_ok = client.post("/api/v1/privacy/delete-user-data", json={"owner_email": test_user, "confirm": True})
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["status"] == "erased"
    assert data["owner_email"] == test_user
    assert data["audit_id"].startswith("del_")
    assert "timestamp" in data


def test_export_user_data_portability(client):
    test_user = "export_user@jyotish.local"
    default_folder_manager.create_folder("Portfolio Folder", parent_id=0, owner_email=test_user)

    res = client.get(f"/api/v1/privacy/export-user-data?owner_email={test_user}")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "exported_data" in data
    assert data["exported_data"]["owner_email"] == test_user
    assert len(data["exported_data"]["folders"]) >= 1

