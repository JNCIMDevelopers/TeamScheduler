"""
Configuration for pytest test suite.
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_app():
    """Create test FastAPI application."""
    from src.api.main import app

    return app


@pytest.fixture(scope="function")
def reset_repositories():
    """Reset repositories to clean state before each test."""
    # This ensures each test starts with fresh sample data
    from src.infrastructure.database.repositories import (
        InMemoryPersonRepository,
        InMemoryEventRepository,
    )

    # Reset repositories to initial state
    InMemoryPersonRepository._persons.clear()
    InMemoryEventRepository._events.clear()

    # Reinitialize with sample data
    InMemoryPersonRepository._initialize_sample_data()

    yield

    # Cleanup after test
    InMemoryPersonRepository._persons.clear()
    InMemoryEventRepository._events.clear()
    InMemoryPersonRepository._initialize_sample_data()


# Note: Using default pytest-asyncio event loop configuration
