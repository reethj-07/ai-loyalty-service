from typing import Dict, List
from app.schemas.segments import SegmentState, SegmentShift


class SegmentShiftDetector:
    """
    Detects significant changes in segments.
    """

    def detect(
        self,
        previous: Dict[str, SegmentState],
        current: Dict[str, SegmentState],
        threshold: float = 0.2,
    ) -> List[SegmentShift]:

        shifts = []

        for segment_id, curr in current.items():
            prev = previous.get(segment_id)
            if not prev:
                continue

            delta = (curr.size - prev.size) / max(prev.size, 1)

            if abs(delta) >= threshold:
                shifts.append(
                    SegmentShift(
                        segment_id=segment_id,
                        previous_size=prev.size,
                        current_size=curr.size,
                        change_ratio=round(delta, 2),
                        reason="segment_population_shift",
                    )
                )

        return shifts
