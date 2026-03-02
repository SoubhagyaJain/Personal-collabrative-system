import asyncio
import csv
import uuid
from pathlib import Path

from sqlalchemy import select

from app.db.models.item import Item
from app.db.models.user import User
from app.db.session import AsyncSessionLocal


def _ml_root_candidates() -> list[Path]:
    return [Path("/app/ml/data/ml-1m"), Path("ml/data/ml-1m")]


def parse_movielens_movies(limit: int = 200) -> list[dict[str, object]]:
    for root in _ml_root_candidates():
        movies_path = root / "movies.dat"
        if movies_path.exists():
            items: list[dict[str, object]] = []
            with movies_path.open("r", encoding="latin-1") as f:
                for line in f:
                    parts = line.strip().split("::")
                    if len(parts) < 3:
                        continue
                    movie_id, title, genres_raw = parts[0], parts[1], parts[2]
                    genres = [g for g in genres_raw.split("|") if g and g != "(no genres listed)"]
                    items.append(
                        {
                            "title": title,
                            "genres": genres or ["Drama"],
                            "poster_url": None,
                            "metadata_json": {
                                "source": "movielens-1m",
                                "movielens_movie_id": int(movie_id),
                            },
                        }
                    )
                    if len(items) >= limit:
                        break
            return items
    return []


def parse_movielens_users(limit: int = 100) -> list[dict[str, object]]:
    for root in _ml_root_candidates():
        users_path = root / "users.dat"
        if users_path.exists():
            users: list[dict[str, object]] = []
            with users_path.open("r", encoding="latin-1") as f:
                for line in f:
                    parts = line.strip().split("::")
                    if len(parts) < 1:
                        continue
                    users.append({"id": uuid.uuid4(), "metadata_json": {"movielens_user_id": int(parts[0])}})
                    if len(users) >= limit:
                        break
            return users
    return []


def fallback_items() -> list[dict[str, object]]:
    return [
        {
            "title": "The Collab Heist",
            "genres": ["Action", "Thriller"],
            "poster_url": None,
            "metadata_json": {"year": 2024},
        },
        {
            "title": "Async Nights",
            "genres": ["Drama"],
            "poster_url": None,
            "metadata_json": {"year": 2023},
        },
        {
            "title": "Redis & Chill",
            "genres": ["Comedy"],
            "poster_url": None,
            "metadata_json": {"year": 2024},
        },
        {
            "title": "Feature Flags",
            "genres": ["Sci-Fi"],
            "poster_url": None,
            "metadata_json": {"year": 2022},
        },
        {
            "title": "Latency Hunters",
            "genres": ["Action", "Sci-Fi"],
            "poster_url": None,
            "metadata_json": {"year": 2021},
        },
    ]


async def main() -> None:
    async with AsyncSessionLocal() as session:
        existing_user = (await session.execute(select(User).limit(1))).scalars().first()
        if existing_user is None:
            ml_users = parse_movielens_users(limit=100)
            if ml_users:
                session.add_all(User(**u) for u in ml_users)
            demo = User(id=uuid.uuid4(), metadata_json=None)
            session.add(demo)
            demo_user = demo
        else:
            demo_user = existing_user

        existing_items = (await session.execute(select(Item).limit(1))).scalars().first()
        if existing_items is None:
            seed_items = parse_movielens_movies(limit=200) or fallback_items()
            session.add_all(Item(**item_data) for item_data in seed_items)

        await session.commit()
        print(f"demo_user_id={demo_user.id}")


if __name__ == "__main__":
    asyncio.run(main())
