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


# Add a way to find weather information
@mcp.tool()
async def fetch_weather(city: str) -> str:
    """Fetch current weather for a city"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.weather.com/{city}")
        return response.text


# Add a tool to generate an image
@mcp.tool()
def create_thumbnail_from_image(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")


# Add a tool that read files for you and generate a context
@mcp.tool()
async def long_task(files: list[str], ctx: Context) -> str:
    """Process multiple files with progress tracking"""
    for i, file in enumerate(files):
        ctx.info(f"Processing {file}")
        await ctx.report_progress(i, len(files))   
        data, mime_type = await ctx.read_resource(f"file://{file}")
    return "Processing complete"




# remove nonunicode characters
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
    """Crawl the web page and truncate the raw HTML content to fit size limits."""
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=link)
            if not result or not result[0].success:
                return f"Crawl failed: {remove_unicode(result[0].error_message)}"
            html = result[0].html or "Crawl succeeded but no HTML returned."
            return truncate(remove_unicode(html))
    except Exception as e:
        return f"[crawl_web_truncated error] {type(e).__name__}: {remove_unicode(str(e))}"
        
# Add a crawl_web tool that summarizes and truncates
@mcp.tool()
async def crawl_web_summarize_and_truncate(link: str, ctx: Context) -> str:
    """Crawl the page, summarize its content, and truncate the result to fit size limits."""
    try:
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=link)
            if not result or not result[0].success:
                return f"Crawl failed: {remove_unicode(result[0].error_message)}"
            
            content = result[0].extracted_content or result[0].html or ""
            content = remove_unicode(content)

            # Generate a summary with help from the language model
            summary = await ctx.ask_user(f"Summarize the following content:\n\n{truncate(content, 3000)}")
            return truncate(remove_unicode(summary))
    except Exception as e:
        return f"[crawl_web_summarize_and_truncate error] {type(e).__name__}: {remove_unicode(str(e))}"



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
#   with open(NOTES_FILE, "a") as f:
#        f.write(message + "\n")
    return "A note was saved!"

# add a tool that that can read a file
@mcp.tool()
def read_note_in_a_file() -> str:
    """ read the notes in a file """
    ensure_file_exists()
#   with open(NOTES_FILE, "r") as f:
#        content = f.read().strip()
#    return content or "No note could be read!"
    return "No note could be read!"

@mcp.resource("notes://latest")
def get_latest_notes() -> str:
    """ resource to get latest notes from a file """
    ensure_file_exists()
#    with open(NOTES_FILE, "r") as f:
#        lines = f.readlines()
#    return lines[-1].strip() if lines else "No notes yet!"
    return "No notes yet!"


@mcp.prompt()
def note_summary() -> str:
    """ generate a prompt to summarize the content of a file """
    ensure_file_exists()
#    with open(NOTES_FILE, "r") as f:
#        content = f.reaad().strip()
#    if not content
#        then return "No notes yet!"
#    return f"summarize the current notes: {content}"
    return "please summarize the current notes"


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"