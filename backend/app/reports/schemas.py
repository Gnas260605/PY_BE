from __future__ import annotations

from pydantic import BaseModel


class TechnicianWorkloadResponse(BaseModel):
    technician_id: int
    username: str
    ho_ten: str
    email: str | None
    active_tickets: int
    resolved_tickets: int
    closed_tickets: int
    total_assigned_tickets: int
