"""
Supabase Transactions Repository
Replaces mock implementation with real database
"""
from typing import List, Optional, Dict
from datetime import datetime
from app.core.supabase_client import get_supabase
from app.repositories.base import BaseRepository


class Transaction:
    """Transaction data model matching Supabase schema"""
    def __init__(
        self,
        id: str,
        created_at: str,
        member_id: str,
        merchant: str,
        type: str,
        amount: float,
        external_id: Optional[str] = None,
        category: Optional[str] = None,
        channel: Optional[str] = None,
        currency: str = "USD",
    ):
        self.id = id
        self.created_at = created_at
        self.member_id = member_id
        self.merchant = merchant
        self.type = type
        self.amount = amount
        self.external_id = external_id
        self.category = category
        self.channel = channel
        self.currency = currency


class SupabaseTransactionsRepository(BaseRepository):
    """
    Transactions repository using Supabase with real-time support
    """

    def __init__(self):
        self.supabase = get_supabase()  # Read operations
        self.admin_supabase = get_supabase(use_service_key=True)  # Write operations

    def list_recent(self, limit: int = 20, tenant_id: Optional[str] = None) -> List[Transaction]:
        """
        Get recent transactions ordered by transaction_date descending
        """
        try:
            query = self.supabase.table("transactions").select("*")
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.order("transaction_date", desc=True).limit(limit).execute()

            transactions = []
            for data in response.data:
                transactions.append(
                    Transaction(
                        id=data["id"],
                        created_at=data.get("transaction_date") or data["created_at"],
                        member_id=data["member_id"],
                        merchant=data.get("merchant", "Unknown"),
                        type=data.get("type", "purchase"),
                        amount=float(data["amount"]),
                        external_id=data.get("external_id"),
                        category=data.get("category"),
                        channel=data.get("channel"),
                        currency=data.get("currency", "USD"),
                    )
                )
            return transactions
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []

    def get_transactions_by_member(
        self, member_id: str, limit: int = 50, tenant_id: Optional[str] = None
    ) -> List[Transaction]:
        """
        Get all transactions for a specific member
        """
        try:
            query = self.supabase.table("transactions").select("*").eq("member_id", member_id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.order("transaction_date", desc=True).limit(limit).execute()

            transactions = []
            for data in response.data:
                transactions.append(
                    Transaction(
                        id=data["id"],
                        created_at=data.get("transaction_date") or data["created_at"],
                        member_id=data["member_id"],
                        merchant=data.get("merchant", "Unknown"),
                        type=data.get("type", "purchase"),
                        amount=float(data["amount"]),
                        external_id=data.get("external_id"),
                        category=data.get("category"),
                        channel=data.get("channel"),
                        currency=data.get("currency", "USD"),
                    )
                )
            return transactions
        except Exception as e:
            print(f"Error fetching member transactions: {e}")
            return []

    def create_transaction(self, transaction_data: Dict, tenant_id: Optional[str] = None) -> Optional[Transaction]:
        """
        Create a new transaction
        """
        try:
            if tenant_id:
                transaction_data = dict(transaction_data)
                transaction_data["tenant_id"] = tenant_id
            # Use admin client to bypass RLS for inserts
            response = (
                self.admin_supabase.table("transactions").insert(transaction_data).execute()
            )

            data = response.data[0]
            return Transaction(
                id=data["id"],
                created_at=data.get("transaction_date") or data["created_at"],
                member_id=data["member_id"],
                merchant=data.get("merchant", "Unknown"),
                type=data.get("type", "purchase"),
                amount=float(data["amount"]),
                external_id=data.get("external_id"),
                category=data.get("category"),
                channel=data.get("channel"),
                currency=data.get("currency", "USD"),
            )
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None

    def get_total_spend_by_member(self, member_id: str) -> float:
        """
        Calculate total spend for a member
        """
        try:
            response = (
                self.supabase.table("transactions")
                .select("amount")
                .eq("member_id", member_id)
                .eq("type", "purchase")
                .execute()
            )

            total = sum(float(t["amount"]) for t in response.data)
            return total
        except Exception as e:
            print(f"Error calculating total spend: {e}")
            return 0.0

    async def get_all_transactions(self, limit: int = 10000, tenant_id: Optional[str] = None) -> List[Dict]:
        """
        Get all transactions as dict for ML processing (async)
        """
        try:
            query = self.supabase.table("transactions").select("*")
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.order("transaction_date", desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching all transactions: {e}")
            return []

    async def get_transactions_since(
        self, since: datetime, limit: int = 10000, tenant_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get transactions since a cutoff datetime (async)
        """
        try:
            query = self.supabase.table("transactions").select("*").gte(
                "transaction_date",
                since.isoformat(),
            )
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.order("transaction_date", desc=True).limit(limit).execute()
            transactions = []
            for data in response.data:
                item = dict(data)
                item["timestamp"] = (
                    item.get("transaction_date") or item.get("created_at")
                )
                if item.get("amount") is None:
                    item["amount"] = 0.0
                else:
                    item["amount"] = float(item["amount"])
                transactions.append(item)
            return transactions
        except Exception as e:
            print(f"Error fetching transactions since {since}: {e}")
            return []

    async def get_member_transactions(
        self, member_id: str, limit: int = 100, tenant_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get recent transactions for a specific member (async)
        """
        try:
            query = self.supabase.table("transactions").select("*").eq("member_id", member_id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.order("transaction_date", desc=True).limit(limit).execute()
            transactions = []
            for data in response.data:
                item = dict(data)
                item["timestamp"] = (
                    item.get("transaction_date") or item.get("created_at")
                )
                if item.get("amount") is None:
                    item["amount"] = 0.0
                else:
                    item["amount"] = float(item["amount"])
                transactions.append(item)
            return transactions
        except Exception as e:
            print(f"Error fetching member transactions: {e}")
            return []


# Singleton instance
transactions_repo = SupabaseTransactionsRepository()
