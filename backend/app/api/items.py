from decimal import Decimal

from fastapi import APIRouter, Depends
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_auth, require_permission
from app.database import get_db
from app.models.item import Item
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
async def list_items(
    search: str = "",
    user: User = Depends(require_auth),
    _perm: User = Depends(require_permission("item.view")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    stmt = select(Item).where(Item.active())
    if search:
        stmt = stmt.where(Item.name.ilike(f"%{search}%"))
    stmt = stmt.order_by(Item.created_at.desc())
    result = await db.execute(stmt)
    items = [ItemOut.from_model(p) for p in result.scalars()]
    return ApiResponse(ok=True, data=[p.model_dump() for p in items])


@router.post("", status_code=201)
async def create_item(
    data: ItemCreate,
    user: User = Depends(require_auth),
    _perm: User = Depends(require_permission("item.add")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    item = Item(
        name=data.name,
        slug=slugify(data.name),
        description=data.description,
        price=Decimal(data.price),
        sku=data.sku,
        is_active=data.is_active,
        created_by=user.id,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ApiResponse(ok=True, data=ItemOut.from_model(item).model_dump())


@router.get("/{slug}")
async def get_item(
    slug: str,
    user: User = Depends(require_auth),
    _perm: User = Depends(require_permission("item.view")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(select(Item).where(Item.slug == slug, Item.active()))
    item = result.scalar_one_or_none()
    if not item:
        return ApiResponse(ok=False, errors=[{"detail": "Not found"}])
    return ApiResponse(ok=True, data=ItemOut.from_model(item).model_dump())


@router.put("/{slug}")
async def update_item(
    slug: str,
    data: ItemUpdate,
    user: User = Depends(require_auth),
    _perm: User = Depends(require_permission("item.change")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(select(Item).where(Item.slug == slug, Item.active()))
    item = result.scalar_one_or_none()
    if not item:
        return ApiResponse(ok=False, errors=[{"detail": "Not found"}])

    if data.name is not None:
        item.name = data.name
        item.slug = slugify(data.name)
    if data.description is not None:
        item.description = data.description
    if data.price is not None:
        item.price = Decimal(data.price)
    if data.sku is not None:
        item.sku = data.sku
    if data.is_active is not None:
        item.is_active = data.is_active

    await db.commit()
    await db.refresh(item)
    return ApiResponse(ok=True, data=ItemOut.from_model(item).model_dump())


@router.delete("/{slug}")
async def delete_item(
    slug: str,
    user: User = Depends(require_auth),
    _perm: User = Depends(require_permission("item.delete")),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse:
    result = await db.execute(select(Item).where(Item.slug == slug, Item.active()))
    item = result.scalar_one_or_none()
    if not item:
        return ApiResponse(ok=False, errors=[{"detail": "Not found"}])

    from sqlalchemy import func

    item.deleted_at = func.now()
    await db.commit()
    return ApiResponse(ok=True, data={"message": f"Item '{item.name}' deleted"})
