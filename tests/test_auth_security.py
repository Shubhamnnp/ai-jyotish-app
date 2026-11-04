"""
Unit tests for Authentication Security & Licence Management (P0-T2).

Verifies:
1. No hard-coded "MASTER" licence codes exist in source code.
2. Licence codes are generated with SHA-256 hash storage.
3. Code redemption validates hash matching.
4. Single-use enforcement (cannot be redeemed twice).
"""

import os
import tempfile
import pytest
from src.jyotish.services.auth import AuthService


@pytest.fixture
def auth_test_instance():
    with tempfile.TemporaryDirectory() as tmp_dir:
        service = AuthService(data_dir=tmp_dir)
        yield service


def test_no_hardcoded_master_code_in_source():
    """Acceptance criterion for P0-T2: No hard-coded MASTER licence code in src/."""
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
    found_matches = []
    
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith(".py"):
                file_path = os.path.join(root, f)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                    for line_num, line in enumerate(fp, 1):
                        if "BH-PRO-2026-MASTER" in line or "MASTER_CODE" in line or '"MASTER"' in line:
                            found_matches.append(f"{file_path}:{line_num}: {line.strip()}")
                            
    assert len(found_matches) == 0, f"Found hard-coded MASTER licence code: {found_matches}"


def test_licence_code_hash_generation_and_redemption(auth_test_instance):
    """Verify purchase codes are generated with hash and redeemed properly."""
    service = auth_test_instance
    
    # 1. Register a test user
    success, msg, user_dict = service.register(
        email="client@example.com",
        password="Password@123",
        name="Test Client"
    )
    assert success is True

    # 2. Generate a purchase code via service
    code = service.generate_purchase_code(
        created_by_email="admin@jyotishos.com",
        tier="pro_annual",
        notes="Security unit test license"
    )
    assert code.startswith("BH-PRO-")

    # 3. Verify code has code_hash in storage
    codes = service._load_codes()
    assert len(codes) >= 1
    target = next((c for c in codes if c.get("code") == code), None)
    assert target is not None
    assert "code_hash" in target
    assert len(target["code_hash"]) == 64  # SHA-256 hex string

    # 4. Redeem code for user
    redeem_success, redeem_msg = service.redeem_purchase_code(
        email="client@example.com",
        code_str=code
    )
    assert redeem_success is True

    # User role should now be upgraded
    users = service._load_users()
    user = users.get("client@example.com")
    assert user is not None
    assert user["is_paid"] is True
    assert user["role"] == "jyotishi"

    # 5. Single-use enforcement: Attempting to redeem again must fail
    second_redeem, second_msg = service.redeem_purchase_code(
        email="another@example.com",
        code_str=code
    )
    assert second_redeem is False
    assert "पहले ही उपयोग" in second_msg or "already" in second_msg.lower()
