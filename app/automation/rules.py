from typing import List, Dict


class CampaignRule:
    def applies(self, context: Dict) -> bool:
        raise NotImplementedError

    def propose(self, context: Dict) -> Dict:
        raise NotImplementedError


class HighValueTransactionRule(CampaignRule):
    """
    Triggered when high-value transaction signal detected
    """

    def applies(self, context: Dict) -> bool:
        return any(
            s["type"] == "high_value_transaction"
            for s in context.get("signals", [])
        )

    def propose(self, context: Dict) -> Dict:
        return {
            "campaign_type": "bonus_points",
            "objective": "increase_frequency",
            "offer": "2x points on next purchase",
            "validity_hours": 48,
            "estimated_roi": 0.64,
            "risk_level": "medium",
        }
