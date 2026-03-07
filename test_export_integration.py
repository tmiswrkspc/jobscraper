"""
Integration test for JSON and CSV export functions

This test verifies that both export functions work together correctly
and produce consistent output.
"""

import os
import json
import csv
import tempfile
from scraper import export_to_json, export_to_csv, generate_output_filename


def test_json_and_csv_export_consistency():
    """Test that JSON and CSV exports produce consistent data."""
    job_records = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, Karnataka',
            'salary': '₹10,00,000 a year',
            'posted_date': '2 days ago',
            'link': 'https://in.indeed.com/viewjob?jk=abc123',
            'description': 'Great opportunity with "excellent" benefits'
        },
        {
            'title': 'Python Developer',
            'company': 'Data Inc',
            'location': 'Remote',
            'link': 'https://in.indeed.com/viewjob?jk=def456'
            # Missing optional fields
        }
    ]
    
    # Create temporary files
    temp_dir = tempfile.mkdtemp()
    json_path = os.path.join(temp_dir, 'jobs.json')
    csv_path = os.path.join(temp_dir, 'jobs.csv')
    
    try:
        # Export to both formats
        export_to_json(job_records, json_path)
        export_to_csv(job_records, csv_path)
        
        # Read JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Read CSV
        with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)
        
        # Verify same number of records
        assert len(json_data) == len(csv_data) == len(job_records)
        
        # Verify data consistency
        for i, (json_rec, csv_rec, orig_rec) in enumerate(zip(json_data, csv_data, job_records)):
            # Check required fields
            assert json_rec['title'] == csv_rec['title'] == orig_rec['title']
            assert json_rec['company'] == csv_rec['company'] == orig_rec['company']
            assert json_rec['location'] == csv_rec['location'] == orig_rec['location']
            assert json_rec['link'] == csv_rec['link'] == orig_rec['link']
            
            # Check optional fields (CSV uses empty string for missing, JSON uses None or missing)
            if 'salary' in orig_rec:
                assert json_rec.get('salary') == csv_rec['salary'] == orig_rec['salary']
            else:
                assert csv_rec['salary'] == ''
            
            if 'posted_date' in orig_rec:
                assert json_rec.get('posted_date') == csv_rec['posted_date'] == orig_rec['posted_date']
            else:
                assert csv_rec['posted_date'] == ''
            
            if 'description' in orig_rec:
                assert json_rec.get('description') == csv_rec['description'] == orig_rec['description']
            else:
                assert csv_rec['description'] == ''
        
        print("✓ JSON and CSV export consistency test passed")
        
    finally:
        # Cleanup
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def test_filename_generation_consistency():
    """Test that filename generation works for both JSON and CSV."""
    import time
    
    # Generate filenames
    json_filename = generate_output_filename('test_jobs', 'json')
    time.sleep(0.01)  # Small delay to ensure different timestamp
    csv_filename = generate_output_filename('test_jobs', 'csv')
    
    # Verify format
    assert json_filename.startswith('test_jobs_')
    assert json_filename.endswith('.json')
    assert csv_filename.startswith('test_jobs_')
    assert csv_filename.endswith('.csv')
    
    # Verify timestamp format (YYYYMMDD_HHMMSS)
    import re
    pattern = r'test_jobs_\d{8}_\d{6}\.(json|csv)'
    assert re.match(pattern, json_filename)
    assert re.match(pattern, csv_filename)
    
    print("✓ Filename generation consistency test passed")


if __name__ == '__main__':
    print("Running export integration tests...\n")
    
    test_json_and_csv_export_consistency()
    test_filename_generation_consistency()
    
    print("\n✅ All export integration tests passed!")
