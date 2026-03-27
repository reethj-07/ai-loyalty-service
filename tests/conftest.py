"""
Pytest configuration and fixtures
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set test environment variables BEFORE any imports
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_KEY"] = "test-service-key"
os.environ["ENVIRONMENT"] = "test"
os.environ["ENABLE_ML_MODELS"] = "false"
os.environ["ENABLE_EMAIL_SENDING"] = "false"
os.environ["ENABLE_SMS_SENDING"] = "false"

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone


@pytest.fixture(scope="session", autouse=True)
def mock_supabase():
    """Mock Supabase client for all tests"""
    try:
        import app.core.supabase_client as supabase_client  # type: ignore
    except Exception:
        yield MagicMock()
        return

    with patch.object(supabase_client, "create_client") as mock_create:
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.execute.return_value.data = []
        mock_create.return_value = mock_client
        yield mock_client


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)


@pytest.fixture(scope="session")
def pg_container():
    """Optional PostgreSQL container fixture for integration tests."""
    try:
        from testcontainers.postgres import PostgresContainer
    except Exception:
        pytest.skip("testcontainers[postgresql] is not installed")

    with PostgresContainer("postgres:16") as postgres:
        yield {"url": postgres.get_connection_url()}


@pytest.fixture(scope="session")
def redis_container():
    """Optional Redis container fixture for integration tests."""
    try:
        from testcontainers.redis import RedisContainer
    except Exception:
        pytest.skip("testcontainers[redis] is not installed")

    with RedisContainer("redis:7") as redis:
        yield {"url": redis.get_connection_url()}


@pytest.fixture
def mock_llm(monkeypatch):
    """Deterministic LLM fixture avoiding real network API calls."""
    from langchain_core.messages import AIMessage

    class DeterministicLLM:
        async def ainvoke(self, _messages, **_kwargs):
            return AIMessage(
                content='{"summary":"mock summary","patterns":["high value"],"recommended_segment":"Champions"}'
            )

    monkeypatch.setattr("app.agents.graph.get_llm", lambda streaming=False: DeterministicLLM())
    return DeterministicLLM()


@pytest.fixture
def sample_members():
    members = []
    tiers = ["Bronze", "Silver", "Gold", "Platinum"]
    for i in range(20):
        members.append(
            {
                "id": f"member_{i}",
                "first_name": f"Member{i}",
                "last_name": "Test",
                "tier": tiers[i % len(tiers)],
                "points_balance": i * 100,
            }
        )
    return members


@pytest.fixture
def sample_transactions(sample_members):
    transactions = []
    now = datetime.now(timezone.utc)
    for i in range(200):
        member = sample_members[i % len(sample_members)]
        transactions.append(
            {
                "id": f"txn_{i}",
                "member_id": member["id"],
                "amount": float(20 + (i % 15) * 10),
                "currency": "USD",
                "merchant": "Test Store",
                "category": "shopping",
                "channel": "online",
                "transaction_date": (now - timedelta(days=i % 90)).isoformat(),
            }
        )
    return transactions
