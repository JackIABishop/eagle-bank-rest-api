from __future__ import annotations

from fastapi import FastAPI

from app.config import settings
from app.db import Base, engine
from app.errors import add_exception_handlers
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(title=settings.app_name, version=settings.api_version)
    add_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(auth_router)

    @app.on_event("startup")
    def startup() -> None:
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()
