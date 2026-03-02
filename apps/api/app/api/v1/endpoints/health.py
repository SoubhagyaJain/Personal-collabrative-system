from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db, get_redis
from app.schemas.health import HealthResponse

router = APIRouter()


async def _dependency_status(db: AsyncSession, redis_client: Redis | None) -> tuple[str, str]:
    db_status = "ok"
    redis_status = "ok"

    try:
        await db.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001
        db_status = "error"

    if redis_client is None:
        redis_status = "error"
    else:
        try:
            await redis_client.ping()
        except Exception:  # noqa: BLE001
            redis_status = "error"

    return db_status, redis_status


@router.get("/health", response_model=HealthResponse)
async def health(
    db: AsyncSession = Depends(get_db), redis_client: Redis | None = Depends(get_redis)
) -> HealthResponse:
    settings = get_settings()
    db_status, redis_status = await _dependency_status(db, redis_client)
    return HealthResponse(
        status="ok",
        model_version=settings.model_version,
        git_sha=settings.git_sha,
        db=db_status,
        redis=redis_status,
    )


@router.get("/ready", response_model=HealthResponse)
async def ready(
    db: AsyncSession = Depends(get_db), redis_client: Redis | None = Depends(get_redis)
) -> HealthResponse:
    settings = get_settings()
    db_status, redis_status = await _dependency_status(db, redis_client)
    if db_status != "ok" or redis_status != "ok":
        raise HTTPException(status_code=503, detail="Service not ready")
    return HealthResponse(
        status="ok",
        model_version=settings.model_version,
        git_sha=settings.git_sha,
        db=db_status,
        redis=redis_status,
    )
