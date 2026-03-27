from pydantic import BaseModel
from typing import Dict
from datetime import datetime


class BehaviorState(BaseModel):
    member_id: str
    metrics: Dict[str, float]
    last_updated: datetime
