"""
ML-Powered Campaign Recommender Service
Uses real ML models for intelligent campaign recommendations
"""
from typing import List, Dict
import asyncio
from datetime import datetime

from app.ml.segmentation_model import segmentation_model
from app.ml.roi_prediction_model import roi_prediction_model
from app.ml.feature_engineering import feature_engineer
from app.ml.campaign_metrics_estimator import get_campaign_estimator


class MLCampaignRecommenderService:
    """
    Intelligent campaign recommendation using ML models
    """

    async def get_recommendations(self) -> List[Dict]:
        """
        Generate campaign recommendations using ML models

        Returns:
            List of campaign recommendations with predicted ROI
        """
        try:
            # 1. Get customer segments using ML
            segmentation_results = await segmentation_model.predict()

            if "error" in segmentation_results:
                # Fallback to mock if no data
                return self._get_mock_recommendations()

            # 2. Analyze each segment and recommend campaigns
            recommendations = []

            for prediction in segmentation_results['predictions'][:10]:  # Top 10 members
                segment_name = prediction['segment_name']
                segment_profile = prediction['segment_profile']

                # 3. Generate campaign recommendation based on segment
                campaign = await self._recommend_campaign_for_segment(
                    segment_name,
                    segment_profile
                )

                if campaign:
                    # Get detailed cost and participation estimates
                    estimator = get_campaign_estimator()
                    estimates = estimator.generate_full_campaign_estimate(
                        segment=segment_name.lower().replace('-', '_'),
                        channel=campaign['channel'],
                        target_count=segment_profile['size'],
                        campaign_type=campaign.get('campaign_type', 'general'),
                        incentive_value=campaign.get('incentive_value', 5.0)  # $5 default incentive
                    )

                    recommendations.append({
                        "id": f"rec-{prediction['member_id'][:8]}",
                        "member_id": prediction['member_id'],
                        "segment": segment_name.lower().replace('-', '_'),
                        "behavior": self._infer_behavior(segment_profile),
                        "campaign": campaign['name'],
                        "campaign_channel": campaign['channel'],
                        "estimated_roi": f"{campaign['predicted_roi']:.0f}%",
                        "confidence": f"{campaign['confidence']:.2f}",
                        "segment_size": segment_profile['size'],
                        "recommendation_reason": campaign['reason'],
                        # NEW: Detailed metrics
                        "participation_rate": estimates['participation_rate'],
                        "estimated_participants": estimates['estimated_participants'],
                        "total_cost": estimates['total_cost'],
                        "message_cost": estimates['message_cost'],
                        "incentive_cost": estimates['incentive_cost'],
                        "estimated_revenue": estimates['estimated_revenue'],
                        "estimated_transactions": estimates['expected_transactions'],
                        "roi_percentage": estimates['roi_percentage'],
                        "profit": estimates['profit'],
                        "cost_per_acquisition": estimates['cost_per_acquisition'],
                    })

            # Deduplicate and return top 5
            unique_campaigns = self._deduplicate_campaigns(recommendations)
            return unique_campaigns[:5]

        except Exception as e:
            print(f"ML recommendation failed: {e}")
            return self._get_mock_recommendations()

    async def _recommend_campaign_for_segment(
        self,
        segment_name: str,
        segment_profile: Dict
    ) -> Dict:
        """
        Recommend best campaign for a segment using ML

        Args:
            segment_name: Name of the segment
            segment_profile: Segment characteristics

        Returns:
            Campaign recommendation with predicted ROI
        """
        # Campaign templates by segment type
        campaign_templates = {
            "Champions": [
                {
                    "name": "VIP Exclusive Rewards",
                    "channel": "email",
                    "type": "bonus_points",
                    "campaign_type": "bonus",
                    "incentive_value": 10.0  # $10 value
                },
                {
                    "name": "Early Access Sale",
                    "channel": "push",
                    "type": "push",
                    "campaign_type": "promo",
                    "incentive_value": 15.0
                },
            ],
            "High-Value": [
                {
                    "name": "2x Points Bonus Campaign",
                    "channel": "email",
                    "type": "email",
                    "campaign_type": "bonus",
                    "incentive_value": 8.0
                },
                {
                    "name": "Premium Tier Upgrade Offer",
                    "channel": "sms",
                    "type": "sms",
                    "campaign_type": "tier_upgrade",
                    "incentive_value": 12.0
                },
            ],
            "At-Risk": [
                {
                    "name": "We Miss You - Special Offer",
                    "channel": "email",
                    "type": "email",
                    "campaign_type": "winback",
                    "incentive_value": 10.0
                },
                {
                    "name": "Win Back Campaign",
                    "channel": "sms",
                    "type": "sms",
                    "campaign_type": "winback",
                    "incentive_value": 15.0
                },
            ],
            "New-Customers": [
                {
                    "name": "Welcome Bonus Campaign",
                    "channel": "sms",
                    "type": "email",
                    "campaign_type": "welcome",
                    "incentive_value": 5.0
                },
                {
                    "name": "Getting Started Guide + Rewards",
                    "channel": "email",
                    "type": "push",
                    "campaign_type": "welcome",
                    "incentive_value": 5.0
                },
            ]
        }

        templates = campaign_templates.get(segment_name, campaign_templates["High-Value"])

        # Predict ROI for each template
        best_campaign = None
        best_roi = -1

        for template in templates:
            # Prepare segment features for ROI prediction
            segment_features = {
                'segment_size': segment_profile['size'],
                'avg_recency': segment_profile['avg_recency_days'],
                'avg_frequency': segment_profile['avg_frequency'],
                'avg_monetary': segment_profile['avg_monetary'],
                'segment_engagement': 0.7 if segment_profile['characteristics']['recent'] else 0.4,
                'day_of_week': datetime.now().weekday(),
                'month': datetime.now().month,
                'historical_avg_roi': 0.5  # Could be fetched from DB
            }

            # Predict ROI using ML model
            roi_prediction = await roi_prediction_model.predict_roi(
                campaign_type=template['type'],
                segment_features=segment_features
            )

            predicted_roi = roi_prediction['predicted_roi']

            if predicted_roi > best_roi:
                best_roi = predicted_roi
                best_campaign = {
                    **template,
                    'predicted_roi': predicted_roi * 100,  # Convert to percentage
                    'confidence': roi_prediction['confidence_score'],
                    'reason': self._generate_reason(segment_name, segment_profile, template)
                }

        return best_campaign

    def _infer_behavior(self, segment_profile: Dict) -> str:
        """Infer behavior signal from segment characteristics"""
        chars = segment_profile['characteristics']

        if chars['high_value'] and chars['recent']:
            return "high_value_transaction"
        elif not chars['recent']:
            return "declining_engagement"
        elif segment_profile['avg_recency_days'] < 60:
            return "first_purchase"
        else:
            return "regular_activity"

    def _generate_reason(self, segment_name: str, profile: Dict, campaign: Dict) -> str:
        """Generate human-readable recommendation reason"""
        reasons = {
            "Champions": f"Top customers with ${profile['avg_monetary']:.0f} avg spend deserve VIP treatment",
            "High-Value": f"High spenders (${profile['avg_monetary']:.0f}) respond well to {campaign['channel']} campaigns",
            "At-Risk": f"Haven't purchased in {profile['avg_recency_days']:.0f} days - re-engagement needed",
            "New-Customers": f"New members need onboarding and early wins via {campaign['channel']}"
        }
        return reasons.get(segment_name, f"Segment of {profile['size']} members with growth potential")

    def _deduplicate_campaigns(self, recommendations: List[Dict]) -> List[Dict]:
        """Remove duplicate campaign types, keep best ROI"""
        seen_campaigns = {}

        for rec in recommendations:
            campaign_key = rec['campaign']

            if campaign_key not in seen_campaigns:
                seen_campaigns[campaign_key] = rec
            else:
                # Keep the one with higher ROI
                current_roi = float(seen_campaigns[campaign_key]['estimated_roi'].rstrip('%'))
                new_roi = float(rec['estimated_roi'].rstrip('%'))

                if new_roi > current_roi:
                    seen_campaigns[campaign_key] = rec

        # Sort by ROI
        sorted_campaigns = sorted(
            seen_campaigns.values(),
            key=lambda x: float(x['estimated_roi'].rstrip('%')),
            reverse=True
        )

        return sorted_campaigns

    def _get_mock_recommendations(self) -> List[Dict]:
        """Fallback mock recommendations if ML fails"""
        estimator = get_campaign_estimator()

        mock_campaigns = [
            {
                "id": "rec-001",
                "segment": "high_value",
                "behavior": "high_value_transaction",
                "campaign": "2x Points Bonus Campaign",
                "campaign_channel": "email",
                "campaign_type": "bonus",
                "target_count": 250,
                "incentive_value": 8.0
            },
            {
                "id": "rec-002",
                "segment": "at_risk",
                "behavior": "declining_engagement",
                "campaign": "We Miss You - Win Back Campaign",
                "campaign_channel": "email",
                "campaign_type": "winback",
                "target_count": 180,
                "incentive_value": 10.0
            },
            {
                "id": "rec-003",
                "segment": "new_customers",
                "behavior": "first_purchase",
                "campaign": "Welcome Bonus Campaign",
                "campaign_channel": "sms",
                "campaign_type": "welcome",
                "target_count": 120,
                "incentive_value": 5.0
            }
        ]

        recommendations = []
        for mock in mock_campaigns:
            estimates = estimator.generate_full_campaign_estimate(
                segment=mock["segment"],
                channel=mock["campaign_channel"],
                target_count=mock["target_count"],
                campaign_type=mock["campaign_type"],
                incentive_value=mock["incentive_value"]
            )

            recommendations.append({
                "id": mock["id"],
                "segment": mock["segment"],
                "behavior": mock["behavior"],
                "campaign": mock["campaign"],
                "campaign_channel": mock["campaign_channel"],
                "estimated_roi": f"{estimates['roi_percentage']:.0f}%",
                "confidence": f"{estimates['confidence_score']:.2f}",
                "recommendation_reason": f"{mock['campaign']} shows {estimates['roi_percentage']:.0f}% ROI for {mock['segment']} segments",
                # Detailed metrics
                "participation_rate": estimates['participation_rate'],
                "estimated_participants": estimates['estimated_participants'],
                "total_cost": estimates['total_cost'],
                "message_cost": estimates['message_cost'],
                "incentive_cost": estimates['incentive_cost'],
                "estimated_revenue": estimates['estimated_revenue'],
                "estimated_transactions": estimates['expected_transactions'],
                "roi_percentage": estimates['roi_percentage'],
                "profit": estimates['profit'],
                "cost_per_acquisition": estimates['cost_per_acquisition'],
                "target_count": mock["target_count"],
            })

        return recommendations


# Async wrapper for API compatibility
ml_recommender_service = MLCampaignRecommenderService()


async def recommend_campaigns_ml() -> List[Dict]:
    """
    Entry point for ML-powered campaign recommendations
    """
    return await ml_recommender_service.get_recommendations()
