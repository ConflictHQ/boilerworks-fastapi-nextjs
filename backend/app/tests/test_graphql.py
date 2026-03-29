import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item


@pytest.mark.asyncio
async def test_me_query_authenticated(admin_client: AsyncClient):
    response = await admin_client.post(
        "/app/gql/config",
        json={"query": "{ me { id profile { username email } isSuperuser } }"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["me"]["profile"]["username"] == "admin"
    assert data["me"]["isSuperuser"] is True


@pytest.mark.asyncio
async def test_me_query_unauthenticated(client: AsyncClient):
    response = await client.post("/app/gql/config", json={"query": "{ me { id } }"})
    assert response.status_code == 200
    assert response.json()["data"]["me"] is None


@pytest.mark.asyncio
async def test_items_query(admin_client: AsyncClient, db: AsyncSession):
    db.add(Item(name="GQL Widget", slug="gql-widget", price=10))
    await db.commit()

    response = await admin_client.post(
        "/app/gql/config",
        json={"query": "{ items { edges { node { name slug price } } totalCount } }"},
    )
    assert response.status_code == 200
    data = response.json()["data"]["items"]
    assert data["totalCount"] >= 1
    names = [e["node"]["name"] for e in data["edges"]]
    assert "GQL Widget" in names


@pytest.mark.asyncio
async def test_items_query_search(admin_client: AsyncClient, db: AsyncSession):
    db.add(Item(name="Findable", slug="findable", price=10))
    db.add(Item(name="Hidden", slug="hidden-item", price=20))
    await db.commit()

    response = await admin_client.post(
        "/app/gql/config",
        json={"query": '{ items(search: "Find") { edges { node { name } } totalCount } }'},
    )
    data = response.json()["data"]["items"]
    names = [e["node"]["name"] for e in data["edges"]]
    assert "Findable" in names
    assert "Hidden" not in names


@pytest.mark.asyncio
async def test_create_item_mutation(admin_client: AsyncClient, db: AsyncSession):
    response = await admin_client.post(
        "/app/gql/config",
        json={"query": 'mutation { createItem(name: "Mutated", price: "42.00") { ok errors { field messages } } }'},
    )
    assert response.status_code == 200
    data = response.json()["data"]["createItem"]
    assert data["ok"] is True

    # Verify in DB
    from sqlalchemy import select

    result = await db.execute(select(Item).where(Item.slug == "mutated"))
    item = result.scalar_one()
    assert item.name == "Mutated"


@pytest.mark.asyncio
async def test_component_query(admin_client: AsyncClient):
    response = await admin_client.post(
        "/app/gql/config",
        json={"query": '{ component(slug: "test-feature") { slug isActive } }'},
    )
    assert response.status_code == 200
    data = response.json()["data"]["component"]
    assert data["slug"] == "test-feature"
    assert data["isActive"] is True
