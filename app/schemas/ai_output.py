from pydantic import BaseModel
from typing import Dict, Any

class BehaviorChange(BaseModel):
    type: str
    confidence: float

class CampaignSuggestion(BaseModel):
    objective: str
    audience_hint: str
    offer_hint: str
    timing_hint: str

class AIResponse(BaseModel):
    behavior_change: BehaviorChange
    suggested_campaign: CampaignSuggestion
    roi_score: float
