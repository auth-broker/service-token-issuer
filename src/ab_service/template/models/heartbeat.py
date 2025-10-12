"""Heartbeat ORM Model."""

from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime, func
from ab_core.database.mixins.id import IDMixin
from ab_core.database.mixins.created_at import CreatedAtMixin
from ab_core.database.mixins.updated_at import UpdatedAtMixin


class Heartbeat(IDMixin, CreatedAtMixin, UpdatedAtMixin, table=True):
    """Heartbeat ORM Model."""

    __tablename__ = "heartbeat"

    last_seen: datetime | None = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        ),
    )
