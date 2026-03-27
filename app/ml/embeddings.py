from __future__ import annotations

from typing import Dict, List

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Uses all-MiniLM-L6-v2 (22MB, runs locally, no API key needed).
    Produces 384-dim embeddings suitable for pgvector.
    """

    _model: SentenceTransformer = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._model

    def embed_text(self, text: str) -> List[float]:
        return self.get_model().encode(text).tolist()

    def embed_member_behavior(self, member: Dict, transactions: List[Dict]) -> str:
        """Converts member + transaction history into a natural-language summary, then embeds it."""
        first_name = member.get("first_name", "Member")
        tier = member.get("tier", "Unknown")
        points = member.get("points_balance", member.get("points", 0))

        tx_count = len(transactions)
        total_spend = sum(float(item.get("amount", 0.0) or 0.0) for item in transactions)
        avg_spend = (total_spend / tx_count) if tx_count else 0.0

        summary = (
            f"{first_name} is in {tier} tier with {points} points. "
            f"Recent activity includes {tx_count} transactions totaling {total_spend:.2f} "
            f"with average spend {avg_spend:.2f}."
        )
        _ = self.embed_text(summary)
        return summary
