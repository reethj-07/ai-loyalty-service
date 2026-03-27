from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

from app.core.redis_client import redis_client
from app.ml.clustering import DynamicSegmentClusterer
from app.ml.rfm_engine import RFMEngine
from app.repositories.supabase_transactions_repo import transactions_repo


class SegmentationService:
    CACHE_TTL_SECONDS = 3600

    def __init__(self):
        self.rfm_engine = RFMEngine()
        self.clusterer = DynamicSegmentClusterer()

    async def _get_scored_rfm(self) -> pd.DataFrame:
        transactions = await transactions_repo.get_all_transactions(limit=100000)
        base = self.rfm_engine.compute_rfm_dataframe(transactions)
        scored = self.rfm_engine.score_to_quintiles(base)
        return scored

    async def retrain(self) -> Dict:
        scored = await self._get_scored_rfm()
        if scored.empty:
            return {"status": "no_data", "message": "No transactions available for retraining"}

        self.clusterer.fit(scored)

        for row in scored.to_dict(orient="records"):
            segment_name = self.clusterer.predict_segment(row)
            payload = {
                **row,
                "cluster_segment": segment_name,
                "explanation": self._build_explanation(row, segment_name),
                "updated_at": datetime.utcnow().isoformat(),
            }
            self._cache_member_rfm(str(row["member_id"]), payload)

        return {
            "status": "retrained",
            "members_processed": int(len(scored)),
            "cluster_stats": self.clusterer.get_cluster_stats(),
        }

    async def get_member_rfm(self, member_id: str) -> Dict:
        cached = self._get_cached_member_rfm(member_id)
        if cached:
            return cached

        scored = await self._get_scored_rfm()
        if scored.empty:
            return {"member_id": member_id, "error": "No transaction history found"}

        row_df = scored[scored["member_id"].astype(str) == str(member_id)]
        if row_df.empty:
            return {"member_id": member_id, "error": "Member has no transaction history"}

        row = row_df.iloc[0].to_dict()
        segment_name = self.clusterer.predict_segment(row)
        payload = {
            **row,
            "cluster_segment": segment_name,
            "explanation": self._build_explanation(row, segment_name),
        }
        self._cache_member_rfm(member_id, payload)
        return payload

    async def get_member_segment(self, member_id: str) -> Dict:
        member_rfm = await self.get_member_rfm(member_id)
        if "error" in member_rfm:
            return {
                "segment": "Unknown",
                "confidence": 0.0,
                "explanation": member_rfm["error"],
            }

        return {
            "segment": member_rfm.get("cluster_segment", member_rfm.get("named_segment", "Unknown")),
            "confidence": round(float(member_rfm.get("rfm_score", 0.0)) / 5, 2),
            "explanation": member_rfm.get("explanation", ""),
            "rfm_score": member_rfm.get("rfm_score"),
        }

    async def get_segment_stats(self) -> Dict:
        stats = self.clusterer.get_cluster_stats()
        if not stats:
            retrained = await self.retrain()
            if retrained.get("status") == "retrained":
                stats = retrained.get("cluster_stats", {})

        feature_importances = self._feature_importance_proxy(stats)
        return {
            "clusters": stats,
            "feature_importances": feature_importances,
            "generated_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def _build_explanation(row: Dict, segment_name: str) -> str:
        recency_days = int(float(row.get("recency_days", 0)))
        r_score = int(row.get("R_score", 0))
        f_score = int(row.get("F_score", 0))
        m_score = int(row.get("M_score", 0))
        return (
            f"Member is {segment_name} because last purchase was {recency_days} days ago "
            f"(R={r_score}) with frequency score F={f_score} and monetary score M={m_score}."
        )

    def _cache_member_rfm(self, member_id: str, payload: Dict) -> None:
        try:
            redis_client.setex(
                f"rfm:{member_id}",
                self.CACHE_TTL_SECONDS,
                json.dumps(payload, default=str),
            )
        except Exception:
            return

    @staticmethod
    def _get_cached_member_rfm(member_id: str) -> Optional[Dict]:
        try:
            raw = redis_client.get(f"rfm:{member_id}")
            if not raw:
                return None
            return json.loads(raw)
        except Exception:
            return None

    @staticmethod
    def _feature_importance_proxy(cluster_stats: Dict) -> Dict[str, float]:
        if not cluster_stats:
            return {"recency": 0.33, "frequency": 0.33, "monetary": 0.34}

        r_vals: List[float] = []
        f_vals: List[float] = []
        m_vals: List[float] = []

        for cluster in cluster_stats.values():
            r_vals.append(float(cluster.get("avg_r_score", 0.0)))
            f_vals.append(float(cluster.get("avg_f_score", 0.0)))
            m_vals.append(float(cluster.get("avg_m_score", 0.0)))

        r_var = pd.Series(r_vals).std() or 0.0
        f_var = pd.Series(f_vals).std() or 0.0
        m_var = pd.Series(m_vals).std() or 0.0
        total = r_var + f_var + m_var

        if total <= 0:
            return {"recency": 0.33, "frequency": 0.33, "monetary": 0.34}

        return {
            "recency": round(r_var / total, 3),
            "frequency": round(f_var / total, 3),
            "monetary": round(m_var / total, 3),
        }


_segmentation_service: Optional[SegmentationService] = None


def get_segmentation_service() -> SegmentationService:
    global _segmentation_service
    if _segmentation_service is None:
        _segmentation_service = SegmentationService()
    return _segmentation_service
