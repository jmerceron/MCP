import pytest

# Configure pytest markers
def pytest_configure(config):
    # Register asyncio marker
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as an asyncio test",
    )
    # Register tools marker
    config.addinivalue_line(
        "markers",
        "tools: mark test as a tools test",
    )

# Event loop configuration is now handled by pytest-asyncio directly
# We don't need to define our own event_loop fixture anymore
