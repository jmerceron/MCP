import asyncio
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

async def test_basic_tools():
    print("\n=== Testing Basic Tools ===", flush=True)
    # Test addition
    result = add(5, 3)
    print(f"Addition test (5 + 3): {result}", flush=True)
    
    # Test currency conversion
    result = usd_to_gbp(100)
    print(f"Currency conversion test (100 USD to GBP): £{result}", flush=True)
    
    # Test screen ratio calculation
    result = get_height_for_16_9(1920)
    print(f"16:9 height calculation test (width=1920): {result}", flush=True)
    
    # Test BMI calculation
    result = calculate_bmi(70, 1.75)
    print(f"BMI calculation test (70kg, 1.75m): {result}", flush=True)

async def test_weather_tools():
    print("\n=== Testing Weather Tools ===", flush=True)
    # Test US weather
    result = await fetch_US_weather("Seattle, WA")
    print(f"US Weather test (Seattle):\n{result}\n", flush=True)
    
    # Test international weather
    result = await fetch_international_weather("London")
    print(f"International Weather test (London):\n{result}", flush=True)

async def test_note_tools():
    print("\n=== Testing Note Tools ===", flush=True)
    # Test adding a note
    import datetime
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = add_note_to_file(f"Test note created on {current_time}")
    print(f"Add note test: {result}", flush=True)

    # Test reading notes
    result = read_note_in_a_file()
    print(f"Read notes test:\n{result}", flush=True)

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
