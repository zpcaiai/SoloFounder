from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import current_user_id
from app.repositories.factory import get_repositories
from app.schemas import ProposalCreate, ProposalUpdate

router = APIRouter(prefix="/api/projects/{project_id}/proposals", tags=["proposals"])


@router.post("")
async def create_proposal(
    project_id: str,
    body: ProposalCreate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    return await get_repositories().business.create(
        user_id=user_id,
        project_id=project_id,
        entity_type="proposals",
        data=body.model_dump(),
    )


@router.get("")
async def list_proposals(project_id: str, user_id: str = Depends(current_user_id)) -> list[dict[str, Any]]:
    return await get_repositories().business.list(
        user_id=user_id,
        entity_type="proposals",
        project_id=project_id,
    )


@router.get("/{proposal_id}")
async def get_proposal(
    project_id: str,
    proposal_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.get(entity_id=UUID(proposal_id), user_id=user_id)
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Proposal not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your proposal") from None


@router.put("/{proposal_id}")
async def update_proposal(
    project_id: str,
    proposal_id: str,
    body: ProposalUpdate,
    user_id: str = Depends(current_user_id),
) -> dict[str, Any]:
    try:
        return await get_repositories().business.update(
            entity_id=UUID(proposal_id),
            user_id=user_id,
            data=body.model_dump(exclude_none=True),
        )
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Proposal not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your proposal") from None


@router.delete("/{proposal_id}")
async def delete_proposal(
    project_id: str,
    proposal_id: str,
    user_id: str = Depends(current_user_id),
) -> dict[str, str]:
    try:
        await get_repositories().business.delete(entity_id=UUID(proposal_id), user_id=user_id)
        return {"status": "deleted"}
    except (KeyError, ValueError):
        raise HTTPException(status_code=404, detail="Proposal not found") from None
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not your proposal") from None
