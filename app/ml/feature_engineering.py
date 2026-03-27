"""
Feature Engineering Pipeline for ML Models
Extracts and transforms features for customer segmentation and ROI prediction
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.repositories.supabase_members_repo import members_repo
from app.repositories.supabase_transactions_repo import transactions_repo


class FeatureEngineer:
    """Extracts and engineers features from raw data"""

    @staticmethod
    async def extract_member_features(member_id: str = None) -> pd.DataFrame:
        """
        Extract RFM (Recency, Frequency, Monetary) and behavioral features

        Args:
            member_id: Optional specific member ID. If None, extracts for all members.

        Returns:
            DataFrame with engineered features
        """
        # Get all members
        members = await members_repo.get_all_members()
        members_df = pd.DataFrame(members)

        # Get all transactions
        transactions = await transactions_repo.get_all_transactions()
        trans_df = pd.DataFrame(transactions)

        if trans_df.empty:
            # Return basic features if no transactions
            return members_df

        if "amount" in trans_df.columns:
            trans_df["amount"] = (
                pd.to_numeric(trans_df["amount"], errors="coerce")
                .fillna(0.0)
            )

        date_col = "transaction_date" if "transaction_date" in trans_df.columns else "created_at"
        trans_df["transaction_date"] = pd.to_datetime(
            trans_df[date_col], utc=True, errors="coerce"
        )

        # Convert dates (handle timezone)
        current_date = pd.Timestamp.now(tz='UTC')

        # Group by member
        member_features = []

        for _, member in members_df.iterrows():
            mid = member['id']
            member_trans = trans_df[trans_df['member_id'] == mid]
            member_trans = member_trans.dropna(subset=['transaction_date'])

            if member_trans.empty:
                # New member with no transactions
                features = {
                    'member_id': mid,
                    'recency_days': 999,  # No transactions
                    'frequency_30d': 0,
                    'frequency_60d': 0,
                    'frequency_90d': 0,
                    'frequency_lifetime': 0,
                    'monetary_total': 0,
                    'monetary_avg': 0,
                    'monetary_max': 0,
                    'monetary_30d': 0,
                    'monetary_trend': 0,  # Spending trend
                    'days_since_signup': (current_date - pd.to_datetime(member['created_at'])).days,
                    'points_balance': member['points_balance'],
                    'tier': member['tier'],
                    'status': member['status'],
                    'category_diversity': 0,  # Number of unique categories
                    'avg_days_between_trans': 0,
                }
            else:
                # Calculate dates
                last_trans_date = member_trans['transaction_date'].max()
                recency_days = (current_date - last_trans_date).days

                # Frequency features
                days_30_ago = current_date - timedelta(days=30)
                days_60_ago = current_date - timedelta(days=60)
                days_90_ago = current_date - timedelta(days=90)

                freq_30d = len(member_trans[member_trans['transaction_date'] >= days_30_ago])
                freq_60d = len(member_trans[member_trans['transaction_date'] >= days_60_ago])
                freq_90d = len(member_trans[member_trans['transaction_date'] >= days_90_ago])
                freq_lifetime = len(member_trans)

                # Monetary features
                monetary_total = member_trans['amount'].sum()
                monetary_avg = member_trans['amount'].mean()
                monetary_max = member_trans['amount'].max()
                monetary_30d = member_trans[member_trans['transaction_date'] >= days_30_ago]['amount'].sum()

                # Spending trend (recent vs historical)
                recent_avg = member_trans[member_trans['transaction_date'] >= days_30_ago]['amount'].mean()
                historical_avg = member_trans[member_trans['transaction_date'] < days_30_ago]['amount'].mean()
                if pd.isna(recent_avg):
                    recent_avg = 0.0
                if pd.isna(historical_avg):
                    historical_avg = 0.0
                monetary_trend = (recent_avg - historical_avg) / (historical_avg + 1)  # Avoid division by zero

                # Category diversity
                if 'category' in member_trans.columns:
                    category_diversity = member_trans['category'].nunique()
                else:
                    category_diversity = 0

                # Average days between transactions
                sorted_dates = member_trans['transaction_date'].sort_values()
                if len(sorted_dates) > 1:
                    date_diffs = sorted_dates.diff().dt.days.dropna()
                    avg_days_between = date_diffs.mean()
                else:
                    avg_days_between = 0

                features = {
                    'member_id': mid,
                    'recency_days': recency_days,
                    'frequency_30d': freq_30d,
                    'frequency_60d': freq_60d,
                    'frequency_90d': freq_90d,
                    'frequency_lifetime': freq_lifetime,
                    'monetary_total': monetary_total,
                    'monetary_avg': monetary_avg,
                    'monetary_max': monetary_max,
                    'monetary_30d': monetary_30d,
                    'monetary_trend': monetary_trend,
                    'days_since_signup': (current_date - pd.to_datetime(member['created_at'])).days,
                    'points_balance': member['points_balance'],
                    'tier': member['tier'],
                    'status': member['status'],
                    'category_diversity': category_diversity,
                    'avg_days_between_trans': avg_days_between,
                }

            member_features.append(features)

        features_df = pd.DataFrame(member_features)

        # Encode categorical variables
        tier_mapping = {'Bronze': 1, 'Silver': 2, 'Gold': 3, 'Platinum': 4}
        features_df['tier_encoded'] = features_df['tier'].map(tier_mapping).fillna(1)

        status_mapping = {'active': 1, 'inactive': 0}
        features_df['status_encoded'] = features_df['status'].map(status_mapping).fillna(0)

        # Calculate RFM score (normalized)
        features_df['recency_score'] = 1 / (1 + features_df['recency_days'] / 30)  # Higher = better (more recent)
        features_df['frequency_score'] = np.log1p(features_df['frequency_lifetime'])  # Log transform
        features_df['monetary_score'] = np.log1p(features_df['monetary_total'])  # Log transform

        # Overall RFM score
        features_df['rfm_score'] = (
            features_df['recency_score'] * 0.3 +
            features_df['frequency_score'] * 0.3 +
            features_df['monetary_score'] * 0.4
        )

        return features_df

    @staticmethod
    def prepare_segmentation_features(features_df: pd.DataFrame) -> np.ndarray:
        """
        Prepare features for customer segmentation (clustering)

        Args:
            features_df: DataFrame with engineered features

        Returns:
            Numpy array with normalized features for clustering
        """
        # Select key features for segmentation
        feature_cols = [
            'recency_days',
            'frequency_lifetime',
            'monetary_total',
            'monetary_avg',
            'category_diversity',
            'days_since_signup',
            'tier_encoded'
        ]

        X = features_df[feature_cols].values

        # Normalize features (StandardScaler equivalent)
        X_normalized = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

        return X_normalized

    @staticmethod
    def prepare_roi_features(
        campaign_type: str,
        target_segment_features: Dict,
        historical_campaigns: List[Dict]
    ) -> np.ndarray:
        """
        Prepare features for ROI prediction

        Args:
            campaign_type: Type of campaign (email, SMS, push, bonus_points)
            target_segment_features: Aggregated features of target segment
            historical_campaigns: Historical campaign performance data

        Returns:
            Feature vector for ROI prediction
        """
        # Campaign type encoding
        campaign_type_encoding = {
            'email': [1, 0, 0, 0],
            'sms': [0, 1, 0, 0],
            'push': [0, 0, 1, 0],
            'bonus_points': [0, 0, 0, 1]
        }
        campaign_features = campaign_type_encoding.get(campaign_type, [0, 0, 0, 0])

        # Segment features (aggregated)
        segment_features = [
            target_segment_features.get('avg_recency', 30),
            target_segment_features.get('avg_frequency', 5),
            target_segment_features.get('avg_monetary', 1000),
            target_segment_features.get('segment_size', 100),
            target_segment_features.get('avg_engagement', 0.5),
        ]

        # Historical performance (avg ROI for this campaign type + segment combo)
        historical_roi = 0.5  # Default
        if historical_campaigns:
            similar_campaigns = [c for c in historical_campaigns if c.get('type') == campaign_type]
            if similar_campaigns:
                historical_roi = np.mean([c.get('roi', 0.5) for c in similar_campaigns])

        # Seasonality (day of week, time of year)
        current_date = datetime.now()
        day_of_week = current_date.weekday() / 7.0  # Normalized
        month = current_date.month / 12.0  # Normalized

        # Combine all features
        features = campaign_features + segment_features + [historical_roi, day_of_week, month]

        return np.array(features)


# Singleton instance
feature_engineer = FeatureEngineer()
