from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """Base class for ORM models."""


engine = create_engine(
    settings.database_url,
    # SQLite is file-based, so brief GUI inspection or reload overlap can
    # temporarily lock the file. A timeout makes startup a bit more forgiving.
    connect_args={"check_same_thread": False, "timeout": 30}
    if settings.database_url.startswith("sqlite")
    else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for a single request."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
