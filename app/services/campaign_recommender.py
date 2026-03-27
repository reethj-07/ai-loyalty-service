from typing import List


class CampaignRecommenderService:
    """
    Converts behavior signals into campaign recommendations
    """

    def recommend_from_signals(self, signals) -> List[dict]:
        # Return mock recommendations for testing
        # Frontend expects: id, segment, behavior, campaign, campaign_channel, estimated_roi
        return [
            {
                "id": "rec-001",
                "segment": "high_value",
                "behavior": "high_value_transaction",
                "campaign": "2x Points Bonus Campaign",
                "campaign_channel": "email",
                "estimated_roi": "60%"
            },
            {
                "id": "rec-002",
                "segment": "at_risk",
                "behavior": "declining_engagement",
                "campaign": "Win Back Campaign",
                "campaign_channel": "push",
                "estimated_roi": "45%"
            },
            {
                "id": "rec-003",
                "segment": "new_member",
                "behavior": "first_purchase",
                "campaign": "Welcome Bonus",
                "campaign_channel": "sms",
                "estimated_roi": "80%"
            }
        ]


# ✅ FUNCTION EXPORT EXPECTED BY FASTAPI ROUTER
def recommend_campaigns() -> List[dict]:
    """
    Entry point used by API layer.
    Keeps API stable even if AI logic evolves.
    """
    service = CampaignRecommenderService()

    # Temporary: empty signals (can be wired later)
    signals = []

    return service.recommend_from_signals(signals)
