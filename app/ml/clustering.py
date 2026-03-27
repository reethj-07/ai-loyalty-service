from __future__ import annotations

import os
from typing import Dict, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


class DynamicSegmentClusterer:
    """
    Runs KMeans(n_clusters=5) on RFM feature vectors.
    Saves the fitted model to disk with joblib.
    Re-fits nightly via Celery beat schedule.
    Maps cluster IDs back to named segments by inspecting cluster centroids.
    """

    MODEL_PATH = "models/rfm_kmeans.joblib"

    def __init__(self):
        self.model: Optional[KMeans] = None
        self.cluster_name_map: Dict[int, str] = {}
        self.cluster_stats: Dict[str, Dict] = {}

    def fit(self, rfm_df: pd.DataFrame) -> None:
        if rfm_df.empty:
            raise ValueError("rfm_df cannot be empty")

        features = rfm_df[["R_score", "F_score", "M_score"]].astype(float)

        self.model = KMeans(n_clusters=5, random_state=42, n_init="auto")
        self.model.fit(features)

        labels = self.model.labels_
        work = rfm_df.copy()
        work["cluster_id"] = labels

        centroids = pd.DataFrame(
            self.model.cluster_centers_, columns=["R_score", "F_score", "M_score"]
        )
        centroids["cluster_id"] = centroids.index
        centroids["composite"] = 0.3 * centroids["R_score"] + 0.3 * centroids["F_score"] + 0.4 * centroids["M_score"]

        ordered_clusters = centroids.sort_values("composite", ascending=False)["cluster_id"].tolist()
        segment_order = ["Champions", "Loyal", "At Risk", "Dormant", "New"]
        self.cluster_name_map = {
            int(cluster_id): segment_order[idx] for idx, cluster_id in enumerate(ordered_clusters)
        }

        self.cluster_stats = {}
        for cluster_id, group in work.groupby("cluster_id"):
            name = self.cluster_name_map.get(int(cluster_id), f"Cluster {cluster_id}")
            self.cluster_stats[name] = {
                "cluster_id": int(cluster_id),
                "size": int(len(group)),
                "avg_r_score": round(float(group["R_score"].mean()), 2),
                "avg_f_score": round(float(group["F_score"].mean()), 2),
                "avg_m_score": round(float(group["M_score"].mean()), 2),
                "avg_rfm_score": round(float(group["rfm_score"].mean()), 2),
                "recommended_action": self._recommended_action(name),
            }

        os.makedirs(os.path.dirname(self.MODEL_PATH), exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "cluster_name_map": self.cluster_name_map,
                "cluster_stats": self.cluster_stats,
            },
            self.MODEL_PATH,
        )

    def predict_segment(self, member_rfm: Dict) -> str:
        if self.model is None:
            self._load_model()
        if self.model is None:
            return "Unknown"

        vector = np.array(
            [[
                float(member_rfm.get("R_score", 3)),
                float(member_rfm.get("F_score", 3)),
                float(member_rfm.get("M_score", 3)),
            ]]
        )
        cluster_id = int(self.model.predict(vector)[0])
        return self.cluster_name_map.get(cluster_id, "Unknown")

    def get_cluster_stats(self) -> Dict:
        """Returns per-cluster size, avg RFM, recommended action."""
        if not self.cluster_stats:
            self._load_model()
        return self.cluster_stats

    def _load_model(self) -> None:
        if not os.path.exists(self.MODEL_PATH):
            return

        payload = joblib.load(self.MODEL_PATH)
        self.model = payload.get("model")
        self.cluster_name_map = payload.get("cluster_name_map", {})
        self.cluster_stats = payload.get("cluster_stats", {})

    @staticmethod
    def _recommended_action(segment_name: str) -> str:
        actions = {
            "Champions": "Upsell premium bundles and referral bonuses",
            "Loyal": "Maintain engagement with streak and tier rewards",
            "At Risk": "Run targeted win-back incentives",
            "Dormant": "Use stronger reactivation campaigns",
            "New": "Onboard with welcome journey and first-purchase nudges",
        }
        return actions.get(segment_name, "Monitor and optimize segment strategy")
