"""
ROI Prediction Model
Uses Random Forest to predict campaign ROI based on features
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os
from typing import Dict, List, Tuple
from datetime import datetime

from app.ml.feature_engineering import feature_engineer


class ROIPredictionModel:
    """ML-based ROI prediction for campaigns"""

    def __init__(self):
        """Initialize ROI prediction model"""
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.is_trained = False
        self.feature_importance = {}

    async def train(self, historical_campaigns: List[Dict]) -> Dict:
        """
        Train ROI prediction model on historical campaign data

        Args:
            historical_campaigns: List of past campaigns with outcomes

        Returns:
            Training metrics
        """
        if len(historical_campaigns) < 20:
            # Not enough data, return mock predictions
            return {
                "status": "insufficient_data",
                "message": "Need at least 20 historical campaigns to train",
                "campaigns_count": len(historical_campaigns)
            }

        # Prepare training data
        X, y = self._prepare_training_data(historical_campaigns)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        self.model.fit(X_train, y_train)

        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        # Feature importance
        self.feature_importance = dict(zip(
            self._get_feature_names(),
            self.model.feature_importances_
        ))

        self.is_trained = True

        return {
            "status": "success",
            "campaigns_count": len(historical_campaigns),
            "train_r2_score": float(train_score),
            "test_r2_score": float(test_score),
            "feature_importance": {k: float(v) for k, v in self.feature_importance.items()},
            "trained_at": datetime.now().isoformat()
        }

    def _prepare_training_data(self, campaigns: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and labels from historical campaigns"""
        X_list = []
        y_list = []

        for campaign in campaigns:
            # Extract features
            features = self._extract_campaign_features(campaign)
            X_list.append(features)

            # Target: actual ROI
            roi = campaign.get('actual_roi', campaign.get('roi', 0))
            y_list.append(roi)

        return np.array(X_list), np.array(y_list)

    def _extract_campaign_features(self, campaign: Dict) -> List[float]:
        """Extract features from campaign data"""
        # Campaign type encoding
        campaign_type = campaign.get('type', 'email')
        type_encoding = {
            'email': [1, 0, 0, 0],
            'sms': [0, 1, 0, 0],
            'push': [0, 0, 1, 0],
            'bonus_points': [0, 0, 0, 1]
        }
        campaign_features = type_encoding.get(campaign_type, [0, 0, 0, 0])

        # Segment features
        segment_features = [
            campaign.get('segment_size', 100),
            campaign.get('avg_recency', 30),
            campaign.get('avg_frequency', 5),
            campaign.get('avg_monetary', 1000),
            campaign.get('segment_engagement', 0.5),
        ]

        # Campaign-specific features
        offer_value = campaign.get('offer_value', 10)  # Discount percentage or points
        estimated_cost = campaign.get('estimated_cost', 100)

        # Temporal features
        day_of_week = campaign.get('day_of_week', 3) / 7.0  # Normalized
        month = campaign.get('month', 6) / 12.0  # Normalized

        # Historical performance
        historical_avg_roi = campaign.get('historical_avg_roi', 0.5)

        # Combine all features
        features = (
            campaign_features +
            segment_features +
            [offer_value, estimated_cost, day_of_week, month, historical_avg_roi]
        )

        return features

    def _get_feature_names(self) -> List[str]:
        """Get feature names for interpretation"""
        return [
            'is_email', 'is_sms', 'is_push', 'is_bonus_points',
            'segment_size', 'avg_recency', 'avg_frequency', 'avg_monetary', 'segment_engagement',
            'offer_value', 'estimated_cost', 'day_of_week', 'month', 'historical_avg_roi'
        ]

    async def predict_roi(
        self,
        campaign_type: str,
        segment_features: Dict,
        offer_details: Dict = None
    ) -> Dict:
        """
        Predict ROI for a proposed campaign

        Args:
            campaign_type: Type of campaign (email, SMS, push, bonus_points)
            segment_features: Features of target segment
            offer_details: Campaign offer details

        Returns:
            ROI prediction with confidence interval
        """
        if not self.is_trained:
            # Use rule-based estimation if model not trained
            return self._rule_based_roi_estimate(campaign_type, segment_features)

        # Prepare features
        campaign_data = {
            'type': campaign_type,
            **segment_features,
            **(offer_details or {})
        }

        features = self._extract_campaign_features(campaign_data)
        X = np.array([features])

        # Predict
        predicted_roi = self.model.predict(X)[0]

        # Calculate confidence interval using tree predictions
        tree_predictions = np.array([tree.predict(X)[0] for tree in self.model.estimators_])
        std = np.std(tree_predictions)
        confidence_interval = (
            float(predicted_roi - 1.96 * std),
            float(predicted_roi + 1.96 * std)
        )

        return {
            "predicted_roi": float(predicted_roi),
            "confidence_interval": confidence_interval,
            "confidence_score": float(1.0 - min(std / (abs(predicted_roi) + 1), 1.0)),
            "model_used": "random_forest",
            "prediction_date": datetime.now().isoformat()
        }

    def _rule_based_roi_estimate(self, campaign_type: str, segment_features: Dict) -> Dict:
        """Fallback rule-based ROI estimation"""
        # Base ROI by campaign type
        base_roi = {
            'email': 0.42,
            'sms': 0.58,
            'push': 0.35,
            'bonus_points': 0.72
        }.get(campaign_type, 0.50)

        # Adjust based on segment quality
        segment_quality = segment_features.get('segment_engagement', 0.5)
        adjusted_roi = base_roi * (0.5 + segment_quality)

        return {
            "predicted_roi": float(adjusted_roi),
            "confidence_interval": (
                float(adjusted_roi * 0.7),
                float(adjusted_roi * 1.3)
            ),
            "confidence_score": 0.6,
            "model_used": "rule_based",
            "note": "Using rule-based estimation. Train model with historical data for better predictions.",
            "prediction_date": datetime.now().isoformat()
        }

    def save_model(self, path: str = "models/roi_prediction_model.pkl"):
        """Save trained model"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'is_trained': self.is_trained,
            'feature_importance': self.feature_importance
        }, path)

    def load_model(self, path: str = "models/roi_prediction_model.pkl"):
        """Load trained model"""
        if not os.path.exists(path):
            return False

        data = joblib.load(path)
        self.model = data['model']
        self.is_trained = data['is_trained']
        self.feature_importance = data.get('feature_importance', {})
        return True


# Singleton instance
roi_prediction_model = ROIPredictionModel()
