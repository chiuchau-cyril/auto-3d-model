"""Structured error response helpers matching contracts/openapi.yaml."""

from typing import Iterable

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ValidationErrorItem(BaseModel):
    field: str
    message: str


class ErrorResponse(BaseModel):
    errors: list[ValidationErrorItem]


def error_response(items: Iterable[tuple[str, str]], status_code: int) -> JSONResponse:
    payload = ErrorResponse(
        errors=[ValidationErrorItem(field=f, message=m) for f, m in items]
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def validation_error_response(items: Iterable[tuple[str, str]]) -> JSONResponse:
    return error_response(items, status_code=400)


def oda_unavailable_response() -> JSONResponse:
    return error_response(
        [("server", "ODA File Converter is not installed or ODAFC_EXEC_PATH is invalid")],
        status_code=503,
    )


def internal_error_response(message: str) -> JSONResponse:
    return error_response([("server", message)], status_code=500)
