"""
Agent API Endpoints
Exposes autonomous agent functionality and status
"""
from fastapi import APIRouter, BackgroundTasks
from typing import Dict, Any

from app.agents.orchestrator import get_agent_orchestrator
from app.agents.memory import get_agent_memory
from app.agents.decision_framework import get_decision_framework

router = APIRouter(
    tags=["Autonomous Agents"]
)


@router.get("/status")
async def get_agent_status():
    """
    Get current status of the autonomous agent system

    Returns:
        Agent status including running state, autonomy config, and metrics
    """
    orchestrator = get_agent_orchestrator()
    status = await orchestrator.get_agent_status()

    return {
        "agent_system": "Loyalty AI Agent",
        "version": "1.0.0",
        **status
    }


@router.post("/start")
async def start_agent(
    background_tasks: BackgroundTasks,
    interval_minutes: int = 15
):
    """
    Start the autonomous agent system

    Args:
        interval_minutes: How often agent analyzes and acts (default: 15)

    Returns:
        Confirmation message
    """
    orchestrator = get_agent_orchestrator()

    if orchestrator.is_running:
        return {
            "status": "already_running",
            "message": "Agent is already operating autonomously"
        }

    # Start agent in background
    background_tasks.add_task(
        orchestrator.start_autonomous_cycle,
        interval_minutes=interval_minutes
    )

    return {
        "status": "started",
        "message": f"Autonomous agent started with {interval_minutes}min analysis cycle",
        "interval_minutes": interval_minutes
    }


@router.post("/stop")
async def stop_agent():
    """
    Stop the autonomous agent system

    Returns:
        Confirmation message
    """
    orchestrator = get_agent_orchestrator()
    await orchestrator.stop_autonomous_cycle()

    return {
        "status": "stopped",
        "message": "Autonomous agent operation stopped"
    }


@router.get("/memory/recent")
async def get_recent_learnings(days: int = 7):
    """
    Get recent learnings from agent memory

    Args:
        days: Number of days to look back (default: 7)

    Returns:
        Recent campaign outcomes and learnings
    """
    memory = get_agent_memory()
    learnings = await memory.get_recent_learnings(days=days)

    return {
        "period_days": days,
        "learnings_count": len(learnings),
        "learnings": learnings
    }


@router.get("/memory/strategy/{strategy_name}")
async def get_strategy_performance(strategy_name: str):
    """
    Get performance metrics for a specific strategy

    Args:
        strategy_name: Name of the strategy

    Returns:
        Performance metrics and confidence score
    """
    memory = get_agent_memory()
    performance = await memory.get_strategy_performance(strategy_name)

    return {
        "strategy": strategy_name,
        **performance
    }


@router.get("/memory/patterns")
async def get_discovered_patterns():
    """
    Get patterns discovered by the agent through analysis

    Returns:
        List of discovered patterns and insights
    """
    memory = get_agent_memory()

    return {
        "patterns": memory.discovered_patterns,
        "count": len(memory.discovered_patterns)
    }


@router.get("/autonomy/config")
async def get_autonomy_configuration():
    """
    Get agent autonomy configuration

    Returns:
        Autonomy levels and what agent can do autonomously
    """
    framework = get_decision_framework()
    config = await framework.get_autonomy_stats()

    return {
        "autonomy_levels": {
            "full_auto": {
                "description": "Agent executes without approval",
                "budget_limit": config["full_auto_budget_limit"],
                "allowed_actions": config["full_auto_actions"]
            },
            "human_in_loop": {
                "description": "Agent proposes, human approves",
                "budget_limit": config["human_in_loop_budget_limit"]
            },
            "human_required": {
                "description": "Always requires human approval",
                "budget_limit": "unlimited"
            }
        },
        "current_override": config.get("override_level")
    }


@router.post("/autonomy/override")
async def set_autonomy_override(level: str):
    """
    Temporarily override autonomy level (for testing/emergencies)

    Args:
        level: "full_auto", "human_in_loop", "human_required", or "none"

    Returns:
        Confirmation message
    """
    from app.agents.decision_framework import AutonomyLevel

    framework = get_decision_framework()

    if level == "none":
        framework.set_autonomy_override(None)
        return {"status": "override_cleared", "message": "Autonomy override removed"}

    try:
        autonomy_level = AutonomyLevel(level)
        framework.set_autonomy_override(autonomy_level)

        return {
            "status": "override_set",
            "message": f"Autonomy override set to {level}",
            "level": level
        }
    except ValueError:
        return {
            "status": "error",
            "message": f"Invalid autonomy level: {level}"
        }


@router.get("/reasoning/latest")
async def get_latest_reasoning():
    """
    Get the agent's latest reasoning and decision-making process

    Returns:
        Latest reasoning chain and decisions
    """
    orchestrator = get_agent_orchestrator()

    if not orchestrator.action_history:
        return {
            "message": "No reasoning history available yet",
            "actions": []
        }

    # Return last 10 actions
    recent_actions = orchestrator.action_history[-10:]

    return {
        "reasoning_history": recent_actions,
        "count": len(recent_actions)
    }


@router.post("/analyze/now")
async def trigger_immediate_analysis():
    """
    Trigger an immediate analysis cycle (doesn't wait for scheduled interval)

    Returns:
        Analysis results and actions taken
    """
    orchestrator = get_agent_orchestrator()

    # Run one cycle
    perceptions = await orchestrator.perceive_environment()
    plan = await orchestrator.reason_about_opportunities(perceptions)
    decisions = await orchestrator.make_decisions(plan)
    results = await orchestrator.execute_decisions(decisions)
    await orchestrator.learn_from_outcomes(results)

    return {
        "status": "analysis_complete",
        "perceptions": perceptions,
        "plan_summary": plan.get("summary"),
        "decisions_made": len(decisions),
        "actions_executed": len([r for r in results if r.get("status") == "executed"]),
        "actions_queued": len([r for r in results if r.get("status") == "queued_for_review"]),
        "results": results
    }
