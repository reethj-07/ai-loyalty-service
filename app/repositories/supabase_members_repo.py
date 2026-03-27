"""
Supabase Members Repository
Replaces SQLite mock implementation
"""
from typing import List, Optional, Dict
from app.core.supabase_client import get_supabase
from app.repositories.base import BaseRepository


class Member:
    """Member data model matching Supabase schema"""
    def __init__(
        self,
        id: str,
        first_name: str,
        last_name: str,
        mobile: str,
        tier: str,
        points: int,
        status: str,
        created_at: str,
        email: Optional[str] = None,
        external_id: Optional[str] = None,
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.mobile = mobile
        self.tier = tier
        self.points = points
        self.status = status
        self.created_at = created_at
        self.email = email
        self.external_id = external_id


class SupabaseMembersRepository(BaseRepository):
    """
    Members repository using Supabase
    """

    def __init__(self):
        self.supabase = get_supabase()  # Read operations
        self.admin_supabase = get_supabase(use_service_key=True)  # Write operations

    def list_members(
        self,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> tuple[List[Member], int]:
        """
        Get members from Supabase with pagination and optional search.
        Returns a tuple of (members, total_count).
        """
        try:
            query = self.supabase.table("members").select("*", count="exact")
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            if search:
                pattern = f"%{search}%"
                query = query.or_(
                    f"first_name.ilike.{pattern},"
                    f"last_name.ilike.{pattern},"
                    f"email.ilike.{pattern},"
                    f"mobile.ilike.{pattern}"
                )
            response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

            members = []
            for data in response.data:
                members.append(
                    Member(
                        id=data["id"],
                        first_name=data["first_name"],
                        last_name=data["last_name"],
                        mobile=data.get("mobile", ""),
                        tier=data.get("tier", "Bronze"),
                        points=data.get("points_balance", 0),
                        status=data.get("status", "active"),
                        created_at=data["created_at"],
                        email=data.get("email"),
                        external_id=data.get("external_id"),
                    )
                )
            total = response.count if response.count is not None else len(response.data)
            return members, total
        except Exception as e:
            print(f"Error fetching members: {e}")
            return [], 0

    async def get_all_members(self, limit: int = 1000, tenant_id: Optional[str] = None) -> List[Dict]:
        """
        Get all members as dict for ML processing (async)
        """
        try:
            query = self.supabase.table("members").select("*")
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching all members: {e}")
            return []

    def get_member_by_id(self, member_id: str, tenant_id: Optional[str] = None) -> Optional[Member]:
        """
        Get a single member by ID
        """
        try:
            query = self.supabase.table("members").select("*").eq("id", member_id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.single().execute()

            data = response.data
            return Member(
                id=data["id"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                mobile=data.get("mobile", ""),
                tier=data.get("tier", "Bronze"),
                points=data.get("points_balance", 0),
                status=data.get("status", "active"),
                created_at=data["created_at"],
                email=data.get("email"),
                external_id=data.get("external_id"),
            )
        except Exception as e:
            print(f"Error fetching member {member_id}: {e}")
            return None

    def get_member_by_email(self, email: str, tenant_id: Optional[str] = None) -> Optional[Member]:
        """
        Get a single member by email
        """
        try:
            query = self.supabase.table("members").select("*").eq("email", email)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.single().execute()

            data = response.data
            return Member(
                id=data["id"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                mobile=data.get("mobile", ""),
                tier=data.get("tier", "Bronze"),
                points=data.get("points_balance", 0),
                status=data.get("status", "active"),
                created_at=data["created_at"],
                email=data.get("email"),
                external_id=data.get("external_id"),
            )
        except Exception as e:
            print(f"Error fetching member by email {email}: {e}")
            return None

    def create_member(self, member_data: Dict, tenant_id: Optional[str] = None) -> Optional[Member]:
        """
        Create a new member
        """
        try:
            if tenant_id:
                member_data = dict(member_data)
                member_data["tenant_id"] = tenant_id
            # Use admin client to bypass RLS for inserts
            response = self.admin_supabase.table("members").insert(member_data).execute()

            data = response.data[0]
            return Member(
                id=data["id"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                mobile=data.get("mobile", ""),
                tier=data.get("tier", "Bronze"),
                points=data.get("points_balance", 0),
                status=data.get("status", "active"),
                created_at=data["created_at"],
                email=data.get("email"),
                external_id=data.get("external_id"),
            )
        except Exception as e:
            print(f"Error creating member: {e}")
            return None

    def update_member_points(self, member_id: str, points: int, tenant_id: Optional[str] = None) -> bool:
        """
        Update member points balance
        """
        try:
            query = self.supabase.table("members").update(
                {"points_balance": points}
            ).eq("id", member_id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            query.execute()
            return True
        except Exception as e:
            print(f"Error updating member points: {e}")
            return False

    def update_member(self, member_id: str, update_data: Dict, tenant_id: Optional[str] = None):
        """
        Update member information
        """
        try:
            query = self.admin_supabase.table("members").update(update_data).eq("id", member_id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)

            response = query.execute()

            if response.data and len(response.data) > 0:
                return self._map_member(response.data[0])
            return None
        except Exception as e:
            print(f"Error updating member: {e}")
            return None

    def delete_member(self, member_id: str, tenant_id: Optional[str] = None) -> bool:
        """
        Delete a member from the database
        """
        try:
            query = self.admin_supabase.table("members").delete().eq("id", member_id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)

            response = query.execute()
            return True
        except Exception as e:
            print(f"Error deleting member: {e}")
            return False


# Singleton instance
members_repo = SupabaseMembersRepository()
