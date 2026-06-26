from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 4096

_JSON_SYSTEM_PROMPT = (
    "You are a precise JSON generation engine for RevenuePilot OS. "
    "Return ONLY a single JSON object that conforms to the provided schema. "
    "Do not include prose, explanations, or markdown code fences."
)


def extract_json_object(text: str) -> str:
    """Extract the outermost JSON object from arbitrary model text.

    Handles leading/trailing prose, ```json fences, and an optional missing
    leading brace (useful when the assistant turn is prefilled with "{").
    Returns the JSON substring (not parsed). Raises ValueError if none found.
    """
    cleaned = text.strip()

    # Strip markdown code fences if present.
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)[1] if cleaned.count("```") >= 2 else cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    start = cleaned.find("{")
    if start == -1:
        raise ValueError("No JSON object found in model output.")

    # Walk braces while respecting string literals and escapes.
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(cleaned)):
        char = cleaned[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return cleaned[start : index + 1]

    raise ValueError("Unbalanced JSON object in model output.")


@dataclass
class AnthropicProvider:
    """Calls the Anthropic Messages API and returns a JSON object string.

    Configure via environment:
      ANTHROPIC_API_KEY   - required
      REVENUEPILOT_MODEL  - model id (default: claude-sonnet-4-6)
      REVENUEPILOT_MAX_TOKENS - response cap (default: 4096)
    """

    model: str = field(default_factory=lambda: os.getenv("REVENUEPILOT_MODEL", DEFAULT_MODEL))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("REVENUEPILOT_MAX_TOKENS", DEFAULT_MAX_TOKENS)))
    api_key: str | None = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    _client: Any = field(default=None, init=False, repr=False)

    def _get_client(self) -> Any:
        if self._client is None:
            try:
                import anthropic  # type: ignore
            except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional dep
                raise RuntimeError(
                    "The 'anthropic' package is required for AnthropicProvider. "
                    "Install it with: pip install anthropic"
                ) from exc
            if not self.api_key:
                raise RuntimeError("ANTHROPIC_API_KEY is not set.")
            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def _call_sync(self, prompt: str) -> str:
        client = self._get_client()
        message = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=_JSON_SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": "{"},  # prefill to force a JSON object
            ],
        )
        text = "".join(getattr(block, "text", "") for block in message.content)
        return "{" + text

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
                # Validate it parses; re-serialize to normalize. Executor re-validates against the schema.
                return json.dumps(json.loads(json_text), ensure_ascii=False)
            except TimeoutError as exc:
                last_error = exc
                logger.warning("Anthropic attempt %s timed out", attempt + 1)
            except Exception as exc:
                last_error = exc
                logger.warning("Anthropic attempt %s failed: %s", attempt + 1, exc.__class__.__name__)
            if attempt < settings.ai_max_retries:
                await asyncio.sleep(min(2**attempt, 8))
        raise RuntimeError(
            f"Anthropic call failed after {settings.ai_max_retries + 1} attempts"
        ) from last_error
