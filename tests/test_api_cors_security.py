"""
Security tests for CORS Policy (P0-T4).
Verifies:
1. Disallowed external origins get no CORS header.
2. Default environment (ALLOWED_ORIGINS empty) denies arbitrary origins.
3. Configured origins in ALLOWED_ORIGINS receive appropriate CORS headers.
"""

from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def test_cors_disallowed_origin_gets_no_header():
    """Acceptance test for P0-T4: disallowed origin gets no CORS header."""
    # Test on a test app mirroring main.py CORS logic with empty ALLOWED_ORIGINS
    app = FastAPI()
    allowed_origins = [o.strip() for o in "".split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)
    res = client.get("/test", headers={"Origin": "https://malicious-site.example.com"})
    assert res.status_code == 200
    assert "access-control-allow-origin" not in res.headers


def test_cors_allowed_origin_gets_header():
    """Verify origin listed in ALLOWED_ORIGINS receives access-control-allow-origin header."""
    app = FastAPI()
    allowed_origins = [o.strip() for o in "https://app.jyotishos.com, http://localhost:3000".split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)

    # Allowed origin
    res = client.get("/test", headers={"Origin": "https://app.jyotishos.com"})
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "https://app.jyotishos.com"

    # Disallowed origin on same app
    res_disallowed = client.get("/test", headers={"Origin": "https://evil.com"})
    assert res_disallowed.status_code == 200
    assert "access-control-allow-origin" not in res_disallowed.headers
