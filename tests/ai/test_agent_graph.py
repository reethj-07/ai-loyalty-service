import pytest


class _FakeTool:
    def __init__(self, payload):
        self.payload = payload

    async def ainvoke(self, _args):
        return self.payload


class _FakeLLM:
    async def ainvoke(self, _messages):
        from langchain_core.messages import AIMessage

        return AIMessage(
            content='{"summary":"Detected surge","patterns":["high value"],"recommended_segment":"Champions"}'
        )


@pytest.mark.asyncio
async def test_graph_produces_proposal_with_all_required_fields(monkeypatch, mock_llm):
    """Agent output must have: campaign_name, target_segment, discount_percent, expected_roi, reasoning"""
    from app.agents import graph as graph_module

    monkeypatch.setattr(graph_module, "get_member_segments_tool", _FakeTool({"segment": {"segment": "Champions"}}))
    monkeypatch.setattr(graph_module, "get_behavioral_alerts_tool", _FakeTool([{"type": "high_value_transaction"}]))
    monkeypatch.setattr(graph_module, "retrieve_similar_campaigns_tool", _FakeTool([]))
    monkeypatch.setattr(graph_module, "get_llm", lambda streaming=False: _FakeLLM())

    service = graph_module.LoyaltyAgentGraphService()
    state = {
        "messages": [],
        "member_context": {"member_id": "member-1"},
        "behavioral_signals": [],
        "segment_data": {},
        "campaign_proposals": [],
        "reasoning_trace": [],
        "tool_calls_made": [],
        "iteration_count": 0,
    }

    result = await service.ainvoke(state)
    proposal = result["campaign_proposals"][-1]

    assert "campaign_name" in proposal
    assert "target_segment" in proposal
    assert "discount_percent" in proposal
    assert "expected_roi" in proposal
    assert "reasoning" in proposal
