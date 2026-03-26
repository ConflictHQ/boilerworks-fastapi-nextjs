# Claude -- Boilerworks FastAPI + Next.js

Primary conventions doc: [`bootstrap.md`](bootstrap.md)

Read it before writing any code.

## Stack

- **Backend**: FastAPI (Python 3.12+), SQLAlchemy 2.0 async, Alembic
- **Frontend**: Next.js 15 (App Router, TypeScript)
- **API**: REST (JSON, OpenAPI at /docs)
- **Auth**: Session-based (httpOnly cookies, SHA256 token hashing)
- **Permissions**: Group-based, checked via FastAPI `Depends()`
- **Database**: PostgreSQL 16 (via asyncpg)
- **Linter**: Ruff (backend), ESLint (frontend)

## Claude-specific notes

- All endpoints return `ApiResponse` format: `{ok, data, errors}`.
- Never expose integer PKs — use UUID `id` from `AuditBase`.
- Auth check via `Depends(require_auth)` on every endpoint.
- Permission checks via `Depends(require_permission("scope"))`.
- Soft-delete only: set `deleted_at`, never call `session.delete()`.
- Tests: pytest-asyncio + httpx AsyncClient + real Postgres.
