from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=255)


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
