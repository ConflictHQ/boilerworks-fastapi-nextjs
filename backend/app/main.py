from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.auth import router as auth_router
from .api.health import router as health_router
from .api.products import router as products_router
from .config import settings

app = FastAPI(title="Boilerworks FastAPI", version="0.1.0", docs_url="/docs" if settings.debug else None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router, prefix="/api")
app.include_router(products_router, prefix="/api")
