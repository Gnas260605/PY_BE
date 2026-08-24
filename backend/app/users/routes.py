from pydantic import ValidationError

from fastapi import APIRouter, Depends, Query, status

from app.core.auth import require_admin_user
from app.core.errors import BadRequestError
from app.users.schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    UpdateUserStatusRequest,
    UserListQuery,
    UserResponse,
)
from app.users.service import (
    create_user,
    get_user_detail,
    list_users,
    update_user,
    update_user_status,
)


router = APIRouter()


@router.get("/users", response_model=list[UserResponse], dependencies=[Depends(require_admin_user)])
def get_users(
    role: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None),
) -> list[dict]:
    try:
        query = UserListQuery(role=role, status=status_value, keyword=keyword)
    except ValidationError as exc:
        raise BadRequestError("INVALID_INPUT") from exc
    return list_users(query)


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_user)],
)
def create_user_route(payload: CreateUserRequest) -> dict:
    return create_user(payload)


@router.get("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin_user)])
def get_user_route(user_id: int) -> dict:
    return get_user_detail(user_id)


@router.patch("/users/{user_id}", response_model=UserResponse, dependencies=[Depends(require_admin_user)])
def update_user_route(user_id: int, payload: UpdateUserRequest) -> dict:
    return update_user(user_id, payload)


@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponse,
    dependencies=[Depends(require_admin_user)],
)
def update_user_status_route(user_id: int, payload: UpdateUserStatusRequest) -> dict:
    return update_user_status(user_id, payload)
