import uuid
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_db, get_redis
from app.main import app


class DummyDB:
    pass


async def override_db() -> AsyncGenerator[DummyDB, None]:
    yield DummyDB()


def override_redis() -> None:
    return None


@pytest.mark.asyncio
async def test_home_returns_three_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.schemas.home import HomeResponse, HomeRow
    from app.schemas.item import ItemCard
    from app.services import home_service

    user_id = uuid.uuid4()
    sample_item = ItemCard(id=uuid.uuid4(), title="Sample", poster_url=None, genres=["Drama"])

    async def fake_build_home(self, _user_id: uuid.UUID) -> HomeResponse:  # type: ignore[no-untyped-def]
        return HomeResponse(
            user_id=user_id,
            rows=[
                HomeRow(id="top_picks", title="Top Picks for You", items=[sample_item]),
                HomeRow(id="because_watched", title="Because you watched Sample", items=[sample_item]),
                HomeRow(id="trending", title="Trending Now", items=[sample_item]),
            ],
        )

    monkeypatch.setattr(home_service.HomeService, "build_home", fake_build_home)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = override_redis
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(f"/api/v1/home?user_id={user_id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data["rows"]) == 3
    assert all(len(row["items"]) > 0 for row in data["rows"])
