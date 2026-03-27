from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

class EventMetadata(BaseModel):
    event_id: str
    occurred_at: datetime
    source: str
