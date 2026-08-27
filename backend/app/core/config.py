from functools import lru_cache

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "cs466-service-desk"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    log_level: str = "INFO"
    mysql_host: str = Field(
        default="127.0.0.1",
        validation_alias=AliasChoices("MYSQL_HOST", "DB_HOST"),
    )
    mysql_port: int = Field(
        default=3306,
        validation_alias=AliasChoices("MYSQL_PORT", "DB_PORT"),
    )
    mysql_database: str = Field(
        default="cs466_helpdesk",
        validation_alias=AliasChoices("MYSQL_DATABASE", "DB_NAME"),
    )
    mysql_user: str = Field(
        default="root",
        validation_alias=AliasChoices("MYSQL_USER", "DB_USER"),
    )
    mysql_password: str = Field(
        default="change-me",
        validation_alias=AliasChoices("MYSQL_PASSWORD", "DB_PASSWORD"),
    )
    jwt_secret_key: str = Field(
        validation_alias=AliasChoices("JWT_SECRET_KEY"),
    )

    jwt_algorithm: str = Field(
        default="HS256",
        validation_alias=AliasChoices("JWT_ALGORITHM"),
    )
    jwt_expire_minutes: int = Field(
        default=480,
        validation_alias=AliasChoices("JWT_EXPIRE_MINUTES"),
    )

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("app_port", "mysql_port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        if not 1 <= value <= 65535:
            raise ValueError("port must be between 1 and 65535")
        return value

    @field_validator("jwt_expire_minutes")
    @classmethod
    def validate_jwt_expire_minutes(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("JWT_EXPIRE_MINUTES must be greater than 0")
        return value

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        secret = value.strip()
        if not secret:
            raise ValueError("JWT_SECRET_KEY is required")
        return secret


@lru_cache
def get_settings() -> Settings:
    return Settings()
