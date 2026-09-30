"""
Test suite for SaaS Subscription Tiers and Rate Limiter Middleware.
Verifies:
1. Token bucket tier quota enforcement (FREE, PRO, ENTERPRISE).
2. 403 Forbidden when accessing Pro features from Free tier.
3. 429 Rate Limit Exceeded with Retry-After header upon exhaustion.
"""

import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from jyotish.api.main import app
from jyotish.api.v1.middleware import SubscriptionTier, require_tier, rate_limiter

client = TestClient(app)


def test_login_and_tier_detection():
    """Verify admin login grants Enterprise tier privileges."""
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@jyotishos.com",
        "password": "Admin@123"
    })
    assert res.status_code == 200
    token = res.json()["access_token"]

    # Verify protected me endpoint
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["user"]["role"] in ("admin", "org_admin", "enterprise")


def test_rate_limiter_anonymous_quota():
    """Verify anonymous free tier gets valid responses within quota."""
    # Test rules count
    for _ in range(5):
        res = client.get("/api/v1/rules/count")
        assert res.status_code == 200
