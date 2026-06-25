from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, slots=True)
class Settings:
    environment: str
    database_url: str | None
    database_backend: str
    ai_provider: str
    log_level: str
    api_key: str | None

    @property
    def use_postgres(self) -> bool:
        return self.database_backend == "postgres" and bool(self.database_url)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        environment=os.getenv("REVENUEPILOT_ENV", "development"),
        database_url=os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL"),
        database_backend=os.getenv("REVENUEPILOT_DB", "memory").strip().lower(),
        ai_provider=os.getenv("REVENUEPILOT_AI_PROVIDER", "deterministic").strip().lower(),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        api_key=os.getenv("REVENUEPILOT_API_KEY"),
    )


def reset_settings_cache() -> None:
    get_settings.cache_clear()
