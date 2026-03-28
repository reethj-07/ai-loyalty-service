from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

import pandas as pd


class RFMEngine:
    """
    Computes RFM scores for all members from transaction history.

    R (Recency):   days since last transaction (lower = better)
    F (Frequency): number of transactions in last 90 days
    M (Monetary):  total spend in last 90 days

    Each dimension is scored 1-5 using quintile binning.
    Combined RFM score = weighted sum: 0.3*R + 0.3*F + 0.4*M
    """

    def compute_rfm_dataframe(self, transactions: List[Dict]) -> pd.DataFrame:
        if not transactions:
            return pd.DataFrame(
                columns=["member_id", "recency_days", "frequency_90d", "monetary_90d"]
            )

        df = pd.DataFrame(transactions)

        if "member_id" not in df.columns:
            raise ValueError("transactions payload must include member_id")

        ts_col = "transaction_date" if "transaction_date" in df.columns else "timestamp"
        if ts_col not in df.columns:
            ts_col = "created_at"

        df[ts_col] = pd.to_datetime(df[ts_col], errors="coerce", utc=True)
        df["amount"] = pd.to_numeric(df.get("amount", 0.0), errors="coerce").fillna(0.0)

        now = datetime.now(timezone.utc)
        cutoff = pd.Timestamp(now) - pd.Timedelta(days=90)

        last_txn = df.groupby("member_id")[ts_col].max().rename("last_transaction")
        recent_df = df[df[ts_col] >= cutoff]

        agg_recent = (
            recent_df.groupby("member_id")
            .agg(
                frequency_90d=("member_id", "count"),
                monetary_90d=("amount", "sum"),
            )
            .reset_index()
        )

        base = last_txn.reset_index().merge(agg_recent, on="member_id", how="left")
        base["frequency_90d"] = base["frequency_90d"].fillna(0).astype(int)
        base["monetary_90d"] = base["monetary_90d"].fillna(0.0).astype(float)
        base["recency_days"] = (
            (pd.Timestamp(now) - base["last_transaction"]).dt.total_seconds() / 86400
        ).fillna(9999).astype(float)

        return base[["member_id", "recency_days", "frequency_90d", "monetary_90d"]]

    def score_to_quintiles(self, df: pd.DataFrame) -> pd.DataFrame:
        """Use pd.qcut for quintile binning on each R, F, M column."""
        if df.empty:
            return df

        out = df.copy()

        def should_use_quintiles(series: pd.Series) -> bool:
            return len(out) >= 5 and series.nunique() > 1

        if should_use_quintiles(out["recency_days"]):
            out["R_score"] = self._safe_qcut_rank(out["recency_days"], reverse=True)
        else:
            out["R_score"] = out["recency_days"].apply(self._score_recency_by_thresholds).astype(int)

        if should_use_quintiles(out["frequency_90d"]):
            out["F_score"] = self._safe_qcut_rank(out["frequency_90d"], reverse=False)
        else:
            out["F_score"] = out["frequency_90d"].apply(self._score_frequency_by_thresholds).astype(int)

        if should_use_quintiles(out["monetary_90d"]):
            out["M_score"] = self._safe_qcut_rank(out["monetary_90d"], reverse=False)
        else:
            out["M_score"] = out["monetary_90d"].apply(self._score_monetary_by_thresholds).astype(int)

        out["rfm_score"] = (
            0.3 * out["R_score"] + 0.3 * out["F_score"] + 0.4 * out["M_score"]
        ).round(2)
        out["named_segment"] = out["rfm_score"].apply(self.assign_named_segment)

        return out

    def assign_named_segment(self, rfm_score: float) -> str:
        """
        Map combined score to human-readable segment:
        >= 4.0: Champions
        3.0-3.9: Loyal
        2.0-2.9: At Risk
        1.0-1.9: Dormant
        < 1.0:  New
        """
        score = float(rfm_score)
        if score >= 4.0:
            return "Champions"
        if score >= 3.0:
            return "Loyal"
        if score >= 2.0:
            return "At Risk"
        if score >= 1.0:
            return "Dormant"
        return "New"

    @staticmethod
    def _safe_qcut_rank(series: pd.Series, reverse: bool = False) -> pd.Series:
        ranked = series.rank(method="first")
        bins = min(5, ranked.nunique())

        if bins <= 1:
            return pd.Series([3] * len(series), index=series.index, dtype=int)

        labels = list(range(1, bins + 1))
        scored = pd.qcut(ranked, q=bins, labels=labels, duplicates="drop")
        scored = scored.astype(int)

        if reverse:
            max_score = int(scored.max())
            scored = (max_score + 1) - scored

        if bins < 5:
            scored = (scored / bins * 5).round().clip(1, 5).astype(int)

        return scored

    @staticmethod
    def _score_recency_by_thresholds(recency_days: float) -> int:
        if recency_days <= 7:
            return 5
        if recency_days <= 30:
            return 4
        if recency_days <= 60:
            return 3
        if recency_days <= 120:
            return 2
        return 1

    @staticmethod
    def _score_frequency_by_thresholds(frequency_90d: float) -> int:
        if frequency_90d >= 12:
            return 5
        if frequency_90d >= 8:
            return 4
        if frequency_90d >= 4:
            return 3
        if frequency_90d >= 2:
            return 2
        return 1

    @staticmethod
    def _score_monetary_by_thresholds(monetary_90d: float) -> int:
        if monetary_90d >= 2000:
            return 5
        if monetary_90d >= 1000:
            return 4
        if monetary_90d >= 500:
            return 3
        if monetary_90d >= 100:
            return 2
        return 1
