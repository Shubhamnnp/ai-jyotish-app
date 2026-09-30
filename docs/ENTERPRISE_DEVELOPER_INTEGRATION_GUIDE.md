# Bharat Jyotish AI SaaS — Enterprise Developer & Partner Integration Guide

Welcome to the **Bharat Jyotish AI SaaS Enterprise API Gateway** (`/api/v1`).

This guide details how external partner applications, web clients (React/Next.js), mobile applications (Flutter/React Native), and enterprise platforms integrate with our deterministic calculation engine, 12,578 classical rules database, and retrospective event verification APIs.

---

## 1. Quick Specifications & Base URLs

- **Local Development:** `http://localhost:8000`
- **Interactive OpenAPI UI (Swagger):** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`
- **OpenAPI 3.1 Spec:** [`docs/openapi.json`](./openapi.json)
- **Postman Collection v2.1.0:** [`docs/Bharat_Jyotish_API_v1.postman_collection.json`](./Bharat_Jyotish_API_v1.postman_collection.json)

---

## 2. Authentication & Security (Argon2id + JWT)

All `/api/v1` endpoints require a Bearer token in the `Authorization` header, except public billing catalogs and login.

### Obtain Access Token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@jyotish.com",
    "password": "AdminPassword123!"
  }'
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "tier": "enterprise",
  "expires_in_minutes": 1440
}
```

---

## 3. Tiered Rate Limiting Headers

Every API response returns standard rate-limiting headers:

| Header | Description | Free Tier | Pro Tier | Enterprise Tier |
| :--- | :--- | :--- | :--- | :--- |
| `X-RateLimit-Limit` | Max requests permitted per minute | `15` | `60` | `300` |
| `X-RateLimit-Remaining` | Remaining requests in current window | Integer | Integer | Integer |
| `X-RateLimit-Reset` | Window expiration (seconds) | `60` | `60` | `60` |

When quota is exhausted, the gateway responds with HTTP `429 Too Many Requests`.

---

## 4. Retrospective Past Event Verification (6 Pillars)

Verify historical life occurrences (*e.g., Marriage, Promotion, Childbirth*) with evidentiary confidence and classical citations.

### cURL Example
```bash
curl -X POST "http://localhost:8000/api/v1/events/verify-past" \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "birth_data": {
      "name": "Arjun Sharma",
      "birth_date": "1992-08-14",
      "birth_time": "09:45:00",
      "latitude": 28.6139,
      "longitude": 77.2090,
      "timezone_offset": 5.5
    },
    "target_event_date": "2020-11-25",
    "event_category": "marriage",
    "natural_query_text": "क्या मेरी शादी हो चुकी है?",
    "ayanamsa": "Lahiri"
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "verification_id": 104,
  "confidence_score": 0.88,
  "verdict": "Strongly Supported",
  "is_event_validated": true,
  "synthesis_rationale": "High multi-pillar resonance across Navamsha (D9) and Jupiter-Saturn double transit over 7th Bhava.",
  "six_pillar_breakdown": {
    "pillar_1_natal_promise": {"score": 0.90, "status": "Strongly Supported"},
    "pillar_2_divisional_varga": {"score": 0.85, "status": "Strongly Supported"},
    "pillar_3_dasha_hierarchy": {"score": 0.92, "status": "Strongly Supported"},
    "pillar_4_double_transit": {"score": 0.82, "status": "Supported"},
    "pillar_5_shastriya_rules": {"score": 0.87, "status": "Strongly Supported"},
    "pillar_6_prashna_resonance": {"score": 0.70, "status": "Supported"}
  }
}
```

---

## 5. TypeScript / React Integration Example

```typescript
// hooks/useJyotishVerification.ts
import { useState } from 'react';

interface VerificationResponse {
  confidence_score: number;
  verdict: string;
  is_event_validated: boolean;
  synthesis_rationale: string;
}

export function useJyotishVerification(token: string) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VerificationResponse | null>(null);

  const verifyEvent = async (birthData: any, eventDate: string, category: string) => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/events/verify-past', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          birth_data: birthData,
          target_event_date: eventDate,
          event_category: category,
          ayanamsa: 'Lahiri'
        })
      });
      const data = await res.json();
      setResult(data);
    } finally {
      setLoading(false);
    }
  };

  return { verifyEvent, result, loading };
}
```

---

## 6. Python SDK Integration Example

```python
# sdk_example.py
import httpx

class JyotishClient:
    def __init__(self, base_url: str = "http://localhost:8000", token: str = None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

    def get_rule_count(self) -> int:
        resp = httpx.get(f"{self.base_url}/api/v1/rules/count", headers=self.headers)
        resp.raise_for_status()
        return resp.json()["total_shastriya_rules"]

    def consult_ai(self, query: str, birth_data: dict, language: str = "Hindi") -> str:
        resp = httpx.post(
            f"{self.base_url}/api/v1/chat/consult",
            headers=self.headers,
            json={"query": query, "birth_data": birth_data, "language": language}
        )
        resp.raise_for_status()
        return resp.json()["response"]
```

---

## 7. Webhook Signature Verification (Stripe & Razorpay)

Commercial upgrades automatically verify HMAC signatures to prevent spoofing:

- **Stripe:** Set header `stripe-signature` computed via webhook secret `STRIPE_WEBHOOK_SECRET`.
- **Razorpay:** Set header `X-Razorpay-Signature` computed via webhook secret `RAZORPAY_WEBHOOK_SECRET`.

Successful webhooks automatically upgrade the organization's tier, grant expanded API rate limits, and record cryptographic timestamps in `audit_logs`.
