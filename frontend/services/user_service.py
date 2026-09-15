from __future__ import annotations

from typing import Any

from core.cache import cached, service_cache
from core.http_client import http_client

DEFAULT_USERS: list[dict[str, Any]] = [
    {
        "id": 1,
        "username": "admin",
        "ho_ten": "Quản trị hệ thống",
        "email": "admin@cs466.local",
        "vai_tro": "ADMIN",
        "trang_thai": "ACTIVE",
        "updated_at": "2026-09-12 08:00:00",
    },
    {
        "id": 2,
        "username": "tech01",
        "ho_ten": "Nguyễn Văn An",
        "email": "tech01@cs466.local",
        "vai_tro": "TECHNICIAN",
        "trang_thai": "ACTIVE",
        "updated_at": "2026-09-12 09:30:00",
    },
    {
        "id": 3,
        "username": "user01",
        "ho_ten": "Trần Thị Mai",
        "email": "user01@cs466.local",
        "vai_tro": "USER",
        "trang_thai": "ACTIVE",
        "updated_at": "2026-09-12 10:15:00",
    },
    {
        "id": 4,
        "username": "tech02",
        "ho_ten": "Lê Minh Tuấn",
        "email": "tech02@cs466.local",
        "vai_tro": "TECHNICIAN",
        "trang_thai": "ACTIVE",
        "updated_at": "2026-09-10 14:20:00",
    },
    {
        "id": 5,
        "username": "user02",
        "ho_ten": "Phạm Hoàng Nam",
        "email": "nam.pham@cs466.local",
        "vai_tro": "USER",
        "trang_thai": "ACTIVE",
        "updated_at": "2026-09-08 11:00:00",
    },
]


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
        try:
            return await cached(
                ("users", tuple(sorted(params.items()))),
                lambda: http_client.get("/users", params=params),
                refresh=refresh,
            )
        except Exception:
            # Fallback to in-memory demo users
            results = list(DEFAULT_USERS)
            if role and role != "ALL":
                results = [u for u in results if u.get("vai_tro") == role]
            if status and status != "ALL":
                results = [u for u in results if u.get("trang_thai") == status]
            if keyword:
                kw = keyword.lower()
                results = [
                    u for u in results
                    if kw in (u.get("username", "").lower() + u.get("ho_ten", "").lower() + u.get("email", "").lower())
                ]
            return results

    async def list_technicians(self, *, refresh: bool = False) -> list[dict[str, Any]]:
        return await self.list_users(role="TECHNICIAN", status="ACTIVE", refresh=refresh)

    async def create_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await http_client.post("/users", data=payload)
            service_cache.clear()
            return response
        except Exception:
            new_id = max([u["id"] for u in DEFAULT_USERS], default=0) + 1
            new_user = {
                "id": new_id,
                "username": payload.get("username"),
                "ho_ten": payload.get("ho_ten"),
                "email": payload.get("email"),
                "vai_tro": payload.get("vai_tro", "USER"),
                "trang_thai": "ACTIVE",
                "updated_at": "Vừa tạo",
            }
            DEFAULT_USERS.insert(0, new_user)
            service_cache.clear()
            return new_user

    async def get_user(self, user_id: int) -> dict[str, Any]:
        try:
            return await http_client.get(f"/users/{user_id}")
        except Exception:
            return next((u for u in DEFAULT_USERS if u["id"] == user_id), DEFAULT_USERS[0])

    async def update_user(self, user_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await http_client.patch(f"/users/{user_id}", data=payload)
            service_cache.clear()
            return response
        except Exception:
            for u in DEFAULT_USERS:
                if u["id"] == user_id:
                    u.update({k: v for k, v in payload.items() if v is not None})
            service_cache.clear()
            return {"status": "ok"}

    async def update_user_status(self, user_id: int, status: str) -> dict[str, Any]:
        try:
            response = await http_client.patch(f"/users/{user_id}/status", data={"status": status})
            service_cache.clear()
            return response
        except Exception:
            for u in DEFAULT_USERS:
                if u["id"] == user_id:
                    u["trang_thai"] = status
            service_cache.clear()
            return {"status": "ok"}


user_service = UserService()
