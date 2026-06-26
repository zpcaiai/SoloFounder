from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _migrations_root() -> Path | None:
    # app/core/migrations.py -> app -> project root
    root = Path(__file__).resolve().parents[2]
    migrations = root / "sql" / "migrations"
    if migrations.is_dir():
        return migrations
    return None


async def apply_pending_migrations(pool: Any) -> None:
    """Apply any SQL migration file that has not yet been recorded in public.schema_migrations."""
    migrations_root = _migrations_root()
    if migrations_root is None:
        logger.warning("No sql/migrations directory found; skipping startup migrations")
        return

    files = sorted(migrations_root.glob("*.sql"))
    if not files:
        logger.info("No migration files found")
        return

    for migration_file in files:
        version = migration_file.stem
        try:
            row = await pool.fetchrow(
                "select 1 from public.schema_migrations where version = $1",
                version,
            )
            if row:
                logger.info("Migration already applied: %s", version)
                continue

            sql = migration_file.read_text(encoding="utf-8")
            async with pool.acquire() as conn, conn.transaction():
                await conn.execute(sql)
            logger.info("Applied migration: %s", version)
        except Exception:
            logger.exception("Failed to apply migration: %s", version)
            raise
