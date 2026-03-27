from app.monitoring.repository import campaign_kpi_repo


class CampaignKPIEngine:
    """
    Stateless KPI engine.
    All persistence handled by campaign_kpi_repo.
    """

    async def register_participation(self, campaign_id: str):
        kpi = campaign_kpi_repo.get(campaign_id)

        # Create KPI record if missing
        if not kpi:
            campaign_kpi_repo.create(
                campaign_id=campaign_id,
                participants=0,
                transactions=0,
                revenue_generated=0.0,
                incentive_cost=0.0,
                estimated_roi=None,
            )
            kpi = campaign_kpi_repo.get(campaign_id)

        # Increment participants
        campaign_kpi_repo.update(
            campaign_id,
            participants=kpi.participants + 1,
        )

    async def register_transaction(
        self,
        campaign_id: str,
        amount: float,
        incentive_cost: float,
    ):
        kpi = campaign_kpi_repo.get(campaign_id)

        # Ignore transaction if campaign KPI does not exist
        if not kpi:
            return

        revenue = kpi.revenue_generated + amount
        cost = kpi.incentive_cost + incentive_cost

        actual_roi = None
        if cost > 0:
            actual_roi = round(((revenue - cost) / cost) * 100, 2)

        campaign_kpi_repo.update(
            campaign_id,
            transactions=kpi.transactions + 1,
            revenue_generated=revenue,
            incentive_cost=cost,
            actual_roi=actual_roi,
        )


# ✅ SINGLETON INSTANCE (DO NOT INSTANTIATE ELSEWHERE)
kpi_engine = CampaignKPIEngine()