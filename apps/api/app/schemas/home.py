import uuid

from pydantic import BaseModel

from app.schemas.item import ItemCard


class HomeRow(BaseModel):
    id: str
    title: str
    items: list[ItemCard]


class HomeResponse(BaseModel):
    user_id: uuid.UUID
    rows: list[HomeRow]
