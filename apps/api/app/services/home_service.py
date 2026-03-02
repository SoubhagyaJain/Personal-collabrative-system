import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import Select, and_, case, desc, func, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.event import Event
from app.db.models.item import Item
from app.schemas.home import HomeResponse, HomeRow
from app.schemas.item import ItemCard, ItemDetail


class HomeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_trending_items(self, limit: int = 12) -> list[Item]:
        since = datetime.now(UTC) - timedelta(days=7)

        plays_last_7d = func.count(case((and_(Event.event_type == "play", Event.ts >= since), 1)))

        stmt = (
            select(Item)
            .outerjoin(Event, Event.item_id == Item.id)
            .group_by(Item.id)
            .order_by(plays_last_7d.desc(), Item.created_at.desc(), Item.id.asc())
            .limit(limit)
        )

        rows = (await self.session.execute(stmt)).scalars().all()
        if rows:
            return list(rows)

        fallback_stmt: Select[tuple[Item]] = (
            select(Item).order_by(Item.created_at.desc(), Item.id.asc()).limit(limit)
        )
        return list((await self.session.execute(fallback_stmt)).scalars().all())

    async def get_user_recent_item(self, user_id: uuid.UUID) -> Item | None:
        stmt = (
            select(Item)
            .join(Event, Event.item_id == Item.id)
            .where(Event.user_id == user_id, Event.event_type.in_(["play", "finish"]))
            .order_by(Event.ts.desc())
            .limit(1)
        )
        return (await self.session.execute(stmt)).scalars().first()

    async def get_seed_item(self) -> Item | None:
        return (
            await self.session.execute(
                select(Item).order_by(Item.created_at.desc(), Item.id.asc()).limit(1)
            )
        ).scalars().first()

    async def get_similar_by_genres(self, base_item: Item, limit: int = 12) -> list[Item]:
        genres = base_item.genres or []
        if not genres:
            return await self.get_trending_items(limit=limit)

        stmt = (
            select(Item)
            .where(Item.id != base_item.id, Item.genres.overlap(array(genres)))
            .outerjoin(Event, Event.item_id == Item.id)
            .group_by(Item.id)
            .order_by(
                func.count(case((Event.event_type == "play", 1))).desc(),
                Item.created_at.desc(),
                Item.id.asc(),
            )
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def get_top_picks(self, user_id: uuid.UUID, limit: int = 12) -> list[Item]:
        pref_stmt = (
            select(func.unnest(Item.genres).label("genre"), func.count().label("score"))
            .join(Event, Event.item_id == Item.id)
            .where(Event.user_id == user_id, Event.event_type.in_(["play", "click"]))
            .group_by("genre")
            .order_by(desc("score"))
            .limit(5)
        )
        preferred_genres = [row.genre for row in (await self.session.execute(pref_stmt)).all()]

        if not preferred_genres:
            return await self.get_trending_items(limit=limit)

        stmt = (
            select(Item)
            .where(Item.genres.overlap(array(preferred_genres)))
            .outerjoin(Event, Event.item_id == Item.id)
            .group_by(Item.id)
            .order_by(
                func.count(case((Event.event_type.in_(["play", "click"]), 1))).desc(),
                Item.created_at.desc(),
                Item.id.asc(),
            )
            .limit(limit)
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def build_home(self, user_id: uuid.UUID) -> HomeResponse:
        top_picks = await self.get_top_picks(user_id)
        recent_item = await self.get_user_recent_item(user_id)
        if recent_item is None:
            recent_item = await self.get_seed_item()

        because_items = (
            await self.get_similar_by_genres(recent_item, limit=12) if recent_item else []
        )
        trending = await self.get_trending_items()

        rows = [
            HomeRow(id="top_picks", title="Top Picks for You", items=[to_card(i) for i in top_picks]),
            HomeRow(
                id="because_watched",
                title=f"Because you watched {recent_item.title}" if recent_item else "Because you watched",
                items=[to_card(i) for i in because_items],
            ),
            HomeRow(id="trending", title="Trending Now", items=[to_card(i) for i in trending]),
        ]
        return HomeResponse(user_id=user_id, rows=rows)

    async def get_item_detail(self, item_id: uuid.UUID) -> tuple[Item | None, list[Item]]:
        item = (await self.session.execute(select(Item).where(Item.id == item_id))).scalars().first()
        if item is None:
            return None, []
        similar = await self.get_similar_by_genres(item, limit=10)
        return item, similar


def to_card(item: Item) -> ItemCard:
    return ItemCard(id=item.id, title=item.title, poster_url=item.poster_url, genres=item.genres)


def to_detail(item: Item) -> ItemDetail:
    return ItemDetail(
        id=item.id,
        title=item.title,
        poster_url=item.poster_url,
        genres=item.genres,
        metadata_json=item.metadata_json,
    )