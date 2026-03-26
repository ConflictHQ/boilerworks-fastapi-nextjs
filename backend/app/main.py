from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from .api.auth import router as auth_router
from .api.health import router as health_router
from .api.products import router as products_router
from .config import settings
from .graphql.context import get_context
from .graphql.schema import schema

app = FastAPI(title="Boilerworks FastAPI", version="0.1.0", docs_url="/docs" if settings.debug else None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL endpoint — matches the frontend's expected path
graphql_router = GraphQLRouter(schema, context_getter=get_context, graphql_ide="graphiql" if settings.debug else None)
app.include_router(graphql_router, prefix="/app/gql/config")

# Auth endpoint — matches the frontend's token exchange path
app.include_router(auth_router, prefix="/app/auth1")

# REST API (still available alongside GraphQL)
app.include_router(health_router)
app.include_router(products_router, prefix="/api")
