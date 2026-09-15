from __future__ import annotations

from typing import Any

from core.cache import cached, service_cache
from core.constants import TicketStatus
from core.http_client import http_client


NEXT_STATUSES = {
    TicketStatus.OPEN.value: [TicketStatus.ASSIGNED.value],
    TicketStatus.ASSIGNED.value: [TicketStatus.IN_PROGRESS.value],
    TicketStatus.IN_PROGRESS.value: [TicketStatus.RESOLVED.value],
    TicketStatus.RESOLVED.value: [TicketStatus.CLOSED.value],
    TicketStatus.CLOSED.value: [],
}

# In-memory fallback tickets for resilient local preview / offline demo
FALLBACK_TICKETS: list[dict[str, Any]] = [
    {
        "id": 1048,
        "title": "Máy in tầng 4 (Phòng Kế toán) không kết nối được mạng Wi-Fi",
        "description": "Máy in HP LaserJet tại phòng Kế toán báo offline và đèn tín hiệu mạng nhấp nháy đỏ từ 09:00 sáng nay.",
        "category": "INCIDENT",
        "priority": "URGENT",
        "status": "IN_PROGRESS",
        "user_id": 3,
        "technician_id": 2,
        "device_id": 2,
        "created_at": "2026-09-12 09:42:00",
        "updated_at": "2026-09-12 10:15:00",
    },
    {
        "id": 1045,
        "title": "Xin cấp quyền truy cập phần mềm ERP SAP phân hệ Kế toán",
        "description": "Cần cấp tài khoản phân hệ kế toán tổng hợp trên SAP S/4HANA cho nhân sự mới nhận việc.",
        "category": "SERVICE_REQUEST",
        "priority": "MEDIUM",
        "status": "ASSIGNED",
        "user_id": 3,
        "technician_id": 2,
        "device_id": 1,
        "created_at": "2026-09-11 14:15:00",
        "updated_at": "2026-09-11 16:30:00",
    },
    {
        "id": 1042,
        "title": "Bảo trì định kỳ máy chủ cơ sở dữ liệu và thiết bị lưu trữ NAS",
        "description": "Thực hiện vệ sinh phần cứng, kiểm tra sức khỏe ổ đĩa RAID và sao lưu toàn phần hệ thống.",
        "category": "MAINTENANCE",
        "priority": "LOW",
        "status": "RESOLVED",
        "user_id": 1,
        "technician_id": 4,
        "device_id": 3,
        "created_at": "2026-09-08 08:30:00",
        "updated_at": "2026-09-10 11:20:00",
    },
    {
        "id": 1039,
        "title": "Màn hình Dell UltraSharp 27 inch bị chớp sọc ngang",
        "description": "Màn hình xuất hiện các đường sọc ngang nhấp nháy sau 15 phút mở máy, đã đổi cáp DisplayPort nhưng không hết.",
        "category": "INCIDENT",
        "priority": "HIGH",
        "status": "OPEN",
        "user_id": 5,
        "technician_id": None,
        "device_id": 4,
        "created_at": "2026-09-13 08:00:00",
        "updated_at": "2026-09-13 08:00:00",
    },
]


class TicketService:
    async def list_tickets(
        self,
        *,
        status: str | None = None,
        priority: str | None = None,
        category: str | None = None,
        technician_id: int | None = None,
        user_id: int | None = None,
        keyword: str | None = None,
        refresh: bool = False,
    ) -> list[dict[str, Any]]:
        params = {
            key: value
            for key, value in {
                "status": status,
                "priority": priority,
                "category": category,
                "technician_id": technician_id,
                "user_id": user_id,
                "keyword": keyword,
            }.items()
            if value not in (None, "")
        }
        try:
            return await cached(
                ("tickets", tuple(sorted(params.items()))),
                lambda: http_client.get("/tickets", params=params),
                refresh=refresh,
            )
        except Exception:
            results = list(FALLBACK_TICKETS)
            if status and status != "ALL":
                results = [t for t in results if t.get("status") == status]
            if priority and priority != "ALL":
                results = [t for t in results if t.get("priority") == priority]
            if category and category != "ALL":
                results = [t for t in results if t.get("category") == category]
            if technician_id is not None:
                results = [t for t in results if t.get("technician_id") == technician_id]
            if user_id is not None:
                results = [t for t in results if t.get("user_id") == user_id]
            if keyword:
                kw = keyword.lower()
                results = [
                    t for t in results
                    if kw in (t.get("title", "").lower() + t.get("description", "").lower())
                ]
            return results

    async def create_ticket(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await http_client.post("/tickets", data=payload)
            service_cache.clear()
            return response
        except Exception:
            new_id = max([t["id"] for t in FALLBACK_TICKETS], default=1000) + 1
            new_ticket = {
                "id": new_id,
                "title": payload.get("title", "Yêu cầu mới"),
                "description": payload.get("description", ""),
                "category": payload.get("category", "INCIDENT"),
                "priority": payload.get("priority", "MEDIUM"),
                "status": "OPEN",
                "user_id": payload.get("user_id", 3),
                "technician_id": None,
                "device_id": payload.get("device_id", 2),
                "created_at": "Vừa tạo",
                "updated_at": "Vừa tạo",
            }
            FALLBACK_TICKETS.insert(0, new_ticket)
            service_cache.clear()
            return new_ticket

    async def get_ticket(self, ticket_id: int) -> dict[str, Any]:
        try:
            return await http_client.get(f"/tickets/{ticket_id}")
        except Exception:
            for t in FALLBACK_TICKETS:
                if t["id"] == ticket_id:
                    return t
            return FALLBACK_TICKETS[0]

    async def update_ticket(self, ticket_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await http_client.patch(f"/tickets/{ticket_id}", data=payload)
            service_cache.clear()
            return response
        except Exception:
            for t in FALLBACK_TICKETS:
                if t["id"] == ticket_id:
                    t.update(payload)
                    t["updated_at"] = "Vừa xong"
                    return t
            return {"id": ticket_id, **payload}

    async def assign_ticket(self, ticket_id: int, technician_id: int) -> dict[str, Any]:
        try:
            response = await http_client.patch(f"/tickets/{ticket_id}/assign", data={"technician_id": technician_id})
            service_cache.clear()
            return response
        except Exception:
            for t in FALLBACK_TICKETS:
                if t["id"] == ticket_id:
                    t["technician_id"] = technician_id
                    t["status"] = "ASSIGNED"
                    t["updated_at"] = "Vừa xong"
                    return t
            return {"id": ticket_id, "technician_id": technician_id, "status": "ASSIGNED"}

    async def update_status(self, ticket_id: int, status: str) -> dict[str, Any]:
        try:
            response = await http_client.patch(f"/tickets/{ticket_id}/status", data={"status": status})
            service_cache.clear()
            return response
        except Exception:
            for t in FALLBACK_TICKETS:
                if t["id"] == ticket_id:
                    t["status"] = status
                    t["updated_at"] = "Vừa xong"
                    return t
            return {"id": ticket_id, "status": status}

    async def close_ticket(self, ticket_id: int, note: str | None = None) -> dict[str, Any]:
        try:
            response = await http_client.patch(f"/tickets/{ticket_id}/close", data={"note": note})
            service_cache.clear()
            return response
        except Exception:
            for t in FALLBACK_TICKETS:
                if t["id"] == ticket_id:
                    t["status"] = "CLOSED"
                    t["close_note"] = note
                    t["updated_at"] = "Vừa xong"
                    return t
            return {"id": ticket_id, "status": "CLOSED", "note": note}

    async def get_history(self, ticket_id: int) -> list[dict[str, Any]]:
        try:
            return await http_client.get(f"/tickets/{ticket_id}/history")
        except Exception:
            return [
                {
                    "performed_at": "2026-09-12 10:15:00",
                    "action": "Cập nhật tiến độ",
                    "old_status": "ASSIGNED",
                    "new_status": "IN_PROGRESS",
                    "detail": "KTV Nguyễn Văn An đang xử lý dải IP switch tầng 4",
                },
                {
                    "performed_at": "2026-09-12 09:50:00",
                    "action": "Phân công kỹ thuật viên",
                    "old_status": "OPEN",
                    "new_status": "ASSIGNED",
                    "detail": "Đã phân công cho KTV Nguyễn Văn An",
                },
                {
                    "performed_at": "2026-09-12 09:42:00",
                    "action": "Khởi tạo yêu cầu",
                    "old_status": None,
                    "new_status": "OPEN",
                    "detail": "Người dùng tạo yêu cầu hỗ trợ",
                },
            ]

    @staticmethod
    def next_statuses(current_status: str | None) -> list[str]:
        return NEXT_STATUSES.get(current_status or "", [])


ticket_service = TicketService()

