"""
Integration tests for Bharat Jyotish AI SaaS API v1 Gateway.
Tests:
- /api/v1/auth/login with Argon2id verification and JWT token receipt
- /api/v1/auth/me with Bearer token
- /api/v1/charts/calculate
- /api/v1/events/verify-past
- /api/v1/rules/count and /api/v1/rules/search
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.api.main import app

client = TestClient(app)


def test_v1_auth_login_and_me():
    """Test login with admin credentials, JWT token emission, and me profile."""
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@jyotishos.com",
        "password": "Admin@123"
    })
    assert res.status_code == 200, f"Login failed: {res.text}"
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "admin@jyotishos.com"

    token = data["access_token"]

    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["status"] == "authenticated"
    assert me_data["user"]["email"] == "admin@jyotishos.com"


def test_v1_charts_calculate():
    """Test full chart calculation through /api/v1/charts/calculate."""
    payload = {
        "name": "API Test Native",
        "birth_date": "1990-05-15",
        "birth_time": "14:30:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5,
        "city": "New Delhi",
        "confidence": "Exact"
    }
    res = client.post("/api/v1/charts/calculate", json=payload)
    assert res.status_code == 200, f"Chart calculation failed: {res.text}"
    chart = res.json()
    assert "lagna_sign_id" in chart
    assert "planets" in chart
    assert "Sun" in chart["planets"]
    assert "vargas" in chart
    assert "D9" in chart["vargas"]


def test_v1_events_verify_past():
    """Test retrospective past event verification through /api/v1/events/verify-past."""
    payload = {
        "birth_data": {
            "name": "Historical Native",
            "birth_date": "1980-01-01",
            "birth_time": "12:00:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5,
            "city": "New Delhi",
            "confidence": "Exact"
        },
        "event_theme": "marriage",
        "query_text": "क्या मेरी शादी हो चुकी है?",
        "target_date": "2010-06-15"
    }
    res = client.post("/api/v1/events/verify-past", json=payload)
    assert res.status_code == 200, f"Event verification failed: {res.text}"
    data = res.json()
    assert data["event_theme"] == "marriage"
    assert "status" in data
    assert "confidence_score" in data
    assert "pillar_1_d1_evidence" in data
    assert "pillar_4_dasha_evidence" in data
    assert "ai_explanation_hi" in data


def test_v1_rules_count_and_search():
    """Test Shastriya rules count and fast indexed search through /api/v1/rules."""
    count_res = client.get("/api/v1/rules/count")
    assert count_res.status_code == 200
    count_data = count_res.json()
    assert count_data["total_rules"] >= 12500
    assert count_data["indexed_rules"] >= 12500

    search_res = client.get("/api/v1/rules/search?planet=Jupiter&theme=career&limit=10")
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert "rules" in search_data
    assert search_data["matched_count"] > 0


def test_v1_charts_multi_dashas():
    """Test 4-system multi-dasha calculation endpoint."""
    payload = {
        "birth_data": {
            "name": "Dasha Native",
            "birth_date": "1995-05-15",
            "birth_time": "14:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        },
        "target_date": "2026-09-30",
        "ayanamsa": "Lahiri"
    }
    res = client.post("/api/v1/charts/dashas", json=payload)
    assert res.status_code == 200, f"Multi-dasha failed: {res.text}"
    data = res.json()
    assert "vimshottari" in data
    assert "yogini" in data
    assert "ashtottari" in data
    assert "chara" in data
    assert data["vimshottari"]["summary"] is not None
    assert data["yogini"]["yogini"] is not None


def test_v1_charts_shadbala():
    """Test Shadbala calculation endpoint."""
    payload = {
        "name": "Shadbala Native",
        "birth_date": "1990-01-01",
        "birth_time": "12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone_offset": 5.5
    }
    res = client.post("/api/v1/charts/shadbala", json=payload)
    assert res.status_code == 200, f"Shadbala failed: {res.text}"
    data = res.json()
    assert "planets" in data
    assert "Sun" in data["planets"]
    assert "bhava_bala" in data


def test_v1_charts_milan():
    """Test 36-guna Kundali Milan compatibility endpoint."""
    payload = {
        "groom": {
            "name": "Groom",
            "birth_date": "1992-04-10",
            "birth_time": "08:15:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        },
        "bride": {
            "name": "Bride",
            "birth_date": "1995-08-22",
            "birth_time": "16:45:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5
        }
    }
    res = client.post("/api/v1/charts/milan", json=payload)
    assert res.status_code == 200, f"Milan failed: {res.text}"
    data = res.json()
    assert "total_score" in data
    assert "varna" in data
    assert "nadi" in data
    assert "verdict" in data
