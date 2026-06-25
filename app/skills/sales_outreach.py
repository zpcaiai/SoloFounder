from __future__ import annotations

from typing import Any

from app.skills.executor import run_skill


async def run(input: dict[str, Any]) -> dict[str, Any]:
    return await run_skill("sales_outreach", input)
