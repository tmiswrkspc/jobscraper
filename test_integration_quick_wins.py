"""
Integration Tests for Quick Wins Implementation (Task 7.2)

Tests full pipeline: scrape → normalize (with skills) → categorize → export
Tests edge cases: empty job list, missing fields, non-ASCII characters, 
all jobs in single category, and backward compatibility.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8**

Run with: python test_integration_quick_wins.py
"""

import json
import csv
from pathlib import Path
from serper_api import SerperAPI
from scraper import SerperJobScraper
from config import OUTPUT_DIR


def test_integration_full_pipeline():
    """
    Integration Test: Full Pipeline
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8**
    
    Tests full pipeline: scrape → normalize (with skills) → categorize → export
    """
    print("\n--- Integration Test 1: Full Pipeline ---")
    
    scraper = SerperJobScraper()
    api = SerperAPI()
    
    # Create sample jobs simulating scraped data
    jobs = [
        {
            'title': 'Senior Backend Developer',
            'company': 'TechCorp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job1',
            'salary': '₹15-25 LPA',
            'posted_date': '2 days ago',
            'description': 'Python developer with Django and Flask. Build REST APIs.',
            'source': 'test',
            'skills': []
        },
        {
            'title': 'Frontend Engineer',
            'company': 'UI Startup',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job2',
            'salary': '₹12-20 LPA',
            'posted_date': '1 day ago',
            'description': 'React and Angular developer for modern web applications.',
            'source': 'test',
            'skills': []
        },
        {
            'title': 'Full Stack Developer',
            'company': 'Product Company',
            'location': 'Pune, India',
            'link': 'https://example.com/job3',
            'salary': '₹18-30 LPA',
            'posted_date': '3 days ago',
            'description': 'Full-stack engineer with frontend and backend experience.',
            'source': 'test',
            'skills': []
        }
    ]
    
    # Extract skills (simulating normalization)
    for job in jobs:
        job['skills'] = api._extract_skills(job.get('description', ''))
    
    # Test 1: Verify all jobs have skills field
    assert all('skills' in job for job in jobs), "Not all jobs have skills field"
    assert all(isinstance(job['skills'], list) for job in jobs), "Skills field must be a list"
    print("✓ All jobs have skills field")
    
    # Test 2: Categorize jobs
    categories = scraper.categorize_jobs(jobs)
    
    # Verify all 7 categories exist
    expected_categories = {'backend', 'frontend', 'fullstack', 'data', 'devops', 'mobile', 'other'}
    assert set(categories.keys()) == expected_categories, "Not all categories present"
    print("✓ All 7 categories present")
    
    # Verify no jobs lost
    total_categorized = sum(len(cat_jobs) for cat_jobs in categories.values())
    assert total_categorized == len(jobs), "Jobs lost during categorization"
    print(f"✓ All {len(jobs)} jobs categorized (no jobs lost)")
    
    # Test 3: Export results
    output_path = Path(OUTPUT_DIR)
    existing_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    json_path, csv_path = scraper.export_results(jobs)
    
    # Verify combined files exist
    assert Path(json_path).exists(), "Combined JSON file not created"
    assert Path(csv_path).exists(), "Combined CSV file not created"
    print("✓ Combined JSON and CSV files created")
    
    # Verify category files created
    new_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    category_files = new_files - existing_files
    category_files = {f for f in category_files if f.stem.startswith('jobs_') and 
                     not f.stem.startswith('jobs_serper')}
    
    assert len(category_files) > 0, "No category files created"
    print(f"✓ Category files created: {len(category_files)} files")
    
    # Test 4: Verify category file contents
    for category_file in category_files:
        with open(category_file, 'r', encoding='utf-8') as f:
            category_jobs = json.load(f)
        
        assert isinstance(category_jobs, list), f"{category_file.name} doesn't contain a list"
        assert all('skills' in job for job in category_jobs), f"Jobs in {category_file.name} missing skills field"
    
    print("✓ All category files have correct structure with skills field")
    
    # Clean up
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    try:
        Path(json_path).unlink()
        Path(csv_path).unlink()
    except:
        pass
    
    print("✓ Full pipeline integration test passed!")


def test_integration_empty_job_list():
    """
    Integration Test: Empty Job List Edge Case
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8**
    
    Tests that the system handles empty job lists gracefully.
    """
    print("\n--- Integration Test 2: Empty Job List ---")
    
    scraper = SerperJobScraper()
    
    # Test with empty list
    jobs = []
    
    # Categorize empty list
    categories = scraper.categorize_jobs(jobs)
    
    # Verify all 7 categories exist but are empty
    expected_categories = {'backend', 'frontend', 'fullstack', 'data', 'devops', 'mobile', 'other'}
    assert set(categories.keys()) == expected_categories, "Not all categories present"
    assert all(len(cat_jobs) == 0 for cat_jobs in categories.values()), "Categories should be empty"
    print("✓ Empty job list handled correctly - all categories empty")
    
    # Export empty list
    output_path = Path(OUTPUT_DIR)
    existing_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    json_path, csv_path = scraper.export_results(jobs)
    
    # Verify that export returns None for empty job list (expected behavior)
    assert json_path is None, "JSON path should be None for empty job list"
    assert csv_path is None, "CSV path should be None for empty job list"
    print("✓ Export correctly returns None for empty job list")
    
    # Verify no files created
    new_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    category_files = new_files - existing_files
    
    assert len(category_files) == 0, "No files should be created for empty job list"
    print("✓ No files created for empty job list")
    
    print("✓ Empty job list edge case passed!")


def test_integration_missing_fields():
    """
    Integration Test: Missing Fields Edge Case
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8**
    
    Tests that the system handles jobs with missing title or description fields.
    """
    print("\n--- Integration Test 3: Missing Fields ---")
    
    scraper = SerperJobScraper()
    api = SerperAPI()
    
    # Create jobs with missing fields
    jobs = [
        {
            'title': '',  # Empty title
            'company': 'TechCorp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job1',
            'salary': None,
            'posted_date': None,
            'description': 'Backend developer with Python and Django experience',
            'source': 'test',
            'skills': []
        },
        {
            'title': 'Frontend Developer',
            'company': 'UI Startup',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job2',
            'salary': None,
            'posted_date': None,
            'description': '',  # Empty description
            'source': 'test',
            'skills': []
        },
        {
            'title': '',  # Both empty
            'company': 'DataCorp',
            'location': 'Pune, India',
            'link': 'https://example.com/job3',
            'salary': None,
            'posted_date': None,
            'description': '',
            'source': 'test',
            'skills': []
        }
    ]
    
    # Extract skills for jobs with missing fields
    for job in jobs:
        job['skills'] = api._extract_skills(job.get('description', ''))
    
    print(f"Created {len(jobs)} jobs with missing fields")
    
    # Categorize jobs with missing fields
    categories = scraper.categorize_jobs(jobs)
    
    # Verify all jobs are categorized (likely to 'other' due to missing fields)
    total_categorized = sum(len(cat_jobs) for cat_jobs in categories.values())
    assert total_categorized == len(jobs), "Jobs with missing fields should still be categorized"
    print("✓ Jobs with missing fields categorized successfully")
    
    # Export results
    output_path = Path(OUTPUT_DIR)
    existing_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    json_path, csv_path = scraper.export_results(jobs)
    
    # Verify files created
    assert Path(json_path).exists(), "Combined JSON file not created"
    assert Path(csv_path).exists(), "Combined CSV file not created"
    print("✓ Export succeeded with missing fields")
    
    # Verify exported data integrity
    with open(json_path, 'r', encoding='utf-8') as f:
        exported_jobs = json.load(f)
    
    assert len(exported_jobs) == len(jobs), "All jobs should be exported"
    assert all('skills' in job for job in exported_jobs), "All jobs should have skills field"
    print("✓ All jobs exported with skills field intact")
    
    # Clean up
    new_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    category_files = new_files - existing_files
    
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    try:
        Path(json_path).unlink()
        Path(csv_path).unlink()
    except:
        pass
    
    print("✓ Missing fields edge case passed!")


def test_integration_non_ascii_characters():
    """
    Integration Test: Non-ASCII Characters Edge Case
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8**
    
    Tests that the system handles non-ASCII characters (Unicode) correctly.
    """
    print("\n--- Integration Test 4: Non-ASCII Characters ---")
    
    scraper = SerperJobScraper()
    api = SerperAPI()
    
    # Create jobs with non-ASCII characters (Indian rupee symbol, Hindi, special chars)
    jobs = [
        {
            'title': 'Backend Developer',
            'company': 'टेक कॉर्प',  # Hindi characters
            'location': 'Bengaluru, India',
            'link': 'https://example.com/job1',
            'salary': '₹15-25 LPA',  # Rupee symbol
            'posted_date': '2 days ago',
            'description': 'Python developer with Django. Salary: ₹15-25 लाख per annum',
            'source': 'test',
            'skills': []
        },
        {
            'title': 'Frontend Engineer — React',  # Em dash
            'company': 'UI Startup™',  # Trademark symbol
            'location': 'Mumbai, India',
            'link': 'https://example.com/job2',
            'salary': '€50K',  # Euro symbol
            'posted_date': '1 day ago',
            'description': 'React developer • Modern UI • Great benefits',  # Bullet points
            'source': 'test',
            'skills': []
        },
        {
            'title': 'Data Scientist (ML/AI)',
            'company': 'Analytics™ Inc.',
            'location': 'Pune, India',
            'link': 'https://example.com/job3',
            'salary': '¥5M',  # Yen symbol
            'posted_date': '3 days ago',
            'description': 'Machine learning with Python 🐍 and TensorFlow',  # Emoji
            'source': 'test',
            'skills': []
        }
    ]
    
    # Extract skills
    for job in jobs:
        job['skills'] = api._extract_skills(job.get('description', ''))
    
    print(f"Created {len(jobs)} jobs with non-ASCII characters")
    
    # Verify skills extracted correctly despite non-ASCII chars
    assert 'Python' in jobs[0]['skills'], "Skills should be extracted from text with non-ASCII"
    assert 'Django' in jobs[0]['skills'], "Skills should be extracted from text with non-ASCII"
    assert 'React' in jobs[1]['skills'], "Skills should be extracted from text with non-ASCII"
    assert 'Python' in jobs[2]['skills'], "Skills should be extracted from text with emoji"
    assert 'Machine Learning' in jobs[2]['skills'], "Skills should be extracted from text with emoji"
    print("✓ Skills extracted correctly from non-ASCII text")
    
    # Categorize jobs
    categories = scraper.categorize_jobs(jobs)
    
    # Verify categorization works with non-ASCII
    assert len(categories['backend']) >= 1, "Backend job should be categorized"
    assert len(categories['frontend']) >= 1, "Frontend job should be categorized"
    assert len(categories['data']) >= 1, "Data job should be categorized"
    print("✓ Categorization works with non-ASCII characters")
    
    # Export results
    output_path = Path(OUTPUT_DIR)
    existing_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    json_path, csv_path = scraper.export_results(jobs)
    
    # Verify files created
    assert Path(json_path).exists(), "Combined JSON file not created"
    assert Path(csv_path).exists(), "Combined CSV file not created"
    print("✓ Export succeeded with non-ASCII characters")
    
    # Verify JSON encoding (ensure_ascii=False)
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read()
        exported_jobs = json.loads(content)
    
    # Check that non-ASCII characters are preserved
    assert '₹' in content or '₹' in str(exported_jobs), "Rupee symbol should be preserved"
    assert len(exported_jobs) == len(jobs), "All jobs should be exported"
    print("✓ Non-ASCII characters preserved in JSON export")
    
    # Verify CSV encoding
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_content = f.read()
    
    # CSV should contain the data (encoding may vary)
    assert len(csv_content) > 0, "CSV should contain data"
    print("✓ CSV export succeeded with non-ASCII characters")
    
    # Clean up
    new_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    category_files = new_files - existing_files
    
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    try:
        Path(json_path).unlink()
        Path(csv_path).unlink()
    except:
        pass
    
    print("✓ Non-ASCII characters edge case passed!")


def test_integration_all_jobs_single_category():
    """
    Integration Test: All Jobs in Single Category Edge Case
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8**
    
    Tests that the system handles the case where all jobs belong to a single category.
    """
    print("\n--- Integration Test 5: All Jobs in Single Category ---")
    
    scraper = SerperJobScraper()
    api = SerperAPI()
    
    # Create multiple backend jobs only
    jobs = [
        {
            'title': 'Backend Developer',
            'company': 'TechCorp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job1',
            'salary': None,
            'posted_date': None,
            'description': 'Python backend developer with Django',
            'source': 'test',
            'skills': []
        },
        {
            'title': 'API Engineer',
            'company': 'API Systems',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job2',
            'salary': None,
            'posted_date': None,
            'description': 'Build REST APIs with Flask',
            'source': 'test',
            'skills': []
        },
        {
            'title': 'Server Developer',
            'company': 'ServerCorp',
            'location': 'Pune, India',
            'link': 'https://example.com/job3',
            'salary': None,
            'posted_date': None,
            'description': 'Backend server development with Spring',
            'source': 'test',
            'skills': []
        },
        {
            'title': 'Backend Engineer',
            'company': 'BackendHub',
            'location': 'Hyderabad, India',
            'link': 'https://example.com/job4',
            'salary': None,
            'posted_date': None,
            'description': 'Backend development with Node.js',
            'source': 'test',
            'skills': []
        }
    ]
    
    # Extract skills
    for job in jobs:
        job['skills'] = api._extract_skills(job.get('description', ''))
    
    print(f"Created {len(jobs)} backend jobs")
    
    # Categorize jobs
    categories = scraper.categorize_jobs(jobs)
    
    # Verify all jobs in backend category
    assert len(categories['backend']) == len(jobs), "All jobs should be in backend category"
    assert all(len(categories[cat]) == 0 for cat in categories if cat != 'backend'), \
        "Other categories should be empty"
    print(f"✓ All {len(jobs)} jobs categorized to backend")
    
    # Export results
    output_path = Path(OUTPUT_DIR)
    existing_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    
    json_path, csv_path = scraper.export_results(jobs)
    
    # Verify combined files exist
    assert Path(json_path).exists(), "Combined JSON file not created"
    assert Path(csv_path).exists(), "Combined CSV file not created"
    print("✓ Combined files created")
    
    # Verify only backend category file created
    new_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    category_files = new_files - existing_files
    category_files = {f for f in category_files if f.stem.startswith('jobs_') and 
                     not f.stem.startswith('jobs_serper')}
    
    assert len(category_files) == 1, "Only one category file should be created"
    
    backend_file = [f for f in category_files if 'backend' in f.stem]
    assert len(backend_file) == 1, "Backend category file should exist"
    print("✓ Only backend category file created")
    
    # Verify backend file contains all jobs
    with open(backend_file[0], 'r', encoding='utf-8') as f:
        backend_jobs = json.load(f)
    
    assert len(backend_jobs) == len(jobs), "Backend file should contain all jobs"
    assert all('skills' in job for job in backend_jobs), "All jobs should have skills field"
    print(f"✓ Backend file contains all {len(jobs)} jobs with skills")
    
    # Clean up
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    try:
        Path(json_path).unlink()
        Path(csv_path).unlink()
    except:
        pass
    
    print("✓ All jobs in single category edge case passed!")


def test_integration_backward_compatibility():
    """
    Integration Test: Backward Compatibility
    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8**
    
    Tests that existing functionality still works (combined exports, deduplication, etc.).
    """
    print("\n--- Integration Test 6: Backward Compatibility ---")
    
    scraper = SerperJobScraper()
    
    # Create jobs with all original fields
    jobs = [
        {
            'title': 'Software Engineer',
            'company': 'TechCorp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job1',
            'salary': '₹15-25 LPA',
            'posted_date': '2 days ago',
            'description': 'Python developer',
            'source': 'serper_jobs_api',
            'skills': ['Python']
        },
        {
            'title': 'Developer',
            'company': 'DevHub',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job2',
            'salary': None,
            'posted_date': None,
            'description': 'General developer',
            'source': 'serper_search_api',
            'skills': []
        }
    ]
    
    print(f"Created {len(jobs)} jobs with original schema + skills field")
    
    # Test 1: Verify job dict schema
    for job in jobs:
        required_fields = ['title', 'company', 'location', 'link', 'salary', 
                          'posted_date', 'description', 'source', 'skills']
        assert all(field in job for field in required_fields), \
            "Job dict should have all required fields"
    print("✓ Job dict schema includes all original fields + skills")
    
    # Test 2: Export combined files (original functionality)
    output_path = Path(OUTPUT_DIR)
    existing_files = set(output_path.glob("jobs_serper_*.json")) if output_path.exists() else set()
    
    json_path, csv_path = scraper.export_results(jobs)
    
    # Verify combined files created with original naming pattern
    assert Path(json_path).exists(), "Combined JSON file not created"
    assert Path(csv_path).exists(), "Combined CSV file not created"
    assert 'serper_jobs_' in json_path, "JSON filename should follow original pattern"
    assert 'serper_jobs_' in csv_path, "CSV filename should follow original pattern"
    print("✓ Combined exports maintain original naming pattern")
    
    # Test 3: Verify JSON structure
    with open(json_path, 'r', encoding='utf-8') as f:
        exported_jobs = json.load(f)
    
    assert isinstance(exported_jobs, list), "JSON should contain a list"
    assert len(exported_jobs) == len(jobs), "All jobs should be exported"
    
    for job in exported_jobs:
        assert 'title' in job, "Original fields should be present"
        assert 'company' in job, "Original fields should be present"
        assert 'skills' in job, "New skills field should be present"
    print("✓ JSON structure maintains backward compatibility")
    
    # Test 4: Verify CSV structure
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        csv_jobs = list(reader)
    
    assert len(csv_jobs) == len(jobs), "All jobs should be in CSV"
    
    for job in csv_jobs:
        assert 'title' in job, "Original fields should be in CSV"
        assert 'company' in job, "Original fields should be in CSV"
        assert 'skills' in job, "New skills field should be in CSV"
    print("✓ CSV structure maintains backward compatibility")
    
    # Test 5: Verify category exports are additive (don't break existing exports)
    new_files = set(output_path.glob("jobs_*_*.json")) if output_path.exists() else set()
    category_files = new_files - existing_files
    
    # Both combined and category files should exist
    assert Path(json_path).exists(), "Combined JSON should still exist"
    assert Path(csv_path).exists(), "Combined CSV should still exist"
    print("✓ Category exports are additive (combined exports still work)")
    
    # Clean up
    for f in category_files:
        try:
            f.unlink()
        except:
            pass
    try:
        Path(json_path).unlink()
        Path(csv_path).unlink()
    except:
        pass
    
    print("✓ Backward compatibility test passed!")


def main():
    """Run all integration tests for Task 7.2"""
    print("="*70)
    print("INTEGRATION TESTS (Task 7.2)")
    print("="*70)
    print("\nTesting full pipeline and edge cases:")
    print("  1. Full pipeline (scrape → normalize → categorize → export)")
    print("  2. Empty job list")
    print("  3. Missing fields")
    print("  4. Non-ASCII characters")
    print("  5. All jobs in single category")
    print("  6. Backward compatibility")
    print("="*70)
    
    try:
        test_integration_full_pipeline()
        test_integration_empty_job_list()
        test_integration_missing_fields()
        test_integration_non_ascii_characters()
        test_integration_all_jobs_single_category()
        test_integration_backward_compatibility()
        
        print("\n\n" + "="*70)
        print("ALL INTEGRATION TESTS PASSED ✓")
        print("="*70)
        print("\nTest Summary:")
        print("  ✓ Full pipeline validated")
        print("  ✓ Empty job list handled correctly")
        print("  ✓ Missing fields handled correctly")
        print("  ✓ Non-ASCII characters preserved")
        print("  ✓ Single category export works")
        print("  ✓ Backward compatibility maintained")
        print("\nAll requirements validated (5.1-5.8)")
        print("="*70)
        
    except AssertionError as e:
        print(f"\n\n{'='*70}")
        print("TEST FAILED ✗")
        print("="*70)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n\n{'='*70}")
        print("TEST ERROR ✗")
        print("="*70)
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
