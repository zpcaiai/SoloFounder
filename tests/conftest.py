from __future__ import annotations

import pytest

from app.repositories.ai_generation_repo import ai_generation_repo
from app.repositories.factory import reset_repository_bundle
from app.repositories.skill_run_repo import skill_run_repo
from app.repositories.workflow_run_repo import workflow_run_repo


@pytest.fixture(autouse=True)
def reset_repositories():
    reset_repository_bundle()
    skill_run_repo.reset()
    ai_generation_repo.reset()
    workflow_run_repo.reset()
    yield
    reset_repository_bundle()
    skill_run_repo.reset()
    ai_generation_repo.reset()
    workflow_run_repo.reset()
