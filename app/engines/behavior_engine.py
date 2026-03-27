from typing import Dict, List


class BehaviorEngine:

    def compute_metrics(self, events: List[Dict]) -> Dict[str, float]:
        total_spend = sum(e.get("amount", 0) for e in events)
        txn_count = len(events)

        avg_ticket = total_spend / txn_count if txn_count else 0

        return {
            "total_spend": total_spend,
            "txn_count": txn_count,
            "avg_ticket": avg_ticket,
        }

    def detect_signals(self, prev: Dict, curr: Dict) -> List[Dict]:
        signals = []

        if prev:
            if curr["total_spend"] < prev.get("total_spend", 0) * 0.7:
                signals.append({
                    "type": "spend_drop_detected",
                    "confidence": 0.75
                })

        return signals
