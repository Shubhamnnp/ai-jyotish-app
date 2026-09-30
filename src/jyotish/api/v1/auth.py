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


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    """Authenticates user credentials using Argon2id and emits JWT access token."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == payload.email.strip().lower()).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        try:
            ph.verify(user.password_hash, payload.password)
        except (VerifyMismatchError, Exception):
            raise HTTPException(status_code=401, detail="Invalid email or password")

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
