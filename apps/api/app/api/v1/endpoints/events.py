from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models.event import Event
from app.db.session import get_db, get_redis
from app.schemas.event import EventCreate, EventCreateResponse
from app.services.cache import CacheService

router = APIRouter()


@router.post("/events", response_model=EventCreateResponse)
async def create_event(
    payload: EventCreate,
    db: AsyncSession = Depends(get_db),
    redis_client: Redis | None = Depends(get_redis),
) -> EventCreateResponse:
    event = Event(
        user_id=payload.user_id,
        item_id=payload.item_id,
        event_type=payload.event_type,
        row_id=payload.row_id,
        rank_position=payload.rank_position,
        session_id=payload.session_id,
        variant_id=payload.variant_id,
        watch_time_sec=payload.watch_time_sec,
        ts=payload.ts,
    )
    db.add(event)
    await db.commit()

    settings = get_settings()
    cache = CacheService(redis_client, settings.home_cache_ttl_seconds)
    await cache.delete(f"home:{payload.user_id}:v1")

    return EventCreateResponse()
