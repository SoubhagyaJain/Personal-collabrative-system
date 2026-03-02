import logging

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, redis_client: Redis | None, ttl_seconds: int) -> None:
        self.redis_client = redis_client
        self.ttl_seconds = ttl_seconds

    async def get(self, key: str) -> str | None:
        if self.redis_client is None:
            return None
        try:
            return await self.redis_client.get(key)
        except Exception as exc:  # noqa: BLE001
            logger.warning("cache_get_failed", extra={"error": str(exc), "key": key})
            return None

    async def set(self, key: str, value: str) -> None:
        if self.redis_client is None:
            return
        try:
            await self.redis_client.setex(key, self.ttl_seconds, value)
        except Exception as exc:  # noqa: BLE001
            logger.warning("cache_set_failed", extra={"error": str(exc), "key": key})

    async def delete(self, key: str) -> None:
        if self.redis_client is None:
            return
        try:
            await self.redis_client.delete(key)
        except Exception as exc:  # noqa: BLE001
            logger.warning("cache_delete_failed", extra={"error": str(exc), "key": key})
