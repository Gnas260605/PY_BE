from __future__ import annotations

import logging

import mysql.connector

from app.core.errors import BadRequestError, ConflictError, NotFoundError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.db.connection import connection_scope
from app.users import repository
from app.users.schemas import CreateUserRequest, UpdateUserRequest, UpdateUserStatusRequest, UserListQuery


logger = logging.getLogger(__name__)


def authenticate_user(username: str, password: str) -> dict:
    normalized_username = username.strip()
    if not normalized_username or not password:
        raise BadRequestError("INVALID_INPUT")

    with connection_scope() as connection:
        user = repository.get_user_by_username(connection, normalized_username)

    if user is None:
        logger.info("LOGIN_FAILED username=%s reason=user_not_found", normalized_username)
        raise UnauthorizedError("AUTH_FAILED")

    if user["trang_thai"] != "ACTIVE":
        logger.info("LOGIN_FAILED username=%s reason=inactive", normalized_username)
        raise UnauthorizedError("AUTH_FAILED")

    try:
        password_valid = verify_password(password, str(user["password_hash"]))
    except Exception as exc:
        logger.exception(
            "LOGIN_FAILED username=%s reason=password_hash_error",
            normalized_username,
        )
        raise UnauthorizedError("AUTH_FAILED") from exc

    if not password_valid:
        logger.info("LOGIN_FAILED username=%s reason=invalid_password", normalized_username)
        raise UnauthorizedError("AUTH_FAILED")

    logger.info("LOGIN_SUCCESS user_id=%s username=%s", user["id"], user["username"])
    user.pop("password_hash", None)
    return user


def list_users(query: UserListQuery) -> list[dict]:
    with connection_scope() as connection:
        return repository.list_users(
            connection,
            role=query.role,
            status=query.status,
            keyword=query.keyword,
        )


def create_user(payload: CreateUserRequest) -> dict:
    with connection_scope() as connection:
        duplicate = repository.find_duplicate_user(
            connection,
            username=payload.username,
            email=str(payload.email) if payload.email else None,
        )
        if duplicate is not None:
            raise ConflictError("DUPLICATE_USER")

        try:
            user_id = repository.create_user(
                connection,
                username=payload.username,
                password_hash=hash_password(payload.password),
                ho_ten=payload.ho_ten,
                email=str(payload.email) if payload.email else None,
                vai_tro=payload.vai_tro,
                trang_thai="ACTIVE",
            )
            connection.commit()
        except ValueError as exc:
            connection.rollback()
            raise BadRequestError("INVALID_INPUT") from exc
        except mysql.connector.IntegrityError as exc:
            connection.rollback()
            raise ConflictError("DUPLICATE_USER") from exc
        except Exception:
            connection.rollback()
            raise
        created_user = repository.get_user_by_id(connection, user_id)

    logger.info("USER_CREATED user_id=%s username=%s role=%s", user_id, payload.username, payload.vai_tro)

    if created_user is None:
        raise NotFoundError("USER_NOT_FOUND")
    return created_user


def get_user_detail(user_id: int) -> dict:
    with connection_scope() as connection:
        user = repository.get_user_by_id(connection, user_id)
    if user is None:
        raise NotFoundError("USER_NOT_FOUND")
    return user


def update_user(user_id: int, payload: UpdateUserRequest) -> dict:
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise BadRequestError("INVALID_INPUT")

    with connection_scope() as connection:
        existing_user = repository.get_user_by_id(connection, user_id)
        if existing_user is None:
            raise NotFoundError("USER_NOT_FOUND")

        duplicate = repository.find_duplicate_user(
            connection,
            email=updates.get("email"),
            exclude_user_id=user_id,
        )
        if duplicate is not None:
            raise ConflictError("DUPLICATE_USER")

        try:
            repository.update_user(connection, user_id, updates)
            connection.commit()
        except mysql.connector.IntegrityError as exc:
            connection.rollback()
            raise ConflictError("DUPLICATE_USER") from exc
        except Exception:
            connection.rollback()
            raise
        updated_user = repository.get_user_by_id(connection, user_id)

    logger.info("USER_UPDATED user_id=%s fields=%s", user_id, ",".join(sorted(updates.keys())))

    if updated_user is None:
        raise NotFoundError("USER_NOT_FOUND")
    return updated_user


def update_user_status(user_id: int, payload: UpdateUserStatusRequest) -> dict:
    with connection_scope() as connection:
        existing_user = repository.get_user_by_id(connection, user_id)
        if existing_user is None:
            raise NotFoundError("USER_NOT_FOUND")

        try:
            repository.update_user_status(connection, user_id, payload.status)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        updated_user = repository.get_user_by_id(connection, user_id)

    logger.info("USER_STATUS_CHANGED user_id=%s status=%s", user_id, payload.status)

    if updated_user is None:
        raise NotFoundError("USER_NOT_FOUND")
    return updated_user
