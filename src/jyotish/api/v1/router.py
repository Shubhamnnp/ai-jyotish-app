"""
Master Router for API v1 Gateway.
Aggregates authentication, charts, events, and rules sub-routers.
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .charts import router as charts_router
from .events import router as events_router
from .rules import router as rules_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(charts_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(rules_router)
