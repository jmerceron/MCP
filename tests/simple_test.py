import pytest
from main import add

@pytest.mark.asyncio
async def test_addition():
    """Test the basic addition function"""
    print("\nTesting simple addition operation")
    a, b = 5, 3
    result = add(a, b)
    print(f"Testing: {a} + {b} = {result}")
    assert result == 8, f"Addition failed: expected 8, got {result}"
