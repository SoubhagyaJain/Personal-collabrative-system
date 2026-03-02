import uuid
from typing import Any

from pydantic import BaseModel


class ItemCard(BaseModel):
    id: uuid.UUID
    title: str
    poster_url: str | None
    genres: list[str]


class ItemDetail(ItemCard):
    metadata_json: dict[str, Any] | None
