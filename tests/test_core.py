import pytest
import os
import tempfile
from unittest.mock import patch, mock_open, AsyncMock, MagicMock
import httpx
from main import (
    # Basic tools
    add, usd_to_gbp, get_height_for_16_9, calculate_bmi,
    # Weather functions
    _get_wind_direction, fetch_US_weather, fetch_international_weather,
    # Web crawler utilities
    remove_unicode, strip_html_tags, truncate,
    crawl_web_truncated, crawl_web_summarize_and_truncate,
    # Notes functionality
    ensure_file_exists, add_note_to_file, read_note_in_a_file,
)

# Basic tools tests
def test_add():
    print("\nTesting addition function")
    result = add(2, 3)
    print(f"2 + 3 = {result}")
    assert result == 5, f"Expected 5, got {result}"
    
    result = add(-1, 1)
    print(f"-1 + 1 = {result}")
    assert result == 0, f"Expected 0, got {result}"
    
    result = add(0, 0)
    print(f"0 + 0 = {result}")
    assert result == 0, f"Expected 0, got {result}"

def test_usd_to_gbp():
    print("\nTesting USD to GBP conversion (exchange rate: 0.79)")
    # Test with known exchange rate of 0.79
    result = usd_to_gbp(100)
    print(f"100 USD = £{result}")
    assert result == 79.00, f"Expected 79.00, got {result}"
    
    result = usd_to_gbp(1)
    print(f"1 USD = £{result}")
    assert result == 0.79, f"Expected 0.79, got {result}"
    
    result = usd_to_gbp(0)
    print(f"0 USD = £{result}")
    assert result == 0.00, f"Expected 0.00, got {result}"

def test_get_height_for_16_9():
    print("\nTesting 16:9 aspect ratio calculations")
    result = get_height_for_16_9(1920)
    print(f"Width 1920 -> Height {result}")
    assert result == 1080, f"Expected 1080, got {result}"
    
    result = get_height_for_16_9(3840)
    print(f"Width 3840 -> Height {result}")
    assert result == 2160, f"Expected 2160, got {result}"
    
    result = get_height_for_16_9(0)
    print(f"Width 0 -> Height {result}")
    assert result == 0, f"Expected 0, got {result}"

def test_calculate_bmi():
    print("\nTesting BMI calculations")
    # Test normal BMI case
    result = calculate_bmi(70, 1.75)
    print(f"BMI for 70kg, 1.75m = {result}")
    assert result == pytest.approx(22.86, rel=1e-2), f"Expected ~22.86, got {result}"
    
    # Test edge cases
    print("Testing BMI with zero height (should raise error)")
    with pytest.raises(ZeroDivisionError):
        calculate_bmi(70, 0)
    print("Zero height error caught successfully")

# Weather function tests
def test_get_wind_direction():
    print("\nTesting wind direction conversion")
    test_cases = [
        (0, "N"), (90, "E"), (180, "S"), 
        (270, "W"), (45, "NE"), (360, "N")
    ]
    for degrees, expected in test_cases:
        result = _get_wind_direction(degrees)
        print(f"{degrees}° -> {result}")
        assert result == expected, f"Expected {expected}, got {result}"

# Web crawler utility tests
def test_remove_unicode():
    print("\nTesting unicode removal")
    test_str = "Hello World"
    result = remove_unicode(test_str)
    print(f"Input: {test_str}")
    print(f"Output: {result}")
    assert result == "Hello World", f"Expected 'Hello World', got {result}"

    test_str = "Hello 世界"
    result = remove_unicode(test_str)
    print(f"Input: {test_str}")
    print(f"Output: {result}")
    assert result == "Hello ", f"Expected 'Hello ', got {result}"

    test_str = "café"
    result = remove_unicode(test_str)
    print(f"Input: {test_str}")
    print(f"Output: {result}")
    assert result == "caf", f"Expected 'caf', got {result}"

def test_strip_html_tags():
    print("\nTesting HTML tag stripping")
    html = """
    <html>
        <head>
            <style>body { color: red; }</style>
            <script>console.log('test');</script>
        </head>
        <body>
            <h1>Title</h1>
            <p>Hello &nbsp; World!</p>
        </body>
    </html>
    """
    expected = "Title Hello World!"
    result = strip_html_tags(html).strip()
    print(f"Input HTML: {html}")
    print(f"Output: {result}")
    assert result == expected, f"Expected '{expected}', got '{result}'"

def test_truncate():
    print("\nTesting text truncation")
    # Test string that doesn't need truncation
    short_text = "Hello"
    result = truncate(short_text, 10)
    print(f"Input: {short_text}")
    print(f"Output: {result}")
    assert result == short_text, f"Expected '{short_text}', got '{result}'"

    # Test string that needs truncation
    long_text = "Hello World" * 1000
    result = truncate(long_text, 20)
    print(f"Input: {long_text[:50]}... (truncated)")
    print(f"Output: {result}")
    assert len(result.encode('utf-8')) <= 20 + len("\n...[truncated]")
    assert result.endswith("\n...[truncated]"), f"Expected output to end with '...[truncated]', got '{result[-15:]}'"

# Notes functionality tests
def test_ensure_file_exists(tmp_path):
    print("\nTesting file existence check")
    test_file = tmp_path / "test_notes.txt"
    with patch('main.NOTES_FILE', str(test_file)):
        ensure_file_exists()
        print(f"File created: {test_file.exists()}")
        assert test_file.exists()
        assert test_file.read_text() == ""

def test_add_note_to_file(tmp_path):
    print("\nTesting adding note to file")
    test_file = tmp_path / "test_notes.txt"
    with patch('main.NOTES_FILE', str(test_file)):
        result = add_note_to_file("Test note")
        print(f"Add note result: {result}")
        assert result == "A note was saved!"
        assert test_file.read_text() == "Test note\n"

        # Add another note
        add_note_to_file("Second note")
        print(f"File content after adding second note: {test_file.read_text()}")
        assert test_file.read_text() == "Test note\nSecond note\n"

def test_read_note_in_a_file(tmp_path):
    print("\nTesting reading note from file")
    test_file = tmp_path / "test_notes.txt"
    with patch('main.NOTES_FILE', str(test_file)):
        # Test empty file
        ensure_file_exists()
        result = read_note_in_a_file()
        print(f"Read result from empty file: {result}")
        assert result == "No notes could be read!"

        # Test with content
        test_file.write_text("Test note\nSecond note\n")
        result = read_note_in_a_file()
        print(f"Read result from file with content: {result}")
        assert result == "Test note\nSecond note"

# Async Weather API Tests
@pytest.mark.asyncio
async def test_fetch_US_weather():
    print("\nTesting US Weather API")
    
    # Mock successful response 
    async def mock_raise_for_status():
        return None
        
    mock_geocode_response = MagicMock()
    mock_geocode_response.status_code = 200
    mock_geocode_response.json.return_value = {
        "result": {
            "addressMatches": [{
                "coordinates": {
                    "x": -122.3301,
                    "y": 47.6038
                }
            }]
        }
    }
    mock_geocode_response.raise_for_status = AsyncMock(side_effect=mock_raise_for_status)

    mock_points_response = MagicMock()
    mock_points_response.status_code = 200
    mock_points_response.json.return_value = {
        "properties": {
            "forecast": "https://api.weather.gov/gridpoints/SEW/130,67/forecast"
        }
    }
    mock_points_response.raise_for_status = AsyncMock(side_effect=mock_raise_for_status)

    mock_forecast_response = MagicMock()
    mock_forecast_response.status_code = 200
    mock_forecast_response.json.return_value = {
        "properties": {
            "periods": [{
                "temperature": 72,
                "temperatureUnit": "F",
                "shortForecast": "Sunny",
                "windSpeed": "10 mph",
                "windDirection": "NW",
                "detailedForecast": "Sunny with high of 72°F"
            }]
        }
    }
    mock_forecast_response.raise_for_status = AsyncMock(side_effect=mock_raise_for_status)

    # Create mock async client
    print("Setting up mock async client with response sequence...")
    async def mock_client_get(url):
        if "geocoding.geo.census.gov" in url:  # Fix geocoding URL check
            return mock_geocode_response
        elif "api.weather.gov/points" in url:  # Fix points URL check
            return mock_points_response
        elif "forecast" in url:  # Fix forecast URL check
            return mock_forecast_response
        else:
            raise ValueError(f"Unexpected URL: {url}")

    async_client = AsyncMock()
    async_client.get = AsyncMock(side_effect=mock_client_get)
    async_client.__aenter__.return_value = async_client
    async_client.__aexit__.return_value = None
    print("Mock client setup complete")

    # Test successful weather fetch
    print("Testing successful US weather fetch for Seattle, WA...")
    with patch('httpx.AsyncClient', return_value=async_client):
        result = await fetch_US_weather("Seattle, WA")
        print(f"Success case result:\n{result}")
        print("Validating response content...")
        assert "Current weather in Seattle, WA" in result, "Location not found in response"
        assert "Temperature: 72°F" in result, "Temperature not found in response"
        assert "Sunny" in result, "Weather condition not found in response"
        print("Response validation successful")

    # Test error handling
    error_client = AsyncMock()
    mock_error = httpx.HTTPStatusError(
        "404 Not Found",
        request=MagicMock(),
        response=MagicMock(status_code=404)
    )
    error_client.get = AsyncMock(side_effect=mock_error)
    error_client.__aenter__.return_value = error_client
    error_client.__aexit__.return_value = None
    
    with patch('httpx.AsyncClient', return_value=error_client):
        result = await fetch_US_weather("NonExistent, XX")
        print(f"Error case result:\n{result}")
        assert "Error:" in result

@pytest.mark.asyncio
async def test_fetch_international_weather():
    print("\nTesting International Weather API")
    
    # Mock successful response
    async def mock_raise_for_status():
        return None

    mock_geocode_response = MagicMock()
    mock_geocode_response.status_code = 200
    mock_geocode_response.json.return_value = {
        "results": [{
            "name": "London",
            "country": "UK",
            "latitude": 51.5074,
            "longitude": -0.1278
        }]
    }
    mock_geocode_response.raise_for_status = AsyncMock(side_effect=mock_raise_for_status)

    mock_weather_response = MagicMock()
    mock_weather_response.status_code = 200
    mock_weather_response.json.return_value = {
        "current": {
            "temperature_2m": 68,
            "relative_humidity_2m": 75,
            "wind_speed_10m": 8,
            "wind_direction_10m": 270
        }
    }
    mock_weather_response.raise_for_status = AsyncMock(side_effect=mock_raise_for_status)

    # Create mock async client
    print("Setting up mock async client with response sequence...")
    async def mock_client_get(url):
        if "geocoding-api" in url:
            return mock_geocode_response
        else:
            return mock_weather_response

    async_client = AsyncMock()
    async_client.get = AsyncMock(side_effect=mock_client_get)
    async_client.__aenter__.return_value = async_client
    async_client.__aexit__.return_value = None
    print("Mock client setup complete")

    # Test successful weather fetch
    print("Testing international weather fetch for London...")
    with patch('httpx.AsyncClient', return_value=async_client):
        result = await fetch_international_weather("London")
        print(f"Success case result:\n{result}")
        print("Validating response content...")
        assert "Current weather in London, UK" in result, "Location not found in response"
        assert "Temperature: 68°F" in result, "Temperature not found in response"
        assert "Wind: 8 mph W" in result, "Wind information not found in response"
        print("Response validation successful")

    # Test error handling
    error_client = AsyncMock()
    mock_error = httpx.HTTPStatusError(
        "404 Not Found",
        request=MagicMock(),
        response=MagicMock(status_code=404)
    )
    error_client.get = AsyncMock(side_effect=mock_error)
    error_client.__aenter__.return_value = error_client
    error_client.__aexit__.return_value = None
    
    with patch('httpx.AsyncClient', return_value=error_client):
        result = await fetch_international_weather("NonExistent")
        print(f"Error case result:\n{result}")
        assert "Error:" in result

# Web Crawler Tests
@pytest.mark.asyncio
async def test_crawl_web_truncated():
    print("\nTesting web crawler with truncation")
    
    # Mock successful crawl
    mock_html = """
    <html>
        <body>
            <h1>Test Page</h1>
            <p>This is a test page content.</p>
            <script>alert('test');</script>
            <style>.test { color: red; }</style>
        </body>
    </html>
    """

    # Create mock result class
    class MockWebCrawlerResult:
        def __init__(self):
            self.success = True
            self.html = mock_html
            self.extracted_content = "Test Page\nThis is a test page content"

        def __str__(self):
            return self.extracted_content

    # Create mock result instance
    mock_result = MockWebCrawlerResult()

    print("Testing web crawling with content truncation...")
    from crawl4ai import AsyncWebCrawler

    # Create a mock crawler
    crawler = AsyncWebCrawler()
    crawler.arun = AsyncMock(return_value=[mock_result])
    
    with patch('main.AsyncWebCrawler', return_value=crawler):
        print("Crawling example.com...")
        result = await crawl_web_truncated("https://example.com")
        print(f"Success case result:\n{result}")
        print("Validating crawled content...")
        assert "Test Page" in result, "Main title not found in crawled content"
        assert "test page content" in result.lower(), "Page content not found"
        assert "<script>" not in result, "Script tags were not removed"
        assert "<style>" not in result, "Style tags were not removed"
        print("Content validation successful")

    # Test error handling
    mock_error_result = MockWebCrawlerResult()
    mock_error_result.success = False
    mock_error_result.error_message = "Failed to fetch page"

    error_crawler = AsyncWebCrawler()
    error_crawler.arun = AsyncMock(return_value=[mock_error_result])

    with patch('main.AsyncWebCrawler', return_value=error_crawler):
        result = await crawl_web_truncated("https://nonexistent.com")
        print(f"Error case result:\n{result}")
        assert "Crawl failed:" in result

@pytest.mark.asyncio
async def test_crawl_web_summarize_and_truncate():
    print("\nTesting web crawler with summarization")
    
    # Mock successful crawl
    mock_html = """
    <html>
        <body>
            <h1>Test Page</h1>
            <p>This is a test page with content that should be summarized.</p>
            <p>It has multiple paragraphs of information.</p>
        </body>
    </html>
    """

    mock_result = MagicMock()
    mock_result.success = True
    mock_result.html = mock_html
    mock_result.extracted_content = "Test Page\nThis is a test page with content that should be summarized.\nIt has multiple paragraphs of information."

    mock_crawler = MagicMock()
    mock_crawler.__aenter__ = AsyncMock(return_value=mock_crawler)
    mock_crawler.__aexit__ = AsyncMock(return_value=None)
    mock_crawler.arun = AsyncMock(return_value=[mock_result])

    mock_context = MagicMock()
    mock_context.ask_user = AsyncMock(return_value="Summary: This is a test page with multiple paragraphs.")

    # Test successful crawl and summarization
    print("Testing web crawling with content summarization...")
    with patch('crawl4ai.AsyncWebCrawler', return_value=mock_crawler):
        print("Crawling and summarizing example.com...")
        result = await crawl_web_summarize_and_truncate("https://example.com", mock_context)
        print(f"Success case result:\n{result}")
        print("Validating summarized content...")
        assert "Summary:" in result, "Summary marker not found in result"
        assert "test page" in result.lower(), "Expected content not found in summary"
        print("Summary validation successful")

    # Test error handling
    mock_error_result = MagicMock()
    mock_error_result.success = False
    mock_error_result.error_message = "Failed to fetch page"

    mock_error_crawler = MagicMock()
    mock_error_crawler.__aenter__ = AsyncMock(return_value=mock_error_crawler)
    mock_error_crawler.__aexit__ = AsyncMock(return_value=None)
    mock_error_crawler.arun = AsyncMock(return_value=[mock_error_result])
    
    with patch('crawl4ai.AsyncWebCrawler', return_value=mock_error_crawler):
        result = await crawl_web_summarize_and_truncate("https://nonexistent.com", mock_context)
        print(f"Error case result:\n{result}")
        assert "Crawl failed:" in result
