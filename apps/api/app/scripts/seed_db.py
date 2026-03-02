import asyncio
import csv
import uuid
from pathlib import Path

from sqlalchemy import select

from app.db.models.item import Item
from app.db.models.user import User
from app.db.session import AsyncSessionLocal


def parse_movielens() -> list[dict[str, object]]:
    candidates = [
        Path("/app/ml/movies.csv"),
        Path("/app/ml/movielens/movies.csv"),
        Path("ml/movies.csv"),
    ]
    for candidate in candidates:
        if candidate.exists():
            items: list[dict[str, object]] = []
            with candidate.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    genres = [g for g in (row.get("genres") or "").split("|") if g and g != "(no genres listed)"]
                    items.append(
                        {
                            "title": row.get("title", "Untitled"),
                            "genres": genres or ["Drama"],
                            "poster_url": None,
                            "metadata_json": {"source": "movielens", "movielens_movie_id": row.get("movieId")},
                        }
                    )
                    if len(items) >= 200:
                        break
            return items
    return []


def fallback_items() -> list[dict[str, object]]:
    return [
        {"title": "The Collab Heist", "genres": ["Action", "Thriller"], "poster_url": None, "metadata_json": {"year": 2024}},
        {"title": "Async Nights", "genres": ["Drama"], "poster_url": None, "metadata_json": {"year": 2023}},
        {"title": "Redis & Chill", "genres": ["Comedy"], "poster_url": None, "metadata_json": {"year": 2024}},
        {"title": "Feature Flags", "genres": ["Sci-Fi"], "poster_url": None, "metadata_json": {"year": 2022}},
        {"title": "Latency Hunters", "genres": ["Action", "Sci-Fi"], "poster_url": None, "metadata_json": {"year": 2021}},
    ]


async def main() -> None:
    async with AsyncSessionLocal() as session:
        existing_user = (await session.execute(select(User).limit(1))).scalars().first()
        user = existing_user or User(id=uuid.uuid4())
        if existing_user is None:
            session.add(user)

        existing_items = (await session.execute(select(Item).limit(1))).scalars().first()
        if existing_items is None:
            seed_items = parse_movielens() or fallback_items()
            session.add_all(Item(**item_data) for item_data in seed_items)

        await session.commit()
        print(f"demo_user_id={user.id}")


if __name__ == "__main__":
    asyncio.run(main())
