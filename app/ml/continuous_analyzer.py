"""
Continuous Behavior Analysis Engine
Monitors customer behavior patterns and detects changes in real-time
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

from app.core.supabase_client import get_supabase
from app.repositories.supabase_transactions_repo import transactions_repo
from app.repositories.supabase_members_repo import members_repo


class ContinuousBehaviorAnalyzer:
    """
    Continuously analyzes purchase history and detects behavioral changes
    """

    def __init__(self):
        self.supabase = get_supabase()
        self.behavior_cache = {}
        self.alerts = []

    async def analyze_recent_behavior(self, days: int = 30) -> Dict:
        """
        Analyze recent customer behavior patterns

        Args:
            days: Number of days to analyze

        Returns:
            dict: Behavior analysis results
        """
        print(f"🔍 Analyzing behavior patterns for last {days} days...")

        try:
            # Get recent transactions
            cutoff_date = datetime.now() - timedelta(days=days)
            transactions = await transactions_repo.get_transactions_since(cutoff_date)

            if not transactions:
                return {
                    "status": "no_data",
                    "message": "No recent transactions to analyze"
                }

            # Analyze patterns
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "period_days": days,
                "total_transactions": len(transactions),
                "behavioral_changes": await self._detect_behavioral_changes(transactions, days),
                "at_risk_customers": await self._identify_at_risk_customers(days),
                "declining_engagement": await self._detect_declining_engagement(days),
                "unusual_patterns": await self._find_unusual_patterns(transactions),
            }

            return analysis

        except Exception as e:
            print(f"Behavior analysis error: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def _detect_behavioral_changes(self, transactions: List[Dict], days: int) -> List[Dict]:
        """
        Detect significant changes in customer behavior

        Args:
            transactions: Recent transactions
            days: Analysis period

        Returns:
            list: Behavioral change alerts
        """
        changes = []

        # Group transactions by member
        member_transactions = defaultdict(list)
        for txn in transactions:
            member_transactions[txn.get('member_id')].append(txn)

        # Analyze each member
        for member_id, txns in member_transactions.items():
            # Get historical baseline
            baseline = await self._get_baseline_behavior(member_id, days)

            if not baseline:
                continue

            # Current behavior
            current_frequency = len(txns) / (days / 30)  # Transactions per month
            current_avg_value = sum(txn.get('amount', 0) for txn in txns) / len(txns)

            # Detect changes
            if baseline['frequency'] > 0:
                frequency_change = (current_frequency - baseline['frequency']) / baseline['frequency']

                # Significant decrease in frequency (> 30% drop)
                if frequency_change < -0.3:
                    changes.append({
                        "member_id": member_id,
                        "change_type": "decreased_frequency",
                        "severity": "high" if frequency_change < -0.5 else "medium",
                        "baseline_frequency": baseline['frequency'],
                        "current_frequency": current_frequency,
                        "change_percentage": round(frequency_change * 100, 1),
                        "detected_at": datetime.now().isoformat()
                    })

            # Detect value changes
            if baseline['avg_value'] > 0:
                value_change = (current_avg_value - baseline['avg_value']) / baseline['avg_value']

                # Significant decrease in spending (> 25% drop)
                if value_change < -0.25:
                    changes.append({
                        "member_id": member_id,
                        "change_type": "decreased_spending",
                        "severity": "medium",
                        "baseline_avg": baseline['avg_value'],
                        "current_avg": current_avg_value,
                        "change_percentage": round(value_change * 100, 1),
                        "detected_at": datetime.now().isoformat()
                    })

        return changes[:20]  # Top 20 changes

    async def _identify_at_risk_customers(self, days: int = 60) -> List[Dict]:
        """
        Identify customers at risk of churning

        Args:
            days: Lookback period

        Returns:
            list: At-risk customers
        """
        at_risk = []

        try:
            # Get all members
            members = await members_repo.get_all_members()

            for member in members[:100]:  # Analyze first 100
                member_id = member.get('id')

                # Get recent transactions
                recent_txns = await transactions_repo.get_member_transactions(member_id, limit=10)

                if not recent_txns:
                    # No transactions ever = new customer, not at risk
                    continue

                # Calculate days since last transaction
                last_txn_date = recent_txns[0].get('timestamp')
                if last_txn_date:
                    if isinstance(last_txn_date, str):
                        last_txn_date = datetime.fromisoformat(last_txn_date.replace('Z', '+00:00'))

                    days_since_last = (datetime.now(last_txn_date.tzinfo) - last_txn_date).days

                    # Historical frequency
                    if len(recent_txns) >= 3:
                        # Calculate average days between transactions
                        intervals = []
                        for i in range(len(recent_txns) - 1):
                            date1 = recent_txns[i].get('timestamp')
                            date2 = recent_txns[i + 1].get('timestamp')
                            if isinstance(date1, str):
                                date1 = datetime.fromisoformat(date1.replace('Z', '+00:00'))
                            if isinstance(date2, str):
                                date2 = datetime.fromisoformat(date2.replace('Z', '+00:00'))
                            intervals.append((date1 - date2).days)

                        avg_interval = sum(intervals) / len(intervals)

                        # At risk if current gap is 2x normal interval
                        if days_since_last > (avg_interval * 2) and days_since_last > 30:
                            at_risk.append({
                                "member_id": member_id,
                                "days_since_last_purchase": days_since_last,
                                "normal_interval": round(avg_interval, 1),
                                "risk_level": "high" if days_since_last > (avg_interval * 3) else "medium",
                                "last_purchase_date": last_txn_date.isoformat(),
                                "recommended_action": "winback_campaign"
                            })

        except Exception as e:
            print(f"At-risk identification error: {e}")

        return sorted(at_risk, key=lambda x: x['days_since_last_purchase'], reverse=True)[:15]

    async def _detect_declining_engagement(self, days: int = 90) -> List[Dict]:
        """
        Detect customers with declining engagement trends

        Args:
            days: Analysis period

        Returns:
            list: Declining engagement alerts
        """
        declining = []

        try:
            # Compare recent period to previous period
            recent_cutoff = datetime.now() - timedelta(days=days // 2)
            old_cutoff = datetime.now() - timedelta(days=days)

            # Get transactions for both periods
            recent_txns = await transactions_repo.get_transactions_since(recent_cutoff)
            all_txns = await transactions_repo.get_transactions_since(old_cutoff)

            # Group by member
            recent_by_member = defaultdict(int)
            total_by_member = defaultdict(int)

            for txn in recent_txns:
                recent_by_member[txn.get('member_id')] += 1

            for txn in all_txns:
                total_by_member[txn.get('member_id')] += 1

            # Find declining members
            for member_id, total_count in total_by_member.items():
                recent_count = recent_by_member.get(member_id, 0)
                old_count = total_count - recent_count

                if old_count > 0:
                    # Compare recent vs old activity
                    decline_ratio = (recent_count - old_count) / old_count

                    if decline_ratio < -0.4:  # 40% decline
                        declining.append({
                            "member_id": member_id,
                            "recent_transactions": recent_count,
                            "previous_transactions": old_count,
                            "decline_percentage": round(decline_ratio * 100, 1),
                            "trend": "declining",
                            "detected_at": datetime.now().isoformat()
                        })

        except Exception as e:
            print(f"Declining engagement detection error: {e}")

        return declining[:15]

    async def _find_unusual_patterns(self, transactions: List[Dict]) -> List[Dict]:
        """
        Find unusual purchase patterns (e.g., missing usual products)

        Args:
            transactions: Recent transactions

        Returns:
            list: Unusual patterns detected
        """
        unusual = []

        try:
            # Group by member and merchant
            member_merchants = defaultdict(lambda: defaultdict(int))

            for txn in transactions:
                member_id = txn.get('member_id')
                merchant = txn.get('merchant', 'Unknown')
                member_merchants[member_id][merchant] += 1

            # Detect missing usual merchants
            # (This is simplified - in production, compare to historical patterns)
            for member_id, merchants in list(member_merchants.items())[:10]:
                # If a member usually shops at multiple merchants but suddenly only one
                if len(merchants) == 1 and sum(merchants.values()) > 3:
                    unusual.append({
                        "member_id": member_id,
                        "pattern_type": "merchant_concentration",
                        "description": f"Customer only shopping at {list(merchants.keys())[0]}",
                        "detected_at": datetime.now().isoformat()
                    })

        except Exception as e:
            print(f"Unusual pattern detection error: {e}")

        return unusual[:10]

    async def _get_baseline_behavior(self, member_id: str, exclude_days: int) -> Optional[Dict]:
        """
        Get baseline behavior for a member (historical average)

        Args:
            member_id: Member ID
            exclude_days: Days to exclude from baseline

        Returns:
            dict: Baseline metrics or None
        """
        try:
            # Get transactions older than exclude period
            cutoff = datetime.now() - timedelta(days=exclude_days)

            # For now, use a simplified approach
            # In production, query historical transactions older than cutoff
            all_txns = await transactions_repo.get_member_transactions(member_id, limit=100)

            if len(all_txns) < 5:  # Need minimum history
                return None

            # Calculate baseline from older transactions
            old_txns = [txn for txn in all_txns[5:] if txn]  # Skip recent 5

            if not old_txns:
                return None

            total_amount = sum(txn.get('amount', 0) for txn in old_txns)
            avg_value = total_amount / len(old_txns)

            # Estimate frequency (transactions per month)
            # This is simplified - should use actual date ranges
            frequency = len(old_txns) / 3  # Assume 3-month history

            return {
                "frequency": frequency,
                "avg_value": avg_value,
                "transaction_count": len(old_txns)
            }

        except Exception as e:
            print(f"Baseline calculation error: {e}")
            return None

    async def generate_behavior_alerts(self) -> List[Dict]:
        """
        Generate actionable alerts based on behavior analysis

        Returns:
            list: Alerts for marketing team
        """
        analysis = await self.analyze_recent_behavior(days=30)

        alerts = []

        # Generate alerts from behavioral changes
        for change in analysis.get('behavioral_changes', []):
            if change['severity'] == 'high':
                alerts.append({
                    "type": "behavioral_change",
                    "priority": "high",
                    "member_id": change['member_id'],
                    "message": f"Customer showing {change['change_type']}: {change['change_percentage']}% change",
                    "recommended_action": "immediate_engagement_campaign",
                    "timestamp": change['detected_at']
                })

        # Generate alerts from at-risk customers
        for customer in analysis.get('at_risk_customers', [])[:5]:
            alerts.append({
                "type": "churn_risk",
                "priority": customer['risk_level'],
                "member_id": customer['member_id'],
                "message": f"Customer inactive for {customer['days_since_last_purchase']} days",
                "recommended_action": customer['recommended_action'],
                "timestamp": datetime.now().isoformat()
            })

        return alerts


# Singleton instance
_analyzer = None


def get_behavior_analyzer() -> ContinuousBehaviorAnalyzer:
    """Get singleton instance of behavior analyzer"""
    global _analyzer
    if _analyzer is None:
        _analyzer = ContinuousBehaviorAnalyzer()
    return _analyzer
