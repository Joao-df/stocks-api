from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import event, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import DateTime


class Base(DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


@event.listens_for(Base, "before_insert", propagate=True)
def create_time(mapper: Any, connection: Any, instance: Base) -> None:
    now = datetime.now(timezone.utc)
    instance.created_at = now
    instance.updated_at = now


@event.listens_for(Base, "before_update", propagate=True)
def update_time(mapper: Any, connection: Any, instance: Base) -> None:
    now = datetime.now(timezone.utc)
    instance.updated_at = now
