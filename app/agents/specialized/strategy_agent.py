"""
Campaign Strategy Agent
Specialized in designing campaign strategies and planning
Uses LLM for creative strategy development
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import json

from app.agents.memory import get_agent_memory
from app.agents.tools import get_agent_toolkit


class CampaignStrategyAgent:
    """
    Designs campaign strategies using historical data and LLM reasoning
    Responsible for: strategy selection, targeting, messaging, timing
    """

    def __init__(self):
        self.agent_id = "strategy_agent"
        self.memory = get_agent_memory()
        self.toolkit = get_agent_toolkit()
        self.llm_client = self._initialize_llm()

    def _initialize_llm(self):
        """Initialize LLM client"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None

        try:
            from anthropic import Anthropic
            return Anthropic(api_key=api_key)
        except ImportError:
            return None

    async def design_campaign_strategy(
        self,
        objective: str,
        segment: str,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Design a comprehensive campaign strategy

        Args:
            objective: Campaign objective (e.g., "retention", "upsell")
            segment: Target segment
            constraints: Budget, timeline, channel restrictions

        Returns:
            Detailed campaign strategy with reasoning
        """
        print(f"🎨 [{self.agent_id}] Designing strategy for {segment} segment...")

        # 1. Gather context from memory
        similar_campaigns = await self.memory.recall_similar_campaigns(
            segment=segment,
            channel=constraints.get("preferred_channel", "email"),
            limit=5
        )

        strategy_performance = await self.memory.get_strategy_performance(objective)

        # 2. Analyze segment
        segment_analysis = await self.toolkit.execute_tool(
            "analyze_segment",
            {"segment": segment, "metrics": ["size", "avg_value", "recency"]}
        )

        # 3. Use LLM for creative strategy design
        if self.llm_client:
            strategy = await self._design_with_llm(
                objective=objective,
                segment=segment,
                constraints=constraints,
                similar_campaigns=similar_campaigns,
                strategy_performance=strategy_performance,
                segment_analysis=segment_analysis.data if segment_analysis.success else {}
            )
        else:
            strategy = await self._design_with_rules(
                objective, segment, constraints
            )

        # 4. Predict ROI
        roi_prediction = await self.toolkit.execute_tool(
            "predict_roi",
            {
                "campaign_config": strategy,
                "segment_size": segment_analysis.data.get("size", 100) if segment_analysis.success else 100
            }
        )

        strategy["predicted_roi"] = roi_prediction.data if roi_prediction.success else {"predicted_roi": 0.5}

        print(f"✅ [{self.agent_id}] Strategy designed: {strategy['name']}")

        return strategy

    async def _design_with_llm(
        self,
        objective: str,
        segment: str,
        constraints: Dict,
        similar_campaigns: List,
        strategy_performance: Dict,
        segment_analysis: Dict
    ) -> Dict:
        """Use LLM to design creative campaign strategy"""

        similar_campaigns_text = "\n".join([
            f"- {c.campaign_id}: ROI {c.actual_roi:.0%}, Response {c.response_rate:.0%}"
            for c in similar_campaigns[:3]
        ]) or "No historical data"

        prompt = f"""You are a campaign strategy expert designing a loyalty program campaign.

Objective: {objective}
Target Segment: {segment}
Budget: ${constraints.get('budget', 'not specified')}
Preferred Channel: {constraints.get('preferred_channel', 'any')}

Segment Analysis:
{json.dumps(segment_analysis, indent=2, default=str)}

Historical Performance (similar campaigns):
{similar_campaigns_text}

Strategy Performance History:
- Success Rate: {strategy_performance.get('success_rate', 0):.0%}
- Avg ROI: {strategy_performance.get('avg_roi', 0):.0%}
- Confidence: {strategy_performance.get('confidence', 0):.0%}

Design a creative, data-driven campaign strategy that:
1. Achieves the objective effectively
2. Learns from past performance
3. Stays within constraints
4. Maximizes ROI

Consider:
- What messaging will resonate with this segment?
- What incentive structure works best?
- When should we send (timing, day of week)?
- Should we run A/B tests?
- What's the fallback if campaign underperforms?

Respond in JSON format:
{{
  "name": "Campaign name",
  "strategy_type": "{objective}",
  "channel": "email|sms|push",
  "messaging_angle": "urgency|value|exclusivity|appreciation",
  "incentive": {{
    "type": "points|discount|bonus",
    "value": 0.0,
    "description": "..."
  }},
  "timing": {{
    "send_hour": 9,
    "send_day": "weekday|weekend",
    "duration_days": 7
  }},
  "personalization": {{
    "enabled": true,
    "fields": ["name", "tier", "points"]
  }},
  "ab_test": {{
    "enabled": true,
    "variants": ["variant1", "variant2"]
  }},
  "success_metrics": ["response_rate", "roi", "conversion"],
  "fallback_strategy": "What to do if underperforming",
  "reasoning": "Why this strategy will work"
}}"""

        try:
            message = self.llm_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text

            # Parse JSON response
            if "{" in response_text and "}" in response_text:
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                json_str = response_text[json_start:json_end]
                strategy = json.loads(json_str)
                return strategy

        except Exception as e:
            print(f"⚠️ LLM strategy design failed: {e}")

        # Fallback to rules
        return await self._design_with_rules(objective, segment, constraints)

    async def _design_with_rules(
        self,
        objective: str,
        segment: str,
        constraints: Dict
    ) -> Dict:
        """Fallback rule-based strategy design"""

        strategy_templates = {
            "retention": {
                "name": f"{segment.title()} Retention Campaign",
                "strategy_type": "retention",
                "channel": constraints.get("preferred_channel", "email"),
                "messaging_angle": "appreciation",
                "incentive": {
                    "type": "bonus_points",
                    "value": 500,
                    "description": "Thank you bonus for loyalty"
                },
                "timing": {
                    "send_hour": 10,
                    "send_day": "weekday",
                    "duration_days": 7
                },
                "personalization": {"enabled": True, "fields": ["name", "tier"]},
                "ab_test": {"enabled": False},
                "success_metrics": ["response_rate", "roi"],
                "reasoning": "Appreciation-based messaging works for retention"
            },
            "upsell": {
                "name": f"{segment.title()} Upsell Campaign",
                "strategy_type": "upsell",
                "channel": "email",
                "messaging_angle": "value",
                "incentive": {
                    "type": "discount",
                    "value": 15.0,
                    "description": "15% off premium tier upgrade"
                },
                "timing": {
                    "send_hour": 9,
                    "send_day": "weekday",
                    "duration_days": 5
                },
                "personalization": {"enabled": True, "fields": ["name", "tier", "points"]},
                "ab_test": {"enabled": True, "variants": ["15% off", "20% off"]},
                "success_metrics": ["conversion_rate", "revenue"],
                "reasoning": "Value proposition drives upsells"
            }
        }

        return strategy_templates.get(objective, strategy_templates["retention"])

    async def optimize_existing_strategy(
        self,
        campaign_id: str,
        current_performance: Dict
    ) -> Dict:
        """
        Optimize an underperforming campaign mid-flight

        Args:
            campaign_id: Campaign to optimize
            current_performance: Current metrics

        Returns:
            Optimization recommendations
        """
        print(f"🔧 [{self.agent_id}] Optimizing campaign {campaign_id}...")

        response_rate = current_performance.get("response_rate", 0)
        expected_rate = current_performance.get("expected_rate", 0.25)

        if response_rate >= expected_rate * 0.9:
            return {
                "action": "continue",
                "reasoning": "Campaign performing as expected",
                "changes": []
            }

        # Campaign is underperforming
        optimizations = []

        if response_rate < expected_rate * 0.5:
            # Severe underperformance
            optimizations.append({
                "change": "pause_and_redesign",
                "reasoning": "Severe underperformance - needs major revision",
                "impact": "high"
            })
        else:
            # Moderate underperformance - try adjustments
            optimizations.extend([
                {
                    "change": "adjust_send_time",
                    "new_value": "9am instead of current time",
                    "reasoning": "9am shows better open rates historically",
                    "impact": "medium"
                },
                {
                    "change": "strengthen_cta",
                    "new_value": "More urgent call-to-action",
                    "reasoning": "May increase click-through",
                    "impact": "low"
                },
                {
                    "change": "increase_incentive",
                    "new_value": "20% increase in offer value",
                    "reasoning": "Make offer more compelling",
                    "impact": "high"
                }
            ])

        return {
            "action": "optimize",
            "current_performance": current_performance,
            "optimizations": optimizations,
            "reasoning": f"Response rate {response_rate:.0%} vs expected {expected_rate:.0%}"
        }

    async def generate_creative_variants(
        self,
        base_strategy: Dict,
        num_variants: int = 3
    ) -> List[Dict]:
        """
        Generate creative variants for A/B testing

        Args:
            base_strategy: Base campaign strategy
            num_variants: Number of variants to generate

        Returns:
            List of strategy variants
        """
        if not self.llm_client:
            # Simple rule-based variants
            return [
                {**base_strategy, "variant_id": "A", "subject": "Original"},
                {**base_strategy, "variant_id": "B", "subject": "Variant 1"},
                {**base_strategy, "variant_id": "C", "subject": "Variant 2"}
            ]

        # Use LLM to generate creative variants
        variants = [base_strategy]  # Include original

        for i in range(num_variants - 1):
            variant = base_strategy.copy()
            variant["variant_id"] = chr(65 + i + 1)  # B, C, D...
            # In production, use LLM to generate different messaging angles
            variants.append(variant)

        return variants


# Singleton
_strategy_agent: Optional[CampaignStrategyAgent] = None


def get_strategy_agent() -> CampaignStrategyAgent:
    """Get singleton strategy agent"""
    global _strategy_agent
    if _strategy_agent is None:
        _strategy_agent = CampaignStrategyAgent()
    return _strategy_agent
