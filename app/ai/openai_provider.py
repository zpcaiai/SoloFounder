from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from app.ai.anthropic_provider import _JSON_SYSTEM_PROMPT, extract_json_object
from app.core.config import get_settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_TOKENS = 4096


@dataclass
class OpenAIProvider:
    """Calls the OpenAI Chat Completions API and returns a JSON object string.

    Configure via environment:
      OPENAI_API_KEY            - required
      REVENUEPILOT_OPENAI_MODEL - model id (default: gpt-4o-mini)
      OPENAI_BASE_URL           - optional override for Azure / compatible gateways
      REVENUEPILOT_MAX_TOKENS   - response cap (default: 4096)

    Uses response_format={"type": "json_object"} so the model returns strict
    JSON; the executor re-validates against each skill's schema.
    """

    model: str = field(
        default_factory=lambda: os.getenv("REVENUEPILOT_OPENAI_MODEL")
        or os.getenv("REVENUEPILOT_MODEL", DEFAULT_MODEL)
    )
    max_tokens: int = field(default_factory=lambda: int(os.getenv("REVENUEPILOT_MAX_TOKENS", DEFAULT_MAX_TOKENS)))
    api_key: str | None = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    base_url: str | None = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL"))
    _client: Any = field(default=None, init=False, repr=False)

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import openai  # type: ignore
            except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional dep
                raise RuntimeError(
                    "The 'openai' package is required for OpenAIProvider. "
                    "Install it with: pip install openai"
                ) from exc
            if not self.api_key:
                raise RuntimeError("OPENAI_API_KEY is not set.")
            kwargs: dict[str, Any] = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = openai.OpenAI(**kwargs)
        return self._client

    def _call_sync(self, prompt: str) -> str:
        client = self._get_client()
        completion = client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _JSON_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content or ""

    async def generate_json(
        self,
        *,
        skill_name: str,
        prompt: str,
        input_payload: dict[str, Any],
        output_schema: dict[str, Any],
    ) -> str:
        settings = get_settings()
        last_error: Exception | None = None
        for attempt in range(settings.ai_max_retries + 1):
            try:
                raw = await asyncio.wait_for(
                    asyncio.to_thread(self._call_sync, prompt),
                    timeout=settings.ai_timeout,
                )
                json_text = extract_json_object(raw)
                return json.dumps(json.loads(json_text), ensure_ascii=False)
            except TimeoutError as exc:
                last_error = exc
                logger.warning("OpenAI attempt %s timed out", attempt + 1)
            except Exception as exc:
                last_error = exc
                logger.warning("OpenAI attempt %s failed: %s", attempt + 1, exc.__class__.__name__)
            if attempt < settings.ai_max_retries:
                await asyncio.sleep(min(2**attempt, 8))
        raise RuntimeError(
            f"OpenAI call failed after {settings.ai_max_retries + 1} attempts"
        ) from last_error
