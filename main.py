# server.py
from mcp.server.fastmcp import FastMCP, Context, Image
from crawl4ai import *
from PIL import Image as PILImage

import os
import httpx  # Add this at the top
import re
import sys

# Patch stdout/stderr encoding to UTF-8 to avoid cp932 issues
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
# Create an MCP server
mcp = FastMCP("julien_mcp_features")
#NOTES_FILES = "julien_generated_notes.txt"
NOTES_FILE = os.path.join(os.path.dirname(__file__),"julien_generated_notes.txt")
# Constants
MAX_RESULT_BYTES = 300_000 #instead oi 1_000_000 


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a currency converter tool
@mcp.tool()
def usd_to_gbp(amount: float) -> float:
    """convert USD(dollars) to GBP(pounds sterling)"""
    EXCHANGE_RATE = 0.79
    return round(amount * EXCHANGE_RATE, 2)


# Add a way to find height of a 16 by 9 screen based on width tool
@mcp.tool()
def get_height_for_16_9(width: float) -> float:
    """get height for a given width based on ratio 16 by 9"""
    return ((width * 9) / 16)


# Add a way to calculate bmi
@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Calculate BMI given weight in kg and height in meters"""
    return weight_kg / (height_m**2)



#################################################
################### WEATHER #####################
#################################################


# Add a way to find weather information
@mcp.tool()
async def fetch_US_weather(city: str) -> str:
    """Fetch current weather for a US city using the National Weather Service API"""
    headers = {
        "User-Agent": "(MCP Weather Tool, contact@example.com)",
        "Accept": "application/geo+json"
    }
    
    try:
        async with httpx.AsyncClient(headers=headers) as client:
            # First get the coordinates for the location
            points_url = f"https://api.weather.gov/points/{city}"
            if ',' not in city:
                return "Error: Please provide city and state in format 'City, ST' (e.g., 'Seattle, WA')"
                
            # Get geocoding data for the city
            geocoding_url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={city}&benchmark=2020&format=json"
            geocode_response = await client.get(geocoding_url)
            geocode_response.raise_for_status()
            geocode_data = geocode_response.json()
            
            # Extract coordinates from geocoding response
            try:
                match = geocode_data["result"]["addressMatches"][0]
                lat = match["coordinates"]["y"]
                lon = match["coordinates"]["x"]
            except (KeyError, IndexError):
                return f"Error: Could not find coordinates for '{city}'"
            
            # Get the forecast office URL for these coordinates
            points_response = await client.get(f"https://api.weather.gov/points/{lat},{lon}")
            points_response.raise_for_status()
            points_data = points_response.json()
            
            # Get the forecast
            forecast_url = points_data["properties"]["forecast"]
            forecast_response = await client.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()
            
            # Get the current period's forecast
            current_period = forecast_data["properties"]["periods"][0]
            
            # Format the weather information nicely
            return f"Current weather in {city}:\n" \
                   f"Temperature: {current_period['temperature']}°{current_period['temperatureUnit']}\n" \
                   f"Conditions: {current_period['shortForecast']}\n" \
                   f"Wind: {current_period['windSpeed']} {current_period['windDirection']}\n" \
                   f"Details: {current_period['detailedForecast']}"
                   
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Error: Location '{city}' not found"
        return f"Error: Weather service returned status {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error: Could not connect to weather service: {str(e)}"
    except KeyError as e:
        return f"Error: Unexpected response format from weather service: {str(e)}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"


# Add a way to find weather information for international cities
@mcp.tool()
async def fetch_international_weather(city: str) -> str:
    """Fetch current weather for any city worldwide using Open-Meteo API"""
    try:
        async with httpx.AsyncClient() as client:
            # First get the coordinates using geocoding API
            geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
            geocode_response = await client.get(geocode_url)
            geocode_response.raise_for_status()
            geocode_data = geocode_response.json()
            
            if not geocode_data.get("results"):
                return f"Error: Could not find location '{city}'"
            
            location = geocode_data["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            
            # Get current weather data
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"
                f"&wind_speed_unit=mph"
                f"&temperature_unit=fahrenheit"
            )
            
            weather_response = await client.get(weather_url)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            
            current = weather_data["current"]
            
            # Format the weather information nicely
            return (
                f"Current weather in {location['name']}, {location.get('country', '')}:\n"
                f"Temperature: {current['temperature_2m']}°F\n"
                f"Humidity: {current['relative_humidity_2m']}%\n"
                f"Wind: {current['wind_speed_10m']} mph {_get_wind_direction(current['wind_direction_10m'])}"
            )
                   
    except httpx.HTTPStatusError as e:
        return f"Error: Weather service returned status {e.response.status_code}"
    except httpx.RequestError as e:
        return f"Error: Could not connect to weather service: {str(e)}"
    except KeyError as e:
        return f"Error: Unexpected response format from weather service: {str(e)}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"

def _get_wind_direction(degrees: float) -> str:
    """Convert wind direction from degrees to cardinal direction"""
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                 "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    index = round(degrees / (360 / len(directions))) % len(directions)
    return directions[index]



#################################################
################## WEB CRAWLER ##################
#################################################


# remove non-unicode characters
def remove_unicode(text: str) -> str:
    """Remove non-ASCII characters from a string."""
    return re.sub(r'[^\x00-\x7F]+', '', text)

# strip HTML tags
def strip_html_tags(html):
    # Remove script and style tags with content
    html = re.sub(r'(?is)<(script|style).*?>.*?(</\1>)', '', html)
    # Remove all remaining tags
    html = re.sub(r'<[^>]+>', '', html)
    # Convert HTML entities (e.g., &nbsp;) to plain text
    html = re.sub(r'&[a-zA-Z]+;', ' ', html)
    # Collapse whitespace
    html = re.sub(r'\s+', ' ', html)
    return html.strip()
    
#truncate text
def truncate(text: str, max_bytes: int = MAX_RESULT_BYTES) -> str:
    """Truncate a string to fit within a byte limit."""
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    return encoded[:max_bytes].decode("utf-8", errors="ignore") + "\n...[truncated]"

# Add a crawl_web tool that truncates
@mcp.tool()
async def crawl_web_truncated(link: str) -> str:
    """Crawl the web page, clean and truncate its content to fit size limits."""
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=link)
            if not result or not result[0].success:
                error_msg = getattr(result[0], 'error_message', 'Unknown error') if result else 'No result returned'
                return f"Crawl failed: {remove_unicode(str(error_msg))}"
            
            # Try to get extracted content first, fall back to HTML if not available
            content = result[0].extracted_content or result[0].html
            if not content:
                return "Crawl succeeded but no content was returned."
            
            # Clean up the content: strip HTML, remove non-unicode chars, and truncate
            cleaned = strip_html_tags(content)  # First strip HTML tags
            cleaned = remove_unicode(cleaned)   # Then remove non-ASCII chars
            cleaned = cleaned.strip()           # Remove leading/trailing whitespace
            
            if not cleaned:
                return "Crawl succeeded but content was empty after cleaning."
                
            return truncate(cleaned)  # Finally truncate to size limit
            
    except Exception as e:
        return f"[crawl_web_truncated error] {type(e).__name__}: {remove_unicode(str(e))}"
        
# Add a crawl_web tool that summarizes and truncates
@mcp.tool()
async def crawl_web_summarize_and_truncate(link: str, ctx: Context) -> str:
    """Crawl the page, clean its content, generate a summary, and truncate the result."""
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=link)
            if not result or not result[0].success:
                error_msg = getattr(result[0], 'error_message', 'Unknown error') if result else 'No result returned'
                return f"Crawl failed: {remove_unicode(str(error_msg))}"
            
            # Try to get extracted content first, fall back to HTML if not available
            content = result[0].extracted_content or result[0].html
            if not content:
                return "Crawl succeeded but no content was returned."
            
            # Clean up the content before summarization
            cleaned = strip_html_tags(content)  # First strip HTML tags
            cleaned = remove_unicode(cleaned)   # Then remove non-ASCII chars
            cleaned = cleaned.strip()           # Remove leading/trailing whitespace
            
            if not cleaned:
                return "Crawl succeeded but content was empty after cleaning."
            
            # Truncate before sending for summarization to avoid overloading
            truncated = truncate(cleaned, 3000)
            
            # Generate a summary with help from the language model
            summary_prompt = (
                f"Please provide a comprehensive summary of the following webpage content. "
                f"Focus on the main points, key information, and important details:\n\n{truncated}"
            )
            summary = await ctx.ask_user(summary_prompt)
            
            if not summary:
                return "Failed to generate summary."
                
            # Clean up the summary and truncate to size limit
            cleaned_summary = remove_unicode(summary.strip())
            return truncate(cleaned_summary)
            
    except Exception as e:
        return f"[crawl_web_summarize_and_truncate error] {type(e).__name__}: {remove_unicode(str(e))}"



#################################################
##################### NOTES #####################
#################################################

#utility for adding notes to a file
def ensure_file_exists():
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w") as f:
            f.write("")

# add a tool that is adding notes to a file
@mcp.tool()
def add_note_to_file(message: str) -> str:
    """ append a new note to a sticky note file """
    ensure_file_exists()
    with open(NOTES_FILE, "a") as f:
        f.write(f"{message}\n")
    return "A note was saved!"

# add a tool that can read a file
@mcp.tool()
def read_note_in_a_file() -> str:
    """ read the notes in a file """
    ensure_file_exists()
    with open(NOTES_FILE, "r") as f:
        content = f.read().strip()
    return content if content else "No notes could be read!"

@mcp.resource("notes://latest")
def get_latest_notes() -> str:
    """ resource to get latest notes from a file """
    ensure_file_exists()
    try:
        with open(NOTES_FILE, "r") as f:
            lines = f.readlines()
        return lines[-1].strip() if lines else "No notes yet!"
    except Exception as e:
        return f"Error reading notes: {str(e)}"

@mcp.prompt()
def note_summary() -> str:
    """ generate a prompt to summarize the content of a file """
    ensure_file_exists()
    try:
        with open(NOTES_FILE, "r") as f:
            content = f.read().strip()
        if not content:
            return "No notes yet!"
        return f"Please summarize these notes:\n\n{content}"
    except Exception as e:
        return f"Error reading notes: {str(e)}"


#################################################
################## END ##########################
#################################################

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"