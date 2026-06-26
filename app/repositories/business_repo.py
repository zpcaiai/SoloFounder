from __future__ import annotations

from typing import Any

from uuid import UUID, uuid4

from app.repositories.models import utcnow


class BusinessEntity:
    __slots__ = ("id", "user_id", "project_id", "entity_type", "data", "created_at", "updated_at")

    def __init__(
        self,
        *,
        user_id: str,
        entity_type: str,
        data: dict[str, Any],
        project_id: str | UUID | None = None,
    ) -> None:
        self.id: UUID = uuid4()
        self.user_id = user_id
        self.project_id = project_id
        self.entity_type = entity_type
        self.data = data
        self.created_at = utcnow()
        self.updated_at = utcnow()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "project_id": str(self.project_id) if self.project_id else None,
            "entity_type": self.entity_type,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class InMemoryBusinessRepository:
    def __init__(self) -> None:
        self._records: dict[UUID, BusinessEntity] = {}

    async def create(
        self,
        *,
        user_id: str,
        entity_type: str,
        data: dict[str, Any],
        project_id: str | UUID | None = None,
    ) -> dict[str, Any]:
        entity = BusinessEntity(
            user_id=user_id,
            entity_type=entity_type,
            data=data,
            project_id=project_id,
        )
        self._records[entity.id] = entity
        return entity.to_dict()

    async def get(self, *, entity_id: UUID, user_id: str) -> dict[str, Any]:
        entity = self._records[entity_id]
        if entity.user_id != user_id:
            raise PermissionError("Entity does not belong to this user.")
        return entity.to_dict()

    async def list(
        self,
        *,
        user_id: str,
        entity_type: str,
        project_id: str | UUID | None = None,
    ) -> list[dict[str, Any]]:
        results = [
            entity.to_dict()
            for entity in self._records.values()
            if entity.user_id == user_id
            and entity.entity_type == entity_type
            and (project_id is None or str(entity.project_id) == str(project_id))
        ]
        results.sort(key=lambda r: r["created_at"], reverse=True)
        return results

    async def update(
        self,
        *,
        entity_id: UUID,
        user_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        entity = self._records[entity_id]
        if entity.user_id != user_id:
            raise PermissionError("Entity does not belong to this user.")
        entity.data.update(data)
        entity.updated_at = utcnow()
        return entity.to_dict()

    async def delete(self, *, entity_id: UUID, user_id: str) -> None:
        entity = self._records[entity_id]
        if entity.user_id != user_id:
            raise PermissionError("Entity does not belong to this user.")
        del self._records[entity_id]

    async def count(
        self,
        *,
        user_id: str,
        entity_type: str,
        project_id: str | UUID | None = None,
    ) -> int:
        return sum(
            1
            for entity in self._records.values()
            if entity.user_id == user_id
            and entity.entity_type == entity_type
            and (project_id is None or str(entity.project_id) == str(project_id))
        )

    def reset(self) -> None:
        self._records.clear()


business_repo = InMemoryBusinessRepository()
