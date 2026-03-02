import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import Select, and_, case, desc, func, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.event import Event
from app.db.models.item import Item
from app.db.models.user import User
from app.schemas.home import HomeResponse, HomeRow
from app.schemas.item import ItemCard, ItemDetail
from app.services.model_store import model_store


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
        fallback_stmt: Select[tuple[Item]] = select(Item).order_by(Item.created_at.desc(), Item.id.asc()).limit(
            limit
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
            await self.session.execute(select(Item).order_by(Item.created_at.desc(), Item.id.asc()).limit(1))
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

    async def _movielens_user_id_for_uuid(self, user_id: uuid.UUID) -> int | None:
        user = (await self.session.execute(select(User).where(User.id == user_id))).scalars().first()
        if not user or not user.metadata_json:
            return None
        raw = user.metadata_json.get("movielens_user_id")
        return int(raw) if isinstance(raw, (int, str)) and str(raw).isdigit() else None

    async def _items_by_movielens_ids(self, movielens_item_ids: list[int], limit: int = 12) -> list[Item]:
        if not movielens_item_ids:
            return []
        stmt = select(Item).where(
            Item.metadata_json["movielens_movie_id"].astext.in_([str(x) for x in movielens_item_ids])
        )
        items = list((await self.session.execute(stmt)).scalars().all())
        score = {mid: idx for idx, mid in enumerate(movielens_item_ids)}
        items.sort(
            key=lambda item: score.get(int(item.metadata_json.get("movielens_movie_id", -1)) if item.metadata_json else -1, 10**9)
        )
        return items[:limit]

    async def _cf_top_picks(self, user_id: uuid.UUID, limit: int = 12) -> list[Item]:
        if not model_store.loaded:
            return []
        ml_user_id = await self._movielens_user_id_for_uuid(user_id)
        if ml_user_id is None:
            return []
        ids = model_store.recommend_for_movielens_user(ml_user_id, k=limit * 3)
        return await self._items_by_movielens_ids(ids, limit=limit)

    async def _cf_similar_items(self, base_item: Item, limit: int = 12) -> list[Item]:
        if not model_store.loaded:
            return []
        if not base_item.metadata_json:
            return []
        movie_id = base_item.metadata_json.get("movielens_movie_id")
        if not isinstance(movie_id, int):
            return []
        ids = model_store.similar_items_for_movielens_item(movie_id, k=limit * 3)
        return await self._items_by_movielens_ids(ids, limit=limit)

    async def build_home(self, user_id: uuid.UUID) -> HomeResponse:
        top_picks = await self._cf_top_picks(user_id, limit=12)
        if not top_picks:
            top_picks = await self.get_top_picks(user_id)

        recent_item = await self.get_user_recent_item(user_id)
        if recent_item is None:
            recent_item = await self.get_seed_item()

        because_items = []
        if recent_item:
            because_items = await self._cf_similar_items(recent_item, limit=12)
            if not because_items:
                because_items = await self.get_similar_by_genres(recent_item, limit=12)

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
        similar = await self._cf_similar_items(item, limit=10)
        if not similar:
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
