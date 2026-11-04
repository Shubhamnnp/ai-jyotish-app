"""
Structured Observability, Tracing, and PII-Scrubbing Middleware (Phase 6, Task P6-T5).
Reference: docs/IMPLEMENTATION_PRD.md (Section 6.5, P6-T5).

Rules:
1. Every request receives or propagates an X-Request-ID.
2. Latency is measured and returned in X-Process-Time.
3. Structured JSON logging is emitted for requests.
4. Strict PII scrubbing: zero astrological client names, birth details, emails, or tokens logged in plaintext.
"""

import time
import uuid
import json
import logging
from typing import Dict, Any, Set
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Configure structured JSON logger
logger = logging.getLogger("jyotish.api.access")
logger.setLevel(logging.INFO)

SENSITIVE_KEYS: Set[str] = {
    "name", "birth_name", "first_name", "last_name",
    "password", "secret", "token", "authorization",
    "email", "phone", "mobile", "birth_date", "birth_time"
}


def scrub_pii(data: Any) -> Any:
    """Recursively redacts sensitive PII fields from payloads or dictionaries."""
    if isinstance(data, dict):
        scrubbed = {}
        for k, v in data.items():
            if str(k).lower() in SENSITIVE_KEYS:
                scrubbed[k] = "[REDACTED_PII]"
            elif isinstance(v, (dict, list)):
                scrubbed[k] = scrub_pii(v)
            else:
                scrubbed[k] = v
        return scrubbed
    elif isinstance(data, list):
        return [scrub_pii(item) for item in data]
    return data


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette Middleware that attaches correlation IDs,
    measures execution duration, and writes PII-scrubbed structured logs.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. Propagate or generate X-Request-ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex[:16]}"
        request.state.request_id = request_id

        # 2. Timing
        start_time = time.perf_counter()

        # 3. Call downstream route handler
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_record = {
                "event": "http_request_error",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
                "error": str(exc)
            }
            logger.error(json.dumps(log_record))
            raise exc

        # 4. Measure duration and populate response headers
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration_ms}ms"

        # 5. Emit structured JSON log
        log_record = {
            "event": "http_request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else "unknown"
        }
        logger.info(json.dumps(log_record))

        return response

