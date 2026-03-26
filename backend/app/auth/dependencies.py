from datetime import datetime

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import Session, User


async def get_current_user(
    session_token: str | None = Cookie(None, alias="session"),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Extract current user from session cookie. Returns None if not authenticated."""
    if not session_token:
        return None

    token_hash = Session.hash_token(session_token)
    result = await db.execute(
        select(Session).where(Session.token_hash == token_hash, Session.expires_at > datetime.now(datetime.UTC))
    )
    session = result.scalar_one_or_none()
    if not session:
        return None

    result = await db.execute(select(User).where(User.id == session.user_id, User.is_active.is_(True)))
    return result.scalar_one_or_none()


async def require_auth(user: User | None = Depends(get_current_user)) -> User:
    """Require authenticated user. Raises 401 if not authenticated."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_permission(codename: str):
    """Factory: returns a dependency that checks the user has a specific permission."""

    async def check(user: User = Depends(require_auth)) -> User:
        if user.is_superuser:
            return user
        for ug in user.groups:
            for perm in ug.group.permissions:
                if perm.codename == codename:
                    return user
        raise HTTPException(status_code=403, detail=f"Missing permission: {codename}")

    return check
