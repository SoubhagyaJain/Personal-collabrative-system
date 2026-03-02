import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    row_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    rank_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    session_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    variant_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    watch_time_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


Index("ix_events_user_ts_desc", Event.user_id, Event.ts.desc())
Index("ix_events_item_ts_desc", Event.item_id, Event.ts.desc())
Index("ix_events_type_ts_desc", Event.event_type, Event.ts.desc())
