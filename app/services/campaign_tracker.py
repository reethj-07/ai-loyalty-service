"""
Real-Time Campaign Tracking Service
Monitors campaign performance with live metrics
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

from app.core.supabase_client import get_supabase
from app.repositories.supabase_transactions_repo import transactions_repo
from app.monitoring.metrics import ACTIVE_CAMPAIGNS


class CampaignTracker:
    """
    Tracks campaign performance in real-time
    """

    def __init__(self):
        self.supabase = get_supabase()
        self.active_campaigns = {}
        self.metrics_cache = {}

    async def track_campaign_execution(
        self,
        campaign_id: str,
        campaign_data: Dict
    ) -> Dict:
        """
        Start tracking a campaign execution

        Args:
            campaign_id: Campaign identifier
            campaign_data: Initial campaign data

        Returns:
            dict: Tracking confirmation
        """
        self.active_campaigns[campaign_id] = {
            **campaign_data,
            "started_at": datetime.now().isoformat(),
            "status": "active",
            "metrics": {
                "messages_sent": 0,
                "messages_delivered": 0,
                "participants": 0,
                "engaged": 0,
                "transactions": 0,
                "revenue": 0.0,
                "points_distributed": 0,
            }
        }
        ACTIVE_CAMPAIGNS.set(len(self.active_campaigns))

        return {
            "campaign_id": campaign_id,
            "status": "tracking_started",
            "timestamp": datetime.now().isoformat()
        }

    async def get_live_metrics(self, campaign_id: str) -> Dict:
        """
        Get real-time metrics for an active campaign

        Args:
            campaign_id: Campaign identifier

        Returns:
            dict: Live campaign metrics
        """
        if campaign_id not in self.active_campaigns:
            # Try to load from database
            campaign = await self._load_campaign_from_db(campaign_id)
            if not campaign:
                return {
                    "error": "Campaign not found",
                    "campaign_id": campaign_id
                }
        else:
            campaign = self.active_campaigns[campaign_id]

        # Calculate real-time metrics
        metrics = await self._calculate_live_metrics(campaign_id, campaign)

        # Update cache
        self.metrics_cache[campaign_id] = {
            **metrics,
            "last_updated": datetime.now().isoformat()
        }

        return metrics

    async def _calculate_live_metrics(
        self,
        campaign_id: str,
        campaign: Dict
    ) -> Dict:
        """
        Calculate current metrics for a campaign

        Args:
            campaign_id: Campaign ID
            campaign: Campaign data

        Returns:
            dict: Calculated metrics
        """
        # Get campaign start time
        started_at = campaign.get('started_at')
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        else:
            started_at = datetime.now()

        # Target segment and count
        target_segment = campaign.get('segment', 'all')
        target_count = campaign.get('target_count', 0)

        # Estimated metrics (from campaign creation)
        estimated_participants = campaign.get('estimated_participants', 0)
        estimated_roi = campaign.get('estimated_roi', 0)
        total_cost = campaign.get('total_cost', 0)
        estimated_revenue = campaign.get('estimated_revenue', 0)

        # Calculate actual metrics
        actual_metrics = await self._get_actual_campaign_results(
            campaign_id,
            started_at,
            target_segment
        )

        # Calculate ROI
        actual_revenue = actual_metrics['revenue_generated']
        actual_cost = total_cost  # Cost is mostly fixed (messages + incentives)

        if actual_cost > 0:
            actual_roi = ((actual_revenue - actual_cost) / actual_cost) * 100
        else:
            actual_roi = 0

        # Calculate progress
        if target_count > 0:
            progress_percent = min((actual_metrics['participants'] / target_count) * 100, 100)
        else:
            progress_percent = 0

        # Status
        status = self._calculate_campaign_status(campaign, actual_metrics)

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.get('name', 'Untitled Campaign'),
            "status": status,
            "started_at": started_at.isoformat() if hasattr(started_at, 'isoformat') else started_at,
            "elapsed_time_hours": (datetime.now() - started_at).total_seconds() / 3600 if hasattr(started_at, 'total_seconds') else 0,

            # Target metrics
            "target_count": target_count,
            "target_segment": target_segment,
            "channel": campaign.get('channel', 'email'),

            # Participation metrics
            "messages_sent": actual_metrics.get('messages_sent', target_count),
            "messages_delivered": actual_metrics.get('messages_delivered', int(target_count * 0.95)),
            "participants": actual_metrics['participants'],
            "engagement_rate": round((actual_metrics['engaged'] / actual_metrics['participants'] * 100), 1) if actual_metrics['participants'] > 0 else 0,

            # Transaction metrics
            "transactions_generated": actual_metrics['transactions_count'],
            "revenue_generated": round(actual_metrics['revenue_generated'], 2),
            "avg_transaction_value": round(actual_metrics['avg_transaction_value'], 2),

            # Points/Rewards
            "points_distributed": actual_metrics['points_distributed'],
            "redemption_rate": round((actual_metrics['points_redeemed'] / actual_metrics['points_distributed'] * 100), 1) if actual_metrics['points_distributed'] > 0 else 0,

            # Cost & ROI
            "actual_cost": round(actual_cost, 2),
            "actual_roi": round(actual_roi, 1),
            "estimated_roi": estimated_roi,
            "roi_vs_estimate": "exceeding" if actual_roi > estimated_roi else "on-track" if actual_roi >= (estimated_roi * 0.8) else "below",

            # Estimated vs Actual
            "estimated_participants": estimated_participants,
            "estimated_revenue": estimated_revenue,
            "performance_vs_estimate": round((actual_revenue / estimated_revenue * 100), 1) if estimated_revenue > 0 else 0,

            # Progress
            "progress_percent": round(progress_percent, 1),
            "completion_estimate": self._estimate_completion(campaign, actual_metrics),

            # Recent activity
            "last_transaction": actual_metrics.get('last_transaction_time'),
            "transactions_last_hour": actual_metrics.get('recent_transactions', 0),
        }

    async def _get_actual_campaign_results(
        self,
        campaign_id: str,
        started_at: datetime,
        target_segment: str
    ) -> Dict:
        """
        Get actual results from database/transactions

        Args:
            campaign_id: Campaign ID
            started_at: Campaign start time
            target_segment: Target customer segment

        Returns:
            dict: Actual performance data
        """
        try:
            # Get transactions since campaign started
            # In a real system, transactions would be tagged with campaign_id
            # For now, we'll use time-based approximation

            recent_txns = await transactions_repo.get_transactions_since(started_at)

            # Calculate metrics
            participants = set()
            total_revenue = 0
            transaction_values = []

            for txn in recent_txns:
                member_id = txn.get('member_id')
                amount = txn.get('amount', 0)

                participants.add(member_id)
                total_revenue += amount
                transaction_values.append(amount)

            # Estimated engagement (30% of participants engage deeply)
            engaged_count = int(len(participants) * 0.3)

            # Points distributed (simplified - would come from actual points table)
            # Assume 10 points per transaction
            points_distributed = len(recent_txns) * 10

            # Last transaction time
            last_txn_time = None
            if recent_txns:
                last_txn = recent_txns[0]
                last_txn_time = last_txn.get('timestamp')

            # Transactions in last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)
            recent_count = sum(1 for txn in recent_txns
                             if datetime.fromisoformat(str(txn.get('timestamp')).replace('Z', '+00:00')) > one_hour_ago)

            return {
                "participants": len(participants),
                "engaged": engaged_count,
                "transactions_count": len(recent_txns),
                "revenue_generated": total_revenue,
                "avg_transaction_value": (total_revenue / len(transaction_values)) if transaction_values else 0,
                "points_distributed": points_distributed,
                "points_redeemed": int(points_distributed * 0.6),  # Assume 60% redemption
                "last_transaction_time": last_txn_time,
                "recent_transactions": recent_count,
            }

        except Exception as e:
            print(f"Error getting actual results: {e}")
            return {
                "participants": 0,
                "engaged": 0,
                "transactions_count": 0,
                "revenue_generated": 0.0,
                "avg_transaction_value": 0.0,
                "points_distributed": 0,
                "points_redeemed": 0,
            }

    def _calculate_campaign_status(self, campaign: Dict, actual_metrics: Dict) -> str:
        """
        Determine current campaign status

        Args:
            campaign: Campaign data
            actual_metrics: Actual performance

        Returns:
            str: Status (active, completed, paused, etc.)
        """
        # Check if manually paused/stopped
        if campaign.get('status') == 'paused':
            return 'paused'

        if campaign.get('status') == 'completed':
            return 'completed'

        # Check if target reached
        target_count = campaign.get('target_count', 0)
        if actual_metrics['participants'] >= target_count:
            return 'completed'

        # Check if end date passed
        end_date = campaign.get('end_date')
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            if datetime.now() > end_date:
                return 'completed'

        # Check if recently active
        last_txn = actual_metrics.get('last_transaction_time')
        if last_txn:
            if isinstance(last_txn, str):
                last_txn = datetime.fromisoformat(last_txn.replace('Z', '+00:00'))
            hours_since_activity = (datetime.now(last_txn.tzinfo) - last_txn).total_seconds() / 3600

            if hours_since_activity < 1:
                return 'active'
            elif hours_since_activity < 24:
                return 'running'
            else:
                return 'ending'

        return 'active'

    def _estimate_completion(self, campaign: Dict, actual_metrics: Dict) -> str:
        """
        Estimate when campaign will complete

        Args:
            campaign: Campaign data
            actual_metrics: Actual metrics

        Returns:
            str: Estimated completion time
        """
        target_count = campaign.get('target_count', 0)
        current_participants = actual_metrics['participants']

        if current_participants >= target_count:
            return "Completed"

        # Calculate rate
        started_at = campaign.get('started_at')
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))

        elapsed_hours = (datetime.now() - started_at).total_seconds() / 3600

        if elapsed_hours > 0 and current_participants > 0:
            rate_per_hour = current_participants / elapsed_hours
            remaining = target_count - current_participants
            hours_to_complete = remaining / rate_per_hour

            if hours_to_complete < 1:
                return f"{int(hours_to_complete * 60)} minutes"
            elif hours_to_complete < 24:
                return f"{int(hours_to_complete)} hours"
            else:
                return f"{int(hours_to_complete / 24)} days"

        return "Calculating..."

    async def _load_campaign_from_db(self, campaign_id: str) -> Optional[Dict]:
        """
        Load campaign data from database

        Args:
            campaign_id: Campaign ID

        Returns:
            dict: Campaign data or None
        """
        try:
            result = self.supabase.table("campaigns").select("*").eq("id", campaign_id).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]

        except Exception as e:
            print(f"Error loading campaign: {e}")

        return None

    async def update_campaign_status(
        self,
        campaign_id: str,
        status: str
    ) -> Dict:
        """
        Update campaign status (pause, resume, complete)

        Args:
            campaign_id: Campaign ID
            status: New status

        Returns:
            dict: Update confirmation
        """
        if campaign_id in self.active_campaigns:
            self.active_campaigns[campaign_id]['status'] = status
            self.active_campaigns[campaign_id]['updated_at'] = datetime.now().isoformat()

        # Update database
        try:
            self.supabase.table("campaigns").update({
                "status": status,
                "updated_at": datetime.now().isoformat()
            }).eq("id", campaign_id).execute()
        except Exception as e:
            print(f"Error updating campaign status: {e}")

        return {
            "campaign_id": campaign_id,
            "status": status,
            "updated_at": datetime.now().isoformat()
        }


# Singleton instance
_tracker = None


def get_campaign_tracker() -> CampaignTracker:
    """Get singleton instance of campaign tracker"""
    global _tracker
    if _tracker is None:
        _tracker = CampaignTracker()
    return _tracker
