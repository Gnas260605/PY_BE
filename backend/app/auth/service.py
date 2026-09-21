import logging

from app.auth.schemas import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
    LoginUserResponse,
    RegisterRequest,
)
from app.core.errors import BadRequestError, NotFoundError, UnauthorizedError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.connection import connection_scope
from app.users import repository as users_repository
from app.users.schemas import CreateUserRequest
from app.users.service import authenticate_user, create_user


logger = logging.getLogger(__name__)


def login(payload: LoginRequest) -> LoginResponse:
    user = authenticate_user(payload.username, payload.password)
    access_token = create_access_token(
        user_id=int(user["id"]),
        username=str(user["username"]),
        role=str(user["vai_tro"]),
    )
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=LoginUserResponse(**user),
    )


def get_me(*, current_user: dict) -> CurrentUserResponse:
    return CurrentUserResponse(**current_user)


def change_password(
    payload: ChangePasswordRequest,
    *,
    current_user: dict,
) -> ChangePasswordResponse:
    if payload.current_password == payload.new_password:
        raise BadRequestError("PASSWORD_UNCHANGED")

    user_id = int(current_user["id"])
    with connection_scope() as connection:
        user = users_repository.get_user_with_password_by_id(connection, user_id)
        if user is None:
            raise NotFoundError("USER_NOT_FOUND")
        if user["trang_thai"] != "ACTIVE":
            raise UnauthorizedError("AUTH_FAILED")

        if not verify_password(payload.current_password, str(user["password_hash"])):
            raise UnauthorizedError("AUTH_FAILED")

        try:
            users_repository.update_password_hash(
                connection,
                user_id,
                hash_password(payload.new_password),
            )
            connection.commit()
        except Exception:
            connection.rollback()
            raise

    logger.info("PASSWORD_CHANGED user_id=%s", user_id)
    return ChangePasswordResponse(status="ok")


def register(payload: RegisterRequest) -> LoginResponse:
    user_req = CreateUserRequest(
        username=payload.username,
        password=payload.password,
        ho_ten=payload.ho_ten,
        email=payload.email,
        vai_tro="USER",
    )
    user = create_user(user_req)
    access_token = create_access_token(
        user_id=int(user["id"]),
        username=str(user["username"]),
        role=str(user["vai_tro"]),
    )
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=LoginUserResponse(**user),
    )

