# Boilerworks FastAPI + Next.js

Async-first Python API with SQLAlchemy 2.0 and a Next.js frontend. Session-based auth, group-based permissions, REST API with OpenAPI docs.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12+) |
| Frontend | Next.js 15 (TypeScript) |
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
| POST | `/api/auth/login` | No | Login (returns session cookie) |
| POST | `/api/auth/logout` | Yes | Logout |
| GET | `/api/auth/me` | No | Current user |
| GET | `/api/products` | Yes | List products |
| POST | `/api/products` | Yes | Create product |
| GET | `/api/products/{slug}` | Yes | Get product |
| PUT | `/api/products/{slug}` | Yes | Update product |
| DELETE | `/api/products/{slug}` | Yes | Soft-delete product |

## Conventions

See [`bootstrap.md`](bootstrap.md) for full conventions.

---

Boilerworks is a [Conflict](https://weareconflict.com) brand. CONFLICT is a registered trademark of Conflict LLC.
