#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "Missing DATABASE_URL" >&2
  exit 1
fi

psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "
create table if not exists public.schema_migrations (
  version text primary key,
  applied_at timestamptz not null default now()
);
"

for migration in sql/migrations/*.sql; do
  version="$(basename "$migration" .sql)"
  already_applied="$(psql "$DATABASE_URL" -v version="$version" -tAc "select 1 from public.schema_migrations where version = :'version'")"
  if [[ "$already_applied" == "1" ]]; then
    echo "Skipping ${version}"
    continue
  fi

  echo "Applying ${version}"
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$migration"
done
