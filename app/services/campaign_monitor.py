from app.schemas.campaign_metrics import CampaignMetrics
from app.repositories.campaign_metrics_repository import CampaignMetricsRepository


class CampaignMonitorService:

    def __init__(self, repo: CampaignMetricsRepository):
        self.repo = repo

    def update_metrics(
        self,
        campaign_id: str,
        revenue: float = 0,
        points: int = 0,
        participant_increment: int = 0,
    ) -> CampaignMetrics:

        metrics = self.repo.get(campaign_id)

        if not metrics:
            metrics = CampaignMetrics(
                campaign_id=campaign_id,
                participants=0,
                transactions=0,
                revenue_generated=0.0,
                points_distributed=0,
                campaign_cost=0.0,
                estimated_roi=0.6,
                actual_roi=0.0,
            )

        metrics.participants += participant_increment
        metrics.transactions += 1 if revenue > 0 else 0
        metrics.revenue_generated += revenue
        metrics.points_distributed += points
        metrics.campaign_cost += points * 0.01  # example cost

        if metrics.campaign_cost > 0:
            metrics.actual_roi = round(
                metrics.revenue_generated / metrics.campaign_cost, 2
            )

        self.repo.save(metrics)
        return metrics
