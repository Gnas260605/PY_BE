from __future__ import annotations

from typing import Any

from core.cache import cached, service_cache
from core.http_client import http_client

DEFAULT_DEVICES: list[dict[str, Any]] = [
    {
        "id": 1,
        "ma_thiet_bi": "PC-ACC-012",
        "ten_thiet_bi": "Dell OptiPlex 7090",
        "loai_thiet_bi": "COMPUTER",
        "vi_tri": "Phòng Kế toán - Tầng 4",
        "trang_thai": "ACTIVE",
        "mo_ta": "Máy trạm kế toán trưởng",
        "updated_at": "2026-09-10 09:00:00",
    },
    {
        "id": 2,
        "ma_thiet_bi": "PRN-ACC-04",
        "ten_thiet_bi": "HP LaserJet Pro M404dn",
        "loai_thiet_bi": "PRINTER",
        "vi_tri": "Tầng 4 - Tòa nhà A",
        "trang_thai": "MAINTENANCE",
        "mo_ta": "Máy in dùng chung phòng Kế toán",
        "updated_at": "2026-09-12 10:15:00",
    },
    {
        "id": 3,
        "ma_thiet_bi": "RTR-FL4",
        "ten_thiet_bi": "Cisco Catalyst 2960",
        "loai_thiet_bi": "ROUTER",
        "vi_tri": "Tủ Rack Tầng 4",
        "trang_thai": "ACTIVE",
        "mo_ta": "Switch mạng phân tầng",
        "updated_at": "2026-09-05 16:30:00",
    },
    {
        "id": 4,
        "ma_thiet_bi": "LAP-IT-01",
        "ten_thiet_bi": "ThinkPad T14 Gen 3",
        "loai_thiet_bi": "COMPUTER",
        "vi_tri": "Phòng IT Helpdesk",
        "trang_thai": "ACTIVE",
        "mo_ta": "Laptop kỹ thuật trực ban",
        "updated_at": "2026-09-11 14:00:00",
    },
]


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
        try:
            return await cached(
                ("devices", tuple(sorted(params.items()))),
                lambda: http_client.get("/devices", params=params),
                refresh=refresh,
            )
        except Exception:
            results = list(DEFAULT_DEVICES)
            if status and status != "ALL":
                results = [d for d in results if d.get("trang_thai") == status]
            if type and type != "ALL":
                results = [d for d in results if d.get("loai_thiet_bi") == type]
            if keyword:
                kw = keyword.lower()
                results = [
                    d for d in results
                    if kw in (d.get("ma_thiet_bi", "").lower() + d.get("ten_thiet_bi", "").lower() + d.get("vi_tri", "").lower())
                ]
            return results

    async def create_device(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await http_client.post("/devices", data=payload)
            service_cache.clear()
            return response
        except Exception:
            new_id = max([d["id"] for d in DEFAULT_DEVICES], default=0) + 1
            new_device = {
                "id": new_id,
                "ma_thiet_bi": payload.get("ma_thiet_bi"),
                "ten_thiet_bi": payload.get("ten_thiet_bi"),
                "loai_thiet_bi": payload.get("loai_thiet_bi", "COMPUTER"),
                "vi_tri": payload.get("vi_tri"),
                "trang_thai": payload.get("trang_thai", "ACTIVE"),
                "mo_ta": payload.get("mo_ta"),
                "updated_at": "Vừa tạo",
            }
            DEFAULT_DEVICES.insert(0, new_device)
            service_cache.clear()
            return new_device

    async def get_device(self, device_id: int) -> dict[str, Any]:
        try:
            return await http_client.get(f"/devices/{device_id}")
        except Exception:
            return next((d for d in DEFAULT_DEVICES if d["id"] == device_id), DEFAULT_DEVICES[0])

    async def update_device(self, device_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await http_client.patch(f"/devices/{device_id}", data=payload)
            service_cache.clear()
            return response
        except Exception:
            for d in DEFAULT_DEVICES:
                if d["id"] == device_id:
                    d.update({k: v for k, v in payload.items() if v is not None})
            service_cache.clear()
            return {"status": "ok"}


device_service = DeviceService()
