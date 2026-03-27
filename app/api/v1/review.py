from app.services.campaign_draft_builder import CampaignDraftBuilder
from app.api.v1.campaigns import create_campaign_draft


@router.post("/{proposal_id}/approve")
def approve_proposal(proposal_id: str, notes: str = ""):
    proposal = repo.get(proposal_id)
    proposal.status = "approved"
    proposal.human_notes = notes
    repo.save(proposal)

    # 🔥 AUTO-CREATE CAMPAIGN DRAFT
    builder = CampaignDraftBuilder()
    draft = builder.build(proposal)
    draft_response = create_campaign_draft(draft)

    return {
        "status": "approved",
        "proposal_id": proposal_id,
        "campaign_draft": draft_response
    }
