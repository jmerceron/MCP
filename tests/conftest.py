import pytest

# Configure asyncio defaults
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as an asyncio test",
    )

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
