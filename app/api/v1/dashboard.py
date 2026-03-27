from fastapi import APIRouter
from app.monitoring.repository import campaign_kpi_repo

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/kpis")
async def get_all_kpis():
    """
    Returns current snapshot of all active campaign KPIs
    """
    return [
        kpi.model_dump()
        for kpi in campaign_kpi_repo.all_active()
    ]
