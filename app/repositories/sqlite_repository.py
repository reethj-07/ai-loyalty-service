from app.repositories.base import BaseRepository
from datetime import datetime


class Member:
    def __init__(self, id, first_name, last_name, mobile, tier, points, status, created_at):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.mobile = mobile
        self.tier = tier
        self.points = points
        self.status = status
        self.created_at = created_at


class SQLiteRepository(BaseRepository):
    def list_members(self):
        """
        Temporary mock implementation with sample data.
        Replace with real DB logic later.
        """
        return [
            Member("M001", "John", "Doe", "+1-555-0101", "Gold", 15000, "active", "2024-01-15T10:30:00Z"),
            Member("M002", "Jane", "Smith", "+1-555-0102", "Platinum", 25000, "active", "2024-02-20T14:45:00Z"),
            Member("M003", "Bob", "Johnson", "+1-555-0103", "Silver", 8000, "active", "2024-03-10T09:15:00Z"),
            Member("M004", "Alice", "Williams", "+1-555-0104", "Gold", 12000, "active", "2024-01-25T16:20:00Z"),
            Member("M005", "Charlie", "Brown", "+1-555-0105", "Bronze", 3000, "inactive", "2023-12-05T11:00:00Z"),
        ]


# ✅ REQUIRED: module-level singleton
sqlite_repo = SQLiteRepository()
