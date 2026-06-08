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
from app.routers.users import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Tables are created when the application starts rather than on import,
    # which keeps local tests isolated from the real development database.
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title=settings.app_name, version=settings.api_version, lifespan=lifespan)
    add_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(account_router)

    return app


app = create_app()
