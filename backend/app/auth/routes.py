from fastapi import APIRouter

from app.auth.schemas import LoginRequest, LoginResponse
from app.auth.service import login


router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login_route(payload: LoginRequest) -> dict:
    return login(payload)
