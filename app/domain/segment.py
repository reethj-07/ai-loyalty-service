from dataclasses import dataclass


@dataclass
class BehavioralSegment:
    segment_id: str
    description: str
    member_count: int
    confidence: float
