from pydantic import BaseModel
from typing import Dict


class SegmentState(BaseModel):
    segment_id: str
    size: int

    avg_spend: float
    activity_rate: float
    risk_score_avg: float


class SegmentShift(BaseModel):
    segment_id: str
    previous_size: int
    current_size: int
    change_ratio: float
    reason: str
