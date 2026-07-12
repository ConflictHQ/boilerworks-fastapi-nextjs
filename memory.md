# Boilerworks Memory

This file is the **AI context seed** for the Boilerworks FastAPI + Next.js template. It captures decisions, constraints, and non-obvious facts that are not derivable from reading a single file.

For conventions and patterns, see [`bootstrap.md`](bootstrap.md).

---

## Template purpose

Full-stack async Python starter: FastAPI backend (SQLAlchemy 2.0 async, Alembic), Next.js 16 frontend with Apollo Client. Ships with session auth, group-based permissions, a Strawberry GraphQL layer, and an Items REST CRUD example.

## Key architectural decisions

| Decision | Why |
|---|---|
| GraphQL (Strawberry) mounted at `/app/gql/config` | The frontend was ported from the django-nextjs template, which serves its schema at that path — kept to reuse the frontend unchanged |
| Auth router mounted at `/app/auth1` | Same reason: mirrors the Django `auth1` app paths (`login`, `logout`, `me`, `session`) the frontend expects |
| REST alongside GraphQL | Items CRUD under `/api` returns `ApiResponse` (`{ok, data, errors}`); GraphQL is what the frontend actually uses |
| Session auth, not JWT | Session tokens stored SHA-256-hashed; httpOnly cookie; `/app/auth1/session` also returns the token as an `Authorization` header value for the frontend token store |
| UUID primary keys (`AuditBase`) | Never expose integer PKs |
| Soft deletes (`SoftDeleteMixin`) | Set `deleted_at`; never `session.delete()` |

## Things that bite newcomers

- **The frontend still carries django-nextjs leftovers** — `frontend/graphql/employees/*` and `frontend/graphql/permissions/*` query types the FastAPI schema does not define (`backend/app/graphql/types.py` has only UserProfile/UserType/ItemType/ItemConnection), and `frontend/lib/auth/auth0.ts` is stubbed to `null` while `@auth0/nextjs-auth0` stays in package.json. See fleet-audit issue #24.
- **`backend/pyproject.toml` declares a broken build backend** (`hatchling.backends`; real module is `hatchling.build`), so `uv sync` / `pip install -e .` fail. CI and the Dockerfile install deps around it instead of building the package. Known P0 in issue #24 — fix the backend string rather than adding more workarounds.
- **CI is backend-only** (ruff + pytest with Postgres/Redis services); a broken Next build still passes green.
- **No seed module** — create the initial superuser with the inline `python -c` snippet in README Quick Start.

## Release status

Template is functional; CI green. Open hygiene and drift items are tracked in fleet-audit issue #24.
