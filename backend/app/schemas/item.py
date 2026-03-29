from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str = ""
    price: str
    sku: str | None = None
    is_active: bool = True


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: str | None = None
    sku: str | None = None
    is_active: bool | None = None


class ItemOut(BaseModel):
    id: str
    name: str
    slug: str
    description: str | None
    price: str
    sku: str | None
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, item) -> "ItemOut":
        return cls(
            id=str(item.id),
            name=item.name,
            slug=item.slug,
            description=item.description,
            price=str(item.price),
            sku=item.sku,
            is_active=item.is_active,
            created_at=item.created_at.isoformat(),
        )
