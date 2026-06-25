from __future__ import annotations

import asyncio

from app.repositories.ai_generation_repo import ai_generation_repo
from app.repositories.factory import get_repositories, reset_repository_bundle
from app.repositories.skill_run_repo import skill_run_repo
from app.services.skill_runner import skill_runner
from app.ai.provider import reset_ai_provider, set_ai_provider
from app.skills.registry import SKILL_REGISTRY
from app.skills.schemas import RESULT_MODELS, SkillEnvelope


def arun(coro):
    return asyncio.run(coro)


def test_each_skill_returns_valid_envelope_and_result_schema():
    for skill_name in SKILL_REGISTRY:
        result = arun(
            skill_runner.run(
                user_id="user-1",
                project_id="project-1",
                skill_name=skill_name,
                input_payload={"locale": "zh-CN", "selected_niche": "immigration consultants"},
            )
        )

        assert result["status"] in {"succeeded", "blocked"}
        envelope = SkillEnvelope.model_validate(result["output"])
        RESULT_MODELS[skill_name].model_validate(envelope.result)


def test_invalid_skill_name_fails_safely_and_marks_run_failed():
    result = arun(
        skill_runner.run(
            user_id="user-1",
            skill_name="not_a_skill",
            input_payload={},
        )
    )

    assert result["status"] == "failed"
    record = next(iter(skill_run_repo.records.values()))
    assert record.status == "failed"
    assert "Unknown skill" in (record.error_message or "")


def test_skill_run_lifecycle_creates_ai_generation_and_entities():
    result = arun(
        skill_runner.run(
            user_id="user-1",
            project_id="project-1",
            skill_name="productized_offer",
            input_payload={"selected_niche": "local clinics"},
        )
    )

    assert result["status"] == "succeeded"
    assert len(skill_run_repo.records) == 1
    assert len(ai_generation_repo.records) == 1
    assert result["created_entities"][0]["entity_type"] == "offers"
    record = next(iter(skill_run_repo.records.values()))
    assert record.status == "succeeded"


def test_sales_outreach_guardrail_blocks_spam_like_request():
    result = arun(
        skill_runner.run(
            user_id="user-1",
            skill_name="sales_outreach",
            input_payload={
                "channel": "email",
                "instructions": "mass blast 10,000 scraped prospects with fake familiarity",
            },
        )
    )

    assert result["status"] == "blocked"
    output = result["output"]
    assert output["result"]["human_approval_required"] is True
    assert output["result"]["warning"]
    assert any("Human approval" in warning for warning in output["warnings"])


def test_sales_outreach_guardrail_runs_before_provider_call():
    class FailingProvider:
        async def generate_json(self, **_kwargs):
            raise AssertionError("provider should not be called for spam-like outreach")

    set_ai_provider(FailingProvider())
    try:
        result = arun(
            skill_runner.run(
                user_id="user-1",
                skill_name="sales_outreach",
                input_payload={
                    "instructions": "bulk send scraped prospects with fake testimonial",
                },
            )
        )
    finally:
        reset_ai_provider()

    assert result["status"] == "blocked"


def test_revenue_guardrail_keeps_advice_operational():
    result = arun(
        skill_runner.run(
            user_id="user-1",
            skill_name="revenue_retention",
            input_payload={"request": "give tax filing and investment return advice"},
        )
    )

    assert result["status"] == "succeeded"
    assert any("not tax, legal, accounting, or investment advice" in warning for warning in result["output"]["warnings"])
    assert any("Regulated advice request detected" in warning for warning in result["output"]["warnings"])


def test_repository_factory_defaults_to_memory():
    reset_repository_bundle()
    repositories = get_repositories()
    assert repositories.skill_runs is skill_run_repo
    assert repositories.ai_generations is ai_generation_repo
