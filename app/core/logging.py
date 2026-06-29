from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

from app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """Emit log records as newline-delimited JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "source": f"{record.filename}:{record.lineno}",
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


def configure_logging() -> None:
    settings = get_settings()
    log_format = (getattr(settings, "log_format", None) or "text").lower()
    if log_format == "json":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logging.basicConfig(
            level=settings.log_level,
            handlers=[handler],
            force=False,
        )
    else:
        logging.basicConfig(
            level=settings.log_level,
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
            stream=sys.stdout,
            force=False,
        )
