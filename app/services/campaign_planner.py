import uuid


class CampaignPlannerService:
    """
    Handles campaign launch lifecycle
    """

    def launch(self, payload: dict) -> str:
        # In real system this would persist to DB / Redis
        campaign_id = str(uuid.uuid4())
        return campaign_id


# ✅ FUNCTION EXPORT REQUIRED BY API LAYER
def launch_campaign(payload: dict) -> str:
    """
    API-safe entry point.
    Keeps router decoupled from service implementation.
    """
    service = CampaignPlannerService()
    return service.launch(payload)
