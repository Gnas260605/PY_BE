from __future__ import annotations

from typing import Any

from core.cache import cached, service_cache
from core.http_client import http_client


class DeviceService:
    async def list_devices(
        self,
        *,
        status: str | None = None,
        type: str | None = None,
        keyword: str | None = None,
        refresh: bool = False,
    ) -> list[dict[str, Any]]:
        params = {key: value for key, value in {"status": status, "type": type, "keyword": keyword}.items() if value}
        return await cached(("devices", tuple(sorted(params.items()))), lambda: http_client.get("/devices", params=params), refresh=refresh)

    async def create_device(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = await http_client.post("/devices", data=payload)
        service_cache.clear()
        return response

    async def get_device(self, device_id: int) -> dict[str, Any]:
        return await http_client.get(f"/devices/{device_id}")

    async def update_device(self, device_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        response = await http_client.patch(f"/devices/{device_id}", data=payload)
        service_cache.clear()
        return response


device_service = DeviceService()
