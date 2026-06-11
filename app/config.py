from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "eagle_bank.db"


class Settings:
    """Application settings loaded from the environment with safe defaults."""

    def __init__(self) -> None:
        self.app_name = os.getenv("APP_NAME", "Eagle Bank REST API")
        self.api_version = os.getenv("API_VERSION", "1.0.0")
        self.database_url = os.getenv(
            "DATABASE_URL",
            f"sqlite:///{DEFAULT_DB_PATH}",
        )
        self.jwt_secret_key = os.getenv(
            "JWT_SECRET_KEY",
            "change-me-before-production",
        )
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_expiry_seconds = int(os.getenv("JWT_EXPIRY_SECONDS", "3600"))


settings = Settings()
