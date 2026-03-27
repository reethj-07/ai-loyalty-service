from typing import List
from app.schemas.segments import SegmentShift


class AutomationEngine:
    """
    Decides whether AI should auto-trigger campaign planning
    """

    def should_trigger(self, shifts: List[SegmentShift]) -> bool:
        for shift in shifts:
            if shift.segment_id in ["high_value_active", "at_risk"] and abs(shift.change_ratio) > 0.25:
                return True
        return False
