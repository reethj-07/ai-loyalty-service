from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CampaignKPI(BaseModel):
    campaign_id: str

    participants: int = 0
    transactions: int = 0

    revenue_generated: float = 0.0
    incentive_cost: float = 0.0

    estimated_roi: Optional[float] = None
    actual_roi: Optional[float] = None

    started_at: datetime
    last_updated: datetime
    status: str = "active"

    def to_json(self):
        return self.model_dump(mode="json")
