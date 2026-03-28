from datetime import datetime, timedelta, timezone
import os
from fastapi import APIRouter, Query, HTTPException, status, Depends
from pydantic import BaseModel, Field
from app.repositories.campaign_proposal_repository import campaign_proposal_repo
from app.repositories.supabase_campaigns_repo import campaigns_repo
from app.services.human_review_service import HumanReviewService
from app.services.campaign_executor import CampaignExecutor
from app.core.tenant import resolve_tenant_id
from app.core.auth import require_roles

router = APIRouter(prefix="/review", tags=["human-review"])

service = HumanReviewService(campaign_proposal_repo)
campaign_executor = CampaignExecutor()


class RejectRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


@router.get("")
def list_proposals(status_filter: str | None = Query(None, alias="status")):
    if status_filter:
        return [p.model_dump() for p in campaign_proposal_repo.list_by_status(status_filter)]
    return [p.model_dump() for p in campaign_proposal_repo.list_all()]


@router.get("/pending")
def list_pending():
    return [p.model_dump() for p in campaign_proposal_repo.list_pending()]


@router.post("/{proposal_id}/approve")
async def approve(
    proposal_id: str,
    notes: str | None = None,
    tenant_id: str | None = Depends(resolve_tenant_id),
    _user: dict = Depends(require_roles("admin")),
):
    proposal = campaign_proposal_repo.get(proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")

    approved = service.approve(proposal_id, notes)

    start_date = datetime.now(timezone.utc).date()
    end_date = (datetime.now(timezone.utc) + timedelta(days=14)).date()

    campaign_data = {
        "name": f"AI {proposal.segment} - {proposal.campaign_type}",
        "description": proposal.suggested_offer,
        "campaign_type": proposal.campaign_type,
        "objective": proposal.objective,
        "channel": "email",
        "status": "scheduled",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "estimated_roi": proposal.estimated_roi,
        "estimated_cost": 0,
        "estimated_revenue": 0,
    }

    created = campaigns_repo.create_campaign(campaign_data, tenant_id=tenant_id)
    execution_result = None

    if created and os.getenv("AUTO_EXECUTE_CAMPAIGNS", "false").lower() == "true":
        execution_result = await campaign_executor.launch_campaign(
            campaign_id=created.id,
            campaign_data={
                "name": created.name,
                "channel": created.channel or "email",
                "target_segment": proposal.segment,
                "offer_details": proposal.suggested_offer,
            },
        )

    return {
        "status": "approved",
        "proposal": approved.model_dump(),
        "campaign": created.to_dict() if created else None,
        "execution": execution_result,
    }


@router.post("/{proposal_id}/reject")
def reject(
    proposal_id: str,
    request: RejectRequest,
    _user: dict = Depends(require_roles("admin")),
):
    proposal = campaign_proposal_repo.get(proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return service.reject(proposal_id, request.reason)


@router.post("/{proposal_id}/modify")
def modify(
    proposal_id: str,
    updates: dict,
    notes: str | None = None,
    _user: dict = Depends(require_roles("admin")),
):
    proposal = campaign_proposal_repo.get(proposal_id)
    if not proposal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proposal not found")
    return service.modify(proposal_id, updates, notes)
