import json
from datetime import datetime, timezone
from typing import List, Optional

from app.core.redis_client import redis_client
from app.monitoring.models import CampaignKPI


class CampaignKPIRepository:
    KEY_PREFIX = "campaign:kpi"

    def _key(self, campaign_id: str) -> str:
        return f"{self.KEY_PREFIX}:{campaign_id}"

    def create(
        self,
        campaign_id: str,
        estimated_roi: Optional[float] = None,
        participants: int = 0,
        transactions: int = 0,
        revenue_generated: float = 0.0,
        incentive_cost: float = 0.0,
    ):
        kpi = CampaignKPI(
            campaign_id=campaign_id,
            estimated_roi=estimated_roi,
            participants=participants,
            transactions=transactions,
            revenue_generated=revenue_generated,
            incentive_cost=incentive_cost,
            started_at=datetime.now(timezone.utc),
            last_updated=datetime.now(timezone.utc),
            status="active",
        )

        redis_client.set(
            self._key(campaign_id),
            json.dumps(kpi.to_json())
        )

    def get(self, campaign_id: str) -> Optional[CampaignKPI]:
        raw = redis_client.get(self._key(campaign_id))
        if not raw:
            return None
        return CampaignKPI(**json.loads(raw))

    def update(self, campaign_id: str, **updates):
        kpi = self.get(campaign_id)
        if not kpi:
            return

        for key, value in updates.items():
            if hasattr(kpi, key):
                setattr(kpi, key, value)

        kpi.last_updated = datetime.now(timezone.utc)

        redis_client.set(
            self._key(campaign_id),
            json.dumps(kpi.to_json())
        )

    def all_active(self) -> List[CampaignKPI]:
        keys = redis_client.keys(f"{self.KEY_PREFIX}:*")
        result = []

        for key in keys:
            raw = redis_client.get(key)
            if not raw:
                continue

            kpi = CampaignKPI(**json.loads(raw))
            if kpi.status == "active":
                result.append(kpi)

        return result


campaign_kpi_repo = CampaignKPIRepository()