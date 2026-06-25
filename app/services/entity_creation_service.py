from __future__ import annotations

from typing import Any
from uuid import uuid4


async def create_entities_from_skill_output(
    *,
    user_id: str,
    project_id: str | None,
    output: dict[str, Any],
) -> list[dict[str, Any]]:
    created: list[dict[str, Any]] = []
    for entity in output.get("entities_to_create", []):
        payload = dict(entity.get("payload", {}))
        payload.setdefault("user_id", user_id)
        if project_id:
            payload.setdefault("project_id", str(project_id))
        created.append(
            {
                "id": str(uuid4()),
                "entity_type": entity["entity_type"],
                "payload": payload,
            }
        )
    return created
