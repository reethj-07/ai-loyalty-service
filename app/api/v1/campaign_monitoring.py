from fastapi import APIRouter, HTTPException
from app.repositories.campaign_metrics_repository import CampaignMetricsRepository

router = APIRouter(prefix="/campaigns", tags=["campaign-monitoring"])

repo = CampaignMetricsRepository()


@router.get("/{campaign_id}/metrics")
def get_campaign_metrics(campaign_id: str):
    metrics = repo.get(campaign_id)
    if not metrics:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return metrics
