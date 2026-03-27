"""
Specialized Autonomous Agents
Each agent has specific expertise and responsibilities
"""
from app.agents.specialized.strategy_agent import CampaignStrategyAgent
from app.agents.specialized.execution_agent import ExecutionAgent
from app.agents.specialized.analysis_agent import AnalysisAgent
from app.agents.specialized.risk_agent import RiskAgent

__all__ = [
    "CampaignStrategyAgent",
    "ExecutionAgent",
    "AnalysisAgent",
    "RiskAgent",
]
