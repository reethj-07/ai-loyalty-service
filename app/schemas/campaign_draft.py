from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime, timezone


class CampaignDraft(BaseModel):
    draft_id: str
    proposal_id: str

    campaign_type: str
    objective: str
    offer: str
    segment: str

    duration_hours: int
    estimated_roi: float
    estimated_uplift: float

    prefilled_fields: Dict[str, str]

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "draft"  # draft | sent | launched
