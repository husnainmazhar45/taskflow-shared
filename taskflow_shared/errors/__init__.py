"""Common error contracts and an optional Starlette HTTP adapter."""

from typing import Any

from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException


class ErrorDetail(BaseModel):
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ErrorResponse(BaseModel):
    error: ErrorDetail


class AppError(Exception):
    """Transport-independent error; the application chooses how to handle it."""

    def __init__(self, code: str, message: str) -> None:
        self.error = ErrorDetail(code=code, message=message)
        super().__init__(message)


class AppHTTPException(HTTPException):
    """Preserve Starlette/FastAPI's existing ``detail.error`` response envelope."""

    detail: Any

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        detail = ErrorResponse(error=ErrorDetail(code=code, message=message))
        super().__init__(status_code, headers=headers)
        self.detail = detail.model_dump()
