from fastapi import APIRouter

from fastapi import Depends

from app.auth.schemas import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
)
from app.auth.service import change_password, get_me, login
from app.core.auth import get_current_user
from app.core.rate_limiter import rate_limit


router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    dependencies=[Depends(rate_limit(max_requests=10, window_seconds=60))],
)
def login_route(payload: LoginRequest) -> dict:
    return login(payload)


@router.get("/auth/me", response_model=CurrentUserResponse)
def get_me_route(current_user: dict = Depends(get_current_user)) -> CurrentUserResponse:
    return get_me(current_user=current_user)


@router.patch("/auth/change-password", response_model=ChangePasswordResponse)
def change_password_route(
    payload: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
) -> ChangePasswordResponse:
    return change_password(payload, current_user=current_user)
