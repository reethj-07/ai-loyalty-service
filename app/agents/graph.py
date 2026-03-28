import json
import os
import time
from datetime import datetime
from typing import Any, AsyncGenerator, Dict

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agents.llm_factory import get_llm
from app.agents.state import LoyaltyAgentState
from app.agents.tools import (
    estimate_roi_tool,
    generate_campaign_proposal_tool,
    get_behavioral_alerts_tool,
    get_member_segments_tool,
    retrieve_similar_campaigns_tool,
)
from app.monitoring.llm_observability import record_llm_call
from app.monitoring.metrics import LLM_LATENCY_SECONDS, LLM_TOKENS_USED


def _safe_json(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return {"text": value}
    return {"value": str(value)}


def _record_node_observability(
    node: str,
    model: str,
    provider: str,
    prompt_text: str,
    output_text: str,
    latency_seconds: float,
):
    tokens_in = max(1, len(prompt_text.split())) if prompt_text else 0
    tokens_out = max(1, len(output_text.split())) if output_text else 0

    LLM_LATENCY_SECONDS.labels(provider=provider, model=model).observe(latency_seconds)
    LLM_TOKENS_USED.labels(provider=provider, type="input").inc(tokens_in)
    LLM_TOKENS_USED.labels(provider=provider, type="output").inc(tokens_out)

    record_llm_call(
        {
            "timestamp": datetime.now().isoformat(),
            "node": node,
            "provider": provider,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "latency_seconds": round(latency_seconds, 4),
        }
    )


async def context_gatherer(state: LoyaltyAgentState) -> LoyaltyAgentState:
    started_at = time.perf_counter()
    member_id = str(state.get("member_context", {}).get("member_id", ""))

    segment_data = await get_member_segments_tool.ainvoke({"member_id": member_id})
    behavioral_alerts = await get_behavioral_alerts_tool.ainvoke({"member_id": member_id})

    trace = list(state.get("reasoning_trace", []))
    trace.append(
        {
            "node": "context_gatherer",
            "timestamp": datetime.now().isoformat(),
            "message": "Retrieved member segmentation context and behavioral alerts",
            "alerts_count": len(behavioral_alerts or []),
        }
    )

    tool_calls = list(state.get("tool_calls_made", []))
    tool_calls.extend([
        {"tool": "get_member_segments_tool", "member_id": member_id},
        {"tool": "get_behavioral_alerts_tool", "member_id": member_id},
    ])

    result = {
        **state,
        "segment_data": segment_data,
        "behavioral_signals": behavioral_alerts,
        "reasoning_trace": trace,
        "tool_calls_made": tool_calls,
        "iteration_count": int(state.get("iteration_count", 0)) + 1,
    }
    _record_node_observability(
        node="context_gatherer",
        model="tools",
        provider="internal",
        prompt_text=member_id,
        output_text=json.dumps(result.get("segment_data", {}), default=str),
        latency_seconds=time.perf_counter() - started_at,
    )
    return result


async def reasoning_node(state: LoyaltyAgentState) -> LoyaltyAgentState:
    started_at = time.perf_counter()
    llm = get_llm(streaming=False)
    provider = os.getenv("LLM_PROVIDER", "groq")
    model = "llama-3.3-70b-versatile" if provider == "groq" else "claude-3-5-haiku-latest"

    rag_query = (
        f"Segment context: {json.dumps(state.get('segment_data', {}), default=str)} "
        f"Behavioral signals: {json.dumps(state.get('behavioral_signals', []), default=str)}"
    )
    similar_campaigns = await retrieve_similar_campaigns_tool.ainvoke(
        {"query_text": rag_query, "top_k": 3}
    )

    prompt = (
        "You are a loyalty AI strategist. Analyze the segment and behavioral alerts, "
        "then respond as JSON with keys: summary, patterns, recommended_segment.\n\n"
        f"Segment data: {json.dumps(state.get('segment_data', {}), default=str)}\n"
        f"Behavioral signals: {json.dumps(state.get('behavioral_signals', []), default=str)}\n"
        f"Similar successful campaigns: {json.dumps(similar_campaigns, default=str)}"
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    parsed = _safe_json(getattr(response, "content", response))

    trace = list(state.get("reasoning_trace", []))
    trace.append(
        {
            "node": "reasoning_node",
            "timestamp": datetime.now().isoformat(),
            "message": parsed.get("summary", "Reasoned over current member signals"),
            "rag_matches": len(similar_campaigns or []),
        }
    )

    tool_calls = list(state.get("tool_calls_made", []))
    tool_calls.append(
        {
            "tool": "retrieve_similar_campaigns_tool",
            "query": rag_query[:400],
            "matches": len(similar_campaigns or []),
        }
    )

    messages = list(state.get("messages", []))
    messages.append(HumanMessage(content=prompt))

    result = {
        **state,
        "messages": messages,
        "reasoning_trace": trace,
        "member_context": {
            **state.get("member_context", {}),
            "reasoning": parsed,
            "similar_campaigns": similar_campaigns,
        },
        "tool_calls_made": tool_calls,
    }
    _record_node_observability(
        node="reasoning_node",
        model=model,
        provider=provider,
        prompt_text=prompt,
        output_text=json.dumps(parsed, default=str),
        latency_seconds=time.perf_counter() - started_at,
    )
    return result


async def proposal_generator(state: LoyaltyAgentState) -> LoyaltyAgentState:
    started_at = time.perf_counter()
    member_id = str(state.get("member_context", {}).get("member_id", ""))
    reasoning = state.get("member_context", {}).get("reasoning", {})
    target_segment = reasoning.get("recommended_segment") or state.get("segment_data", {}).get("segment", {}).get("segment", "general")
    summary = reasoning.get("summary", "Generated proposal from available context")

    proposal = await generate_campaign_proposal_tool.ainvoke(
        {
            "member_id": member_id,
            "target_segment": str(target_segment),
            "reasoning_summary": str(summary),
        }
    )

    proposals = list(state.get("campaign_proposals", []))
    proposals.append(proposal)

    trace = list(state.get("reasoning_trace", []))
    trace.append(
        {
            "node": "proposal_generator",
            "timestamp": datetime.now().isoformat(),
            "message": "Generated structured campaign proposal",
            "proposal_id": proposal.get("proposal_id"),
        }
    )

    result = {
        **state,
        "campaign_proposals": proposals,
        "reasoning_trace": trace,
    }
    _record_node_observability(
        node="proposal_generator",
        model="tools",
        provider="internal",
        prompt_text=summary,
        output_text=json.dumps(proposal, default=str),
        latency_seconds=time.perf_counter() - started_at,
    )
    return result


async def roi_estimator(state: LoyaltyAgentState) -> LoyaltyAgentState:
    started_at = time.perf_counter()
    if not state.get("campaign_proposals"):
        return state

    latest = dict(state["campaign_proposals"][-1])
    roi = await estimate_roi_tool.ainvoke(
        {
            "member_id": latest.get("member_id", ""),
            "campaign_type": latest.get("campaign_type", "personalized_offer"),
            "discount_percent": latest.get("discount_percent", 10),
        }
    )

    latest["expected_roi"] = roi.get("expected_roi", 0.0)
    latest["roi_estimate"] = roi

    proposals = list(state.get("campaign_proposals", []))
    proposals[-1] = latest

    trace = list(state.get("reasoning_trace", []))
    trace.append(
        {
            "node": "roi_estimator",
            "timestamp": datetime.now().isoformat(),
            "message": f"Estimated ROI at {roi.get('expected_roi', 0.0)}",
        }
    )

    result = {
        **state,
        "campaign_proposals": proposals,
        "reasoning_trace": trace,
    }
    _record_node_observability(
        node="roi_estimator",
        model="tools",
        provider="internal",
        prompt_text=json.dumps(latest, default=str),
        output_text=json.dumps(roi, default=str),
        latency_seconds=time.perf_counter() - started_at,
    )
    return result


async def confidence_scorer(state: LoyaltyAgentState) -> LoyaltyAgentState:
    started_at = time.perf_counter()
    confidence = 0.5
    if state.get("campaign_proposals"):
        expected_roi = float(state["campaign_proposals"][-1].get("expected_roi", 0.0) or 0.0)
        alerts = len(state.get("behavioral_signals", []))
        confidence = min(0.98, round(0.55 + (expected_roi * 0.6) + min(alerts, 5) * 0.03, 2))

    trace = list(state.get("reasoning_trace", []))
    trace.append(
        {
            "node": "confidence_scorer",
            "timestamp": datetime.now().isoformat(),
            "message": f"Proposal confidence scored at {confidence}",
            "confidence": confidence,
        }
    )

    member_context = dict(state.get("member_context", {}))
    member_context["confidence"] = confidence

    result = {
        **state,
        "member_context": member_context,
        "reasoning_trace": trace,
    }
    _record_node_observability(
        node="confidence_scorer",
        model="heuristic",
        provider="internal",
        prompt_text=json.dumps(state.get("campaign_proposals", []), default=str),
        output_text=json.dumps({"confidence": confidence}),
        latency_seconds=time.perf_counter() - started_at,
    )
    return result


async def human_approval_gate(state: LoyaltyAgentState) -> LoyaltyAgentState:
    started_at = time.perf_counter()
    confidence = float(state.get("member_context", {}).get("confidence", 0.0) or 0.0)
    decision = "auto_propose" if confidence > 0.85 else "flag_for_review"

    proposals = list(state.get("campaign_proposals", []))
    if proposals:
        proposals[-1] = {**proposals[-1], "decision": decision, "confidence": confidence}

    trace = list(state.get("reasoning_trace", []))
    trace.append(
        {
            "node": "human_approval_gate",
            "timestamp": datetime.now().isoformat(),
            "message": f"Decision: {decision}",
            "decision": decision,
        }
    )

    result = {
        **state,
        "campaign_proposals": proposals,
        "reasoning_trace": trace,
    }
    _record_node_observability(
        node="human_approval_gate",
        model="policy",
        provider="internal",
        prompt_text=str(confidence),
        output_text=decision,
        latency_seconds=time.perf_counter() - started_at,
    )
    return result


async def auto_propose(state: LoyaltyAgentState) -> LoyaltyAgentState:
    trace = list(state.get("reasoning_trace", []))
    trace.append(
        {
            "node": "auto_propose",
            "timestamp": datetime.now().isoformat(),
            "message": "Proposal auto-routed for immediate proposal publication",
        }
    )
    return {**state, "reasoning_trace": trace}


async def flag_for_review(state: LoyaltyAgentState) -> LoyaltyAgentState:
    trace = list(state.get("reasoning_trace", []))
    trace.append(
        {
            "node": "flag_for_review",
            "timestamp": datetime.now().isoformat(),
            "message": "Proposal routed to human-in-the-loop review queue",
        }
    )
    return {**state, "reasoning_trace": trace}


def approval_router(state: LoyaltyAgentState) -> str:
    confidence = float(state.get("member_context", {}).get("confidence", 0.0) or 0.0)
    return "auto_propose" if confidence > 0.85 else "flag_for_review"


def build_loyalty_agent_graph():
    graph = StateGraph(LoyaltyAgentState)

    graph.add_node("context_gatherer", context_gatherer)
    graph.add_node("reasoning_node", reasoning_node)
    graph.add_node("proposal_generator", proposal_generator)
    graph.add_node("roi_estimator", roi_estimator)
    graph.add_node("confidence_scorer", confidence_scorer)
    graph.add_node("human_approval_gate", human_approval_gate)
    graph.add_node("auto_propose", auto_propose)
    graph.add_node("flag_for_review", flag_for_review)

    graph.add_edge(START, "context_gatherer")
    graph.add_edge("context_gatherer", "reasoning_node")
    graph.add_edge("reasoning_node", "proposal_generator")
    graph.add_edge("proposal_generator", "roi_estimator")
    graph.add_edge("roi_estimator", "confidence_scorer")
    graph.add_edge("confidence_scorer", "human_approval_gate")

    graph.add_conditional_edges(
        "human_approval_gate",
        approval_router,
        {
            "auto_propose": "auto_propose",
            "flag_for_review": "flag_for_review",
        },
    )

    graph.add_edge("auto_propose", END)
    graph.add_edge("flag_for_review", END)

    return graph.compile(checkpointer=MemorySaver())


class LoyaltyAgentGraphService:
    def __init__(self):
        self.graph = build_loyalty_agent_graph()

    @staticmethod
    def _graph_config() -> Dict[str, Any]:
        return {
            "configurable": {
                "thread_id": f"agent-{int(time.time() * 1000)}"
            }
        }

    async def ainvoke(self, state: LoyaltyAgentState) -> LoyaltyAgentState:
        return await self.graph.ainvoke(state, config=self._graph_config())

    async def astream_node_updates(self, state: LoyaltyAgentState) -> AsyncGenerator[Dict[str, Any], None]:
        async for chunk in self.graph.astream(
            state,
            config=self._graph_config(),
            stream_mode="updates",
        ):
            if isinstance(chunk, dict):
                for node_name, node_output in chunk.items():
                    yield {
                        "event": "node_complete",
                        "node": node_name,
                        "output": node_output,
                    }
