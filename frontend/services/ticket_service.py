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
        return await cached(("tickets", tuple(sorted(params.items()))), lambda: http_client.get("/tickets", params=params), refresh=refresh)

    async def create_ticket(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = await http_client.post("/tickets", data=payload)
        service_cache.clear()
        return response

    async def get_ticket(self, ticket_id: int) -> dict[str, Any]:
        return await http_client.get(f"/tickets/{ticket_id}")

    async def update_ticket(self, ticket_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        response = await http_client.patch(f"/tickets/{ticket_id}", data=payload)
        service_cache.clear()
        return response

    async def assign_ticket(self, ticket_id: int, technician_id: int) -> dict[str, Any]:
        response = await http_client.patch(f"/tickets/{ticket_id}/assign", data={"technician_id": technician_id})
        service_cache.clear()
        return response

    async def update_status(self, ticket_id: int, status: str) -> dict[str, Any]:
        response = await http_client.patch(f"/tickets/{ticket_id}/status", data={"status": status})
        service_cache.clear()
        return response

    async def close_ticket(self, ticket_id: int, note: str | None = None) -> dict[str, Any]:
        response = await http_client.patch(f"/tickets/{ticket_id}/close", data={"note": note})
        service_cache.clear()
        return response

    async def get_history(self, ticket_id: int) -> list[dict[str, Any]]:
        return await http_client.get(f"/tickets/{ticket_id}/history")

    @staticmethod
    def next_statuses(current_status: str | None) -> list[str]:
        return NEXT_STATUSES.get(current_status or "", [])


ticket_service = TicketService()
