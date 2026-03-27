"""
Execution Agent
Specialized in launching and monitoring campaigns
Responsible for: execution, monitoring, real-time adaptation
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from app.agents.memory import get_agent_memory
from app.agents.tools import get_agent_toolkit


class ExecutionAgent:
    """
    Executes campaigns and monitors performance in real-time
    Makes tactical adjustments during campaign execution
    """

    def __init__(self):
        self.agent_id = "execution_agent"
        self.memory = get_agent_memory()
        self.toolkit = get_agent_toolkit()
        self.active_monitors: Dict[str, bool] = {}

    async def execute_campaign(
        self,
        strategy: Dict[str, Any],
        approved: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a campaign based on strategy

        Args:
            strategy: Campaign strategy from strategy agent
            approved: Whether human approval was given

        Returns:
            Execution result with campaign_id and status
        """
        print(f"🚀 [{self.agent_id}] Executing campaign: {strategy.get('name')}...")

        # Prepare campaign configuration
        campaign_config = {
            "name": strategy.get("name"),
            "type": strategy.get("strategy_type"),
            "channel": strategy.get("channel", "email"),
            "segment": strategy.get("segment", "general"),
            "messaging": strategy.get("messaging_angle"),
            "incentive": strategy.get("incentive"),
            "timing": strategy.get("timing"),
            "personalization": strategy.get("personalization", {}),
            "approved": approved
        }

        # Execute via tool
        result = await self.toolkit.execute_tool(
            "execute_campaign",
            {
                "campaign_config": campaign_config,
                "segment": strategy.get("segment"),
                "channel": strategy.get("channel")
            }
        )

        if result.success:
            campaign_id = result.data.get("campaign_id")

            # Start monitoring
            asyncio.create_task(
                self.monitor_campaign(campaign_id, strategy)
            )

            print(f"✅ [{self.agent_id}] Campaign {campaign_id} launched and monitoring started")

            return {
                "success": True,
                "campaign_id": campaign_id,
                "status": "active",
                "monitoring": True
            }
        else:
            print(f"❌ [{self.agent_id}] Campaign execution failed: {result.error}")
            return {
                "success": False,
                "error": result.error
            }

    async def monitor_campaign(
        self,
        campaign_id: str,
        strategy: Dict,
        check_interval_minutes: int = 30
    ):
        """
        Monitor campaign performance in real-time and adapt if needed

        Args:
            campaign_id: Campaign to monitor
            strategy: Original strategy for comparison
            check_interval_minutes: How often to check performance
        """
        print(f"👁️ [{self.agent_id}] Starting monitor for campaign {campaign_id}")

        self.active_monitors[campaign_id] = True

        while self.active_monitors.get(campaign_id, False):
            try:
                # Check performance
                performance = await self.toolkit.execute_tool(
                    "analyze_campaign_performance",
                    {
                        "campaign_id": campaign_id,
                        "metrics": ["response_rate", "roi", "revenue"]
                    }
                )

                if performance.success:
                    metrics = performance.data.get("metrics", {})

                    # Check if adaptation needed
                    needs_adaptation = await self._check_adaptation_needed(
                        campaign_id, metrics, strategy
                    )

                    if needs_adaptation:
                        print(f"⚠️ [{self.agent_id}] Campaign {campaign_id} needs adaptation")
                        await self._adapt_campaign(campaign_id, metrics, strategy)

                # Wait before next check
                await asyncio.sleep(check_interval_minutes * 60)

            except Exception as e:
                print(f"❌ [{self.agent_id}] Monitor error for {campaign_id}: {e}")
                await asyncio.sleep(check_interval_minutes * 60)

    async def _check_adaptation_needed(
        self,
        campaign_id: str,
        current_metrics: Dict,
        expected_strategy: Dict
    ) -> bool:
        """Check if campaign needs tactical adaptation"""

        response_rate = current_metrics.get("response_rate", 0)
        expected_roi = expected_strategy.get("predicted_roi", {}).get("predicted_roi", 0.5)
        actual_roi = current_metrics.get("roi", 0)

        # Adaptation triggers
        if response_rate < 0.10:  # Less than 10% response
            return True

        if actual_roi < expected_roi * 0.5:  # ROI is less than 50% of predicted
            return True

        return False

    async def _adapt_campaign(
        self,
        campaign_id: str,
        current_metrics: Dict,
        strategy: Dict
    ):
        """
        Adapt campaign mid-flight based on performance

        Tactical adaptations:
        - Adjust send timing
        - Pause underperforming variants
        - Increase incentive
        - Change messaging tone
        """
        print(f"🔧 [{self.agent_id}] Adapting campaign {campaign_id}...")

        adaptations = []

        # If very low response, pause and escalate
        if current_metrics.get("response_rate", 0) < 0.05:
            adaptations.append({
                "action": "pause_campaign",
                "reasoning": "Extremely low response rate"
            })

            # Escalate to human review
            print(f"🚨 [{self.agent_id}] Campaign {campaign_id} paused - escalating to human")

        # If moderate underperformance, try adjustments
        elif current_metrics.get("roi", 0) < 0.3:
            adaptations.extend([
                {
                    "action": "adjust_timing",
                    "new_timing": "9am next day",
                    "reasoning": "Shift to higher engagement window"
                },
                {
                    "action": "increase_incentive_10_percent",
                    "reasoning": "Boost offer attractiveness"
                }
            ])

        # Store adaptation in memory for learning
        await self.memory.store_campaign_outcome(
            campaign_id=campaign_id,
            strategy=strategy.get("strategy_type", "unknown"),
            segment=strategy.get("segment", "unknown"),
            channel=strategy.get("channel", "email"),
            budget=0.0,  # Would get actual budget
            actual_roi=current_metrics.get("roi", 0),
            predicted_roi=strategy.get("predicted_roi", {}).get("predicted_roi", 0),
            response_rate=current_metrics.get("response_rate", 0),
            learnings={
                "adaptations_made": adaptations,
                "timestamp": datetime.now().isoformat()
            }
        )

        return adaptations

    async def stop_monitoring(self, campaign_id: str):
        """Stop monitoring a campaign"""
        self.active_monitors[campaign_id] = False
        print(f"⏹️ [{self.agent_id}] Stopped monitoring campaign {campaign_id}")

    async def get_active_campaigns(self) -> List[str]:
        """Get list of actively monitored campaigns"""
        return [
            campaign_id
            for campaign_id, active in self.active_monitors.items()
            if active
        ]


# Singleton
_execution_agent: Optional[ExecutionAgent] = None


def get_execution_agent() -> ExecutionAgent:
    """Get singleton execution agent"""
    global _execution_agent
    if _execution_agent is None:
        _execution_agent = ExecutionAgent()
    return _execution_agent
