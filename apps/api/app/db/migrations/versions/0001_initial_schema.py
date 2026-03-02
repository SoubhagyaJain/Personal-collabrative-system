"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-03-02 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("genres", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("poster_url", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("items.id"), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("row_id", sa.Text(), nullable=True),
        sa.Column("rank_position", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.Text(), nullable=True),
        sa.Column("variant_id", sa.Text(), nullable=True),
        sa.Column("watch_time_sec", sa.Integer(), nullable=True),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_index("ix_events_user_ts_desc", "events", ["user_id", sa.text("ts DESC")])
    op.create_index("ix_events_item_ts_desc", "events", ["item_id", sa.text("ts DESC")])
    op.create_index("ix_events_type_ts_desc", "events", ["event_type", sa.text("ts DESC")])


def downgrade() -> None:
    op.drop_index("ix_events_type_ts_desc", table_name="events")
    op.drop_index("ix_events_item_ts_desc", table_name="events")
    op.drop_index("ix_events_user_ts_desc", table_name="events")
    op.drop_table("events")
    op.drop_table("items")
    op.drop_table("users")
