from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _field_name(location: tuple[str | int, ...]) -> str:
    filtered = [str(part) for part in location if part not in {"body", "query", "path"}]
    return ".".join(filtered) if filtered else "request"


def add_exception_handlers(app: FastAPI) -> None:
    """Register application-wide exception handlers matching the API contract."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            {
                "field": _field_name(tuple(error["loc"])),
                "message": error["msg"],
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=400,
            content={"message": "Invalid details supplied", "details": details},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "An unexpected error occurred"
        return JSONResponse(status_code=exc.status_code, content={"message": message})
