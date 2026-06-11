from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401
from app.config import settings
from app.db import Base, engine
from app.errors import add_exception_handlers
from app.routers.accounts import router as account_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.transactions import router as transaction_router
from app.routers.users import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Tables are created when the application starts rather than on import,
    # which keeps local tests isolated from the real development database.
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
        description=(
            "A versioned REST API demonstrating authentication, resource ownership, "
            "validation, persistence, and transactional business rules."
        ),
        lifespan=lifespan,
        contact={"name": "Jack Bishop"},
    )
    add_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(account_router)
    app.include_router(transaction_router)

    return app


app = create_app()


@app.get("/", tags=["meta"], include_in_schema=False)
def api_index() -> dict[str, str]:
    """Expose useful entry points for people exploring the API."""

    return {
        "name": settings.app_name,
        "version": settings.api_version,
        "health": "/health",
        "documentation": "/docs",
        "openapi": "/openapi.json",
    }
