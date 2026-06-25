from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.services.workflow_runner import workflow_runner

router = APIRouter(prefix="/api", tags=["workflows"])


class WorkflowRunRequest(BaseModel):
    project_id: str | None = None
    locale: str = "zh-CN"
    founder_profile: dict[str, Any] = Field(default_factory=dict)
    selected_idea: dict[str, Any] = Field(default_factory=dict)
    lead: dict[str, Any] = Field(default_factory=dict)
    deal: dict[str, Any] = Field(default_factory=dict)
    offer: dict[str, Any] = Field(default_factory=dict)
    revenue_records: list[dict[str, Any]] = Field(default_factory=list)
    knowledge_assets: list[dict[str, Any]] = Field(default_factory=list)
    target_audience: str | None = None
    desired_product_type: str = "course"
    business_goal: str | None = None


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if is_dataclass(value):
        return {key: _serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value


def _payload(request: WorkflowRunRequest) -> dict[str, Any]:
    return request.model_dump(exclude_none=True)


@router.post("/workflows/idea-to-offer/run")
async def run_idea_to_offer(request: WorkflowRunRequest, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    return await workflow_runner.run(
        user_id=user_id,
        workflow_name="idea_to_offer",
        input_payload=_payload(request),
        project_id=request.project_id,
    )


@router.post("/workflows/deal-to-delivery/run")
async def run_deal_to_delivery(request: WorkflowRunRequest, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    return await workflow_runner.run(
        user_id=user_id,
        workflow_name="deal_to_delivery",
        input_payload=_payload(request),
        project_id=request.project_id,
    )


@router.post("/workflows/content-to-product/run")
async def run_content_to_product(request: WorkflowRunRequest, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    return await workflow_runner.run(
        user_id=user_id,
        workflow_name="content_to_product",
        input_payload=_payload(request),
        project_id=request.project_id,
    )


@router.get("/workflow-runs")
async def list_workflow_runs(user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    records = await get_repositories().workflow_runs.list_for_user(user_id)
    return [_serialize(record) for record in records]


@router.get("/workflow-runs/{workflow_run_id}")
async def get_workflow_run(workflow_run_id: str, user_id: str = Depends(current_user_id)) -> dict[str, Any]:
    try:
        record = await get_repositories().workflow_runs.get_for_user(UUID(workflow_run_id), user_id)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Workflow run not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Workflow run does not belong to this user") from None
    return _serialize(record)
