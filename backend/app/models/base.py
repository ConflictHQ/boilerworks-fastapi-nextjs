import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AuditBase(Base):
    """Abstract base with UUID PK and audit timestamps."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class SoftDeleteMixin:
    """Mixin for soft-deleting records. Never call session.delete() on business objects."""

    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True, default=None)

    @classmethod
    def active(cls):
        return cls.deleted_at.is_(None)
