from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from app.repositories.postgres import BUSINESS_TABLES, PostgresBusinessRepository


class FakePostgresPool:
    def __init__(self) -> None:
        self.rows: dict[str, list[dict[str, Any]]] = {}

    async def fetchrow(self, query: str, *args: Any) -> dict[str, Any] | None:
        if "insert into public." in query:
            return self._insert(query, args)
        if query.strip().startswith("select * from public."):
            table = self._table(query)
            entity_id = args[0]
            return next((row for row in self.rows.get(table, []) if row["id"] == entity_id), None)
        if query.strip().startswith("update public."):
            return self._update(query, args)
        if query.strip().startswith("select count(*)"):
            table = self._table(query)
            user_id = args[0]
            project_id = args[1] if len(args) > 1 else None
            rows = self._filter_rows(table, user_id=user_id, project_id=project_id)
            return {"count": len(rows)}
        raise AssertionError(f"Unexpected query: {query}")

    async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]:
        table = self._table(query)
        user_id = args[0]
        project_id = args[1] if len(args) > 1 else None
        return self._filter_rows(table, user_id=user_id, project_id=project_id)

    async def execute(self, query: str, *args: Any) -> str:
        table = self._table(query)
        entity_id, user_id = args
        before = len(self.rows.get(table, []))
        self.rows[table] = [
            row for row in self.rows.get(table, []) if not (row["id"] == entity_id and row["user_id"] == user_id)
        ]
        deleted = before - len(self.rows[table])
        return f"DELETE {deleted}"

    def _insert(self, query: str, args: tuple[Any, ...]) -> dict[str, Any]:
        table = self._table(query)
        columns_text = query.split("(", 1)[1].split(")", 1)[0]
        columns = [column.strip() for column in columns_text.split(",")]
        row = self._blank_row(table)
        row.update(dict(zip(columns, args, strict=True)))
        self.rows.setdefault(table, []).append(row)
        return row

    def _update(self, query: str, args: tuple[Any, ...]) -> dict[str, Any] | None:
        table = self._table(query)
        assignments = query.split(" set ", 1)[1].split(" where ", 1)[0]
        columns = [assignment.split("=", 1)[0].strip() for assignment in assignments.split(",")]
        entity_id = args[-2]
        user_id = args[-1]
        for row in self.rows.get(table, []):
            if row["id"] == entity_id and row["user_id"] == user_id:
                row.update(dict(zip(columns, args[:-2], strict=True)))
                row["updated_at"] = datetime.now(UTC)
                return row
        return None

    def _blank_row(self, table: str) -> dict[str, Any]:
        config = next(item for item in BUSINESS_TABLES.values() if item.table == table)
        row: dict[str, Any] = {
            "id": uuid4(),
            "user_id": None,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        if config.has_project_id:
            row["project_id"] = None
        for column in config.columns:
            row[column] = "{}" if column in config.json_columns else None
        return row

    def _filter_rows(self, table: str, *, user_id: str, project_id: UUID | None) -> list[dict[str, Any]]:
        rows = [row for row in self.rows.get(table, []) if row["user_id"] == user_id]
        if project_id is not None:
            rows = [row for row in rows if row.get("project_id") == project_id]
        return rows

    def _table(self, query: str) -> str:
        return query.split("public.", 1)[1].split()[0]


class FakePoolWrapper:
    def __init__(self, pool: FakePostgresPool) -> None:
        self._pool = pool

    async def pool(self) -> FakePostgresPool:
        return self._pool


def _repo() -> tuple[PostgresBusinessRepository, FakePostgresPool]:
    pool = FakePostgresPool()
    return PostgresBusinessRepository(FakePoolWrapper(pool)), pool  # type: ignore[arg-type]


def test_postgres_business_repository_project_lifecycle() -> None:
    async def run() -> None:
        repo, _ = _repo()

        created = await repo.create(
            user_id="user-1",
            entity_type="projects",
            data={"name": "RevenuePilot", "description": "Console", "metadata": {"stage": "prod"}},
        )
        assert created["project_id"] is None
        assert created["data"]["name"] == "RevenuePilot"
        assert created["data"]["metadata"] == {"stage": "prod"}

        entity_id = UUID(created["id"])
        updated = await repo.update(entity_id=entity_id, user_id="user-1", data={"name": "RevenuePilot OS"})
        assert updated["data"]["name"] == "RevenuePilot OS"

        listed = await repo.list(user_id="user-1", entity_type="projects")
        assert [item["id"] for item in listed] == [created["id"]]
        assert await repo.count(user_id="user-1", entity_type="projects") == 1

        await repo.delete(entity_id=entity_id, user_id="user-1")
        assert await repo.count(user_id="user-1", entity_type="projects") == 0

    asyncio.run(run())


def test_postgres_business_repository_preserves_uuid_foreign_keys_as_strings() -> None:
    async def run() -> None:
        repo, _ = _repo()
        project_id = uuid4()
        delivery_project_id = uuid4()

        task = await repo.create(
            user_id="user-1",
            entity_type="delivery_tasks",
            project_id=project_id,
            data={"delivery_project_id": str(delivery_project_id), "title": "Setup", "status": "todo"},
        )

        assert task["project_id"] == str(project_id)
        assert task["data"]["delivery_project_id"] == str(delivery_project_id)

    asyncio.run(run())
