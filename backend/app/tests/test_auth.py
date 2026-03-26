import pytest
from httpx import AsyncClient

from app.models.user import User


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user: User):
    response = await client.post("/api/auth/login", json={"username": "admin", "password": "testpass123"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["data"]["username"] == "admin"
    assert "session" in response.cookies


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, admin_user: User):
    response = await client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    data = response.json()
    assert data["ok"] is False


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post("/api/auth/login", json={"username": "ghost", "password": "x"})
    data = response.json()
    assert data["ok"] is False


@pytest.mark.asyncio
async def test_me_authenticated(admin_client: AsyncClient):
    response = await admin_client.get("/api/auth/me")
    data = response.json()
    assert data["ok"] is True
    assert data["data"]["username"] == "admin"


@pytest.mark.asyncio
async def test_me_unauthenticated(client: AsyncClient):
    response = await client.get("/api/auth/me")
    data = response.json()
    assert data["ok"] is False


@pytest.mark.asyncio
async def test_logout(admin_client: AsyncClient):
    response = await admin_client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json()["ok"] is True
