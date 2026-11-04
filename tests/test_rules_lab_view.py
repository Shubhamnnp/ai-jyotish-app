"""Unit tests for Rules Lab Admin View and API endpoints (P6-T3)."""

import pytest
from fastapi.testclient import TestClient
from src.jyotish.api.main import app
from src.jyotish.rules.engine import default_rules_engine
from src.jyotish.ui.modules.rules_library_view import render_rules_lab_admin_panel


@pytest.fixture
def client():
    return TestClient(app)


def test_audit_stats_endpoint_security(client):
    # Without header
    res = client.get("/api/v1/rules/audit-stats")
    assert res.status_code == 403

    # With invalid role
    res = client.get("/api/v1/rules/audit-stats", headers={"X-Admin-Role": "guest"})
    assert res.status_code == 403

    # With admin role
    res = client.get("/api/v1/rules/audit-stats", headers={"X-Admin-Role": "admin"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "stats" in data
    assert "scholar_verified" in data["stats"]
    assert "draft" in data["stats"]


def test_draft_rules_endpoint(client):
    # Unauthenticated
    res = client.get("/api/v1/rules/drafts")
    assert res.status_code == 403

    # Scholar role
    res = client.get("/api/v1/rules/drafts?limit=5&offset=0", headers={"X-Admin-Role": "scholar"})
    assert res.status_code == 200
    data = res.json()
    assert "total_drafts" in data
    assert "drafts" in data
    assert len(data["drafts"]) <= 5


def test_review_rule_promote_and_reject(client):
    # Ensure there is a test rule in the engine
    sample_rule = {
        "id": "TEST_LAB_RULE_001",
        "name": "Test Lab Review Yoga",
        "source": {"text": "Brihat Parashara", "chapter": 1, "verse": 1},
        "condition": {"type": "planet_in_house", "planet": "Jupiter", "house": 1},
        "verification": {"status": "draft"}
    }
    default_rules_engine.rules.append(sample_rule)
    default_rules_engine.rules_by_id[sample_rule["id"]] = sample_rule

    # 1. Promote to scholar_verified
    res = client.post(
        "/api/v1/rules/review",
        json={
            "rule_id": "TEST_LAB_RULE_001",
            "new_status": "scholar_verified",
            "scholar_notes": "Verified against BPHS ch 1 v 1"
        },
        headers={"X-Admin-Role": "scholar"}
    )
    assert res.status_code == 200
    assert res.json()["new_status"] == "scholar_verified"
    assert sample_rule["verification"]["status"] == "scholar_verified"
    assert sample_rule["verification"]["notes"] == "Verified against BPHS ch 1 v 1"

    # 2. Reject
    res = client.post(
        "/api/v1/rules/review",
        json={
            "rule_id": "TEST_LAB_RULE_001",
            "new_status": "rejected",
            "scholar_notes": "Spurious formula"
        },
        headers={"X-Admin-Role": "admin"}
    )
    assert res.status_code == 200
    assert res.json()["new_status"] == "rejected"
    assert sample_rule["verification"]["status"] == "rejected"

    # Clean up test rule
    default_rules_engine.rules.remove(sample_rule)
    default_rules_engine.rules_by_id.pop(sample_rule["id"], None)


def test_rules_lab_admin_panel_mock(monkeypatch):
    """Verifies that render_rules_lab_admin_panel executes safely with streamlit mocked."""
    import streamlit as st

    # Simulate session state
    session_store = {"admin_authenticated": True}
    monkeypatch.setattr(st, "session_state", session_store)

    sample_rules = [
        {
            "id": "R_SAMPLE_001",
            "name": "Sample Verified Yoga",
            "source": {"text": "BPHS", "chapter": 2, "verse": 5},
            "verification": {"status": "scholar_verified"}
        },
        {
            "id": "R_SAMPLE_002",
            "name": "Sample Draft Rule",
            "source": {"text": "Jataka Parijata", "chapter": 4, "verse": 10},
            "verification": {"status": "draft"}
        }
    ]

    # Should run without error
    render_rules_lab_admin_panel(all_rules=sample_rules)

