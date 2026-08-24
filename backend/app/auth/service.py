from app.auth.schemas import LoginRequest, LoginResponse, LoginUserResponse
from app.core.security import create_access_token
from app.users.service import authenticate_user


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
