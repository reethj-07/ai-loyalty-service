# app/domain/behavior.py

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class BehaviorSignal:
    type: str
    confidence: float
    member_id: str
    tenant_id: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
