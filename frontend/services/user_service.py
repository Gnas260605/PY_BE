from __future__ import annotations

from typing import Any

from core.cache import cached, service_cache
from core.http_client import http_client


class UserService:
    async def list_users(
        self,
        *,
        role: str | None = None,
        status: str | None = None,
        keyword: str | None = None,
        refresh: bool = False,
    ) -> list[dict[str, Any]]:
        params = {key: value for key, value in {"role": role, "status": status, "keyword": keyword}.items() if value}
        return await cached(("users", tuple(sorted(params.items()))), lambda: http_client.get("/users", params=params), refresh=refresh)

    async def list_technicians(self, *, refresh: bool = False) -> list[dict[str, Any]]:
        return await self.list_users(role="TECHNICIAN", status="ACTIVE", refresh=refresh)

    async def create_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = await http_client.post("/users", data=payload)
        service_cache.clear()
        return response

    async def get_user(self, user_id: int) -> dict[str, Any]:
        return await http_client.get(f"/users/{user_id}")

    async def update_user(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        response = await http_client.patch(f"/users/{user_id}", data=payload)
        service_cache.clear()
        return response

    async def update_user_status(self, user_id: int, status: str) -> dict[str, Any]:
        response = await http_client.patch(f"/users/{user_id}/status", data={"status": status})
        service_cache.clear()
        return response


user_service = UserService()
