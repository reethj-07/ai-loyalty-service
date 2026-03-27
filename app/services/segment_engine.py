from typing import Dict, List
from collections import defaultdict
from app.schemas.segments import SegmentState, SegmentShift


class SegmentEngine:
    """
    Aggregates member states into segment-level intelligence
    """

    def compute_segments(self, member_states: List[Dict]) -> Dict[str, SegmentState]:
        buckets = defaultdict(list)

        for state in member_states:
            segment = state.get("segment")
            if not segment:
                continue
            buckets[segment].append(state)

        segments = {}
        for segment, members in buckets.items():
            size = len(members)
            if size == 0:
                continue

            segments[segment] = SegmentState(
                segment_id=segment,
                size=size,
                avg_spend=sum(m.get("avg_spend", 0) for m in members) / size,
                activity_rate=sum(m.get("activity_rate", 0) for m in members) / size,
                risk_score_avg=sum(m.get("risk_score", 0) for m in members) / size,
            )

        return segments

    def detect_shifts(
        self,
        previous: Dict[str, SegmentState],
        current: Dict[str, SegmentState],
        threshold: float = 0.2,
    ) -> List[SegmentShift]:

        shifts = []

        for seg_id, curr in current.items():
            prev = previous.get(seg_id)
            if not prev:
                continue

            change_ratio = (curr.size - prev.size) / max(prev.size, 1)

            if abs(change_ratio) >= threshold:
                shifts.append(
                    SegmentShift(
                        segment_id=seg_id,
                        previous_size=prev.size,
                        current_size=curr.size,
                        change_ratio=round(change_ratio, 2),
                        reason="significant_segment_size_change",
                    )
                )

        return shifts
