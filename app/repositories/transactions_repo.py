from app.repositories.base import BaseRepository
from datetime import datetime, timedelta


class Transaction:
    def __init__(self, id, created_at, member_id, merchant, type, amount):
        self.id = id
        self.created_at = created_at
        self.member_id = member_id
        self.merchant = merchant
        self.type = type
        self.amount = amount


class TransactionsRepository(BaseRepository):
    def list_recent(self, limit: int = 20):
        # Temporary mock data with recent transactions
        now = datetime.now()
        return [
            Transaction("T001", (now - timedelta(minutes=5)).isoformat(), "M001", "Amazon", "purchase", 125.50),
            Transaction("T002", (now - timedelta(minutes=15)).isoformat(), "M002", "Starbucks", "purchase", 8.75),
            Transaction("T003", (now - timedelta(minutes=25)).isoformat(), "M003", "Walmart", "purchase", 234.00),
            Transaction("T004", (now - timedelta(minutes=35)).isoformat(), "M001", "Target", "purchase", 89.99),
            Transaction("T005", (now - timedelta(minutes=45)).isoformat(), "M004", "Best Buy", "purchase", 599.00),
            Transaction("T006", (now - timedelta(hours=1)).isoformat(), "M002", "Uber", "purchase", 25.50),
            Transaction("T007", (now - timedelta(hours=2)).isoformat(), "M005", "Netflix", "subscription", 15.99),
            Transaction("T008", (now - timedelta(hours=3)).isoformat(), "M003", "Apple Store", "purchase", 1299.00),
        ]


# ✅ REQUIRED singleton (THIS WAS MISSING)
transactions_repo = TransactionsRepository()
