from fastapi import APIRouter, HTTPException, status, File, UploadFile, Depends
from pydantic import BaseModel, Field
import logging
import csv
import io
from datetime import datetime, timezone
from app.repositories.supabase_campaigns_repo import campaigns_repo
from app.core.tenant import resolve_tenant_id
from app.core.auth import require_roles

router = APIRouter(tags=["campaigns"])

logger = logging.getLogger(__name__)

VALID_STATUSES = {"draft", "scheduled", "active", "running", "completed", "paused"}
VALID_CHANNELS = {"email", "sms", "push", "in-app"}


class CreateCampaignRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    description: str = Field(default="", description="Campaign description")
    campaign_type: str = Field(default="promotion", description="Campaign type")
    objective: str = Field(default="engagement", description="Campaign objective")
    channel: str = Field(default="email", description="Channel (email, sms, push, in-app)")
    status: str = Field(default="draft", description="Status")
    start_date: str = Field(default=None, description="Start date (ISO format)")
    end_date: str = Field(default=None, description="End date (ISO format)")
    estimated_roi: float = Field(default=0, description="Estimated ROI %")
    estimated_cost: float = Field(default=0, description="Estimated cost")
    estimated_revenue: float = Field(default=0, description="Estimated revenue")


@router.get("")
def list_campaigns(tenant_id: str | None = Depends(resolve_tenant_id)):
    """Get all campaigns"""
    try:
        campaigns = campaigns_repo.list_campaigns(tenant_id=tenant_id)
        return [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "start_date": c.start_date,
                "end_date": c.end_date,
                "created_at": c.created_at,
                "created_by": c.created_by or "Admin",
                "campaign_type": c.campaign_type,
                "channel": c.channel,
                "estimated_roi": c.estimated_roi,
            }
            for c in campaigns
        ]
    except Exception as e:
        logger.error(f"Error listing campaigns: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch campaigns",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_campaign(
    request: CreateCampaignRequest,
    tenant_id: str | None = Depends(resolve_tenant_id),
    _user: dict = Depends(require_roles("admin")),
):
    """Create a new campaign"""
    try:
        if request.channel not in VALID_CHANNELS:
            raise ValueError(f"Invalid channel. Must be one of: {', '.join(VALID_CHANNELS)}")
        
        if request.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")

        campaign_data = {
            "name": request.name,
            "description": request.description,
            "campaign_type": request.campaign_type,
            "objective": request.objective,
            "channel": request.channel,
            "status": request.status,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "estimated_roi": request.estimated_roi,
            "estimated_cost": request.estimated_cost,
            "estimated_revenue": request.estimated_revenue,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        new_campaign = campaigns_repo.create_campaign(campaign_data, tenant_id=tenant_id)

        if not new_campaign:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create campaign",
            )

        logger.info(f"Campaign created: {new_campaign.id}")

        return {
            "id": new_campaign.id,
            "name": new_campaign.name,
            "status": new_campaign.status,
            "start_date": new_campaign.start_date,
            "end_date": new_campaign.end_date,
            "created_at": new_campaign.created_at,
            "campaign_type": new_campaign.campaign_type,
            "channel": new_campaign.channel,
            "estimated_roi": new_campaign.estimated_roi,
        }
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("/{campaign_id}")
def get_campaign(campaign_id: str, tenant_id: str | None = Depends(resolve_tenant_id)):
    """Get a single campaign"""
    try:
        campaign = campaigns_repo.get_campaign_by_id(campaign_id, tenant_id=tenant_id)
        
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found",
            )

        return {
            "id": campaign.id,
            "name": campaign.name,
            "status": campaign.status,
            "start_date": campaign.start_date,
            "end_date": campaign.end_date,
            "created_at": campaign.created_at,
            "campaign_type": campaign.campaign_type,
            "channel": campaign.channel,
            "estimated_roi": campaign.estimated_roi,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching campaign: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch campaign",
        )


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_create_campaigns(
    file: UploadFile = File(...),
    tenant_id: str | None = Depends(resolve_tenant_id),
    _user: dict = Depends(require_roles("admin")),
):
    """Bulk import campaigns from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file",
        )

    try:
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))

        created_count = 0
        failed_count = 0
        error_details = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                campaign_data = {
                    "name": row.get("name", "").strip(),
                    "description": row.get("description", "").strip(),
                    "campaign_type": row.get("campaign_type", "promotion").strip(),
                    "objective": row.get("objective", "engagement").strip(),
                    "channel": row.get("channel", "email").strip(),
                    "status": row.get("status", "draft").strip(),
                    "start_date": row.get("start_date", "").strip() or None,
                    "end_date": row.get("end_date", "").strip() or None,
                    "estimated_roi": float(row.get("estimated_roi", 0)) if row.get("estimated_roi") else 0,
                    "estimated_cost": float(row.get("estimated_cost", 0)) if row.get("estimated_cost") else 0,
                    "estimated_revenue": float(row.get("estimated_revenue", 0)) if row.get("estimated_revenue") else 0,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }

                if not campaign_data["name"]:
                    raise ValueError("Campaign name is required")

                new_campaign = campaigns_repo.create_campaign(campaign_data, tenant_id=tenant_id)
                if new_campaign:
                    created_count += 1
                else:
                    failed_count += 1
                    error_details.append(f"Row {row_num}: Failed to create campaign")

            except Exception as e:
                failed_count += 1
                error_details.append(f"Row {row_num}: {str(e)}")
                logger.warning(f"Failed to import campaign row {row_num}: {str(e)}")

        logger.info(f"Bulk campaign import: {created_count} created, {failed_count} failed")

        return {
            "status": "completed",
            "created": created_count,
            "failed": failed_count,
            "errors": error_details[:10],
            "message": f"Successfully imported {created_count} campaigns. {failed_count} failed.",
        }

    except Exception as e:
        logger.error(f"Error processing CSV file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV file: {str(e)}",
        )
