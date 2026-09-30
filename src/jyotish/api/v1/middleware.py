"""
SaaS Subscription Tiers & In-Memory / Redis Token-Bucket Rate Limiter.
Enforces multi-tier monetization:
- FREE: 15 requests / minute, Basic Charts & Panchang.
- PRO: 60 requests / minute, 6-Pillar Retrospective Event Verification & Vargas.
- ENTERPRISE: 300 requests / minute, Full API, BTR, Unlimited Clients.
"""

import time
from enum import Enum
from typing import Dict, Tuple, Optional
from fastapi import HTTPException, Header, Depends
import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET", "jyotish-saas-enterprise-secret-key-2026")
JWT_ALGORITHM = "HS256"


class SubscriptionTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


TIER_RATE_LIMITS = {
    SubscriptionTier.FREE: 15,          # 15 requests / min
    SubscriptionTier.PRO: 60,           # 60 requests / min
    SubscriptionTier.ENTERPRISE: 300    # 300 requests / min
}

# In-memory token bucket tracking: client_id -> (tokens, last_refreshed_timestamp)
_buckets: Dict[str, Tuple[float, float]] = {}


def get_current_user_tier(authorization: Optional[str] = Header(None)) -> Tuple[str, SubscriptionTier]:
    """Extracts client identity and tier from Bearer token, or defaults to Anonymous Free."""
    if not authorization or not authorization.startswith("Bearer "):
        return "anonymous_client", SubscriptionTier.FREE

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        role = payload.get("role", "astrologer").lower()
        sub = payload.get("sub", "user")

        if "admin" in role or "enterprise" in role:
            return sub, SubscriptionTier.ENTERPRISE
        elif "pro" in role or "astrologer" in role:
            return sub, SubscriptionTier.PRO
        return sub, SubscriptionTier.FREE
    except Exception:
        return "anonymous_client", SubscriptionTier.FREE


def rate_limiter(client_info: Tuple[str, SubscriptionTier] = Depends(get_current_user_tier)):
    """Token bucket rate limiter enforcing requests-per-minute quotas per tier."""
    client_id, tier = client_info
    limit_per_min = TIER_RATE_LIMITS.get(tier, 15)
    capacity = float(limit_per_min)
    refill_rate = capacity / 60.0  # tokens per second

    now = time.time()

    if client_id not in _buckets:
        _buckets[client_id] = (capacity - 1.0, now)
        return True

    current_tokens, last_time = _buckets[client_id]
    elapsed = now - last_time
    refreshed_tokens = min(capacity, current_tokens + (elapsed * refill_rate))

    if refreshed_tokens < 1.0:
        retry_after = int((1.0 - refreshed_tokens) / refill_rate) + 1
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {tier.value} tier ({limit_per_min} req/min). Try again in {retry_after}s.",
            headers={"Retry-After": str(retry_after)}
        )

    _buckets[client_id] = (refreshed_tokens - 1.0, now)
    return True


def require_tier(min_tier: SubscriptionTier):
    """Enforces minimum subscription tier requirement on endpoints."""
    def dependency(client_info: Tuple[str, SubscriptionTier] = Depends(get_current_user_tier)):
        client_id, tier = client_info
        TIER_HIERARCHY = {
            SubscriptionTier.FREE: 1,
            SubscriptionTier.PRO: 2,
            SubscriptionTier.ENTERPRISE: 3
        }
        if TIER_HIERARCHY.get(tier, 1) < TIER_HIERARCHY.get(min_tier, 1):
            raise HTTPException(
                status_code=403,
                detail=f"Feature requires '{min_tier.value.upper()}' subscription tier. Current tier: '{tier.value.upper()}'."
            )
        return tier
    return dependency
