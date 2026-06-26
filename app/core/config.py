from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Settings(BaseModel):
    """Validated, environment-driven configuration for RevenuePilot OS."""

    model_config = ConfigDict(extra="ignore")

    environment: str = Field(default="development")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    database_url: str | None = Field(default=None)
    database_backend: str = Field(default="memory")
    db_pool_min: int = Field(default=2)
    db_pool_max: int = Field(default=10)
    db_connect_timeout: int = Field(default=10)
    skip_db_migration: bool = Field(default=False)

    ai_provider: str = Field(default="deterministic")
    ai_timeout: float = Field(default=60.0)
    ai_max_retries: int = Field(default=2)
    model: str = Field(default="claude-sonnet-4-6")

    api_key: str | None = Field(default=None)
    api_key_header: str = Field(default="X-API-Key")
    supabase_jwt_secret: str | None = Field(default=None)
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    rate_limit_per_minute: int = Field(default=120)
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="text")
    request_timeout: float = Field(default=30.0)
    max_request_body_size: int = Field(default=1_000_000)
    metrics_enabled: bool = Field(default=False)

    @property
    def use_postgres(self) -> bool:
        return self.database_backend == "postgres" and bool(self.database_url)

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("log_level", mode="after")
    @classmethod
    def _normalize_log_level(cls, value: str) -> str:
        return value.upper()


def _int_env(*values: str | None, default: int) -> int:
    for value in values:
        if value is None:
            continue
        value = value.strip()
        if value:
            try:
                return int(value)
            except ValueError:
                continue
    return default


def _float_env(*values: str | None, default: float) -> float:
    for value in values:
        if value is None:
            continue
        value = value.strip()
        if value:
            try:
                return float(value)
            except ValueError:
                continue
    return default


def _bool_env(*values: str | None, default: bool) -> bool:
    for value in values:
        if value is None:
            continue
        value = value.strip().lower()
        if value in {"1", "true", "yes", "on"}:
            return True
        if value in {"0", "false", "no", "off"}:
            return False
    return default


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    env = os.environ
    return Settings(
        environment=env.get("REVENUEPILOT_ENV", "development"),
        host=env.get("HOST") or env.get("REVENUEPILOT_HOST", "0.0.0.0"),
        port=_int_env(env.get("PORT"), env.get("REVENUEPILOT_PORT"), default=8000),
        database_url=env.get("DATABASE_URL") or env.get("POSTGRES_URL") or env.get("NEON_DATABASE_URL"),
        database_backend=env.get("REVENUEPILOT_DB", "memory").strip().lower(),
        db_pool_min=_int_env(env.get("DB_POOL_MIN"), env.get("REVENUEPILOT_DB_POOL_MIN"), default=2),
        db_pool_max=_int_env(env.get("DB_POOL_MAX"), env.get("REVENUEPILOT_DB_POOL_MAX"), default=10),
        db_connect_timeout=_int_env(
            env.get("DB_CONNECT_TIMEOUT"), env.get("REVENUEPILOT_DB_CONNECT_TIMEOUT"), default=10
        ),
        skip_db_migration=_bool_env(
            env.get("REVENUEPILOT_SKIP_DB_MIGRATION"), env.get("SKIP_DB_MIGRATION"), default=False
        ),
        ai_provider=env.get("REVENUEPILOT_AI_PROVIDER", "deterministic").strip().lower(),
        ai_timeout=_float_env(env.get("REVENUEPILOT_AI_TIMEOUT"), env.get("AI_TIMEOUT"), default=60.0),
        ai_max_retries=_int_env(env.get("REVENUEPILOT_AI_MAX_RETRIES"), env.get("AI_MAX_RETRIES"), default=2),
        model=env.get("REVENUEPILOT_MODEL") or env.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"),
        api_key=env.get("REVENUEPILOT_API_KEY"),
        api_key_header=env.get("API_KEY_HEADER") or env.get("REVENUEPILOT_API_KEY_HEADER", "X-API-Key"),
        supabase_jwt_secret=env.get("SUPABASE_JWT_SECRET") or env.get("REVENUEPILOT_JWT_SECRET"),
        cors_origins=[
            item.strip()
            for item in (env.get("CORS_ORIGINS") or env.get("REVENUEPILOT_CORS_ORIGINS") or "*").split(",")
            if item.strip()
        ],
        rate_limit_per_minute=_int_env(
            env.get("RATE_LIMIT_PER_MINUTE"), env.get("REVENUEPILOT_RATE_LIMIT_PER_MINUTE"), default=120
        ),
        log_level=env.get("LOG_LEVEL", "INFO"),
        log_format=env.get("LOG_FORMAT") or env.get("REVENUEPILOT_LOG_FORMAT", "text"),
        request_timeout=_float_env(
            env.get("REVENUEPILOT_REQUEST_TIMEOUT"), env.get("REQUEST_TIMEOUT"), default=30.0
        ),
        max_request_body_size=_int_env(
            env.get("REVENUEPILOT_MAX_REQUEST_BODY_SIZE"),
            env.get("MAX_REQUEST_BODY_SIZE"),
            default=1_000_000,
        ),
        metrics_enabled=_bool_env(
            env.get("METRICS_ENABLED"), env.get("REVENUEPILOT_METRICS_ENABLED"), default=False
        ),
    )


def reset_settings_cache() -> None:
    get_settings.cache_clear()
