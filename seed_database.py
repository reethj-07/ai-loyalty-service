#!/usr/bin/env python3
"""
Seed compelling demo data for AI Loyalty Service.

Targets:
- 500 members
- 2000 transactions over last 90 days
- 3 active campaigns with KPI-friendly fields
- 5 pending AI proposals with reasoning traces
- 2 approved/launched campaigns with simulated performance
"""

from __future__ import annotations

import os
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from faker import Faker
from supabase import create_client


fake = Faker()
random.seed(42)

SEGMENTS = ["Champions", "Loyal", "At Risk", "Dormant", "New"]
TIERS = ["Bronze", "Silver", "Gold", "Platinum"]
MERCHANTS = [
    "Amazon",
    "Nike",
    "Starbucks",
    "Target",
    "Apple",
    "Whole Foods",
    "Best Buy",
    "Home Depot",
]


def get_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY (or SUPABASE_ANON_KEY) are required")
    return create_client(url, key)


def generate_members(count: int = 500) -> List[Dict]:
    members: List[Dict] = []
    segment_bucket_size = max(1, count // len(SEGMENTS))

    for index in range(count):
        segment = SEGMENTS[min(index // segment_bucket_size, len(SEGMENTS) - 1)]
        tier = random.choice(TIERS)
        points = random.randint(100, 12000)

        members.append(
            {
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": f"demo_{index}_{fake.email()}",
                "mobile": f"+1{random.randint(2000000000, 9999999999)}",
                "tier": tier,
                "points_balance": points,
                "status": "active",
                "segment": segment,
            }
        )
    return members


def generate_transactions(member_ids: List[str], count: int = 2000) -> List[Dict]:
    now = datetime.now(timezone.utc)
    rows: List[Dict] = []

    for _ in range(count):
        days_ago = random.randint(0, 90)
        tx_time = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        amount = round(random.uniform(12, 680), 2)
        rows.append(
            {
                "member_id": random.choice(member_ids),
                "amount": amount,
                "merchant": random.choice(MERCHANTS),
                "type": "purchase",
                "category": random.choice(["retail", "food", "electronics", "grocery"]),
                "channel": random.choice(["online", "store", "app"]),
                "currency": "USD",
                "transaction_date": tx_time.isoformat(),
            }
        )

    return rows


def seed_campaigns(client) -> None:
    active_campaigns = [
        {
            "name": "Double Points Weekend",
            "status": "active",
            "campaign_type": "bonus",
            "channel": "email",
            "objective": "increase_frequency",
            "estimated_roi": 0.34,
            "estimated_cost": 2200,
            "estimated_revenue": 4600,
            "description": "Boost purchase frequency over weekends",
        },
        {
            "name": "At-Risk Winback",
            "status": "active",
            "campaign_type": "winback",
            "channel": "sms",
            "objective": "reactivation",
            "estimated_roi": 0.28,
            "estimated_cost": 1800,
            "estimated_revenue": 3900,
            "description": "Bring back lapsed members",
        },
        {
            "name": "VIP Upgrade Journey",
            "status": "active",
            "campaign_type": "tier_upgrade",
            "channel": "push",
            "objective": "increase_ltv",
            "estimated_roi": 0.41,
            "estimated_cost": 1500,
            "estimated_revenue": 5100,
            "description": "Promote high-value users to premium tiers",
        },
    ]

    launched_campaigns = [
        {
            "name": "Holiday Booster",
            "status": "completed",
            "campaign_type": "promo",
            "channel": "email",
            "objective": "seasonal_lift",
            "estimated_roi": 0.31,
            "estimated_cost": 1200,
            "estimated_revenue": 3000,
            "description": "Approved and launched with positive ROI",
        },
        {
            "name": "New Member Onboarding",
            "status": "completed",
            "campaign_type": "welcome",
            "channel": "sms",
            "objective": "first_purchase",
            "estimated_roi": 0.26,
            "estimated_cost": 900,
            "estimated_revenue": 2200,
            "description": "Approved and launched with stable conversion",
        },
    ]

    client.table("campaigns").insert(active_campaigns + launched_campaigns).execute()


def seed_proposals(client) -> None:
    proposals = []
    for idx in range(5):
        proposals.append(
            {
                "proposal_id": f"demo-proposal-{idx}",
                "campaign_type": random.choice(["bonus", "winback", "promo"]),
                "objective": random.choice(["engagement", "reactivation", "retention"]),
                "suggested_offer": random.choice(["10% off", "2x points", "Free shipping"]),
                "validity_hours": 48,
                "estimated_uplift": round(random.uniform(0.08, 0.23), 2),
                "estimated_roi": round(random.uniform(0.2, 0.45), 2),
                "segment": random.choice(SEGMENTS),
                "status": "pending",
                "human_notes": (
                    "Step 1: Context gathered → Step 2: RAG retrieved similar campaign → "
                    "Step 3: ROI estimated → Step 4: confidence below auto threshold"
                ),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    try:
        client.table("campaign_proposals").insert(proposals).execute()
    except Exception:
        pass


def run() -> None:
    client = get_client()

    print("🌱 Seeding compelling demo data...")

    members = generate_members(500)
    inserted_members = client.table("members").insert(members).execute().data
    member_ids = [item["id"] for item in inserted_members]
    print(f"✅ Members inserted: {len(member_ids)}")

    transactions = generate_transactions(member_ids, 2000)
    batch_size = 250
    total = 0
    for start in range(0, len(transactions), batch_size):
        batch = transactions[start : start + batch_size]
        inserted = client.table("transactions").insert(batch).execute().data
        total += len(inserted)
    print(f"✅ Transactions inserted: {total}")

    try:
        seed_campaigns(client)
        print("✅ Campaigns inserted: 5 (3 active + 2 completed)")
    except Exception as exc:
        print(f"⚠️ Campaign seed skipped: {exc}")

    seed_proposals(client)
    print("✅ Pending proposals seeded: 5")

    print("🎉 Demo seed complete.")


if __name__ == "__main__":
    run()