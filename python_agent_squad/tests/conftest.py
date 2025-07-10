"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import the app for testing
try:
    from python_agent_squad.main import app
except ImportError:
    app = None


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client():
    """Create test client for FastAPI app."""
    if app is None:
        pytest.skip("FastAPI app not available")
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client for FastAPI app."""
    if app is None:
        pytest.skip("FastAPI app not available")
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("GENERATOR_PORT", "8001")
    monkeypatch.setenv("SQUAD_API_PORT", "8000")
    return monkeypatch