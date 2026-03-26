import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


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
async def test_products_query(admin_client: AsyncClient, db: AsyncSession):
    db.add(Product(name="GQL Widget", slug="gql-widget", price=10))
    await db.commit()

    response = await admin_client.post(
        "/app/gql/config",
        json={"query": "{ products { edges { node { name slug price } } totalCount } }"},
    )
    assert response.status_code == 200
    data = response.json()["data"]["products"]
    assert data["totalCount"] >= 1
    names = [e["node"]["name"] for e in data["edges"]]
    assert "GQL Widget" in names


@pytest.mark.asyncio
async def test_products_query_search(admin_client: AsyncClient, db: AsyncSession):
    db.add(Product(name="Findable", slug="findable", price=10))
    db.add(Product(name="Hidden", slug="hidden-item", price=20))
    await db.commit()

    response = await admin_client.post(
        "/app/gql/config",
        json={"query": '{ products(search: "Find") { edges { node { name } } totalCount } }'},
    )
    data = response.json()["data"]["products"]
    names = [e["node"]["name"] for e in data["edges"]]
    assert "Findable" in names
    assert "Hidden" not in names


@pytest.mark.asyncio
async def test_create_product_mutation(admin_client: AsyncClient, db: AsyncSession):
    response = await admin_client.post(
        "/app/gql/config",
        json={"query": 'mutation { createProduct(name: "Mutated", price: "42.00") { ok errors { field messages } } }'},
    )
    assert response.status_code == 200
    data = response.json()["data"]["createProduct"]
    assert data["ok"] is True

    # Verify in DB
    from sqlalchemy import select

    result = await db.execute(select(Product).where(Product.slug == "mutated"))
    product = result.scalar_one()
    assert product.name == "Mutated"


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
