from decimal import Decimal

import strawberry
from slugify import slugify
from strawberry.types import Info

from .types import FieldError, MutationResult


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_product(self, info: Info, name: str, price: str, description: str = "") -> MutationResult:
        user = info.context["user"]
        if not user:
            raise PermissionError("Authentication required")

        from app.models.product import Product

        db = info.context["db"]
        product = Product(
            name=name,
            slug=slugify(name),
            description=description,
            price=Decimal(price),
            created_by=user.id,
        )
        db.add(product)
        await db.commit()
        return MutationResult(ok=True)

    @strawberry.mutation
    async def update_product(
        self, info: Info, slug: str, name: str | None = None, price: str | None = None, description: str | None = None
    ) -> MutationResult:
        user = info.context["user"]
        if not user:
            raise PermissionError("Authentication required")

        from sqlalchemy import select

        from app.models.product import Product

        db = info.context["db"]
        result = await db.execute(select(Product).where(Product.slug == slug, Product.active()))
        product = result.scalar_one_or_none()
        if not product:
            return MutationResult(ok=False, errors=[FieldError(field="slug", messages=["Product not found"])])

        if name is not None:
            product.name = name
            product.slug = slugify(name)
        if price is not None:
            product.price = Decimal(price)
        if description is not None:
            product.description = description

        await db.commit()
        return MutationResult(ok=True)

    @strawberry.mutation
    async def delete_product(self, info: Info, slug: str) -> MutationResult:
        user = info.context["user"]
        if not user:
            raise PermissionError("Authentication required")

        from sqlalchemy import func, select

        from app.models.product import Product

        db = info.context["db"]
        result = await db.execute(select(Product).where(Product.slug == slug, Product.active()))
        product = result.scalar_one_or_none()
        if not product:
            return MutationResult(ok=False, errors=[FieldError(field="slug", messages=["Product not found"])])

        product.deleted_at = func.now()
        await db.commit()
        return MutationResult(ok=True)
