from decimal import Decimal

from fastapi import APIRouter, Depends
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_auth, require_permission
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("")
async def list_products(
    search: str = "",
    user: User = Depends(require_auth),
    _perm: User = Depends(require_permission("product.view")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    stmt = select(Product).where(Product.active())
    if search:
        stmt = stmt.where(Product.name.ilike(f"%{search}%"))
    stmt = stmt.order_by(Product.created_at.desc())
    result = await db.execute(stmt)
    products = [ProductOut.from_model(p) for p in result.scalars()]
    return ApiResponse(ok=True, data=[p.model_dump() for p in products])


@router.post("", status_code=201)
async def create_product(
    data: ProductCreate,
    user: User = Depends(require_auth),
    _perm: User = Depends(require_permission("product.add")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    product = Product(
        name=data.name,
        slug=slugify(data.name),
        description=data.description,
        price=Decimal(data.price),
        sku=data.sku,
        is_active=data.is_active,
        created_by=user.id,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return ApiResponse(ok=True, data=ProductOut.from_model(product).model_dump())


@router.get("/{slug}")
async def get_product(
    slug: str,
    user: User = Depends(require_auth),
    _perm: User = Depends(require_permission("product.view")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(select(Product).where(Product.slug == slug, Product.active()))
    product = result.scalar_one_or_none()
    if not product:
        return ApiResponse(ok=False, errors=[{"detail": "Not found"}])
    return ApiResponse(ok=True, data=ProductOut.from_model(product).model_dump())


@router.put("/{slug}")
async def update_product(
    slug: str,
    data: ProductUpdate,
    user: User = Depends(require_auth),
    _perm: User = Depends(require_permission("product.change")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(select(Product).where(Product.slug == slug, Product.active()))
    product = result.scalar_one_or_none()
    if not product:
        return ApiResponse(ok=False, errors=[{"detail": "Not found"}])

    if data.name is not None:
        product.name = data.name
        product.slug = slugify(data.name)
    if data.description is not None:
        product.description = data.description
    if data.price is not None:
        product.price = Decimal(data.price)
    if data.sku is not None:
        product.sku = data.sku
    if data.is_active is not None:
        product.is_active = data.is_active

    await db.commit()
    await db.refresh(product)
    return ApiResponse(ok=True, data=ProductOut.from_model(product).model_dump())


@router.delete("/{slug}")
async def delete_product(
    slug: str,
    user: User = Depends(require_auth),
    _perm: User = Depends(require_permission("product.delete")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(select(Product).where(Product.slug == slug, Product.active()))
    product = result.scalar_one_or_none()
    if not product:
        return ApiResponse(ok=False, errors=[{"detail": "Not found"}])

    from sqlalchemy import func

    product.deleted_at = func.now()
    await db.commit()
    return ApiResponse(ok=True, data={"message": f"Product '{product.name}' deleted"})
