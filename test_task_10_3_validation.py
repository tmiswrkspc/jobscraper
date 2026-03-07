"""
Test validation for Task 10.3: Create intermediate results save function

This test validates that the save_intermediate_results() function correctly:
1. Saves job records to a JSON file
2. Creates output directory if it doesn't exist
3. Uses UTF-8 encoding for international characters
4. Overwrites existing files
5. Handles empty job lists
6. Preserves all job record fields

Requirements validated: 14.1, 14.3
"""

import json
import os
import tempfile
import shutil
from scraper import save_intermediate_results


def test_save_intermediate_results_basic():
    """Test basic functionality of saving intermediate results."""
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp()
    
    try:
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
                'company': 'Software Solutions',
                'location': 'Bangalore, Karnataka',
                'link': 'https://in.indeed.com/viewjob?jk=def456',
                'salary': None,
                'posted_date': '1 week ago',
                'description': 'Python developer needed for backend development'
            }
        ]
        
        # Save intermediate results
        output_path = os.path.join(test_dir, 'intermediate_results.json')
        save_intermediate_results(job_records, output_path)
        
        # Verify file was created
        assert os.path.exists(output_path), "Intermediate results file was not created"
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_records = json.load(f)
        
        # Verify all records were saved
        assert len(loaded_records) == 2, f"Expected 2 records, got {len(loaded_records)}"
        
        # Verify first record fields
        assert loaded_records[0]['title'] == 'Software Engineer'
        assert loaded_records[0]['company'] == 'Tech Corp'
        assert loaded_records[0]['location'] == 'Bangalore, Karnataka'
        assert loaded_records[0]['link'] == 'https://in.indeed.com/viewjob?jk=abc123'
        assert loaded_records[0]['salary'] == '₹8,00,000 - ₹12,00,000 a year'
        assert loaded_records[0]['posted_date'] == '2 days ago'
        
        # Verify second record fields
        assert loaded_records[1]['title'] == 'Python Developer'
        assert loaded_records[1]['company'] == 'Software Solutions'
        assert loaded_records[1]['salary'] is None
        
        print("✓ Basic save intermediate results test passed")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)


def test_save_intermediate_results_creates_directory():
    """Test that save_intermediate_results creates output directory if it doesn't exist."""
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp()
    
    try:
        # Sample job records
        job_records = [
            {
                'title': 'Data Analyst',
                'company': 'Analytics Inc',
                'location': 'Bangalore',
                'link': 'https://in.indeed.com/viewjob?jk=xyz789'
            }
        ]
        
        # Use nested directory that doesn't exist
        output_path = os.path.join(test_dir, 'output', 'intermediate_results.json')
        
        # Verify directory doesn't exist yet
        assert not os.path.exists(os.path.dirname(output_path))
        
        # Save intermediate results
        save_intermediate_results(job_records, output_path)
        
        # Verify directory was created
        assert os.path.exists(os.path.dirname(output_path)), "Output directory was not created"
        
        # Verify file was created
        assert os.path.exists(output_path), "Intermediate results file was not created"
        
        print("✓ Directory creation test passed")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)


def test_save_intermediate_results_empty_list():
    """Test that save_intermediate_results handles empty job list."""
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp()
    
    try:
        # Empty job records
        job_records = []
        
        # Save intermediate results
        output_path = os.path.join(test_dir, 'intermediate_results.json')
        save_intermediate_results(job_records, output_path)
        
        # Verify file was created
        assert os.path.exists(output_path), "Intermediate results file was not created"
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_records = json.load(f)
        
        # Verify empty list
        assert loaded_records == [], f"Expected empty list, got {loaded_records}"
        
        print("✓ Empty list test passed")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)


def test_save_intermediate_results_overwrites_existing():
    """Test that save_intermediate_results overwrites existing file."""
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp()
    
    try:
        output_path = os.path.join(test_dir, 'intermediate_results.json')
        
        # First save
        job_records_1 = [
            {
                'title': 'Job 1',
                'company': 'Company 1',
                'location': 'Location 1',
                'link': 'https://in.indeed.com/viewjob?jk=111'
            }
        ]
        save_intermediate_results(job_records_1, output_path)
        
        # Second save with different data
        job_records_2 = [
            {
                'title': 'Job 2',
                'company': 'Company 2',
                'location': 'Location 2',
                'link': 'https://in.indeed.com/viewjob?jk=222'
            },
            {
                'title': 'Job 3',
                'company': 'Company 3',
                'location': 'Location 3',
                'link': 'https://in.indeed.com/viewjob?jk=333'
            }
        ]
        save_intermediate_results(job_records_2, output_path)
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_records = json.load(f)
        
        # Verify second save overwrote first save
        assert len(loaded_records) == 2, f"Expected 2 records, got {len(loaded_records)}"
        assert loaded_records[0]['title'] == 'Job 2'
        assert loaded_records[1]['title'] == 'Job 3'
        
        print("✓ Overwrite existing file test passed")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)


def test_save_intermediate_results_utf8_encoding():
    """Test that save_intermediate_results uses UTF-8 encoding for international characters."""
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp()
    
    try:
        # Job records with international characters
        job_records = [
            {
                'title': 'Software Engineer',
                'company': 'Tech Corp',
                'location': 'Bangalore, Karnataka',
                'link': 'https://in.indeed.com/viewjob?jk=abc123',
                'salary': '₹8,00,000 - ₹12,00,000 a year',  # Rupee symbol
                'posted_date': '2 days ago',
                'description': 'Looking for engineers with C++ and Python experience'
            }
        ]
        
        # Save intermediate results
        output_path = os.path.join(test_dir, 'intermediate_results.json')
        save_intermediate_results(job_records, output_path)
        
        # Read and verify UTF-8 encoding
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            loaded_records = json.loads(content)
        
        # Verify rupee symbol is preserved
        assert '₹' in content, "Rupee symbol not preserved in file"
        assert loaded_records[0]['salary'] == '₹8,00,000 - ₹12,00,000 a year'
        
        print("✓ UTF-8 encoding test passed")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)


def test_save_intermediate_results_preserves_all_fields():
    """Test that save_intermediate_results preserves all job record fields."""
    # Create temporary directory for test
    test_dir = tempfile.mkdtemp()
    
    try:
        # Job record with all fields
        job_records = [
            {
                'title': 'Full Stack Developer',
                'company': 'Web Solutions Ltd',
                'location': 'Bangalore, Karnataka',
                'link': 'https://in.indeed.com/viewjob?jk=fullstack123',
                'salary': '₹10,00,000 - ₹15,00,000 a year',
                'posted_date': '3 days ago',
                'description': 'Full stack developer with React and Node.js experience required'
            }
        ]
        
        # Save intermediate results
        output_path = os.path.join(test_dir, 'intermediate_results.json')
        save_intermediate_results(job_records, output_path)
        
        # Read and verify all fields
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_records = json.load(f)
        
        # Verify all fields are present and correct
        record = loaded_records[0]
        assert 'title' in record
        assert 'company' in record
        assert 'location' in record
        assert 'link' in record
        assert 'salary' in record
        assert 'posted_date' in record
        assert 'description' in record
        
        assert record['title'] == 'Full Stack Developer'
        assert record['company'] == 'Web Solutions Ltd'
        assert record['location'] == 'Bangalore, Karnataka'
        assert record['link'] == 'https://in.indeed.com/viewjob?jk=fullstack123'
        assert record['salary'] == '₹10,00,000 - ₹15,00,000 a year'
        assert record['posted_date'] == '3 days ago'
        assert record['description'] == 'Full stack developer with React and Node.js experience required'
        
        print("✓ Preserve all fields test passed")
        
    finally:
        # Cleanup
        shutil.rmtree(test_dir)


if __name__ == '__main__':
    print("Running Task 10.3 validation tests...\n")
    
    test_save_intermediate_results_basic()
    test_save_intermediate_results_creates_directory()
    test_save_intermediate_results_empty_list()
    test_save_intermediate_results_overwrites_existing()
    test_save_intermediate_results_utf8_encoding()
    test_save_intermediate_results_preserves_all_fields()
    
    print("\n✅ All Task 10.3 validation tests passed!")
