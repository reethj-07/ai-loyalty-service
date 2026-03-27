from pydantic import BaseModel
from typing import Optional


class CampaignMetrics(BaseModel):
    campaign_id: str

    participants: int
    transactions: int

    revenue_generated: float
    points_distributed: int
    campaign_cost: float

    estimated_roi: float
    actual_roi: float
