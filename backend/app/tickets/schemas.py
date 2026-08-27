from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_TICKET_CATEGORIES = {"INCIDENT", "SERVICE_REQUEST", "MAINTENANCE"}
VALID_TICKET_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "URGENT"}
VALID_TICKET_STATUSES = {"OPEN", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"}


class TicketSummaryResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    priority: str
    status: str
    user_id: int
    device_id: int | None
    technician_id: int | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    closed_at: datetime | None


class TicketListQuery(BaseModel):
    status: str | None = None
    priority: str | None = None
    category: str | None = None
    technician_id: int | None = None
    user_id: int | None = None
    keyword: str | None = Field(default=None, max_length=200)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in VALID_TICKET_STATUSES:
            raise ValueError("status must be OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, or CLOSED")
        return normalized

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in VALID_TICKET_PRIORITIES:
            raise ValueError("priority must be LOW, MEDIUM, HIGH, or URGENT")
        return normalized

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in VALID_TICKET_CATEGORIES:
            raise ValueError("category must be INCIDENT, SERVICE_REQUEST, or MAINTENANCE")
        return normalized

    @field_validator("keyword")
    @classmethod
    def normalize_keyword(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        return normalized or None


class CreateTicketRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    device_id: int | None = None
    category: str
    priority: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "description")
    @classmethod
    def strip_required(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("required field must not be blank")
        return normalized

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_TICKET_CATEGORIES:
            raise ValueError("category must be INCIDENT, SERVICE_REQUEST, or MAINTENANCE")
        return normalized

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_TICKET_PRIORITIES:
            raise ValueError("priority must be LOW, MEDIUM, HIGH, or URGENT")
        return normalized


class TicketDetailUser(BaseModel):
    id: int
    username: str
    ho_ten: str
    email: str | None
    vai_tro: str
    trang_thai: str


class TicketDetailDevice(BaseModel):
    id: int
    ma_thiet_bi: str
    ten_thiet_bi: str
    loai_thiet_bi: str | None
    vi_tri: str | None
    trang_thai: str
    mo_ta: str | None


class TicketDetailResponse(TicketSummaryResponse):
    creator: TicketDetailUser
    device: TicketDetailDevice | None
    technician: TicketDetailUser | None


class AssignTicketRequest(BaseModel):
    technician_id: int

    model_config = ConfigDict(extra="forbid")


class UpdateTicketStatusRequest(BaseModel):
    status: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_TICKET_STATUSES:
            raise ValueError("status must be OPEN, ASSIGNED, IN_PROGRESS, RESOLVED, or CLOSED")
        return normalized


class CloseTicketRequest(BaseModel):
    note: str | None = Field(default=None, max_length=500)

    model_config = ConfigDict(extra="forbid")

    @field_validator("note")
    @classmethod
    def normalize_note(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        return normalized or None


class TicketHistoryResponse(BaseModel):
    id: int
    action: str
    old_status: str | None
    new_status: str | None
    detail: str | None
    performed_by: int | None
    performed_at: datetime


class UpdateTicketRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    category: str | None = None
    priority: str | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("title", "description")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("required field must not be blank")
        return normalized

    @field_validator("category")
    @classmethod
    def validate_category(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in VALID_TICKET_CATEGORIES:
            raise ValueError("category must be INCIDENT, SERVICE_REQUEST, or MAINTENANCE")
        return normalized

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in VALID_TICKET_PRIORITIES:
            raise ValueError("priority must be LOW, MEDIUM, HIGH, or URGENT")
        return normalized
