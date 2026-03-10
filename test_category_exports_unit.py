"""
Unit tests for category-specific exports (Task 5.6)

This module contains concrete unit tests with specific examples to complement
the property-based tests. These tests verify:
- Category file creation for non-empty categories
- Filename pattern matching
- File location in output directory
- JSON structure and encoding
- Combined exports still work (backward compatibility)
- Logging output for category exports

**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9**
"""

import json
import logging
import io
from pathlib import Path
from scraper import SerperJobScraper
from config import OUTPUT_DIR


def test_category_file_creation_for_non_empty_categories():
    """
    Test that category files are created only for non-empty categories.
    
    Validates: Requirements 4.2
    """
    print("\n" + "="*70)
    print("Unit Test: Category File Creation for Non-Empty Categories")
    print("="*70)
    
    scraper = SerperJobScraper()
    
    # Create test jobs for specific categories
    jobs = [
        {
            'title': 'Backend Developer',
            'company': 'TechCorp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'salary': None,
            'posted_date': None,
            'description': 'Looking for backend developer with Django experience',
            'source': 'test',
            'skills': ['Python', 'Django']
        },
        {
            'title': 'Frontend Developer',
            'company': 'WebWorks',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job/2',
            'salary': None,
            'posted_date': None,
            'description': 'React developer needed for UI work',
            'source': 'test',
            'skills': ['React', 'JavaScript']
        },
        {
            'title': 'DevOps Engineer',
            'company': 'CloudSys',
            'location': 'Pune, India',
            'link': 'https://example.com/job/3',
            'salary': None,
            'posted_date': None,
            'description': 'DevOps engineer with Kubernetes experience',
            'source': 'test',
            'skills': ['Kubernetes', 'Docker']
        }
    ]
    
    # Get output directory
    output_path = Path(OUTPUT_DIR)
    
    # Get existing files before export
    existing_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    # Export results
    json_path, csv_path = scraper.export_results(jobs)
    
    # Get new files after export
    new_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    # Find category files (exclude combined files)
    category_files = new_files - existing_files
    category_files = {f for f in category_files if f.stem.startswith('jobs_') and 
                     not f.stem.startswith('jobs_serper')}
    
    # Verify we have exactly 3 category files (backend, frontend, devops)
    assert len(category_files) == 3, f"Expected 3 category files, got {len(category_files)}"
    
    # Verify the specific categories exist
    category_names = set()
    for f in category_files:
        parts = f.stem.split('_')
        if len(parts) >= 2:
            category_names.add(parts[1])
    
    expected_categories = {'backend', 'frontend', 'devops'}
    assert category_names == expected_categories, \
        f"Expected categories {expected_categories}, got {category_names}"
    
    # Verify categories without jobs don't have files
    unexpected_categories = {'fullstack', 'data', 'mobile', 'other'}
    for f in category_files:
        parts = f.stem.split('_')
        if len(parts) >= 2:
            assert parts[1] not in unexpected_categories, \
                f"Unexpected category file created: {f.name}"
    
    # Clean up
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    if json_path:
        try:
            Path(json_path).unlink()
        except:
            pass
    if csv_path:
        try:
            Path(csv_path).unlink()
        except:
            pass
    
    print("✓ Category files created only for non-empty categories")



def test_filename_pattern_matching():
    """
    Test that category filenames follow the pattern jobs_{category}_{timestamp}.json
    
    Validates: Requirements 4.3
    """
    print("\n" + "="*70)
    print("Unit Test: Filename Pattern Matching")
    print("="*70)
    
    scraper = SerperJobScraper()
    
    # Create a simple test job
    jobs = [
        {
            'title': 'Data Scientist',
            'company': 'DataCorp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'salary': None,
            'posted_date': None,
            'description': 'Data scientist with machine learning experience',
            'source': 'test',
            'skills': ['Python', 'Machine Learning']
        }
    ]
    
    # Get output directory
    output_path = Path(OUTPUT_DIR)
    
    # Get existing files before export
    existing_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    # Export results
    json_path, csv_path = scraper.export_results(jobs)
    
    # Get new files after export
    new_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    # Find category files
    category_files = new_files - existing_files
    category_files = {f for f in category_files if f.stem.startswith('jobs_') and 
                     not f.stem.startswith('jobs_serper')}
    
    # Verify filename pattern for each category file
    import re
    pattern = re.compile(r'^jobs_([a-z]+)_(\d{8})_(\d{6})\.json$')
    
    for category_file in category_files:
        filename = category_file.name
        match = pattern.match(filename)
        
        assert match is not None, \
            f"Filename '{filename}' doesn't match pattern 'jobs_{{category}}_{{YYYYMMDD}}_{{HHMMSS}}.json'"
        
        category_name = match.group(1)
        date_part = match.group(2)
        time_part = match.group(3)
        
        # Verify category name is valid
        valid_categories = {'backend', 'frontend', 'fullstack', 'data', 'devops', 'mobile', 'other'}
        assert category_name in valid_categories, \
            f"Invalid category name '{category_name}' in filename"
        
        # Verify date format (YYYYMMDD)
        assert len(date_part) == 8 and date_part.isdigit(), \
            f"Invalid date format '{date_part}' (expected YYYYMMDD)"
        
        # Verify time format (HHMMSS)
        assert len(time_part) == 6 and time_part.isdigit(), \
            f"Invalid time format '{time_part}' (expected HHMMSS)"
        
        print(f"  ✓ Valid filename: {filename}")
    
    # Clean up
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    if json_path:
        try:
            Path(json_path).unlink()
        except:
            pass
    if csv_path:
        try:
            Path(csv_path).unlink()
        except:
            pass
    
    print("✓ All category filenames follow the correct pattern")



def test_file_location_in_output_directory():
    """
    Test that category files are created in the output directory.
    
    Validates: Requirements 4.4
    """
    print("\n" + "="*70)
    print("Unit Test: File Location in Output Directory")
    print("="*70)
    
    scraper = SerperJobScraper()
    
    # Create test jobs for multiple categories
    jobs = [
        {
            'title': 'Mobile Developer',
            'company': 'AppWorks',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'salary': None,
            'posted_date': None,
            'description': 'Android developer needed for mobile app',
            'source': 'test',
            'skills': ['Android', 'Kotlin']
        },
        {
            'title': 'Full Stack Developer',
            'company': 'WebCorp',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job/2',
            'salary': None,
            'posted_date': None,
            'description': 'Full stack developer with React and Node.js',
            'source': 'test',
            'skills': ['React', 'Node.js']
        }
    ]
    
    # Get output directory
    output_path = Path(OUTPUT_DIR)
    
    # Get existing files before export
    existing_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    # Export results
    json_path, csv_path = scraper.export_results(jobs)
    
    # Get new files after export
    new_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    # Find category files
    category_files = new_files - existing_files
    category_files = {f for f in category_files if f.stem.startswith('jobs_') and 
                     not f.stem.startswith('jobs_serper')}
    
    # Verify each file is in the output directory
    for category_file in category_files:
        # Check parent directory name matches OUTPUT_DIR
        assert category_file.parent.name == OUTPUT_DIR, \
            f"File {category_file.name} not in output directory (found in {category_file.parent})"
        
        # Verify file exists and is accessible
        assert category_file.exists(), \
            f"File {category_file.name} doesn't exist"
        
        # Verify it's a file, not a directory
        assert category_file.is_file(), \
            f"{category_file.name} is not a file"
        
        print(f"  ✓ File in correct location: {category_file}")
    
    # Clean up
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    if json_path:
        try:
            Path(json_path).unlink()
        except:
            pass
    if csv_path:
        try:
            Path(csv_path).unlink()
        except:
            pass
    
    print("✓ All category files are in the output directory")



def test_json_structure_and_encoding():
    """
    Test that category files have correct JSON structure and UTF-8 encoding.
    
    Validates: Requirements 4.5, 4.6, 4.7
    """
    print("\n" + "="*70)
    print("Unit Test: JSON Structure and Encoding")
    print("="*70)
    
    scraper = SerperJobScraper()
    
    # Create test jobs with non-ASCII characters to test encoding
    jobs = [
        {
            'title': 'Backend Developer',
            'company': 'TechCorp™',  # Non-ASCII character
            'location': 'Bengaluru, India',
            'link': 'https://example.com/job/1',
            'salary': '₹15-25 LPA',  # Rupee symbol
            'posted_date': None,
            'description': 'Backend developer with API experience • Must know Django',
            'source': 'test',
            'skills': ['Python', 'Django', 'REST API']
        },
        {
            'title': 'Frontend Developer',
            'company': 'WebWorks',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job/2',
            'salary': None,
            'posted_date': None,
            'description': 'React developer for UI/UX work',
            'source': 'test',
            'skills': ['React', 'JavaScript']
        }
    ]
    
    # Get output directory
    output_path = Path(OUTPUT_DIR)
    
    # Get existing files before export
    existing_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    # Export results
    json_path, csv_path = scraper.export_results(jobs)
    
    # Get new files after export
    new_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    # Find category files
    category_files = new_files - existing_files
    category_files = {f for f in category_files if f.stem.startswith('jobs_') and 
                     not f.stem.startswith('jobs_serper')}
    
    # Verify JSON structure and encoding for each file
    for category_file in category_files:
        print(f"\n  Testing file: {category_file.name}")
        
        # Test 1: UTF-8 encoding
        try:
            with open(category_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"    ✓ UTF-8 encoding verified")
        except UnicodeDecodeError:
            assert False, f"File {category_file.name} is not UTF-8 encoded"
        
        # Test 2: Valid JSON structure
        try:
            data = json.loads(content)
            print(f"    ✓ Valid JSON structure")
        except json.JSONDecodeError as e:
            assert False, f"File {category_file.name} contains invalid JSON: {e}"
        
        # Test 3: Data is a list
        assert isinstance(data, list), \
            f"File {category_file.name} doesn't contain a list (found {type(data).__name__})"
        print(f"    ✓ Data is a list")
        
        # Test 4: List contains job dictionaries
        assert len(data) > 0, f"File {category_file.name} contains empty list"
        for idx, job in enumerate(data):
            assert isinstance(job, dict), \
                f"Job {idx} in {category_file.name} is not a dictionary"
        print(f"    ✓ Contains {len(data)} job dictionaries")
        
        # Test 5: 2-space indentation
        # Re-serialize with indent=2 and compare
        expected_content = json.dumps(data, indent=2, ensure_ascii=False)
        content_normalized = content.replace('\r\n', '\n').strip()
        expected_normalized = expected_content.replace('\r\n', '\n').strip()
        
        assert content_normalized == expected_normalized, \
            f"File {category_file.name} doesn't use 2-space indentation"
        print(f"    ✓ 2-space indentation verified")
        
        # Test 6: ensure_ascii=False (non-ASCII characters preserved)
        # Check if non-ASCII characters are present in the content
        if any(ord(c) > 127 for c in content):
            print(f"    ✓ Non-ASCII characters preserved (ensure_ascii=False)")
        
        # Test 7: Job dictionary structure
        for job in data:
            required_fields = ['title', 'company', 'location', 'link', 'description', 'source', 'skills']
            for field in required_fields:
                assert field in job, \
                    f"Job in {category_file.name} missing required field '{field}'"
        print(f"    ✓ All jobs have required fields")
    
    # Clean up
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    if json_path:
        try:
            Path(json_path).unlink()
        except:
            pass
    if csv_path:
        try:
            Path(csv_path).unlink()
        except:
            pass
    
    print("\n✓ All category files have correct JSON structure and encoding")



def test_combined_exports_backward_compatibility():
    """
    Test that combined JSON and CSV exports still work (backward compatibility).
    
    Validates: Requirements 4.9, 5.2
    """
    print("\n" + "="*70)
    print("Unit Test: Combined Exports Backward Compatibility")
    print("="*70)
    
    scraper = SerperJobScraper()
    
    # Create diverse test jobs
    jobs = [
        {
            'title': 'Backend Developer',
            'company': 'TechCorp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'salary': None,
            'posted_date': None,
            'description': 'Backend developer with Django',
            'source': 'test',
            'skills': ['Python', 'Django']
        },
        {
            'title': 'Frontend Developer',
            'company': 'WebWorks',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job/2',
            'salary': None,
            'posted_date': None,
            'description': 'React developer',
            'source': 'test',
            'skills': ['React']
        },
        {
            'title': 'DevOps Engineer',
            'company': 'CloudSys',
            'location': 'Pune, India',
            'link': 'https://example.com/job/3',
            'salary': None,
            'posted_date': None,
            'description': 'DevOps with Kubernetes',
            'source': 'test',
            'skills': ['Kubernetes']
        }
    ]
    
    # Export results
    json_path, csv_path = scraper.export_results(jobs)
    
    # Test 1: Both paths are returned
    assert json_path is not None, "JSON path not returned"
    assert csv_path is not None, "CSV path not returned"
    print("  ✓ Both JSON and CSV paths returned")
    
    # Test 2: Combined JSON file exists
    json_file = Path(json_path)
    assert json_file.exists(), f"Combined JSON file doesn't exist: {json_path}"
    print(f"  ✓ Combined JSON file exists: {json_file.name}")
    
    # Test 3: Combined CSV file exists
    csv_file = Path(csv_path)
    assert csv_file.exists(), f"Combined CSV file doesn't exist: {csv_path}"
    print(f"  ✓ Combined CSV file exists: {csv_file.name}")
    
    # Test 4: Combined JSON contains all jobs
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    assert isinstance(json_data, list), "Combined JSON doesn't contain a list"
    assert len(json_data) == len(jobs), \
        f"Combined JSON has {len(json_data)} jobs, expected {len(jobs)}"
    print(f"  ✓ Combined JSON contains all {len(jobs)} jobs")
    
    # Test 5: Combined CSV contains all jobs
    import csv
    with open(csv_file, 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        csv_data = list(csv_reader)
    
    assert len(csv_data) == len(jobs), \
        f"Combined CSV has {len(csv_data)} jobs, expected {len(jobs)}"
    print(f"  ✓ Combined CSV contains all {len(jobs)} jobs")
    
    # Test 6: Combined files use correct naming pattern
    assert json_file.name.startswith('serper_jobs_'), \
        f"Combined JSON doesn't follow naming pattern: {json_file.name}"
    assert csv_file.name.startswith('serper_jobs_'), \
        f"Combined CSV doesn't follow naming pattern: {csv_file.name}"
    print("  ✓ Combined files follow naming pattern 'serper_jobs_{timestamp}'")
    
    # Test 7: Category files also exist (new functionality)
    output_path = Path(OUTPUT_DIR)
    all_json_files = set(output_path.glob("jobs_*_*.json"))
    category_files = {f for f in all_json_files if f.stem.startswith('jobs_') and 
                     not f.stem.startswith('jobs_serper')}
    
    assert len(category_files) > 0, "No category files created"
    print(f"  ✓ Category files also created: {len(category_files)} files")
    
    # Clean up
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    try:
        json_file.unlink()
    except:
        pass
    try:
        csv_file.unlink()
    except:
        pass
    
    print("✓ Combined exports work correctly (backward compatibility maintained)")



def test_logging_output_for_category_exports():
    """
    Test that logging output is generated for category exports.
    
    Validates: Requirements 4.8
    """
    print("\n" + "="*70)
    print("Unit Test: Logging Output for Category Exports")
    print("="*70)
    
    scraper = SerperJobScraper()
    
    # Create test jobs for specific categories
    jobs = [
        {
            'title': 'Data Analyst',
            'company': 'DataCorp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'salary': None,
            'posted_date': None,
            'description': 'Data analyst with SQL and Python',
            'source': 'test',
            'skills': ['Python', 'SQL']
        },
        {
            'title': 'Data Scientist',
            'company': 'MLWorks',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job/2',
            'salary': None,
            'posted_date': None,
            'description': 'Data scientist with machine learning',
            'source': 'test',
            'skills': ['Python', 'Machine Learning']
        },
        {
            'title': 'Backend Engineer',
            'company': 'TechCorp',
            'location': 'Pune, India',
            'link': 'https://example.com/job/3',
            'salary': None,
            'posted_date': None,
            'description': 'Backend engineer with API development',
            'source': 'test',
            'skills': ['Python', 'REST API']
        }
    ]
    
    # Set up log capture
    log_stream = io.StringIO()
    log_handler = logging.StreamHandler(log_stream)
    log_handler.setLevel(logging.INFO)
    
    # Get the root logger and add our handler
    logger = logging.getLogger()
    original_handlers = logger.handlers[:]
    original_level = logger.level
    
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    
    # Export results
    json_path, csv_path = scraper.export_results(jobs)
    
    # Get the log output
    log_output = log_stream.getvalue()
    
    # Remove our handler and restore original configuration
    logger.removeHandler(log_handler)
    logger.setLevel(original_level)
    log_handler.close()
    
    print("\n  Captured log output:")
    print("  " + "-"*66)
    for line in log_output.split('\n'):
        if line.strip():
            print(f"  {line}")
    print("  " + "-"*66)
    
    # Categorize jobs to know what to expect
    categories = scraper.categorize_jobs(jobs)
    
    # Test 1: Log contains category export messages
    for category_name, category_jobs in categories.items():
        if len(category_jobs) == 0:
            continue
        
        # Expected format: "✓ {category_name.capitalize()} jobs exported: {path} ({count} jobs)"
        category_capitalized = category_name.capitalize()
        
        # Check category name is in log
        assert category_capitalized in log_output, \
            f"Log missing category name '{category_capitalized}'"
        print(f"\n  ✓ Log contains '{category_capitalized}'")
        
        # Check job count is in log
        job_count_str = f"({len(category_jobs)} jobs)"
        assert job_count_str in log_output, \
            f"Log missing job count '{job_count_str}' for category '{category_name}'"
        print(f"  ✓ Log contains job count '{job_count_str}'")
        
        # Check file path pattern is in log
        file_pattern = f"jobs_{category_name}_"
        assert file_pattern in log_output, \
            f"Log missing file path pattern '{file_pattern}'"
        print(f"  ✓ Log contains file path pattern '{file_pattern}'")
        
        # Check "exported" keyword is in log
        assert 'exported' in log_output.lower(), \
            "Log missing 'exported' keyword"
    
    # Test 2: Combined export logs also present
    assert 'JSON exported' in log_output, "Log missing combined JSON export message"
    assert 'CSV exported' in log_output, "Log missing combined CSV export message"
    print("\n  ✓ Log contains combined export messages")
    
    # Clean up
    output_path = Path(OUTPUT_DIR)
    all_json_files = set(output_path.glob("jobs_*_*.json"))
    category_files = {f for f in all_json_files if f.stem.startswith('jobs_') and 
                     not f.stem.startswith('jobs_serper')}
    
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    if json_path:
        try:
            Path(json_path).unlink()
        except:
            pass
    if csv_path:
        try:
            Path(csv_path).unlink()
        except:
            pass
    
    print("\n✓ Logging output correctly generated for category exports")



if __name__ == "__main__":
    """Run all unit tests for category-specific exports."""
    print("\n" + "="*70)
    print("UNIT TESTS: Category-Specific Exports (Task 5.6)")
    print("="*70)
    
    try:
        test_category_file_creation_for_non_empty_categories()
        test_filename_pattern_matching()
        test_file_location_in_output_directory()
        test_json_structure_and_encoding()
        test_combined_exports_backward_compatibility()
        test_logging_output_for_category_exports()
        
        print("\n" + "="*70)
        print("✓ ALL UNIT TESTS PASSED!")
        print("="*70)
        print("\nValidated Requirements:")
        print("  - 4.1: Category-specific exports")
        print("  - 4.2: Non-empty category file creation")
        print("  - 4.3: Filename pattern")
        print("  - 4.4: File location in output directory")
        print("  - 4.5: Category file content")
        print("  - 4.6: UTF-8 encoding")
        print("  - 4.7: 2-space indentation")
        print("  - 4.8: Logging output")
        print("  - 4.9: Backward compatibility")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print("\n" + "="*70)
        print("✗ TEST FAILED")
        print("="*70)
        print(f"\nError: {e}\n")
        raise
    except Exception as e:
        print("\n" + "="*70)
        print("✗ TEST ERROR")
        print("="*70)
        print(f"\nUnexpected error: {e}\n")
        raise
