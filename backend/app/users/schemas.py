from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.security import validate_bcrypt_password_input


VALID_ROLES = {"USER", "TECHNICIAN", "ADMIN"}
VALID_STATUSES = {"ACTIVE", "INACTIVE"}


class UserResponse(BaseModel):
    id: int
    username: str
    ho_ten: str
    email: str | None
    vai_tro: str
    trang_thai: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListQuery(BaseModel):
    role: str | None = None
    status: str | None = None
    keyword: str | None = Field(default=None, max_length=100)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in VALID_ROLES:
            raise ValueError("role must be USER, TECHNICIAN, or ADMIN")
        return normalized

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in VALID_STATUSES:
            raise ValueError("status must be ACTIVE or INACTIVE")
        return normalized

    @field_validator("keyword")
    @classmethod
    def normalize_keyword(cls, value: str | None) -> str | None:
        if value is None:
            return value
        keyword = value.strip()
        return keyword or None


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=255)
    ho_ten: str = Field(min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=120)
    vai_tro: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("username must not be blank")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_bcrypt_password_input(value)

    @field_validator("ho_ten")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("ho_ten must not be blank")
        return normalized

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            return None
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("email must be a valid email address")
        return normalized

    @field_validator("vai_tro")
    @classmethod
    def validate_role(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_ROLES:
            raise ValueError("vai_tro must be USER, TECHNICIAN, or ADMIN")
        return normalized


class UpdateUserRequest(BaseModel):
    ho_ten: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=120)
    vai_tro: str | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("ho_ten")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("ho_ten must not be blank")
        return normalized

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            return None
        if "@" not in normalized or normalized.startswith("@") or normalized.endswith("@"):
            raise ValueError("email must be a valid email address")
        return normalized

    @field_validator("vai_tro")
    @classmethod
    def validate_role(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in VALID_ROLES:
            raise ValueError("vai_tro must be USER, TECHNICIAN, or ADMIN")
        return normalized


class UpdateUserStatusRequest(BaseModel):
    status: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in VALID_STATUSES:
            raise ValueError("status must be ACTIVE or INACTIVE")
        return normalized
