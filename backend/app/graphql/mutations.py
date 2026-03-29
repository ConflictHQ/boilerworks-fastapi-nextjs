from decimal import Decimal

import strawberry
from slugify import slugify
from strawberry.types import Info

from .types import FieldError, MutationResult


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_item(self, info: Info, name: str, price: str, description: str = "") -> MutationResult:
        user = info.context["user"]
        if not user:
            raise PermissionError("Authentication required")

        from app.models.item import Item

        db = info.context["db"]
        item = Item(
            name=name,
            slug=slugify(name),
            description=description,
            price=Decimal(price),
            created_by=user.id,
        )
        db.add(item)
        await db.commit()
        return MutationResult(ok=True)

    @strawberry.mutation
    async def update_item(
        self, info: Info, slug: str, name: str | None = None, price: str | None = None, description: str | None = None
    ) -> MutationResult:
        user = info.context["user"]
        if not user:
            raise PermissionError("Authentication required")

        from sqlalchemy import select

        from app.models.item import Item

        db = info.context["db"]
        result = await db.execute(select(Item).where(Item.slug == slug, Item.active()))
        item = result.scalar_one_or_none()
        if not item:
            return MutationResult(ok=False, errors=[FieldError(field="slug", messages=["Item not found"])])

        if name is not None:
            item.name = name
            item.slug = slugify(name)
        if price is not None:
            item.price = Decimal(price)
        if description is not None:
            item.description = description

        await db.commit()
        return MutationResult(ok=True)

    @strawberry.mutation
    async def delete_item(self, info: Info, slug: str) -> MutationResult:
        user = info.context["user"]
        if not user:
            raise PermissionError("Authentication required")

        from sqlalchemy import func, select

        from app.models.item import Item

        db = info.context["db"]
        result = await db.execute(select(Item).where(Item.slug == slug, Item.active()))
        item = result.scalar_one_or_none()
        if not item:
            return MutationResult(ok=False, errors=[FieldError(field="slug", messages=["Item not found"])])

        item.deleted_at = func.now()
        await db.commit()
        return MutationResult(ok=True)
