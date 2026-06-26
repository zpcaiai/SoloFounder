from __future__ import annotations

import asyncio

import pytest

from app.core.migrations import apply_pending_migrations


class FakeTransaction:
    async def __aenter__(self) -> "FakeTransaction":
        return self

    async def __aexit__(self, *args) -> None:
        pass


class FakeConnection:
    def __init__(self, pool: "FakePool") -> None:
        self._pool = pool

    async def __aenter__(self) -> "FakeConnection":
        return self

    async def __aexit__(self, *args) -> None:
        pass

    def transaction(self) -> FakeTransaction:
        return FakeTransaction()

    async def execute(self, sql: str) -> None:
        self._pool.applied.append(sql)


class FakePool:
    def __init__(self) -> None:
        self.applied: list[str] = []
        self.existing: set[str] = set()

    async def fetchrow(self, query: str, version: str) -> dict[str, int] | None:
        if version in self.existing:
            return {"exists": 1}
        return None

    def acquire(self) -> FakeConnection:
        return FakeConnection(self)


@pytest.fixture
def migrations_dir(tmp_path, monkeypatch):
    migrations = tmp_path / "sql" / "migrations"
    migrations.mkdir(parents=True)
    (migrations / "001_first.sql").write_text("CREATE TABLE first (id int);")
    (migrations / "002_second.sql").write_text("CREATE TABLE second (id int);")
    monkeypatch.setattr(
        "app.core.migrations._migrations_root",
        lambda: migrations,
    )
    return migrations


def test_applies_only_new_migrations(migrations_dir):
    pool = FakePool()
    pool.existing = {"001_first"}

    asyncio.run(apply_pending_migrations(pool))

    assert len(pool.applied) == 1
    assert "CREATE TABLE second" in pool.applied[0]
