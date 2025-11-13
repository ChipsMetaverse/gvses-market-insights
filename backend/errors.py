from pydantic import BaseModel
from typing import Any, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette import status


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None
    correlation_id: str


def _json(status_code: int, code: str, message: str, cid: str, details: Any = None):
    return JSONResponse(
        status_code=status_code,
        content={"error": ErrorPayload(code=code, message=message, details=details, correlation_id=cid).model_dump()}
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    cid = getattr(request.state, "correlation_id", "unknown")
    return _json(exc.status_code, "http_error", exc.detail, cid)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    cid = getattr(request.state, "correlation_id", "unknown")
    return _json(status.HTTP_422_UNPROCESSABLE_ENTITY, "validation_error", "Request validation failed.", cid, exc.errors())


async def unhandled_exception_handler(request: Request, exc: Exception):
    cid = getattr(request.state, "correlation_id", "unknown")
    return _json(status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", "An unexpected error occurred.", cid)
