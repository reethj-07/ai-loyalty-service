import json
from typing import Any, AsyncGenerator, Dict, Optional

from app.agents.graph import LoyaltyAgentGraphService
from app.agents.state import LoyaltyAgentState
from app.repositories.supabase_members_repo import members_repo
from app.repositories.supabase_transactions_repo import transactions_repo


class AIService:
    def __init__(self):
        self.graph_service = LoyaltyAgentGraphService()

    async def _build_initial_state(self, member_id: str, prompt: Optional[str] = None) -> LoyaltyAgentState:
        member = members_repo.get_member_by_id(member_id)
        member_payload: Dict[str, Any] = {}
        if member:
            member_payload = {
                "member_id": member.id,
                "first_name": member.first_name,
                "last_name": member.last_name,
                "tier": member.tier,
                "points": member.points,
                "email": member.email,
            }
        else:
            member_payload = {"member_id": member_id}

        recent_txns = await transactions_repo.get_member_transactions(member_id=member_id, limit=20)

        return LoyaltyAgentState(
            messages=[{"role": "user", "content": prompt or "Generate campaign proposal"}],
            member_context={
                **member_payload,
                "prompt": prompt or "Generate campaign proposal",
                "recent_transactions": recent_txns,
            },
            behavioral_signals=[],
            segment_data={},
            campaign_proposals=[],
            reasoning_trace=[],
            tool_calls_made=[],
            iteration_count=0,
        )

    async def run_member_pipeline(self, member_id: str, prompt: Optional[str] = None) -> dict:
        state = await self._build_initial_state(member_id=member_id, prompt=prompt)
        result = await self.graph_service.ainvoke(state)

        proposals = result.get("campaign_proposals", [])
        latest_proposal = proposals[-1] if proposals else None

        return {
            "member_id": member_id,
            "proposal": latest_proposal,
            "reasoning_trace": result.get("reasoning_trace", []),
            "tool_calls_made": result.get("tool_calls_made", []),
            "iteration_count": result.get("iteration_count", 0),
            "state": result,
        }

    async def stream_member_pipeline(
        self,
        member_id: str,
        prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        state = await self._build_initial_state(member_id=member_id, prompt=prompt)

        async for update in self.graph_service.astream_node_updates(state):
            event_name = update.get("event", "node_complete")
            payload = {
                "node": update.get("node"),
                "output": update.get("output"),
            }
            yield f"event: {event_name}\ndata: {json.dumps(payload, default=str)}\n\n"

        final_state = await self.graph_service.ainvoke(state)
        proposals = final_state.get("campaign_proposals", [])
        latest_proposal = proposals[-1] if proposals else {}
        confidence = latest_proposal.get("confidence", final_state.get("member_context", {}).get("confidence", 0.0))

        yield (
            "event: proposal_ready\n"
            f"data: {json.dumps({'proposal': latest_proposal, 'confidence': confidence}, default=str)}\n\n"
        )


_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
