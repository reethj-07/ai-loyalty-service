from typing import Dict, List
from app.schemas.campaign_proposal import CampaignProposal


class CampaignProposalRepository:
    """
    Stores AI-generated campaign proposals
    """

    def __init__(self):
        self._store: Dict[str, CampaignProposal] = {}

    def save(self, proposal: CampaignProposal):
        self._store[proposal.proposal_id] = proposal

    def get(self, proposal_id: str) -> CampaignProposal | None:
        return self._store.get(proposal_id)

    def list_pending(self):
        return [
            p for p in self._store.values()
            if p.status == "pending"
        ]

    def list_all(self) -> List[CampaignProposal]:
        return list(self._store.values())

    def list_by_status(self, status: str) -> List[CampaignProposal]:
        return [
            p for p in self._store.values()
            if p.status == status
        ]


campaign_proposal_repo = CampaignProposalRepository()
