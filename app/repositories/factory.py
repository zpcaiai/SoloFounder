from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import get_settings
from app.repositories.ai_generation_repo import InMemoryAIGenerationRepository, ai_generation_repo
from app.repositories.business_repo import InMemoryBusinessRepository, business_repo
from app.repositories.skill_run_repo import InMemorySkillRunRepository, skill_run_repo
from app.repositories.workflow_run_repo import InMemoryWorkflowRunRepository, workflow_run_repo


@dataclass(slots=True)
class RepositoryBundle:
    skill_runs: Any
    ai_generations: Any
    workflow_runs: Any
    entities: Any | None = None
    business: Any = None


_repository_bundle: RepositoryBundle | None = None


def get_repositories() -> RepositoryBundle:
    global _repository_bundle
    if _repository_bundle is not None:
        return _repository_bundle

    settings = get_settings()
    if settings.use_postgres:
        from app.repositories.postgres import PostgresRepositoryBundle

        _repository_bundle = PostgresRepositoryBundle(
            settings.database_url or "",
            min_size=settings.db_pool_min,
            max_size=settings.db_pool_max,
            command_timeout=settings.db_connect_timeout,
        )
    else:
        _repository_bundle = RepositoryBundle(
            skill_runs=skill_run_repo,
            ai_generations=ai_generation_repo,
            workflow_runs=workflow_run_repo,
            entities=None,
            business=business_repo,
        )
    return _repository_bundle


def set_repositories(bundle: RepositoryBundle) -> None:
    global _repository_bundle
    _repository_bundle = bundle


def reset_repository_bundle() -> None:
    global _repository_bundle
    _repository_bundle = None


async def close_repository_bundle() -> None:
    """Close any persistent connections held by the current repository bundle."""
    global _repository_bundle
    if _repository_bundle is None:
        return
    if hasattr(_repository_bundle, "close"):
        await _repository_bundle.close()
    _repository_bundle = None


def reset_in_memory_repositories() -> None:
    for repo in (skill_run_repo, ai_generation_repo, workflow_run_repo, business_repo):
        repo.reset()


def new_in_memory_bundle() -> RepositoryBundle:
    return RepositoryBundle(
        skill_runs=InMemorySkillRunRepository(),
        ai_generations=InMemoryAIGenerationRepository(),
        workflow_runs=InMemoryWorkflowRunRepository(),
        entities=None,
        business=InMemoryBusinessRepository(),
    )
