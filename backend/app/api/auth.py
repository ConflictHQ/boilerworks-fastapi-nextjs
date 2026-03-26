from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_auth
from app.config import settings
from app.database import get_db
from app.models.user import Session, User
from app.schemas.auth import LoginRequest, UserOut
from app.schemas.common import ApiResponse

router = APIRouter(tags=["auth"])


@router.post("/login")
async def login(data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)) -> ApiResponse:
    result = await db.execute(select(User).where(User.username == data.username, User.is_active.is_(True)))
    user = result.scalar_one_or_none()

    if not user or not user.verify_password(data.password):
        return ApiResponse(ok=False, errors=[{"detail": "Invalid credentials"}])

    session, raw_token = Session.create_token(user.id, days=settings.session_max_age_days)
    db.add(session)
    await db.commit()

    response.set_cookie(
        key="session",
        value=raw_token,
        httponly=True,
        samesite="lax",
        max_age=settings.session_max_age_days * 86400,
        secure=not settings.debug,
    )
    return ApiResponse(ok=True, data=UserOut.from_model(user).model_dump())


@router.post("/logout")
async def logout(
    response: Response,
    user: User = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    response.delete_cookie("session")
    return ApiResponse(ok=True, data={"message": "Logged out"})


@router.get("/me")
async def me(user: User | None = Depends(get_current_user)) -> ApiResponse:
    if not user:
        return ApiResponse(ok=False, errors=[{"detail": "Not authenticated"}])
    return ApiResponse(ok=True, data=UserOut.from_model(user).model_dump())


@router.post("/session")
async def session_exchange(
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Token exchange endpoint — frontend POSTs credentials, gets back an Authorization token.
    This matches the path the shared Next.js frontend expects at /app/auth1/session."""
    result = await db.execute(select(User).where(User.username == data.username, User.is_active.is_(True)))
    user = result.scalar_one_or_none()

    if not user or not user.verify_password(data.password):
        return {"error": "Invalid credentials"}

    session, raw_token = Session.create_token(user.id, days=settings.session_max_age_days)
    db.add(session)
    await db.commit()

    response.set_cookie(
        key="session",
        value=raw_token,
        httponly=True,
        samesite="lax",
        max_age=settings.session_max_age_days * 86400,
        secure=not settings.debug,
    )
    return {"Authorization": f"Session {raw_token}"}
