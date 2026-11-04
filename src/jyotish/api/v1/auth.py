"""
Enterprise Authentication & JWT Bearer Token Management for /api/v1.
Verifies Argon2id password hashes and issues secure JWT tokens.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from ...db.session import SessionLocal
from ...db.models import User
from .middleware import rate_limiter
import time

# Brute-force Login Lockout Tracking (P0-T5)
_failed_login_attempts: Dict[str, Any] = {}
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SEC = 300.0  # 5 minutes


def check_login_lockout(email: str) -> None:
    now = time.time()
    attempts = _failed_login_attempts.get(email, [])
    valid_attempts = [t for t in attempts if now - t < LOCKOUT_DURATION_SEC]
    _failed_login_attempts[email] = valid_attempts
    if len(valid_attempts) >= MAX_FAILED_ATTEMPTS:
        retry_after = max(1, int(LOCKOUT_DURATION_SEC - (now - valid_attempts[0])))
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed login attempts. Account temporarily locked for security. Try again in {retry_after}s.",
            headers={"Retry-After": str(retry_after)}
        )


def record_failed_login(email: str) -> None:
    now = time.time()
    attempts = _failed_login_attempts.get(email, [])
    attempts.append(now)
    _failed_login_attempts[email] = attempts


def clear_failed_login(email: str) -> None:
    if email in _failed_login_attempts:
        del _failed_login_attempts[email]

router = APIRouter(prefix="/auth", tags=["v1-auth"])

JWT_SECRET = os.getenv("JWT_SECRET", "jyotish-saas-enterprise-secret-key-2026")
JWT_ALGORITHM = "HS256"
ph = PasswordHasher()


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


@router.post("/login", response_model=LoginResponse, dependencies=[Depends(rate_limiter)])
def login(payload: LoginRequest):
    """Authenticates user credentials using Argon2id with lockout defense and emits JWT access token."""
    email_clean = payload.email.strip().lower()
    check_login_lockout(email_clean)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email_clean).first()
        if not user:
            record_failed_login(email_clean)
            raise HTTPException(status_code=401, detail="Invalid email or password")

        try:
            ph.verify(user.password_hash, payload.password)
        except (VerifyMismatchError, Exception):
            record_failed_login(email_clean)
            raise HTTPException(status_code=401, detail="Invalid email or password")

        clear_failed_login(email_clean)

        exp_time = datetime.now(timezone.utc) + timedelta(days=7)
        token_payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "exp": exp_time
        }
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        )
    finally:
        db.close()


@router.get("/me")
def get_current_user_profile(authorization: Optional[str] = Header(None)):
    """Validates JWT bearer token and returns current authenticated user profile."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Bearer token")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == payload.get("sub")).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "status": "authenticated",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }
    finally:
        db.close()
