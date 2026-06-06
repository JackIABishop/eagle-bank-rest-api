from __future__ import annotations

from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> dict[str, str]:
    """Simple health endpoint to confirm the app is running."""

    return {"status": "ok"}
