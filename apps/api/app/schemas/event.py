import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

EventType = Literal["impression", "click", "play", "like", "add_to_list", "finish"]


class EventCreate(BaseModel):
    user_id: uuid.UUID
    item_id: uuid.UUID
    event_type: EventType
    row_id: str | None = None
    rank_position: int | None = None
    session_id: str | None = None
    variant_id: str | None = None
    watch_time_sec: int | None = None
    ts: datetime | None = None


class EventCreateResponse(BaseModel):
    status: str = "ok"
