from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_DEVICE_STATUSES = {"ACTIVE", "MAINTENANCE", "BROKEN", "INACTIVE"}


class DeviceResponse(BaseModel):
    id: int
    ma_thiet_bi: str
    ten_thiet_bi: str
    loai_thiet_bi: str | None
    vi_tri: str | None
    trang_thai: str
    mo_ta: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviceListQuery(BaseModel):
    status: str | None = None
    type: str | None = Field(default=None, alias="type")
    keyword: str | None = Field(default=None, max_length=150)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in VALID_DEVICE_STATUSES:
            raise ValueError("status must be ACTIVE, MAINTENANCE, BROKEN, or INACTIVE")
        return normalized

    @field_validator("type")
    @classmethod
    def normalize_type(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        return normalized or None

    @field_validator("keyword")
    @classmethod
    def normalize_keyword(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        return normalized or None


class CreateDeviceRequest(BaseModel):
    ma_thiet_bi: str = Field(min_length=1, max_length=50)
    ten_thiet_bi: str = Field(min_length=1, max_length=150)
    loai_thiet_bi: str | None = Field(default=None, max_length=100)
    vi_tri: str | None = Field(default=None, max_length=150)
    trang_thai: str = "ACTIVE"
    mo_ta: str | None = None

    model_config = ConfigDict(extra="forbid")



    @field_validator("ma_thiet_bi", "ten_thiet_bi")
    @classmethod
    def strip_required(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("required field must not be blank")
        return normalized

    @field_validator("loai_thiet_bi", "vi_tri", "mo_ta")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        return normalized or None

    @field_validator("trang_thai")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_DEVICE_STATUSES:
            raise ValueError("trang_thai must be ACTIVE, MAINTENANCE, BROKEN, or INACTIVE")
        return normalized


class UpdateDeviceRequest(BaseModel):
    ma_thiet_bi: str | None = Field(default=None, min_length=1, max_length=50)
    ten_thiet_bi: str | None = Field(default=None, min_length=1, max_length=150)
    loai_thiet_bi: str | None = Field(default=None, max_length=100)
    vi_tri: str | None = Field(default=None, max_length=150)
    trang_thai: str | None = None
    mo_ta: str | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("ma_thiet_bi", "ten_thiet_bi")
    @classmethod
    def strip_required(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("required field must not be blank")
        return normalized

    @field_validator("loai_thiet_bi", "vi_tri", "mo_ta")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        return normalized or None

    @field_validator("trang_thai")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in VALID_DEVICE_STATUSES:
            raise ValueError("trang_thai must be ACTIVE, MAINTENANCE, BROKEN, or INACTIVE")
        return normalized
