from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.security import validate_bcrypt_password_input


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=255)

    model_config = ConfigDict(extra="forbid")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("username must not be blank")
        return normalized

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return validate_bcrypt_password_input(value)


class LoginUserResponse(BaseModel):
    id: int
    username: str
    ho_ten: str
    email: str | None
    vai_tro: str
    trang_thai: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: LoginUserResponse

    model_config = ConfigDict(from_attributes=True)
