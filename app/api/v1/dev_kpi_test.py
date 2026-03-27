from fastapi import APIRouter
from app.monitoring.kpi_engine import kpi_engine

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/trigger-kpi")
async def trigger_kpi(
    campaign_id: str,
    amount: float = 500.0,
):
    await kpi_engine.register_participation(campaign_id)
    await kpi_engine.register_transaction(
        campaign_id,
        amount=amount,
        incentive_cost=amount * 0.05,
    )

    return {
        "status": "ok",
        "campaign_id": campaign_id,
        "amount": amount,
    }
