import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


@pytest.mark.asyncio
async def test_create_product(admin_client: AsyncClient, db: AsyncSession):
    response = await admin_client.post(
        "/api/products",
        json={"name": "Widget", "price": "29.99", "sku": "WGT-001"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["ok"] is True
    assert data["data"]["name"] == "Widget"
    assert data["data"]["slug"] == "widget"

    result = await db.execute(select(Product).where(Product.slug == "widget"))
    product = result.scalar_one()
    assert product.name == "Widget"


@pytest.mark.asyncio
async def test_list_products(admin_client: AsyncClient, db: AsyncSession):
    db.add(Product(name="Alpha", slug="alpha", price=10, created_by=None))
    db.add(Product(name="Beta", slug="beta", price=20, created_by=None))
    await db.commit()

    response = await admin_client.get("/api/products")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_list_products_search(admin_client: AsyncClient, db: AsyncSession):
    db.add(Product(name="Searchable", slug="searchable", price=10))
    db.add(Product(name="Hidden", slug="hidden", price=20))
    await db.commit()

    response = await admin_client.get("/api/products?search=Search")
    data = response.json()["data"]
    names = [p["name"] for p in data]
    assert "Searchable" in names
    assert "Hidden" not in names


@pytest.mark.asyncio
async def test_get_product(admin_client: AsyncClient, db: AsyncSession):
    db.add(Product(name="Detail", slug="detail-prod", price=50))
    await db.commit()

    response = await admin_client.get("/api/products/detail-prod")
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "Detail"


@pytest.mark.asyncio
async def test_get_product_not_found(admin_client: AsyncClient):
    response = await admin_client.get("/api/products/nonexistent")
    assert response.json()["ok"] is False


@pytest.mark.asyncio
async def test_update_product(admin_client: AsyncClient, db: AsyncSession):
    db.add(Product(name="Old", slug="old-prod", price=10))
    await db.commit()

    response = await admin_client.put("/api/products/old-prod", json={"name": "New", "price": "99.99"})
    assert response.status_code == 200
    assert response.json()["data"]["name"] == "New"


@pytest.mark.asyncio
async def test_delete_product(admin_client: AsyncClient, db: AsyncSession):
    db.add(Product(name="Delete Me", slug="delete-me", price=10))
    await db.commit()

    response = await admin_client.delete("/api/products/delete-me")
    assert response.status_code == 200
    assert response.json()["ok"] is True

    # Verify soft-deleted (not returned in list)
    response = await admin_client.get("/api/products/delete-me")
    assert response.json()["ok"] is False


@pytest.mark.asyncio
async def test_products_require_auth(client: AsyncClient):
    response = await client.get("/api/products")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_products_require_permission(viewer_client: AsyncClient, db: AsyncSession):
    # Viewer can list (has product.view)
    response = await viewer_client.get("/api/products")
    assert response.status_code == 200

    # Viewer cannot create (no product.add)
    response = await viewer_client.post("/api/products", json={"name": "X", "price": "1"})
    assert response.status_code == 403
