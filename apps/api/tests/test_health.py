from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_db, get_redis
from app.main import app


class BrokenDB:
    async def execute(self, *_args, **_kwargs):
        raise RuntimeError("db down")


async def override_db() -> AsyncGenerator[BrokenDB, None]:
    yield BrokenDB()


def override_redis() -> None:
    return None


@pytest.mark.asyncio
async def test_health_endpoint_returns_ok_with_dependency_failures() -> None:
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = override_redis
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/health")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["db"] == "error"
    assert payload["redis"] == "error"