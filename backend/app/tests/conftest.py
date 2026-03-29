from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import get_db
from app.main import app
from app.models.base import Base
from app.models.user import Group, Permission, Session, User, UserGroup

test_engine = create_async_engine(settings.database_url, poolclass=NullPool)
TestSessionFactory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        # Truncate all tables instead of drop/create to avoid connection pool issues
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionFactory() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionFactory() as session:
        yield session


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession) -> User:
    user = User(email="admin@test.com", username="admin", is_superuser=True)
    user.set_password("testpass123")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def viewer_user(db: AsyncSession) -> User:
    user = User(email="viewer@test.com", username="viewer", is_superuser=False)
    user.set_password("testpass123")
    db.add(user)
    await db.commit()
    await db.refresh(user)

    group = Group(name="Viewers")
    db.add(group)
    await db.commit()
    await db.refresh(group)

    perm = Permission(group_id=group.id, codename="item.view")
    db.add(perm)
    ug = UserGroup(user_id=user.id, group_id=group.id)
    db.add(ug)
    await db.commit()
    return user


@pytest_asyncio.fixture
async def admin_session(db: AsyncSession, admin_user: User) -> str:
    session, raw_token = Session.create_token(admin_user.id)
    db.add(session)
    await db.commit()
    return raw_token


@pytest_asyncio.fixture
async def viewer_session(db: AsyncSession, viewer_user: User) -> str:
    session, raw_token = Session.create_token(viewer_user.id)
    db.add(session)
    await db.commit()
    return raw_token


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_client(admin_session: str) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", cookies={"session": admin_session}) as ac:
        yield ac


@pytest_asyncio.fixture
async def viewer_client(viewer_session: str) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", cookies={"session": viewer_session}) as ac:
        yield ac
