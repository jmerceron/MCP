import pytest
from main import (
    # Basic tools
    add, usd_to_gbp, get_height_for_16_9, calculate_bmi,
    # Weather tools
    fetch_US_weather, fetch_international_weather,
    # Notes tools
    add_note_to_file, read_note_in_a_file,
)

@pytest.mark.tools
def test_basic_tools():
    """Test the basic calculation tools"""
    # Test addition
    assert add(5, 3) == 8
    
    # Test currency conversion
    assert usd_to_gbp(100) == 79.00
    
    # Test screen ratio calculation
    assert get_height_for_16_9(1920) == 1080
    
    # Test BMI calculation
    assert calculate_bmi(70, 1.75) == pytest.approx(22.86, rel=1e-2)

@pytest.mark.asyncio
@pytest.mark.tools
async def test_weather_tools():
    """Test the weather API tools"""
    # Test US weather
    us_weather = await fetch_US_weather("Seattle, WA")
    assert "weather in Seattle, WA" in us_weather or "Error" in us_weather
    
    # Test international weather
    intl_weather = await fetch_international_weather("London")
    assert "weather in London" in intl_weather

@pytest.mark.tools
def test_note_tools(tmp_path):
    """Test the note management tools"""
    import datetime
    from unittest.mock import patch
    
    test_file = tmp_path / "test_notes.txt"
    with patch('main.NOTES_FILE', str(test_file)):
        # Test adding a note
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_note = f"Test note created on {current_time}"
        
        result = add_note_to_file(test_note)
        assert result == "A note was saved!"
        
        # Test reading notes
        content = read_note_in_a_file()
        assert test_note in content
