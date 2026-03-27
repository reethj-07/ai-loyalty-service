from typing import Dict
from app.schemas.campaign_metrics import CampaignMetrics


class CampaignMetricsRepository:
    """
    PoC in-memory metrics store
    Replace with Redis / ClickHouse later
    """

    def __init__(self):
        self._store: Dict[str, CampaignMetrics] = {}

    def get(self, campaign_id: str) -> CampaignMetrics | None:
        return self._store.get(campaign_id)

    def save(self, metrics: CampaignMetrics):
        self._store[metrics.campaign_id] = metrics
