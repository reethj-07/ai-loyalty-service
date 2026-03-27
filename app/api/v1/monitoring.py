from fastapi import APIRouter, HTTPException
from app.monitoring.repository import campaign_kpi_repo

router = APIRouter(tags=["monitoring"])


@router.get("/campaign/{campaign_id}")
def get_campaign_kpis(campaign_id: str):
    """
    Real-time KPI view for a single campaign.
    """
    kpi = campaign_kpi_repo.get(campaign_id)

    if not kpi:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return kpi.to_json()


@router.get("/campaigns/active")
def get_active_campaigns():
    """
    List all active campaigns with KPIs.
    Frontend-safe: always returns a list.
    """
    campaigns = campaign_kpi_repo.all_active()
    return [kpi.to_json() for kpi in campaigns]