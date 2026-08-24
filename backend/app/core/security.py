from __future__ import annotations

import bcrypt
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config import get_settings
from app.core.errors import UnauthorizedError


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    password_bytes = password.encode("utf-8")
    password_hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(password_bytes, password_hash_bytes)


def create_access_token(*, user_id: int, username: str, role: str) -> str:
    settings = get_settings()
    expire_at = datetime.now(UTC) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire_at,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except ExpiredSignatureError as exc:
        raise UnauthorizedError("TOKEN_EXPIRED") from exc
    except InvalidTokenError as exc:
        raise UnauthorizedError("INVALID_TOKEN") from exc

    if "sub" not in payload:
        raise UnauthorizedError("INVALID_TOKEN")
    return payload
