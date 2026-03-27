"""
Risk Agent
Specialized in risk assessment and fraud detection
Monitors for anomalies, fraud, and compliance issues
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.agents.memory import get_agent_memory
from app.agents.tools import get_agent_toolkit


class RiskAgent:
    """
    Assesses risk and detects potential fraud or compliance issues
    Safety-focused agent that can veto high-risk actions
    """

    def __init__(self):
        self.agent_id = "risk_agent"
        self.memory = get_agent_memory()
        self.toolkit = get_agent_toolkit()

    async def assess_campaign_risk(
        self,
        campaign_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Assess risk level of a proposed campaign

        Args:
            campaign_strategy: Proposed campaign strategy

        Returns:
            Risk assessment with score and recommendations
        """
        print(f"🛡️ [{self.agent_id}] Assessing risk for campaign...")

        risk_factors = []
        risk_score = 0.0

        # 1. Budget risk
        budget = campaign_strategy.get("budget", 0)
        if budget > 10000:
            risk_factors.append({
                "factor": "high_budget",
                "severity": "high",
                "description": f"Budget ${budget} exceeds $10,000 threshold",
                "points": 0.3
            })
            risk_score += 0.3
        elif budget > 5000:
            risk_factors.append({
                "factor": "medium_budget",
                "severity": "medium",
                "description": f"Budget ${budget} requires attention",
                "points": 0.15
            })
            risk_score += 0.15

        # 2. Experimental strategy risk
        if campaign_strategy.get("is_experimental", False):
            risk_factors.append({
                "factor": "experimental_strategy",
                "severity": "medium",
                "description": "Untested strategy - higher uncertainty",
                "points": 0.2
            })
            risk_score += 0.2

        # 3. Segment risk (targeting sensitive segments)
        segment = campaign_strategy.get("segment", "")
        if segment in ["all_members", "platinum", "vip"]:
            risk_factors.append({
                "factor": "sensitive_segment",
                "severity": "medium",
                "description": f"Targeting {segment} - high visibility",
                "points": 0.15
            })
            risk_score += 0.15

        # 4. Incentive risk (overly generous offers)
        incentive_value = campaign_strategy.get("incentive", {}).get("value", 0)
        if incentive_value > 100:
            risk_factors.append({
                "factor": "high_incentive",
                "severity": "medium",
                "description": f"Incentive value ${incentive_value} may not be sustainable",
                "points": 0.1
            })
            risk_score += 0.1

        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "critical"
            recommendation = "DENY - Too risky, requires major revision"
        elif risk_score >= 0.4:
            risk_level = "high"
            recommendation = "REQUIRE_APPROVAL - Human review mandatory"
        elif risk_score >= 0.2:
            risk_level = "medium"
            recommendation = "REVIEW_RECOMMENDED - Consider approval with monitoring"
        else:
            risk_level = "low"
            recommendation = "APPROVE - Low risk, safe to proceed"

        assessment = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendation": recommendation,
            "requires_human_approval": risk_score >= 0.4,
            "assessed_by": self.agent_id,
            "timestamp": datetime.now().isoformat()
        }

        print(f"{'🚨' if risk_level in ['high', 'critical'] else '✅'} [{self.agent_id}] Risk: {risk_level} (score: {risk_score:.2f})")

        return assessment

    async def detect_fraud_signals(
        self,
        member_id: str,
        transaction_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Detect potential fraud signals for a member

        Args:
            member_id: Member to check
            transaction_data: Optional transaction details

        Returns:
            Fraud assessment
        """
        print(f"🔍 [{self.agent_id}] Checking fraud signals for {member_id}...")

        fraud_signals = []
        fraud_score = 0.0

        # Get member data
        member_tool = await self.toolkit.execute_tool(
            "get_member_data",
            {
                "member_ids": [member_id],
                "fields": ["tier", "points", "created_at", "total_transactions"]
            }
        )

        if member_tool.success and member_tool.data.get("members"):
            member = member_tool.data["members"][0]

            # Signal 1: New account with high activity
            # (Would check account age and transaction volume)

            # Signal 2: Unusual point accumulation
            points = member.get("points", 0)
            if points > 50000:  # Unusually high points
                fraud_signals.append({
                    "signal": "high_points",
                    "severity": "medium",
                    "description": f"Points balance {points} is unusually high"
                })
                fraud_score += 0.3

            # Signal 3: Rapid tier escalation
            # (Would check tier history)

        # Signal 4: Transaction pattern analysis
        if transaction_data:
            amount = transaction_data.get("amount", 0)
            if amount > 5000:  # Very large transaction
                fraud_signals.append({
                    "signal": "large_transaction",
                    "severity": "medium",
                    "description": f"Transaction amount ${amount} exceeds normal range"
                })
                fraud_score += 0.2

        # Assess fraud risk
        if fraud_score >= 0.6:
            fraud_level = "high"
            action = "FLAG_AND_REVIEW - Manual investigation required"
        elif fraud_score >= 0.3:
            fraud_level = "medium"
            action = "MONITOR - Watch for additional signals"
        else:
            fraud_level = "low"
            action = "CLEAR - No significant fraud indicators"

        return {
            "member_id": member_id,
            "fraud_score": fraud_score,
            "fraud_level": fraud_level,
            "signals": fraud_signals,
            "recommended_action": action,
            "timestamp": datetime.now().isoformat()
        }

    async def validate_compliance(
        self,
        campaign_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate campaign complies with policies and regulations

        Args:
            campaign_strategy: Campaign to validate

        Returns:
            Compliance assessment
        """
        print(f"📋 [{self.agent_id}] Checking compliance...")

        compliance_issues = []
        is_compliant = True

        # Check 1: Privacy compliance (GDPR, etc.)
        personalization = campaign_strategy.get("personalization", {})
        if personalization.get("enabled") and not personalization.get("consent_verified"):
            compliance_issues.append({
                "issue": "missing_consent",
                "severity": "high",
                "description": "Personalization requires verified consent",
                "regulation": "GDPR/CCPA"
            })
            is_compliant = False

        # Check 2: Promotional compliance
        incentive = campaign_strategy.get("incentive", {})
        if incentive.get("type") == "discount" and not campaign_strategy.get("terms_conditions"):
            compliance_issues.append({
                "issue": "missing_terms",
                "severity": "medium",
                "description": "Promotional offers require terms and conditions",
                "regulation": "FTC"
            })

        # Check 3: Frequency limits (don't spam)
        # (Would check how many campaigns member has received recently)

        # Check 4: Opt-out compliance
        channel = campaign_strategy.get("channel")
        if channel == "sms" and not campaign_strategy.get("opt_out_mechanism"):
            compliance_issues.append({
                "issue": "missing_opt_out",
                "severity": "high",
                "description": "SMS campaigns must include opt-out mechanism",
                "regulation": "TCPA"
            })
            is_compliant = False

        return {
            "is_compliant": is_compliant,
            "issues": compliance_issues,
            "recommendation": "APPROVE" if is_compliant else "REJECT - Fix compliance issues",
            "checked_by": self.agent_id,
            "timestamp": datetime.now().isoformat()
        }

    async def monitor_system_health(self) -> Dict[str, Any]:
        """
        Monitor overall system health and identify risks

        Returns:
            System health assessment
        """
        health_checks = []

        # Check 1: Budget utilization
        # (Would check how much of total budget has been spent)

        # Check 2: Campaign success rate
        # (Would check recent campaign performance)

        # Check 3: Member engagement trends
        # (Would check if overall engagement is declining)

        return {
            "system_health": "healthy",
            "checks": health_checks,
            "alerts": [],
            "timestamp": datetime.now().isoformat()
        }


# Singleton
_risk_agent: Optional[RiskAgent] = None


def get_risk_agent() -> RiskAgent:
    """Get singleton risk agent"""
    global _risk_agent
    if _risk_agent is None:
        _risk_agent = RiskAgent()
    return _risk_agent
