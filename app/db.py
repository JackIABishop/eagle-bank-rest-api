from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base class for ORM models."""


def _sqlite_connect_args(database_url: str) -> dict[str, object]:
    if not database_url.startswith("sqlite"):
        return {}

    # SQLite is file-based, so brief GUI inspection or reload overlap can
    # temporarily lock the file. A timeout makes startup a bit more forgiving.
    return {"check_same_thread": False, "timeout": 30}


def configure_sqlite(engine: Engine) -> None:
    """Apply SQLite-specific safety settings to an engine."""

    if not str(engine.url).startswith("sqlite"):
        return

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
        # SQLite does not enforce foreign keys unless this pragma is enabled.
        # Turning it on keeps the take-home closer to how a relational system
        # would protect account/user integrity in a fuller deployment.
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


engine = create_engine(settings.database_url, connect_args=_sqlite_connect_args(settings.database_url))
configure_sqlite(engine)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for a single request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
