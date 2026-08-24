from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token
from app.db.connection import connection_scope
from app.users.repository import get_user_by_id


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("MISSING_TOKEN")

    payload = decode_access_token(credentials.credentials)
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("INVALID_TOKEN") from exc

    with connection_scope() as connection:
        user = get_user_by_id(connection, user_id)

    if user is None or user["trang_thai"] != "ACTIVE":
        raise UnauthorizedError("AUTH_FAILED")

    return user


def require_roles(*allowed_roles: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def dependency(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
        if current_user["vai_tro"] not in allowed_roles:
            raise ForbiddenError("FORBIDDEN")
        return current_user

    return dependency


def require_admin_user(
    current_user: dict[str, Any] = Depends(require_roles("ADMIN")),
) -> dict[str, Any]:
    return current_user
