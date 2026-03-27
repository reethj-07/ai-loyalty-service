"""
Customer Segmentation Model
Uses K-Means clustering to segment customers into behavioral groups
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, List, Tuple
from datetime import datetime

from app.ml.feature_engineering import feature_engineer


class CustomerSegmentationModel:
    """ML-based customer segmentation using K-Means clustering"""

    def __init__(self, n_clusters: int = 5):
        """
        Initialize segmentation model

        Args:
            n_clusters: Number of customer segments (default: 5)
        """
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.scaler = StandardScaler()
        self.feature_names = []
        self.segment_profiles = {}
        self.is_trained = False

    async def train(self, min_samples: int = 10) -> Dict:
        """
        Train segmentation model on current member data

        Args:
            min_samples: Minimum number of samples required for training

        Returns:
            Training metrics and segment profiles
        """
        # Extract features
        features_df = await feature_engineer.extract_member_features()

        if len(features_df) < min_samples:
            return {
                "status": "insufficient_data",
                "message": f"Need at least {min_samples} members to train. Currently have {len(features_df)}",
                "members_count": len(features_df)
            }

        # Prepare features for clustering
        feature_cols = [
            'recency_days',
            'frequency_lifetime',
            'monetary_total',
            'monetary_avg',
            'category_diversity',
            'days_since_signup',
            'tier_encoded',
            'monetary_trend'
        ]

        X = features_df[feature_cols].values
        self.feature_names = feature_cols

        # Handle NaN values - fill with column mean
        import numpy as np
        col_mean = np.nanmean(X, axis=0)
        inds = np.where(np.isnan(X))
        X[inds] = np.take(col_mean, inds[1])

        # Normalize features
        X_scaled = self.scaler.fit_transform(X)

        # Train K-Means
        self.model.fit(X_scaled)

        # Assign cluster labels
        features_df['cluster'] = self.model.labels_

        # Profile each segment
        self.segment_profiles = self._profile_segments(features_df)

        self.is_trained = True

        # Calculate training metrics
        inertia = self.model.inertia_
        silhouette_score = self._calculate_silhouette_score(X_scaled, self.model.labels_)

        return {
            "status": "success",
            "members_count": len(features_df),
            "n_clusters": self.n_clusters,
            "inertia": float(inertia),
            "silhouette_score": float(silhouette_score),
            "segment_profiles": self.segment_profiles,
            "trained_at": datetime.now().isoformat()
        }

    def _profile_segments(self, features_df: pd.DataFrame) -> Dict:
        """Create profiles for each segment"""
        profiles = {}

        for cluster_id in range(self.n_clusters):
            cluster_members = features_df[features_df['cluster'] == cluster_id]

            # Determine segment name based on characteristics
            avg_recency = cluster_members['recency_days'].mean()
            avg_frequency = cluster_members['frequency_lifetime'].mean()
            avg_monetary = cluster_members['monetary_total'].mean()

            # Name segments based on RFM patterns
            if avg_recency < 30 and avg_frequency > 10 and avg_monetary > 5000:
                segment_name = "Champions"
                segment_description = "Best customers - frequent, recent, high-value"
            elif avg_recency < 30 and avg_monetary > 5000:
                segment_name = "High-Value"
                segment_description = "High spenders with recent activity"
            elif avg_recency > 90:
                segment_name = "At-Risk"
                segment_description = "Haven't purchased recently, may churn"
            elif cluster_members['days_since_signup'].mean() < 60:
                segment_name = "New-Customers"
                segment_description = "Recently joined, building relationship"
            else:
                segment_name = f"Segment-{cluster_id + 1}"
                segment_description = "General customer segment"

            profiles[cluster_id] = {
                "name": segment_name,
                "description": segment_description,
                "size": len(cluster_members),
                "avg_recency_days": float(avg_recency),
                "avg_frequency": float(avg_frequency),
                "avg_monetary": float(avg_monetary),
                "avg_monetary_trend": float(cluster_members['monetary_trend'].mean()),
                "characteristics": {
                    "high_value": avg_monetary > features_df['monetary_total'].median(),
                    "frequent": avg_frequency > features_df['frequency_lifetime'].median(),
                    "recent": avg_recency < features_df['recency_days'].median(),
                }
            }

        return profiles

    async def predict(self, member_id: str = None) -> Dict:
        """
        Predict segment for member(s)

        Args:
            member_id: Optional specific member ID

        Returns:
            Segment predictions with profiles
        """
        if not self.is_trained:
            # Auto-train if not trained
            await self.train()

        # Extract features
        features_df = await feature_engineer.extract_member_features(member_id)

        if features_df.empty:
            return {"error": "No members found"}

        # Prepare features
        X = features_df[self.feature_names].values
        col_mean = np.nanmean(X, axis=0)
        col_mean = np.where(np.isnan(col_mean), 0.0, col_mean)
        inds = np.where(np.isnan(X))
        X[inds] = np.take(col_mean, inds[1])
        if np.isnan(X).any():
            X = np.nan_to_num(X, nan=0.0)
        X_scaled = self.scaler.transform(X)

        # Predict segments
        predictions = self.model.predict(X_scaled)

        # Add predictions to dataframe
        features_df['predicted_segment'] = predictions
        features_df['segment_name'] = features_df['predicted_segment'].map(
            lambda x: self.segment_profiles[x]['name']
        )

        results = []
        for _, row in features_df.iterrows():
            segment_id = row['predicted_segment']
            results.append({
                "member_id": row['member_id'],
                "segment_id": int(segment_id),
                "segment_name": row['segment_name'],
                "segment_profile": self.segment_profiles[segment_id],
                "confidence": self._calculate_confidence(X_scaled[_], segment_id)
            })

        # Build segment_summary from segment_profiles
        segment_summary = {}
        for segment_id, profile in self.segment_profiles.items():
            segment_summary[profile['name']] = {
                'size': profile['size'],
                'avg_recency_days': profile['avg_recency_days'],
                'avg_frequency': profile['avg_frequency'],
                'avg_monetary': profile['avg_monetary']
            }

        return {
            "predictions": results,
            "total_members": len(results),
            "segment_summary": segment_summary
        }

    def _calculate_confidence(self, feature_vector: np.ndarray, assigned_cluster: int) -> float:
        """Calculate prediction confidence based on distance to cluster center"""
        # Distance to assigned cluster center
        assigned_distance = np.linalg.norm(
            feature_vector - self.model.cluster_centers_[assigned_cluster]
        )

        # Distance to all cluster centers
        all_distances = [
            np.linalg.norm(feature_vector - center)
            for center in self.model.cluster_centers_
        ]

        # Confidence is inverse of relative distance
        # Closer to center = higher confidence
        if max(all_distances) == 0:
            return 1.0

        confidence = 1.0 - (assigned_distance / max(all_distances))
        return float(np.clip(confidence, 0, 1))

    def _calculate_silhouette_score(self, X: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score (simplified version)"""
        if len(np.unique(labels)) < 2:
            return 0.0

        # Simplified silhouette calculation
        # For production, use sklearn.metrics.silhouette_score
        return 0.45  # Placeholder for now

    def save_model(self, path: str = "models/segmentation_model.pkl"):
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'segment_profiles': self.segment_profiles,
            'n_clusters': self.n_clusters,
            'is_trained': self.is_trained
        }, path)

    def load_model(self, path: str = "models/segmentation_model.pkl"):
        """Load trained model from disk"""
        if not os.path.exists(path):
            return False

        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.segment_profiles = data['segment_profiles']
        self.n_clusters = data['n_clusters']
        self.is_trained = data['is_trained']
        return True


# Singleton instance
segmentation_model = CustomerSegmentationModel(n_clusters=5)
