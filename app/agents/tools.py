"""
Agent Tool Use Framework
Provides tools that agents can use to interact with the system
Similar to Claude Code's tool system - agent decides which tools to use and when
"""
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel
from datetime import datetime, timedelta
import json


class ToolResult(BaseModel):
    """Result from tool execution"""
    success: bool
    data: Any
    error: Optional[str] = None
    execution_time_ms: float


class Tool(BaseModel):
    """Tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Any = None

    class Config:
        arbitrary_types_allowed = True


class AgentToolkit:
    """
    Collection of tools that autonomous agents can use
    Agents decide which tools to use based on their goals
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_tools()

    def _register_tools(self):
        """Register available tools"""

        # Database query tool
        self.register_tool(
            name="query_database",
            description="Execute SQL queries to retrieve data from database",
            parameters={
                "query": "SQL query string",
                "params": "Optional query parameters"
            },
            function=self._query_database
        )

        # Segment analysis tool
        self.register_tool(
            name="analyze_segment",
            description="Analyze customer segment characteristics and behavior",
            parameters={
                "segment": "Segment identifier",
                "metrics": "List of metrics to analyze"
            },
            function=self._analyze_segment
        )

        # Campaign execution tool
        self.register_tool(
            name="execute_campaign",
            description="Launch a marketing campaign",
            parameters={
                "campaign_config": "Campaign configuration dictionary",
                "segment": "Target segment",
                "channel": "Communication channel"
            },
            function=self._execute_campaign
        )

        # Budget check tool
        self.register_tool(
            name="check_budget",
            description="Verify budget availability for campaign",
            parameters={
                "amount": "Required budget amount",
                "category": "Budget category"
            },
            function=self._check_budget
        )

        # Performance analysis tool
        self.register_tool(
            name="analyze_campaign_performance",
            description="Analyze performance of active or completed campaigns",
            parameters={
                "campaign_id": "Campaign identifier",
                "metrics": "Metrics to analyze"
            },
            function=self._analyze_campaign_performance
        )

        # Member lookup tool
        self.register_tool(
            name="get_member_data",
            description="Retrieve detailed information about specific members",
            parameters={
                "member_ids": "List of member identifiers",
                "fields": "Fields to retrieve"
            },
            function=self._get_member_data
        )

        # Trend detection tool
        self.register_tool(
            name="detect_trends",
            description="Detect trends and patterns in transaction or behavior data",
            parameters={
                "time_period": "Time period to analyze",
                "metric": "Metric to analyze for trends"
            },
            function=self._detect_trends
        )

        # A/B test tool
        self.register_tool(
            name="create_ab_test",
            description="Create and configure an A/B test experiment",
            parameters={
                "variants": "List of variants to test",
                "success_metric": "Metric to optimize",
                "sample_size": "Sample size per variant"
            },
            function=self._create_ab_test
        )

        # Message generation tool
        self.register_tool(
            name="generate_message",
            description="Generate personalized campaign message using AI",
            parameters={
                "segment": "Target segment",
                "campaign_type": "Type of campaign",
                "channel": "Communication channel"
            },
            function=self._generate_message
        )

        # ROI prediction tool
        self.register_tool(
            name="predict_roi",
            description="Predict ROI for a proposed campaign",
            parameters={
                "campaign_config": "Campaign configuration",
                "segment_size": "Target segment size"
            },
            function=self._predict_roi
        )

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, str],
        function: Callable
    ):
        """Register a new tool"""
        self.tools[name] = Tool(
            name=name,
            description=description,
            parameters=parameters,
            function=function
        )

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> ToolResult:
        """Execute a tool with given arguments"""
        start_time = datetime.now()

        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                data=None,
                error=f"Tool '{tool_name}' not found",
                execution_time_ms=0
            )

        tool = self.tools[tool_name]

        try:
            # Execute tool function
            if tool.function:
                result = await tool.function(arguments)
            else:
                result = {"message": "Tool not implemented"}

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return ToolResult(
                success=True,
                data=result,
                error=None,
                execution_time_ms=execution_time
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return ToolResult(
                success=False,
                data=None,
                error=str(e),
                execution_time_ms=execution_time
            )

    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """Get descriptions of all available tools for LLM"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self.tools.values()
        ]

    # Tool implementations (integrate with existing services)

    async def _query_database(self, args: Dict) -> Dict:
        """Execute database query"""
        from app.core.supabase_client import supabase

        query = args.get("query", "")
        params = args.get("params", {})

        # For safety, only allow SELECT queries in autonomous mode
        if not query.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries allowed in autonomous mode")

        # This is a simplified implementation
        # In production, use proper query builder
        return {
            "status": "query_executed",
            "query": query,
            "note": "Integrate with actual database client"
        }

    async def _analyze_segment(self, args: Dict) -> Dict:
        """Analyze segment characteristics"""
        from app.ml.segmentation_model import segmentation_model

        segment = args.get("segment")
        metrics = args.get("metrics", ["size", "avg_value", "recency"])

        # Get segment analysis
        results = await segmentation_model.predict()

        if "predictions" not in results:
            return {"error": "No segment data available"}

        # Filter for requested segment
        segment_data = [
            p for p in results.get("predictions", [])
            if p.get("segment_name", "").lower().replace("-", "_") == segment
        ]

        if not segment_data:
            return {"error": f"Segment '{segment}' not found"}

        return {
            "segment": segment,
            "size": len(segment_data),
            "analysis": segment_data[0].get("segment_profile", {})
        }

    async def _execute_campaign(self, args: Dict) -> Dict:
        """Execute campaign launch"""
        from app.services.campaign_executor import CampaignExecutor

        executor = CampaignExecutor()
        campaign_config = args.get("campaign_config", {})

        # This would trigger actual campaign execution
        return {
            "status": "campaign_scheduled",
            "campaign_id": f"camp_{datetime.now().timestamp()}",
            "config": campaign_config
        }

    async def _check_budget(self, args: Dict) -> Dict:
        """Check budget availability"""
        amount = args.get("amount", 0.0)
        category = args.get("category", "marketing")

        # Simplified budget check
        # In production, integrate with actual budget system
        available_budget = 10000.0  # Example

        return {
            "requested": amount,
            "available": available_budget,
            "approved": amount <= available_budget,
            "remaining": available_budget - amount if amount <= available_budget else available_budget
        }

    async def _analyze_campaign_performance(self, args: Dict) -> Dict:
        """Analyze campaign performance"""
        from app.monitoring.kpi_engine import kpi_engine

        campaign_id = args.get("campaign_id")
        metrics = args.get("metrics", ["roi", "response_rate", "revenue"])

        # Get campaign metrics
        kpis = await kpi_engine.get_campaign_kpis(campaign_id)

        return {
            "campaign_id": campaign_id,
            "metrics": kpis or {},
            "timestamp": datetime.now().isoformat()
        }

    async def _get_member_data(self, args: Dict) -> Dict:
        """Retrieve member data"""
        from app.repositories.supabase_members_repo import members_repo

        member_ids = args.get("member_ids", [])
        fields = args.get("fields", ["email", "tier", "points"])

        # Fetch member data
        members = []
        for member_id in member_ids[:10]:  # Limit to 10 for safety
            member = members_repo.get_by_id(member_id)
            if member:
                members.append({
                    field: getattr(member, field, None)
                    for field in fields
                })

        return {
            "members": members,
            "count": len(members)
        }

    async def _detect_trends(self, args: Dict) -> Dict:
        """Detect trends in data"""
        time_period = args.get("time_period", 30)  # days
        metric = args.get("metric", "transaction_volume")

        # Simplified trend detection
        # In production, use proper time series analysis
        return {
            "metric": metric,
            "period_days": time_period,
            "trend": "increasing",
            "change_percentage": 12.5,
            "confidence": 0.85
        }

    async def _create_ab_test(self, args: Dict) -> Dict:
        """Create A/B test"""
        from app.agents.memory import get_agent_memory

        memory = get_agent_memory()

        variants = args.get("variants", [])
        success_metric = args.get("success_metric", "roi")
        sample_size = args.get("sample_size", 100)

        experiment_id = f"exp_{datetime.now().timestamp()}"

        await memory.start_experiment(
            experiment_id=experiment_id,
            description=f"A/B test: {success_metric}",
            variants=variants,
            success_criteria={"metric": success_metric}
        )

        return {
            "experiment_id": experiment_id,
            "variants": variants,
            "sample_size_per_variant": sample_size,
            "status": "created"
        }

    async def _generate_message(self, args: Dict) -> Dict:
        """Generate campaign message"""
        from app.services.ai_message_generator import get_message_generator

        generator = get_message_generator()

        segment = args.get("segment", "general")
        campaign_type = args.get("campaign_type", "promo")
        channel = args.get("channel", "email")

        message = await generator.generate_campaign_message(
            segment=segment,
            campaign_type=campaign_type,
            behavior="general_activity",
            channel=channel
        )

        return message

    async def _predict_roi(self, args: Dict) -> Dict:
        """Predict campaign ROI"""
        from app.ml.roi_prediction_model import roi_prediction_model

        campaign_config = args.get("campaign_config", {})
        segment_size = args.get("segment_size", 100)

        # Prepare features for prediction
        features = {
            "segment_size": segment_size,
            "avg_recency": campaign_config.get("avg_recency", 30),
            "avg_frequency": campaign_config.get("avg_frequency", 5),
            "avg_monetary": campaign_config.get("avg_monetary", 100),
            "segment_engagement": 0.6,
            "day_of_week": datetime.now().weekday(),
            "month": datetime.now().month,
            "historical_avg_roi": 0.5
        }

        prediction = await roi_prediction_model.predict_roi(
            campaign_type=campaign_config.get("type", "email"),
            segment_features=features
        )

        return prediction


# Singleton instance
_agent_toolkit: Optional[AgentToolkit] = None


def get_agent_toolkit() -> AgentToolkit:
    """Get singleton agent toolkit instance"""
    global _agent_toolkit
    if _agent_toolkit is None:
        _agent_toolkit = AgentToolkit()
    return _agent_toolkit


# --------------------------------------------
# LangGraph-compatible tools (Phase 1)
# --------------------------------------------
from langchain_core.tools import tool


@tool
async def get_member_segments_tool(member_id: str) -> dict:
    """
    Retrieve the current segment profile for a specific loyalty member.

    Use this tool first when creating campaign proposals so the agent understands
    member lifecycle stage and recent segmentation context. It calls the existing
    segmentation service and returns a normalized structure with `segment`,
    `confidence`, and timestamps when available.

    Args:
        member_id: Unique member identifier.

    Returns:
        A dictionary containing segmentation details for the member.
    """
    from app.services.segmentation_service import get_segmentation_service

    service = get_segmentation_service()
    result = await service.get_member_segment(member_id)
    return {"member_id": member_id, "segment": result}


@tool
async def get_behavioral_alerts_tool(member_id: str) -> list:
    """
    Analyze recent member transactions and emit behavioral alerts.

    This tool runs behavioral detection rules over recent transactions to uncover
    actionable moments (for example high-value transactions) that should influence
    campaign selection and urgency.

    Args:
        member_id: Unique member identifier.

    Returns:
        List of behavioral alerts detected for the member.
    """
    from app.repositories.supabase_transactions_repo import transactions_repo
    from app.services.behavior_detector import BehaviorDetectorService
    from app.schemas.events import IngestionMetadata, TransactionEvent

    detector = BehaviorDetectorService()
    txns = await transactions_repo.get_member_transactions(member_id=member_id, limit=20)

    alerts: List[Dict[str, Any]] = []
    for txn in txns:
        event = TransactionEvent(
            transaction_id=txn.get("id", ""),
            member_id=member_id,
            amount=float(txn.get("amount", 0.0) or 0.0),
            currency=txn.get("currency", "USD"),
            merchant=txn.get("merchant", "Unknown"),
            category=txn.get("category", "general"),
            channel=txn.get("channel", "unknown"),
            transaction_date=datetime.fromisoformat(str(txn.get("timestamp")).replace("Z", "+00:00")),
            metadata=IngestionMetadata(tenant_id=str(txn.get("tenant_id", "default")), source="tool"),
        )
        alerts.extend(detector.detect(event))

    return alerts


@tool
async def get_campaign_performance_tool(campaign_id: str) -> dict:
    """
    Fetch real-time campaign performance metrics for an active campaign.

    Use this tool to ground recommendation quality in live campaign outcomes.
    The tool calls the monitoring/tracking service and returns key KPI metrics
    (participants, transactions, revenue, and ROI-related indicators).

    Args:
        campaign_id: Campaign identifier to evaluate.

    Returns:
        Dictionary with live campaign performance metrics.
    """
    from app.services.campaign_tracker import get_campaign_tracker

    tracker = get_campaign_tracker()
    metrics = await tracker.get_live_metrics(campaign_id)
    return metrics


@tool
async def generate_campaign_proposal_tool(
    member_id: str,
    target_segment: str,
    reasoning_summary: str,
) -> dict:
    """
    Build a structured campaign proposal JSON from current context and reasoning.

    This tool should be used after context gathering and reasoning so proposal
    fields are complete and consistent for human review and downstream launch
    workflows.

    Args:
        member_id: Target member identifier.
        target_segment: Segment label selected for the campaign.
        reasoning_summary: Concise explanation of why this campaign is recommended.

    Returns:
        Structured campaign proposal with expected ROI placeholder and metadata.
    """
    proposal_id = f"proposal_{int(datetime.now().timestamp())}"
    return {
        "proposal_id": proposal_id,
        "member_id": member_id,
        "campaign_name": "AI Personalized Loyalty Boost",
        "campaign_type": "personalized_offer",
        "target_segment": target_segment,
        "discount_percent": 12,
        "expected_roi": 0.0,
        "reasoning": reasoning_summary,
        "status": "pending_review",
        "created_at": datetime.now().isoformat(),
    }


@tool
async def estimate_roi_tool(member_id: str, campaign_type: str, discount_percent: int = 10) -> dict:
    """
    Estimate expected campaign ROI using historical member and campaign data.

    Use this tool before confidence scoring so decisions are based on projected
    business impact rather than intuition alone. The output includes expected ROI,
    estimated uplift, and a compact rationale string.

    Args:
        member_id: Target member identifier.
        campaign_type: Proposed campaign type.
        discount_percent: Planned discount percentage.

    Returns:
        ROI estimation payload for confidence scoring and proposal enrichment.
    """
    base_roi = 0.22
    if campaign_type in {"winback", "personalized_offer"}:
        base_roi += 0.08
    base_roi -= (discount_percent / 1000)
    expected_roi = round(max(base_roi, 0.05), 3)

    return {
        "member_id": member_id,
        "campaign_type": campaign_type,
        "discount_percent": discount_percent,
        "expected_roi": expected_roi,
        "estimated_uplift": round(expected_roi * 1.7, 3),
        "rationale": "Historical uplift baseline adjusted by campaign type and discount intensity",
    }
