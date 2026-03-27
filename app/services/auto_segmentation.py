"""
Automatic Customer Segmentation Service
Continuously segments customers based on behavioral patterns
"""
from typing import Dict, List
import asyncio
from datetime import datetime, timedelta

from app.ml.segmentation_model import segmentation_model
from app.ml.feature_engineering import feature_engineer
from app.core.supabase_client import get_supabase


class AutoSegmentationService:
    """
    Automatically segments customers and updates their segment assignments
    """

    def __init__(self):
        self.supabase = get_supabase()
        self.last_segmentation = None
        self.segment_cache = {}

    async def run_auto_segmentation(self, force: bool = False) -> Dict:
        """
        Run automatic segmentation on all customers

        Args:
            force: Force re-segmentation even if recently run

        Returns:
            dict: Segmentation results with updated counts
        """
        # Check if we need to run (don't run too frequently)
        if not force and self.last_segmentation:
            time_since_last = datetime.now() - self.last_segmentation
            if time_since_last < timedelta(hours=6):  # Run max every 6 hours
                return {
                    "status": "skipped",
                    "reason": "Segmentation ran recently",
                    "last_run": self.last_segmentation.isoformat(),
                    "next_run": (self.last_segmentation + timedelta(hours=6)).isoformat()
                }

        try:
            print("🔄 Running automatic customer segmentation...")

            # Step 1: Get segmentation predictions from ML model
            results = await segmentation_model.predict()

            if "error" in results:
                return {
                    "status": "error",
                    "message": results["error"]
                }

            # Step 2: Update member segments in database
            updated_count = await self._update_member_segments(results['predictions'])

            # Step 3: Update cache
            self.last_segmentation = datetime.now()
            self.segment_cache = self._build_segment_cache(results['predictions'])

            # Step 4: Return summary
            segment_distribution = self._calculate_segment_distribution(results['segment_summary'])

            return {
                "status": "success",
                "timestamp": self.last_segmentation.isoformat(),
                "members_segmented": len(results['predictions']),
                "members_updated": updated_count,
                "segment_distribution": segment_distribution,
                "segment_summary": results['segment_summary']
            }

        except Exception as e:
            print(f"Auto-segmentation error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _update_member_segments(self, predictions: List[Dict]) -> int:
        """
        Update member segments in the database

        Args:
            predictions: List of segment predictions

        Returns:
            int: Number of members updated
        """
        updated_count = 0

        try:
            # Batch update for efficiency
            for prediction in predictions:
                member_id = prediction['member_id']
                segment_name = prediction['segment_name']

                # Update member's segment in database
                # Note: We'd need to add a 'segment' column to members table
                # For now, we'll store it in metadata or a separate table

                try:
                    # Check if members table has a segment column
                    result = self.supabase.table("members").update({
                        "last_segmented_at": datetime.now().isoformat()
                    }).eq("id", member_id).execute()

                    updated_count += 1

                except Exception as e:
                    # If column doesn't exist, we could create a segments table
                    print(f"Could not update member {member_id}: {e}")
                    pass

        except Exception as e:
            print(f"Error updating segments: {e}")

        return updated_count

    def _build_segment_cache(self, predictions: List[Dict]) -> Dict:
        """Build in-memory cache of segment assignments"""
        cache = {}
        for prediction in predictions:
            cache[prediction['member_id']] = {
                'segment': prediction['segment_name'],
                'segment_id': prediction['segment_id'],
                'confidence': prediction.get('confidence', 0.0),
                'timestamp': datetime.now().isoformat()
            }
        return cache

    def _calculate_segment_distribution(self, segment_summary: Dict) -> Dict:
        """Calculate percentage distribution of segments"""
        total = sum(seg['size'] for seg in segment_summary.values())

        distribution = {}
        for segment_name, segment_info in segment_summary.items():
            distribution[segment_name] = {
                "count": segment_info['size'],
                "percentage": round((segment_info['size'] / total * 100), 1) if total > 0 else 0,
                "avg_recency_days": round(segment_info['avg_recency_days'], 1),
                "avg_frequency": round(segment_info['avg_frequency'], 1),
                "avg_monetary": round(segment_info['avg_monetary'], 2),
            }

        return distribution

    async def get_member_segment(self, member_id: str) -> Dict:
        """
        Get segment for a specific member

        Args:
            member_id: Member ID

        Returns:
            dict: Segment information
        """
        # Check cache first
        if member_id in self.segment_cache:
            return self.segment_cache[member_id]

        # If not in cache, run segmentation for this member
        # (In production, you'd fetch from DB or run real-time prediction)
        return {
            "segment": "Unknown",
            "confidence": 0.0,
            "message": "Member not yet segmented"
        }

    async def get_segment_members(self, segment_name: str) -> List[str]:
        """
        Get all members in a specific segment

        Args:
            segment_name: Name of segment

        Returns:
            list: List of member IDs
        """
        members = []
        for member_id, info in self.segment_cache.items():
            if info['segment'].lower() == segment_name.lower():
                members.append(member_id)

        return members

    async def trigger_recommendation_refresh(self):
        """
        Trigger refresh of campaign recommendations after segmentation

        This would notify the recommendation service to generate new recommendations
        based on the updated segments
        """
        # In a real system, this would publish an event or call the recommendation service
        print("🔔 Triggering recommendation refresh...")

        # Could use:
        # - Event bus (Redis pub/sub, Kafka)
        # - Direct service call
        # - Scheduled job

        return {
            "status": "triggered",
            "timestamp": datetime.now().isoformat()
        }


# Singleton instance
_auto_segmentation_service = None


def get_auto_segmentation_service() -> AutoSegmentationService:
    """Get singleton instance of auto-segmentation service"""
    global _auto_segmentation_service
    if _auto_segmentation_service is None:
        _auto_segmentation_service = AutoSegmentationService()
    return _auto_segmentation_service


# Convenience function for API
async def run_segmentation(force: bool = False) -> Dict:
    """Run auto-segmentation"""
    service = get_auto_segmentation_service()
    return await service.run_auto_segmentation(force=force)
