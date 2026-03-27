from collections import defaultdict
from typing import Dict, List

from app.schemas.segments import SegmentState
from app.schemas.ai_response import MemberState


class SegmentAggregator:
    """
    Aggregates member states into segment-level metrics.
    """

    def aggregate(
        self, member_states: List[MemberState]
    ) -> Dict[str, SegmentState]:

        buckets = defaultdict(list)

        for state in member_states:
            buckets[state.segment].append(state)

        segments: Dict[str, SegmentState] = {}

        for segment_id, members in buckets.items():
            size = len(members)

            segments[segment_id] = SegmentState(
                segment_id=segment_id,
                size=size,
                avg_spend=0.0,
                activity_rate=1.0,
                risk_score_avg=round(
                    sum(m.risk_score for m in members) / size, 2
                ),
                lifecycle_distribution=self._lifecycle_distribution(members),
            )

        return segments

    def _lifecycle_distribution(
        self, members: List[MemberState]
    ) -> Dict[str, float]:
        counts = defaultdict(int)

        for m in members:
            counts[m.lifecycle_stage] += 1

        total = len(members)
        return {k: round(v / total, 2) for k, v in counts.items()}
