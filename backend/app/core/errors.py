import logging

import mysql.connector
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


class ContractNotLockedError(Exception):
    def __init__(self, message: str = "CONTRACT_NOT_LOCKED") -> None:
        self.message = message
        super().__init__(message)


class ApiError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class BadRequestError(ApiError):
    def __init__(self, detail: str = "INVALID_INPUT") -> None:
        super().__init__(400, detail)


class UnauthorizedError(ApiError):
    def __init__(self, detail: str = "AUTH_FAILED") -> None:
        super().__init__(401, detail)


class ForbiddenError(ApiError):
    def __init__(self, detail: str = "FORBIDDEN") -> None:
        super().__init__(403, detail)


class NotFoundError(ApiError):
    def __init__(self, detail: str = "NOT_FOUND") -> None:
        super().__init__(404, detail)


class ConflictError(ApiError):
    def __init__(self, detail: str = "CONFLICT") -> None:
        super().__init__(409, detail)


def register_exception_handlers(app: FastAPI) -> None:
    def _sanitize_validation_errors(errors: list[dict]) -> list[dict]:
        sanitized: list[dict] = []
        for item in errors:
            sanitized_item = dict(item)
            ctx = sanitized_item.get("ctx")
            if ctx:
                sanitized_item["ctx"] = {
                    key: str(value) for key, value in ctx.items()
                }
            sanitized.append(sanitized_item)
        return sanitized

    @app.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(ContractNotLockedError)
    async def contract_not_locked_handler(
        request: Request, exc: ContractNotLockedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=501,
            content={
                "detail": exc.message,
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "detail": "INVALID_INPUT",
                "path": str(request.url.path),
                "errors": _sanitize_validation_errors(exc.errors()),
            },
        )

    @app.exception_handler(mysql.connector.Error)
    async def mysql_error_handler(
        request: Request, exc: mysql.connector.Error
    ) -> JSONResponse:
        logger.exception("Unhandled database error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "INTERNAL_SERVER_ERROR",
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled application error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "INTERNAL_SERVER_ERROR",
                "path": str(request.url.path),
            },
        )
