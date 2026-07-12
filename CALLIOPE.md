# Calliope — Boilerworks FastAPI + Next.js
<!-- Agent shim for https://github.com/calliopeai/calliope-cli -->

Primary conventions doc: [`bootstrap.md`](bootstrap.md)
Context seed: [`memory.md`](memory.md)

Read both before writing any code.

---

## Project-specific notes

- Backend: FastAPI (Python 3.12+), SQLAlchemy 2.0 async, Alembic. Frontend: Next.js 16 (App Router, TypeScript, Apollo Client). PostgreSQL 16 via asyncpg.
- API: GraphQL (Strawberry at `/app/gql/config`) + REST (JSON, OpenAPI at `/docs`).
- Session auth (httpOnly cookies, SHA256 token hashing); group-based permissions checked via FastAPI `Depends()`.
- All REST endpoints return the `ApiResponse` format: `{ok, data, errors}`. Never expose integer PKs — use the UUID `id` from `AuditBase`.
- Auth via `Depends(require_auth)` on every endpoint; permissions via `Depends(require_permission("scope"))`.
- Soft-delete only: set `deleted_at`, never `session.delete()`. Ruff (backend) + ESLint (frontend); tests: pytest-asyncio + httpx `AsyncClient` + real Postgres.
