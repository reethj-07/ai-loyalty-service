from app.repositories.campaign_proposal_repository import CampaignProposalRepository
from app.schemas.campaign_proposal import CampaignProposal


class HumanReviewService:

    def __init__(self, repo: CampaignProposalRepository):
        self.repo = repo

    def approve(self, proposal_id: str, notes: str | None = None):
        proposal = self.repo.get(proposal_id)
        proposal.status = "approved"
        proposal.human_notes = notes
        self.repo.save(proposal)
        return proposal

    def reject(self, proposal_id: str, reason: str):
        proposal = self.repo.get(proposal_id)
        proposal.status = "rejected"
        proposal.human_notes = reason
        self.repo.save(proposal)
        return proposal

    def modify(
        self,
        proposal_id: str,
        updates: dict,
        notes: str | None = None
    ):
        proposal = self.repo.get(proposal_id)

        for field, value in updates.items():
            if hasattr(proposal, field):
                setattr(proposal, field, value)

        proposal.status = "modified"
        proposal.human_notes = notes
        self.repo.save(proposal)
        return proposal
