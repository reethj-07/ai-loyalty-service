"""
Agent Memory System
Stores agent's knowledge, experiences, and learned strategies
Enables contextual decision-making and continuous learning
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pydantic import BaseModel


class CampaignMemory(BaseModel):
    """Memory of past campaign execution and outcomes"""
    campaign_id: str
    strategy: str
    segment: str
    channel: str
    budget: float
    actual_roi: float
    predicted_roi: float
    response_rate: float
    timestamp: datetime
    learnings: Dict[str, Any]


class MemberPreference(BaseModel):
    """Learned preferences for individual members"""
    member_id: str
    preferred_channel: Optional[str] = None
    best_send_time: Optional[int] = None  # Hour of day
    response_patterns: Dict[str, float] = {}
    last_updated: datetime


class StrategyOutcome(BaseModel):
    """Outcome tracking for different strategies"""
    strategy_name: str
    success_count: int
    failure_count: int
    avg_roi: float
    contexts: List[Dict[str, Any]]  # When it worked/failed
    confidence_score: float


class AgentMemory:
    """
    Persistent memory store for autonomous agent
    Enables learning from past experiences and contextual decision-making
    """

    def __init__(self):
        self.campaign_history: List[CampaignMemory] = []
        self.member_preferences: Dict[str, MemberPreference] = {}
        self.strategy_outcomes: Dict[str, StrategyOutcome] = {}
        self.ongoing_experiments: Dict[str, Dict] = {}
        self.discovered_patterns: List[Dict] = []

    async def store_campaign_outcome(
        self,
        campaign_id: str,
        strategy: str,
        segment: str,
        channel: str,
        budget: float,
        actual_roi: float,
        predicted_roi: float,
        response_rate: float,
        learnings: Dict[str, Any]
    ):
        """Store campaign results for future learning"""
        memory = CampaignMemory(
            campaign_id=campaign_id,
            strategy=strategy,
            segment=segment,
            channel=channel,
            budget=budget,
            actual_roi=actual_roi,
            predicted_roi=predicted_roi,
            response_rate=response_rate,
            timestamp=datetime.now(),
            learnings=learnings
        )

        self.campaign_history.append(memory)

        # Update strategy outcome tracking
        await self._update_strategy_outcome(strategy, actual_roi, learnings)

    async def _update_strategy_outcome(
        self,
        strategy_name: str,
        roi: float,
        context: Dict
    ):
        """Update success/failure tracking for strategies"""
        if strategy_name not in self.strategy_outcomes:
            self.strategy_outcomes[strategy_name] = StrategyOutcome(
                strategy_name=strategy_name,
                success_count=0,
                failure_count=0,
                avg_roi=0.0,
                contexts=[],
                confidence_score=0.0
            )

        outcome = self.strategy_outcomes[strategy_name]

        if roi > 0.5:  # 50% ROI threshold for success
            outcome.success_count += 1
        else:
            outcome.failure_count += 1

        # Update average ROI
        total = outcome.success_count + outcome.failure_count
        outcome.avg_roi = (outcome.avg_roi * (total - 1) + roi) / total

        # Calculate confidence score
        outcome.confidence_score = min(
            outcome.success_count / max(total, 1),
            total / 20  # Need 20+ samples for full confidence
        )

        outcome.contexts.append(context)

    async def recall_similar_campaigns(
        self,
        segment: str,
        channel: str,
        limit: int = 5
    ) -> List[CampaignMemory]:
        """Retrieve similar past campaigns for context"""
        similar = [
            c for c in self.campaign_history
            if c.segment == segment and c.channel == channel
        ]

        # Sort by recency and ROI
        similar.sort(
            key=lambda x: (x.timestamp, x.actual_roi),
            reverse=True
        )

        return similar[:limit]

    async def get_member_preferences(self, member_id: str) -> Optional[MemberPreference]:
        """Get learned preferences for a member"""
        return self.member_preferences.get(member_id)

    async def update_member_preference(
        self,
        member_id: str,
        channel: Optional[str] = None,
        response: bool = False
    ):
        """Update member preferences based on interactions"""
        if member_id not in self.member_preferences:
            self.member_preferences[member_id] = MemberPreference(
                member_id=member_id,
                last_updated=datetime.now()
            )

        pref = self.member_preferences[member_id]

        if channel:
            # Track channel response rates
            if channel not in pref.response_patterns:
                pref.response_patterns[channel] = 0.0

            # Update with exponential moving average
            current = pref.response_patterns[channel]
            new_value = 1.0 if response else 0.0
            pref.response_patterns[channel] = 0.7 * current + 0.3 * new_value

            # Update preferred channel
            if pref.response_patterns[channel] > 0.5:
                pref.preferred_channel = channel

        pref.last_updated = datetime.now()

    async def get_strategy_confidence(self, strategy_name: str) -> float:
        """Get confidence score for a strategy (0-1)"""
        outcome = self.strategy_outcomes.get(strategy_name)
        if not outcome:
            return 0.0
        return outcome.confidence_score

    async def get_strategy_performance(self, strategy_name: str) -> Dict:
        """Get detailed performance metrics for a strategy"""
        outcome = self.strategy_outcomes.get(strategy_name)
        if not outcome:
            return {
                "success_rate": 0.0,
                "avg_roi": 0.0,
                "confidence": 0.0,
                "sample_size": 0
            }

        total = outcome.success_count + outcome.failure_count
        return {
            "success_rate": outcome.success_count / max(total, 1),
            "avg_roi": outcome.avg_roi,
            "confidence": outcome.confidence_score,
            "sample_size": total,
            "contexts": outcome.contexts[-5:]  # Last 5 contexts
        }

    async def store_discovered_pattern(
        self,
        pattern_description: str,
        data: Dict,
        confidence: float
    ):
        """Store patterns discovered through analysis"""
        self.discovered_patterns.append({
            "description": pattern_description,
            "data": data,
            "confidence": confidence,
            "discovered_at": datetime.now().isoformat()
        })

    async def get_recent_learnings(self, days: int = 7) -> List[Dict]:
        """Get recent learnings and insights"""
        cutoff = datetime.now() - timedelta(days=days)

        recent_campaigns = [
            c for c in self.campaign_history
            if c.timestamp > cutoff
        ]

        learnings = []
        for campaign in recent_campaigns:
            learnings.append({
                "campaign_id": campaign.campaign_id,
                "strategy": campaign.strategy,
                "roi": campaign.actual_roi,
                "learnings": campaign.learnings,
                "timestamp": campaign.timestamp.isoformat()
            })

        return learnings

    async def start_experiment(
        self,
        experiment_id: str,
        description: str,
        variants: List[Dict],
        success_criteria: Dict
    ):
        """Track ongoing experiments (A/B tests)"""
        self.ongoing_experiments[experiment_id] = {
            "description": description,
            "variants": variants,
            "success_criteria": success_criteria,
            "started_at": datetime.now().isoformat(),
            "results": []
        }

    async def record_experiment_result(
        self,
        experiment_id: str,
        variant: str,
        outcome: Dict
    ):
        """Record results from ongoing experiments"""
        if experiment_id in self.ongoing_experiments:
            self.ongoing_experiments[experiment_id]["results"].append({
                "variant": variant,
                "outcome": outcome,
                "timestamp": datetime.now().isoformat()
            })

    async def get_experiment_status(self, experiment_id: str) -> Optional[Dict]:
        """Get status of ongoing experiment"""
        return self.ongoing_experiments.get(experiment_id)

    async def export_memory(self) -> Dict:
        """Export memory for persistence"""
        return {
            "campaign_history": [c.model_dump() for c in self.campaign_history],
            "member_preferences": {
                k: v.model_dump() for k, v in self.member_preferences.items()
            },
            "strategy_outcomes": {
                k: v.model_dump() for k, v in self.strategy_outcomes.items()
            },
            "ongoing_experiments": self.ongoing_experiments,
            "discovered_patterns": self.discovered_patterns
        }

    async def import_memory(self, data: Dict):
        """Import memory from storage"""
        if "campaign_history" in data:
            self.campaign_history = [
                CampaignMemory(**c) for c in data["campaign_history"]
            ]

        if "member_preferences" in data:
            self.member_preferences = {
                k: MemberPreference(**v)
                for k, v in data["member_preferences"].items()
            }

        if "strategy_outcomes" in data:
            self.strategy_outcomes = {
                k: StrategyOutcome(**v)
                for k, v in data["strategy_outcomes"].items()
            }

        if "ongoing_experiments" in data:
            self.ongoing_experiments = data["ongoing_experiments"]

        if "discovered_patterns" in data:
            self.discovered_patterns = data["discovered_patterns"]


# Singleton instance
_agent_memory: Optional[AgentMemory] = None


def get_agent_memory() -> AgentMemory:
    """Get singleton agent memory instance"""
    global _agent_memory
    if _agent_memory is None:
        _agent_memory = AgentMemory()
    return _agent_memory
