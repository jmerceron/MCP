import pytest
import os
import tempfile
from unittest.mock import patch, mock_open
from main import (
    # Basic tools
    add, usd_to_gbp, get_height_for_16_9, calculate_bmi,
    # Weather functions
    _get_wind_direction,
    # Web crawler utilities
    remove_unicode, strip_html_tags, truncate,
    # Notes functionality
    ensure_file_exists, add_note_to_file, read_note_in_a_file,
)

# Basic tools tests
def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_usd_to_gbp():
    # Test with known exchange rate of 0.79
    assert usd_to_gbp(100) == 79.00
    assert usd_to_gbp(1) == 0.79
    assert usd_to_gbp(0) == 0.00

def test_get_height_for_16_9():
    assert get_height_for_16_9(1920) == 1080
    assert get_height_for_16_9(3840) == 2160
    assert get_height_for_16_9(0) == 0

def test_calculate_bmi():
    # Test normal BMI case
    assert calculate_bmi(70, 1.75) == pytest.approx(22.86, rel=1e-2)
    # Test edge cases
    with pytest.raises(ZeroDivisionError):
        calculate_bmi(70, 0)

# Weather function tests
def test_get_wind_direction():
    assert _get_wind_direction(0) == "N"
    assert _get_wind_direction(90) == "E"
    assert _get_wind_direction(180) == "S"
    assert _get_wind_direction(270) == "W"
    assert _get_wind_direction(45) == "NE"
    assert _get_wind_direction(360) == "N"

# Web crawler utility tests
def test_remove_unicode():
    assert remove_unicode("Hello World") == "Hello World"
    assert remove_unicode("Hello 世界") == "Hello "
    assert remove_unicode("café") == "caf"

def test_strip_html_tags():
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
    assert strip_html_tags(html).strip() == expected

def test_truncate():
    # Test string that doesn't need truncation
    short_text = "Hello"
    assert truncate(short_text, 10) == short_text

    # Test string that needs truncation
    long_text = "Hello World" * 1000
    truncated = truncate(long_text, 20)
    assert len(truncated.encode('utf-8')) <= 20 + len("\n...[truncated]")
    assert truncated.endswith("\n...[truncated]")

# Notes functionality tests
def test_ensure_file_exists(tmp_path):
    test_file = tmp_path / "test_notes.txt"
    with patch('main.NOTES_FILE', str(test_file)):
        ensure_file_exists()
        assert test_file.exists()
        assert test_file.read_text() == ""

def test_add_note_to_file(tmp_path):
    test_file = tmp_path / "test_notes.txt"
    with patch('main.NOTES_FILE', str(test_file)):
        result = add_note_to_file("Test note")
        assert result == "A note was saved!"
        assert test_file.read_text() == "Test note\n"

        # Add another note
        add_note_to_file("Second note")
        assert test_file.read_text() == "Test note\nSecond note\n"

def test_read_note_in_a_file(tmp_path):
    test_file = tmp_path / "test_notes.txt"
    with patch('main.NOTES_FILE', str(test_file)):
        # Test empty file
        ensure_file_exists()
        assert read_note_in_a_file() == "No notes could be read!"

        # Test with content
        test_file.write_text("Test note\nSecond note\n")
        assert read_note_in_a_file() == "Test note\nSecond note"
