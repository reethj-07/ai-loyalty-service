from fastapi import APIRouter, HTTPException, Depends
from app.monitoring.repository import campaign_kpi_repo
from app.repositories.supabase_transactions_repo import transactions_repo
from app.repositories.supabase_campaigns_repo import campaigns_repo
from app.core.tenant import resolve_tenant_id
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import Optional

router = APIRouter(tags=["analytics"])


@router.get("/campaigns")
def list_campaigns():
    try:
        campaigns = campaign_kpi_repo.all_active()
        return [kpi.to_json() for kpi in campaigns]
    except Exception:
        return []


@router.get("/campaigns/{campaign_id}")
def get_campaign_analytics(campaign_id: str):
    """
    Get KPI analytics for a specific campaign.
    Called by CampaignLive.tsx every 5 seconds.
    """
    try:
        kpi = campaign_kpi_repo.get(campaign_id)
        if not kpi:
            # Return default values if campaign not found
            return {
                "campaign_id": campaign_id,
                "participants": 0,
                "transactions": 0,
                "revenue_generated": 0.0,
                "incentive_cost": 0.0,
                "actual_roi": 0.0,
                "status": "active"
            }

        return {
            "campaign_id": kpi.campaign_id,
            "participants": kpi.participants,
            "transactions": kpi.transactions,
            "revenue_generated": kpi.revenue_generated,
            "incentive_cost": kpi.incentive_cost,
            "actual_roi": kpi.actual_roi or 0.0,
            "status": kpi.status
        }
    except Exception as e:
        # Return default values on error to prevent frontend crash
        return {
            "campaign_id": campaign_id,
            "participants": 0,
            "transactions": 0,
            "revenue_generated": 0.0,
            "incentive_cost": 0.0,
            "actual_roi": 0.0,
            "status": "active"
        }


@router.get("/campaigns/{campaign_id}/timeseries")
async def get_campaign_timeseries(
    campaign_id: str,
    tenant_id: Optional[str] = Depends(resolve_tenant_id)
):
    """
    Get timeseries data for campaign analytics chart.
    Called by CampaignLive.tsx every 3 seconds.

    Returns array of {time, value} for Recharts LineChart showing
    real transaction counts over time for campaign participants.
    """
    try:
        # Get campaign details
        campaign = campaigns_repo.get_campaign_by_id(campaign_id, tenant_id=tenant_id)
        if not campaign:
            return []

        # Get campaign start time
        campaign_start = campaign.get('start_date')
        if not campaign_start:
            # If no start date, use created_at
            campaign_start = campaign.get('created_at')

        if isinstance(campaign_start, str):
            campaign_start = datetime.fromisoformat(campaign_start.replace('Z', '+00:00'))

        # Get all transactions since campaign started
        all_transactions = await transactions_repo.get_all_transactions(tenant_id=tenant_id)

        # Filter transactions that occurred after campaign start
        if campaign_start:
            campaign_transactions = [
                txn for txn in all_transactions
                if txn.get('transaction_date') or txn.get('created_at')
            ]

            # Further filter by date
            filtered_transactions = []
            for txn in campaign_transactions:
                txn_date = txn.get('transaction_date') or txn.get('created_at')
                if isinstance(txn_date, str):
                    txn_date = datetime.fromisoformat(txn_date.replace('Z', '+00:00'))

                if txn_date >= campaign_start:
                    filtered_transactions.append({
                        'timestamp': txn_date,
                        'amount': float(txn.get('amount', 0))
                    })
        else:
            filtered_transactions = []

        # Create time buckets (last 20 time points, 5-minute intervals)
        now = datetime.now(timezone.utc)
        time_buckets = defaultdict(int)

        # Initialize 20 time buckets (last 100 minutes)
        for i in range(20):
            time_point = now - timedelta(minutes=100-i*5)
            bucket_key = time_point.strftime("%H:%M")
            time_buckets[bucket_key] = 0

        # Count transactions in each bucket
        for txn in filtered_transactions:
            # Round transaction time to nearest 5-minute bucket
            txn_time = txn['timestamp']
            bucket_minutes = (txn_time.minute // 5) * 5
            bucket_time = txn_time.replace(minute=bucket_minutes, second=0, microsecond=0)
            bucket_key = bucket_time.strftime("%H:%M")

            if bucket_key in time_buckets:
                time_buckets[bucket_key] += 1

        # Convert to array format for Recharts
        data = [
            {"time": time_key, "value": count}
            for time_key, count in sorted(time_buckets.items())
        ]

        # Return last 20 data points
        return data[-20:]

    except Exception as e:
        print(f"Error fetching timeseries: {e}")
        # Return empty array on error
        return []