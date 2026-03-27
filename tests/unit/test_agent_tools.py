import pytest


@pytest.mark.asyncio
async def test_estimate_roi_tool_returns_expected_fields():
    from app.agents.tools import estimate_roi_tool

    result = await estimate_roi_tool.ainvoke(
        {"member_id": "member-1", "campaign_type": "personalized_offer", "discount_percent": 10}
    )

    assert "expected_roi" in result
    assert "estimated_uplift" in result
    assert result["expected_roi"] > 0
