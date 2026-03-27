from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


# -----------------------------
# Ingestion Metadata
# -----------------------------

class IngestionMetadata(BaseModel):
    tenant_id: str
    source: str
    trace_id: Optional[str] = None


# -----------------------------
# Transaction Event
# -----------------------------

class TransactionEvent(BaseModel):
    transaction_id: str
    member_id: str

    amount: float = Field(..., gt=0)
    currency: str

    merchant: str
    category: str
    channel: str

    transaction_date: datetime
    metadata: IngestionMetadata
