"""
Inter-Agent Communication Protocol
Enables agents to communicate, collaborate, and coordinate
"""
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
import asyncio
from collections import defaultdict


class MessageType(str, Enum):
    """Types of inter-agent messages"""
    REQUEST = "request"  # Request another agent to do something
    RESPONSE = "response"  # Response to a request
    NOTIFICATION = "notification"  # Inform other agents of an event
    QUERY = "query"  # Ask for information
    ALERT = "alert"  # Urgent notification


class AgentMessage(BaseModel):
    """Message exchanged between agents"""
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    subject: str
    content: Dict[str, Any]
    timestamp: datetime
    reply_to: Optional[str] = None
    priority: str = "normal"  # low, normal, high, urgent


class AgentCommunicationBus:
    """
    Central communication bus for inter-agent messaging
    Agents subscribe to topics and exchange messages
    """

    def __init__(self):
        self.message_queue: List[AgentMessage] = []
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[AgentMessage] = []

    async def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message_type: MessageType,
        subject: str,
        content: Dict[str, Any],
        priority: str = "normal",
        reply_to: Optional[str] = None
    ) -> str:
        """
        Send a message from one agent to another

        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            message_type: Type of message
            subject: Message subject
            content: Message payload
            priority: Message priority
            reply_to: ID of message this is replying to

        Returns:
            message_id: ID of sent message
        """
        message_id = f"msg_{datetime.now().timestamp()}_{from_agent}"

        message = AgentMessage(
            message_id=message_id,
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            subject=subject,
            content=content,
            timestamp=datetime.now(),
            reply_to=reply_to,
            priority=priority
        )

        # Add to queue
        self.message_queue.append(message)
        self.message_history.append(message)

        # Notify subscribers
        await self._notify_subscribers(to_agent, message)

        print(f"📨 Message: {from_agent} → {to_agent}: {subject}")

        return message_id

    async def _notify_subscribers(self, agent_id: str, message: AgentMessage):
        """Notify all subscribers for an agent"""
        if agent_id in self.subscribers:
            for handler in self.subscribers[agent_id]:
                try:
                    await handler(message)
                except Exception as e:
                    print(f"❌ Error in message handler for {agent_id}: {e}")

    def subscribe(self, agent_id: str, handler: Callable):
        """
        Subscribe to messages for a specific agent

        Args:
            agent_id: Agent to receive messages for
            handler: Async function to handle messages
        """
        self.subscribers[agent_id].append(handler)
        print(f"📮 {agent_id} subscribed to message bus")

    async def get_messages_for_agent(
        self,
        agent_id: str,
        unread_only: bool = True
    ) -> List[AgentMessage]:
        """Get messages for a specific agent"""
        messages = [
            msg for msg in self.message_queue
            if msg.to_agent == agent_id
        ]

        if unread_only:
            # Remove from queue (marking as read)
            self.message_queue = [
                msg for msg in self.message_queue
                if msg.to_agent != agent_id
            ]

        return messages

    async def broadcast(
        self,
        from_agent: str,
        subject: str,
        content: Dict[str, Any],
        message_type: MessageType = MessageType.NOTIFICATION
    ):
        """
        Broadcast message to all agents

        Args:
            from_agent: Sender agent ID
            subject: Message subject
            content: Message payload
            message_type: Type of message
        """
        # In practice, would send to all registered agents
        print(f"📢 Broadcast from {from_agent}: {subject}")

        # Store in history
        message = AgentMessage(
            message_id=f"broadcast_{datetime.now().timestamp()}",
            from_agent=from_agent,
            to_agent="all",
            message_type=message_type,
            subject=subject,
            content=content,
            timestamp=datetime.now()
        )

        self.message_history.append(message)

    async def get_conversation(
        self,
        agent1: str,
        agent2: str,
        limit: int = 20
    ) -> List[AgentMessage]:
        """Get conversation history between two agents"""
        conversation = [
            msg for msg in self.message_history
            if (msg.from_agent == agent1 and msg.to_agent == agent2) or
               (msg.from_agent == agent2 and msg.to_agent == agent1)
        ]

        return conversation[-limit:]


class AgentCollaborationSession:
    """
    Represents a collaboration session between multiple agents
    Agents work together to accomplish a complex goal
    """

    def __init__(
        self,
        session_id: str,
        goal: str,
        participating_agents: List[str]
    ):
        self.session_id = session_id
        self.goal = goal
        self.agents = participating_agents
        self.messages: List[AgentMessage] = []
        self.status = "active"
        self.results: Dict[str, Any] = {}
        self.started_at = datetime.now()

    async def add_message(self, message: AgentMessage):
        """Add message to collaboration session"""
        self.messages.append(message)

    async def complete(self, results: Dict[str, Any]):
        """Mark collaboration session as complete"""
        self.status = "completed"
        self.results = results
        print(f"✅ Collaboration session {self.session_id} completed")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of collaboration session"""
        return {
            "session_id": self.session_id,
            "goal": self.goal,
            "agents": self.agents,
            "messages_exchanged": len(self.messages),
            "status": self.status,
            "duration_seconds": (datetime.now() - self.started_at).total_seconds(),
            "results": self.results
        }


# Example collaboration patterns

async def example_multi_agent_campaign_creation(comm_bus: AgentCommunicationBus):
    """
    Example: Multi-agent collaboration to create a campaign

    Flow:
    1. Analysis Agent identifies opportunity
    2. Requests Strategy Agent to design campaign
    3. Strategy Agent designs and asks Risk Agent for assessment
    4. Risk Agent assesses and approves
    5. Execution Agent launches campaign
    """

    # 1. Analysis Agent identifies opportunity
    await comm_bus.send_message(
        from_agent="analysis_agent",
        to_agent="strategy_agent",
        message_type=MessageType.REQUEST,
        subject="Design campaign for dormant VIPs",
        content={
            "opportunity": {
                "type": "dormant_vip",
                "segment_size": 342,
                "avg_recency": 25,
                "potential_revenue": 51300
            },
            "budget_constraint": 2000
        }
    )

    # 2. Strategy Agent designs campaign
    await comm_bus.send_message(
        from_agent="strategy_agent",
        to_agent="risk_agent",
        message_type=MessageType.QUERY,
        subject="Risk assessment for VIP retention campaign",
        content={
            "campaign_strategy": {
                "name": "VIP Win-Back",
                "budget": 1800,
                "segment": "high_value",
                "incentive_value": 15
            }
        }
    )

    # 3. Risk Agent assesses
    await comm_bus.send_message(
        from_agent="risk_agent",
        to_agent="strategy_agent",
        message_type=MessageType.RESPONSE,
        subject="Risk assessment complete",
        content={
            "risk_level": "low",
            "approved": True,
            "recommendation": "APPROVE - Low risk campaign"
        }
    )

    # 4. Strategy Agent confirms to Execution Agent
    await comm_bus.send_message(
        from_agent="strategy_agent",
        to_agent="execution_agent",
        message_type=MessageType.REQUEST,
        subject="Execute VIP Win-Back campaign",
        content={
            "campaign_id": "camp_vip_001",
            "strategy": {"name": "VIP Win-Back", "budget": 1800},
            "approved": True
        }
    )

    # 5. Execution Agent launches and notifies all
    await comm_bus.broadcast(
        from_agent="execution_agent",
        subject="Campaign camp_vip_001 launched",
        content={
            "campaign_id": "camp_vip_001",
            "status": "active",
            "start_time": datetime.now().isoformat()
        }
    )


# Singleton
_communication_bus: Optional[AgentCommunicationBus] = None


def get_communication_bus() -> AgentCommunicationBus:
    """Get singleton communication bus"""
    global _communication_bus
    if _communication_bus is None:
        _communication_bus = AgentCommunicationBus()
    return _communication_bus
