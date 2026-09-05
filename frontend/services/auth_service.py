from __future__ import annotations

from typing import Any

from core.auth_context import auth_context
from core.cache import service_cache
from core.http_client import http_client


class AuthService:
    async def health(self) -> dict[str, Any]:
        return await http_client.get("/health", auth_required=False)

    async def login(self, username: str, password: str) -> dict[str, Any]:
        response = await http_client.post(
            "/login",
            data={"username": username.strip(), "password": password},
            auth_required=False,
        )
        auth_context.set_session(response["access_token"], response["user"])
        service_cache.clear()
        return response

    def logout(self) -> None:
        auth_context.clear_session()
        service_cache.clear()

    def current_user(self) -> dict[str, Any] | None:
        return auth_context.get_current_user()

    def is_authenticated(self) -> bool:
        return auth_context.is_authenticated()


auth_service = AuthService()
