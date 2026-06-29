# RevenuePilot OS Batch 3

This repository implements the Batch 3 AI workflow engine for a Solo Founder Business OS.

Implemented:

- 12 core skills plus the optional `content_to_product` skill.
- Shared prompt and AI provider abstraction.
- Pydantic result schemas and standard `SkillEnvelope` validation.
- Skill registry and `SkillRunner` lifecycle.
- In-memory `skill_runs`, `ai_generations`, and `workflow_runs` repositories for local development and tests.
- LangGraph-compatible workflows with a fallback runner when `langgraph` is not installed in the active Python environment.
- FastAPI routes for skills and workflows.
- Guardrails for outreach spam, regulated revenue advice, and faith-based content tone in prompts.

## Run Tests

Backend (Python 3.10+):

```bash
pytest -q
```

Frontend (Vitest + Testing Library):

```bash
cd frontend
npm install
npm test
```

End-to-end (Playwright, drives the console against the live backend):

```bash
cd frontend
npm run e2e:install   # one-time Chromium download
npm run e2e
```

CI runs the backend suite, frontend unit tests, and the Playwright E2E smoke test (plus `ruff`, `mypy`, `bandit`, and the frontend build) on every push.

## Start API

```bash
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. After building the frontend (`npm run build`), the root path serves the React console. The build also generates `app/ui_embed.py`, which embeds the UI as a Python string for reliable Vercel deployments.

## Frontend console

A React + Vite + TailwindCSS console lives in `frontend/`:

```bash
cd frontend
npm install
npm run build
```

During development the Vite dev server proxies `/api`, `/health`, and `/metrics` to the FastAPI backend:

```bash
# terminal 1
uvicorn app.main:app --reload

# terminal 2
cd frontend
npm run dev
```

Open `http://localhost:5173` to use the console. Configure the user ID, API key, and project ID in the Settings page.

## Deploy to Vercel

This project is configured for Vercel's FastAPI runtime through:

- `pyproject.toml` with `tool.vercel.entrypoint = "app.main:app"`
- `requirements.txt`
- `vercel.json`

Deploy manually:

```bash
vercel
vercel --prod
```

Vercel's FastAPI runtime looks for a `FastAPI` instance named `app` at supported entrypoints or the explicit `tool.vercel.entrypoint` configured above.

## Neon Migrations on Git Push

The workflow in `.github/workflows/neon-migrate.yml` applies every SQL file under `sql/migrations/*.sql` to Neon when code is pushed to `main`.

Set this GitHub repository secret before pushing:

```text
NEON_DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

For the deployed Vercel app, set:

```text
REVENUEPILOT_ENV=production
REVENUEPILOT_DB=postgres
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
REVENUEPILOT_API_KEY=<optional shared API key>
```

When `REVENUEPILOT_ENV=production`, protected API routes require `X-User-Id`.
When `REVENUEPILOT_API_KEY` is set, protected API routes also require `X-API-Key`.

The first migration is:

```text
sql/migrations/001_revenuepilot_core.sql
```

It creates the core Batch 3 tables, including `skill_runs`, `ai_generations`, `workflow_runs`, `founder_profiles`, `business_ideas`, `offers`, `landing_pages`, `outreach_assets`, `crm_deals`, `proposals`, `delivery_projects`, `revenue_records`, and `retention_plans`.

## Skill Endpoint

```http
POST /api/skills/run
```

```json
{
  "skill_name": "productized_offer",
  "project_id": "project-1",
  "input_payload": {
    "selected_niche": "immigration consultants",
    "locale": "zh-CN"
  }
}
```

## Workflow Endpoints

```http
POST /api/workflows/idea-to-offer/run
POST /api/workflows/deal-to-delivery/run
POST /api/workflows/content-to-product/run
GET /api/workflow-runs
GET /api/workflow-runs/{workflow_run_id}
```

The default AI provider is deterministic so the system runs without an API key. Select a real provider with `REVENUEPILOT_AI_PROVIDER` (`deterministic` | `anthropic` | `openai`) and set the matching key (`ANTHROPIC_API_KEY` / `OPENAI_API_KEY`); or inject a custom adapter via `app.ai.provider.set_ai_provider(...)`.

## Production configuration

Copy `.env.example` to `.env` and set the required values. Key knobs:

- `DATABASE_URL` / `REVENUEPILOT_DB=postgres` for persistence (memory is the default).
- `DB_POOL_MIN`, `DB_POOL_MAX`, `DB_CONNECT_TIMEOUT` for Postgres connection tuning.
- `REVENUEPILOT_API_KEY` and `API_KEY_HEADER` for API-key auth.
- `CORS_ORIGINS` (comma-separated) for the CORS allow-list. A wildcard `*` disables credentialed CORS (per the spec); set explicit origins to allow credentials.
- `RATE_LIMIT_PER_MINUTE` for the per-user token bucket (default 120).
- `RATE_LIMIT_BACKEND` (`memory` default, or `redis`) and `REDIS_URL` for a shared limiter across instances.
- `REVENUEPILOT_AI_PROVIDER` (`deterministic` | `anthropic` | `openai`) plus the matching API key.
- `REVENUEPILOT_REQUEST_TIMEOUT`, `REVENUEPILOT_MAX_REQUEST_BODY_SIZE` for runtime guards.
- `REVENUEPILOT_AI_TIMEOUT`, `REVENUEPILOT_AI_MAX_RETRIES` for LLM calls.
- `REVENUEPILOT_SKIP_DB_MIGRATION=1` to skip startup migrations on read-only replicas.

In production (`REVENUEPILOT_ENV=production`) protected routes are fail-closed: an API key must be configured, and every request must supply both `X-API-Key` and `X-User-Id`.

## Health and observability

- `GET /health` returns service status and database connectivity (`memory` or `connected`/`degraded`).
- `GET /metrics` returns Prometheus-style request counters when `METRICS_ENABLED=true`.
- Every response includes `X-Request-ID` and `X-Response-Time-Ms` headers.
- Security headers (`X-Content-Type-Options`, `X-Frame-Options`, etc.) are added automatically.
- API keys are compared with constant-time `secrets.compare_digest` and never logged.
- Set `LOG_FORMAT=json` to emit newline-delimited JSON logs for log aggregation.

## Docker (local)

A `Dockerfile` and `docker-compose.yml` are included for local development with Postgres:

```bash
docker compose up --build
```

This starts the API on `http://localhost:8000` and applies migrations on startup.
