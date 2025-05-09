import asyncio
import pytest
from main import (
    # Basic tools
    add, usd_to_gbp, get_height_for_16_9, calculate_bmi,
    # Weather tools
    fetch_US_weather, fetch_international_weather,
    # Notes tools
    add_note_to_file, read_note_in_a_file,
    # MCP instance
    mcp
)

@pytest.mark.asyncio
async def test_basic_tools(capfd):
    """Test basic calculation tools"""
    # Test addition
    result = add(5, 3)
    print(f"\nTesting addition: 5 + 3 = {result}")
    assert result == 8, f"Addition test failed: expected 8, got {result}"
    
    # Test currency conversion
    result = usd_to_gbp(100)
    print(f"Testing currency conversion: 100 USD = £{result}")
    assert result == 79.00, f"Currency conversion test failed: expected 79.00, got {result}"
    
    # Test screen ratio calculation
    result = get_height_for_16_9(1920)
    print(f"Testing 16:9 ratio calculation: width=1920, height={result}")
    assert result == 1080.0, f"Screen ratio test failed: expected 1080.0, got {result}"
    
    # Test BMI calculation
    result = calculate_bmi(70, 1.75)
    print(f"Testing BMI calculation: 70kg, 1.75m = {result}")
    assert abs(result - 22.86) < 0.01, f"BMI calculation test failed: expected ~22.86, got {result}"

@pytest.mark.asyncio
async def test_weather_tools(capfd):
    """Test weather information retrieval tools"""
    # Test US weather
    print("\nTesting US Weather API with Seattle, WA")
    result = await fetch_US_weather("Seattle, WA")
    print(f"US Weather result:\n{result}")
    
    if "Error:" in result:
        pytest.xfail(f"US Weather API test failed: {result}")
    
    assert isinstance(result, str), "US Weather should return a string"
    assert "Current weather in Seattle, WA" in result, "Expected weather information for Seattle, WA"
    assert "Temperature:" in result, "Response should contain temperature"
    assert "Wind:" in result, "Response should contain wind information"
    
    # Test international weather
    print("\nTesting International Weather API with London")
    result = await fetch_international_weather("London")
    print(f"International Weather result:\n{result}")
    
    if "Error:" in result:
        pytest.xfail(f"International Weather API test failed: {result}")
    
    assert isinstance(result, str), "International Weather should return a string"
    assert "Current weather in London" in result, "Expected weather information for London"
    assert "Temperature:" in result, "Response should contain temperature"
    assert "Wind:" in result, "Response should contain wind information"

@pytest.mark.asyncio
async def test_note_tools(capfd):
    """Test note management tools"""
    import datetime
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    test_note = f"Test note created on {current_time}"
    
    print("\nTesting note addition")
    result = add_note_to_file(test_note)
    print(f"Add note result: {result}")
    assert result == "A note was saved!", f"Note addition failed: {result}"

    print("\nTesting note reading")
    result = read_note_in_a_file()
    print(f"Read notes result:\n{result}")
    assert isinstance(result, str), "Note reading should return a string"
    assert test_note in result, "Recently added note not found in results"

# Keep the main() function for manual testing if needed
async def main():
    print("Starting MCP Tools Test Suite...", flush=True)
    try:
        await test_basic_tools()
        await test_weather_tools()
        await test_note_tools()
        print("\nAll tests completed!", flush=True)
    except Exception as e:
        print(f"\nError during testing: {type(e).__name__}: {str(e)}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())