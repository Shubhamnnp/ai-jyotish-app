"""
Integration tests for Commercial Services in JyotishOS API v1:
- Billing & Webhooks (Stripe / Razorpay role upgrade, audit logging)
- 50+ Page Master Dossier & Certified Verification Export
- Grounded Astrological Consultation (Chat Advisor)
"""

import pytest
from fastapi.testclient import TestClient
from src.jyotish.api.main import app

client = TestClient(app)


def test_billing_plans_catalog():
    response = client.get("/api/v1/billing/plans")
    assert response.status_code == 200
    data = response.json()
    assert "plans" in data
    assert "pro_monthly" in data["plans"]
    assert "enterprise_monthly" in data["plans"]


def test_billing_checkout_session():
    # Login as admin to get token
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@jyotishos.com",
        "password": "Admin@123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    checkout_res = client.post(
        "/api/v1/billing/checkout",
        json={"plan_id": "enterprise_monthly", "gateway": "razorpay", "currency": "INR"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert checkout_res.status_code == 200
    session_data = checkout_res.json()
    assert session_data["plan_id"] == "enterprise_monthly"
    assert session_data["gateway"] == "razorpay"
    assert "checkout_url" in session_data


def test_billing_webhook_user_role_upgrade():
    # Trigger webhook to upgrade user to enterprise
    webhook_payload = {
        "event": "payment.captured",
        "email": "admin@jyotishos.com",
        "tier": "enterprise",
        "amount": 499900
    }
    wh_res = client.post(
        "/api/v1/billing/webhook",
        json=webhook_payload,
        headers={"x-webhook-token": "jyotish-saas-whsec-2026-production"}
    )
    assert wh_res.status_code == 200
    data = wh_res.json()
    assert data["status"] == "success"
    assert data["new_role"] == "enterprise"

    # Check status with upgraded user
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@jyotishos.com",
        "password": "Admin@123"
    })
    token = login_res.json()["access_token"]
    status_res = client.get("/api/v1/billing/status", headers={"Authorization": f"Bearer {token}"})
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["tier"] == "enterprise"
    assert status_data["rate_limit_per_min"] == 300
    assert status_data["permissions"]["btr_tattwa_rectification"] is True


def test_master_html_report_export():
    # Login as admin / enterprise
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@jyotishos.com",
        "password": "Admin@123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    report_payload = {
        "birth_data": {
            "name": "Arjun Sharma",
            "birth_date": "1995-05-15",
            "birth_time": "14:30:00",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5,
            "city": "New Delhi"
        },
        "astro_name": "ज्योतिषाचार्य पं. शुभम तिवारी",
        "astro_org": "वैदिक ज्योतिष अनुसंधान केंद्र"
    }
    res = client.post(
        "/api/v1/reports/master-html",
        json=report_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "पं. शुभम तिवारी" in res.text
    assert "लग्न कुण्डली" in res.text


def test_event_verification_certificate_export():
    login_res = client.post("/api/v1/auth/login", json={
        "email": "admin@jyotishos.com",
        "password": "Admin@123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    cert_payload = {
        "birth_data": {
            "name": "Meera Patel",
            "birth_date": "1992-08-20",
            "birth_time": "10:15:00",
            "latitude": 23.0225,
            "longitude": 72.5714,
            "timezone_offset": 5.5,
            "city": "Ahmedabad"
        },
        "event_theme": "marriage",
        "query_text": "क्या मेरी शादी वर्ष 2018-2019 में संपन्न हो चुकी है?",
        "event_start_year": 2018,
        "event_end_year": 2019,
        "astro_name": "पं. शुभम तिवारी"
    }
    res = client.post(
        "/api/v1/reports/event-verification-certificate",
        json=cert_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "षट्-स्तंभ सत्यापन रिपोर्ट" in res.text
    assert "Meera Patel" in res.text


def test_chat_astrological_consult():
    consult_payload = {
        "birth_data": {
            "name": "Devendra Kumar",
            "birth_date": "1988-11-12",
            "birth_time": "08:45:00",
            "latitude": 26.8467,
            "longitude": 80.9462,
            "timezone_offset": 5.5,
            "city": "Lucknow"
        },
        "question": "मेरे करियर और पदोन्नति का समय कब अनुकूल होगा?",
        "language": "hi"
    }
    res = client.post("/api/v1/chat/consult", json=consult_payload)
    assert res.status_code == 200
    data = res.json()
    assert "consultation_narrative" in data
    assert "active_dasha" in data
    assert "ethical_disclaimer" in data
    assert len(data["key_planetary_influences"]) > 0
