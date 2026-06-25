from __future__ import annotations

import asyncio

import pytest

from app.repositories.workflow_run_repo import workflow_run_repo
from app.services.workflow_runner import workflow_runner


def arun(coro):
    return asyncio.run(coro)


def test_idea_to_offer_workflow_completes():
    result = arun(
        workflow_runner.run(
            user_id="user-1",
            workflow_name="idea_to_offer",
            project_id="project-1",
            input_payload={
                "locale": "zh-CN",
                "founder_profile": {"skills": ["automation"], "monthly_income_goal": 5000},
                "selected_idea": {"pain_point": "slow lead follow-up"},
            },
        )
    )

    assert result["status"] == "succeeded"
    output = result["output"]
    assert output["next_step"] == "done"
    assert output["outreach_assets"]["human_approval_required"] is True
    assert len(output["skill_run_ids"]) == 8


def test_deal_to_delivery_workflow_completes():
    result = arun(
        workflow_runner.run(
            user_id="user-1",
            workflow_name="deal_to_delivery",
            project_id="project-1",
            input_payload={
                "lead": {"name": "Client"},
                "deal": {"stage": "qualified", "pain_summary": "missed leads"},
                "offer": {"offer_name": "Lead Sprint"},
                "revenue_records": [{"amount": 1500}],
            },
        )
    )

    assert result["status"] == "succeeded"
    output = result["output"]
    assert output["next_step"] == "done"
    assert output["proposal"]["proposal_title"]
    assert len(output["skill_run_ids"]) == 4


def test_content_to_product_workflow_completes():
    result = arun(
        workflow_runner.run(
            user_id="user-1",
            workflow_name="content_to_product",
            project_id="project-1",
            input_payload={
                "knowledge_assets": [{"title": "Course notes", "raw_text": "lesson material"}],
                "target_audience": "church educators",
                "desired_product_type": "course",
            },
        )
    )

    assert result["status"] == "succeeded"
    output = result["output"]
    assert output["next_step"] == "done"
    assert output["content_product_plan"]["recommended_products"]
    assert len(output["skill_run_ids"]) == 4


def test_workflow_run_lifecycle_and_user_isolation():
    result = arun(
        workflow_runner.run(
            user_id="user-a",
            workflow_name="content_to_product",
            project_id="project-1",
            input_payload={"knowledge_assets": [], "target_audience": "educators"},
        )
    )

    assert result["status"] == "succeeded"
    assert len(arun(workflow_run_repo.list_for_user("user-a"))) == 1
    assert len(arun(workflow_run_repo.list_for_user("user-b"))) == 0

    workflow_run_id = next(iter(workflow_run_repo.records))
    with pytest.raises(PermissionError):
        arun(workflow_run_repo.get_for_user(workflow_run_id, "user-b"))
