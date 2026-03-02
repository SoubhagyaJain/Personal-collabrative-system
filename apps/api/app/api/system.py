from fastapi import APIRouter

from app.core.config import settings
from app.models.health import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(service=settings.name, environment=settings.env)
