import hashlib
import secrets
import uuid
from datetime import datetime, timedelta

import bcrypt as _bcrypt
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import AuditBase, Base


class User(AuditBase):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)

    groups: Mapped[list["UserGroup"]] = relationship(back_populates="user", lazy="selectin")

    def set_password(self, password: str) -> None:
        self.password_hash = _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()

    def verify_password(self, password: str) -> bool:
        return _bcrypt.checkpw(password.encode(), self.password_hash.encode())


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    @classmethod
    def create_token(cls, user_id: uuid.UUID, days: int = 30) -> tuple["Session", str]:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        session = cls(user_id=user_id, token_hash=token_hash, expires_at=datetime.utcnow() + timedelta(days=days))
        return session, raw_token

    @classmethod
    def hash_token(cls, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()


class Group(AuditBase):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    permissions: Mapped[list["Permission"]] = relationship(back_populates="group", lazy="selectin")


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("groups.id"))
    codename: Mapped[str] = mapped_column(String(100), index=True)

    group: Mapped["Group"] = relationship(back_populates="permissions")


class UserGroup(Base):
    __tablename__ = "user_groups"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("groups.id"))

    user: Mapped["User"] = relationship(back_populates="groups")
    group: Mapped["Group"] = relationship(lazy="selectin")
