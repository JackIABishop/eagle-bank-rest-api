from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
import sys

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db import Base, configure_sqlite, get_db
from app.main import app


@pytest.fixture()
async def client(tmp_path) -> Generator[httpx.AsyncClient, None, None]:
    """Provide an API client backed by an isolated temporary SQLite database."""

    # Creates a temporary SQLite database for the test environment
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    configure_sqlite(engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Overide the app's normal database dependecy 
    app.dependency_overrides[get_db] = override_get_db

    # Create an async client that can make requests to the test server
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client

    # Clean up 
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
