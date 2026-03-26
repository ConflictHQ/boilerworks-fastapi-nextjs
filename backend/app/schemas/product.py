from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str = ""
    price: str
    sku: str | None = None
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: str | None = None
    sku: str | None = None
    is_active: bool | None = None


class ProductOut(BaseModel):
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
    def from_model(cls, product) -> "ProductOut":
        return cls(
            id=str(product.id),
            name=product.name,
            slug=product.slug,
            description=product.description,
            price=str(product.price),
            sku=product.sku,
            is_active=product.is_active,
            created_at=product.created_at.isoformat(),
        )
