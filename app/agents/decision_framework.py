"""
Autonomous Decision Framework
Defines what the agent can decide autonomously vs. requiring human approval
Implements safety guardrails and risk assessment
"""
from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel


class AutonomyLevel(str, Enum):
    """Levels of agent autonomy"""
    FULL_AUTO = "full_auto"  # Agent decides and executes
    HUMAN_IN_LOOP = "human_in_loop"  # Agent proposes, human approves
    HUMAN_REQUIRED = "human_required"  # Always requires human decision


class RiskLevel(str, Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Decision(BaseModel):
    """Represents an agent decision"""
    decision_id: str
    action_type: str
    parameters: Dict[str, Any]
    autonomy_level: AutonomyLevel
    risk_level: RiskLevel
    reasoning: str
    estimated_impact: Dict[str, float]
    requires_approval: bool
    auto_approved: bool = False


class AutonomousDecisionFramework:
    """
    Framework for determining what decisions agent can make autonomously
    Implements safety guardrails and escalation logic
    """

    # Configuration for autonomy levels
    AUTONOMY_CONFIG = {
        AutonomyLevel.FULL_AUTO: {
            "max_budget": 500.0,
            "max_risk_score": 0.3,
            "allowed_actions": [
                "launch_proven_campaign",
                "adjust_campaign_timing",
                "optimize_message",
                "segment_analysis",
                "a_b_test_small"
            ],
            "segment_restrictions": None,  # Any segment
            "min_confidence": 0.7
        },
        AutonomyLevel.HUMAN_IN_LOOP: {
            "max_budget": 5000.0,
            "max_risk_score": 0.7,
            "allowed_actions": [
                "launch_new_campaign",
                "create_new_segment",
                "major_strategy_change",
                "budget_reallocation",
                "a_b_test_large"
            ],
            "segment_restrictions": ["high_value", "vip", "at_risk"],
            "min_confidence": 0.5
        },
        AutonomyLevel.HUMAN_REQUIRED: {
            "max_budget": float('inf'),
            "max_risk_score": 1.0,
            "allowed_actions": [
                "experimental_strategy",
                "major_policy_change",
                "high_budget_campaign",
                "risk_high_action"
            ],
            "segment_restrictions": None,
            "min_confidence": 0.0
        }
    }

    def __init__(self):
        self.override_mode: Optional[AutonomyLevel] = None

    async def evaluate_decision(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        agent_confidence: float,
        estimated_impact: Dict[str, float]
    ) -> Decision:
        """
        Evaluate whether agent can make decision autonomously

        Args:
            action_type: Type of action (e.g., "launch_campaign")
            parameters: Action parameters (budget, segment, etc.)
            agent_confidence: Agent's confidence in this decision (0-1)
            estimated_impact: Predicted impact (roi, revenue, etc.)

        Returns:
            Decision object with autonomy level and approval status
        """
        # Calculate risk level
        risk_level = await self._assess_risk(
            action_type, parameters, estimated_impact
        )

        # Determine autonomy level
        autonomy_level = await self._determine_autonomy_level(
            action_type=action_type,
            budget=parameters.get("budget", 0.0),
            risk_level=risk_level,
            confidence=agent_confidence,
            segment=parameters.get("segment")
        )

        # Check if override is active
        if self.override_mode:
            autonomy_level = self.override_mode

        # Determine if approval needed
        requires_approval = autonomy_level != AutonomyLevel.FULL_AUTO
        auto_approved = autonomy_level == AutonomyLevel.FULL_AUTO

        return Decision(
            decision_id=f"dec_{hash(str(parameters))}",
            action_type=action_type,
            parameters=parameters,
            autonomy_level=autonomy_level,
            risk_level=risk_level,
            reasoning=await self._generate_reasoning(
                autonomy_level, risk_level, parameters
            ),
            estimated_impact=estimated_impact,
            requires_approval=requires_approval,
            auto_approved=auto_approved
        )

    async def _assess_risk(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        estimated_impact: Dict[str, float]
    ) -> RiskLevel:
        """Assess risk level of proposed action"""
        risk_score = 0.0

        # Budget risk
        budget = parameters.get("budget", 0.0)
        if budget > 5000:
            risk_score += 0.4
        elif budget > 1000:
            risk_score += 0.2
        elif budget > 500:
            risk_score += 0.1

        # Strategy risk (new vs proven)
        if parameters.get("is_experimental", False):
            risk_score += 0.3

        if parameters.get("is_new_strategy", False):
            risk_score += 0.2

        # Segment risk
        sensitive_segments = ["vip", "platinum", "all_members"]
        if parameters.get("segment") in sensitive_segments:
            risk_score += 0.2

        # ROI uncertainty risk
        roi_variance = estimated_impact.get("roi_variance", 0.0)
        risk_score += roi_variance * 0.3

        # Classify risk level
        if risk_score < 0.3:
            return RiskLevel.LOW
        elif risk_score < 0.6:
            return RiskLevel.MEDIUM
        elif risk_score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL

    async def _determine_autonomy_level(
        self,
        action_type: str,
        budget: float,
        risk_level: RiskLevel,
        confidence: float,
        segment: Optional[str]
    ) -> AutonomyLevel:
        """Determine appropriate autonomy level for action"""

        # Start with most restrictive and relax if criteria met

        # Check FULL_AUTO eligibility
        config = self.AUTONOMY_CONFIG[AutonomyLevel.FULL_AUTO]
        if (
            budget <= config["max_budget"] and
            risk_level in [RiskLevel.LOW] and
            confidence >= config["min_confidence"] and
            action_type in config["allowed_actions"]
        ):
            return AutonomyLevel.FULL_AUTO

        # Check HUMAN_IN_LOOP eligibility
        config = self.AUTONOMY_CONFIG[AutonomyLevel.HUMAN_IN_LOOP]
        if (
            budget <= config["max_budget"] and
            risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM] and
            confidence >= config["min_confidence"]
        ):
            return AutonomyLevel.HUMAN_IN_LOOP

        # Default to HUMAN_REQUIRED for high-risk actions
        return AutonomyLevel.HUMAN_REQUIRED

    async def _generate_reasoning(
        self,
        autonomy_level: AutonomyLevel,
        risk_level: RiskLevel,
        parameters: Dict[str, Any]
    ) -> str:
        """Generate human-readable reasoning for decision"""
        budget = parameters.get("budget", 0)

        if autonomy_level == AutonomyLevel.FULL_AUTO:
            return (
                f"Auto-approved: Low risk ({risk_level.value}), "
                f"budget ${budget:.2f} within autonomous limit ($500), "
                f"using proven strategy with high confidence."
            )
        elif autonomy_level == AutonomyLevel.HUMAN_IN_LOOP:
            return (
                f"Requires approval: Medium risk ({risk_level.value}), "
                f"budget ${budget:.2f}, new strategy or larger impact. "
                f"Recommending human review before execution."
            )
        else:
            return (
                f"Human approval required: High risk ({risk_level.value}), "
                f"budget ${budget:.2f} exceeds autonomous limits, "
                f"or experimental strategy. Manual review necessary."
            )

    def set_autonomy_override(self, level: Optional[AutonomyLevel]):
        """Temporarily override autonomy level (for testing or emergencies)"""
        self.override_mode = level

    async def get_autonomy_stats(self) -> Dict[str, Any]:
        """Get statistics about autonomy configuration"""
        return {
            "full_auto_budget_limit": self.AUTONOMY_CONFIG[AutonomyLevel.FULL_AUTO]["max_budget"],
            "human_in_loop_budget_limit": self.AUTONOMY_CONFIG[AutonomyLevel.HUMAN_IN_LOOP]["max_budget"],
            "full_auto_actions": self.AUTONOMY_CONFIG[AutonomyLevel.FULL_AUTO]["allowed_actions"],
            "override_active": self.override_mode is not None,
            "override_level": self.override_mode.value if self.override_mode else None
        }


# Singleton instance
_decision_framework: Optional[AutonomousDecisionFramework] = None


def get_decision_framework() -> AutonomousDecisionFramework:
    """Get singleton decision framework instance"""
    global _decision_framework
    if _decision_framework is None:
        _decision_framework = AutonomousDecisionFramework()
    return _decision_framework
