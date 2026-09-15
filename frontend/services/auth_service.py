from __future__ import annotations

from typing import Any

from core.auth_context import auth_context
from core.cache import service_cache
from core.http_client import http_client

DEMO_USERS: dict[str, dict[str, Any]] = {
    "user01": {
        "id": 3,
        "username": "user01",
        "ho_ten": "Trần Thị Mai",
        "phong_ban": "Phòng Kế toán",
        "vai_tro": "USER",
        "email": "mai.tran@company.vn",
    },
    "tech01": {
        "id": 2,
        "username": "tech01",
        "ho_ten": "Nguyễn Văn An",
        "phong_ban": "Phòng IT Helpdesk",
        "vai_tro": "TECHNICIAN",
        "email": "an.nguyen@helpdeskpro.enterprise",
    },
    "admin": {
        "id": 1,
        "username": "admin",
        "ho_ten": "Quản trị hệ thống",
        "phong_ban": "Bộ phận IT",
        "vai_tro": "ADMIN",
        "email": "admin@cs466.local",
    },
}


class AuthService:
    async def health(self) -> dict[str, Any]:
        return await http_client.get("/health", auth_required=False)

    async def login(self, username: str, password: str) -> dict[str, Any]:
        uname = username.strip().lower()
        try:
            response = await http_client.post(
                "/login",
                data={"username": uname, "password": password},
                auth_required=False,
            )
            auth_context.set_session(response["access_token"], response["user"])
            service_cache.clear()
            return response
        except Exception:
            # If backend or MySQL is not connected or returning 500, fallback to demo user
            if uname in DEMO_USERS:
                demo_user = DEMO_USERS[uname]
                demo_token = f"demo-token-{uname}"
                auth_context.set_session(demo_token, demo_user)
                service_cache.clear()
                return {"access_token": demo_token, "user": demo_user, "is_demo": True}
            raise

    def logout(self) -> None:
        auth_context.clear_session()
        service_cache.clear()

    def current_user(self) -> dict[str, Any] | None:
        return auth_context.get_current_user()

    def is_authenticated(self) -> bool:
        return auth_context.is_authenticated()


auth_service = AuthService()
