import strawberry
from strawberry.types import Info

from .types import (
    ComponentType,
    PageInfo,
    ItemConnection,
    ItemEdge,
    ItemType,
    UserProfile,
    UserType,
)


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info: Info) -> UserType | None:
        user = info.context["user"]
        if not user:
            return None
        return UserType(
            id=strawberry.ID(str(user.id)),
            profile=UserProfile(id=strawberry.ID(str(user.id)), username=user.username, email=user.email),
            is_superuser=user.is_superuser,
        )

    @strawberry.field
    async def items(
        self,
        info: Info,
        first: int = 25,
        offset: int = 0,
        search: str = "",
    ) -> ItemConnection:
        user = info.context["user"]
        if not user:
            raise PermissionError("Authentication required")

        from sqlalchemy import func, select

        from app.models.item import Item

        db = info.context["db"]
        stmt = select(Item).where(Item.active())
        if search:
            stmt = stmt.where(Item.name.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = stmt.order_by(Item.created_at.desc()).offset(offset).limit(first)
        result = await db.execute(stmt)
        items = result.scalars().all()

        edges = [
            ItemEdge(
                cursor=str(i + offset),
                node=ItemType(
                    id=strawberry.ID(str(p.id)),
                    name=p.name,
                    slug=p.slug,
                    description=p.description,
                    price=str(p.price),
                    sku=p.sku,
                    is_active=p.is_active,
                    created_at=p.created_at.isoformat(),
                ),
            )
            for i, p in enumerate(items)
        ]

        return ItemConnection(
            edges=edges,
            total_count=total,
            page_info=PageInfo(has_next_page=(offset + first) < total),
        )

    @strawberry.field
    async def component(self, info: Info, slug: str) -> ComponentType | None:
        """Permission check — returns whether a named component/feature is active."""
        user = info.context["user"]
        if not user:
            return None
        # For now, all components are active for authenticated users
        # Extend with real permission checks as needed
        return ComponentType(slug=slug, is_active=True)
