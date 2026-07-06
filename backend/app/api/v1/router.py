"""API v1 router aggregation."""

from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.chat import router as chat_router
from app.api.v1.zones import router as zones_router
from app.api.v1.scenarios import router as scenarios_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(recommendations_router)
router.include_router(chat_router)
router.include_router(zones_router)
router.include_router(scenarios_router)
