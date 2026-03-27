from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime, timezone


class CampaignProposal(BaseModel):
    proposal_id: str
    campaign_type: str
    objective: str
    suggested_offer: str
    validity_hours: int

    estimated_uplift: float
    estimated_roi: float

    segment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    status: str  # pending | approved | rejected | modified
    human_notes: Optional[str] = None
