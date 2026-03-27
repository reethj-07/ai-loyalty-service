from uuid import uuid4
from app.schemas.campaign_draft import CampaignDraft
from app.schemas.campaign_proposal import CampaignProposal


class CampaignDraftBuilder:

    def build(self, proposal: CampaignProposal) -> CampaignDraft:
        return CampaignDraft(
            draft_id=str(uuid4()),
            proposal_id=proposal.proposal_id,

            campaign_type=proposal.campaign_type,
            objective=proposal.objective,
            offer=proposal.suggested_offer,
            segment=proposal.segment,

            duration_hours=proposal.validity_hours,
            estimated_roi=proposal.estimated_roi,
            estimated_uplift=proposal.estimated_uplift,

            prefilled_fields={
                "campaign_name": f"AI_{proposal.segment}_{proposal.campaign_type}",
                "message": proposal.suggested_offer,
                "target_segment": proposal.segment,
                "duration_hours": str(proposal.validity_hours),
            }
        )
