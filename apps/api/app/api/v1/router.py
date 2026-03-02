from fastapi import APIRouter

from app.api.v1.endpoints.events import router as events_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.home import router as home_router
from app.api.v1.endpoints.items import router as items_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(home_router)
api_router.include_router(items_router)
api_router.include_router(events_router)
