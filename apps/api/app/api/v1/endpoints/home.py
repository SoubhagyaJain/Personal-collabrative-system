import json
import uuid

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db, get_redis
from app.schemas.home import HomeResponse
from app.services.cache import CacheService
from app.services.home_service import HomeService

router = APIRouter()


@router.get("/home", response_model=HomeResponse)
async def get_home(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    redis_client: Redis | None = Depends(get_redis),
) -> HomeResponse:
    settings = get_settings()
    cache = CacheService(redis_client, settings.home_cache_ttl_seconds)
    cache_key = f"home:{user_id}:v1"

    cached = await cache.get(cache_key)
    if cached:
        return HomeResponse.model_validate_json(cached)

    home = await HomeService(db).build_home(user_id)
    await cache.set(cache_key, home.model_dump_json())
    return home
