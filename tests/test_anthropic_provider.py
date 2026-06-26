from __future__ import annotations

import asyncio

import pytest

from app.ai.anthropic_provider import AnthropicProvider
from app.core.config import reset_settings_cache


async def _run_with_retries(monkeypatch, max_retries: int, failures: int) -> tuple[str, int]:
    reset_settings_cache()
    monkeypatch.setenv("REVENUEPILOT_AI_MAX_RETRIES", str(max_retries))
    provider = AnthropicProvider(api_key="test", model="test")
    calls: list[str] = []

    def _call_sync(prompt: str) -> str:
        calls.append(prompt)
        if len(calls) <= failures:
            raise RuntimeError("boom")
        return '{"ok": true}'

    async def _noop_sleep(_delay: float) -> None:
        return None

    monkeypatch.setattr(provider, "_call_sync", _call_sync)
    monkeypatch.setattr(asyncio, "sleep", _noop_sleep)

    result = await provider.generate_json(
        skill_name="test",
        prompt="hello",
        input_payload={},
        output_schema={},
    )
    return result, len(calls)


def test_retries_until_success(monkeypatch):
    result, calls = asyncio.run(_run_with_retries(monkeypatch, max_retries=2, failures=2))
    assert calls == 3
    assert result == '{"ok": true}'


def test_fails_after_max_retries(monkeypatch):
    with pytest.raises(RuntimeError, match="failed after 3 attempts"):
        asyncio.run(_run_with_retries(monkeypatch, max_retries=2, failures=5))
