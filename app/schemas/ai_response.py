from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class BehavioralSignal(BaseModel):
    signal: str
    reason: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = None


class MemberState(BaseModel):
    segment: str
    lifecycle_stage: str
    risk_score: float


class CampaignRecommendation(BaseModel):
    campaign_type: str
    objective: str
    suggested_offer: str
    validity_hours: int
    estimated_uplift: float
    estimated_roi: float
    automation_ready: bool


class AIResponse(BaseModel):
    status: str
    member_id: str
    behavioral_signals: List[BehavioralSignal]
    member_state: MemberState
    campaign_recommendations: List[CampaignRecommendation]
    next_actions: List[str]
