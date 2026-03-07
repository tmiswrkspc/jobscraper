"""
Unit tests for Task 8.1: Create filename generation function

This test file validates the generate_output_filename() function implementation.

Requirements validated:
- 6.7: Data_Exporter shall generate unique filenames using timestamps
"""

import re
import time
from scraper import generate_output_filename


def test_filename_format():
    """Test that generated filename follows the correct format."""
    filename = generate_output_filename("indeed_jobs", "json")
    
    # Expected format: base_name_YYYYMMDD_HHMMSS.extension
    pattern = r'^indeed_jobs_\d{8}_\d{6}\.json$'
    assert re.match(pattern, filename), f"Filename '{filename}' does not match expected format"
    print(f"✓ Filename format is correct: {filename}")


def test_filename_components():
    """Test that filename contains all required components."""
    base_name = "test_results"
    extension = "csv"
    filename = generate_output_filename(base_name, extension)
    
    # Check base name is present
    assert filename.startswith(base_name), f"Filename should start with '{base_name}'"
    
    # Check extension is present
    assert filename.endswith(f".{extension}"), f"Filename should end with '.{extension}'"
    
    # Check timestamp is present (8 digits for date + underscore + 6 digits for time)
    parts = filename.split('_')
    assert len(parts) >= 3, "Filename should have at least 3 underscore-separated parts"
    
    # Date part should be 8 digits
    date_part = parts[-2]
    assert len(date_part) == 8 and date_part.isdigit(), f"Date part '{date_part}' should be 8 digits"
    
    # Time part should be 6 digits (before the extension)
    time_part = parts[-1].split('.')[0]
    assert len(time_part) == 6 and time_part.isdigit(), f"Time part '{time_part}' should be 6 digits"
    
    print(f"✓ All filename components are present: {filename}")


def test_filename_uniqueness():
    """Test that filenames generated at different times are unique."""
    # Generate first filename
    filename1 = generate_output_filename("indeed_jobs", "json")
    
    # Wait 1 second to ensure different timestamp
    time.sleep(1)
    
    # Generate second filename
    filename2 = generate_output_filename("indeed_jobs", "json")
    
    # Filenames should be different
    assert filename1 != filename2, "Filenames generated 1 second apart should be different"
    print(f"✓ Filenames are unique:")
    print(f"  First:  {filename1}")
    print(f"  Second: {filename2}")


def test_different_base_names():
    """Test that different base names produce different filenames."""
    filename1 = generate_output_filename("jobs", "json")
    filename2 = generate_output_filename("results", "json")
    
    # Base names should be different
    assert filename1.startswith("jobs_"), f"First filename should start with 'jobs_'"
    assert filename2.startswith("results_"), f"Second filename should start with 'results_'"
    
    print(f"✓ Different base names produce different filenames:")
    print(f"  {filename1}")
    print(f"  {filename2}")


def test_different_extensions():
    """Test that different extensions produce different filenames."""
    filename1 = generate_output_filename("indeed_jobs", "json")
    filename2 = generate_output_filename("indeed_jobs", "csv")
    
    # Extensions should be different
    assert filename1.endswith(".json"), f"First filename should end with '.json'"
    assert filename2.endswith(".csv"), f"Second filename should end with '.csv'"
    
    print(f"✓ Different extensions produce different filenames:")
    print(f"  {filename1}")
    print(f"  {filename2}")


def test_timestamp_format():
    """Test that timestamp components are valid date/time values."""
    filename = generate_output_filename("test", "txt")
    
    # Extract timestamp from filename
    # Format: test_YYYYMMDD_HHMMSS.txt
    parts = filename.replace('.txt', '').split('_')
    date_part = parts[-2]  # YYYYMMDD
    time_part = parts[-1]  # HHMMSS
    
    # Validate date components
    year = int(date_part[0:4])
    month = int(date_part[4:6])
    day = int(date_part[6:8])
    
    assert 2020 <= year <= 2100, f"Year {year} should be reasonable"
    assert 1 <= month <= 12, f"Month {month} should be 1-12"
    assert 1 <= day <= 31, f"Day {day} should be 1-31"
    
    # Validate time components
    hour = int(time_part[0:2])
    minute = int(time_part[2:4])
    second = int(time_part[4:6])
    
    assert 0 <= hour <= 23, f"Hour {hour} should be 0-23"
    assert 0 <= minute <= 59, f"Minute {minute} should be 0-59"
    assert 0 <= second <= 59, f"Second {second} should be 0-59"
    
    print(f"✓ Timestamp components are valid: {date_part}_{time_part}")
    print(f"  Date: {year}-{month:02d}-{day:02d}")
    print(f"  Time: {hour:02d}:{minute:02d}:{second:02d}")


if __name__ == "__main__":
    print("Testing Task 8.1: generate_output_filename()\n")
    
    test_filename_format()
    print()
    
    test_filename_components()
    print()
    
    test_different_base_names()
    print()
    
    test_different_extensions()
    print()
    
    test_timestamp_format()
    print()
    
    test_filename_uniqueness()
    print()
    
    print("✅ All tests passed!")
