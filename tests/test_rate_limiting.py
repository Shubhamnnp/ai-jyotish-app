"""
Security & Rate Limiting Tests (P0-T5).
Verifies:
1. HTTP 429 on Token-Bucket rate limit exhaustion.
2. HTTP 429 on 5 consecutive failed login attempts (Brute-force lockout defense).
"""

import pytest
from fastapi.testclient import TestClient
from src.jyotish.api.main import app
from src.jyotish.api.v1.auth import _failed_login_attempts
from src.jyotish.api.v1.middleware import _buckets

client = TestClient(app)


def test_token_bucket_rate_limit_exceeded_429():
    """Verify that exceeding token-bucket limit produces HTTP 429."""
    _buckets.clear()

    # Anonymous tier limit is 15 requests / minute on endpoints with rate_limiter
    # /api/v1/auth/login has rate_limiter enabled
    responses = []
    for i in range(20):
        res = client.post("/api/v1/auth/login", json={
            "email": f"rate-user-{i}@example.com",
            "password": "wrong-password"
        })
        responses.append(res.status_code)

    # At least one request beyond the 15 req/min token capacity must return 429
    assert 429 in responses, f"Expected HTTP 429 in responses, got {responses}"


def test_login_lockout_after_five_failed_attempts_429():
    """Verify that 5 failed login attempts trigger HTTP 429 lockout."""
    # Reset both rate limit bucket and lockout attempts
    _buckets.clear()
    target_email = "lockout-test@example.com"
    _failed_login_attempts[target_email] = []

    # Send 5 incorrect login attempts
    for _ in range(5):
        res = client.post("/api/v1/auth/login", json={
            "email": target_email,
            "password": "WrongPassword!99"
        })
        assert res.status_code == 401

    # The 6th attempt must now be locked out with HTTP 429
    locked_res = client.post("/api/v1/auth/login", json={
        "email": target_email,
        "password": "WrongPassword!99"
    })
    assert locked_res.status_code == 429, f"Expected 429 lockout, got {locked_res.status_code}"
    assert "locked" in locked_res.json()["detail"].lower()
    assert "Retry-After" in locked_res.headers
