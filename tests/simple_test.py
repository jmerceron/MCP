import asyncio
from main import add

async def test_addition():
    print("Testing addition...")
    try:
        add_tool = add
        result = add_tool(5, 3)
        print(f"5 + 3 = {result}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")

async def main():
    print("Starting MCP function test...")
    await test_addition()
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
