import strawberry


@strawberry.type
class UserProfile:
    id: strawberry.ID
    username: str
    email: str


@strawberry.type
class UserType:
    id: strawberry.ID
    profile: UserProfile
    is_superuser: bool


@strawberry.type
class ItemType:
    id: strawberry.ID
    name: str
    slug: str
    description: str | None
    price: str
    sku: str | None
    is_active: bool
    created_at: str


@strawberry.type
class ItemEdge:
    cursor: str
    node: ItemType


@strawberry.type
class PageInfo:
    has_next_page: bool


@strawberry.type
class ItemConnection:
    edges: list[ItemEdge]
    total_count: int
    page_info: PageInfo


@strawberry.type
class FieldError:
    field: str
    messages: list[str]


@strawberry.type
class MutationResult:
    ok: bool
    errors: list[FieldError] | None = None


@strawberry.type
class ComponentType:
    slug: str
    is_active: bool
