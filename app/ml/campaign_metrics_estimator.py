"""
Campaign Metrics Estimator
Calculates participation rates, costs, and ROI predictions for campaigns
"""
from typing import Dict, List, Optional
from datetime import datetime
import statistics


class CampaignMetricsEstimator:
    """Estimates campaign performance metrics based on historical data and segment characteristics"""

    # Historical participation rates by channel and segment (based on industry benchmarks)
    PARTICIPATION_RATES = {
        "email": {
            "high_value": 0.18,      # 18% for high-value customers
            "at_risk": 0.12,          # 12% for at-risk (lower engagement)
            "new_customers": 0.22,    # 22% for new customers (higher curiosity)
            "regular": 0.15,          # 15% baseline
            "champions": 0.25,        # 25% for champions (most engaged)
        },
        "sms": {
            "high_value": 0.25,       # 25% - SMS has higher open rates
            "at_risk": 0.15,
            "new_customers": 0.28,
            "regular": 0.20,
            "champions": 0.30,
        },
        "push": {
            "high_value": 0.20,
            "at_risk": 0.10,
            "new_customers": 0.18,
            "regular": 0.15,
            "champions": 0.22,
        }
    }

    # Cost per message by channel
    CHANNEL_COSTS = {
        "email": 0.001,    # $0.001 per email (SendGrid pricing)
        "sms": 0.01,       # $0.01 per SMS (Twilio pricing)
        "push": 0.0005,    # $0.0005 per push notification
    }

    # Average transaction value by segment (example data - should be calculated from actual data)
    AVG_TRANSACTION_VALUE = {
        "high_value": 150.00,
        "at_risk": 80.00,
        "new_customers": 65.00,
        "regular": 95.00,
        "champions": 200.00,
    }

    def __init__(self):
        """Initialize the estimator"""
        pass

    def estimate_participation_rate(
        self,
        segment: str,
        channel: str,
        campaign_type: str = "general"
    ) -> float:
        """
        Estimate participation rate based on segment and channel

        Args:
            segment: Customer segment (high_value, at_risk, new_customers, etc.)
            channel: Communication channel (email, sms, push)
            campaign_type: Type of campaign (welcome, winback, promo, etc.)

        Returns:
            float: Estimated participation rate (0.0 to 1.0)
        """
        # Normalize inputs
        segment_key = segment.lower().replace(" ", "_")
        channel_key = channel.lower()

        # Get base participation rate
        base_rate = self.PARTICIPATION_RATES.get(channel_key, {}).get(
            segment_key,
            0.15  # Default 15% if segment not found
        )

        # Adjust based on campaign type
        campaign_multipliers = {
            "welcome": 1.2,      # Welcome campaigns perform 20% better
            "winback": 0.9,      # Winback is harder (10% lower)
            "promo": 1.1,        # Promotions perform 10% better
            "bonus": 1.15,       # Bonus points campaigns perform 15% better
            "tier_upgrade": 1.3, # Tier upgrades highly motivating
            "general": 1.0,      # Baseline
        }

        multiplier = campaign_multipliers.get(campaign_type.lower(), 1.0)

        return min(base_rate * multiplier, 0.95)  # Cap at 95%

    def calculate_campaign_cost(
        self,
        channel: str,
        target_count: int,
        incentive_type: str = "points",
        incentive_value: float = 0.0,
        estimated_participants: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Calculate total campaign cost breakdown

        Args:
            channel: Communication channel (email, sms, push)
            target_count: Number of members targeted
            incentive_type: Type of incentive (points, discount, bonus)
            incentive_value: Value of incentive in currency
            estimated_participants: Expected number of participants (optional)

        Returns:
            dict: Cost breakdown with message_cost, incentive_cost, total_cost, cost_per_acquisition
        """
        channel_key = channel.lower()

        # Message delivery cost
        cost_per_message = self.CHANNEL_COSTS.get(channel_key, 0.01)
        message_cost = cost_per_message * target_count

        # Incentive cost (only paid to participants)
        if estimated_participants is None:
            estimated_participants = int(target_count * 0.15)  # Default 15%

        incentive_cost = incentive_value * estimated_participants

        # Total cost
        total_cost = message_cost + incentive_cost

        # Cost per acquisition (CPA)
        cost_per_acquisition = total_cost / estimated_participants if estimated_participants > 0 else 0

        return {
            "message_cost": round(message_cost, 2),
            "incentive_cost": round(incentive_cost, 2),
            "total_cost": round(total_cost, 2),
            "cost_per_acquisition": round(cost_per_acquisition, 2),
            "target_count": target_count,
            "estimated_participants": estimated_participants,
        }

    def estimate_revenue(
        self,
        segment: str,
        estimated_participants: int,
        campaign_type: str = "general",
        conversion_rate: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Estimate revenue generated from campaign

        Args:
            segment: Customer segment
            estimated_participants: Expected participants
            campaign_type: Type of campaign
            conversion_rate: Override conversion rate (optional)

        Returns:
            dict: Revenue estimates
        """
        segment_key = segment.lower().replace(" ", "_")

        # Average transaction value for this segment
        avg_transaction = self.AVG_TRANSACTION_VALUE.get(segment_key, 100.00)

        # Conversion rate (participants who actually make a purchase)
        if conversion_rate is None:
            conversion_rates = {
                "welcome": 0.65,      # 65% of welcome participants buy
                "winback": 0.45,      # 45% for winback
                "promo": 0.70,        # 70% for promotions
                "bonus": 0.60,        # 60% for bonus campaigns
                "tier_upgrade": 0.50, # 50% for tier upgrades
                "general": 0.55,      # 55% baseline
            }
            conversion_rate = conversion_rates.get(campaign_type.lower(), 0.55)

        # Calculate revenue
        expected_transactions = int(estimated_participants * conversion_rate)
        estimated_revenue = expected_transactions * avg_transaction

        # Incremental revenue (what wouldn't have happened without campaign)
        # Assume 70% is incremental (30% would have purchased anyway)
        incremental_revenue = estimated_revenue * 0.70

        return {
            "estimated_revenue": round(estimated_revenue, 2),
            "incremental_revenue": round(incremental_revenue, 2),
            "expected_transactions": expected_transactions,
            "conversion_rate": round(conversion_rate * 100, 1),  # Return as percentage
            "avg_transaction_value": round(avg_transaction, 2),
        }

    def calculate_roi(
        self,
        revenue: float,
        cost: float
    ) -> Dict[str, float]:
        """
        Calculate ROI and related metrics

        Args:
            revenue: Total revenue generated
            cost: Total campaign cost

        Returns:
            dict: ROI metrics
        """
        if cost == 0:
            return {
                "roi_percentage": 0.0,
                "roi_ratio": 0.0,
                "profit": round(revenue, 2),
                "break_even": False,
            }

        roi_ratio = (revenue - cost) / cost
        roi_percentage = roi_ratio * 100

        return {
            "roi_percentage": round(roi_percentage, 1),
            "roi_ratio": round(roi_ratio, 2),
            "profit": round(revenue - cost, 2),
            "break_even": revenue >= cost,
        }

    def generate_full_campaign_estimate(
        self,
        segment: str,
        channel: str,
        target_count: int,
        campaign_type: str = "general",
        incentive_value: float = 0.0
    ) -> Dict:
        """
        Generate complete campaign performance estimate

        Args:
            segment: Customer segment
            channel: Communication channel
            target_count: Number of members to target
            campaign_type: Type of campaign
            incentive_value: Value of incentive per participant

        Returns:
            dict: Complete campaign estimate with all metrics
        """
        # Step 1: Estimate participation
        participation_rate = self.estimate_participation_rate(
            segment, channel, campaign_type
        )
        estimated_participants = int(target_count * participation_rate)

        # Step 2: Calculate costs
        cost_breakdown = self.calculate_campaign_cost(
            channel,
            target_count,
            "points" if incentive_value > 0 else "none",
            incentive_value,
            estimated_participants
        )

        # Step 3: Estimate revenue
        revenue_estimate = self.estimate_revenue(
            segment,
            estimated_participants,
            campaign_type
        )

        # Step 4: Calculate ROI
        roi_metrics = self.calculate_roi(
            revenue_estimate["incremental_revenue"],
            cost_breakdown["total_cost"]
        )

        # Combine all metrics
        return {
            "segment": segment,
            "channel": channel,
            "campaign_type": campaign_type,
            "target_count": target_count,
            "participation_rate": round(participation_rate * 100, 1),  # As percentage
            "estimated_participants": estimated_participants,
            **cost_breakdown,
            **revenue_estimate,
            **roi_metrics,
            "confidence_score": self._calculate_confidence(target_count, campaign_type),
        }

    def _calculate_confidence(self, target_count: int, campaign_type: str) -> float:
        """
        Calculate confidence score for the estimate

        Args:
            target_count: Number of targets
            campaign_type: Campaign type

        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        # Higher confidence with more targets (more data)
        size_confidence = min(target_count / 1000, 1.0) * 0.5

        # Higher confidence for common campaign types
        type_confidence_map = {
            "welcome": 0.85,
            "promo": 0.80,
            "bonus": 0.75,
            "winback": 0.70,
            "tier_upgrade": 0.65,
            "general": 0.60,
        }
        type_confidence = type_confidence_map.get(campaign_type.lower(), 0.60) * 0.5

        return round(size_confidence + type_confidence, 2)


# Singleton instance
_estimator = None


def get_campaign_estimator() -> CampaignMetricsEstimator:
    """Get singleton instance of campaign estimator"""
    global _estimator
    if _estimator is None:
        _estimator = CampaignMetricsEstimator()
    return _estimator
