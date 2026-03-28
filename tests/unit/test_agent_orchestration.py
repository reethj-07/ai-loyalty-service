import pytest

from app.agents.decision_framework import (
    AutonomyLevel,
    AutonomousDecisionFramework,
    Decision,
    RiskLevel,
)
from app.agents.orchestrator import LoyaltyAgentOrchestrator


@pytest.mark.asyncio
async def test_decision_framework_normalizes_action_aliases():
    framework = AutonomousDecisionFramework()

    decision = await framework.evaluate_decision(
        action_type="launch_proven_campaign",
        parameters={"budget": 200.0, "segment": "general"},
        agent_confidence=0.9,
        estimated_impact={"roi": 1.4, "roi_variance": 0.0},
    )

    assert decision.autonomy_level == AutonomyLevel.FULL_AUTO
    assert decision.auto_approved is True


def test_orchestrator_validates_tool_sequence_by_action_policy():
    orchestrator = LoyaltyAgentOrchestrator.__new__(LoyaltyAgentOrchestrator)

    invalid = orchestrator._validate_action_tool_sequence(
        {
            "action_type": "launch_campaign",
            "tool_sequence": ["execute_campaign", "query_database"],
        }
    )
    valid = orchestrator._validate_action_tool_sequence(
        {
            "action_type": "launch_campaign",
            "tool_sequence": ["analyze_segment", "predict_roi", "execute_campaign"],
        }
    )

    assert invalid is not None
    assert "unauthorized tools" in invalid
    assert valid is None


def test_orchestrator_validates_action_aliases_and_owner_contract():
    orchestrator = LoyaltyAgentOrchestrator.__new__(LoyaltyAgentOrchestrator)

    aliased_valid = orchestrator._validate_action_tool_sequence(
        {
            "action_type": "launch_proven_campaign",
            "tool_sequence": ["analyze_segment", "predict_roi", "execute_campaign"],
            "owner": "execution_agent",
        }
    )
    owner_mismatch = orchestrator._validate_action_tool_sequence(
        {
            "action_type": "launch_campaign",
            "tool_sequence": ["analyze_segment", "predict_roi", "execute_campaign"],
            "owner": "risk_agent",
        }
    )

    assert aliased_valid is None
    assert owner_mismatch is not None
    assert "must be owned by" in owner_mismatch


def test_owner_for_action_uses_canonical_aliases():
    orchestrator = LoyaltyAgentOrchestrator.__new__(LoyaltyAgentOrchestrator)

    assert orchestrator._owner_for_action("launch_proven_campaign") == "execution_agent"
    assert orchestrator._owner_for_action("segment_analysis") == "analysis_agent"


@pytest.mark.asyncio
async def test_make_decisions_propagates_estimated_budget_into_parameters():
    orchestrator = LoyaltyAgentOrchestrator.__new__(LoyaltyAgentOrchestrator)

    captured = {}

    class _FakeFramework:
        async def evaluate_decision(self, action_type, parameters, agent_confidence, estimated_impact):
            captured["action_type"] = action_type
            captured["parameters"] = dict(parameters)
            return Decision(
                decision_id="d1",
                action_type=action_type,
                parameters=parameters,
                autonomy_level=AutonomyLevel.FULL_AUTO,
                risk_level=RiskLevel.LOW,
                reasoning="ok",
                estimated_impact=estimated_impact,
                requires_approval=False,
                auto_approved=True,
            )

    orchestrator.decision_framework = _FakeFramework()

    decisions = await orchestrator.make_decisions(
        {
            "recommended_actions": [
                {
                    "action_type": "launch_campaign",
                    "parameters": {"segment": "high_value"},
                    "estimated_budget": 450.0,
                    "estimated_roi": 1.2,
                    "confidence": 0.8,
                }
            ]
        }
    )

    assert decisions[0]["will_execute"] is True
    assert captured["parameters"].get("budget") == 450.0


@pytest.mark.asyncio
async def test_execute_launch_campaign_uses_specialized_agents_when_safe():
    orchestrator = LoyaltyAgentOrchestrator.__new__(LoyaltyAgentOrchestrator)

    class _FakeStrategy:
        async def design_campaign_strategy(self, objective, segment, constraints):
            return {
                "name": "Retention Strategy",
                "strategy_type": objective,
                "channel": constraints.get("preferred_channel", "email"),
                "segment": segment,
                "incentive": {"type": "discount", "value": 10},
                "personalization": {"enabled": True, "consent_verified": True},
                "terms_conditions": True,
                "opt_out_mechanism": True,
            }

    class _FakeRisk:
        async def assess_campaign_risk(self, strategy):
            return {"requires_human_approval": False, "risk_level": "low"}

        async def validate_compliance(self, strategy):
            return {"is_compliant": True, "issues": []}

    class _FakeExecution:
        async def execute_campaign(self, strategy, approved=False):
            return {"success": True, "campaign_id": "camp_123", "status": "active"}

    class _FakeToolkit:
        async def execute_tool(self, *_args, **_kwargs):
            raise AssertionError("Fallback toolkit execution should not be used for safe specialized path")

    orchestrator.strategy_agent = _FakeStrategy()
    orchestrator.risk_agent = _FakeRisk()
    orchestrator.execution_agent = _FakeExecution()
    orchestrator.toolkit = _FakeToolkit()

    result = await orchestrator._execute_action(
        {
            "action_type": "launch_campaign",
            "parameters": {
                "campaign_type": "retention",
                "segment": "high_value",
                "channel": "email",
                "budget": 300.0,
            },
        }
    )

    assert result.get("campaign_id") == "camp_123"
    assert result.get("execution", {}).get("success") is True
