"""
Loyalty Agent Orchestrator
Main autonomous agent that coordinates sub-agents and makes strategic decisions
Uses LLM for reasoning, planning, and decision-making
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import os
import json

from app.agents.memory import get_agent_memory, AgentMemory
from app.agents.decision_framework import get_decision_framework, AutonomousDecisionFramework, AutonomyLevel
from app.agents.tools import get_agent_toolkit, AgentToolkit
from app.agents.specialized.strategy_agent import get_strategy_agent
from app.agents.specialized.execution_agent import get_execution_agent
from app.agents.specialized.analysis_agent import get_analysis_agent
from app.agents.specialized.risk_agent import get_risk_agent
from app.agents.communication import get_communication_bus, MessageType


class AgentAction(dict):
    """Represents an action the agent wants to take"""
    pass


class LoyaltyAgentOrchestrator:
    """
    Main autonomous agent orchestrator
    Uses LLM for reasoning and coordinates tool use, memory, and decision-making
    """

    def __init__(self):
        self.memory: AgentMemory = get_agent_memory()
        self.decision_framework: AutonomousDecisionFramework = get_decision_framework()
        self.toolkit: AgentToolkit = get_agent_toolkit()

        # Specialized agents
        self.strategy_agent = get_strategy_agent()
        self.execution_agent = get_execution_agent()
        self.analysis_agent = get_analysis_agent()
        self.risk_agent = get_risk_agent()

        # Communication bus
        self.comm_bus = get_communication_bus()

        # LLM client for reasoning
        self.llm_client = self._initialize_llm()

        # Agent state
        self.is_running = False
        self.current_goals: List[str] = []
        self.action_history: List[Dict] = []

    def _initialize_llm(self):
        """Initialize LLM client for agent reasoning"""
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            print("⚠️ No ANTHROPIC_API_KEY found - agent reasoning will be limited")
            return None

        try:
            from anthropic import Anthropic
            return Anthropic(api_key=api_key)
        except ImportError:
            print("⚠️ anthropic package not installed")
            return None

    async def start_autonomous_cycle(self, interval_minutes: int = 15):
        """
        Start continuous autonomous operation
        Agent will analyze, plan, and act on its own

        Args:
            interval_minutes: How often to run analysis cycle
        """
        self.is_running = True
        print(f"🤖 Loyalty Agent starting autonomous operation...")
        print(f"📊 Analysis cycle: every {interval_minutes} minutes")

        cycle_count = 0

        while self.is_running:
            cycle_count += 1
            print(f"\n{'='*60}")
            print(f"🔄 Agent Cycle #{cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")

            try:
                # 1. PERCEIVE: Gather information about current state
                opportunities = await self.perceive_environment()

                # 2. REASON: Use LLM to analyze and create plan
                plan = await self.reason_about_opportunities(opportunities)

                # 3. DECIDE: Evaluate what to do autonomously vs. escalate
                decisions = await self.make_decisions(plan)

                # 4. EXECUTE: Take autonomous actions
                results = await self.execute_decisions(decisions)

                # 5. LEARN: Update memory with outcomes
                await self.learn_from_outcomes(results)

            except Exception as e:
                print(f"❌ Error in agent cycle: {e}")
                import traceback
                traceback.print_exc()

            # Wait for next cycle
            await asyncio.sleep(interval_minutes * 60)

    async def perceive_environment(self) -> Dict[str, Any]:
        """
        Step 1: PERCEIVE
        Gather information about current state using tools and specialized agents
        """
        print("👀 PERCEIVING environment...")

        perceptions = {
            "timestamp": datetime.now().isoformat(),
            "opportunities": [],
            "issues": [],
            "metrics": {}
        }

        # Use Analysis Agent for proactive opportunity discovery
        try:
            # Let Analysis Agent discover opportunities
            opportunities = await self.analysis_agent.discover_opportunities()
            perceptions["opportunities"] = opportunities

            # Analyze segments
            segment_tool = await self.toolkit.execute_tool(
                "analyze_segment",
                {"segment": "high_value", "metrics": ["size", "avg_value"]}
            )

            if segment_tool.success:
                perceptions["segments"] = {
                    "high_value": segment_tool.data
                }

            # Check for trends
            trend_tool = await self.toolkit.execute_tool(
                "detect_trends",
                {"time_period": 7, "metric": "transaction_volume"}
            )

            if trend_tool.success:
                perceptions["trends"] = trend_tool.data

            # Get recent learnings from memory
            recent_learnings = await self.memory.get_recent_learnings(days=7)
            perceptions["recent_learnings"] = recent_learnings

        except Exception as e:
            print(f"⚠️ Error during perception: {e}")

        print(f"✅ Perceived {len(perceptions.get('opportunities', []))} opportunities")
        return perceptions

    async def reason_about_opportunities(
        self,
        perceptions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Step 2: REASON
        Use LLM to analyze perceptions and create strategic plan
        """
        print("🧠 REASONING about opportunities...")

        if not self.llm_client:
            # Fallback to rule-based reasoning
            return await self._fallback_reasoning(perceptions)

        try:
            # Build prompt for LLM reasoning
            prompt = self._build_reasoning_prompt(perceptions)

            # Call Claude for strategic reasoning
            message = self.llm_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            response_text = message.content[0].text

            # Parse LLM response
            plan = self._parse_reasoning_response(response_text)

            print(f"✅ Generated plan with {len(plan.get('actions', []))} actions")
            print(f"📝 Reasoning: {plan.get('summary', 'N/A')[:100]}...")

            return plan

        except Exception as e:
            print(f"⚠️ Error during LLM reasoning: {e}")
            return await self._fallback_reasoning(perceptions)

    def _build_reasoning_prompt(self, perceptions: Dict) -> str:
        """Build prompt for LLM reasoning"""

        tools_description = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.toolkit.get_tool_descriptions()
        ])

        recent_learnings_text = "\n".join([
            f"- Campaign {learning['campaign_id']}: ROI {learning['roi']:.0%}, {learning.get('learnings', {})}"
            for learning in perceptions.get("recent_learnings", [])[:5]
        ])

        prompt = f"""You are an autonomous AI agent managing a loyalty program platform.

Your goal: Maximize customer engagement and campaign ROI while minimizing costs.

Current State:
{json.dumps(perceptions, indent=2, default=str)}

Recent Learnings (past 7 days):
{recent_learnings_text or "No recent data"}

Available Tools:
{tools_description}

Your Autonomy Levels:
- FULL_AUTO: Budget up to $500, proven strategies, auto-execute
- HUMAN_IN_LOOP: Budget up to $5000, new strategies, propose for approval
- HUMAN_REQUIRED: High budget, experimental, always needs approval

Based on the current state and recent learnings, create a strategic plan.

Identify:
1. Opportunities to improve engagement or revenue
2. Risks that need attention
3. Specific actions to take (with tool usage)
4. Expected impact and confidence level

Format your response as JSON:
{{
  "summary": "Brief summary of analysis",
  "opportunities": [
    {{
      "description": "What you found",
      "priority": "high|medium|low",
      "estimated_impact": "Description of impact"
    }}
  ],
  "recommended_actions": [
    {{
      "action_type": "launch_campaign|analyze|optimize|etc",
      "tool_sequence": ["tool1", "tool2"],
      "parameters": {{}},
      "reasoning": "Why this action",
      "estimated_budget": 0.0,
      "estimated_roi": 0.0,
      "confidence": 0.0
    }}
  ]
}}

Provide your strategic plan now:"""

        return prompt

    def _parse_reasoning_response(self, response_text: str) -> Dict:
        """Parse LLM response into structured plan"""
        try:
            # Extract JSON from response
            if "{" in response_text and "}" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                json_str = response_text[json_start:json_end]
                plan = json.loads(json_str)
                return plan
        except Exception as e:
            print(f"⚠️ Error parsing LLM response: {e}")

        # Fallback structure
        return {
            "summary": "Analysis complete",
            "opportunities": [],
            "recommended_actions": []
        }

    async def _fallback_reasoning(self, perceptions: Dict) -> Dict:
        """Fallback reasoning when LLM not available"""
        print("⚠️ Using fallback rule-based reasoning")

        # Simple rule-based logic
        actions = []

        # Check if high-value segment needs attention
        if "segments" in perceptions:
            hv_segment = perceptions["segments"].get("high_value", {})
            if hv_segment and hv_segment.get("analysis", {}).get("avg_recency_days", 0) > 20:
                actions.append({
                    "action_type": "launch_campaign",
                    "parameters": {
                        "segment": "high_value",
                        "campaign_type": "retention",
                        "budget": 300.0
                    },
                    "reasoning": "High-value segment showing signs of inactivity",
                    "estimated_roi": 1.5,
                    "confidence": 0.7
                })

        return {
            "summary": "Rule-based analysis complete",
            "opportunities": [],
            "recommended_actions": actions
        }

    async def make_decisions(self, plan: Dict) -> List[Dict]:
        """
        Step 3: DECIDE
        Evaluate each planned action through decision framework
        """
        print("⚖️ MAKING decisions...")

        decisions = []

        for action in plan.get("recommended_actions", []):
            # Evaluate through decision framework
            decision = await self.decision_framework.evaluate_decision(
                action_type=action.get("action_type", "unknown"),
                parameters=action.get("parameters", {}),
                agent_confidence=action.get("confidence", 0.5),
                estimated_impact={
                    "roi": action.get("estimated_roi", 0.0),
                    "budget": action.get("estimated_budget", 0.0)
                }
            )

            decisions.append({
                "action": action,
                "decision": decision.dict(),
                "will_execute": decision.auto_approved
            })

            # Log decision
            autonomy_emoji = "🟢" if decision.auto_approved else "🟡" if decision.autonomy_level == AutonomyLevel.HUMAN_IN_LOOP else "🔴"
            print(f"{autonomy_emoji} {action['action_type']}: {decision.reasoning}")

        print(f"✅ Made {len(decisions)} decisions")
        return decisions

    async def execute_decisions(self, decisions: List[Dict]) -> List[Dict]:
        """
        Step 4: EXECUTE
        Execute autonomous actions, queue others for human review
        """
        print("⚡ EXECUTING autonomous actions...")

        results = []

        for decision_item in decisions:
            action = decision_item["action"]
            decision = decision_item["decision"]

            if decision_item["will_execute"]:
                # Execute autonomously
                try:
                    result = await self._execute_action(action)
                    results.append({
                        "action": action,
                        "result": result,
                        "status": "executed",
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"✅ Executed: {action['action_type']}")

                except Exception as e:
                    print(f"❌ Execution failed: {e}")
                    results.append({
                        "action": action,
                        "error": str(e),
                        "status": "failed"
                    })

            else:
                # Queue for human review
                await self._queue_for_human_review(action, decision)
                results.append({
                    "action": action,
                    "status": "queued_for_review"
                })
                print(f"📋 Queued for review: {action['action_type']}")

        print(f"✅ Processed {len(results)} actions")
        return results

    async def _execute_action(self, action: Dict) -> Dict:
        """Execute a specific action using tools"""
        action_type = action.get("action_type")
        parameters = action.get("parameters", {})

        # Map action types to tool executions
        if action_type == "launch_campaign":
            return await self.toolkit.execute_tool(
                "execute_campaign",
                {
                    "campaign_config": parameters,
                    "segment": parameters.get("segment"),
                    "channel": parameters.get("channel", "email")
                }
            )

        elif action_type == "analyze":
            return await self.toolkit.execute_tool(
                "analyze_segment",
                parameters
            )

        elif action_type == "create_ab_test":
            return await self.toolkit.execute_tool(
                "create_ab_test",
                parameters
            )

        else:
            return {"status": "unknown_action_type", "action": action_type}

    async def _queue_for_human_review(self, action: Dict, decision: Dict):
        """Queue action for human review"""
        from app.repositories.campaign_proposal_repository import campaign_proposal_repo
        from app.schemas.campaign_proposal import CampaignProposal
        from uuid import uuid4

        # Create proposal for human review
        proposal = CampaignProposal(
            proposal_id=str(uuid4()),
            campaign_type=action.get("parameters", {}).get("campaign_type", "promotion"),
            objective="agent_recommended",
            suggested_offer=action.get("reasoning", "AI-recommended action"),
            validity_hours=48,
            estimated_uplift=action.get("estimated_roi", 0.5) * 0.15,
            estimated_roi=action.get("estimated_roi", 0.5),
            segment=action.get("parameters", {}).get("segment", "general"),
            status="pending"
        )

        campaign_proposal_repo.save(proposal)
        print(f"📝 Created proposal {proposal.proposal_id} for human review")

    async def learn_from_outcomes(self, results: List[Dict]):
        """
        Step 5: LEARN
        Update memory with outcomes for future improvement
        """
        print("📚 LEARNING from outcomes...")

        for result in results:
            if result.get("status") == "executed":
                action = result["action"]

                # Store in memory
                await self.memory.store_campaign_outcome(
                    campaign_id=result.get("result", {}).get("campaign_id", "unknown"),
                    strategy=action.get("action_type", "unknown"),
                    segment=action.get("parameters", {}).get("segment", "general"),
                    channel=action.get("parameters", {}).get("channel", "email"),
                    budget=action.get("estimated_budget", 0.0),
                    actual_roi=0.0,  # Will be updated when campaign completes
                    predicted_roi=action.get("estimated_roi", 0.0),
                    response_rate=0.0,
                    learnings={
                        "action": action,
                        "execution_time": result.get("timestamp")
                    }
                )

        print(f"✅ Updated memory with {len(results)} outcomes")

    async def stop_autonomous_cycle(self):
        """Stop the autonomous operation"""
        self.is_running = False
        print("🛑 Stopping autonomous agent operation...")

    async def get_agent_status(self) -> Dict:
        """Get current agent status and metrics"""
        autonomy_stats = await self.decision_framework.get_autonomy_stats()
        recent_learnings = await self.memory.get_recent_learnings(days=7)

        return {
            "is_running": self.is_running,
            "current_goals": self.current_goals,
            "actions_taken": len(self.action_history),
            "recent_learnings_count": len(recent_learnings),
            "autonomy_config": autonomy_stats,
            "tools_available": len(self.toolkit.tools),
            "llm_enabled": self.llm_client is not None
        }


# Singleton instance
_agent_orchestrator: Optional[LoyaltyAgentOrchestrator] = None


def get_agent_orchestrator() -> LoyaltyAgentOrchestrator:
    """Get singleton agent orchestrator"""
    global _agent_orchestrator
    if _agent_orchestrator is None:
        _agent_orchestrator = LoyaltyAgentOrchestrator()
    return _agent_orchestrator
