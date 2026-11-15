# Boilerworks FastAPI + Next.js

Async-first Python API with SQLAlchemy 2.0 and a Next.js frontend. Session-based auth, group-based permissions, GraphQL (Strawberry) consumed by Apollo Client, plus a REST API with OpenAPI docs.

## Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12+) |
| Frontend | Next.js 16 (TypeScript, Apollo Client, `@calliopelabs/ui`, Storybook 10) |
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

## The Calliope AI happy path

This template builds on the Calliope AI design system and platform. A new app made from it starts on the shared UI library, deploys on Astrolift, shows its Storybook in the Calliope AI UX front door, and receives library upgrades automatically.

### What the template ships

- **The design system.** `frontend/` depends on [`@calliopelabs/ui`](https://www.npmjs.com/package/@calliopelabs/ui). `app/globals.css` imports its Tailwind preset (tokens, theme map, `dark:` on `data-mode`, base layer). The root layout renders `AppearanceScript` in `<head>` and mounts `AppearanceProvider` and `UIProvider`, the latter through `ui-app/providers/UiEnvironment.tsx`, which gives the library `next/link` and translates every string it renders from the `ui` namespace of `messages/<locale>.json`.
- **The product.** `ui-app/product.ts` defines the app with `defineProduct`: a neutral `boilerworks` brand and the navigation model the sidebar and breadcrumb read.
- **The shell and patterns from the library.** `AppShell`, `Sidebar`, `BrandMark`, `UserMenu`, `Breadcrumbs`, `PageHeader`, `DataTable`, `EmptyState`, `ErrorState`, `LoadingState`, `StatusBadge`, `AppearancePicker`, and the primitives `Button`, `Input`, `Checkbox`, `DropdownMenu`, `Popover`, `Skeleton`, `AlertDialog` and `Drawer`.
- **The app's own layer, `ui-app/`.** The shadcn components the library does not have (`primitives/`), the signed-in frame (`shell/AppFrame.tsx`), and the two `TableController`s for the library `DataTable` (`table/`: `paginatedController` over `usePaginatedQuery`, used by the GraphQL `items` table, and `useLocalTable` for rows already in hand).
- **A Storybook with gates.** `npm run storybook` in `frontend/` (Storybook 10, `@storybook/nextjs-vite`). `npm test` renders every story with the a11y addon's WCAG A and AA checks and fails on a violation, and requires a sibling story for every component in `ui-app/`. CI runs lint, format, typecheck, tests and both builds for `frontend/`.
- **Astrolift manifests.** Astrolift builds one image per app, so there are three: `astrolift.toml` for the API (`backend/Dockerfile`, migrations on start, Postgres), `frontend/astrolift.toml` for the web (`frontend/Dockerfile`, Next.js standalone), and `storybook/` (Dockerfile, nginx, `astrolift.toml`) for the Storybook.
- **Upgrades.** `.github/dependabot.yml` checks `frontend/` daily and puts `@calliopelabs/*` releases in their own pull request.

### Rename the product

1. `frontend/ui-app/product.ts`: set `id` (lowercase slug, also the appearance storage key) and `name`; pick an `accent` (a family accent or the product's own) and a `sidebar` colour, or spread a shipped brand (`astroliftBrand`, `zentinelleBrand`, ...). Edit `NAV` for the app's areas and rows; each row's `key` is its message key in the `nav` namespace.
2. `frontend/ui-app/shell/AppFrame.tsx`: the brand mark (a lucide icon by default; an `<img>` of the logo works).
3. Replace `boilerworks-app` in `astrolift.toml`, `frontend/astrolift.toml` and `storybook/astrolift.toml` (`name`, `slug`, `display_name`, `repo`, the managed service name).

### Deploy with Astrolift

```shell
astro app register --project-id <uuid> --source-repo <org>/<repo>
astro app register -f frontend/astrolift.toml --manifest-path frontend/astrolift.toml \
  --project-id <uuid> --source-repo <org>/<repo>
astro app register -f storybook/astrolift.toml --manifest-path storybook/astrolift.toml \
  --project-id <uuid> --source-repo <org>/<repo>
astro app secrets create APP_DATABASE_URL boilerworks-app --stdin   # and the others astrolift.toml lists
```

Pushes to `main` deploy through the managed workflow. The browser calls the API directly, so the web's `NEXT_PUBLIC_API_ROOT` is the API's public URL (compiled into the bundle, so a build argument of the web app) and the API's `APP_CORS_ORIGINS` is the web's. Build and check the images locally:

```shell
docker build -t app-api backend
docker build -t app-web --build-arg NEXT_PUBLIC_API_ROOT=http://localhost:8000 frontend
docker build -f storybook/Dockerfile -t app-storybook .
docker run --rm -p 8080:8080 app-storybook        # http://localhost:8080, /healthz answers ok
```

### Add the Storybook to the front door

The front door, [calliopeai/calliope-ux](https://github.com/calliopeai/calliope-ux), composes each app's Storybook as a section. Once the Storybook app is deployed, add an entry to its `catalogs.json` and push:

```json
{
  "id": "boilerworks-app",
  "title": "Boilerworks",
  "group": "web",
  "kind": "storybook",
  "repo": "ConflictHQ/boilerworks-fastapi-nextjs",
  "app": "storybook-boilerworks-app",
  "upstream": "web.conflict-storybook-boilerworks-app.svc.cluster.local:8080"
}
```

`upstream` is `<workload>.conflict-<app slug>.svc.cluster.local:8080`; the workload here is `web`.

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
