"""Application-wide configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings are read from backend/.env or real environment variables.

    Environment variables always win over values in the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "StaySmart API"
    environment: Literal["development", "test", "production"] = "development"

    database_url: str = Field(..., min_length=1)
    jwt_secret_key: SecretStr
    jwt_algorithm: Literal["HS256"] = "HS256"
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    cookie_name: str = "staysmart_access_token"
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cookie_domain: str | None = None

    @field_validator("jwt_secret_key")
    @classmethod
    def validate_jwt_secret(cls, value: SecretStr) -> SecretStr:
        secret = value.get_secret_value()
        blocked_values = {
            "change-me",
            "changeme",
            "secret",
            "development-secret",
            "your-secret-key",
        }
        if (
            len(secret) < 32
            or secret.strip().lower() in blocked_values
            or secret.strip().upper().startswith("CHANGE_ME")
        ):
            raise ValueError(
                "JWT_SECRET_KEY must be a random value of at least 32 characters."
            )
        return value

    @field_validator("cookie_domain")
    @classmethod
    def empty_domain_is_none(cls, value: str | None) -> str | None:
        return value or None

    @model_validator(mode="after")
    def production_safety_checks(self) -> "Settings":
        if "CHANGE_ME_DB_PASSWORD" in self.database_url:
            raise ValueError(
                "DATABASE_URL still contains the example password placeholder."
            )
        if self.cookie_samesite == "none" and not self.cookie_secure:
            raise ValueError("COOKIE_SECURE must be true when COOKIE_SAMESITE=none.")
        if self.environment == "production":
            if not self.cookie_secure:
                raise ValueError("COOKIE_SECURE must be true in production.")
            if not self.database_url.startswith("postgresql"):
                raise ValueError("Production DATABASE_URL must use PostgreSQL.")
            if "*" in self.allowed_origins:
                raise ValueError("Wildcard CORS origins are not allowed in production.")
        return self

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def access_token_seconds(self) -> int:
        return self.access_token_expire_minutes * 60


@lru_cache
def get_settings() -> Settings:
    """Return one cached Settings instance for the process."""
    return Settings()
