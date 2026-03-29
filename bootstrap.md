# Boilerworks FastAPI + Next.js -- Bootstrap

Primary conventions document. All agent shims point here.

---

## What's Already Built

| Layer | What's there |
|---|---|
| Backend | FastAPI + SQLAlchemy 2.0 async, Alembic migrations |
| Auth | Session-based (httpOnly cookies, SHA256 hashing), login/logout/me endpoints |
| Permissions | User, Group, Permission, UserGroup models; `require_permission()` dependency |
| API | REST endpoints returning `ApiResponse` (`{ok, data, errors}`) |
| Frontend | Next.js 15 with login, dashboard, products list |
| Infra | Docker Compose: api, ui, postgres, redis |
| CI | GitHub Actions: lint + tests |
| Example | Products CRUD (create, list, get, update, soft-delete) |

---

## Backend Conventions

### Models

```python
from app.models.base import AuditBase, SoftDeleteMixin

class Product(AuditBase, SoftDeleteMixin):
    __tablename__ = "products"
    name: Mapped[str] = mapped_column(String(255))
```

`AuditBase`: UUID `id`, `created_at`, `updated_at`. `SoftDeleteMixin`: `deleted_at`, `active()` filter.

### API Responses

All endpoints return: `{"ok": true, "data": {...}, "errors": null}`

### Auth

Session cookie auth. Every endpoint uses `Depends(require_auth)`. Permissions via `Depends(require_permission("product.view"))`.

### Tests

pytest-asyncio + httpx `AsyncClient` against real Postgres. Both auth and permission denied cases tested.

---

## Ports

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Frontend | http://localhost:3000 |
| OpenAPI Docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |
| Postgres | localhost:5432 |
| Redis | localhost:6379 |
