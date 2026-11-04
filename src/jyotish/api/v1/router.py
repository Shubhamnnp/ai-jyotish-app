"""
Master Router for API v1 Gateway.
Aggregates authentication, charts, events, and rules sub-routers.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .charts import router as charts_router
from .events import router as events_router
from .rules import router as rules_router
from .billing import router as billing_router
from .reports import router as reports_router
from .chat import router as chat_router
from .astronomy import router as astronomy_router
from .evidence import router as evidence_router
from .health import router as health_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(charts_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(rules_router)
api_v1_router.include_router(billing_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(chat_router)
api_v1_router.include_router(astronomy_router)
api_v1_router.include_router(evidence_router)
api_v1_router.include_router(health_router)

