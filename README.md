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

```bash
pytest -q
```

## Start API

```bash
uvicorn app.main:app --reload
```

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

The default AI provider is deterministic so the system runs without an API key. Replace `app.ai.provider.set_ai_provider(...)` with a real provider adapter to call a production LLM.
