from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class LoyaltyAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    member_context: dict
    behavioral_signals: list
    segment_data: dict
    campaign_proposals: list
    reasoning_trace: list
    tool_calls_made: list
    iteration_count: int
