"""
Supabase Campaigns Repository
Manages campaign CRUD operations
"""
from typing import List, Optional, Dict
from app.core.supabase_client import get_supabase
from app.repositories.base import BaseRepository


class Campaign:
    """Campaign data model matching Supabase schema"""
    def __init__(
        self,
        id: str,
        name: str,
        status: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        created_at: str = None,
        created_by: Optional[str] = None,
        campaign_type: Optional[str] = None,
        channel: Optional[str] = None,
        objective: Optional[str] = None,
        estimated_roi: Optional[float] = None,
        estimated_cost: Optional[float] = None,
        estimated_revenue: Optional[float] = None,
        description: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.created_at = created_at
        self.created_by = created_by
        self.campaign_type = campaign_type
        self.channel = channel
        self.objective = objective
        self.estimated_roi = estimated_roi
        self.estimated_cost = estimated_cost
        self.estimated_revenue = estimated_revenue
        self.description = description

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "campaign_type": self.campaign_type,
            "channel": self.channel,
            "objective": self.objective,
            "estimated_roi": self.estimated_roi,
            "estimated_cost": self.estimated_cost,
            "estimated_revenue": self.estimated_revenue,
            "description": self.description,
        }


class SupabaseCampaignsRepository(BaseRepository):
    """Campaigns repository using Supabase"""

    def __init__(self):
        self.supabase = get_supabase()  # Read operations
        self.admin_supabase = get_supabase(use_service_key=True)  # Write operations

    def list_campaigns(self, limit: int = 100, tenant_id: Optional[str] = None) -> List[Campaign]:
        """Get all campaigns"""
        try:
            query = self.supabase.table("campaigns").select("*")
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.order("created_at", desc=True).limit(limit).execute()

            campaigns = []
            for data in response.data:
                campaigns.append(
                    Campaign(
                        id=data["id"],
                        name=data["name"],
                        status=data.get("status", "draft"),
                        start_date=data.get("start_date"),
                        end_date=data.get("end_date"),
                        created_at=data.get("created_at"),
                        created_by=data.get("created_by"),
                        campaign_type=data.get("campaign_type"),
                        channel=data.get("channel"),
                        objective=data.get("objective"),
                        estimated_roi=float(data.get("estimated_roi", 0)) if data.get("estimated_roi") else None,
                        estimated_cost=float(data.get("estimated_cost", 0)) if data.get("estimated_cost") else None,
                        estimated_revenue=float(data.get("estimated_revenue", 0)) if data.get("estimated_revenue") else None,
                        description=data.get("description"),
                    )
                )
            return campaigns
        except Exception as e:
            print(f"Error fetching campaigns: {e}")
            return []

    def get_campaign_by_id(self, campaign_id: str, tenant_id: Optional[str] = None) -> Optional[Campaign]:
        """Get a single campaign by ID"""
        try:
            query = self.supabase.table("campaigns").select("*").eq("id", campaign_id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.single().execute()

            data = response.data
            return Campaign(
                id=data["id"],
                name=data["name"],
                status=data.get("status", "draft"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
                created_at=data.get("created_at"),
                created_by=data.get("created_by"),
                campaign_type=data.get("campaign_type"),
                channel=data.get("channel"),
                objective=data.get("objective"),
                estimated_roi=float(data.get("estimated_roi", 0)) if data.get("estimated_roi") else None,
                estimated_cost=float(data.get("estimated_cost", 0)) if data.get("estimated_cost") else None,
                estimated_revenue=float(data.get("estimated_revenue", 0)) if data.get("estimated_revenue") else None,
                description=data.get("description"),
            )
        except Exception as e:
            print(f"Error fetching campaign {campaign_id}: {e}")
            return None

    def create_campaign(self, campaign_data: Dict, tenant_id: Optional[str] = None) -> Optional[Campaign]:
        """Create a new campaign"""
        try:
            if tenant_id:
                campaign_data = dict(campaign_data)
                campaign_data["tenant_id"] = tenant_id
            # Use admin client to bypass RLS for inserts
            response = self.admin_supabase.table("campaigns").insert(campaign_data).execute()

            data = response.data[0]
            return Campaign(
                id=data["id"],
                name=data["name"],
                status=data.get("status", "draft"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
                created_at=data.get("created_at"),
                created_by=data.get("created_by"),
                campaign_type=data.get("campaign_type"),
                channel=data.get("channel"),
                objective=data.get("objective"),
                estimated_roi=float(data.get("estimated_roi", 0)) if data.get("estimated_roi") else None,
                estimated_cost=float(data.get("estimated_cost", 0)) if data.get("estimated_cost") else None,
                estimated_revenue=float(data.get("estimated_revenue", 0)) if data.get("estimated_revenue") else None,
                description=data.get("description"),
            )
        except Exception as e:
            print(f"Error creating campaign: {e}")
            raise

    def update_campaign(self, campaign_id: str, updates: Dict, tenant_id: Optional[str] = None) -> Optional[Campaign]:
        """Update an existing campaign"""
        try:
            query = self.supabase.table("campaigns").update(updates).eq("id", campaign_id)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            response = query.execute()

            if not response.data:
                return None

            data = response.data[0]
            return Campaign(
                id=data["id"],
                name=data["name"],
                status=data.get("status", "draft"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
                created_at=data.get("created_at"),
                created_by=data.get("created_by"),
                campaign_type=data.get("campaign_type"),
                channel=data.get("channel"),
                objective=data.get("objective"),
                estimated_roi=float(data.get("estimated_roi", 0)) if data.get("estimated_roi") else None,
                estimated_cost=float(data.get("estimated_cost", 0)) if data.get("estimated_cost") else None,
                estimated_revenue=float(data.get("estimated_revenue", 0)) if data.get("estimated_revenue") else None,
                description=data.get("description"),
            )
        except Exception as e:
            print(f"Error updating campaign: {e}")
            return None

    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign"""
        try:
            self.supabase.table("campaigns").delete().eq("id", campaign_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting campaign: {e}")
            return False


# Singleton instance
campaigns_repo = SupabaseCampaignsRepository()
