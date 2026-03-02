import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_db, get_redis
from app.main import app


class FakeDB:
    def __init__(self) -> None:
        self.add_called = False
        self.commit_called = False

    def add(self, _obj: object) -> None:
        self.add_called = True

    async def commit(self) -> None:
        self.commit_called = True


@pytest.mark.asyncio
async def test_post_events_creates_event() -> None:
    db = FakeDB()

    async def override_db() -> AsyncGenerator[FakeDB, None]:
        yield db

    def override_redis() -> None:
        return None

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = override_redis

    payload = {
        "user_id": str(uuid.uuid4()),
        "item_id": str(uuid.uuid4()),
        "event_type": "play",
        "row_id": "trending",
        "rank_position": 1,
        "session_id": "sess-1",
        "variant_id": "A",
        "watch_time_sec": 12,
    }

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/events", json=payload)
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert db.add_called
    assert db.commit_called
