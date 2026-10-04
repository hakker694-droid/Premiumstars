"""Application configuration, loaded from environment variables / .env file."""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    bot_token: str = Field(..., min_length=20)
    admin_ids: str = ""
    database_url: str = "sqlite+aiosqlite:///./star_market.db"
    auto_create_tables: bool = True
    log_level: str = "INFO"
    log_dir: str = "logs"
    throttle_interval: float = 0.6
    support_username: str = ""

    @field_validator("database_url")
    @classmethod
    def _normalize_db_url(cls, value: str) -> str:
        value = value.strip()
        if value.startswith("postgres://"):
            return "postgresql+asyncpg://" + value[len("postgres://"):]
        if value.startswith("postgresql://"):
            return "postgresql+asyncpg://" + value[len("postgresql://"):]
        if value.startswith("sqlite://"):
            return value.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return value

    @field_validator("support_username")
    @classmethod
    def _strip_at(cls, value: str) -> str:
        return value.strip().lstrip("@")

    @property
    def admin_id_list(self) -> list[int]:
        ids: list[int] = []
        for part in self.admin_ids.replace(";", ",").split(","):
            part = part.strip()
            if part.isdigit():
                ids.append(int(part))
        return ids


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
