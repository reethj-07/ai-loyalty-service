import pytest


@pytest.mark.asyncio
async def test_proposal_contains_quality_fields(mock_llm):
    from app.services.ai_service import get_ai_service

    service = get_ai_service()
    result = await service.run_member_pipeline(member_id="quality-member", prompt="Generate proposal")
    proposal = result.get("proposal") or {}

    required = {"campaign_name", "target_segment", "discount_percent", "expected_roi", "reasoning"}
    assert required.issubset(set(proposal.keys()))
