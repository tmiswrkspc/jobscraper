"""
Validation tests for Task 8.2: Create JSON export function

This test file validates the export_to_json function implementation.
Tests cover:
- Basic JSON export functionality
- UTF-8 encoding support
- Proper indentation and formatting
- Round-trip validation (export and parse)
- Empty list handling
- Directory creation
"""

import json
import os
import tempfile
import shutil
from scraper import export_to_json


def test_basic_json_export():
    """Test basic JSON export with sample job records."""
    # Sample job records
    job_records = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=abc123',
            'salary': '₹8,00,000 - ₹12,00,000 a year',
            'posted_date': '2 days ago',
            'description': 'We are looking for a skilled software engineer...'
        },
        {
            'title': 'Python Developer',
            'company': 'Software Inc',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=def456',
            'salary': None,
            'posted_date': '1 week ago',
            'description': 'Join our team as a Python developer...'
        }
    ]
    
    # Create temporary directory for test output
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, 'test_jobs.json')
        
        # Export to JSON
        export_to_json(job_records, output_path)
        
        # Verify file exists
        assert os.path.exists(output_path), "JSON file was not created"
        
        # Read and parse JSON file
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_records = json.load(f)
        
        # Verify content matches
        assert len(loaded_records) == 2, f"Expected 2 records, got {len(loaded_records)}"
        assert loaded_records[0]['title'] == 'Software Engineer'
        assert loaded_records[1]['title'] == 'Python Developer'
        
        print("✓ Basic JSON export test passed")


def test_utf8_encoding():
    """Test UTF-8 encoding with special characters."""
    job_records = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=test123',
            'salary': '₹10,00,000 - ₹15,00,000 a year',  # Rupee symbol
            'posted_date': '2 days ago',
            'description': 'Great opportunity with café culture! 🚀'  # Unicode emoji
        }
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, 'test_utf8.json')
        
        # Export to JSON
        export_to_json(job_records, output_path)
        
        # Read and verify UTF-8 encoding
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            loaded_records = json.loads(content)
        
        # Verify special characters are preserved
        assert '₹' in content, "Rupee symbol not preserved"
        assert '🚀' in content, "Emoji not preserved"
        assert loaded_records[0]['salary'] == '₹10,00,000 - ₹15,00,000 a year'
        
        print("✓ UTF-8 encoding test passed")


def test_json_formatting():
    """Test proper indentation and formatting."""
    job_records = [
        {
            'title': 'Test Job',
            'company': 'Test Company',
            'location': 'Test Location',
            'link': 'https://example.com/job',
            'salary': None,
            'posted_date': None,
            'description': None
        }
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, 'test_format.json')
        
        # Export to JSON
        export_to_json(job_records, output_path)
        
        # Read file content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify formatting
        assert content.startswith('['), "JSON should start with ["
        assert content.strip().endswith(']'), "JSON should end with ]"
        assert '  ' in content, "JSON should have indentation"
        
        # Verify it's valid JSON
        parsed = json.loads(content)
        assert isinstance(parsed, list), "JSON should be an array"
        
        print("✓ JSON formatting test passed")


def test_round_trip():
    """Test export and parse round-trip (Property 14)."""
    original_records = [
        {
            'title': 'Data Scientist',
            'company': 'Analytics Co',
            'location': 'Bangalore',
            'link': 'https://in.indeed.com/viewjob?jk=xyz789',
            'salary': '₹12,00,000 a year',
            'posted_date': '3 days ago',
            'description': 'Exciting data science role...'
        },
        {
            'title': 'Frontend Developer',
            'company': 'Web Solutions',
            'location': 'Remote',
            'link': 'https://in.indeed.com/viewjob?jk=uvw456',
            'salary': None,
            'posted_date': '1 week ago',
            'description': 'Build amazing user interfaces...'
        }
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, 'test_roundtrip.json')
        
        # Export to JSON
        export_to_json(original_records, output_path)
        
        # Parse JSON file
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_records = json.load(f)
        
        # Verify round-trip equivalence
        assert len(loaded_records) == len(original_records)
        
        for original, loaded in zip(original_records, loaded_records):
            assert original['title'] == loaded['title']
            assert original['company'] == loaded['company']
            assert original['location'] == loaded['location']
            assert original['link'] == loaded['link']
            assert original['salary'] == loaded['salary']
            assert original['posted_date'] == loaded['posted_date']
            assert original['description'] == loaded['description']
        
        print("✓ Round-trip test passed (Property 14)")


def test_empty_list():
    """Test export with empty job records list."""
    job_records = []
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, 'test_empty.json')
        
        # Export empty list
        export_to_json(job_records, output_path)
        
        # Verify file exists and contains empty array
        assert os.path.exists(output_path)
        
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_records = json.load(f)
        
        assert loaded_records == []
        assert isinstance(loaded_records, list)
        
        print("✓ Empty list test passed")


def test_directory_creation():
    """Test that output directory is created if it doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create nested directory path that doesn't exist
        nested_path = os.path.join(temp_dir, 'output', 'results', 'test.json')
        
        job_records = [
            {
                'title': 'Test Job',
                'company': 'Test Company',
                'location': 'Test Location',
                'link': 'https://example.com/job',
                'salary': None,
                'posted_date': None,
                'description': None
            }
        ]
        
        # Export should create directories
        export_to_json(job_records, nested_path)
        
        # Verify file exists
        assert os.path.exists(nested_path), "File should be created with nested directories"
        
        # Verify content
        with open(nested_path, 'r', encoding='utf-8') as f:
            loaded_records = json.load(f)
        
        assert len(loaded_records) == 1
        
        print("✓ Directory creation test passed")


def test_large_dataset():
    """Test export with larger dataset (100 records)."""
    # Generate 100 sample job records
    job_records = []
    for i in range(100):
        job_records.append({
            'title': f'Job Title {i}',
            'company': f'Company {i}',
            'location': f'Location {i}',
            'link': f'https://in.indeed.com/viewjob?jk=job{i}',
            'salary': f'₹{i},00,000 a year' if i % 2 == 0 else None,
            'posted_date': f'{i} days ago',
            'description': f'Description for job {i}...'
        })
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, 'test_large.json')
        
        # Export large dataset
        export_to_json(job_records, output_path)
        
        # Verify file exists
        assert os.path.exists(output_path)
        
        # Parse and verify
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_records = json.load(f)
        
        assert len(loaded_records) == 100
        assert loaded_records[0]['title'] == 'Job Title 0'
        assert loaded_records[99]['title'] == 'Job Title 99'
        
        print("✓ Large dataset test passed")


if __name__ == '__main__':
    print("Running Task 8.2 validation tests...\n")
    
    test_basic_json_export()
    test_utf8_encoding()
    test_json_formatting()
    test_round_trip()
    test_empty_list()
    test_directory_creation()
    test_large_dataset()
    
    print("\n✅ All Task 8.2 validation tests passed!")
    print("\nTask 8.2 Implementation Summary:")
    print("- ✓ export_to_json() function created")
    print("- ✓ UTF-8 encoding support")
    print("- ✓ Proper indentation (2 spaces)")
    print("- ✓ Valid JSON array format")
    print("- ✓ Round-trip validation (Property 14)")
    print("- ✓ Directory creation")
    print("- ✓ Requirements 6.1, 6.3, 6.5 validated")
