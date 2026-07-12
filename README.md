# Boilerworks FastAPI + Next.js

Async-first Python API with SQLAlchemy 2.0 and a Next.js frontend. Session-based auth, group-based permissions, GraphQL (Strawberry) consumed by Apollo Client, plus a REST API with OpenAPI docs.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12+) |
| Frontend | Next.js 16 (TypeScript, Apollo Client) |
| API | GraphQL (Strawberry) + REST |
| ORM | SQLAlchemy 2.0 async |
| Migrations | Alembic |
| Auth | Session-based (httpOnly cookies) |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Linter | Ruff (backend) |

## Quick Start

```bash
docker compose up -d --build

# Run migrations
docker compose exec api alembic upgrade head

# Create a superuser (via Python)
docker compose exec api python -c "
import asyncio
from app.database import async_session_factory
from app.models.user import User
async def seed():
    async with async_session_factory() as db:
        u = User(email='admin@test.com', username='admin', is_superuser=True)
        u.set_password('admin')
        db.add(u)
        await db.commit()
asyncio.run(seed())
"

# Open the frontend
open http://localhost:3000
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check |
| POST | `/app/gql/config` | Varies | GraphQL endpoint (Strawberry; used by the frontend via Apollo) |
| POST | `/app/auth1/login` | No | Login (returns session cookie) |
| POST | `/app/auth1/logout` | Yes | Logout |
| GET | `/app/auth1/me` | No | Current user |
| POST | `/app/auth1/session` | No | Token exchange (returns `Authorization` token for the frontend) |
| GET | `/api/items` | Yes | List items |
| POST | `/api/items` | Yes | Create item |
| GET | `/api/items/{slug}` | Yes | Get item |
| PUT | `/api/items/{slug}` | Yes | Update item |
| DELETE | `/api/items/{slug}` | Yes | Soft-delete item |

## Conventions

See [`bootstrap.md`](bootstrap.md) for full conventions.

---

Boilerworks is a [CONFLICT](https://weareconflict.com) brand. CONFLICT is a registered trademark of CONFLICT LLC.
