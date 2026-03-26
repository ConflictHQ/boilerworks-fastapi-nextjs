from datetime import datetime

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import Session, User


async def get_user_from_token(token: str, db: AsyncSession) -> User | None:
    """Look up user from a raw session token."""
    token_hash = Session.hash_token(token)
    result = await db.execute(
        select(Session).where(Session.token_hash == token_hash, Session.expires_at > datetime.utcnow())
    )
    session = result.scalar_one_or_none()
    if not session:
        return None

    result = await db.execute(select(User).where(User.id == session.user_id, User.is_active.is_(True)))
    return result.scalar_one_or_none()


async def get_context(request: Request, db: AsyncSession = Depends(get_db)) -> dict:
    """GraphQL context getter — extracts user from Authorization header or session cookie."""
    token = None

    auth_header = request.headers.get("Authorization")
    if auth_header:
        token = auth_header.replace("Bearer ", "").replace("Session ", "")

    if not token:
        token = request.cookies.get("session")

    user = None
    if token:
        user = await get_user_from_token(token, db)

    return {"request": request, "user": user, "db": db}
