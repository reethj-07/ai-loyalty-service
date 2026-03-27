from typing import Dict, List


class MembersRepository:

    async def get_member_profile(self, member_id: str) -> Dict:
        return {}

    async def get_active_members(self) -> List[str]:
        return []
