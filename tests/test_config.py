from __future__ import annotations

from app.core.config import get_settings, reset_settings_cache


def test_settings_defaults():
    reset_settings_cache()
    settings = get_settings()
    assert settings.environment == "development"
    assert settings.use_postgres is False
    assert settings.host == "0.0.0.0"
    assert settings.port == 8000
    assert settings.rate_limit_per_minute == 120
    assert settings.cors_origins == ["*"]
    assert settings.log_level == "INFO"


def test_settings_reads_aliases_and_parses_lists(monkeypatch):
    monkeypatch.setenv("REVENUEPILOT_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://host/db")
    monkeypatch.setenv("REVENUEPILOT_DB", "postgres")
    monkeypatch.setenv("CORS_ORIGINS", "https://a.example, https://b.example")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "60")
    monkeypatch.setenv("LOG_LEVEL", "debug")
    monkeypatch.setenv("REVENUEPILOT_REQUEST_TIMEOUT", "45.5")
    monkeypatch.setenv("REVENUEPILOT_SKIP_DB_MIGRATION", "1")
    reset_settings_cache()

    settings = get_settings()
    assert settings.is_production is True
    assert settings.use_postgres is True
    assert settings.cors_origins == ["https://a.example", "https://b.example"]
    assert settings.rate_limit_per_minute == 60
    assert settings.log_level == "DEBUG"
    assert settings.request_timeout == 45.5
    assert settings.skip_db_migration is True


def test_settings_coerces_invalid_int_to_default(monkeypatch):
    monkeypatch.setenv("PORT", "not-an-int")
    reset_settings_cache()
    assert get_settings().port == 8000
